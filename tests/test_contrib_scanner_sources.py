"""Tests for expanded scanner data sources."""

from unittest.mock import patch

from contrib_engine.scanner import (
    _extract_dependency_signals,
    _extract_fork_signals,
    _extract_pr_history,
    _extract_star_signals,
)


class TestStarSignals:
    def test_extracts_stargazers(self):
        with patch("contrib_engine.scanner.who_starred_my_repos") as mock:
            mock.return_value = [{"login": "user1", "repo": "4444J99/hive"}]
            result = _extract_star_signals()
            assert len(result) == 1
            assert result[0]["login"] == "user1"

    def test_empty_on_no_stars(self):
        with patch("contrib_engine.scanner.who_starred_my_repos") as mock:
            mock.return_value = []
            result = _extract_star_signals()
            assert result == []


class TestForkSignals:
    def test_extracts_forks(self):
        with patch("contrib_engine.scanner.list_user_forks") as mock:
            mock.return_value = [
                {"name": "hive", "parent": {"owner": "adenhq", "name": "hive"}},
                {"name": "langgraph", "parent": {"owner": "langchain-ai", "name": "langgraph"}},
            ]
            result = _extract_fork_signals()
            assert len(result) == 2
            assert result[0]["github"] == "adenhq/hive"

    def test_empty_on_no_forks(self):
        with patch("contrib_engine.scanner.list_user_forks") as mock:
            mock.return_value = []
            result = _extract_fork_signals()
            assert result == []


class TestPRHistory:
    def test_extracts_from_journals(self, tmp_path):
        journal_dir = tmp_path / "contrib--test" / "journal"
        journal_dir.mkdir(parents=True)
        (journal_dir / "session.md").write_text("- **PR:** PR #123\n- **Repo:** owner/repo")
        result = _extract_pr_history(tmp_path)
        assert len(result) == 1
        assert result[0]["workspace"] == "contrib--test"
        assert 123 in result[0]["pr_numbers"]

    def test_empty_on_no_journals(self, tmp_path):
        result = _extract_pr_history(tmp_path)
        assert result == []


class TestDependencySignals:
    def test_extracts_from_pyproject(self, tmp_path):
        proj = tmp_path / "repo"
        proj.mkdir()
        toml = proj / "pyproject.toml"
        toml.write_text('[project]\nname = "test"\ndependencies = [\n    "pydantic>=2.0",\n    "fastapi",\n]\n')
        result = _extract_dependency_signals(tmp_path)
        assert len(result) == 2
        packages = [r["package"] for r in result]
        assert "pydantic" in packages
        assert "fastapi" in packages

    def test_empty_on_no_projects(self, tmp_path):
        result = _extract_dependency_signals(tmp_path)
        assert result == []
