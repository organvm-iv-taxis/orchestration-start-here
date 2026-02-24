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

## ORGANVM Context

This repository is part of the **ORGANVM** eight-organ creative-institutional system.
It belongs to **ORGAN IV (Orchestration)** under the `organvm-iv-taxis` GitHub organization.

**Registry:** [`registry-v2.json`](https://github.com/meta-organvm/organvm-corpvs-testamentvm/blob/main/registry-v2.json)
**Corpus:** [`organvm-corpvs-testamentvm`](https://github.com/meta-organvm/organvm-corpvs-testamentvm)

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-IV (Orchestration) | **Tier:** flagship | **Status:** PUBLIC_PROCESS
**Org:** `organvm-iv-taxis` | **Repo:** `orchestration-start-here`

### Edges
- **Produces** → `all`: governance-rules
- **Produces** → `all`: health-reports
- **Produces** → `all`: promotion-decisions
- **Consumes** ← `any`: registry-updates
- **Consumes** ← `ORGAN-V`: essay-notifications

### Siblings in Orchestration
`petasum-super-petasum`, `universal-node-network`, `.github`, `agentic-titan`, `agent--claude-smith`, `a-i--skills`

### Governance
- *Standard ORGANVM governance applies*

*Last synced: 2026-02-24T12:41:28Z*
<!-- ORGANVM:AUTO:END -->
