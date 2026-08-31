"""Tests for the versioned event-to-evidence execution contract."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from action_ledger.execution import (
    UnsupportedExecutionEventError,
    dispatch_receipt_envelope,
    github_pr_event_envelope,
    record_execution,
    ucc_collector_exception_envelope,
    verify_ucc_jurisdiction_activation,
)
from action_ledger.execution_schemas import (
    ApprovalGate,
    ApprovalStatus,
    Authority,
    CommandResult,
    EventRef,
    EvidenceRef,
    ExecutionEnvelope,
    ExecutionStage,
    FailureDetail,
    PolicyCheck,
    PolicyDecision,
    RollbackPlan,
    RollbackStatus,
    ScopedContext,
    Verification,
    VerificationStatus,
    WorkAction,
    WorkflowArtifact,
)
from action_ledger.ledger import load_actions
from action_ledger.schemas import ActionIndex, ParamRegistry, SequenceIndex


def _envelope(**updates) -> ExecutionEnvelope:
    values = {
        "execution_id": "exec-1",
        "idempotency_key": "delivery-1:received",
        "stage": ExecutionStage.RECEIVED,
        "event": EventRef(
            provider="test",
            event_type="test.created",
            event_id="delivery-1",
            occurred_at="2026-08-31T12:00:00Z",
            source="test://delivery-1",
        ),
        "scope": ScopedContext(refs=["repo://organvm/example@abc"]),
        "authority": Authority(
            principal="test-worker",
            delegated_by="test-suite",
            permissions=["read"],
            policy_ref="policy://test/v1",
        ),
        "policy": PolicyCheck(decision=PolicyDecision.ALLOW, reason="test policy"),
        "approval": ApprovalGate(required=False, status=ApprovalStatus.NOT_REQUIRED),
        "work": WorkAction(kind="inspect", target="organvm/example"),
        "workflow": WorkflowArtifact(objective="Inspect the example"),
        "rollback": RollbackPlan(strategy="No mutation", status=RollbackStatus.NOT_NEEDED),
    }
    values.update(updates)
    return ExecutionEnvelope(**values)


class TestExecutionValidation:
    def test_approval_pending_requires_required_pending_gate(self):
        with pytest.raises(ValidationError, match="approval_pending"):
            _envelope(stage=ExecutionStage.APPROVAL_PENDING)

    def test_verified_requires_approval_and_evidence(self):
        with pytest.raises(ValidationError, match="approved human gate"):
            _envelope(
                stage=ExecutionStage.VERIFIED,
                approval=ApprovalGate(required=True, status=ApprovalStatus.PENDING),
                verification=Verification(status=VerificationStatus.PASSED),
                evidence=[EvidenceRef(kind="test", ref="artifact://test")],
            )

        with pytest.raises(ValidationError, match="requires evidence"):
            _envelope(
                stage=ExecutionStage.VERIFIED,
                verification=Verification(status=VerificationStatus.PASSED),
            )

    def test_failed_requires_failure_detail(self):
        with pytest.raises(ValidationError, match="failure details"):
            _envelope(stage=ExecutionStage.FAILED)

        failed = _envelope(
            stage=ExecutionStage.FAILED,
            failure=FailureDetail(code="test.failed", message="expected failure"),
        )
        assert failed.failure is not None


class TestRecordExecution:
    def test_records_in_existing_ledger_and_deduplicates_redelivery(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()
        envelope = _envelope()

        first = record_execution(actions, sequences, registry, envelope)
        redelivery = record_execution(actions, sequences, registry, envelope.model_dump())

        assert first is redelivery
        assert len(actions.actions) == 1
        assert first.execution == envelope
        assert first.verb == "execution.received"
        assert first.params["contract_version"] == "organvm.execution/v1"
        assert len(sequences.sequences) == 1

    def test_same_execution_accepts_a_new_lifecycle_stage(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()
        first = _envelope()
        verified = _envelope(
            idempotency_key="delivery-1:verified",
            stage=ExecutionStage.VERIFIED,
            evidence=[EvidenceRef(kind="test_report", ref="artifact://test-report")],
            verification=Verification(status=VerificationStatus.PASSED),
        )

        record_execution(actions, sequences, registry, first)
        record_execution(actions, sequences, registry, verified)

        assert len(actions.actions) == 2
        assert {action.execution.stage for action in actions.actions} == {
            ExecutionStage.RECEIVED,
            ExecutionStage.VERIFIED,
        }

    def test_same_idempotency_key_does_not_collide_across_executions(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        first = _envelope(execution_id="exec-1", idempotency_key="provider:delivery-1")
        second = _envelope(execution_id="exec-2", idempotency_key="provider:delivery-1")

        recorded_first = record_execution(actions, sequences, registry, first)
        recorded_second = record_execution(actions, sequences, registry, second)

        assert recorded_first is not recorded_second
        assert len(actions.actions) == 2


class TestGitHubAdapter:
    def test_review_event_wakes_scoped_proposal_worker(self):
        payload = {
            "action": "submitted",
            "repository": {"full_name": "organvm/example"},
            "pull_request": {
                "number": 42,
                "html_url": "https://github.com/organvm/example/pull/42",
                "head": {"sha": "abc123"},
            },
            "review": {
                "id": 99,
                "submitted_at": "2026-08-31T12:00:00Z",
                "body": "untrusted review text must not enter the contract",
            },
        }

        envelope = github_pr_event_envelope(
            "pull_request_review",
            payload,
            delivery_id="github-delivery-1",
        )

        assert envelope.work.kind == "respond_to_review"
        assert envelope.scope.refs == [
            "https://github.com/organvm/example/pull/42",
            "git:organvm/example@abc123",
        ]
        assert envelope.authority.permissions == [
            "contents:read",
            "pull_requests:read",
            "changes:propose",
        ]
        assert "untrusted review text" not in envelope.model_dump_json()

    def test_plain_issue_comment_does_not_wake_pr_worker(self):
        payload = {
            "action": "created",
            "repository": {"full_name": "organvm/example"},
            "issue": {"number": 42},
            "comment": {"id": 99},
        }
        with pytest.raises(UnsupportedExecutionEventError, match="does not reference"):
            github_pr_event_envelope("issue_comment", payload)

    @pytest.mark.parametrize(
        ("event_name", "action", "expected"),
        [
            ("pull_request", "synchronize", "reverify_pr_commit"),
            ("pull_request", "closed", "record_pr_resolution"),
            ("pull_request", "ready_for_review", "run_pr_readiness_checks"),
        ],
    )
    def test_pr_lifecycle_routes(self, event_name: str, action: str, expected: str):
        envelope = github_pr_event_envelope(
            event_name,
            {
                "action": action,
                "repository": {"full_name": "organvm/example"},
                "pull_request": {
                    "id": 88,
                    "number": 42,
                    "html_url": "https://github.com/organvm/example/pull/42",
                    "head": {"sha": "abc123"},
                    "merged": action == "closed",
                    "updated_at": "2026-08-31T12:00:00Z",
                },
            },
        )
        assert envelope.work.kind == expected


class TestDispatchConvergence:
    def test_open_dispatch_becomes_received_action(self):
        envelope = dispatch_receipt_envelope(
            {
                "id": "D-2026-0831-001",
                "agent": "codex",
                "repo": "organvm/example",
                "work_type": "testing",
                "outbound": {
                    "dispatched_at": "2026-08-31T12:00:00Z",
                    "context_provided": ["AGENTS.md"],
                    "context_missing": ["secrets"],
                    "work_description": "Add tests",
                    "files_expected": ["tests/test_example.py"],
                    "write_permission": "propose_only",
                },
            }
        )
        assert envelope.stage == ExecutionStage.RECEIVED
        assert envelope.scope.refs == ["AGENTS.md"]
        assert envelope.provider_receipt_refs == ["dispatch://D-2026-0831-001"]

    def test_clean_return_becomes_verified_action(self):
        envelope = dispatch_receipt_envelope(
            {
                "id": "D-2026-0831-001",
                "agent": "codex",
                "repo": "organvm/example",
                "work_type": "testing",
                "outbound": {
                    "dispatched_at": "2026-08-31T12:00:00Z",
                    "work_description": "Add tests",
                },
                "return": {
                    "completed_at": "2026-08-31T12:05:00Z",
                    "outcome": "clean",
                    "files_touched": ["tests/test_example.py"],
                },
            }
        )
        assert envelope.stage == ExecutionStage.VERIFIED
        assert envelope.verification.status == VerificationStatus.PASSED
        assert envelope.evidence[0].ref == "tests/test_example.py"


class TestUccCollectorLifecycle:
    def test_worked_example_validates_against_contract(self):
        example = yaml.safe_load(
            Path("examples/execution-contracts/ucc-ny-collector-activation.yaml").read_text()
        )
        snapshots = [ExecutionEnvelope.model_validate(item) for item in example["snapshots"]]

        assert [snapshot.stage for snapshot in snapshots] == [
            ExecutionStage.FAILED,
            ExecutionStage.VERIFIED,
        ]

    def test_exception_fails_closed_pending_activation_approval(self):
        failed = ucc_collector_exception_envelope(
            jurisdiction="ny",
            strategy="scrape",
            event_id="queue-event-77",
            job_id="job-77",
            error="portal parser no longer matched the filing table",
            evidence_ref="audit://ucc/job-77/exception",
            occurred_at="2026-08-31T12:00:00Z",
        )

        assert failed.stage == ExecutionStage.FAILED
        assert failed.approval.status == ApprovalStatus.PENDING
        assert failed.policy.decision == PolicyDecision.REVIEW
        assert failed.scope.redacted is True
        assert failed.failure is not None
        assert failed.rollback.status == RollbackStatus.PLANNED

    def test_approved_activation_preserves_workflow_learning_and_evidence(self):
        failed = ucc_collector_exception_envelope(
            jurisdiction="NY",
            strategy="scrape",
            event_id="queue-event-77",
            job_id="job-77",
            error="portal parser no longer matched the filing table",
            evidence_ref="audit://ucc/job-77/exception",
            occurred_at="2026-08-31T12:00:00Z",
        )
        verified = verify_ucc_jurisdiction_activation(
            failed,
            approver="ucc-operations-owner",
            approval_ref="approval://ucc/NY/2026-08-31",
            principal="ucc-forward-deployed-engineer",
            command_results=[
                CommandResult(
                    command="npm run test:scrapers:ny",
                    exit_code=0,
                    result_ref="artifact://tests/ny-collector",
                    summary="NY collector fixture and dry run passed.",
                )
            ],
            dead_ends=["A CSS-only selector still matched the navigation table."],
            decisions=["Use header-labelled table discovery plus filing-number validation."],
            evidence=[
                EvidenceRef(kind="test_report", ref="artifact://tests/ny-collector"),
                EvidenceRef(kind="provenance", ref="artifact://provenance/ny-dry-run"),
            ],
            checks=["NY collector suite passed", "provenance fields complete"],
            occurred_at="2026-08-31T13:00:00Z",
        )

        assert verified.execution_id == failed.execution_id
        assert verified.stage == ExecutionStage.VERIFIED
        assert verified.approval.status == ApprovalStatus.APPROVED
        assert verified.verification.status == VerificationStatus.PASSED
        assert len(verified.workflow.command_results) == 1
        assert len(verified.workflow.dead_ends) == 1
        assert verified.workflow.approvals == ["approval://ucc/NY/2026-08-31"]


class TestGitHubEventCli:
    def test_dry_run_prints_contract_without_persisting(
        self, tmp_path, monkeypatch, capsys
    ):
        import json

        from action_ledger.__main__ import main

        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path / "ledger")
        event_path = tmp_path / "event.json"
        event_path.write_text(
            json.dumps(
                {
                    "action": "synchronize",
                    "repository": {"full_name": "organvm/example"},
                    "pull_request": {
                        "id": 88,
                        "number": 42,
                        "html_url": "https://github.com/organvm/example/pull/42",
                        "head": {"sha": "abc123"},
                    },
                }
            )
        )

        main(
            [
                "ingest-github-event",
                "--event-name",
                "pull_request",
                "--event-path",
                str(event_path),
                "--delivery-id",
                "delivery-42",
                "--dry-run",
            ]
        )

        assert '"schema_version": "organvm.execution/v1"' in capsys.readouterr().out
        assert not (tmp_path / "ledger" / "actions.yaml").exists()

    def test_redelivery_is_deduplicated_on_disk(self, tmp_path, monkeypatch, capsys):
        import json

        from action_ledger.__main__ import main

        ledger_dir = tmp_path / "ledger"
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", ledger_dir)
        event_path = tmp_path / "event.json"
        event_path.write_text(
            json.dumps(
                {
                    "action": "synchronize",
                    "repository": {"full_name": "organvm/example"},
                    "pull_request": {
                        "id": 88,
                        "number": 42,
                        "html_url": "https://github.com/organvm/example/pull/42",
                        "head": {"sha": "abc123"},
                    },
                }
            )
        )
        args = [
            "ingest-github-event",
            "--event-name",
            "pull_request",
            "--event-path",
            str(event_path),
            "--delivery-id",
            "delivery-42",
        ]

        main(args)
        main(args)

        output = capsys.readouterr().out
        assert "recorded:" in output
        assert "deduplicated:" in output
        assert len(load_actions(ledger_dir / "actions.yaml").actions) == 1
