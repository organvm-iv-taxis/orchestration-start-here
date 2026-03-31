"""CLI for the intake router."""

from __future__ import annotations

import argparse
import sys

from intake_router.router import (
    IntakeDomain,
    classify,
    emit_routing,
    recent_dispatches,
    route,
    routing_table_rows,
)


def register_intake_router_commands(
    subparsers: argparse._SubParsersAction,
    prefix: str = "",
) -> None:
    """Register intake-router commands."""

    intake = subparsers.add_parser(f"{prefix}intake", help="Classify and route raw intake text")
    intake.add_argument("raw_text", help="Operator intake text")
    intake.set_defaults(func=_cmd_intake)

    table = subparsers.add_parser(f"{prefix}table", help="Show the routing table")
    table.set_defaults(func=_cmd_table)

    history = subparsers.add_parser(f"{prefix}history", help="Show recent routed dispatches")
    history.add_argument("--domain", choices=[domain.value for domain in IntakeDomain], default="")
    history.add_argument("--limit", type=int, default=10, help="Number of dispatches to show")
    history.set_defaults(func=_cmd_history)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="intake_router",
        description="Intake Router — classify, route, and emit operator intake",
    )
    subparsers = parser.add_subparsers(dest="command")
    register_intake_router_commands(subparsers, prefix="")

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


def _cmd_intake(args: argparse.Namespace) -> None:
    item = classify(args.raw_text)
    dispatch = route(item)
    emit_routing(dispatch)

    print(f"domain: {item.domain.value}")
    print(f"keywords: {', '.join(item.keywords) or 'none'}")
    print(f"tension: {item.tension:.2f}")
    print(f"archetype: {dispatch.archetype}")
    print(f"workspace: {dispatch.workspace or '—'}")
    print(f"agent: {dispatch.agent}")
    print(f"token_budget: {dispatch.token_budget}")
    print("\nprompt:\n")
    print(dispatch.prompt)


def _cmd_table(args: argparse.Namespace) -> None:
    rows = routing_table_rows()
    print(
        f"{'Domain':<16s} {'Archetype':<10s} {'Agent':<16s} "
        f"{'Budget':<8s} {'Workspace':<68s} Prompt"
    )
    print("-" * 140)
    for row in rows:
        print(
            f"{row['domain']:<16s} {row['archetype']:<10s} {row['agent']:<16s} "
            f"{row['token_budget']:<8s} {row['workspace']:<68s} {row['prompt']}"
        )


def _cmd_history(args: argparse.Namespace) -> None:
    domain = IntakeDomain(args.domain) if args.domain else None
    actions = recent_dispatches(domain=domain, limit=args.limit)
    if not actions:
        print("No routed dispatches found.")
        return

    print(f"{'When':<20s} {'Domain':<16s} {'Archetype':<10s} {'Agent':<16s} Workspace")
    print("-" * 110)
    for action in actions:
        print(
            f"{action.timestamp[:19]:<20s} "
            f"{str(action.params.get('domain', '')):<16s} "
            f"{str(action.params.get('archetype', '')):<10s} "
            f"{str(action.params.get('agent', '')):<16s} "
            f"{str(action.params.get('workspace', ''))}"
        )

