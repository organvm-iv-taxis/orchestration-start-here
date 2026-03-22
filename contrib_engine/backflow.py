"""Backflow Pipeline — tracks knowledge flowing back into ORGANVM organs."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import yaml

from contrib_engine.schemas import BackflowIndex, BackflowItem, BackflowStatus, BackflowType

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent / "data"


def add_item(index: BackflowIndex, workspace: str, organ: str, backflow_type: str,
             title: str, description: str = "") -> None:
    """Add a pending backflow item."""
    item = BackflowItem(
        workspace=workspace, organ=organ,
        backflow_type=BackflowType(backflow_type),
        title=title, description=description,
    )
    index.items.append(item)


def deposit_item(index: BackflowIndex, item_index: int) -> bool:
    """Mark a backflow item as deposited into its target organ."""
    if item_index < 0 or item_index >= len(index.items):
        return False
    index.items[item_index].status = BackflowStatus.DEPOSITED
    index.items[item_index].deposited_at = datetime.now().isoformat()
    return True


def save_backflow(index: BackflowIndex, output_path: Path | None = None) -> Path:
    """Persist a BackflowIndex to YAML."""
    path = output_path or DATA_DIR / "backflow.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(index.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)
    return path


def load_backflow(input_path: Path | None = None) -> BackflowIndex:
    """Load a BackflowIndex from YAML, returning an empty index if missing."""
    path = input_path or DATA_DIR / "backflow.yaml"
    if not path.exists():
        return BackflowIndex()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return BackflowIndex()
    return BackflowIndex.model_validate(data)
