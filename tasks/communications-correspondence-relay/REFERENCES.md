# References: External Pointers

Everything outside this portal that the task touches.

---

## Files to Read (before writing anything)

### Structural Templates
| File | Read for |
|------|----------|
| `docs/sop-war-master-protocol.md` | SOP format: authority, purpose, preconditions, laws/phases, injection pattern |
| `docs/score-rehearse-perform.md` | PR lifecycle phases — this task's own delivery follows this |

### Prior Art (subsystems being unified)
| File | Read for |
|------|----------|
| `docs/mail-triage-2026-04-01.md` | Phase 1-2 shape: formal sort, P0-P2 classification, handler assignment, ledger state |
| `docs/handoff-72h-reconciliation.md` | Phase 4 shape: handoff format, forward blocks, relay prompts |
| `docs/handoff-maddie-spiral-path-2026-04-01.md` | Phase 4 shape: large intake handoff, 13-section structure |

### Code to Understand
| File | Read for |
|------|----------|
| `action_ledger/schemas.py` | `Action`, `Sequence`, `Chain`, `RouteKind`, `ActionOrigin` — the data model for ledger entries |
| `action_ledger/ledger.py` | `record()`, `compose_chain()`, `close_session()` — the functions to call |
| `action_ledger/emissions.py` | `emit_state_change()` — auto-emission on state transitions |
| `intake_router/router.py` | `IntakeDomain`, `DOMAIN_KEYWORDS`, `ROUTING_TABLE` — where to add CORRESPONDENCE |

### Event Catalog
| File | Read for |
|------|----------|
| `docs/event-catalog.yaml` | Inter-organ dispatch event schema — correspondence events may need to be cataloged here |

---

## Channels

| Channel | Access Method | Agent Capability |
|---------|--------------|------------------|
| Email (Gmail) | Gmail API via MCP / `mcp__claude_ai_Gmail__*` | Read, search, draft |
| GitHub | `gh` CLI / GitHub MCP / `mcp__github__*` | Issues, PRs, comments, reviews |
| iMessage | Manual (human handler) | Read-only (screenshot PDF) |
| LinkedIn | Manual (human handler) | No API access |
| Slack | Slack API (if configured) | Messages, channels |
| USPS (physical) | Informed Delivery email | Read-only, informational |

---

## People / Counterparties (from mail-triage)

| Name | Channel | Context |
|------|---------|---------|
| Ryan McKellips | Email | Grafana Labs recruiter — P0 scheduling |
| Ivan Shymko (ishymko) | GitHub | a2aproject maintainer — PR #915 split |
| Alex Morris | Email/web | tribecode.ai — MCP wave inbound lead |
| Maddie | iMessage/Drive | Spiral Path collaborator — ORGAN-III |

---

## Memory Files (contextual)

| Memory | Relevance |
|--------|-----------|
| `feedback_pr_comment_discipline.md` | GitHub correspondence constraints |
| `feedback_realm_boundary_handoff.md` | Handoff relay pattern origin |
| `feedback_network_routing_mode.md` | Act as routing junction, not executor |
| `project_mail_triage_event.md` | Mail-triage event shape — Phase 1-2 source |
| `project_inbound_tribecode.md` | Active outbound correspondence target |
| `user_maddie_relationship.md` | Communication style context |
