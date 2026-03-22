"""PR Monitor — watches active contributions and manages lifecycle.

Polls GitHub for PR state changes, creates journal entries,
and triggers downstream actions (distribution, archival).
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from contrib_engine.github_client import get_issue_assignees, get_pr_status
from contrib_engine.schemas import (
    ContributionStatus,
    ContributionStatusIndex,
    PRState,
)

logger = logging.getLogger(__name__)

ORGAN_IV_DIR = Path.home() / "Workspace" / "organvm-iv-taxis"
DATA_DIR = Path(__file__).parent / "data"


def discover_contributions() -> list[ContributionStatus]:
    """Discover all contrib--* workspaces in ORGAN-IV."""
    contributions = []
    if not ORGAN_IV_DIR.exists():
        return contributions

    for d in ORGAN_IV_DIR.iterdir():
        if not d.is_dir() or not d.name.startswith("contrib--"):
            continue

        seed_path = d / "seed.yaml"
        if not seed_path.exists():
            continue

        with open(seed_path, encoding="utf-8") as f:
            seed = yaml.safe_load(f)

        # Try to find PR info from journal or status file
        status = ContributionStatus(
            workspace=d.name,
            target=_infer_target(seed),
        )
        contributions.append(status)

    return contributions


def _infer_target(seed: dict) -> str:
    """Infer target repo from seed.yaml produces edges."""
    for edge in seed.get("produces", []):
        if isinstance(edge, str) and edge.startswith("pr_to_"):
            parts = edge.replace("pr_to_", "").split("_", 1)
            if len(parts) == 2:
                return f"{parts[0]}/{parts[1]}"
    return ""


def check_pr_state(contribution: ContributionStatus) -> dict[str, Any]:
    """Check current PR state from GitHub. Returns dict of changes detected."""
    if not contribution.target or not contribution.pr_number:
        return {}

    owner, repo = contribution.target.split("/", 1)
    pr_data = get_pr_status(owner, repo, contribution.pr_number)
    if not pr_data:
        return {}

    changes: dict[str, Any] = {}
    new_state = PRState(pr_data.get("state", "OPEN"))

    if contribution.pr_state != new_state:
        changes["state_changed"] = {
            "from": contribution.pr_state,
            "to": new_state,
        }
        contribution.pr_state = new_state

    # Check for new comments
    comments = pr_data.get("comments", [])
    if comments:
        latest = comments[-1]
        latest_time = latest.get("createdAt", "")
        if latest_time and latest_time != contribution.last_comment:
            changes["new_comment"] = {
                "author": latest.get("author", {}).get("login", ""),
                "body": latest.get("body", "")[:200],
                "created_at": latest_time,
            }
            contribution.last_comment = latest_time

    # Check for new reviews
    reviews = pr_data.get("reviews", [])
    if reviews:
        latest_review = reviews[-1]
        review_time = latest_review.get("submittedAt", "")
        if review_time and review_time != contribution.last_review:
            changes["new_review"] = {
                "author": latest_review.get("author", {}).get("login", ""),
                "state": latest_review.get("state", ""),
                "body": latest_review.get("body", "")[:200],
            }
            contribution.last_review = review_time

    # Check CI status
    checks = pr_data.get("statusCheckRollup", [])
    if checks:
        statuses = [c.get("conclusion", c.get("status", "")) for c in checks]
        if all(s == "SUCCESS" for s in statuses if s):
            contribution.last_ci = "pass"
        elif any(s in ("FAILURE", "ERROR") for s in statuses):
            contribution.last_ci = "fail"
        else:
            contribution.last_ci = "pending"

    # Check issue assignment
    if contribution.issue_number:
        assignees = get_issue_assignees(owner, repo, contribution.issue_number)
        was_assigned = contribution.assigned
        contribution.assigned = "4444J99" in assignees
        if not was_assigned and contribution.assigned:
            changes["assigned"] = True

    return changes


def journal_changes(
    contribution: ContributionStatus,
    changes: dict[str, Any],
) -> None:
    """Write detected changes to the contribution's journal."""
    if not changes:
        return

    ws_path = ORGAN_IV_DIR / contribution.workspace
    journal_dir = ws_path / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M")
    entry_path = journal_dir / f"{date}-monitor.md"

    lines = [f"\n## Monitor — {time}\n"]

    if "state_changed" in changes:
        c = changes["state_changed"]
        lines.append(f"- PR state: {c['from']} → {c['to']}")

    if "assigned" in changes:
        lines.append("- Issue ASSIGNED to 4444J99 — CI should clear")

    if "new_comment" in changes:
        c = changes["new_comment"]
        lines.append(f"- New comment by @{c['author']}: {c['body'][:100]}...")

    if "new_review" in changes:
        c = changes["new_review"]
        lines.append(f"- New review by @{c['author']} ({c['state']}): {c['body'][:100]}...")

    lines.append("")

    with open(entry_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Journaled %d changes for %s", len(changes), contribution.workspace)


def determine_next_action(contribution: ContributionStatus) -> str:
    """Determine what should happen next for this contribution."""
    if contribution.pr_state == PRState.MERGED:
        return "celebrate_and_phase2"
    if contribution.pr_state == PRState.CLOSED:
        return "journal_and_archive"
    if not contribution.assigned and contribution.pr_number:
        return "await_assignment"
    if contribution.assigned and contribution.last_ci == "fail":
        return "diagnose_ci"
    if contribution.last_review:
        return "respond_to_review"
    if contribution.assigned and contribution.last_ci == "pass":
        return "await_merge"
    return "monitor"


def run_monitoring_cycle() -> ContributionStatusIndex:
    """Run one full monitoring cycle across all contributions."""
    contributions = discover_contributions()
    index = ContributionStatusIndex(
        generated=datetime.now().isoformat(),
        contributions=contributions,
    )

    for contrib in contributions:
        if not contrib.pr_number:
            logger.debug("Skipping %s — no PR number", contrib.workspace)
            continue

        changes = check_pr_state(contrib)
        if changes:
            journal_changes(contrib, changes)
            logger.info(
                "%s: %d changes detected",
                contrib.workspace,
                len(changes),
            )

        contrib.next_action = determine_next_action(contrib)

    # Save status
    save_status(index)
    return index


def save_status(index: ContributionStatusIndex, output_path: Path | None = None) -> Path:
    """Save contribution status to YAML."""
    path = output_path or DATA_DIR / "contribution_status.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            index.model_dump(mode="python"),
            f,
            default_flow_style=False,
            sort_keys=False,
        )
    return path


def load_status(input_path: Path | None = None) -> ContributionStatusIndex:
    """Load contribution status from YAML."""
    path = input_path or DATA_DIR / "contribution_status.yaml"
    if not path.exists():
        return ContributionStatusIndex()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return ContributionStatusIndex()
    return ContributionStatusIndex.model_validate(data)
