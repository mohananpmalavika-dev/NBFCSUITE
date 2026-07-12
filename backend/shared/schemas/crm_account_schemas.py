"""
CRM Account Management Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


# ============================================================================
# ENUMS
# ============================================================================

class AccountTypeEnum:
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    PARTNER = "partner"
    VENDOR = "vendor"
    COMPETITOR = "competitor"
    OTHER = "other"


class AccountStatusEnum:
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    DORMANT = "dormant"
    CLOSED = "closed"


class IndustryTypeEnum:
    AGRICULTURE = "agriculture"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    REAL_ESTATE = "real_estate"
    HOSPITALITY = "hospitality"
    TRANSPORTATION = "transportation"
    CONSTRUCTION = "construction"
    PROFESSIONAL_SERVICES = "professional_services"
    OTHER = "other"


class ContactTypeEnum:
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BILLING = "billing"
    TECHNICAL = "technical"
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    OTHER = "other"


class ContactStatusEnum:
    ACTIVE = "active"
    INACTIVE = "inactive"
    DO_NOT_CONTACT = "do_not_contact"


class RelationshipTypeEnum:
    PARENT_CHILD = "parent_child"
    SUBSIDIARY = "subsidiary"
    PARTNER = "partner"
    COMPETITOR = "competitor"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    REFERRAL = "referral"
    OTHER = "other"


# ============================================================================
# ACCOUNT SCHEMAS
# ============================================================================

class CRMAccountBase(BaseModel):
    """Base CRM Account schema"""
    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: str = Field(default=AccountTypeEnum.BUSINESS)
    status: str = Field(default=AccountStatusEnum.PROSPECT)
    industry: Optional[str] = None
    annual_revenue: Optional[Decimal] = None
    employee_count: Optional[str] = None
    
    # Tax & Registration
    pan_number: Optional[str] = Field(None, max_length=20)
    gst_number: Optional[str] = Field(None, max_length=20)
    cin_number: Optional[str] = Field(None, max_length=30)
    registration_number: Optional[str] = Field(None, max_length=50)
    
    # Contact Information
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)
    
    # Billing Address
    billing_address_line1: Optional[str] = Field(None, max_length=200)
    billing_address_line2: Optional[str] = Field(None, max_length=200)
    billing_city: Optional[str] = Field(None, max_length=100)
    billing_state: Optional[str] = Field(None, max_length=100)
    billing_pincode: Optional[str] = Field(None, max_length=10)
    billing_country: str = Field(default="India", max_length=100)
    
    # Shipping Address
    shipping_address_line1: Optional[str] = Field(None, max_length=200)
    shipping_address_line2: Optional[str] = Field(None, max_length=200)
    shipping_city: Optional[str] = Field(None, max_length=100)
    shipping_state: Optional[str] = Field(None, max_length=100)
    shipping_pincode: Optional[str] = Field(None, max_length=10)
    shipping_country: str = Field(default="India", max_length=100)
    same_as_billing: str = Field(default="no")
    
    # Relationship
    parent_account_id: Optional[UUID] = None
    account_owner_id: Optional[UUID] = None
    
    # Business Metrics
    customer_since: Optional[date] = None
    last_activity_date: Optional[date] = None
    next_followup_date: Optional[date] = None
    
    # Additional Information
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    # Social Media
    linkedin_url: Optional[str] = Field(None, max_length=200)
    facebook_url: Optional[str] = Field(None, max_length=200)
    twitter_handle: Optional[str] = Field(None, max_length=100)
    
    # Rating
    rating: Optional[str] = Field(None, max_length=20)
    priority: Optional[str] = Field(None, max_length=20)


class CRMAccountCreate(CRMAccountBase):
    """Schema for creating a new account"""
    pass


class CRMAccountUpdate(BaseModel):
    """Schema for updating an account"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=200)
    account_type: Optional[str] = None
    status: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[Decimal] = None
    employee_count: Optional[str] = None
    
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    cin_number: Optional[str] = None
    registration_number: Optional[str] = None
    
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    
    billing_address_line1: Optional[str] = None
    billing_address_line2: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_pincode: Optional[str] = None
    billing_country: Optional[str] = None
    
    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_pincode: Optional[str] = None
    shipping_country: Optional[str] = None
    same_as_billing: Optional[str] = None
    
    parent_account_id: Optional[UUID] = None
    account_owner_id: Optional[UUID] = None
    
    customer_since: Optional[date] = None
    last_activity_date: Optional[date] = None
    next_followup_date: Optional[date] = None
    
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    linkedin_url: Optional[str] = None
    facebook_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    
    rating: Optional[str] = None
    priority: Optional[str] = None


class CRMAccountResponse(CRMAccountBase):
    """Schema for account response"""
    id: UUID
    account_number: str
    tenant_id: str
    total_opportunities: Optional[Decimal] = None
    total_revenue: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# CONTACT SCHEMAS
# ============================================================================

class CRMContactBase(BaseModel):
    """Base CRM Contact schema"""
    account_id: UUID
    salutation: Optional[str] = Field(None, max_length=10)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    
    contact_type: str = Field(default=ContactTypeEnum.PRIMARY)
    status: str = Field(default=ContactStatusEnum.ACTIVE)
    
    # Job Information
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)
    
    # Contact Information
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    fax: Optional[str] = Field(None, max_length=20)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="India", max_length=100)
    
    # Personal Details
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    
    # Preferences
    preferred_contact_method: Optional[str] = Field(None, max_length=20)
    best_time_to_call: Optional[str] = Field(None, max_length=50)
    email_opt_out: str = Field(default="no")
    
    # Relationship
    reports_to_contact_id: Optional[UUID] = None
    contact_owner_id: Optional[UUID] = None
    
    # Activity
    last_contacted_date: Optional[date] = None
    next_followup_date: Optional[date] = None
    
    # Additional Information
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    # Social Media
    linkedin_url: Optional[str] = Field(None, max_length=200)
    twitter_handle: Optional[str] = Field(None, max_length=100)
    
    @validator('full_name', pre=True, always=True)
    def set_full_name(cls, v, values):
        """Auto-generate full name"""
        first = values.get('first_name', '')
        middle = values.get('middle_name', '')
        last = values.get('last_name', '')
        return f"{first} {middle} {last}".strip() if middle else f"{first} {last}".strip()


class CRMContactCreate(CRMContactBase):
    """Schema for creating a new contact"""
    pass


class CRMContactUpdate(BaseModel):
    """Schema for updating a contact"""
    account_id: Optional[UUID] = None
    salutation: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    
    contact_type: Optional[str] = None
    status: Optional[str] = None
    
    job_title: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    fax: Optional[str] = None
    
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    
    preferred_contact_method: Optional[str] = None
    best_time_to_call: Optional[str] = None
    email_opt_out: Optional[str] = None
    
    reports_to_contact_id: Optional[UUID] = None
    contact_owner_id: Optional[UUID] = None
    
    last_contacted_date: Optional[date] = None
    next_followup_date: Optional[date] = None
    
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None


class CRMContactResponse(CRMContactBase):
    """Schema for contact response"""
    id: UUID
    contact_number: str
    full_name: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# RELATIONSHIP SCHEMAS
# ============================================================================

class CRMAccountRelationshipBase(BaseModel):
    """Base Account Relationship schema"""
    primary_account_id: UUID
    related_account_id: UUID
    relationship_type: str = Field(default=RelationshipTypeEnum.OTHER)
    relationship_description: Optional[str] = Field(None, max_length=200)
    strength: Optional[str] = Field(None, max_length=20)
    is_active: str = Field(default="yes")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class CRMAccountRelationshipCreate(CRMAccountRelationshipBase):
    """Schema for creating a relationship"""
    pass


class CRMAccountRelationshipUpdate(BaseModel):
    """Schema for updating a relationship"""
    relationship_type: Optional[str] = None
    relationship_description: Optional[str] = None
    strength: Optional[str] = None
    is_active: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class CRMAccountRelationshipResponse(CRMAccountRelationshipBase):
    """Schema for relationship response"""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# ACTIVITY SCHEMAS
# ============================================================================

class CRMActivityBase(BaseModel):
    """Base Activity schema"""
    activity_type: str = Field(..., max_length=50)
    subject: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    account_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    activity_date: date
    duration_minutes: Optional[str] = Field(None, max_length=10)
    location: Optional[str] = Field(None, max_length=200)
    status: str = Field(default="planned")
    priority: Optional[str] = Field(None, max_length=20)
    outcome: Optional[str] = Field(None, max_length=50)
    follow_up_required: str = Field(default="no")
    follow_up_date: Optional[date] = None
    activity_owner_id: Optional[UUID] = None
    notes: Optional[str] = None
    attachments: Optional[str] = None


class CRMActivityCreate(CRMActivityBase):
    """Schema for creating an activity"""
    pass


class CRMActivityUpdate(BaseModel):
    """Schema for updating an activity"""
    activity_type: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    account_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    activity_date: Optional[date] = None
    duration_minutes: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    outcome: Optional[str] = None
    follow_up_required: Optional[str] = None
    follow_up_date: Optional[date] = None
    activity_owner_id: Optional[UUID] = None
    notes: Optional[str] = None
    attachments: Optional[str] = None


class CRMActivityResponse(CRMActivityBase):
    """Schema for activity response"""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# ACCOUNT 360 VIEW SCHEMA
# ============================================================================

class Account360View(BaseModel):
    """Complete 360 view of an account"""
    account: CRMAccountResponse
    contacts: List[CRMContactResponse] = []
    relationships: List[CRMAccountRelationshipResponse] = []
    recent_activities: List[CRMActivityResponse] = []
    child_accounts: List[CRMAccountResponse] = []
    opportunities_count: int = 0
    total_revenue: Decimal = Decimal(0)
    
    class Config:
        from_attributes = True


# ============================================================================
# LIST SCHEMAS
# ============================================================================

class PaginatedAccountList(BaseModel):
    """Paginated list of accounts"""
    total: int
    page: int
    page_size: int
    accounts: List[CRMAccountResponse]


class PaginatedContactList(BaseModel):
    """Paginated list of contacts"""
    total: int
    page: int
    page_size: int
    contacts: List[CRMContactResponse]


class PaginatedActivityList(BaseModel):
    """Paginated list of activities"""
    total: int
    page: int
    page_size: int
    activities: List[CRMActivityResponse]
