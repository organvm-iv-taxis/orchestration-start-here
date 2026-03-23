# CLAUDE.md — orchestration-start-here

**ORGAN IV** (Orchestration) · `organvm-iv-taxis/orchestration-start-here`
**Status:** ACTIVE · **Branch:** `main`

## What This Repo Is

Central orchestration hub: registry, governance rules, 5 workflows, 3 Python scripts. The central nervous system of the eight-organ system.

## Stack

**Languages:** TypeScript, Python

## Directory Structure

```
📁 .github/
📁 .meta/
📁 docs/
    adr
    autonomous-systems-design.md
    coordination-protocols
    flow-patterns
    metasystem-manifest
    seed-schema
📁 scripts/
    calculate-metrics.py
    organ-audit.py
    validate-deps.py
📁 src/
    agents
    dreamcatcher
  .gitignore
  CHANGELOG.md
  LICENSE
  README.md
  audit-report.md
  governance-rules.json
  registry.json
  renovate.json
  seed.yaml
```

## Key Files

- `README.md` — Project documentation
- `seed.yaml` — ORGANVM orchestration metadata
- `src/` — Main source code
- `contrib_engine/` — Outbound open-source contribution engine (scanner, orchestrator, monitor)

## Contribution Engine (`contrib_engine/`)

The Plague Campaign — systematic open-source contribution engine with income-weighted prioritization.

```bash
python -m contrib_engine scan          # Scan signals for targets (4 sources: contacts, stars, forks, deps)
python -m contrib_engine list          # Show ranked targets
python -m contrib_engine approve <t>   # Initialize cross-organ workspace
python -m contrib_engine status        # Show active contribution states
python -m contrib_engine monitor       # Poll PRs, journal changes, determine next actions
python -m contrib_engine campaign show # Campaign sequencer — next actions, phase summary
python -m contrib_engine outreach show # Outreach tracker — relationship lifecycle
python -m contrib_engine backflow pending # Backflow pipeline — knowledge routing to organs
```

**Core modules:** `scanner.py` (4 signal sources + scoring), `orchestrator.py` (workspace init), `monitor.py` (PR lifecycle — handles both seed.yaml formats), `capabilities.py` (8 capability definitions), `schemas.py` (25 Pydantic models), `github_client.py` (gh CLI wrapper), `cli.py` (dual-mode prefix registration).

**Campaign modules (new S32):** `campaign.py` (phase sequencer: UNBLOCK→ENGAGE→CULTIVATE→HARVEST→INJECT), `outreach.py` (relationship scoring, event logging), `backflow.py` (6-organ routing: theory/generative/code/narrative/community/distribution).

**Data files** (committed, living state): `data/campaign.yaml` (15 actions, income-weighted), `data/outreach.yaml` (7 relationships), `data/backflow.yaml` (8 pending items).

**Testament:** 13 articles of codified writing rules formalized into logic/algorithms/math at `docs/testament-formalization.md`. Constitutional authority — governs all written output.

**Tests:** 111 passing, 0 failures.

## ORGANVM Context

This repository is part of the **ORGANVM** eight-organ creative-institutional system.
It belongs to **ORGAN IV (Orchestration)** under the `organvm-iv-taxis` GitHub organization.

**Registry:** [`registry-v2.json`](https://github.com/meta-organvm/organvm-corpvs-testamentvm/blob/main/registry-v2.json)
**Corpus:** [`organvm-corpvs-testamentvm`](https://github.com/meta-organvm/organvm-corpvs-testamentvm)

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-IV (Orchestration) | **Tier:** flagship | **Status:** GRADUATED
**Org:** `organvm-iv-taxis` | **Repo:** `orchestration-start-here`

### Edges
- **Produces** → `unspecified`: artifact

### Siblings in Orchestration
`petasum-super-petasum`, `universal-node-network`, `.github`, `agentic-titan`, `agent--claude-smith`, `a-i--skills`, `tool-interaction-design`, `system-governance-framework`, `reverse-engine-recursive-run`, `collective-persona-operations`

### Governance
- *Standard ORGANVM governance applies*

*Last synced: 2026-03-21T13:20:59Z*

## Session Review Protocol

At the end of each session that produces or modifies files:
1. Run `organvm session review --latest` to get a session summary
2. Check for unimplemented plans: `organvm session plans --project .`
3. Export significant sessions: `organvm session export <id> --slug <slug>`
4. Run `organvm prompts distill --dry-run` to detect uncovered operational patterns

Transcripts are on-demand (never committed):
- `organvm session transcript <id>` — conversation summary
- `organvm session transcript <id> --unabridged` — full audit trail
- `organvm session prompts <id>` — human prompts only


## Active Directives

| Scope | Phase | Name | Description |
|-------|-------|------|-------------|
| system | any | prompting-standards | Prompting Standards |
| system | any | research-standards-bibliography | APPENDIX: Research Standards Bibliography |
| system | any | phase-closing-and-forward-plan | METADOC: Phase-Closing Commemoration & Forward Attack Plan |
| system | any | research-standards | METADOC: Architectural Typology & Research Standards |
| system | any | sop-ecosystem | METADOC: SOP Ecosystem — Taxonomy, Inventory & Coverage |
| system | any | autonomous-content-syndication | SOP: Autonomous Content Syndication (The Broadcast Protocol) |
| system | any | autopoietic-systems-diagnostics | SOP: Autopoietic Systems Diagnostics (The Mirror of Eternity) |
| system | any | background-task-resilience | background-task-resilience |
| system | any | cicd-resilience-and-recovery | SOP: CI/CD Pipeline Resilience & Recovery |
| system | any | community-event-facilitation | SOP: Community Event Facilitation (The Dialectic Crucible) |
| system | any | context-window-conservation | context-window-conservation |
| system | any | conversation-to-content-pipeline | SOP — Conversation-to-Content Pipeline |
| system | any | cross-agent-handoff | SOP: Cross-Agent Session Handoff |
| system | any | cross-channel-publishing-metrics | SOP: Cross-Channel Publishing Metrics (The Echo Protocol) |
| system | any | data-migration-and-backup | SOP: Data Migration and Backup Protocol (The Memory Vault) |
| system | any | document-audit-feature-extraction | SOP: Document Audit & Feature Extraction |
| system | any | dynamic-lens-assembly | SOP: Dynamic Lens Assembly |
| system | any | essay-publishing-and-distribution | SOP: Essay Publishing & Distribution |
| system | any | formal-methods-applied-protocols | SOP: Formal Methods Applied Protocols |
| system | any | formal-methods-master-taxonomy | SOP: Formal Methods Master Taxonomy (The Blueprint of Proof) |
| system | any | formal-methods-tla-pluscal | SOP: Formal Methods — TLA+ and PlusCal Verification (The Blueprint Verifier) |
| system | any | generative-art-deployment | SOP: Generative Art Deployment (The Gallery Protocol) |
| system | any | market-gap-analysis | SOP: Full-Breath Market-Gap Analysis & Defensive Parrying |
| system | any | mcp-server-fleet-management | SOP: MCP Server Fleet Management (The Server Protocol) |
| system | any | multi-agent-swarm-orchestration | SOP: Multi-Agent Swarm Orchestration (The Polymorphic Swarm) |
| system | any | network-testament-protocol | SOP: Network Testament Protocol (The Mirror Protocol) |
| system | any | open-source-licensing-and-ip | SOP: Open Source Licensing and IP (The Commons Protocol) |
| system | any | performance-interface-design | SOP: Performance Interface Design (The Stage Protocol) |
| system | any | pitch-deck-rollout | SOP: Pitch Deck Generation & Rollout |
| system | any | polymorphic-agent-testing | SOP: Polymorphic Agent Testing (The Adversarial Protocol) |
| system | any | promotion-and-state-transitions | SOP: Promotion & State Transitions |
| system | any | recursive-study-feedback | SOP: Recursive Study & Feedback Loop (The Ouroboros) |
| system | any | repo-onboarding-and-habitat-creation | SOP: Repo Onboarding & Habitat Creation |
| system | any | research-to-implementation-pipeline | SOP: Research-to-Implementation Pipeline (The Gold Path) |
| system | any | security-and-accessibility-audit | SOP: Security & Accessibility Audit |
| system | any | session-self-critique | session-self-critique |
| system | any | smart-contract-audit-and-legal-wrap | SOP: Smart Contract Audit and Legal Wrap (The Ledger Protocol) |
| system | any | source-evaluation-and-bibliography | SOP: Source Evaluation & Annotated Bibliography (The Refinery) |
| system | any | stranger-test-protocol | SOP: Stranger Test Protocol |
| system | any | strategic-foresight-and-futures | SOP: Strategic Foresight & Futures (The Telescope) |
| system | any | styx-pipeline-traversal | SOP: Styx Pipeline Traversal (The 7-Organ Transmutation) |
| system | any | system-dashboard-telemetry | SOP: System Dashboard Telemetry (The Panopticon Protocol) |
| system | any | the-descent-protocol | the-descent-protocol |
| system | any | the-membrane-protocol | the-membrane-protocol |
| system | any | theoretical-concept-versioning | SOP: Theoretical Concept Versioning (The Epistemic Protocol) |
| system | any | theory-to-concrete-gate | theory-to-concrete-gate |
| system | any | typological-hermeneutic-analysis | SOP: Typological & Hermeneutic Analysis (The Archaeology) |

Linked skills: cicd-resilience-and-recovery, continuous-learning-agent, evaluation-to-growth, genesis-dna, multi-agent-workforce-planner, promotion-and-state-transitions, quality-gate-baseline-calibration, repo-onboarding-and-habitat-creation, structural-integrity-audit


**Prompting (Anthropic)**: context 200K tokens, format: XML tags, thinking: extended thinking (budget_tokens)


## Ecosystem Status

- **delivery**: 2/2 live, 0 planned
- **content**: 0/1 live, 1 planned

Run: `organvm ecosystem show orchestration-start-here` | `organvm ecosystem validate --organ IV`


## Task Queue (from pipeline)

**7** pending tasks | Last pipeline: unknown

- `782d0cd0916e` CHANGELOG.md — EDIT
- `137b05854caa` 1. Praxis-perpetua structure mapping — COMPLETE [bash, mcp, python]
- `cef79aa9684a` 2. Corpus governance documentation — COMPLETE [bash, mcp, python]
- `2a69a4cde207` 3. Orchestration scripts inventory — COMPLETE [bash, mcp, python]
- `db5b98816944` 4. Engine CLI subcommands — COMPLETE [bash, mcp, python]
- `dd5f9e285ca3` 5. MCP server tool count — COMPLETE [bash, mcp, python]
- `eb85ad178653` 4. Archiving

Cross-organ links: 591 | Top tags: `mcp`, `python`, `bash`, `pytest`, `fastapi`

Run: `organvm atoms pipeline --write && organvm atoms fanout --write`


## Entity Identity (Ontologia)

**UID:** `ent_repo_01KKKX3RVPM7DRFFFEK98P0GRW` | **Matched by:** primary_name

Resolve: `organvm ontologia resolve orchestration-start-here` | History: `organvm ontologia history ent_repo_01KKKX3RVPM7DRFFFEK98P0GRW`


## Live System Variables (Ontologia)

| Variable | Value | Scope | Updated |
|----------|-------|-------|---------|
| `active_repos` | 62 | global | 2026-03-21 |
| `archived_repos` | 53 | global | 2026-03-21 |
| `ci_workflows` | 104 | global | 2026-03-21 |
| `code_files` | 23121 | global | 2026-03-21 |
| `dependency_edges` | 55 | global | 2026-03-21 |
| `operational_organs` | 8 | global | 2026-03-21 |
| `published_essays` | 0 | global | 2026-03-21 |
| `repos_with_tests` | 47 | global | 2026-03-21 |
| `sprints_completed` | 0 | global | 2026-03-21 |
| `test_files` | 4337 | global | 2026-03-21 |
| `total_organs` | 8 | global | 2026-03-21 |
| `total_repos` | 116 | global | 2026-03-21 |
| `total_words_formatted` | 740,907 | global | 2026-03-21 |
| `total_words_numeric` | 740907 | global | 2026-03-21 |
| `total_words_short` | 741K+ | global | 2026-03-21 |

Metrics: 9 registered | Observations: 8632 recorded
Resolve: `organvm ontologia status` | Refresh: `organvm refresh`


## System Density (auto-generated)

AMMOI: 54% | Edges: 28 | Tensions: 33 | Clusters: 5 | Adv: 3 | Events(24h): 14977
Structure: 8 organs / 117 repos / 1654 components (depth 17) | Inference: 98% | Organs: META-ORGANVM:66%, ORGAN-I:55%, ORGAN-II:47%, ORGAN-III:56% +4 more
Last pulse: 2026-03-21T13:20:54 | Δ24h: n/a | Δ7d: n/a


## Dialect Identity (Trivium)

**Dialect:** GOVERNANCE_LOGIC | **Classical Parallel:** Rhetoric | **Translation Role:** The Meta-Logic — governance rules ARE propositions

Strongest translations: I (formal), V (structural), META (structural)

Scan: `organvm trivium scan IV <OTHER>` | Matrix: `organvm trivium matrix` | Synthesize: `organvm trivium synthesize`

<!-- ORGANVM:AUTO:END -->


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
