"""
AML/CFT Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


# ============================================================================
# TRANSACTION MONITORING SCHEMAS
# ============================================================================

class TransactionMonitoringCreate(BaseModel):
    transaction_id: str = Field(..., max_length=100)
    transaction_type: str = Field(..., max_length=50)
    transaction_date: datetime
    posting_date: date
    customer_id: UUID
    customer_name: str = Field(..., max_length=300)
    customer_type: str = Field(..., max_length=50)
    account_id: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    counterparty_name: Optional[str] = Field(None, max_length=300)
    counterparty_account: Optional[str] = Field(None, max_length=100)
    counterparty_bank: Optional[str] = Field(None, max_length=200)
    counterparty_country: Optional[str] = Field(None, max_length=100)
    transaction_amount: Decimal = Field(..., gt=0)
    transaction_currency: str = Field(default='INR', max_length=3)
    branch_code: Optional[str] = Field(None, max_length=50)
    channel: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, max_length=50)
    device_id: Optional[str] = Field(None, max_length=100)
    is_cash_transaction: bool = False
    is_cross_border: bool = False
    transaction_purpose: Optional[str] = Field(None, max_length=500)
    transaction_details: Optional[Dict[str, Any]] = None


class TransactionMonitoringResponse(BaseModel):
    id: UUID
    tenant_id: str
    transaction_id: str
    transaction_type: str
    transaction_date: datetime
    customer_id: UUID
    customer_name: str
    transaction_amount: Decimal
    transaction_currency: str
    risk_score: Decimal
    risk_level: str
    is_cash_transaction: bool
    is_cross_border: bool
    customer_is_pep: bool
    rules_triggered: Optional[List[str]]
    alerts_generated: int
    requires_review: bool
    review_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionMonitoringFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    customer_id: Optional[UUID] = None
    risk_level: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    transaction_type: Optional[str] = None
    requires_review: Optional[bool] = None
    is_cash_transaction: Optional[bool] = None


# ============================================================================
# MONITORING RULE SCHEMAS
# ============================================================================

class MonitoringRuleCreate(BaseModel):
    rule_code: str = Field(..., max_length=50)
    rule_name: str = Field(..., max_length=200)
    rule_type: str
    description: Optional[str] = None
    threshold_amount: Optional[Decimal] = None
    threshold_count: Optional[int] = None
    time_period_days: Optional[int] = None
    risk_score_addition: Decimal = Field(default=0)
    auto_risk_level: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    priority: int = Field(default=5, ge=1, le=10)
    generate_alert: bool = True
    require_review: bool = False
    block_transaction: bool = False


class MonitoringRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    threshold_amount: Optional[Decimal] = None
    threshold_count: Optional[int] = None
    time_period_days: Optional[int] = None
    risk_score_addition: Optional[Decimal] = None
    auto_risk_level: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    generate_alert: Optional[bool] = None
    require_review: Optional[bool] = None
    block_transaction: Optional[bool] = None


class MonitoringRuleResponse(BaseModel):
    id: UUID
    tenant_id: str
    rule_code: str
    rule_name: str
    rule_type: str
    description: Optional[str]
    threshold_amount: Optional[Decimal]
    threshold_count: Optional[int]
    time_period_days: Optional[int]
    risk_score_addition: Decimal
    auto_risk_level: Optional[str]
    is_active: bool
    priority: int
    generate_alert: bool
    require_review: bool
    block_transaction: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AML ALERT SCHEMAS
# ============================================================================

class AMLAlertCreate(BaseModel):
    alert_type: str = Field(..., max_length=100)
    alert_category: str = Field(..., max_length=50)
    severity: str = Field(default="medium")
    transaction_monitoring_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    alert_title: str = Field(..., max_length=500)
    alert_description: Optional[str] = None
    rule_triggered: Optional[str] = Field(None, max_length=100)
    risk_score: Decimal = Field(default=0)
    risk_indicators: Optional[List[Dict[str, Any]]] = None
    due_date: Optional[datetime] = None


class AMLAlertResponse(BaseModel):
    id: UUID
    tenant_id: str
    alert_id: str
    alert_type: str
    alert_category: str
    severity: str
    transaction_monitoring_id: Optional[UUID]
    customer_id: Optional[UUID]
    alert_title: str
    alert_description: Optional[str]
    rule_triggered: Optional[str]
    risk_score: Decimal
    status: str
    assigned_to: Optional[UUID]
    false_positive: bool
    str_filed: bool
    due_date: Optional[datetime]
    is_overdue: bool
    escalation_level: int
    created_at: datetime

    class Config:
        from_attributes = True


class AMLAlertAssignment(BaseModel):
    assigned_to: UUID


class AMLAlertReview(BaseModel):
    investigation_notes: str
    false_positive: bool = False


class AMLAlertClose(BaseModel):
    resolution: str  # false_positive, reported, no_action
    notes: str


# ============================================================================
# CTR SCHEMAS
# ============================================================================

class CTRReportCreate(BaseModel):
    reporting_month: str = Field(..., max_length=7)  # YYYY-MM
    transaction_date: date
    transaction_type: str = Field(..., max_length=50)
    transaction_amount: Decimal = Field(..., gt=0)
    customer_id: UUID
    customer_name: str = Field(..., max_length=300)
    customer_type: str = Field(..., max_length=50)
    pan_number: Optional[str] = Field(None, max_length=10)
    aadhaar_number: Optional[str] = Field(None, max_length=12)
    passport_number: Optional[str] = Field(None, max_length=50)
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = Field(None, max_length=20)
    occupation: Optional[str] = Field(None, max_length=200)
    nature_of_business: Optional[str] = Field(None, max_length=300)
    account_number: str = Field(..., max_length=50)
    account_type: Optional[str] = Field(None, max_length=50)
    branch_code: Optional[str] = Field(None, max_length=50)
    branch_name: Optional[str] = Field(None, max_length=200)
    mode_of_transaction: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default='INR', max_length=3)
    identity_verified: bool = False
    verification_document_type: Optional[str] = Field(None, max_length=100)
    verification_document_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None


class CTRReportResponse(BaseModel):
    id: UUID
    tenant_id: str
    ctr_number: str
    reporting_month: str
    reporting_date: date
    transaction_date: date
    transaction_type: str
    transaction_amount: Decimal
    customer_id: UUID
    customer_name: str
    pan_number: Optional[str]
    account_number: str
    status: str
    submitted_to_fiu: bool
    fiu_submission_date: Optional[datetime]
    fiu_reference_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CTRBulkSubmit(BaseModel):
    reporting_month: str = Field(..., max_length=7)
    ctr_ids: List[UUID]


# ============================================================================
# STR SCHEMAS
# ============================================================================

class STRReportCreate(BaseModel):
    customer_id: UUID
    customer_name: str = Field(..., max_length=300)
    customer_type: str = Field(..., max_length=50)
    pan_number: Optional[str] = Field(None, max_length=10)
    aadhaar_number: Optional[str] = Field(None, max_length=12)
    passport_number: Optional[str] = Field(None, max_length=50)
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_email: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    account_numbers: List[str]
    suspicious_activity_type: str = Field(..., max_length=100)
    activity_start_date: date
    activity_end_date: date
    total_amount_involved: Decimal = Field(..., gt=0)
    number_of_transactions: int = Field(default=1, ge=1)
    suspicious_activity_description: str
    reason_for_suspicion: str
    transaction_ids: Optional[List[str]] = None
    alert_ids: Optional[List[UUID]] = None
    risk_level: str = Field(default="high")
    risk_indicators: Optional[List[Dict[str, Any]]] = None
    investigation_summary: Optional[str] = None
    supporting_documents: Optional[List[Dict[str, Any]]] = None
    related_parties: Optional[List[Dict[str, Any]]] = None


class STRReportUpdate(BaseModel):
    suspicious_activity_description: Optional[str] = None
    reason_for_suspicion: Optional[str] = None
    investigation_summary: Optional[str] = None
    supporting_documents: Optional[List[Dict[str, Any]]] = None


class STRReportResponse(BaseModel):
    id: UUID
    tenant_id: str
    str_number: str
    report_date: date
    customer_id: UUID
    customer_name: str
    customer_type: str
    suspicious_activity_type: str
    activity_start_date: date
    activity_end_date: date
    total_amount_involved: Decimal
    number_of_transactions: int
    risk_level: str
    status: str
    prepared_by: UUID
    prepared_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    submitted_to_fiu: bool
    fiu_submission_date: Optional[datetime]
    fiu_reference_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class STRReportApproval(BaseModel):
    approval_remarks: str


class STRFIUSubmission(BaseModel):
    fiu_reference_number: str


# ============================================================================
# PEP SCREENING SCHEMAS
# ============================================================================

class PEPScreeningCreate(BaseModel):
    customer_id: UUID
    customer_name: str = Field(..., max_length=300)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)
    screening_type: str = Field(..., max_length=50)
    trigger_event: Optional[str] = Field(None, max_length=100)


class PEPScreeningUpdate(BaseModel):
    screening_status: str
    is_pep: bool
    pep_category: Optional[str] = None
    match_score: Optional[Decimal] = None
    match_details: Optional[Dict[str, Any]] = None
    pep_position: Optional[str] = Field(None, max_length=300)
    pep_organization: Optional[str] = Field(None, max_length=300)
    pep_country: Optional[str] = Field(None, max_length=100)
    pep_start_date: Optional[date] = None
    pep_end_date: Optional[date] = None
    edd_required: bool = False
    source_of_wealth: Optional[str] = None
    source_of_funds: Optional[str] = None
    risk_rating: Optional[str] = Field(None, max_length=20)


class PEPScreeningResponse(BaseModel):
    id: UUID
    tenant_id: str
    screening_id: str
    screening_date: datetime
    customer_id: UUID
    customer_name: str
    date_of_birth: Optional[date]
    nationality: Optional[str]
    screening_type: str
    screening_status: str
    is_pep: bool
    pep_category: Optional[str]
    match_score: Optional[Decimal]
    pep_position: Optional[str]
    pep_organization: Optional[str]
    pep_country: Optional[str]
    edd_required: bool
    edd_completed: bool
    risk_rating: Optional[str]
    next_review_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class PEPEDDCompletion(BaseModel):
    edd_summary: str
    source_of_wealth: str
    source_of_funds: str
    risk_rating: str
    approval_remarks: Optional[str] = None


# ============================================================================
# SANCTION LIST SCHEMAS
# ============================================================================

class SanctionListCreate(BaseModel):
    list_id: str = Field(..., max_length=50)
    list_name: str = Field(..., max_length=200)
    list_type: str = Field(..., max_length=100)
    list_source: Optional[str] = Field(None, max_length=200)
    list_url: Optional[str] = Field(None, max_length=500)
    entity_name: str = Field(..., max_length=500)
    entity_type: Optional[str] = Field(None, max_length=50)
    aliases: Optional[List[str]] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = Field(None, max_length=200)
    nationality: Optional[str] = Field(None, max_length=100)
    passport_numbers: Optional[List[str]] = None
    identification_numbers: Optional[List[Dict[str, str]]] = None
    addresses: Optional[List[Dict[str, str]]] = None
    sanction_type: Optional[str] = Field(None, max_length=100)
    sanction_reason: Optional[str] = None
    designation_date: Optional[date] = None
    is_active: bool = True
    additional_info: Optional[Dict[str, Any]] = None


class SanctionListResponse(BaseModel):
    id: UUID
    tenant_id: str
    list_id: str
    list_name: str
    list_type: str
    entity_name: str
    entity_type: Optional[str]
    aliases: Optional[List[str]]
    nationality: Optional[str]
    sanction_type: Optional[str]
    designation_date: Optional[date]
    is_active: bool
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SanctionScreeningCreate(BaseModel):
    customer_id: UUID
    customer_name: str = Field(..., max_length=300)
    screening_name: Optional[str] = Field(None, max_length=300)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=100)
    screening_type: str = Field(..., max_length=50)
    trigger_event: Optional[str] = Field(None, max_length=100)


class SanctionScreeningUpdate(BaseModel):
    screening_status: str
    is_match_found: bool
    match_type: Optional[str] = Field(None, max_length=50)
    match_score: Optional[Decimal] = None
    matched_list_id: Optional[UUID] = None
    matched_list_name: Optional[str] = Field(None, max_length=200)
    match_details: Optional[Dict[str, Any]] = None
    decision: Optional[str] = Field(None, max_length=50)
    decision_rationale: Optional[str] = None
    account_blocked: bool = False
    transaction_blocked: bool = False
    authorities_notified: bool = False


class SanctionScreeningResponse(BaseModel):
    id: UUID
    tenant_id: str
    screening_id: str
    screening_date: datetime
    customer_id: UUID
    customer_name: str
    screening_type: str
    screening_status: str
    is_match_found: bool
    match_type: Optional[str]
    match_score: Optional[Decimal]
    matched_list_name: Optional[str]
    risk_level: str
    decision: Optional[str]
    account_blocked: bool
    transaction_blocked: bool
    authorities_notified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD & ANALYTICS SCHEMAS
# ============================================================================

class AMLDashboardStats(BaseModel):
    total_transactions_monitored: int
    high_risk_transactions: int
    cash_transactions: int
    cross_border_transactions: int
    total_alerts: int
    open_alerts: int
    under_review_alerts: int
    escalated_alerts: int
    closed_alerts: int
    total_ctr_reports: int
    pending_ctr_reports: int
    submitted_ctr_reports: int
    total_str_reports: int
    pending_str_reports: int
    submitted_str_reports: int
    total_pep_screenings: int
    confirmed_peps: int
    total_sanction_screenings: int
    sanction_matches: int
    alerts_by_type: Dict[str, int]
    transactions_by_risk: Dict[str, int]


class AMLAlertTrend(BaseModel):
    date: date
    alert_count: int
    high_severity_count: int
    closed_count: int


class TransactionAnalytics(BaseModel):
    period: str
    total_volume: int
    total_amount: Decimal
    high_risk_volume: int
    high_risk_amount: Decimal
    cash_volume: int
    cash_amount: Decimal
    average_transaction_amount: Decimal
