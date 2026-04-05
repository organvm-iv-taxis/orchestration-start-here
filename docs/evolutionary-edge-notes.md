# Evolutionary Edge Notes — orchestration-start-here → successor

**Date:** 2026-04-05
**Purpose:** Document structural constraints in this version that the successor can transcend.

---

## 1. Package Architecture — Three Siblings, No Parent

This repo contains three independent Python packages (`contrib_engine`, `action_ledger`, `intake_router`) that share no common library. Each was grown organically for a different purpose.

**Constraint in this version:** The packages import each other directly (action_ledger emits into contrib_engine's data paths), but there's no shared foundation — no common schemas, no shared config loading, no unified CLI entry point. The `pyproject.toml` lists three separate `[project.scripts]` entry points.

**Evolutionary possibility:** The successor can design a shared kernel that the three packages compose from — common schema types (Pydantic models for actions, routes, atoms), a unified config loader, and a single CLI with subcommands. This turns siblings into layers.

---

## 2. Linting — 160 Remaining Violations at Birth

Ruff was introduced on 2026-04-05 with 269 violations found, 111 auto-fixed, 160 remaining. The bulk (138) are line-length violations — lines grown beyond 100 chars over months of development without enforcement.

**Constraint in this version:** Fixing 138 line-length violations requires judgment about where to break lines, which affects readability differently per module. Bulk reformatting risks introducing bugs in string literals, URLs, and complex expressions.

**Evolutionary possibility:** The successor starts with ruff enforcement from commit 0. No accumulated debt. The line-length convention (100 chars) and rule set (`E`, `F`, `I`, `N`, `W`, `UP`) are established and can be inherited.

---

## 3. Cross-Boundary Imports — Flat Structure Limits

All three packages and the `scripts/` directory live at the repo root. This works because `pythonpath = ["."]` in pytest config makes everything importable. But it means there's no isolation — any module can import any other module.

**Constraint in this version:** The flat structure was necessary for rapid development of the contrib_engine, action_ledger, and intake_router as they co-evolved. Enforcing boundaries now would require refactoring import paths across 246 tests.

**Evolutionary possibility:** The successor can use a `src/` layout with explicit public APIs per package. Each package declares what it exports; internal modules are private. Cross-package communication goes through defined interfaces, not direct imports.

---

## 4. SOP Corpus — Documents Without Executable Hooks

23 SOPs in `docs/` define protocols with ledger emissions, but no tooling reads these SOPs at runtime. They're human-readable documents, not machine-executable specifications.

**Constraint in this version:** The SOPs were formalized as markdown for immediate value — agents and humans can read and follow them. Making them executable (YAML specs consumed by an SOP runner) requires building the runner first.

**Evolutionary possibility:** The successor can design SOPs as YAML specifications (like the prompt chains in `praxis-perpetua/library/chains/`) with a runtime that:
- Validates phase transitions
- Emits ledger entries automatically at phase boundaries
- Enforces checkpoint gates
- Tracks SOP execution state in `XGR-META.yaml`-style metadata files

This turns SOPs from documents into infrastructure.
