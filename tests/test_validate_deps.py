"""Tests for scripts/validate-deps.py — dependency direction validation."""
import json
import sys
from pathlib import Path

# Add scripts/ to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import with hyphenated filename
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "validate_deps",
    Path(__file__).parent.parent / "scripts" / "validate-deps.py",
)
validate_deps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_deps)


class TestOrgToOrganMapping:
    """Test the ORG_TO_ORGAN constant."""

    def test_all_supported_orgs_mapped(self):
        mapping = validate_deps.ORG_TO_ORGAN
        expected = {
            "organvm-i-theoria": "ORGAN-I",
            "organvm-ii-poiesis": "ORGAN-II",
            "organvm-iii-ergon": "ORGAN-III",
            "organvm-iv-taxis": "ORGAN-IV",
            "organvm-v-logos": "ORGAN-V",
            "organvm-vi-koinonia": "ORGAN-VI",
            "organvm-vii-kerygma": "ORGAN-VII",
            "meta-organvm": "META-ORGANVM",
        }
        assert mapping == expected

    def test_organ_values_format(self):
        for value in validate_deps.ORG_TO_ORGAN.values():
            assert value.startswith("ORGAN-") or value == "META-ORGANVM"


class TestLoadRegistry:
    """Test load_registry() fallback and redirect behavior."""

    def test_missing_registry_falls_back_to_default_candidate(self, tmp_path, monkeypatch):
        canonical = tmp_path / "registry-v2.json"
        canonical.write_text(
            json.dumps({"version": "2.0", "organs": {}}),
            encoding="utf-8",
        )
        monkeypatch.setattr(validate_deps, "DEFAULT_REGISTRY_CANDIDATES", (canonical,))

        loaded = validate_deps.load_registry(str(tmp_path / "missing-registry.json"))
        assert loaded["organs"] == {}

    def test_redirect_registry_follows_default_candidate(self, tmp_path, monkeypatch):
        redirect = tmp_path / "registry.json"
        redirect.write_text(
            json.dumps({"_redirect": "Use registry-v2.json"}),
            encoding="utf-8",
        )
        canonical = tmp_path / "registry-v2.json"
        canonical.write_text(
            json.dumps({"version": "2.0", "organs": {}}),
            encoding="utf-8",
        )
        monkeypatch.setattr(validate_deps, "DEFAULT_REGISTRY_CANDIDATES", (canonical,))

        loaded = validate_deps.load_registry(str(redirect))
        assert loaded["version"] == "2.0"


class TestValidate:
    """Test the validate() function."""

    def test_valid_registry_returns_zero(self, valid_registry, governance_rules, write_json):
        reg_path = write_json(valid_registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 0

    def test_back_edge_detected(self, registry_with_back_edge, governance_rules, write_json):
        reg_path = write_json(registry_with_back_edge, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        violations = validate_deps.validate(str(reg_path), str(gov_path))
        assert violations > 0

    def test_back_edge_organ_i_to_ii(self, governance_rules, write_json):
        """ORGAN-I cannot depend on ORGAN-II (I has no allowed deps)."""
        registry = {
            "organs": {
                "ORGAN-I": {
                    "repositories": [
                        {
                            "name": "bad-repo",
                            "org": "organvm-i-theoria",
                            "dependencies": ["organvm-ii-poiesis/some-repo"],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 1

    def test_back_edge_organ_ii_to_iii(self, governance_rules, write_json):
        """ORGAN-II can depend on ORGAN-I but not ORGAN-III."""
        registry = {
            "organs": {
                "ORGAN-II": {
                    "repositories": [
                        {
                            "name": "bad-repo",
                            "org": "organvm-ii-poiesis",
                            "dependencies": ["organvm-iii-ergon/some-repo"],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 1

    def test_allowed_organ_ii_to_i(self, governance_rules, write_json):
        """ORGAN-II depending on ORGAN-I is allowed."""
        registry = {
            "organs": {
                "ORGAN-II": {
                    "repositories": [
                        {
                            "name": "ok-repo",
                            "org": "organvm-ii-poiesis",
                            "dependencies": ["organvm-i-theoria/some-repo"],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 0

    def test_organ_vii_can_depend_on_v(self, governance_rules, write_json):
        """ORGAN-VII is allowed to depend on ORGAN-V."""
        registry = {
            "organs": {
                "ORGAN-VII": {
                    "repositories": [
                        {
                            "name": "amplifier",
                            "org": "organvm-vii-kerygma",
                            "dependencies": ["organvm-v-logos/essays"],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 0

    def test_organ_vii_cannot_depend_on_i(self, governance_rules, write_json):
        """ORGAN-VII can only depend on ORGAN-V."""
        registry = {
            "organs": {
                "ORGAN-VII": {
                    "repositories": [
                        {
                            "name": "bad-amplifier",
                            "org": "organvm-vii-kerygma",
                            "dependencies": ["organvm-i-theoria/some-repo"],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 1

    def test_same_organ_deps_allowed(self, governance_rules, write_json):
        """Dependencies within the same organ are always allowed."""
        registry = {
            "organs": {
                "ORGAN-I": {
                    "repositories": [
                        {
                            "name": "repo-a",
                            "org": "organvm-i-theoria",
                            "dependencies": ["organvm-i-theoria/repo-b"],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 0

    def test_empty_registry_returns_zero(self, empty_registry, governance_rules, write_json):
        reg_path = write_json(empty_registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 0

    def test_multiple_violations_counted(self, governance_rules, write_json):
        """Multiple violations in the same repo are counted individually."""
        registry = {
            "organs": {
                "ORGAN-I": {
                    "repositories": [
                        {
                            "name": "multi-bad",
                            "org": "organvm-i-theoria",
                            "dependencies": [
                                "organvm-ii-poiesis/art",
                                "organvm-iii-ergon/tool",
                            ],
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 2

    def test_repos_without_dependencies_skipped(self, governance_rules, write_json):
        """Repos with no dependencies should not produce violations."""
        registry = {
            "organs": {
                "ORGAN-I": {
                    "repositories": [
                        {
                            "name": "clean-repo",
                            "org": "organvm-i-theoria",
                        },
                    ],
                },
            },
        }
        reg_path = write_json(registry, "registry.json")
        gov_path = write_json(governance_rules, "governance.json")
        assert validate_deps.validate(str(reg_path), str(gov_path)) == 0
