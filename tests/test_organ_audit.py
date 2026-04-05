"""Tests for scripts/organ-audit.py — monthly organ audit."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "organ_audit",
    Path(__file__).parent.parent / "scripts" / "organ-audit.py",
)
organ_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(organ_audit)


class TestFindCycles:
    """Test the find_cycles() function."""

    def test_no_cycles_in_dag(self):
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": [],
        }
        assert organ_audit.find_cycles(graph) == []

    def test_simple_cycle_detected(self):
        graph = {
            "a": ["b"],
            "b": ["a"],
        }
        cycles = organ_audit.find_cycles(graph)
        assert len(cycles) > 0

    def test_self_loop_detected(self):
        graph = {
            "a": ["a"],
        }
        cycles = organ_audit.find_cycles(graph)
        assert len(cycles) > 0

    def test_longer_cycle_detected(self):
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"],
        }
        cycles = organ_audit.find_cycles(graph)
        assert len(cycles) > 0

    def test_empty_graph(self):
        assert organ_audit.find_cycles({}) == []

    def test_disconnected_nodes(self):
        graph = {
            "a": [],
            "b": [],
            "c": [],
        }
        assert organ_audit.find_cycles(graph) == []


class TestValidateDependencyDirections:
    """Test the validate_dependency_directions() function."""

    def test_valid_deps_no_violations(self, valid_registry, governance_rules):
        violations = organ_audit.validate_dependency_directions(
            valid_registry, governance_rules
        )
        assert violations == []

    def test_back_edge_violation(self, registry_with_back_edge, governance_rules):
        violations = organ_audit.validate_dependency_directions(
            registry_with_back_edge, governance_rules
        )
        assert len(violations) == 1
        assert "ORGAN-II" in violations[0]

    def test_empty_registry_no_violations(self, empty_registry, governance_rules):
        violations = organ_audit.validate_dependency_directions(
            empty_registry, governance_rules
        )
        assert violations == []


class TestAuditOrgans:
    """Test the audit_organs() function."""

    def test_clean_audit_no_critical(self, valid_registry, governance_rules, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        report, alerts = organ_audit.audit_organs(str(reg_path), str(gov_path))

        assert alerts["critical"] == []
        assert "No violations" in report or "None" in report

    def test_back_edge_produces_critical(
        self, registry_with_back_edge, governance_rules, write_json
    ):
        reg_path = write_json(registry_with_back_edge, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        report, alerts = organ_audit.audit_organs(str(reg_path), str(gov_path))

        assert len(alerts["critical"]) > 0
        assert any("violation" in a.lower() or "Direction" in a for a in alerts["critical"])

    def test_cycle_produces_critical(
        self, registry_with_cycle, governance_rules, write_json
    ):
        reg_path = write_json(registry_with_cycle, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        report, alerts = organ_audit.audit_organs(str(reg_path), str(gov_path))

        assert any("ircular" in a for a in alerts["critical"])

    def test_undocumented_repos_produce_warnings(
        self, registry_with_undocumented, governance_rules, write_json
    ):
        reg_path = write_json(registry_with_undocumented, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        report, alerts = organ_audit.audit_organs(str(reg_path), str(gov_path))

        assert len(alerts["warning"]) > 0
        assert any("undocumented-repo" in w for w in alerts["warning"])

    def test_planned_repos_excluded_from_warnings(
        self, registry_with_undocumented, governance_rules, write_json
    ):
        """Repos with NOT_CREATED in note should not trigger undocumented warnings."""
        reg_path = write_json(registry_with_undocumented, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        _, alerts = organ_audit.audit_organs(str(reg_path), str(gov_path))

        for warning in alerts["warning"]:
            assert "planned-repo" not in warning

    def test_report_contains_organ_sections(
        self, valid_registry, governance_rules, write_json
    ):
        reg_path = write_json(valid_registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        report, _ = organ_audit.audit_organs(str(reg_path), str(gov_path))

        assert "Organ Status" in report
        assert "Dependency Validation" in report
        assert "Alerts" in report
        assert "Metrics" in report

    def test_empty_registry_audit(self, empty_registry, governance_rules, write_json):
        reg_path = write_json(empty_registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        report, alerts = organ_audit.audit_organs(str(reg_path), str(gov_path))

        assert alerts["critical"] == []
        assert isinstance(report, str)
