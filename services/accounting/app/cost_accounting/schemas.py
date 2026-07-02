from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CostCenterCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    cost_center_type: Optional[str] = None
    budget_amount: Optional[float] = 0.0
    actual_amount: Optional[float] = 0.0
    status: Optional[str] = "active"
    metadata: Optional[Dict[str, Any]] = None


class CostCenterResponse(BaseModel):
    id: str
    tenant_id: str
    code: str
    name: str
    cost_center_type: Optional[str] = None
    budget_amount: float
    actual_amount: float
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfitCenterCreate(BaseModel):
    tenant_id: str
    code: str
    name: str
    profit_center_type: Optional[str] = None
    manager: Optional[str] = None
    status: Optional[str] = "active"
    metadata: Optional[Dict[str, Any]] = None


class ProfitCenterResponse(BaseModel):
    id: str
    tenant_id: str
    code: str
    name: str
    profit_center_type: Optional[str] = None
    manager: Optional[str] = None
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AllocationReceiver(BaseModel):
    receiver_id: str
    receiver_name: str
    receiver_type: str
    allocation_percentage: float


class AllocationRunCreate(BaseModel):
    tenant_id: str
    source_cost_center_id: str
    amount: float
    allocation_rule_type: Optional[str] = "percentage"
    receivers: List[AllocationReceiver] = []


class AllocationResultItem(BaseModel):
    receiver_id: str
    receiver_name: str
    receiver_type: str
    allocation_percentage: float
    allocated_amount: float


class AllocationRunResponse(BaseModel):
    id: str
    tenant_id: str
    source_cost_center_id: str
    amount: float
    allocation_rule_type: str
    status: str
    results: List[AllocationResultItem]
    created_at: datetime

    class Config:
        from_attributes = True


class ProfitabilityItem(BaseModel):
    metric_type: str
    name: str
    amount: float


class ProfitabilityResponse(BaseModel):
    tenant_id: str
    items: List[ProfitabilityItem]


class CostDashboardResponse(BaseModel):
    tenant_id: str
    total_cost_centers: int
    total_profit_centers: int
    total_allocated_amount: float
    total_budget_amount: float


class CostSimulationResponse(BaseModel):
    tenant_id: str
    adjustment_percent: float
    projected_total_cost: float


class CostReportItem(BaseModel):
    report_type: str
    title: str
    amount: float


class CostReportsResponse(BaseModel):
    tenant_id: str
    total_reports: int
    reports: List[CostReportItem]
