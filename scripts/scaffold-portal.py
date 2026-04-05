#!/usr/bin/env python3
"""Portal scaffolder — seeds a complete 5-file portal genome."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    """Find the repo root by looking for .git."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Not in a git repo")


def create_portal(
    slug: str,
    archetype: str,
    description: str,
    war_report: str,
    parent_repo: Path,
    dry_run: bool = False,
) -> None:
    """Create a complete portal genome in tasks/<slug>/."""

    portal_dir = parent_repo / "tasks" / slug

    if portal_dir.exists() and any(portal_dir.iterdir()):
        print(f"ERROR: Portal directory already exists and is not empty: {portal_dir}")
        sys.exit(1)

    portal_dir.mkdir(parents=True, exist_ok=bool(dry_run))

    # CLAUDE.md template
    claude_md = f"""# Portal — {slug.replace("-", " ").title()}

**Nature:** Reality-rectification intervention
**Scale:** ORGAN-IV module → {description}
**Archetype:** {archetype}

---

## What a Portal Is

A portal opens where rendered reality and imagined ideal diverge at a given scale. Two futures orbit the divergence — the utopic (where coherence increases) and the dystopic (where fragmentation compounds). The portal injects the minimum form required to shift the trajectory toward the utopic attractor, then precipitates the next intervention and stops.

The portal is not a task. The task is what the trajectory-shift looks like from the inside.

---

## The War at This Scale

{war_report}

### Counter-Force Field

| Dystopic Attractor | Utopic Attractor | The State |
|-------------------|------------------|-----------|
| **Homeostasis** — preserves local equilibrium | **Homeorhesis** — returns to shared trajectory | **Coherence** |
| **Elasticity** — snaps back to defaults | **Plasticity** — new shape holds | **Adaptability** |
| **Reactive** — fires on trigger accumulation | **Allostasis** — anticipates full lifecycle | **Resilience** |
| **Preservation** — frozen format | **Kinorhesis** — evolving format | **Evolution** |

**This portal operates in the utopic column.**

---

## Lifecycle

```
INJECT → CREATE → OPERATE → VERIFY → PRECIPITATE → STOP
```

There is no EVAPORATE phase. Evaporation happens when the next portal (or the operator) consumes the RECEIPT.md this portal deposits.

## Rules

1. Read `BRIEFING.md` — the war report from the border between two futures.
2. Read `SEQUENCE.md` — the intervention procedure α→ε.
3. Read `REFERENCES.md` — keys only: the doors that need opening.
4. Work in the parent repo (`../../`), not in this directory.
5. Do not create files inside this directory except `RECEIPT.md`.
6. Every operation is a repeatable procedure.
7. **On completion**: write `RECEIPT.md` with forward deposit for the next portal, then STOP. Do not delete this directory. Do not continue.

## Parent Context

- **Repo:** {parent_repo.name}
- **Session:** S52+
"""

    # BRIEFING.md template
    briefing_md = f"""# War Report: {slug.replace("-", " ").title()}

**Session:** S52+ | **Date:** {datetime.now().strftime("%Y-%m-%d")}
**Archetype:** {archetype}

---

## The Front Line

{war_report}

### Where Dystopia Is Currently Winning

_Describe what's failing, what's being lost, what's calcifying._

### What Utopia Looks Like If This Portal Succeeds

_Describe the ideal state after trajectory shifts._

### What Dystopia Looks Like If This Portal Fails

_Describe what happens if the gap remains unfilled._

---

## Campaign Dependencies

| What | State | Door |
|------|-------|------|
| | | |

---

## Deliverables

| Key | Artifact | Door |
|-----|----------|------|
| K1 | | CREATE |
| K2 | | EDIT |
| K3 | | APPEND |
"""

    # REFERENCES.md template
    references_md = f"""# References: {slug}

External pointers: files, repos, channels, people, memory.

---

## Keys to Doors

| Key | Location | What It Is | How to Open |
|-----|----------|-----------|-------------|
| K1 | | | |
| K2 | | | |
| K3 | | | |

---

## Context Stream

What else the agent needs to know:
- Recent commits affecting this domain
- Related SOPs or patterns
- Pending IRF items

---

## The Terrain

Existing forms mapped to dystopic/utopic pulls:

| Existing Form | Dystopic Pull (preserve frozen) | Utopic Pull (transform alive) |
|---------------|----------------------------------|------------------------------|
| | | |

---

## Channels (for SOP content)

| Channel | What It Handles | Current State |
|---------|----------------|---------------|
| | | |
"""

    # SEQUENCE.md template
    sequence_md = f"""# Sequence: {archetype} α → ε

The ordered intervention. Every injection, creation, operation, verification, and forward deposit as a repeatable procedure.

---

## Phase α — INJECT

| Step | Procedure | Output |
|------|-----------|--------|
| α.1 | Read BRIEFING.md, understand the war | Context loaded |
| α.2 | Read REFERENCES.md, identify doors | Keys mapped |
| α.3 | Read SEQUENCE.md, understand procedure | Plan formed |

---

## Phase β — CREATE

| Step | Procedure | Output |
|------|-----------|--------|
| β.1 | Create artifact K1 | |
| β.2 | Edit file for K2 | |
| β.3 | Append to ledger for K3 | |

---

## Phase γ — OPERATE

| Step | Procedure | Output |
|------|-----------|--------|
| γ.1 | | |
| γ.2 | | |
| γ.3 | | |

---

## Phase δ — VERIFY

| Step | Procedure | Command | Expected |
|------|-----------|---------|----------|
| δ.1 | Run tests | `python -m pytest tests/ -q` | All pass |
| δ.2 | Verify local:remote | `git status` | Clean |
| δ.3 | Check constraints | | |

---

## Phase ε — PRECIPITATE (Forward Deposit + Stop)

| Step | Procedure | Output |
|------|-----------|--------|
| ε.1 | Commit all artifacts | |
| ε.2 | Push to origin | local:remote = 1:1 |
| ε.3 | Write `RECEIPT.md` | Forward deposit for next portal |
| ε.4 | If next task is predictable, seed `tasks/<next-slug>/BRIEFING.md` | |
| ε.5 | **STOP** | Do not evaporate. Do not continue. |

---

### RECEIPT.md Template

```markdown
# Receipt: {slug}

**Completed:** <timestamp>
**Session:** S52+
**Commit:** <sha>

## What Was Done
- <artifacts produced>

## What Was NOT Done (and why)
- <deferred items>

## Forward Deposit

### Next Portal Location
`tasks/<next-slug>/`

### Next Portal Prompt
```

The avalanche pauses here.
"""

    if dry_run:
        print(f"[DRY RUN] Would create {portal_dir}/ with 4 genome files")
        print(f"  CLAUDE.md: {len(claude_md)} chars")
        print(f"  BRIEFING.md: {len(briefing_md)} chars")
        print(f"  REFERENCES.md: {len(references_md)} chars")
        print(f"  SEQUENCE.md: {len(sequence_md)} chars")
        return

    # Write files
    (portal_dir / "CLAUDE.md").write_text(claude_md)
    (portal_dir / "BRIEFING.md").write_text(briefing_md)
    (portal_dir / "REFERENCES.md").write_text(references_md)
    (portal_dir / "SEQUENCE.md").write_text(sequence_md)

    print(f"Created portal: {portal_dir}")
    print("  - CLAUDE.md")
    print("  - BRIEFING.md")
    print("  - REFERENCES.md")
    print("  - SEQUENCE.md")
    print("  - RECEIPT.md (write at completion)")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a portal genome in tasks/<slug>/"
    )
    parser.add_argument(
        "slug",
        help="Portal slug (e.g., correspondence-compose-templates)",
    )
    parser.add_argument(
        "--archetype",
        default="RELAY-CIRCUIT",
        help="Portal archetype (default: RELAY-CIRCUIT)",
    )
    parser.add_argument(
        "--description",
        default="cross-organ governance",
        help="Scale description",
    )
    parser.add_argument(
        "--war-report",
        default="The divergence between reality and ideal exists...",
        help="War report text for BRIEFING.md",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without creating it",
    )

    args = parser.parse_args()

    try:
        repo_root = get_repo_root()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Verify tasks/ directory exists
    tasks_dir = repo_root / "tasks"
    if not tasks_dir.exists():
        print(f"ERROR: tasks/ directory does not exist: {tasks_dir}")
        sys.exit(1)

    create_portal(
        slug=args.slug,
        archetype=args.archetype,
        description=args.description,
        war_report=args.war_report,
        parent_repo=repo_root,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
