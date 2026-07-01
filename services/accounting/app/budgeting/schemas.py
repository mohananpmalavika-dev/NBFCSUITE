from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BudgetVersionResponse(BaseModel):
    id: str
    version_name: str
    amount: float
    status: str
    period: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetForecastResponse(BaseModel):
    id: str
    forecast_name: str
    forecast_amount: float
    forecast_date: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetResponse(BaseModel):
    id: str
    tenant_id: str
    budget_name: str
    description: Optional[str] = None
    financial_year: str
    currency: str
    status: str
    scope_level: Optional[str] = None
    scope_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    versions: List[BudgetVersionResponse] = []
    forecasts: List[BudgetForecastResponse] = []

    class Config:
        from_attributes = True


class BudgetCreate(BaseModel):
    tenant_id: str
    budget_name: str
    description: Optional[str] = None
    financial_year: str
    currency: Optional[str] = "INR"
    scope_level: Optional[str] = None
    scope_id: Optional[str] = None
    status: Optional[str] = "draft"
    metadata: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    initial_amount: Optional[float] = None
    initial_version_name: Optional[str] = "Original"
    initial_period: Optional[str] = None


class BudgetUpdate(BaseModel):
    budget_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    scope_level: Optional[str] = None
    scope_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BudgetApproveRequest(BaseModel):
    approved_by: Optional[str] = None
    status: Optional[str] = "approved"


class BudgetForecastCreate(BaseModel):
    forecast_name: str
    forecast_amount: float
    forecast_date: datetime
    status: Optional[str] = "pending"
    metadata: Optional[Dict[str, Any]] = None


class BudgetRevisionCreate(BaseModel):
    version_name: str
    amount: float
    status: Optional[str] = "active"
    period: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BudgetAvailabilityRequest(BaseModel):
    tenant_id: str
    scope_level: Optional[str] = None
    scope_id: Optional[str] = None
    requested_amount: float


class BudgetAvailabilityResponse(BaseModel):
    tenant_id: str
    available_amount: float
    total_committed: float
    total_budget: float
    status: str


class BudgetDashboardResponse(BaseModel):
    tenant_id: str
    total_budgets: int
    total_budget_amount: float
    total_forecast_amount: float
    budgets_by_status: Dict[str, int]

    class Config:
        from_attributes = True
