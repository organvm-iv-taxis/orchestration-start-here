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
📁 tasks/                # Portals — reality-rectification interventions between competing futures
    <slug>/
        CLAUDE.md        # Portal nature + counter-force field + lifecycle (INJECT→PRECIPITATE→STOP)
        BRIEFING.md      # War report: front line, utopic/dystopic attractors, deliverables
        REFERENCES.md    # Keys to doors + context stream + terrain (what the war is fought over)
        SEQUENCE.md      # Intervention procedure α→ε: inject, create, operate, verify, precipitate
        RECEIPT.md       # Forward deposit (written at completion, consumed by next portal)
📁 action_ledger/
    schemas.py          # Action, Sequence, Chain, Route, ParamAxis, ParamRegistry, ActionOrigin
    ledger.py           # record() atomic, compose_chain(), close_session(), emit_session_closed(), YAML persistence
    emissions.py        # State change emission — self-recording transitions via emit_state_change()
    routes.py           # Patch bay — bidirectional route graph, lineage tracing, provenance
    cycles.py           # Cycle detection — verb sequences, trajectories, intents, stalls
    cli.py              # CLI: record, show (--origin filter), sequence, chain, routes, cycles, params
    __main__.py         # Standalone entry: python -m action_ledger
    data/               # Append-only YAML streams: actions, sequences, param_registry
📁 docs/
    adr
    autonomous-systems-design.md
    coordination-protocols
    flow-patterns
    metasystem-manifest
    seed-schema
    superproject-topology-audit.md
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
- `docs/superproject-topology-audit.md` — SOP for structural auditing of git superprojects (7+1 steps, proven across 5 agents). Tool: `meta-organvm/tools/superproject_topology_audit.py`

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

**Core modules:** `scanner.py` (4 signal sources + scoring), `orchestrator.py` (workspace init), `monitor.py` (PR lifecycle + absorption trigger), `capabilities.py` (8 capability definitions), `schemas.py` (40 Pydantic models incl. 8 StrEnum + 1 IntEnum), `github_client.py` (gh CLI wrapper), `cli.py` (dual-mode prefix registration).

**Campaign modules (S32):** `campaign.py` (phase sequencer: UNBLOCK→ENGAGE→CULTIVATE→HARVEST→INJECT), `outreach.py` (relationship scoring, event logging), `backflow.py` (6-organ routing: theory/generative/code/narrative/community/distribution).

**Absorption Protocol (S35):** `absorption.py` (inbound question detection → auto-formalization → backflow deposit). Scans tracked conversations for expansion-worthy questions using 8 heuristics + 6 reduction filters. Runs autonomously inside the monitor cycle. Protocol doc: `docs/absorption-protocol.md`.

**Fieldwork Intelligence (S-fieldwork-mvp):** `fieldwork.py` (process observations from contribution workflows). Layer 1 of 4-layer system. Records observations with 10 categories, 5-level spectrum (AVOID to ABSORB as IntEnum), 6 strategic tags, 6 sources. CLI: `fieldwork record` + `fieldwork show`. Spec: `docs/superpowers/specs/2026-03-30-fieldwork-intelligence-system-design.md`.

```bash
python -m contrib_engine fieldwork record --workspace WS --category CAT --signal "..." --spectrum N --source SRC
python -m contrib_engine fieldwork show [--workspace WS] [--category CAT] [--min-spectrum N]
```

**Data files** (committed, living state): `data/campaign.yaml` (15 actions, income-weighted), `data/outreach.yaml` (10 relationships), `data/backflow.yaml` (13 deposited items), `data/absorption.yaml` (4 detected + formalized), `data/tracked_conversations.yaml` (conversation URLs for absorption scanning), `data/ranked_targets.yaml` (scanner output), `data/fieldwork.yaml` (observation stream, append-only, created on first write).

**Artifacts:** `artifacts/dbt-mcp-patterns-absorption.md` (5 architectural patterns absorbed from dbt-mcp contribution). 4 render scripts in `artifacts/` (canvas, post001, post002, post002-audit) — standalone, no CLI integration (IRF-OSS-029).

**Testament:** 13 articles of codified writing rules formalized into logic/algorithms/math at `docs/testament-formalization.md`. Constitutional authority — governs all written output.

**Tests:** 240 passing, 0 failures.

## Action Ledger (`action_ledger/`)

System-wide process recording infrastructure — the synthesizer paradigm applied to ideas. Records semantic actions as they move through parameter space, composes them into sequences and chains, detects repeated cycles across sessions.

```bash
python -m action_ledger record --session S42 --verb explored --target fieldwork \
  --context "understanding Layer 1 MVP" --param abstraction=0.7 --param maturity=0.3
python -m action_ledger show [--session S42] [--verb explored] [--origin emitted] [--routes]
python -m action_ledger sequence show [--session S42]
python -m action_ledger sequence close --session S42 [--outcome "patterns reusable"]
python -m action_ledger chain close-session --session S42 [--essence "built recording infra"]
python -m action_ledger routes from <action_id>
python -m action_ledger routes to <target>
python -m action_ledger routes lineage <action_id> [--depth 3]
python -m action_ledger cycles [--min-recurrence 2] [--type verb_sequence|trajectory|intent|stall]
python -m action_ledger params
```

**Core modules:** `schemas.py` (Action, Sequence, Chain, Route, ParamAxis, ParamRegistry, ActionOrigin — open parameter model), `ledger.py` (atomic record() that appends+composes+registers; `close_session()` closes sequences+composes chain, `emit_session_closed()` emits AFTER caller persists — avoids stale-read race), `emissions.py` (self-recording state changes — `emit_state_change()` auto-records transitions as ledger entries with `origin: emitted`), `routes.py` (bidirectional route graph, lineage tracing, provenance injection), `cycles.py` (4 detection methods: verb sequences, trajectories, intents, stalls).

**Data files** (committed, living state): `data/actions.yaml` (append-only action stream), `data/sequences.yaml` (composed sequences with automation lanes), `data/param_registry.yaml` (discovered parameter axes).

**Conceptual prior art:** Alchemical Synthesizer (ORGAN-II) — module registry → parameter registry, patch bay → route system, CHRONOS automation → parameter trajectories, Euclidean rhythms → cycle detection.

**Design spec:** `.claude/plans/scalable-baking-conway.md`

## Intake Router (`intake_router/`)

Keyword-based operator intake router for low-token dispatch. Classifies messy ideas into routing domains, resolves the target workspace/archetype/agent, emits both the manual intake and the routed follow-up into the action ledger, and prints a ready-to-paste execution prompt sourced from the archetype plan.

```bash
python -m intake_router intake "third function build for a-organvm"
python -m intake_router table
python -m intake_router history [--domain organism] [--limit 10]
```

**Core modules:** `router.py` (keyword classification, routing table, archetype prompt loading, ledger emission), `cli.py` (standalone argparse entrypoints: intake/table/history), `__main__.py` (module entry).

**Ledger integration:** emits `received_intake` (manual) and `routed_intake` (emitted) actions with `subsystem: intake_router`, plus `RouteKind.FEEDS` routes to the destination workspace/archetype.

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
- **Produces** → `unspecified`: governance_rules
- **Produces** → `unspecified`: registry_data
- **Produces** → `unspecified`: dependency_validation
- **Produces** → `unspecified`: audit_reports
- **Produces** → `unspecified`: campaign_data
- **Produces** → `unspecified`: outreach_data
- **Produces** → `unspecified`: backflow_data
- **Produces** → `unspecified`: testament_formalization
- **Produces** → `unspecified`: absorption_data
- **Produces** → `unspecified`: fieldwork_data
- **Produces** → `unspecified`: action_ledger_data
- **Consumes** ← `unspecified`: github_pr_states
- **Consumes** ← `unspecified`: github_issue_states

### Siblings in Orchestration
`petasum-super-petasum`, `universal-node-network`, `.github`, `agentic-titan`, `agent--claude-smith`, `a-i--skills`, `tool-interaction-design`, `system-governance-framework`, `reverse-engine-recursive-run`, `collective-persona-operations`, `contrib--adenhq-hive`, `contrib--ipqwery-ipapi-py`, `contrib--primeinc-github-stars`, `contrib--temporal-sdk-python`, `contrib--dbt-mcp` ... and 2 more

### Governance
- *Standard ORGANVM governance applies*

*Last synced: 2026-04-03T15:19:55Z*

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
| system | any | atomic-clock | The Atomic Clock |
| system | any | execution-sequence | Execution Sequence |
| system | any | multi-agent-dispatch | Multi-Agent Dispatch |
| system | any | session-handoff-avalanche | Session Handoff Avalanche |
| system | any | system-loops | System Loops |
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
| unknown | any | communications-correspondence | SOP: Communications & Correspondence — Relay Protocol |
| unknown | any | war-master-protocol | SOP: War-Master Protocol |
| unknown | any | SOP-github-project-setup | SOP: GitHub Project Board Setup from Template |

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


## System Density (auto-generated)

AMMOI: 56% | Edges: 41 | Tensions: 0 | Clusters: 0 | Adv: 12 | Events(24h): 27428
Structure: 8 organs / 128 repos / 1654 components (depth 17) | Inference: 0% | Organs: META-ORGANVM:64%, ORGAN-I:55%, ORGAN-II:47%, ORGAN-III:55% +4 more
Last pulse: 2026-04-03T15:19:54 | Δ24h: -0.0% | Δ7d: n/a


## Dialect Identity (Trivium)

**Dialect:** GOVERNANCE_LOGIC | **Classical Parallel:** Rhetoric | **Translation Role:** The Meta-Logic — governance rules ARE propositions

Strongest translations: I (formal), V (structural), META (structural)

Scan: `organvm trivium scan IV <OTHER>` | Matrix: `organvm trivium matrix` | Synthesize: `organvm trivium synthesize`


## Logos Documentation Layer

**Status:** MISSING | **Symmetry:** 0.5 (GHOST)

Nature demands a documentation counterpart. This formation maintains its narrative record in `docs/logos/`.

### The Tetradic Counterpart
- **[Telos (Idealized Form)](../docs/logos/telos.md)** — The dream and theoretical grounding.
- **[Pragma (Concrete State)](../docs/logos/pragma.md)** — The honest account of what exists.
- **[Praxis (Remediation Plan)](../docs/logos/praxis.md)** — The attack vectors for evolution.
- **[Receptio (Reception)](../docs/logos/receptio.md)** — The account of the constructed polis.

### Alchemical I/O
- **[Source & Transmutation](../docs/logos/alchemical-io.md)** — Narrative of inputs, process, and returns.

- **[Public Essay](https://organvm-v-logos.github.io/public-process/)** — System-wide narrative entry.

*Compliance: Implementation exists without record.*

<!-- ORGANVM:AUTO:END -->

## Active Handoff Protocol

If `.conductor/active-handoff.md` exists, **READ IT FIRST** before doing any work.
It contains constraints, locked files, conventions, and completed work from the
originating agent. You MUST honor all constraints listed there.

If the handoff says "CROSS-VERIFICATION REQUIRED", your self-assessment will
NOT be trusted. A different agent will verify your output against these constraints.


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
