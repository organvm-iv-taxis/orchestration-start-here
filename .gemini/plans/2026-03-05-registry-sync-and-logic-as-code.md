# Implementation Plan: Registry Sync & Logic-as-Code

**Date:** 2026-03-05
**Author:** Gemini CLI
**Objective:** Align ORGAN-IV orchestration with the unified system registry and formalize governance principles as machine-readable rules.

## 1. Registry Sync (Reinforcement)

### 1.1 Update `registry.json` Pointer
- **Task:** Formally deprecate the local `orchestration-start-here/registry.json` and ensure all scripts point to `../meta-organvm/organvm-corpvs-testamentvm/registry-v2.json`.
- **Reasoning:** Eliminates "split-brain" logic where local audits report 79 repos while the meta-registry reports 101.

### 1.2 Update `validate-deps.py`
- **Task:** Modify the script to accept the new registry schema (v2.0) and handle the sibling directory path as a default.
- **Verification:** Run `python3 scripts/validate-deps.py --registry ../meta-organvm/organvm-corpvs-testamentvm/registry-v2.json --governance governance-rules.json`.

## 2. Logic-as-Code (Growth)

### 2.1 Create `logic-rules.json`
- **Task:** Extract the hierarchy from `petasum-super-petasum/COMMANDMENTS.md` into a structured JSON format.
- **Structure:**
  - `meta_principle` (Level 0)
  - `principles` (Array of objects with level, derivation, and constraints)
- **Path:** `petasum-super-petasum/logic-rules.json`

### 2.2 Integrate with Orchestration
- **Task:** Update `orchestration-start-here/seed.yaml` to include `logic-rules.json` as a produced artifact.

## 3. Testing & Validation

### 3.1 Dependency Validation
- Execute the updated `validate-deps.py` against the production registry.

### 3.2 Logic Consistency
- Validate that `logic-rules.json` is valid JSON and accurately represents the Markdown source.

## 4. Archiving
- Move any superseded plan fragments to `plans/archive/2026-03/`.
