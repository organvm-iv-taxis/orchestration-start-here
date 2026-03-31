"""CLI for the action ledger.

Registers as subcommands under a parent CLI or runs standalone.
"""

from __future__ import annotations

import argparse


def register_ledger_commands(
    subparsers: argparse._SubParsersAction,
    prefix: str = "",
) -> None:
    """Register action_ledger subcommands."""

    # --- record ---
    rec = subparsers.add_parser(
        f"{prefix}record",
        help="Record a semantic action",
    )
    rec.add_argument("--session", required=True, help="Session identifier (e.g., S42)")
    rec.add_argument("--verb", required=True, help="What was done (e.g., explored, designed, built)")
    rec.add_argument("--target", required=True, help="What it was done to/with")
    rec.add_argument("--context", default="", help="Why / surrounding intent")
    rec.add_argument(
        "--param", action="append", default=[],
        help="Parameter as key=value (repeatable, e.g., --param abstraction=0.7)",
    )
    rec.add_argument(
        "--produced", action="append", default=[],
        help="Produced artifact as type:ref (repeatable, e.g., --produced insight:'spectrum model is reusable')",
    )
    rec.add_argument(
        "--route", action="append", default=[],
        help="Route as kind:target[:amount] (repeatable, e.g., --route consumed:fieldwork.py)",
    )
    rec.set_defaults(func=_cmd_record)

    # --- show ---
    show = subparsers.add_parser(
        f"{prefix}show",
        help="Show recorded actions",
    )
    show.add_argument("--session", default="", help="Filter by session")
    show.add_argument("--verb", default="", help="Filter by verb")
    show.add_argument("--target", default="", help="Filter by target (substring)")
    show.add_argument("--routes", action="store_true", help="Show routes")
    show.set_defaults(func=_cmd_show)

    # --- sequence ---
    seq = subparsers.add_parser(
        f"{prefix}sequence",
        help="Sequence operations",
    )
    seq_sub = seq.add_subparsers(dest="seq_command")

    seq_show = seq_sub.add_parser("show", help="Show sequences")
    seq_show.add_argument("--session", default="", help="Filter by session")
    seq_show.set_defaults(func=_cmd_sequence_show)

    seq_close = seq_sub.add_parser("close", help="Close the active sequence")
    seq_close.add_argument("--session", required=True, help="Session identifier")
    seq_close.add_argument("--outcome", default="", help="Sequence outcome")
    seq_close.set_defaults(func=_cmd_sequence_close)

    seq_intent = seq_sub.add_parser("intent", help="Set intent on active sequence")
    seq_intent.add_argument("--session", required=True, help="Session identifier")
    seq_intent.add_argument("intent", help="The intent text")
    seq_intent.set_defaults(func=_cmd_sequence_intent)

    seq.set_defaults(func=lambda args: seq.print_help())

    # --- params ---
    params = subparsers.add_parser(
        f"{prefix}params",
        help="Show the parameter registry",
    )
    params.set_defaults(func=_cmd_params)


# ---------------------------------------------------------------------------
# Argument parsers
# ---------------------------------------------------------------------------

def _parse_params(raw: list[str]) -> dict[str, float | str]:
    """Parse --param key=value arguments into a dict."""
    result: dict[str, float | str] = {}
    for item in raw:
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        try:
            result[key.strip()] = float(val.strip())
        except ValueError:
            result[key.strip()] = val.strip()
    return result


def _parse_produced(raw: list[str]) -> list[dict[str, str]]:
    """Parse --produced type:ref arguments."""
    result = []
    for item in raw:
        if ":" not in item:
            continue
        ptype, ref = item.split(":", 1)
        result.append({"type": ptype.strip(), "ref": ref.strip()})
    return result


def _parse_routes(raw: list[str]) -> list[dict[str, str | float]]:
    """Parse --route kind:target[:amount] arguments."""
    result: list[dict[str, str | float]] = []
    for item in raw:
        parts = item.split(":", 2)
        if len(parts) < 2:
            continue
        route: dict[str, str | float] = {
            "kind": parts[0].strip(),
            "target": parts[1].strip(),
        }
        if len(parts) == 3:
            try:
                route["amount"] = float(parts[2].strip())
            except ValueError:
                pass
        result.append(route)
    return result


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------

def _cmd_record(args: argparse.Namespace) -> None:
    from action_ledger.ledger import (
        load_actions,
        load_param_registry,
        load_sequences,
        record,
        save_actions,
        save_param_registry,
        save_sequences,
    )

    actions = load_actions()
    sequences = load_sequences()
    registry = load_param_registry()

    params = _parse_params(args.param)
    produced = _parse_produced(args.produced)
    routes = _parse_routes(args.route)

    action = record(
        actions, sequences, registry,
        session=args.session,
        verb=args.verb,
        target=args.target,
        context=args.context,
        params=params,
        produced=produced,
        routes=routes,
    )

    save_actions(actions)
    save_sequences(sequences)
    save_param_registry(registry)

    param_str = " ".join(f"{k}={v}" for k, v in action.params.items()) if action.params else ""
    print(f"Recorded: {action.id} [{action.verb}] {action.target}")
    if param_str:
        print(f"  Params: {param_str}")
    print(f"  Sequence: {action.sequence_id}")


def _cmd_show(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_actions

    index = load_actions()
    actions = index.actions

    if args.session:
        actions = [a for a in actions if a.session == args.session]
    if args.verb:
        actions = [a for a in actions if a.verb == args.verb]
    if args.target:
        actions = [a for a in actions if args.target in a.target]

    if not actions:
        print("No actions found.")
        return

    print(f"{'ID':<28s}  {'Session':>7s}  {'Verb':<12s}  {'Target':<25s}  Context")
    print("-" * 100)
    for a in actions:
        ctx = a.context[:35] if a.context else ""
        print(f"{a.id:<28s}  {a.session:>7s}  {a.verb:<12s}  {a.target:<25s}  {ctx}")
        if args.routes and a.routes:
            for r in a.routes:
                print(f"  -> {r.kind.value}: {r.target} (amount={r.effective_amount():.1f})")


def _cmd_sequence_show(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_sequences

    index = load_sequences()
    sequences = index.sequences

    if args.session:
        sequences = [s for s in sequences if s.session == args.session]

    if not sequences:
        print("No sequences found.")
        return

    for s in sequences:
        status = "OPEN" if not s.closed else "CLOSED"
        print(f"{s.id} [{status}] {s.intent or '(no intent)'}")
        print(f"  Actions: {len(s.action_ids)}")
        if s.automation:
            print(f"  Automation lanes:")
            for axis, values in s.automation.items():
                trajectory = " -> ".join(f"{v:.1f}" for v in values)
                print(f"    {axis}: {trajectory}")
        if s.outcome:
            print(f"  Outcome: {s.outcome}")
        print()


def _cmd_sequence_close(args: argparse.Namespace) -> None:
    from action_ledger.ledger import close_sequence, load_sequences, save_sequences

    index = load_sequences()
    seq = close_sequence(index, args.session, outcome=args.outcome)
    if seq:
        save_sequences(index)
        print(f"Closed: {seq.id}")
    else:
        print(f"No active sequence for session {args.session}")


def _cmd_sequence_intent(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_sequences, save_sequences, set_sequence_intent

    index = load_sequences()
    seq = set_sequence_intent(index, args.session, args.intent)
    if seq:
        save_sequences(index)
        print(f"Intent set on {seq.id}: {args.intent}")
    else:
        print(f"No active sequence for session {args.session}")


def _cmd_params(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_param_registry

    registry = load_param_registry()

    if not registry.axes:
        print("No parameter axes registered yet.")
        return

    print(f"{'Axis':<25s}  {'Range':<15s}  {'Freq':>5s}  {'First Seen':<12s}  Description")
    print("-" * 90)
    for name, axis in sorted(registry.axes.items(), key=lambda x: -x[1].frequency):
        rng = f"[{axis.range[0]:.1f}, {axis.range[1]:.1f}]"
        print(f"{name:<25s}  {rng:<15s}  {axis.frequency:>5d}  {axis.first_seen:<12s}  {axis.description}")
