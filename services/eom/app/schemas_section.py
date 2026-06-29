from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SectionCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str
    section_type: Optional[str] = None
    status: Optional[str] = 'draft'
    department_id: Optional[str] = None
    section_head: Optional[str] = None
    deputy_head: Optional[str] = None
    business_unit_id: Optional[str] = None
    branch_id: Optional[str] = None
    reporting_department_id: Optional[str] = None
    working_calendar: Optional[str] = None
    shift: Optional[str] = None
    capacity: Optional[str] = None
    business_hours: Optional[str] = None
    sla_profile: Optional[str] = None
    service_catalog: Optional[str] = None
    business_capabilities: Optional[str] = None
    workflows: Optional[str] = None
    description: Optional[str] = None


class SectionUpdate(BaseModel):
    name: Optional[str] = None
    section_type: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[str] = None
    section_head: Optional[str] = None
    deputy_head: Optional[str] = None
    business_unit_id: Optional[str] = None
    branch_id: Optional[str] = None
    reporting_department_id: Optional[str] = None
    working_calendar: Optional[str] = None
    shift: Optional[str] = None
    capacity: Optional[str] = None
    business_hours: Optional[str] = None
    sla_profile: Optional[str] = None
    service_catalog: Optional[str] = None
    business_capabilities: Optional[str] = None
    workflows: Optional[str] = None
    description: Optional[str] = None


class SectionResponse(BaseModel):
    id: str
    code: str
    name: str
    section_type: Optional[str]
    status: str
    department_id: Optional[str]
    section_head: Optional[str]
    deputy_head: Optional[str]
    business_unit_id: Optional[str]
    branch_id: Optional[str]
    reporting_department_id: Optional[str]
    working_calendar: Optional[str]
    shift: Optional[str]
    capacity: Optional[str]
    business_hours: Optional[str]
    sla_profile: Optional[str]
    service_catalog: Optional[str]
    business_capabilities: Optional[str]
    workflows: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class SectionListResponse(BaseModel):
    total: int
    items: list[SectionResponse]


class SectionDashboardResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    section_type: Optional[str]
    section_head: Optional[str]
    employees: int
    teams: int
    projects: int
    health_score: int


class SectionHealthResponse(BaseModel):
    id: str
    code: str
    name: str
    status: str
    health_score: int
    rating: str
    issues: list[str]
