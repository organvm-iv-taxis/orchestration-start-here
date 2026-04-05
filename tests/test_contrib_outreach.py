"""Tests for the outreach tracker."""

from contrib_engine.schemas import (
    OutreachChannel,
    OutreachDirection,
    OutreachEvent,
    OutreachIndex,
    TargetRelationship,
)


class TestLogEvent:
    def test_logs_event_to_existing_relationship(self):
        from contrib_engine.outreach import log_event
        index = OutreachIndex(
            generated="2026-03-22",
            relationships=[TargetRelationship(workspace="contrib--adenhq-hive", target="adenhq/hive")],
        )
        log_event(index, "contrib--adenhq-hive", "github_pr", "Submitted PR #6707")
        assert len(index.relationships[0].outreach_events) == 1
        assert index.relationships[0].outreach_events[0].channel == OutreachChannel.GITHUB_PR

    def test_logs_event_creates_relationship_if_missing(self):
        from contrib_engine.outreach import log_event
        index = OutreachIndex(generated="2026-03-22")
        log_event(index, "contrib--new", "discord", "Joined community")
        assert len(index.relationships) == 1
        assert index.relationships[0].workspace == "contrib--new"

    def test_multiple_events(self):
        from contrib_engine.outreach import log_event
        index = OutreachIndex(
            generated="2026-03-22",
            relationships=[TargetRelationship(workspace="w", target="t")],
        )
        log_event(index, "w", "github_pr", "PR submitted")
        log_event(index, "w", "discord", "Joined server")
        assert len(index.relationships[0].outreach_events) == 2


class TestRelationshipScore:
    def test_score_increases_with_events(self):
        from contrib_engine.outreach import compute_relationship_score
        rel = TargetRelationship(
            workspace="w", target="t",
            outreach_events=[
                OutreachEvent(channel=OutreachChannel.GITHUB_PR, date="2026-03-22", direction=OutreachDirection.OUTBOUND, summary="PR"),
                OutreachEvent(channel=OutreachChannel.DISCORD, date="2026-03-22", direction=OutreachDirection.OUTBOUND, summary="Joined"),
            ],
        )
        score = compute_relationship_score(rel)
        assert score > 0

    def test_score_zero_with_no_events(self):
        from contrib_engine.outreach import compute_relationship_score
        rel = TargetRelationship(workspace="w", target="t")
        assert compute_relationship_score(rel) == 0


class TestPersistence:
    def test_save_and_load_roundtrip(self, tmp_path):
        from contrib_engine.outreach import load_outreach, save_outreach
        index = OutreachIndex(
            generated="2026-03-22",
            relationships=[TargetRelationship(workspace="w", target="t", issue_claimed=True)],
        )
        path = save_outreach(index, tmp_path / "outreach.yaml")
        loaded = load_outreach(path)
        assert len(loaded.relationships) == 1
        assert loaded.relationships[0].issue_claimed is True
