"""Absorption Protocol — detect expansive questions from external conversations.

Scans inbound comments across tracked relationships for questions that:
1. Contain assumptions we don't share (assumption divergence)
2. Point at unnamed patterns in our architecture
3. Reveal independent convergence with our design choices

Flagged items enter the formalization pipeline: detect → assess → formalize → deposit.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from contrib_engine.github_client import _run_gh
from contrib_engine.schemas import (
    AbsorptionItem,
    AbsorptionIndex,
    AbsorptionStatus,
    AbsorptionTrigger,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"

# --- Detection heuristics ---

EXPANSION_PATTERNS: list[tuple[str, AbsorptionTrigger, str]] = [
    # (regex, trigger type, evidence template)
    (
        r"how do you (?:handle|deal with|manage|approach)",
        AbsorptionTrigger.UNNAMED_PATTERN,
        "Asks about handling strategy — may point at unnamed pattern",
    ),
    (
        r"what happens (?:when|if)",
        AbsorptionTrigger.UNNAMED_PATTERN,
        "Probes edge case / failure mode — may expose undocumented behavior",
    ),
    (
        r"we (?:ended up|built|did|use|have|went with|opted for|chose)",
        AbsorptionTrigger.INDEPENDENT_CONVERGENCE,
        "Describes their own implementation — potential convergence signal",
    ),
    (
        r"(?:does|would) .+ (?:win|override|take precedence|beat)",
        AbsorptionTrigger.ASSUMPTION_DIVERGENCE,
        "Assumes conflict resolution hierarchy — we may resolve differently",
    ),
    (
        r"isn't that (?:just|basically|essentially)",
        AbsorptionTrigger.ASSUMPTION_DIVERGENCE,
        "Equates our approach with a known pattern — we may differ",
    ),
    (
        r"(?:most|other|typical) (?:\w+ )?(?:systems|frameworks|tools|approaches)",
        AbsorptionTrigger.ASSUMPTION_DIVERGENCE,
        "References conventional approach — our divergence may be the insight",
    ),
    (
        r"(?:the (?:hard|tricky|interesting) part|the real challenge)",
        AbsorptionTrigger.UNNAMED_PATTERN,
        "Identifies a hard subproblem — may point at a pattern worth naming",
    ),
    (
        r"(?:instead of|rather than|as opposed to)",
        AbsorptionTrigger.ASSUMPTION_DIVERGENCE,
        "Contrasts approaches — divergence point worth examining",
    ),
]

REDUCTION_PATTERNS: list[str] = [
    r"what version",
    r"can you add",
    r"this (?:doesn't work|is broken|fails)",
    r"when will",
    r"is there a (?:plan|timeline|eta)",
    r"how do i install",
    r"what (?:license|language)",
]

# Minimum quality thresholds for questioner
MIN_COMMENT_LENGTH = 80  # Short comments rarely contain deep questions


def detect_triggers(text: str) -> list[tuple[AbsorptionTrigger, str]]:
    """Run expansion heuristics against a comment body.

    Returns list of (trigger_type, evidence) for all matches.
    Returns empty list if text matches reduction patterns or is too short.
    """
    if len(text) < MIN_COMMENT_LENGTH:
        return []

    # Check reduction patterns first — early exit
    for pattern in REDUCTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return []

    triggers = []
    for pattern, trigger_type, evidence in EXPANSION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            triggers.append((trigger_type, evidence))

    return triggers


def fetch_inbound_comments(
    owner: str,
    repo: str,
    issue_number: int,
    since: str = "",
    our_username: str = "4444J99",
) -> list[dict[str, Any]]:
    """Fetch comments on an issue/PR from external users (not us).

    Args:
        owner: Repo owner.
        repo: Repo name.
        issue_number: Issue or PR number.
        since: ISO date string — only return comments after this date.
        our_username: Our GitHub username to exclude.

    Returns:
        List of {user, body, created_at, url} dicts.
    """
    result = _run_gh([
        "api", f"repos/{owner}/{repo}/issues/{issue_number}/comments",
        "-q", f'[.[] | select(.user.login != "{our_username}") '
              f'| {{user: .user.login, body: .body, '
              f'created_at: .created_at, '
              f'url: .html_url}}]',
    ], timeout=15)

    if not isinstance(result, list):
        return []

    if since:
        result = [c for c in result if c.get("created_at", "") > since]

    return result


def scan_conversations(
    conversations: list[dict[str, Any]] | None = None,
    since: str = "",
) -> list[AbsorptionItem]:
    """Scan tracked conversations for expansion-worthy questions.

    Args:
        conversations: List of {owner, repo, issue_number} dicts.
            If None, reads from outreach.yaml to find all tracked issues/PRs.
        since: Only scan comments after this ISO date.

    Returns:
        List of newly detected AbsorptionItems.
    """
    if conversations is None:
        conversations = _load_tracked_conversations()

    existing = load_absorption()
    existing_urls = {item.source_url for item in existing.items}

    detected: list[AbsorptionItem] = []

    for conv in conversations:
        owner = conv["owner"]
        repo = conv["repo"]
        issue_number = conv["issue_number"]
        workspace = conv.get("workspace", f"contrib--{owner}-{repo}")

        comments = fetch_inbound_comments(owner, repo, issue_number, since=since)

        for comment in comments:
            url = comment.get("url", "")
            if url in existing_urls:
                continue  # Already tracked

            triggers = detect_triggers(comment.get("body", ""))
            if not triggers:
                continue

            item = AbsorptionItem(
                id=f"abs-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(detected)}",
                workspace=workspace,
                source_url=url,
                questioner=comment.get("user", ""),
                question_text=comment.get("body", "")[:500],
                detected_at=datetime.now().isoformat(),
                triggers=[t for t, _ in triggers],
                trigger_evidence="; ".join(e for _, e in triggers),
                status=AbsorptionStatus.DETECTED,
            )
            detected.append(item)
            logger.info(
                "Detected absorption candidate from @%s: %d triggers — %s",
                item.questioner,
                len(triggers),
                item.trigger_evidence,
            )

    return detected


def _load_tracked_conversations() -> list[dict[str, Any]]:
    """Load tracked conversations from outreach.yaml.

    Extracts GitHub issue/PR URLs from outreach events and returns
    them as {owner, repo, issue_number, workspace} dicts.
    """
    outreach_path = DATA_DIR / "outreach.yaml"
    if not outreach_path.exists():
        return []

    with open(outreach_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or not isinstance(data, dict):
        return []

    conversations = []
    seen = set()

    for rel in data.get("relationships", []):
        target = rel.get("target", "")
        workspace = rel.get("workspace", "")
        if not target or "/" not in target:
            continue

        owner, repo = target.split("/", 1)

        for event in rel.get("outreach_events", []):
            url = event.get("url", "")
            # Extract issue/PR numbers from URLs
            for pattern in [
                rf"github\.com/{re.escape(owner)}/{re.escape(repo)}/(?:pull|issues)/(\d+)",
            ]:
                match = re.search(pattern, url)
                if match:
                    issue_number = int(match.group(1))
                    key = (owner, repo, issue_number)
                    if key not in seen:
                        seen.add(key)
                        conversations.append({
                            "owner": owner,
                            "repo": repo,
                            "issue_number": issue_number,
                            "workspace": workspace,
                        })

    return conversations


def run_absorption_scan(since: str = "") -> AbsorptionIndex:
    """Run a full absorption scan across all tracked conversations.

    Args:
        since: Only scan comments after this ISO date.

    Returns:
        Updated AbsorptionIndex with newly detected items appended.
    """
    index = load_absorption()
    new_items = scan_conversations(since=since)

    if new_items:
        index.items.extend(new_items)
        save_absorption(index)
        logger.info("Absorption scan: %d new items detected", len(new_items))
    else:
        logger.info("Absorption scan: no new items detected")

    return index


def save_absorption(index: AbsorptionIndex, output_path: Path | None = None) -> Path:
    """Save absorption state to YAML."""
    path = output_path or DATA_DIR / "absorption.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            index.model_dump(mode="json"),
            f,
            default_flow_style=False,
            sort_keys=False,
        )
    return path


def load_absorption(input_path: Path | None = None) -> AbsorptionIndex:
    """Load absorption state from YAML."""
    path = input_path or DATA_DIR / "absorption.yaml"
    if not path.exists():
        return AbsorptionIndex()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return AbsorptionIndex()
    return AbsorptionIndex.model_validate(data)
