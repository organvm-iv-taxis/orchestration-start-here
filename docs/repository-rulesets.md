# Org-Wide Repository Rulesets

> **Governance**: Feature Backlog F-17
> **Scope**: All GitHub organizations in the ORGANVM system
> **Version**: 1.0

---

## Purpose

Define GitHub repository rulesets that enforce branch protection, commit conventions, and merge requirements across all organs. Rulesets replace per-repo branch protection rules with org-level policies that can be applied consistently.

---

## Ruleset Definitions

### Ruleset 1: Main Branch Protection

**Applies to**: `main` branch across all repos

| Rule | Setting | Notes |
|---|---|---|
| Restrict deletions | Enabled | `main` cannot be deleted |
| Restrict force pushes | Enabled | No `git push --force` to `main` |
| Require linear history | Enabled | Squash merges only (matches branching strategy) |
| Require signed commits | Disabled | Not enforced yet (aspirational) |

### Ruleset 2: Required Status Checks

**Applies to**: `main` branch, all repos with CI

| Rule | Setting |
|---|---|
| Require status checks to pass | Enabled |
| Required checks | `ci` (matches workflow job name) |
| Strict status checks | Enabled (branch must be up to date) |

### Ruleset 3: Required Reviews (Flagships Only)

**Applies to**: `main` branch on flagship repos only

| Rule | Setting |
|---|---|
| Required approving reviews | 1 minimum |
| Dismiss stale reviews | Enabled |
| Require review from CODEOWNERS | Enabled |

**Flagship repos**: `orchestration-start-here`, `agentic-titan`, `organvm-corpvs-testamentvm`, `organvm-engine`, and any repo with `tier: flagship` in `seed.yaml`.

### Ruleset 4: Commit Metadata

**Applies to**: All repos (advisory in Phase 1, blocking in Phase 2)

| Rule | Setting |
|---|---|
| Commit message pattern | `^(feat|fix|docs|chore|refactor|test|ci|style|perf|build|revert)(\(.+\))?!?: .+` |
| Require conventional commits | Pattern-matched |

---

## Rollout Strategy

### Phase 1 — Flagships (Immediate)

Apply Rulesets 1, 2, and 3 to:
- `organvm-iv-taxis/orchestration-start-here`
- `organvm-iv-taxis/agentic-titan`
- `meta-organvm/organvm-corpvs-testamentvm`
- `meta-organvm/organvm-engine`

### Phase 2 — Standard Repos

Apply Rulesets 1 and 2 to all repos with `tier: standard` and passing CI. Skip Ruleset 3 (reviews) since most standard repos are single-maintainer.

### Phase 3 — Infrastructure Repos

Apply Ruleset 1 only to infrastructure repos (`.github`, `org-dotgithub`). These rarely need CI gates but should prevent force-push accidents.

### Phase 4 — Commit Convention Enforcement

Enable Ruleset 4 as blocking (not just advisory) once all active contributors are using conventional commits consistently.

---

## GitHub CLI Commands

### Create an org-level ruleset

```bash
# Create ruleset via GitHub API
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /orgs/organvm-iv-taxis/rulesets \
  -f name="main-branch-protection" \
  -f target="branch" \
  -f enforcement="active" \
  -f 'conditions[ref_name][include][]=refs/heads/main' \
  -f 'rules[][type]=deletion' \
  -f 'rules[][type]=non_fast_forward' \
  -f 'rules[][type]=required_linear_history'
```

### Create required status checks

```bash
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /orgs/organvm-iv-taxis/rulesets \
  -f name="required-ci" \
  -f target="branch" \
  -f enforcement="active" \
  -f 'conditions[ref_name][include][]=refs/heads/main' \
  -f 'rules[0][type]=required_status_checks' \
  -f 'rules[0][parameters][required_status_checks][0][context]=ci' \
  -f 'rules[0][parameters][strict_required_status_checks_policy]=true'
```

### List existing rulesets

```bash
gh api /orgs/organvm-iv-taxis/rulesets
```

### Apply to specific repos (repo-level ruleset)

```bash
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  /repos/organvm-iv-taxis/orchestration-start-here/rulesets \
  -f name="flagship-reviews" \
  -f target="branch" \
  -f enforcement="active" \
  -f 'conditions[ref_name][include][]=refs/heads/main' \
  -f 'rules[0][type]=pull_request' \
  -f 'rules[0][parameters][required_approving_review_count]=1' \
  -f 'rules[0][parameters][dismiss_stale_reviews_on_push]=true' \
  -f 'rules[0][parameters][require_code_owner_review]=true'
```

### Audit all rulesets across orgs

```bash
for org in organvm-iv-taxis meta-organvm organvm-i-theoria omni-dromenon-machina organvm-iii-ergon; do
  echo "=== $org ==="
  gh api "/orgs/$org/rulesets" --jq '.[].name' 2>/dev/null || echo "  (no rulesets or no access)"
done
```

---

## Exceptions

- **Billing-locked orgs** (e.g., `organvm-i-theoria`): Rulesets require GitHub Team or Enterprise plan. Free orgs can use repo-level branch protection instead (limited feature set).
- **Archived repos**: No rulesets needed — archived repos are read-only by definition.
- **LOCAL repos**: No rulesets until promoted to CANDIDATE (CI must exist first).

---

## References

- [CODEOWNERS Strategy](codeowners-strategy.md) — Review routing that rulesets enforce
- [Branching Strategy](branching-strategy.md) — Trunk-based model these rulesets protect
- [CI Templates](ci-templates.md) — Status check names that rulesets require
- `governance-rules.json` — Article VI (promotion state machine)
