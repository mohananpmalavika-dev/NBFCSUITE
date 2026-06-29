from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PositionCreate(BaseModel):
    enterprise_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    department_id: Optional[str] = None
    section_id: Optional[str] = None
    team_id: Optional[str] = None
    grade_id: Optional[str] = None
    code: str = Field(..., min_length=2)
    title: str
    status: Optional[str] = 'open'
    reports_to_position_id: Optional[str] = None
    description: Optional[str] = None


class PositionUpdate(BaseModel):
    team_id: Optional[str] = None
    grade_id: Optional[str] = None
    status: Optional[str] = None
    reports_to_position_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class PositionResponse(BaseModel):
    id: str
    enterprise_id: Optional[str]
    business_unit_id: Optional[str]
    department_id: Optional[str]
    section_id: Optional[str]
    team_id: Optional[str]
    grade_id: Optional[str]
    code: str
    title: str
    status: str
    reports_to_position_id: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class PositionListResponse(BaseModel):
    total: int
    items: list[PositionResponse]
