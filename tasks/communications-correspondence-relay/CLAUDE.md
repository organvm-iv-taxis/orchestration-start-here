# CLAUDE.md — Dispatch Portal

**Type:** Ephemeral task portal
**Lifecycle:** INJECT → CREATE → OPERATE → VERIFY → EVAPORATE

This directory is a dispatch portal. It opens here and reaches into whatever workspaces the task requires, touching nothing on the way through. Once the task is complete and artifacts land in their proper locations, this directory evaporates — the portal closes, evidence persists in the ledger and git history.

## Portal Rules

1. **Read BRIEFING.md first.** It is the mission context — vacuum identified, ideal state defined, campaign dependencies mapped.
2. **Read SEQUENCE.md for execution order.** It is the relay circuit α→ω — every SOP, skill, tool, and procedure in order.
3. **Read REFERENCES.md for external pointers.** Files, repos, channels, people — everything outside this container the task touches.
4. **Work in the parent repo and referenced workspaces**, not in this directory. This container holds instructions, not source code.
5. **Do not create files inside this directory.** Artifacts belong where the plan specifies.
6. **Every operation is a repeatable procedure.** If you can't describe what you did as a reproducible command or protocol, you haven't finished.

## Evaporation Protocol

On completion:
1. All artifacts committed to their proper locations
2. Ledger entries recorded and sequence closed
3. This directory deleted: `rm -rf tasks/communications-correspondence-relay/`
4. Deletion committed: `chore: evaporate dispatch portal — communications-correspondence-relay`

The portal closes. The evidence persists. The pattern replicates.

## Parent Context

- **Repo:** `orchestration-start-here` (ORGAN-IV, flagship)
- **Parent CLAUDE.md:** `../../CLAUDE.md`
- **Session:** S51
