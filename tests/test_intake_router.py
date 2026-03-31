"""Tests for the keyword-based intake router."""

from __future__ import annotations

from action_ledger.ledger import load_actions
from action_ledger.schemas import ActionOrigin, RouteKind
from intake_router.cli import main
from intake_router.router import IntakeDomain, classify, emit_routing, route


def test_classify_organism():
    item = classify("third function build")
    assert item.domain == IntakeDomain.ORGANISM


def test_classify_transmutation():
    item = classify("exit interview spec")
    assert item.domain == IntakeDomain.TRANSMUTATION


def test_classify_emission():
    item = classify("wire emission into fieldwork")
    assert item.domain == IntakeDomain.EMISSION


def test_classify_unknown():
    item = classify("something random")
    assert item.domain == IntakeDomain.UNKNOWN
    assert item.suggested_agent == "claude"


def test_route_returns_workspace():
    dispatch = route(classify("third function build for a-organvm"))
    assert dispatch.workspace.endswith("/Workspace/a-organvm")
    assert dispatch.archetype == "I"
    assert "third function build for a-organvm" in dispatch.prompt


def test_emit_routing_records_action():
    dispatch = route(classify("wire emission into fieldwork"))
    emit_routing(dispatch)

    actions = load_actions().actions
    manual = [action for action in actions if action.origin == ActionOrigin.MANUAL]
    emitted = [action for action in actions if action.origin == ActionOrigin.EMITTED]

    assert len(manual) == 1
    assert len(emitted) == 1
    assert emitted[0].params["subsystem"] == "intake_router"
    assert emitted[0].params["domain"] == IntakeDomain.EMISSION.value
    assert any(route.kind == RouteKind.FEEDS for route in emitted[0].routes)


def test_cli_history_shows_dispatch(capsys):
    emit_routing(route(classify("third function build for a-organvm")))

    main(["history", "--limit", "1"])
    out = capsys.readouterr().out

    assert "organism" in out
    assert "codex/gemini" in out
