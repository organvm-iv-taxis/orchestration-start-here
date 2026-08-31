"""Versioned event-to-evidence execution contract.

The action ledger remains the canonical append-only history.  This module adds
typed execution metadata to an ``Action`` without introducing a second ledger.
Provider-specific objects (GitHub events, Conductor dispatch receipts, model
responses) enter through adapters and are retained only as evidence references.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

EXECUTION_CONTRACT_VERSION = "organvm.execution/v1"


class ExecutionStage(StrEnum):
    """Lifecycle stages recorded as append-only action events."""

    RECEIVED = "received"
    CONTEXT_SCOPED = "context_scoped"
    APPROVAL_PENDING = "approval_pending"
    AUTHORIZED = "authorized"
    RUNNING = "running"
    EVIDENCED = "evidenced"
    VERIFIED = "verified"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"


class ApprovalStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NOT_REQUIRED = "not_required"


class RollbackStatus(StrEnum):
    NOT_NEEDED = "not_needed"
    PLANNED = "planned"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class EventRef(BaseModel):
    """Provider-neutral reference to the event that awakened the worker."""

    provider: str
    event_type: str
    event_id: str
    occurred_at: str
    source: str
    delivery_id: str = ""
    replay_of: str = ""


class ScopedContext(BaseModel):
    """The bounded context retrieved for this execution."""

    refs: list[str] = Field(default_factory=list)
    forbidden: list[str] = Field(default_factory=list)
    context_hash: str = ""
    retrieved_at: str = ""
    redacted: bool = True


class Authority(BaseModel):
    """Acting principal and delegated capabilities."""

    principal: str
    delegated_by: str = ""
    permissions: list[str] = Field(default_factory=list)
    policy_ref: str


class PolicyCheck(BaseModel):
    decision: PolicyDecision
    reason: str


class ApprovalGate(BaseModel):
    required: bool = False
    status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    approver: str = ""
    decided_at: str = ""
    evidence_ref: str = ""

    @model_validator(mode="after")
    def status_matches_requirement(self) -> ApprovalGate:
        if self.required and self.status == ApprovalStatus.NOT_REQUIRED:
            raise ValueError("required approval cannot have status not_required")
        if not self.required and self.status not in {
            ApprovalStatus.NOT_REQUIRED,
            ApprovalStatus.APPROVED,
        }:
            raise ValueError("optional approval cannot be pending or rejected")
        return self


class WorkAction(BaseModel):
    kind: str
    target: str
    mutation_ref: str = ""


class CommandResult(BaseModel):
    """A redacted command plus its durable result reference."""

    command: str
    exit_code: int | None = None
    result_ref: str = ""
    summary: str = ""
    redacted: bool = True


class WorkflowArtifact(BaseModel):
    """Reviewable procedure that accumulates operational learning."""

    objective: str
    plan: list[str] = Field(default_factory=list)
    command_results: list[CommandResult] = Field(default_factory=list)
    dead_ends: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    approvals: list[str] = Field(default_factory=list)


class EvidenceRef(BaseModel):
    kind: str
    ref: str
    digest: str = ""
    summary: str = ""


class Verification(BaseModel):
    status: VerificationStatus = VerificationStatus.PENDING
    checks: list[str] = Field(default_factory=list)
    reviewer: str = ""
    reviewed_at: str = ""


class RollbackPlan(BaseModel):
    strategy: str
    status: RollbackStatus = RollbackStatus.PLANNED
    ref: str = ""


class FailureDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False
    evidence_ref: str = ""


class ExecutionEnvelope(BaseModel):
    """A versioned execution snapshot embedded in an Action Ledger action.

    One execution may produce several snapshots.  ``execution_id`` links the
    lifecycle; ``idempotency_key`` uniquely identifies a stage/attempt so event
    redelivery can be ignored without suppressing legitimate transitions.
    """

    schema_version: Literal["organvm.execution/v1"] = EXECUTION_CONTRACT_VERSION
    execution_id: str
    idempotency_key: str
    stage: ExecutionStage
    event: EventRef
    scope: ScopedContext
    authority: Authority
    policy: PolicyCheck
    approval: ApprovalGate
    work: WorkAction
    workflow: WorkflowArtifact
    evidence: list[EvidenceRef] = Field(default_factory=list)
    verification: Verification = Field(default_factory=Verification)
    rollback: RollbackPlan
    failure: FailureDetail | None = None
    provider_receipt_refs: list[str] = Field(default_factory=list)
    dispute_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lifecycle_gate(self) -> ExecutionEnvelope:
        active_stages = {
            ExecutionStage.AUTHORIZED,
            ExecutionStage.RUNNING,
            ExecutionStage.EVIDENCED,
            ExecutionStage.VERIFIED,
        }
        if self.stage in active_stages and self.policy.decision != PolicyDecision.ALLOW:
            raise ValueError(f"stage {self.stage} requires an allow policy decision")
        if (
            self.stage in active_stages
            and self.approval.required
            and self.approval.status != ApprovalStatus.APPROVED
        ):
            raise ValueError(f"stage {self.stage} requires approved human gate")
        if self.stage == ExecutionStage.APPROVAL_PENDING:
            if not self.approval.required or self.approval.status != ApprovalStatus.PENDING:
                raise ValueError("approval_pending requires a pending required approval")
        if self.stage == ExecutionStage.VERIFIED:
            if self.verification.status != VerificationStatus.PASSED:
                raise ValueError("verified stage requires passed verification")
            if not self.evidence:
                raise ValueError("verified stage requires evidence")
        if self.stage == ExecutionStage.FAILED and self.failure is None:
            raise ValueError("failed stage requires failure details")
        if (
            self.stage == ExecutionStage.ROLLED_BACK
            and self.rollback.status != RollbackStatus.COMPLETED
        ):
            raise ValueError("rolled_back stage requires completed rollback")
        return self
