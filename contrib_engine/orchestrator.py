"""Contribution Orchestrator — initializes cross-organ contribution workspaces.

On human approval, creates the full ORGANVM infrastructure for contributing
to an open-source project: fork, workspace, submodule, registry entry,
seed.yaml, journal, CLAUDE.md, CONTRIBUTION-PROMPT.md.
"""

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from contrib_engine.capabilities import CAPABILITIES, match_capabilities
from contrib_engine.github_client import create_repo, fork_repo
from contrib_engine.schemas import ContributionTarget, TargetStatus

logger = logging.getLogger(__name__)

ORGAN_IV_DIR = Path.home() / "Workspace" / "organvm-iv-taxis"
REGISTRY_PATH = (
    Path.home()
    / "Workspace"
    / "meta-organvm"
    / "organvm-corpvs-testamentvm"
    / "registry-v2.json"
)


def workspace_name(target: ContributionTarget) -> str:
    """Generate workspace directory name from target."""
    owner, repo = target.github.split("/", 1) if "/" in target.github else (target.name, target.name)
    return f"contrib--{owner.lower()}-{repo.lower()}"


def approve_and_initialize(
    target: ContributionTarget,
    skip_fork: bool = False,
    skip_remote: bool = False,
    skip_submodule: bool = False,
    skip_registry: bool = False,
) -> Path:
    """Initialize full cross-organ contribution workspace.

    Returns path to the created workspace.
    """
    ws_name = workspace_name(target)
    ws_path = ORGAN_IV_DIR / ws_name

    if ws_path.exists():
        logger.info("Workspace already exists: %s", ws_path)
        target.status = TargetStatus.ACTIVE
        target.workspace = ws_name
        return ws_path

    logger.info("Initializing workspace: %s", ws_name)

    # 1. Fork target repo
    if not skip_fork and target.github:
        owner, repo = target.github.split("/", 1)
        fork_url = fork_repo(owner, repo)
        logger.info("Forked to: %s", fork_url)

    # 2. Create workspace directory
    ws_path.mkdir(parents=True, exist_ok=True)

    # 3. Initialize git repo
    subprocess.run(["git", "init"], cwd=ws_path, capture_output=True)

    # 4. Generate seed.yaml
    _write_seed_yaml(ws_path, target)

    # 5. Generate README.md
    _write_readme(ws_path, target)

    # 6. Generate CLAUDE.md
    _write_claude_md(ws_path, target)

    # 7. Generate CONTRIBUTION-PROMPT.md
    _write_contribution_prompt(ws_path, target)

    # 8. Create journal directory with session-00
    _write_initial_journal(ws_path, target)

    # 9. Create plans directory
    (ws_path / ".claude" / "plans").mkdir(parents=True, exist_ok=True)

    # 10. Initial commit
    subprocess.run(
        ["git", "add", "."],
        cwd=ws_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"feat: initialize contribution workspace for {target.github}"],
        cwd=ws_path,
        capture_output=True,
    )

    # 11. Create GitHub remote
    if not skip_remote:
        create_repo(
            "organvm-iv-taxis",
            ws_name,
            description=f"Cross-organ symbiotic contribution to {target.github}",
            public=True,
        )
        subprocess.run(
            ["git", "remote", "add", "origin", f"git@github.com:organvm-iv-taxis/{ws_name}.git"],
            cwd=ws_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            cwd=ws_path,
            capture_output=True,
        )

    # 12. Add as submodule in superproject
    if not skip_submodule:
        subprocess.run(
            ["git", "submodule", "add", "-f",
             f"git@github.com:organvm-iv-taxis/{ws_name}.git", ws_name],
            cwd=ORGAN_IV_DIR,
            capture_output=True,
        )

    # 13. Register in registry
    if not skip_registry:
        _register_in_registry(target, ws_name)

    target.status = TargetStatus.ACTIVE
    target.workspace = ws_name

    logger.info("Workspace initialized: %s", ws_path)
    return ws_path


def _write_seed_yaml(ws_path: Path, target: ContributionTarget) -> None:
    """Generate seed.yaml for the contribution workspace."""
    owner, repo = target.github.split("/", 1) if "/" in target.github else (target.name, "")
    caps = target.domain_overlap or [c.id for c in match_capabilities(target.notes)]

    seed = {
        "name": workspace_name(target),
        "organ": "IV",
        "tier": "contrib",
        "promotion_status": "LOCAL",
        "produces": [
            f"pr_to_{owner}_{repo}".replace("/", "_"),
            "theory_extraction",
            "generative_artifacts",
            "public_narrative",
            "relationship_capital",
        ],
        "consumes": [
            "agentic_titan_patterns",
            "organvm_governance_rules",
            f"{repo}_codebase_data",
        ],
        "subscriptions": [
            "product.release",
            "distribution.dispatched",
        ],
    }

    with open(ws_path / "seed.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(seed, f, default_flow_style=False, sort_keys=False)


def _write_readme(ws_path: Path, target: ContributionTarget) -> None:
    """Generate README.md."""
    owner, repo = target.github.split("/", 1) if "/" in target.github else (target.name, target.name)
    caps = target.domain_overlap or []

    content = f"""# {workspace_name(target)}

Open-source contribution workspace for [{owner}/{repo}](https://github.com/{target.github}).

## ORGANVM Alignment

| Capability | Relevance |
|-----------|-----------|
"""
    for cap_id in caps:
        for cap in CAPABILITIES:
            if cap.id == cap_id:
                content += f"| {cap.name} | {cap.description[:80]} |\n"

    content += f"""
## Contacts

{chr(10).join(f'- {c}' for c in target.contacts) if target.contacts else '- (none identified)'}

## Organ Membership

- **Organ:** IV (Taxis — Orchestration)
- **Tier:** contrib (external open-source contribution)
- **Status:** LOCAL
"""

    (ws_path / "README.md").write_text(content, encoding="utf-8")


def _write_claude_md(ws_path: Path, target: ContributionTarget) -> None:
    """Generate CLAUDE.md."""
    owner, repo = target.github.split("/", 1) if "/" in target.github else (target.name, target.name)

    content = f"""# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Contribution workspace for [{owner}/{repo}](https://github.com/{target.github}). Part of ORGAN-IV (Taxis/Orchestration), tier: contrib.

The target fork lives (or will live) in `./repo/` once cloned. The root directory contains coordination docs only.

## Setup

```bash
# Clone fork (after forking)
git clone https://github.com/4444J99/{repo}.git repo
cd repo
git remote add upstream https://github.com/{target.github}.git
```

## Working in This Directory

- `CONTRIBUTION-PROMPT.md` — Full session prompt for contribution sessions
- `README.md` — Relationship map and capability alignment
- `journal/` — Timestamped session logs
- `seed.yaml` — Formal ORGANVM contract
- Once `repo/` exists, defer to its own CLAUDE.md for code conventions
"""

    (ws_path / "CLAUDE.md").write_text(content, encoding="utf-8")


def _write_contribution_prompt(ws_path: Path, target: ContributionTarget) -> None:
    """Generate CONTRIBUTION-PROMPT.md."""
    owner, repo = target.github.split("/", 1) if "/" in target.github else (target.name, target.name)
    caps = target.domain_overlap or []

    content = f"""# {owner}/{repo} Contribution Prompt

Use this prompt when starting a session to work on {owner}/{repo} PRs.

---

## Context

I'm contributing to {target.github} (https://github.com/{target.github}).
Signal: {target.signal_type}. Contacts: {', '.join(target.contacts) or 'none identified'}.

My background (ORGANVM):
- 118-repo multi-agent orchestration system
- Promotion state machine with forward-only transitions
- 23,470+ tests, 104 CI/CD pipelines
- Deep Python, testing, CI/CD, documentation, security experience

## ORGANVM Capabilities Matching This Target

{chr(10).join(f'- **{cap_id}**' for cap_id in caps) if caps else '- (run scanner to identify matching capabilities)'}

## Approach

1. Fork to 4444J99/{repo} (if not done)
2. Clone into `./repo/`
3. Read CONTRIBUTING.md, CLAUDE.md, AGENTS.md
4. Explore codebase deeply — understand patterns, conventions, test framework
5. Identify highest-impact issue where ORGANVM patterns apply
6. Design the fusion — what flows from ORGANVM, what flows back
7. Build Phase 1 — TDD, following their patterns exactly
8. Wire ORGANVM infrastructure
9. Claim issue, submit PR
10. Journal the session
"""

    (ws_path / "CONTRIBUTION-PROMPT.md").write_text(content, encoding="utf-8")


def _write_initial_journal(ws_path: Path, target: ContributionTarget) -> None:
    """Create journal directory with session-00 entry."""
    journal_dir = ws_path / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d")
    content = f"""# Session 00 — {date}

## Workspace Initialized

- **Target:** {target.github}
- **Signal:** {target.signal_type}
- **Score:** {target.score}
- **Contacts:** {', '.join(target.contacts) or 'none'}
- **Domain overlap:** {', '.join(target.domain_overlap) or 'pending scan'}
- **Matching issues:** {target.matching_issues or 'pending scan'}

## Next Steps

- [ ] Clone fork into `./repo/`
- [ ] Read CONTRIBUTING.md and upstream CLAUDE.md
- [ ] Deep-explore codebase
- [ ] Identify target issue
- [ ] Design fusion
- [ ] Build Phase 1
"""

    (journal_dir / f"{date}-session-00.md").write_text(content, encoding="utf-8")


def _register_in_registry(target: ContributionTarget, ws_name: str) -> bool:
    """Add entry to registry-v2.json."""
    if not REGISTRY_PATH.exists():
        logger.warning("Registry not found: %s", REGISTRY_PATH)
        return False

    with open(REGISTRY_PATH, encoding="utf-8") as f:
        reg = json.load(f)

    repos = reg["organs"]["ORGAN-IV"]["repositories"]

    # Check not already registered
    if any(r["name"] == ws_name for r in repos):
        logger.info("Already registered: %s", ws_name)
        return True

    repos.append({
        "name": ws_name,
        "org": "organvm-iv-taxis",
        "status": "ACTIVE",
        "public": True,
        "description": f"Cross-organ contribution to {target.github}",
        "documentation_status": "DEPLOYED",
        "portfolio_relevance": "HIGH - Public process contribution",
        "dependencies": ["agentic-titan", "orchestration-start-here"],
        "promotion_status": "LOCAL",
        "tier": "contrib",
        "last_validated": datetime.now().strftime("%Y-%m-%d"),
    })
    reg["organs"]["ORGAN-IV"]["repository_count"] = len(repos)

    # Safety check
    total = sum(len(o.get("repositories", [])) for o in reg["organs"].values())
    if total < 50:
        logger.error("Safety check failed: only %d repos, refusing to write", total)
        return False

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write("\n")

    logger.info("Registered %s in registry (%d total repos)", ws_name, total)
    return True
