"""Standalone CLI entry point for the contribution engine.

Usage:
    python -m contrib_engine scan [--no-github]
    python -m contrib_engine list [--status STATUS] [--min-score N]
    python -m contrib_engine approve TARGET [--skip-fork] [--skip-remote] [--skip-registry]
    python -m contrib_engine status
    python -m contrib_engine monitor
    python -m contrib_engine campaign {show,next,complete,plan}
    python -m contrib_engine outreach {show,log,check}
    python -m contrib_engine backflow {show,pending,add,deposit}
"""

from __future__ import annotations

import argparse
import sys

from contrib_engine.cli import register_contrib_commands


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="contrib_engine",
        description="ORGANVM Contribution Engine — The Plague Campaign",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Register existing commands with no prefix (standalone mode)
    register_contrib_commands(subparsers, prefix="")

    # Register new campaign commands
    _register_campaign_commands(subparsers)
    _register_outreach_commands(subparsers)
    _register_backflow_commands(subparsers)
    _register_fieldwork_commands(subparsers)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


def _register_campaign_commands(subparsers: argparse._SubParsersAction) -> None:
    campaign = subparsers.add_parser("campaign", help="Campaign sequencer")
    campaign_sub = campaign.add_subparsers(dest="campaign_command")

    show = campaign_sub.add_parser("show", help="Show campaign state + next actions")
    show.set_defaults(func=_cmd_campaign_show)

    nxt = campaign_sub.add_parser("next", help="Show single next action")
    nxt.set_defaults(func=_cmd_campaign_next)

    complete = campaign_sub.add_parser("complete", help="Mark action complete")
    complete.add_argument("action_id", help="Action ID to complete")
    complete.set_defaults(func=_cmd_campaign_complete)

    plan = campaign_sub.add_parser("plan", help="Generate action queue from workspace state")
    plan.set_defaults(func=_cmd_campaign_plan)

    campaign.set_defaults(func=lambda args: campaign.print_help())


def _register_outreach_commands(subparsers: argparse._SubParsersAction) -> None:
    outreach = subparsers.add_parser("outreach", help="Outreach tracker")
    outreach_sub = outreach.add_subparsers(dest="outreach_command")

    show = outreach_sub.add_parser("show", help="Show relationships")
    show.add_argument("workspace", nargs="?", help="Filter by workspace")
    show.set_defaults(func=_cmd_outreach_show)

    log = outreach_sub.add_parser("log", help="Log an outreach event")
    log.add_argument("workspace", help="Workspace name")
    log.add_argument("channel", help="Channel (github_issue, discord, email, ...)")
    log.add_argument("summary", help="Event summary")
    log.set_defaults(func=_cmd_outreach_log)

    check = outreach_sub.add_parser("check", help="Poll GitHub for new interactions")
    check.set_defaults(func=_cmd_outreach_check)

    outreach.set_defaults(func=lambda args: outreach.print_help())


def _register_backflow_commands(subparsers: argparse._SubParsersAction) -> None:
    backflow = subparsers.add_parser("backflow", help="Backflow pipeline")
    backflow_sub = backflow.add_subparsers(dest="backflow_command")

    show = backflow_sub.add_parser("show", help="Show backflow items by organ")
    show.set_defaults(func=_cmd_backflow_show)

    pending = backflow_sub.add_parser("pending", help="Show pending extractions")
    pending.set_defaults(func=_cmd_backflow_pending)

    add = backflow_sub.add_parser("add", help="Add a backflow item")
    add.add_argument("workspace", help="Workspace name")
    add.add_argument("organ", help="Target organ (I, II, III, V, VI, VII)")
    add.add_argument("backflow_type", help="Type (theory, generative, code, narrative, community, distribution)")
    add.add_argument("title", help="Item title")
    add.set_defaults(func=_cmd_backflow_add)

    deposit = backflow_sub.add_parser("deposit", help="Mark item as deposited")
    deposit.add_argument("index", type=int, help="Item index (0-based)")
    deposit.set_defaults(func=_cmd_backflow_deposit)

    backflow.set_defaults(func=lambda args: backflow.print_help())


# --- Command implementations (delegate to modules) ---


def _cmd_campaign_show(args: argparse.Namespace) -> None:
    from contrib_engine.campaign import load_campaign
    campaign = load_campaign()
    print(f"Campaign: {campaign.name} (started {campaign.started})")
    print(f"Targets: {len(campaign.targets)}")
    summary = campaign.phase_summary()
    for phase, count in summary.items():
        print(f"  {phase}: {count} pending")
    print("\nNext actions:")
    for a in campaign.next_actions():
        manual = " [MANUAL]" if a.manual else ""
        print(f"  [{a.priority}] {a.id}: {a.action}{manual}")


def _cmd_campaign_next(args: argparse.Namespace) -> None:
    from contrib_engine.campaign import load_campaign
    campaign = load_campaign()
    actions = campaign.next_actions(limit=1)
    if not actions:
        print("No pending actions. Campaign complete!")
        return
    a = actions[0]
    manual = " [MANUAL — requires human action]" if a.manual else ""
    print(f"{a.id}: {a.action}{manual}")
    print(f"  Workspace: {a.workspace}")
    print(f"  Phase: {a.phase}")
    print(f"  Priority: {a.priority}")


def _cmd_campaign_complete(args: argparse.Namespace) -> None:
    from contrib_engine.campaign import complete_action, load_campaign, save_campaign
    campaign = load_campaign()
    if complete_action(campaign, args.action_id):
        save_campaign(campaign)
        print(f"Completed: {args.action_id}")
    else:
        print(f"Action not found: {args.action_id}")
        sys.exit(1)


def _cmd_campaign_plan(args: argparse.Namespace) -> None:
    from contrib_engine.campaign import generate_campaign, save_campaign
    campaign = generate_campaign()
    save_campaign(campaign)
    print(f"Generated campaign with {len(campaign.actions)} actions")


def _cmd_outreach_show(args: argparse.Namespace) -> None:
    from contrib_engine.outreach import load_outreach
    index = load_outreach()
    for r in index.relationships:
        if args.workspace and r.workspace != args.workspace:
            continue
        score = r.relationship_score
        events = len(r.outreach_events)
        print(f"{r.workspace}: {r.target} (score: {score}, events: {events})")
        if args.workspace:
            for e in r.outreach_events:
                print(f"  [{e.date}] {e.channel} ({e.direction}): {e.summary}")


def _cmd_outreach_log(args: argparse.Namespace) -> None:
    from contrib_engine.outreach import load_outreach, log_event, save_outreach
    index = load_outreach()
    log_event(index, args.workspace, args.channel, args.summary)
    save_outreach(index)
    print(f"Logged: {args.channel} event for {args.workspace}")


def _cmd_outreach_check(args: argparse.Namespace) -> None:
    from contrib_engine.outreach import check_github_interactions, load_outreach, save_outreach
    index = load_outreach()
    changes = check_github_interactions(index)
    save_outreach(index)
    print(f"Checked {len(index.relationships)} relationships, {changes} new interactions")


def _cmd_backflow_show(args: argparse.Namespace) -> None:
    from contrib_engine.backflow import load_backflow
    index = load_backflow()
    by_organ: dict[str, list] = {}
    for item in index.items:
        by_organ.setdefault(item.organ, []).append(item)
    for organ, items in sorted(by_organ.items()):
        print(f"\nORGAN-{organ}:")
        for item in items:
            print(f"  [{item.status}] {item.workspace}: {item.title} ({item.backflow_type})")


def _cmd_backflow_pending(args: argparse.Namespace) -> None:
    from contrib_engine.backflow import load_backflow
    index = load_backflow()
    pending = index.pending_by_organ()
    if not pending:
        print("No pending backflow items.")
        return
    for organ, items in sorted(pending.items()):
        print(f"\nORGAN-{organ}: {len(items)} pending")
        for item in items:
            print(f"  {item.workspace}: {item.title}")


def _cmd_backflow_add(args: argparse.Namespace) -> None:
    from contrib_engine.backflow import add_item, load_backflow, save_backflow
    index = load_backflow()
    add_item(index, args.workspace, args.organ, args.backflow_type, args.title)
    save_backflow(index)
    print(f"Added backflow item: {args.title} -> ORGAN-{args.organ}")


def _cmd_backflow_deposit(args: argparse.Namespace) -> None:
    from contrib_engine.backflow import deposit_item, load_backflow, save_backflow
    index = load_backflow()
    if deposit_item(index, args.index):
        save_backflow(index)
        print(f"Deposited item {args.index}")
    else:
        print(f"Item index {args.index} not found")
        sys.exit(1)


def _register_fieldwork_commands(subparsers: argparse._SubParsersAction) -> None:
    fieldwork = subparsers.add_parser("fieldwork", help="Fieldwork intelligence")
    fieldwork_sub = fieldwork.add_subparsers(dest="fieldwork_command")

    rec = fieldwork_sub.add_parser("record", help="Record a process observation")
    rec.add_argument("--workspace", required=True, help="Workspace name (e.g., contrib--dbt-mcp)")
    rec.add_argument(
        "--category", required=True,
        help="Observation category (merge_protocol, review_culture, ci_architecture, "
             "repo_layout, tooling, contributor_experience, communication_style, "
             "governance, documentation, security_posture)",
    )
    rec.add_argument("--signal", required=True, help="What was observed (natural language)")
    rec.add_argument("--spectrum", required=True, type=int, help="Spectrum score (-2=AVOID to +2=ABSORB)")
    rec.add_argument(
        "--source", required=True,
        help="How observed (pr_submission, review_response, ci_run, "
             "repo_exploration, phase_transition, automated)",
    )
    rec.add_argument("--evidence", default="", help="Supporting detail")
    rec.add_argument("--strategic", action="append", default=[], help="Strategic tag (repeatable)")
    rec.add_argument("--scored-by", default="agent", help="Who scored (agent or orchestrator)")
    rec.set_defaults(func=_cmd_fieldwork_record)

    show = fieldwork_sub.add_parser("show", help="Show observations")
    show.add_argument("--workspace", default="", help="Filter by workspace")
    show.add_argument("--category", default="", help="Filter by category")
    show.add_argument("--min-spectrum", type=int, default=None, help="Minimum spectrum level")
    show.set_defaults(func=_cmd_fieldwork_show)

    fieldwork.set_defaults(func=lambda args: fieldwork.print_help())


def _cmd_fieldwork_record(args: argparse.Namespace) -> None:
    from contrib_engine.fieldwork import load_fieldwork, record, save_fieldwork

    index = load_fieldwork()
    obs = record(
        index,
        workspace=args.workspace,
        category=args.category,
        signal=args.signal,
        spectrum=args.spectrum,
        source=args.source,
        evidence=args.evidence,
        strategic=args.strategic,
        scored_by=args.scored_by,
    )
    save_fieldwork(index)
    print(f"Recorded: {obs.id} [{obs.spectrum.name}] {obs.signal[:60]}")


def _cmd_fieldwork_show(args: argparse.Namespace) -> None:
    from contrib_engine.fieldwork import load_fieldwork
    from contrib_engine.schemas import ObservationCategory, SpectrumLevel

    index = load_fieldwork()
    obs_list = index.observations

    if args.workspace:
        obs_list = [o for o in obs_list if o.workspace == args.workspace]
    if args.category:
        cat = ObservationCategory(args.category)
        obs_list = [o for o in obs_list if o.category == cat]
    if args.min_spectrum is not None:
        level = SpectrumLevel(args.min_spectrum)
        obs_list = [o for o in obs_list if o.spectrum >= level]

    if not obs_list:
        print("No observations found.")
        return

    print(f"{'ID':<28s}  {'Workspace':<25s}  {'Category':<22s}  {'Spec':>4s}  Signal")
    print("-" * 110)
    for o in obs_list:
        spec = f"{o.spectrum.value:+d}"
        print(f"{o.id:<28s}  {o.workspace:<25s}  {o.category.value:<22s}  {spec:>4s}  {o.signal[:40]}")


if __name__ == "__main__":
    main()
