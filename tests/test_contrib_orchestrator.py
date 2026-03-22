"""Tests for the contribution orchestrator."""

from pathlib import Path

from contrib_engine.orchestrator import workspace_name, _write_seed_yaml, _write_claude_md
from contrib_engine.schemas import ContributionTarget


def _make_target() -> ContributionTarget:
    return ContributionTarget(
        name="adenhq-hive",
        github="adenhq/hive",
        score=92,
        signal_type="inbound",
        domain_overlap=["governance-lifecycle", "testing-infrastructure"],
        contacts=["Vincent Jiang"],
    )


class TestWorkspaceName:
    def test_generates_kebab_name(self):
        target = _make_target()
        assert workspace_name(target) == "contrib--adenhq-hive"

    def test_handles_uppercase(self):
        target = ContributionTarget(name="Test", github="MyOrg/MyRepo")
        assert workspace_name(target) == "contrib--myorg-myrepo"


class TestSeedYaml:
    def test_writes_valid_seed(self, tmp_path):
        target = _make_target()
        _write_seed_yaml(tmp_path, target)
        seed_path = tmp_path / "seed.yaml"
        assert seed_path.exists()
        import yaml
        with open(seed_path) as f:
            seed = yaml.safe_load(f)
        assert seed["organ"] == "IV"
        assert seed["tier"] == "contrib"
        assert seed["promotion_status"] == "LOCAL"
        assert "pr_to_adenhq_hive" in seed["produces"]
        assert "agentic_titan_patterns" in seed["consumes"]


class TestClaudeMd:
    def test_writes_claude_md(self, tmp_path):
        target = _make_target()
        _write_claude_md(tmp_path, target)
        claude_path = tmp_path / "CLAUDE.md"
        assert claude_path.exists()
        content = claude_path.read_text()
        assert "adenhq/hive" in content
        assert "ORGAN-IV" in content
        assert "repo/" in content
