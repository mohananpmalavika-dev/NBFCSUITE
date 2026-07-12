"""
Legal License Management - Pydantic Schemas
Request/Response models for license management API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from .license_models import (
    LicenseType,
    LicenseStatus,
    RenewalStatus,
    ComplianceStatus,
    ReminderFrequency,
)


# ============================================
# LICENSE SCHEMAS
# ============================================

class LicenseCreate(BaseModel):
    """Schema for creating a new license"""
    license_number: str = Field(..., min_length=1, max_length=200)
    license_name: str = Field(..., min_length=1, max_length=500)
    license_type: LicenseType
    license_category: Optional[str] = None
    description: Optional[str] = None
    
    # Issuing Authority
    issuing_authority: str = Field(..., min_length=1, max_length=500)
    authority_contact_person: Optional[str] = None
    authority_email: Optional[str] = None
    authority_phone: Optional[str] = None
    authority_website: Optional[str] = None
    authority_address: Optional[str] = None
    
    # Dates
    application_date: Optional[date] = None
    issue_date: date
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    # Duration
    validity_period_months: Optional[int] = None
    is_perpetual: bool = False
    
    # Renewal
    is_renewable: bool = True
    auto_renewal_enabled: bool = False
    renewal_notice_days: int = 60
    renewal_submission_deadline_days: int = 30
    
    # Compliance
    compliance_requirements: List[str] = []
    compliance_notes: Optional[str] = None
    
    # Financial
    application_fee: Optional[Decimal] = None
    renewal_fee: Optional[Decimal] = None
    annual_fee: Optional[Decimal] = None
    penalty_for_late_renewal: Optional[Decimal] = None
    currency: str = "INR"
    
    # Responsible Personnel
    license_holder_name: Optional[str] = None
    responsible_department: Optional[str] = None
    responsible_person_id: Optional[UUID] = None
    backup_person_id: Optional[UUID] = None
    
    # Documents
    license_document_url: Optional[str] = None
    application_document_url: Optional[str] = None
    supporting_documents: List[str] = []
    
    # Conditions
    license_conditions: List[str] = []
    restrictions: Optional[str] = None
    scope_of_license: Optional[str] = None
    geographical_coverage: Optional[str] = None
    
    # Alerts
    alert_enabled: bool = True
    alert_days_before_expiry: List[int] = Field(default=[90, 60, 30, 15, 7])
    reminder_frequency: ReminderFrequency = ReminderFrequency.WEEKLY
    alert_recipients: List[str] = []
    escalation_to: List[str] = []
    
    # Risk
    criticality_level: Optional[str] = None
    business_impact: Optional[str] = None
    risk_of_non_compliance: Optional[str] = None
    
    # Metadata
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'issue_date' in values and v < values['issue_date']:
            raise ValueError('Expiry date must be after issue date')
        return v


class LicenseUpdate(BaseModel):
    """Schema for updating a license"""
    license_name: Optional[str] = Field(None, min_length=1, max_length=500)
    license_category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LicenseStatus] = None
    
    # Authority
    issuing_authority: Optional[str] = None
    authority_contact_person: Optional[str] = None
    authority_email: Optional[str] = None
    authority_phone: Optional[str] = None
    authority_website: Optional[str] = None
    authority_address: Optional[str] = None
    
    # Dates
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    last_renewal_date: Optional[date] = None
    next_renewal_date: Optional[date] = None
    
    # Renewal
    is_renewable: Optional[bool] = None
    auto_renewal_enabled: Optional[bool] = None
    renewal_status: Optional[RenewalStatus] = None
    renewal_notice_days: Optional[int] = None
    renewal_submission_deadline_days: Optional[int] = None
    
    # Compliance
    compliance_status: Optional[ComplianceStatus] = None
    last_compliance_check_date: Optional[date] = None
    next_compliance_check_date: Optional[date] = None
    compliance_requirements: Optional[List[str]] = None
    compliance_notes: Optional[str] = None
    
    # Financial
    renewal_fee: Optional[Decimal] = None
    annual_fee: Optional[Decimal] = None
    penalty_for_late_renewal: Optional[Decimal] = None
    
    # Personnel
    license_holder_name: Optional[str] = None
    responsible_department: Optional[str] = None
    responsible_person_id: Optional[UUID] = None
    backup_person_id: Optional[UUID] = None
    
    # Documents
    license_document_url: Optional[str] = None
    supporting_documents: Optional[List[str]] = None
    
    # Conditions
    license_conditions: Optional[List[str]] = None
    restrictions: Optional[str] = None
    scope_of_license: Optional[str] = None
    geographical_coverage: Optional[str] = None
    
    # Alerts
    alert_enabled: Optional[bool] = None
    alert_days_before_expiry: Optional[List[int]] = None
    reminder_frequency: Optional[ReminderFrequency] = None
    alert_recipients: Optional[List[str]] = None
    escalation_to: Optional[List[str]] = None
    
    # Risk
    criticality_level: Optional[str] = None
    business_impact: Optional[str] = None
    risk_of_non_compliance: Optional[str] = None
    
    # Metadata
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None


class LicenseRenewalResponse(BaseModel):
    """Schema for license renewal response"""
    id: UUID
    renewal_number: int
    renewal_status: RenewalStatus
    renewal_due_date: date
    renewal_initiated_date: Optional[date]
    application_submitted_date: Optional[date]
    approval_received_date: Optional[date]
    renewal_completed_date: Optional[date]
    new_expiry_date: Optional[date]
    application_number: Optional[str]
    renewal_fee_paid: Optional[Decimal]
    late_fee_paid: Optional[Decimal]
    total_amount_paid: Optional[Decimal]
    payment_date: Optional[date]
    payment_reference: Optional[str]
    terms_modified: bool
    modification_summary: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LicenseComplianceCheckResponse(BaseModel):
    """Schema for compliance check response"""
    id: UUID
    check_number: int
    check_date: date
    check_type: Optional[str]
    compliance_status: ComplianceStatus
    overall_score: Optional[Decimal]
    compliant_items: int
    non_compliant_items: int
    findings: Optional[str]
    non_compliance_issues: List[Any]
    recommendations: Optional[str]
    action_required: bool
    action_items: List[Any]
    action_deadline: Optional[date]
    actions_completed: bool
    conducted_by: Optional[str]
    next_check_due_date: Optional[date]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LicenseDocumentResponse(BaseModel):
    """Schema for license document response"""
    id: UUID
    document_name: str
    document_type: Optional[str]
    description: Optional[str]
    file_name: str
    file_size: Optional[int]
    file_type: Optional[str]
    file_url: str
    document_date: Optional[date]
    valid_from: Optional[date]
    valid_until: Optional[date]
    is_confidential: bool
    version: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class LicenseReminderResponse(BaseModel):
    """Schema for license reminder response"""
    id: UUID
    reminder_type: str
    reminder_date: datetime
    days_before_due: Optional[int]
    is_sent: bool
    sent_at: Optional[datetime]
    recipients: List[str]
    subject: Optional[str]
    is_acknowledged: bool
    acknowledged_at: Optional[datetime]
    is_escalated: bool
    delivery_status: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LicenseResponse(BaseModel):
    """Schema for license response"""
    id: UUID
    tenant_id: str
    license_number: str
    license_name: str
    license_type: LicenseType
    license_category: Optional[str]
    description: Optional[str]
    status: LicenseStatus
    
    # Authority
    issuing_authority: str
    authority_contact_person: Optional[str]
    authority_email: Optional[str]
    authority_phone: Optional[str]
    
    # Dates
    application_date: Optional[date]
    issue_date: date
    effective_date: Optional[date]
    expiry_date: Optional[date]
    last_renewal_date: Optional[date]
    next_renewal_date: Optional[date]
    
    # Duration
    validity_period_months: Optional[int]
    is_perpetual: bool
    
    # Renewal
    is_renewable: bool
    auto_renewal_enabled: bool
    renewal_status: RenewalStatus
    renewal_notice_days: int
    
    # Compliance
    compliance_status: ComplianceStatus
    last_compliance_check_date: Optional[date]
    next_compliance_check_date: Optional[date]
    compliance_requirements: List[str]
    
    # Financial
    application_fee: Optional[Decimal]
    renewal_fee: Optional[Decimal]
    annual_fee: Optional[Decimal]
    currency: str
    
    # Personnel
    license_holder_name: Optional[str]
    responsible_department: Optional[str]
    responsible_person_id: Optional[UUID]
    
    # Documents
    license_document_url: Optional[str]
    
    # Risk
    criticality_level: Optional[str]
    business_impact: Optional[str]
    
    # Alerts
    alert_enabled: bool
    last_alert_sent: Optional[datetime]
    total_reminders_sent: int
    escalation_triggered: bool
    
    # Metadata
    tags: List[str]
    custom_fields: Dict[str, Any]
    notes: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Related data
    renewals: List[LicenseRenewalResponse] = []
    compliance_checks: List[LicenseComplianceCheckResponse] = []
    documents: List[LicenseDocumentResponse] = []
    reminders: List[LicenseReminderResponse] = []
    
    # Computed fields
    days_until_expiry: Optional[int] = None
    is_expiring_soon: bool = False
    is_expired: bool = False
    requires_renewal_action: bool = False

    class Config:
        from_attributes = True


class LicenseListResponse(BaseModel):
    """Schema for paginated license list"""
    items: List[LicenseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================
# LICENSE RENEWAL SCHEMAS
# ============================================

class LicenseRenewalCreate(BaseModel):
    """Schema for creating a license renewal"""
    renewal_due_date: date
    application_submitted_date: Optional[date] = None
    application_number: Optional[str] = None
    application_document_url: Optional[str] = None
    renewal_fee_paid: Optional[Decimal] = None
    late_fee_paid: Optional[Decimal] = None
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    payment_receipt_url: Optional[str] = None
    terms_modified: bool = False
    modification_summary: Optional[str] = None
    conditions_changed: bool = False
    conditions_summary: Optional[str] = None
    notes: Optional[str] = None


class LicenseRenewalUpdate(BaseModel):
    """Schema for updating a license renewal"""
    renewal_status: Optional[RenewalStatus] = None
    renewal_initiated_date: Optional[date] = None
    application_submitted_date: Optional[date] = None
    approval_received_date: Optional[date] = None
    renewal_completed_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    application_number: Optional[str] = None
    application_document_url: Optional[str] = None
    renewal_fee_paid: Optional[Decimal] = None
    late_fee_paid: Optional[Decimal] = None
    total_amount_paid: Optional[Decimal] = None
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    payment_receipt_url: Optional[str] = None
    authority_reference_number: Optional[str] = None
    terms_modified: Optional[bool] = None
    modification_summary: Optional[str] = None
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


# ============================================
# COMPLIANCE CHECK SCHEMAS
# ============================================

class LicenseComplianceCheckCreate(BaseModel):
    """Schema for creating a compliance check"""
    check_date: date
    check_type: Optional[str] = None
    compliance_status: ComplianceStatus
    overall_score: Optional[Decimal] = None
    checklist_items: List[Dict[str, Any]] = []
    compliant_items: int = 0
    non_compliant_items: int = 0
    findings: Optional[str] = None
    non_compliance_issues: List[Dict[str, Any]] = []
    recommendations: Optional[str] = None
    action_required: bool = False
    action_items: List[Dict[str, Any]] = []
    action_deadline: Optional[date] = None
    conducted_by: Optional[str] = None
    inspector_name: Optional[str] = None
    inspector_designation: Optional[str] = None
    inspector_organization: Optional[str] = None
    report_document_url: Optional[str] = None
    evidence_documents: List[str] = []
    next_check_due_date: Optional[date] = None
    check_frequency_months: int = 12
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None


class LicenseComplianceCheckUpdate(BaseModel):
    """Schema for updating a compliance check"""
    compliance_status: Optional[ComplianceStatus] = None
    overall_score: Optional[Decimal] = None
    findings: Optional[str] = None
    non_compliance_issues: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[str] = None
    action_required: Optional[bool] = None
    action_items: Optional[List[Dict[str, Any]]] = None
    action_deadline: Optional[date] = None
    actions_completed: Optional[bool] = None
    report_document_url: Optional[str] = None
    evidence_documents: Optional[List[str]] = None
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None


# ============================================
# DOCUMENT SCHEMAS
# ============================================

class LicenseDocumentCreate(BaseModel):
    """Schema for creating a license document"""
    document_name: str = Field(..., min_length=1, max_length=500)
    document_type: Optional[str] = None
    description: Optional[str] = None
    file_name: str = Field(..., min_length=1, max_length=500)
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_url: str = Field(..., min_length=1, max_length=1000)
    file_hash: Optional[str] = None
    document_date: Optional[date] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_confidential: bool = False
    version: int = 1
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}


# ============================================
# FILTER & SEARCH SCHEMAS
# ============================================

class LicenseFilterParams(BaseModel):
    """Schema for license filtering parameters"""
    license_type: Optional[LicenseType] = None
    status: Optional[LicenseStatus] = None
    renewal_status: Optional[RenewalStatus] = None
    compliance_status: Optional[ComplianceStatus] = None
    is_renewable: Optional[bool] = None
    is_perpetual: Optional[bool] = None
    expiring_in_days: Optional[int] = None
    issue_date_from: Optional[date] = None
    issue_date_to: Optional[date] = None
    expiry_date_from: Optional[date] = None
    expiry_date_to: Optional[date] = None
    issuing_authority: Optional[str] = None
    responsible_department: Optional[str] = None
    criticality_level: Optional[str] = None
    tags: Optional[List[str]] = None
    search_query: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


# ============================================
# STATISTICS SCHEMAS
# ============================================

class LicenseStatistics(BaseModel):
    """Schema for license statistics"""
    total_licenses: int
    active_licenses: int
    expired_licenses: int
    expiring_soon: int
    pending_renewals: int
    non_compliant_licenses: int
    licenses_by_type: Dict[str, int]
    licenses_by_status: Dict[str, int]
    licenses_by_compliance_status: Dict[str, int]
    total_renewal_fees_due: Decimal
    average_renewal_time_days: float


# ============================================
# REMINDER SCHEMAS
# ============================================

class LicenseReminderCreate(BaseModel):
    """Schema for creating a reminder"""
    reminder_type: str
    reminder_date: datetime
    days_before_due: Optional[int] = None
    recipients: List[str] = []
    cc_recipients: List[str] = []
    subject: Optional[str] = None
    message_body: Optional[str] = None
    notes: Optional[str] = None
