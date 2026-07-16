"""
Locker Compliance API Router
Handles RBI guidelines compliance, audits, and inspections
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.auth.dependencies import get_current_user
from .compliance_service import (
    LockerComplianceService,
    ComplianceType,
    ComplianceStatus,
    AuditType,
    AuditStatus,
    InspectionType,
    FindingsSeverity
)


router = APIRouter(prefix="/api/locker/compliance", tags=["Locker Compliance"])


# ==================== REQUEST MODELS ====================

class ComplianceCheckRequest(BaseModel):
    """Request model for compliance check"""
    branch_id: str
    compliance_areas: Optional[List[ComplianceType]] = None


class ComplianceIssueRequest(BaseModel):
    """Request model for recording compliance issue"""
    compliance_type: ComplianceType
    branch_id: str
    severity: FindingsSeverity
    description: str
    remediation_plan: Optional[str] = None
    target_resolution_date: Optional[datetime] = None


class ComplianceStatusUpdateRequest(BaseModel):
    """Request model for updating compliance status"""
    status: str
    remediation_details: Optional[str] = None


class AuditScheduleRequest(BaseModel):
    """Request model for scheduling audit"""
    audit_type: AuditType
    branch_id: str
    scheduled_date: datetime
    auditor_name: str
    audit_scope: str
    checklist_items: Optional[List[dict]] = []


class AuditExecutionRequest(BaseModel):
    """Request model for audit execution"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    checklist_results: Optional[List[dict]] = []
    findings: Optional[List[dict]] = []
    observations: Optional[str] = None
    recommendations: Optional[str] = None


class AuditReportRequest(BaseModel):
    """Request model for audit report generation"""
    executive_summary: str
    detailed_findings: str
    risk_rating: str
    compliance_score: float
    recommendations: str
    action_items: List[dict]


class InspectionRequest(BaseModel):
    """Request model for conducting inspection"""
    inspection_type: InspectionType
    branch_id: str
    inspection_date: Optional[datetime] = None
    inspector_name: str
    items_checked: Optional[List[dict]] = []
    findings: Optional[List[dict]] = []
    discrepancies_found: Optional[List[dict]] = []
    recommendations: Optional[str] = None


class VerificationPeriodRequest(BaseModel):
    """Request model for verification period"""
    branch_id: str
    start_date: datetime
    end_date: datetime


class PhysicalVerificationRequest(BaseModel):
    """Request model for physical verification"""
    branch_id: str
    locker_ids: List[str]


# ==================== COMPLIANCE ENDPOINTS ====================

@router.post("/check-compliance")
async def check_rbi_compliance(
    request: ComplianceCheckRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check RBI compliance across various areas
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.check_rbi_compliance(
        branch_id=request.branch_id,
        compliance_areas=request.compliance_areas
    )
    
    return result


@router.post("/issues")
async def record_compliance_issue(
    request: ComplianceIssueRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Record a compliance issue
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.record_compliance_issue(
        issue_data=request.dict()
    )
    
    return result


@router.put("/issues/{issue_id}/status")
async def update_compliance_status(
    issue_id: str,
    request: ComplianceStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update compliance issue status
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.update_compliance_status(
        issue_id=issue_id,
        status=request.status,
        remediation_details=request.remediation_details
    )
    
    return result


@router.get("/issues")
async def get_compliance_issues(
    branch_id: Optional[str] = Query(None),
    compliance_type: Optional[ComplianceType] = Query(None),
    severity: Optional[FindingsSeverity] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of compliance issues with filters
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    issues = await service.get_compliance_issues(
        branch_id=branch_id,
        compliance_type=compliance_type,
        severity=severity,
        status=status
    )
    
    return {"issues": issues}


# ==================== AUDIT ENDPOINTS ====================

@router.post("/audits/schedule")
async def schedule_audit(
    request: AuditScheduleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Schedule an audit
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.schedule_audit(
        audit_data=request.dict()
    )
    
    return result


@router.post("/audits/{audit_id}/execute")
async def execute_audit(
    audit_id: str,
    request: AuditExecutionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute an audit
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.execute_audit(
        audit_id=audit_id,
        execution_data=request.dict()
    )
    
    return result


@router.post("/audits/{audit_id}/report")
async def generate_audit_report(
    audit_id: str,
    request: AuditReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate audit report
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.generate_audit_report(
        audit_id=audit_id,
        report_data=request.dict()
    )
    
    return result


@router.get("/audits")
async def get_audits(
    branch_id: Optional[str] = Query(None),
    audit_type: Optional[AuditType] = Query(None),
    status: Optional[AuditStatus] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of audits with filters
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    audits = await service.get_audits(
        branch_id=branch_id,
        audit_type=audit_type,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    
    return {"audits": audits}


@router.get("/audits/{audit_id}")
async def get_audit_details(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed audit information
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    audit = await service.get_audit_details(audit_id=audit_id)
    
    return audit


# ==================== INSPECTION ENDPOINTS ====================

@router.post("/inspections")
async def conduct_inspection(
    request: InspectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Conduct an inspection
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.conduct_inspection(
        inspection_data=request.dict()
    )
    
    return result


@router.post("/inspections/verify-access-logs")
async def verify_access_logs(
    request: VerificationPeriodRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Verify locker access logs
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.verify_access_logs(
        branch_id=request.branch_id,
        verification_period={
            "start": request.start_date,
            "end": request.end_date
        }
    )
    
    return result


@router.post("/inspections/verify-rent-collection")
async def verify_rent_collection(
    request: VerificationPeriodRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Verify rent collection
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.verify_rent_collection(
        branch_id=request.branch_id,
        verification_period={
            "start": request.start_date,
            "end": request.end_date
        }
    )
    
    return result


@router.post("/inspections/physical-verification")
async def physical_verification(
    request: PhysicalVerificationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Conduct physical verification of lockers
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    result = await service.physical_verification_of_lockers(
        branch_id=request.branch_id,
        locker_ids=request.locker_ids
    )
    
    return result


@router.get("/inspections")
async def get_inspections(
    branch_id: Optional[str] = Query(None),
    inspection_type: Optional[InspectionType] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of inspections with filters
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    inspections = await service.get_inspections(
        branch_id=branch_id,
        inspection_type=inspection_type,
        from_date=from_date,
        to_date=to_date
    )
    
    return {"inspections": inspections}


@router.get("/inspections/{inspection_id}")
async def get_inspection_details(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed inspection information
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    inspection = await service.get_inspection_details(inspection_id=inspection_id)
    
    return inspection


# ==================== DASHBOARD & STATISTICS ====================

@router.get("/dashboard")
async def get_compliance_dashboard(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get compliance dashboard with key metrics
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    dashboard = await service.get_compliance_dashboard(branch_id=branch_id)
    
    return dashboard


@router.get("/statistics")
async def get_statistics(
    branch_id: Optional[str] = Query(None),
    period: Optional[str] = Query("month"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get compliance statistics
    """
    service = LockerComplianceService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    stats = await service.get_statistics(
        branch_id=branch_id,
        period=period
    )
    
    return stats
