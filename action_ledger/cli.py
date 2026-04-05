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
    show.add_argument("--origin", default="", help="Filter by origin (manual, emitted)")
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

    # --- chain ---
    chain_cmd = subparsers.add_parser(
        f"{prefix}chain",
        help="Chain operations",
    )
    chain_sub = chain_cmd.add_subparsers(dest="chain_command")

    chain_show = chain_sub.add_parser("show", help="Show chains")
    chain_show.add_argument("--session", default="", help="Filter by session")
    chain_show.set_defaults(func=_cmd_chain_show)

    chain_close = chain_sub.add_parser("close-session", help="Close session and compose chain")
    chain_close.add_argument("--session", required=True, help="Session identifier")
    chain_close.add_argument("--essence", default="", help="Prompt essence for the chain")
    chain_close.add_argument("--artifact", action="append", default=[], help="Produced artifact path (repeatable)")
    chain_close.set_defaults(func=_cmd_chain_close_session)

    chain_cmd.set_defaults(func=lambda args: chain_cmd.print_help())

    # --- routes ---
    routes_cmd = subparsers.add_parser(
        f"{prefix}routes",
        help="Route graph operations",
    )
    routes_sub = routes_cmd.add_subparsers(dest="routes_command")

    routes_from = routes_sub.add_parser("from", help="Show routes FROM an action")
    routes_from.add_argument("action_id", help="Action ID")
    routes_from.set_defaults(func=_cmd_routes_from)

    routes_to = routes_sub.add_parser("to", help="Show routes TO a target")
    routes_to.add_argument("target", help="Target (action ID, file path, URI)")
    routes_to.set_defaults(func=_cmd_routes_to)

    routes_lineage = routes_sub.add_parser("lineage", help="Trace causal lineage of an action")
    routes_lineage.add_argument("action_id", help="Action ID")
    routes_lineage.add_argument("--depth", type=int, default=3, help="Max traversal depth")
    routes_lineage.set_defaults(func=_cmd_routes_lineage)

    routes_cmd.set_defaults(func=lambda args: routes_cmd.print_help())

    # --- cycles ---
    cycles_cmd = subparsers.add_parser(
        f"{prefix}cycles",
        help="Detect repeated cycles across sessions",
    )
    cycles_cmd.add_argument("--min-recurrence", type=int, default=2, help="Minimum occurrences to report")
    cycles_cmd.add_argument("--verb-window", type=int, default=3, help="Verb n-gram window size")
    cycles_cmd.add_argument("--type", default="", help="Filter by cycle type (verb_sequence, trajectory, intent, stall)")
    cycles_cmd.set_defaults(func=_cmd_cycles)

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
    if args.origin:
        actions = [a for a in actions if a.origin == args.origin]

    if not actions:
        print("No actions found.")
        return

    print(f"{'ID':<28s}  {'Session':>7s}  {'Verb':<12s}  {'Target':<25s}  {'Origin':<8s}  Context")
    print("-" * 110)
    for a in actions:
        ctx = a.context[:35] if a.context else ""
        print(f"{a.id:<28s}  {a.session:>7s}  {a.verb:<12s}  {a.target:<25s}  {a.origin:<8s}  {ctx}")
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
            print("  Automation lanes:")
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


def _cmd_chain_show(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_chains

    index = load_chains()
    chains = index.chains

    if args.session:
        chains = [c for c in chains if c.session == args.session]

    if not chains:
        print("No chains found.")
        return

    for c in chains:
        print(f"{c.id} [{c.session}] {c.prompt_essence or '(no essence)'}")
        print(f"  Sequences: {len(c.sequence_ids)}")
        if c.arc:
            print("  Arc:")
            for axis, trajectory in c.arc.items():
                print(f"    {axis}: {trajectory}")
        if c.produced_artifacts:
            print(f"  Artifacts: {', '.join(c.produced_artifacts)}")
        print()


def _cmd_chain_close_session(args: argparse.Namespace) -> None:
    from action_ledger.ledger import (
        close_session,
        emit_session_closed,
        load_chains,
        load_sequences,
        save_chains,
        save_sequences,
    )

    sequences = load_sequences()
    chains = load_chains()

    chain = close_session(
        sequences, chains, args.session,
        prompt_essence=args.essence,
        produced_artifacts=args.artifact,
    )

    if chain:
        # Persist BEFORE emitting — avoids stale-read race in emit_state_change
        save_sequences(sequences)
        save_chains(chains)
        emit_session_closed(args.session, chain)
        print(f"Session closed: {chain.id}")
        if chain.arc:
            for axis, trajectory in chain.arc.items():
                print(f"  {axis}: {trajectory}")
    else:
        print(f"No sequences found for session {args.session}")


def _cmd_routes_from(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_actions
    from action_ledger.routes import build_route_graph, routes_from

    graph = build_route_graph(load_actions())
    resolved = routes_from(graph, args.action_id)
    if not resolved:
        print(f"No routes from {args.action_id}")
        return
    for r in resolved:
        print(f"  -> {r.kind}: {r.target} (amount={r.amount:.1f})")


def _cmd_routes_to(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_actions
    from action_ledger.routes import build_route_graph, routes_to

    graph = build_route_graph(load_actions())
    resolved = routes_to(graph, args.target)
    if not resolved:
        print(f"No routes to {args.target}")
        return
    for r in resolved:
        print(f"  <- {r.kind}: from {r.source_id} (amount={r.amount:.1f})")


def _cmd_routes_lineage(args: argparse.Namespace) -> None:
    from action_ledger.ledger import load_actions
    from action_ledger.routes import build_route_graph, trace_lineage

    graph = build_route_graph(load_actions())
    layers = trace_lineage(graph, args.action_id, depth=args.depth)
    if not layers:
        print(f"No lineage found for {args.action_id}")
        return
    for i, layer in enumerate(layers):
        print(f"Layer {i} (depth={i + 1}):")
        for r in layer:
            print(f"  <- {r.kind}: from {r.source_id} -> {r.target} (amount={r.amount:.1f})")


def _cmd_cycles(args: argparse.Namespace) -> None:
    from action_ledger.cycles import detect_all_cycles
    from action_ledger.ledger import load_actions, load_sequences

    actions = load_actions()
    sequences = load_sequences()

    cycles = detect_all_cycles(
        actions, sequences,
        min_recurrence=args.min_recurrence,
        verb_window=args.verb_window,
    )

    if args.type:
        cycles = [c for c in cycles if c.cycle_type == args.type]

    if not cycles:
        print("No cycles detected.")
        return

    for c in cycles:
        print(f"[{c.cycle_type.upper()}] x{c.recurrence} — {c.pattern}")
        print(f"  Sessions: {', '.join(c.sessions)}")
        if c.evidence:
            print(f"  Evidence: {', '.join(c.evidence[:5])}")
        print()


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
