"""GitHub API wrapper using gh CLI subprocess.

All GitHub interaction goes through the gh CLI to stay consistent
with the workspace policy (no octokit, no direct API tokens in code).
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


def _run_gh(args: list[str], timeout: int = 30) -> dict | list | str | None:
    """Run a gh CLI command and return parsed JSON output."""
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            logger.warning("gh command failed: %s\nstderr: %s", " ".join(cmd), result.stderr)
            return None
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        logger.warning("gh command timed out: %s", " ".join(cmd))
        return None
    except json.JSONDecodeError:
        return result.stdout.strip()
    except FileNotFoundError:
        logger.error("gh CLI not found — install from https://cli.github.com/")
        return None


def get_repo_info(owner: str, repo: str) -> dict[str, Any] | None:
    """Get repository metadata."""
    result = _run_gh([
        "repo", "view", f"{owner}/{repo}",
        "--json", "name,description,stargazerCount,isArchived,hasIssuesEnabled,"
        "primaryLanguage,licenseInfo,openIssues",
    ])
    return result if isinstance(result, dict) else None


def get_repo_stargazers(owner: str, repo: str, limit: int = 100) -> list[str]:
    """Get recent stargazers of a repo."""
    result = _run_gh([
        "api", f"repos/{owner}/{repo}/stargazers",
        "--paginate", "-q", ".[].login",
        "--header", "Accept: application/vnd.github.v3.star+json",
    ])
    if isinstance(result, str):
        return result.strip().split("\n")[:limit]
    return []


def search_issues(
    owner: str,
    repo: str,
    keywords: list[str],
    state: str = "open",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search issues in a repo matching keywords."""
    query = f"repo:{owner}/{repo} state:{state} " + " OR ".join(keywords[:5])
    result = _run_gh([
        "search", "issues",
        "--json", "number,title,body,labels,assignees,comments",
        "--limit", str(limit),
        "--", query,
    ])
    if isinstance(result, list):
        return result
    return []


def get_pr_status(owner: str, repo: str, pr_number: int) -> dict[str, Any] | None:
    """Get PR state, reviews, comments, CI checks."""
    result = _run_gh([
        "pr", "view", str(pr_number),
        "--repo", f"{owner}/{repo}",
        "--json", "state,reviews,comments,labels,assignees,mergeable,statusCheckRollup",
    ])
    return result if isinstance(result, dict) else None


def get_issue_assignees(owner: str, repo: str, issue_number: int) -> list[str]:
    """Get assignees for an issue."""
    result = _run_gh([
        "issue", "view", str(issue_number),
        "--repo", f"{owner}/{repo}",
        "--json", "assignees",
    ])
    if isinstance(result, dict):
        return [a.get("login", "") for a in result.get("assignees", [])]
    return []


def fork_repo(owner: str, repo: str) -> str | None:
    """Fork a repo to the authenticated user's account. Returns fork URL."""
    result = _run_gh(["repo", "fork", f"{owner}/{repo}", "--clone=false"])
    if isinstance(result, str) and "http" in result:
        return result.strip()
    return f"https://github.com/4444J99/{repo}"


def create_repo(org: str, name: str, description: str = "", public: bool = True) -> str | None:
    """Create a new repo in an org."""
    args = ["repo", "create", f"{org}/{name}"]
    if public:
        args.append("--public")
    else:
        args.append("--private")
    if description:
        args.extend(["--description", description])
    result = _run_gh(args)
    if isinstance(result, str) and "http" in result:
        return result.strip()
    return f"https://github.com/{org}/{name}"


def who_starred_my_repos(username: str = "4444J99", limit: int = 50) -> list[dict[str, str]]:
    """Find users/orgs that recently starred repos owned by username.

    Returns list of {login, repo, starred_at}.
    """
    # gh api doesn't easily give "who starred me" — use notifications + events as proxy
    result = _run_gh([
        "api", f"users/{username}/received_events",
        "--paginate",
        "-q", '[.[] | select(.type == "WatchEvent") | {login: .actor.login, repo: .repo.name}]',
    ], timeout=15)
    if isinstance(result, list):
        return result[:limit]
    return []
