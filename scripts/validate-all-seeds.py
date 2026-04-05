#!/usr/bin/env python3
"""Validate all seed.yaml files across the workspace.
# ISOTOPE DISSOLUTION: Gate circulatory--contribute G1

Three validation layers:
  1. Schema — YAML parseable, required fields present
  2. Registry agreement — metadata matches registry-v2.json
  3. Graph integrity — produces/consumes references resolve

When organvm-engine is installed, delegates seed discovery and contract
validation to the canonical modules. Falls back to standalone implementation.

Usage:
    python3 scripts/validate-all-seeds.py
    python3 scripts/validate-all-seeds.py --registry /path/to/registry-v2.json
    python3 scripts/validate-all-seeds.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

# --- Canonical engine imports (isotope dissolution) ---
try:
    from organvm_engine.paths import registry_path as _engine_registry_path
    from organvm_engine.registry.loader import load_registry as _engine_load_registry
    from organvm_engine.seed.contracts import validate_contract as _engine_validate_contract
    from organvm_engine.seed.discover import discover_seeds as _engine_discover_seeds
    from organvm_engine.seed.graph import validate_edge_resolution as _engine_validate_edges

    _HAS_ENGINE = True
except ImportError:
    _HAS_ENGINE = False

WORKSPACE = Path.home() / "Workspace"
REGISTRY_PATH = WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json"

ORGAN_ORGS = [
    "organvm-i-theoria",
    "organvm-ii-poiesis",
    "organvm-iii-ergon",
    "organvm-iv-taxis",
    "organvm-v-logos",
    "organvm-vi-koinonia",
    "organvm-vii-kerygma",
    "meta-organvm",
]

REQUIRED_FIELDS = ["schema_version", "organ", "repo", "org"]

VALID_IMPLEMENTATION_STATUS = {"ACTIVE", "PROTOTYPE", "SKELETON", "DESIGN_ONLY", "ARCHIVED"}
VALID_PROMOTION_STATUS = {"LOCAL", "CANDIDATE", "PUBLIC_PROCESS", "GRADUATED", "ARCHIVED"}
VALID_TIERS = {"flagship", "standard", "stub", "archive", "infrastructure"}

STATUS_NORMALIZATION = {"PRODUCTION": "ACTIVE"}


def discover_seeds(workspace: Path) -> dict[str, Path]:
    """Find all seed.yaml in workspace, keyed by org/repo."""
    found: dict[str, Path] = {}
    for org_name in ORGAN_ORGS:
        org_dir = workspace / org_name
        if not org_dir.is_dir():
            continue
        for repo_dir in sorted(org_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            seed_path = repo_dir / "seed.yaml"
            if seed_path.is_file():
                found[f"{org_name}/{repo_dir.name}"] = seed_path
    return found


def load_registry(path: Path) -> dict[str, dict]:
    """Load registry-v2.json into {org/repo: entry} dict."""
    with open(path) as f:
        data = json.load(f)
    flat: dict[str, dict] = {}
    for organ_id, organ in data.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            org = repo.get("org", "")
            name = repo.get("name", "")
            if org and name:
                flat[f"{org}/{name}"] = repo
    return flat


def validate_schema(path: Path, key: str) -> list[str]:
    """Layer 1: Schema validation."""
    errors = []
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"{key}: YAML parse error: {e}"]

    if not isinstance(data, dict):
        return [f"{key}: Not a YAML mapping"]

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{key}: Missing required field '{field}'")

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        errors.append(f"{key}: 'metadata' is not a mapping")
    else:
        impl_status = metadata.get("implementation_status", "")
        normalized = STATUS_NORMALIZATION.get(impl_status, impl_status)
        if normalized and normalized not in VALID_IMPLEMENTATION_STATUS:
            errors.append(f"{key}: Invalid implementation_status '{impl_status}'")

        promo = metadata.get("promotion_status", "")
        if promo and promo not in VALID_PROMOTION_STATUS:
            errors.append(f"{key}: Invalid promotion_status '{promo}'")

        tier = metadata.get("tier", "")
        if tier and tier not in VALID_TIERS:
            errors.append(f"{key}: Invalid tier '{tier}'")

    # Validate identity matches path
    seed_org = data.get("org", "")
    seed_repo = data.get("repo", "")
    expected_org, expected_repo = key.split("/", 1)
    if seed_org and seed_org != expected_org:
        errors.append(f"{key}: org mismatch (seed says '{seed_org}', expected '{expected_org}')")
    if seed_repo and seed_repo != expected_repo:
        errors.append(f"{key}: repo mismatch (seed says '{seed_repo}', expected '{expected_repo}')")

    return errors


def validate_registry_agreement(
    path: Path, key: str, registry: dict[str, dict]
) -> list[str]:
    """Layer 2: Check metadata matches registry."""
    errors = []

    if key not in registry:
        errors.append(f"{key}: Not in registry-v2.json")
        return errors

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except Exception:
        return []  # Already caught in schema layer

    if not isinstance(data, dict):
        return []

    metadata = data.get("metadata", {})
    reg = registry[key]

    check_fields = {
        "tier": "tier",
        "promotion_status": "promotion_status",
    }

    for reg_field, seed_field in check_fields.items():
        reg_val = str(reg.get(reg_field, ""))
        seed_val = str(metadata.get(seed_field, ""))
        if reg_val and seed_val and reg_val != seed_val:
            errors.append(
                f"{key}: {seed_field} mismatch "
                f"(registry='{reg_val}', seed='{seed_val}')"
            )

    # Check implementation_status with normalization
    reg_impl = reg.get("implementation_status", "")
    seed_impl = metadata.get("implementation_status", "")
    normalized_seed_impl = STATUS_NORMALIZATION.get(seed_impl, seed_impl)
    if reg_impl and normalized_seed_impl and reg_impl != normalized_seed_impl:
        errors.append(
            f"{key}: implementation_status mismatch "
            f"(registry='{reg_impl}', seed='{seed_impl}')"
        )

    return errors


def validate_graph_integrity(seeds: dict[str, Path]) -> list[str]:
    """Layer 3: Check that produces/consumes references resolve."""
    errors = []

    all_keys = set(seeds.keys())

    for key, path in sorted(seeds.items()):
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except Exception:
            continue

        if not isinstance(data, dict):
            continue

        # Check produces consumers
        for prod in data.get("produces", []) or []:
            if not isinstance(prod, dict):
                continue
            for consumer in prod.get("consumers", []) or []:
                if not isinstance(consumer, str):
                    continue
                # Skip organ-level references (not specific repos)
                if "/" not in consumer:
                    continue
                if consumer not in all_keys:
                    errors.append(
                        f"{key}: produces.consumers references '{consumer}' "
                        f"which has no seed.yaml"
                    )

        # Check consumes sources
        for cons in data.get("consumes", []) or []:
            if not isinstance(cons, dict):
                continue
            source = cons.get("source", "")
            # Skip generic sources like "META-ORGANVM", "ORGAN-IV"
            if "/" in source and source not in all_keys:
                errors.append(
                    f"{key}: consumes.source references '{source}' "
                    f"which has no seed.yaml"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate all seed.yaml files")
    parser.add_argument("--registry", default=str(
        _engine_registry_path() if _HAS_ENGINE else REGISTRY_PATH
    ))
    parser.add_argument("--workspace", default=str(WORKSPACE))
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    workspace = Path(args.workspace)

    if _HAS_ENGINE:
        # Use engine's canonical seed discovery (returns list of Paths)
        seed_paths = _engine_discover_seeds(workspace=workspace)
        seeds = {}
        for p in seed_paths:
            # Reconstruct org/repo key from path structure
            repo_dir = p.parent
            org_dir = repo_dir.parent
            key = f"{org_dir.name}/{repo_dir.name}"
            seeds[key] = p
    else:
        seeds = discover_seeds(workspace)

    registry = load_registry(Path(args.registry))

    schema_errors: list[str] = []
    registry_errors: list[str] = []

    for key, path in sorted(seeds.items()):
        schema_errors.extend(validate_schema(path, key))
        registry_errors.extend(validate_registry_agreement(path, key, registry))

    graph_errors = validate_graph_integrity(seeds)

    total_errors = len(schema_errors) + len(registry_errors) + len(graph_errors)
    valid_count = len(seeds) - len({e.split(":")[0] for e in schema_errors})

    if args.json:
        result = {
            "total_seeds": len(seeds),
            "valid_seeds": valid_count,
            "registry_entries": len(registry),
            "schema_errors": schema_errors,
            "registry_errors": registry_errors,
            "graph_errors": graph_errors,
            "total_errors": total_errors,
        }
        print(json.dumps(result, indent=2))
    else:
        print("Seed Validation Report")
        print("=" * 60)
        print(f"Seeds discovered:   {len(seeds)}")
        print(f"Registry entries:   {len(registry)}")
        print(f"Schema valid:       {valid_count}/{len(seeds)}")
        print()

        if schema_errors:
            print(f"Schema errors ({len(schema_errors)}):")
            for e in schema_errors:
                print(f"  {e}")
            print()

        if registry_errors:
            print(f"Registry agreement errors ({len(registry_errors)}):")
            for e in registry_errors:
                print(f"  {e}")
            print()

        if graph_errors:
            print(f"Graph integrity errors ({len(graph_errors)}):")
            for e in graph_errors:
                print(f"  {e}")
            print()

        if total_errors == 0:
            print("All seeds valid.")
        else:
            print(f"Total errors: {total_errors}")

    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
