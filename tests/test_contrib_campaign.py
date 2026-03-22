"""Tests for the campaign sequencer."""

from contrib_engine.schemas import Campaign, CampaignAction, CampaignPhase


class TestNextActions:
    def test_returns_lowest_priority_first(self):
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(id="low", workspace="w", phase=CampaignPhase.ENGAGE, action="low", priority=3),
                CampaignAction(id="high", workspace="w", phase=CampaignPhase.UNBLOCK, action="high", priority=0),
                CampaignAction(id="mid", workspace="w", phase=CampaignPhase.ENGAGE, action="mid", priority=1),
            ],
        )
        result = campaign.next_actions(limit=2)
        assert [a.id for a in result] == ["high", "mid"]

    def test_excludes_completed(self):
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(id="done", workspace="w", phase=CampaignPhase.UNBLOCK, action="done", completed=True),
                CampaignAction(id="todo", workspace="w", phase=CampaignPhase.ENGAGE, action="todo", priority=1),
            ],
        )
        result = campaign.next_actions()
        assert [a.id for a in result] == ["todo"]

    def test_respects_blocked_by(self):
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(id="first", workspace="w", phase=CampaignPhase.UNBLOCK, action="first", priority=0),
                CampaignAction(id="second", workspace="w", phase=CampaignPhase.UNBLOCK, action="second", priority=0, blocked_by=["first"]),
            ],
        )
        result = campaign.next_actions()
        assert [a.id for a in result] == ["first"]

    def test_unblocks_when_dependency_completed(self):
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(id="first", workspace="w", phase=CampaignPhase.UNBLOCK, action="first", completed=True),
                CampaignAction(id="second", workspace="w", phase=CampaignPhase.UNBLOCK, action="second", blocked_by=["first"]),
            ],
        )
        result = campaign.next_actions()
        assert [a.id for a in result] == ["second"]

    def test_missing_blocked_by_treated_as_unblocked(self):
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(id="orphan", workspace="w", phase=CampaignPhase.ENGAGE, action="orphan", blocked_by=["nonexistent"]),
            ],
        )
        result = campaign.next_actions()
        assert [a.id for a in result] == ["orphan"]

    def test_empty_campaign(self):
        campaign = Campaign(started="2026-03-22")
        assert campaign.next_actions() == []


class TestPhaseSummary:
    def test_counts_incomplete_by_phase(self):
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(id="a", workspace="w", phase=CampaignPhase.UNBLOCK, action="a"),
                CampaignAction(id="b", workspace="w", phase=CampaignPhase.UNBLOCK, action="b", completed=True),
                CampaignAction(id="c", workspace="w", phase=CampaignPhase.ENGAGE, action="c"),
            ],
        )
        summary = campaign.phase_summary()
        assert summary["unblock"] == 1
        assert summary["engage"] == 1
        assert "cultivate" not in summary


class TestCompleteAction:
    def test_complete_marks_done(self):
        from contrib_engine.campaign import complete_action
        campaign = Campaign(
            started="2026-03-22",
            actions=[CampaignAction(id="test", workspace="w", phase=CampaignPhase.UNBLOCK, action="test")],
        )
        assert complete_action(campaign, "test")
        assert campaign.actions[0].completed
        assert campaign.actions[0].completed_at != ""

    def test_complete_nonexistent_returns_false(self):
        from contrib_engine.campaign import complete_action
        campaign = Campaign(started="2026-03-22")
        assert not complete_action(campaign, "nonexistent")
