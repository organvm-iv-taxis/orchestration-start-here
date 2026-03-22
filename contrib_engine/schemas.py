"""Data schemas for the outbound contribution engine."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TargetStatus(StrEnum):
    """Lifecycle of a contribution target."""

    DISCOVERED = "discovered"  # Scanner found it
    RANKED = "ranked"  # Scored and prioritized
    APPROVED = "approved"  # Human approved workspace creation
    ACTIVE = "active"  # Workspace created, work in progress
    SHIPPED = "shipped"  # PR submitted
    MERGED = "merged"  # PR merged upstream
    DECLINED = "declined"  # Human declined or target rejected PR
    ARCHIVED = "archived"  # Engagement complete


class ContributionTarget(BaseModel):
    """A ranked open-source contribution target."""

    name: str  # kebab-case identifier (e.g., "adenhq-hive")
    github: str  # owner/repo (e.g., "adenhq/hive")
    score: int = 0  # 0-100 composite score
    signal_type: str = "outbound"  # inbound | outbound | mutual
    domain_overlap: list[str] = Field(default_factory=list)
    stars: int = 0
    open_issues: int = 0
    contacts: list[str] = Field(default_factory=list)
    matching_issues: list[int] = Field(default_factory=list)
    status: TargetStatus = TargetStatus.DISCOVERED
    workspace: str = ""  # contrib--{name} if created
    notes: str = ""

    model_config = {"extra": "allow"}


class RankedTargets(BaseModel):
    """Output of the scanner: scored and ranked targets."""

    generated: str = ""
    targets: list[ContributionTarget] = Field(default_factory=list)

    def get_target(self, name: str) -> ContributionTarget | None:
        for t in self.targets:
            if t.name == name:
                return t
        return None

    def ranked(self) -> list[ContributionTarget]:
        return sorted(self.targets, key=lambda t: -t.score)


class PRState(StrEnum):
    """GitHub PR state."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


class ContributionStatus(BaseModel):
    """Status of an active contribution."""

    workspace: str  # contrib--{name}
    target: str  # owner/repo
    pr_number: int | None = None
    pr_state: PRState | None = None
    issue_number: int | None = None
    assigned: bool = False
    last_ci: str = ""
    last_review: str | None = None
    last_comment: str | None = None
    organs_delivered: list[str] = Field(default_factory=list)
    phase: int = 1
    next_action: str = ""
    next_action_date: str = ""

    model_config = {"extra": "allow"}


class ContributionStatusIndex(BaseModel):
    """All active contributions."""

    generated: str = ""
    contributions: list[ContributionStatus] = Field(default_factory=list)

    def get_contribution(self, workspace: str) -> ContributionStatus | None:
        for c in self.contributions:
            if c.workspace == workspace:
                return c
        return None
