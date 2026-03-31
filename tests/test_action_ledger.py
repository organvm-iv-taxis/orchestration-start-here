"""Tests for the action ledger — Phases 1-4."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from action_ledger.cycles import (
    detect_all_cycles,
    detect_intent_cycles,
    detect_stalls,
    detect_trajectory_cycles,
    detect_verb_cycles,
)
from action_ledger.routes import (
    build_route_graph,
    find_consumers,
    find_producers,
    provenance_comment,
    provenance_yaml_header,
    routes_from,
    routes_to,
    trace_lineage,
)
from action_ledger.schemas import (
    Action,
    ActionIndex,
    ChainIndex,
    ParamAxis,
    ParamRegistry,
    Produced,
    Route,
    RouteKind,
    Sequence,
    SequenceIndex,
)
from action_ledger.ledger import (
    close_sequence,
    close_session,
    compose_chain,
    load_actions,
    load_chains,
    load_param_registry,
    load_sequences,
    record,
    save_actions,
    save_chains,
    save_param_registry,
    save_sequences,
    set_sequence_intent,
)


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestAction:
    def test_minimal_action(self):
        a = Action(id="act-S42-0331-001", timestamp="2026-03-31T14:00:00",
                    session="S42", verb="explored", target="fieldwork")
        assert a.id == "act-S42-0331-001"
        assert a.params == {}
        assert a.produced == []
        assert a.routes == []

    def test_action_with_open_params(self):
        a = Action(id="act-S42-0331-001", timestamp="2026-03-31T14:00:00",
                    session="S42", verb="designed", target="action-ledger",
                    params={"abstraction": 0.7, "maturity": 0.3, "domain": "orchestration"})
        assert a.params["abstraction"] == 0.7
        assert a.params["domain"] == "orchestration"

    def test_action_with_routes(self):
        a = Action(id="act-S42-0331-001", timestamp="2026-03-31T14:00:00",
                    session="S42", verb="explored", target="fieldwork",
                    routes=[Route(kind=RouteKind.CONSUMED, target="fieldwork.py")])
        assert len(a.routes) == 1
        assert a.routes[0].effective_amount() == 1.0

    def test_route_defaults(self):
        r_contradict = Route(kind=RouteKind.CONTRADICTS, target="x")
        assert r_contradict.effective_amount() == -1.0

        r_informed = Route(kind=RouteKind.INFORMED_BY, target="y")
        assert r_informed.effective_amount() == 0.6

        r_custom = Route(kind=RouteKind.CONSUMED, target="z", amount=0.3)
        assert r_custom.effective_amount() == 0.3


class TestParamRegistry:
    def test_register_new_axis(self):
        reg = ParamRegistry()
        reg.register("abstraction", 0.7, "2026-03-31T14:00:00")
        assert "abstraction" in reg.axes
        assert reg.axes["abstraction"].frequency == 1
        assert reg.axes["abstraction"].first_seen == "2026-03-31"

    def test_register_increments_frequency(self):
        reg = ParamRegistry()
        reg.register("abstraction", 0.7, "2026-03-31T14:00:00")
        reg.register("abstraction", 0.5, "2026-03-31T15:00:00")
        assert reg.axes["abstraction"].frequency == 2

    def test_register_expands_range(self):
        reg = ParamRegistry()
        reg.register("urgency", 0.5, "2026-03-31T14:00:00")
        reg.register("urgency", 1.5, "2026-03-31T15:00:00")
        assert reg.axes["urgency"].range[1] == 1.5

    def test_register_multiple_axes(self):
        reg = ParamRegistry()
        reg.register("abstraction", 0.7, "2026-03-31T14:00:00")
        reg.register("maturity", 0.3, "2026-03-31T14:00:00")
        reg.register("urgency", 1.0, "2026-03-31T14:00:00")
        assert len(reg.axes) == 3


class TestSequenceIndex:
    def test_active_for_session(self):
        idx = SequenceIndex(sequences=[
            Sequence(id="seq-S42-001", session="S42", closed=True),
            Sequence(id="seq-S42-002", session="S42", closed=False),
        ])
        active = idx.active_for_session("S42")
        assert active is not None
        assert active.id == "seq-S42-002"

    def test_active_for_session_none(self):
        idx = SequenceIndex(sequences=[
            Sequence(id="seq-S42-001", session="S42", closed=True),
        ])
        assert idx.active_for_session("S42") is None

    def test_active_for_session_wrong_session(self):
        idx = SequenceIndex(sequences=[
            Sequence(id="seq-S42-001", session="S42", closed=False),
        ])
        assert idx.active_for_session("S43") is None


# ---------------------------------------------------------------------------
# Ledger tests
# ---------------------------------------------------------------------------


class TestRecord:
    def test_basic_record(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        action = record(
            actions, sequences, registry,
            session="S42", verb="explored", target="fieldwork",
        )

        assert action.id.startswith("act-S42-")
        assert action.verb == "explored"
        assert action.target == "fieldwork"
        assert len(actions.actions) == 1

    def test_record_auto_creates_sequence(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        action = record(
            actions, sequences, registry,
            session="S42", verb="explored", target="fieldwork",
        )

        assert len(sequences.sequences) == 1
        seq = sequences.sequences[0]
        assert seq.session == "S42"
        assert action.id in seq.action_ids
        assert action.sequence_id == seq.id

    def test_record_slots_into_existing_sequence(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        a1 = record(actions, sequences, registry,
                     session="S42", verb="explored", target="fieldwork")
        a2 = record(actions, sequences, registry,
                     session="S42", verb="designed", target="schemas")

        assert len(sequences.sequences) == 1
        assert a1.sequence_id == a2.sequence_id
        assert len(sequences.sequences[0].action_ids) == 2

    def test_record_registers_params(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork",
               params={"abstraction": 0.7, "maturity": 0.3})

        assert "abstraction" in registry.axes
        assert "maturity" in registry.axes
        assert registry.axes["abstraction"].frequency == 1

    def test_record_builds_automation_lanes(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork",
               params={"abstraction": 0.7})
        record(actions, sequences, registry,
               session="S42", verb="designed", target="schemas",
               params={"abstraction": 0.5})
        record(actions, sequences, registry,
               session="S42", verb="built", target="ledger",
               params={"abstraction": 0.3})

        seq = sequences.sequences[0]
        assert "abstraction" in seq.automation
        assert seq.automation["abstraction"] == [0.7, 0.5, 0.3]

    def test_record_with_string_params_skips_automation(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork",
               params={"domain": "orchestration", "abstraction": 0.7})

        seq = sequences.sequences[0]
        assert "abstraction" in seq.automation
        assert "domain" not in seq.automation

    def test_record_with_routes(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        action = record(
            actions, sequences, registry,
            session="S42", verb="explored", target="fieldwork",
            routes=[{"kind": "consumed", "target": "fieldwork.py"}],
        )

        assert len(action.routes) == 1
        assert action.routes[0].kind == RouteKind.CONSUMED
        assert action.routes[0].target == "fieldwork.py"

    def test_record_with_produced(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        action = record(
            actions, sequences, registry,
            session="S42", verb="designed", target="action-ledger",
            produced=[{"type": "insight", "ref": "spectrum model is reusable"}],
        )

        assert len(action.produced) == 1
        assert action.produced[0].type == "insight"

    def test_separate_sessions_get_separate_sequences(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        a1 = record(actions, sequences, registry,
                     session="S42", verb="explored", target="a")
        a2 = record(actions, sequences, registry,
                     session="S43", verb="explored", target="b")

        assert len(sequences.sequences) == 2
        assert a1.sequence_id != a2.sequence_id


class TestCloseSequence:
    def test_close(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork")

        seq = close_sequence(sequences, "S42", outcome="patterns reusable", emit=False)
        assert seq is not None
        assert seq.closed is True
        assert seq.outcome == "patterns reusable"

    def test_close_creates_new_on_next_record(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork")
        close_sequence(sequences, "S42", emit=False)
        record(actions, sequences, registry,
               session="S42", verb="built", target="ledger")

        assert len(sequences.sequences) == 2

    def test_close_no_active(self):
        sequences = SequenceIndex()
        assert close_sequence(sequences, "S42", emit=False) is None


class TestSetSequenceIntent:
    def test_set_intent(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork")
        seq = set_sequence_intent(sequences, "S42", "determine reusability")

        assert seq is not None
        assert seq.intent == "determine reusability"


# ---------------------------------------------------------------------------
# Persistence tests
# ---------------------------------------------------------------------------


class TestPersistence:
    def test_actions_round_trip(self, tmp_path: Path):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork",
               params={"abstraction": 0.7},
               routes=[{"kind": "consumed", "target": "fieldwork.py"}],
               produced=[{"type": "insight", "ref": "reusable"}])

        path = tmp_path / "actions.yaml"
        save_actions(actions, path)

        loaded = load_actions(path)
        assert len(loaded.actions) == 1
        a = loaded.actions[0]
        assert a.verb == "explored"
        assert a.params["abstraction"] == 0.7
        assert len(a.routes) == 1
        assert a.routes[0].kind == RouteKind.CONSUMED
        assert len(a.produced) == 1

    def test_sequences_round_trip(self, tmp_path: Path):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="a",
               params={"abstraction": 0.7})
        record(actions, sequences, registry,
               session="S42", verb="designed", target="b",
               params={"abstraction": 0.5})

        path = tmp_path / "sequences.yaml"
        save_sequences(sequences, path)

        loaded = load_sequences(path)
        assert len(loaded.sequences) == 1
        seq = loaded.sequences[0]
        assert len(seq.action_ids) == 2
        assert seq.automation["abstraction"] == [0.7, 0.5]

    def test_param_registry_round_trip(self, tmp_path: Path):
        registry = ParamRegistry()
        registry.register("abstraction", 0.7, "2026-03-31T14:00:00")
        registry.register("maturity", 0.3, "2026-03-31T14:00:00")
        registry.register("abstraction", 0.5, "2026-03-31T15:00:00")

        path = tmp_path / "param_registry.yaml"
        save_param_registry(registry, path)

        loaded = load_param_registry(path)
        assert len(loaded.axes) == 2
        assert loaded.axes["abstraction"].frequency == 2
        assert loaded.axes["maturity"].frequency == 1

    def test_load_nonexistent_returns_empty(self, tmp_path: Path):
        assert len(load_actions(tmp_path / "nope.yaml").actions) == 0
        assert len(load_sequences(tmp_path / "nope.yaml").sequences) == 0
        assert len(load_param_registry(tmp_path / "nope.yaml").axes) == 0

    def test_yaml_structure(self, tmp_path: Path):
        """Verify the YAML output is human-readable and structured."""
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork",
               params={"abstraction": 0.7, "maturity": 0.3})

        path = tmp_path / "actions.yaml"
        save_actions(actions, path)

        raw = yaml.safe_load(path.read_text())
        assert "actions" in raw
        assert raw["actions"][0]["verb"] == "explored"
        assert raw["actions"][0]["params"]["abstraction"] == 0.7

    def test_chains_round_trip(self, tmp_path: Path):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="a",
               params={"abstraction": 0.7})
        record(actions, sequences, registry,
               session="S42", verb="built", target="b",
               params={"abstraction": 0.3})

        close_session(sequences, chains, "S42", prompt_essence="test chain", emit=False)

        path = tmp_path / "chains.yaml"
        save_chains(chains, path)

        loaded = load_chains(path)
        assert len(loaded.chains) == 1
        assert loaded.chains[0].prompt_essence == "test chain"
        assert loaded.chains[0].arc.get("abstraction") == "descended"


# ---------------------------------------------------------------------------
# Phase 2: Route graph tests
# ---------------------------------------------------------------------------


class TestRouteGraph:
    def _make_action_index(self) -> ActionIndex:
        """Build a test action index with routes."""
        return ActionIndex(actions=[
            Action(
                id="act-S42-0331-001", timestamp="2026-03-31T14:00:00",
                session="S42", verb="explored", target="fieldwork",
                routes=[
                    Route(kind=RouteKind.CONSUMED, target="fieldwork.py"),
                    Route(kind=RouteKind.PRODUCED, target="insight-001"),
                ],
            ),
            Action(
                id="act-S42-0331-002", timestamp="2026-03-31T14:10:00",
                session="S42", verb="designed", target="schemas",
                routes=[
                    Route(kind=RouteKind.CONSUMED, target="insight-001"),
                    Route(kind=RouteKind.INFORMED_BY, target="act-S42-0331-001"),
                    Route(kind=RouteKind.PRODUCED, target="schemas.py"),
                ],
            ),
            Action(
                id="act-S42-0331-003", timestamp="2026-03-31T14:20:00",
                session="S42", verb="built", target="ledger",
                routes=[
                    Route(kind=RouteKind.CONSUMED, target="schemas.py"),
                    Route(kind=RouteKind.FEEDS, target="act-S42-0331-004"),
                ],
            ),
        ])

    def test_build_graph_forward(self):
        graph = build_route_graph(self._make_action_index())
        fwd = routes_from(graph, "act-S42-0331-001")
        assert len(fwd) == 2
        assert {r.kind for r in fwd} == {"consumed", "produced"}

    def test_build_graph_reverse(self):
        graph = build_route_graph(self._make_action_index())
        rev = routes_to(graph, "fieldwork.py")
        assert len(rev) == 1
        assert rev[0].kind == "consumed_by"
        assert rev[0].source_id == "act-S42-0331-001"

    def test_find_producers(self):
        graph = build_route_graph(self._make_action_index())
        producers = find_producers(graph, "schemas.py")
        assert len(producers) == 1
        assert producers[0].source_id == "act-S42-0331-002"

    def test_find_consumers(self):
        graph = build_route_graph(self._make_action_index())
        consumers = find_consumers(graph, "schemas.py")
        assert len(consumers) == 1
        assert consumers[0].source_id == "act-S42-0331-003"

    def test_artifact_bidirectional(self):
        """An artifact should be reachable from both its producer and consumer."""
        graph = build_route_graph(self._make_action_index())
        # insight-001 was produced by action 001, consumed by action 002
        producers = find_producers(graph, "insight-001")
        consumers = find_consumers(graph, "insight-001")
        assert len(producers) == 1
        assert producers[0].source_id == "act-S42-0331-001"
        assert len(consumers) == 1
        assert consumers[0].source_id == "act-S42-0331-002"

    def test_trace_lineage(self):
        graph = build_route_graph(self._make_action_index())
        # action 002 was informed_by action 001, consumed insight-001
        layers = trace_lineage(graph, "act-S42-0331-002", depth=2)
        assert len(layers) >= 1
        # Layer 0 should include inputs: act-S42-0331-001 (informed_by) and insight-001 (consumed)
        layer0_targets = {r.target for r in layers[0]}
        assert "act-S42-0331-001" in layer0_targets

    def test_routes_to_nonexistent(self):
        graph = build_route_graph(self._make_action_index())
        assert routes_to(graph, "nonexistent") == []

    def test_routes_from_nonexistent(self):
        graph = build_route_graph(self._make_action_index())
        assert routes_from(graph, "nonexistent") == []


class TestProvenance:
    def test_provenance_comment(self):
        a = Action(id="act-S42-0331-001", timestamp="2026-03-31T14:00:00",
                    session="S42", verb="designed", target="schemas")
        comment = provenance_comment(a)
        assert "act-S42-0331-001" in comment
        assert "[designed]" in comment

    def test_provenance_yaml_header(self):
        a = Action(id="act-S42-0331-001", timestamp="2026-03-31T14:00:00",
                    session="S42", verb="designed", target="schemas")
        header = provenance_yaml_header(a)
        assert header["provenance_action"] == "act-S42-0331-001"
        assert header["provenance_session"] == "S42"


# ---------------------------------------------------------------------------
# Phase 3: Chain composition tests
# ---------------------------------------------------------------------------


class TestChainComposition:
    def test_compose_chain_basic(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="a",
               params={"abstraction": 0.7})
        record(actions, sequences, registry,
               session="S42", verb="built", target="b",
               params={"abstraction": 0.3})

        chain = compose_chain(sequences, chains, "S42", prompt_essence="test", emit=False)
        assert chain is not None
        assert chain.session == "S42"
        assert chain.prompt_essence == "test"
        assert len(chain.sequence_ids) == 1

    def test_chain_arc_descended(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="a", target="x", params={"abstraction": 0.9})
        record(actions, sequences, registry,
               session="S42", verb="b", target="y", params={"abstraction": 0.5})
        record(actions, sequences, registry,
               session="S42", verb="c", target="z", params={"abstraction": 0.2})

        chain = compose_chain(sequences, chains, "S42", emit=False)
        assert chain is not None
        assert chain.arc["abstraction"] == "descended"

    def test_chain_arc_ascended(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="a", target="x", params={"maturity": 0.1})
        record(actions, sequences, registry,
               session="S42", verb="b", target="y", params={"maturity": 0.5})
        record(actions, sequences, registry,
               session="S42", verb="c", target="z", params={"maturity": 0.9})

        chain = compose_chain(sequences, chains, "S42", emit=False)
        assert chain is not None
        assert chain.arc["maturity"] == "ascended"

    def test_chain_arc_stalled(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="a", target="x", params={"maturity": 0.4})
        record(actions, sequences, registry,
               session="S42", verb="b", target="y", params={"maturity": 0.6})
        record(actions, sequences, registry,
               session="S42", verb="c", target="z", params={"maturity": 0.4})

        chain = compose_chain(sequences, chains, "S42", emit=False)
        assert chain is not None
        # Went up then back down to start — stalled
        assert chain.arc["maturity"] in ("stalled", "oscillated")

    def test_close_session_closes_sequence_and_composes(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="a")

        chain = close_session(sequences, chains, "S42", prompt_essence="done", emit=False)
        assert chain is not None
        # Sequence should be closed
        assert sequences.sequences[0].closed is True
        # Sequence should have chain_id
        assert sequences.sequences[0].chain_id == chain.id

    def test_compose_chain_multiple_sequences(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        chains = ChainIndex()
        registry = ParamRegistry()

        # First sequence
        record(actions, sequences, registry,
               session="S42", verb="explored", target="a",
               params={"abstraction": 0.8})
        close_sequence(sequences, "S42", emit=False)

        # Second sequence
        record(actions, sequences, registry,
               session="S42", verb="built", target="b",
               params={"abstraction": 0.3})
        close_sequence(sequences, "S42", emit=False)

        chain = compose_chain(sequences, chains, "S42", emit=False)
        assert chain is not None
        assert len(chain.sequence_ids) == 2
        assert chain.arc["abstraction"] == "descended"

    def test_compose_chain_no_sequences(self):
        sequences = SequenceIndex()
        chains = ChainIndex()
        assert compose_chain(sequences, chains, "S99", emit=False) is None


# ---------------------------------------------------------------------------
# Phase 4: Cycle detection tests
# ---------------------------------------------------------------------------


def _build_multi_session_data():
    """Build test data with repeated patterns across 3 sessions."""
    actions = ActionIndex()
    sequences = SequenceIndex()
    registry = ParamRegistry()

    # S38: explore → design → abandon
    for session in ["S38", "S40", "S42"]:
        record(actions, sequences, registry,
               session=session, verb="explored", target="recording-infra",
               params={"abstraction": 0.8, "maturity": 0.2})
        record(actions, sequences, registry,
               session=session, verb="designed", target="recording-infra",
               params={"abstraction": 0.5, "maturity": 0.4})
        record(actions, sequences, registry,
               session=session, verb="abandoned", target="recording-infra",
               params={"abstraction": 0.5, "maturity": 0.4})

        set_sequence_intent(sequences, session, "build recording infrastructure")
        close_sequence(sequences, session, emit=False)

    return actions, sequences, registry


class TestVerbCycles:
    def test_detect_repeated_verb_sequence(self):
        actions, sequences, _ = _build_multi_session_data()
        cycles = detect_verb_cycles(actions, min_recurrence=2, window=3)
        # "explored -> designed -> abandoned" should appear in 3 sessions
        patterns = [c.pattern for c in cycles]
        assert any("explored -> designed -> abandoned" in p for p in patterns)

    def test_no_cycles_below_threshold(self):
        actions, sequences, _ = _build_multi_session_data()
        cycles = detect_verb_cycles(actions, min_recurrence=5, window=3)
        assert len(cycles) == 0

    def test_window_size_matters(self):
        actions, sequences, _ = _build_multi_session_data()
        # With window=2, we get 2-grams which might match more broadly
        cycles_w2 = detect_verb_cycles(actions, min_recurrence=2, window=2)
        cycles_w3 = detect_verb_cycles(actions, min_recurrence=2, window=3)
        assert len(cycles_w2) >= len(cycles_w3)


class TestTrajectoryCycles:
    def test_detect_repeated_trajectory(self):
        actions, sequences, _ = _build_multi_session_data()
        cycles = detect_trajectory_cycles(sequences, min_recurrence=2)
        # abstraction descended in all 3 sessions
        patterns = [c.pattern for c in cycles]
        assert any("abstraction" in p and "descended" in p for p in patterns)

    def test_no_trajectories_without_data(self):
        sequences = SequenceIndex()
        cycles = detect_trajectory_cycles(sequences, min_recurrence=2)
        assert len(cycles) == 0


class TestIntentCycles:
    def test_detect_repeated_intent(self):
        actions, sequences, _ = _build_multi_session_data()
        cycles = detect_intent_cycles(sequences, min_recurrence=2)
        patterns = [c.pattern for c in cycles]
        assert any("build recording infrastructure" in p for p in patterns)

    def test_no_intent_cycles_without_intents(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()
        record(actions, sequences, registry, session="S42", verb="a", target="x")
        cycles = detect_intent_cycles(sequences, min_recurrence=2)
        assert len(cycles) == 0


class TestStallDetection:
    def test_detect_stalled_parameter(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        # maturity stalls at 0.4 across 4 sequences
        for i in range(4):
            record(actions, sequences, registry,
                   session=f"S{40 + i}", verb="worked", target="thing",
                   params={"maturity": 0.4})
            close_sequence(sequences, f"S{40 + i}", emit=False)

        cycles = detect_stalls(sequences, min_sequences=3)
        assert len(cycles) >= 1
        assert any("maturity" in c.pattern and "stalled" in c.pattern for c in cycles)

    def test_no_stall_when_moving(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        for i in range(4):
            record(actions, sequences, registry,
                   session=f"S{40 + i}", verb="worked", target="thing",
                   params={"maturity": 0.2 * i})
            close_sequence(sequences, f"S{40 + i}", emit=False)

        cycles = detect_stalls(sequences, min_sequences=3)
        maturity_stalls = [c for c in cycles if "maturity" in c.pattern]
        assert len(maturity_stalls) == 0


class TestUnifiedDetection:
    def test_detect_all(self):
        actions, sequences, _ = _build_multi_session_data()
        all_cycles = detect_all_cycles(actions, sequences, min_recurrence=2)
        # Should find verb sequences, trajectories, AND intents
        types = {c.cycle_type for c in all_cycles}
        assert "verb_sequence" in types
        assert "trajectory" in types
        assert "intent" in types
