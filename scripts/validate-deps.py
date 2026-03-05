#!/usr/bin/env python3
"""Dependency validation script for the eight-organ system.

Validates that all dependencies in registry.json respect the unidirectional
flow rules defined in governance-rules.json.

Usage:
    python3 scripts/validate-deps.py \
        --registry registry.json \
        --governance governance-rules.json
"""
import json
import sys
import argparse
from pathlib import Path


ORG_TO_ORGAN = {
    "organvm-i-theoria": "ORGAN-I",
    "organvm-ii-poiesis": "ORGAN-II",
    "organvm-iii-ergon": "ORGAN-III",
    "organvm-iv-taxis": "ORGAN-IV",
    "organvm-v-logos": "ORGAN-V",
    "organvm-vi-koinonia": "ORGAN-VI",
    "organvm-vii-kerygma": "ORGAN-VII",
    "meta-organvm": "META-ORGANVM",
}

WORKSPACE = Path.home() / "Workspace"
SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT_WORKSPACE = SCRIPT_DIR.parents[2]
DEFAULT_REGISTRY_CANDIDATES = (
    WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json",
    SCRIPT_WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json",
)


def resolve_default_registry() -> Path | None:
    """Return first existing canonical registry path, if available."""
    for candidate in DEFAULT_REGISTRY_CANDIDATES:
        if candidate.is_file():
            return candidate.resolve()
    return None


def load_registry(path: str, visited: set[Path] | None = None) -> dict:
    """Load registry with fallback to meta-organvm if needed."""
    visited = visited or set()
    requested_path = (Path.cwd() / path).resolve()
    resolved_path = requested_path

    if not requested_path.is_file():
        default_registry = resolve_default_registry()
        if default_registry is None:
            tried = ", ".join(str(p) for p in DEFAULT_REGISTRY_CANDIDATES)
            raise FileNotFoundError(
                f"Registry not found at {requested_path}; no canonical registry found in [{tried}]"
            )
        print(f"Registry {requested_path} not found. Falling back to {default_registry}")
        resolved_path = default_registry

    if resolved_path in visited:
        raise RuntimeError(f"Redirect loop detected while loading registry: {resolved_path}")
    visited.add(resolved_path)

    with resolved_path.open(encoding="utf-8") as f:
        data = json.load(f)

    # Check if this is a redirect file
    if "_redirect" in data and "organs" not in data:
        default_registry = resolve_default_registry()
        if default_registry is None:
            tried = ", ".join(str(p) for p in DEFAULT_REGISTRY_CANDIDATES)
            raise FileNotFoundError(
                f"Registry {resolved_path} is a redirect but no canonical registry found in [{tried}]"
            )
        if default_registry == resolved_path:
            raise FileNotFoundError(
                f"Registry {resolved_path} is a redirect and no alternate canonical registry is available"
            )
        print(f"Registry {resolved_path} is a redirect. Following to {default_registry}")
        return load_registry(str(default_registry), visited)

    return data


def validate(registry_path: str, governance_path: str) -> int:
    """Validate all dependencies. Returns count of violations."""
    registry = load_registry(registry_path)
    with open(governance_path) as f:
        governance = json.load(f)

    # In governance-rules.json, allowed dependencies are usually in a specific structure
    # We'll assume the structure is still valid or handle the key error
    try:
        allowed = governance["articles"]["II"]["allowed_dependencies"]
    except KeyError:
        print("Error: Could not find allowed_dependencies in governance rules.")
        return 1

    violations = []
    total_deps = 0

    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            deps = repo.get("dependencies", [])
            if not deps:
                continue

            source_organ = organ_id  # Use the organ ID from the registry structure

            for dep in deps:
                total_deps += 1
                # Handle both 'org/repo' and just 'repo' (internal organ dep)
                if "/" in dep:
                    dep_org = dep.split("/")[0]
                    dep_organ = ORG_TO_ORGAN.get(dep_org, "UNKNOWN")
                else:
                    dep_organ = source_organ

                # Same-organ deps are always allowed
                if dep_organ == source_organ:
                    continue

                allowed_targets = allowed.get(source_organ, [])
                if dep_organ not in allowed_targets:
                    violations.append({
                        "source": f"{source_organ}/{repo['name']}",
                        "target": dep,
                        "target_organ": dep_organ,
                        "rule": f"{source_organ} cannot depend on {dep_organ}",
                    })

    # Report
    print(f"Dependency Validation Report (Registry v{registry.get('version', 'unknown')})")
    print(f"{'=' * 50}")
    print(f"Total dependencies checked: {total_deps}")
    print(f"Violations found: {len(violations)}")
    print()

    if violations:
        print("VIOLATIONS:")
        for v in violations:
            print(f"  {v['source']} -> {v['target']}")
            print(f"    Rule: {v['rule']}")
        return len(violations)

    print("All dependencies valid. No violations detected.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate dependency directions")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--governance", required=True)
    args = parser.parse_args()

    violation_count = validate(args.registry, args.governance)
    sys.exit(1 if violation_count > 0 else 0)


if __name__ == "__main__":
    main()
