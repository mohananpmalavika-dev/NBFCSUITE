"""
Audit & Compliance Models
Phase 12: Audit & Compliance
"""
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric, Text, ARRAY, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class AuditTrail(Base):
    """Universal audit trail for all system activities"""
    __tablename__ = 'audit_trails'
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event Information
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    entity_reference = Column(String(100))
    
    # User Information
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_name = Column(String(200))
    user_role = Column(String(100))
    user_ip_address = Column(INET)
    user_location = Column(String(200))
    session_id = Column(UUID(as_uuid=True), index=True)
    
    # Change Information
    action_performed = Column(String(200), nullable=False)
    action_status = Column(String(20), nullable=False, index=True)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    changed_fields = Column(ARRAY(Text))
    
    # Request Information
    request_method = Column(String(10))
    request_endpoint = Column(String(500))
    request_payload = Column(JSONB)
    response_status = Column(Integer)
    response_message = Column(Text)
    
    # Business Context
    transaction_id = Column(UUID(as_uuid=True), index=True)
    parent_audit_id = Column(UUID(as_uuid=True))
    workflow_id = Column(UUID(as_uuid=True))
    approval_level = Column(Integer)
    
    # Risk & Security
    risk_level = Column(String(20), index=True)
    security_flag = Column(Boolean, default=False, index=True)
    compliance_flag = Column(Boolean, default=False, index=True)
    fraud_flag = Column(Boolean, default=False, index=True)
    
    # Additional Information
    remarks = Column(Text)
    metadata = Column(JSONB)
    tags = Column(ARRAY(Text))
    
    # Timing
    event_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    processing_duration_ms = Column(Integer)
    
    # Archival
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime(timezone=True))
    retention_until = Column(Date, index=True)


class ComplianceRule(Base):
    """Compliance rules and regulatory requirements"""
    __tablename__ = 'compliance_rules'
    
    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Rule Identification
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    rule_category = Column(String(50), nullable=False, index=True)
    
    # Regulatory Information
    regulation_name = Column(String(200))
    regulation_code = Column(String(100))
    regulatory_body = Column(String(200))
    jurisdiction = Column(String(100))
    
    # Rule Details
    rule_description = Column(Text, nullable=False)
    rule_type = Column(String(50), nullable=False, index=True)
    severity_level = Column(String(20), nullable=False, index=True)
    
    # Scope
    applicable_entities = Column(ARRAY(Text))
    applicable_processes = Column(ARRAY(Text))
    applicable_departments = Column(ARRAY(Text))
    
    # Implementation
    validation_method = Column(String(50))
    validation_frequency = Column(String(50))
    validation_query = Column(Text)
    validation_script = Column(Text)
    
    # Thresholds & Limits
    threshold_values = Column(JSONB)
    breach_conditions = Column(JSONB)
    
    # Actions
    on_breach_action = Column(String(50))
    escalation_rules = Column(JSONB)
    remediation_steps = Column(Text)
    
    # Documentation
    reference_documents = Column(JSONB)
    related_rules = Column(ARRAY(UUID(as_uuid=True)))
    change_history = Column(JSONB)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    last_reviewed_date = Column(Date)
    next_review_date = Column(Date, index=True)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    violations = relationship("ComplianceViolation", back_populates="rule")




class ComplianceViolation(Base):
    """Compliance rule violations and breaches"""
    __tablename__ = 'compliance_violations'
    
    violation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Violation Identification
    violation_number = Column(String(50), unique=True, nullable=False, index=True)
    rule_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Violation Details
    violation_type = Column(String(50), nullable=False, index=True)
    severity_level = Column(String(20), nullable=False, index=True)
    violation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    detection_method = Column(String(50))
    
    # Entity Information
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    entity_reference = Column(String(200))
    
    # Context
    violation_description = Column(Text, nullable=False)
    root_cause = Column(Text)
    contributing_factors = Column(JSONB)
    business_impact = Column(Text)
    financial_impact = Column(Numeric(15, 2))
    
    # Evidence
    evidence_documents = Column(JSONB)
    screenshots = Column(JSONB)
    audit_trail_references = Column(ARRAY(UUID(as_uuid=True)))
    
    # Response
    immediate_action_taken = Column(Text)
    corrective_actions = Column(JSONB)
    preventive_actions = Column(JSONB)
    
    # Resolution
    violation_status = Column(String(20), nullable=False, default='open', index=True)
    resolution_date = Column(DateTime(timezone=True))
    resolution_summary = Column(Text)
    lessons_learned = Column(Text)
    
    # Responsibility
    detected_by = Column(UUID(as_uuid=True))
    assigned_to = Column(UUID(as_uuid=True), index=True)
    responsible_party = Column(UUID(as_uuid=True))
    resolved_by = Column(UUID(as_uuid=True))
    
    # Regulatory Reporting
    requires_regulatory_reporting = Column(Boolean, default=False, index=True)
    reported_to_regulator = Column(Boolean, default=False)
    regulator_reference = Column(String(100))
    reporting_date = Column(Date)
    regulator_response = Column(Text)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date, index=True)
    follow_up_notes = Column(Text)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rule = relationship("ComplianceRule", back_populates="violations")


class AuditSchedule(Base):
    """Scheduled audit plans and calendars"""
    __tablename__ = 'audit_schedules'
    
    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Schedule Information
    schedule_name = Column(String(200), nullable=False)
    schedule_code = Column(String(50), unique=True, nullable=False, index=True)
    audit_type = Column(String(50), nullable=False, index=True)
    audit_category = Column(String(50), nullable=False, index=True)
    
    # Scope
    audit_scope = Column(Text, nullable=False)
    audit_objectives = Column(Text)
    areas_to_audit = Column(ARRAY(Text))
    processes_to_review = Column(ARRAY(Text))
    
    # Frequency
    frequency_type = Column(String(50), nullable=False)
    frequency_value = Column(Integer)
    frequency_unit = Column(String(20))
    
    # Scheduling
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_audit_date = Column(Date, index=True)
    last_audit_date = Column(Date)
    
    # Resources
    lead_auditor = Column(UUID(as_uuid=True), index=True)
    audit_team = Column(ARRAY(UUID(as_uuid=True)))
    estimated_duration_days = Column(Integer)
    budget_amount = Column(Numeric(15, 2))
    
    # Notifications
    notification_before_days = Column(Integer, default=7)
    notify_users = Column(ARRAY(UUID(as_uuid=True)))
    
    # Status
    schedule_status = Column(String(20), nullable=False, default='active', index=True)
    is_mandatory = Column(Boolean, default=False)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("AuditExecution", back_populates="schedule")


class AuditExecution(Base):
    """Actual audit execution records"""
    __tablename__ = 'audit_executions'
    
    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Execution Information
    execution_number = Column(String(50), unique=True, nullable=False, index=True)
    schedule_id = Column(UUID(as_uuid=True), index=True)
    audit_type = Column(String(50), nullable=False, index=True)
    audit_name = Column(String(200), nullable=False)
    
    # Planning
    planned_start_date = Column(Date, nullable=False, index=True)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Scope
    audit_scope = Column(Text, nullable=False)
    audit_criteria = Column(Text)
    sampling_method = Column(String(100))
    sample_size = Column(Integer)
    
    # Team
    lead_auditor = Column(UUID(as_uuid=True), nullable=False, index=True)
    audit_team_members = Column(ARRAY(UUID(as_uuid=True)))
    external_auditors = Column(JSONB)
    
    # Execution
    execution_status = Column(String(20), nullable=False, default='planned', index=True)
    completion_percentage = Column(Integer, default=0)
    
    # Findings Summary
    total_findings = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    
    # Results
    overall_rating = Column(String(20), index=True)
    key_observations = Column(Text)
    strengths_identified = Column(Text)
    areas_for_improvement = Column(Text)
    
    # Reports
    draft_report_date = Column(Date)
    final_report_date = Column(Date)
    report_file_path = Column(String(500))
    executive_summary = Column(Text)
    
    # Follow-up
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(Date, index=True)
    follow_up_completed = Column(Boolean, default=False)
    
    # Metadata
    methodology_used = Column(String(100))
    standards_followed = Column(ARRAY(Text))
    tools_used = Column(ARRAY(Text))
    evidence_collected = Column(JSONB)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedule = relationship("AuditSchedule", back_populates="executions")
    findings = relationship("AuditFinding", back_populates="execution")


class AuditFinding(Base):
    """Individual audit findings and observations"""
    __tablename__ = 'audit_findings'
    
    finding_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Finding Information
    finding_number = Column(String(50), unique=True, nullable=False, index=True)
    execution_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Classification
    finding_type = Column(String(50), nullable=False, index=True)
    finding_category = Column(String(50), nullable=False)
    severity_level = Column(String(20), nullable=False, index=True)
    risk_level = Column(String(20), nullable=False, index=True)
    
    # Details
    finding_title = Column(String(500), nullable=False)
    finding_description = Column(Text, nullable=False)
    condition_observed = Column(Text, nullable=False)
    criteria_reference = Column(Text)
    cause_analysis = Column(Text)
    effect_impact = Column(Text)
    
    # Impact Assessment
    financial_impact = Column(Numeric(15, 2))
    operational_impact = Column(Text)
    reputational_impact = Column(Text)
    compliance_impact = Column(Text)
    
    # Recommendation
    recommendation = Column(Text, nullable=False)
    management_response = Column(Text)
    agreed_action_plan = Column(Text)
    
    # Responsible Parties
    process_owner = Column(UUID(as_uuid=True))
    responsible_person = Column(UUID(as_uuid=True), index=True)
    remediation_owner = Column(UUID(as_uuid=True))
    
    # Timeline
    target_completion_date = Column(Date, index=True)
    actual_completion_date = Column(Date)
    extended_deadline = Column(Date)
    extension_reason = Column(Text)
    
    # Status
    finding_status = Column(String(20), nullable=False, default='open', index=True)
    
    # Resolution
    resolution_description = Column(Text)
    resolution_evidence = Column(JSONB)
    verified_by = Column(UUID(as_uuid=True))
    verified_at = Column(DateTime(timezone=True))
    verification_notes = Column(Text)
    
    # Recurrence
    is_repeat_finding = Column(Boolean, default=False, index=True)
    previous_finding_id = Column(UUID(as_uuid=True))
    recurrence_count = Column(Integer, default=0)
    
    # Evidence
    evidence_documents = Column(JSONB)
    screenshots = Column(JSONB)
    supporting_data = Column(JSONB)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=True)
    follow_up_date = Column(Date, index=True)
    follow_up_notes = Column(Text)
    
    # Audit
    identified_by = Column(UUID(as_uuid=True), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    execution = relationship("AuditExecution", back_populates="findings")




class RegulatoryReport(Base):
    """Regulatory reporting submissions"""
    __tablename__ = 'regulatory_reports'
    
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report Information
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False, index=True)
    report_category = Column(String(50), nullable=False)
    
    # Regulatory Details
    regulatory_body = Column(String(200), nullable=False, index=True)
    regulation_reference = Column(String(100))
    report_template_code = Column(String(50))
    
    # Reporting Period
    reporting_frequency = Column(String(50))
    reporting_period_from = Column(Date, nullable=False, index=True)
    reporting_period_to = Column(Date, nullable=False, index=True)
    
    # Submission
    due_date = Column(Date, nullable=False, index=True)
    submission_date = Column(Date)
    submission_method = Column(String(50))
    submission_reference = Column(String(100))
    
    # Content
    report_data = Column(JSONB, nullable=False)
    calculated_metrics = Column(JSONB)
    supporting_schedules = Column(JSONB)
    explanatory_notes = Column(Text)
    
    # Files
    report_file_path = Column(String(500))
    report_format = Column(String(20))
    file_size_kb = Column(Integer)
    file_hash = Column(String(128))
    
    # Status
    report_status = Column(String(20), nullable=False, default='draft', index=True)
    
    # Workflow
    prepared_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    submitted_by = Column(UUID(as_uuid=True))
    
    # Response
    acknowledgement_received = Column(Boolean, default=False)
    acknowledgement_date = Column(Date)
    acknowledgement_reference = Column(String(100))
    regulator_feedback = Column(Text)
    
    # Revisions
    is_revised = Column(Boolean, default=False)
    revision_number = Column(Integer, default=1)
    revision_reason = Column(Text)
    original_report_id = Column(UUID(as_uuid=True))
    
    # Alerts
    is_overdue = Column(Boolean, default=False, index=True)
    reminder_sent = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceCertification(Base):
    """Compliance certifications and attestations"""
    __tablename__ = 'compliance_certifications'
    
    certification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Certification Information
    certification_number = Column(String(50), unique=True, nullable=False, index=True)
    certification_name = Column(String(200), nullable=False)
    certification_type = Column(String(50), nullable=False, index=True)
    certification_category = Column(String(50), nullable=False)
    
    # Standards
    standard_name = Column(String(200), nullable=False, index=True)
    standard_version = Column(String(50))
    standard_body = Column(String(200))
    
    # Scope
    certification_scope = Column(Text, nullable=False)
    covered_processes = Column(ARRAY(Text))
    covered_systems = Column(ARRAY(Text))
    covered_locations = Column(ARRAY(Text))
    
    # Validity
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    renewal_date = Column(Date)
    
    # Assessment
    assessment_body = Column(String(200))
    assessor_name = Column(String(200))
    assessment_date_from = Column(Date)
    assessment_date_to = Column(Date)
    
    # Results
    certification_status = Column(String(20), nullable=False, default='active', index=True)
    assessment_result = Column(String(50))
    conditions_or_observations = Column(Text)
    
    # Documentation
    certificate_file_path = Column(String(500))
    certificate_number = Column(String(100))
    assessment_report_path = Column(String(500))
    supporting_documents = Column(JSONB)
    
    # Maintenance
    surveillance_audits = Column(JSONB)
    last_surveillance_date = Column(Date)
    next_surveillance_date = Column(Date)
    
    # Compliance
    compliance_requirements = Column(JSONB)
    gaps_identified = Column(JSONB)
    remediation_plan = Column(Text)
    
    # Notifications
    renewal_reminder_days = Column(Integer, default=90)
    notify_users = Column(ARRAY(UUID(as_uuid=True)))
    
    # Costs
    certification_cost = Column(Numeric(15, 2))
    annual_maintenance_cost = Column(Numeric(15, 2))
    
    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PolicyAcknowledgement(Base):
    """Policy and procedure acknowledgements by users"""
    __tablename__ = 'policy_acknowledgements'
    
    acknowledgement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Policy Information
    policy_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    policy_name = Column(String(200), nullable=False)
    policy_version = Column(String(20), nullable=False)
    policy_type = Column(String(50), nullable=False)
    
    # User Information
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_name = Column(String(200), nullable=False)
    user_role = Column(String(100))
    user_department = Column(String(100))
    
    # Acknowledgement
    acknowledgement_date = Column(DateTime(timezone=True), nullable=False, index=True)
    acknowledgement_method = Column(String(50))
    acknowledgement_ip_address = Column(INET)
    acknowledgement_device = Column(String(200))
    
    # Understanding
    understanding_confirmed = Column(Boolean, nullable=False)
    quiz_taken = Column(Boolean, default=False)
    quiz_score = Column(Numeric(5, 2))
    quiz_passed = Column(Boolean)
    
    # Compliance
    compliance_status = Column(String(20), nullable=False, default='acknowledged', index=True)
    
    # Training
    training_completed = Column(Boolean, default=False)
    training_date = Column(Date)
    training_certificate_id = Column(UUID(as_uuid=True))
    
    # Validity
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, index=True)
    requires_renewal = Column(Boolean, default=True)
    renewal_frequency_days = Column(Integer)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_date = Column(Date)
    escalation_sent = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class DataRetentionLog(Base):
    """Data retention and deletion activity logs"""
    __tablename__ = 'data_retention_logs'
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Retention Information
    log_number = Column(String(50), unique=True, nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    entity_reference = Column(String(200))
    
    # Action Details
    action_type = Column(String(50), nullable=False, index=True)
    action_reason = Column(String(100), nullable=False)
    retention_policy_id = Column(UUID(as_uuid=True))
    
    # Data Details
    data_category = Column(String(100), nullable=False)
    data_classification = Column(String(50))
    record_count = Column(Integer)
    data_size_mb = Column(Numeric(15, 2))
    
    # Timing
    original_creation_date = Column(Date)
    retention_period_days = Column(Integer)
    retention_expiry_date = Column(Date, index=True)
    action_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Legal & Compliance
    legal_hold_applied = Column(Boolean, default=False, index=True)
    legal_hold_id = Column(UUID(as_uuid=True))
    compliance_requirement = Column(Text)
    regulatory_reference = Column(String(200))
    
    # Verification
    verification_required = Column(Boolean, default=True)
    verified_by = Column(UUID(as_uuid=True))
    verified_at = Column(DateTime(timezone=True))
    verification_method = Column(String(100))
    
    # Recovery
    is_recoverable = Column(Boolean, default=False)
    recovery_window_days = Column(Integer)
    recovery_location = Column(String(500))
    
    # Audit Trail
    data_hash = Column(String(128))
    deletion_certificate_id = Column(UUID(as_uuid=True))
    evidence_file_path = Column(String(500))
    
    # Metadata
    affected_systems = Column(ARRAY(Text))
    backup_status = Column(String(50))
    related_entities = Column(JSONB)
    
    # Status
    action_status = Column(String(20), nullable=False, default='pending', index=True)
    error_message = Column(Text)
    
    # Audit
    initiated_by = Column(UUID(as_uuid=True), nullable=False)
    approved_by = Column(UUID(as_uuid=True))
    executed_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))
