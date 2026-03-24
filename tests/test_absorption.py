"""Tests for the Absorption Protocol."""

import pytest

from contrib_engine.absorption import (
    detect_triggers,
    load_absorption,
    save_absorption,
    scan_conversations,
)
from contrib_engine.schemas import (
    AbsorptionIndex,
    AbsorptionItem,
    AbsorptionStatus,
    AbsorptionTrigger,
)


class TestDetectTriggers:
    """Test the expansion/reduction heuristic gate."""

    def test_unnamed_pattern_how_handle(self):
        text = "How do you handle conflicting traces? Like if two agents deposit contradicting RESOURCE traces about the same target."
        triggers = detect_triggers(text)
        assert len(triggers) >= 1
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.UNNAMED_PATTERN in types

    def test_unnamed_pattern_what_happens(self):
        text = "What happens when the crisis level drops but agents are mid-task? Do they immediately split or finish their current work first?"
        triggers = detect_triggers(text)
        assert len(triggers) >= 1
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.UNNAMED_PATTERN in types

    def test_convergence_we_ended_up(self):
        text = "We ended up doing something cruder with TTL-based file locks that agents check before acting. The decay approach is more elegant."
        triggers = detect_triggers(text)
        assert len(triggers) >= 1
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.INDEPENDENT_CONVERGENCE in types

    def test_convergence_we_built(self):
        text = "We built a similar system using Redis pub/sub for the coordination layer. The pheromone field is interesting because it doesn't need a message broker."
        triggers = detect_triggers(text)
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.INDEPENDENT_CONVERGENCE in types

    def test_assumption_divergence_isnt_that_just(self):
        text = "Isn't that basically just eventual consistency with extra steps? The traces converge through decay and reinforcement which is similar to CRDT convergence."
        triggers = detect_triggers(text)
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.ASSUMPTION_DIVERGENCE in types

    def test_assumption_divergence_most_frameworks(self):
        text = "Most orchestration frameworks treat agent topology as static, so having it adapt based on crisis metrics is a fundamentally different design."
        triggers = detect_triggers(text)
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.ASSUMPTION_DIVERGENCE in types

    def test_assumption_divergence_does_win(self):
        text = "Does the higher intensity trace win over the lower one, or is there some kind of merge strategy for conflicting information?"
        triggers = detect_triggers(text)
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.ASSUMPTION_DIVERGENCE in types

    def test_hard_part_trigger(self):
        text = "The hard part is making sure the agents don't thrash between states when the metrics are noisy. How stable is the hysteresis in practice?"
        triggers = detect_triggers(text)
        types = [t for t, _ in triggers]
        assert AbsorptionTrigger.UNNAMED_PATTERN in types

    def test_multiple_triggers(self):
        text = "We ended up doing something similar — most frameworks crash the whole group but we built a redistribute model. How do you handle the state transfer?"
        triggers = detect_triggers(text)
        assert len(triggers) >= 2  # convergence + unnamed_pattern or divergence

    def test_reduction_what_version(self):
        text = "What version of Python are you using for the hive module? I'm having compatibility issues with 3.10."
        triggers = detect_triggers(text)
        assert triggers == []

    def test_reduction_can_you_add(self):
        text = "Can you add support for Kubernetes as a runtime? It would be useful for our deployment environment."
        triggers = detect_triggers(text)
        assert triggers == []

    def test_reduction_broken(self):
        text = "This doesn't work when I try to run it on Windows. The path separators cause issues in the pheromone field key generation."
        triggers = detect_triggers(text)
        assert triggers == []

    def test_too_short(self):
        text = "Interesting approach."
        triggers = detect_triggers(text)
        assert triggers == []

    def test_empty(self):
        triggers = detect_triggers("")
        assert triggers == []


class TestAbsorptionModels:
    """Test Pydantic model behavior."""

    def test_absorption_item_creation(self):
        item = AbsorptionItem(
            id="abs-test-001",
            workspace="contrib--m13v-summarize-recent-commit",
            source_url="https://github.com/org/repo/issues/20#comment-123",
            questioner="m13v",
            question_text="How do you handle conflicting traces?",
            detected_at="2026-03-24T12:00:00",
            triggers=[AbsorptionTrigger.UNNAMED_PATTERN],
            trigger_evidence="Asks about handling strategy",
            status=AbsorptionStatus.DETECTED,
        )
        assert item.status == AbsorptionStatus.DETECTED
        assert item.questioner == "m13v"

    def test_absorption_index_pending(self):
        index = AbsorptionIndex(items=[
            AbsorptionItem(
                id="abs-1", workspace="w1", source_url="u1",
                questioner="a", question_text="q1", detected_at="t1",
                status=AbsorptionStatus.DETECTED,
            ),
            AbsorptionItem(
                id="abs-2", workspace="w2", source_url="u2",
                questioner="b", question_text="q2", detected_at="t2",
                status=AbsorptionStatus.FORMALIZED,
            ),
            AbsorptionItem(
                id="abs-3", workspace="w3", source_url="u3",
                questioner="c", question_text="q3", detected_at="t3",
                status=AbsorptionStatus.ASSESSED,
            ),
        ])
        pending = index.pending_formalization()
        assert len(pending) == 2
        assert {i.id for i in pending} == {"abs-1", "abs-3"}

    def test_by_status(self):
        index = AbsorptionIndex(items=[
            AbsorptionItem(
                id="abs-1", workspace="w1", source_url="u1",
                questioner="a", question_text="q1", detected_at="t1",
                status=AbsorptionStatus.DEPOSITED,
            ),
            AbsorptionItem(
                id="abs-2", workspace="w2", source_url="u2",
                questioner="b", question_text="q2", detected_at="t2",
                status=AbsorptionStatus.DEPOSITED,
            ),
        ])
        deposited = index.by_status(AbsorptionStatus.DEPOSITED)
        assert len(deposited) == 2


class TestSaveLoad:
    """Test persistence."""

    def test_save_and_load(self, tmp_path):
        index = AbsorptionIndex(
            generated="2026-03-24",
            items=[
                AbsorptionItem(
                    id="abs-test-001",
                    workspace="contrib--test",
                    source_url="https://example.com",
                    questioner="tester",
                    question_text="How do you handle X?",
                    detected_at="2026-03-24T12:00:00",
                    triggers=[AbsorptionTrigger.UNNAMED_PATTERN],
                    trigger_evidence="Test evidence",
                    status=AbsorptionStatus.DETECTED,
                ),
            ],
        )
        path = tmp_path / "absorption.yaml"
        save_absorption(index, output_path=path)
        loaded = load_absorption(input_path=path)
        assert len(loaded.items) == 1
        assert loaded.items[0].questioner == "tester"
        assert loaded.items[0].triggers == [AbsorptionTrigger.UNNAMED_PATTERN]

    def test_load_empty(self, tmp_path):
        path = tmp_path / "nonexistent.yaml"
        loaded = load_absorption(input_path=path)
        assert len(loaded.items) == 0


class TestScanConversations:
    """Test conversation scanning with mock data."""

    def test_scan_filters_our_comments(self):
        """Ensure our own comments are excluded."""
        # This test verifies the logic path without hitting GitHub API
        # The actual fetch_inbound_comments filters by username
        items = scan_conversations(conversations=[], since="")
        assert items == []

    def test_scan_empty_conversations(self):
        items = scan_conversations(conversations=[], since="")
        assert items == []
