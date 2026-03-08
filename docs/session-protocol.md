---
name: session-protocol
version: "1.0"
applies_to: all-organs
lifecycle: per-task
duration_minutes: 90-120
phases: [FRAME, SHAPE, BUILD, PROVE, DONE]
references:
  - docs/conductor-playbook.md
  - governance-rules.json
---

# Session Protocol — 90-Minute Development Ritual

> A concrete checklist for running a single development session using the
> Frame/Shape/Build/Prove lifecycle. See `docs/conductor-playbook.md` for
> the theory; this document is the practice.

---

## Pre-Session (2 min)

- [ ] Run `python3 scripts/validate-wip.py` — check WIP limits before starting new work
- [ ] Pick **one repo** and **one issue** (or create one)
- [ ] Write scope in one sentence: "This session will ____"

**If WIP limits are exceeded**: finish existing work before starting new work. The script output tells you which organs are over-limit.

---

## Step 1 — FRAME: Read and Orient (5 min)

- [ ] Read the repo's `CLAUDE.md` and `seed.yaml`
- [ ] Read the issue description and any linked issues
- [ ] Check recent commits (`git log --oneline -10`)
- [ ] Check CI status (green? failing? no CI?)
- [ ] Note any constraints discovered

**Output**: Understanding of current state. No code written yet.

**Exit gate**: You can explain the problem and its constraints to someone unfamiliar with the repo.

---

## Step 2 — SHAPE: Draft Micro-Plan (5 min)

- [ ] Create plan file: `.claude/plans/YYYY-MM-DD-slug.md`
- [ ] List 3–7 **acceptance criteria** (specific, testable)
- [ ] List critical files (CREATE / EDIT / DELETE)
- [ ] List out-of-scope items explicitly
- [ ] Estimate: will this fit in the remaining session time?

**Output**: Plan file committed or saved locally.

**Exit gate**: Acceptance criteria exist and are specific enough that a different person could verify them.

---

## Step 3 — Create Branch + Checklist (3 min)

- [ ] `git checkout -b feat/slug` (or `fix/slug`, `docs/slug`)
- [ ] Copy acceptance criteria into the issue as a checklist (if not already there)

---

## Step 4 — BUILD: Work in Tiny Testable Slices (60–90 min)

- [ ] Implement changes per the plan
- [ ] Run tests every 30 minutes at minimum
- [ ] If scope needs to change → back-transition to SHAPE, update the plan
- [ ] If new work is discovered → create a follow-up issue, stay in scope

**Role modes** — note which you're using per slice:

| Mode | When | Focus |
|------|------|-------|
| **Architect** | Designing interfaces, choosing patterns | Decisions, not code |
| **Implementer** | Writing production code | Code that meets criteria |
| **Tester** | Writing tests, running verification | Coverage and correctness |
| **Librarian** | Writing docs, updating metadata | Clarity and completeness |

---

## Step 5 — PROVE: Verify (5–10 min)

- [ ] Run full test suite for the repo
- [ ] Run linter (`ruff check .` / `tsc --noEmit`)
- [ ] Validate any JSON/YAML files (`python3 -c "import json; ..."`)
- [ ] Walk through acceptance criteria — each one passes?
- [ ] Check for unintended changes (`git diff` review)

**Exit gate**: All acceptance criteria verified. No test failures. No lint errors.

---

## Step 6 — DONE: Breadcrumb + Close (5 min)

- [ ] Commit with conventional commit message
- [ ] Update issue with status comment:
  ```
  **Done:**
  - [list what was completed]

  **Next:**
  - [list follow-up items, if any]

  **Commit:** <sha>
  ```
- [ ] Update `CHANGELOG.md` if the change is user-visible
- [ ] Merge branch if all criteria met, or note what remains

---

## Session Failure Protocol

Not every session succeeds. If you run out of time or hit a blocker:

1. **Commit what you have** (even if incomplete) on the feature branch
2. **Update the issue** with what was attempted and what blocked progress
3. **Do not merge** incomplete work to main
4. **Create follow-up issues** for remaining work

A failed session with a good breadcrumb is more valuable than a "successful" session with no documentation.

---

## Quick Reference

```
┌─────────────────────────────────────────────────┐
│  PRE-SESSION (2 min)                            │
│  validate-wip.py → pick repo → pick issue       │
├─────────────────────────────────────────────────┤
│  1. FRAME  (5 min)   Read code, read issue      │
│  2. SHAPE  (5 min)   Plan + acceptance criteria  │
│  3. BRANCH (3 min)   Create branch + checklist   │
│  4. BUILD  (60-90m)  Implement in small slices   │
│  5. PROVE  (5-10m)   Test, lint, verify criteria │
│  6. DONE   (5 min)   Commit, update issue, merge │
└─────────────────────────────────────────────────┘
```

---

## References

- **Conductor Playbook**: `docs/conductor-playbook.md` — phase definitions and anti-patterns
- **WIP Limits**: `governance-rules.json` → `wip_limits` — work-in-progress constraints
- **Governance Amendment E**: `governance-rules.json` → `amendments.E` — lifecycle mandate
