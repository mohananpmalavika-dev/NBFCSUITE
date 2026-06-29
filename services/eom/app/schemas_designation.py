from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DesignationCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str
    short_name: Optional[str] = None
    job_family_id: Optional[str] = None
    grade_id: Optional[str] = None
    department_id: Optional[str] = None
    reports_to_designation_id: Optional[str] = None
    status: Optional[str] = 'draft'
    description: Optional[str] = None


class DesignationUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    job_family_id: Optional[str] = None
    grade_id: Optional[str] = None
    department_id: Optional[str] = None
    reports_to_designation_id: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


class DesignationResponse(BaseModel):
    id: str
    code: str
    name: str
    short_name: Optional[str]
    job_family_id: Optional[str]
    grade_id: Optional[str]
    department_id: Optional[str]
    reports_to_designation_id: Optional[str]
    status: str
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class DesignationListResponse(BaseModel):
    total: int
    items: list[DesignationResponse]
