from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BranchCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str
    branch_type: Optional[str] = None
    status: Optional[str] = 'active'
    manager: Optional[str] = None
    business_unit_id: Optional[str] = None
    legal_entity_id: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    cash_limit: Optional[float] = None
    vault_limit: Optional[float] = None
    gold_loan_enabled: Optional[bool] = False
    deposit_enabled: Optional[bool] = False
    forex_enabled: Optional[bool] = False
    atm: Optional[bool] = False
    locker: Optional[bool] = False
    kiosk: Optional[bool] = False


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    branch_type: Optional[str] = None
    status: Optional[str] = None
    manager: Optional[str] = None
    business_unit_id: Optional[str] = None
    legal_entity_id: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    cash_limit: Optional[float] = None
    vault_limit: Optional[float] = None
    gold_loan_enabled: Optional[bool] = None
    deposit_enabled: Optional[bool] = None
    forex_enabled: Optional[bool] = None
    atm: Optional[bool] = None
    locker: Optional[bool] = None
    kiosk: Optional[bool] = None


class BranchResponse(BaseModel):
    id: str
    code: str
    name: str
    branch_type: Optional[str]
    status: str
    manager: Optional[str]
    business_unit_id: Optional[str]
    legal_entity_id: Optional[str]
    city: Optional[str]
    region: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    description: Optional[str]
    cash_limit: Optional[float]
    vault_limit: Optional[float]
    gold_loan_enabled: Optional[bool]
    deposit_enabled: Optional[bool]
    forex_enabled: Optional[bool]
    atm: Optional[bool]
    locker: Optional[bool]
    kiosk: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class BranchListResponse(BaseModel):
    total: int
    items: list[BranchResponse]


class BranchDashboardResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    health_score: int
    active_customers: int
    loans: int
    deposits: int
    cash_balance: float
    vault_balance: float
    revenue: float
    expenses: float
    profit: float


class BranchHealthResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    health_score: int
    rating: str
    issues: list[str]


class BranchAnalyticsResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    customer_growth: float
    loan_growth: float
    deposit_growth: float
    collection_efficiency: float
    audit_score: float
