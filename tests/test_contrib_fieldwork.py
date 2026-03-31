"""Tests for the fieldwork intelligence system."""

from contrib_engine.schemas import (
    FieldObservation,
    FieldworkIndex,
    ObservationCategory,
    ObservationSource,
    SpectrumLevel,
    StrategicTag,
)


class TestFieldObservationModel:
    def test_spectrum_ordering(self):
        assert SpectrumLevel.AVOID < SpectrumLevel.NOTE
        assert SpectrumLevel.NOTE < SpectrumLevel.STUDY
        assert SpectrumLevel.STUDY < SpectrumLevel.ABSORB

    def test_strategic_multiple_tags(self):
        obs = FieldObservation(
            id="fo-test-0330-001",
            workspace="contrib--test",
            timestamp="2026-03-30T12:00:00",
            category=ObservationCategory.CI_ARCHITECTURE,
            signal="Test signal",
            spectrum=SpectrumLevel.STUDY,
            strategic=[StrategicTag.SHATTERPOINT, StrategicTag.COMPETITIVE_GAP],
            source=ObservationSource.REPO_EXPLORATION,
        )
        assert len(obs.strategic) == 2
        assert StrategicTag.SHATTERPOINT in obs.strategic

    def test_atom_id_defaults_empty(self):
        obs = FieldObservation(
            id="fo-test-0330-001",
            workspace="contrib--test",
            timestamp="2026-03-30T12:00:00",
            category=ObservationCategory.TOOLING,
            signal="Test",
            spectrum=SpectrumLevel.NOTE,
            source=ObservationSource.AUTOMATED,
        )
        assert obs.atom_id == ""

    def test_spectrum_integer_values(self):
        assert SpectrumLevel.AVOID == -2
        assert SpectrumLevel.CAUTION == -1
        assert SpectrumLevel.NOTE == 0
        assert SpectrumLevel.STUDY == 1
        assert SpectrumLevel.ABSORB == 2


class TestRecord:
    def test_record_appends_observation(self):
        from contrib_engine.fieldwork import record

        index = FieldworkIndex(generated="2026-03-30")
        obs = record(
            index,
            workspace="contrib--dbt-mcp",
            category="ci_architecture",
            signal="GitHub Actions matrix with 3 Python versions",
            spectrum=1,
            source="repo_exploration",
        )
        assert len(index.observations) == 1
        assert obs.category == ObservationCategory.CI_ARCHITECTURE
        assert obs.spectrum == SpectrumLevel.STUDY

    def test_record_generates_sequential_ids(self):
        from contrib_engine.fieldwork import record

        index = FieldworkIndex(generated="2026-03-30")
        obs1 = record(index, "contrib--dbt-mcp", "tooling", "Signal A", 0, "automated")
        obs2 = record(index, "contrib--dbt-mcp", "governance", "Signal B", 1, "automated")

        # Same workspace, same day — sequential numbering
        assert obs1.id.endswith("-001")
        assert obs2.id.endswith("-002")

    def test_record_strips_contrib_prefix_from_id(self):
        from contrib_engine.fieldwork import record

        index = FieldworkIndex(generated="2026-03-30")
        obs = record(index, "contrib--dbt-mcp", "tooling", "Signal", 0, "automated")
        assert "contrib--" not in obs.id
        assert "dbt-mcp" in obs.id

    def test_record_with_strategic_tags(self):
        from contrib_engine.fieldwork import record

        index = FieldworkIndex(generated="2026-03-30")
        obs = record(
            index,
            workspace="contrib--a2a-python",
            category="merge_protocol",
            signal="Requires signed commits",
            spectrum=-1,
            source="pr_submission",
            strategic=["friction_point", "missing_shield"],
        )
        assert len(obs.strategic) == 2
        assert obs.spectrum == SpectrumLevel.CAUTION


class TestFieldworkIndex:
    def _make_index(self):
        return FieldworkIndex(
            generated="2026-03-30",
            observations=[
                FieldObservation(
                    id="fo-dbt-mcp-0330-001", workspace="contrib--dbt-mcp",
                    timestamp="2026-03-30T10:00:00", category=ObservationCategory.CI_ARCHITECTURE,
                    signal="CI signal", spectrum=SpectrumLevel.STUDY,
                    source=ObservationSource.REPO_EXPLORATION,
                ),
                FieldObservation(
                    id="fo-dbt-mcp-0330-002", workspace="contrib--dbt-mcp",
                    timestamp="2026-03-30T10:05:00", category=ObservationCategory.TOOLING,
                    signal="Tool signal", spectrum=SpectrumLevel.NOTE,
                    source=ObservationSource.AUTOMATED,
                ),
                FieldObservation(
                    id="fo-a2a-0330-001", workspace="contrib--a2a-python",
                    timestamp="2026-03-30T11:00:00", category=ObservationCategory.CI_ARCHITECTURE,
                    signal="A2A CI", spectrum=SpectrumLevel.ABSORB,
                    source=ObservationSource.PR_SUBMISSION,
                ),
            ],
        )

    def test_by_workspace_filters(self):
        index = self._make_index()
        result = index.by_workspace("contrib--dbt-mcp")
        assert len(result) == 2

    def test_by_category_filters(self):
        index = self._make_index()
        result = index.by_category(ObservationCategory.CI_ARCHITECTURE)
        assert len(result) == 2

    def test_by_spectrum_filters_gte(self):
        index = self._make_index()
        result = index.by_spectrum(SpectrumLevel.STUDY)
        assert len(result) == 2  # STUDY + ABSORB


class TestPersistence:
    def test_save_and_load_roundtrip(self, tmp_path):
        from contrib_engine.fieldwork import load_fieldwork, record, save_fieldwork

        index = FieldworkIndex(generated="2026-03-30")
        record(index, "contrib--dbt-mcp", "tooling", "Ruff linter configured", 1, "repo_exploration")
        path = save_fieldwork(index, tmp_path / "fieldwork.yaml")

        loaded = load_fieldwork(path)
        assert len(loaded.observations) == 1
        assert loaded.observations[0].spectrum == SpectrumLevel.STUDY

    def test_load_missing_returns_empty(self, tmp_path):
        from contrib_engine.fieldwork import load_fieldwork

        loaded = load_fieldwork(tmp_path / "nonexistent.yaml")
        assert len(loaded.observations) == 0

    def test_append_preserves_existing(self, tmp_path):
        from contrib_engine.fieldwork import load_fieldwork, record, save_fieldwork

        index = FieldworkIndex(generated="2026-03-30")
        record(index, "contrib--dbt-mcp", "tooling", "First", 0, "automated")
        save_fieldwork(index, tmp_path / "fieldwork.yaml")

        reloaded = load_fieldwork(tmp_path / "fieldwork.yaml")
        record(reloaded, "contrib--dbt-mcp", "governance", "Second", 1, "automated")
        save_fieldwork(reloaded, tmp_path / "fieldwork.yaml")

        final = load_fieldwork(tmp_path / "fieldwork.yaml")
        assert len(final.observations) == 2
