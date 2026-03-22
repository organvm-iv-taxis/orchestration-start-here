"""Campaign Sequencer — prescriptive action queue for the Plague campaign."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import yaml

from contrib_engine.schemas import Campaign, CampaignAction, CampaignPhase

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


def complete_action(campaign: Campaign, action_id: str) -> bool:
    """Mark a campaign action as completed."""
    for action in campaign.actions:
        if action.id == action_id:
            action.completed = True
            action.completed_at = datetime.now().isoformat()
            return True
    return False


def generate_campaign() -> Campaign:
    """Generate a campaign from current workspace states."""
    existing = load_campaign()
    if existing.actions:
        return existing
    return Campaign(started=datetime.now().strftime("%Y-%m-%d"))


def save_campaign(campaign: Campaign, output_path: Path | None = None) -> Path:
    """Save campaign state to YAML."""
    path = output_path or DATA_DIR / "campaign.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(campaign.model_dump(mode="python"), f, default_flow_style=False, sort_keys=False)
    return path


def load_campaign(input_path: Path | None = None) -> Campaign:
    """Load campaign state from YAML."""
    path = input_path or DATA_DIR / "campaign.yaml"
    if not path.exists():
        return Campaign()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return Campaign()
    return Campaign.model_validate(data)
