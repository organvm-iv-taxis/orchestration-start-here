#!/usr/bin/env python3
"""Per-project alpha-to-omega progress bar.

Evaluates every repo against 11 contextually-adjusted gates (α→Ω).
Gates auto-adjust based on the detected project profile — infrastructure
repos skip TESTS/DEPLOY, documentation repos skip TESTS, stubs only check
early gates, etc.

Modes
-----
    Default             System heatmap + organ breakdowns
    --repo NAME         Single repo detail view
    --organ IV          Single organ summary
    --gate-stats        Gate pass-rate table
    --next-actions      Prioritized recommendations
    --blockers          Promotion blockers report
    --discrepancies     Registry/local mismatches
    --stale             Staleness report
    --snapshot          Save evaluation to timestamped JSON
    --compare A B       Delta between two snapshots

Filters
-------
    --profile X         Filter by profile (code-full, documentation, etc.)
    --tier X            Filter by tier (flagship, standard, etc.)
    --gate X            Only repos failing a specific gate
    --min-score N       Only repos scoring >= N%
    --max-score N       Only repos scoring <= N%
    --failing           Only repos with at least one failing gate
    --passing           Only repos at 100%
    --promo-ready       Only repos ready for next promotion

Output
------
    --json              Machine-readable JSON
    --export csv|md     Export format
    --color / --no-color  ANSI color (auto-detect by default)
    --sort score|organ|name|pct|stale  Sort order
    --verbose           More detail in summaries
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.progress import (
    GATE_NAMES,
    Profile,
    compute_delta,
    compute_gate_stats,
    compute_system_summary,
    evaluate_all,
    export_csv,
    export_markdown,
    list_snapshots,
    load_registry,
    load_snapshot,
    render_blockers,
    render_delta,
    render_detail,
    render_discrepancies,
    render_gate_stats,
    render_heatmap,
    render_next_actions,
    render_organ_summary,
    render_stale,
    save_snapshot,
)

_ORGAN_ALIASES: dict[str, str] = {
    "I": "ORGAN-I", "1": "ORGAN-I",
    "II": "ORGAN-II", "2": "ORGAN-II",
    "III": "ORGAN-III", "3": "ORGAN-III",
    "IV": "ORGAN-IV", "4": "ORGAN-IV",
    "V": "ORGAN-V", "5": "ORGAN-V",
    "VI": "ORGAN-VI", "6": "ORGAN-VI",
    "VII": "ORGAN-VII", "7": "ORGAN-VII",
    "META": "META-ORGANVM", "M": "META-ORGANVM",
}


def resolve_organ(raw: str) -> str:
    """Normalize organ argument to canonical ID."""
    upper = raw.upper().replace("-", "")
    if upper in _ORGAN_ALIASES:
        return _ORGAN_ALIASES[upper]
    for canonical in ("ORGAN-I", "ORGAN-II", "ORGAN-III", "ORGAN-IV",
                      "ORGAN-V", "ORGAN-VI", "ORGAN-VII", "META-ORGANVM"):
        if upper == canonical.replace("-", ""):
            return canonical
    return raw.upper()


def detect_color(args: argparse.Namespace) -> bool:
    """Determine whether to use ANSI colors."""
    if args.no_color:
        return False
    if args.color:
        return True
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Per-project alpha-to-omega progress bar with contextual gate awareness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Data sources ---
    parser.add_argument("--registry", required=True, type=Path, help="Path to registry-v2.json")
    parser.add_argument("--workspace", type=Path, default=None, help="Workspace root for local filesystem checks")

    # --- Display modes (mutually exclusive) ---
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--repo", type=str, help="Single repo detail view")
    modes.add_argument("--organ", type=str, help="Single organ summary (e.g., IV, ORGAN-IV, 4)")
    modes.add_argument("--gate-stats", action="store_true", help="Gate pass-rate table")
    modes.add_argument("--next-actions", action="store_true", help="Prioritized recommendations")
    modes.add_argument("--blockers", action="store_true", help="Promotion blockers report")
    modes.add_argument("--discrepancies", action="store_true", help="Registry/local mismatches")
    modes.add_argument("--stale", action="store_true", help="Staleness report")
    modes.add_argument("--snapshot", action="store_true", help="Save evaluation snapshot")
    modes.add_argument("--compare", nargs=2, metavar=("OLD", "NEW"), help="Compare two snapshots")

    # --- Filters ---
    parser.add_argument("--profile", type=str, choices=[p.value for p in Profile], help="Filter by profile")
    parser.add_argument("--tier", type=str, choices=["flagship", "standard", "infrastructure", "stub", "archive"], help="Filter by tier")
    parser.add_argument("--gate", type=str, choices=[g.lower() for g in GATE_NAMES], help="Only repos failing this gate")
    parser.add_argument("--min-score", type=int, metavar="N", help="Only repos scoring >= N%%")
    parser.add_argument("--max-score", type=int, metavar="N", help="Only repos scoring <= N%%")
    parser.add_argument("--failing", action="store_true", help="Only repos with failing gates")
    parser.add_argument("--passing", action="store_true", help="Only repos at 100%%")
    parser.add_argument("--promo-ready", action="store_true", help="Only repos ready for promotion")

    # --- Output ---
    parser.add_argument("--json", action="store_true", dest="json_output", help="Machine-readable JSON")
    parser.add_argument("--export", choices=["csv", "md"], help="Export format")
    parser.add_argument("--color", action="store_true", help="Force ANSI colors")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    parser.add_argument("--sort", choices=["score", "organ", "name", "pct", "stale"], default="organ", help="Sort order")
    parser.add_argument("--verbose", action="store_true", help="More detail in summaries")

    # --- Advanced ---
    parser.add_argument("--probe-git", action="store_true", help="Probe git health (slower)")
    parser.add_argument("--snapshot-dir", type=Path, default=None, help="Directory for snapshot files")
    parser.add_argument("--limit", type=int, default=20, help="Limit for list outputs")

    args = parser.parse_args()
    use_color = detect_color(args)

    if not args.registry.is_file():
        print(f"Error: registry not found at {args.registry}", file=sys.stderr)
        sys.exit(1)

    # --- Snapshot compare mode (no registry eval needed) ---
    if args.compare:
        old_path, new_path = Path(args.compare[0]), Path(args.compare[1])
        if not old_path.is_file() or not new_path.is_file():
            print("Error: both snapshot files must exist", file=sys.stderr)
            sys.exit(1)
        old_snap = load_snapshot(old_path)
        new_snap = load_snapshot(new_path)
        delta = compute_delta(old_snap, new_snap)
        if args.json_output:
            print(json.dumps(delta.to_dict(), indent=2))
        else:
            print(render_delta(delta, color=use_color))
        return

    # --- Load and evaluate ---
    registry = load_registry(args.registry)
    workspace = args.workspace.expanduser() if args.workspace else None
    all_projects = evaluate_all(registry, workspace, probe_git=args.probe_git)

    # --- Apply filters ---
    if args.profile:
        all_projects = [p for p in all_projects if p.profile.value == args.profile]
    if args.tier:
        all_projects = [p for p in all_projects if p.tier == args.tier]
    if args.gate:
        gate_upper = args.gate.upper()
        all_projects = [
            p for p in all_projects
            if any(c.name == gate_upper and c.applicable and not c.passed for c in p.checkpoints)
        ]
    if args.min_score is not None:
        all_projects = [p for p in all_projects if p.pct >= args.min_score]
    if args.max_score is not None:
        all_projects = [p for p in all_projects if p.pct <= args.max_score]
    if args.failing:
        all_projects = [p for p in all_projects if p.failures]
    if args.passing:
        all_projects = [p for p in all_projects if p.pct == 100]
    if args.promo_ready:
        all_projects = [p for p in all_projects if p.promotion_ready]

    if not all_projects:
        print("No repos match the given filters.", file=sys.stderr)
        sys.exit(0)

    # --- Apply sort ---
    if args.sort == "score":
        all_projects.sort(key=lambda p: (-p.pct, -p.score, p.repo))
    elif args.sort == "pct":
        all_projects.sort(key=lambda p: (-p.pct, p.repo))
    elif args.sort == "name":
        all_projects.sort(key=lambda p: p.repo)
    elif args.sort == "stale":
        all_projects.sort(key=lambda p: (-p.staleness_days, p.repo))

    # --- Export modes ---
    if args.export == "csv":
        print(export_csv(all_projects))
        return
    if args.export == "md":
        summary = compute_system_summary(all_projects)
        print(export_markdown(all_projects, summary))
        return

    # --- Snapshot mode ---
    if args.snapshot:
        summary = compute_system_summary(all_projects)
        snap_dir = args.snapshot_dir or (args.registry.parent / "snapshots")
        path = save_snapshot(all_projects, summary, snap_dir)
        print(f"Snapshot saved: {path}")
        snaps = list_snapshots(snap_dir)
        if len(snaps) > 1:
            print(f"  {len(snaps)} snapshots in {snap_dir}")
            print(f"  Compare: --compare {snaps[1]} {snaps[0]}")
        return

    # --- Single repo detail ---
    if args.repo:
        matches = [p for p in all_projects if p.repo == args.repo]
        if not matches:
            matches = [p for p in all_projects if args.repo.lower() in p.repo.lower()]
        if not matches:
            print(f"Error: repo '{args.repo}' not found", file=sys.stderr)
            sys.exit(1)
        for m in matches:
            if args.json_output:
                print(json.dumps(m.to_dict(), indent=2))
            else:
                print(render_detail(m, color=use_color))
                print()
        return

    # --- Gate stats mode ---
    if args.gate_stats:
        stats = compute_gate_stats(all_projects)
        if args.json_output:
            print(json.dumps([s.to_dict() for s in stats], indent=2))
        else:
            print(render_gate_stats(stats, color=use_color))
        return

    # --- Next actions mode ---
    if args.next_actions:
        if args.json_output:
            actions = []
            for p in all_projects:
                for cp in p.checkpoints:
                    if cp.applicable and not cp.passed and cp.next_action:
                        actions.append({"repo": p.repo, "organ": p.organ, "gate": cp.name, "action": cp.next_action})
            print(json.dumps(actions, indent=2))
        else:
            print(render_next_actions(all_projects, limit=args.limit))
        return

    # --- Blockers mode ---
    if args.blockers:
        if args.json_output:
            data = []
            for p in all_projects:
                if p.blockers and p.promotion_status not in ("GRADUATED", "ARCHIVED"):
                    data.append({"repo": p.repo, "organ": p.organ, "promo": p.promotion_status,
                                 "next": p.next_promotion, "ready": p.promotion_ready,
                                 "blockers": p.blockers})
            print(json.dumps(data, indent=2))
        else:
            print(render_blockers(all_projects, color=use_color))
        return

    # --- Discrepancies mode ---
    if args.discrepancies:
        if args.json_output:
            discs = []
            for p in all_projects:
                for cp in p.discrepancies:
                    discs.append({"repo": p.repo, "gate": cp.name, "discrepancy": cp.discrepancy})
            print(json.dumps(discs, indent=2))
        else:
            print(render_discrepancies(all_projects))
        return

    # --- Stale mode ---
    if args.stale:
        if args.json_output:
            stale_data = [
                {"repo": p.repo, "organ": p.organ, "days": p.staleness_days,
                 "critical": p.is_stale, "warning": p.is_warn_stale}
                for p in all_projects if p.is_stale or p.is_warn_stale
            ]
            print(json.dumps(stale_data, indent=2))
        else:
            print(render_stale(all_projects))
        return

    # --- Organ filter ---
    if args.organ:
        target = resolve_organ(args.organ)
        all_projects = [p for p in all_projects if p.organ == target]
        if not all_projects:
            print(f"Error: no repos found for organ '{args.organ}'", file=sys.stderr)
            sys.exit(1)

    # --- JSON output ---
    if args.json_output:
        summary = compute_system_summary(all_projects)
        output = {
            "summary": summary.to_dict(),
            "projects": [p.to_dict() for p in all_projects],
        }
        print(json.dumps(output, indent=2))
        return

    # --- Single organ summary ---
    if args.organ:
        organ_id = all_projects[0].organ
        organ_name = _organ_display_name(organ_id, registry)
        print(render_organ_summary(organ_id, organ_name, all_projects, color=use_color))
        if args.verbose:
            print()
            stats = compute_gate_stats(all_projects)
            print(render_gate_stats(stats, color=use_color))
        return

    # --- Default: system heatmap ---
    print(render_heatmap(all_projects, color=use_color))
    print()

    # Per-organ breakdowns
    organs: dict[str, list] = defaultdict(list)
    for p in all_projects:
        organs[p.organ].append(p)

    for organ_id in sorted(organs.keys()):
        projs = organs[organ_id]
        organ_name = _organ_display_name(organ_id, registry)
        print()
        print(render_organ_summary(organ_id, organ_name, projs, color=use_color))

    # Verbose: append gate stats and blockers
    if args.verbose:
        print()
        stats = compute_gate_stats(all_projects)
        print(render_gate_stats(stats, color=use_color))
        print()
        print(render_blockers(all_projects, color=use_color))
        print()
        print(render_stale(all_projects))


def _organ_display_name(organ_id: str, registry: dict) -> str:
    organ_data = registry.get("organs", {}).get(organ_id, {})
    return organ_data.get("name", organ_id)


if __name__ == "__main__":
    main()
