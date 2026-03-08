# F-50: Package ORGANVM Orchestration Framework

> **Governance**: `governance-rules.json` Article I (Registry as Source of Truth)
> **Scope**: Extraction of ORGANVM into a standalone MIT-licensed package
> **Version**: 1.0
> **Status**: Design Document
> **Backlog**: F-50

---

## Why This Exists

The ORGANVM system has evolved from a personal creative-institutional framework into a reusable pattern for orchestrating multi-repo ecosystems. The current implementation is tightly coupled to the specific eight-organ topology. This document designs the extraction of core primitives into a standalone package that others can adopt — cloning the approach, not just the code.

The goal is not to open-source the entire system, but to distill the governance primitives that make the system work: seed contracts, promotion state machines, dependency validation, and registry management.

---

## Components to Extract

### 1. organvm-engine (Core Library)

The Python package that provides:

- **Registry management**: Load, validate, query, and update a `registry.json` file tracking all repos in the system
- **Seed contract parser**: Read and validate `seed.yaml` files declaring repo metadata, edges, and subscriptions
- **Promotion state machine**: Enforce the `LOCAL → CANDIDATE → PUBLIC_PROCESS → GRADUATED → ARCHIVED` lifecycle with no state skipping
- **Dependency graph validator**: Detect back-edges in the organ dependency graph and reject forbidden flows
- **Metrics calculator**: Compute system health metrics from registry + CI data

### 2. Schema Definitions

- **seed.yaml v1.0 schema**: JSON Schema for validating seed contracts
- **registry.json schema**: JSON Schema for the system registry
- **governance-rules.json schema**: JSON Schema for governance configuration
- **organ-aesthetic.yaml schema**: Optional visual identity metadata

### 3. Promotion State Machine

States and transitions:

```
LOCAL ──────► CANDIDATE ──────► PUBLIC_PROCESS ──────► GRADUATED ──────► ARCHIVED
  │                                                                        ▲
  └────────────────────────────────────────────────────────────────────────┘
                              (direct archive from any state)
```

Promotion criteria encoded per-transition:

| Transition | Requirements |
|---|---|
| LOCAL → CANDIDATE | seed.yaml present, CI green, README exists |
| CANDIDATE → PUBLIC_PROCESS | Docs complete, tests passing, no lint errors |
| PUBLIC_PROCESS → GRADUATED | 30-day soak, external usage, security review |
| GRADUATED → ARCHIVED | Successor identified or sunset plan documented |

### 4. Seed Contracts

The `seed.yaml` file is the per-repo automation contract:

```yaml
# seed.yaml v1.0 — minimal example
schema_version: "1.0"
organ: III
name: my-product
tier: standard
promotion_status: CANDIDATE
produces:
  - target: all
    type: api-events
consumes:
  - source: orchestration-start-here
    type: governance-rules
subscriptions:
  - event: promotion.completed
    action: notify
```

### 5. Dependency-Graph Validator

Enforces unidirectional flow between organs:

- **Allowed**: I → II → III (theory feeds creation feeds products)
- **Orchestrator**: IV may depend on any organ
- **Observer**: V reads from all, writes to none
- **Consumer**: VII consumes from all, produces to none
- **Back-edges**: Forbidden and automatically rejected

---

## Starter Templates

Each organ archetype gets a starter template:

| Archetype | Description | Example |
|---|---|---|
| **Theory** | Research, engines, symbolic computing | ORGAN-I pattern |
| **Creation** | Generative art, performance, creative coding | ORGAN-II pattern |
| **Product** | Commercial tools, SaaS, developer utilities | ORGAN-III pattern |
| **Orchestrator** | Governance, CI, agent infrastructure | ORGAN-IV pattern |
| **Discourse** | Publishing, essays, editorial | ORGAN-V pattern |
| **Community** | Learning groups, salons, forums | ORGAN-VI pattern |
| **Distribution** | POSSE, social automation, announcements | ORGAN-VII pattern |
| **Meta** | Cross-cutting governance, dashboards | META pattern |

Each template includes:

- Pre-configured `seed.yaml` with archetype defaults
- README template with ORGANVM context section
- CI workflow template (GitHub Actions)
- CLAUDE.md template for AI-assisted development
- `.github/` community health files

---

## 4-Tier Maturity Model

### Tier 1: Single Repo with Seed Contract

**Target audience**: Individual developers wanting structured repo metadata.

- Install `organvm` as a dev dependency
- Run `organvm init` to generate `seed.yaml`
- Validate with `organvm seed validate`
- No registry, no multi-repo coordination

**Deliverables**: CLI tool, seed schema, validation logic.

### Tier 2: Multi-Repo with Registry

**Target audience**: Teams managing 5-30 repos.

- Create `registry.json` tracking all repos
- Run `organvm registry sync` to reconcile seed files with registry
- Dependency graph visualization
- Promotion status tracking

**Deliverables**: Registry schema, sync commands, graph visualization.

### Tier 3: Full Governance with CI

**Target audience**: Organizations managing 30-100 repos.

- GitHub Actions workflows for automated validation
- Promotion gate enforcement in CI
- Drift detection (registry vs reality)
- Audit reports and health dashboards

**Deliverables**: CI templates, audit scripts, dashboard components.

### Tier 4: Self-Sustaining with Metrics

**Target audience**: Mature ecosystems with autonomous governance.

- Automated promotion recommendations
- System-wide metrics (coverage, drift, health scores)
- AI-conductor integration for session management
- Event-driven orchestration across repos

**Deliverables**: Metrics engine, promotion recommender, event bus integration.

---

## Extraction Timeline

```
Phase 1: Core Extraction (Weeks 1-4)
├── Week 1: Extract seed schema + validator into standalone package
├── Week 2: Extract promotion state machine + tests
├── Week 3: Extract registry management + dependency validator
└── Week 4: CLI scaffolding (organvm init, validate, sync)

Phase 2: Templates & Docs (Weeks 5-8)
├── Week 5: Create starter templates for each archetype
├── Week 6: Write getting-started guide + API reference
├── Week 7: Build example "mini-organvm" with 3 repos
└── Week 8: Package for PyPI, write CONTRIBUTING.md

Phase 3: CI & Governance (Weeks 9-12)
├── Week 9:  GitHub Actions workflow templates
├── Week 10: Drift detection + audit scripts
├── Week 11: Dashboard components (optional web UI)
└── Week 12: Beta release, gather feedback

Phase 4: Maturity & Metrics (Weeks 13-16)
├── Week 13: Metrics engine extraction
├── Week 14: Promotion recommender
├── Week 15: Event bus integration patterns
└── Week 16: v1.0 release
```

---

## Package Structure

```
organvm/
├── pyproject.toml          # MIT license, Python >=3.11
├── src/
│   └── organvm/
│       ├── __init__.py
│       ├── cli.py          # Click-based CLI
│       ├── seed.py         # Seed contract parser + validator
│       ├── registry.py     # Registry management
│       ├── promotion.py    # State machine
│       ├── deps.py         # Dependency graph validator
│       ├── metrics.py      # Health metrics
│       └── schemas/
│           ├── seed-v1.0.json
│           ├── registry.json
│           └── governance.json
├── templates/
│   ├── theory/
│   ├── creation/
│   ├── product/
│   └── ...
├── tests/
├── docs/
└── examples/
    └── mini-organvm/       # 3-repo example system
```

---

## Philosophy: Clone the Approach, Not Just the Code

The ORGANVM package is not a framework that imposes structure. It is a toolkit that encodes governance patterns discovered through operating a 100+ repo ecosystem. Adopters should:

1. **Start with seed contracts** — even a single `seed.yaml` adds value by making repo metadata explicit and machine-readable
2. **Add governance incrementally** — the maturity tiers are not gates; they are options
3. **Adapt the organ model** — the eight-organ topology is one instantiation; the primitives (bounded contexts, unidirectional flow, promotion gates) are universal
4. **Keep humans in the loop** — the AI-conductor model assumes human direction; automation amplifies judgment, it does not replace it

The package succeeds when someone can run `organvm init` in a repo and immediately benefit from structured metadata — without needing to understand the full eight-organ system.

---

## References

- `governance-rules.json` — Articles I-VI defining governance constraints
- `registry.json` — Current system registry (~100 repos)
- `seed-schema/` — Seed contract schema definitions
- `scripts/validate-deps.py` — Dependency graph validator (extraction source)
- `scripts/calculate-metrics.py` — Metrics calculator (extraction source)
