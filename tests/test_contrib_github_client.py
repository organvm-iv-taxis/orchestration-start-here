"""Tests for github_client with mocks."""

from unittest.mock import patch

from contrib_engine.github_client import search_issues, who_starred_my_repos


class TestWhoStarredMyRepos:
    def test_returns_list(self):
        with patch("contrib_engine.github_client._run_gh") as mock:
            mock.return_value = [{"login": "user1", "repo": "4444J99/hive"}]
            result = who_starred_my_repos()
            assert isinstance(result, list)

    def test_returns_empty_on_timeout(self):
        with patch("contrib_engine.github_client._run_gh") as mock:
            mock.return_value = None
            result = who_starred_my_repos()
            assert result == []


class TestSearchIssues:
    def test_returns_empty_on_no_results(self):
        with patch("contrib_engine.github_client._run_gh") as mock:
            mock.return_value = []
            result = search_issues("owner", "repo", ["keyword"])
            assert result == []
