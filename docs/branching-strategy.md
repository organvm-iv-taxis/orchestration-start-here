# Branching Strategy

> **Governance**: Amendment G (Score/Rehearse/Perform lifecycle)
> **Scope**: All repositories across the eight-organ system
> **Version**: 1.0

---

## Model: Trunk-Based Development with Short-Lived Branches

All repos use **trunk-based development**: `main` is the primary branch,
feature work happens on short-lived branches, and merges use squash-merge
to keep history clean.

---

## Branch Naming

```
<type>/<slug>
```

| Type | When | Example |
|------|------|---------|
| `feat/` | New feature or enhancement | `feat/sensitivity-routing` |
| `fix/` | Bug fix | `fix/context-window-default` |
| `docs/` | Documentation only | `docs/branching-strategy` |
| `chore/` | Maintenance, CI, deps | `chore/update-ruff-config` |
| `refactor/` | Code restructuring (no behavior change) | `refactor/adapter-base-class` |

**Rules:**
- Slugs are kebab-case, max 50 characters
- No organ prefix needed (the repo already implies the organ)
- No issue numbers in branch names (link via PR body instead)

---

## Branch Lifecycle

```
main ──────────────────────────────────────────────────►
       \                                    /
        └── feat/slug ──── commits ────────┘
            (SCORE)    (REHEARSE)     (PERFORM: squash-merge)
```

1. **Create** branch from `main` at the start of REHEARSE (F-09)
2. **Commit** using conventional commits (`feat:`, `fix:`, `docs:`, etc.)
3. **Push** regularly — CI validates on every push
4. **Squash-merge** to `main` at PERFORM — produces one clean commit
5. **Delete** the branch after merge (GitHub auto-deletes if configured)

---

## Merge Strategy

### Squash Merge (default)

All PRs use **squash merge** to `main`. This produces a single commit
per feature, keeping `main` history readable.

The squash commit message should follow conventional commit format:

```
feat: sensitivity-based model routing (F-24)

- DataClassification enum with 4 tiers
- Local-only enforcement for CONFIDENTIAL/REGULATED
- AUDIT logging for regulated requests
- 13 tests added
```

### When NOT to Squash

- **Superproject pointer syncs**: Regular merge (to preserve submodule history)
- **Release branches** (if used): Regular merge with merge commit

---

## Tags and Releases

| Repo Type | Tag Format | When |
|-----------|------------|------|
| **Code repos** | `vX.Y.Z` (semver) | Significant milestones or API changes |
| **Doc repos** | `YYYY-MM-DD` | Snapshot releases |
| **Infrastructure** | `vX.Y.Z` | Breaking changes to templates/workflows |

Tags trigger release notes via GitHub Releases. Include:
- Summary of changes since last release
- Breaking changes (if any)
- Migration notes (if any)

---

## Long-Lived Branches

Long-lived branches are discouraged. If a feature takes more than
2 weeks, consider:

1. **Split** the feature into smaller PRs that can merge independently
2. **Feature flags** if partial work must land on `main` without being active
3. **Park** with a breadcrumb if the work is blocked (don't leave stale branches)

### Stale Branch Policy

Branches with no commits for 14+ days should be:
- Cleaned up (deleted) if the work is abandoned
- Rebased on `main` and continued if the work is still relevant
- Parked with a breadcrumb issue comment explaining the delay

---

## Protected Branch Rules

### main (all repos)

- **Required**: Status checks must pass before merge
- **Required**: At least 1 review (for flagship repos)
- **Forbidden**: Direct pushes (use PRs)
- **Forbidden**: Force pushes

### Flagship repos (orchestration-start-here, agentic-titan)

- All `main` protections plus:
- **Required**: `validate-dependencies` check passes
- **Required**: Governance checklist in PR is complete

---

## References

- **Score/Rehearse/Perform**: `docs/score-rehearse-perform.md` — per-PR lifecycle
- **PR Template**: `.github/PULL_REQUEST_TEMPLATE.md` — governance-aware PR form
- **Conventional Commits**: `https://www.conventionalcommits.org/`
- **Governance Rules**: `governance-rules.json` — Amendment G
