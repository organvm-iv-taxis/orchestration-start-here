# F-79: Source-of-Truth Drift Detection

> **Governance**: `governance-rules.json` Article I (Registry as Source of Truth)
> **Scope**: Automated detection of divergence between governance files and reality
> **Version**: 1.0
> **Status**: Design Document
> **Backlog**: F-79
> **Reference**: `scripts/organ-audit.py`, `registry.json`, `governance-rules.json`

---

## Why This Exists

The ORGANVM system has multiple sources of truth that must agree:

- `CLAUDE.md` describes repo structure, commands, and conventions
- `seed.yaml` declares organ membership, tier, edges, and promotion status
- `registry.json` aggregates seed data into a global view
- GitHub itself reflects the actual state of repos (archived, renamed, missing)

When these sources diverge — and they will, because the system changes faster than documentation — governance decisions are made on stale data. Drift detection turns silent divergence into visible, actionable mismatches.

---

## Drift Categories

### Category 1: CLAUDE.md vs Actual Repo Structure

**What drifts**: Directory listings, file paths, build commands, dependency descriptions.

**Detection method**: Parse CLAUDE.md for structural claims and verify them against the filesystem.

| Check | Technique | Example Drift |
|---|---|---|
| Listed directories exist | Parse directory tree from CLAUDE.md, `os.path.exists()` each | CLAUDE.md lists `src/agents/` but directory was renamed to `src/agent/` |
| Listed commands work | Extract `bash` code blocks, dry-run or syntax-check | `npm run typecheck` listed but `package.json` has no `typecheck` script |
| Listed files exist | Parse file references, verify presence | "See `docs/architecture.md`" but file was deleted |
| Stack description matches | Check for `pyproject.toml` vs `package.json` vs `Cargo.toml` | CLAUDE.md says "Python" but repo is now TypeScript |

**Severity**: Medium. Stale CLAUDE.md misleads AI agents, causing wasted cycles.

### Category 2: seed.yaml vs registry.json

**What drifts**: Promotion status, tier, organ membership, produces/consumes edges.

**Detection method**: Parse all `seed.yaml` files and compare field-by-field against registry entries.

| Check | Technique | Example Drift |
|---|---|---|
| Promotion status matches | Compare `seed.yaml.promotion_status` vs `registry[name].promotion_status` | seed says CANDIDATE, registry says LOCAL |
| Tier matches | Compare `seed.yaml.tier` vs `registry[name].tier` | seed says flagship, registry says standard |
| Organ matches | Compare `seed.yaml.organ` vs `registry[name].organ` | seed says IV, registry says III |
| Edges match | Compare produces/consumes lists | seed declares edge to `agentic-titan`, registry missing it |
| All seeds in registry | Check registry contains entry for every seed.yaml found | New repo has seed.yaml but was never added to registry |
| All registry in seeds | Check every registry entry has a corresponding seed.yaml | Registry lists repo but seed.yaml was deleted |

**Severity**: High. Mismatched promotion status causes incorrect audit results and governance decisions.

### Category 3: registry.json vs GitHub API

**What drifts**: Repo existence, archived status, visibility, description, topics.

**Detection method**: Query GitHub API for each registry entry and compare.

| Check | Technique | Example Drift |
|---|---|---|
| Repo exists | `gh repo view <org>/<repo>` | Registry lists repo but it was deleted on GitHub |
| Archived status | Compare `registry[name].archived` vs GitHub `isArchived` | Registry says active, GitHub says archived |
| Visibility matches | Compare expected vs actual public/private status | Registry assumes public, repo is private |
| Description matches | Compare `registry[name].description` vs GitHub description | Description updated on GitHub but not in registry |
| Missing from registry | List all repos in org, find ones not in registry | New repo created on GitHub but never registered |

**Severity**: High. Ghost entries in registry inflate metrics; missing entries are ungoverned.

### Category 4: Cross-File Consistency

**What drifts**: References between governance files, outdated counts, stale links.

| Check | Technique | Example Drift |
|---|---|---|
| Repo count in CLAUDE.md | Parse "~N repos" claims, compare to registry count | CLAUDE.md says "~97 repos", registry has 105 |
| Organ repo counts | Parse per-organ counts, compare to registry | "ORGAN-I: 20 repos" but registry shows 18 |
| Governance article references | Verify article numbers referenced in docs exist in `governance-rules.json` | Doc references "Article VII" but only Articles I-VI exist |
| Link validity | Check internal doc links resolve | `[see patterns](patterns-catalog.md)` but file is `pattern-catalog.md` |

**Severity**: Low-Medium. Cosmetic but erodes trust in documentation accuracy.

---

## Detection Implementation

### Script: `scripts/detect-drift.py`

```python
#!/usr/bin/env python3
"""Detect drift between ORGANVM source-of-truth files."""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DriftItem:
    category: str
    severity: Severity
    source_a: str
    source_b: str
    field: str
    value_a: str
    value_b: str
    suggestion: str

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity.value,
            "source_a": self.source_a,
            "source_b": self.source_b,
            "field": self.field,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "suggestion": self.suggestion,
        }


@dataclass
class DriftReport:
    timestamp: str
    items: list[DriftItem] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def add(self, item: DriftItem) -> None:
        self.items.append(item)

    def to_json(self) -> str:
        self.summary = {
            "total": len(self.items),
            "by_severity": {
                s.value: len([i for i in self.items if i.severity == s])
                for s in Severity
            },
            "by_category": {},
        }
        categories = set(i.category for i in self.items)
        for cat in categories:
            self.summary["by_category"][cat] = len(
                [i for i in self.items if i.category == cat]
            )
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "summary": self.summary,
                "items": [i.to_dict() for i in self.items],
            },
            indent=2,
        )


def check_seed_vs_registry(workspace: Path, report: DriftReport) -> None:
    """Compare all seed.yaml files against registry.json entries."""
    registry_path = workspace / "orchestration-start-here" / "registry.json"
    if not registry_path.exists():
        report.add(DriftItem(
            category="seed-vs-registry",
            severity=Severity.CRITICAL,
            source_a="filesystem",
            source_b="registry.json",
            field="file_exists",
            value_a="missing",
            value_b="expected",
            suggestion="Registry file not found — system is ungoverned",
        ))
        return

    with open(registry_path) as f:
        registry = json.load(f)

    # Build registry lookup by repo name
    registry_by_name = {}
    for entry in registry.get("repos", registry) if isinstance(registry, dict) else registry:
        name = entry.get("name", entry.get("repo", ""))
        if name:
            registry_by_name[name] = entry

    # Find all seed.yaml files
    for seed_path in workspace.rglob("seed.yaml"):
        # Skip node_modules, .venv, etc.
        if any(part.startswith(".") or part == "node_modules" for part in seed_path.parts):
            continue

        try:
            import yaml
            with open(seed_path) as f:
                seed = yaml.safe_load(f)
        except Exception:
            continue

        if not seed or "name" not in seed:
            continue

        name = seed["name"]
        if name not in registry_by_name:
            report.add(DriftItem(
                category="seed-vs-registry",
                severity=Severity.ERROR,
                source_a=str(seed_path),
                source_b="registry.json",
                field="existence",
                value_a=f"seed.yaml exists for '{name}'",
                value_b="no registry entry",
                suggestion=f"Add '{name}' to registry.json",
            ))
            continue

        reg = registry_by_name[name]
        # Compare fields
        for field_name in ["promotion_status", "tier", "organ"]:
            seed_val = str(seed.get(field_name, ""))
            reg_val = str(reg.get(field_name, ""))
            if seed_val and reg_val and seed_val != reg_val:
                report.add(DriftItem(
                    category="seed-vs-registry",
                    severity=Severity.ERROR,
                    source_a=str(seed_path),
                    source_b="registry.json",
                    field=field_name,
                    value_a=seed_val,
                    value_b=reg_val,
                    suggestion=f"Update registry '{name}.{field_name}' from '{reg_val}' to '{seed_val}' (seed is authoritative)",
                ))


def check_registry_vs_github(registry_path: Path, report: DriftReport) -> None:
    """Compare registry entries against GitHub API."""
    # Implementation uses `gh` CLI
    # Skipped in offline mode — requires GitHub API access
    pass


def main():
    workspace = Path(os.environ.get("WORKSPACE_ROOT", Path.home() / "Workspace"))
    organ_iv = workspace / "organvm-iv-taxis"

    from datetime import datetime, timezone
    report = DriftReport(timestamp=datetime.now(timezone.utc).isoformat())

    check_seed_vs_registry(organ_iv, report)
    # check_registry_vs_github(...)  # Enable when running with network access

    print(report.to_json())

    # Exit with error if any ERROR or CRITICAL items found
    error_count = len([i for i in report.items if i.severity in (Severity.ERROR, Severity.CRITICAL)])
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
```

---

## Integration with organ-audit.py

The existing `organ-audit.py` already performs some drift detection (checking seed.yaml presence, CI status). Rather than replacing it, drift detection extends it:

### Current organ-audit.py Coverage

| Check | Status |
|---|---|
| seed.yaml exists per repo | Covered |
| CI workflow exists | Covered |
| README exists | Covered |
| Promotion status distribution | Covered |

### Proposed Extensions

| Check | Implementation |
|---|---|
| seed.yaml vs registry field comparison | New function: `audit_seed_registry_drift()` |
| CLAUDE.md structural claims verification | New function: `audit_claude_md_accuracy()` |
| Registry vs GitHub reconciliation | New function: `audit_registry_github_sync()` |
| Cross-file reference validity | New function: `audit_internal_links()` |

### Integration Approach

```python
# In organ-audit.py, add drift detection as a new audit section:

def run_drift_detection(workspace: Path) -> dict:
    """Run drift detection and return results for audit report."""
    from detect_drift import DriftReport, check_seed_vs_registry
    report = DriftReport(timestamp=datetime.now(timezone.utc).isoformat())
    check_seed_vs_registry(workspace, report)
    return {
        "drift_items": len(report.items),
        "by_severity": report.summary.get("by_severity", {}),
        "details": [i.to_dict() for i in report.items],
    }
```

---

## Scheduling

### Option A: GitHub Action (Weekly)

```yaml
name: Drift Detection
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9:00 UTC
  workflow_dispatch:

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run drift detection
        run: python scripts/detect-drift.py > drift-report.json

      - name: Check for errors
        run: |
          errors=$(jq '.summary.by_severity.error // 0' drift-report.json)
          critical=$(jq '.summary.by_severity.critical // 0' drift-report.json)
          if [ "$errors" -gt 0 ] || [ "$critical" -gt 0 ]; then
            echo "::error::Drift detected: $errors errors, $critical critical"
            cat drift-report.json | jq '.items[] | select(.severity == "error" or .severity == "critical")'
            exit 1
          fi

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: drift-report
          path: drift-report.json
```

### Option B: Local Script (On-Demand)

```bash
# Run from workspace root
cd ~/Workspace/organvm-iv-taxis/orchestration-start-here
python3 scripts/detect-drift.py | jq .

# Or as part of the regular audit
python3 scripts/organ-audit.py --include-drift
```

---

## Drift Report Format

### JSON Output

```json
{
  "timestamp": "2026-03-08T12:00:00Z",
  "summary": {
    "total": 5,
    "by_severity": {
      "info": 1,
      "warning": 2,
      "error": 2,
      "critical": 0
    },
    "by_category": {
      "seed-vs-registry": 3,
      "claude-md-structure": 1,
      "cross-file-consistency": 1
    }
  },
  "items": [
    {
      "category": "seed-vs-registry",
      "severity": "error",
      "source_a": "agentic-titan/seed.yaml",
      "source_b": "registry.json",
      "field": "promotion_status",
      "value_a": "PUBLIC_PROCESS",
      "value_b": "CANDIDATE",
      "suggestion": "Update registry 'agentic-titan.promotion_status' from 'CANDIDATE' to 'PUBLIC_PROCESS' (seed is authoritative)"
    }
  ]
}
```

### Human-Readable Summary

```
DRIFT DETECTION REPORT — 2026-03-08
====================================

5 items found: 0 critical, 2 error, 2 warning, 1 info

ERRORS (must fix):
  [seed-vs-registry] agentic-titan.promotion_status: seed=PUBLIC_PROCESS, registry=CANDIDATE
    → Update registry to match seed

  [seed-vs-registry] new-repo: exists in seed.yaml but not in registry
    → Add to registry.json

WARNINGS (should fix):
  [claude-md-structure] orchestration-start-here: CLAUDE.md lists 'src/dreamcatcher/' but directory is empty
    → Remove from CLAUDE.md or populate directory

  [cross-file-consistency] CLAUDE.md says "~97 repos" but registry has 105
    → Update count in CLAUDE.md

INFO:
  [cross-file-consistency] governance-rules.json last modified 45 days ago
    → Review for staleness
```

---

## Reconciliation Workflow

When drift is detected, the reconciliation follows a priority order:

1. **seed.yaml is authoritative** for per-repo metadata → update registry to match
2. **GitHub API is authoritative** for repo existence/status → update registry and seeds to match
3. **Filesystem is authoritative** for directory structure → update CLAUDE.md to match
4. **governance-rules.json is authoritative** for governance rules → update docs to match

### Auto-Fix (Safe Operations)

Some drift can be auto-fixed:

```bash
# Sync registry from seeds (safe — seeds are authoritative)
python3 scripts/organvm-registry-sync.py --from-seeds

# Update CLAUDE.md repo counts (safe — cosmetic)
python3 scripts/update-claude-md-counts.py
```

### Manual Review Required

Some drift requires human judgment:

- Repo archived on GitHub but not in registry → was this intentional?
- Promotion status mismatch → which source is correct?
- Missing seed.yaml → should the repo have one, or is it excluded by design?

---

## References

- `scripts/organ-audit.py` — Existing audit script (extension target)
- `registry.json` — System registry (drift target)
- `governance-rules.json` — Governance configuration (drift target)
- `docs/patterns-catalog.md` — Pattern 5: Registry as Single Source of Truth
- `docs/conductor-playbook-reference.md` — QR1: Governance Configuration
