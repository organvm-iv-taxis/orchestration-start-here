"""Tests for the contribution scanner."""


import yaml

from contrib_engine.capabilities import CAPABILITIES, match_capabilities
from contrib_engine.scanner import _extract_contacts_with_github, scan, score_target
from contrib_engine.schemas import ContributionTarget, TargetStatus


class TestCapabilities:
    def test_capabilities_exist(self):
        assert len(CAPABILITIES) >= 8

    def test_match_versioning(self):
        matches = match_capabilities("improve versioning and reproducibility for agents")
        ids = [m.id for m in matches]
        assert "governance-lifecycle" in ids

    def test_match_testing(self):
        matches = match_capabilities("enable parallel test execution with pytest-xdist")
        ids = [m.id for m in matches]
        assert "testing-infrastructure" in ids

    def test_match_empty(self):
        matches = match_capabilities("buy groceries")
        assert len(matches) == 0

    def test_match_multiple(self):
        matches = match_capabilities("multi-agent orchestration with versioning and testing")
        assert len(matches) >= 3


class TestScoring:
    def test_inbound_scores_highest(self):
        inbound = ContributionTarget(
            name="test", github="test/test", signal_type="inbound",
            stars=10000, domain_overlap=["a", "b", "c"], matching_issues=[1, 2, 3],
            contacts=["Alice", "Bob", "Charlie"],
        )
        outbound = ContributionTarget(
            name="test2", github="test2/test2", signal_type="outbound",
            stars=10000, domain_overlap=["a", "b", "c"], matching_issues=[1, 2, 3],
            contacts=["Alice", "Bob", "Charlie"],
        )
        assert score_target(inbound) > score_target(outbound)

    def test_more_stars_scores_higher(self):
        big = ContributionTarget(name="big", github="b/b", stars=10000)
        small = ContributionTarget(name="small", github="s/s", stars=50)
        assert score_target(big) > score_target(small)

    def test_domain_overlap_matters(self):
        overlap = ContributionTarget(
            name="o", github="o/o",
            domain_overlap=["a", "b", "c", "d", "e"],
        )
        none = ContributionTarget(name="n", github="n/n", domain_overlap=[])
        assert score_target(overlap) > score_target(none)

    def test_score_capped_at_100(self):
        maxed = ContributionTarget(
            name="max", github="m/m", signal_type="inbound",
            stars=100000, domain_overlap=["a"] * 10,
            matching_issues=list(range(20)), contacts=["a"] * 5,
        )
        assert score_target(maxed) <= 100


class TestContactExtraction:
    def test_extract_github_contacts(self, tmp_path):
        contacts_file = tmp_path / "contacts.yaml"
        contacts_file.write_text(yaml.safe_dump({
            "contacts": [
                {
                    "name": "Vincent Jiang",
                    "organization": "AdenHQ",
                    "interactions": [
                        {"type": "email", "note": "Starred GitHub profile, open-source contribution request", "date": "2026-03-13"},
                    ],
                },
                {
                    "name": "John Doe",
                    "organization": "SomeCorp",
                    "interactions": [
                        {"type": "email", "note": "General inquiry about pricing", "date": "2026-03-14"},
                    ],
                },
            ]
        }), encoding="utf-8")

        result = _extract_contacts_with_github(contacts_file)
        assert len(result) == 1
        assert result[0]["name"] == "Vincent Jiang"
        assert result[0]["organization"] == "AdenHQ"

    def test_extract_empty_contacts(self, tmp_path):
        contacts_file = tmp_path / "contacts.yaml"
        contacts_file.write_text(yaml.safe_dump({"contacts": []}), encoding="utf-8")
        result = _extract_contacts_with_github(contacts_file)
        assert result == []


class TestScanOffline:
    def test_scan_offline(self, tmp_path):
        # Create minimal contacts file
        contacts_file = tmp_path / "contacts.yaml"
        contacts_file.write_text(yaml.safe_dump({
            "contacts": [
                {
                    "name": "Alice",
                    "organization": "TestOrg",
                    "interactions": [
                        {"type": "email", "note": "Starred our GitHub repos", "date": "2026-03-21"},
                    ],
                },
            ]
        }), encoding="utf-8")

        outreach_file = tmp_path / "outreach.yaml"
        outreach_file.write_text(yaml.safe_dump({"entries": []}), encoding="utf-8")

        result = scan(
            contacts_path=contacts_file,
            outreach_path=outreach_file,
            enrich_github=False,
        )
        assert len(result.targets) == 1
        assert result.targets[0].signal_type == "inbound"
        assert result.targets[0].status == TargetStatus.RANKED
