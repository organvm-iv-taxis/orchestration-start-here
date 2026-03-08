# Release Discipline Checklist

> **Governance**: Feature Backlog F-15
> **Scope**: All repositories producing versioned releases
> **Version**: 1.0

---

## Purpose

Standardize the release process across code and documentation repos. Every release must be traceable, reversible, and announced through the appropriate organ channels.

---

## Code Repositories

### Pre-Release

- [ ] All CI checks passing on `main`
- [ ] No open P0/P1 issues targeting this release
- [ ] Changelog entry written for this version (follow Keep a Changelog format)
- [ ] Version bump applied:
  - Python: `pyproject.toml` version field
  - TypeScript: `package.json` version field
  - Manual: any hardcoded version strings in `__version__`, constants, or docs
- [ ] `seed.yaml` updated if promotion_status or produces/consumes edges changed
- [ ] Dependencies pinned or range-constrained (no floating `*` versions in production)
- [ ] Local smoke test: install from clean environment, run primary command/entrypoint

### Release

- [ ] Create git tag: `git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>: <one-line summary>"`
- [ ] Push tag: `git push origin v<X.Y.Z>`
- [ ] Create GitHub Release with release notes:
  ```bash
  gh release create v<X.Y.Z> --title "v<X.Y.Z>" --notes-file RELEASE_NOTES.md
  ```
- [ ] Attach build artifacts if applicable (wheels, tarballs, binaries)

### Post-Release

- [ ] Smoke test on `main` after tag (clone fresh, install, run)
- [ ] Update `registry-v2.json` if version is tracked there
- [ ] Announce via ORGAN-VII if the repo is PUBLIC_PROCESS or GRADUATED
- [ ] Document rollback procedure:
  ```bash
  # Rollback: revert to previous tag
  git checkout v<PREVIOUS>
  # Or: revert the merge commit
  git revert <merge-sha> --mainline 1
  ```
- [ ] Close the milestone (if using GitHub milestones)
- [ ] Create next-version milestone with deferred items

---

## Documentation Repositories

### Pre-Release

- [ ] All internal links verified (no broken `[text](url)` references)
- [ ] Spell check / grammar pass completed
- [ ] Table of contents or index updated if structure changed
- [ ] Metadata updated: date, version, author fields in frontmatter

### Release

- [ ] Publish: merge to `main` (triggers GitHub Pages / static site build)
- [ ] Verify published site renders correctly
- [ ] Run link checker against published URL:
  ```bash
  npx linkinator https://<org>.github.io/<repo> --recurse
  ```

### Post-Release

- [ ] Update `registry-v2.json` with new doc version or publish date
- [ ] Announce via ORGAN-VII:
  - Create or update kerygma profile if new doc repo
  - Trigger distribution dispatch event: `distribution.dispatched`
- [ ] Archive previous version if maintaining versioned docs

---

## Versioning Convention

All repos follow [Semantic Versioning](https://semver.org/):

| Change Type | Version Bump | Example |
|---|---|---|
| Breaking API change | MAJOR | 1.0.0 → 2.0.0 |
| New feature, backward-compatible | MINOR | 1.0.0 → 1.1.0 |
| Bug fix, backward-compatible | PATCH | 1.0.0 → 1.0.1 |

For pre-1.0 repos (most of the system currently): MINOR = new features, PATCH = fixes. Breaking changes are expected and don't require MAJOR bumps until 1.0.

---

## Tag Naming

Tags follow the pattern `v<MAJOR>.<MINOR>.<PATCH>`:
- `v0.1.0` — first tagged release
- `v0.2.0-rc.1` — release candidate (pre-release)
- `v1.0.0` — first stable release

See [Branching Strategy](branching-strategy.md) for tag conventions and branch protection rules around tags.

---

## References

- [Branching Strategy](branching-strategy.md) — Tag conventions and merge strategy
- [CI Templates](ci-templates.md) — Automated release workflows
- ORGAN-VII kerygma profiles — Distribution channel configuration
