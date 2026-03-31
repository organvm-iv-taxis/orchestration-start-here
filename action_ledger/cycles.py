"""Cycle detection — pattern matching on automation lanes across sessions.

Detects repeated patterns so they can be formalized into systems:
1. Verb sequence matching — same verb patterns repeating
2. Automation lane trajectory matching — same parameter trajectories
3. Cross-session intent matching — same intent re-entering the system
4. Parameter stall detection — an axis that stops moving

Like recognizing Euclidean rhythms in step sequences — the regularity
in the data reveals the pattern the human hasn't seen yet.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from action_ledger.schemas import (
    ActionIndex,
    Chain,
    ChainIndex,
    Sequence,
    SequenceIndex,
)


@dataclass
class DetectedCycle:
    """A repeated pattern detected across sessions."""

    cycle_type: str          # verb_sequence | trajectory | intent | stall
    pattern: str             # human-readable description of the pattern
    sessions: list[str]      # sessions where this pattern appeared
    recurrence: int          # how many times it appeared
    evidence: list[str] = field(default_factory=list)  # supporting IDs


# ---------------------------------------------------------------------------
# Verb sequence matching
# ---------------------------------------------------------------------------

def _extract_verb_sequences(
    action_index: ActionIndex,
    window: int = 3,
) -> dict[str, list[tuple[str, str]]]:
    """Extract verb n-grams per session.

    Returns {session: [(ngram_str, first_action_id), ...]}
    """
    by_session: dict[str, list] = {}
    for a in action_index.actions:
        by_session.setdefault(a.session, []).append(a)

    result: dict[str, list[tuple[str, str]]] = {}
    for session, actions in by_session.items():
        ngrams: list[tuple[str, str]] = []
        for i in range(len(actions) - window + 1):
            gram = " -> ".join(a.verb for a in actions[i : i + window])
            ngrams.append((gram, actions[i].id))
        result[session] = ngrams

    return result


def detect_verb_cycles(
    action_index: ActionIndex,
    min_recurrence: int = 2,
    window: int = 3,
) -> list[DetectedCycle]:
    """Find verb sequences that repeat across sessions."""
    per_session = _extract_verb_sequences(action_index, window)

    # Count how many sessions each ngram appears in
    ngram_sessions: dict[str, list[str]] = {}
    ngram_evidence: dict[str, list[str]] = {}
    for session, ngrams in per_session.items():
        seen: set[str] = set()
        for gram, action_id in ngrams:
            if gram not in seen:
                ngram_sessions.setdefault(gram, []).append(session)
                seen.add(gram)
            ngram_evidence.setdefault(gram, []).append(action_id)

    cycles: list[DetectedCycle] = []
    for gram, sessions in ngram_sessions.items():
        if len(sessions) >= min_recurrence:
            cycles.append(DetectedCycle(
                cycle_type="verb_sequence",
                pattern=gram,
                sessions=sessions,
                recurrence=len(sessions),
                evidence=ngram_evidence.get(gram, []),
            ))

    return sorted(cycles, key=lambda c: -c.recurrence)


# ---------------------------------------------------------------------------
# Automation lane trajectory matching
# ---------------------------------------------------------------------------

def _classify_trajectory(values: list[float]) -> str:
    """Classify a parameter trajectory into a named pattern."""
    if len(values) < 2:
        return "single_point"

    diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    delta = values[-1] - values[0]
    all_up = all(d >= 0 for d in diffs)
    all_down = all(d <= 0 for d in diffs)
    all_flat = all(abs(d) < 0.05 for d in diffs)

    if all_flat:
        return "stable"
    elif all_up and delta > 0.1:
        return "ascended"
    elif all_down and delta < -0.1:
        return "descended"
    elif abs(delta) < 0.1:
        return "stalled"
    else:
        return "oscillated"


def detect_trajectory_cycles(
    sequence_index: SequenceIndex,
    min_recurrence: int = 2,
) -> list[DetectedCycle]:
    """Find parameter trajectories that repeat across sessions.

    Groups sequences by session, classifies each axis's trajectory, then
    finds trajectory fingerprints that appear in multiple sessions.
    """
    # Build per-session trajectory fingerprints
    session_fingerprints: dict[str, dict[str, str]] = {}
    session_evidence: dict[str, list[str]] = {}

    for seq in sequence_index.sequences:
        fp = session_fingerprints.setdefault(seq.session, {})
        session_evidence.setdefault(seq.session, []).append(seq.id)
        for axis, values in seq.automation.items():
            trajectory = _classify_trajectory(values)
            # Use the most recent trajectory for each axis per session
            fp[axis] = trajectory

    # Find axis:trajectory pairs that repeat
    pair_sessions: dict[str, list[str]] = {}
    for session, fp in session_fingerprints.items():
        for axis, trajectory in fp.items():
            key = f"{axis}:{trajectory}"
            pair_sessions.setdefault(key, []).append(session)

    cycles: list[DetectedCycle] = []
    for key, sessions in pair_sessions.items():
        if len(sessions) >= min_recurrence:
            axis, trajectory = key.split(":", 1)
            cycles.append(DetectedCycle(
                cycle_type="trajectory",
                pattern=f"{axis} {trajectory} in {len(sessions)} sessions",
                sessions=sessions,
                recurrence=len(sessions),
                evidence=[
                    eid
                    for s in sessions
                    for eid in session_evidence.get(s, [])
                ],
            ))

    return sorted(cycles, key=lambda c: -c.recurrence)


# ---------------------------------------------------------------------------
# Cross-session intent matching
# ---------------------------------------------------------------------------

def detect_intent_cycles(
    sequence_index: SequenceIndex,
    min_recurrence: int = 2,
) -> list[DetectedCycle]:
    """Find intents that reappear across sessions.

    Uses exact string matching on sequence intents. Ignores empty intents.
    """
    intent_sessions: dict[str, list[str]] = {}
    intent_evidence: dict[str, list[str]] = {}

    for seq in sequence_index.sequences:
        if not seq.intent:
            continue
        key = seq.intent.lower().strip()
        if seq.session not in intent_sessions.get(key, []):
            intent_sessions.setdefault(key, []).append(seq.session)
        intent_evidence.setdefault(key, []).append(seq.id)

    cycles: list[DetectedCycle] = []
    for intent, sessions in intent_sessions.items():
        if len(sessions) >= min_recurrence:
            cycles.append(DetectedCycle(
                cycle_type="intent",
                pattern=f'Intent "{intent}" appeared in {len(sessions)} sessions',
                sessions=sessions,
                recurrence=len(sessions),
                evidence=intent_evidence.get(intent, []),
            ))

    return sorted(cycles, key=lambda c: -c.recurrence)


# ---------------------------------------------------------------------------
# Parameter stall detection
# ---------------------------------------------------------------------------

def detect_stalls(
    sequence_index: SequenceIndex,
    min_sequences: int = 3,
    stall_threshold: float = 0.05,
) -> list[DetectedCycle]:
    """Detect parameters that have stopped moving across recent sequences.

    A stall is when a parameter's value hasn't changed significantly
    across N consecutive sequences — the idea is stuck.
    """
    # Collect the last value of each axis per sequence, ordered by time
    axis_history: dict[str, list[tuple[str, str, float]]] = {}  # axis → [(session, seq_id, value)]

    for seq in sequence_index.sequences:
        for axis, values in seq.automation.items():
            if values:
                axis_history.setdefault(axis, []).append(
                    (seq.session, seq.id, values[-1])
                )

    cycles: list[DetectedCycle] = []
    for axis, history in axis_history.items():
        if len(history) < min_sequences:
            continue

        # Check the last N entries for stall
        recent = history[-min_sequences:]
        values = [v for _, _, v in recent]
        value_range = max(values) - min(values)

        if value_range < stall_threshold:
            sessions = list(dict.fromkeys(s for s, _, _ in recent))
            cycles.append(DetectedCycle(
                cycle_type="stall",
                pattern=f"{axis} stalled at ~{values[-1]:.2f} across {len(recent)} sequences",
                sessions=sessions,
                recurrence=len(recent),
                evidence=[sid for _, sid, _ in recent],
            ))

    return sorted(cycles, key=lambda c: -c.recurrence)


# ---------------------------------------------------------------------------
# Unified detection
# ---------------------------------------------------------------------------

def detect_all_cycles(
    action_index: ActionIndex,
    sequence_index: SequenceIndex,
    min_recurrence: int = 2,
    verb_window: int = 3,
    stall_sequences: int = 3,
) -> list[DetectedCycle]:
    """Run all cycle detectors and return combined results."""
    results: list[DetectedCycle] = []
    results.extend(detect_verb_cycles(action_index, min_recurrence, verb_window))
    results.extend(detect_trajectory_cycles(sequence_index, min_recurrence))
    results.extend(detect_intent_cycles(sequence_index, min_recurrence))
    results.extend(detect_stalls(sequence_index, stall_sequences))
    return sorted(results, key=lambda c: (-c.recurrence, c.cycle_type))
