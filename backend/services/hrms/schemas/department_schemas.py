"""
HRMS Department Schemas
Pydantic schemas for department operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class DepartmentTypeEnum(str, Enum):
    """Department type"""
    OPERATIONS = "operations"
    FINANCE = "finance"
    IT = "it"
    HR = "hr"
    MARKETING = "marketing"
    SALES = "sales"
    ADMIN = "admin"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    RISK = "risk"
    CREDIT = "credit"
    COLLECTIONS = "collections"
    CUSTOMER_SERVICE = "customer_service"
    OTHER = "other"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class DepartmentBase(BaseModel):
    """Base department schema with common fields"""
    department_name: str = Field(..., min_length=1, max_length=100, description="Department name")
    department_type: DepartmentTypeEnum = Field(DepartmentTypeEnum.OTHER, description="Department type")
    description: Optional[str] = Field(None, description="Department description")
    organization_id: str = Field(..., description="Organization ID")
    parent_department_id: Optional[str] = Field(None, description="Parent department ID")
    hod_employee_id: Optional[str] = Field(None, description="Head of Department employee ID")
    email: Optional[str] = Field(None, max_length=100, description="Department email")
    phone: Optional[str] = Field(None, max_length=20, description="Department phone")
    extension: Optional[str] = Field(None, max_length=10, description="Phone extension")
    location: Optional[str] = Field(None, max_length=100, description="Department location")
    floor: Optional[str] = Field(None, max_length=50, description="Floor number/name")
    cost_center_code: Optional[str] = Field(None, max_length=20, description="Cost center code")
    is_active: bool = Field(True, description="Is active")


# ============================================================================
# CREATE/UPDATE SCHEMAS
# ============================================================================

class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department"""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating a department (all fields optional)"""
    department_name: Optional[str] = Field(None, min_length=1, max_length=100)
    department_type: Optional[DepartmentTypeEnum] = None
    description: Optional[str] = None
    parent_department_id: Optional[str] = None
    hod_employee_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    extension: Optional[str] = None
    location: Optional[str] = None
    floor: Optional[str] = None
    cost_center_code: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DepartmentResponse(DepartmentBase):
    """Full department response with all details"""
    id: str
    tenant_id: str
    department_code: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class DepartmentListItem(BaseModel):
    """Lightweight department item for list views"""
    id: str
    department_code: str
    department_name: str
    department_type: DepartmentTypeEnum
    organization_id: str
    parent_department_id: Optional[str] = None
    parent_department_name: Optional[str] = None
    hod_employee_id: Optional[str] = None
    hod_name: Optional[str] = None
    employee_count: int = 0
    location: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class PaginatedDepartmentResponse(BaseModel):
    """Paginated department list response"""
    items: List[DepartmentListItem]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# TREE & HIERARCHY SCHEMAS
# ============================================================================

class DepartmentTreeNode(BaseModel):
    """Department tree node for hierarchical display"""
    id: str
    department_code: str
    department_name: str
    department_type: DepartmentTypeEnum
    parent_department_id: Optional[str] = None
    hod_employee_id: Optional[str] = None
    hod_name: Optional[str] = None
    employee_count: int = 0
    is_active: bool
    children: List['DepartmentTreeNode'] = []
    
    class Config:
        from_attributes = True


# Update forward reference
DepartmentTreeNode.model_rebuild()


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class DepartmentStats(BaseModel):
    """Department statistics"""
    department_id: str
    department_name: str
    total_employees: int = 0
    active_employees: int = 0
    permanent_employees: int = 0
    contract_employees: int = 0
    probation_employees: int = 0
    male_employees: int = 0
    female_employees: int = 0
    average_age: Optional[float] = None
    average_experience: Optional[float] = None
    average_ctc: Optional[float] = None
    subdepartment_count: int = 0
