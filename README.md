# orchestration-start-here

**Central orchestration hub for the organvm eight-organ system.**

This repository contains the registry, governance rules, automation workflows, and validation scripts that coordinate ~79 repositories across 8 GitHub organizations.

## What This Repository Contains

| File | Purpose |
|------|---------|
| `registry.json` | Machine-readable source of truth for all 79 repos — status, dependencies, promotion state, portfolio relevance |
| `governance-rules.json` | Constitutional articles, amendments, quality gates, and promotion criteria |
| `.github/workflows/` | 5 GitHub Actions workflows for automated governance |
| `scripts/` | Python scripts for audit and validation |

## The Eight-Organ System

| Organ | Domain | Organization | Repos |
|-------|--------|-------------|-------|
| I | Theory (Theoria) | [organvm-i-theoria](https://github.com/organvm-i-theoria) | 18 |
| II | Art (Poiesis) | [organvm-ii-poiesis](https://github.com/organvm-ii-poiesis) | 22 |
| III | Commerce (Ergon) | [organvm-iii-ergon](https://github.com/organvm-iii-ergon) | 21 |
| IV | Orchestration (Taxis) | [organvm-iv-taxis](https://github.com/organvm-iv-taxis) | 9 |
| V | Public Process (Logos) | [organvm-v-logos](https://github.com/organvm-v-logos) | 2 |
| VI | Community (Koinonia) | [organvm-vi-koinonia](https://github.com/organvm-vi-koinonia) | 3 |
| VII | Marketing (Kerygma) | [organvm-vii-kerygma](https://github.com/organvm-vii-kerygma) | 4 |
| VIII | Meta | [meta-organvm](https://github.com/meta-organvm) | 0 (hub) |

## Governance Rules

Six constitutional articles govern the system:

1. **Registry as Single Source of Truth** — All repo state lives in `registry.json`
2. **Unidirectional Dependencies** — Flow is I→II→III only; no back-edges
3. **All Eight Organs Visible** — Each organ has at least one representative
4. **Documentation Precedes Deployment** — No Phase N+1 until Phase N is complete
5. **Portfolio-Quality Documentation** — Every README passes the "Stranger Test"
6. **Promotion State Machine** — LOCAL → CANDIDATE → PUBLIC_PROCESS → GRADUATED → ARCHIVED

## Workflows

| Workflow | Status | Trigger | Purpose |
|----------|--------|---------|---------|
| `validate-dependencies` | Functional | PR / manual | Block merges that violate dependency rules |
| `monthly-organ-audit` | Functional | 1st of month / manual | Full system health check with issue report |
| `promote-repo` | Draft | Issue comment | Handle Theory→Art→Commerce promotions |
| `publish-process` | Skeleton | Issue comment | Automate ORGAN-V essay creation |
| `distribute-content` | Skeleton | Issue label | POSSE distribution to social channels |

## Quick Start

### Run a dependency validation

```bash
python3 scripts/validate-deps.py \
  --registry registry.json \
  --governance governance-rules.json
```

### Run a full organ audit

```bash
python3 scripts/organ-audit.py \
  --registry registry.json \
  --governance governance-rules.json \
  --output audit-report.md
```

### Trigger the monthly audit manually

Go to **Actions** → **Monthly Organ Audit** → **Run workflow**

## Architecture

```
Trigger Event
    ↓
Read Central Registry (registry.json)
    ↓
Apply Governance Rules (governance-rules.json)
    ↓
Execute Actions (validate, audit, promote, publish, distribute)
    ↓
Update Registry + Create Audit Trail
```

All workflows are data-driven: logic lives in JSON files, not workflow code.

## Related Resources

- [ORGAN-V Essays](https://github.com/organvm-v-logos/public-process/tree/main/essays/meta-system) — Meta-system essays about orchestration and governance
- [Planning Corpus](https://github.com/meta-organvm) — Full planning documentation
- [Constitution](governance-rules.json) — Machine-readable governance rules

---

*Part of the [organvm eight-organ system](https://github.com/meta-organvm) — ORGAN-IV: Orchestration (Taxis)*
