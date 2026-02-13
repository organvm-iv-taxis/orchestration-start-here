# Flow Patterns

Central definitions for inter-organ communication in the omni-dromenon metasystem.

## Overview

This directory contains the canonical definitions for how artifacts flow between the 7 organs of the metasystem.

## Files

| File | Purpose |
|------|---------|
| `organ-flow-manifest.yaml` | Master organ definitions and flow rules |
| `gate-definitions.yaml` | Gate requirements and approval processes |
| `artifact-schemas.yaml` | Schemas for artifacts that flow between organs |

## The Seven Organs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   I (Origin)  ──→  II (Art)  ──→  III (Commerce)  ──→  V (Public)          │
│       ↑                                                      │              │
│       │                                                      ↓              │
│   VII (Marketing)  ←──  VI (Community)  ←────────────────────┘              │
│                                                                             │
│                         IV (Orchestration)                                  │
│                    [observes and coordinates all]                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Flow Summary

| Flow | From → To | Gate | Key Artifacts |
|------|-----------|------|---------------|
| Creation | I → II | none | seed.yaml, intent-manifests |
| Packaging | II → III | version-freeze | stable-releases, api-specs |
| Exposure | III → V | security-review | public-apis, documentation |
| Cultivation | V → VI | community-approval | contributor-onboarding |
| Amplification | VI → VII | quality-threshold | success-stories, metrics |
| Feedback | VII → I | synthesis-review | market-signals, user-research |

## Gate Types

1. **version-freeze**: Semantic versioning check before packaging
2. **security-review**: Automated + manual security audit
3. **community-approval**: RFC process for public changes
4. **quality-threshold**: Metrics-based release criteria
5. **synthesis-review**: Human synthesis of market feedback

## Usage

These files are read by:
- **Dreamcatcher router**: Enforces flow rules
- **Watchman**: Monitors for gate violations
- **Agents**: Understand their scope and boundaries

## Validation

```bash
# Validate YAML syntax
yamllint flow-patterns/*.yaml

# Validate against schemas (future)
dreamcatcher validate-flows
```

## Updates

Changes to flow patterns require:
1. RFC in ORG VI (Community)
2. Architect approval
3. Update to this directory
4. Propagation to all organ seed.yaml files
