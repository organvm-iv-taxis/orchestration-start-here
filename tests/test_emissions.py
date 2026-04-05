"""Tests for the emission layer — state changes that expel energy."""

from __future__ import annotations

from action_ledger.emissions import emit_state_change
from action_ledger.ledger import (
    close_sequence,
    close_session,
    compose_chain,
    load_actions,
    record,
    save_actions,
    save_param_registry,
    save_sequences,
)
from action_ledger.schemas import (
    ActionIndex,
    ActionOrigin,
    ChainIndex,
    ParamRegistry,
    SequenceIndex,
)


class TestEmitStateChange:
    """Core emission function."""

    def test_emit_creates_action_with_emitted_origin(self, tmp_path, monkeypatch):
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path)

        # Seed empty indexes
        save_actions(ActionIndex(), tmp_path / "actions.yaml")
        save_sequences(SequenceIndex(), tmp_path / "sequences.yaml")
        save_param_registry(ParamRegistry(), tmp_path / "param_registry.yaml")

        action = emit_state_change(
            subsystem="test_subsystem",
            verb="tested_emission",
            target="test_entity",
            from_state="alpha",
            to_state="beta",
            session="S-test",
        )

        assert action is not None
        assert action.origin == ActionOrigin.EMITTED
        assert action.verb == "tested_emission"
        assert action.params["subsystem"] == "test_subsystem"
        assert action.params["from_state"] == "alpha"
        assert action.params["to_state"] == "beta"

    def test_emit_creates_continues_route(self, tmp_path, monkeypatch):
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path)

        save_actions(ActionIndex(), tmp_path / "actions.yaml")
        save_sequences(SequenceIndex(), tmp_path / "sequences.yaml")
        save_param_registry(ParamRegistry(), tmp_path / "param_registry.yaml")

        action = emit_state_change(
            subsystem="action_ledger",
            verb="closed_sequence",
            target="seq-S42-001",
            from_state="open",
            to_state="closed",
        )

        assert action is not None
        assert len(action.routes) >= 1
        continues = [r for r in action.routes if r.kind == "continues"]
        assert len(continues) == 1
        assert continues[0].target == "seq-S42-001"

    def test_emit_persists_to_disk(self, tmp_path, monkeypatch):
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path)

        save_actions(ActionIndex(), tmp_path / "actions.yaml")
        save_sequences(SequenceIndex(), tmp_path / "sequences.yaml")
        save_param_registry(ParamRegistry(), tmp_path / "param_registry.yaml")

        emit_state_change(
            subsystem="test",
            verb="persisted",
            target="entity",
            from_state="a",
            to_state="b",
        )

        reloaded = load_actions(tmp_path / "actions.yaml")
        assert len(reloaded.actions) == 1
        assert reloaded.actions[0].origin == ActionOrigin.EMITTED

    def test_emit_returns_none_on_failure(self, tmp_path, monkeypatch):
        # Force load_actions to raise by pointing at a path with corrupt data
        bad_path = tmp_path / "bad"
        bad_path.mkdir()
        (bad_path / "actions.yaml").write_text("not: [valid: {yaml")
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", bad_path)

        result = emit_state_change(
            subsystem="test",
            verb="will_fail",
            target="entity",
            from_state="a",
            to_state="b",
        )

        # Should not crash — returns None
        assert result is None

    def test_emit_with_extra_params(self, tmp_path, monkeypatch):
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path)

        save_actions(ActionIndex(), tmp_path / "actions.yaml")
        save_sequences(SequenceIndex(), tmp_path / "sequences.yaml")
        save_param_registry(ParamRegistry(), tmp_path / "param_registry.yaml")

        action = emit_state_change(
            subsystem="action_ledger",
            verb="composed_chain",
            target="chain-S42-001",
            from_state="sequences",
            to_state="chain",
            params={"sequence_count": 3.0},
        )

        assert action is not None
        assert action.params["sequence_count"] == 3.0

    def test_emit_with_produced(self, tmp_path, monkeypatch):
        monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path)

        save_actions(ActionIndex(), tmp_path / "actions.yaml")
        save_sequences(SequenceIndex(), tmp_path / "sequences.yaml")
        save_param_registry(ParamRegistry(), tmp_path / "param_registry.yaml")

        action = emit_state_change(
            subsystem="action_ledger",
            verb="closed_session",
            target="S42",
            from_state="active",
            to_state="closed",
            produced=[{"type": "chain", "ref": "chain-S42-001"}],
        )

        assert action is not None
        assert len(action.produced) == 1
        assert action.produced[0].type == "chain"


class TestEmissionOptOut:
    """Emission suppression via emit=False."""

    def test_close_sequence_suppresses_emission(self):
        sequences = SequenceIndex()
        actions = ActionIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork")

        # Suppress emission — should not attempt disk I/O
        seq = close_sequence(sequences, "S42", emit=False)
        assert seq is not None
        assert seq.closed is True

    def test_compose_chain_suppresses_emission(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()
        chains = ChainIndex()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork")

        chain = compose_chain(sequences, chains, "S42", emit=False)
        assert chain is not None

    def test_close_session_suppresses_emission(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()
        chains = ChainIndex()

        record(actions, sequences, registry,
               session="S42", verb="explored", target="fieldwork")

        chain = close_session(sequences, chains, "S42", emit=False)
        assert chain is not None


class TestActionOriginSchema:
    """ActionOrigin field on Action model."""

    def test_default_origin_is_manual(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        action = record(actions, sequences, registry,
                        session="S42", verb="test", target="thing")
        assert action.origin == ActionOrigin.MANUAL

    def test_explicit_emitted_origin(self):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        action = record(actions, sequences, registry,
                        session="S42", verb="test", target="thing",
                        origin=ActionOrigin.EMITTED)
        assert action.origin == ActionOrigin.EMITTED

    def test_origin_serializes_to_yaml(self, tmp_path):
        actions = ActionIndex()
        sequences = SequenceIndex()
        registry = ParamRegistry()

        record(actions, sequences, registry,
               session="S42", verb="test", target="thing",
               origin=ActionOrigin.EMITTED)

        path = tmp_path / "actions.yaml"
        save_actions(actions, path)
        reloaded = load_actions(path)
        assert reloaded.actions[0].origin == ActionOrigin.EMITTED
