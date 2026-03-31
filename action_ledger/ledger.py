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
