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
    AbsorptionIndex,
    AbsorptionItem,
    AbsorptionStatus,
    AbsorptionTrigger,
    BackflowItem,
    BackflowStatus,
    BackflowType,
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

    # Also include explicitly tracked conversations
    for conv in load_tracked_conversations_config():
        key = (conv["owner"], conv["repo"], conv["issue_number"])
        if key not in seen:
            seen.add(key)
            conversations.append(conv)

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


# --- Tracked conversations (beyond outreach URLs) ---

TRACKED_CONVERSATIONS_PATH = DATA_DIR / "tracked_conversations.yaml"


def load_tracked_conversations_config() -> list[dict[str, Any]]:
    """Load explicitly tracked conversations (issues, discussions, etc.)."""
    if not TRACKED_CONVERSATIONS_PATH.exists():
        return []
    with open(TRACKED_CONVERSATIONS_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, list) else []


def save_tracked_conversations_config(conversations: list[dict[str, Any]]) -> None:
    """Save tracked conversations config."""
    TRACKED_CONVERSATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKED_CONVERSATIONS_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(conversations, f, default_flow_style=False, sort_keys=False)


def add_tracked_conversation(
    owner: str, repo: str, issue_number: int, workspace: str = "", label: str = "",
) -> None:
    """Add a conversation to the tracked list."""
    conversations = load_tracked_conversations_config()
    key = f"{owner}/{repo}#{issue_number}"
    for c in conversations:
        if f"{c['owner']}/{c['repo']}#{c['issue_number']}" == key:
            return  # Already tracked
    conversations.append({
        "owner": owner,
        "repo": repo,
        "issue_number": issue_number,
        "workspace": workspace or f"{owner}-{repo}",
        "label": label,
    })
    save_tracked_conversations_config(conversations)
    logger.info("Now tracking conversation: %s", key)


# --- Formalization ---

ORGAN_MAP: dict[str, str] = {
    "theory": "I",
    "formal": "I",
    "pattern": "I",
    "mathematical": "I",
    "generative": "II",
    "diagram": "II",
    "visual": "II",
    "code": "III",
    "implementation": "III",
    "narrative": "V",
    "essay": "V",
    "community": "VI",
    "distribution": "VII",
}


def infer_organ(item: AbsorptionItem) -> str:
    """Infer target organ from triggers and question content.

    Theory/pattern questions → ORGAN-I
    Implementation questions → ORGAN-III
    Most absorption items are theory-level → default to I.
    """
    text = (item.question_text + " " + item.trigger_evidence).lower()
    for keyword, organ in ORGAN_MAP.items():
        if keyword in text:
            return organ
    # Default: unnamed patterns and assumption divergence are theory-level
    return "I"


def generate_formalization_prompt(item: AbsorptionItem) -> str:
    """Generate a structured prompt for formalizing an absorbed question.

    Returns a prompt that can be passed to an LLM agent to produce
    the theory note artifact.
    """
    triggers_str = ", ".join(t.value for t in item.triggers)
    organ = infer_organ(item)

    return f"""## Absorption Protocol — Formalization Task

**Source:** {item.source_url}
**Questioner:** @{item.questioner}
**Workspace:** {item.workspace}
**Triggers:** {triggers_str}
**Evidence:** {item.trigger_evidence}
**Target Organ:** {organ}

### The Question

{item.question_text}

### Your Task

This question triggered the Absorption Protocol because it {_explain_triggers(item.triggers)}.

Write a theory note (markdown) that:

1. **Names the pattern** the question exposed — give it a clear, reusable name
2. **States formal properties** — what are the invariants, guarantees, or constraints?
3. **Distinguishes from similar patterns** — what is this NOT? (table format)
4. **Identifies biological/mathematical analogues** if applicable
5. **Notes independent convergence** if the questioner described their own implementation
6. **Places in relationship to sibling patterns** in the ORGANVM theory corpus

### Output Format

Save the theory note to:
`organvm-{_organ_name(organ)}/my-knowledge-base/intake/canonical/contributions/<pattern-name-kebab>.md`

Then return the pattern name and artifact path for backflow registration.
"""


def _explain_triggers(triggers: list[AbsorptionTrigger]) -> str:
    """Human-readable explanation of why triggers fired."""
    parts = []
    if AbsorptionTrigger.ASSUMPTION_DIVERGENCE in triggers:
        parts.append("contains an assumption we don't share")
    if AbsorptionTrigger.UNNAMED_PATTERN in triggers:
        parts.append("points at something we haven't named")
    if AbsorptionTrigger.INDEPENDENT_CONVERGENCE in triggers:
        parts.append("reveals independent convergence with our design")
    return ", ".join(parts) if parts else "matched expansion heuristics"


def _organ_name(organ: str) -> str:
    """Map organ number to directory name component."""
    names = {
        "I": "i-theoria",
        "II": "ii-poiesis",
        "III": "iii-ergon",
        "IV": "iv-taxis",
        "V": "v-logos",
        "VI": "vi-koinonia",
        "VII": "vii-kerygma",
    }
    return names.get(organ, "i-theoria")


def mark_formalized(
    index: AbsorptionIndex,
    item_id: str,
    pattern_name: str,
    organ: str = "",
) -> AbsorptionItem | None:
    """Mark an absorption item as formalized.

    Args:
        index: The absorption index.
        item_id: ID of the item to mark.
        pattern_name: Name of the pattern that was formalized.
        organ: Target organ (inferred if empty).

    Returns:
        The updated item, or None if not found.
    """
    for item in index.items:
        if item.id == item_id:
            old_status = item.status
            item.status = AbsorptionStatus.FORMALIZED
            item.pattern_name = pattern_name
            item.organ = organ or infer_organ(item)
            try:
                from action_ledger.emissions import emit_state_change
                emit_state_change(
                    subsystem="contrib_engine",
                    verb="absorption_advanced",
                    target=item_id,
                    from_state=old_status.value,
                    to_state="formalized",
                    params={"pattern": pattern_name},
                )
            except Exception:
                logger.debug("Emission failed for absorption %s", item_id)
            return item
    return None


def deposit_to_backflow(
    item: AbsorptionItem,
    artifact_path: str,
) -> BackflowItem:
    """Create a backflow item from a formalized absorption item.

    Args:
        item: The formalized absorption item.
        artifact_path: Path to the theory note artifact.

    Returns:
        The created BackflowItem (caller must add to BackflowIndex and save).
    """
    if item.status != AbsorptionStatus.FORMALIZED:
        raise ValueError(f"Item {item.id} is not formalized (status: {item.status})")

    backflow = BackflowItem(
        workspace=item.workspace,
        organ=item.organ or infer_organ(item),
        backflow_type=BackflowType.THEORY,
        title=item.pattern_name,
        description=f"Absorbed from @{item.questioner}'s question: {item.question_text[:100]}",
        status=BackflowStatus.DEPOSITED,
        artifact_path=artifact_path,
        deposited_at=datetime.now().strftime("%Y-%m-%d"),
    )

    # Update absorption item
    item.status = AbsorptionStatus.DEPOSITED
    item.backflow_ref = f"backflow:{item.organ}:{item.pattern_name}"

    try:
        from action_ledger.emissions import emit_state_change
        emit_state_change(
            subsystem="contrib_engine",
            verb="absorption_deposited",
            target=item.id,
            from_state="formalized",
            to_state="deposited",
            params={"organ": item.organ or "unknown"},
            produced=[{"type": "backflow", "ref": item.backflow_ref}],
        )
    except Exception:
        logger.debug("Emission failed for deposit %s", item.id)

    return backflow


# --- Autonomous formalization ---

ORGAN_DIRS = Path.home() / "Workspace"
CONTRIBUTIONS_SUBDIR = "docs/contributions"
ORGAN_DIR_MAP = {
    "I": "organvm-i-theoria/my-knowledge-base",
    "II": "organvm-ii-poiesis",
    "III": "organvm-iii-ergon",
    "V": "organvm-v-logos",
    "VI": "organvm-vi-koinonia",
    "VII": "organvm-vii-kerygma",
}


def _slugify(text: str) -> str:
    """Convert a pattern name to a kebab-case filename slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60]  # Keep filenames reasonable


def auto_formalize(item: AbsorptionItem) -> str | None:
    """Automatically formalize a detected absorption item into a theory note.

    Generates a structured markdown artifact from the question's triggers,
    evidence, and context. This is the autonomous formalization — no human
    or LLM API needed for the structural skeleton.

    Returns:
        Artifact path relative to workspace root, or None if formalization
        was skipped (e.g., already formalized, or insufficient signal).
    """
    if item.status not in (AbsorptionStatus.DETECTED, AbsorptionStatus.ASSESSED):
        return None

    # Determine pattern name from the question
    pattern_name = _extract_pattern_name(item)
    if not pattern_name:
        return None

    organ = infer_organ(item)
    organ_dir = ORGAN_DIR_MAP.get(organ)
    if not organ_dir:
        return None

    slug = _slugify(pattern_name)
    artifact_dir = ORGAN_DIRS / organ_dir / CONTRIBUTIONS_SUBDIR
    artifact_path = artifact_dir / f"{slug}.md"

    # Don't overwrite existing formalizations
    if artifact_path.exists():
        logger.info("Artifact already exists: %s", artifact_path)
        item.status = AbsorptionStatus.FORMALIZED
        item.pattern_name = pattern_name
        item.organ = organ
        return str(artifact_path.relative_to(ORGAN_DIRS))

    # Generate the theory note
    content = _generate_theory_note(item, pattern_name, organ)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(content, encoding="utf-8")

    item.status = AbsorptionStatus.FORMALIZED
    item.pattern_name = pattern_name
    item.organ = organ

    logger.info("Formalized: %s → %s", item.id, artifact_path)
    return str(artifact_path.relative_to(ORGAN_DIRS))


def _extract_pattern_name(item: AbsorptionItem) -> str:
    """Extract a pattern name from the question and triggers.

    Uses keyword extraction from the question text to derive a descriptive
    pattern name. Returns empty string if no clear pattern emerges.
    """
    text = item.question_text.lower()

    # Look for explicit "how do you handle X" patterns
    handle_match = re.search(
        r"how do you (?:handle|deal with|manage|approach) (?:the )?(.+?)(?:\?|$)",
        text,
    )
    if handle_match:
        raw = handle_match.group(1).strip().rstrip("?. ")
        # Clean up to a pattern name
        raw = re.sub(r"\b(?:the|a|an|in|of|for|with|and|or|but|is|are|was|were)\b", " ", raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        if len(raw) > 5:
            return raw[:50]

    # Look for "what happens when X" patterns
    happens_match = re.search(
        r"what happens (?:when|if) (.+?)(?:\?|$)",
        text,
    )
    if happens_match:
        raw = happens_match.group(1).strip().rstrip("?. ")
        raw = re.sub(r"\b(?:the|a|an|in|of|for|with|and|or|but)\b", " ", raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        if len(raw) > 5:
            return raw[:50]

    # Fallback: use the most distinctive noun phrases from the question
    # Extract words >4 chars that aren't common stopwords
    words = re.findall(r"\b[a-z]{5,}\b", text)
    stopwords = {
        "about", "would", "could", "should", "these", "those", "their",
        "there", "where", "which", "really", "actually", "basically",
        "interesting", "approach", "system", "using", "something",
    }
    distinctive = [w for w in words if w not in stopwords][:4]
    if len(distinctive) >= 2:
        return " ".join(distinctive)

    return ""


def _generate_theory_note(
    item: AbsorptionItem,
    pattern_name: str,
    organ: str,
) -> str:
    """Generate a structured theory note markdown artifact."""
    triggers_str = ", ".join(t.value for t in item.triggers)
    has_convergence = AbsorptionTrigger.INDEPENDENT_CONVERGENCE in item.triggers
    has_divergence = AbsorptionTrigger.ASSUMPTION_DIVERGENCE in item.triggers
    has_unnamed = AbsorptionTrigger.UNNAMED_PATTERN in item.triggers

    sections = [
        f"# {pattern_name.title()}",
        "",
        f"**Origin:** Absorbed from @{item.questioner}'s question on {item.workspace}",
        f"**Source:** {item.source_url}",
        f"**Triggers:** {triggers_str}",
        f"**Target Organ:** {organ}",
        "",
        "---",
        "",
        "## The Question That Opened This",
        "",
        f"> {item.question_text}",
        "",
    ]

    if has_divergence:
        sections.extend([
            "## Assumption Divergence",
            "",
            "The question assumes a resolution or handling strategy that differs "
            "from our implementation. This divergence is the insight — our approach "
            "is worth naming precisely because it departs from the expected pattern.",
            "",
        ])

    if has_unnamed:
        sections.extend([
            "## Unnamed Pattern",
            "",
            "The question points at a behavior or property in our architecture "
            "that exists in the code but has not been given a formal name or "
            "articulated as a reusable principle.",
            "",
            "### Properties (to be formalized)",
            "",
            "1. *[What invariant does this pattern maintain?]*",
            "2. *[What does it guarantee under failure?]*",
            "3. *[What does it explicitly NOT guarantee?]*",
            "",
        ])

    if has_convergence:
        sections.extend([
            "## Independent Convergence",
            "",
            "The questioner described an independent implementation that solves "
            "a similar problem with a different mechanism. When two systems evolve "
            "the same solution shape independently, the pattern is a structural "
            "attractor — worth formalizing because it emerges from the problem's "
            "constraints, not from copying.",
            "",
        ])

    sections.extend([
        "## Relationship to Existing Theory",
        "",
        "- *[How does this relate to forward-only FSM governance?]*",
        "- *[How does this relate to idempotent checkpoint writes?]*",
        "- *[How does this relate to reader-side resolution?]*",
        "",
        "---",
        "",
        f"*Absorption Protocol — auto-formalized {datetime.now().strftime('%Y-%m-%d')}*",
        f"*Backflow source: {item.workspace}, @{item.questioner}*",
    ])

    return "\n".join(sections) + "\n"


def run_full_absorption_cycle(since: str = "") -> dict[str, int]:
    """Run the complete absorption cycle: detect → formalize → deposit.

    This is the autonomous version — no human intervention needed.
    The system detects expansion-worthy questions, generates theory note
    skeletons, and deposits them into the backflow pipeline.

    Returns:
        Dict with counts: detected, formalized, deposited.
    """
    from contrib_engine.backflow import load_backflow, save_backflow

    results = {"detected": 0, "formalized": 0, "deposited": 0}

    # Phase 1: Detect
    index = load_absorption()
    new_items = scan_conversations(since=since)
    if new_items:
        index.items.extend(new_items)
        results["detected"] = len(new_items)

    # Phase 2: Formalize all pending items
    pending = index.pending_formalization()
    backflow_index = load_backflow()

    for item in pending:
        artifact_path = auto_formalize(item)
        if artifact_path:
            results["formalized"] += 1

            # Phase 3: Deposit to backflow
            try:
                backflow_item = deposit_to_backflow(item, artifact_path)
                backflow_index.items.append(backflow_item)
                results["deposited"] += 1
            except ValueError:
                pass  # Item wasn't in formalized state (shouldn't happen)

    # Save state
    if results["detected"] or results["formalized"]:
        save_absorption(index)
    if results["deposited"]:
        save_backflow(backflow_index)

    logger.info(
        "Absorption cycle: %d detected, %d formalized, %d deposited",
        results["detected"],
        results["formalized"],
        results["deposited"],
    )

    return results
