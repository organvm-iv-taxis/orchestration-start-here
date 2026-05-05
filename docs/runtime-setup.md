# Runtime Setup

Local Python venv bypasses the system pydantic-core ↔ pydantic mismatch
that was tracked through the 2026-05-04 / 2026-05-05 sessions.

## One-time setup

```bash
cd ~/Workspace/organvm/orchestration-start-here
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install "pydantic>=2.10,<3.0" "click>=8.0" "pyyaml>=6.0" "requests>=2.28"
```

## Running CLIs

The repo ships multiple module entry points; run them via `.venv/bin/python -m`
from the repo root so source changes take effect without reinstall:

```bash
.venv/bin/python -m action_ledger --help
.venv/bin/python -m precedent_engine search --verb merged --target "#130"
.venv/bin/python -m contrib_engine list
.venv/bin/python -m intake_router table
```

## Known issue

`pip install -e .` fails because `pyproject.toml` declares
`name = "orchestration-start-here"` but no directory matches that distribution
name (the repo ships several sibling packages: `action_ledger/`,
`contrib_engine/`, `intake_router/`, `precedent_engine/`, `ecosystem/`).
Resolution requires either:

- Adding `[tool.hatch.build.targets.wheel] packages = [...]` listing all
  sibling packages, or
- Renaming the project to match one of the package directories.

Out of scope for the runtime fix; tracked separately if hatchling-clean
editable installs become required.
