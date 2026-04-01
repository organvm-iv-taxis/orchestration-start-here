# War Report: Communications & Correspondence — The Relay Protocol

**Session:** S51 | **Date:** 2026-04-01
**Archetype:** RELAY-CIRCUIT
**Plan source:** `.claude/plans/2026-04-01-communications-correspondence-relay-protocol.md`

---

## The Front Line

The divergence between reality and ideal exists at the module scale: four communication subsystems operate independently where one lifecycle should govern all channels.

### Where Dystopia Is Currently Winning

| Fragment | What it preserves | What it lets decay |
|----------|-------------------|-------------------|
| Mail triage | Inbound sweep → classify → route | No outbound. No cross-channel. No response tracking. Each triage event is born and dies alone. |
| Handoff docs | Inter-session context relay | Ad-hoc format. No provenance chain. No verification that the relay was received. |
| PR discipline | GitHub correspondence etiquette | Behavioral constraint only. Not connected to any lifecycle. Exists as memory, not as protocol. |
| Outbound | **Nothing.** | No process. No tracking. No state. Recruiter replies, maintainer responses, client follow-ups are improvised every time. |

### What Utopia Looks Like If This Portal Succeeds

One SOP. Six phases. One state machine. All channels.

```
SWEEP → CLASSIFY → COMPOSE → RELAY → DISPATCH → VERIFY
  ↓         ↓          ↓         ↓         ↓          ↓
RECEIVED → TRIAGED → COMPOSED → RELAYED → DISPATCHED → CONFIRMED → CLOSED
```

A received email already knows it will be triaged, may need composition, will be dispatched, must be verified. The system anticipates. The format evolves. New channels absorb into the protocol without structural surgery.

### What Dystopia Looks Like If This Portal Fails

The fragments calcify. Mail-triage becomes the only governed channel. Outbound correspondence remains improvised. Every new channel (Slack, LinkedIn, USPS) creates another independent fragment. The organism's communication capacity scales linearly with the operator's attention, not with the system's architecture. Eventually, correspondence falls through gaps that no single fragment was designed to catch.

---

## Campaign Dependencies

| What | State | Door |
|------|-------|------|
| Action ledger | Built | Ready to consume correspondence verbs |
| Intake router | Built | Needs CORRESPONDENCE domain (K2) |
| Mail triage pattern | Exists | Becomes Phase 1-2 (plasticity, not preservation) |
| Handoff pattern | Exists in 3 docs | Becomes Phase 4 (formalized, not ad-hoc) |
| Contrib engine monitor | Built | PR correspondence already flows — SOP governs the human layer |

---

## Deliverables

| Key | Artifact | Door |
|-----|----------|------|
| K1 | `docs/sop-communications-correspondence.md` | CREATE |
| K2 | `intake_router/router.py` CORRESPONDENCE domain | EDIT |
| K3-K5 | `action_ledger/data/{actions,sequences,chains}.yaml` | APPEND |
