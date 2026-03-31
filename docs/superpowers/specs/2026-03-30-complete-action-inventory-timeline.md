# Complete Action Inventory & Timeline — orchestration-start-here

**Date:** 2026-03-30
**Scope:** Every executable action, script, workflow, CLI command, automation, and data pipeline in the repo. Dead, alive, retired, planned, and missing.

---

## Timeline: The Full Sequence

```
2026-02-10  GOLD SPRINT G4 — Repo initialized
    │
    ├── validate-dependencies.yml (CI, push/PR)
    ├── promote-repo.yml (manual dispatch)
    ├── publish-process.yml (manual dispatch)
    ├── monthly-organ-audit.yml (cron: 1st of month)
    ├── distribute-content.yml (issue trigger)
    ├── calculate-metrics.py (called by audit workflow)
    ├── validate-deps.py (CI gatekeeper)
    ├── organ-audit.py (monthly system health)
    │
2026-02-11  PLATINUM SPRINT
    │
    ├── ci.yml (minimal CI — push/PR/dispatch)
    ├── distribute-content.yml upgraded (Mastodon, Discord, LinkedIn, Ghost)
    │
2026-02-12  GENESIS SPRINT → AUTONOMY SPRINT
    │
    ├── src/agents/dispatcher.ts (100 lines — orchestrator stubs)
    ├── src/agents/metasystem-manager.ts (88 lines — metasystem stubs)
    ├── src/dreamcatcher/router.ts (163 lines — LLM model router)
    ├── src/dreamcatcher/watchman.ts (221 lines — circuit breaker agent)
    ├── orchestrator-agent.yml (cron: Mon 7am)
    ├── promotion-recommender.yml (cron: 1st of month)
    ├── registry-health-audit.yml (cron: Mon 6am)
    ├── essay-monitor.yml (cron: daily 9am)
    ├── distribution-agent.yml (cron: Wed 10am)
    ├── codeql.yml (security, cron: Mon 6am)
    ├── secret-scan.yml (push/PR)
    ├── stale.yml (cron: Mon 9am)
    │
2026-02-16  REMEDIUM
    │
    ├── essay-monitor.yml fixed (YAML parse error)
    ├── registry-sync-check.yml (cron: Mon 5am)
    │
2026-02-17  DISTRIBUTIO SPRINT
    │
    ├── backfill-distribution.yml (cron: MWF 2pm)
    ├── Bluesky added to distribute-content.yml
    │
2026-02-18  EDGE IMPLEMENTATION
    │
    ├── theory-input-handler.yml (dispatch event: VII→IV→I edge)
    ├── distribute-content.yml: essay.published → ORGAN-VI,VII routing
    │
    ╔══════════════════════════════════════════════════════════╗
    ║  6 WEEKS DORMANT — workflows running on cron, no new   ║
    ║  scripts or modules. GitHub Actions only visible work.  ║
    ╚══════════════════════════════════════════════════════════╝
    │
2026-03-21  THE PLAGUE BEGINS — S30 (Hive contribution)
    │
    ├── contrib_engine/ created
    │   ├── scanner.py (4 signal sources, composite scoring)
    │   ├── orchestrator.py (workspace init: fork, seed, CLAUDE.md, journal)
    │   ├── monitor.py (PR polling, journal changes, next-action)
    │   ├── capabilities.py (8 capability definitions)
    │   ├── schemas.py (12 Pydantic models)
    │   ├── github_client.py (gh CLI wrapper)
    │   └── cli.py (__main__.py)
    │
2026-03-22  S32 — PLAGUE CAMPAIGN EXPANSION
    │
    ├── campaign.py (phase sequencer: UNBLOCK→ENGAGE→CULTIVATE→HARVEST→INJECT)
    ├── outreach.py (relationship scoring, event logging)
    ├── backflow.py (6-organ knowledge routing)
    ├── __main__.py (full standalone CLI: campaign/outreach/backflow subcommands)
    ├── cli.py expanded (absorb/absorb-pending/absorb-track/absorb-formalize)
    ├── data/campaign.yaml (living state)
    ├── data/outreach.yaml (living state)
    ├── data/backflow.yaml (living state)
    ├── data/ranked_targets.yaml (scanner output)
    │
2026-03-23  CAMPAIGN VELOCITY
    │
    ├── scanner.py expanded (forks, stars, deps, PR-history signal sources)
    ├── monitor.py fixed (both seed.yaml formats)
    ├── generate-seed-from-registry.py
    ├── validate-all-seeds.py
    ├── deploy-seeds-local.sh
    ├── fetch-registry.sh
    ├── data/tracked_conversations.yaml
    │
2026-03-24  S35 — ABSORPTION PROTOCOL
    │
    ├── absorption.py (8 heuristics, 6 reduction filters, auto-formalization)
    ├── data/absorption.yaml (living state)
    ├── artifacts/dbt-mcp-patterns-absorption.md
    ├── artifacts/render_canvas.py (LinkedIn carousel renderer)
    ├── artifacts/render_post001.py (Post #001 visuals)
    ├── artifacts/render_post002.py (Post #002 visuals)
    ├── artifacts/render_post002_audit.py (Testament audit visual)
    │
2026-03-27  WAVE 2-3 EXPANSION
    │
    ├── 15 new outreach relationships added
    ├── 30+ new campaign actions
    ├── 15 new backflow items deposited
    │
2026-03-30  S-PLAGUE — THIS SESSION
    │
    ├── docs/superpowers/specs/2026-03-30-fieldwork-intelligence-system-design.md (SPEC, not code)
    ├── docs/superpowers/specs/2026-03-30-fieldwork-zettelkasten-convergence-recs.md (SPEC)
    ├── 5 missing campaign targets added
    ├── 2 new outreach relationships (dapr, a2a-python)
    ├── 2 new campaign actions (a2a)
    │
    ╔══════════════════════════════════════════════════════════╗
    ║  PLANNED — Fieldwork Intelligence System                ║
    ║  fieldwork.py (not yet built, spec v4.0 ready)          ║
    ║  data/fieldwork.yaml, data/dossiers/, knowledge_outputs ║
    ╚══════════════════════════════════════════════════════════╝
```

---

## Complete Inventory

### I. GitHub Actions Workflows (17)

| # | Workflow | Trigger | Status | What It Does |
|---|---------|---------|--------|-------------|
| 1 | `ci.yml` | push, PR, dispatch | **ALIVE** | Minimal CI — validates YAML, runs validate-deps.py |
| 2 | `validate-dependencies.yml` | push, PR, Mon 6:30am | **ALIVE** | Dependency graph validation — no back-edges, cycle detection |
| 3 | `secret-scan.yml` | push, PR | **ALIVE** | Scans for leaked secrets (patterns: sk-, ghp_, AKIA) |
| 4 | `codeql.yml` | push, PR, Mon 6am | **ALIVE** | GitHub CodeQL security analysis |
| 5 | `stale.yml` | Mon 9am | **ALIVE** | Auto-label stale issues/PRs |
| 6 | `registry-health-audit.yml` | Mon 6am, dispatch | **ALIVE** | Registry integrity audit, creates issues for drift |
| 7 | `registry-sync-check.yml` | Mon 5am | **ALIVE** | Checks registry.json sync across organs |
| 8 | `monthly-organ-audit.yml` | 1st of month 2am | **ALIVE** | Full organ health audit, calls calculate-metrics.py |
| 9 | `promotion-recommender.yml` | 1st of month 8am | **ALIVE** | Recommends repos for promotion state advancement |
| 10 | `orchestrator-agent.yml` | Mon 7am | **ALIVE** | Builds system graph from seed.yaml, creates oversight issues |
| 11 | `essay-monitor.yml` | daily 9am | **ALIVE** | Monitors ORGAN-V essay pipeline for stalls |
| 12 | `distribute-content.yml` | issue labeled `distribute` | **ALIVE** | POSSE distribution: Mastodon, Discord, LinkedIn, Ghost, Bluesky |
| 13 | `distribution-agent.yml` | Wed 10am | **ALIVE** | POSSE audit — checks distribution coverage gaps |
| 14 | `backfill-distribution.yml` | MWF 2pm | **ALIVE** | Catch-up pass for essays missed by event-driven distribution |
| 15 | `promote-repo.yml` | `repository_dispatch` | **ALIVE** | Automated promotion pipeline (LOCAL→CANDIDATE→...) |
| 16 | `publish-process.yml` | `repository_dispatch` | **ALIVE** | Extract content from repo, create ORGAN-V PR |
| 17 | `theory-input-handler.yml` | `repository_dispatch` | **ALIVE** | Edge 6 routing: VII→IV→I theory input |

**Assessment:** All 17 workflows are syntactically alive and cron-scheduled. However, workflows #10-17 depend on external infrastructure (ORGAN-V repos, distribution credentials, dispatch events) that may or may not be wired. No workflow has been verified as actually executing successfully in production since their creation. **Recommendation: Run `gh workflow list` + `gh run list` to check actual execution history.**

### II. Python Scripts (15)

| # | Script | Status | What It Does |
|---|--------|--------|-------------|
| 1 | `validate-deps.py` | **ALIVE** | CI gatekeeper — validates unidirectional dependency graph |
| 2 | `organ-audit.py` | **ALIVE** | Monthly system health audit across 8 organs |
| 3 | `calculate-metrics.py` | **ALIVE** | Registry metrics computation (called by audit workflow) |
| 4 | `generate-seed-from-registry.py` | **ALIVE** | Reconcile seed.yaml files against registry-v2.json |
| 5 | `validate-all-seeds.py` | **ALIVE** | Validate all seed.yaml files workspace-wide |
| 6 | `deploy-seeds-local.sh` | **ALIVE** | Commit + push seed changes per organ (16GB RAM-aware) |
| 7 | `fetch-registry.sh` | **ALIVE** | Fetch canonical registry from corpvs-testamentvm |
| 8 | `handle-dispatch-promotion.py` | **ALIVE** | Handle `repository_dispatch` promotion events |
| 9 | `orchestrator-dry-run.py` | **ALIVE** | Local dry-run: build system graph from seed.yaml |
| 10 | `project-progress.py` | **ALIVE** | Per-project alpha-to-omega progress bar |
| 11 | `validate-agent-run.py` | **ALIVE** | Validate agent run dirs against F-57 logging standard |
| 12 | `validate-wip.py` | **ALIVE** | WIP limit enforcement |
| 13 | `enforce-ci-mandate.py` | **ALIVE** | Enforce CI workflow presence across all repos |
| 14 | `lib/__init__.py` | **ALIVE** | Shared script library (progress bars, etc.) |
| 15 | `lib/progress.py` | **ALIVE** | Progress bar utility for scripts |

**Note:** Scripts #1-3 have `# ISOTOPE DISSOLUTION` comments marking them as gates in the circulatory--contribute pathway. This refers to an earlier architecture (isotopes) that was dissolved into canonical imports on 2026-03-30.

### III. Contribution Engine — CLI Commands (21)

| # | Command | Status | What It Does |
|---|---------|--------|-------------|
| 1 | `scan [--no-github]` | **ALIVE** | Scan 4 signal sources for contribution targets |
| 2 | `list [--status] [--min-score]` | **ALIVE** | Show ranked targets with filters |
| 3 | `approve <target> [--skip-fork/remote/registry]` | **ALIVE** | Initialize cross-organ workspace |
| 4 | `status` | **ALIVE** | Show active contribution states |
| 5 | `monitor` | **ALIVE** | Poll PRs, journal changes, determine next actions |
| 6 | `absorb` | **ALIVE** | Run full absorption cycle (detect→formalize→deposit) |
| 7 | `absorb-pending` | **ALIVE** | Show pending formalization items |
| 8 | `absorb-track <owner> <repo> <issue>` | **ALIVE** | Add conversation to tracked list |
| 9 | `absorb-formalize <item-id>` | **ALIVE** | Formalize a specific absorption item |
| 10 | `campaign show` | **ALIVE** | Show campaign state + next actions |
| 11 | `campaign next` | **ALIVE** | Show single next unblocked action |
| 12 | `campaign complete <action_id>` | **ALIVE** | Mark campaign action complete |
| 13 | `campaign plan` | **ALIVE** | Generate action queue from workspace state |
| 14 | `outreach show [workspace]` | **ALIVE** | Show relationships + events |
| 15 | `outreach log <workspace> <channel> <summary>` | **ALIVE** | Log an outreach event |
| 16 | `outreach check` | **ALIVE** | Poll GitHub for new interactions |
| 17 | `backflow show` | **ALIVE** | Show backflow items by organ |
| 18 | `backflow pending` | **ALIVE** | Show pending extractions |
| 19 | `backflow add <ws> <organ> <type> <title>` | **ALIVE** | Add a backflow item |
| 20 | `backflow deposit <index>` | **ALIVE** | Mark item as deposited |
| 21 | `fieldwork *` | **PLANNED** | Record, dossier, synthesize, shatterpoints, outputs (spec v4.0) |

### IV. Contribution Engine — Modules (13 + 4 renderers)

| # | Module | Lines | Status | What It Does |
|---|--------|-------|--------|-------------|
| 1 | `scanner.py` | ~300 | **ALIVE** | 4 signal sources (contacts, stars, forks, deps) + composite scoring |
| 2 | `orchestrator.py` | ~200 | **ALIVE** | Workspace init: fork, git remote, seed.yaml, CLAUDE.md, journal |
| 3 | `monitor.py` | ~200 | **ALIVE** | PR state polling, journal updates, next-action determination |
| 4 | `campaign.py` | ~150 | **ALIVE** | Phase sequencer (5 phases), action queue, blocking dependencies |
| 5 | `outreach.py` | ~150 | **ALIVE** | Relationship scoring, event logging, GitHub interaction polling |
| 6 | `backflow.py` | ~60 | **ALIVE** | 6-organ knowledge routing (add, deposit, load/save) |
| 7 | `absorption.py` | ~775 | **ALIVE** | 8 heuristics, 6 reduction filters, auto-formalization, full cycle |
| 8 | `capabilities.py` | ~100 | **ALIVE** | 8 capability definitions for contribution targeting |
| 9 | `schemas.py` | ~345 | **ALIVE** | 30+ Pydantic models (all data contracts) |
| 10 | `github_client.py` | ~50 | **ALIVE** | `gh` CLI subprocess wrapper |
| 11 | `cli.py` | ~300 | **ALIVE** | Dual-mode prefix registration, 9 commands |
| 12 | `__main__.py` | ~235 | **ALIVE** | Standalone CLI entry point, 12 additional commands |
| 13 | `__init__.py` | ~5 | **ALIVE** | Package init |
| 14 | `render_canvas.py` | ~200 | **ALIVE** | LinkedIn carousel renderer (matplotlib) |
| 15 | `render_post001.py` | ~150 | **ALIVE** | Post #001 visuals |
| 16 | `render_post002.py` | ~200 | **ALIVE** | Post #002 carousel visuals |
| 17 | `render_post002_audit.py` | ~100 | **ALIVE** | Testament audit diagnostic image |

### V. TypeScript Source (4 files, 572 lines)

| # | File | Lines | Status | What It Does |
|---|------|-------|--------|-------------|
| 1 | `src/agents/dispatcher.ts` | 100 | **DEAD** | Orchestrator agent stubs — imports non-existent `scout.js` |
| 2 | `src/agents/metasystem-manager.ts` | 88 | **DEAD** | Metasystem manager — imports `scout.js`, `analyst.js` (don't exist) |
| 3 | `src/dreamcatcher/router.ts` | 163 | **DEAD** | LLM model router — imports `llm-client.js`, `kg-integration.js` (don't exist) |
| 4 | `src/dreamcatcher/watchman.ts` | 221 | **DEAD** | Night watchman circuit breaker — imports `circuit.js`, `model-router.js` (don't exist) |

**Assessment:** All 4 TypeScript files are GENESIS Sprint stubs (2026-02-12). They import modules that were never created (`scout.js`, `analyst.js`, `llm-client.js`, `kg-integration.js`, `circuit.js`). Zero test coverage. No `package.json`, no `tsconfig.json`, no build pipeline. **Status: DEAD.** The functionality they aspired to was superseded by the Python contrib_engine and the agentic-titan framework.

### VI. Data Files (8)

| # | File | Records | Status | What It Does |
|---|------|---------|--------|-------------|
| 1 | `data/campaign.yaml` | 20 targets, 52 actions | **ALIVE** | Campaign state — The Plague |
| 2 | `data/outreach.yaml` | 22 relationships | **ALIVE** | Relationship lifecycle tracking |
| 3 | `data/backflow.yaml` | 27 items | **ALIVE** | Knowledge routing to 6 organs |
| 4 | `data/absorption.yaml` | 4 items | **ALIVE** | Detected expansive questions |
| 5 | `data/tracked_conversations.yaml` | ~10 conversations | **ALIVE** | Absorption scanner targets |
| 6 | `data/ranked_targets.yaml` | ~10 targets | **ALIVE** | Scanner output |
| 7 | `ecosystem/pillar-dna/delivery.yaml` | 2 entries | **ALIVE** | Delivery pillar DNA |
| 8 | `ecosystem/pillar-dna/content.yaml` | 1 entry | **ALIVE** | Content pillar DNA |

### VII. Tests (16 files, 150 passing)

| # | File | Tests | Status |
|---|------|-------|--------|
| 1 | `test_validate_deps.py` | ~15 | **ALIVE** |
| 2 | `test_organ_audit.py` | ~10 | **ALIVE** |
| 3 | `test_calculate_metrics.py` | ~8 | **ALIVE** |
| 4 | `test_contrib_scanner.py` | ~15 | **ALIVE** |
| 5 | `test_contrib_scanner_sources.py` | ~10 | **ALIVE** |
| 6 | `test_contrib_orchestrator.py` | ~12 | **ALIVE** |
| 7 | `test_contrib_monitor.py` | ~10 | **ALIVE** |
| 8 | `test_contrib_cli.py` | ~8 | **ALIVE** |
| 9 | `test_contrib_github_client.py` | ~5 | **ALIVE** |
| 10 | `test_contrib_integration.py` | ~8 | **ALIVE** |
| 11 | `test_contrib_campaign.py` | ~12 | **ALIVE** |
| 12 | `test_contrib_outreach.py` | ~10 | **ALIVE** |
| 13 | `test_contrib_backflow.py` | ~8 | **ALIVE** |
| 14 | `test_absorption.py` | ~19 | **ALIVE** |
| 15 | `conftest.py` | — | **ALIVE** |
| 16 | `__init__.py` | — | **ALIVE** |

### VIII. Documentation & Specs (key action-related docs)

| # | File | Status | What It Does |
|---|------|--------|-------------|
| 1 | `docs/absorption-protocol.md` | **ALIVE** | Protocol spec for inbound question detection |
| 2 | `docs/testament-formalization.md` | **ALIVE** | 13 articles formalized into logic/algorithms/math |
| 3 | `docs/coordination-protocols/DREAMCATCHER_SPEC.md` | **RETIRED** | Dreamcatcher architecture — superseded by agentic-titan |
| 4 | `docs/coordination-protocols/AI_ORCHESTRATION_TIMELINE.md` | **RETIRED** | Early orchestration timeline — superseded |
| 5 | `docs/coordination-protocols/HANDOFF_MASTER.md` | **ALIVE** | Session handoff protocol |
| 6 | `docs/coordination-protocols/GITHUB_SYNC_MASTER.md` | **ALIVE** | GitHub sync coordination |
| 7 | `docs/session-protocol.md` | **ALIVE** | Session lifecycle protocol |
| 8 | `docs/breadcrumb-protocol.md` | **ALIVE** | Breadcrumb trail for cross-session tracking |
| 9 | `docs/flow-patterns/README.md` | **ALIVE** | Flow pattern catalog |
| 10 | `fieldwork-intelligence-system-design.md` | **PLANNED** | Fieldwork system spec v4.0 |
| 11 | `fieldwork-zettelkasten-convergence-recs.md` | **PLANNED** | Convergence recommendations |

### IX. GitHub Templates (5)

| # | File | Status |
|---|------|--------|
| 1 | `.github/ISSUE_TEMPLATE/bug_report.yml` | **ALIVE** |
| 2 | `.github/ISSUE_TEMPLATE/feature_request.yml` | **ALIVE** |
| 3 | `.github/ISSUE_TEMPLATE/governance.yml` | **ALIVE** |
| 4 | `.github/ISSUE_TEMPLATE/config.yml` | **ALIVE** |
| 5 | `.github/PULL_REQUEST_TEMPLATE.md` | **ALIVE** |

### X. Static Config (3)

| # | File | Status |
|---|------|--------|
| 1 | `seed.yaml` | **ALIVE** (stale — last_validated 2026-03-23, IRF-OSS-017 P0) |
| 2 | `renovate.json` | **ALIVE** (dependency update bot config) |
| 3 | `governance-rules.json` | **ALIVE** (6 articles of codified governance) |

---

## Status Summary

| Status | Count | Items |
|--------|-------|-------|
| **ALIVE** | 82 | 17 workflows, 15 scripts, 21 CLI commands, 17 modules, 8 data files, 16 tests, 5 templates, 3 config |
| **DEAD** | 4 | 4 TypeScript stubs (src/agents/, src/dreamcatcher/) — never completed, imports broken |
| **RETIRED** | 2 | DREAMCATCHER_SPEC.md, AI_ORCHESTRATION_TIMELINE.md — superseded by agentic-titan |
| **PLANNED** | 3 | fieldwork.py, fieldwork CLI commands, fieldwork data files (spec v4.0 ready) |
| **MISSING** | 5 | scout.js, analyst.js, llm-client.js, kg-integration.js, circuit.js (TypeScript imports that never existed) |

---

## Vacuums Identified

| Vacuum | Priority | What's Missing |
|--------|----------|---------------|
| **seed.yaml stale** | P0 | `last_validated: 2026-03-23` — missing fieldwork module, absorption module, test count wrong (111→150+). IRF-OSS-017. |
| **TypeScript dead code** | P2 | 572 lines of never-completed stubs. No build pipeline. Should be archived or deleted. |
| **Workflow execution history unverified** | P1 | All 17 workflows are syntactically valid but actual cron execution unverified. `gh run list` audit needed. |
| **Fieldwork not built** | P1 | Spec v4.0 hardened, convergence recs written, but zero implementation code. IRF-OSS-022. |
| **Render scripts uncalled** | P2 | 4 artifact renderers exist but no workflow or CLI command invokes them. Manual execution only. |
| **No pyproject.toml/Makefile** | P2 | No task runner. All scripts invoked by path. Consider `just` or `pyproject.toml [project.scripts]`. |

---

*Inventory version: 1.0 | 2026-03-30 | 96 items catalogued across 10 categories*
