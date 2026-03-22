# Outbound Contribution Engine — Design Spec

**Date:** 2026-03-21
**Status:** APPROVED
**Location:** `orchestration-start-here/contrib_engine/`

---

## 1. What This Is

An automated public-facing engine that scans for high-signal open-source projects, ranks them by symbiotic potential with ORGANVM, initializes cross-organ contribution workspaces, monitors active PRs, and triggers distribution when work ships. This is the automation layer that makes the public-facing contribution process self-initiating rather than session-prompted.

---

## 2. Architecture

Three modules in a single package (`contrib_engine/`), consuming from the application pipeline and producing contribution workspaces in ORGAN-IV:

```
application-pipeline/signals/  ──→  Scanner  ──→  ranked_targets.yaml
                                                        │
                                                        ▼
                                                  Orchestrator  ──→  contrib--{project}/
                                                                          │
                                                                          ▼
                                                                     Monitor  ──→  ORGAN-VII
```

### Module 1: Scanner (`contrib_engine/scanner.py`)

**Inputs:**
- `application-pipeline/signals/contacts.yaml` — inbound leads with org/channel
- `application-pipeline/signals/network.yaml` — network graph nodes
- `application-pipeline/signals/outreach-log.yaml` — prior interactions
- GitHub API — repos that starred `4444J99/*`, open issues on target repos

**Outputs:**
- `orchestration-start-here/contrib_engine/data/ranked_targets.yaml` — scored targets

**Scoring criteria:**
- Inbound signal strength (they reached out = highest)
- Domain overlap with ORGANVM capabilities (multi-agent, governance, testing, CI/CD, versioning)
- Repo health (stars, active issues, contribution guidelines exist, recent commits)
- Relationship capital potential (YC-backed, hiring, team size)
- Issue match quality (open issues where ORGANVM patterns apply)

**Capability map** (what ORGANVM can contribute):
- Promotion state machines / lifecycle governance
- Multi-agent orchestration patterns
- Testing infrastructure (pytest, CI/CD)
- Design versioning / reproducibility
- Dependency validation / graph governance
- MCP server integration
- Documentation governance
- Security patterns

### Module 2: Orchestrator (`contrib_engine/orchestrator.py`)

**Inputs:**
- `ranked_targets.yaml` — from Scanner
- Human approval (CLI: `organvm contrib approve <target>`)

**Actions on approval:**
1. Fork target repo to `4444J99/{repo}`
2. Create `contrib--{project}/` directory in ORGAN-IV superproject
3. Initialize git repo with README, CLAUDE.md, CONTRIBUTION-PROMPT.md, seed.yaml
4. Create GitHub remote at `organvm-iv-taxis/contrib--{project}`
5. Add as submodule in superproject
6. Register in `registry-v2.json`
7. Create journal directory with session-00 entry
8. Generate CONTRIBUTION-PROMPT.md from target repo's CONTRIBUTING.md + ORGANVM capability map
9. Update IRF with new OSS items

**CLI:**
```bash
organvm contrib scan                    # Run scanner, update ranked_targets.yaml
organvm contrib list                    # Show ranked targets
organvm contrib approve <target>        # Initialize workspace for target
organvm contrib status                  # Show all active contributions
```

### Module 3: Monitor (`contrib_engine/monitor.py`)

**Inputs:**
- All `contrib--*/` directories in ORGAN-IV superproject
- GitHub API — PR state, reviews, comments, CI checks

**Actions:**
- Poll active PRs every cycle (designed for cron/LaunchAgent)
- Detect state changes: new comments, review requests, CI failures, merges, closures
- On new review comment: create journal entry, flag for human response
- On CI failure: diagnose and create fix plan
- On merge: update journal, promote seed.yaml LOCAL→CANDIDATE, trigger ORGAN-VII distribution
- On close/reject: journal the outcome, archive the workspace

**Output:**
- `contrib_engine/data/contribution_status.yaml` — current state of all contributions
- Journal entries in each `contrib--*/journal/`
- Notifications (stdout for now, LaunchAgent integration later)

**CLI:**
```bash
organvm contrib monitor                 # Run one monitoring cycle
organvm contrib monitor --watch         # Continuous monitoring (for LaunchAgent)
```

---

## 3. Data Schemas

### ranked_targets.yaml
```yaml
generated: "2026-03-21T22:00:00Z"
targets:
  - name: "adenhq-hive"
    github: "adenhq/hive"
    score: 92
    signal_type: "inbound"
    domain_overlap: ["multi-agent", "governance", "versioning", "testing"]
    stars: 9633
    open_issues: 1374
    contacts: ["Vincent Jiang", "Timothy Zhang"]
    matching_issues: [6613, 6612, 2805]
    status: "active"  # active | approved | completed | declined
    workspace: "contrib--adenhq-hive"
```

### contribution_status.yaml
```yaml
generated: "2026-03-21T22:00:00Z"
contributions:
  - workspace: "contrib--adenhq-hive"
    target: "adenhq/hive"
    pr_number: 6707
    pr_state: "OPEN"
    issue_number: 6613
    assigned: false
    last_ci: "fail"  # check-requirements (expected)
    last_review: null
    last_comment: "2026-03-22T02:57:01Z"
    organs_delivered: ["I", "II", "III", "IV", "V"]
    phase: 1
    next_action: "await_assignment"
    next_action_date: "2026-03-23"
```

---

## 4. File Structure

```
orchestration-start-here/
├── contrib_engine/
│   ├── __init__.py
│   ├── scanner.py          # Module 1: Signal scanning + scoring
│   ├── orchestrator.py     # Module 2: Workspace initialization
│   ├── monitor.py          # Module 3: PR monitoring + distribution
│   ├── capabilities.py     # ORGANVM capability map (what we can contribute)
│   ├── schemas.py          # Pydantic models for YAML data
│   ├── github_client.py    # GitHub API wrapper (gh CLI subprocess)
│   ├── cli.py              # CLI entry points (organvm contrib *)
│   └── data/
│       ├── ranked_targets.yaml
│       └── contribution_status.yaml
├── tests/
│   ├── test_scanner.py
│   ├── test_orchestrator.py
│   ├── test_monitor.py
│   └── test_capabilities.py
```

---

## 5. Integration Points

- **Application pipeline:** Read-only consumer of `signals/` YAML files
- **Superproject:** Orchestrator creates submodules, pushes to remotes
- **Registry:** Orchestrator adds entries via Python (same pattern as Hive registration)
- **IRF:** Orchestrator and Monitor update IRF completions
- **ORGAN-VII:** Monitor triggers distribution on PR merge (future: Kerygma profile creation)
- **LaunchAgent:** Monitor designed for periodic execution via `com.4jp.contrib-monitor.plist`

---

## 6. Constraints

- GitHub API via `gh` CLI (subprocess), not octokit — consistent with workspace policy
- All YAML I/O via PyYAML with safe_load/safe_dump
- No external dependencies beyond stdlib + pydantic + pyyaml
- Scanner runs offline-capable (cached GitHub data) with online enrichment
- Human approval required before any workspace creation (no autonomous forking)
- Monitor never pushes code — only journals and flags
