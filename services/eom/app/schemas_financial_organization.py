from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Literal
from datetime import datetime


# -----------------------------
# Cost Center
# -----------------------------
CostCenterStatus = Literal['draft', 'active', 'inactive']


class CostCenterCreate(BaseModel):
    enterprise_id: Optional[str] = None
    code: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=256)
    category: Optional[str] = None
    status: Optional[CostCenterStatus] = 'draft'
    description: Optional[str] = None

    parent_cost_center_id: Optional[str] = None
    budget_owner: Optional[str] = None
    currency: Optional[str] = None
    gl_mapping: Optional[str] = None
    department_id: Optional[str] = None


class CostCenterUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[CostCenterStatus] = None
    description: Optional[str] = None
    parent_cost_center_id: Optional[str] = None
    budget_owner: Optional[str] = None
    currency: Optional[str] = None
    gl_mapping: Optional[str] = None
    department_id: Optional[str] = None


class CostCenterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    enterprise_id: Optional[str] = None
    code: str
    name: str
    category: Optional[str] = None
    status: CostCenterStatus
    description: Optional[str] = None

    parent_cost_center_id: Optional[str] = None
    budget_owner: Optional[str] = None
    currency: Optional[str] = None
    gl_mapping: Optional[str] = None
    department_id: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CostCenterListResponse(BaseModel):
    total: int
    items: List[CostCenterResponse]


# -----------------------------
# Profit Center
# -----------------------------
ProfitCenterStatus = Literal['draft', 'active', 'inactive']


class ProfitCenterCreate(BaseModel):
    enterprise_id: Optional[str] = None
    code: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=256)
    category: Optional[str] = None
    status: Optional[ProfitCenterStatus] = 'draft'
    description: Optional[str] = None

    parent_profit_center_id: Optional[str] = None
    responsibility_owner: Optional[str] = None
    currency: Optional[str] = None
    gl_mapping: Optional[str] = None
    branch_id: Optional[str] = None


class ProfitCenterUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[ProfitCenterStatus] = None
    description: Optional[str] = None
    parent_profit_center_id: Optional[str] = None
    responsibility_owner: Optional[str] = None
    currency: Optional[str] = None
    gl_mapping: Optional[str] = None
    branch_id: Optional[str] = None


class ProfitCenterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    enterprise_id: Optional[str] = None
    code: str
    name: str
    category: Optional[str] = None
    status: ProfitCenterStatus
    description: Optional[str] = None

    parent_profit_center_id: Optional[str] = None
    responsibility_owner: Optional[str] = None
    currency: Optional[str] = None
    gl_mapping: Optional[str] = None
    branch_id: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfitCenterListResponse(BaseModel):
    total: int
    items: List[ProfitCenterResponse]


# -----------------------------
# Budget (MVP)
# -----------------------------
BudgetStatus = Literal['original', 'revised', 'forecast', 'actual']


class BudgetCreate(BaseModel):
    enterprise_id: Optional[str] = None
    budget_center_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None

    year: int
    status: Optional[BudgetStatus] = 'original'

    original_total: Optional[float] = None
    revised_total: Optional[float] = None
    committed_total: Optional[float] = None
    actual_total: Optional[float] = None
    forecast_total: Optional[float] = None

    currency: Optional[str] = None


class BudgetUpdate(BaseModel):
    budget_center_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    status: Optional[BudgetStatus] = None

    original_total: Optional[float] = None
    revised_total: Optional[float] = None
    committed_total: Optional[float] = None
    actual_total: Optional[float] = None
    forecast_total: Optional[float] = None

    currency: Optional[str] = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    enterprise_id: Optional[str] = None
    budget_center_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    year: int

    status: BudgetStatus
    original_total: Optional[float] = None
    revised_total: Optional[float] = None
    committed_total: Optional[float] = None
    actual_total: Optional[float] = None
    forecast_total: Optional[float] = None

    currency: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BudgetListResponse(BaseModel):
    total: int
    items: List[BudgetResponse]


# -----------------------------
# Internal Order
# -----------------------------
InternalOrderStatus = Literal['draft', 'approved', 'open', 'active', 'closed', 'archived']


class InternalOrderCreate(BaseModel):
    enterprise_id: Optional[str] = None
    code: str = Field(..., min_length=2, max_length=64)
    name: str = Field(..., min_length=2, max_length=256)
    description: Optional[str] = None

    status: Optional[InternalOrderStatus] = 'draft'

    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    budget_center_id: Optional[str] = None
    responsibility_center_id: Optional[str] = None
    investment_center_id: Optional[str] = None


class InternalOrderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[InternalOrderStatus] = None
    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    budget_center_id: Optional[str] = None
    responsibility_center_id: Optional[str] = None
    investment_center_id: Optional[str] = None


class InternalOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    enterprise_id: Optional[str] = None
    code: str
    name: str
    description: Optional[str] = None
    status: InternalOrderStatus

    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    budget_center_id: Optional[str] = None
    responsibility_center_id: Optional[str] = None
    investment_center_id: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InternalOrderListResponse(BaseModel):
    total: int
    items: List[InternalOrderResponse]


# -----------------------------
# Dashboard
# -----------------------------
class FinancialDashboardResponse(BaseModel):
    enterprise_id: Optional[str] = None
    kpis: dict
    summary: dict

