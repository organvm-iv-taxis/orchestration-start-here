# Plan: N/A Vacuum Audit & Remediation

**Date:** 2026-03-25
**Session:** S35
**Scope:** System-wide — context generator, density layer, atoms pipeline, ecosystem metrics
**Priority:** P1 (rendering bug) + P2 (strategic gaps)

---

## Summary

Six N/A vacuums identified in the auto-generated CLAUDE.md context. Three are bugs (fixable now), three are strategic gaps (already tracked in IRF). This plan addresses the bugs.

---

## Vacuum Inventory

| # | Surface | Root Cause | Type | Fix Location |
|---|---------|------------|------|--------------|
| V1 | `Δ24h: n/a \| Δ7d: n/a` | Python truthiness bug — `0.0` is falsy | **Bug** | `contextmd/generator.py:656-657` + `pulse/ammoi.py:287-288` |
| V2 | Inter-Organ Edges: placeholder text | Hardcoded string, never computed | **Bug** | `contextmd/generator.py:271` |
| V3 | `Last pipeline: unknown` | Pipeline doesn't persist execution metadata | **Bug** | `cli/atoms.py:cmd_atoms_pipeline()` |
| V4 | `content: 0/1 live, 1 planned` | No content delivery arm has reached live | Strategic | IRF-LOG-001 |
| V5 | `sprints_completed: 0` | System uses sessions, not sprints | Strategic | Metric-reality mismatch |
| V6 | `published_essays: 0` | 741K words, zero through pipeline | Strategic | IRF-LOG-001, IRF-LOG-004 |

---

## V1: Density Delta Rendering Bug

### Diagnosis
- **History exists**: 773 AMMOI snapshots, `~/.organvm/pulse/ammoi-history.jsonl`, 2.9MB, March 14—present
- **Computation works**: `_compute_temporal_deltas()` finds closest snapshot within 50% window, computes difference
- **Delta is genuinely 0.0**: System density stable at 52.5% — no change IS the correct answer
- **Rendering bug**: `if d24h else "n/a"` treats 0.0 as falsy

### Fix (2 files)

**File 1:** `src/organvm_engine/pulse/ammoi.py`
- `_compute_temporal_deltas()` currently returns `(0.0, 0.0, 0.0)` for BOTH "no historical data" and "no change"
- Change return type to `tuple[float | None, float | None, float | None]`
- Return `None` when `_find_closest()` returns `None` (no data), `0.0` when delta is genuinely zero
- Update `AMMOI` dataclass fields `density_delta_24h/7d/30d` to `float | None = None`
- Update `to_dict()`, `from_dict()` to handle None

```python
# Before (ammoi.py:287-288):
delta_24h = current_density - d24 if d24 is not None else 0.0
delta_7d = current_density - d7 if d7 is not None else 0.0

# After:
delta_24h = current_density - d24 if d24 is not None else None
delta_7d = current_density - d7 if d7 is not None else None
```

**File 2:** `src/organvm_engine/contextmd/generator.py`
```python
# Before (generator.py:656-657):
d24h_str = f"{'+' if d24h > 0 else ''}{d24h:.1%}" if d24h else "n/a"
d7d_str = f"{'+' if d7d > 0 else ''}{d7d:.1%}" if d7d else "n/a"

# After:
d24h_str = f"{'+' if d24h > 0 else ''}{d24h:.1%}" if d24h is not None else "n/a"
d7d_str = f"{'+' if d7d > 0 else ''}{d7d:.1%}" if d7d is not None else "n/a"
```

### Tests to update
- `tests/test_pulse_density.py` — verify delta returns None for empty history
- `tests/test_pulse_ammoi.py` — verify AMMOI serialization with None deltas
- `tests/test_contextmd.py` — verify "n/a" only when data missing, "+0.0%" when stable

---

## V2: Inter-Organ Edges Placeholder

### Diagnosis
- `contextmd/generator.py:271` hardcodes: `organ_edges_block="- *Edges computed from system-wide seed graph*"`
- The `SeedGraph` in `seed/graph.py` already computes cross-organ edges (used by density module)
- The context generator never queries it

### Fix
- In the organ-map generator function, compute edges from SeedGraph
- Format as markdown table: `| Source Organ | → | Target Organ | Edge Type | Count |`
- Fallback to placeholder if SeedGraph unavailable

---

## V3: Pipeline Audit Trail

### Diagnosis
- `cli/atoms.py:cmd_atoms_pipeline()` runs 7 stages, prints results, writes atomized tasks
- Never persists: timestamp, duration, success/failure, item counts
- Context generator has no data source for "Last pipeline" field

### Fix
- After pipeline completion, write `pipeline-manifest.json` (already printed at stage 7 but not persisted as structured data)
- Add fields: `last_run_at`, `duration_seconds`, `stages_completed`, `total_atoms`, `status`
- Context generator reads manifest timestamp for "Last pipeline" field

---

## V5: Sprint Metric Mismatch

### Observation
The system works in **sessions** (S1-S35+), not sprints. The `sprints_completed: 0` metric accurately reflects that no formal sprints have been run — but it also creates a perpetual vacuum in every CLAUDE.md.

### Options
1. **Redefine**: Map sessions to sprint-like cycles (e.g., every 5 sessions = 1 sprint)
2. **Replace**: Rename to `work_cycles_completed` and count session clusters
3. **Acknowledge**: Add a note in the context generator: "sessions-based (not sprint-based)"
4. **Remove**: Drop the metric if it doesn't map to reality

### Recommendation
Option 3 for now — the metric infra should stay for when/if formal sprints are adopted. Add a conditional render: if `sprints_completed == 0`, show "sessions-based" instead of "0".

---

## Execution Order

1. V1 (density delta bug) — highest impact, smallest change, unblocks accurate self-description
2. V2 (edge computation) — medium impact, wires existing code into template
3. V3 (pipeline audit trail) — enables pipeline monitoring
4. V5 (sprint metric) — cosmetic, lowest priority

V4 and V6 are strategic work tracked elsewhere (IRF-LOG-001/004).

---

## IRF Updates Needed

| IRF ID | Action |
|--------|--------|
| IRF-MON-004 | **Revise**: Not a "missing snapshots" problem — 773 exist. Root cause is Python truthiness bug + semantic ambiguity in return types |
| NEW: IRF-MON-006 | Inter-organ edges placeholder — context generator never computes edges from SeedGraph |
| NEW: IRF-MON-007 | Sprint metric mismatch — system is session-based, metric assumes sprint-based |
