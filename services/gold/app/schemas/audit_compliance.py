"""
Audit & Compliance Schemas
Phase 12: Audit & Compliance
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# ============================================================================
# AUDIT TRAIL SCHEMAS
# ============================================================================

class AuditTrailBase(BaseModel):
    event_type: str = Field(..., max_length=50)
    event_category: str = Field(..., max_length=50)
    entity_type: str = Field(..., max_length=100)
    entity_id: Optional[UUID] = None
    entity_reference: Optional[str] = Field(None, max_length=100)
    user_id: UUID
    user_name: Optional[str] = Field(None, max_length=200)
    user_role: Optional[str] = Field(None, max_length=100)
    user_ip_address: Optional[str] = None
    user_location: Optional[str] = Field(None, max_length=200)
    session_id: Optional[UUID] = None
    action_performed: str = Field(..., max_length=200)
    action_status: str = Field(..., max_length=20)
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_fields: Optional[List[str]] = None
    request_method: Optional[str] = Field(None, max_length=10)
    request_endpoint: Optional[str] = Field(None, max_length=500)
    request_payload: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_message: Optional[str] = None
    transaction_id: Optional[UUID] = None
    parent_audit_id: Optional[UUID] = None
    workflow_id: Optional[UUID] = None
    approval_level: Optional[int] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    security_flag: bool = False
    compliance_flag: bool = False
    fraud_flag: bool = False
    remarks: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    processing_duration_ms: Optional[int] = None


class AuditTrailCreate(AuditTrailBase):
    pass


class AuditTrailResponse(AuditTrailBase):
    audit_id: UUID
    event_timestamp: datetime
    is_archived: bool
    archived_at: Optional[datetime]
    retention_until: Optional[date]

    class Config:
        from_attributes = True


class AuditTrailFilter(BaseModel):
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    action_status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    security_flag: Optional[bool] = None
    compliance_flag: Optional[bool] = None
    fraud_flag: Optional[bool] = None


# ============================================================================
# COMPLIANCE RULE SCHEMAS
# ============================================================================

class ComplianceRuleBase(BaseModel):
    rule_code: str = Field(..., max_length=50)
    rule_name: str = Field(..., max_length=200)
    rule_category: str = Field(..., max_length=50)
    regulation_name: Optional[str] = Field(None, max_length=200)
    regulation_code: Optional[str] = Field(None, max_length=100)
    regulatory_body: Optional[str] = Field(None, max_length=200)
    jurisdiction: Optional[str] = Field(None, max_length=100)
    rule_description: str
    rule_type: str = Field(..., max_length=50)
    severity_level: str = Field(..., max_length=20)
    applicable_entities: Optional[List[str]] = None
    applicable_processes: Optional[List[str]] = None
    applicable_departments: Optional[List[str]] = None
    validation_method: Optional[str] = Field(None, max_length=50)
    validation_frequency: Optional[str] = Field(None, max_length=50)
    validation_query: Optional[str] = None
    validation_script: Optional[str] = None
    threshold_values: Optional[Dict[str, Any]] = None
    breach_conditions: Optional[Dict[str, Any]] = None
    on_breach_action: Optional[str] = Field(None, max_length=50)
    escalation_rules: Optional[Dict[str, Any]] = None
    remediation_steps: Optional[str] = None
    reference_documents: Optional[Dict[str, Any]] = None
    related_rules: Optional[List[UUID]] = None
    is_active: bool = True
    effective_from: date
    effective_to: Optional[date] = None
    next_review_date: Optional[date] = None


class ComplianceRuleCreate(ComplianceRuleBase):
    created_by: UUID


class ComplianceRuleUpdate(BaseModel):
    rule_name: Optional[str] = Field(None, max_length=200)
    rule_description: Optional[str] = None
    severity_level: Optional[str] = Field(None, max_length=20)
    validation_method: Optional[str] = Field(None, max_length=50)
    validation_frequency: Optional[str] = Field(None, max_length=50)
    threshold_values: Optional[Dict[str, Any]] = None
    on_breach_action: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    effective_to: Optional[date] = None
    next_review_date: Optional[date] = None
    updated_by: UUID


class ComplianceRuleResponse(ComplianceRuleBase):
    rule_id: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    last_reviewed_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMPLIANCE VIOLATION SCHEMAS
# ============================================================================

class ComplianceViolationBase(BaseModel):
    rule_id: UUID
    violation_type: str = Field(..., max_length=50)
    severity_level: str = Field(..., max_length=20)
    violation_date: datetime
    detection_method: Optional[str] = Field(None, max_length=50)
    entity_type: str = Field(..., max_length=100)
    entity_id: Optional[UUID] = None
    entity_reference: Optional[str] = Field(None, max_length=200)
    violation_description: str
    root_cause: Optional[str] = None
    contributing_factors: Optional[Dict[str, Any]] = None
    business_impact: Optional[str] = None
    financial_impact: Optional[Decimal] = None
    evidence_documents: Optional[Dict[str, Any]] = None
    screenshots: Optional[Dict[str, Any]] = None
    audit_trail_references: Optional[List[UUID]] = None
    immediate_action_taken: Optional[str] = None
    corrective_actions: Optional[Dict[str, Any]] = None
    preventive_actions: Optional[Dict[str, Any]] = None
    assigned_to: Optional[UUID] = None
    responsible_party: Optional[UUID] = None
    requires_regulatory_reporting: bool = False
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None


class ComplianceViolationCreate(ComplianceViolationBase):
    detected_by: UUID
    created_by: UUID


class ComplianceViolationUpdate(BaseModel):
    violation_status: Optional[str] = Field(None, max_length=20)
    assigned_to: Optional[UUID] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[Dict[str, Any]] = None
    preventive_actions: Optional[Dict[str, Any]] = None
    resolution_summary: Optional[str] = None
    lessons_learned: Optional[str] = None
    reported_to_regulator: Optional[bool] = None
    regulator_reference: Optional[str] = Field(None, max_length=100)
    updated_by: UUID


class ComplianceViolationResponse(ComplianceViolationBase):
    violation_id: UUID
    violation_number: str
    violation_status: str
    resolution_date: Optional[datetime]
    resolution_summary: Optional[str]
    lessons_learned: Optional[str]
    detected_by: UUID
    resolved_by: Optional[UUID]
    reported_to_regulator: bool
    regulator_reference: Optional[str]
    reporting_date: Optional[date]
    regulator_response: Optional[str]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceViolationResolve(BaseModel):
    resolution_summary: str
    lessons_learned: Optional[str] = None
    resolved_by: UUID


# ============================================================================
# AUDIT SCHEDULE SCHEMAS
# ============================================================================

class AuditScheduleBase(BaseModel):
    schedule_name: str = Field(..., max_length=200)
    schedule_code: str = Field(..., max_length=50)
    audit_type: str = Field(..., max_length=50)
    audit_category: str = Field(..., max_length=50)
    audit_scope: str
    audit_objectives: Optional[str] = None
    areas_to_audit: Optional[List[str]] = None
    processes_to_review: Optional[List[str]] = None
    frequency_type: str = Field(..., max_length=50)
    frequency_value: Optional[int] = None
    frequency_unit: Optional[str] = Field(None, max_length=20)
    start_date: date
    end_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    lead_auditor: Optional[UUID] = None
    audit_team: Optional[List[UUID]] = None
    estimated_duration_days: Optional[int] = None
    budget_amount: Optional[Decimal] = None
    notification_before_days: int = 7
    notify_users: Optional[List[UUID]] = None
    is_mandatory: bool = False


class AuditScheduleCreate(AuditScheduleBase):
    created_by: UUID


class AuditScheduleUpdate(BaseModel):
    schedule_name: Optional[str] = Field(None, max_length=200)
    audit_scope: Optional[str] = None
    next_audit_date: Optional[date] = None
    lead_auditor: Optional[UUID] = None
    audit_team: Optional[List[UUID]] = None
    schedule_status: Optional[str] = Field(None, max_length=20)
    updated_by: UUID


class AuditScheduleResponse(AuditScheduleBase):
    schedule_id: UUID
    last_audit_date: Optional[date]
    schedule_status: str
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



# ============================================================================
# AUDIT EXECUTION SCHEMAS
# ============================================================================

class AuditExecutionBase(BaseModel):
    schedule_id: Optional[UUID] = None
    audit_type: str = Field(..., max_length=50)
    audit_name: str = Field(..., max_length=200)
    planned_start_date: date
    planned_end_date: date
    audit_scope: str
    audit_criteria: Optional[str] = None
    sampling_method: Optional[str] = Field(None, max_length=100)
    sample_size: Optional[int] = None
    lead_auditor: UUID
    audit_team_members: Optional[List[UUID]] = None
    external_auditors: Optional[Dict[str, Any]] = None
    methodology_used: Optional[str] = Field(None, max_length=100)
    standards_followed: Optional[List[str]] = None
    tools_used: Optional[List[str]] = None


class AuditExecutionCreate(AuditExecutionBase):
    created_by: UUID


class AuditExecutionUpdate(BaseModel):
    execution_status: Optional[str] = Field(None, max_length=20)
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    overall_rating: Optional[str] = Field(None, max_length=20)
    key_observations: Optional[str] = None
    strengths_identified: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    draft_report_date: Optional[date] = None
    final_report_date: Optional[date] = None
    report_file_path: Optional[str] = Field(None, max_length=500)
    executive_summary: Optional[str] = None
    evidence_collected: Optional[Dict[str, Any]] = None
    updated_by: UUID


class AuditExecutionResponse(AuditExecutionBase):
    execution_id: UUID
    execution_number: str
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    execution_status: str
    completion_percentage: int
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    overall_rating: Optional[str]
    key_observations: Optional[str]
    strengths_identified: Optional[str]
    areas_for_improvement: Optional[str]
    draft_report_date: Optional[date]
    final_report_date: Optional[date]
    report_file_path: Optional[str]
    executive_summary: Optional[str]
    requires_follow_up: bool
    follow_up_date: Optional[date]
    follow_up_completed: bool
    evidence_collected: Optional[Dict[str, Any]]
    created_by: UUID
    updated_by: Optional[UUID]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditExecutionApprove(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


# ============================================================================
# AUDIT FINDING SCHEMAS
# ============================================================================

class AuditFindingBase(BaseModel):
    execution_id: UUID
    finding_type: str = Field(..., max_length=50)
    finding_category: str = Field(..., max_length=50)
    severity_level: str = Field(..., max_length=20)
    risk_level: str = Field(..., max_length=20)
    finding_title: str = Field(..., max_length=500)
    finding_description: str
    condition_observed: str
    criteria_reference: Optional[str] = None
    cause_analysis: Optional[str] = None
    effect_impact: Optional[str] = None
    financial_impact: Optional[Decimal] = None
    operational_impact: Optional[str] = None
    reputational_impact: Optional[str] = None
    compliance_impact: Optional[str] = None
    recommendation: str
    management_response: Optional[str] = None
    agreed_action_plan: Optional[str] = None
    process_owner: Optional[UUID] = None
    responsible_person: Optional[UUID] = None
    remediation_owner: Optional[UUID] = None
    target_completion_date: Optional[date] = None
    evidence_documents: Optional[Dict[str, Any]] = None
    screenshots: Optional[Dict[str, Any]] = None
    supporting_data: Optional[Dict[str, Any]] = None
    is_repeat_finding: bool = False
    previous_finding_id: Optional[UUID] = None


class AuditFindingCreate(AuditFindingBase):
    identified_by: UUID
    created_by: UUID


class AuditFindingUpdate(BaseModel):
    finding_status: Optional[str] = Field(None, max_length=20)
    management_response: Optional[str] = None
    agreed_action_plan: Optional[str] = None
    responsible_person: Optional[UUID] = None
    target_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    resolution_description: Optional[str] = None
    resolution_evidence: Optional[Dict[str, Any]] = None
    follow_up_notes: Optional[str] = None
    updated_by: UUID


class AuditFindingResponse(AuditFindingBase):
    finding_id: UUID
    finding_number: str
    finding_status: str
    actual_completion_date: Optional[date]
    extended_deadline: Optional[date]
    extension_reason: Optional[str]
    resolution_description: Optional[str]
    resolution_evidence: Optional[Dict[str, Any]]
    verified_by: Optional[UUID]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    recurrence_count: int
    follow_up_required: bool
    follow_up_date: Optional[date]
    follow_up_notes: Optional[str]
    identified_by: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditFindingVerify(BaseModel):
    verified_by: UUID
    verification_notes: Optional[str] = None


# ============================================================================
# REGULATORY REPORT SCHEMAS
# ============================================================================

class RegulatoryReportBase(BaseModel):
    report_name: str = Field(..., max_length=200)
    report_type: str = Field(..., max_length=50)
    report_category: str = Field(..., max_length=50)
    regulatory_body: str = Field(..., max_length=200)
    regulation_reference: Optional[str] = Field(None, max_length=100)
    report_template_code: Optional[str] = Field(None, max_length=50)
    reporting_frequency: Optional[str] = Field(None, max_length=50)
    reporting_period_from: date
    reporting_period_to: date
    due_date: date
    report_data: Dict[str, Any]
    calculated_metrics: Optional[Dict[str, Any]] = None
    supporting_schedules: Optional[Dict[str, Any]] = None
    explanatory_notes: Optional[str] = None
    submission_method: Optional[str] = Field(None, max_length=50)
    report_format: Optional[str] = Field(None, max_length=20)


class RegulatoryReportCreate(RegulatoryReportBase):
    prepared_by: UUID
    created_by: UUID


class RegulatoryReportUpdate(BaseModel):
    report_status: Optional[str] = Field(None, max_length=20)
    report_data: Optional[Dict[str, Any]] = None
    calculated_metrics: Optional[Dict[str, Any]] = None
    explanatory_notes: Optional[str] = None
    report_file_path: Optional[str] = Field(None, max_length=500)
    updated_by: UUID


class RegulatoryReportResponse(RegulatoryReportBase):
    report_id: UUID
    report_number: str
    submission_date: Optional[date]
    submission_reference: Optional[str]
    report_file_path: Optional[str]
    file_size_kb: Optional[int]
    file_hash: Optional[str]
    report_status: str
    prepared_by: UUID
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    submitted_by: Optional[UUID]
    acknowledgement_received: bool
    acknowledgement_date: Optional[date]
    acknowledgement_reference: Optional[str]
    regulator_feedback: Optional[str]
    is_revised: bool
    revision_number: int
    revision_reason: Optional[str]
    original_report_id: Optional[UUID]
    is_overdue: bool
    reminder_sent: bool
    escalation_level: int
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegulatoryReportApprove(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


class RegulatoryReportSubmit(BaseModel):
    submitted_by: UUID
    submission_date: date
    submission_reference: Optional[str] = Field(None, max_length=100)


# ============================================================================
# COMPLIANCE CERTIFICATION SCHEMAS
# ============================================================================

class ComplianceCertificationBase(BaseModel):
    certification_name: str = Field(..., max_length=200)
    certification_type: str = Field(..., max_length=50)
    certification_category: str = Field(..., max_length=50)
    standard_name: str = Field(..., max_length=200)
    standard_version: Optional[str] = Field(None, max_length=50)
    standard_body: Optional[str] = Field(None, max_length=200)
    certification_scope: str
    covered_processes: Optional[List[str]] = None
    covered_systems: Optional[List[str]] = None
    covered_locations: Optional[List[str]] = None
    issue_date: date
    expiry_date: date
    assessment_body: Optional[str] = Field(None, max_length=200)
    assessor_name: Optional[str] = Field(None, max_length=200)
    assessment_result: Optional[str] = Field(None, max_length=50)
    conditions_or_observations: Optional[str] = None
    certificate_file_path: Optional[str] = Field(None, max_length=500)
    certificate_number: Optional[str] = Field(None, max_length=100)
    certification_cost: Optional[Decimal] = None
    annual_maintenance_cost: Optional[Decimal] = None


class ComplianceCertificationCreate(ComplianceCertificationBase):
    created_by: UUID


class ComplianceCertificationUpdate(BaseModel):
    certification_status: Optional[str] = Field(None, max_length=20)
    expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    last_surveillance_date: Optional[date] = None
    next_surveillance_date: Optional[date] = None
    surveillance_audits: Optional[Dict[str, Any]] = None
    gaps_identified: Optional[Dict[str, Any]] = None
    remediation_plan: Optional[str] = None
    updated_by: UUID


class ComplianceCertificationResponse(ComplianceCertificationBase):
    certification_id: UUID
    certification_number: str
    renewal_date: Optional[date]
    assessment_date_from: Optional[date]
    assessment_date_to: Optional[date]
    certification_status: str
    assessment_report_path: Optional[str]
    supporting_documents: Optional[Dict[str, Any]]
    surveillance_audits: Optional[Dict[str, Any]]
    last_surveillance_date: Optional[date]
    next_surveillance_date: Optional[date]
    compliance_requirements: Optional[Dict[str, Any]]
    gaps_identified: Optional[Dict[str, Any]]
    remediation_plan: Optional[str]
    renewal_reminder_days: int
    notify_users: Optional[List[UUID]]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# POLICY ACKNOWLEDGEMENT SCHEMAS
# ============================================================================

class PolicyAcknowledgementBase(BaseModel):
    policy_id: UUID
    policy_name: str = Field(..., max_length=200)
    policy_version: str = Field(..., max_length=20)
    policy_type: str = Field(..., max_length=50)
    user_id: UUID
    user_name: str = Field(..., max_length=200)
    user_role: Optional[str] = Field(None, max_length=100)
    user_department: Optional[str] = Field(None, max_length=100)
    acknowledgement_method: Optional[str] = Field(None, max_length=50)
    acknowledgement_ip_address: Optional[str] = None
    acknowledgement_device: Optional[str] = Field(None, max_length=200)
    understanding_confirmed: bool
    quiz_taken: bool = False
    quiz_score: Optional[Decimal] = None
    quiz_passed: Optional[bool] = None
    valid_from: date
    valid_until: Optional[date] = None
    requires_renewal: bool = True
    renewal_frequency_days: Optional[int] = None


class PolicyAcknowledgementCreate(PolicyAcknowledgementBase):
    acknowledgement_date: datetime


class PolicyAcknowledgementUpdate(BaseModel):
    compliance_status: Optional[str] = Field(None, max_length=20)
    training_completed: Optional[bool] = None
    training_date: Optional[date] = None
    training_certificate_id: Optional[UUID] = None


class PolicyAcknowledgementResponse(PolicyAcknowledgementBase):
    acknowledgement_id: UUID
    acknowledgement_date: datetime
    compliance_status: str
    training_completed: bool
    training_date: Optional[date]
    training_certificate_id: Optional[UUID]
    reminder_sent: bool
    reminder_date: Optional[date]
    escalation_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DATA RETENTION LOG SCHEMAS
# ============================================================================

class DataRetentionLogBase(BaseModel):
    entity_type: str = Field(..., max_length=100)
    entity_id: Optional[UUID] = None
    entity_reference: Optional[str] = Field(None, max_length=200)
    action_type: str = Field(..., max_length=50)
    action_reason: str = Field(..., max_length=100)
    retention_policy_id: Optional[UUID] = None
    data_category: str = Field(..., max_length=100)
    data_classification: Optional[str] = Field(None, max_length=50)
    record_count: Optional[int] = None
    data_size_mb: Optional[Decimal] = None
    original_creation_date: Optional[date] = None
    retention_period_days: Optional[int] = None
    retention_expiry_date: Optional[date] = None
    legal_hold_applied: bool = False
    legal_hold_id: Optional[UUID] = None
    compliance_requirement: Optional[str] = None
    regulatory_reference: Optional[str] = Field(None, max_length=200)
    verification_required: bool = True
    is_recoverable: bool = False
    recovery_window_days: Optional[int] = None


class DataRetentionLogCreate(DataRetentionLogBase):
    initiated_by: UUID
    action_date: datetime


class DataRetentionLogUpdate(BaseModel):
    action_status: Optional[str] = Field(None, max_length=20)
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    verification_method: Optional[str] = Field(None, max_length=100)
    executed_by: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DataRetentionLogResponse(DataRetentionLogBase):
    log_id: UUID
    log_number: str
    action_date: datetime
    verified_by: Optional[UUID]
    verified_at: Optional[datetime]
    verification_method: Optional[str]
    recovery_location: Optional[str]
    data_hash: Optional[str]
    deletion_certificate_id: Optional[UUID]
    evidence_file_path: Optional[str]
    affected_systems: Optional[List[str]]
    backup_status: Optional[str]
    related_entities: Optional[Dict[str, Any]]
    action_status: str
    error_message: Optional[str]
    initiated_by: UUID
    approved_by: Optional[UUID]
    executed_by: Optional[UUID]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DataRetentionLogApprove(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class AuditTrailStatistics(BaseModel):
    total_events: int
    events_by_category: Dict[str, int]
    events_by_status: Dict[str, int]
    security_events: int
    compliance_events: int
    fraud_events: int
    unique_users: int


class ComplianceStatistics(BaseModel):
    total_rules: int
    active_rules: int
    total_violations: int
    open_violations: int
    violations_by_severity: Dict[str, int]
    total_financial_impact: Decimal


class AuditExecutionStatistics(BaseModel):
    total_executions: int
    executions_by_status: Dict[str, int]
    executions_by_type: Dict[str, int]
    total_findings: int
    findings_by_severity: Dict[str, int]
    average_completion_percentage: float


class RegulatoryReportStatistics(BaseModel):
    total_reports: int
    reports_by_status: Dict[str, int]
    overdue_reports: int
    pending_submissions: int
    reports_by_regulatory_body: Dict[str, int]
