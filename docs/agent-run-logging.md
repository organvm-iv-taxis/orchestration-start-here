# Agent Run Logging Standard

> **Governance**: Amendment F of `governance-rules.json`
> **Scope**: All agent sessions (interactive and non-interactive)
> **Version**: 1.0
> **Issue**: F-57 (#107)

---

## Why This Exists

Agent sessions produce work across 100+ repos but leave no standardized audit trail.
The breadcrumb protocol (F-06) solves the "what happened?" question at session end.
This standard solves the "show me everything" question — full prompt, tool outputs,
file changes, and timing data for any agent run.

The non-interactive agent safety protocol (F-82) requires audit records with specific
fields. This document defines the canonical format for those records.

---

## Directory Layout

Every agent run creates a directory under `$AGENTS_LOG`:

```
$AGENTS_LOG/
└── <run-id>/
    ├── manifest.json       # Required — run metadata and audit fields
    ├── prompt.md           # Required — the prompt/task given to the agent
    ├── session.log         # Required — chronological event log
    ├── patch.diff          # Optional — git diff of changes made
    ├── breadcrumb.md       # Optional — breadcrumb:v1 block from session end
    └── artifacts/          # Optional — any additional outputs
        ├── tool-output.json
        └── ...
```

### Environment Variable

`$AGENTS_LOG` defaults to `~/.local/share/organvm/agent-runs/`.

Implementations SHOULD respect `$AGENTS_LOG` if set, falling back to the default.

### Run ID Format

Run IDs use the format: `<agent-id>_<ISO-date>_<short-uuid>`

Examples:
- `claude-code_2026-03-08_a1b2c3d4`
- `auto-sync_2026-03-08_e5f6g7h8`
- `titan-reviewer_2026-03-08_i9j0k1l2`

---

## manifest.json Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "version",
    "run_id",
    "session_id",
    "agent_name",
    "agent_type",
    "repo_path",
    "start_time",
    "end_time",
    "exit_status"
  ],
  "properties": {
    "version":          { "const": "1.0" },
    "run_id":           { "type": "string", "description": "Directory name / unique run identifier" },
    "session_id":       { "type": "string", "description": "Session ID from the orchestrator" },
    "agent_name":       { "type": "string", "description": "Agent identifier (e.g., claude-code, auto-sync)" },
    "agent_type":       { "type": "string", "enum": ["interactive", "non-interactive"] },
    "repo_path":        { "type": "string", "description": "Working directory / repo path" },
    "organ":            { "type": "string", "description": "Organ identifier (e.g., ORGAN-IV)" },
    "issue_ref":        { "type": "string", "description": "GitHub issue reference (e.g., #107)" },
    "start_time":       { "type": "string", "format": "date-time" },
    "end_time":         { "type": "string", "format": "date-time" },
    "temporal_coordinate": {
      "type": "object",
      "required": ["macro_pulse", "meso_step"],
      "properties": {
        "macro_pulse":   { "type": "integer", "description": "Global event count at session start (τ_M)" },
        "meso_step":    { "type": "integer", "description": "Turn sequence number (τ_m)" },
        "micro_density": { "type": "number", "description": "Tokens per ms (τ_µ)" }
      }
    },
    "exit_status":      { "type": "string", "enum": ["success", "failed", "rolled_back", "timeout", "cancelled"] },
    "files_read":       { "type": "array", "items": { "type": "string" } },
    "files_written":    { "type": "array", "items": { "type": "string" } },
    "rollback_events":  { "type": "array", "items": { "type": "string" } },
    "cross_organ_impulses": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "target_repo": { "type": "string" },
          "issue_number": { "type": "integer" },
          "description": { "type": "string" }
        }
      }
    },
    "token_usage": {
      "type": "object",
      "properties": {
        "input_tokens":  { "type": "integer" },
        "output_tokens": { "type": "integer" },
        "total_tokens":  { "type": "integer" }
      }
    },
    "budget": {
      "type": "object",
      "properties": {
        "max_tokens":       { "type": "integer" },
        "max_wall_clock_ms": { "type": "integer" }
      }
    },
    "commit_sha":       { "type": "string", "description": "Commit SHA if changes were committed" },
    "error":            { "type": "string", "description": "Error message if exit_status is not success" }
  }
}
```

### Example manifest.json

```json
{
  "version": "1.0",
  "run_id": "claude-code_2026-03-08_a1b2c3d4",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "claude-code",
  "agent_type": "interactive",
  "repo_path": "/Users/4jp/Workspace/organvm-iv-taxis/orchestration-start-here",
  "organ": "ORGAN-IV",
  "issue_ref": "#107",
  "start_time": "2026-03-08T10:00:00Z",
  "end_time": "2026-03-08T11:30:00Z",
  "temporal_coordinate": {
    "macro_pulse": 24029,
    "meso_step": 12,
    "micro_density": 1.2
  },
  "exit_status": "success",
  "files_read": ["docs/session-protocol.md", "governance-rules.json"],
  "files_written": ["docs/agent-run-logging.md", "scripts/validate-agent-run.py"],
  "rollback_events": [],
  "cross_organ_impulses": [],
  "token_usage": {
    "input_tokens": 45000,
    "output_tokens": 12000,
    "total_tokens": 57000
  },
  "commit_sha": "abc1234"
}
```

---

## prompt.md

The full prompt or task description given to the agent. For interactive sessions,
this is the initial task. For non-interactive sessions, this is the scheduled
task definition.

No required format — plain text or markdown. Should capture enough context that
a reviewer can understand what the agent was asked to do.

---

## session.log

Chronological log of significant events during the session. One line per event,
structured as:

```
<ISO-timestamp> <level> <event-type> <message>
```

### Event Types

| Type | Description |
|------|-------------|
| `SESSION_START` | Agent session begins |
| `SESSION_END` | Agent session completes |
| `TOOL_CALL` | Tool invoked (name + summary) |
| `TOOL_RESULT` | Tool completed (status + duration) |
| `FILE_READ` | File read operation |
| `FILE_WRITE` | File write operation |
| `SCOPE_CHECK` | Scope validation result |
| `ROLLBACK` | Rollback triggered |
| `IMPULSE` | Cross-organ impulse captured |
| `BREADCRUMB` | Breadcrumb written |
| `ERROR` | Error encountered |

### Example

```
[τ_M:24029 | τ_m:001 | τ_µ:0.8] INFO SESSION_START agent=claude-code repo=orchestration-start-here
[τ_M:24029 | τ_m:002 | τ_µ:1.1] INFO FILE_READ path=docs/session-protocol.md
[τ_M:24029 | τ_m:003 | τ_µ:1.5] INFO TOOL_CALL tool=Edit file=docs/session-protocol.md
[τ_M:24029 | τ_m:004 | τ_µ:0.9] INFO TOOL_RESULT tool=Edit status=success duration_ms=120
[τ_M:24029 | τ_m:005 | τ_µ:1.2] INFO FILE_WRITE path=docs/agent-run-logging.md
[τ_M:24029 | τ_m:006 | τ_µ:1.0] INFO BREADCRUMB issue=#107
[τ_M:24029 | τ_m:007 | τ_µ:0.7] INFO SESSION_END exit_status=success duration_ms=5400000
```

---

## patch.diff

If the agent made changes that were committed, include the full diff:

```bash
git diff HEAD~1..HEAD > patch.diff
```

If the session produced no commits, this file may be omitted or contain the
unstaged diff (`git diff`).

---

## Retention Policy

| Age | Action |
|-----|--------|
| 0–30 days | Retain all run directories |
| 30–90 days | Compress to `.tar.gz`, delete raw files |
| 90+ days | Delete compressed archives |

A future rotation script (`scripts/rotate-agent-logs.py`) will automate this.
Until then, manual cleanup is acceptable.

---

## Relationship to Existing Systems

### agent--claude-smith AuditLogEntry

The `AuditLogEntry` in `agent--claude-smith/src/hooks/self-correction.ts` captures
tool-level events in memory (CircularBuffer). To integrate with this standard:

1. Add an `onAuditEntry` callback that appends to `session.log`
2. On session completion, write `manifest.json` from the SessionState
3. Export the patch via `git diff`

This is a follow-up integration task, not part of F-57.

### agentic-titan AuditLogger

The `AuditLogger` in `agentic-titan/titan/persistence/audit.py` writes to PostgreSQL.
To integrate:

1. Add a file-based fallback that writes to the standard directory layout
2. Map `AuditEvent` fields to manifest.json fields
3. Use `session.log` format for the event stream

This is a follow-up integration task, not part of F-57.

### Breadcrumb Protocol (F-06)

The `breadcrumb.md` file in the run directory captures the breadcrumb:v1 block.
This provides a persistent copy independent of the GitHub issue comment.

### Non-Interactive Safety Protocol (F-82)

The manifest.json schema includes all fields required by F-82's audit requirements
table: session_id, agent_name, agent_type, repo_path, start/end times, files_read,
files_written, rollback_events, cross_organ_impulses, token_usage, exit_status.

---

## Validation

Use `scripts/validate-agent-run.py` to validate a run directory:

```bash
python3 scripts/validate-agent-run.py /path/to/run-directory
python3 scripts/validate-agent-run.py --all  # validate all runs in $AGENTS_LOG
```

---

## References

- **Breadcrumb Protocol**: `docs/breadcrumb-protocol.md` — session completion format (F-06)
- **Safety Protocol**: `petasum-super-petasum/docs/NON-INTERACTIVE-AGENT-SAFETY.md` — audit requirements (F-82)
- **Governance**: `governance-rules.json` — Amendment F
- **Session Protocol**: `docs/session-protocol.md` — session lifecycle
