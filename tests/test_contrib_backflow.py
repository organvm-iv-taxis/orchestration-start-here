"""Tests for the backflow pipeline."""

from contrib_engine.schemas import BackflowIndex, BackflowItem, BackflowStatus, BackflowType


class TestAddItem:
    def test_adds_item(self):
        from contrib_engine.backflow import add_item
        index = BackflowIndex(generated="2026-03-22")
        add_item(index, "contrib--adenhq-hive", "I", "theory", "Forward-only lifecycle pattern")
        assert len(index.items) == 1
        assert index.items[0].organ == "I"
        assert index.items[0].backflow_type == BackflowType.THEORY

    def test_adds_multiple_items(self):
        from contrib_engine.backflow import add_item
        index = BackflowIndex(generated="2026-03-22")
        add_item(index, "w", "I", "theory", "Pattern A")
        add_item(index, "w", "II", "generative", "Diagram B")
        add_item(index, "w", "V", "narrative", "Essay C")
        assert len(index.items) == 3


class TestDepositItem:
    def test_deposits_item(self):
        from contrib_engine.backflow import deposit_item
        index = BackflowIndex(
            generated="2026-03-22",
            items=[BackflowItem(workspace="w", organ="I", backflow_type=BackflowType.THEORY, title="T", description="D")],
        )
        assert deposit_item(index, 0)
        assert index.items[0].status == BackflowStatus.DEPOSITED
        assert index.items[0].deposited_at != ""

    def test_deposit_invalid_index(self):
        from contrib_engine.backflow import deposit_item
        index = BackflowIndex(generated="2026-03-22")
        assert not deposit_item(index, 0)


class TestPendingByOrgan:
    def test_groups_pending(self):
        index = BackflowIndex(
            generated="2026-03-22",
            items=[
                BackflowItem(workspace="w", organ="I", backflow_type=BackflowType.THEORY, title="A", description=""),
                BackflowItem(workspace="w", organ="I", backflow_type=BackflowType.CODE, title="B", description=""),
                BackflowItem(workspace="w", organ="V", backflow_type=BackflowType.NARRATIVE, title="C", description=""),
                BackflowItem(workspace="w", organ="I", backflow_type=BackflowType.THEORY, title="D", description="", status=BackflowStatus.DEPOSITED),
            ],
        )
        pending = index.pending_by_organ()
        assert len(pending["I"]) == 2
        assert len(pending["V"]) == 1

    def test_empty_returns_empty(self):
        index = BackflowIndex(generated="2026-03-22")
        assert index.pending_by_organ() == {}


class TestPersistence:
    def test_save_and_load_roundtrip(self, tmp_path):
        from contrib_engine.backflow import load_backflow, save_backflow
        index = BackflowIndex(
            generated="2026-03-22",
            items=[BackflowItem(workspace="w", organ="I", backflow_type=BackflowType.THEORY, title="T", description="D")],
        )
        path = save_backflow(index, tmp_path / "backflow.yaml")
        loaded = load_backflow(path)
        assert len(loaded.items) == 1
        assert loaded.items[0].backflow_type == BackflowType.THEORY
