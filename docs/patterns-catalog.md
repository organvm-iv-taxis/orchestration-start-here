# F-51: ORGANVM Patterns Catalog

> **Governance**: `governance-rules.json` Articles I-VI
> **Scope**: Pattern language for the ORGANVM orchestration system
> **Version**: 1.0
> **Status**: Design Document
> **Backlog**: F-51

---

## About This Catalog

This catalog documents the recurring architectural patterns that govern the ORGANVM eight-organ system. Each pattern follows the Alexandrian structure: **Context**, **Forces**, **Solution**, **Resulting Context**, **Related Patterns**, and **Known Uses**. The patterns are interdependent — most require or benefit from the presence of others.

---

## Pattern 1: No Back Edges Governance

### Context

You are managing a multi-repo ecosystem where different domains (theory, creation, products, distribution) produce artifacts consumed by other domains. Teams or agents work across domains simultaneously.

### Forces

- Circular dependencies create coupling that makes independent evolution impossible
- Without explicit flow direction, repos accumulate implicit dependencies that are discovered only when something breaks
- In a system with 100+ repos, undirected dependency graphs become incomprehensible
- Developers naturally want to import utilities from wherever they exist, regardless of domain boundaries

### Solution

**Enforce strict unidirectional dependency flow between organ boundaries.** Define a topological ordering of organs and reject any dependency edge that flows against the ordering.

In ORGANVM, the ordering is:

```
I (Theory) → II (Creation) → III (Products)
IV (Orchestration) → all organs (hub, not a linear position)
V (Discourse) → reads from all, writes to none
VII (Distribution) → consumes from all, produces to none
```

Enforcement is automated: `validate-deps.py` reads every `seed.yaml` in the system, builds the dependency graph, and fails CI if any back-edge is detected. The script runs on every PR to `orchestration-start-here`.

### Resulting Context

- Each organ can be developed, tested, and deployed independently
- The dependency graph is always a DAG — no cycles, no deadlocks
- Teams can reason about impact: changes in ORGAN-I may affect II and III, never the reverse
- The orchestrator (IV) is the only node with edges to all others, making it the natural place for cross-cutting concerns

### Related Patterns

- [Organ Separation](#pattern-6-organ-separation) — defines the boundaries that No Back Edges enforces
- [Seed Contract](#pattern-4-seed-contract) — declares the edges that No Back Edges validates
- [Registry as Single Source of Truth](#pattern-5-registry-as-single-source-of-truth) — provides the global view for validation

### Known Uses

- **ORGANVM dependency validation**: `validate-deps.py` enforces this across 100+ repos
- **Hexagonal architecture**: Ports and adapters enforce dependency inversion at the module level — this pattern applies the same principle at the repo/organization level
- **Linux kernel subsystems**: Subsystem maintainers enforce directional dependency between kernel layers

---

## Pattern 2: Documentation-First Promotion

### Context

You have repos at various stages of maturity. Some are experimental sketches; others are production-ready. You need a way to distinguish them and ensure quality increases before wider adoption.

### Forces

- Code without documentation is a liability — it works until the author forgets why
- Requiring perfect documentation before any code discourages experimentation
- "We'll document it later" is a debt that compounds faster than technical debt
- Promotion decisions based purely on code quality miss the human-readable context that makes a repo maintainable

### Solution

**Make documentation completeness a gate for each promotion level.** Each state in the promotion state machine requires specific documentation artifacts:

| State | Required Documentation |
|---|---|
| LOCAL | None — experimentation is free |
| CANDIDATE | `seed.yaml`, `README.md` with purpose statement |
| PUBLIC_PROCESS | Architecture docs, API reference, CHANGELOG, contributing guide |
| GRADUATED | User guide, deployment docs, security review, maintenance plan |

The audit script (`organ-audit.py`) checks documentation presence at each level and flags repos that have been promoted beyond their documentation maturity.

### Resulting Context

- Documentation grows with the repo rather than being retrofitted
- The promotion state signals documentation quality, not just code quality
- New contributors can assess a repo's maturity by its promotion state
- The system self-documents: the registry tells you what exists and the docs tell you how it works

### Related Patterns

- [Promotion State Machine](#pattern-7-promotion-state-machine) — defines the states that documentation gates enforce
- [Seed Contract](#pattern-4-seed-contract) — the first documentation artifact required at CANDIDATE
- [AI Conductor Protocol](#pattern-3-ai-conductor-protocol) — AI agents generate documentation drafts during the SHAPE and PROVE phases

### Known Uses

- **ORGANVM promotion pipeline**: `organ-audit.py` validates documentation completeness per tier
- **Rust RFC process**: Features require an RFC document before implementation begins
- **Architecture Decision Records (ADRs)**: Decisions are documented before they are enacted
- **DORA metrics**: Documentation quality correlates with deployment frequency and change failure rate

---

## Pattern 3: AI Conductor Protocol

### Context

You use AI coding agents (Claude Code, Codex, Aider, etc.) to generate code, documentation, and configuration across many repos. The volume of output is high, but so is the risk of drift, hallucination, and context loss.

### Forces

- AI agents generate volume that exceeds human review capacity if unchecked
- Without structure, AI sessions produce scattered artifacts with no clear lifecycle
- AI-generated code that bypasses human review accumulates quality debt silently
- The value of AI is in amplification, not replacement — but the default mode is replacement

### Solution

**Establish a three-phase protocol: Human directs → AI generates → Human reviews.** Every AI-assisted session follows the FRAME → SHAPE → BUILD → PROVE lifecycle:

1. **FRAME**: Human defines scope. AI explores, reads, asks questions. No code produced.
2. **SHAPE**: Human approves scope. AI designs approach. Human reviews design.
3. **BUILD**: AI generates code within approved scope. Changes are atomic and reviewable.
4. **PROVE**: AI runs tests, lints, audits. Human reviews results and promotes or rejects.

The protocol is enforced by session management: the Conductor MCP server tracks phase transitions and prevents phase skipping. Session artifacts (plans, diffs, test results) are persisted for audit.

### Resulting Context

- Human judgment gates every phase transition — AI never promotes its own work
- Session artifacts create an audit trail showing what was directed, what was generated, and what was reviewed
- The volume advantage of AI is preserved while the quality advantage of human review is maintained
- AI agents become predictable collaborators rather than unpredictable autonomous actors

### Related Patterns

- [Documentation-First Promotion](#pattern-2-documentation-first-promotion) — AI generates documentation during SHAPE and PROVE
- [WIP Limits](#pattern-8-wip-limits) — constrains the number of simultaneous AI sessions
- [Promotion State Machine](#pattern-7-promotion-state-machine) — session completion triggers promotion evaluation

### Known Uses

- **ORGANVM conductor playbook**: `conductor-playbook.md` codifies the four-phase lifecycle
- **Pair programming**: The driver/navigator model is the two-person analog
- **GitHub Copilot Workspace**: Specification → Plan → Implementation → Review follows the same shape
- **Architecture review boards**: Design approval before implementation is a governance pattern older than software

---

## Pattern 4: Seed Contract

### Context

You manage many repos, each with different owners, stacks, and purposes. You need machine-readable metadata to automate governance decisions without manual inspection.

### Forces

- READMEs are human-readable but not machine-parseable
- CI configuration describes how to build, not what the repo is or where it fits
- Without metadata, governance scripts must hardcode knowledge about individual repos
- Metadata formats proliferate (package.json, pyproject.toml, Cargo.toml) — none capture organizational context

### Solution

**Require every repo to declare a `seed.yaml` file** that captures organizational metadata in a standard schema:

```yaml
schema_version: "1.0"
organ: IV
name: orchestration-start-here
tier: flagship            # flagship | standard | infrastructure
promotion_status: PUBLIC_PROCESS
produces:
  - target: all
    type: governance-rules
consumes:
  - source: any
    type: registry-updates
subscriptions:
  - event: promotion.completed
    action: validate-deps
```

The schema is versioned (`schema_version: "1.0"`) and validated by CI. Fields are intentionally minimal — enough to drive automation, not so many that maintenance becomes a burden.

### Resulting Context

- Governance scripts operate on structured data rather than heuristics
- The registry can be rebuilt from seed files (seeds are authoritative, registry is derived)
- New repos get a seed file from a template — the metadata question is answered at creation time
- Edges (produces/consumes) make the system's data flow explicit and queryable

### Related Patterns

- [Registry as Single Source of Truth](#pattern-5-registry-as-single-source-of-truth) — aggregates seed data into a global view
- [No Back Edges Governance](#pattern-1-no-back-edges-governance) — validates the edges declared in seeds
- [Organ Separation](#pattern-6-organ-separation) — the `organ` field places the repo in its bounded context

### Known Uses

- **ORGANVM seed.yaml**: 100+ repos each declare a seed contract
- **Kubernetes labels and annotations**: Machine-readable metadata on every resource
- **npm package.json**: Declares dependencies, scripts, and metadata — seed.yaml does the same at the organization level
- **Backstage catalog-info.yaml**: Spotify's service catalog uses a similar per-repo metadata file

---

## Pattern 5: Registry as Single Source of Truth

### Context

You have many repos with seed contracts, but no single place to query the state of the whole system. Answering "how many repos are in CANDIDATE status?" requires scanning every repo.

### Forces

- Distributed metadata (one seed per repo) is authoritative but slow to query
- A central registry is fast to query but risks drifting from reality
- Multiple sources of truth create conflicting answers to the same question
- Governance decisions (promotion, audit, metrics) need a global view

### Solution

**Maintain a single `registry.json` file as the canonical aggregation of all seed data.** The registry is the queryable global view; seed files are the authoritative per-repo declarations. When they conflict, the reconciliation process updates the registry to match the seeds.

Rules:

- The registry file is protected: `save_registry()` refuses to write fewer than 50 entries (guards against test fixtures leaking into production)
- Updates flow: seed.yaml → registry sync → registry.json (never the reverse)
- The registry includes computed fields (last CI status, health score, last audit date) that are not in seeds
- One and only one file is the registry. No copies, no shards, no per-organ registries.

### Resulting Context

- Any governance query ("which repos lack CI?", "what is the promotion distribution?") resolves against a single file
- Drift between seeds and registry is detectable and reconcilable
- The registry file is version-controlled — its history shows how the system evolved
- Dashboards, audit scripts, and metrics all consume the same data source

### Related Patterns

- [Seed Contract](#pattern-4-seed-contract) — the authoritative per-repo data that feeds the registry
- [Documentation-First Promotion](#pattern-2-documentation-first-promotion) — promotion status is tracked in the registry
- [No Back Edges Governance](#pattern-1-no-back-edges-governance) — dependency validation reads from the registry

### Known Uses

- **ORGANVM registry.json**: ~100 entries, 2,200+ lines, single file in `orchestration-start-here`
- **Terraform state**: Single state file is the source of truth for all managed infrastructure
- **DNS root zone**: One authoritative root, delegated zones derive from it
- **Backstage software catalog**: Central catalog aggregated from per-repo catalog-info.yaml files

---

## Pattern 6: Organ Separation

### Context

Your creative or institutional system spans multiple domains: research, creation, products, governance, discourse, community, distribution. You need boundaries that allow independent evolution while maintaining system coherence.

### Forces

- Without boundaries, repos accumulate cross-domain dependencies that make the system brittle
- Too-rigid boundaries prevent the natural flow of ideas from research through creation to products
- Domain boundaries based on technology (frontend/backend) create artificial splits — boundaries should follow creative function
- One person operating the system cannot maintain cognitive context across all domains simultaneously

### Solution

**Partition repos into organs — bounded contexts defined by creative function, not technology.** Each organ has:

- A GitHub organization (namespace isolation)
- A visual identity (`organ-aesthetic.yaml` — palette, typography, tone)
- A tier system (flagship, standard, infrastructure)
- Explicit edges to other organs (declared in seed contracts, validated by dependency rules)

The eight-organ model:

| Organ | Function | Metaphor |
|---|---|---|
| I — Theoria | Foundational theory, symbolic computing | The mind |
| II — Poiesis | Generative art, performance systems | The hands |
| III — Ergon | Commercial products, developer tools | The workshop |
| IV — Taxis | Orchestration, governance, agents | The nervous system |
| V — Logos | Public discourse, essays, editorial | The voice |
| VI — Koinonia | Community, learning, salons | The gathering |
| VII — Kerygma | Distribution, social automation | The herald |
| META | Cross-cutting governance, dashboards | The spine |

### Resulting Context

- Each organ can be understood, developed, and discussed independently
- The creative pipeline (theory → creation → products) has a natural flow direction
- Governance (IV) and observation (V) are separated from production (I-III)
- The metaphor makes the system legible to humans, not just machines

### Related Patterns

- [No Back Edges Governance](#pattern-1-no-back-edges-governance) — enforces the flow direction between organs
- [Seed Contract](#pattern-4-seed-contract) — the `organ` field places each repo in its bounded context
- [Promotion State Machine](#pattern-7-promotion-state-machine) — promotion criteria may vary by organ tier

### Known Uses

- **ORGANVM eight-organ system**: 100+ repos across 8 GitHub organizations
- **Wardley Maps**: Value chain positioning separates genesis from commodity
- **Conway's Law**: System architecture mirrors communication structure — organs mirror creative workflow
- **Unix philosophy**: Small, composable programs with clear interfaces — organs are the macro-scale analog

---

## Pattern 7: Promotion State Machine

### Context

Repos exist at different levels of maturity. Without formal states, maturity is implicit — guessed from activity, documentation presence, or team knowledge.

### Forces

- Implicit maturity creates disagreement ("is this repo production-ready?")
- Without gates, repos get deployed before they are ready
- Without a lifecycle model, there is no path from experiment to production — repos either stay experimental forever or are prematurely treated as stable
- State transitions need criteria, not just intent — "I think it's ready" is not a promotion

### Solution

**Define an explicit state machine with five states and enforced transitions:**

```
LOCAL → CANDIDATE → PUBLIC_PROCESS → GRADUATED → ARCHIVED
```

Rules:

- **No state skipping**: A repo cannot jump from LOCAL to PUBLIC_PROCESS
- **Criteria per transition**: Each transition has documented requirements (see Documentation-First Promotion)
- **Back-transitions allowed**: GRADUATED → CANDIDATE is valid (demotion for quality regression)
- **Archive from any state**: A repo can be archived regardless of current state
- **Machine-enforced**: The promotion script validates criteria before allowing transitions

State semantics:

| State | Meaning |
|---|---|
| LOCAL | Experimental. No external consumers. May break at any time. |
| CANDIDATE | Structured. Has seed.yaml, CI, README. Ready for internal use. |
| PUBLIC_PROCESS | Documented. Architecture docs, tests, changelog. Ready for external visibility. |
| GRADUATED | Stable. Security reviewed, soak-tested, maintenance plan. Production-grade. |
| ARCHIVED | Retired. Successor identified or sunset plan documented. Read-only. |

### Resulting Context

- Every repo has an unambiguous maturity level
- Promotion decisions are explicit, documented, and auditable
- The system can report its maturity distribution (e.g., "72 CANDIDATE, 12 PUBLIC_PROCESS, 4 GRADUATED")
- Quality gates prevent premature deployment — experiments stay experiments until they earn promotion

### Related Patterns

- [Documentation-First Promotion](#pattern-2-documentation-first-promotion) — documentation is the primary gate for each transition
- [Registry as Single Source of Truth](#pattern-5-registry-as-single-source-of-truth) — promotion status is tracked centrally
- [WIP Limits](#pattern-8-wip-limits) — constrains how many repos can be in active promotion simultaneously

### Known Uses

- **ORGANVM promotion pipeline**: 100+ repos tracked through five states
- **Kubernetes API versioning**: alpha → beta → stable lifecycle with explicit promotion criteria
- **npm semver**: Major/minor/patch signals maturity — promotion states signal organizational maturity
- **CMMI maturity levels**: Organizational process maturity measured in levels with defined criteria

---

## Pattern 8: WIP Limits

### Context

You operate a large system with many repos that could be improved. The temptation is to start improving everything simultaneously. A single operator (with AI amplification) has high throughput but limited review bandwidth.

### Forces

- Starting many improvements simultaneously means finishing none
- AI agents can generate changes faster than a human can review them
- Context-switching between too many active workstreams degrades judgment quality
- Without limits, the system accumulates half-finished work that is worse than unstarted work

### Solution

**Limit the number of repos in active promotion (CANDIDATE with active work) to a maximum of 3 system-wide.** This applies to the human operator's attention, not to AI agent capacity.

Rules:

- At most 3 repos may have active promotion work (open PRs, in-progress issues, active sessions)
- A repo enters the WIP queue when promotion work begins and exits when promotion is completed or deferred
- If the limit is reached, new promotion work must wait or an existing workstream must be completed/deferred
- The limit applies to promotion work specifically — maintenance, bug fixes, and documentation updates are not counted

The limit is inspired by kanban WIP limits and calibrated to the observation that a single human can maintain deep context on at most 3 repos simultaneously.

### Resulting Context

- Active work is finished before new work begins — completion rate increases
- Review quality remains high because the human reviewer is not overloaded
- The system's promotion velocity is steady rather than bursty
- AI agents work deeply on fewer repos rather than shallowly on many

### Related Patterns

- [AI Conductor Protocol](#pattern-3-ai-conductor-protocol) — sessions are the unit of work that WIP limits constrain
- [Promotion State Machine](#pattern-7-promotion-state-machine) — WIP limits apply specifically to promotion transitions
- [Registry as Single Source of Truth](#pattern-5-registry-as-single-source-of-truth) — the registry shows which repos have active promotion work

### Known Uses

- **ORGANVM governance**: Max 3 active promotions enforced by convention (automation planned)
- **Kanban**: WIP limits are a core kanban principle — limiting work in progress improves flow
- **Theory of Constraints**: The bottleneck (human review bandwidth) determines system throughput — WIP limits protect the bottleneck
- **Agile sprint capacity**: Fixed capacity per sprint prevents overcommitment

---

## Pattern Index

| # | Pattern | Primary Force |
|---|---|---|
| 1 | [No Back Edges Governance](#pattern-1-no-back-edges-governance) | Prevent circular dependencies |
| 2 | [Documentation-First Promotion](#pattern-2-documentation-first-promotion) | Ensure docs grow with maturity |
| 3 | [AI Conductor Protocol](#pattern-3-ai-conductor-protocol) | Keep humans in the loop |
| 4 | [Seed Contract](#pattern-4-seed-contract) | Machine-readable repo metadata |
| 5 | [Registry as Single Source of Truth](#pattern-5-registry-as-single-source-of-truth) | One queryable global view |
| 6 | [Organ Separation](#pattern-6-organ-separation) | Bounded contexts by function |
| 7 | [Promotion State Machine](#pattern-7-promotion-state-machine) | Explicit maturity lifecycle |
| 8 | [WIP Limits](#pattern-8-wip-limits) | Protect review bandwidth |
