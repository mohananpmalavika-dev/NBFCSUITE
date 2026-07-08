"""
Grievance & Complaint Management - API Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from .complaint_service import ComplaintService
from .escalation_service import EscalationService
from .ombudsman_service import OmbudsmanService
from .schemas import (
    # Complaint schemas
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintAssign,
    ComplaintAcknowledge,
    ComplaintResolve,
    ComplaintClose,
    ComplaintReopen,
    ComplaintResponse,
    ComplaintFilter,
    ComplaintStatistics,
    # Channel schemas
    ComplaintChannelCreate,
    ComplaintChannelResponse,
    # Escalation schemas
    ComplaintEscalationCreate,
    ComplaintEscalationAcknowledge,
    ComplaintEscalationResolve,
    ComplaintEscalationResponse,
    # Ombudsman schemas
    OmbudsmanCaseCreate,
    OmbudsmanCaseUpdate,
    OmbudsmanCaseSubmit,
    OmbudsmanCaseHearing,
    OmbudsmanCaseAward,
    OmbudsmanCaseResponse,
)
from .models import EscalationLevel, OmbudsmanStatus

router = APIRouter()


# ============================================================================
# COMPLAINT ENDPOINTS
# ============================================================================

@router.post("/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db)
):
    """Register a new complaint"""
    service = ComplaintService(db)
    return service.create_complaint(complaint)


@router.get("/complaints", response_model=dict)
def list_complaints(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    channel: Optional[str] = None,
    assigned_to: Optional[int] = None,
    customer_id: Optional[int] = None,
    sla_breach: Optional[bool] = None,
    search_text: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all complaints with filters"""
    service = ComplaintService(db)
    
    filters = ComplaintFilter(
        status=status,
        priority=priority,
        category=category,
        channel=channel,
        assigned_to=assigned_to,
        customer_id=customer_id,
        sla_breach=sla_breach,
        search_text=search_text,
        skip=skip,
        limit=limit,
    )
    
    complaints, total = service.list_complaints(filters)
    
    return {
        "complaints": complaints,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Get complaint by ID"""
    service = ComplaintService(db)
    complaint = service.get_complaint(complaint_id)
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    return complaint


@router.get("/complaints/number/{complaint_number}", response_model=ComplaintResponse)
def get_complaint_by_number(
    complaint_number: str,
    db: Session = Depends(get_db)
):
    """Get complaint by complaint number"""
    service = ComplaintService(db)
    complaint = service.get_complaint_by_number(complaint_number)
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    return complaint


@router.put("/complaints/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(
    complaint_id: int,
    complaint_update: ComplaintUpdate,
    db: Session = Depends(get_db)
):
    """Update complaint details"""
    service = ComplaintService(db)
    return service.update_complaint(complaint_id, complaint_update)


@router.post("/complaints/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_complaint(
    complaint_id: int,
    assignment: ComplaintAssign,
    db: Session = Depends(get_db)
):
    """Assign complaint to user/department"""
    service = ComplaintService(db)
    return service.assign_complaint(complaint_id, assignment)


@router.post("/complaints/{complaint_id}/acknowledge", response_model=ComplaintResponse)
def acknowledge_complaint(
    complaint_id: int,
    acknowledgement: ComplaintAcknowledge,
    db: Session = Depends(get_db)
):
    """Acknowledge receipt of complaint"""
    service = ComplaintService(db)
    return service.acknowledge_complaint(complaint_id, acknowledgement)


@router.post("/complaints/{complaint_id}/resolve", response_model=ComplaintResponse)
def resolve_complaint(
    complaint_id: int,
    resolution: ComplaintResolve,
    db: Session = Depends(get_db)
):
    """Resolve a complaint"""
    service = ComplaintService(db)
    return service.resolve_complaint(complaint_id, resolution)


@router.post("/complaints/{complaint_id}/close", response_model=ComplaintResponse)
def close_complaint(
    complaint_id: int,
    closure: ComplaintClose,
    db: Session = Depends(get_db)
):
    """Close a resolved complaint"""
    service = ComplaintService(db)
    return service.close_complaint(complaint_id, closure)


@router.post("/complaints/{complaint_id}/reopen", response_model=ComplaintResponse)
def reopen_complaint(
    complaint_id: int,
    reopen_data: ComplaintReopen,
    db: Session = Depends(get_db)
):
    """Reopen a closed complaint"""
    service = ComplaintService(db)
    return service.reopen_complaint(complaint_id, reopen_data)


@router.delete("/complaints/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Delete a complaint"""
    service = ComplaintService(db)
    service.delete_complaint(complaint_id)
    return None


@router.get("/complaints/statistics/summary", response_model=ComplaintStatistics)
def get_complaint_statistics(
    db: Session = Depends(get_db)
):
    """Get complaint statistics for dashboard"""
    service = ComplaintService(db)
    return service.get_statistics()


# ============================================================================
# ESCALATION ENDPOINTS
# ============================================================================

@router.post("/escalations", response_model=ComplaintEscalationResponse, status_code=status.HTTP_201_CREATED)
def create_escalation(
    escalation: ComplaintEscalationCreate,
    db: Session = Depends(get_db)
):
    """Create a complaint escalation"""
    service = EscalationService(db)
    return service.create_escalation(escalation)


@router.post("/escalations/auto-escalate/{complaint_id}", response_model=ComplaintEscalationResponse)
def auto_escalate_complaint(
    complaint_id: int,
    escalated_to: int,
    db: Session = Depends(get_db)
):
    """Auto-escalate a complaint due to SLA breach"""
    service = EscalationService(db)
    return service.auto_escalate_complaint(complaint_id, escalated_to)


@router.get("/escalations", response_model=dict)
def list_escalations(
    complaint_id: Optional[int] = None,
    escalation_level: Optional[EscalationLevel] = None,
    escalated_to: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List escalations with filters"""
    service = EscalationService(db)
    escalations, total = service.list_escalations(
        complaint_id=complaint_id,
        escalation_level=escalation_level,
        escalated_to=escalated_to,
        status=status,
        skip=skip,
        limit=limit,
    )
    
    return {
        "escalations": escalations,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/escalations/{escalation_id}", response_model=ComplaintEscalationResponse)
def get_escalation(
    escalation_id: int,
    db: Session = Depends(get_db)
):
    """Get escalation by ID"""
    service = EscalationService(db)
    escalation = service.get_escalation(escalation_id)
    
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    return escalation


@router.post("/escalations/{escalation_id}/acknowledge", response_model=ComplaintEscalationResponse)
def acknowledge_escalation(
    escalation_id: int,
    acknowledgement: ComplaintEscalationAcknowledge,
    db: Session = Depends(get_db)
):
    """Acknowledge an escalation"""
    service = EscalationService(db)
    return service.acknowledge_escalation(escalation_id, acknowledgement)


@router.post("/escalations/{escalation_id}/resolve", response_model=ComplaintEscalationResponse)
def resolve_escalation(
    escalation_id: int,
    resolution: ComplaintEscalationResolve,
    db: Session = Depends(get_db)
):
    """Resolve an escalation"""
    service = EscalationService(db)
    return service.resolve_escalation(escalation_id, resolution)


@router.get("/escalations/pending/list", response_model=List[ComplaintEscalationResponse])
def get_pending_escalations(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get pending escalations for a user"""
    service = EscalationService(db)
    return service.get_pending_escalations(user_id)


@router.get("/escalations/sla-breach/list", response_model=List[ComplaintEscalationResponse])
def get_sla_breach_escalations(
    db: Session = Depends(get_db)
):
    """Get escalations that have breached SLA"""
    service = EscalationService(db)
    return service.get_sla_breach_escalations()


@router.delete("/escalations/{escalation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_escalation(
    escalation_id: int,
    db: Session = Depends(get_db)
):
    """Delete an escalation"""
    service = EscalationService(db)
    service.delete_escalation(escalation_id)
    return None


# ============================================================================
# OMBUDSMAN ENDPOINTS
# ============================================================================

@router.post("/ombudsman", response_model=OmbudsmanCaseResponse, status_code=status.HTTP_201_CREATED)
def create_ombudsman_case(
    case: OmbudsmanCaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new ombudsman case"""
    service = OmbudsmanService(db)
    return service.create_ombudsman_case(case)


@router.get("/ombudsman", response_model=dict)
def list_ombudsman_cases(
    status: Optional[OmbudsmanStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List ombudsman cases with filters"""
    service = OmbudsmanService(db)
    cases, total = service.list_ombudsman_cases(status=status, skip=skip, limit=limit)
    
    return {
        "cases": cases,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/ombudsman/{case_id}", response_model=OmbudsmanCaseResponse)
def get_ombudsman_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Get ombudsman case by ID"""
    service = OmbudsmanService(db)
    case = service.get_ombudsman_case(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ombudsman case not found"
        )
    
    return case


@router.get("/ombudsman/complaint/{complaint_id}", response_model=OmbudsmanCaseResponse)
def get_ombudsman_case_by_complaint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Get ombudsman case by complaint ID"""
    service = OmbudsmanService(db)
    case = service.get_ombudsman_case_by_complaint(complaint_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ombudsman case not found for this complaint"
        )
    
    return case


@router.put("/ombudsman/{case_id}", response_model=OmbudsmanCaseResponse)
def update_ombudsman_case(
    case_id: int,
    case_update: OmbudsmanCaseUpdate,
    db: Session = Depends(get_db)
):
    """Update ombudsman case"""
    service = OmbudsmanService(db)
    return service.update_ombudsman_case(case_id, case_update)


@router.post("/ombudsman/{case_id}/submit", response_model=OmbudsmanCaseResponse)
def submit_to_ombudsman(
    case_id: int,
    submission: OmbudsmanCaseSubmit,
    db: Session = Depends(get_db)
):
    """Submit case to ombudsman"""
    service = OmbudsmanService(db)
    return service.submit_to_ombudsman(case_id, submission)


@router.post("/ombudsman/{case_id}/schedule-hearing", response_model=OmbudsmanCaseResponse)
def schedule_hearing(
    case_id: int,
    hearing: OmbudsmanCaseHearing,
    db: Session = Depends(get_db)
):
    """Schedule ombudsman hearing"""
    service = OmbudsmanService(db)
    return service.schedule_hearing(case_id, hearing)


@router.post("/ombudsman/{case_id}/award", response_model=OmbudsmanCaseResponse)
def record_award(
    case_id: int,
    award: OmbudsmanCaseAward,
    db: Session = Depends(get_db)
):
    """Record ombudsman award"""
    service = OmbudsmanService(db)
    return service.record_award(case_id, award)


@router.post("/ombudsman/{case_id}/close", response_model=OmbudsmanCaseResponse)
def close_ombudsman_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Close ombudsman case"""
    service = OmbudsmanService(db)
    return service.close_case(case_id)


@router.delete("/ombudsman/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ombudsman_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Delete ombudsman case"""
    service = OmbudsmanService(db)
    service.delete_ombudsman_case(case_id)
    return None
