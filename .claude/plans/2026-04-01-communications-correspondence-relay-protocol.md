# Plan: Communications & Correspondence Handoff-Relay SOP

**Date:** 2026-04-01
**Session:** S51
**Scope:** New SOP + orchestration event recording

---

## Context

The system handles communications across multiple channels (email, GitHub, iMessage, LinkedIn, Slack) and multiple modes (inbound triage, outbound drafting, inter-session relay, cross-channel dispatch). Today these are fragmented:

- **Mail-triage** (`docs/mail-triage-*.md`) covers inbound email sweep → classify → route
- **Handoff docs** (`docs/handoff-*.md`) cover inter-session context relay — structured prompts
- **PR comment discipline** (memory) covers GitHub correspondence etiquette
- **Outbound correspondence** has no formal process — recruiter replies, maintainer responses, client follow-ups are ad-hoc

The SOP unifies these under one governance surface. Mail-triage becomes Phase 1. Outbound drafting, inter-session relay, and cross-channel dispatch get formalized as distinct phases of a single lifecycle.

---

## Deliverables

### 1. SOP Document — `docs/sop-communications-correspondence.md`

Structure (following War-Master Protocol SOP format):

```
# SOP: Communications & Correspondence (The Relay Protocol)

Authority, Purpose, Preconditions

## The Communications Lifecycle
  Phase 1: SWEEP (inbound collection — subsumes mail-triage)
  Phase 2: CLASSIFY (priority + channel + handler assignment)
  Phase 3: COMPOSE (outbound drafting — new phase)
  Phase 4: RELAY (inter-session handoff — formalizes handoff prompt pattern)
  Phase 5: DISPATCH (cross-channel routing — email→GitHub, GitHub→iMessage, etc.)
  Phase 6: VERIFY (delivery confirmation + response tracking)

## Channel Registry
  Table: channel → access method → trigger → cadence → constraints

## Handler Taxonomy
  HUMAN, AGENT-SESSION, CONTRIB-ENGINE, INTAKE-ROUTER, AUTOMATED

## Correspondence State Machine
  RECEIVED → TRIAGED → COMPOSED → DISPATCHED → CONFIRMED → CLOSED
  (with back-edges: COMPOSED → TRIAGED for re-routing)

## Trigger Modes
  1. Daily recurring (post-morning, subsumes mail-triage cadence)
  2. On-demand (correspondence accumulation threshold)
  3. Event-driven (post-triage items needing responses)

## Handoff Relay Format
  Formalize the structured prompt pattern from mail-triage handoffs:
  - CONTEXT block
  - TASK block (numbered steps)
  - DISCIPLINE block (constraints)
  - PROVENANCE block (source action ID, session, channel)

## Integration Points
  - Action Ledger: verbs (received, triaged, composed, dispatched, relayed, confirmed, closed)
  - Intake Router: correspondence domain addition
  - Contribution Engine: PR/issue correspondence → contrib_engine monitor
  - Fieldwork: correspondence patterns → observation recording
```

### 2. Action Ledger Entries — `action_ledger/data/actions.yaml`

Record the S51 orchestration event:
- `act-S51-0401-001`: `verb: formalized_sop`, `target: communications-correspondence`
- `act-S51-0401-002`: `verb: defined_lifecycle`, `target: relay-protocol-6-phase`
- `act-S51-0401-003`: `verb: unified_subsystems`, `target: mail-triage+handoff+relay+dispatch`

Sequence: `seq-S51-001` → chain: `chain-S51-001`

### 3. Action Ledger Sequences — `action_ledger/data/sequences.yaml`

New sequence for S51 with the 3 actions above.

### 4. Intake Router Domain Update (optional, if scope permits)

Add `CORRESPONDENCE` to `IntakeDomain` enum in `intake_router/router.py` and add keyword mappings for: `email, reply, respond, follow-up, recruiter, maintainer, draft, send, correspondence, letter, outreach`.

---

## Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `docs/sop-communications-correspondence.md` | **CREATE** | The SOP document |
| `action_ledger/data/actions.yaml` | APPEND | S51 orchestration event actions |
| `action_ledger/data/sequences.yaml` | APPEND | S51 sequence |
| `action_ledger/data/chains.yaml` | APPEND | S51 chain |
| `intake_router/router.py` | EDIT | Add CORRESPONDENCE domain (lines 26-34) |

## Existing Code to Reuse

- `action_ledger/ledger.py:record()` — atomic append function for action entries
- `action_ledger/ledger.py:compose_chain()` / `close_session()` — session lifecycle
- `action_ledger/schemas.py:RouteKind` — FEEDS, CONTINUES, REFINES for inter-phase routes
- `action_ledger/emissions.py:emit_state_change()` — auto-records state transitions
- `intake_router/router.py:IntakeDomain` — enum to extend with CORRESPONDENCE
- Mail-triage doc (`docs/mail-triage-2026-04-01.md`) — template for SWEEP/CLASSIFY phases
- Handoff docs (`docs/handoff-*.md`) — template for RELAY phase format
- War-Master SOP (`docs/sop-war-master-protocol.md`) — structural template for the SOP itself

## Verification

1. **SOP coherence:** Read `docs/sop-communications-correspondence.md` end-to-end — all 6 phases present, no dangling references
2. **Ledger integrity:** `python -m action_ledger show --session S51` returns 3 actions
3. **Sequence closure:** `python -m action_ledger sequence show --session S51` shows closed sequence
4. **Intake router:** `python -m intake_router table` shows CORRESPONDENCE domain in routing table
5. **Git commit:** `feat: S51 orchestration event — communications & correspondence relay protocol formalized`

## Commit Convention

Single commit: `feat: S51 orchestration event — communications & correspondence relay protocol formalized`
