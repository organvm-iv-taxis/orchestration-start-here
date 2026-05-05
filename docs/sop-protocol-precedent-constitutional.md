# SOP-IV-PPC-001: Protocol → Precedent → Constitutional Decision Framework

**Version:** 1.0
**Date:** 2026-05-04
**Scope:** System-wide (any agent, any session, any decision)
**Lifecycle Stage:** ABSORB (codified 2026-05-04; second run 2026-05-05 "proceed w all" session exercised all five phases against the 6-item handoff list)
**Provenance:** Codified from `~/.claude/projects/-Users-4jp/memory/feedback_protocol_precedent_layered_framework.md` and plan `~/.claude/plans/if-protocol-doesn-t-dictate-expressive-cat.md`. Triggers: user corrections 2026-05-02 (`feedback_protocols_dictate_actions`) + 2026-05-04 (`If protocol doesn't dictate, then precedent might dictate` + `Further exploration required until impossible certainty`).

> Five-layer decision hierarchy that prevents agent deferral-to-user when protocol or precedent already speaks. Replaces ad-hoc "I don't know, ask the user" with disciplined search through layered authoritative sources.

---

## 1. When This Protocol Applies

Five invariant conditions, all of which must hold:

| # | Condition | Negative Test (does NOT apply) |
|---|-----------|-------------------------------|
| 1 | Agent is about to enumerate an action sequence or declare an item user-gated | Action is mechanically derivable with no decisional component |
| 2 | A user-prompt does not explicitly resolve the question | User explicitly authorized the specific action being considered |
| 3 | The decision is potentially recurring (similar decisions have been made before in this system) | Decision is genuinely unique to this moment with no precedent space |
| 4 | The cost of asking exceeds the cost of disciplined search | Question is small enough that asking is cheaper than searching |
| 5 | The system contains queryable precedent stores (action_ledger, feedback memories, plans, git log) | Greenfield system with no historical decision corpus |

If conditions 1-4 hold but 5 does not, build the precedent infrastructure first (SOP-IV-PPC governs its own bootstrap).

---

## 2. Protocol Phases

```
DECISION SURFACE EMERGES (action sequence to enumerate, or item to gate)
    │
    ├── Phase L1: USER PROMPT       Check current-session explicit instruction
    ├── Phase L2: PROTOCOL           Survey SOPs, plan-as-protocol, hard-rule memory
    ├── Phase L3: PRECEDENT          Search action_ledger + feedback_*.md + git log
    ├── Phase L3.5: CONST. DERIV.    Apply MEMORY rules as axioms when L3 sparse
    ├── Phase L4: FIRST-PRINCIPLES   Derive from absent rule corpus
    └── Phase L5: ASK                Surface to user only when L1-L4 exhausted
```

### Phase L1 — USER PROMPT

**Purpose:** The current-session explicit instruction is supreme. Resolves all lower layers when it speaks.

**Invariant steps:**
1. Read the current user message (and recent message history if relevant)
2. Identify any explicit instruction matching the decision verb+target
3. If found → execute per L1; record `decision_layer=L1` in audit
4. If absent or ambiguous → proceed to L2

**Anti-pattern:** treating "complete all" or "proceed all" as silent → still execute under L1 authorization.

### Phase L2 — PROTOCOL

**Purpose:** Defer to codified protocols (SOPs, plan-as-protocol, hard-rule memory).

**Invariant steps:**
1. Survey `~/Workspace/organvm/orchestration-start-here/docs/sop-*.md` for matching protocol
2. Survey active plans in `~/.claude/plans/` (most-recent first per freshness rule)
3. Survey feedback memories at `~/.claude/projects/-Users-4jp/memory/feedback_*.md`
4. If matching protocol found → execute per protocol's prescribed sequence
5. If protocol exists but ambiguous → apply protocol's "When applicable" criteria; if still ambiguous → L3
6. If no protocol → L3

**Conflict resolution:** Platform protocols (e.g., GitHub branch protection) and ORGANVM protocols (SOPs/plans) operate in different domains. Internal precedent does not override platform protocol; it CAN inform how to invoke the platform's authorized override path.

### Phase L3 — PRECEDENT

**Purpose:** Search prior decisions in this system; apply 3-of-4 rubric to determine "dictates" vs "suggests."

**Invariant steps:**
1. Query stores **exhaustively** (impossible-certainty rule):
   - `python -m action_ledger show --verb <V> --target <T>`
   - `python -m action_ledger cycles --type verb_sequence --min-recurrence 2`
   - `grep -l "<keywords>" ~/.claude/projects/-Users-4jp/memory/feedback_*.md`
   - `grep -l "<keywords>" ~/.claude/projects/-Users-4jp/memory/project_artifact_*.md`
   - `grep -l "<keywords>" ~/.claude/projects/-Users-4jp/memory/project_session_*.md`
   - GitHub API: `gh pr list ...`, `gh search prs ...`, `gh api repos/.../branches/main/protection`
   - Originating plan files (NOT briefing-recap memories — freshness rule)
2. Apply 3-of-4 rubric per match:
   - **Sample size**: n ≥ 5 ledger instances OR ≥ 2 feedback memories OR n=1 with exact verb+target+config match within 30 days
   - **Recency**: most recent within 30 days
   - **Coherence**: ≥ 80% directional agreement
   - **Domain match**: precedent verb+target matches current verb+target (not analogous-only)
3. If 3-of-4 met → precedent **dictates**, execute per precedent's mechanism
4. If below 3-of-4 → precedent **suggests**, surface alongside L3.5/L4 analysis
5. If no precedent at all → confirm exhaustive search ran (log search trail to action_ledger), proceed to L3.5

**Failure trigger:** if a single 30-day commit-log scan was the only search performed, the search was insufficient. Re-run with broader keyword set + additional stores before declaring no-precedent.

### Phase L3.5 — CONSTITUTIONAL DERIVATION

**Purpose:** When explicit precedent is sparse but the rule corpus has direct application, treat MEMORY rules as compressed precedent (not abstract first-principles).

**Trigger condition:** user signals (or has previously codified) "research until certain + never defer to human" / "system does everything else" / Conductor principle.

**Invariant steps:**
1. Identify any named MEMORY rule (#1-#61) whose verb+target hooks match the current decision
2. Apply the rule as an axiom; derive the policy answer
3. Common L3.5 hooks:
   - Rule #2 ("nothing local only") → parity-required gates
   - Rule #21 ("never preempt") → require user signal for atom-closing decisions
   - Rule #22 ("triple-check") → preservation gates with three independent checks
   - Rule #26 ("stagger") → batch-operation rate limits
   - Rule #53 ("only human closes") → per-atom user-authorization gates
4. If no rule matches → L4

### Phase L4 — FIRST-PRINCIPLES

**Purpose:** Last-resort derivation when neither protocol, precedent, nor rule corpus speaks.

**Invariant steps:**
1. Articulate the underlying constraints (safety, reversibility, blast radius, user intent inference)
2. Derive the minimal decision satisfying all constraints
3. Document the derivation reasoning so it becomes precedent for future sessions
4. If the derivation feels novel or risky → L5

### Phase L5 — ASK

**Purpose:** Surface to user only when L1-L4 are genuinely exhausted.

**Invariant steps:**
1. State precisely what was searched (which stores, which keywords)
2. State precisely what L4 derivation produced
3. Frame the question as a binary or small-N choice (avoid open-ended)
4. Wait for user answer; record in action_ledger as new precedent for next session

**Anti-pattern:** asking the user when L2/L3 has the answer but the search was insufficient. The "complete all" failure mode is enumerating L5 questions that L2/L3 already resolved.

---

## 3. Outputs

| Phase | Output | Type | Purpose |
|-------|--------|------|---------|
| L1 | Execution + audit entry `decision_layer=L1` | Action | Direct fulfillment |
| L2 | Execution per protocol + audit entry citing SOP/plan | Action + citation | Protocol-driven dispatch |
| L3 | Execution per precedent + 3-of-4 rubric verdict | Action + verdict | Precedent-driven dispatch |
| L3.5 | Execution per derived rule + axiom citation | Action + citation | Constitutional dispatch |
| L4 | Execution + first-principles derivation log | Action + reasoning | New precedent |
| L5 | User question + search-trail report | Question + audit | Genuinely novel decision |

**Cross-cutting output:** every layer logs to action_ledger so subsequent sessions can audit "was the search exhaustive?" and "which layer resolved this?"

---

## 4. Failure Modes and Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Agent enumerates L5 questions L2/L3 could resolve | User corrects: "answered before elsewhere similarly" | Re-run L2/L3 search with broader keywords; codify the corrected verdict |
| Search at L3 was non-exhaustive (single store, single keyword) | Search trail shows < 4 stores queried | Re-search across all stores listed in Phase L3 step 1 |
| Memory rule cited at L3.5 doesn't actually apply (forced fit) | Subsequent session contests the derivation | Pull citation; demote to "suggests" tier; surface as L5 question instead |
| Stale precedent cited (>30 days, unverified) | State of cited file/repo no longer matches the precedent's claim | Verify against current disk state per Memory Rule #12; if stale, demote and re-search |
| Platform protocol cited as overridable by internal precedent | Action attempts platform-protocol violation | Re-classify: platform protocols require L1 (explicit user authorization), not L3 inference |
| L1 user-prompt re-interpreted beyond literal scope | User contests with "I asked for X, not Y" | Reverse the action; re-execute under literal L1 reading |

---

## 5. Relationship to Existing SOPs

| SOP | Relationship | Integration Point |
|-----|-------------|-------------------|
| `feedback_protocols_dictate_actions` (origin) | Predecessor / L2 source | This SOP is the layered extension of the protocol-first rule |
| SOP-IV-SAD-001 (Single-Authority Data Model) | Domain example | When SAD-001 named anti-patterns ("manual parity ritual"), L3 search finds that explicit rule and dispatches accordingly |
| SOP-IV-STL-001 (Staleness Mapping) | Provides L3 freshness rules | Memory/precedent staleness uses STL-001's day-count buckets |
| SOP-IV-DSC-001 (Disposition Classification) | Frequent L2 dispatch target | When agent must classify items for disposition, DSC governs the protocol |
| `feedback_no_recovery_telemetry_2026_05_03` | L3 precedent example | Cited as recoverability constraint for deletion gates |

---

## 6. Protocol Governance

- **Owner:** ORGAN-IV (Taxis)
- **Lifecycle:** ABSORB — second-session run on 2026-05-05 exercised all five phases (L1 user authorization for the 6-item list; L2 protocol consultation; L3 precedent verification via the precedent_engine CLI; L3.5 constitutional derivation for the direct-push deviation; structural-precondition honoring for Lane I cooldown)
- **Versioning:** SemVer. Major when layer ordering changes. Minor when phase steps refined. Patch when failure-mode entries added.
- **Anti-pattern registry:**
  - "I'll just ask the user" — when L2/L3 has the answer. The framework's purpose is to prevent this.
  - "Single-store search is enough" — impossible-certainty rule requires multi-store exhaustion.
  - "Memory rule fits if I squint" — L3.5 demands direct verb+target match, not analogous-only.
  - "Briefing-recap is the answer" — freshness rule says originating plan/source wins over recap.
  - "Platform protocol = override-able by precedent" — wrong domain; require L1 explicit authorization.

- **Bootstrap requirement:** L3 needs queryable stores. Build infrastructure (action_ledger CLI + feedback memory naming convention + plan dating) before deploying SOP in a new system.
- **Review cadence:** Every 5 sessions, sample 3 decisions and verify which layer resolved them. If >40% are L5, the L2/L3 stores are under-populated and need reinforcement. If >40% are L4, the rule corpus is incomplete and needs distillation.
