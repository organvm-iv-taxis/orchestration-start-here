"""CLI entry points for the outbound contribution engine.

Registers as subcommands under the `organvm` CLI:
    organvm contrib scan
    organvm contrib list
    organvm contrib approve <target>
    organvm contrib status
    organvm contrib monitor

Can also be registered without a prefix for standalone use via
``register_contrib_commands(subparsers, prefix="")``.
"""

from __future__ import annotations

import argparse
import sys


def register_contrib_commands(
    subparsers: argparse._SubParsersAction,
    prefix: str = "contrib-",
) -> None:
    """Register contrib subcommands.

    Args:
        subparsers: The subparsers action to register commands under.
        prefix: Prefix for command names. Defaults to ``"contrib-"`` for use
            under the ``organvm`` parent CLI. Pass ``""`` for standalone use.
    """

    # organvm contrib scan
    scan_parser = subparsers.add_parser(
        f"{prefix}scan",
        help="Scan for open-source contribution targets",
        description="Read application pipeline signals and GitHub data to find targets.",
    )
    scan_parser.add_argument(
        "--no-github", action="store_true", help="Skip GitHub API enrichment (offline mode)"
    )
    scan_parser.set_defaults(func=cmd_contrib_scan)

    # organvm contrib list
    list_parser = subparsers.add_parser(
        f"{prefix}list",
        help="List ranked contribution targets",
    )
    list_parser.add_argument("--status", type=str, help="Filter by status")
    list_parser.add_argument("--min-score", type=int, default=0, help="Minimum score threshold")
    list_parser.set_defaults(func=cmd_contrib_list)

    # organvm contrib approve
    approve_parser = subparsers.add_parser(
        f"{prefix}approve",
        help="Approve a target and initialize workspace",
    )
    approve_parser.add_argument("target", type=str, help="Target name (from contrib-list)")
    approve_parser.add_argument(
        "--skip-fork", action="store_true", help="Skip forking the target repo"
    )
    approve_parser.add_argument(
        "--skip-remote", action="store_true", help="Skip creating GitHub remote"
    )
    approve_parser.add_argument(
        "--skip-registry", action="store_true", help="Skip registry-v2.json update"
    )
    approve_parser.set_defaults(func=cmd_contrib_approve)

    # organvm contrib status
    status_parser = subparsers.add_parser(
        f"{prefix}status",
        help="Show status of all active contributions",
    )
    status_parser.set_defaults(func=cmd_contrib_status)

    # organvm contrib monitor
    monitor_parser = subparsers.add_parser(
        f"{prefix}monitor",
        help="Run one PR monitoring cycle",
    )
    monitor_parser.set_defaults(func=cmd_contrib_monitor)


def cmd_contrib_scan(args: argparse.Namespace) -> None:
    """Run the signal scanner."""
    from contrib_engine.scanner import save_targets, scan

    print("Scanning for contribution targets...")
    targets = scan(enrich_github=not args.no_github)
    path = save_targets(targets)
    print(f"\nFound {len(targets.targets)} targets:")
    for t in targets.ranked():
        print(f"  [{t.score:3d}] {t.name:<30s} {t.signal_type:<10s} {t.github or '(no repo)'}")
    print(f"\nSaved to {path}")


def cmd_contrib_list(args: argparse.Namespace) -> None:
    """List ranked targets."""
    from contrib_engine.scanner import load_targets

    targets = load_targets()
    if not targets.targets:
        print("No targets found. Run `organvm contrib-scan` first.")
        return

    filtered = targets.ranked()
    if args.status:
        filtered = [t for t in filtered if t.status == args.status]
    if args.min_score:
        filtered = [t for t in filtered if t.score >= args.min_score]

    print(f"{'Score':>5s}  {'Name':<30s}  {'Signal':<10s}  {'Status':<12s}  {'GitHub'}")
    print("-" * 90)
    for t in filtered:
        print(f"{t.score:5d}  {t.name:<30s}  {t.signal_type:<10s}  {t.status:<12s}  {t.github}")


def cmd_contrib_approve(args: argparse.Namespace) -> None:
    """Approve target and initialize workspace."""
    from contrib_engine.orchestrator import approve_and_initialize
    from contrib_engine.scanner import load_targets, save_targets

    targets = load_targets()
    target = targets.get_target(args.target)

    if not target:
        print(f"Target '{args.target}' not found. Available targets:")
        for t in targets.ranked():
            print(f"  {t.name}")
        sys.exit(1)

    print(f"Initializing workspace for {target.name} ({target.github})...")
    ws_path = approve_and_initialize(
        target,
        skip_fork=args.skip_fork,
        skip_remote=args.skip_remote,
        skip_registry=args.skip_registry,
    )
    save_targets(targets)  # Persist status change
    print(f"\nWorkspace created: {ws_path}")
    print(f"Next: cd {ws_path} && read CONTRIBUTION-PROMPT.md")


def cmd_contrib_status(args: argparse.Namespace) -> None:
    """Show status of all active contributions."""
    from contrib_engine.monitor import load_status

    index = load_status()
    if not index.contributions:
        print("No active contributions. Run `organvm contrib-monitor` to discover.")
        return

    print(f"{'Workspace':<35s}  {'Target':<25s}  {'PR':>5s}  {'State':<8s}  {'CI':<6s}  {'Next Action'}")
    print("-" * 110)
    for c in index.contributions:
        pr = str(c.pr_number or "-")
        state = (c.pr_state or "-").value if c.pr_state else "-"
        print(
            f"{c.workspace:<35s}  {c.target:<25s}  {pr:>5s}  {state:<8s}  "
            f"{c.last_ci or '-':<6s}  {c.next_action}"
        )


def cmd_contrib_monitor(args: argparse.Namespace) -> None:
    """Run one monitoring cycle."""
    from contrib_engine.monitor import run_monitoring_cycle

    print("Running monitoring cycle...")
    index = run_monitoring_cycle()
    print(f"\nMonitored {len(index.contributions)} contributions:")
    for c in index.contributions:
        action = c.next_action or "monitor"
        print(f"  {c.workspace}: {action}")
