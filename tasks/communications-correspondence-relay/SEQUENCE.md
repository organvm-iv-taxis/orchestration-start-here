# Sequence: Relay Circuit α → ε

The ordered intervention. Every injection, creation, operation, verification, and forward deposit as a repeatable procedure. The circuit ends at PRECIPITATE, not at destruction. Evaporation is the next portal's prerogative.

---

## Phase α — INJECT (Read Context)

| Step | Procedure | Tool/Skill | Verification |
|------|-----------|------------|--------------|
| α.1 | Read `BRIEFING.md` | — | Vacuum and ideal state internalized |
| α.2 | Read `REFERENCES.md` | — | All external pointers identified |
| α.3 | Read `docs/sop-war-master-protocol.md` | Read | SOP structural template loaded |
| α.4 | Read `docs/mail-triage-2026-04-01.md` | Read | Phase 1-2 prior art loaded |
| α.5 | Read `docs/handoff-72h-reconciliation.md` | Read | Phase 4 prior art loaded |
| α.6 | Read `action_ledger/schemas.py` | Read | Data model understood |
| α.7 | Read `intake_router/router.py` | Read | Extension points identified |

---

## Phase β — CREATE (Write Artifacts)

| Step | Procedure | Tool/Skill | Output |
|------|-----------|------------|--------|
| β.1 | Write SOP document | Write | `docs/sop-communications-correspondence.md` |
| β.2 | Validate SOP structure | Read | All 6 phases present, channel registry, state machine, handoff format, integration points |
| β.3 | Add CORRESPONDENCE to `IntakeDomain` | Edit `intake_router/router.py:33` | New enum value after BILLING |
| β.4 | Add keyword mappings | Edit `intake_router/router.py:131` | New entry in `DOMAIN_KEYWORDS` |
| β.5 | Add routing table entry | Edit `intake_router/router.py:164` | New entry in `ROUTING_TABLE` |

### SOP Sections (β.1 detail)

Write in this order, matching War-Master Protocol format:

```
1. Authority + Purpose + Preconditions
2. The Communications Lifecycle (6 phases with operational detail)
   2.1 SWEEP — inbound collection across all channels
   2.2 CLASSIFY — priority (P0-P2-Noise) + channel + handler
   2.3 COMPOSE — outbound drafting with tone/format per channel
   2.4 RELAY — inter-session handoff (CONTEXT/TASK/DISCIPLINE/PROVENANCE)
   2.5 DISPATCH — cross-channel routing logic
   2.6 VERIFY — delivery confirmation + response tracking
3. Channel Registry (table)
4. Handler Taxonomy
5. Correspondence State Machine (with diagram)
6. Trigger Modes (3 modes)
7. Handoff Relay Format (canonical block structure)
8. Integration Points (ledger, router, contrib engine, fieldwork)
9. Injection Pattern (how to invoke this SOP in any session)
```

### Intake Router Update (β.3-β.5 detail)

```python
# In IntakeDomain enum (after BILLING):
CORRESPONDENCE = "correspondence"

# In DOMAIN_KEYWORDS (new entry):
IntakeDomain.CORRESPONDENCE: (
    "email", "reply", "respond", "follow-up", "followup",
    "recruiter", "maintainer", "draft", "send",
    "correspondence", "letter", "outreach", "communicate",
    "mail", "triage", "inbox",
),

# In ROUTING_TABLE (new entry):
IntakeDomain.CORRESPONDENCE: RouteTarget(
    workspace="~/Workspace/organvm-iv-taxis/orchestration-start-here",
    archetype="V",
    agent="claude",
    token_budget="medium",
),
```

---

## Phase γ — OPERATE (Record to Ledger)

| Step | Procedure | Tool | Output |
|------|-----------|------|--------|
| γ.1 | Append 3 actions to `action_ledger/data/actions.yaml` | Edit | `act-S51-0401-{001,002,003}` |
| γ.2 | Append sequence to `action_ledger/data/sequences.yaml` | Edit | `seq-S51-001` |
| γ.3 | Close sequence | `python -m action_ledger sequence close --session S51` | Sequence marked closed |
| γ.4 | Compose chain | `python -m action_ledger chain close-session --session S51` | `chain-S51-001` |

### Action Templates (γ.1 detail)

```yaml
- id: act-S51-0401-001
  timestamp: '<generate at execution time>'
  session: S51
  verb: formalized_sop
  target: communications-correspondence
  context: "6-phase lifecycle unifying mail-triage, handoff relay, outbound compose, cross-channel dispatch"
  params:
    abstraction: 0.7
    maturity: 0.5
  produced:
  - type: sop
    ref: docs/sop-communications-correspondence.md
  routes:
  - kind: feeds
    target: intake_router:correspondence
    amount: 0.0
  origin: manual
  sequence_id: seq-S51-001

- id: act-S51-0401-002
  timestamp: '<generate at execution time>'
  session: S51
  verb: defined_lifecycle
  target: relay-protocol-6-phase
  context: "SWEEP>CLASSIFY>COMPOSE>RELAY>DISPATCH>VERIFY. State: RECEIVED>TRIAGED>COMPOSED>DISPATCHED>CONFIRMED>CLOSED"
  params:
    abstraction: 0.8
    maturity: 0.4
  produced: []
  routes:
  - kind: refines
    target: docs/mail-triage-2026-04-01.md
    amount: 0.0
  origin: manual
  sequence_id: seq-S51-001

- id: act-S51-0401-003
  timestamp: '<generate at execution time>'
  session: S51
  verb: unified_subsystems
  target: mail-triage+handoff+relay+dispatch
  context: "4 fragmented patterns > 1 SOP. Mail-triage=Phase 1-2. Handoff=Phase 4. New: Phase 3,5,6"
  params:
    abstraction: 0.5
    maturity: 0.6
  produced: []
  routes:
  - kind: continues
    target: act-S48-0401-006
    amount: 0.0
  origin: manual
  sequence_id: seq-S51-001
```

---

## Phase δ — VERIFY

| Step | Procedure | Command | Expected |
|------|-----------|---------|----------|
| δ.1 | SOP completeness | `grep -c "^## " docs/sop-communications-correspondence.md` | ≥ 9 sections |
| δ.2 | Ledger entries | `python -m action_ledger show --session S51` | 3 actions |
| δ.3 | Sequence state | `python -m action_ledger sequence show --session S51` | Closed |
| δ.4 | Intake router | `python -m intake_router table` | CORRESPONDENCE row present |
| δ.5 | Tests | `python -m pytest tests/ -q` | 240+ passing, 0 failures |

---

## Phase ε — PRECIPITATE (Forward Deposit + Stop)

The portal does not destroy itself. It deposits the baton for the next runner and stops.

| Step | Procedure | Output |
|------|-----------|--------|
| ε.1 | Commit all artifacts | `feat: S51 — communications & correspondence relay protocol formalized` |
| ε.2 | Push to origin | local:remote = 1:1 |
| ε.3 | Write `RECEIPT.md` in this directory | Forward deposit for next portal |
| ε.4 | If next task is predictable, seed `tasks/<next-slug>/BRIEFING.md` | Pre-written war report for next intervention |
| ε.5 | **STOP** | Do not evaporate. Do not continue. The operator decides what happens next. |

```bash
git add docs/sop-communications-correspondence.md \
       action_ledger/data/actions.yaml \
       action_ledger/data/sequences.yaml \
       action_ledger/data/chains.yaml \
       intake_router/router.py \
       tasks/communications-correspondence-relay/RECEIPT.md

git commit -m "feat: S51 — communications & correspondence relay protocol formalized"
git push origin main
```

### RECEIPT.md Template

Write this as the final act:

```markdown
# Receipt: communications-correspondence-relay

**Completed:** <timestamp>
**Session:** S51
**Commit:** <sha>

## What Was Done
- <artifacts produced, files modified, tests passed>

## What Was NOT Done (and why)
- <anything deferred, with reason — these are the front lines that remain>

## Forward Deposit

### Next Portal Location
`tasks/<next-slug>/`

### Next Portal Prompt
\`\`\`
cd ~/Workspace/organvm-iv-taxis/orchestration-start-here/tasks/<next-slug>/
claude
\`\`\`

### Next War Report (pre-seeded)
<the front line that remains after this portal's intervention>
<which attractor is now gaining vs losing>
<the K-doors that need opening next>
```

---

The avalanche pauses here. The operator reads the receipt. If they open a terminal at the next portal location and prompt, the avalanche continues. If they don't, the receipt waits. The portal's evidence persists in git. The trajectory has shifted. The next intervention knows where to begin.
