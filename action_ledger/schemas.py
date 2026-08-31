"""Data schemas for the action ledger.

Open parameter model: actions carry whatever params are relevant at capture time.
The parameter registry grows as the system discovers what it needs to track.
Routes are typed and weighted connections (patch bay model from Brahma).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from action_ledger.execution_schemas import ExecutionEnvelope


class ActionOrigin(StrEnum):
    """How an action entered the ledger."""

    MANUAL = "manual"      # CLI-recorded by human or agent
    EMITTED = "emitted"    # Auto-emitted by a state change


class RouteKind(StrEnum):
    """How one action/artifact relates to another."""

    CONSUMED = "consumed"          # Action read/used this resource
    PRODUCED = "produced"          # Action created this artifact
    INFORMED_BY = "informed_by"    # Action was influenced by this source
    FEEDS = "feeds"                # Action's output routes to another's input
    CONTINUES = "continues"        # Cross-session continuity
    CONTRADICTS = "contradicts"    # Action invalidates a prior action
    REFINES = "refines"            # Action sharpens a prior action


# Default influence weights per route kind
ROUTE_DEFAULTS: dict[RouteKind, float] = {
    RouteKind.CONSUMED: 1.0,
    RouteKind.PRODUCED: 1.0,
    RouteKind.INFORMED_BY: 0.6,
    RouteKind.FEEDS: 1.0,
    RouteKind.CONTINUES: 1.0,
    RouteKind.CONTRADICTS: -1.0,
    RouteKind.REFINES: 0.5,
}

# Inverse route kinds for bidirectional traversal
ROUTE_INVERSES: dict[RouteKind, str] = {
    RouteKind.CONSUMED: "consumed_by",
    RouteKind.PRODUCED: "produced_by",
    RouteKind.INFORMED_BY: "informs",
    RouteKind.FEEDS: "fed_by",
    RouteKind.CONTINUES: "continued_by",
    RouteKind.CONTRADICTS: "contradicted_by",
    RouteKind.REFINES: "refined_by",
}


class Route(BaseModel):
    """A typed, weighted connection between an action and a target.

    Modelled on the Brahma patch bay: (src * amount * scale) + offset.
    """

    kind: RouteKind
    target: str                    # action ID, file path, memory:// URI, etc.
    amount: float = 0.0            # influence weight — 0 means use kind default

    def effective_amount(self) -> float:
        if self.amount != 0.0:
            return self.amount
        return ROUTE_DEFAULTS.get(self.kind, 1.0)


class Produced(BaseModel):
    """Something an action yielded."""

    type: str                      # insight, artifact, memory, issue, etc.
    ref: str                       # reference to the produced thing


class Action(BaseModel):
    """A semantic event — an idea at a point in its parameter trajectory.

    Captured at state/phase transitions or parameter changes.
    """

    id: str                        # act-{session}-{MMDD}-{seq:03d}
    timestamp: str                 # ISO 8601
    session: str                   # session identifier (e.g., S42)
    verb: str                      # what was done
    target: str                    # what it was done to/with
    context: str = ""              # why / surrounding intent
    params: dict[str, float | str] = Field(default_factory=dict)
    produced: list[Produced] = Field(default_factory=list)
    routes: list[Route] = Field(default_factory=list)
    origin: ActionOrigin = ActionOrigin.MANUAL
    sequence_id: str = ""          # which sequence this belongs to
    execution: ExecutionEnvelope | None = None


class ActionIndex(BaseModel):
    """The append-only action stream."""

    generated: str = ""
    actions: list[Action] = Field(default_factory=list)


class Sequence(BaseModel):
    """A group of actions sharing a common intent.

    Like a CHRONOS track — has automation lanes recording how parameters
    changed across its constituent actions.
    """

    id: str                        # seq-{session}-{seq:03d}
    session: str
    intent: str = ""
    action_ids: list[str] = Field(default_factory=list)
    automation: dict[str, list[float]] = Field(default_factory=dict)
    outcome: str = ""
    chain_id: str = ""
    closed: bool = False


class SequenceIndex(BaseModel):
    """All composed sequences."""

    generated: str = ""
    sequences: list[Sequence] = Field(default_factory=list)

    def active_for_session(self, session: str) -> Sequence | None:
        """Return the current open sequence for a session, if any."""
        for seq in reversed(self.sequences):
            if seq.session == session and not seq.closed:
                return seq
        return None


class Chain(BaseModel):
    """A complete thought-arc: sequences grouped into a prompt-response cycle.

    Like a CHRONOS pattern — multiple tracks playing simultaneously.
    """

    id: str                        # chain-{session}-{seq:03d}
    session: str
    prompt_essence: str = ""
    sequence_ids: list[str] = Field(default_factory=list)
    arc: dict[str, str] = Field(default_factory=dict)
    produced_artifacts: list[str] = Field(default_factory=list)
    routes: list[Route] = Field(default_factory=list)


class ChainIndex(BaseModel):
    """All composed chains."""

    generated: str = ""
    chains: list[Chain] = Field(default_factory=list)


class ParamAxis(BaseModel):
    """A known parameter axis in the registry.

    Like a module param in Brahma's module_registry — discovered at runtime.
    """

    name: str
    range: list[float] = Field(default_factory=lambda: [0.0, 1.0])
    description: str = ""
    first_seen: str = ""           # ISO date
    frequency: int = 0             # how often this axis appears in actions


class ParamRegistry(BaseModel):
    """Registry of known parameter axes. Grows as actions introduce new ones."""

    axes: dict[str, ParamAxis] = Field(default_factory=dict)

    def register(self, name: str, value: float, timestamp: str) -> None:
        """Register or update a parameter axis from an action's params."""
        if name in self.axes:
            axis = self.axes[name]
            axis.frequency += 1
            # Expand range if needed
            if value < axis.range[0]:
                axis.range[0] = value
            if value > axis.range[1]:
                axis.range[1] = value
        else:
            self.axes[name] = ParamAxis(
                name=name,
                range=[min(0.0, value), max(1.0, value)],
                first_seen=timestamp[:10],
                frequency=1,
            )
