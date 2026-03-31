"""Fieldwork Intelligence — process observations from contribution workflows.

Captures what we see while contributing: merge protocols, review culture,
CI architecture, tooling, governance patterns. Each observation is scored
on a spectrum from AVOID (-2) to ABSORB (+2) and tagged with strategic
significance (shatterpoint, fortress, friction point, etc.).

Append-only stream with rotation at 500 entries (rotation not in MVP).
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

from contrib_engine.schemas import (
    FieldObservation,
    FieldworkIndex,
    ObservationCategory,
    ObservationSource,
    SpectrumLevel,
    StrategicTag,
)

DATA_DIR = Path(__file__).parent / "data"


def record(
    index: FieldworkIndex,
    workspace: str,
    category: str | ObservationCategory,
    signal: str,
    spectrum: int | SpectrumLevel,
    source: str | ObservationSource,
    evidence: str = "",
    strategic: list[str | StrategicTag] | None = None,
    scored_by: str = "agent",
    related_absorption_ids: list[str] | None = None,
) -> FieldObservation:
    """Append a new observation to the fieldwork stream.

    ID format: fo-{workspace_short}-{MMDD}-{seq:03d}
    """
    now = datetime.now()
    ws_short = workspace.removeprefix("contrib--")
    date_tag = now.strftime("%m%d")
    prefix = f"fo-{ws_short}-{date_tag}-"

    seq = sum(1 for o in index.observations if o.id.startswith(prefix)) + 1

    obs = FieldObservation(
        id=f"{prefix}{seq:03d}",
        workspace=workspace,
        timestamp=now.isoformat(),
        category=ObservationCategory(category),
        signal=signal,
        spectrum=SpectrumLevel(spectrum),
        strategic=[StrategicTag(s) for s in (strategic or [])],
        source=ObservationSource(source),
        evidence=evidence,
        scored_by=scored_by,
        related_absorption_ids=related_absorption_ids or [],
    )
    index.observations.append(obs)
    return obs


def load_fieldwork(input_path: Path | None = None) -> FieldworkIndex:
    """Load fieldwork observations from YAML, returning empty index if missing."""
    path = input_path or DATA_DIR / "fieldwork.yaml"
    if not path.exists():
        return FieldworkIndex()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return FieldworkIndex()
    return FieldworkIndex.model_validate(data)


def save_fieldwork(index: FieldworkIndex, output_path: Path | None = None) -> Path:
    """Persist a FieldworkIndex to YAML."""
    path = output_path or DATA_DIR / "fieldwork.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            index.model_dump(mode="json"), f,
            default_flow_style=False, sort_keys=False,
        )
    return path
