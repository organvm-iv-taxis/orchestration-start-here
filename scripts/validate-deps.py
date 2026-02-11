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


ORG_TO_ORGAN = {
    "organvm-i-theoria": "ORGAN-I",
    "organvm-ii-poiesis": "ORGAN-II",
    "organvm-iii-ergon": "ORGAN-III",
    "organvm-iv-taxis": "ORGAN-IV",
    "organvm-v-logos": "ORGAN-V",
    "organvm-vi-koinonia": "ORGAN-VI",
    "organvm-vii-kerygma": "ORGAN-VII",
}


def validate(registry_path: str, governance_path: str) -> int:
    """Validate all dependencies. Returns count of violations."""
    with open(registry_path) as f:
        registry = json.load(f)
    with open(governance_path) as f:
        governance = json.load(f)

    allowed = governance["articles"]["II"]["allowed_dependencies"]
    violations = []
    total_deps = 0

    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            deps = repo.get("dependencies", [])
            if not deps:
                continue

            repo_org = repo.get("org", "")
            source_organ = ORG_TO_ORGAN.get(repo_org, organ_id)

            for dep in deps:
                total_deps += 1
                dep_org = dep.split("/")[0] if "/" in dep else ""
                dep_organ = ORG_TO_ORGAN.get(dep_org, "UNKNOWN")

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
    print(f"Dependency Validation Report")
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
