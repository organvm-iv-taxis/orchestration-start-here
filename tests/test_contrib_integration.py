"""Cross-module integration tests."""

from contrib_engine.schemas import (
    Campaign,
    CampaignAction,
    CampaignPhase,
    OutreachIndex,
    TargetRelationship,
)


class TestCampaignMonitorIntegration:
    def test_campaign_next_action_reflects_pr_state(self):
        """Campaign actions should be ordered by workspace PR state."""
        campaign = Campaign(
            started="2026-03-22",
            targets=["contrib--a", "contrib--b"],
            actions=[
                CampaignAction(
                    id="a-unblock", workspace="contrib--a",
                    phase=CampaignPhase.UNBLOCK, action="Fix CLA", priority=0,
                ),
                CampaignAction(
                    id="b-engage", workspace="contrib--b",
                    phase=CampaignPhase.ENGAGE, action="Bump PR", priority=2,
                ),
            ],
        )
        next_actions = campaign.next_actions()
        assert next_actions[0].id == "a-unblock"


class TestCampaignOutreachInteraction:
    def test_outreach_events_inform_campaign_state(self):
        """Outreach events and campaign actions operate on the same workspaces."""
        campaign = Campaign(
            started="2026-03-22",
            actions=[
                CampaignAction(
                    id="join-discord", workspace="contrib--adenhq-hive",
                    phase=CampaignPhase.ENGAGE, action="Join Discord",
                ),
            ],
        )
        outreach = OutreachIndex(
            relationships=[
                TargetRelationship(workspace="contrib--adenhq-hive", target="adenhq/hive"),
            ],
        )
        assert campaign.actions[0].workspace == outreach.relationships[0].workspace
