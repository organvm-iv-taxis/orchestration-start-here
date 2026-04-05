"""Tests for scripts/calculate-metrics.py — system-wide metrics calculation."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "calculate_metrics",
    Path(__file__).parent.parent / "scripts" / "calculate-metrics.py",
)
calculate_metrics_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(calculate_metrics_mod)


class TestCalculateMetrics:
    """Test the calculate_metrics() function."""

    def test_valid_registry_metrics(self, valid_registry, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        assert metrics["total_repos"] == 4
        assert metrics["total_organs"] == 3
        assert metrics["flagship_repos"] == 3
        assert "date" in metrics

    def test_empty_registry(self, empty_registry, write_json):
        reg_path = write_json(empty_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        assert metrics["total_repos"] == 0
        assert metrics["total_organs"] == 0
        assert metrics["flagship_repos"] == 0
        assert metrics["completion"] == 0.0

    def test_dependency_counting(self, valid_registry, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        # ORGAN-II has 1 dep, ORGAN-III has 2 deps = 3 total
        assert metrics["total_dependencies"] == 3
        assert metrics["repos_with_dependencies"] == 2

    def test_documentation_counting(self, valid_registry, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        # All 4 repos have docs: 3 DEPLOYED + 1 FLAGSHIP README DEPLOYED
        assert metrics["documented_repos"] == 4

    def test_operational_organs(self, valid_registry, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        # COMPLETE, OPERATIONAL, LOCKED all count as operational
        assert metrics["operational_organs"] == 3

    def test_completion_percentage(self, write_json):
        registry = {
            "organs": {
                "ORGAN-I": {
                    "name": "Theoria",
                    "repositories": [
                        {
                            "name": "repo-1",
                            "org": "organvm-i-theoria",
                            "documentation_status": "DEPLOYED",
                        },
                        {
                            "name": "repo-2",
                            "org": "organvm-i-theoria",
                            "documentation_status": "PENDING",
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        # 1 documented / 2 on github = 50%
        assert metrics["completion"] == 50.0

    def test_planned_repos_excluded_from_github_count(self, write_json):
        registry = {
            "organs": {
                "ORGAN-I": {
                    "name": "Theoria",
                    "repositories": [
                        {
                            "name": "on-github",
                            "org": "organvm-i-theoria",
                            "documentation_status": "DEPLOYED",
                        },
                        {
                            "name": "planned",
                            "org": "organvm-i-theoria",
                            "note": "NOT_CREATED — planned for Phase 2",
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        assert metrics["repos_on_github"] == 1
        assert metrics["repos_planned"] == 1

    def test_per_organ_breakdown(self, valid_registry, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        assert "ORGAN-I" in metrics["organs"]
        assert "ORGAN-II" in metrics["organs"]
        assert "ORGAN-III" in metrics["organs"]

        organ_i = metrics["organs"]["ORGAN-I"]
        assert organ_i["repos"] == 2
        assert organ_i["name"] == "Theoria"

    def test_output_structure(self, valid_registry, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        metrics = calculate_metrics_mod.calculate_metrics(str(reg_path))

        required_keys = [
            "date", "total_repos", "repos_on_github", "repos_planned",
            "documented_repos", "flagship_repos", "operational_organs",
            "total_organs", "total_dependencies", "repos_with_dependencies",
            "critical_alerts", "warnings", "completion", "organs",
        ]
        for key in required_keys:
            assert key in metrics, f"Missing key: {key}"
