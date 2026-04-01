# Orchestrator Intake Router — The Missing Routing Function

**Date:** 2026-03-31
**Workspace:** `~/Workspace/organvm-iv-taxis/orchestration-start-here`
**Status:** DESIGN

## Context

The operator runs 4+ agents in parallel (Claude, Codex, Gemini, Claude-twins), cycling raw ideas rapidly between them. Tonight's session proved the pattern works — 6 sessions produced 7 artifacts — but the routing is manual: the operator copies output, decides which workspace/archetype it belongs to, pastes it into the right session.

The three-block notation the operator described encodes the missing function:

```
SORT   {triage} {define} {prioritize}
ROUTE  {assign} {spec} {scope}
CLOSE  {open} {track} {close}
```

The SOP (`docs/sop-war-master-protocol.md`) captures the meta-process (Four Laws, 5 phases). The archetype plan (`.claude/plans/2026-03-31-hanging-task-archetypes.md`) captures the dispatch targets. What's missing is the **intake router** — the function that takes raw, messy human input and produces a structured dispatch to the right archetype, workspace, and agent.

The goal: preserve Claude tokens. Claude does routing (small burst). Codex/Gemini do execution (unlimited). Claude verifies (small burst). The router is the 30-second general.

## Design

### What Gets Built

A new module `intake_router/` in orchestration-start-here. Three files, one CLI entry point. ~200 lines total.

### Architecture

The intake router extends the action ledger's existing infrastructure:
- Uses `RouteKind.FEEDS` to connect intake actions to archetype targets
- Uses `ActionOrigin.MANUAL` for operator intake, `ActionOrigin.EMITTED` for auto-routed follow-ups
- Emits via `emit_state_change()` so routing decisions are observable in the action stream

```
intake_router/
  __init__.py
  router.py        # Core: classify → route → emit
  cli.py           # CLI: intake, dispatch, status
```

### Module 1: `router.py` (~120 lines)

**`classify(raw_input: str) -> IntakeItem`**

Takes raw text (the operator's messy idea) and produces a structured classification:

```python
class IntakeDomain(StrEnum):
    ORGANISM = "organism"          # a-organvm — growth, functions, signals
    TRANSMUTATION = "transmutation" # meta-organvm — exit interview, governance handoff
    EMISSION = "emission"          # orchestration-start-here — wiring, ledger, monitoring
    HOUSEKEEPING = "housekeeping"  # corpus + a-organvm — IRF, concordance, GH issues
    PIPELINE = "pipeline"          # application-pipeline — jobs, applications, triage
    BILLING = "billing"            # human action — GitHub billing, infra
    UNKNOWN = "unknown"            # needs operator decision

class IntakeItem(BaseModel):
    raw: str                       # original input
    domain: IntakeDomain           # classified domain
    keywords: list[str]            # extracted signal words
    tension: float                 # 0-1 urgency estimate
    suggested_archetype: str       # I, II, III, IV, or "new"
    suggested_agent: str           # claude, codex, gemini, human
    suggested_workspace: str       # directory path
    prompt_fragment: str           # ready-to-paste prompt excerpt
```

Classification is keyword-based (not LLM-based — that would burn tokens). Pattern matching against known vocabulary:
- organism/seed/function/gate/signal/axiom → ORGANISM
- exit-interview/testimony/rectification/governance → TRANSMUTATION
- emission/wire/emit/ledger/action → EMISSION
- IRF/concordance/issue/registry → HOUSEKEEPING
- pipeline/application/job/resume → PIPELINE
- billing/enterprise/org/copilot → BILLING

**`route(item: IntakeItem) -> Dispatch`**

```python
class Dispatch(BaseModel):
    item: IntakeItem
    workspace: str                 # absolute path
    archetype: str                 # from hanging-task-archetypes
    agent: str                     # recommended executor
    prompt: str                    # complete copy-paste prompt
    token_budget: str              # "small" (Claude verify), "large" (Codex/Gemini execute)
```

Routing table (hardcoded, updated as archetypes evolve):

| Domain | Workspace | Archetype | Default Agent | Token Budget |
|--------|-----------|-----------|---------------|--------------|
| ORGANISM | `~/Workspace/a-organvm` | I | codex/gemini | large |
| TRANSMUTATION | `~/Workspace/meta-organvm/organvm-engine` | II | codex/gemini | large |
| EMISSION | `~/Workspace/organvm-iv-taxis/orchestration-start-here` | III | codex/gemini | large |
| HOUSEKEEPING | `~/Workspace/meta-organvm/organvm-corpvs-testamentvm` | IV | codex/gemini | large |
| PIPELINE | `~/Workspace/4444J99/application-pipeline` | — | codex/gemini | large |
| BILLING | — | — | human | — |
| UNKNOWN | — | — | claude (routing burst) | small |

**`emit_routing(dispatch: Dispatch) -> None`**

Records the routing decision in the action ledger via `emit_state_change()`. This makes every routing decision observable — the cycle detector can find patterns in what gets routed where.

### Module 2: `cli.py` (~80 lines)

Three commands:

```bash
# Classify and route raw input
python -m intake_router intake "messy idea text here"
# → prints: domain, archetype, workspace, agent, prompt

# Show routing table
python -m intake_router table
# → prints the routing table with current archetype prompts

# Show recent dispatches from action ledger
python -m intake_router history [--domain ORGANISM] [--limit 10]
# → queries action stream for origin:emitted, subsystem:intake_router
```

CLI registers under the existing argparse pattern (same as `action_ledger/cli.py` and `contrib_engine/cli.py`).

### Integration Points

1. **Action Ledger** — routing decisions emit as actions with `origin: emitted`, `subsystem: intake_router`
2. **Archetype Prompts** — router reads prompt templates from `.claude/plans/2026-03-31-hanging-task-archetypes.md` (or a structured YAML extracted from it)
3. **SOP** — the router IS Phase 2 (SHAPE/Demand Formation) of the War-Master Protocol automated

### What This Does NOT Do

- No LLM calls. Classification is keyword/regex. Preserves tokens by design.
- No agent spawning. The router produces a prompt; the operator pastes it. The operator is the bridge.
- No cross-workspace execution. Each dispatch targets one workspace. The operator carries context between sessions.

## Files to Modify

| File | Action |
|------|--------|
| `intake_router/__init__.py` | Create — empty |
| `intake_router/router.py` | Create — classify, route, emit_routing (~120 lines) |
| `intake_router/cli.py` | Create — intake, table, history commands (~80 lines) |
| `seed.yaml` | Update — add intake_router to modules |
| `CLAUDE.md` | Update — document intake_router |
| `tests/test_intake_router.py` | Create — classification + routing tests (~60 lines) |

## Reusable Existing Code

- `action_ledger/schemas.py:ActionOrigin, RouteKind, Action` — reuse for emission typing
- `action_ledger/emissions.py:emit_state_change()` — reuse for routing emission
- `action_ledger/cli.py:register_ledger_commands()` — pattern for CLI registration
- `contrib_engine/schemas.py:StrEnum` pattern — reuse for IntakeDomain

## Verification

```bash
# Tests pass
python -m pytest tests/test_intake_router.py -v

# Full suite still passes
python -m pytest tests/ -v  # expect 233 + new tests

# Classify a known input
python -m intake_router intake "third function build for a-organvm"
# → domain: organism, archetype: I, workspace: ~/Workspace/a-organvm

# Classify an unknown input
python -m intake_router intake "something completely new"
# → domain: unknown, agent: claude (routing burst)

# Show routing table
python -m intake_router table

# Verify emission was recorded
python -m action_ledger show --origin emitted --target intake_router
```

## Dispatch: This Plan Is the Prompt

**This plan is NOT executed here.** Claude's tokens were spent on design. The build is dispatched to Codex or Gemini.

Copy the prompt below into Codex or Gemini in the target workspace:

```
cd ~/Workspace/organvm-iv-taxis/orchestration-start-here

# BUILD: Intake Router Module
# Spec: .claude/plans/tingly-painting-rainbow.md (read it first)

Create intake_router/ with 3 files:

1. intake_router/__init__.py — empty

2. intake_router/router.py (~120 lines):
   - IntakeDomain(StrEnum): organism, transmutation, emission, housekeeping, pipeline, billing, unknown
   - IntakeItem(BaseModel): raw, domain, keywords, tension, suggested_archetype, suggested_agent, suggested_workspace, prompt_fragment
   - Dispatch(BaseModel): item, workspace, archetype, agent, prompt, token_budget
   - classify(raw_input: str) -> IntakeItem — keyword-based, NO LLM calls
     Keywords: organism/seed/function/gate/signal/axiom → ORGANISM
              exit-interview/testimony/rectification/governance → TRANSMUTATION
              emission/wire/emit/ledger/action → EMISSION
              IRF/concordance/issue/registry → HOUSEKEEPING
              pipeline/application/job/resume → PIPELINE
              billing/enterprise/org/copilot → BILLING
   - route(item: IntakeItem) -> Dispatch — lookup table mapping domain→workspace+archetype+agent
   - emit_routing(dispatch: Dispatch) -> None — calls emit_state_change() from action_ledger.emissions

   Routing table:
     ORGANISM → ~/Workspace/a-organvm, archetype I, codex/gemini, large
     TRANSMUTATION → ~/Workspace/meta-organvm/organvm-engine, archetype II, codex/gemini, large
     EMISSION → ~/Workspace/organvm-iv-taxis/orchestration-start-here, archetype III, codex/gemini, large
     HOUSEKEEPING → ~/Workspace/meta-organvm/organvm-corpvs-testamentvm, archetype IV, codex/gemini, large
     PIPELINE → ~/Workspace/4444J99/application-pipeline, none, codex/gemini, large
     BILLING → none, none, human, none
     UNKNOWN → none, none, claude, small

3. intake_router/cli.py (~80 lines):
   - python -m intake_router intake "raw text" → prints classification + dispatch
   - python -m intake_router table → prints routing table
   - python -m intake_router history → queries action ledger for intake_router emissions
   Follow the argparse registration pattern in action_ledger/cli.py

4. intake_router/__main__.py — standalone entry: python -m intake_router

5. tests/test_intake_router.py (~60 lines):
   - test_classify_organism: "third function build" → ORGANISM
   - test_classify_transmutation: "exit interview spec" → TRANSMUTATION
   - test_classify_emission: "wire emission into fieldwork" → EMISSION
   - test_classify_unknown: "something random" → UNKNOWN
   - test_route_returns_workspace: classified item → correct workspace path
   - test_emit_routing_records_action: dispatch → action in ledger with origin:emitted

Existing code to reuse:
  - action_ledger/schemas.py: ActionOrigin, RouteKind, Action, StrEnum pattern
  - action_ledger/emissions.py: emit_state_change()
  - action_ledger/cli.py: register_ledger_commands() pattern
  - contrib_engine/schemas.py: StrEnum pattern

After building:
  python -m pytest tests/test_intake_router.py -v
  python -m pytest tests/ -v  # expect 233 + new tests all passing
  python -m intake_router intake "third function build for a-organvm"
  python -m intake_router table

Update seed.yaml: add intake_router to action_ledger modules list.
Update CLAUDE.md: add intake_router section.
```

## Token Economics

| Phase | Agent | Token Cost |
|-------|-------|------------|
| Design (this plan) | Claude | ~5K tokens (already spent) |
| Build (dispatch prompt above) | Codex/Gemini | 0 Claude tokens |
| Verify (run tests, check output) | Claude | ~1K tokens |
| **Total Claude cost** | | **~6K tokens** |

The router, once built, makes every future intake cost ~500 Claude tokens (classify + print prompt) instead of ~50K tokens (full session with exploration).

## Forward

- Structured YAML archetype registry (replaces reading markdown prompts)
- Multi-domain classification (an idea that spans organism + emission)
- Token budget tracking (how many Claude tokens spent on routing vs execution)
- Integration with `domus` CLI for one-command dispatch
