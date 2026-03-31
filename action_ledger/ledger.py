"""Core ledger operations — record, load, save, compose.

record() is atomic: it simultaneously appends the action to the stream,
slots it into the current active sequence, and registers any new parameter
axes. Recording IS composing IS manifesting.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import yaml

from action_ledger.schemas import (
    Action,
    ActionIndex,
    Chain,
    ChainIndex,
    ParamRegistry,
    Produced,
    Route,
    Sequence,
    SequenceIndex,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_actions(path: Path | None = None) -> ActionIndex:
    """Load the action stream from YAML."""
    p = path or DATA_DIR / "actions.yaml"
    if not p.exists():
        return ActionIndex()
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return ActionIndex()
    return ActionIndex.model_validate(data)


def save_actions(index: ActionIndex, path: Path | None = None) -> Path:
    """Persist the action stream to YAML."""
    p = path or DATA_DIR / "actions.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            index.model_dump(mode="json"), f,
            default_flow_style=False, sort_keys=False,
        )
    return p


def load_sequences(path: Path | None = None) -> SequenceIndex:
    """Load sequences from YAML."""
    p = path or DATA_DIR / "sequences.yaml"
    if not p.exists():
        return SequenceIndex()
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return SequenceIndex()
    return SequenceIndex.model_validate(data)


def save_sequences(index: SequenceIndex, path: Path | None = None) -> Path:
    """Persist sequences to YAML."""
    p = path or DATA_DIR / "sequences.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            index.model_dump(mode="json"), f,
            default_flow_style=False, sort_keys=False,
        )
    return p


def load_param_registry(path: Path | None = None) -> ParamRegistry:
    """Load the parameter registry from YAML."""
    p = path or DATA_DIR / "param_registry.yaml"
    if not p.exists():
        return ParamRegistry()
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return ParamRegistry()
    return ParamRegistry.model_validate(data)


def save_param_registry(registry: ParamRegistry, path: Path | None = None) -> Path:
    """Persist the parameter registry to YAML."""
    p = path or DATA_DIR / "param_registry.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            registry.model_dump(mode="json"), f,
            default_flow_style=False, sort_keys=False,
        )
    return p


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------

def _make_action_id(session: str, actions: list[Action]) -> str:
    """Generate action ID: act-{session}-{MMDD}-{seq:03d}."""
    now = datetime.now()
    date_tag = now.strftime("%m%d")
    prefix = f"act-{session}-{date_tag}-"
    seq = sum(1 for a in actions if a.id.startswith(prefix)) + 1
    return f"{prefix}{seq:03d}"


def _make_sequence_id(session: str, sequences: list[Sequence]) -> str:
    """Generate sequence ID: seq-{session}-{seq:03d}."""
    existing = sum(1 for s in sequences if s.session == session)
    return f"seq-{session}-{existing + 1:03d}"


# ---------------------------------------------------------------------------
# Core recording — the atomic operation
# ---------------------------------------------------------------------------

def record(
    action_index: ActionIndex,
    sequence_index: SequenceIndex,
    param_registry: ParamRegistry,
    *,
    session: str,
    verb: str,
    target: str,
    context: str = "",
    params: dict[str, float | str] | None = None,
    produced: list[dict[str, str]] | None = None,
    routes: list[dict[str, str | float]] | None = None,
) -> Action:
    """Record an action — atomically appends, composes, and manifests.

    1. Creates the action and appends to the stream.
    2. Slots into the current active sequence (creates one if none exists).
    3. Registers any new numeric parameter axes in the registry.
    """
    now = datetime.now()
    params = params or {}
    action_id = _make_action_id(session, action_index.actions)

    # Build produced list
    produced_models = [Produced(**p) for p in (produced or [])]

    # Build routes list
    route_models = [Route(**r) for r in (routes or [])]

    action = Action(
        id=action_id,
        timestamp=now.isoformat(),
        session=session,
        verb=verb,
        target=target,
        context=context,
        params=params,
        produced=produced_models,
        routes=route_models,
    )

    # --- 1. Append to stream ---
    action_index.actions.append(action)

    # --- 2. Auto-slot into current sequence ---
    active_seq = sequence_index.active_for_session(session)
    if active_seq is None:
        active_seq = Sequence(
            id=_make_sequence_id(session, sequence_index.sequences),
            session=session,
        )
        sequence_index.sequences.append(active_seq)

    active_seq.action_ids.append(action_id)
    action.sequence_id = active_seq.id

    # Update automation lanes with numeric params
    for key, value in params.items():
        if isinstance(value, (int, float)):
            lane = active_seq.automation.setdefault(key, [])
            lane.append(float(value))

    # --- 3. Register parameter axes ---
    ts = now.isoformat()
    for key, value in params.items():
        if isinstance(value, (int, float)):
            param_registry.register(key, float(value), ts)

    return action


# ---------------------------------------------------------------------------
# Sequence operations
# ---------------------------------------------------------------------------

def close_sequence(
    sequence_index: SequenceIndex,
    session: str,
    outcome: str = "",
) -> Sequence | None:
    """Close the active sequence for a session, optionally recording its outcome."""
    active = sequence_index.active_for_session(session)
    if active is None:
        return None
    active.closed = True
    if outcome:
        active.outcome = outcome
    return active


def set_sequence_intent(
    sequence_index: SequenceIndex,
    session: str,
    intent: str,
) -> Sequence | None:
    """Set the intent on the active sequence for a session."""
    active = sequence_index.active_for_session(session)
    if active is None:
        return None
    active.intent = intent
    return active


# ---------------------------------------------------------------------------
# Chain persistence
# ---------------------------------------------------------------------------

def load_chains(path: Path | None = None) -> ChainIndex:
    """Load chains from YAML."""
    p = path or DATA_DIR / "chains.yaml"
    if not p.exists():
        return ChainIndex()
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return ChainIndex()
    return ChainIndex.model_validate(data)


def save_chains(index: ChainIndex, path: Path | None = None) -> Path:
    """Persist chains to YAML."""
    p = path or DATA_DIR / "chains.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            index.model_dump(mode="json"), f,
            default_flow_style=False, sort_keys=False,
        )
    return p


def _make_chain_id(session: str, chains: list[Chain]) -> str:
    """Generate chain ID: chain-{session}-{seq:03d}."""
    existing = sum(1 for c in chains if c.session == session)
    return f"chain-{session}-{existing + 1:03d}"


# ---------------------------------------------------------------------------
# Chain composition
# ---------------------------------------------------------------------------

def _compute_arc(sequences: list[Sequence]) -> dict[str, str]:
    """Compute the arc summary from sequence automation lanes.

    For each parameter axis, describes the overall trajectory across
    all sequences: ascended, descended, stable, oscillated, or stalled.
    """
    # Merge all automation lanes across sequences
    merged: dict[str, list[float]] = {}
    for seq in sequences:
        for axis, values in seq.automation.items():
            merged.setdefault(axis, []).extend(values)

    arc: dict[str, str] = {}
    for axis, values in merged.items():
        if len(values) < 2:
            arc[axis] = "single_point"
            continue

        first, last = values[0], values[-1]
        delta = last - first

        # Check for monotonicity
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        all_up = all(d >= 0 for d in diffs)
        all_down = all(d <= 0 for d in diffs)
        all_flat = all(abs(d) < 0.05 for d in diffs)

        if all_flat:
            arc[axis] = "stable"
        elif all_up and delta > 0.1:
            arc[axis] = "ascended"
        elif all_down and delta < -0.1:
            arc[axis] = "descended"
        elif abs(delta) < 0.1:
            arc[axis] = "stalled" if not all_flat else "stable"
        else:
            arc[axis] = "oscillated"

    return arc


def compose_chain(
    sequence_index: SequenceIndex,
    chain_index: ChainIndex,
    session: str,
    prompt_essence: str = "",
    produced_artifacts: list[str] | None = None,
) -> Chain | None:
    """Compose all sequences for a session into a chain.

    Collects all sequences (open and closed) for the session, computes the
    arc summary from their combined automation lanes, and creates a Chain.
    Returns None if no sequences exist for the session.
    """
    session_seqs = [s for s in sequence_index.sequences if s.session == session]
    if not session_seqs:
        return None

    chain = Chain(
        id=_make_chain_id(session, chain_index.chains),
        session=session,
        prompt_essence=prompt_essence,
        sequence_ids=[s.id for s in session_seqs],
        arc=_compute_arc(session_seqs),
        produced_artifacts=produced_artifacts or [],
    )
    chain_index.chains.append(chain)

    # Back-reference: stamp each sequence with its chain
    for seq in session_seqs:
        seq.chain_id = chain.id

    return chain


def close_session(
    sequence_index: SequenceIndex,
    chain_index: ChainIndex,
    session: str,
    prompt_essence: str = "",
    produced_artifacts: list[str] | None = None,
) -> Chain | None:
    """Close a session: close the active sequence, compose a chain.

    This is the session-boundary operation. It:
    1. Closes the active sequence (if any)
    2. Composes all session sequences into a chain
    """
    # Close any open sequence
    close_sequence(sequence_index, session)

    # Compose into chain
    return compose_chain(
        sequence_index, chain_index, session,
        prompt_essence=prompt_essence,
        produced_artifacts=produced_artifacts,
    )
