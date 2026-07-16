"""
API Router for Locker Safety & Security
Provides RESTful endpoints for physical security, insurance, and incident management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from .safety_security_service import (
    LockerSafetySecurityService,
    VaultAccessType,
    SecurityEventType,
    SecurityEventSeverity,
    InsuranceType,
    InsuranceStatus,
    IncidentType,
    IncidentSeverity,
    IncidentStatus,
    CompensationStatus
)

router = APIRouter(prefix="/safety-security", tags=["Safety & Security"])


# ==================== REQUEST MODELS ====================

class OpenVaultRequest(BaseModel):
    branch_id: str
    access_type: VaultAccessType
    official_1_id: str
    official_2_id: str
    purpose: str
    time_lock_override: bool = False
    override_reason: Optional[str] = None


class CloseVaultRequest(BaseModel):
    access_record_id: str
    official_1_id: str
    official_2_id: str
    notes: Optional[str] = None


class CCTVStatusRequest(BaseModel):
    branch_id: str
    camera_id: str
    status: str
    recording_status: bool
    last_check: datetime


class AlarmTriggerRequest(BaseModel):
    branch_id: str
    alarm_type: str
    triggered_by: str
    location: str
    reason: str



class InsurancePolicyRequest(BaseModel):
    policy_type: InsuranceType
    locker_id: Optional[str] = None
    customer_id: Optional[str] = None
    insurer_name: str
    coverage_amount: float
    premium_amount: float
    start_date: datetime
    end_date: datetime
    terms_conditions: Optional[str] = None


class RenewPolicyRequest(BaseModel):
    policy_id: str
    new_end_date: datetime
    premium_amount: float


class InsuranceClaimRequest(BaseModel):
    policy_id: str
    incident_id: str
    claim_amount: float
    claim_description: str
    supporting_documents: List[str] = []


class ReportIncidentRequest(BaseModel):
    incident_type: IncidentType
    severity: IncidentSeverity
    branch_id: str
    affected_lockers: List[str] = []
    incident_date: datetime
    description: str


class InvestigateIncidentRequest(BaseModel):
    findings: str
    evidence_collected: List[str] = []
    root_cause: Optional[str] = None
    recommendations: Optional[str] = None


class NotifyAuthoritiesRequest(BaseModel):
    authority_type: str  # "rbi" or "police"
    reference_number: Optional[str] = None
    contact_person: Optional[str] = None
    acknowledgment_received: bool = False


class CompensationRequest(BaseModel):
    customer_id: str
    locker_id: str
    compensation_amount: float
    compensation_type: str
    approved_by: str
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None


# ==================== VAULT OPERATIONS ENDPOINTS ====================

@router.post("/vault/open")
async def open_vault(
    request: OpenVaultRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Open vault with dual custody"""
    try:
        result = await service.open_vault(
            branch_id=request.branch_id,
            access_type=request.access_type,
            official_1_id=request.official_1_id,
            official_2_id=request.official_2_id,
            purpose=request.purpose,
            time_lock_override=request.time_lock_override,
            override_reason=request.override_reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vault/close")
async def close_vault(
    request: CloseVaultRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Close vault with dual custody"""
    try:
        result = await service.close_vault(
            access_record_id=request.access_record_id,
            official_1_id=request.official_1_id,
            official_2_id=request.official_2_id,
            notes=request.notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vault/access-log")
async def get_vault_access_log(
    branch_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: LockerSafetySecurityService = Depends()
):
    """Get vault access history"""
    result = await service.get_vault_access_log(branch_id, start_date, end_date)
    return result


# ==================== SECURITY MONITORING ENDPOINTS ====================

@router.post("/cctv/status")
async def record_cctv_status(
    request: CCTVStatusRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Record CCTV camera status"""
    result = await service.record_cctv_status(
        branch_id=request.branch_id,
        camera_id=request.camera_id,
        status=request.status,
        recording_status=request.recording_status,
        last_check=request.last_check
    )
    return result


@router.post("/alarm/trigger")
async def trigger_alarm(
    request: AlarmTriggerRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Record alarm trigger event"""
    result = await service.trigger_alarm(
        branch_id=request.branch_id,
        alarm_type=request.alarm_type,
        triggered_by=request.triggered_by,
        location=request.location,
        reason=request.reason
    )
    return result


@router.get("/security-events")
async def get_security_events(
    branch_id: Optional[str] = None,
    severity: Optional[SecurityEventSeverity] = None,
    limit: int = 50,
    service: LockerSafetySecurityService = Depends()
):
    """Get security events with filters"""
    result = await service.get_security_events(branch_id, severity, limit)
    return result


@router.get("/dashboard")
async def get_security_dashboard(
    branch_id: Optional[str] = None,
    service: LockerSafetySecurityService = Depends()
):
    """Get real-time security dashboard"""
    result = await service.get_security_dashboard(branch_id)
    return result


# ==================== INSURANCE ENDPOINTS ====================

@router.post("/insurance/policy")
async def create_insurance_policy(
    request: InsurancePolicyRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Create new insurance policy"""
    policy_data = request.dict()
    result = await service.create_insurance_policy(policy_data)
    return result


@router.post("/insurance/renew")
async def renew_insurance_policy(
    request: RenewPolicyRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Renew existing insurance policy"""
    result = await service.renew_insurance_policy(
        policy_id=request.policy_id,
        new_end_date=request.new_end_date,
        premium_amount=request.premium_amount
    )
    return result


@router.post("/insurance/claim")
async def file_insurance_claim(
    request: InsuranceClaimRequest,
    service: LockerSafetySecurityService = Depends()
):
    """File insurance claim"""
    claim_data = request.dict()
    result = await service.file_insurance_claim(claim_data)
    return result


@router.get("/insurance/policies")
async def get_insurance_policies(
    customer_id: Optional[str] = None,
    status: Optional[InsuranceStatus] = None,
    service: LockerSafetySecurityService = Depends()
):
    """Get insurance policies with filters"""
    result = await service.get_insurance_policies(customer_id, status)
    return result


# ==================== INCIDENT MANAGEMENT ENDPOINTS ====================

@router.post("/incident/report")
async def report_incident(
    request: ReportIncidentRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Report security incident"""
    incident_data = request.dict()
    result = await service.report_incident(incident_data)
    return result


@router.post("/incident/{incident_id}/investigate")
async def investigate_incident(
    incident_id: str,
    request: InvestigateIncidentRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Update incident with investigation findings"""
    investigation_data = request.dict()
    result = await service.investigate_incident(incident_id, investigation_data)
    return result


@router.post("/incident/{incident_id}/notify-authorities")
async def notify_authorities(
    incident_id: str,
    request: NotifyAuthoritiesRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Notify RBI/Police about incident"""
    notification_data = request.dict()
    result = await service.notify_authorities(
        incident_id, request.authority_type, notification_data
    )
    return result


@router.post("/incident/{incident_id}/compensation")
async def process_compensation(
    incident_id: str,
    request: CompensationRequest,
    service: LockerSafetySecurityService = Depends()
):
    """Process customer compensation"""
    compensation_data = request.dict()
    result = await service.process_compensation(incident_id, compensation_data)
    return result


@router.get("/incident/list")
async def get_incidents(
    branch_id: Optional[str] = None,
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    service: LockerSafetySecurityService = Depends()
):
    """Get incidents with filters"""
    result = await service.get_incidents(branch_id, status, severity)
    return result


@router.get("/incident/{incident_id}")
async def get_incident_details(
    incident_id: str,
    service: LockerSafetySecurityService = Depends()
):
    """Get incident details by ID"""
    # Implementation would fetch from database
    return {"incident_id": incident_id, "details": {}}


# ==================== STATISTICS ENDPOINT ====================

@router.get("/statistics")
async def get_statistics(
    service: LockerSafetySecurityService = Depends()
):
    """Get safety & security statistics"""
    result = await service.get_statistics()
    return result
