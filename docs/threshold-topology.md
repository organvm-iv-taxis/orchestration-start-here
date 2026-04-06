# Threshold Topology — Governance Radius of Effects

The membrane model for ORGANVM governance. Two axes, sixteen thresholds, selective permeability.

## The Problem

Governance-rules.json codifies 6 articles + 8 amendments — all flat. Every rule nominally applies system-wide. No concept of depth (how granular?), containment (what's inside what?), or radius (how far does this rule reach?). The result: either everything is governed by everything (noise), or enforcement is aspirational (silence).

The ORGAN-IV obituary confirmed the failure: petasum-super-petasum, collective-persona-operations, and system-governance-framework declared governance but enforced nothing.

## The Model

Two axes, unified:

**UMFAS scope** (what domain) — derived from the Universal Modular Fractal Alchemical Synthesizer's 3-layer + 1 substrate topology:
- **SUBSTRATE** (META-ORGANVM) — constitutional authority
- **CONTROL** (ORGAN-IV) — orchestration enforcement
- **PRODUCTION** (ORGAN-I → II → III) — creative pipeline
- **INTERFACE** (ORGAN-V → VI → VII) — outward-facing

**Atomic Clock depth** (how granular) — derived from the universal sequencing primitive (SOP-SYS-004):
- **ORGANISM** — the whole synthesizer
- **COMPOUND** — one organ
- **MOLECULE** — one repo
- **ATOM** — one file, CI step, or action

The grid:

```
              SUBSTRATE    CONTROL      PRODUCTION    INTERFACE
              (META)       (IV/Taxis)   (I→II→III)    (V→VI→VII)
ORGANISM      T(S,O)       T(C,O)       T(P,O)        T(I,O)
COMPOUND      T(S,C)       T(C,C)       T(P,C)        T(I,C)
MOLECULE      T(S,M)       T(C,M)       T(P,M)        T(I,M)
ATOM          T(S,A)       T(C,A)       T(P,A)        T(I,A)
```

Each cell is a **threshold** — a governance membrane with selective permeability.

## Threshold Properties

Every threshold carries:

| Property | What it means |
|----------|---------------|
| `radius_down` (0-3) | How many depth levels downward this threshold's rules reach |
| `radius_up` (0-3) | How many depth levels upward |
| `radius_lateral` (0-3) | How many scope columns it can reach |
| `permeability.down` (0.0-1.0) | How much external governance passes through going down |
| `permeability.up` (0.0-1.0) | How much passes through going up |
| `permeability.lateral` (0.0-1.0) | How much passes through laterally |
| `local_rules` | Rule IDs that originate at this threshold |

**Radius** = outbound reach. How far a rule extends from its origin.
**Permeability** = inbound acceptance. How much governance from outside passes through this boundary.

They are complementary: a rule at T(S,O) with `radius_down=3` reaches all 16 cells. But a cell at T(P,A) with `permeability.up=0.2` only accepts 20% of what arrives from above.

## How Rules Are Classified

Every governance rule (article, amendment, promotion rule, quality gate, WIP limit) gets:
- **origin** — which threshold cell it lives at
- **radius_down / radius_up / radius_lateral** — how far it reaches

Example: Article I (Registry as Single Source of Truth) lives at T(S,O) with radius 3×3 — constitutional, reaches everything. Amendment E (Session Lifecycle) lives at T(C,M) with radius_down=1, radius_lateral=2 — per-session, reaches atoms, spans production and interface scopes.

## Hardening Waves

The topology hardens progressively, not all-at-once:

1. **Wave 0** — Define the 16-cell grid with default permeability. No rules classified.
2. **Wave 1** — Classify existing governance rules. Each gets an origin + radius.
3. **Wave 2** — Classify repositories. Each seed.yaml gets a threshold assignment.
4. **Wave 3** — Discover vacuums: unplugged rules, empty cells, unreachable repos.
5. **Wave N** — Progressive tightening. Permeability values decrease as enforcement matures.

Each wave is atomic — the system stays valid between waves.

## Reading the Validator Output

Run: `python3 scripts/validate-thresholds.py`

The report has four sections:

**PLUGGED** — Rules that have a threshold assignment and valid radius. Shows how many repos each rule reaches.

**UNPLUGGED** — Rules that exist but have no threshold assignment. This is governance debt — visible vacuums, not silent absences.

**EMPTY** — Threshold cells with no originating rules. These are governance gaps — no local governance exists at this scope×depth.

**UNREACHABLE** — Repos that no rule's radius reaches. Governance orphans.

## Files

| File | Purpose |
|------|---------|
| `governance-thresholds.json` | The 16-cell topology with axes, mappings, permeability |
| `governance-rules.json` | Existing rules extended with `threshold` annotations |
| `scripts/validate-thresholds.py` | Executable validator — the enforcement |
| `docs/threshold-topology.md` | This document |
