#!/usr/bin/env python3
"""Monthly organ audit script for the eight-organ system.
# ISOTOPE DISSOLUTION: Gate circulatory--contribute G1

Reads registry.json and governance-rules.json, validates system health,
and produces a markdown audit report.

When organvm-engine is installed, delegates to the canonical
governance.audit.run_audit. Falls back to standalone implementation.

Utilizes dynamic environment variables (ORG_I...VII, ORGANVM_WORKSPACE_DIR)
for validation and context.
"""
import argparse
import json
import os
import sys
from datetime import datetime

# --- Canonical engine imports (isotope dissolution) ---
try:
    from organvm_engine.governance.audit import run_audit as _engine_run_audit
    from organvm_engine.governance.rules import load_governance_rules as _engine_load_rules
    from organvm_engine.registry.loader import load_registry as _engine_load_registry

    _HAS_ENGINE = True
except ImportError:
    _HAS_ENGINE = False


def get_organ_env_map():
    """Retrieve the organ org-name mapping from environment variables."""
    id_to_env = {
        "ORGAN-I": "ORG_I",
        "ORGAN-II": "ORG_II",
        "ORGAN-III": "ORG_III",
        "ORGAN-IV": "ORG_IV",
        "ORGAN-V": "ORG_V",
        "ORGAN-VI": "ORG_VI",
        "ORGAN-VII": "ORG_VII",
        "META-ORGANVM": "ORG_META"
    }

    mapping = {}
    for organ_id, env_var in id_to_env.items():
        val = os.environ.get(env_var)
        if val:
            mapping[organ_id] = val
    return mapping


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

    repo_to_organ = {}
    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            repo_to_organ[repo["name"]] = organ_id
            if "org" in repo:
                repo_to_organ[f"{repo['org']}/{repo['name']}"] = organ_id

    violations = []
    for organ_id, organ in registry.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            source_organ = organ_id
            for dep in repo.get("dependencies", []):
                dep_organ = repo_to_organ.get(dep, "UNKNOWN")

                if dep_organ == "UNKNOWN" and "/" in dep:
                    dep_name = dep.split("/")[-1]
                    dep_organ = repo_to_organ.get(dep_name, "UNKNOWN")

                if dep_organ != source_organ and dep_organ != "UNKNOWN":
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

    # Environment-based stats validation
    env_total_repos = os.environ.get("CONDUCTOR_TOTAL_REPOS")
    if env_total_repos:
        metrics["expected_total"] = int(env_total_repos)

    report.append("## Organ Status\n")

    env_map = get_organ_env_map()
    all_organs = sorted(registry.get("organs", {}).keys())

    for organ_id in all_organs:
        organ = registry.get("organs", {}).get(organ_id, {})
        repos = organ.get("repositories", [])
        repo_count = len(repos)
        metrics["total_repos"] += repo_count

        # Validate registry org vs environment org
        if organ_id in env_map:
            reg_org = None
            if repos:
                reg_org = repos[0].get("org")
            if reg_org and reg_org != env_map[organ_id]:
                alerts["warning"].append(
                    f"{organ_id} Org Mismatch: Registry has '{reg_org}', "
                    f"Env has '{env_map[organ_id]}'"
                )

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

    # Dependency graph
    report.append("\n## Dependency Validation\n")
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
    if "expected_total" in metrics and metrics["total_repos"] != metrics["expected_total"]:
        report.append(f"  - ⚠️ DISCREPANCY: Expected {metrics['expected_total']} from CONDUCTOR_TOTAL_REPOS")
        alerts["warning"].append(f"Repo count discrepancy: Registry={metrics['total_repos']}, Env={metrics['expected_total']}")

    report.append(f"- **Documented repos:** {metrics['documented_repos']}")
    report.append(f"- **Organs operational:** {metrics['organs_operational']}/7")
    report.append(f"- **Dependency violations:** {metrics['dependency_violations']}")

    return "\n".join(report), alerts


def _run_via_engine(registry_path: str, governance_path: str, output_path: str) -> int:
    """Run audit using canonical organvm-engine governance.audit."""
    registry = _engine_load_registry(registry_path)
    rules = _engine_load_rules(governance_path)
    result = _engine_run_audit(registry, rules)

    # Format engine result as markdown report
    lines = ["## Governance Audit Report (via organvm-engine)\n"]
    if result.critical:
        lines.append(f"### Critical ({len(result.critical)})\n")
        for item in result.critical:
            lines.append(f"- {item}")
    if result.warnings:
        lines.append(f"\n### Warnings ({len(result.warnings)})\n")
        for item in result.warnings:
            lines.append(f"- {item}")
    if result.info:
        lines.append(f"\n### Info ({len(result.info)})\n")
        for item in result.info:
            lines.append(f"- {item}")
    if not result.critical and not result.warnings:
        lines.append("No critical alerts or warnings.\n")

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)

    print(f"Audit complete (via organvm-engine). Report written to {output_path}")
    print(f"  Critical: {len(result.critical)}")
    print(f"  Warnings: {len(result.warnings)}")
    return 1 if result.critical else 0


def main():
    parser = argparse.ArgumentParser(description="Monthly organ audit")
    parser.add_argument("--registry", required=True, help="Path to registry.json")
    parser.add_argument("--governance", required=True, help="Path to governance-rules.json")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    if _HAS_ENGINE:
        exit_code = _run_via_engine(args.registry, args.governance, args.output)
        sys.exit(exit_code)

    report, alerts = audit_organs(args.registry, args.governance)

    with open(args.output, "w") as f:
        f.write(report)

    print(f"Audit complete (standalone fallback). Report written to {args.output}")
    print(f"  Critical: {len(alerts['critical'])}")
    print(f"  Warnings: {len(alerts['warning'])}")

    sys.exit(1 if alerts["critical"] else 0)


if __name__ == "__main__":
    main()
