# CODEOWNERS Strategy for Organ-Aware Review

> **Governance**: Feature Backlog F-16
> **Scope**: All repositories across the eight-organ system
> **Version**: 1.0

---

## Purpose

Define CODEOWNERS patterns that reflect the organ model's separation of concerns. In a single-person system, CODEOWNERS documents **intent** — which organ is responsible for which files — so that future contributors (human or AI) route reviews correctly.

---

## Ownership Model

| Path Pattern | Owner Role | Rationale |
|---|---|---|
| `registry-v2.json` | ORGAN-IV maintainer | Single source of truth; changes ripple across all organs |
| `governance-rules.json` | ORGAN-IV maintainer | Governance amendments require deliberate review |
| `seed.yaml` | Repo primary maintainer | Organ membership and edge declarations |
| `.github/workflows/` | ORGAN-IV stage crew | CI/CD is orchestration infrastructure |
| `.github/CODEOWNERS` | ORGAN-IV maintainer | Meta-governance: who owns the ownership file |
| `docs/` | ORGAN-V (Logos) | Documentation is discourse; Logos observes and narrates |
| `src/` | Repo primary maintainer | Implementation is the repo owner's domain |
| `tests/` | Repo primary maintainer | Tests co-owned with source |
| `assets/`, `content/` | Repo primary maintainer | Creative/content assets |
| `scripts/` | ORGAN-IV stage crew | Automation scripts are orchestration concern |

---

## Template CODEOWNERS File

Place this at `.github/CODEOWNERS` in each repo. Adjust GitHub usernames/teams as the contributor base grows.

```
# CODEOWNERS — organ-aware review routing
# See: orchestration-start-here/docs/codeowners-strategy.md

# Default: repo primary maintainer
*                           @4444j99

# Governance files — ORGAN-IV maintainer
/seed.yaml                  @4444j99
/governance-rules.json      @4444j99
/registry.json              @4444j99

# CI/CD — ORGAN-IV stage crew
/.github/workflows/         @4444j99

# Documentation — ORGAN-V (Logos)
/docs/                      @4444j99
/README.md                  @4444j99
/CHANGELOG.md               @4444j99

# Source code — repo primary maintainer
/src/                       @4444j99
/tests/                     @4444j99
```

---

## Per-Organ Variations

### ORGAN-I (Theoria) — Research repos

```
# Research references require careful review
/references/                @4444j99
/docs/bibliography.md       @4444j99
```

### ORGAN-II (Poiesis) — Creative system repos

```
# Creative assets may have licensing implications
/assets/                    @4444j99
/examples/                  @4444j99
```

### ORGAN-III (Ergon) — Product repos

```
# API surfaces and public interfaces
/src/api/                   @4444j99
/src/public/                @4444j99
/pyproject.toml             @4444j99
/package.json               @4444j99
```

### ORGAN-IV (Taxis) — Orchestration repos

```
# High-sensitivity governance files
/governance-rules.json      @4444j99
/registry-v2.json           @4444j99
/scripts/validate-deps.py   @4444j99
```

---

## Aspirational Note

This system is currently operated by a single person. CODEOWNERS serves three purposes even in a solo context:

1. **Documentation of intent** — makes explicit which organ "owns" which concern
2. **AI routing** — AI agents can use CODEOWNERS to determine review scope
3. **Future-proofing** — when contributors join, ownership is already defined

As the system grows, replace `@4444j99` with GitHub teams:
- `@organvm-iv-taxis/maintainers` — ORGAN-IV core
- `@organvm-iv-taxis/stage-crew` — CI/CD and automation
- `@organvm-v-logos/editors` — Documentation reviewers

---

## Implementation

To apply CODEOWNERS across repos:

```bash
# For a single repo
cd <organ>/<repo>
mkdir -p .github
cp /path/to/template/CODEOWNERS .github/CODEOWNERS
# Edit to match repo-specific paths
git add .github/CODEOWNERS
git commit -m "chore: add CODEOWNERS for organ-aware review routing"
```

CODEOWNERS requires branch protection to be enabled for review enforcement. See [Repository Rulesets](repository-rulesets.md) for branch protection configuration.

---

## References

- [Repository Rulesets](repository-rulesets.md) — Branch protection enabling CODEOWNERS enforcement
- `governance-rules.json` — Article II (organ responsibilities)
- [Conductor Playbook](conductor-playbook.md) — Session review routing
