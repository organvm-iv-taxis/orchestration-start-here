# tmux Swarm Layout for Multi-Agent Operations

> **Governance**: Feature Backlog F-58
> **Scope**: Local development environment for AI conductor sessions
> **Version**: 1.0

---

## Purpose

A standardized 4-pane tmux layout that gives the AI conductor simultaneous visibility into agent interaction, test feedback, version control state, and structured logs. Designed for sessions where you're directing AI agents across multiple repos.

---

## Pane Layout

```
┌──────────────────────────┬──────────────────────────┐
│                          │                          │
│   1. Agent CLI           │   2. Tests + Linters     │
│   (main interaction)     │   (watch mode)           │
│                          │                          │
│   60% width              │   40% width              │
│                          │                          │
├──────────────────────────┼──────────────────────────┤
│                          │                          │
│   3. Git Status/Review   │   4. Log Viewer          │
│   (version control)      │   (structured logs)      │
│                          │                          │
│   60% width              │   40% width              │
│                          │                          │
└──────────────────────────┴──────────────────────────┘
```

### Pane Ratios

- Top row: 65% of terminal height
- Bottom row: 35% of terminal height
- Left column: 60% of terminal width
- Right column: 40% of terminal width

---

## Pane Descriptions

### Pane 1 — Agent CLI (Top Left)

The primary interaction pane. This is where you run Claude Code, agentic-titan CLI, or any agent interface.

**Typical commands**:
```bash
claude                          # Claude Code CLI
titan run spec.yaml -p "task"   # agentic-titan
npm run dev                     # agent--claude-smith dev mode
```

### Pane 2 — Tests + Linters (Top Right)

Continuous feedback on code quality. Runs in watch mode so changes are validated immediately.

**Typical commands**:
```bash
# Python (agentic-titan)
ptw -- -x -q                                    # pytest-watch, stop on first failure
ruff check --watch .                             # ruff in watch mode

# TypeScript (agent--claude-smith)
npm run test:watch                               # vitest watch mode
npx tsc --noEmit --watch                         # typecheck watch mode

# Combined (using entr or watchexec)
find . -name '*.py' | entr -c pytest -x -q       # re-run on file change
watchexec -e ts -- npx tsc --noEmit              # TypeScript watch
```

### Pane 3 — Git Status/Review (Bottom Left)

Version control awareness. See what's changed, what's staged, and recent history.

**Typical commands**:
```bash
# Quick status loop
watch -n 5 'git status -sb && echo "---" && git diff --stat'

# Interactive (if installed)
lazygit                                          # TUI for git

# Manual checks
git status
git diff
git log --oneline -10
git diff --cached                                # staged changes
```

### Pane 4 — Log Viewer (Bottom Right)

Structured log output from agents, CI, or system processes.

**Typical commands**:
```bash
# Agent logs (JSON structured)
tail -f agent.log | jq '.'

# MCP server logs
tail -f /Users/4jp/System/Logs/mcp-servers.log

# CI log streaming (if using act for local CI)
act --verbose 2>&1 | tail -f

# Generic log with filtering
tail -f *.log | jq 'select(.level == "error")'
```

---

## tmux Configuration Snippet

Add to `~/.tmux.conf` or source as a separate file:

```tmux
# ORGANVM Swarm Layout
# Bind to prefix + S (for Swarm)
bind S source-file ~/.tmux/organvm-swarm.conf

# Pane border styling
set -g pane-border-style 'fg=colour238'
set -g pane-active-border-style 'fg=colour39'

# Status bar shows session context
set -g status-right '#[fg=colour39]#{pane_current_path} #[fg=colour245]| %H:%M'
```

---

## Session Startup Script

Save as `~/.local/bin/organvm-swarm` and make executable:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Usage: organvm-swarm [project-dir]
# Default: current directory

PROJECT_DIR="${1:-.}"
SESSION_NAME="organvm-$(basename "$PROJECT_DIR")"

# Kill existing session if present
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Create session with first pane (Agent CLI)
tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR" -x "$(tput cols)" -y "$(tput lines)"

# Split horizontally (top/bottom)
tmux split-window -v -t "$SESSION_NAME" -c "$PROJECT_DIR" -p 35

# Split top pane vertically (left/right)
tmux select-pane -t "$SESSION_NAME:0.0"
tmux split-window -h -t "$SESSION_NAME" -c "$PROJECT_DIR" -p 40

# Split bottom pane vertically (left/right)
tmux select-pane -t "$SESSION_NAME:0.2"
tmux split-window -h -t "$SESSION_NAME" -c "$PROJECT_DIR" -p 40

# Pane 0 (top-left): Agent CLI — left empty for manual use
# Pane 1 (top-right): Tests + Linters
tmux send-keys -t "$SESSION_NAME:0.1" "echo 'Tests pane — run: ptw or npm run test:watch'" Enter

# Pane 2 (bottom-left): Git status
tmux send-keys -t "$SESSION_NAME:0.2" "git status -sb && git log --oneline -5" Enter

# Pane 3 (bottom-right): Log viewer
tmux send-keys -t "$SESSION_NAME:0.3" "echo 'Log pane — run: tail -f <logfile> | jq'" Enter

# Focus on Agent CLI pane
tmux select-pane -t "$SESSION_NAME:0.0"

# Attach
tmux attach-session -t "$SESSION_NAME"
```

Make executable:
```bash
chmod +x ~/.local/bin/organvm-swarm
```

---

## Usage

```bash
# Start swarm for current project
organvm-swarm .

# Start swarm for a specific repo
organvm-swarm ~/Workspace/organvm-iv-taxis/agentic-titan

# Start swarm for orchestration hub
organvm-swarm ~/Workspace/organvm-iv-taxis/orchestration-start-here
```

---

## Keybindings Reference

| Action | Keys | Notes |
|---|---|---|
| Switch pane | `Ctrl-b` + arrow key | Navigate between panes |
| Zoom pane | `Ctrl-b` + `z` | Toggle fullscreen for current pane |
| Resize pane | `Ctrl-b` + `Ctrl-arrow` | Adjust pane size |
| Kill pane | `Ctrl-b` + `x` | Close current pane |
| Scroll mode | `Ctrl-b` + `[` | Enter copy mode to scroll back |
| Exit scroll | `q` | Return to normal mode |

---

## References

- [Domus Agent Infrastructure](domus-agent-infrastructure.md) — F-56, broader agent infrastructure context
- [Conductor Playbook](conductor-playbook.md) — Session lifecycle that runs in Pane 1
- [Breadcrumb Protocol](breadcrumb-protocol.md) — Session logs that appear in Pane 4
