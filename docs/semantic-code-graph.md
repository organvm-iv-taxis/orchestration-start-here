# Semantic Code Graph

> **Governance**: Feature Backlog F-81
> **Scope**: Cross-repo code navigation and impact analysis
> **Version**: 1.0

---

## Purpose

Build a dependency-aware code graph that enables cross-repo navigation, impact analysis, and dead code detection across the ORGANVM system. The graph connects function-level symbols to module-level imports to repo-level edges to organ-level boundaries.

---

## Graph Model

### Node Hierarchy

```
Organ (I–VII, META)
  └── Repository
        └── Module (file)
              └── Symbol (function, class, constant, type)
```

### Edge Types

| Edge Type | Scope | Source |
|---|---|---|
| `imports` | Module → Module | Static analysis (AST/tree-sitter) |
| `calls` | Symbol → Symbol | Static analysis (call graph) |
| `produces` | Repo → Repo | `seed.yaml` produces/consumes |
| `consumes` | Repo → Repo | `seed.yaml` produces/consumes |
| `subscribes` | Repo → Event | `seed.yaml` subscriptions |
| `organ_boundary` | Organ → Organ | Governance dependency graph |

### Node Properties

```json
{
  "id": "organvm-iv-taxis/agentic-titan/titan/cli.py::main",
  "type": "function",
  "module": "titan/cli.py",
  "repo": "agentic-titan",
  "organ": "IV",
  "visibility": "public",
  "language": "python",
  "line_start": 42,
  "line_end": 87
}
```

### Edge Properties

```json
{
  "source": "organvm-iv-taxis/agentic-titan/titan/cli.py::main",
  "target": "organvm-iv-taxis/agentic-titan/orchestrator/engine.py::TopologyEngine",
  "type": "calls",
  "weight": 1,
  "file": "titan/cli.py",
  "line": 55
}
```

---

## Implementation Options

### Option A: Lightweight Grep-Based (Recommended for Phase 1)

**Approach**: Regex-based extraction of imports and function definitions. Fast, no external dependencies, sufficient for cross-repo queries.

**Pros**: Simple, runs anywhere, no build system required
**Cons**: Misses dynamic imports, no type resolution, limited call graph accuracy

```python
#!/usr/bin/env python3
"""Lightweight code graph builder using regex extraction."""

import re
import json
from pathlib import Path

def extract_python_symbols(file_path: Path) -> dict:
    """Extract function and class definitions from a Python file."""
    symbols = []
    content = file_path.read_text()

    # Functions
    for match in re.finditer(r'^(?:async\s+)?def\s+(\w+)\s*\(', content, re.MULTILINE):
        symbols.append({
            "name": match.group(1),
            "type": "function",
            "line": content[:match.start()].count('\n') + 1,
        })

    # Classes
    for match in re.finditer(r'^class\s+(\w+)\s*[:\(]', content, re.MULTILINE):
        symbols.append({
            "name": match.group(1),
            "type": "class",
            "line": content[:match.start()].count('\n') + 1,
        })

    return symbols

def extract_python_imports(file_path: Path) -> list[str]:
    """Extract import targets from a Python file."""
    imports = []
    content = file_path.read_text()

    # from X import Y
    for match in re.finditer(r'^from\s+([\w.]+)\s+import', content, re.MULTILINE):
        imports.append(match.group(1))

    # import X
    for match in re.finditer(r'^import\s+([\w.]+)', content, re.MULTILINE):
        imports.append(match.group(1))

    return imports
```

### Option B: Tree-Sitter Parsing (Phase 2)

**Approach**: Use tree-sitter for language-aware AST parsing. Supports Python, TypeScript, and other languages with a single framework.

**Pros**: Accurate AST, handles edge cases, multi-language
**Cons**: Requires tree-sitter installation and language grammars

```bash
pip install tree-sitter tree-sitter-python tree-sitter-typescript
```

### Option C: LSP-Based Indexing (Phase 3)

**Approach**: Run language servers (Pyright, tsserver) to build a fully resolved symbol graph with type information and cross-file references.

**Pros**: Full type resolution, accurate call graphs, refactoring support
**Cons**: Heavy, requires build environments for each repo, slow to index

---

## Storage Format

### Graph File (JSON)

```json
{
  "version": "1.0",
  "generated": "2026-03-08T12:00:00Z",
  "organs": {
    "IV": {
      "repos": {
        "agentic-titan": {
          "modules": {
            "titan/cli.py": {
              "symbols": [
                {"name": "main", "type": "function", "line": 42, "visibility": "public"}
              ],
              "imports": ["orchestrator.engine", "agents.base", "argparse"]
            }
          }
        }
      }
    }
  },
  "edges": [
    {
      "source": "IV/agentic-titan/titan/cli.py::main",
      "target": "IV/agentic-titan/orchestrator/engine.py::TopologyEngine",
      "type": "calls"
    }
  ]
}
```

### Storage Location

```
meta-organvm/organvm-corpvs-testamentvm/
├── registry-v2.json          # Repo-level metadata
├── code-graph.json           # Symbol-level graph (new)
└── system-metrics.json       # Computed metrics
```

---

## Query Interface

### CLI Queries

```bash
# Find all consumers of a symbol
python3 scripts/query-graph.py consumers "DataClassification"
# → agentic-titan/agents/classifier.py:34
# → agentic-titan/runtime/sandbox.py:112
# → orchestration-start-here/scripts/validate-deps.py:67

# Find all cross-repo imports
python3 scripts/query-graph.py cross-repo-imports
# → (lists all imports that cross repo boundaries — potential coupling)

# Impact analysis: what breaks if I change this function?
python3 scripts/query-graph.py impact "TopologyEngine.run"
# → titan/cli.py:55 (direct call)
# → tests/test_topology.py:23 (test coverage)
# → docs/architecture.md:89 (documentation reference)

# Dead code detection
python3 scripts/query-graph.py dead-symbols --repo agentic-titan
# → agents/deprecated_agent.py::OldAgent (no callers)
# → utils/legacy.py::format_v1 (no callers)
```

### Dashboard Integration

The code graph can be visualized in the system dashboard (`meta-organvm/system-dashboard/`):
- Interactive node graph with organ-colored clusters
- Click-through from symbol to GitHub file view
- Highlight cross-organ edges (should be rare and via ORGAN-IV)

---

## Use Cases

### 1. Impact Analysis

Before modifying a function, query its callers across all repos. Prevents breaking changes in downstream consumers.

### 2. Dead Code Detection

Symbols with no incoming `calls` or `imports` edges are candidates for removal. Filter by age (last modified date) to prioritize truly abandoned code.

### 3. Cross-Organ Dependency Validation

The graph should confirm that code-level imports respect the organ dependency rules (I → II → III, IV orchestrates all). Any import edge that violates this is a code-level back-edge — even if `seed.yaml` doesn't declare it.

```python
def find_code_back_edges(graph: dict) -> list[dict]:
    """Find imports that violate organ dependency rules."""
    organ_order = {"I": 1, "II": 2, "III": 3}
    violations = []

    for edge in graph["edges"]:
        if edge["type"] != "imports":
            continue
        source_organ = edge["source"].split("/")[0]
        target_organ = edge["target"].split("/")[0]

        if source_organ in organ_order and target_organ in organ_order:
            if organ_order[source_organ] < organ_order[target_organ]:
                continue  # Forward edge, OK
            violations.append(edge)

    return violations
```

### 4. Onboarding Navigation

New contributors (human or AI) can query "show me all entry points in this repo" or "what does this repo depend on?" without reading every file.

### 5. Registry Completeness Validation

Compare `seed.yaml` produces/consumes declarations against actual code-level imports. Undeclared dependencies are governance violations.

---

## Build Pipeline

### Generation

```bash
# Build graph for all organs (from workspace root)
python3 scripts/build-code-graph.py \
  --workspace ~/Workspace \
  --organs I II III IV \
  --output meta-organvm/organvm-corpvs-testamentvm/code-graph.json
```

### CI Integration

```yaml
# Run on schedule (weekly) or on-demand
name: Code Graph Update
on:
  schedule:
    - cron: '0 6 * * 1'  # Monday 6am UTC
  workflow_dispatch:

jobs:
  build-graph:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - run: python3 scripts/build-code-graph.py --output code-graph.json
      - run: python3 scripts/query-graph.py back-edges --fail-on-violation
```

---

## References

- `scripts/validate-deps.py` — Existing repo-level dependency validation (graph extends this to symbol level)
- `registry-v2.json` — Repo metadata that the graph enriches
- `governance-rules.json` — Article II (dependency rules the graph enforces)
- [GitHub Custom Properties](github-custom-properties.md) — Complementary metadata layer
- tree-sitter: https://tree-sitter.github.io/tree-sitter/
