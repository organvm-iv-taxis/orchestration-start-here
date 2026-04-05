"""Tests for the contribution monitor."""

from contrib_engine.monitor import _infer_target, determine_next_action
from contrib_engine.schemas import ContributionStatus, PRState


class TestInferTarget:
    def test_infers_from_produces(self):
        seed = {"produces": ["pr_to_adenhq_hive", "theory_extraction"]}
        assert _infer_target(seed) == "adenhq/hive"

    def test_empty_produces(self):
        seed = {"produces": []}
        assert _infer_target(seed) == ""

    def test_no_pr_edge(self):
        seed = {"produces": ["theory_extraction"]}
        assert _infer_target(seed) == ""


class TestDetermineNextAction:
    def test_merged(self):
        c = ContributionStatus(workspace="w", target="t", pr_state=PRState.MERGED)
        assert determine_next_action(c) == "celebrate_and_phase2"

    def test_closed(self):
        c = ContributionStatus(workspace="w", target="t", pr_state=PRState.CLOSED)
        assert determine_next_action(c) == "journal_and_archive"

    def test_awaiting_assignment(self):
        c = ContributionStatus(
            workspace="w", target="t", pr_number=123, pr_state=PRState.OPEN, assigned=False
        )
        assert determine_next_action(c) == "await_assignment"

    def test_ci_failure(self):
        c = ContributionStatus(
            workspace="w", target="t", pr_number=123,
            pr_state=PRState.OPEN, assigned=True, last_ci="fail",
        )
        assert determine_next_action(c) == "diagnose_ci"

    def test_review_pending(self):
        c = ContributionStatus(
            workspace="w", target="t", pr_number=123,
            pr_state=PRState.OPEN, assigned=True, last_ci="pass",
            last_review="2026-03-22T00:00:00Z",
        )
        assert determine_next_action(c) == "respond_to_review"

    def test_awaiting_merge(self):
        c = ContributionStatus(
            workspace="w", target="t", pr_number=123,
            pr_state=PRState.OPEN, assigned=True, last_ci="pass",
        )
        assert determine_next_action(c) == "await_merge"


class TestInferTargetDictFormat:
    def test_infers_from_dict_produces(self):
        seed = {
            "produces": [
                {"type": "contribution", "description": "Skills", "consumers": ["anthropics/skills"]}
            ]
        }
        assert _infer_target(seed) == "anthropics/skills"

    def test_infers_from_mixed_produces(self):
        seed = {
            "produces": [
                "theory_extraction",
                {"type": "contribution", "consumers": ["dbt-labs/dbt-mcp"]},
            ]
        }
        assert _infer_target(seed) == "dbt-labs/dbt-mcp"

    def test_dict_without_consumers(self):
        seed = {
            "produces": [
                {"type": "artifact", "description": "something"}
            ]
        }
        assert _infer_target(seed) == ""
