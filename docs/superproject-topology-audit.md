# SOP: Superproject Topology Audit

> **Governance**: `governance-rules.json` Article I (Registry as Source of Truth)
> **Scope**: Structural audit of any git superproject — declared boundary vs. actual inventory
> **Version**: 1.0
> **Status**: Proven (3 targets, 5 agents)
> **Tool**: `meta-organvm/tools/superproject_topology_audit.py` (843 lines, above/below modes)
> **Tests**: `meta-organvm/tools/test_superproject_topology_audit.py` (237 lines)

---

## Purpose

Given any git superproject (a root repo with N declared submodules and M additional repos
potentially present on disk), produce a topology map that answers:

1. What does this superproject **declare**?
2. What does it **actually** contain?
3. What **gap** exists between 1 and 2?
4. What **external systems** does it reference?
5. What is the **disposition** of each component?

The SOP is agent-portable: it has been executed by Claude, Gemini, and Codex with
structurally consistent results despite different execution styles.

## Preconditions

- Target directory is a git repository
- Submodules may or may not be initialized
- Additional cloned repos may exist alongside declared submodules
- Non-git directories (infrastructure, docs, data) may exist at root

## Procedure

### Step 1 — Boundary Declaration

**Command:**
```bash
cat .gitmodules
git submodule status
```

**Extracts:**
- Declared submodule count
- Each submodule's path, remote URL, commit hash
- Dirty state indicators (`+` prefix = uncommitted changes)

**Output schema:**
```
DECLARED_SET: [{path, url, commit, dirty}]
DECLARED_COUNT: int
```

### Step 2 — Actual Inventory

**Command:**
```bash
for d in */; do
  d="${d%/}"
  if [ -d "$d/.git" ]; then
    remote=$(git -C "$d" remote get-url origin 2>/dev/null || echo "NO_REMOTE")
    echo "REPO|$d|$remote"
  else
    echo "DIR|$d"
  fi
done | sort
```

**Extracts:**
- Every root-level directory classified as REPO (has `.git`) or DIR (no `.git`)
- Git remote URL for each repo

**Output schema:**
```
ACTUAL_REPOS: [{path, remote_url}]
ACTUAL_DIRS: [path]
ACTUAL_REPO_COUNT: int
```

**Important:** Include hidden directories (`.claude`, `.gemini`, `.github`, `.meta`,
`.pytest_cache`, etc.) in the inventory. The SOP requires exhaustive classification —
omitting hidden directories is a procedural violation.

### Step 3 — Boundary Gap Analysis

**Computation:** `UNDECLARED_SET = ACTUAL_REPOS - DECLARED_SET` (set difference by path)

**Metrics:**
```
GAP_COUNT: len(UNDECLARED_SET)
GAP_RATIO: GAP_COUNT / ACTUAL_REPO_COUNT
```

**Diagnostic thresholds (empirically derived from 3 runs):**

| Gap Ratio | Interpretation |
|-----------|----------------|
| 0-15% | Tight governance — nearly all repos are declared |
| 15-40% | Moderate drift — some repos added without registration |
| 40-70% | Structural drift — .gitmodules is aspirational, not actual |
| 70%+ | Superproject is a container, not a governance instrument |

**Proof:**
- META-ORGANVM: 2/14 = 14% → tight governance (pre-remediation)
- ORGAN-IV: 19/28 = 68% → structural drift
- orchestration-start-here: 0/0 = 0% → non-superproject (hub)

### Step 4 — External Organization Mapping

**Command:**
```bash
# From git remotes (primary signal)
for d in */; do
  d="${d%/}"
  [ -d "$d/.git" ] || continue
  git -C "$d" remote get-url origin 2>/dev/null
done | sed 's|.*github\.com[:/]\([^/]*\)/.*|\1|' | sort -u

# From package manifests (secondary signal)
find . -maxdepth 2 -name 'package.json' -exec grep -l '"repository"' {} \;
find . -maxdepth 2 -name 'pyproject.toml' -exec grep -l 'repository' {} \;
```

**Extracts:**
- Every distinct GitHub organization referenced by any repo remote
- Package manifest references to external organizations

**Classification:**
- **Primary org:** owns the superproject
- **Sibling orgs:** other organs in the ORGANVM system
- **Personal orgs:** individual forks/staging (e.g., 4444J99)
- **External orgs:** third-party upstream (e.g., makenotion, dbt-labs)

**Output schema:**
```
ORGS: [{name, repo_count, is_primary: bool}]
CROSS_ORG_REPOS: [{path, org, relationship}]
```

### Step 5 — Dependency Edge Extraction

**Command:**
```bash
find . -maxdepth 2 -name 'seed.yaml' -exec echo "--- {} ---" \; -exec cat {} \;
```

**Extracts from each seed.yaml:**
- `consumes` entries → inbound edges
- `produces` entries → outbound edges
- `organ` membership → confirms affiliation
- `tier` → flagship / standard / infrastructure
- `promotion_status` → current lifecycle state

**Output schema:**
```
EDGES: [{source_repo, target_repo, edge_type, data_type}]
CROSS_ORGAN_EDGES: [subset where source.organ != target.organ]
```

**Fallback (for non-ORGANVM repos):**
- `package.json` dependencies
- `pyproject.toml` dependencies
- Import graph analysis

### Step 6 — Infrastructure Layer Inventory

**Check each canonical location:**

| Location | Signal | Interpretation |
|----------|--------|----------------|
| `.atoms/` | System state snapshots | Serialization layer exists |
| `research/` | Prose artifacts | Knowledge corpus accumulated |
| `tools/` | Executable scripts | Operational tooling accumulated |
| `docs/` | Documentation | Documentation accumulated |
| `intake/` | Unsorted material | Ingest pipeline active |
| Root `*.md` | Superproject-level docs | Self-description exists |

**For each present location, report:**
- Item count
- Total size
- Key files (by name/size)
- Last modification date

**For each absent location:** report as missing data — it means the superproject
doesn't accumulate that type of content.

### Step 7 — Stratum Classification

**Classify every root-level directory into exactly one stratum:**

```
Stratum I  (Declared):       path ∈ DECLARED_SET
Stratum II (Undeclared):     path ∈ ACTUAL_REPOS - DECLARED_SET
Stratum III (Infrastructure): path ∈ ACTUAL_DIRS (no .git)
```

**This classification is:**
- **Exhaustive:** every directory is classified (including hidden directories)
- **Mutually exclusive:** no directory appears in two strata
- **Mechanically derivable:** no judgment required, pure set operations

**Within Stratum II, sub-classify by organizational affiliation:**
- Same-org undeclared → governance gap (missing submodule or removed)
- Sibling-org clone → cross-organ presence (check directionality rules)
- External clone → contribution workspace or fork

**Within Stratum III, sub-classify by content type:**
- Build artifacts (`.atoms/`, `.pytest_cache/`, `.venv/`)
- Knowledge assets (`research/`, `docs/`)
- Operational tools (`tools/`, `scripts/`)
- Ingest/staging (`intake/`, `post-flood/`)
- Agent configuration (`.claude/`, `.gemini/`, `.codex/`)

---

## Step 8 — Lateral Presence Detection

*Added by Codex after reading Claude's blind-spot identification. Not in original SOP.*

For each Stratum II and Stratum III entry, answer: **"Why are you here?"**

```python
def classify_lateral_presence(path, org_primary, org_siblings):
    """Determine why a non-declared component exists at root."""
    if has_git and org == org_primary:
        return "GOVERNANCE_GAP"       # Should be in .gitmodules
    if has_git and org in org_siblings:
        return "CROSS_ORGAN_CLONE"    # Check dependency direction
    if has_git and org not in known_orgs:
        return "EXTERNAL_WORKSPACE"   # Contribution or exploration
    if not has_git and is_config_dir:
        return "AGENT_CONFIG"         # AI agent working directories
    if not has_git and is_cache_dir:
        return "BUILD_CACHE"          # Ephemeral, safe to ignore
    return "UNKNOWN"                  # Requires human judgment
```

This step catches what Steps 1-7 miss: directories that are present but whose
presence is unexplained by the governance model.

---

## Output Format — Single Hierarchy Map

```
{TARGET_NAME} ({ACTUAL_REPO_COUNT} sub-repos, {GAP_RATIO}% undeclared)
├── Stratum I — Declared
│   └── {repo} → {remote_url}
│       └── edges: consumes [...], produces [...]
├── Stratum II — Undeclared
│   ├── Same-Org ({count})
│   │   └── {repo} → {remote_url}
│   ├── Sibling-Org ({count})
│   │   └── {repo} → {remote_url}
│   └── External ({count})
│       └── {repo} → {remote_url}
├── Stratum III — Infrastructure
│   └── {dir} ({item_count} items, {size})
│       └── lateral: {LATERAL_CLASSIFICATION}
├── External Dependency Graph
│   └── {org} ← consumed by [{repos}]
└── Diagnostics
    ├── Gap Ratio: {GAP_RATIO}%
    ├── Cross-Org Edges: {count}
    ├── Dirty Submodules: [{list}]
    └── Dormant Components: [{list}]
```

---

## Tool Implementation

The SOP is mechanized as `meta-organvm/tools/superproject_topology_audit.py` (843 lines).

**Usage:**
```bash
# Fleet-level audit (Steps 1-8, all at once)
python3 tools/superproject_topology_audit.py above

# JSON output for downstream processing
python3 tools/superproject_topology_audit.py above --format json

# Component-level drill-down
python3 tools/superproject_topology_audit.py below cvrsvs-honorvm

# Specify a different root
python3 tools/superproject_topology_audit.py above --root /path/to/superproject
```

The tool emits rows, not advice. It implements Steps 1-8 mechanically,
including lateral presence detection (`classify_lateral_presence()`).

---

## Proof of Repeatability

| Run | Target | Agent | Repos | Orgs | Gap | Remediation |
|-----|--------|-------|-------|------|-----|-------------|
| 1 | organvm-iv-taxis | Claude | 28 | 4 | 68% | None (structural drift noted) |
| 2 | meta-organvm | Claude | 14 | 1 | 14% | None (tight governance) |
| 3 | meta-organvm | Gemini | 14 | 1 | 14% | Added 2 repos to .gitmodules → 0% |
| 4 | meta-organvm | Codex | 14 | 1 | 14% | Compared with Run 3, matched |
| 5 | orchestration-start-here | Claude | 0 | 1 | 0% | Hub classification (non-superproject) |
| 6 | orchestration-start-here | Gemini | 0 | 1 | 0% | Matched Run 5 |

Every run produced structurally consistent output despite different agent execution
styles. The SOP is agent-portable: procedure stable, vocabulary fluid.

## Arrhythmic Trace

The SOP's development and execution across 5 agents (Claude, Gemini, Codex, plus
two agents in remediation roles) was itself an arrhythmic trace — each action falling
when the work demanded it, not on a schedule:

| Phase | Agent | Output | Weight |
|-------|-------|--------|--------|
| Concept | Claude | SOP v1 (262 lines) | Design |
| Validation | Claude | SOP v2 + lateral audit step | Extension |
| Execution | Gemini | Audit output (meta-organvm) | Data |
| Execution | Codex | Audit output + comparison | Data + judgment |
| Mechanization | Codex | `superproject_topology_audit.py` (843 lines) + tests (237 lines) | Tool |
| Extension | Codex | Lateral presence detection (+75 lines) | Lateral talisman |
| Crash | Gemini | OOM at 4GB heap (x2) | Physical limit data |
| Remediation | Gemini | Added 2 repos to .gitmodules, 0% gap | Action |

**Key findings from the arrhythmic trace:**
- The SOP said "produce tables, not tools." Codex produced the tool. The tool is the
  talisman the SOP was describing — the concrete artifact that makes the procedure
  repeatable without re-reading the document.
- The lateral audit (Step 8) was adopted cross-agent without coordination. Claude
  identified the blind spot. Codex encoded the check. The SOP was legible enough
  for a different agent to extend it.
- Gemini CLI consumed 4GB heap on a 16GB machine (25% system RAM) during audit
  operations. This is physical limit data about which agents can run the SOP.

---

## Generalization Notes

### What's ORGANVM-specific (remove for external use)
- `seed.yaml` schema (Step 5) — replace with any dependency declaration format
- Organ affiliation — replace with any organizational unit concept
- Promotion state machine — replace with any lifecycle model

### What's universally applicable
- Steps 1-4 (boundary, inventory, gap, orgs) — pure git primitives
- Step 6 (infrastructure layers) — directory classification
- Step 7 (stratum classification) — exhaustive set-based
- Step 8 (lateral presence) — blind-spot detection
- Gap ratio diagnostic — universally applicable to any multi-repo structure
- Single hierarchy output format — works for any multi-repo structure

### Adaptation for non-superproject targets
If the target is a workspace directory (no `.gitmodules`), skip Step 1 and treat
all repos as Stratum II. The gap ratio becomes `100%` (or equivalently `∞` → "no
governance instrument exists"). Steps 2-8 still produce useful output. The tool
handles this case automatically — orchestration-start-here demonstrated it.
