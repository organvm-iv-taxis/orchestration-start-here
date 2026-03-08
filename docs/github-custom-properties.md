# GitHub Custom Properties as Metadata

> **Governance**: Feature Backlog F-64
> **Scope**: All GitHub organizations in the ORGANVM system
> **Version**: 1.0

---

## Purpose

Evaluate GitHub Custom Properties API as a supplementary metadata layer for ORGANVM repos. Custom Properties allow org-level metadata to be attached to repos and queried through the GitHub UI and API — potentially surfacing organ, tier, and promotion status without requiring file access.

---

## Proposed Properties

| Property | Type | Values | Maps To |
|---|---|---|---|
| `organ` | single_select | `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `META` | `seed.yaml` → `organ` |
| `tier` | single_select | `flagship`, `standard`, `infrastructure` | `seed.yaml` → `tier` |
| `promotion_status` | single_select | `LOCAL`, `CANDIDATE`, `PUBLIC_PROCESS`, `GRADUATED`, `ARCHIVED` | `seed.yaml` → `promotion_status` |
| `ci_workflow` | single_select | `full-pipeline`, `lint-and-test`, `markdown-lint`, `yaml-lint`, `none` | `seed.yaml` → `ci_agent` |
| `stack` | multi_select | `python`, `typescript`, `markdown`, `mixed` | Inferred from repo content |

---

## Advantages

### Visible in GitHub UI

Custom Properties appear in the repository list view. Org members can filter repos by organ, tier, or promotion status directly in GitHub — no CLI or API needed.

### Queryable via API

```bash
# List all flagship repos
gh api /orgs/organvm-iv-taxis/properties/values \
  --jq '.[] | select(.properties[] | select(.property_name == "tier" and .value == "flagship")) | .repository_name'

# List all CANDIDATE repos
gh api /orgs/organvm-iv-taxis/properties/values \
  --jq '.[] | select(.properties[] | select(.property_name == "promotion_status" and .value == "CANDIDATE")) | .repository_name'
```

### No Separate File Needed

For quick queries ("which repos are flagships?"), you don't need to clone the repo or read `seed.yaml`. The answer is in the GitHub API.

### Ruleset Integration

GitHub rulesets can target repos based on custom properties. Example: apply flagship branch protection to all repos where `tier == flagship`.

```bash
# Ruleset targeting flagship repos
gh api \
  --method POST \
  /orgs/organvm-iv-taxis/rulesets \
  -f name="flagship-protection" \
  -f target="branch" \
  -f enforcement="active" \
  -f 'conditions[ref_name][include][]=refs/heads/main' \
  -f 'conditions[repository_property][][name]=tier' \
  -f 'conditions[repository_property][][property_values][]=flagship' \
  -f 'rules[0][type]=pull_request' \
  -f 'rules[0][parameters][required_approving_review_count]=1'
```

---

## Disadvantages

### GitHub-Specific

Custom Properties only exist in GitHub. If the system ever migrates to another platform (GitLab, Gitea), this metadata is lost. `seed.yaml` and `registry-v2.json` are platform-agnostic.

### Cannot Store Complex Data

Properties are limited to:
- Single-select (one value from a predefined list)
- Multi-select (multiple values from a predefined list)
- String (free text, max 1024 chars)
- True/False

No support for nested objects, arrays, or structured data. The `produces`/`consumes` edges in `seed.yaml` have no equivalent in Custom Properties.

### No Versioning

Custom Properties have no history. When a repo's promotion_status changes from CANDIDATE to PUBLIC_PROCESS, there's no record of when the change happened. `seed.yaml` changes are tracked in git history; registry changes are tracked in `registry-v2.json` commits.

### Org-Level Restriction

Custom Properties are defined per GitHub organization. ORGANVM spans 8+ organizations. Each org must define the same property schema independently — no cross-org inheritance.

### Plan Requirements

Custom Properties require GitHub Team plan or higher for some features. Free organizations have limited access.

---

## Recommendation

**Use Custom Properties as a read-side supplement, not a replacement for `registry-v2.json` or `seed.yaml`.**

### Source of Truth Hierarchy

1. **`seed.yaml`** (per-repo) — Canonical declaration of organ, tier, edges, subscriptions
2. **`registry-v2.json`** (system-wide) — Aggregated view of all repos, computed metrics
3. **GitHub Custom Properties** (per-org) — Read-optimized view for GitHub UI/API queries

### Sync Direction

```
seed.yaml → registry-v2.json → GitHub Custom Properties
```

Never write to seed.yaml or registry based on Custom Properties. The sync is one-way: source files push to GitHub, not the reverse.

---

## Implementation Plan

### Phase 1 — Define Properties

```bash
# Define properties for each org
for org in organvm-iv-taxis meta-organvm organvm-iii-ergon omni-dromenon-machina; do
  # organ property
  gh api --method POST /orgs/$org/properties/schema \
    -f property_name="organ" \
    -f value_type="single_select" \
    -f 'allowed_values[]=I' \
    -f 'allowed_values[]=II' \
    -f 'allowed_values[]=III' \
    -f 'allowed_values[]=IV' \
    -f 'allowed_values[]=V' \
    -f 'allowed_values[]=VI' \
    -f 'allowed_values[]=VII' \
    -f 'allowed_values[]=META'

  # tier property
  gh api --method POST /orgs/$org/properties/schema \
    -f property_name="tier" \
    -f value_type="single_select" \
    -f 'allowed_values[]=flagship' \
    -f 'allowed_values[]=standard' \
    -f 'allowed_values[]=infrastructure'

  # promotion_status property
  gh api --method POST /orgs/$org/properties/schema \
    -f property_name="promotion_status" \
    -f value_type="single_select" \
    -f 'allowed_values[]=LOCAL' \
    -f 'allowed_values[]=CANDIDATE' \
    -f 'allowed_values[]=PUBLIC_PROCESS' \
    -f 'allowed_values[]=GRADUATED' \
    -f 'allowed_values[]=ARCHIVED'
done
```

### Phase 2 — Sync Script

Add to `orchestration-start-here/scripts/`:

```python
#!/usr/bin/env python3
"""Sync registry-v2.json metadata to GitHub Custom Properties."""

import json
import subprocess
import sys

def sync_properties(registry_path: str) -> None:
    with open(registry_path) as f:
        registry = json.load(f)

    for repo in registry["repos"]:
        org = repo["github_org"]
        name = repo["name"]
        properties = {
            "organ": repo.get("organ", ""),
            "tier": repo.get("tier", ""),
            "promotion_status": repo.get("promotion_status", ""),
        }

        for prop_name, value in properties.items():
            if value:
                subprocess.run([
                    "gh", "api", "--method", "PATCH",
                    f"/orgs/{org}/properties/values",
                    "-f", f"repository_names[]={name}",
                    "-f", f"properties[0][property_name]={prop_name}",
                    "-f", f"properties[0][value]={value}",
                ], check=True)

if __name__ == "__main__":
    sync_properties(sys.argv[1] if len(sys.argv) > 1 else "registry.json")
```

### Phase 3 — CI Integration

Add a workflow step that syncs Custom Properties after any registry update:

```yaml
- name: Sync GitHub Custom Properties
  if: github.ref == 'refs/heads/main'
  run: python3 scripts/sync-custom-properties.py registry.json
  env:
    GH_TOKEN: ${{ secrets.ORG_ADMIN_TOKEN }}
```

---

## References

- `registry-v2.json` — System-wide registry (source of truth)
- `seed.yaml` schema — Per-repo metadata (canonical declaration)
- `governance-rules.json` — Article I (registry is single source of truth)
- [Repository Rulesets](repository-rulesets.md) — Rulesets can target repos by Custom Properties
- GitHub docs: https://docs.github.com/en/organizations/managing-organization-settings/managing-custom-properties-for-repositories-in-your-organization
