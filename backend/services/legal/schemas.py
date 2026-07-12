"""
Legal Contract Management - Pydantic Schemas
Request/Response models for contract management API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from backend.shared.database.legal_models import (
    ContractType,
    ContractStatus,
    RenewalStatus,
    PartyType,
)


# ============================================
# CONTRACT SCHEMAS
# ============================================

class ContractCreate(BaseModel):
    """Schema for creating a new contract"""
    title: str = Field(..., min_length=1, max_length=500)
    contract_type: ContractType
    description: Optional[str] = None
    effective_date: date
    expiry_date: Optional[date] = None
    execution_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    currency: str = "INR"
    is_renewable: bool = False
    auto_renewal: bool = False
    renewal_notice_days: int = 90
    document_url: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    alert_before_expiry_days: int = 30
    notes: Optional[str] = None

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'effective_date' in values and v < values['effective_date']:
            raise ValueError('Expiry date must be after effective date')
        return v


class ContractUpdate(BaseModel):
    """Schema for updating a contract"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[ContractStatus] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    execution_date: Optional[date] = None
    termination_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    currency: Optional[str] = None
    is_renewable: Optional[bool] = None
    auto_renewal: Optional[bool] = None
    renewal_notice_days: Optional[int] = None
    renewal_status: Optional[RenewalStatus] = None
    document_url: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    alert_before_expiry_days: Optional[int] = None
    notes: Optional[str] = None
    approved_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None


class ContractPartyResponse(BaseModel):
    """Schema for contract party response"""
    id: UUID
    party_type: PartyType
    party_name: str
    party_designation: Optional[str]
    organization_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_signatory: bool
    signature_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class ContractDocumentResponse(BaseModel):
    """Schema for contract document response"""
    id: UUID
    document_name: str
    document_type: Optional[str]
    description: Optional[str]
    file_name: str
    file_size: Optional[int]
    file_type: Optional[str]
    file_url: str
    version: int
    is_confidential: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ContractVersionResponse(BaseModel):
    """Schema for contract version response"""
    id: UUID
    version_number: int
    version_name: Optional[str]
    title: str
    description: Optional[str]
    contract_value: Optional[Decimal]
    effective_date: date
    expiry_date: Optional[date]
    document_url: str
    changes_summary: Optional[str]
    change_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContractRenewalResponse(BaseModel):
    """Schema for contract renewal response"""
    id: UUID
    renewal_number: int
    renewal_status: RenewalStatus
    renewal_due_date: date
    renewal_initiated_date: Optional[date]
    renewal_completed_date: Optional[date]
    new_expiry_date: Optional[date]
    new_contract_value: Optional[Decimal]
    value_change_percentage: Optional[Decimal]
    terms_modified: bool
    modification_summary: Optional[str]
    alert_sent_date: Optional[datetime]
    reminder_count: int
    approval_notes: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    """Schema for contract response"""
    id: UUID
    tenant_id: str
    contract_number: str
    title: str
    contract_type: ContractType
    description: Optional[str]
    status: ContractStatus
    effective_date: date
    expiry_date: Optional[date]
    execution_date: Optional[date]
    termination_date: Optional[date]
    contract_value: Optional[Decimal]
    currency: str
    is_renewable: bool
    auto_renewal: bool
    renewal_notice_days: int
    renewal_status: RenewalStatus
    current_version: int
    is_latest: bool
    document_url: Optional[str]
    tags: List[str]
    custom_fields: Dict[str, Any]
    alert_before_expiry_days: int
    last_alert_sent: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    parties: List[ContractPartyResponse] = []
    documents: List[ContractDocumentResponse] = []
    versions: List[ContractVersionResponse] = []
    renewals: List[ContractRenewalResponse] = []
    
    # Computed fields
    days_until_expiry: Optional[int] = None
    is_expiring_soon: bool = False
    is_expired: bool = False

    class Config:
        from_attributes = True


class ContractListResponse(BaseModel):
    """Schema for paginated contract list"""
    items: List[ContractResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================
# CONTRACT PARTY SCHEMAS
# ============================================

class ContractPartyCreate(BaseModel):
    """Schema for creating a contract party"""
    party_type: PartyType
    party_name: str = Field(..., min_length=1, max_length=500)
    party_designation: Optional[str] = Field(None, max_length=200)
    organization_name: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    legal_entity_type: Optional[str] = Field(None, max_length=100)
    registration_number: Optional[str] = Field(None, max_length=200)
    is_signatory: bool = False
    signature_date: Optional[date] = None
    signature_url: Optional[str] = None
    custom_fields: Dict[str, Any] = {}


class ContractPartyUpdate(BaseModel):
    """Schema for updating a contract party"""
    party_type: Optional[PartyType] = None
    party_name: Optional[str] = Field(None, min_length=1, max_length=500)
    party_designation: Optional[str] = None
    organization_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_signatory: Optional[bool] = None
    signature_date: Optional[date] = None
    signature_url: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


# ============================================
# CONTRACT DOCUMENT SCHEMAS
# ============================================

class ContractDocumentCreate(BaseModel):
    """Schema for creating a contract document"""
    document_name: str = Field(..., min_length=1, max_length=500)
    document_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    file_name: str = Field(..., min_length=1, max_length=500)
    file_size: Optional[int] = None
    file_type: Optional[str] = Field(None, max_length=100)
    file_url: str = Field(..., min_length=1, max_length=1000)
    file_hash: Optional[str] = None
    version: int = 1
    tags: List[str] = []
    is_confidential: bool = False


# ============================================
# CONTRACT RENEWAL SCHEMAS
# ============================================

class ContractRenewalCreate(BaseModel):
    """Schema for creating a contract renewal"""
    renewal_due_date: date
    new_expiry_date: Optional[date] = None
    new_contract_value: Optional[Decimal] = None
    value_change_percentage: Optional[Decimal] = None
    terms_modified: bool = False
    modification_summary: Optional[str] = None
    notes: Optional[str] = None


class ContractRenewalUpdate(BaseModel):
    """Schema for updating a contract renewal"""
    renewal_status: Optional[RenewalStatus] = None
    renewal_initiated_date: Optional[date] = None
    renewal_completed_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    new_contract_value: Optional[Decimal] = None
    value_change_percentage: Optional[Decimal] = None
    terms_modified: Optional[bool] = None
    modification_summary: Optional[str] = None
    approval_notes: Optional[str] = None
    notes: Optional[str] = None


# ============================================
# CONTRACT VERSION SCHEMAS
# ============================================

class ContractVersionCreate(BaseModel):
    """Schema for creating a contract version"""
    version_name: Optional[str] = Field(None, max_length=200)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    contract_value: Optional[Decimal] = None
    effective_date: date
    expiry_date: Optional[date] = None
    document_url: str = Field(..., min_length=1, max_length=1000)
    document_hash: Optional[str] = None
    changes_summary: Optional[str] = None
    change_reason: Optional[str] = None
    custom_fields: Dict[str, Any] = {}


# ============================================
# FILTER & SEARCH SCHEMAS
# ============================================

class ContractFilterParams(BaseModel):
    """Schema for contract filtering parameters"""
    contract_type: Optional[ContractType] = None
    status: Optional[ContractStatus] = None
    renewal_status: Optional[RenewalStatus] = None
    is_renewable: Optional[bool] = None
    expiring_in_days: Optional[int] = None
    effective_date_from: Optional[date] = None
    effective_date_to: Optional[date] = None
    expiry_date_from: Optional[date] = None
    expiry_date_to: Optional[date] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    tags: Optional[List[str]] = None
    search_query: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


# ============================================
# STATISTICS SCHEMAS
# ============================================

class ContractStatistics(BaseModel):
    """Schema for contract statistics"""
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    expiring_soon: int
    pending_renewals: int
    total_contract_value: Decimal
    contracts_by_type: Dict[str, int]
    contracts_by_status: Dict[str, int]
    average_contract_value: Decimal
    renewal_completion_rate: float
