"""
Base Pydantic schemas
Common response and request models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict, List
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime
    updated_at: datetime


class TenantSchema(BaseSchema):
    """Schema with tenant field"""
    tenant_id: str


class BaseDBSchema(TimestampSchema, TenantSchema):
    """Base schema for database models"""
    id: UUID
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = "Success"
    data: Any = None
    meta: Optional[Dict[str, Any]] = None


class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: ErrorDetail


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel):
    """Paginated response"""
    success: bool = True
    message: str = "Success"
    data: List[Any]
    meta: Dict[str, PaginationMeta]


class TenantCreate(BaseSchema):
    """Tenant creation schema"""
    id: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=200)
    display_name: str = Field(min_length=2, max_length=200)
    email: str = Field(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = None
    domain: Optional[str] = None
    
    # Address
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"
    
    # Configuration
    max_users: int = Field(default=50, ge=1, le=10000)
    max_branches: int = Field(default=10, ge=1, le=1000)
    max_customers: int = Field(default=10000, ge=1, le=10000000)


class TenantResponse(BaseDBSchema):
    """Tenant response schema"""
    id: str
    name: str
    display_name: str
    email: str
    phone: Optional[str]
    domain: Optional[str]
    is_active: bool
    is_trial: bool
    trial_ends_at: Optional[datetime]
    subscription_plan: str
    subscription_status: str
    max_users: int
    max_branches: int
    max_customers: int


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: float
    services: Dict[str, str]
