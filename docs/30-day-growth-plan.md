# 30-Day Growth Plan Template

> **Governance**: Feature Backlog F-08
> **Scope**: New repo or organ onboarding across the eight-organ system
> **Version**: 1.0

---

## Purpose

A reusable 4-week template that takes a newly created (or newly adopted) repo from empty shell to governance-compliant, portfolio-ready member of the ORGANVM system. Each week has a clear deliverable gate and an epistemic tuning checkpoint.

---

## Week 1 — Canonical Spine

**Goal**: The repo has the minimum structural files required for any ORGANVM repo.

### Deliverables

- [ ] `seed.yaml` — organ membership, tier, promotion_status (LOCAL), produces/consumes edges
- [ ] `README.md` — project name, one-paragraph description, quickstart, license badge
- [ ] `CLAUDE.md` — stack, directory structure, key commands, ORGANVM context block
- [ ] `.gitignore` — language-appropriate ignores
- [ ] 4-verb lifecycle awareness — FRAME/SHAPE/BUILD/PROVE documented in CLAUDE.md or README

### Activities

1. Clone or init the repo
2. Copy from the appropriate organ template (see `docs/repo-templates.md`)
3. Fill `seed.yaml` fields — use `orchestration-start-here/seed-schema/` for validation
4. Write README with honest status ("Week 1 — scaffolding only")
5. First commit: `chore: canonical spine — seed.yaml, README, CLAUDE.md`

### Epistemic Tuning — Week 1

- **Breadcrumb reconciliation**: Does the seed.yaml accurately reflect what the repo will produce/consume? Cross-check against `registry-v2.json` edges for sibling repos.
- **Staleness check**: Is the README description still accurate after the first few commits? Update immediately if scope shifted during setup.

---

## Week 2 — Session Protocol

**Goal**: The repo supports structured development sessions with traceability.

### Deliverables

- [ ] First FSBP session completed and documented
- [ ] Breadcrumb trail established (session logs, plan files)
- [ ] WIP tracking operational (issues or local plan files)
- [ ] `.claude/plans/` directory created with at least one dated plan

### Activities

1. Run a full FRAME → SHAPE → BUILD → PROVE cycle on a small task
2. Create the first issue(s) reflecting actual work items
3. Establish breadcrumb convention: `plans/YYYY-MM-DD-{slug}.md`
4. Document session outcomes — what was learned, what was deferred

### Epistemic Tuning — Week 2

- **Breadcrumb reconciliation**: Review all plan files created this week. Do they reflect what actually happened, or do they describe abandoned approaches? Archive stale plans to `plans/archive/`.
- **Staleness check**: Re-read CLAUDE.md after completing the first session. Update any commands, paths, or architectural assumptions that changed.

---

## Week 3 — Taxis Upgrades

**Goal**: The repo meets ORGAN-IV governance standards and is CI-green.

### Deliverables

- [ ] CI pipeline operational (GitHub Actions workflow passing)
- [ ] Registry entry added to `registry-v2.json` (or confirmed existing)
- [ ] `validate-deps.py` passes with this repo included (no back-edges)
- [ ] Governance compliance verified: correct organ, tier, promotion_status
- [ ] Promotion to CANDIDATE (if CI green + all spine files present)

### Activities

1. Add CI workflow — use `docs/ci-templates.md` for the appropriate stack
2. Ensure all tests pass locally before pushing
3. Run `python3 scripts/validate-deps.py` from `orchestration-start-here/`
4. Submit registry update PR (or self-serve if maintainer)
5. Run `python3 scripts/organ-audit.py` to confirm repo appears healthy

### Epistemic Tuning — Week 3

- **Breadcrumb reconciliation**: Compare the CI workflow against what the repo actually needs. Over-configured CI (testing code that doesn't exist yet) is as harmful as no CI.
- **Staleness check**: Is the seed.yaml `promotion_status` accurate? Does it reflect the actual state, not the aspirational state?

---

## Week 4 — Commodify and Tell the Story

**Goal**: The repo is externally presentable and promotion-ready.

### Deliverables

- [ ] Documentation complete: README has usage examples, architecture section if applicable
- [ ] Portfolio clarity: a stranger can understand what this repo does in 60 seconds
- [ ] Promotion readiness: all CANDIDATE criteria met, PUBLIC_PROCESS criteria documented
- [ ] ORGAN-VII integration: distribution profile exists (if applicable)
- [ ] Changelog or release notes for v0.1.0

### Activities

1. Apply the Stranger Test: would someone with no context understand this repo?
2. Write or refine architecture documentation
3. Create social preview image using organ palette (see `organ-aesthetic.yaml`)
4. Draft the "story" — what problem does this solve, for whom, and why does it matter?
5. If ready: submit promotion request from CANDIDATE → PUBLIC_PROCESS

### Epistemic Tuning — Week 4

- **Breadcrumb reconciliation**: Review all 4 weeks of plan files. Create a summary breadcrumb: `plans/YYYY-MM-DD-30-day-retrospective.md` documenting what worked, what was skipped, and what needs follow-up.
- **Staleness check**: Final pass on all files — README, CLAUDE.md, seed.yaml, CI config. Flag anything that drifted from reality during the 4-week sprint.

---

## Adaptation Notes

- **For organs (not individual repos)**: Scale each week to cover the flagship repo first, then fan out to standard repos. Infrastructure repos can follow a compressed 2-week variant (Weeks 1 and 3 only).
- **For existing repos being adopted**: Skip Week 1 deliverables that already exist. Focus Week 1 on auditing existing files against current standards.
- **For research repos (ORGAN-I)**: Week 4 "commodify" means "make citable" — Zenodo DOI, bibliography entry, clear abstract.

---

## References

- [Conductor Playbook](conductor-playbook.md) — FRAME/SHAPE/BUILD/PROVE lifecycle
- [Score/Rehearse/Perform](score-rehearse-perform.md) — Maturity progression model
- [Repo Templates](repo-templates.md) — Starter templates per organ archetype
- [CI Templates](ci-templates.md) — Workflow configurations by stack
