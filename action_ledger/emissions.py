"""State change emission — the system records its own transitions.

Every state machine in the orchestration hub can emit a structured action
when it transitions. Emitted actions carry `origin: emitted` and standardized
params (from_state, to_state, subsystem) so the cycle detector and route
graph can observe the system's own behavior.

Emissions never crash the caller. If the ledger is unavailable or persistence
fails, the function returns None and logs the failure.
"""

from __future__ import annotations

import logging
from typing import Any

from action_ledger.schemas import (
    Action,
    ActionOrigin,
    RouteKind,
)

logger = logging.getLogger(__name__)

# Session identifier for emissions when no session context is provided
_EMISSION_SESSION = "_sys"


def emit_state_change(
    subsystem: str,
    verb: str,
    target: str,
    from_state: str,
    to_state: str,
    session: str = "",
    params: dict[str, Any] | None = None,
    routes: list[dict[str, Any]] | None = None,
    produced: list[dict[str, str]] | None = None,
) -> Action | None:
    """Record a state change as an action ledger entry.

    Returns the recorded Action, or None if the ledger is unavailable.
    """
    # Lazy import to avoid circular dependency — emissions.py is imported
    # by ledger.py, but also calls record() from ledger.py
    from action_ledger.ledger import (
        load_actions,
        load_param_registry,
        load_sequences,
        record,
        save_actions,
        save_param_registry,
        save_sequences,
    )

    try:
        action_index = load_actions()
        sequence_index = load_sequences()
        param_registry = load_param_registry()

        emission_params: dict[str, float | str] = {
            "subsystem": subsystem,
            "from_state": from_state,
            "to_state": to_state,
        }
        if params:
            emission_params.update(params)

        # Build routes — always include a CONTINUES route to the target entity
        emission_routes = [
            {"kind": RouteKind.CONTINUES, "target": target},
        ]
        if routes:
            emission_routes.extend(routes)

        action = record(
            action_index,
            sequence_index,
            param_registry,
            session=session or _EMISSION_SESSION,
            verb=verb,
            target=target,
            context=f"{subsystem}: {from_state} → {to_state}",
            params=emission_params,
            produced=produced,
            routes=emission_routes,
            origin=ActionOrigin.EMITTED,
        )

        save_actions(action_index)
        save_sequences(sequence_index)
        save_param_registry(param_registry)

        logger.debug(
            "Emitted state change: %s %s (%s → %s)",
            verb, target, from_state, to_state,
        )
        return action

    except Exception:
        logger.debug(
            "Emission failed for %s %s — ledger unavailable",
            verb, target, exc_info=True,
        )
        return None
