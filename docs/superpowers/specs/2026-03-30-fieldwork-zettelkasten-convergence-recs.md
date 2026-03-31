# Convergence Recommendations: Fieldwork Intelligence × Zettelkasten × Patches

**Date:** 2026-03-30
**Status:** Recommendations for flawless integration
**Prerequisite specs:**
- `docs/superpowers/specs/2026-03-30-fieldwork-intelligence-system-design.md` (v4.0)
- `meta-organvm/.claude/plans/2026-03-30-patch-signal-architecture.md`
- `meta-organvm/.claude/plans/2026-03-30-unified-implementation-zettelkasten-patches.md`

---

## The Isomorphism

Three systems designed in one session cycle. They look separate but share a single skeleton:

| Concept | Fieldwork | Zettelkasten | Patches |
|---------|-----------|-------------|---------|
| **Atomic unit** | `FieldObservation` | Zettel atom (`GraphNode`) | Patch definition (YAML) |
| **Lifecycle** | agent-scored → orchestrator-scored → compiled → synthesized | fleeting → literature → permanent / discarded | signal received → SOP executed → output signal emitted |
| **Maturity signal** | `spectrum` score converging from NOTE(0) to ABSORB(+2) or AVOID(-2) | promote after 7 days or discard | recurrence: on signal / schedule / manual |
| **Routing** | category → dossier section → organ via backflow | zettel_type → hub indexing → issue projection | input_signal → sop_ref → output_signal |
| **Storage** | append-only YAML, rotation at 500 | UAKS graph (JSON/YAML), issue projection | YAML definitions in `praxis-perpetua/patches/` |
| **Cross-ref** | `related_absorption_ids`, `outreach_workspace` | `follows`, `references`, `contradicts` edges | signal chains (output of one = input of next) |

**The identity:** A `FieldObservation` with `spectrum: +2 (absorb)` IS a Zettel being promoted to permanent. The promote action IS a patch firing: `signal:fieldwork:observation-absorbed → SOP:backflow-deposit → signal:backflow:item-deposited`.

---

## Recommendation 1: Shared Signal Namespace

Define signal names NOW, before either system is built. Both systems emit and consume signals. If the names diverge, stitching is painful. If they share a namespace, integration is free.

**Signal namespace convention:** `{domain}:{entity}:{event}`

### Fieldwork signals (contrib_engine emits)

```
signal:fieldwork:observation-recorded       # Layer 1: new observation appended
signal:fieldwork:observation-rescored       # Orchestrator re-scored an agent observation
signal:fieldwork:shatterpoint-detected      # Strategic detection found a gap
signal:fieldwork:dossier-compiled           # Layer 2: dossier regenerated
signal:fieldwork:synthesis-complete         # Layer 3: cross-repo patterns extracted
signal:fieldwork:output-candidate-detected  # Layer 4: knowledge output auto-detected
signal:fieldwork:output-published           # Knowledge output produced and deposited
```

### Zettelkasten signals (UAKS emits)

```
signal:zettel:atom-created                  # New fleeting atom deposited
signal:zettel:atom-promoted                 # Fleeting → permanent (7-day window)
signal:zettel:atom-discarded                # Fleeting → discarded
signal:zettel:hub-indexed                   # Atom added to hub index
signal:zettel:issue-projected               # Atom projected to GitHub Issue
signal:zettel:issue-synced                  # Issue state backflowed to atom
```

### Integration signals (the stitching)

```
signal:fieldwork:observation-absorbed       # Fieldwork → Zettelkasten bridge
signal:zettel:fieldwork-atom-promoted       # Zettelkasten → Backflow bridge
```

**Action:** Add a `SIGNAL_REGISTRY.md` to `praxis-perpetua/` before building either system. Both specs reference it. The registry is the contract.

---

## Recommendation 2: FieldObservation Embeds Zettel Identity

When a `FieldObservation` is created, it should optionally carry a UAKS atom ID. This means the observation IS the zettel — not a separate object that gets converted later.

```python
class FieldObservation(BaseModel):
    id: str                                  # fo-{workspace}-{date}-{seq}
    atom_id: str = ""                        # UAKS GraphNode ID (empty until zettel integration)
    # ... existing fields ...
```

**Before Zettelkasten is built:** `atom_id` is always empty. Observations are standalone.
**After Zettelkasten is built:** `record()` calls `uaks.source_intake()` to create a fleeting atom alongside the observation. The `atom_id` links them. The fieldwork stream and the Zettelkasten graph are two projections of the same underlying data.

**Why this works:** No migration needed. The field exists from day one, empty. When UAKS integration lands (Batch 4 of the unified plan), `record()` gains one additional call. No schema change, no data migration, no stitching.

---

## Recommendation 3: Spectrum Score = Promote/Discard Signal

The Zettelkasten's 7-day promote/discard cycle and fieldwork's dual scoring protocol (agent inline + orchestrator at phase transition) are the same mechanism at different time scales.

**Map them explicitly:**

| Spectrum Score | Zettel Lifecycle | Patch Response |
|---------------|-----------------|----------------|
| Unscored (agent just recorded) | fleeting | No patch fires — atom is in intake |
| NOTE (0) | fleeting, 7-day clock starts | `zettel-processing-pass.yaml` nudges at day 7 |
| STUDY (+1) | literature (promoted from fleeting) | No automatic action — awaits deeper review |
| ABSORB (+2) | permanent (full promotion) | `signal:fieldwork:observation-absorbed` fires → backflow deposit |
| CAUTION (-1) | literature (kept for reference) | Anti-pattern flagged in synthesis |
| AVOID (-2) | discarded (with audit trail) | Anti-pattern logged, `signal:fieldwork:anti-pattern-logged` |

**The convergence patch:** `zettel-processing-pass.yaml` (already in Batch 3E of the unified plan) wires `signal:session-insight:deposited` to `SOP:zettel-processing`. Extend it to also subscribe to `signal:fieldwork:observation-recorded`. When a fieldwork observation is recorded AND has an atom_id, the Zettelkasten processing SOP governs its lifecycle. The fieldwork system doesn't need its own lifecycle engine — it delegates to the Zettelkasten's.

---

## Recommendation 4: Three Fieldwork Patches

Define three patches that wire fieldwork signals to SOPs. Create the YAML definitions NOW (they can sit idle until the patches module is built — they're just data).

### Patch 1: Shatterpoint → Campaign Action

```yaml
patch_id: fieldwork-shatterpoint-to-campaign
input_signal: signal:fieldwork:shatterpoint-detected
sop_ref: campaign-action-generation
parameters:
  physics:
    schema_ref: null
  bio:
    min_promotion_state: LOCAL
  chem:
    cross_reference_depth: 0
    orphan_tolerance: 5
  met:
    stranger_test: false
    automated_validation: "python -m contrib_engine fieldwork shatterpoints --validate"
output_signal: signal:campaign:action-generated
recurrence:
  on: signal
```

### Patch 2: Absorb → Backflow Deposit

```yaml
patch_id: fieldwork-absorb-to-backflow
input_signal: signal:fieldwork:observation-absorbed
sop_ref: backflow-deposit
parameters:
  physics:
    schema_ref: backflow-v1
  bio:
    min_promotion_state: CANDIDATE
  chem:
    cross_reference_depth: 1
    orphan_tolerance: 0
  met:
    stranger_test: false
    automated_validation: null
output_signal: signal:backflow:item-deposited
recurrence:
  on: signal
```

### Patch 3: Synthesis → Knowledge Output Detection

```yaml
patch_id: fieldwork-synthesis-to-output
input_signal: signal:fieldwork:synthesis-complete
sop_ref: knowledge-output-detection
parameters:
  physics:
    schema_ref: null
  bio:
    min_promotion_state: LOCAL
  chem:
    cross_reference_depth: 0
    orphan_tolerance: 10
  met:
    stranger_test: false
    automated_validation: null
output_signal: signal:fieldwork:output-candidate-detected
recurrence:
  on: signal
  also: weekly
```

**Action:** Write these three YAML files into `praxis-perpetua/patches/` alongside the three from Batch 3E. They're inert until the patches module processes them — but their existence proves the signal graph works across both systems.

---

## Recommendation 5: Build Fieldwork First, Integrate Second

The unified Zettelkasten+patches plan has 6 batches across 5 repos. The fieldwork system is 1 module in 1 repo. The dependency graph:

```
Fieldwork MVP (record + stream)     ← can ship independently
  ↓
Fieldwork dossier + synthesis       ← can ship independently
  ↓
Unified Batch 1 (schemas)          ← patches and zettel schemas
  ↓
Unified Batch 3E (patch YAMLs)    ← include the 3 fieldwork patches
  ↓
Unified Batch 4 (UAKS projection) ← now FieldObservation.atom_id gets wired
  ↓
Unified Batch 5 (dispatch)        ← fieldwork signals routed through patches
```

**The flawless sequence:**

1. **Tomorrow:** Implement fieldwork MVP — `record()`, `FieldObservation` model (with empty `atom_id` field), `fieldwork.yaml`. This is 100-150 lines. Ship it. Start recording observations during the next PR cycle.

2. **Same session or next:** Implement dossier compilation + synthesis + knowledge output detection. This is 300-400 lines. Ship it. The fieldwork system is fully operational standalone.

3. **When Zettelkasten lands (Batch 4):** Add one line to `record()`:
   ```python
   if uaks_available:
       atom_id = uaks.source_intake(signal, tags=[category, source])
       observation.atom_id = atom_id
   ```
   No refactoring. The field was always there. The integration is one conditional.

4. **When patches module lands (Batch 3):** The three fieldwork patch YAMLs are already sitting in `praxis-perpetua/patches/`. The dispatch router picks them up automatically. No fieldwork code changes needed — the patches system consumes the signals the fieldwork system already emits.

5. **When both land (Batch 5):** The dispatch extension routes fieldwork signals through the patches module to the Zettelkasten. The full loop closes: observe → record → atom created → patch fires → SOP executes → new signal → next patch → ... The stitching was the architecture all along.

---

## Recommendation 6: Dossier = Zettelkasten Hub

A `RepoDossier` compiled from 15 observations across 10 categories IS a Zettelkasten hub atom indexing 15 permanent atoms. The dossier's `verdicts` are the hub's `indexes` edges. The dossier's `shatterpoints` are the hub's `references` edges to work atoms.

When the Zettelkasten projection layer lands:

```python
def compile_dossier(workspace) -> RepoDossier:
    # ... existing compilation logic ...

    # If UAKS available, project dossier as hub atom
    if uaks_available:
        hub = uaks.create_hub(
            title=f"Dossier: {workspace}",
            indexed_atoms=[obs.atom_id for obs in observations if obs.atom_id],
        )
        dossier.hub_atom_id = hub.id
```

The dossier hub gets projected as a GitHub Issue with label `zettel:hub`. The issue body contains the compiled verdicts, shatterpoints, and strategic assessment. It's simultaneously:
- Internal intelligence (the dossier)
- A Zettelkasten hub (the atom graph)
- A public artifact (the GitHub Issue)
- A knowledge output candidate (the contribution playbook)

Four projections of one object. Build the object once.

---

## Recommendation 7: Signal Registry as Test Contract

The signal names from Recommendation 1 become test fixtures. Before either system is built, write integration tests that assert:

```python
def test_fieldwork_signals_are_registered():
    """Every signal the fieldwork system emits must be in SIGNAL_REGISTRY."""
    for signal in FIELDWORK_SIGNALS:
        assert signal in SIGNAL_REGISTRY

def test_fieldwork_patches_reference_valid_signals():
    """Every fieldwork patch's input_signal must be in SIGNAL_REGISTRY."""
    for patch in FIELDWORK_PATCHES:
        assert patch.input_signal in SIGNAL_REGISTRY
        if patch.output_signal:
            assert patch.output_signal in SIGNAL_REGISTRY

def test_no_blind_spots_in_fieldwork_signals():
    """Every fieldwork output signal must have at least one subscriber."""
    for signal in FIELDWORK_OUTPUT_SIGNALS:
        subscribers = [p for p in ALL_PATCHES if p.input_signal == signal]
        assert len(subscribers) > 0, f"Blind spot: {signal}"
```

These tests pass trivially at first (empty registries). As both systems are built, they enforce the contract. A signal added to fieldwork without a patch subscriber fails the blind-spot test. A patch referencing a signal that fieldwork doesn't emit fails the registry test. The test suite IS the convergence enforcement.

---

## Summary: The Seven Moves

| # | Recommendation | When | Lines | Effect |
|---|---------------|------|-------|--------|
| 1 | Shared signal namespace | Before building either | 1 file | Contract prevents divergence |
| 2 | `atom_id` field on FieldObservation | Fieldwork MVP (tomorrow) | 1 field | Zero-cost integration point |
| 3 | Spectrum ↔ promote/discard mapping | Design doc (now) | 0 code | Mental model alignment |
| 4 | Three fieldwork patch YAMLs | Alongside Batch 3E | 3 files | Proves cross-system signal graph |
| 5 | Build fieldwork first, integrate second | Tomorrow → next week | Sequential | No blocking, no stitching |
| 6 | Dossier = hub atom | When UAKS lands (Batch 4) | ~10 lines | Four projections of one object |
| 7 | Signal registry as test contract | Before building either | ~30 lines | Tests enforce convergence |

**Total convergence cost if built in this order: ~40 lines of integration code.** Everything else is architecture that was already going to be built. The stitching IS the architecture because the seams were designed to be seams.

---

*Recommendations version: 1.0 | 2026-03-30*
*Cross-references: fieldwork-intelligence-system-design.md (v4.0), patch-signal-architecture.md, unified-implementation-zettelkasten-patches.md*
