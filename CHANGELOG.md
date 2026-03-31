# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Emissions module (2026-03-31)** — `action_ledger/emissions.py` (106 lines) — self-recording state changes via `emit_state_change()`. Auto-records transitions as ledger entries with `origin: emitted`. 230-line test suite.
- **Action Ledger Phases 2-4 (2026-03-31)** — routes.py (bidirectional route graph, lineage tracing, provenance), cycles.py (4 detection methods: verb sequences, trajectories, intents, stalls), chain composition, close_session(). 57 action_ledger tests, 233 total suite.
- **Temporal coordinate system (2026-03-31)** — Article H (temporal coordinates) + manifest schema for action ledger temporal model.
- **Plan archiving (2026-03-31)** — 6 superseded plans moved to `.claude/plans/archive/2026-03/`. Archive protocol operational.
- **Memory persistence backup (2026-03-31)** — `.meta/memory/` snapshot of 29 Claude Code memory files committed to repo. Soul persists in git; local:remote = 1:1 for all artifacts.
- **Fieldwork Intelligence MVP (2026-03-31)** — Layer 1 built: `fieldwork.py` (record + show), `FieldObservation` model, `FieldworkIndex`, 10 categories, 5-level spectrum, 14 tests. Layers 2-4 designed (issue #145).
- **Superproject Topology Audit SOP (2026-03-31)** — formalized from 5-agent arrhythmic trace into 7+1 step reproducible procedure (`docs/superproject-topology-audit.md`).
- **Action Ledger design (2026-03-31)** — system-wide process recording with synthesizer paradigm. Plan at `.claude/plans/scalable-baking-conway.md`, spec pending.
- **ORGAN-IV Remediation Complete (2026-03-31)** — achieved 0% gap ratio in superproject boundary; all 14 repositories (`cvrsvs-honorvm`, `aerarium--res-publica`, etc.) declared and synced.
- **System Audit (2026-03-31)** — identified casing drift in `cvrsvs-honorvm` functional class and archive candidacy for `announcement-templates`.
- Documentation sync — updated `GEMINI.md` and `AGENTS.md` with current 14-repo boundary and sync timestamps.
- Agent Run Logging Standard (`docs/agent-run-logging.md`) — directory layout, manifest schema, session log format (F-57)
- Run directory validation script (`scripts/validate-agent-run.py`) with JSON output mode (F-57)
- Breadcrumb Protocol (`docs/breadcrumb-protocol.md`) — standardized session completion format with machine-parseable delimiters (F-06)
- Amendment F in governance-rules.json — Agent Coordination Visibility mandate
- Conductor Playbook (`docs/conductor-playbook.md`) — Frame/Shape/Build/Prove lifecycle reference (F-01)
- Session Protocol (`docs/session-protocol.md`) — 90-minute development ritual checklist (F-02)
- WIP limit enforcement script (`scripts/validate-wip.py`) and `wip_limits` section in governance-rules.json (F-03)
- Amendment E in governance-rules.json — Session Lifecycle Mandate
- Platinum Sprint: CI/CD workflow, standardized badge row, ADR documentation
- Initial CHANGELOG following Keep a Changelog format

## [0.1.0] - 2026-02-11

### Added

- Initial public release as part of the organvm eight-organ system
- Core project structure and documentation
- README with portfolio-quality documentation

[Unreleased]: https://github.com/organvm-iv-taxis/orchestration-start-here/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/organvm-iv-taxis/orchestration-start-here/releases/tag/v0.1.0
