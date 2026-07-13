"""
HRMS Organization Schemas
Pydantic schemas for organization/company operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class OrganizationBase(BaseModel):
    """Base organization schema with common fields"""
    organization_name: str = Field(..., min_length=1, max_length=200, description="Organization name")
    short_name: Optional[str] = Field(None, max_length=50, description="Short name")
    legal_name: Optional[str] = Field(None, max_length=200, description="Legal name")
    
    # Registration Details
    pan_number: Optional[str] = Field(None, max_length=10, description="PAN number")
    tan_number: Optional[str] = Field(None, max_length=10, description="TAN number")
    gstin: Optional[str] = Field(None, max_length=15, description="GSTIN")
    cin_number: Optional[str] = Field(None, max_length=21, description="CIN (Corporate Identity Number)")
    
    # Contact Information
    email: Optional[str] = Field(None, max_length=100, description="Organization email")
    phone: Optional[str] = Field(None, max_length=20, description="Organization phone")
    website: Optional[str] = Field(None, max_length=200, description="Organization website")
    
    # Registered Address
    registered_address_line1: Optional[str] = Field(None, max_length=200, description="Registered address line 1")
    registered_address_line2: Optional[str] = Field(None, max_length=200, description="Registered address line 2")
    registered_city: Optional[str] = Field(None, max_length=100, description="Registered city")
    registered_state: Optional[str] = Field(None, max_length=100, description="Registered state")
    registered_pincode: Optional[str] = Field(None, max_length=10, description="Registered pincode")
    registered_country: str = Field("India", max_length=100, description="Registered country")
    
    # Status
    is_active: bool = Field(True, description="Is active")
    established_date: Optional[date] = Field(None, description="Established date")


# ============================================================================
# CREATE/UPDATE SCHEMAS
# ============================================================================

class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization"""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization (all fields optional)"""
    organization_name: Optional[str] = Field(None, min_length=1, max_length=200)
    short_name: Optional[str] = None
    legal_name: Optional[str] = None
    pan_number: Optional[str] = None
    tan_number: Optional[str] = None
    gstin: Optional[str] = None
    cin_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    registered_address_line1: Optional[str] = None
    registered_address_line2: Optional[str] = None
    registered_city: Optional[str] = None
    registered_state: Optional[str] = None
    registered_pincode: Optional[str] = None
    registered_country: Optional[str] = None
    is_active: Optional[bool] = None
    established_date: Optional[date] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class OrganizationResponse(OrganizationBase):
    """Full organization response with all details"""
    id: str
    tenant_id: str
    organization_code: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrganizationListItem(BaseModel):
    """Lightweight organization item for list views"""
    id: str
    organization_code: str
    organization_name: str
    short_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    registered_city: Optional[str] = None
    registered_state: Optional[str] = None
    is_active: bool
    employee_count: int = 0
    department_count: int = 0
    
    class Config:
        from_attributes = True


class PaginatedOrganizationResponse(BaseModel):
    """Paginated organization list response"""
    items: List[OrganizationListItem]
    total: int
    page: int
    page_size: int
    pages: int
