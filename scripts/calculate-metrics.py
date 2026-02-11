#!/usr/bin/env python3
"""Calculate system-wide metrics from registry.json.

Produces a metrics.json file with health indicators for the monthly audit.

Usage:
    python3 scripts/calculate-metrics.py \
        --registry registry.json \
        --output metrics.json
"""
import json
import sys
import argparse
from datetime import datetime


def calculate_metrics(registry_path: str) -> dict:
    """Calculate system-wide metrics from registry."""
    with open(registry_path) as f:
        registry = json.load(f)

    metrics = {
        "date": datetime.now().isoformat(),
        "total_repos": 0,
        "repos_on_github": 0,
        "repos_planned": 0,
        "documented_repos": 0,
        "flagship_repos": 0,
        "operational_organs": 0,
        "total_organs": 0,
        "total_dependencies": 0,
        "repos_with_dependencies": 0,
        "critical_alerts": 0,
        "warnings": 0,
        "completion": 0.0,
        "organs": {},
    }

    organ_ids = [
        "ORGAN-I", "ORGAN-II", "ORGAN-III", "ORGAN-IV",
        "ORGAN-V", "ORGAN-VI", "ORGAN-VII", "META-ORGANVM",
    ]

    for organ_id in organ_ids:
        organ = registry.get("organs", {}).get(organ_id, {})
        if not organ:
            continue

        metrics["total_organs"] += 1
        repos = organ.get("repositories", [])
        repo_count = len(repos)
        metrics["total_repos"] += repo_count

        on_gh = sum(1 for r in repos if "NOT_CREATED" not in r.get("note", ""))
        planned = sum(1 for r in repos if "NOT_CREATED" in r.get("note", ""))
        metrics["repos_on_github"] += on_gh
        metrics["repos_planned"] += planned

        documented = sum(
            1 for r in repos
            if r.get("documentation_status", "") in (
                "DEPLOYED", "FLAGSHIP README DEPLOYED", "ARCHIVED — README DEPLOYED"
            )
        )
        metrics["documented_repos"] += documented

        flagships = sum(1 for r in repos if r.get("tier") == "flagship")
        metrics["flagship_repos"] += flagships

        with_deps = sum(1 for r in repos if r.get("dependencies"))
        dep_count = sum(len(r.get("dependencies", [])) for r in repos)
        metrics["repos_with_dependencies"] += with_deps
        metrics["total_dependencies"] += dep_count

        status = organ.get("launch_status", "")
        is_operational = status in ("LOCKED", "COMPLETE", "OPERATIONAL")
        if is_operational:
            metrics["operational_organs"] += 1

        metrics["organs"][organ_id] = {
            "name": organ.get("name", ""),
            "status": status,
            "repos": repo_count,
            "on_github": on_gh,
            "documented": documented,
            "flagships": flagships,
            "dependencies": dep_count,
        }

    # Overall completion percentage
    if metrics["repos_on_github"] > 0:
        metrics["completion"] = round(
            (metrics["documented_repos"] / metrics["repos_on_github"]) * 100, 1
        )

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Calculate system metrics")
    parser.add_argument("--registry", required=True, help="Path to registry.json")
    parser.add_argument("--output", required=True, help="Output JSON file")
    args = parser.parse_args()

    metrics = calculate_metrics(args.registry)

    with open(args.output, "w") as f:
        json.dump(metrics, f, indent=2)
        f.write("\n")

    print(f"Metrics calculated:")
    print(f"  Total repos: {metrics['total_repos']}")
    print(f"  On GitHub: {metrics['repos_on_github']}")
    print(f"  Documented: {metrics['documented_repos']}")
    print(f"  Flagships: {metrics['flagship_repos']}")
    print(f"  Operational organs: {metrics['operational_organs']}/{metrics['total_organs']}")
    print(f"  Completion: {metrics['completion']}%")
    print(f"  Dependencies: {metrics['total_dependencies']}")


if __name__ == "__main__":
    main()
