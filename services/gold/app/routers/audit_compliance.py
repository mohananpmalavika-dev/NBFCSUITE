"""
Audit & Compliance Router
Phase 12: Audit & Compliance
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from ..database import get_db
from ..models.audit_compliance import (
    AuditTrail, ComplianceRule, ComplianceViolation, AuditSchedule,
    AuditExecution, AuditFinding, RegulatoryReport, ComplianceCertification,
    PolicyAcknowledgement, DataRetentionLog
)
from ..schemas.audit_compliance import (
    AuditTrailCreate, AuditTrailResponse, AuditTrailFilter,
    ComplianceRuleCreate, ComplianceRuleUpdate, ComplianceRuleResponse,
    ComplianceViolationCreate, ComplianceViolationUpdate, ComplianceViolationResponse,
    ComplianceViolationResolve, AuditScheduleCreate, AuditScheduleUpdate, AuditScheduleResponse,
    AuditExecutionCreate, AuditExecutionUpdate, AuditExecutionResponse, AuditExecutionApprove,
    AuditFindingCreate, AuditFindingUpdate, AuditFindingResponse, AuditFindingVerify,
    RegulatoryReportCreate, RegulatoryReportUpdate, RegulatoryReportResponse,
    RegulatoryReportApprove, RegulatoryReportSubmit, ComplianceCertificationCreate,
    ComplianceCertificationUpdate, ComplianceCertificationResponse, PolicyAcknowledgementCreate,
    PolicyAcknowledgementUpdate, PolicyAcknowledgementResponse, DataRetentionLogCreate,
    DataRetentionLogUpdate, DataRetentionLogResponse, DataRetentionLogApprove,
    AuditTrailStatistics, ComplianceStatistics, AuditExecutionStatistics, RegulatoryReportStatistics
)

router = APIRouter(prefix="/api/v1/gold/audit-compliance", tags=["audit-compliance"])


# =====================================================
# Audit Trail Endpoints
# =====================================================

@router.post("/audit-trails", response_model=AuditTrailResponse, status_code=201)
def create_audit_trail(
    audit: AuditTrailCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit trail entry"""
    db_audit = AuditTrail(**audit.model_dump())
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit


@router.get("/audit-trails", response_model=List[AuditTrailResponse])
def list_audit_trails(
    event_type: Optional[str] = None,
    event_category: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    action_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    security_flag: Optional[bool] = None,
    compliance_flag: Optional[bool] = None,
    fraud_flag: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List audit trail entries with filters"""
    query = db.query(AuditTrail)
    
    if event_type:
        query = query.filter(AuditTrail.event_type == event_type)
    if event_category:
        query = query.filter(AuditTrail.event_category == event_category)
    if entity_type:
        query = query.filter(AuditTrail.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditTrail.entity_id == entity_id)
    if user_id:
        query = query.filter(AuditTrail.user_id == user_id)
    if action_status:
        query = query.filter(AuditTrail.action_status == action_status)
    if date_from:
        query = query.filter(AuditTrail.event_timestamp >= date_from)
    if date_to:
        query = query.filter(AuditTrail.event_timestamp <= date_to)
    if security_flag is not None:
        query = query.filter(AuditTrail.security_flag == security_flag)
    if compliance_flag is not None:
        query = query.filter(AuditTrail.compliance_flag == compliance_flag)
    if fraud_flag is not None:
        query = query.filter(AuditTrail.fraud_flag == fraud_flag)
    
    query = query.order_by(desc(AuditTrail.event_timestamp))
    return query.offset(skip).limit(limit).all()


@router.get("/audit-trails/{audit_id}", response_model=AuditTrailResponse)
def get_audit_trail(audit_id: UUID, db: Session = Depends(get_db)):
    """Get audit trail entry by ID"""
    audit = db.query(AuditTrail).filter(AuditTrail.audit_id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit trail entry not found")
    return audit


@router.get("/audit-trails/entity/{entity_type}/{entity_id}", response_model=List[AuditTrailResponse])
def get_entity_audit_trail(
    entity_type: str,
    entity_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get audit trail for a specific entity"""
    query = db.query(AuditTrail).filter(
        AuditTrail.entity_type == entity_type,
        AuditTrail.entity_id == entity_id
    ).order_by(desc(AuditTrail.event_timestamp))
    
    return query.offset(skip).limit(limit).all()


@router.post("/audit-trails/{audit_id}/archive", response_model=AuditTrailResponse)
def archive_audit_trail(audit_id: UUID, db: Session = Depends(get_db)):
    """Archive an audit trail entry"""
    audit = db.query(AuditTrail).filter(AuditTrail.audit_id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit trail entry not found")
    
    audit.is_archived = True
    audit.archived_at = datetime.utcnow()
    db.commit()
    db.refresh(audit)
    return audit


# =====================================================
# Compliance Rule Endpoints
# =====================================================

@router.post("/compliance-rules", response_model=ComplianceRuleResponse, status_code=201)
def create_compliance_rule(
    rule: ComplianceRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new compliance rule"""
    # Check for duplicate code
    existing = db.query(ComplianceRule).filter(
        ComplianceRule.rule_code == rule.rule_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule code already exists")
    
    db_rule = ComplianceRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/compliance-rules", response_model=List[ComplianceRuleResponse])
def list_compliance_rules(
    rule_category: Optional[str] = None,
    rule_type: Optional[str] = None,
    severity_level: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List compliance rules with filters"""
    query = db.query(ComplianceRule)
    
    if rule_category:
        query = query.filter(ComplianceRule.rule_category == rule_category)
    if rule_type:
        query = query.filter(ComplianceRule.rule_type == rule_type)
    if severity_level:
        query = query.filter(ComplianceRule.severity_level == severity_level)
    if is_active is not None:
        query = query.filter(ComplianceRule.is_active == is_active)
    
    query = query.order_by(ComplianceRule.rule_code)
    return query.offset(skip).limit(limit).all()


@router.get("/compliance-rules/{rule_id}", response_model=ComplianceRuleResponse)
def get_compliance_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """Get compliance rule by ID"""
    rule = db.query(ComplianceRule).filter(ComplianceRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    return rule


@router.put("/compliance-rules/{rule_id}", response_model=ComplianceRuleResponse)
def update_compliance_rule(
    rule_id: UUID,
    rule: ComplianceRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update compliance rule"""
    db_rule = db.query(ComplianceRule).filter(ComplianceRule.rule_id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    
    update_data = rule.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/compliance-rules/{rule_id}", status_code=204)
def delete_compliance_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """Delete compliance rule"""
    rule = db.query(ComplianceRule).filter(ComplianceRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")
    
    # Check if rule has violations
    violations = db.query(ComplianceViolation).filter(
        ComplianceViolation.rule_id == rule_id
    ).count()
    if violations > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete rule with existing violations. Deactivate instead."
        )
    
    db.delete(rule)
    db.commit()
    return None




# =====================================================
# Compliance Violation Endpoints
# =====================================================

@router.post("/compliance-violations", response_model=ComplianceViolationResponse, status_code=201)
def create_compliance_violation(
    violation: ComplianceViolationCreate,
    db: Session = Depends(get_db)
):
    """Create a new compliance violation"""
    db_violation = ComplianceViolation(**violation.model_dump())
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation


@router.get("/compliance-violations", response_model=List[ComplianceViolationResponse])
def list_compliance_violations(
    rule_id: Optional[UUID] = None,
    violation_type: Optional[str] = None,
    severity_level: Optional[str] = None,
    violation_status: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    assigned_to: Optional[UUID] = None,
    requires_regulatory_reporting: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List compliance violations with filters"""
    query = db.query(ComplianceViolation)
    
    if rule_id:
        query = query.filter(ComplianceViolation.rule_id == rule_id)
    if violation_type:
        query = query.filter(ComplianceViolation.violation_type == violation_type)
    if severity_level:
        query = query.filter(ComplianceViolation.severity_level == severity_level)
    if violation_status:
        query = query.filter(ComplianceViolation.violation_status == violation_status)
    if entity_type:
        query = query.filter(ComplianceViolation.entity_type == entity_type)
    if date_from:
        query = query.filter(ComplianceViolation.violation_date >= date_from)
    if date_to:
        query = query.filter(ComplianceViolation.violation_date <= date_to)
    if assigned_to:
        query = query.filter(ComplianceViolation.assigned_to == assigned_to)
    if requires_regulatory_reporting is not None:
        query = query.filter(ComplianceViolation.requires_regulatory_reporting == requires_regulatory_reporting)
    
    query = query.order_by(desc(ComplianceViolation.violation_date))
    return query.offset(skip).limit(limit).all()


@router.get("/compliance-violations/{violation_id}", response_model=ComplianceViolationResponse)
def get_compliance_violation(violation_id: UUID, db: Session = Depends(get_db)):
    """Get compliance violation by ID"""
    violation = db.query(ComplianceViolation).filter(
        ComplianceViolation.violation_id == violation_id
    ).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Compliance violation not found")
    return violation


@router.put("/compliance-violations/{violation_id}", response_model=ComplianceViolationResponse)
def update_compliance_violation(
    violation_id: UUID,
    violation: ComplianceViolationUpdate,
    db: Session = Depends(get_db)
):
    """Update compliance violation"""
    db_violation = db.query(ComplianceViolation).filter(
        ComplianceViolation.violation_id == violation_id
    ).first()
    if not db_violation:
        raise HTTPException(status_code=404, detail="Compliance violation not found")
    
    if db_violation.violation_status == 'closed':
        raise HTTPException(status_code=400, detail="Cannot update closed violation")
    
    update_data = violation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_violation, field, value)
    
    db.commit()
    db.refresh(db_violation)
    return db_violation


@router.post("/compliance-violations/{violation_id}/resolve", response_model=ComplianceViolationResponse)
def resolve_compliance_violation(
    violation_id: UUID,
    request: ComplianceViolationResolve,
    db: Session = Depends(get_db)
):
    """Resolve a compliance violation"""
    violation = db.query(ComplianceViolation).filter(
        ComplianceViolation.violation_id == violation_id
    ).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Compliance violation not found")
    
    if violation.violation_status == 'closed':
        raise HTTPException(status_code=400, detail="Violation already closed")
    
    violation.violation_status = 'closed'
    violation.resolution_date = datetime.utcnow()
    violation.resolution_summary = request.resolution_summary
    violation.lessons_learned = request.lessons_learned
    violation.resolved_by = request.resolved_by
    
    db.commit()
    db.refresh(violation)
    return violation


@router.delete("/compliance-violations/{violation_id}", status_code=204)
def delete_compliance_violation(violation_id: UUID, db: Session = Depends(get_db)):
    """Delete compliance violation"""
    violation = db.query(ComplianceViolation).filter(
        ComplianceViolation.violation_id == violation_id
    ).first()
    if not violation:
        raise HTTPException(status_code=404, detail="Compliance violation not found")
    
    if violation.violation_status == 'closed':
        raise HTTPException(status_code=400, detail="Cannot delete closed violation")
    
    db.delete(violation)
    db.commit()
    return None


# =====================================================
# Audit Schedule Endpoints
# =====================================================

@router.post("/audit-schedules", response_model=AuditScheduleResponse, status_code=201)
def create_audit_schedule(
    schedule: AuditScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit schedule"""
    # Check for duplicate code
    existing = db.query(AuditSchedule).filter(
        AuditSchedule.schedule_code == schedule.schedule_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Schedule code already exists")
    
    db_schedule = AuditSchedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/audit-schedules", response_model=List[AuditScheduleResponse])
def list_audit_schedules(
    audit_type: Optional[str] = None,
    audit_category: Optional[str] = None,
    schedule_status: Optional[str] = None,
    lead_auditor: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List audit schedules with filters"""
    query = db.query(AuditSchedule)
    
    if audit_type:
        query = query.filter(AuditSchedule.audit_type == audit_type)
    if audit_category:
        query = query.filter(AuditSchedule.audit_category == audit_category)
    if schedule_status:
        query = query.filter(AuditSchedule.schedule_status == schedule_status)
    if lead_auditor:
        query = query.filter(AuditSchedule.lead_auditor == lead_auditor)
    
    query = query.order_by(AuditSchedule.next_audit_date)
    return query.offset(skip).limit(limit).all()


@router.get("/audit-schedules/{schedule_id}", response_model=AuditScheduleResponse)
def get_audit_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    """Get audit schedule by ID"""
    schedule = db.query(AuditSchedule).filter(
        AuditSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Audit schedule not found")
    return schedule


@router.put("/audit-schedules/{schedule_id}", response_model=AuditScheduleResponse)
def update_audit_schedule(
    schedule_id: UUID,
    schedule: AuditScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Update audit schedule"""
    db_schedule = db.query(AuditSchedule).filter(
        AuditSchedule.schedule_id == schedule_id
    ).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Audit schedule not found")
    
    update_data = schedule.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.delete("/audit-schedules/{schedule_id}", status_code=204)
def delete_audit_schedule(schedule_id: UUID, db: Session = Depends(get_db)):
    """Delete audit schedule"""
    schedule = db.query(AuditSchedule).filter(
        AuditSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Audit schedule not found")
    
    db.delete(schedule)
    db.commit()
    return None



# =====================================================
# Audit Execution Endpoints
# =====================================================

@router.post("/audit-executions", response_model=AuditExecutionResponse, status_code=201)
def create_audit_execution(
    execution: AuditExecutionCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit execution"""
    db_execution = AuditExecution(**execution.model_dump())
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


@router.get("/audit-executions", response_model=List[AuditExecutionResponse])
def list_audit_executions(
    schedule_id: Optional[UUID] = None,
    audit_type: Optional[str] = None,
    execution_status: Optional[str] = None,
    lead_auditor: Optional[UUID] = None,
    overall_rating: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List audit executions with filters"""
    query = db.query(AuditExecution)
    
    if schedule_id:
        query = query.filter(AuditExecution.schedule_id == schedule_id)
    if audit_type:
        query = query.filter(AuditExecution.audit_type == audit_type)
    if execution_status:
        query = query.filter(AuditExecution.execution_status == execution_status)
    if lead_auditor:
        query = query.filter(AuditExecution.lead_auditor == lead_auditor)
    if overall_rating:
        query = query.filter(AuditExecution.overall_rating == overall_rating)
    if date_from:
        query = query.filter(AuditExecution.planned_start_date >= date_from)
    if date_to:
        query = query.filter(AuditExecution.planned_start_date <= date_to)
    
    query = query.order_by(desc(AuditExecution.planned_start_date))
    return query.offset(skip).limit(limit).all()


@router.get("/audit-executions/{execution_id}", response_model=AuditExecutionResponse)
def get_audit_execution(execution_id: UUID, db: Session = Depends(get_db)):
    """Get audit execution by ID"""
    execution = db.query(AuditExecution).filter(
        AuditExecution.execution_id == execution_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Audit execution not found")
    return execution


@router.put("/audit-executions/{execution_id}", response_model=AuditExecutionResponse)
def update_audit_execution(
    execution_id: UUID,
    execution: AuditExecutionUpdate,
    db: Session = Depends(get_db)
):
    """Update audit execution"""
    db_execution = db.query(AuditExecution).filter(
        AuditExecution.execution_id == execution_id
    ).first()
    if not db_execution:
        raise HTTPException(status_code=404, detail="Audit execution not found")
    
    update_data = execution.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_execution, field, value)
    
    db.commit()
    db.refresh(db_execution)
    return db_execution


@router.post("/audit-executions/{execution_id}/approve", response_model=AuditExecutionResponse)
def approve_audit_execution(
    execution_id: UUID,
    request: AuditExecutionApprove,
    db: Session = Depends(get_db)
):
    """Approve audit execution"""
    execution = db.query(AuditExecution).filter(
        AuditExecution.execution_id == execution_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Audit execution not found")
    
    execution.approved_by = request.approved_by
    execution.approved_at = datetime.utcnow()
    execution.execution_status = 'completed'
    
    db.commit()
    db.refresh(execution)
    return execution


@router.delete("/audit-executions/{execution_id}", status_code=204)
def delete_audit_execution(execution_id: UUID, db: Session = Depends(get_db)):
    """Delete audit execution"""
    execution = db.query(AuditExecution).filter(
        AuditExecution.execution_id == execution_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Audit execution not found")
    
    db.delete(execution)
    db.commit()
    return None


# =====================================================
# Audit Finding Endpoints
# =====================================================

@router.post("/audit-findings", response_model=AuditFindingResponse, status_code=201)
def create_audit_finding(
    finding: AuditFindingCreate,
    db: Session = Depends(get_db)
):
    """Create a new audit finding"""
    db_finding = AuditFinding(**finding.model_dump())
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@router.get("/audit-findings", response_model=List[AuditFindingResponse])
def list_audit_findings(
    execution_id: Optional[UUID] = None,
    finding_type: Optional[str] = None,
    severity_level: Optional[str] = None,
    risk_level: Optional[str] = None,
    finding_status: Optional[str] = None,
    responsible_person: Optional[UUID] = None,
    is_repeat_finding: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List audit findings with filters"""
    query = db.query(AuditFinding)
    
    if execution_id:
        query = query.filter(AuditFinding.execution_id == execution_id)
    if finding_type:
        query = query.filter(AuditFinding.finding_type == finding_type)
    if severity_level:
        query = query.filter(AuditFinding.severity_level == severity_level)
    if risk_level:
        query = query.filter(AuditFinding.risk_level == risk_level)
    if finding_status:
        query = query.filter(AuditFinding.finding_status == finding_status)
    if responsible_person:
        query = query.filter(AuditFinding.responsible_person == responsible_person)
    if is_repeat_finding is not None:
        query = query.filter(AuditFinding.is_repeat_finding == is_repeat_finding)
    
    query = query.order_by(AuditFinding.severity_level, AuditFinding.target_completion_date)
    return query.offset(skip).limit(limit).all()


@router.get("/audit-findings/{finding_id}", response_model=AuditFindingResponse)
def get_audit_finding(finding_id: UUID, db: Session = Depends(get_db)):
    """Get audit finding by ID"""
    finding = db.query(AuditFinding).filter(
        AuditFinding.finding_id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")
    return finding


@router.put("/audit-findings/{finding_id}", response_model=AuditFindingResponse)
def update_audit_finding(
    finding_id: UUID,
    finding: AuditFindingUpdate,
    db: Session = Depends(get_db)
):
    """Update audit finding"""
    db_finding = db.query(AuditFinding).filter(
        AuditFinding.finding_id == finding_id
    ).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")
    
    update_data = finding.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_finding, field, value)
    
    db.commit()
    db.refresh(db_finding)
    return db_finding


@router.post("/audit-findings/{finding_id}/verify", response_model=AuditFindingResponse)
def verify_audit_finding(
    finding_id: UUID,
    request: AuditFindingVerify,
    db: Session = Depends(get_db)
):
    """Verify resolution of audit finding"""
    finding = db.query(AuditFinding).filter(
        AuditFinding.finding_id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")
    
    finding.finding_status = 'verified'
    finding.verified_by = request.verified_by
    finding.verified_at = datetime.utcnow()
    finding.verification_notes = request.verification_notes
    
    db.commit()
    db.refresh(finding)
    return finding


@router.delete("/audit-findings/{finding_id}", status_code=204)
def delete_audit_finding(finding_id: UUID, db: Session = Depends(get_db)):
    """Delete audit finding"""
    finding = db.query(AuditFinding).filter(
        AuditFinding.finding_id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")
    
    db.delete(finding)
    db.commit()
    return None


# =====================================================
# Regulatory Report Endpoints
# =====================================================

@router.post("/regulatory-reports", response_model=RegulatoryReportResponse, status_code=201)
def create_regulatory_report(
    report: RegulatoryReportCreate,
    db: Session = Depends(get_db)
):
    """Create a new regulatory report"""
    db_report = RegulatoryReport(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/regulatory-reports", response_model=List[RegulatoryReportResponse])
def list_regulatory_reports(
    report_type: Optional[str] = None,
    regulatory_body: Optional[str] = None,
    report_status: Optional[str] = None,
    is_overdue: Optional[bool] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List regulatory reports with filters"""
    query = db.query(RegulatoryReport)
    
    if report_type:
        query = query.filter(RegulatoryReport.report_type == report_type)
    if regulatory_body:
        query = query.filter(RegulatoryReport.regulatory_body == regulatory_body)
    if report_status:
        query = query.filter(RegulatoryReport.report_status == report_status)
    if is_overdue is not None:
        query = query.filter(RegulatoryReport.is_overdue == is_overdue)
    if date_from:
        query = query.filter(RegulatoryReport.due_date >= date_from)
    if date_to:
        query = query.filter(RegulatoryReport.due_date <= date_to)
    
    query = query.order_by(RegulatoryReport.due_date)
    return query.offset(skip).limit(limit).all()


@router.get("/regulatory-reports/{report_id}", response_model=RegulatoryReportResponse)
def get_regulatory_report(report_id: UUID, db: Session = Depends(get_db)):
    """Get regulatory report by ID"""
    report = db.query(RegulatoryReport).filter(
        RegulatoryReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Regulatory report not found")
    return report


@router.put("/regulatory-reports/{report_id}", response_model=RegulatoryReportResponse)
def update_regulatory_report(
    report_id: UUID,
    report: RegulatoryReportUpdate,
    db: Session = Depends(get_db)
):
    """Update regulatory report"""
    db_report = db.query(RegulatoryReport).filter(
        RegulatoryReport.report_id == report_id
    ).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Regulatory report not found")
    
    update_data = report.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


@router.post("/regulatory-reports/{report_id}/approve", response_model=RegulatoryReportResponse)
def approve_regulatory_report(
    report_id: UUID,
    request: RegulatoryReportApprove,
    db: Session = Depends(get_db)
):
    """Approve regulatory report"""
    report = db.query(RegulatoryReport).filter(
        RegulatoryReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Regulatory report not found")
    
    report.approved_by = request.approved_by
    report.approved_at = datetime.utcnow()
    report.report_status = 'approved'
    
    db.commit()
    db.refresh(report)
    return report


@router.post("/regulatory-reports/{report_id}/submit", response_model=RegulatoryReportResponse)
def submit_regulatory_report(
    report_id: UUID,
    request: RegulatoryReportSubmit,
    db: Session = Depends(get_db)
):
    """Submit regulatory report"""
    report = db.query(RegulatoryReport).filter(
        RegulatoryReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Regulatory report not found")
    
    if report.report_status != 'approved':
        raise HTTPException(status_code=400, detail="Report must be approved before submission")
    
    report.submitted_by = request.submitted_by
    report.submission_date = request.submission_date
    report.submission_reference = request.submission_reference
    report.report_status = 'submitted'
    
    db.commit()
    db.refresh(report)
    return report


@router.delete("/regulatory-reports/{report_id}", status_code=204)
def delete_regulatory_report(report_id: UUID, db: Session = Depends(get_db)):
    """Delete regulatory report"""
    report = db.query(RegulatoryReport).filter(
        RegulatoryReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Regulatory report not found")
    
    db.delete(report)
    db.commit()
    return None


# =====================================================
# Statistics Endpoints
# =====================================================

@router.get("/statistics/audit-trails", response_model=AuditTrailStatistics)
def get_audit_trail_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get audit trail statistics"""
    query = db.query(AuditTrail)
    
    if date_from:
        query = query.filter(AuditTrail.event_timestamp >= date_from)
    if date_to:
        query = query.filter(AuditTrail.event_timestamp <= date_to)
    
    audits = query.all()
    
    events_by_category = {}
    events_by_status = {}
    unique_users = set()
    
    for audit in audits:
        events_by_category[audit.event_category] = events_by_category.get(audit.event_category, 0) + 1
        events_by_status[audit.action_status] = events_by_status.get(audit.action_status, 0) + 1
        unique_users.add(audit.user_id)
    
    return AuditTrailStatistics(
        total_events=len(audits),
        events_by_category=events_by_category,
        events_by_status=events_by_status,
        security_events=sum(1 for a in audits if a.security_flag),
        compliance_events=sum(1 for a in audits if a.compliance_flag),
        fraud_events=sum(1 for a in audits if a.fraud_flag),
        unique_users=len(unique_users)
    )


@router.get("/statistics/compliance", response_model=ComplianceStatistics)
def get_compliance_statistics(db: Session = Depends(get_db)):
    """Get compliance statistics"""
    rules = db.query(ComplianceRule).all()
    violations = db.query(ComplianceViolation).all()
    
    violations_by_severity = {}
    for v in violations:
        violations_by_severity[v.severity_level] = violations_by_severity.get(v.severity_level, 0) + 1
    
    return ComplianceStatistics(
        total_rules=len(rules),
        active_rules=sum(1 for r in rules if r.is_active),
        total_violations=len(violations),
        open_violations=sum(1 for v in violations if v.violation_status == 'open'),
        violations_by_severity=violations_by_severity,
        total_financial_impact=sum(v.financial_impact or 0 for v in violations)
    )


@router.get("/statistics/audit-executions", response_model=AuditExecutionStatistics)
def get_audit_execution_statistics(db: Session = Depends(get_db)):
    """Get audit execution statistics"""
    executions = db.query(AuditExecution).all()
    findings = db.query(AuditFinding).all()
    
    executions_by_status = {}
    executions_by_type = {}
    findings_by_severity = {}
    
    for e in executions:
        executions_by_status[e.execution_status] = executions_by_status.get(e.execution_status, 0) + 1
        executions_by_type[e.audit_type] = executions_by_type.get(e.audit_type, 0) + 1
    
    for f in findings:
        findings_by_severity[f.severity_level] = findings_by_severity.get(f.severity_level, 0) + 1
    
    avg_completion = sum(e.completion_percentage for e in executions) / len(executions) if executions else 0
    
    return AuditExecutionStatistics(
        total_executions=len(executions),
        executions_by_status=executions_by_status,
        executions_by_type=executions_by_type,
        total_findings=len(findings),
        findings_by_severity=findings_by_severity,
        average_completion_percentage=avg_completion
    )


@router.get("/statistics/regulatory-reports", response_model=RegulatoryReportStatistics)
def get_regulatory_report_statistics(db: Session = Depends(get_db)):
    """Get regulatory report statistics"""
    reports = db.query(RegulatoryReport).all()
    
    reports_by_status = {}
    reports_by_body = {}
    
    for r in reports:
        reports_by_status[r.report_status] = reports_by_status.get(r.report_status, 0) + 1
        reports_by_body[r.regulatory_body] = reports_by_body.get(r.regulatory_body, 0) + 1
    
    return RegulatoryReportStatistics(
        total_reports=len(reports),
        reports_by_status=reports_by_status,
        overdue_reports=sum(1 for r in reports if r.is_overdue),
        pending_submissions=sum(1 for r in reports if r.report_status in ['draft', 'approved']),
        reports_by_regulatory_body=reports_by_body
    )


# =====================================================
# Compliance Certification Endpoints
# =====================================================

@router.post("/compliance-certifications", response_model=ComplianceCertificationResponse, status_code=201)
def create_compliance_certification(
    certification: ComplianceCertificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new compliance certification"""
    # Check for duplicate certification number
    existing = db.query(ComplianceCertification).filter(
        ComplianceCertification.certification_number == certification.certification_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Certification number already exists")
    
    db_certification = ComplianceCertification(**certification.model_dump())
    db.add(db_certification)
    db.commit()
    db.refresh(db_certification)
    return db_certification


@router.get("/compliance-certifications", response_model=List[ComplianceCertificationResponse])
def list_compliance_certifications(
    certification_type: Optional[str] = None,
    certification_status: Optional[str] = None,
    issuing_body: Optional[str] = None,
    is_expired: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List compliance certifications with filters"""
    query = db.query(ComplianceCertification)
    
    if certification_type:
        query = query.filter(ComplianceCertification.certification_type == certification_type)
    if certification_status:
        query = query.filter(ComplianceCertification.certification_status == certification_status)
    if issuing_body:
        query = query.filter(ComplianceCertification.issuing_body == issuing_body)
    if is_expired is not None:
        query = query.filter(ComplianceCertification.is_expired == is_expired)
    
    query = query.order_by(ComplianceCertification.expiry_date)
    return query.offset(skip).limit(limit).all()


@router.get("/compliance-certifications/{certification_id}", response_model=ComplianceCertificationResponse)
def get_compliance_certification(certification_id: UUID, db: Session = Depends(get_db)):
    """Get compliance certification by ID"""
    certification = db.query(ComplianceCertification).filter(
        ComplianceCertification.certification_id == certification_id
    ).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Compliance certification not found")
    return certification


@router.put("/compliance-certifications/{certification_id}", response_model=ComplianceCertificationResponse)
def update_compliance_certification(
    certification_id: UUID,
    certification: ComplianceCertificationUpdate,
    db: Session = Depends(get_db)
):
    """Update compliance certification"""
    db_certification = db.query(ComplianceCertification).filter(
        ComplianceCertification.certification_id == certification_id
    ).first()
    if not db_certification:
        raise HTTPException(status_code=404, detail="Compliance certification not found")
    
    update_data = certification.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_certification, field, value)
    
    db.commit()
    db.refresh(db_certification)
    return db_certification


@router.delete("/compliance-certifications/{certification_id}", status_code=204)
def delete_compliance_certification(certification_id: UUID, db: Session = Depends(get_db)):
    """Delete compliance certification"""
    certification = db.query(ComplianceCertification).filter(
        ComplianceCertification.certification_id == certification_id
    ).first()
    if not certification:
        raise HTTPException(status_code=404, detail="Compliance certification not found")
    
    db.delete(certification)
    db.commit()
    return None


# =====================================================
# Policy Acknowledgement Endpoints
# =====================================================

@router.post("/policy-acknowledgements", response_model=PolicyAcknowledgementResponse, status_code=201)
def create_policy_acknowledgement(
    acknowledgement: PolicyAcknowledgementCreate,
    db: Session = Depends(get_db)
):
    """Create a new policy acknowledgement"""
    db_acknowledgement = PolicyAcknowledgement(**acknowledgement.model_dump())
    db.add(db_acknowledgement)
    db.commit()
    db.refresh(db_acknowledgement)
    return db_acknowledgement


@router.get("/policy-acknowledgements", response_model=List[PolicyAcknowledgementResponse])
def list_policy_acknowledgements(
    policy_type: Optional[str] = None,
    acknowledgement_status: Optional[str] = None,
    user_id: Optional[UUID] = None,
    is_mandatory: Optional[bool] = None,
    acknowledged: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List policy acknowledgements with filters"""
    query = db.query(PolicyAcknowledgement)
    
    if policy_type:
        query = query.filter(PolicyAcknowledgement.policy_type == policy_type)
    if acknowledgement_status:
        query = query.filter(PolicyAcknowledgement.acknowledgement_status == acknowledgement_status)
    if user_id:
        query = query.filter(PolicyAcknowledgement.user_id == user_id)
    if is_mandatory is not None:
        query = query.filter(PolicyAcknowledgement.is_mandatory == is_mandatory)
    if acknowledged is not None:
        if acknowledged:
            query = query.filter(PolicyAcknowledgement.acknowledged_at.isnot(None))
        else:
            query = query.filter(PolicyAcknowledgement.acknowledged_at.is_(None))
    
    query = query.order_by(desc(PolicyAcknowledgement.policy_effective_date))
    return query.offset(skip).limit(limit).all()


@router.get("/policy-acknowledgements/{acknowledgement_id}", response_model=PolicyAcknowledgementResponse)
def get_policy_acknowledgement(acknowledgement_id: UUID, db: Session = Depends(get_db)):
    """Get policy acknowledgement by ID"""
    acknowledgement = db.query(PolicyAcknowledgement).filter(
        PolicyAcknowledgement.acknowledgement_id == acknowledgement_id
    ).first()
    if not acknowledgement:
        raise HTTPException(status_code=404, detail="Policy acknowledgement not found")
    return acknowledgement


@router.put("/policy-acknowledgements/{acknowledgement_id}", response_model=PolicyAcknowledgementResponse)
def update_policy_acknowledgement(
    acknowledgement_id: UUID,
    acknowledgement: PolicyAcknowledgementUpdate,
    db: Session = Depends(get_db)
):
    """Update policy acknowledgement (typically for acknowledgement action)"""
    db_acknowledgement = db.query(PolicyAcknowledgement).filter(
        PolicyAcknowledgement.acknowledgement_id == acknowledgement_id
    ).first()
    if not db_acknowledgement:
        raise HTTPException(status_code=404, detail="Policy acknowledgement not found")
    
    update_data = acknowledgement.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_acknowledgement, field, value)
    
    # If being acknowledged, set timestamp
    if update_data.get('acknowledged_at') and not db_acknowledgement.acknowledged_at:
        db_acknowledgement.acknowledged_at = datetime.utcnow()
        db_acknowledgement.acknowledgement_status = 'acknowledged'
    
    db.commit()
    db.refresh(db_acknowledgement)
    return db_acknowledgement


# =====================================================
# Data Retention Log Endpoints
# =====================================================

@router.post("/data-retention-logs", response_model=DataRetentionLogResponse, status_code=201)
def create_data_retention_log(
    log: DataRetentionLogCreate,
    db: Session = Depends(get_db)
):
    """Create a new data retention log"""
    db_log = DataRetentionLog(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/data-retention-logs", response_model=List[DataRetentionLogResponse])
def list_data_retention_logs(
    data_category: Optional[str] = None,
    retention_action: Optional[str] = None,
    retention_status: Optional[str] = None,
    policy_code: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List data retention logs with filters"""
    query = db.query(DataRetentionLog)
    
    if data_category:
        query = query.filter(DataRetentionLog.data_category == data_category)
    if retention_action:
        query = query.filter(DataRetentionLog.retention_action == retention_action)
    if retention_status:
        query = query.filter(DataRetentionLog.retention_status == retention_status)
    if policy_code:
        query = query.filter(DataRetentionLog.policy_code == policy_code)
    if date_from:
        query = query.filter(DataRetentionLog.scheduled_date >= date_from)
    if date_to:
        query = query.filter(DataRetentionLog.scheduled_date <= date_to)
    
    query = query.order_by(desc(DataRetentionLog.scheduled_date))
    return query.offset(skip).limit(limit).all()


@router.get("/data-retention-logs/{log_id}", response_model=DataRetentionLogResponse)
def get_data_retention_log(log_id: UUID, db: Session = Depends(get_db)):
    """Get data retention log by ID"""
    log = db.query(DataRetentionLog).filter(
        DataRetentionLog.log_id == log_id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Data retention log not found")
    return log


@router.put("/data-retention-logs/{log_id}", response_model=DataRetentionLogResponse)
def update_data_retention_log(
    log_id: UUID,
    log: DataRetentionLogUpdate,
    db: Session = Depends(get_db)
):
    """Update data retention log"""
    db_log = db.query(DataRetentionLog).filter(
        DataRetentionLog.log_id == log_id
    ).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Data retention log not found")
    
    if db_log.retention_status == 'completed':
        raise HTTPException(status_code=400, detail="Cannot update completed retention log")
    
    update_data = log.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)
    
    db.commit()
    db.refresh(db_log)
    return db_log


@router.post("/data-retention-logs/{log_id}/approve", response_model=DataRetentionLogResponse)
def approve_data_retention_log(
    log_id: UUID,
    request: DataRetentionLogApprove,
    db: Session = Depends(get_db)
):
    """Approve data retention log"""
    log = db.query(DataRetentionLog).filter(
        DataRetentionLog.log_id == log_id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Data retention log not found")
    
    if log.retention_status != 'pending':
        raise HTTPException(status_code=400, detail="Can only approve pending logs")
    
    log.approved_by = request.approved_by
    log.approved_at = datetime.utcnow()
    log.retention_status = 'approved'
    
    db.commit()
    db.refresh(log)
    return log


@router.post("/data-retention-logs/{log_id}/execute", response_model=DataRetentionLogResponse)
def execute_data_retention_log(
    log_id: UUID,
    db: Session = Depends(get_db)
):
    """Execute data retention action"""
    log = db.query(DataRetentionLog).filter(
        DataRetentionLog.log_id == log_id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Data retention log not found")
    
    if log.retention_status != 'approved':
        raise HTTPException(status_code=400, detail="Can only execute approved logs")
    
    log.execution_date = datetime.utcnow()
    log.retention_status = 'completed'
    
    # Here you would typically trigger the actual data retention/deletion process
    # This is a placeholder for the actual execution logic
    
    db.commit()
    db.refresh(log)
    return log
