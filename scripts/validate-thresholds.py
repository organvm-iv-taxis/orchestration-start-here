#!/usr/bin/env python3
"""Threshold topology validation for the governance membrane model.

Validates that governance rules respect their declared radius of effect,
that repositories are governed by rules whose radius reaches them, and
reports unplugged rules, empty thresholds, and unreachable repos.

Permeability model: governance signals attenuate as they cross threshold
boundaries. Each boundary multiplies the signal by its permeability value.
Effective strength below ADVISORY_THRESHOLD (0.3) means the rule is
advisory only — it reaches the target but cannot block.

Usage:
    python3 scripts/validate-thresholds.py
    python3 scripts/validate-thresholds.py --workspace ~/Workspace
    python3 scripts/validate-thresholds.py --ci --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
WORKSPACE = Path.home() / "Workspace"

SCOPE_ORDER = ["SUBSTRATE", "CONTROL", "PRODUCTION", "INTERFACE"]
DEPTH_ORDER = ["ORGANISM", "COMPOUND", "MOLECULE", "ATOM"]

# Enforcement level quantification — maps enforcement strings to signal strength
ENFORCEMENT_STRENGTH: dict[str, float] = {
    "automated": 1.0,
    "manual": 0.6,
    "warn": 0.3,
    "audit": 0.2,
    "unspecified": 0.1,
}

# Below this effective strength, governance is advisory (cannot block)
ADVISORY_THRESHOLD = 0.3

DEFAULT_ORGAN_TO_SCOPE: dict[str, str] = {
    "META-ORGANVM": "SUBSTRATE",
    "ORGAN-IV": "CONTROL",
    "ORGAN-I": "PRODUCTION",
    "ORGAN-II": "PRODUCTION",
    "ORGAN-III": "PRODUCTION",
    "ORGAN-V": "INTERFACE",
    "ORGAN-VI": "INTERFACE",
    "ORGAN-VII": "INTERFACE",
}

ORG_TO_ORGAN: dict[str, str] = {
    "organvm-i-theoria": "ORGAN-I",
    "organvm-ii-poiesis": "ORGAN-II",
    "omni-dromenon-machina": "ORGAN-II",
    "organvm-iii-ergon": "ORGAN-III",
    "labores-profani-crux": "ORGAN-III",
    "organvm-iv-taxis": "ORGAN-IV",
    "organvm-v-logos": "ORGAN-V",
    "organvm-vi-koinonia": "ORGAN-VI",
    "organvm-vii-kerygma": "ORGAN-VII",
    "meta-organvm": "META-ORGANVM",
}

# Organ superproject directories in ~/Workspace
ORGAN_DIRS = [
    "organvm-i-theoria",
    "omni-dromenon-machina",
    "organvm-iii-ergon",
    "organvm-iv-taxis",
    "organvm-v-logos",
    "organvm-vi-koinonia",
    "organvm-vii-kerygma",
    "meta-organvm",
]


def parse_threshold_id(tid: str) -> tuple[str, str] | None:
    """Parse 'T(S,O)' → ('SUBSTRATE', 'ORGANISM'), etc."""
    abbrev_to_scope = {"S": "SUBSTRATE", "C": "CONTROL", "P": "PRODUCTION", "I": "INTERFACE"}
    abbrev_to_depth = {"O": "ORGANISM", "C": "COMPOUND", "M": "MOLECULE", "A": "ATOM"}
    tid = tid.strip()
    if not tid.startswith("T(") or not tid.endswith(")"):
        return None
    inner = tid[2:-1]
    parts = [p.strip() for p in inner.split(",")]
    if len(parts) != 2:
        return None
    scope = abbrev_to_scope.get(parts[0])
    depth = abbrev_to_depth.get(parts[1])
    if scope is None or depth is None:
        return None
    return (scope, depth)


def make_threshold_id(scope: str, depth: str) -> str:
    """Build threshold ID from scope and depth names."""
    scope_abbrev = {"SUBSTRATE": "S", "CONTROL": "C", "PRODUCTION": "P", "INTERFACE": "I"}
    depth_abbrev = {"ORGANISM": "O", "COMPOUND": "C", "MOLECULE": "M", "ATOM": "A"}
    return f"T({scope_abbrev[scope]},{depth_abbrev[depth]})"


def scope_distance(s1: str, s2: str) -> int:
    """Lateral distance between two scopes."""
    return abs(SCOPE_ORDER.index(s1) - SCOPE_ORDER.index(s2))


def depth_distance(d1: str, d2: str) -> int:
    """Vertical distance between two depths (positive = deeper)."""
    return DEPTH_ORDER.index(d2) - DEPTH_ORDER.index(d1)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file with clear error on failure."""
    if not path.is_file():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(2)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_organ_to_scope(thresholds: dict) -> dict[str, str]:
    """Build organ→scope mapping from thresholds file scope_mapping."""
    mapping: dict[str, str] = {}
    for scope, info in thresholds.get("scope_mapping", {}).items():
        for organ in info.get("organs", []):
            mapping[organ] = scope
    return mapping or DEFAULT_ORGAN_TO_SCOPE


def discover_seed_files(workspace: Path, local_only: bool = False) -> list[Path]:
    """Find all seed.yaml files across the workspace or locally."""
    seeds: list[Path] = []
    if local_only:
        for p in PROJECT_DIR.parent.rglob("seed.yaml"):
            seeds.append(p)
        return seeds

    for organ_dir in ORGAN_DIRS:
        organ_path = workspace / organ_dir
        if not organ_path.is_dir():
            continue
        for p in organ_path.rglob("seed.yaml"):
            # Skip deeply nested paths (node_modules, .venv, etc.)
            rel = p.relative_to(organ_path)
            if any(part.startswith(".") or part in ("node_modules", ".venv", "__pycache__")
                   for part in rel.parts[:-1]):
                continue
            seeds.append(p)
    return seeds


def classify_repo_from_seed(seed_path: Path) -> dict[str, str] | None:
    """Extract organ and repo name from a seed.yaml file."""
    try:
        import yaml
    except ImportError:
        return _classify_seed_simple(seed_path)
    with seed_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return None
    organ_num = data.get("organ")
    repo = data.get("repo", seed_path.parent.name)
    org = data.get("org", "")
    organ = _resolve_organ(organ_num, org)
    if organ is None:
        return None
    return {"organ": organ, "repo": repo, "path": str(seed_path)}


def _classify_seed_simple(seed_path: Path) -> dict[str, str] | None:
    """Parse seed.yaml without pyyaml — extract organ and repo fields."""
    organ_num = None
    repo = seed_path.parent.name
    org = ""
    with seed_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("organ:") and "organ_name" not in line:
                val = line.split(":", 1)[1].strip().strip("'\"")
                organ_num = val
            elif line.startswith("repo:"):
                repo = line.split(":", 1)[1].strip().strip("'\"")
            elif line.startswith("org:"):
                org = line.split(":", 1)[1].strip().strip("'\"")
    organ = _resolve_organ(organ_num, org)
    if organ is None:
        return None
    return {"organ": organ, "repo": repo, "path": str(seed_path)}


def _resolve_organ(organ_num: str | None, org: str) -> str | None:
    """Resolve organ identifier from number or org name."""
    if organ_num is not None:
        organ_num_str = str(organ_num).strip()
        if organ_num_str.startswith("ORGAN-") or organ_num_str.startswith("META"):
            return organ_num_str
        roman = {"I": "ORGAN-I", "II": "ORGAN-II", "III": "ORGAN-III",
                 "IV": "ORGAN-IV", "V": "ORGAN-V", "VI": "ORGAN-VI",
                 "VII": "ORGAN-VII", "META": "META-ORGANVM"}
        if organ_num_str in roman:
            return roman[organ_num_str]
    if org in ORG_TO_ORGAN:
        return ORG_TO_ORGAN[org]
    return None


def collect_rules(governance: dict) -> list[dict[str, Any]]:
    """Collect all governance rules with their threshold annotations."""
    rules: list[dict[str, Any]] = []

    for art_id, art in governance.get("articles", {}).items():
        rules.append({
            "id": f"art_{art_id}",
            "title": art.get("title", ""),
            "type": "article",
            "enforcement": art.get("enforcement", "unspecified"),
            "threshold": art.get("threshold"),
        })

    for amend_id, amend in governance.get("amendments", {}).items():
        rules.append({
            "id": f"amend_{amend_id}",
            "title": amend.get("title", ""),
            "type": "amendment",
            "enforcement": amend.get("enforcement", "unspecified"),
            "threshold": amend.get("threshold"),
        })

    for rule_id, rule in governance.get("rules", {}).items():
        rules.append({
            "id": f"rule_{rule_id}",
            "title": rule_id.replace("-", " ").replace("_", " ").title(),
            "type": "promotion_rule",
            "enforcement": "manual",
            "threshold": rule.get("threshold"),
        })

    for gate_id, gate in governance.get("quality_gates", {}).items():
        threshold = gate.get("threshold") if isinstance(gate, dict) else None
        rules.append({
            "id": f"gate_{gate_id}",
            "title": f"Quality Gate: {gate_id}",
            "type": "quality_gate",
            "enforcement": "manual",
            "threshold": threshold,
        })

    wip = governance.get("wip_limits", {})
    if isinstance(wip, dict) and "threshold" in wip:
        rules.append({
            "id": "wip_limits",
            "title": "WIP Limits",
            "type": "wip_limit",
            "enforcement": wip.get("enforcement", "warn"),
            "threshold": wip["threshold"],
        })

    for cg_id, cg in governance.get("classified_governance", {}).items():
        if cg_id.startswith("_"):
            continue
        rules.append({
            "id": f"classified_{cg_id}",
            "title": cg.get("title", ""),
            "type": "classified",
            "enforcement": cg.get("enforcement", "unspecified"),
            "threshold": cg.get("threshold"),
        })

    return rules


def validate_rule_radius(rule: dict, thresholds: dict) -> list[str]:
    """Validate that a rule's declared radius is physically possible."""
    errors: list[str] = []
    threshold = rule.get("threshold")
    if threshold is None:
        return errors

    origin_id = threshold.get("origin", "")
    parsed = parse_threshold_id(origin_id)
    if parsed is None:
        errors.append(f"{rule['id']}: invalid origin threshold ID '{origin_id}'")
        return errors

    origin_scope, origin_depth = parsed
    r_down = threshold.get("radius_down", 0)
    r_up = threshold.get("radius_up", 0)
    r_lat = threshold.get("radius_lateral", 0)

    depth_idx = DEPTH_ORDER.index(origin_depth)
    scope_idx = SCOPE_ORDER.index(origin_scope)

    max_down = len(DEPTH_ORDER) - 1 - depth_idx
    if r_down > max_down:
        errors.append(f"{rule['id']}: radius_down={r_down} exceeds max={max_down} from {origin_id}")

    max_up = depth_idx
    if r_up > max_up:
        errors.append(f"{rule['id']}: radius_up={r_up} exceeds max={max_up} from {origin_id}")

    max_lat = max(scope_idx, len(SCOPE_ORDER) - 1 - scope_idx)
    if r_lat > max_lat:
        errors.append(f"{rule['id']}: radius_lateral={r_lat} exceeds max={max_lat} from {origin_id}")

    if origin_id not in thresholds.get("thresholds", {}):
        errors.append(f"{rule['id']}: origin {origin_id} not found in threshold topology")

    return errors


def compute_effective_strength(
    rule: dict,
    repo_scope: str,
    threshold_cells: dict[str, Any],
) -> float | None:
    """Compute effective governance strength of a rule at a repo.

    The signal starts at the rule's enforcement strength, then attenuates
    as it crosses each threshold boundary along the path from origin to
    the repo's cell (scope, MOLECULE depth).

    Returns None if the rule cannot reach the repo (radius insufficient).
    Returns the attenuated strength otherwise.
    """
    threshold = rule.get("threshold")
    if threshold is None:
        return None

    parsed = parse_threshold_id(threshold.get("origin", ""))
    if parsed is None:
        return None

    origin_scope, origin_depth = parsed
    r_down = threshold.get("radius_down", 0)
    r_up = threshold.get("radius_up", 0)
    r_lat = threshold.get("radius_lateral", 0)

    target_depth = "MOLECULE"
    d_dist = depth_distance(origin_depth, target_depth)

    if d_dist > 0 and d_dist > r_down:
        return None
    if d_dist < 0 and abs(d_dist) > r_up:
        return None

    s_dist = scope_distance(origin_scope, repo_scope)
    if s_dist > r_lat:
        return None

    # Start with rule's base enforcement strength
    base = ENFORCEMENT_STRENGTH.get(rule.get("enforcement", "unspecified"), 0.1)
    strength = base

    # Attenuate through each depth boundary crossed
    origin_depth_idx = DEPTH_ORDER.index(origin_depth)
    target_depth_idx = DEPTH_ORDER.index(target_depth)

    if d_dist > 0:
        # Going down — multiply by each cell's permeability.down along the path
        for di in range(origin_depth_idx + 1, target_depth_idx + 1):
            cell_id = make_threshold_id(origin_scope, DEPTH_ORDER[di])
            cell = threshold_cells.get(cell_id, {})
            perm = cell.get("permeability", {}).get("down", 0.8)
            strength *= perm
    elif d_dist < 0:
        # Going up
        for di in range(origin_depth_idx - 1, target_depth_idx - 1, -1):
            cell_id = make_threshold_id(origin_scope, DEPTH_ORDER[di])
            cell = threshold_cells.get(cell_id, {})
            perm = cell.get("permeability", {}).get("up", 0.2)
            strength *= perm

    # Attenuate through lateral boundary crossings
    if s_dist > 0:
        origin_scope_idx = SCOPE_ORDER.index(origin_scope)
        repo_scope_idx = SCOPE_ORDER.index(repo_scope)
        step = 1 if repo_scope_idx > origin_scope_idx else -1
        for si in range(origin_scope_idx + step, repo_scope_idx + step, step):
            cell_id = make_threshold_id(SCOPE_ORDER[si], target_depth)
            cell = threshold_cells.get(cell_id, {})
            perm = cell.get("permeability", {}).get("lateral", 0.5)
            strength *= perm

    return strength


def rule_reaches_repo(rule: dict, repo_scope: str, organ_to_scope: dict) -> bool:
    """Check if a rule's radius reaches a repo at MOLECULE depth in given scope."""
    threshold = rule.get("threshold")
    if threshold is None:
        return False

    parsed = parse_threshold_id(threshold.get("origin", ""))
    if parsed is None:
        return False

    origin_scope, origin_depth = parsed
    r_down = threshold.get("radius_down", 0)
    r_up = threshold.get("radius_up", 0)
    r_lat = threshold.get("radius_lateral", 0)

    target_depth = "MOLECULE"
    d_dist = depth_distance(origin_depth, target_depth)

    if d_dist > 0 and d_dist > r_down:
        return False
    if d_dist < 0 and abs(d_dist) > r_up:
        return False

    s_dist = scope_distance(origin_scope, repo_scope)
    if s_dist > r_lat:
        return False

    return True


def validate(
    thresholds_path: Path,
    governance_path: Path,
    workspace: Path,
    local_only: bool = False,
    show_strength: bool = False,
) -> dict[str, Any]:
    """Run full threshold topology validation. Returns structured results."""
    thresholds = load_json(thresholds_path)
    governance = load_json(governance_path)

    current_wave = thresholds.get("wave", 0)
    organ_to_scope = build_organ_to_scope(thresholds)
    all_rules = collect_rules(governance)
    threshold_cells = thresholds.get("thresholds", {})

    plugged: list[dict] = []
    unplugged: list[dict] = []
    errors: list[str] = []

    for rule in all_rules:
        if rule.get("threshold") is None:
            unplugged.append(rule)
        else:
            plugged.append(rule)
            errs = validate_rule_radius(rule, thresholds)
            errors.extend(errs)

    cells_with_rules: set[str] = set()
    for rule in plugged:
        origin = rule["threshold"].get("origin", "")
        cells_with_rules.add(origin)
    empty_cells = [tid for tid in threshold_cells if tid not in cells_with_rules]

    seeds = discover_seed_files(workspace, local_only=local_only)
    repos: list[dict] = []
    unreachable: list[dict] = []
    repo_governance: dict[str, list[dict]] = {}  # repo_key → list of {rule_id, strength, advisory}

    for seed_path in seeds:
        info = classify_repo_from_seed(seed_path)
        if info is None:
            continue
        organ = info["organ"]
        repo_scope = organ_to_scope.get(organ)
        if repo_scope is None:
            continue

        repo_key = f"{organ}/{info['repo']}"
        repos.append({**info, "scope": repo_scope, "key": repo_key})

        governing_rules: list[dict] = []
        for r in plugged:
            strength = compute_effective_strength(r, repo_scope, threshold_cells)
            if strength is not None:
                governing_rules.append({
                    "rule_id": r["id"],
                    "strength": round(strength, 3),
                    "advisory": strength < ADVISORY_THRESHOLD,
                })

        repo_governance[repo_key] = governing_rules
        if not governing_rules:
            unreachable.append(info)

    # Count repos per scope
    scope_counts: dict[str, int] = {}
    for r in repos:
        scope_counts[r["scope"]] = scope_counts.get(r["scope"], 0) + 1

    return {
        "wave": current_wave,
        "threshold_count": len(threshold_cells),
        "rule_count": len(all_rules),
        "repo_count": len(repos),
        "scope_counts": scope_counts,
        "plugged": plugged,
        "unplugged": unplugged,
        "empty_cells": empty_cells,
        "unreachable": unreachable,
        "errors": errors,
        "repos": repos,
        "repo_governance": repo_governance,
        "organ_to_scope": organ_to_scope,
        "threshold_cells": threshold_cells,
        "show_strength": show_strength,
    }


def print_report(results: dict[str, Any]) -> None:
    """Print human-readable validation report."""
    plugged = results["plugged"]
    unplugged = results["unplugged"]
    repos = results["repos"]
    repo_governance = results["repo_governance"]
    organ_to_scope = results["organ_to_scope"]
    threshold_cells = results["threshold_cells"]
    show_strength = results["show_strength"]

    print("=== Threshold Topology Validation ===")
    print(f"Wave: {results['wave']} | Thresholds: {results['threshold_count']} | "
          f"Rules: {results['rule_count']} | Repos: {results['repo_count']}")
    if results["scope_counts"]:
        parts = [f"{s}: {c}" for s, c in sorted(results["scope_counts"].items())]
        print(f"  Scope breakdown: {', '.join(parts)}")
    print()

    print(f"PLUGGED ({len(plugged)}/{results['rule_count']}):")
    for rule in plugged:
        t = rule["threshold"]
        origin = t.get("origin", "?")
        r_down = t.get("radius_down", 0)
        r_lat = t.get("radius_lateral", 0)
        reached_count = sum(
            1 for r in repos
            if rule_reaches_repo(rule, r["scope"], organ_to_scope)
        )
        # Count active vs advisory
        active_count = 0
        advisory_count = 0
        for r in repos:
            strength = compute_effective_strength(rule, r["scope"], threshold_cells)
            if strength is not None:
                if strength >= ADVISORY_THRESHOLD:
                    active_count += 1
                else:
                    advisory_count += 1

        status = "✓" if reached_count > 0 or r_down == 0 else "⚠ reaches 0 repos"
        strength_info = ""
        if show_strength and advisory_count > 0:
            strength_info = f" ({active_count} active, {advisory_count} advisory)"
        print(f"  {rule['id']:<40s} {origin} r↓{r_down} r↔{r_lat}  "
              f"{status} {reached_count}/{results['repo_count']}{strength_info}")
    print()

    if unplugged:
        print(f"UNPLUGGED ({len(unplugged)}/{results['rule_count']}):")
        for rule in unplugged:
            print(f"  {rule['id']:<40s} — no origin_threshold assigned")
        print()

    if results["empty_cells"]:
        print(f"EMPTY ({len(results['empty_cells'])}/{results['threshold_count']} thresholds):")
        print(f"  {', '.join(sorted(results['empty_cells']))}")
        print()

    unreachable = results["unreachable"]
    if unreachable:
        print(f"UNREACHABLE ({len(unreachable)}/{results['repo_count']} repos):")
        for r in unreachable:
            print(f"  {r['organ']}/{r['repo']}")
        print()
    else:
        print(f"UNREACHABLE (0/{results['repo_count']} repos): ✓ All governed")
        print()

    if results["errors"]:
        print(f"ERRORS ({len(results['errors'])}):")
        for err in results["errors"]:
            print(f"  ✗ {err}")
        print()

    # Permeability strength summary
    if show_strength and repos:
        print("GOVERNANCE STRENGTH (per scope):")
        for scope in SCOPE_ORDER:
            scope_repos = [r for r in repos if r["scope"] == scope]
            if not scope_repos:
                print(f"  {scope:<12s} — no repos")
                continue
            strengths: list[float] = []
            for r in scope_repos:
                gov = repo_governance.get(r["key"], [])
                active = [g for g in gov if not g["advisory"]]
                strengths.append(len(active))
            avg_active = sum(strengths) / len(strengths) if strengths else 0
            print(f"  {scope:<12s} {len(scope_repos):>3d} repos, avg {avg_active:.1f} active rules/repo")
        print()

    total_issues = len(results["errors"]) + len(unreachable)
    if total_issues == 0:
        print("Topology valid. All rules within declared radius. All repos governed.")
    else:
        print(f"{total_issues} issue(s) found.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate governance threshold topology"
    )
    parser.add_argument(
        "--thresholds",
        default=str(PROJECT_DIR / "governance-thresholds.json"),
        help="Path to governance-thresholds.json",
    )
    parser.add_argument(
        "--governance",
        default=str(PROJECT_DIR / "governance-rules.json"),
        help="Path to governance-rules.json",
    )
    parser.add_argument(
        "--workspace",
        default=str(WORKSPACE),
        help="Workspace root containing organ superproject directories",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Only scan local submodules (not full workspace)",
    )
    parser.add_argument(
        "--strength",
        action="store_true",
        help="Show permeability-attenuated governance strength per scope",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode — strict exit codes, compact output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON (for CI consumption)",
    )
    args = parser.parse_args()

    results = validate(
        thresholds_path=Path(args.thresholds),
        governance_path=Path(args.governance),
        workspace=Path(args.workspace),
        local_only=args.local,
        show_strength=args.strength or args.ci,
    )

    if args.json_output:
        output = {
            "wave": results["wave"],
            "thresholds": results["threshold_count"],
            "rules": results["rule_count"],
            "repos": results["repo_count"],
            "scope_counts": results["scope_counts"],
            "plugged": len(results["plugged"]),
            "unplugged": len(results["unplugged"]),
            "empty_cells": results["empty_cells"],
            "unreachable": [f"{r['organ']}/{r['repo']}" for r in results["unreachable"]],
            "errors": results["errors"],
            "valid": len(results["errors"]) == 0 and len(results["unreachable"]) == 0,
        }
        json.dump(output, sys.stdout, indent=2)
        print()
    else:
        print_report(results)

    issue_count = len(results["errors"]) + len(results["unreachable"])
    sys.exit(1 if issue_count > 0 else 0)


if __name__ == "__main__":
    main()
