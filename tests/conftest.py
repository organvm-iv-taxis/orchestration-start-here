"""Shared fixtures for orchestration-start-here tests."""
import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_ledger_data(tmp_path, monkeypatch):
    """Redirect action_ledger DATA_DIR to tmp_path for ALL tests.

    Prevents emission side effects from contaminating production
    data files (actions.yaml, sequences.yaml, param_registry.yaml).
    Without this, any test calling close_sequence/compose_chain/close_session
    with default emit=True writes to the real data directory.
    """
    monkeypatch.setattr("action_ledger.ledger.DATA_DIR", tmp_path)


@pytest.fixture
def governance_rules():
    """Governance rules matching production governance-rules.json structure."""
    return {
        "version": "1.0",
        "articles": {
            "I": {
                "title": "Registry as Single Source of Truth",
                "rule": "All repo state lives in registry.json.",
                "enforcement": "automated",
            },
            "II": {
                "title": "Unidirectional Dependencies",
                "rule": "Flow is I→II→III only.",
                "enforcement": "automated",
                "allowed_dependencies": {
                    "ORGAN-I": [],
                    "ORGAN-II": ["ORGAN-I"],
                    "ORGAN-III": ["ORGAN-I", "ORGAN-II"],
                    "ORGAN-IV": ["ORGAN-I", "ORGAN-II", "ORGAN-III"],
                    "ORGAN-V": ["ORGAN-I", "ORGAN-II", "ORGAN-III", "ORGAN-IV"],
                    "ORGAN-VI": ["ORGAN-I", "ORGAN-II", "ORGAN-III"],
                    "ORGAN-VII": ["ORGAN-V"],
                },
            },
            "VI": {
                "title": "Promotion State Machine",
                "rule": "LOCAL → CANDIDATE → PUBLIC_PROCESS → GRADUATED → ARCHIVED",
                "enforcement": "automated",
                "states": ["LOCAL", "CANDIDATE", "PUBLIC_PROCESS", "GRADUATED", "ARCHIVED"],
                "valid_transitions": {
                    "LOCAL": ["CANDIDATE"],
                    "CANDIDATE": ["PUBLIC_PROCESS"],
                    "PUBLIC_PROCESS": ["GRADUATED"],
                    "GRADUATED": ["ARCHIVED"],
                },
            },
        },
    }


@pytest.fixture
def valid_registry():
    """Registry with valid unidirectional dependencies (no back-edges)."""
    return {
        "organs": {
            "ORGAN-I": {
                "name": "Theoria",
                "launch_status": "COMPLETE",
                "repositories": [
                    {
                        "name": "recursive-engine",
                        "org": "organvm-i-theoria",
                        "dependencies": [],
                        "documentation_status": "DEPLOYED",
                        "tier": "flagship",
                    },
                    {
                        "name": "symbol-forge",
                        "org": "organvm-i-theoria",
                        "dependencies": [],
                        "documentation_status": "DEPLOYED",
                    },
                ],
            },
            "ORGAN-II": {
                "name": "Poiesis",
                "launch_status": "OPERATIONAL",
                "repositories": [
                    {
                        "name": "generative-art",
                        "org": "organvm-ii-poiesis",
                        "dependencies": ["organvm-i-theoria/recursive-engine"],
                        "documentation_status": "DEPLOYED",
                        "tier": "flagship",
                    },
                ],
            },
            "ORGAN-III": {
                "name": "Ergon",
                "launch_status": "LOCKED",
                "repositories": [
                    {
                        "name": "saas-tool",
                        "org": "organvm-iii-ergon",
                        "dependencies": [
                            "organvm-i-theoria/recursive-engine",
                            "organvm-ii-poiesis/generative-art",
                        ],
                        "documentation_status": "FLAGSHIP README DEPLOYED",
                        "tier": "flagship",
                    },
                ],
            },
        },
    }


@pytest.fixture
def registry_with_back_edge():
    """Registry with a forbidden back-edge: ORGAN-I depends on ORGAN-II."""
    return {
        "organs": {
            "ORGAN-I": {
                "name": "Theoria",
                "launch_status": "COMPLETE",
                "repositories": [
                    {
                        "name": "recursive-engine",
                        "org": "organvm-i-theoria",
                        "dependencies": ["organvm-ii-poiesis/generative-art"],
                        "documentation_status": "DEPLOYED",
                    },
                ],
            },
            "ORGAN-II": {
                "name": "Poiesis",
                "launch_status": "OPERATIONAL",
                "repositories": [
                    {
                        "name": "generative-art",
                        "org": "organvm-ii-poiesis",
                        "dependencies": [],
                        "documentation_status": "DEPLOYED",
                    },
                ],
            },
        },
    }


@pytest.fixture
def registry_with_cycle():
    """Registry with a circular dependency."""
    return {
        "organs": {
            "ORGAN-II": {
                "name": "Poiesis",
                "launch_status": "OPERATIONAL",
                "repositories": [
                    {
                        "name": "art-a",
                        "org": "organvm-ii-poiesis",
                        "dependencies": ["organvm-ii-poiesis/art-b"],
                    },
                    {
                        "name": "art-b",
                        "org": "organvm-ii-poiesis",
                        "dependencies": ["organvm-ii-poiesis/art-a"],
                    },
                ],
            },
        },
    }


@pytest.fixture
def registry_with_undocumented():
    """Registry with repos missing documentation."""
    return {
        "organs": {
            "ORGAN-I": {
                "name": "Theoria",
                "launch_status": "COMPLETE",
                "repositories": [
                    {
                        "name": "documented-repo",
                        "org": "organvm-i-theoria",
                        "dependencies": [],
                        "documentation_status": "DEPLOYED",
                        "tier": "flagship",
                    },
                    {
                        "name": "undocumented-repo",
                        "org": "organvm-i-theoria",
                        "dependencies": [],
                        "documentation_status": "PENDING",
                    },
                    {
                        "name": "planned-repo",
                        "org": "organvm-i-theoria",
                        "dependencies": [],
                        "documentation_status": "",
                        "note": "NOT_CREATED",
                    },
                ],
            },
        },
    }


@pytest.fixture
def empty_registry():
    """Registry with no organs or repos."""
    return {"organs": {}}


@pytest.fixture
def write_json(tmp_path):
    """Helper to write a dict as JSON to a temp file."""
    def _write(data: dict, filename: str) -> Path:
        path = tmp_path / filename
        path.write_text(json.dumps(data, indent=2))
        return path
    return _write
