# F-53: Conductor Playbook — Aggregate Reference

> **Governance**: `governance-rules.json` Articles I-VI, Amendment E
> **Scope**: Consolidated quick-reference for all governance, schema, and operational rules
> **Version**: 1.0
> **Status**: Reference Document
> **Backlog**: F-53
> **Related**: `conductor-playbook.md` (session lifecycle detail)

---

## About This Document

This is the aggregate reference companion to `conductor-playbook.md`. Where the playbook describes the session lifecycle in depth, this document consolidates all governance primitives into a quick-reference format suitable for printing, PDF export, or GitHub Pages publishing.

Each section is a self-contained one-pager. Read them independently or sequentially.

---

## Quick Reference 1: Governance Configuration

**Source**: `governance-rules.json`

### Articles

| Article | Title | Summary |
|---|---|---|
| I | Registry as Source of Truth | `registry.json` is the single canonical file for all repo metadata |
| II | Dependency Flow | Unidirectional: I→II→III. IV orchestrates all. V observes. VII consumes. |
| III | Promotion States | Five states: LOCAL → CANDIDATE → PUBLIC_PROCESS → GRADUATED → ARCHIVED |
| IV | Tier System | Three tiers: flagship (strategic), standard (active), infrastructure (supporting) |
| V | Audit Cadence | Monthly system audit via `organ-audit.py`. Results in `audit-report.md` |
| VI | Seed Contracts | Every repo must have `seed.yaml` declaring organ, tier, edges, subscriptions |

### Amendment E: Session Lifecycle

All development work follows FRAME → SHAPE → BUILD → PROVE → DONE. Hard gates between phases. Back-transitions allowed (BUILD → SHAPE). No phase skipping.

### Enforcement

| Rule | Enforced By |
|---|---|
| No back-edge dependencies | `validate-deps.py` (CI) |
| Seed schema compliance | `seed.yaml` JSON Schema validation (CI) |
| Registry integrity | `save_registry()` minimum-50-entry guard |
| Promotion criteria | `organ-audit.py` documentation checks |
| Session phases | Conductor MCP server phase gates |

---

## Quick Reference 2: Seed Contract Schema (v1.0)

**Source**: `docs/seed-schema/`

### Required Fields

| Field | Type | Values |
|---|---|---|
| `schema_version` | string | `"1.0"` |
| `organ` | string | `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `META` |
| `name` | string | Repo name (kebab-case, double-hyphen for function-descriptor) |
| `tier` | enum | `flagship`, `standard`, `infrastructure` |
| `promotion_status` | enum | `LOCAL`, `CANDIDATE`, `PUBLIC_PROCESS`, `GRADUATED`, `ARCHIVED` |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `produces` | list | Edges: `[{target, type}]` — what this repo outputs |
| `consumes` | list | Edges: `[{source, type}]` — what this repo depends on |
| `subscriptions` | list | Events: `[{event, action}]` — event-driven triggers |
| `ci_agent` | object | CI configuration overrides |
| `tags` | list | Freeform classification tags |

### Example

```yaml
schema_version: "1.0"
organ: IV
name: orchestration-start-here
tier: flagship
promotion_status: PUBLIC_PROCESS
produces:
  - target: all
    type: governance-rules
  - target: agentic-titan, agent--claude-smith
    type: logic-as-code
consumes:
  - source: any
    type: registry-updates
subscriptions:
  - event: promotion.completed
    action: validate-deps
```

---

## Quick Reference 3: Promotion State Machine

**Source**: `governance-rules.json` Article III

### State Diagram

```
                    ┌──────────────────────────────────────────────┐
                    │              ARCHIVED                        │
                    └──────────────────────────────────────────────┘
                      ▲         ▲            ▲            ▲
                      │         │            │            │
LOCAL ──────► CANDIDATE ──────► PUBLIC_PROCESS ──────► GRADUATED
                      ◄──────────────────────────────────┘
                              (demotion allowed)
```

### Transition Criteria

| From | To | Requirements |
|---|---|---|
| LOCAL | CANDIDATE | `seed.yaml` present and valid, CI workflow exists and green, `README.md` with purpose statement |
| CANDIDATE | PUBLIC_PROCESS | Architecture documentation, test suite with passing tests, `CHANGELOG.md`, no lint errors, contributing guide |
| PUBLIC_PROCESS | GRADUATED | 30-day soak period at PUBLIC_PROCESS, security review completed, external usage demonstrated, maintenance plan documented |
| GRADUATED | ARCHIVED | Successor repo identified OR sunset plan documented, migration guide if consumers exist |
| Any | ARCHIVED | Explicit archive decision with rationale |
| Higher | Lower | Quality regression documented, remediation plan filed |

### Current Distribution

Track live distribution via: `python3 scripts/calculate-metrics.py`

---

## Quick Reference 4: AI Interaction Model

**Source**: `conductor-playbook.md`, Amendment E

### Three Roles

| Role | Responsibilities |
|---|---|
| **Director** (Human) | Define scope, approve designs, review outputs, promote or reject |
| **Generator** (AI Agent) | Explore code, draft designs, generate implementations, run validations |
| **Reviewer** (Human) | Verify correctness, assess quality, make promotion decisions |

### Session Lifecycle

| Phase | Activities | Exit Criteria |
|---|---|---|
| **FRAME** | Read code, check issues, identify constraints, ask questions | Scope statement written |
| **SHAPE** | Design approach, draft plan, identify risks | Human approves design |
| **BUILD** | Generate code, write tests, create documentation | All artifacts produced |
| **PROVE** | Run tests, lint, audit, verify against scope | All checks pass, human reviews |
| **DONE** | Archive session, update registry, file issues for follow-ups | Session closed |

### Hard Rules

- No phase skipping (FRAME → BUILD is forbidden)
- Back-transitions allowed (BUILD → SHAPE for redesign)
- AI never self-promotes — human gates every transition
- Session artifacts persisted for audit trail
- Effort measured in LLM tokens, not hours

---

## Quick Reference 5: Quality Ladders by Tier

### Flagship Repos

Flagship repos are strategic — they define the system's core capabilities.

| Quality Dimension | Requirement |
|---|---|
| Documentation | Full architecture docs, API reference, user guide, deployment guide |
| Testing | Unit + integration + E2E tests, coverage ≥80% |
| CI/CD | Full pipeline: lint → typecheck → test → build → deploy |
| Security | Dependency scanning, secret detection, security review documented |
| Monitoring | Health checks, error tracking, usage metrics |
| Maintenance | Named maintainer, response SLA, upgrade schedule |

### Standard Repos

Standard repos are active contributors to the system.

| Quality Dimension | Requirement |
|---|---|
| Documentation | README, CHANGELOG, seed.yaml, architecture overview |
| Testing | Unit tests, coverage ≥60% |
| CI/CD | Lint → test → build pipeline |
| Security | Dependency scanning, secret detection |
| Monitoring | CI status badge |
| Maintenance | Reviewed quarterly |

### Infrastructure Repos

Infrastructure repos provide supporting services (org profiles, templates, CI configs).

| Quality Dimension | Requirement |
|---|---|
| Documentation | README, seed.yaml |
| Testing | Validation scripts where applicable |
| CI/CD | Basic CI (lint or validate) |
| Security | Secret detection |
| Monitoring | None required |
| Maintenance | Updated as needed |

---

## Quick Reference 6: Naming Conventions

### Repo Naming

- **kebab-case**: Words separated by single hyphens (`orchestration-start-here`)
- **Double-hyphen**: Separates function from descriptor (`agent--claude-smith`, `a-i--skills`)
- **Org prefix not in repo name**: The GitHub org provides the namespace

### File Naming

| File | Convention |
|---|---|
| `seed.yaml` | Always at repo root, always this exact name |
| `CLAUDE.md` | AI assistant context, at repo root |
| `CHANGELOG.md` | Conventional Commits format |
| `governance-rules.json` | In `orchestration-start-here` only |
| `registry.json` | In `orchestration-start-here` only |
| `organ-aesthetic.yaml` | In each org's `.github` repo |

### Branch Naming

- `feature/descriptive-name` — new capabilities
- `fix/descriptive-name` — bug fixes
- `docs/descriptive-name` — documentation only
- `chore/descriptive-name` — maintenance, CI, dependencies

### Commit Messages

Conventional Commits in imperative mood, under 72 characters:

```
feat: add promotion gate validation to CI pipeline
fix: correct back-edge detection for ORGAN-V edges
docs: update seed schema to v1.0 with subscription fields
chore: sync organvm-iv-taxis submodule pointers
```

---

## Quick Reference 7: Organ Topology

### Dependency Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  I: Theoria  │────►│  II: Poiesis  │────►│  III: Ergon  │
│  (Theory)    │     │  (Creation)   │     │  (Products)  │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                    ┌──────────────┐             │
                    │  IV: Taxis   │◄────────────┘
                    │  (Orchestr.) │──────► all organs
                    └──────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
      ┌────────────┐ ┌──────────┐ ┌───────────┐
      │ V: Logos   │ │VI: Koin. │ │VII: Keryg.│
      │ (Discourse)│ │(Community│ │(Distribn.)│
      └────────────┘ └──────────┘ └───────────┘

      META: Cross-cutting governance (spine)
```

### GitHub Organizations

| Organ | GitHub Org |
|---|---|
| I | `organvm-i-theoria` |
| II | `omni-dromenon-machina` |
| III | `organvm-iii-ergon` |
| IV | `organvm-iv-taxis` |
| V | (TBD) |
| VI | `organvm-vi-koinonia` |
| VII | `organvm-vii-kerygma` |
| META | `meta-organvm` |

---

## Quick Reference 8: Common Commands

### System Health

```bash
# Full system audit
cd orchestration-start-here && python3 scripts/organ-audit.py

# Dependency validation (detect back-edges)
python3 scripts/validate-deps.py

# Registry metrics
python3 scripts/calculate-metrics.py

# Conductor system status (if MCP available)
python3 -m conductor patch --json
```

### Per-Repo Operations

```bash
# Validate seed contract
organvm seed validate

# Check promotion eligibility
organvm promote check --repo <name>

# Sync registry from seeds
organvm registry sync

# Run session lifecycle
conductor session start --organ IV --repo orchestration-start-here
```

### AI Skills

```bash
# Validate skills collection
cd a-i--skills && python3 scripts/validate_skills.py --collection example --unique

# Refresh build artifacts
python3 scripts/refresh_skill_collections.py

# Health check single skill
python3 scripts/skill_health_check.py --skill mcp-builder
```

---

## Document Map

This reference consolidates information from:

| Source Document | Quick Reference |
|---|---|
| `governance-rules.json` | QR1: Governance Configuration |
| `docs/seed-schema/` | QR2: Seed Contract Schema |
| `governance-rules.json` Article III | QR3: Promotion State Machine |
| `conductor-playbook.md` | QR4: AI Interaction Model |
| Tier definitions (Articles III-IV) | QR5: Quality Ladders |
| Convention docs, CLAUDE.md | QR6: Naming Conventions |
| `governance-rules.json` Article II | QR7: Organ Topology |
| Scripts, CLI tools | QR8: Common Commands |
