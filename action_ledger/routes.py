"""Patch bay — bidirectional route resolution and provenance injection.

Every route implies an inverse: if action A `feeds` action B, then B is
`fed_by` A. This module builds the reverse lookup and provides graph
traversal across the action stream.

Provenance injection writes back-references into artifacts so the graph
is traversable from either direction: action → artifact and artifact → action.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from action_ledger.schemas import (
    ROUTE_INVERSES,
    Action,
    ActionIndex,
    RouteKind,
)


@dataclass
class ResolvedRoute:
    """A route with its source action resolved."""

    source_id: str          # the action that declared this route
    kind: str               # route kind or its inverse name
    target: str             # what the route points to
    amount: float           # effective influence weight
    inverse: bool = False   # True if this is the reverse direction


@dataclass
class RouteGraph:
    """Bidirectional index over all routes in an action stream.

    forward[source_id] → list of routes FROM that action
    reverse[target]    → list of routes TO that target (with inverse kinds)
    """

    forward: dict[str, list[ResolvedRoute]] = field(default_factory=dict)
    reverse: dict[str, list[ResolvedRoute]] = field(default_factory=dict)


def build_route_graph(index: ActionIndex) -> RouteGraph:
    """Build the bidirectional route graph from an action stream.

    For every route on every action, creates both the forward entry
    (source → target) and the reverse entry (target ← source with
    inverse kind name).
    """
    graph = RouteGraph()

    for action in index.actions:
        for route in action.routes:
            fwd = ResolvedRoute(
                source_id=action.id,
                kind=route.kind.value,
                target=route.target,
                amount=route.effective_amount(),
                inverse=False,
            )

            # Forward: source_id → target
            graph.forward.setdefault(action.id, []).append(fwd)

            # Reverse: target → source_id (with inverse kind)
            inv_kind = ROUTE_INVERSES.get(route.kind, f"inv_{route.kind.value}")
            rev = ResolvedRoute(
                source_id=action.id,
                kind=inv_kind,
                target=action.id,
                amount=route.effective_amount(),
                inverse=True,
            )
            graph.reverse.setdefault(route.target, []).append(rev)

    return graph


def routes_from(graph: RouteGraph, source_id: str) -> list[ResolvedRoute]:
    """All routes originating FROM a given action."""
    return graph.forward.get(source_id, [])


def routes_to(graph: RouteGraph, target: str) -> list[ResolvedRoute]:
    """All routes pointing TO a given target (action ID, file path, URI).

    Returns inverse routes — e.g., if action A has a `consumed` route to
    target X, this returns a `consumed_by` route from X back to A.
    """
    return graph.reverse.get(target, [])


def find_producers(graph: RouteGraph, artifact: str) -> list[ResolvedRoute]:
    """Find all actions that produced a given artifact.

    Filters reverse routes for `produced_by` kind specifically.
    """
    return [r for r in routes_to(graph, artifact) if r.kind == "produced_by"]


def find_consumers(graph: RouteGraph, artifact: str) -> list[ResolvedRoute]:
    """Find all actions that consumed a given artifact."""
    return [r for r in routes_to(graph, artifact) if r.kind == "consumed_by"]


_INPUT_KINDS = {RouteKind.CONSUMED, RouteKind.INFORMED_BY, RouteKind.CONTINUES}


def trace_lineage(
    graph: RouteGraph,
    action_id: str,
    depth: int = 3,
) -> list[list[ResolvedRoute]]:
    """Trace the lineage of an action — what fed it, what fed those, etc.

    Walks two paths simultaneously:
    1. Reverse graph: what other actions have routes pointing TO this action
    2. Forward graph: this action's own input routes (consumed, informed_by,
       continues) — these are declared dependencies

    Returns a list of layers, each layer being the routes one step further
    back in the causal chain.
    """
    layers: list[list[ResolvedRoute]] = []
    current_ids = {action_id}
    visited: set[str] = {action_id}

    for _ in range(depth):
        layer: list[ResolvedRoute] = []
        next_ids: set[str] = set()

        for aid in current_ids:
            # Path 1: reverse graph — what points at this action
            for route in routes_to(graph, aid):
                layer.append(route)
                if route.source_id not in visited:
                    next_ids.add(route.source_id)

            # Path 2: forward graph — this action's own input routes
            for route in routes_from(graph, aid):
                if route.kind in {k.value for k in _INPUT_KINDS}:
                    # The route target is the input source
                    fwd_as_lineage = ResolvedRoute(
                        source_id=aid,
                        kind=route.kind,
                        target=route.target,
                        amount=route.amount,
                        inverse=False,
                    )
                    layer.append(fwd_as_lineage)
                    if route.target not in visited:
                        next_ids.add(route.target)

        if not layer:
            break
        layers.append(layer)
        visited.update(next_ids)
        current_ids = next_ids

    return layers


def provenance_comment(action: Action) -> str:
    """Generate a provenance comment for injection into an artifact.

    Returns a comment string that can be prepended or appended to an artifact
    to create the backward reference from artifact → action.

    Format: `# Provenance: {action_id} [{verb}] {target} ({timestamp})`
    """
    return (
        f"# Provenance: {action.id} [{action.verb}] "
        f"{action.target} ({action.timestamp})"
    )


def provenance_yaml_header(action: Action) -> dict[str, str]:
    """Generate provenance metadata suitable for YAML frontmatter.

    Returns a dict that can be merged into a YAML file's metadata section.
    """
    return {
        "provenance_action": action.id,
        "provenance_verb": action.verb,
        "provenance_target": action.target,
        "provenance_timestamp": action.timestamp,
        "provenance_session": action.session,
    }
