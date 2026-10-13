"""Pydantic schemas shared by the pipeline, the API and the eval harness."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Cite(BaseModel):
    doc: str
    page: int
    quote: str = Field(description="Verbatim span copied from the cited page. Never paraphrase.")


class Hypothesis(BaseModel):
    fault_id: str
    likelihood: Literal["high", "medium", "low"]
    why: str
    cite: Cite


class Step(BaseModel):
    id: int
    action: str = Field(description="One concrete instruction the technician can perform.")
    expected: str = Field(description="What the technician should observe if the step succeeds.")
    if_yes: int | None = Field(default=None, description="Next step id if the expected observation is seen.")
    if_no: int | None = Field(default=None, description="Next step id if it is not seen.")
    tools_needed: list[str] = []
    duration_min: int = 5
    safety_class: Literal["none", "caution", "stop"] = "none"
    cite: Cite


class PartCandidate(BaseModel):
    name: str
    part_number: str | None = None
    cite: Cite | None = None


class FaultTree(BaseModel):
    """A manual-grounded troubleshooting tree. Every step and hypothesis must quote a provided page verbatim."""

    device_id: str
    summary: str = Field(description="Two plain sentences for the technician: what is most likely and what to do first.")
    hypotheses: list[Hypothesis]
    steps: list[Step]
    parts_candidates: list[PartCandidate] = []
    escalate_if: list[str] = []


class AuditVerdict(BaseModel):
    """Auditor decision per step."""

    step_id: int
    verdict: Literal["approve", "repair", "reject"]
    reason: str
    repaired_action: str | None = None


class AuditReport(BaseModel):
    """Independent audit of a fault tree against the full manual."""

    verdicts: list[AuditVerdict]
    overall: Literal["approve", "approve_with_repairs", "reject"]
    notes: str = ""


class WorkOrder(BaseModel):
    asset_id: str | None = None
    facility: str | None = None
    device_id: str
    model_label: str
    serial: str | None = None
    reported_fault: str
    indicators: list[str] = []
    steps_performed: list[str] = []
    parts_used: list[str] = []
    outcome: Literal["fixed", "needs_part", "escalated", "decommissioned", "open"] = "open"
    downtime_hours: float | None = None
    technician: str | None = None
    ai_trace_id: str
    notes: str = ""
