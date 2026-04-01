# Briefing: Communications & Correspondence — The Relay Protocol

**Session:** S51 | **Date:** 2026-04-01
**Priority:** P1
**Handler:** AGENT SESSION
**Plan source:** `.claude/plans/2026-04-01-communications-correspondence-relay-protocol.md`

---

## Vacuum Identified

Four communications subsystems operate independently with no shared lifecycle, no state machine, no cross-channel dispatch logic:

| Subsystem | Location | Covers | Gap |
|-----------|----------|--------|-----|
| Mail triage | `docs/mail-triage-*.md` | Inbound email sweep → classify → route | No outbound. No cross-channel. No response tracking. |
| Handoff docs | `docs/handoff-*.md` | Inter-session context relay | Ad-hoc format. No provenance chain. No verification. |
| PR comment discipline | Memory: `feedback_pr_comment_discipline.md` | GitHub correspondence etiquette | Behavioral only. Not connected to lifecycle. |
| Outbound correspondence | **Nowhere** | Recruiter replies, maintainer responses, client follow-ups | No process. No tracking. No state. |

## Ideal State

One SOP governing all communications across all channels with:
- 6-phase lifecycle (SWEEP → CLASSIFY → COMPOSE → RELAY → DISPATCH → VERIFY)
- Correspondence state machine (RECEIVED → TRIAGED → COMPOSED → DISPATCHED → CONFIRMED → CLOSED)
- Channel registry (email, GitHub, iMessage, LinkedIn, Slack — access method, trigger, cadence, constraints)
- Handler taxonomy (HUMAN, AGENT-SESSION, CONTRIB-ENGINE, INTAKE-ROUTER, AUTOMATED)
- Three trigger modes (daily recurring, on-demand, event-driven post-triage)
- Handoff relay format formalized (CONTEXT/TASK/DISCIPLINE/PROVENANCE blocks)
- Action ledger integration (7 verbs: received, triaged, composed, dispatched, relayed, confirmed, closed)
- Intake router domain (CORRESPONDENCE added to `IntakeDomain` enum)

## Campaign Dependencies

| Dependency | State | Impact |
|------------|-------|--------|
| Action ledger (Phases 1-4) | Built, operational | Verb vocabulary and route system ready to consume correspondence events |
| Intake router | Built, operational | Needs CORRESPONDENCE domain added to enum + keyword map + routing table |
| Mail triage SOP | Exists as event pattern, not as SOP | Phases 1-2 of this SOP formalize what mail-triage already does |
| Handoff relay pattern | Exists in 3 docs, no formal spec | Phase 4 extracts the pattern into a reusable format |
| Contribution engine monitor | Built | PR/issue correspondence already flows through `monitor.py` — this SOP governs the human-facing layer |
| Score/Rehearse/Perform | Built | Per-PR lifecycle applies to the implementation of this SOP itself |

## Deliverables

1. **SOP Document** → `docs/sop-communications-correspondence.md`
2. **Action Ledger Entries** → `action_ledger/data/actions.yaml` (3 actions, 1 sequence, 1 chain)
3. **Intake Router Update** → `intake_router/router.py` (CORRESPONDENCE domain + keywords + route)
