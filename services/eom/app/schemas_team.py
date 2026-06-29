from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TeamCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str
    team_type: Optional[str] = None
    status: Optional[str] = 'draft'
    section_id: Optional[str] = None
    team_lead: Optional[str] = None
    deputy_lead: Optional[str] = None
    reporting_manager: Optional[str] = None
    shift: Optional[str] = None
    capacity: Optional[str] = None
    working_days: Optional[str] = None
    business_calendar: Optional[str] = None
    location: Optional[str] = None
    primary_skills: Optional[str] = None
    secondary_skills: Optional[str] = None
    certifications: Optional[str] = None
    required_competencies: Optional[str] = None
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    team_type: Optional[str] = None
    status: Optional[str] = None
    section_id: Optional[str] = None
    team_lead: Optional[str] = None
    deputy_lead: Optional[str] = None
    reporting_manager: Optional[str] = None
    shift: Optional[str] = None
    capacity: Optional[str] = None
    working_days: Optional[str] = None
    business_calendar: Optional[str] = None
    location: Optional[str] = None
    primary_skills: Optional[str] = None
    secondary_skills: Optional[str] = None
    certifications: Optional[str] = None
    required_competencies: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    code: str
    name: str
    team_type: Optional[str]
    status: str
    section_id: Optional[str]
    team_lead: Optional[str]
    deputy_lead: Optional[str]
    reporting_manager: Optional[str]
    shift: Optional[str]
    capacity: Optional[str]
    working_days: Optional[str]
    business_calendar: Optional[str]
    location: Optional[str]
    primary_skills: Optional[str]
    secondary_skills: Optional[str]
    certifications: Optional[str]
    required_competencies: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TeamListResponse(BaseModel):
    total: int
    items: list[TeamResponse]


class TeamCapacityResponse(BaseModel):
    total_positions: int
    filled: int
    vacant: int
    available_capacity: float
    utilization_pct: float
    overtime: float
    idle_pct: float


class TeamWorkloadResponse(BaseModel):
    assigned_tasks: int
    completed: int
    pending: int
    overdue: int
    average_sla: float
    productivity: float


class TeamHealthScoreResponse(BaseModel):
    score: float
    rating: str
    capacity_utilization: float
    productivity: float
    sla_compliance: float
    employee_satisfaction: float
    attrition: float
    training_completion: float
    project_delivery: float
    audit_findings: float
