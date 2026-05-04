"""Per-store query functions. Each returns a list of Match dataclasses with citations."""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

HOME = Path(os.path.expanduser("~"))
MEMORY_DIR = HOME / ".claude" / "projects" / "-Users-4jp" / "memory"
PLANS_DIR = HOME / ".claude" / "plans"
LEDGER_FILE = HOME / "Workspace" / "organvm" / "orchestration-start-here" / "action_ledger" / "data" / "actions.yaml"
WORKSPACE_DIR = HOME / "Workspace"


@dataclass
class Match:
    store: str  # e.g., "action_ledger", "feedback", "project_artifact"
    citation: str  # file path + line, or PR URL, or commit hash
    excerpt: str  # short snippet of the matching content
    timestamp: datetime | None = None  # when the precedent was created/last-updated
    verb: str | None = None  # extracted verb if known
    target: str | None = None  # extracted target if known
    extras: dict = field(default_factory=dict)


def _matches_keywords(text: str, keywords: Iterable[str]) -> bool:
    """Case-insensitive substring match — all keywords must appear."""
    lowered = text.lower()
    return all(kw.lower() in lowered for kw in keywords)


def _extract_excerpt(text: str, keyword: str, context_chars: int = 120) -> str:
    idx = text.lower().find(keyword.lower())
    if idx < 0:
        return text[:context_chars].strip()
    start = max(0, idx - context_chars // 2)
    end = min(len(text), idx + context_chars // 2)
    return text[start:end].strip().replace("\n", " ")


def query_action_ledger(verb: str, target: str) -> list[Match]:
    """Read actions.yaml directly (avoids the broken pydantic-based CLI)."""
    if not LEDGER_FILE.exists():
        return []
    try:
        text = LEDGER_FILE.read_text(encoding="utf-8")
    except OSError:
        return []
    matches: list[Match] = []
    blocks = re.split(r"^---$", text, flags=re.MULTILINE)
    for block in blocks:
        if not block.strip():
            continue
        if verb.lower() not in block.lower() and target.lower() not in block.lower():
            continue
        if not _matches_keywords(block, [verb, target] if verb and target else [verb or target]):
            continue
        ts_match = re.search(r"timestamp:\s*['\"]?([0-9T:\-\.+]+)['\"]?", block)
        ts = None
        if ts_match:
            try:
                ts = datetime.fromisoformat(ts_match.group(1).replace("Z", "+00:00"))
            except ValueError:
                pass
        matches.append(Match(
            store="action_ledger",
            citation=f"{LEDGER_FILE}",
            excerpt=block.strip()[:200],
            timestamp=ts,
            verb=verb,
            target=target,
        ))
    return matches


def _grep_memory_files(pattern: str, keywords: list[str]) -> list[Match]:
    matches: list[Match] = []
    if not MEMORY_DIR.exists():
        return matches
    for path in MEMORY_DIR.glob(pattern):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not _matches_keywords(text, keywords):
            continue
        store_kind = path.stem.split("_")[0]
        excerpt = _extract_excerpt(text, keywords[0])
        ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        matches.append(Match(
            store=store_kind,
            citation=str(path),
            excerpt=excerpt,
            timestamp=ts,
        ))
    return matches


def query_feedback_memories(keywords: list[str]) -> list[Match]:
    return _grep_memory_files("feedback_*.md", keywords)


def query_project_artifacts(keywords: list[str]) -> list[Match]:
    return _grep_memory_files("project_artifact_*.md", keywords)


def query_project_sessions(keywords: list[str]) -> list[Match]:
    return _grep_memory_files("project_session_*.md", keywords)


def query_originating_plans(keywords: list[str], days: int | None = None) -> list[Match]:
    matches: list[Match] = []
    if not PLANS_DIR.exists():
        return matches
    cutoff = datetime.now(timezone.utc) - timedelta(days=days) if days else None
    for path in PLANS_DIR.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not _matches_keywords(text, keywords):
            continue
        ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if cutoff and ts < cutoff:
            continue
        matches.append(Match(
            store="plan",
            citation=str(path),
            excerpt=_extract_excerpt(text, keywords[0]),
            timestamp=ts,
        ))
    return matches


def query_git_log(verb: str, target: str, repo_paths: list[Path] | None = None,
                  days: int | None = 30) -> list[Match]:
    """Search git commit messages across workspace repos."""
    matches: list[Match] = []
    if repo_paths is None:
        repo_paths = [p for p in WORKSPACE_DIR.glob("organvm/*") if (p / ".git").is_dir()]
    since_arg = []
    if days:
        since_arg = [f"--since={days}.days.ago"]
    pattern = f"{verb}.*{target}|{target}.*{verb}" if verb and target else verb or target
    for repo in repo_paths:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo), "log", "--all", "--format=%H|%aI|%s", *since_arg, f"--grep={pattern}", "-E", "-i"],
                capture_output=True, text=True, timeout=10,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            parts = line.split("|", 2)
            if len(parts) != 3:
                continue
            sha, ts_str, subject = parts
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                ts = None
            matches.append(Match(
                store="git",
                citation=f"{repo.name}@{sha[:8]}",
                excerpt=subject,
                timestamp=ts,
                extras={"repo": repo.name, "sha": sha},
            ))
    return matches
