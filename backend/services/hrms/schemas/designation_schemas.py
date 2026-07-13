"""
HRMS Designation Schemas
Pydantic schemas for designation/job title operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class DesignationBase(BaseModel):
    """Base designation schema with common fields"""
    designation_name: str = Field(..., min_length=1, max_length=100, description="Designation name")
    description: Optional[str] = Field(None, description="Designation description")
    level: Optional[int] = Field(None, ge=1, description="Hierarchy level (1=Top, 2=Senior, 3=Middle, 4=Junior)")
    grade: Optional[str] = Field(None, max_length=10, description="Grade (A, B, C, D, etc.)")
    min_salary: Optional[Decimal] = Field(None, ge=0, description="Minimum salary")
    max_salary: Optional[Decimal] = Field(None, ge=0, description="Maximum salary")
    min_experience_years: Optional[int] = Field(None, ge=0, description="Minimum experience required (years)")
    required_qualification: Optional[str] = Field(None, max_length=200, description="Required qualification")
    is_active: bool = Field(True, description="Is active")


# ============================================================================
# CREATE/UPDATE SCHEMAS
# ============================================================================

class DesignationCreate(DesignationBase):
    """Schema for creating a new designation"""
    pass


class DesignationUpdate(BaseModel):
    """Schema for updating a designation (all fields optional)"""
    designation_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    level: Optional[int] = Field(None, ge=1)
    grade: Optional[str] = None
    min_salary: Optional[Decimal] = Field(None, ge=0)
    max_salary: Optional[Decimal] = Field(None, ge=0)
    min_experience_years: Optional[int] = Field(None, ge=0)
    required_qualification: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DesignationResponse(DesignationBase):
    """Full designation response with all details"""
    id: str
    tenant_id: str
    designation_code: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class DesignationListItem(BaseModel):
    """Lightweight designation item for list views"""
    id: str
    designation_code: str
    designation_name: str
    level: Optional[int] = None
    grade: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    employee_count: int = 0
    is_active: bool
    
    class Config:
        from_attributes = True


class PaginatedDesignationResponse(BaseModel):
    """Paginated designation list response"""
    items: List[DesignationListItem]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class DesignationStats(BaseModel):
    """Designation statistics"""
    designation_id: str
    designation_name: str
    total_employees: int = 0
    active_employees: int = 0
    permanent_employees: int = 0
    contract_employees: int = 0
    male_employees: int = 0
    female_employees: int = 0
    average_age: Optional[float] = None
    average_experience: Optional[float] = None
    average_ctc: Optional[float] = None
    min_ctc: Optional[Decimal] = None
    max_ctc: Optional[Decimal] = None
