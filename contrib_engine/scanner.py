"""Signal Scanner — discovers and ranks open-source contribution targets.

Reads from application-pipeline signals (contacts, network, outreach-log)
and GitHub API to produce a ranked list of targets scored by symbiotic
potential with ORGANVM.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from contrib_engine.capabilities import CAPABILITIES, match_capabilities
from contrib_engine.github_client import get_repo_info, search_issues
from contrib_engine.schemas import ContributionTarget, RankedTargets, TargetStatus

logger = logging.getLogger(__name__)

# Default paths
APP_PIPELINE = Path.home() / "Workspace" / "4444J99" / "application-pipeline"
DATA_DIR = Path(__file__).parent / "data"


def _load_yaml(path: Path) -> dict | list | None:
    """Safely load a YAML file."""
    if not path.exists():
        logger.warning("YAML file not found: %s", path)
        return None
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _extract_contacts_with_github(
    contacts_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Extract contacts that have GitHub-related orgs or signals."""
    path = contacts_path or APP_PIPELINE / "signals" / "contacts.yaml"
    data = _load_yaml(path)
    if not data or not isinstance(data, dict):
        return []

    github_contacts = []
    for contact in data.get("contacts", []):
        org = contact.get("organization", "")
        interactions = contact.get("interactions", [])
        for interaction in interactions:
            note = interaction.get("note", "").lower()
            if any(kw in note for kw in ["github", "starred", "open-source", "repo", "contribution"]):
                github_contacts.append({
                    "name": contact.get("name", ""),
                    "organization": org,
                    "signal_type": interaction.get("type", ""),
                    "note": interaction.get("note", ""),
                    "date": interaction.get("date", ""),
                })
    return github_contacts


def _extract_outreach_targets(
    outreach_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Extract orgs from outreach log that have open-source repos."""
    path = outreach_path or APP_PIPELINE / "signals" / "outreach-log.yaml"
    data = _load_yaml(path)
    if not data or not isinstance(data, dict):
        return []

    orgs_seen: set[str] = set()
    targets = []
    for entry in data.get("entries", []):
        contact = entry.get("contact", "")
        related = entry.get("related_targets", [])
        # Extract org name from target slugs
        for target_slug in related:
            org = target_slug.split("-")[0] if "-" in target_slug else target_slug
            if org and org not in orgs_seen:
                orgs_seen.add(org)
                targets.append({
                    "org": org,
                    "contact": contact,
                    "slug": target_slug,
                })
    return targets


def score_target(
    target: ContributionTarget,
    github_info: dict[str, Any] | None = None,
    matching_issues: list[dict[str, Any]] | None = None,
) -> int:
    """Compute composite score (0-100) for a contribution target."""
    score = 0

    # Signal type (0-30)
    if target.signal_type == "inbound":
        score += 30  # They reached out to us
    elif target.signal_type == "mutual":
        score += 20  # Bidirectional interest
    else:
        score += 5  # Outbound only

    # Stars / repo health (0-20)
    if target.stars >= 10000:
        score += 20
    elif target.stars >= 5000:
        score += 15
    elif target.stars >= 1000:
        score += 10
    elif target.stars >= 100:
        score += 5

    # Domain overlap (0-25)
    overlap_score = min(len(target.domain_overlap) * 5, 25)
    score += overlap_score

    # Matching issues (0-15)
    issue_count = len(target.matching_issues)
    if issue_count >= 5:
        score += 15
    elif issue_count >= 3:
        score += 10
    elif issue_count >= 1:
        score += 5

    # Contacts / relationship (0-10)
    if len(target.contacts) >= 3:
        score += 10
    elif len(target.contacts) >= 1:
        score += 5

    return min(score, 100)


def scan(
    contacts_path: Path | None = None,
    outreach_path: Path | None = None,
    enrich_github: bool = True,
) -> RankedTargets:
    """Run the full scan pipeline.

    1. Extract signals from application pipeline
    2. Optionally enrich with GitHub API data
    3. Score and rank targets
    """
    targets: dict[str, ContributionTarget] = {}

    # Phase 1: Extract inbound GitHub signals from contacts
    github_contacts = _extract_contacts_with_github(contacts_path)
    for contact in github_contacts:
        org = contact["organization"].lower().replace(" ", "-")
        if org not in targets:
            targets[org] = ContributionTarget(
                name=org,
                github="",  # Will be enriched
                signal_type="inbound",
                contacts=[contact["name"]],
                notes=contact.get("note", ""),
            )
        else:
            if contact["name"] not in targets[org].contacts:
                targets[org].contacts.append(contact["name"])

    # Phase 2: Enrich with GitHub data
    if enrich_github:
        for name, target in targets.items():
            if not target.github:
                # Try to find the GitHub org/repo
                # For now, use name as org and look for main repo
                info = get_repo_info(name, name)
                if info:
                    target.github = f"{name}/{name}"
                    target.stars = info.get("stargazerCount", 0)

            if target.github:
                owner, repo = target.github.split("/", 1)
                # Search for issues matching ORGANVM capabilities
                all_keywords = []
                for cap in CAPABILITIES:
                    all_keywords.extend(cap.issue_keywords[:3])
                issues = search_issues(owner, repo, all_keywords[:10])
                target.matching_issues = [i.get("number", 0) for i in issues]

                # Determine domain overlap
                for issue in issues:
                    text = f"{issue.get('title', '')} {issue.get('body', '')}"
                    caps = match_capabilities(text)
                    for cap in caps:
                        if cap.id not in target.domain_overlap:
                            target.domain_overlap.append(cap.id)

    # Phase 3: Score all targets
    for target in targets.values():
        target.score = score_target(target)
        target.status = TargetStatus.RANKED

    result = RankedTargets(
        generated=datetime.now().isoformat(),
        targets=list(targets.values()),
    )

    return result


def save_targets(targets: RankedTargets, output_path: Path | None = None) -> Path:
    """Save ranked targets to YAML."""
    path = output_path or DATA_DIR / "ranked_targets.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            targets.model_dump(mode="python"),
            f,
            default_flow_style=False,
            sort_keys=False,
        )
    logger.info("Saved %d ranked targets to %s", len(targets.targets), path)
    return path


def load_targets(input_path: Path | None = None) -> RankedTargets:
    """Load ranked targets from YAML."""
    path = input_path or DATA_DIR / "ranked_targets.yaml"
    data = _load_yaml(path)
    if not data:
        return RankedTargets()
    return RankedTargets.model_validate(data)
