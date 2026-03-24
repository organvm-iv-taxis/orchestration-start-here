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


# --- Campaign models ---


class CampaignPhase(StrEnum):
    """Phase of a contribution campaign."""

    UNBLOCK = "unblock"
    ENGAGE = "engage"
    CULTIVATE = "cultivate"
    HARVEST = "harvest"
    INJECT = "inject"


class CampaignAction(BaseModel):
    """A single action in the campaign queue."""

    id: str
    workspace: str
    phase: CampaignPhase
    action: str
    priority: int = 0
    manual: bool = False
    automated: bool = False
    blocked_by: list[str] = Field(default_factory=list)
    completed: bool = False
    completed_at: str = ""

    model_config = {"extra": "allow"}


class Campaign(BaseModel):
    """The full campaign state."""

    name: str = "The Plague"
    started: str = ""
    targets: list[str] = Field(default_factory=list)
    actions: list[CampaignAction] = Field(default_factory=list)

    model_config = {"extra": "allow"}

    def next_actions(self, limit: int = 5) -> list[CampaignAction]:
        """Return top-priority unblocked incomplete actions."""
        completed_ids = {a.id for a in self.actions if a.completed}
        available = []
        for a in self.actions:
            if a.completed:
                continue
            blocked = any(
                bid not in completed_ids
                for bid in a.blocked_by
                if any(x.id == bid for x in self.actions)
            )
            if not blocked:
                available.append(a)
        return sorted(available, key=lambda a: a.priority)[:limit]

    def phase_summary(self) -> dict[str, int]:
        """Count incomplete actions per phase."""
        summary: dict[str, int] = {}
        for a in self.actions:
            if not a.completed:
                summary[a.phase] = summary.get(a.phase, 0) + 1
        return summary


# --- Outreach models ---


class OutreachChannel(StrEnum):
    """Communication channel for outreach."""

    GITHUB_ISSUE = "github_issue"
    GITHUB_PR = "github_pr"
    DISCORD = "discord"
    SLACK = "slack"
    EMAIL = "email"
    TWITTER = "twitter"


class OutreachDirection(StrEnum):
    """Direction of an outreach interaction."""

    OUTBOUND = "outbound"
    INBOUND = "inbound"
    MUTUAL = "mutual"


class OutreachEvent(BaseModel):
    """A single outreach interaction."""

    channel: OutreachChannel
    date: str
    direction: OutreachDirection
    summary: str
    url: str = ""

    model_config = {"extra": "allow"}


class TargetRelationship(BaseModel):
    """Relationship state with a single external target."""

    workspace: str
    target: str
    maintainers: list[str] = Field(default_factory=list)
    community_channels: list[dict] = Field(default_factory=list)
    outreach_events: list[OutreachEvent] = Field(default_factory=list)
    issue_claimed: bool = False
    issue_assigned: bool = False
    cla_signed: bool = False
    first_human_contact: str = ""
    relationship_score: int = 0

    model_config = {"extra": "allow"}


class OutreachIndex(BaseModel):
    """All outreach relationships."""

    generated: str = ""
    relationships: list[TargetRelationship] = Field(default_factory=list)

    model_config = {"extra": "allow"}

    def get_relationship(self, workspace: str) -> TargetRelationship | None:
        for r in self.relationships:
            if r.workspace == workspace:
                return r
        return None


# --- Backflow models ---


class BackflowType(StrEnum):
    """Type of knowledge flowing back into ORGANVM."""

    THEORY = "theory"
    GENERATIVE = "generative"
    CODE = "code"
    NARRATIVE = "narrative"
    COMMUNITY = "community"
    DISTRIBUTION = "distribution"


class BackflowStatus(StrEnum):
    """Status of a backflow item."""

    PENDING = "pending"
    EXTRACTED = "extracted"
    DEPOSITED = "deposited"
    PUBLISHED = "published"


class BackflowItem(BaseModel):
    """A single backflow item to deposit into an ORGANVM organ."""

    workspace: str
    organ: str
    backflow_type: BackflowType
    title: str
    description: str
    status: BackflowStatus = BackflowStatus.PENDING
    artifact_path: str = ""
    deposited_at: str = ""

    model_config = {"extra": "allow"}


class BackflowIndex(BaseModel):
    """All backflow items across all contributions."""

    generated: str = ""
    items: list[BackflowItem] = Field(default_factory=list)

    model_config = {"extra": "allow"}

    def pending_by_organ(self) -> dict[str, list[BackflowItem]]:
        """Group pending items by target organ."""
        result: dict[str, list[BackflowItem]] = {}
        for item in self.items:
            if item.status == BackflowStatus.PENDING:
                result.setdefault(item.organ, []).append(item)
        return result


# --- Absorption models ---


class AbsorptionTrigger(StrEnum):
    """What made an external question worth formalizing."""

    ASSUMPTION_DIVERGENCE = "assumption_divergence"
    UNNAMED_PATTERN = "unnamed_pattern"
    INDEPENDENT_CONVERGENCE = "convergence"


class AbsorptionStatus(StrEnum):
    """Lifecycle of an absorbed question."""

    DETECTED = "detected"  # Heuristic matched
    ASSESSED = "assessed"  # Confirmed expansive (not reductive)
    FORMALIZED = "formalized"  # Theory note written
    DEPOSITED = "deposited"  # Backflow entry created
    DISMISSED = "dismissed"  # Assessed as reductive


class AbsorptionItem(BaseModel):
    """A single external question flagged for formalization."""

    id: str
    workspace: str
    source_url: str  # GitHub comment URL
    questioner: str  # GitHub username
    question_text: str  # First 500 chars
    detected_at: str
    triggers: list[AbsorptionTrigger] = Field(default_factory=list)
    trigger_evidence: str = ""
    status: AbsorptionStatus = AbsorptionStatus.DETECTED
    pattern_name: str = ""  # Named after formalization
    backflow_ref: str = ""  # Reference to backflow item if deposited
    organ: str = ""  # Target organ for deposit

    model_config = {"extra": "allow"}


class AbsorptionIndex(BaseModel):
    """All tracked absorption items."""

    generated: str = ""
    items: list[AbsorptionItem] = Field(default_factory=list)

    model_config = {"extra": "allow"}

    def by_status(self, status: AbsorptionStatus) -> list[AbsorptionItem]:
        return [i for i in self.items if i.status == status]

    def pending_formalization(self) -> list[AbsorptionItem]:
        """Items detected or assessed but not yet formalized."""
        return [
            i for i in self.items
            if i.status in (AbsorptionStatus.DETECTED, AbsorptionStatus.ASSESSED)
        ]
