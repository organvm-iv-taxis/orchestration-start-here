# Demystification Checklist

> **Governance**: Feature Backlog F-61
> **Scope**: Daily practice for all AI conductor sessions
> **Version**: 1.0

---

## Purpose

A 5-item daily reflection artifact that combats the "AI makes everything feel easy" illusion. When AI generates code, documentation, and architecture at speed, it creates a false sense of mastery. This checklist forces honest accounting of what you actually learned versus what you merely witnessed.

---

## The Checklist

Complete at the end of each working day (or at session boundaries for multi-session days). Store as a daily breadcrumb file.

### 1. What did I learn today?

Not "what did the AI produce" — what did **you** understand that you didn't understand before?

_Examples_:
- "I learned that `asyncio.gather` swallows exceptions by default unless you pass `return_exceptions=True`"
- "I learned that GitHub rulesets can be applied at org level, not just repo level"
- "Nothing new today — I directed work I already understood"

### 2. What assumption was wrong?

Every session surfaces at least one incorrect mental model. Name it.

_Examples_:
- "I assumed `git rebase` would preserve merge commits — it doesn't by default"
- "I assumed the CI was failing because of a test — it was a dependency resolution error"
- "I assumed seed.yaml was validated on push — it's only validated by the audit script"

### 3. What tool or pattern did I discover?

New commands, techniques, libraries, or workflows you encountered.

_Examples_:
- "Discovered `gh api` can create org-level rulesets, not just repo-level"
- "Learned the `ptw` (pytest-watch) tool for continuous test feedback"
- "Found that `jq 'select(.level == \"error\")'` filters structured logs effectively"

### 4. What would I do differently?

Hindsight reflection. No blame, just improvement.

_Examples_:
- "I should have read the existing tests before asking the AI to write new ones — it duplicated coverage"
- "I should have run `validate-deps.py` before committing — the back-edge was obvious"
- "I spent too long on formatting when the content was the priority"

### 5. What's the most important thing for tomorrow?

One sentence. Forces prioritization.

_Examples_:
- "Finish the CI pipeline for agentic-titan — everything else is blocked on it"
- "Review the 5 PRs from yesterday's batch before starting new work"
- "Read the FastAPI docs section on dependency injection before implementing auth"

---

## File Format

Store as a markdown file in the project's breadcrumb trail or a personal log directory.

**Filename**: `YYYY-MM-DD-demystification.md`

**Template**:

```markdown
# Demystification — YYYY-MM-DD

## 1. What did I learn today?


## 2. What assumption was wrong?


## 3. What tool or pattern did I discover?


## 4. What would I do differently?


## 5. What's the most important thing for tomorrow?

```

---

## Storage Options

| Location | When to Use |
|---|---|
| `<project>/.claude/breadcrumbs/` | Project-specific learning |
| `~/Documents/demystification/` | Cross-project daily practice |
| GitHub Issue (label: `reflection`) | Public accountability |

---

## Anti-Patterns to Watch For

- **"I learned everything"** — If every day feels like a breakthrough, you're confusing exposure with understanding. Test yourself: can you explain it without looking at the code?
- **"No assumptions were wrong"** — Either you're not reflecting honestly, or you're only working on things you already know. Push into unfamiliar territory.
- **"The AI did it"** — The checklist is about YOUR learning, not the AI's output. If you can't fill it in, you were a passenger, not a conductor.
- **Skipping days** — The value is in the habit, not any single entry. A one-line entry is better than no entry.

---

## References

- [Conductor Playbook](conductor-playbook.md) — Session lifecycle that generates learning opportunities
- [Three-Prompt Rule](three-prompt-rule.md) — F-60, constraining AI interaction to force understanding
- [50-Hour Learning Roadmap](learning-roadmap.md) — Structured learning to complement daily reflection
