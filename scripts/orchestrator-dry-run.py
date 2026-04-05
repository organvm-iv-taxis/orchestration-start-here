#!/usr/bin/env python3
"""Local orchestrator dry-run: build system graph from seed.yaml files.

Discovers all seed.yaml across the workspace, builds a directed graph of
produces/consumes relationships, detects orphans and broken references,
and generates a Mermaid diagram.

Usage:
    python3 scripts/orchestrator-dry-run.py
    python3 scripts/orchestrator-dry-run.py --output seed-coverage.json
    python3 scripts/orchestrator-dry-run.py --mermaid graph.mmd
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

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


def discover_seeds(workspace: Path) -> dict[str, Path]:
    """Find all seed.yaml, keyed by org/repo."""
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
    """Load registry into {org/repo: entry} dict."""
    with open(path) as f:
        data = json.load(f)
    flat: dict[str, dict] = {}
    for organ_id, organ in data.get("organs", {}).items():
        for repo in organ.get("repositories", []):
            org = repo.get("org", "")
            name = repo.get("name", "")
            if org and name:
                repo["_organ_id"] = organ_id
                flat[f"{org}/{name}"] = repo
    return flat


def parse_seed(path: Path) -> dict | None:
    """Parse a seed.yaml, return None on error."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def build_graph(seeds: dict[str, Path]) -> dict:
    """Build the produces/consumes directed graph.

    Returns dict with nodes, edges, orphans, broken_refs, errors.
    """
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    errors: list[str] = []
    all_keys = set(seeds.keys())

    # Parse all seeds
    for key, path in sorted(seeds.items()):
        data = parse_seed(path)
        if data is None:
            errors.append(f"Parse error: {key}")
            continue
        org_name = key.split("/")[0]
        nodes[key] = {
            "organ": ORG_TO_ORGAN.get(org_name, "UNKNOWN"),
            "tier": data.get("metadata", {}).get("tier", ""),
            "promotion_status": data.get("metadata", {}).get("promotion_status", ""),
            "produces": data.get("produces", []) or [],
            "consumes": data.get("consumes", []) or [],
        }

    # Build edges from produces.consumers
    for key, node in nodes.items():
        for prod in node["produces"]:
            if not isinstance(prod, dict):
                continue
            ptype = prod.get("type", "unknown")
            for consumer in prod.get("consumers", []) or []:
                if not isinstance(consumer, str):
                    continue
                edges.append({"source": key, "target": consumer, "type": ptype})

    # Build edges from consumes.source (when it's a specific org/repo)
    for key, node in nodes.items():
        for cons in node["consumes"]:
            if not isinstance(cons, dict):
                continue
            source = cons.get("source", "")
            ctype = cons.get("type", "unknown")
            if "/" in source:
                edges.append({"source": source, "target": key, "type": ctype})

    # Detect orphans (no produces and no consumes)
    nodes_with_edges = set()
    for e in edges:
        nodes_with_edges.add(e["source"])
        nodes_with_edges.add(e["target"])
    orphans = [k for k in nodes if k not in nodes_with_edges]

    # Detect broken references
    broken_refs = []
    for e in edges:
        if e["source"] not in all_keys and "/" in e["source"]:
            broken_refs.append(f"Source '{e['source']}' not found (referenced by {e['target']})")
        if e["target"] not in all_keys and "/" in e["target"]:
            broken_refs.append(f"Target '{e['target']}' not found (referenced by {e['source']})")

    return {
        "nodes": nodes,
        "edges": edges,
        "orphans": orphans,
        "broken_refs": broken_refs,
        "errors": errors,
    }


def generate_mermaid(graph: dict) -> str:
    """Generate Mermaid diagram from the graph."""
    lines = ["graph LR"]

    # Group nodes by organ for subgraphs
    by_organ: dict[str, list[str]] = defaultdict(list)
    for key, node in graph["nodes"].items():
        by_organ[node["organ"]].append(key)

    # Node ID sanitizer
    def node_id(key: str) -> str:
        return key.replace("/", "__").replace("-", "_").replace(".", "_")

    def short_name(key: str) -> str:
        return key.split("/", 1)[1] if "/" in key else key

    for organ in sorted(by_organ.keys()):
        repos = by_organ[organ]
        lines.append(f"  subgraph {organ}")
        for repo_key in sorted(repos):
            nid = node_id(repo_key)
            name = short_name(repo_key)
            lines.append(f"    {nid}[\"{name}\"]")
        lines.append("  end")

    # Edges
    for edge in graph["edges"]:
        src = node_id(edge["source"])
        tgt = node_id(edge["target"])
        etype = edge["type"]
        lines.append(f"  {src} -->|{etype}| {tgt}")

    return "\n".join(lines)


def organ_stats(graph: dict, registry: dict[str, dict]) -> dict:
    """Compute per-organ coverage stats."""
    stats: dict[str, dict] = {}

    for organ_id in sorted(set(ORG_TO_ORGAN.values())):
        organ_nodes = [k for k, n in graph["nodes"].items() if n["organ"] == organ_id]
        organ_registry = [k for k, r in registry.items() if r.get("_organ_id") == organ_id]

        stats[organ_id] = {
            "seeds_found": len(organ_nodes),
            "registry_entries": len(organ_registry),
            "coverage": f"{len(organ_nodes)}/{len(organ_registry)}" if organ_registry else "0/0",
        }

    return stats


def main():
    parser = argparse.ArgumentParser(description="Local orchestrator dry-run")
    parser.add_argument("--workspace", default=str(WORKSPACE))
    parser.add_argument("--registry", default=str(REGISTRY_PATH))
    parser.add_argument("--output", help="Write seed-coverage.json to this path")
    parser.add_argument("--mermaid", help="Write Mermaid diagram to this path")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    seeds = discover_seeds(workspace)
    registry = load_registry(Path(args.registry))
    graph = build_graph(seeds)
    stats = organ_stats(graph, registry)

    print("Orchestrator Dry-Run Report")
    print("=" * 60)
    print(f"Seeds discovered:    {len(seeds)}")
    print(f"Registry entries:    {len(registry)}")
    print(f"Graph nodes:         {len(graph['nodes'])}")
    print(f"Graph edges:         {len(graph['edges'])}")
    print(f"Orphan nodes:        {len(graph['orphans'])}")
    print(f"Broken references:   {len(graph['broken_refs'])}")
    print(f"Parse errors:        {len(graph['errors'])}")
    print()

    print("Per-Organ Coverage:")
    for organ_id, s in sorted(stats.items()):
        print(f"  {organ_id:15s} {s['coverage']:>7s} seeds")
    print()

    if graph["orphans"]:
        print(f"Orphan nodes ({len(graph['orphans'])}):")
        for o in sorted(graph["orphans"]):
            print(f"  {o}")
        print()

    if graph["broken_refs"]:
        print(f"Broken references ({len(graph['broken_refs'])}):")
        for b in graph["broken_refs"]:
            print(f"  {b}")
        print()

    if graph["errors"]:
        print(f"Errors ({len(graph['errors'])}):")
        for e in graph["errors"]:
            print(f"  {e}")
        print()

    # Generate Mermaid
    mermaid = generate_mermaid(graph)
    if args.mermaid:
        Path(args.mermaid).write_text(mermaid)
        print(f"Mermaid diagram written to {args.mermaid}")
    else:
        print("Mermaid Diagram:")
        print("-" * 40)
        print(mermaid)

    # Write coverage JSON
    if args.output:
        coverage = {
            "total_seeds": len(seeds),
            "total_registry": len(registry),
            "total_edges": len(graph["edges"]),
            "orphans": graph["orphans"],
            "broken_refs": graph["broken_refs"],
            "errors": graph["errors"],
            "per_organ": stats,
        }
        Path(args.output).write_text(json.dumps(coverage, indent=2))
        print(f"Coverage JSON written to {args.output}")

    has_issues = bool(graph["broken_refs"] or graph["errors"])
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
