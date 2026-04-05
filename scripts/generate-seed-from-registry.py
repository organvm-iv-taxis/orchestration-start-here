#!/usr/bin/env python3
"""Reconcile seed.yaml files against registry-v2.json.
# ISOTOPE DISSOLUTION: Gate circulatory--contribute G1

Three modes:
  --mode report    Dry-run: show drift between seeds and registry
  --mode reconcile Update metadata in existing seeds to match registry (registry wins)
  --mode generate  Create seed.yaml for repos that are missing one

When organvm-engine is installed, uses canonical seed discovery and registry
loading. Falls back to standalone implementation.

Registry is the single source of truth (Article I).

Usage:
    python3 scripts/generate-seed-from-registry.py --mode report
    python3 scripts/generate-seed-from-registry.py --mode reconcile
    python3 scripts/generate-seed-from-registry.py --mode generate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

# --- Canonical engine imports (isotope dissolution) ---
try:
    from organvm_engine.organ_config import get_organ_map as _engine_get_organ_map
    from organvm_engine.paths import registry_path as _engine_registry_path
    from organvm_engine.registry.loader import load_registry as _engine_load_registry
    from organvm_engine.seed.discover import discover_seeds as _engine_discover_seeds

    _HAS_ENGINE = True
except ImportError:
    _HAS_ENGINE = False

WORKSPACE = Path.home() / "Workspace"
REGISTRY_PATH = WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json"

ORG_DIRS = {
    "organvm-i-theoria": "organvm-i-theoria",
    "organvm-ii-poiesis": "organvm-ii-poiesis",
    "organvm-iii-ergon": "organvm-iii-ergon",
    "organvm-iv-taxis": "organvm-iv-taxis",
    "organvm-v-logos": "organvm-v-logos",
    "organvm-vi-koinonia": "organvm-vi-koinonia",
    "organvm-vii-kerygma": "organvm-vii-kerygma",
    "meta-organvm": "meta-organvm",
}

ORGAN_NAMES = {
    "ORGAN-I": "Theory",
    "ORGAN-II": "Art",
    "ORGAN-III": "Commerce",
    "ORGAN-IV": "Orchestration",
    "ORGAN-V": "Public Process",
    "ORGAN-VI": "Community",
    "ORGAN-VII": "Marketing",
    "META-ORGANVM": "Meta",
}

ORGAN_NUMBERS = {
    "ORGAN-I": "I",
    "ORGAN-II": "II",
    "ORGAN-III": "III",
    "ORGAN-IV": "IV",
    "ORGAN-V": "V",
    "ORGAN-VI": "VI",
    "ORGAN-VII": "VII",
    "META-ORGANVM": "Meta",
}

# Fields to reconcile (registry key → seed metadata key)
RECONCILE_FIELDS = {
    "implementation_status": "implementation_status",
    "tier": "tier",
    "promotion_status": "promotion_status",
    "last_validated": "last_validated",
}

# Map old implementation_status values to current schema
STATUS_NORMALIZATION = {
    "PRODUCTION": "ACTIVE",
}


def load_registry(path: Path) -> dict:
    """Load registry-v2.json and flatten into {org/repo: entry} dict."""
    with open(path) as f:
        data = json.load(f)

    flat: dict[str, dict] = {}
    for organ_id, organ in data.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            org = repo.get("org", "")
            name = repo.get("name", "")
            if org and name:
                key = f"{org}/{name}"
                repo["_organ_id"] = organ_id
                flat[key] = repo
    return flat


def discover_seeds(workspace: Path) -> dict[str, Path]:
    """Find all seed.yaml in workspace, keyed by org/repo."""
    found: dict[str, Path] = {}
    for org_name, org_dir_name in ORG_DIRS.items():
        org_dir = workspace / org_dir_name
        if not org_dir.is_dir():
            continue
        for repo_dir in sorted(org_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            seed_path = repo_dir / "seed.yaml"
            if seed_path.is_file():
                found[f"{org_name}/{repo_dir.name}"] = seed_path
    return found


def read_seed(path: Path) -> dict | None:
    """Parse a seed.yaml, returning None on error."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def compute_drift(registry: dict, seeds: dict[str, Path]) -> list[dict]:
    """Compare registry entries against seed.yaml metadata. Returns drift items."""
    drifts = []

    for key, reg_entry in sorted(registry.items()):
        if key not in seeds:
            drifts.append({
                "key": key,
                "type": "missing_seed",
                "message": "No seed.yaml found on disk",
            })
            continue

        seed_data = read_seed(seeds[key])
        if seed_data is None:
            drifts.append({
                "key": key,
                "type": "parse_error",
                "message": "Could not parse seed.yaml",
            })
            continue

        metadata = seed_data.get("metadata", {})

        for reg_field, seed_field in RECONCILE_FIELDS.items():
            reg_value = reg_entry.get(reg_field, "")
            seed_value = metadata.get(seed_field, "")

            # Normalize known renames
            normalized_seed = STATUS_NORMALIZATION.get(seed_value, seed_value)

            if str(reg_value) != str(normalized_seed):
                drifts.append({
                    "key": key,
                    "type": "field_drift",
                    "field": seed_field,
                    "registry_value": reg_value,
                    "seed_value": seed_value,
                    "normalized_seed": normalized_seed,
                })

    # Seeds without registry entries
    for key in sorted(seeds):
        if key not in registry:
            drifts.append({
                "key": key,
                "type": "orphan_seed",
                "message": "seed.yaml exists but no registry entry",
            })

    return drifts


def report_mode(registry: dict, seeds: dict[str, Path]) -> int:
    """Dry-run: print drift report."""
    drifts = compute_drift(registry, seeds)

    print("Seed Reconciliation Report")
    print("=" * 60)
    print(f"Registry entries: {len(registry)}")
    print(f"Seeds on disk:    {len(seeds)}")
    print()

    missing = [d for d in drifts if d["type"] == "missing_seed"]
    field_drifts = [d for d in drifts if d["type"] == "field_drift"]
    orphans = [d for d in drifts if d["type"] == "orphan_seed"]
    errors = [d for d in drifts if d["type"] == "parse_error"]

    if not drifts:
        print("No drift detected. Registry and seeds are in sync.")
        return 0

    if missing:
        print(f"\nMissing seeds ({len(missing)}):")
        for d in missing:
            print(f"  {d['key']}")

    if field_drifts:
        print(f"\nField drift ({len(field_drifts)}):")
        for d in field_drifts:
            print(f"  {d['key']}.metadata.{d['field']}:")
            print(f"    registry: {d['registry_value']}")
            print(f"    seed:     {d['seed_value']}", end="")
            if d["seed_value"] != d["normalized_seed"]:
                print(f" (normalized: {d['normalized_seed']})", end="")
            print()

    if orphans:
        print(f"\nOrphan seeds ({len(orphans)}):")
        for d in orphans:
            print(f"  {d['key']}")

    if errors:
        print(f"\nParse errors ({len(errors)}):")
        for d in errors:
            print(f"  {d['key']}: {d['message']}")

    total_issues = len(drifts)
    print(f"\nTotal issues: {total_issues}")
    return total_issues


def reconcile_mode(registry: dict, seeds: dict[str, Path]) -> int:
    """Update seed.yaml metadata to match registry."""
    drifts = compute_drift(registry, seeds)
    field_drifts = [d for d in drifts if d["type"] == "field_drift"]

    if not field_drifts:
        print("No field drift to reconcile.")
        return 0

    # Group drifts by key
    by_key: dict[str, list[dict]] = {}
    for d in field_drifts:
        by_key.setdefault(d["key"], []).append(d)

    updated = 0
    for key, key_drifts in sorted(by_key.items()):
        if key not in seeds:
            continue

        path = seeds[key]
        with open(path) as f:
            content = f.read()

        for d in key_drifts:
            old_field = d["field"]
            old_value = d["seed_value"]
            new_value = d["registry_value"]

            # Simple string replacement in YAML
            old_line = f"  {old_field}: {old_value}"
            new_line = f"  {old_field}: {new_value}"

            # Try with quotes too
            old_line_quoted = f'  {old_field}: "{old_value}"'
            new_line_final = f'  {old_field}: "{new_value}"' if isinstance(new_value, str) and not new_value.startswith('"') else new_line

            if old_line_quoted in content:
                content = content.replace(old_line_quoted, new_line_final, 1)
            elif old_line in content:
                content = content.replace(old_line, new_line, 1)
            else:
                print(f"  WARNING: Could not find '{old_line}' in {path}")
                continue

        with open(path, "w") as f:
            f.write(content)

        updated += 1
        print(f"  Updated {key} ({len(key_drifts)} fields)")

    print(f"\nReconciled {updated} seeds.")
    return 0


def generate_seed(key: str, reg_entry: dict, workspace: Path) -> Path | None:
    """Generate a seed.yaml for a repo missing one."""
    org, repo = key.split("/", 1)
    organ_id = reg_entry.get("_organ_id", "UNKNOWN")
    organ_number = ORGAN_NUMBERS.get(organ_id, organ_id)
    organ_name = ORGAN_NAMES.get(organ_id, "Unknown")

    repo_dir = workspace / ORG_DIRS.get(org, org) / repo
    if not repo_dir.is_dir():
        return None

    seed = {
        "schema_version": "1.0",
        "organ": organ_number,
        "organ_name": organ_name,
        "repo": repo,
        "org": org,
        "metadata": {
            "implementation_status": reg_entry.get("implementation_status", "ACTIVE"),
            "tier": reg_entry.get("tier", "standard"),
            "promotion_status": reg_entry.get("promotion_status", "LOCAL"),
            "last_validated": reg_entry.get("last_validated", ""),
            "generated": "2026-02-24",
            "sprint": "IGNITION",
        },
        "agents": [{
            "name": "ci",
            "trigger": "on_push",
            "workflow": f".github/workflows/{reg_entry.get('ci_workflow', 'ci-python.yml')}",
            "description": "Continuous integration pipeline",
        }],
        "consumes": [],
        "subscriptions": [],
    }

    # Add dependencies as consumes entries
    for dep in reg_entry.get("dependencies", []):
        seed.setdefault("consumes", []).append({
            "type": "dependency",
            "source": dep,
            "description": f"Depends on {dep}",
        })

    seed_path = repo_dir / "seed.yaml"
    header = (
        f"# seed.yaml — Automation Contract for {key}\n"
        f"# Schema: seed/v1.0\n"
        f"# Generated: 2026-02-24 (IGNITION Sprint)\n\n"
    )
    with open(seed_path, "w") as f:
        f.write(header)
        yaml.dump(seed, f, default_flow_style=False, sort_keys=False)

    return seed_path


def generate_mode(registry: dict, seeds: dict[str, Path]) -> int:
    """Generate seed.yaml for repos missing one."""
    missing = [key for key in registry if key not in seeds]

    if not missing:
        print("All registry repos have seed.yaml files.")
        return 0

    generated = 0
    for key in sorted(missing):
        path = generate_seed(key, registry[key], WORKSPACE)
        if path:
            print(f"  Generated {path}")
            generated += 1
        else:
            print(f"  SKIPPED {key} (repo dir not found on disk)")

    print(f"\nGenerated {generated} seed.yaml files.")
    return 0


def main():
    default_registry = str(_engine_registry_path()) if _HAS_ENGINE else str(REGISTRY_PATH)

    parser = argparse.ArgumentParser(description="Reconcile seed.yaml vs registry-v2.json")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["report", "reconcile", "generate"],
        help="report=dry-run, reconcile=update seeds, generate=create missing seeds",
    )
    parser.add_argument(
        "--registry",
        default=default_registry,
        help=f"Path to registry-v2.json (default: {default_registry})",
    )
    parser.add_argument(
        "--workspace",
        default=str(WORKSPACE),
        help=f"Workspace root (default: {WORKSPACE})",
    )
    args = parser.parse_args()

    if _HAS_ENGINE:
        # Use engine's canonical registry loader
        registry = load_registry(Path(args.registry))
        # Use engine's canonical seed discovery, convert to keyed dict
        seed_paths = _engine_discover_seeds(workspace=Path(args.workspace))
        seeds = {}
        for p in seed_paths:
            repo_dir = p.parent
            org_dir = repo_dir.parent
            key = f"{org_dir.name}/{repo_dir.name}"
            seeds[key] = p
    else:
        registry = load_registry(Path(args.registry))
        seeds = discover_seeds(Path(args.workspace))

    if args.mode == "report":
        issues = report_mode(registry, seeds)
        sys.exit(1 if issues > 0 else 0)
    elif args.mode == "reconcile":
        sys.exit(reconcile_mode(registry, seeds))
    elif args.mode == "generate":
        sys.exit(generate_mode(registry, seeds))


if __name__ == "__main__":
    main()
