"""Adapters and recording operations for the event-to-evidence contract."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

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
from action_ledger.ledger import record
from action_ledger.schemas import (
    Action,
    ActionIndex,
    ActionOrigin,
    ParamRegistry,
    RouteKind,
    SequenceIndex,
)


class UnsupportedExecutionEventError(ValueError):
    """Raised when a provider event should not awaken an execution worker."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def record_execution(
    action_index: ActionIndex,
    sequence_index: SequenceIndex,
    param_registry: ParamRegistry,
    envelope: ExecutionEnvelope | Mapping[str, Any],
) -> Action:
    """Append one idempotent execution snapshot to the existing Action Ledger.

    Redelivery returns the original action.  A legitimate lifecycle transition
    uses the same ``execution_id`` and a new stage-specific ``idempotency_key``.
    """

    execution = (
        envelope
        if isinstance(envelope, ExecutionEnvelope)
        else ExecutionEnvelope.model_validate(envelope)
    )

    for existing in action_index.actions:
        if (
            existing.execution is not None
            and existing.execution.execution_id == execution.execution_id
            and existing.execution.idempotency_key == execution.idempotency_key
        ):
            return existing

    routes: list[dict[str, str | float]] = [
        {"kind": RouteKind.INFORMED_BY, "target": execution.event.source},
    ]
    routes.extend(
        {"kind": RouteKind.CONSUMED, "target": ref}
        for ref in execution.scope.refs
    )
    routes.extend(
        {"kind": RouteKind.INFORMED_BY, "target": ref}
        for ref in execution.provider_receipt_refs
    )

    return record(
        action_index,
        sequence_index,
        param_registry,
        session=execution.execution_id,
        verb=f"execution.{execution.stage.value}",
        target=execution.work.target,
        context=execution.workflow.objective,
        params={
            "contract_version": execution.schema_version,
            "execution_id": execution.execution_id,
            "stage": execution.stage.value,
            "provider": execution.event.provider,
            "event_type": execution.event.event_type,
            "policy_decision": execution.policy.decision.value,
            "approval_status": execution.approval.status.value,
            "verification_status": execution.verification.status.value,
        },
        produced=[{"type": item.kind, "ref": item.ref} for item in execution.evidence],
        routes=routes,
        origin=ActionOrigin.EMITTED,
        execution=execution,
    )


_PR_EVENT_ROUTES: dict[tuple[str, str], str] = {
    ("pull_request_review", "submitted"): "respond_to_review",
    ("issue_comment", "created"): "triage_pr_comment",
    ("issue_comment", "edited"): "triage_pr_comment",
    ("pull_request", "synchronize"): "reverify_pr_commit",
    ("pull_request", "ready_for_review"): "run_pr_readiness_checks",
    ("pull_request", "reopened"): "run_pr_readiness_checks",
    ("pull_request", "closed"): "record_pr_resolution",
}


def github_pr_event_envelope(
    event_name: str,
    payload: Mapping[str, Any],
    *,
    delivery_id: str = "",
    principal: str = "organvm-pr-worker",
    occurred_at: str = "",
) -> ExecutionEnvelope:
    """Translate a GitHub PR event into a bounded worker wake-up receipt.

    The adapter deliberately excludes raw comment/review bodies.  Workers fetch
    scoped context by reference after policy evaluation, limiting secret and
    prompt-injection propagation from untrusted event payloads.
    """

    action = str(payload.get("action", ""))
    worker_action = _PR_EVENT_ROUTES.get((event_name, action))
    if worker_action is None:
        raise UnsupportedExecutionEventError(
            f"unsupported GitHub event: {event_name}:{action}"
        )

    repository = payload.get("repository", {})
    if not isinstance(repository, Mapping):
        repository = {}
    repo = str(repository.get("full_name", ""))
    if not repo:
        raise UnsupportedExecutionEventError(
            "GitHub event is missing repository.full_name"
        )

    if event_name == "issue_comment":
        issue = payload.get("issue", {})
        if not isinstance(issue, Mapping) or not issue.get("pull_request"):
            raise UnsupportedExecutionEventError(
                "issue_comment does not reference a pull request"
            )
        pr_number = int(issue.get("number", 0))
        provider_object = payload.get("comment", {})
    else:
        pull_request = payload.get("pull_request", {})
        if not isinstance(pull_request, Mapping):
            pull_request = {}
        pr_number = int(pull_request.get("number", 0))
        if event_name == "pull_request_review":
            provider_object = payload.get("review", {})
        else:
            provider_object = pull_request

    if pr_number <= 0:
        raise UnsupportedExecutionEventError(
            "GitHub event is missing a pull request number"
        )
    if not isinstance(provider_object, Mapping):
        provider_object = {}

    pull_request = payload.get("pull_request", {})
    if not isinstance(pull_request, Mapping):
        pull_request = {}
    head = pull_request.get("head", {})
    if not isinstance(head, Mapping):
        head = {}
    head_sha = str(head.get("sha", ""))
    object_id = str(provider_object.get("id", ""))
    event_id = delivery_id or ":".join(
        part for part in (repo, str(pr_number), event_name, action, object_id, head_sha) if part
    )
    timestamp = occurred_at or str(
        provider_object.get("submitted_at")
        or provider_object.get("updated_at")
        or provider_object.get("created_at")
        or _now()
    )
    execution_id = f"github:{repo}:pr-{pr_number}"
    source_url = str(
        provider_object.get("html_url")
        or pull_request.get("html_url")
        or f"https://github.com/{repo}/pull/{pr_number}"
    )
    merged = bool(pull_request.get("merged", False))
    target = f"{repo}#pull-{pr_number}"

    return ExecutionEnvelope(
        execution_id=execution_id,
        idempotency_key=f"{event_id}:{worker_action}",
        stage=ExecutionStage.RECEIVED,
        event=EventRef(
            provider="github",
            event_type=f"{event_name}.{action}",
            event_id=event_id,
            occurred_at=timestamp,
            source=source_url,
            delivery_id=delivery_id,
        ),
        scope=ScopedContext(
            refs=[source_url, *([f"git:{repo}@{head_sha}"] if head_sha else [])],
            forbidden=["repository secrets", "unrelated repositories", "protected-branch writes"],
            retrieved_at=timestamp,
            redacted=True,
        ),
        authority=Authority(
            principal=principal,
            delegated_by="github.event",
            permissions=["contents:read", "pull_requests:read", "changes:propose"],
            policy_ref="policy://organvm/pr-event-worker/v1",
        ),
        policy=PolicyCheck(
            decision=PolicyDecision.ALLOW,
            reason=(
                "Event authorizes scoped analysis and proposal only; "
                "mutation needs a later gate."
            ),
        ),
        approval=ApprovalGate(required=False, status=ApprovalStatus.NOT_REQUIRED),
        work=WorkAction(kind=worker_action, target=target),
        workflow=WorkflowArtifact(
            objective=f"Handle {event_name}.{action} for {target}",
            plan=[
                "Retrieve only the referenced PR, changed paths, and current checks.",
                "Evaluate repository policy and determine the smallest permitted response.",
                "Produce a change or response proposal with evidence.",
                "Require approval before consequential mutation, then verify the result.",
            ],
            decisions=[f"merged={str(merged).lower()}"],
        ),
        verification=Verification(status=VerificationStatus.PENDING),
        rollback=RollbackPlan(
            strategy=(
                "No mutation at wake-up; later mutations must name a revert "
                "or compensating action."
            ),
            status=RollbackStatus.NOT_NEEDED,
        ),
    )


def dispatch_receipt_envelope(
    receipt: Mapping[str, Any],
    *,
    dispatched_by: str = "conductor",
) -> ExecutionEnvelope:
    """Map a Conductor dispatch receipt into the canonical Action Ledger contract."""

    dispatch_id = str(receipt.get("id") or receipt.get("dispatch_id") or "")
    if not dispatch_id:
        raise ValueError("dispatch receipt is missing id")
    outbound = receipt.get("outbound", {})
    if not isinstance(outbound, Mapping):
        outbound = {}
    returned = receipt.get("return")
    if returned is not None and not isinstance(returned, Mapping):
        returned = {}

    outcome = str(returned.get("outcome", "")) if isinstance(returned, Mapping) else ""
    is_clean = outcome == "clean"
    stage = (
        ExecutionStage.VERIFIED
        if is_clean
        else ExecutionStage.FAILED
        if returned is not None
        else ExecutionStage.RECEIVED
    )
    verification_status = (
        VerificationStatus.PASSED
        if is_clean
        else VerificationStatus.FAILED
        if returned is not None
        else VerificationStatus.PENDING
    )
    repo = str(receipt.get("repo", ""))
    touched = list(returned.get("files_touched", [])) if isinstance(returned, Mapping) else []
    evidence = [EvidenceRef(kind="changed_file", ref=str(path)) for path in touched]
    if is_clean and not evidence:
        evidence = [EvidenceRef(kind="dispatch_receipt", ref=f"dispatch://{dispatch_id}")]

    failure = None
    if returned is not None and not is_clean:
        failure = FailureDetail(
            code=f"dispatch.{outcome or 'failed'}",
            message=str(returned.get("what_failed", "Dispatch did not verify cleanly.")),
            retryable=outcome == "partial_fix",
            evidence_ref=f"dispatch://{dispatch_id}",
        )

    dispatched_at = str(outbound.get("dispatched_at", "")) or _now()
    write_permission = str(outbound.get("write_permission", "direct_edit"))
    return ExecutionEnvelope(
        execution_id=dispatch_id,
        idempotency_key=f"dispatch:{dispatch_id}:{stage.value}",
        stage=stage,
        event=EventRef(
            provider="conductor",
            event_type="dispatch.returned" if returned is not None else "dispatch.created",
            event_id=dispatch_id,
            occurred_at=(
                str(returned.get("completed_at", ""))
                if isinstance(returned, Mapping)
                else dispatched_at
            )
            or dispatched_at,
            source=f"dispatch://{dispatch_id}",
        ),
        scope=ScopedContext(
            refs=[str(ref) for ref in outbound.get("context_provided", [])],
            forbidden=[str(ref) for ref in outbound.get("context_missing", [])],
            retrieved_at=dispatched_at,
            redacted=True,
        ),
        authority=Authority(
            principal=str(receipt.get("agent", "unknown-agent")),
            delegated_by=dispatched_by,
            permissions=[write_permission],
            policy_ref="policy://conductor/dispatch/v1",
        ),
        policy=PolicyCheck(
            decision=PolicyDecision.ALLOW,
            reason="A persisted Conductor dispatch receipt records the evaluated delegation.",
        ),
        approval=ApprovalGate(required=False, status=ApprovalStatus.NOT_REQUIRED),
        work=WorkAction(
            kind=str(receipt.get("work_type", "dispatch")),
            target=repo or dispatch_id,
        ),
        workflow=WorkflowArtifact(
            objective=str(outbound.get("work_description", "Conductor dispatch")),
            plan=[f"Produce expected file: {path}" for path in outbound.get("files_expected", [])],
            decisions=[f"write_permission={write_permission}"],
        ),
        evidence=evidence,
        verification=Verification(
            status=verification_status,
            checks=[f"dispatch outcome={outcome}"] if outcome else [],
            reviewer=dispatched_by if returned is not None else "",
            reviewed_at=(
                str(returned.get("completed_at", ""))
                if isinstance(returned, Mapping)
                else ""
            ),
        ),
        rollback=RollbackPlan(
            strategy="Revert the attributed diff and retain the original dispatch receipt.",
            status=RollbackStatus.NOT_NEEDED if is_clean else RollbackStatus.PLANNED,
        ),
        failure=failure,
        provider_receipt_refs=[f"dispatch://{dispatch_id}"],
    )


def ucc_collector_exception_envelope(
    *,
    jurisdiction: str,
    strategy: str,
    event_id: str,
    job_id: str,
    error: str,
    evidence_ref: str,
    occurred_at: str = "",
    principal: str = "ucc-ingestion-worker",
) -> ExecutionEnvelope:
    """Create the UCC collector-exception snapshot used before activation review."""

    state = jurisdiction.strip().upper()
    timestamp = occurred_at or _now()
    execution_id = f"ucc:{state}:collector:{job_id}"
    return ExecutionEnvelope(
        execution_id=execution_id,
        idempotency_key=f"{event_id}:failed",
        stage=ExecutionStage.FAILED,
        event=EventRef(
            provider="ucc-worker",
            event_type="ucc.collector.exception",
            event_id=event_id,
            occurred_at=timestamp,
            source=evidence_ref,
        ),
        scope=ScopedContext(
            refs=[
                f"jurisdiction://{state}",
                f"collector://{state}/{strategy}",
                evidence_ref,
            ],
            forbidden=["unrelated jurisdictions", "raw credentials", "production activation"],
            retrieved_at=timestamp,
            redacted=True,
        ),
        authority=Authority(
            principal=principal,
            delegated_by="ucc.ingestion.queue",
            permissions=["collector:read", "telemetry:write", "patch:propose"],
            policy_ref="policy://ucc/jurisdiction-activation/v1",
        ),
        policy=PolicyCheck(
            decision=PolicyDecision.REVIEW,
            reason="Collector remediation may be proposed, but activation requires owner approval.",
        ),
        approval=ApprovalGate(required=True, status=ApprovalStatus.PENDING),
        work=WorkAction(kind="repair_and_activate_collector", target=f"ucc:{state}:{strategy}"),
        workflow=WorkflowArtifact(
            objective=f"Restore trustworthy {state} UCC collection after a {strategy} failure.",
            plan=[
                "Inspect the collector exception and source provenance.",
                "Reproduce against a non-production fixture or dry run.",
                "Patch the collector and run jurisdiction-specific validation.",
                "Request activation approval with test and provenance evidence.",
            ],
            decisions=[
                "Fail closed: do not activate or silently fall back without policy evidence."
            ],
        ),
        evidence=[
            EvidenceRef(
                kind="collector_exception",
                ref=evidence_ref,
                summary="Redacted collector failure and telemetry receipt.",
            )
        ],
        verification=Verification(
            status=VerificationStatus.PENDING,
            checks=[f"collector test:{state}", "provenance completeness", "duplicate-safe upsert"],
        ),
        rollback=RollbackPlan(
            strategy="Keep the collector disabled and retain the last verified dataset.",
            status=RollbackStatus.PLANNED,
        ),
        failure=FailureDetail(
            code="ucc.collector.exception",
            message=error,
            retryable=True,
            evidence_ref=evidence_ref,
        ),
    )


def verify_ucc_jurisdiction_activation(
    failed: ExecutionEnvelope,
    *,
    approver: str,
    approval_ref: str,
    principal: str,
    command_results: list[CommandResult],
    evidence: list[EvidenceRef],
    checks: list[str],
    occurred_at: str = "",
    dead_ends: list[str] | None = None,
    decisions: list[str] | None = None,
) -> ExecutionEnvelope:
    """Advance a reviewed UCC collector exception to verified activation."""

    if failed.event.event_type != "ucc.collector.exception":
        raise ValueError("activation verification requires a UCC collector exception")
    if not evidence or not checks:
        raise ValueError("activation verification requires evidence and checks")

    timestamp = occurred_at or _now()
    workflow = failed.workflow.model_copy(deep=True)
    workflow.command_results.extend(command_results)
    workflow.dead_ends.extend(dead_ends or [])
    workflow.decisions.extend(decisions or [])
    workflow.approvals.append(approval_ref)

    return ExecutionEnvelope(
        execution_id=failed.execution_id,
        idempotency_key=f"{failed.execution_id}:verified:{approval_ref}",
        stage=ExecutionStage.VERIFIED,
        event=EventRef(
            provider="ucc-activation",
            event_type="ucc.jurisdiction.activation.approved",
            event_id=approval_ref,
            occurred_at=timestamp,
            source=approval_ref,
        ),
        scope=failed.scope,
        authority=Authority(
            principal=principal,
            delegated_by=approver,
            permissions=["collector:activate", "evidence:write"],
            policy_ref=failed.authority.policy_ref,
        ),
        policy=PolicyCheck(
            decision=PolicyDecision.ALLOW,
            reason=(
                "Named approver accepted the jurisdiction-specific test "
                "and provenance evidence."
            ),
        ),
        approval=ApprovalGate(
            required=True,
            status=ApprovalStatus.APPROVED,
            approver=approver,
            decided_at=timestamp,
            evidence_ref=approval_ref,
        ),
        work=failed.work.model_copy(update={"mutation_ref": approval_ref}),
        workflow=workflow,
        evidence=evidence,
        verification=Verification(
            status=VerificationStatus.PASSED,
            checks=checks,
            reviewer=approver,
            reviewed_at=timestamp,
        ),
        rollback=RollbackPlan(
            strategy="Disable the collector and restore the last verified dataset snapshot.",
            status=RollbackStatus.NOT_NEEDED,
            ref=f"rollback://{failed.execution_id}",
        ),
        provider_receipt_refs=[approval_ref],
    )
