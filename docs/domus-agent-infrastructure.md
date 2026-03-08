# F-56: Domus-Anchored Agent Infrastructure

> **Governance**: `governance-rules.json` Article VI (Seed Contracts)
> **Scope**: Canonical 10-step procedure for agent runtime infrastructure
> **Version**: 1.0
> **Status**: Design Document
> **Backlog**: F-56
> **Reference**: `domus-semper-palingenesis` (chezmoi-managed environment controller)

---

## Why This Exists

AI coding agents (Claude Code, Goose, Aider, Codex, etc.) need consistent runtime environments to operate reliably across sessions. Without a canonical infrastructure, each agent session starts from scratch — discovering paths, guessing tool versions, and writing to unpredictable locations.

The Domus system (managed by chezmoi at `~/Workspace/organvm-iv-taxis/domus-semper-palingenesis`) provides the environmental foundation. This document codifies the 10-step canonical procedure for anchoring agent infrastructure to that foundation.

---

## Step 1: DOMUS_ROOT — Structural Domains

**`DOMUS_ROOT` = `~/` (the home directory)**

The home directory is the root of all agent-accessible infrastructure. It is partitioned into structural domains:

| Domain | Path | Purpose |
|---|---|---|
| Workspace | `~/Workspace/` | All git repos, organized by organ |
| Agents | `~/Agents/` | Agent runtimes, caches, logs, temp storage |
| System | `~/System/` | System-level configs, LaunchAgents, logs |
| Documents | `~/Documents/` | Human documents (agents: read-only) |

**Rule**: Every path an agent uses must resolve under `DOMUS_ROOT`. Absolute paths only — never relative.

---

## Step 2: Agent Subsystem Layout

**`AGENTS_ROOT` = `~/Agents/`**

```
~/Agents/
├── cache/                  # Shared cache (model weights, embeddings, etc.)
│   ├── models/
│   └── embeddings/
├── config/                 # Agent-specific configuration
│   ├── claude-code/
│   ├── goose/
│   ├── aider/
│   └── codex/
├── logs/                   # Run logs (see Step 8)
│   └── YYYY-MM-DD/
├── tmp/                    # Ephemeral scratch space
├── sessions/               # Persisted session state
│   ├── claude-code/
│   └── goose/
└── registry.json           # CLI agent registry (see Step 5)
```

**Bootstrap**: `mkdir -p ~/Agents/{cache/{models,embeddings},config,logs,tmp,sessions}`

---

## Step 3: Environment Variable Contract

Every agent session inherits these environment variables. They are set in the shell profile (managed by chezmoi) and must not be overridden by individual agents.

| Variable | Value | Purpose |
|---|---|---|
| `DOMUS_ROOT` | `~` | Root of all infrastructure |
| `WORKSPACE_ROOT` | `~/Workspace` | All git repos |
| `AGENTS_ROOT` | `~/Agents` | Agent subsystem root |
| `AGENTS_LOG` | `~/Agents/logs` | Run log directory |
| `AGENTS_CACHE` | `~/Agents/cache` | Shared cache directory |
| `AGENTS_TMP` | `~/Agents/tmp` | Ephemeral scratch |
| `ORGANVM_REGISTRY` | `~/Workspace/organvm-iv-taxis/orchestration-start-here/registry.json` | System registry path |

### Shell Profile Integration

```bash
# ~/.zshrc (managed by chezmoi)
export DOMUS_ROOT="$HOME"
export WORKSPACE_ROOT="$HOME/Workspace"
export AGENTS_ROOT="$HOME/Agents"
export AGENTS_LOG="$AGENTS_ROOT/logs"
export AGENTS_CACHE="$AGENTS_ROOT/cache"
export AGENTS_TMP="$AGENTS_ROOT/tmp"
export ORGANVM_REGISTRY="$WORKSPACE_ROOT/organvm-iv-taxis/orchestration-start-here/registry.json"
```

---

## Step 4: Canonical Runtime Paths

Agents must use system-managed runtimes. No agent may install its own runtime or modify the system PATH.

| Runtime | Version | Path | Manager |
|---|---|---|---|
| Python | ≥3.11 | `/opt/anaconda3/bin/python3` | Anaconda |
| Node.js | ≥22 | `/opt/homebrew/bin/node` | Homebrew |
| Go | latest | `/opt/homebrew/bin/go` | Homebrew |
| Rust | latest | `~/.cargo/bin/rustc` | rustup |
| Git | latest | `/opt/homebrew/bin/git` | Homebrew |

### Virtual Environments

- Python projects: `.venv/` within the project directory (never global)
- Node projects: `node_modules/` within the project directory
- Go projects: `GOPATH` within the project or system default

**Rule**: Agents must activate the project's virtual environment before running Python commands. Never install packages globally.

---

## Step 5: CLI Agent Registry

**`~/Agents/registry.json`** tracks all installed CLI agents and their capabilities.

```json
{
  "schema_version": "1.0",
  "agents": [
    {
      "name": "claude-code",
      "binary": "claude",
      "version_command": "claude --version",
      "config_dir": "~/Agents/config/claude-code",
      "session_dir": "~/Agents/sessions/claude-code",
      "capabilities": ["code-generation", "code-review", "documentation", "testing"],
      "workspace_policy": "WORKSPACE_ROOT_ONLY"
    },
    {
      "name": "goose",
      "binary": "goose",
      "version_command": "goose --version",
      "config_dir": "~/Agents/config/goose",
      "session_dir": "~/Agents/sessions/goose",
      "capabilities": ["code-generation", "shell-execution", "web-browsing"],
      "workspace_policy": "WORKSPACE_ROOT_ONLY"
    },
    {
      "name": "aider",
      "binary": "aider",
      "version_command": "aider --version",
      "config_dir": "~/Agents/config/aider",
      "session_dir": "~/Agents/sessions/aider",
      "capabilities": ["code-generation", "git-integration"],
      "workspace_policy": "WORKSPACE_ROOT_ONLY"
    },
    {
      "name": "codex",
      "binary": "codex",
      "version_command": "codex --version",
      "config_dir": "~/Agents/config/codex",
      "session_dir": "~/Agents/sessions/codex",
      "capabilities": ["code-generation", "code-review"],
      "workspace_policy": "WORKSPACE_ROOT_ONLY"
    }
  ]
}
```

---

## Step 6: Orchestration Framework Integration

Agents coordinate through `agentic-titan`, the polymorphic multi-agent orchestration framework in ORGAN-IV.

### Integration Points

| Component | Purpose | Agent Interaction |
|---|---|---|
| **Topology Engine** | Multi-agent patterns (pipeline, swarm, hierarchy) | Agent receives topology assignment |
| **LLM Adapter** | Model-agnostic API (Anthropic, OpenAI, Ollama) | Agent uses adapter for LLM calls |
| **Hive Mind** | Shared state (Redis), vector memory (ChromaDB) | Agent reads/writes shared context |
| **Safety Layer** | HITL gates, RBAC, budget tracking | Agent respects safety constraints |

### Session Handoff

When one agent hands off to another (e.g., Claude Code → Goose for browser testing):

1. Export session context to `$AGENTS_ROOT/sessions/<agent>/handoff-<id>.json`
2. Include: scope statement, completed work, open issues, file paths modified
3. Receiving agent reads handoff file before starting
4. Both sessions reference the same `AGENT_RUN_ID` for log correlation

---

## Step 7: Homebrew Integration

All agent tooling is managed through Homebrew. The `Brewfile` (managed by chezmoi) declares agent dependencies.

```ruby
# Brewfile — agent infrastructure
brew "node"           # Node.js runtime
brew "python@3.12"    # Python runtime (supplement to Anaconda)
brew "go"             # Go runtime
brew "git"            # Version control
brew "gh"             # GitHub CLI
brew "jq"             # JSON processing
brew "yq"             # YAML processing
brew "fzf"            # Fuzzy finder
brew "ripgrep"        # Fast search
brew "fd"             # Fast find
brew "bat"            # Syntax-highlighted cat
brew "delta"          # Git diff viewer

# Agent-specific
tap "anthropics/claude"
brew "claude"         # Claude Code CLI
```

### Update Procedure

```bash
brew bundle --file=~/Brewfile    # Install/update all
brew upgrade                     # Upgrade all formulae
brew cleanup                     # Remove old versions
```

---

## Step 8: Run Logging Directory

**`AGENTS_LOG` = `~/Agents/logs/`**

Every agent run produces a log directory identified by `AGENT_RUN_ID`.

```
~/Agents/logs/
├── 2026-03-08/
│   ├── claude-code-a1b2c3d4/
│   │   ├── session.json         # Session metadata
│   │   ├── plan.md              # Plan (if SHAPE phase produced one)
│   │   ├── files-modified.txt   # List of files touched
│   │   ├── stdout.log           # Agent stdout
│   │   └── metrics.json         # Token usage, duration, phase transitions
│   └── goose-e5f6g7h8/
│       ├── session.json
│       └── stdout.log
└── 2026-03-07/
    └── ...
```

### AGENT_RUN_ID Format

```
<agent-name>-<8-char-hex>
```

Generated at session start: `AGENT_RUN_ID="claude-code-$(openssl rand -hex 4)"`

### Log Retention

- Keep 30 days of logs
- Archive older logs to `~/Agents/logs/archive/YYYY-MM/`
- Never delete logs for sessions that produced commits

---

## Step 9: Workspace Write Policy

Agents may write ONLY to approved directories. See `docs/workspace-write-policy.md` for the full policy.

### Summary

| Directory | Permission | Notes |
|---|---|---|
| `$WORKSPACE_ROOT` (`~/Workspace/`) | Read + Write | Must `cd` into repo first |
| `$AGENTS_ROOT` (`~/Agents/`) | Read + Write | Caches, logs, sessions |
| `$TMPDIR` | Read + Write | Ephemeral scratch |
| `~/` (root) | Read only | No writes to home root |
| `~/Documents/`, `~/Desktop/`, `~/Downloads/` | Read only | Human directories |
| `/usr/`, `/etc/`, `/opt/` (except Homebrew) | Forbidden | System directories |

### Enforcement

- `CLAUDE.md` instructions (soft enforcement — agent follows instructions)
- Pre-commit hooks (medium enforcement — rejects commits with forbidden paths)
- Agent wrapper scripts (hard enforcement — intercepts write syscalls)

---

## Step 10: Composable Bootstrap via Chezmoi

The entire agent infrastructure is bootstrapped by chezmoi, the dotfile manager anchored at `~/Workspace/organvm-iv-taxis/domus-semper-palingenesis`.

### Bootstrap Sequence

```bash
# 1. Install chezmoi
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply <repo-url>

# 2. Chezmoi applies:
#    - Shell profile with environment variables (Step 3)
#    - Brewfile for tool installation (Step 7)
#    - Directory structure creation (Steps 1-2)
#    - Agent registry initialization (Step 5)
#    - LaunchAgent for MCP servers
#    - Git configuration

# 3. Post-apply validation
chezmoi verify                  # Check all managed files
source ~/.zshrc                 # Reload environment
mkdir -p "$AGENTS_ROOT"/{cache/{models,embeddings},config,logs,tmp,sessions}
```

### Chezmoi Templates

Chezmoi templates handle machine-specific differences:

```
{{ if eq .chezmoi.os "darwin" }}
export HOMEBREW_PREFIX="/opt/homebrew"
{{ else }}
export HOMEBREW_PREFIX="/home/linuxbrew/.linuxbrew"
{{ end }}
```

### Recovery

If the agent environment is corrupted:

```bash
chezmoi apply --force           # Reapply all managed files
brew bundle --file=~/Brewfile   # Reinstall tools
# Agent sessions and logs are preserved (not managed by chezmoi)
```

---

## Canonical Procedure Summary

| Step | Action | Artifact |
|---|---|---|
| 1 | Define DOMUS_ROOT domains | Directory layout |
| 2 | Create agent subsystem layout | `~/Agents/` structure |
| 3 | Set environment variables | Shell profile exports |
| 4 | Document canonical runtime paths | Runtime version table |
| 5 | Create CLI agent registry | `~/Agents/registry.json` |
| 6 | Integrate with agentic-titan | Topology + handoff protocol |
| 7 | Declare Homebrew dependencies | `Brewfile` |
| 8 | Configure run logging | `~/Agents/logs/` structure |
| 9 | Enforce workspace write policy | Policy doc + enforcement layers |
| 10 | Bootstrap via chezmoi | `chezmoi init --apply` |

---

## References

- `domus-semper-palingenesis` — Chezmoi-managed environment controller
- `agentic-titan/` — Multi-agent orchestration framework
- `docs/workspace-write-policy.md` — Full write policy specification
- `conductor-playbook.md` — Session lifecycle (FRAME/SHAPE/BUILD/PROVE)
