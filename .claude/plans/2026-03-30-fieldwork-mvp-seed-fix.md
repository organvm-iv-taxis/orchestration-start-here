# Fieldwork Intelligence System MVP + seed.yaml P0 Fix

## Context

The session close report from 2026-03-30 identified 6 vacuums. This session tackles the 3 **in-realm** items (Python / contrib_engine):

1. **P0: seed.yaml stale** — missing fieldwork/absorption modules, inaccurate test count, missing produces edge
2. **P1: Fieldwork MVP** — spec v4.0 approved, zero code exists, build `record()` + `FieldObservation` + YAML persistence + CLI
3. **P1: SIGNAL_REGISTRY.md** — deferred (belongs in `praxis-perpetua/`, out-of-realm for this session)

**Out-of-realm items** get a handoff relay prompt (TypeScript dead code, workflow audit).

Spec: `docs/superpowers/specs/2026-03-30-fieldwork-intelligence-system-design.md`
Convergence recs: `docs/superpowers/specs/2026-03-30-fieldwork-zettelkasten-convergence-recs.md`

---

## Step 1: seed.yaml P0 Fix (mechanical)

**File:** `/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here/seed.yaml`

Changes:
- Add `absorption.py` to `metadata.modules.contrib_engine` list (missing, module exists since S35)
- Add `fieldwork.py` to `metadata.modules.contrib_engine` list (will exist after Step 3)
- Add `artifacts/` renderer files to modules: `render_canvas.py`, `render_post001.py`, `render_post002.py`, `render_post002_audit.py`
- Update `test_count` from `111` to actual count (run `pytest --co -q | tail -1` to get real number)
- Update `last_validated` from `2026-03-23` to `2026-03-30`
- Update `description` to include absorption + fieldwork
- Add produces edge: `fieldwork_data` — "Process observations from contribution workflows, append-only stream with spectrum scoring."
- Add produces edge: `absorption_data` — "Detected expansion-worthy questions from external conversations."

**Verification:** `python3 scripts/validate-all-seeds.py` (if available) or manual YAML lint

---

## Step 2: Pydantic Models (schemas.py)

**File:** `/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here/contrib_engine/schemas.py`

Append after line 344 (end of AbsorptionIndex class). ~45 lines.

### New enums (all StrEnum except SpectrumLevel):

```
ObservationCategory(StrEnum): merge_protocol, review_culture, ci_architecture, repo_layout, tooling, contributor_experience, communication_style, governance, documentation, security_posture

SpectrumLevel(IntEnum): AVOID=-2, CAUTION=-1, NOTE=0, STUDY=1, ABSORB=2
  — IntEnum because ordinal comparison matters (STUDY > NOTE)

StrategicTag(StrEnum): shatterpoint, missing_shield, friction_point, fortress, competitive_edge, competitive_gap

ObservationSource(StrEnum): pr_submission, review_response, ci_run, repo_exploration, phase_transition, automated
```

### New models:

```python
class FieldObservation(BaseModel):
    id: str
    workspace: str
    timestamp: str
    category: ObservationCategory
    signal: str
    spectrum: SpectrumLevel
    strategic: list[StrategicTag] = Field(default_factory=list)
    source: ObservationSource
    evidence: str = ""
    scored_by: str = "agent"
    related_absorption_ids: list[str] = Field(default_factory=list)
    atom_id: str = ""  # Future Zettelkasten link
    model_config = {"extra": "allow"}

class FieldworkIndex(BaseModel):
    generated: str = ""
    observations: list[FieldObservation] = Field(default_factory=list)
    model_config = {"extra": "allow"}

    def by_workspace(self, workspace: str) -> list[FieldObservation]: ...
    def by_category(self, category: ObservationCategory) -> list[FieldObservation]: ...
    def by_spectrum(self, min_level: SpectrumLevel) -> list[FieldObservation]: ...
```

**Design decisions:**
- D1: IntEnum for SpectrumLevel (first in codebase, justified by ordinal semantics)
- D2: `atom_id: str = ""` present but unused — zero-cost Zettelkasten hook
- D3: `strategic` is `list[StrategicTag]` — observation can carry multiple tags simultaneously

---

## Step 3: fieldwork.py Module

**File:** `/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here/contrib_engine/fieldwork.py` (NEW)

~75 lines. Pattern source: `backflow.py` (56 lines).

### Functions:

```
DATA_DIR = Path(__file__).parent / "data"

record(index, workspace, category, signal, spectrum, source, evidence="", strategic=None, scored_by="agent", related_absorption_ids=None) -> FieldObservation
  — Constructs FieldObservation with auto-generated ID
  — ID format: fo-{workspace_short}-{MMDD}-{seq:03d}
  — workspace_short strips "contrib--" prefix
  — seq = count of existing obs with same workspace+date prefix + 1
  — Appends to index.observations, returns the observation

load_fieldwork(input_path=None) -> FieldworkIndex
  — Loads from data/fieldwork.yaml, empty index if missing

save_fieldwork(index, output_path=None) -> Path
  — yaml.safe_dump(index.model_dump(mode="json"), ...)
```

**No display logic in this module.** CLI handlers format output directly (matches backflow/outreach pattern).

---

## Step 4: CLI Integration (__main__.py)

**File:** `/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here/contrib_engine/__main__.py`

Add `_register_fieldwork_commands(subparsers)` + call it in `main()`. ~45 lines.

### Subcommands:

```
fieldwork record --workspace WS --category CAT --signal "..." --spectrum N --source SRC [--evidence "..."] [--strategic TAG ...] [--scored-by WHO]
fieldwork show [--workspace WS] [--category CAT] [--min-spectrum N]
```

### Command handlers:

```
_cmd_fieldwork_record(args):
  — Lazy import load_fieldwork, save_fieldwork, record
  — Call record() with args
  — save_fieldwork(index)
  — Print confirmation with observation ID

_cmd_fieldwork_show(args):
  — Lazy import load_fieldwork
  — Load index, apply filters
  — Print table: ID | Workspace | Category | Spectrum | Signal (truncated)
```

Also register in `cli.py`'s `register_contrib_commands()`:
- Add `fieldwork` as nested subparser group (same pattern as campaign/outreach/backflow in __main__.py)
- Or: add `fieldwork-record` and `fieldwork-show` as flat commands with prefix

**Decision:** Use the nested subparser pattern from __main__.py for fieldwork (it's a multi-subcommand group like campaign/outreach/backflow). Add `_register_fieldwork_commands(subparsers)` call in `main()` alongside the existing three.

---

## Step 5: Tests

**File:** `/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here/tests/test_contrib_fieldwork.py` (NEW)

~120 lines. Pattern source: `test_contrib_backflow.py`.

### Test classes:

```
TestFieldObservationModel:
  - test_spectrum_ordering (IntEnum: AVOID < NOTE < ABSORB)
  - test_strategic_multiple_tags
  - test_atom_id_defaults_empty

TestRecord:
  - test_record_appends_observation
  - test_record_generates_sequential_ids
  - test_record_strips_contrib_prefix_from_id

TestFieldworkIndex:
  - test_by_workspace_filters
  - test_by_category_filters
  - test_by_spectrum_filters_gte

TestPersistence:
  - test_save_and_load_roundtrip(tmp_path)
  - test_load_missing_returns_empty(tmp_path)
  - test_append_preserves_existing(tmp_path)
```

---

## Step 6: Verify

1. `cd /Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here`
2. `python -m pytest tests/test_contrib_fieldwork.py -v` — all new tests pass
3. `python -m pytest tests/ -v` — full suite passes, no regressions
4. `python -m contrib_engine fieldwork record --workspace contrib--dbt-mcp --category ci_architecture --signal "GitHub Actions matrix with 3 Python versions" --spectrum 1 --source repo_exploration` — produces valid observation
5. `python -m contrib_engine fieldwork show` — displays the observation
6. `python -m contrib_engine fieldwork show --workspace contrib--dbt-mcp` — filtered view
7. Count final tests: `python -m pytest --co -q | tail -1` — update seed.yaml test_count

---

## Out-of-Realm Handoff Relay Prompt

For the user to dispatch in a separate session targeting `orchestration-start-here` root:

```
SESSION: TypeScript Dead Code + Workflow Audit (P2 mechanical)

TASK 1: Archive TypeScript dead code
- Files: src/agents/dispatcher.ts, src/agents/metasystem-manager.ts,
         src/dreamcatcher/router.ts, src/dreamcatcher/watchman.ts
- Total: 572 lines, all stubs, no imports reference them
- Action: Move to src/_archive/ (preserve history) or delete entirely
- Commit: "chore: archive dead TypeScript stubs (572 lines)"

TASK 2: Workflow execution audit
- 17 cron workflows in .github/workflows/
- Run: gh run list --workflow <name> --limit 5 for each
- Report: which have actually executed, which are dormant
- No changes needed — audit only, output to docs/ or stdout

Both tasks are mechanical, no design decisions needed.
```

---

## Implementation Order

| Step | What | Lines | Time |
|------|------|-------|------|
| 1 | seed.yaml P0 fix | ~15 edits | 5 min |
| 2 | schemas.py model additions | ~45 new | 10 min |
| 3 | fieldwork.py new module | ~75 new | 15 min |
| 4 | __main__.py CLI integration | ~45 new | 10 min |
| 5 | test_contrib_fieldwork.py | ~120 new | 15 min |
| 6 | Verify full suite + manual test | — | 5 min |

Total new code: ~285 lines production + ~120 lines tests
