# F-59: Workspace Write Policy

> **Governance**: `governance-rules.json` Article VI (Seed Contracts)
> **Scope**: Agent filesystem write permissions and enforcement
> **Version**: 1.0
> **Status**: Policy Document
> **Backlog**: F-59
> **Reference**: `docs/domus-agent-infrastructure.md` (Step 9)

---

## Why This Exists

AI coding agents have filesystem write access. Without explicit boundaries, agents can write to arbitrary locations — modifying system files, overwriting personal documents, or creating files outside the workspace that are invisible to version control and audit.

This policy defines exactly where agents may write, what they may not touch, and how violations are detected and handled.

---

## Allowed Write Zones

### Zone 1: Workspace (`$WORKSPACE_ROOT`)

**Path**: `~/Workspace/`
**Permission**: Read + Write
**Constraint**: Agent must `cd` into the specific repo directory before writing. No writes to the workspace root itself.

```
~/Workspace/
├── organvm-i-theoria/repo-name/   ← agent may write here (after cd)
├── organvm-iv-taxis/repo-name/    ← agent may write here (after cd)
└── ...
```

**Rules**:

- Always `cd` into the target repo before running any command that produces output files
- Never write to `~/Workspace/` root (it is not a git repo)
- Respect `.gitignore` — do not commit generated artifacts unless the repo expects them (e.g., `a-i--skills/.build/`)
- Never overwrite protected files without reading them first (see Data Integrity Rules below)

### Zone 2: Agent Subsystem (`$AGENTS_ROOT`)

**Path**: `~/Agents/`
**Permission**: Read + Write
**Purpose**: Caches, logs, temporary storage, session state

```
~/Agents/
├── cache/       ← model weights, embeddings, downloaded assets
├── config/      ← agent-specific configuration
├── logs/        ← run logs (structured by date and run ID)
├── tmp/         ← ephemeral scratch space (cleaned periodically)
└── sessions/    ← persisted session state
```

**Rules**:

- Log files must go in `$AGENTS_LOG` (`~/Agents/logs/`), not in repo directories
- Cache files must go in `$AGENTS_CACHE` (`~/Agents/cache/`), not in `/tmp/` or home root
- Session exports go in `$AGENTS_ROOT/sessions/<agent-name>/`

### Zone 3: System Temporary (`$TMPDIR`)

**Path**: Set by OS (typically `/var/folders/.../T/`)
**Permission**: Read + Write
**Purpose**: Ephemeral scratch that the OS may clean at any time

**Rules**:

- Use `$TMPDIR` for truly ephemeral operations (pipe buffers, intermediate transforms)
- Do not store anything in `$TMPDIR` that must survive a reboot
- Prefer `$AGENTS_TMP` (`~/Agents/tmp/`) for scratch that should persist across commands within a session

---

## Forbidden Write Zones

### Home Root (`~/`)

Agents must not create files directly in the home directory. All agent artifacts belong in `$WORKSPACE_ROOT` or `$AGENTS_ROOT`.

**Exception**: Dotfiles managed by chezmoi (e.g., `~/.zshrc`, `~/.claude/`) may be read but not written by agents. Only chezmoi modifies these files.

### Human Directories

| Path | Status | Reason |
|---|---|---|
| `~/Documents/` | Forbidden | Personal documents — not agent territory |
| `~/Desktop/` | Forbidden | User's visual workspace |
| `~/Downloads/` | Forbidden | Browser downloads — untrusted inbound |
| `~/Pictures/` | Forbidden | Personal media |
| `~/Music/` | Forbidden | Personal media |
| `~/Movies/` | Forbidden | Personal media |

### System Directories

| Path | Status | Reason |
|---|---|---|
| `/usr/` | Forbidden | System binaries |
| `/etc/` | Forbidden | System configuration |
| `/opt/` (except `/opt/homebrew/`) | Forbidden | Optional system packages |
| `/var/` (except `$TMPDIR`) | Forbidden | System state |
| `/Library/` | Forbidden | System libraries |
| `~/Library/` | Forbidden (except LaunchAgents) | User libraries — managed by apps |

### Special Cases

| Path | Status | Reason |
|---|---|---|
| `/opt/homebrew/` | Read only for agents | Homebrew manages this — use `brew install` |
| `/opt/anaconda3/` | Read only for agents | Anaconda manages this — use `conda` or `pip` in venvs |
| `~/.cargo/` | Read only for agents | Rustup manages this — use `cargo` commands |

---

## Data Integrity Rules

These rules apply to all writes within allowed zones.

### Protected Files

The following files must never be overwritten wholesale. Always read before write, apply targeted edits:

| File | Location | Guard |
|---|---|---|
| `registry-v2.json` | `meta-organvm/organvm-corpvs-testamentvm/` | `save_registry()` refuses <50 entries |
| `registry.json` | `orchestration-start-here/` | Same guard |
| `governance-rules.json` | `orchestration-start-here/` | Manual review required |
| `system-metrics.json` | Multiple locations | Computed — never hand-edit |
| `seed.yaml` | Every repo root | Read before modifying |

### Write Protocol for Data Files

1. **Read** the existing file content
2. **Parse** into structured data
3. **Apply** targeted modifications
4. **Validate** the result (schema check, entry count, integrity)
5. **Write** the modified content
6. **Verify** the write succeeded (re-read and compare)

### Git Commit Rules

- Never commit secrets (`.env`, credentials, API keys, tokens)
- Never commit large binaries without explicit approval
- Always use specific `git add <file>` — never `git add -A` or `git add .`
- Commit messages in imperative mood, under 72 characters

---

## Enforcement Layers

### Layer 1: CLAUDE.md Instructions (Soft)

Every repo's `CLAUDE.md` includes write policy rules. AI agents that follow instructions will respect these boundaries.

**Effectiveness**: High for well-behaved agents (Claude Code, Cursor). No protection against agents that ignore instructions.

### Layer 2: Pre-Commit Hooks (Medium)

Git hooks that reject commits containing files from forbidden paths:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Reject commits that include files outside allowed paths
FORBIDDEN_PATTERNS=(
  "^/Users/.*/Documents/"
  "^/Users/.*/Desktop/"
  "^/Users/.*/Downloads/"
  "^/usr/"
  "^/etc/"
)

for file in $(git diff --cached --name-only); do
  abs_path="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"
  for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    if [[ "$abs_path" =~ $pattern ]]; then
      echo "ERROR: Commit includes file in forbidden path: $abs_path"
      exit 1
    fi
  done
done
```

**Effectiveness**: Catches violations at commit time. Does not prevent writes — only prevents commits.

### Layer 3: Agent Wrapper Scripts (Hard)

Wrapper scripts that intercept agent commands and validate write targets:

```bash
#!/usr/bin/env bash
set -euo pipefail

# agent-guard.sh — wraps agent CLI invocations
ALLOWED_ROOTS=(
  "$WORKSPACE_ROOT"
  "$AGENTS_ROOT"
  "$TMPDIR"
)

validate_write_target() {
  local target="$1"
  local abs_target
  abs_target="$(realpath "$target" 2>/dev/null || echo "$target")"

  for root in "${ALLOWED_ROOTS[@]}"; do
    if [[ "$abs_target" == "$root"* ]]; then
      return 0
    fi
  done

  echo "BLOCKED: Write to $abs_target is outside allowed zones"
  echo "Allowed: ${ALLOWED_ROOTS[*]}"
  return 1
}
```

**Effectiveness**: Prevents writes at execution time. Requires wrapping every agent invocation.

---

## Violation Response

When a write policy violation is detected:

### Severity Levels

| Level | Example | Response |
|---|---|---|
| **Info** | Agent writes to `$AGENTS_TMP` instead of `$TMPDIR` | Log, no action |
| **Warning** | Agent writes to `~/` root | Log, alert operator, allow (may be intentional) |
| **Error** | Agent writes to `~/Documents/` | Log, alert, block write |
| **Critical** | Agent writes to `/etc/` or `/usr/` | Log, alert, block, terminate session |

### Response Protocol

1. **Log**: Record the violation in `$AGENTS_LOG/<run-id>/violations.log`
   - Timestamp, agent name, attempted path, severity level
2. **Alert**: Notify the operator (stdout warning or notification)
3. **Block**: Prevent the write from completing (Layer 3 enforcement)
4. **Terminate**: Kill the agent session if critical violation detected

### Post-Incident Review

After any Error or Critical violation:

1. Review the session log to understand context
2. Determine if the violation was intentional (operator error) or emergent (agent misbehavior)
3. Update CLAUDE.md or wrapper scripts to prevent recurrence
4. File an issue if the agent's behavior indicates a bug

---

## Quick Reference Card

```
WRITE ALLOWED:
  ~/Workspace/<organ>/<repo>/   (after cd into repo)
  ~/Agents/                     (logs, cache, sessions, tmp)
  $TMPDIR                       (ephemeral scratch)

WRITE FORBIDDEN:
  ~/                            (home root)
  ~/Documents/                  (personal)
  ~/Desktop/                    (personal)
  ~/Downloads/                  (personal)
  /usr/, /etc/, /opt/           (system)
  ~/Library/                    (apps)

PROTECTED FILES (read before write, never overwrite wholesale):
  registry-v2.json, registry.json, governance-rules.json,
  system-metrics.json, seed.yaml

ENFORCEMENT:
  Soft   → CLAUDE.md instructions
  Medium → Pre-commit hooks
  Hard   → Agent wrapper scripts
```

---

## References

- `docs/domus-agent-infrastructure.md` — Full agent infrastructure specification
- `governance-rules.json` — System governance rules
- `CLAUDE.md` (workspace root) — Data Integrity Rules section
- `domus-semper-palingenesis` — Chezmoi environment controller
