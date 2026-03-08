# 50-Hour Learning Roadmap for AI Conductors

> **Governance**: Feature Backlog F-54
> **Scope**: Human operators directing AI agents across the ORGANVM system
> **Version**: 1.0

---

## Purpose

This is NOT "learn to code." This is "learn enough to direct AI effectively." An AI conductor needs to understand what AI is doing, verify its output, and intervene when it goes wrong — without necessarily writing every line themselves.

The roadmap covers minimum viable software engineering knowledge in approximately 50 hours, spread across 6–8 weeks.

---

## Week 1–2: Git Fundamentals (4–8 hours)

### Why This Matters

Every ORGANVM operation touches git. If you can't read a diff, resolve a conflict, or understand branch history, you can't verify what AI agents commit on your behalf.

### Core Concepts

| Concept | What to Learn | Time |
|---|---|---|
| Repository basics | init, clone, status, add, commit, push, pull | 1 hr |
| Branching | create, switch, merge, delete branches | 1 hr |
| Reading diffs | `git diff`, `git log`, understanding +/- lines | 1 hr |
| Merge conflicts | why they happen, how to resolve, when to abort | 1 hr |
| Rebasing | interactive rebase, squash, when to use vs. merge | 1–2 hr |
| Tags and releases | creating tags, semantic versioning, GitHub Releases | 30 min |
| Undoing things | reset, revert, checkout, reflog (the safety net) | 1 hr |

### Recommended Resources

- **Pro Git** (free online): https://git-scm.com/book — Chapters 1–3, 7
- **Oh My Git!** (game): https://ohmygit.org/ — Interactive visual learning
- **GitHub Skills**: https://skills.github.com/ — Guided exercises
- **Atlassian Git Tutorial**: https://www.atlassian.com/git/tutorials — Clear visual explanations

### Practice Exercise

Clone `orchestration-start-here`, create a branch, make a change, read the diff, merge it back. Then intentionally create a merge conflict and resolve it.

---

## Week 2–3: Debugging Methodology (3–5 hours)

### Why This Matters

AI generates plausible-looking code that may be subtly wrong. The conductor must be able to read error messages, form hypotheses, and isolate failures — even without deep language expertise.

### Core Concepts

| Concept | What to Learn | Time |
|---|---|---|
| Reading error messages | Stack traces, error types, line numbers | 45 min |
| Reproduce the bug | Isolating conditions, minimal reproduction | 45 min |
| Binary search debugging | Bisecting: which change introduced the bug? | 30 min |
| Print/log debugging | Strategic placement of print statements | 30 min |
| Rubber duck debugging | Explaining the problem forces understanding | 15 min |
| When to stop | Time-boxing, asking for help, escalating | 15 min |

### Recommended Resources

- **"How to Debug"** by John Regehr: https://blog.regehr.org/archives/199
- **Julia Evans' debugging zines**: https://jvns.ca/ — Visual, approachable
- **The Pragmatic Programmer** (Chapter on Debugging): Classic methodology
- **`git bisect`**: Built-in binary search for regressions

### Practice Exercise

Introduce a deliberate bug into a test file in `agentic-titan/`. Use `pytest` output to find it. Then use `git bisect` to find which commit introduced a historical regression.

---

## Week 3–4: Project Structure (2–3 hours)

### Why This Matters

When AI creates files, you need to know if they're in the right place. When AI reads a `pyproject.toml`, you need to know what it means.

### Core Concepts

| Concept | What to Learn | Time |
|---|---|---|
| Directory conventions | `src/`, `tests/`, `docs/`, `scripts/`, `.github/` | 30 min |
| Config files | `pyproject.toml`, `package.json`, `tsconfig.json`, `.gitignore` | 30 min |
| Entry points | How a program starts: `main()`, CLI commands, module imports | 30 min |
| Build systems | What "build" means: compilation, bundling, packaging | 30 min |
| Environment files | `.env`, `.envrc`, config vs. secrets | 30 min |

### Recommended Resources

- **Real Python — Python Project Structure**: https://realpython.com/python-application-layouts/
- **Node.js docs — package.json**: https://docs.npmjs.com/cli/v10/configuring-npm/package-json
- Browse ORGANVM repos: compare `agentic-titan/` (Python) vs `agent--claude-smith/` (TypeScript)

### Practice Exercise

Map the directory structure of `agentic-titan/` without reading CLAUDE.md. Then compare your map against CLAUDE.md. What did you miss? What surprised you?

---

## Week 4–5: Dependencies and Environments (4–6 hours)

### Why This Matters

"It works on my machine" is the most common failure mode. Understanding virtual environments, package managers, and version pinning prevents entire classes of errors.

### Core Concepts

| Concept | What to Learn | Time |
|---|---|---|
| Virtual environments | Python venv, Node node_modules, isolation purpose | 1 hr |
| Package managers | pip, npm/pnpm, Homebrew — what they do, lockfiles | 1 hr |
| Version pinning | Why `>=1.0,<2.0` is different from `*` | 30 min |
| Dependency conflicts | Diamond dependencies, resolution strategies | 30 min |
| Reproducibility | lockfiles, Docker, "works on CI = works anywhere" | 1 hr |

### Recommended Resources

- **Python Packaging User Guide**: https://packaging.python.org/
- **npm docs**: https://docs.npmjs.com/
- **Docker Getting Started**: https://docs.docker.com/get-started/ (conceptual, not deep dive)

### Practice Exercise

Create a fresh Python venv, install `agentic-titan` in dev mode, run tests. Then deliberately break a dependency version and observe the error.

---

## Week 5–6: CI/CD (4–6 hours)

### Why This Matters

CI is the automated quality gate. If you can't read a CI log, you can't diagnose why a PR is blocked or why a deployment failed.

### Core Concepts

| Concept | What to Learn | Time |
|---|---|---|
| What CI does | Runs tests, linting, type checking on every push | 30 min |
| GitHub Actions basics | Workflows, jobs, steps, triggers | 1 hr |
| Reading CI logs | Finding the failing step, understanding output | 1 hr |
| Common CI failures | Dependency install failures, flaky tests, timeouts | 30 min |
| CD basics | What deployment means, staging vs. production | 30 min |
| Secrets in CI | Environment variables, GitHub Secrets, never in code | 30 min |

### Recommended Resources

- **GitHub Actions docs**: https://docs.github.com/en/actions
- **ORGANVM CI Templates**: `orchestration-start-here/docs/ci-templates.md`
- Browse `.github/workflows/` in any ORGANVM repo

### Practice Exercise

Read the CI workflow for `agent--claude-smith`. Trace what happens on a push to `main`: which jobs run, in what order, what they check.

---

## Week 6–8: Architecture (As Needed, 8–12 hours)

### Why This Matters

As you direct more complex AI work — multi-repo changes, cross-organ features, system-wide refactors — you need mental models for how software systems fit together.

### Core Concepts

| Concept | What to Learn | Time |
|---|---|---|
| Modules and interfaces | How code is organized into units with clear boundaries | 1–2 hr |
| APIs and contracts | REST, CLI, function signatures — how systems talk | 1–2 hr |
| Data flow | Where data comes from, transforms, and goes | 1–2 hr |
| State management | Where state lives: files, databases, memory, environment | 1–2 hr |
| Trade-offs | Speed vs. safety, simplicity vs. flexibility, DRY vs. clarity | 1–2 hr |
| System design | How ORGANVM organs connect, dependency graph, event flow | 1–2 hr |

### Recommended Resources

- **"A Philosophy of Software Design"** by John Ousterhout — short, practical
- **"The Missing README"** by Riccomini & Ryaboy — junior engineer survival guide
- **Martin Fowler's architecture articles**: https://martinfowler.com/architecture/
- **ORGANVM governance-rules.json** — a real-world architecture constraint document

### Practice Exercise

Draw the dependency graph of ORGANVM from memory. Then validate against `validate-deps.py`. Where were you wrong?

---

## Progress Tracking

Use a simple checklist. Mark each topic as:
- ⬜ Not started
- 🟡 In progress
- ✅ Comfortable enough to verify AI output

The goal is not mastery — it's **confident oversight**.

---

## References

- [Conductor Playbook](conductor-playbook.md) — The workflow you're learning to direct
- [Demystification Checklist](demystification-checklist.md) — Daily reflection to track real learning
- [30-Day Growth Plan](30-day-growth-plan.md) — Applies this learning to a real repo
