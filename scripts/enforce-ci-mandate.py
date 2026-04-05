#!/usr/bin/env python3
"""Enforce the CI mandate across the eight-organ system.

Audits every repository listed in registry-v2.json for the presence 
of a valid CI workflow file. Produces a Maturity Report.

Utilizes dynamic environment variables (ORG_I...VII, ORGANVM_WORKSPACE_DIR)
to resolve paths and validate state.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Adjust search path to find local registry if needed
WORKSPACE_DEFAULT = Path.home() / "Workspace"
WORKSPACE = Path(os.environ.get("ORGANVM_WORKSPACE_DIR", str(WORKSPACE_DEFAULT)))

# Try relative path first for the current environment
REGISTRY_REL = Path("tool-interaction-design/.conductor/corpus-cache/registry-v2.json")

def get_submodule_mappings():
    """Parse .gitmodules to map GitHub URLs to local paths."""
    mappings = {}
    gitmodules = Path(".gitmodules")
    if not gitmodules.exists():
        return mappings

    content = gitmodules.read_text()

    # Simple parser for .gitmodules
    sections = re.findall(r'\[submodule "(.*?)"\](.*?)(?=\[submodule|$)', content, re.DOTALL)
    for name, body in sections:
        path_match = re.search(r'path\s*=\s*(.*)', body)
        url_match = re.search(r'url\s*=\s*(.*)', body)
        if path_match and url_match:
            path = path_match.group(1).strip()
            url = url_match.group(1).strip()
            slug_match = re.search(r'[:/]([^/:]+/[^/.]+)(\.git)?$', url)
            if slug_match:
                slug = slug_match.group(1)
                mappings[slug] = path
    return mappings

def audit_ci():
    registry_path = REGISTRY_REL
    if not registry_path.exists():
        # Fallback to absolute workspace path
        corpus_dir = os.environ.get("ORGANVM_CORPUS_DIR")
        if corpus_dir:
            registry_path = Path(corpus_dir) / "registry-v2.json"
        else:
            registry_path = WORKSPACE / "meta-organvm" / "organvm-corpvs-testamentvm" / "registry-v2.json"

    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path}")
        return None

    with open(registry_path) as f:
        registry = json.load(f)

    submodule_paths = get_submodule_mappings()

    report = {
        "summary": {"total": 0, "has_ci": 0, "missing_ci": 0},
        "by_organ": {}
    }

    # Internalization of environment-based stats
    env_total_repos = os.environ.get("CONDUCTOR_TOTAL_REPOS")
    if env_total_repos:
        report["summary"]["expected_total"] = int(env_total_repos)

    for organ_id, organ in registry.get("organs", {}).items():
        organ_stats = {"total": 0, "has_ci": 0, "missing_ci": 0, "repos": []}
        for repo in organ.get("repositories", []):
            org_name = repo.get("org")
            repo_name = repo.get("name")
            if not org_name or not repo_name:
                continue

            slug = f"{org_name}/{repo_name}"

            # Resolution Strategy:
            # 1. Check .gitmodules mapping
            # 2. Check current organ directory if matching
            # 3. Check sibling organ directories using WORKSPACE root

            if slug in submodule_paths:
                repo_path = Path(".") / submodule_paths[slug]
            elif org_name == "organvm-iv-taxis":
                repo_path = Path(".") / repo_name
            else:
                # Use environment-aware workspace root
                repo_path = WORKSPACE / org_name / repo_name

            # Special case for .github which might be org-dotgithub
            if repo_name == ".github" and not (repo_path / ".github" / "workflows").exists():
                if (Path(".") / "org-dotgithub" / ".github" / "workflows").exists():
                    repo_path = Path(".") / "org-dotgithub"

            ci_dir = repo_path / ".github" / "workflows"

            has_ci = False
            found_files = []
            if ci_dir.exists() and ci_dir.is_dir():
                found_files = [f.name for f in ci_dir.iterdir() if f.is_file() and (f.suffix in ('.yml', '.yaml'))]
                if found_files:
                    has_ci = True

            repo_entry = {
                "name": f"{org_name}/{repo_name}",
                "has_ci": has_ci,
                "workflows": found_files,
                "promotion_status": repo.get("promotion_status")
            }

            organ_stats["total"] += 1
            report["summary"]["total"] += 1
            if has_ci:
                organ_stats["has_ci"] += 1
                report["summary"]["has_ci"] += 1
            else:
                organ_stats["missing_ci"] += 1
                report["summary"]["missing_ci"] += 1

            organ_stats["repos"].append(repo_entry)

        report["by_organ"][organ_id] = organ_stats

    return report

def print_markdown_report(report):
    print("# CI Maturity Report")
    print(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n## Summary")
    print(f"- **Total Repositories:** {report['summary']['total']}")
    if "expected_total" in report["summary"]:
        if report["summary"]["total"] != report["summary"]["expected_total"]:
            print(f"  - ⚠️ DISCREPANCY: Expected {report['summary']['expected_total']} from CONDUCTOR_TOTAL_REPOS")

    print(f"- **With CI:** {report['summary']['has_ci']}")
    print(f"- **Missing CI:** {report['summary']['missing_ci']}")

    total = report['summary']['total']
    rate = (report['summary']['has_ci'] / total * 100) if total > 0 else 0
    print(f"- **Adherence Rate:** {rate:.1f}%")

    for organ_id in sorted(report["by_organ"].keys()):
        stats = report["by_organ"][organ_id]
        print(f"\n### {organ_id}")
        print(f"**Adherence:** {stats['has_ci']}/{stats['total']}")

        missing = [r['name'] for r in stats['repos'] if not r['has_ci']]
        if missing:
            print(f"**Missing CI ({len(missing)}):**")
            for m in missing:
                print(f"- {m}")
        else:
            print("✅ 100% Adherence")

if __name__ == "__main__":
    report = audit_ci()
    if report:
        print_markdown_report(report)
