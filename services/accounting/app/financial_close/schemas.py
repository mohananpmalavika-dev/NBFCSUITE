from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CloseDashboardResponse(BaseModel):
    tenant_id: str
    close_readiness: int
    open_tasks: int
    blocked_tasks: int
    reconciliation_issues: int
    consolidation_progress: int
    board_pack_status: str
    rbi_status: str
    audit_ready: bool
    health_score: int


class CloseStartRequest(BaseModel):
    tenant_id: str
    cycle_name: str
    period: str
    initiated_by: Optional[str] = None
    close_type: Optional[str] = "monthly"
    metadata: Optional[Dict[str, Any]] = None


class CloseStartResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_name: str
    period: str
    stage: str
    status: str
    started_at: datetime


class CloseTaskCreate(BaseModel):
    tenant_id: str
    cycle_id: Optional[str] = None
    name: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    dependency: Optional[str] = None
    priority: Optional[str] = "medium"
    status: Optional[str] = "pending"
    evidence: Optional[str] = None
    approval_required: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None


class CloseTaskResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: Optional[str] = None
    name: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    dependency: Optional[str] = None
    priority: Optional[str]
    status: str
    evidence: Optional[str] = None
    approval_status: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime


class CloseTaskListResponse(BaseModel):
    tenant_id: str
    total: int
    items: List[CloseTaskResponse]


class CloseReconciliationRequest(BaseModel):
    tenant_id: str
    cycle_id: Optional[str] = None
    source: str
    target: str
    difference_amount: float
    metadata: Optional[Dict[str, Any]] = None


class CloseReconciliationResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: Optional[str] = None
    source: str
    target: str
    difference_amount: float
    status: str


class CloseConsolidationRequest(BaseModel):
    tenant_id: str
    cycle_id: Optional[str] = None
    entity_from: str
    entity_to: str
    result_summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CloseConsolidationResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: Optional[str] = None
    entity_from: str
    entity_to: str
    result_summary: Optional[str] = None
    status: str


class CloseEliminationRequest(BaseModel):
    tenant_id: str
    cycle_id: Optional[str] = None
    description: str
    amount: float
    metadata: Optional[Dict[str, Any]] = None


class CloseEliminationResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: Optional[str] = None
    description: str
    amount: float
    status: str


class BoardPackRequest(BaseModel):
    tenant_id: str
    cycle_id: Optional[str] = None
    report_type: Optional[str] = "board_pack"


class BoardPackResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: Optional[str] = None
    report_type: str
    status: str


class RbiReportRequest(BaseModel):
    tenant_id: str
    cycle_id: Optional[str] = None
    return_type: Optional[str] = "NBS"


class RbiReportResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: Optional[str] = None
    return_type: str
    status: str


class CloseCompleteRequest(BaseModel):
    tenant_id: str
    cycle_id: str
    completed_by: Optional[str] = None
    final_notes: Optional[Dict[str, Any]] = None


class CloseCompleteResponse(BaseModel):
    id: str
    tenant_id: str
    cycle_id: str
    status: str
    completed_at: datetime
    final_notes: Optional[Dict[str, Any]] = None


class CloseStatusResponse(BaseModel):
    message: str
    status: str
