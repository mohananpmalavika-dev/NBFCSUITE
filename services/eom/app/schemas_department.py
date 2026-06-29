from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str
    status: Optional[str] = 'active'
    department_head: Optional[str] = None
    branch_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    legal_entity_id: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    department_head: Optional[str] = None
    branch_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    legal_entity_id: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    department_head: Optional[str]
    branch_id: Optional[str]
    business_unit_id: Optional[str]
    legal_entity_id: Optional[str]
    city: Optional[str]
    region: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class DepartmentListResponse(BaseModel):
    total: int
    items: list[DepartmentResponse]


class DepartmentDashboardResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    department_head: Optional[str]
    health_score: int
    active_personnel: int
    teams: int
    open_requests: int
    budget_utilization: float
    productivity_index: float


class DepartmentHealthResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    health_score: int
    rating: str
    issues: list[str]


class DepartmentAnalyticsResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    department_head: Optional[str]
    headcount_growth: float
    cost_variance: float
    efficiency: float
    compliance_score: float
