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

    # organvm contrib absorb
    absorb_parser = subparsers.add_parser(
        f"{prefix}absorb",
        help="Scan conversations for expansion-worthy questions (Absorption Protocol)",
    )
    absorb_parser.add_argument(
        "--since", type=str, default="", help="Only scan comments after this ISO date"
    )
    absorb_parser.set_defaults(func=cmd_contrib_absorb)

    # organvm contrib absorb-pending
    absorb_pending_parser = subparsers.add_parser(
        f"{prefix}absorb-pending",
        help="Show questions awaiting formalization",
    )
    absorb_pending_parser.set_defaults(func=cmd_contrib_absorb_pending)

    # organvm contrib absorb-track
    absorb_track_parser = subparsers.add_parser(
        f"{prefix}absorb-track",
        help="Track a conversation for absorption scanning",
    )
    absorb_track_parser.add_argument("url", help="GitHub issue/PR URL to track")
    absorb_track_parser.add_argument("--workspace", type=str, default="", help="Workspace name")
    absorb_track_parser.add_argument("--label", type=str, default="", help="Label for this conversation")
    absorb_track_parser.set_defaults(func=cmd_contrib_absorb_track)

    # organvm contrib absorb-formalize
    absorb_formalize_parser = subparsers.add_parser(
        f"{prefix}absorb-formalize",
        help="Generate formalization prompt for a detected item",
    )
    absorb_formalize_parser.add_argument("item_id", nargs="?", help="Item ID (or shows all pending)")
    absorb_formalize_parser.set_defaults(func=cmd_contrib_absorb_formalize)


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


def cmd_contrib_absorb(args: argparse.Namespace) -> None:
    """Run absorption scan across all tracked conversations."""
    from contrib_engine.absorption import run_absorption_scan

    print("Running absorption scan...")
    index = run_absorption_scan(since=args.since)

    pending = index.pending_formalization()
    if pending:
        print(f"\n{len(pending)} items awaiting formalization:")
        for item in pending:
            triggers = ", ".join(t.value for t in item.triggers)
            print(f"  [{item.status.value:>10s}] @{item.questioner:<20s} [{triggers}]")
            print(f"             {item.question_text[:80]}...")
            print(f"             {item.source_url}")
    else:
        print("\nNo pending items. All quiet on the absorption front.")

    total = len(index.items)
    if total:
        by_status = {}
        for item in index.items:
            by_status[item.status.value] = by_status.get(item.status.value, 0) + 1
        counts = " | ".join(f"{k}: {v}" for k, v in sorted(by_status.items()))
        print(f"\nTotal: {total} ({counts})")


def cmd_contrib_absorb_pending(args: argparse.Namespace) -> None:
    """Show questions awaiting formalization."""
    from contrib_engine.absorption import load_absorption

    index = load_absorption()
    pending = index.pending_formalization()

    if not pending:
        print("No items awaiting formalization.")
        return

    for item in pending:
        triggers = ", ".join(t.value for t in item.triggers)
        print(f"\n{'=' * 70}")
        print(f"ID:         {item.id}")
        print(f"From:       @{item.questioner} ({item.workspace})")
        print(f"Triggers:   {triggers}")
        print(f"Evidence:   {item.trigger_evidence}")
        print(f"Source:     {item.source_url}")
        print(f"Detected:   {item.detected_at}")
        print("\nQuestion:")
        print(f"  {item.question_text}")
        print(f"{'=' * 70}")


def cmd_contrib_absorb_track(args: argparse.Namespace) -> None:
    """Track a conversation URL for absorption scanning."""
    import re

    from contrib_engine.absorption import add_tracked_conversation

    # Parse GitHub URL
    match = re.search(r"github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)", args.url)
    if not match:
        print(f"Could not parse GitHub URL: {args.url}")
        print("Expected format: https://github.com/owner/repo/issues/N")
        return

    owner, repo, issue_number = match.group(1), match.group(2), int(match.group(3))
    workspace = args.workspace or f"{owner}-{repo}"

    add_tracked_conversation(owner, repo, issue_number, workspace, args.label)
    print(f"Tracking: {owner}/{repo}#{issue_number} (workspace: {workspace})")


def cmd_contrib_absorb_formalize(args: argparse.Namespace) -> None:
    """Generate formalization prompt for a detected absorption item."""
    from contrib_engine.absorption import generate_formalization_prompt, load_absorption

    index = load_absorption()
    pending = index.pending_formalization()

    if not pending:
        print("No items awaiting formalization.")
        return

    if args.item_id:
        # Generate prompt for specific item
        item = next((i for i in pending if i.id == args.item_id), None)
        if not item:
            print(f"Item {args.item_id} not found in pending items.")
            return
        prompt = generate_formalization_prompt(item)
        print(prompt)
    else:
        # Show all pending with their IDs for selection
        print(f"{len(pending)} items awaiting formalization:\n")
        for item in pending:
            triggers = ", ".join(t.value for t in item.triggers)
            print(f"  {item.id}")
            print(f"    @{item.questioner}: {item.question_text[:80]}...")
            print(f"    Triggers: {triggers}")
            print()
        print("Run: python -m contrib_engine absorb-formalize <item_id>")
