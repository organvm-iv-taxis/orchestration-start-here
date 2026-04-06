# Substrate Threshold Topology — Governance Radius of Effects

**Date:** 2026-04-06
**Scope:** `organvm-iv-taxis/orchestration-start-here/`
**Status:** PLAN

## Context

Current governance is **topologically flat**. `governance-rules.json` has 6 articles + 8 amendments — all apply at a single level with no concept of depth, radius, or containment. The ORGAN-IV obituary confirmed: petasum, collective-persona-operations, and system-governance-framework had **zero executable enforcement**. Governance exists as declarations but not as membranes.

The UMFAS derivation (2026-04-06) confirmed the 8 organs are 3 layers + 1 substrate. The Atomic Clock (SOP-SYS-004) defines 4 depth tiers. Neither has been instantiated as a governance topology.

**Goal:** Create a 2D governance membrane model where UMFAS scopes define WHAT governance applies and Atomic Clock depths define HOW DEEP it reaches. Each boundary (threshold) has defined permeability — what governance passes through going up, down, and laterally. Rules that currently float free become visible as UNPLUGGED vacuums.

## The Grid: 4 Scopes × 4 Depths = 16 Threshold Cells

```
              SUBSTRATE    CONTROL      PRODUCTION    INTERFACE
              (META)       (IV/Taxis)   (I→II→III)    (V→VI→VII)
ORGANISM      T(S,O)       T(C,O)       T(P,O)        T(I,O)
COMPOUND      T(S,C)       T(C,C)       T(P,C)        T(I,C)
MOLECULE      T(S,M)       T(C,M)       T(P,M)        T(I,M)
ATOM          T(S,A)       T(C,A)       T(P,A)        T(I,A)
```

**Scope axis (UMFAS — what domain):**
- **SUBSTRATE** (META) — constitutional, universal authority
- **CONTROL** (IV/Taxis) — orchestration, cross-organ enforcement
- **PRODUCTION** (I→II→III) — creative pipeline, commercial delivery
- **INTERFACE** (V→VI→VII) — discourse, community, distribution

**Depth axis (Atomic Clock — how granular):**
- **ORGANISM** — system-wide (the whole synthesizer)
- **COMPOUND** — per-organ (one of the 8 organs)
- **MOLECULE** — per-repo (one git repository)
- **ATOM** — per-file/action (one script, one CI step, one session)

## Threshold Properties

Each cell T(scope, depth) carries:

```json
{
  "id": "T(S,O)",
  "scope": "SUBSTRATE",
  "depth": "ORGANISM",
  "radius_down": 3,
  "radius_up": 0,
  "radius_lateral": 3,
  "permeability": {
    "down": 1.0,
    "up": 0.0,
    "lateral": 1.0
  },
  "local_rules": ["art_I", "art_III", "amend_H"]
}
```

| Property | Type | Meaning |
|----------|------|---------|
| `radius_down` | int 0-3 | Depth levels downward this threshold's rules reach |
| `radius_up` | int 0-3 | Depth levels upward |
| `radius_lateral` | int 0-3 | Scope columns reachable (0 = local scope only) |
| `permeability.down` | 0.0-1.0 | How much external governance passes through going down |
| `permeability.up` | 0.0-1.0 | How much passes through going up |
| `permeability.lateral` | 0.0-1.0 | How much passes through laterally |
| `local_rules` | string[] | Rule IDs that originate at this threshold |

**Radius = how far a rule reaches from its origin.** Permeability = how much governance from OUTSIDE passes through this threshold boundary. They are complementary: radius is outbound reach, permeability is inbound acceptance.

## Rule Classification

Each existing governance rule gets `origin_threshold` and radius annotations:

| Rule | Origin | r_down | r_lat | Rationale |
|------|--------|--------|-------|-----------|
| Art. I (Registry as truth) | T(S,O) | 3 | 3 | Constitutional — universal |
| Art. II (Unidirectional deps) | T(C,C) | 2 | 2 | Cross-organ, reaches repos+atoms |
| Art. III (All organs visible) | T(S,O) | 0 | 3 | Organism-only, all scopes |
| Art. IV (Doc precedes deploy) | T(C,C) | 1 | 2 | Organ-level, reaches repos |
| Art. V (Portfolio-quality) | T(I,C) | 1 | 0 | Interface organs, reaches repos |
| Art. VI (Promotion FSM) | T(S,C) | 1 | 3 | All organs, down to repo level |
| Amend. A (Bronze tier) | T(S,C) | 1 | 3 | Promotion strategy, all organs |
| Amend. B (Coordination budget) | T(C,O) | 2 | 1 | Control-level overhead |
| Amend. C (Registry schema) | T(S,M) | 1 | 3 | Per-repo schema compliance |
| Amend. D (AI non-determinism) | T(C,O) | 3 | 3 | Universal — all AI output |
| Amend. E (Session lifecycle) | T(C,M) | 1 | 2 | Per-session, reaches atoms |
| Amend. F (Agent coordination) | T(C,M) | 1 | 2 | Per-session, breadcrumbs |
| Amend. G (Score/Rehearse/Perform) | T(C,M) | 1 | 2 | Per-PR lifecycle |
| Amend. H (Temporal manifest.) | T(S,O) | 3 | 3 | Meta-axiom — universal |
| seed.yaml contracts | T(*,M) | 1 | 0 | Per-repo, local only |
| COMMANDMENTS.md | **UNPLUGGED** | — | — | No enforcement path |
| promote-to-art rule | T(C,C) | 1 | 1 | I→II transition |
| promote-to-commerce rule | T(C,C) | 1 | 1 | II→III transition |
| WIP limits | T(C,C) | 1 | 3 | Per-organ, warn-only |

## Hardening Waves

Progressive, not all-at-once. Each wave is atomic — system stays valid between waves.

### Wave 0: Define the Grid
- Create `governance-thresholds.json` with 16 cells
- Default permeability: SUBSTRATE cells = {down: 1.0, up: 0.0, lateral: 1.0}, others = {down: 0.8, up: 0.2, lateral: 0.5}
- No rules classified yet — just the topology

### Wave 1: Classify Existing Rules
- Add `origin_threshold`, `radius_down`, `radius_up`, `radius_lateral` to each rule in `governance-rules.json`
- Validator checks: does any rule's declared radius exceed what's physically possible from its origin?

### Wave 2: Classify Repositories
- Each seed.yaml gets a `governance_threshold` field placing it in the grid
- Validator checks: is this repo governed by rules whose radius actually reaches it?

### Wave 3: Discover Vacuums
- **UNPLUGGED rules**: exist but have no threshold assignment (governance debt)
- **EMPTY thresholds**: cells with no originating rules (governance gaps)
- **UNREACHABLE repos**: repos no rule's radius reaches (orphans)
- All reported as first-class findings, not silent absences

### Wave N: Progressive Tightening
- Subsequent waves plug more governance into the grid
- Permeability values tighten as enforcement matures
- Mesh hardens from organism→atom, substrate→interface

## Artifacts to Create

### 1. `governance-thresholds.json` (NEW)

Location: `orchestration-start-here/governance-thresholds.json`

Schema:
```json
{
  "schema_version": "1.0",
  "axes": {
    "scope": ["SUBSTRATE", "CONTROL", "PRODUCTION", "INTERFACE"],
    "depth": ["ORGANISM", "COMPOUND", "MOLECULE", "ATOM"]
  },
  "scope_mapping": {
    "SUBSTRATE": { "organs": ["META"], "description": "Constitutional authority" },
    "CONTROL": { "organs": ["IV"], "description": "Orchestration enforcement" },
    "PRODUCTION": { "organs": ["I", "II", "III"], "description": "Creative pipeline" },
    "INTERFACE": { "organs": ["V", "VI", "VII"], "description": "Outward-facing" }
  },
  "depth_mapping": {
    "ORGANISM": { "level": 0, "unit": "system", "description": "The whole synthesizer" },
    "COMPOUND": { "level": 1, "unit": "organ", "description": "One of the 8 organs" },
    "MOLECULE": { "level": 2, "unit": "repo", "description": "One git repository" },
    "ATOM": { "level": 3, "unit": "file", "description": "One script, CI step, or action" }
  },
  "thresholds": {
    "T(S,O)": { "scope": "SUBSTRATE", "depth": "ORGANISM", "radius_down": 3, "radius_up": 0, "radius_lateral": 3, "permeability": { "down": 1.0, "up": 0.0, "lateral": 1.0 }, "local_rules": [] },
    "...": "... (16 cells total)"
  },
  "wave": 0,
  "hardening_log": []
}
```

### 2. `governance-rules.json` (EXTEND)

Location: `orchestration-start-here/governance-rules.json` (existing)

Add to each article/amendment:
```json
{
  "I": {
    "title": "Registry as Single Source of Truth",
    "rule": "...",
    "enforcement": "automated",
    "threshold": {
      "origin": "T(S,O)",
      "radius_down": 3,
      "radius_up": 0,
      "radius_lateral": 3,
      "wave_classified": 1
    }
  }
}
```

### 3. `scripts/validate-thresholds.py` (NEW)

Location: `orchestration-start-here/scripts/validate-thresholds.py`

Reads:
- `governance-thresholds.json` (topology)
- `governance-rules.json` (annotated rules)
- All `seed.yaml` files found via git submodule paths

Validates:
- No rule's radius exceeds physical possibility from its origin
- No rule reaches a threshold whose permeability blocks it
- Every repo's seed.yaml is governed by at least one rule that reaches it
- Reports: PLUGGED, UNPLUGGED, EMPTY, UNREACHABLE

Output format:
```
=== Threshold Topology Validation ===
Wave: 1 | Thresholds: 16 | Rules: 19 | Repos: 128

PLUGGED (14/19):
  Art.I    T(S,O) → r_down=3 r_lat=3  ✓ reaches 128/128 repos
  Art.II   T(C,C) → r_down=2 r_lat=2  ✓ reaches 97/97 prod+iface repos
  ...

UNPLUGGED (2/19):
  COMMANDMENTS.md — no origin_threshold assigned
  quality_gates.completeness — enforcement path undefined

EMPTY (7/16 thresholds):
  T(I,A), T(I,M), T(P,A), T(P,M), T(S,A), T(S,M), T(C,A)

UNREACHABLE (0/128 repos): ✓ All governed
```

### 4. `docs/threshold-topology.md` (NEW)

Location: `orchestration-start-here/docs/threshold-topology.md`

Prose companion explaining the membrane model, the two axes, the hardening wave strategy, and how to read the validator output. Not a replacement for the schema — a companion for human comprehension.

## Implementation Steps

### Step 1: Create `governance-thresholds.json`
- Define the 16-cell grid with axes, mappings, and default permeability
- Wave 0 — no rules classified yet
- **File:** `orchestration-start-here/governance-thresholds.json`

### Step 2: Annotate `governance-rules.json`
- Add `threshold` object to each of the 6 articles and 8 amendments
- Add `threshold` to the 2 promotion rules and WIP limits
- Mark quality_gates with threshold origins
- Wave 1 — rules classified
- **File:** `orchestration-start-here/governance-rules.json`

### Step 3: Write `validate-thresholds.py`
- Read topology + rules + seed.yaml files
- Validate radius constraints and permeability
- Report plugged/unplugged/empty/unreachable
- Follow existing `validate-deps.py` patterns (same directory, same CLI style)
- **File:** `orchestration-start-here/scripts/validate-thresholds.py`

### Step 4: Write `docs/threshold-topology.md`
- Prose explanation of the membrane model
- The grid diagram
- How hardening waves work
- How to read validator output
- **File:** `orchestration-start-here/docs/threshold-topology.md`

### Step 5: Run validation
- Execute `python3 scripts/validate-thresholds.py` against the current state
- Confirm Wave 0/1 output is coherent
- Fix any schema issues

## Critical Files

| File | Action | Purpose |
|------|--------|---------|
| `orchestration-start-here/governance-thresholds.json` | CREATE | 16-cell threshold topology |
| `orchestration-start-here/governance-rules.json` | EXTEND | Add threshold annotations to existing rules |
| `orchestration-start-here/scripts/validate-thresholds.py` | CREATE | Executable enforcement |
| `orchestration-start-here/scripts/validate-deps.py` | READ | Pattern to follow for validator style |
| `orchestration-start-here/docs/threshold-topology.md` | CREATE | Prose companion |
| `orchestration-start-here/seed.yaml` | READ | Understand existing contract schema |

## Existing Code to Reuse

- **`scripts/validate-deps.py`** — CLI pattern, exit codes, JSON loading, seed.yaml discovery
- **`governance-rules.json`** — existing schema to extend (not replace)
- **`seed.yaml` schema** — `organ`, `metadata.tier`, `metadata.promotion_status` already classify repos by organ/tier

## Verification

1. `python3 orchestration-start-here/scripts/validate-thresholds.py` exits 0 with coherent Wave 1 report
2. All 14 articles/amendments have valid `threshold` annotations
3. Every threshold cell in `governance-thresholds.json` has valid permeability values (0.0-1.0)
4. Validator correctly identifies COMMANDMENTS.md as UNPLUGGED
5. Validator correctly reports which threshold cells are EMPTY
6. No existing tests break (`pytest orchestration-start-here/tests/ -v`)
7. `python3 orchestration-start-here/scripts/validate-deps.py` still passes (extending, not breaking)
