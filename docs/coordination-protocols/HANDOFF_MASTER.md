# Omni-Dromenon-Machina: Master Orchestration Plan

**Project:** Omni-Dromenon-Engine (Real-time audience-participatory performance system)
**GitHub Org:** https://github.com/orgs/omni-dromenon-machina
**Local Root:** `/Users/4jp/Desktop/omni-dromenon-machina/`
**Status:** Phase C (Deployment & Narrative) In Progress - Deliverables A2/D1 Drafted
**Live Core:** https://omni-dromenon-core-dkxnci5fua-uc.a.run.app
**Live SDK:** https://omni-dromenon-sdk-dkxnci5fua-uc.a.run.app
**Date:** December 26, 2025

## Overview

This document orchestrates autonomous AI execution (Dec 7-8) followed by human review gate (Dec 11).

## Phase A: Dec 7-8 (AI Services Autonomous)

Three parallel deliverables with zero coordination required:

### Task A1: Consensus Algorithm Implementation (Jules)
- **Input:** Weighted consensus specification
- **Output:** `/core-engine/src/consensus/weighted-consensus.ts` + tests
- **Success:** `npm test` passes, P95 latency <1ms, 100% coverage
- **Deadline:** Dec 8, 11:59 PM

### Task A2: Grant Narrative (Gemini)
- **Input:** Problem/structure outline
- **Output:** `/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`
- **Success:** 1200±50 words, submission-ready
- **Deadline:** Dec 8, 11:59 PM

### Task A3: CI/CD Workflows (Copilot)
- **Input:** GitHub Actions specifications
- **Output:** `.github/workflows/{test,deploy-docs,release}.yml`
- **Success:** Valid YAML, ready to push
- **Deadline:** Dec 8, 11:59 PM

## Phase B: Dec 11 Morning (Human Review Gate)

### Validation Commands
```bash
cd /Users/4jp/Desktop/omni-dromenon-machina

# Check A1
cd core-engine && npm test
# Expected: Pass

# Check A2
wc -w ../GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md
# Expected: ~1200

# Check A3
ls .github/workflows/{test,deploy-docs,release}.yml
# Expected: All 3 files exist
```

### Decision Framework
- **✅ APPROVE:** All three pass → Push to GitHub immediately
- **⚠️ REWORK:** One or more fail → Provide feedback, 24-hour rework
- **⏸️ HOLD:** Critical issues → Debug, re-validate

## Phase C: Dec 13-27 (Deployment)

- Demo deployment
- Video recording
- Narrative synthesis

## Phase D: Dec 27+ (Grants)

- Ars Electronica (€40k, deadline Jul 13, 2025)
- S+T+ARTS Prize (€20k, deadline Jan 2026)

## Repository Structure (12 Total)

**Core:** core-engine, performance-sdk, client-sdk, audio-synthesis-bridge
**Theory:** docs, academic-publication
**Examples:** example-generative-music, example-generative-visual, example-choreographic-interface, example-theatre-dialogue
**Resources:** artist-toolkit-and-templates
**Org:** .github

## Critical Files

- `_COORDINATION_DOCS/` — All handoff infrastructure
- `_archive/` — Backups
- Root level scripts (push, validation)

---

See accompanying docs for detailed specifications and templates.
