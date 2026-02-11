#!/usr/bin/env python3
"""Monthly organ audit script for the eight-organ system.

Reads registry.json and governance-rules.json, validates system health,
and produces a markdown audit report.

Usage:
    python3 scripts/organ-audit.py \
        --registry registry.json \
        --governance governance-rules.json \
        --output audit-report.md
"""
import json
import sys
import argparse
from datetime import datetime


def find_cycles(graph: dict) -> list:
    """Detect circular dependencies using DFS."""
    visited = set()
    path = set()
    cycles = []

    def dfs(node, current_path):
        if node in path:
            cycle_start = list(current_path)
            idx = cycle_start.index(node)
            cycles.append(cycle_start[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.add(node)
        current_path.append(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor, current_path)
        path.remove(node)
        current_path.pop()

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles


def validate_dependency_directions(registry: dict, governance: dict) -> list:
    """Check that all dependencies respect unidirectional flow."""
    allowed = governance.get("articles", {}).get("II", {}).get("allowed_dependencies", {})

    org_to_organ = {
        "organvm-i-theoria": "ORGAN-I",
        "organvm-ii-poiesis": "ORGAN-II",
        "organvm-iii-ergon": "ORGAN-III",
        "organvm-iv-taxis": "ORGAN-IV",
        "organvm-v-logos": "ORGAN-V",
        "organvm-vi-koinonia": "ORGAN-VI",
        "organvm-vii-kerygma": "ORGAN-VII",
    }

    violations = []
    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            repo_org = repo.get("org", "")
            source_organ = org_to_organ.get(repo_org, organ_id)
            for dep in repo.get("dependencies", []):
                dep_org = dep.split("/")[0] if "/" in dep else ""
                dep_organ = org_to_organ.get(dep_org, "UNKNOWN")
                if dep_organ != source_organ:
                    allowed_targets = allowed.get(source_organ, [])
                    if dep_organ not in allowed_targets:
                        violations.append(
                            f"{source_organ}/{repo['name']} -> {dep_organ} "
                            f"(depends on {dep})"
                        )
    return violations


def audit_organs(registry_path: str, governance_path: str) -> tuple:
    """Run comprehensive system audit."""
    with open(registry_path) as f:
        registry = json.load(f)
    with open(governance_path) as f:
        governance = json.load(f)

    report = []
    alerts = {"critical": [], "warning": [], "info": []}
    metrics = {
        "date": datetime.now().isoformat(),
        "total_repos": 0,
        "documented_repos": 0,
        "empty_deps": 0,
        "dependency_violations": 0,
        "organs_operational": 0,
    }

    report.append("## Organ Status\n")

    for organ_id in [
        "ORGAN-I", "ORGAN-II", "ORGAN-III", "ORGAN-IV",
        "ORGAN-V", "ORGAN-VI", "ORGAN-VII",
    ]:
        organ = registry.get("organs", {}).get(organ_id, {})
        repos = organ.get("repositories", [])
        repo_count = len(repos)
        metrics["total_repos"] += repo_count

        documented = sum(
            1 for r in repos
            if r.get("documentation_status", "") in ("DEPLOYED", "FLAGSHIP README DEPLOYED")
        )
        metrics["documented_repos"] += documented

        empty_deps = sum(1 for r in repos if not r.get("dependencies"))
        metrics["empty_deps"] += empty_deps

        status = organ.get("launch_status", "UNKNOWN")
        if "COMPLETE" in str(status):
            metrics["organs_operational"] += 1

        report.append(f"### {organ_id}: {organ.get('name', 'Unknown')}\n")
        report.append(f"- **Status:** {status}")
        report.append(f"- **Repos:** {repo_count} ({documented} documented)")
        report.append(f"- **Repos with dependencies:** {repo_count - empty_deps}/{repo_count}")
        report.append("")

        # Check for repos without documentation
        undocumented = [
            r["name"] for r in repos
            if r.get("documentation_status", "") not in (
                "DEPLOYED", "FLAGSHIP README DEPLOYED", "INFRASTRUCTURE"
            )
            and "NOT_CREATED" not in r.get("note", "")
        ]
        if undocumented:
            alerts["warning"].append(
                f"{organ_id}: {len(undocumented)} repos not fully documented: "
                + ", ".join(undocumented[:5])
            )

    # Dependency validation
    report.append("\n## Dependency Validation\n")

    # Build dependency graph for cycle detection
    dep_graph = {}
    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            full_name = f"{repo.get('org', '')}/{repo['name']}"
            dep_graph[full_name] = repo.get("dependencies", [])

    cycles = find_cycles(dep_graph)
    if cycles:
        for cycle in cycles:
            alerts["critical"].append(f"Circular dependency: {' -> '.join(cycle)}")
        report.append(f"- **Circular dependencies:** {len(cycles)} FOUND")
    else:
        report.append("- **Circular dependencies:** None detected")

    # Direction violations
    violations = validate_dependency_directions(registry, governance)
    metrics["dependency_violations"] = len(violations)
    if violations:
        for v in violations:
            alerts["critical"].append(f"Direction violation: {v}")
        report.append(f"- **Direction violations:** {len(violations)} FOUND")
    else:
        report.append("- **Direction violations:** None")

    # Alerts summary
    report.append("\n## Alerts\n")
    if alerts["critical"]:
        report.append(f"### Critical ({len(alerts['critical'])})\n")
        for a in alerts["critical"]:
            report.append(f"- {a}")
    if alerts["warning"]:
        report.append(f"\n### Warnings ({len(alerts['warning'])})\n")
        for a in alerts["warning"]:
            report.append(f"- {a}")
    if not alerts["critical"] and not alerts["warning"]:
        report.append("No critical alerts or warnings.\n")

    # Metrics summary
    report.append("\n## Metrics\n")
    report.append(f"- **Total repos:** {metrics['total_repos']}")
    report.append(f"- **Documented repos:** {metrics['documented_repos']}")
    report.append(f"- **Organs operational:** {metrics['organs_operational']}/7")
    report.append(f"- **Dependency violations:** {metrics['dependency_violations']}")

    return "\n".join(report), alerts


def main():
    parser = argparse.ArgumentParser(description="Monthly organ audit")
    parser.add_argument("--registry", required=True, help="Path to registry.json")
    parser.add_argument("--governance", required=True, help="Path to governance-rules.json")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    report, alerts = audit_organs(args.registry, args.governance)

    with open(args.output, "w") as f:
        f.write(report)

    print(f"Audit complete. Report written to {args.output}")
    print(f"  Critical: {len(alerts['critical'])}")
    print(f"  Warnings: {len(alerts['warning'])}")

    sys.exit(1 if alerts["critical"] else 0)


if __name__ == "__main__":
    main()
