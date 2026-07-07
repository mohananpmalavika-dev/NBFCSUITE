"""
RBI Returns Automation Router
FastAPI endpoints for NBS-7, Statutory Returns, XBRL, Compliance Calendar
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User

from .schemas import (
    # RBI Return Master
    RBIReturnMasterCreate, RBIReturnMasterUpdate, RBIReturnMasterResponse,
    
    # NBS-7 Returns
    NBS7ReturnCreate, NBS7ReturnUpdate, NBS7ReturnResponse,
    NBS7ReturnGenerateRequest,
    
    # Statutory Returns
    StatutoryReturnCreate, StatutoryReturnUpdate, StatutoryReturnResponse,
    
    # XBRL Documents
    XBRLDocumentCreate, XBRLDocumentResponse,
    XBRLGenerateRequest, XBRLValidationResponse,
    
    # Compliance Calendar
    ComplianceCalendarCreate, ComplianceCalendarUpdate, ComplianceCalendarResponse,
    ComplianceCalendarCompleteRequest,
    
    # Dashboard & Analytics
    RBIReturnsDashboardStats, ComplianceCalendarSummary,
    ReturnSubmissionHistoryResponse,
    
    # Filters
    RBIReturnsFilter, ComplianceCalendarFilter
)
from .rbi_returns_service import RBIReturnsService


router = APIRouter(prefix="/api/rbi-returns", tags=["RBI Returns Automation"])


# ============================================================================
# RBI RETURN MASTER ENDPOINTS
# ============================================================================

@router.get("/masters", response_model=List[RBIReturnMasterResponse])
def list_return_masters(
    return_type: Optional[str] = None,
    is_active: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List RBI return master configurations"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    masters = service.get_return_masters(
        return_type=return_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return masters


@router.post("/masters", response_model=RBIReturnMasterResponse)
def create_return_master(
    data: RBIReturnMasterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create RBI return master configuration"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    master = service.create_return_master(data.dict())
    return master


# ============================================================================
# NBS-7 RETURN ENDPOINTS
# ============================================================================

@router.post("/nbs7/generate", response_model=NBS7ReturnResponse)
def generate_nbs7_return(
    request: NBS7ReturnGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-generate NBS-7 return from system data"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    nbs7_return = service.generate_nbs7_return(request)
    return nbs7_return


@router.get("/nbs7", response_model=List[NBS7ReturnResponse])
def list_nbs7_returns(
    financial_year: Optional[str] = None,
    quarter: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List NBS-7 returns"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    returns = service.list_nbs7_returns(
        financial_year=financial_year,
        quarter=quarter,
        status=status,
        skip=skip,
        limit=limit
    )
    return returns


@router.get("/nbs7/{return_id}", response_model=NBS7ReturnResponse)
def get_nbs7_return(
    return_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get NBS-7 return details"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    nbs7_return = service.get_nbs7_return(return_id)
    
    if not nbs7_return:
        raise HTTPException(status_code=404, detail="NBS-7 return not found")
    
    return nbs7_return


@router.put("/nbs7/{return_id}", response_model=NBS7ReturnResponse)
def update_nbs7_return(
    return_id: UUID,
    data: NBS7ReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update NBS-7 return"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    nbs7_return = service.update_nbs7_return(return_id, data)
    
    if not nbs7_return:
        raise HTTPException(status_code=404, detail="NBS-7 return not found")
    
    return nbs7_return


@router.post("/nbs7/{return_id}/approve", response_model=NBS7ReturnResponse)
def approve_nbs7_return(
    return_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve NBS-7 return"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    nbs7_return = service.approve_nbs7_return(return_id)
    
    if not nbs7_return:
        raise HTTPException(status_code=404, detail="NBS-7 return not found")
    
    return nbs7_return



@router.post("/nbs7/{return_id}/submit", response_model=NBS7ReturnResponse)
def submit_nbs7_return(
    return_id: UUID,
    submission_reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit NBS-7 return to RBI"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    nbs7_return = service.submit_nbs7_return(return_id, submission_reference)
    
    if not nbs7_return:
        raise HTTPException(status_code=404, detail="NBS-7 return not found or not approved")
    
    return nbs7_return


# ============================================================================
# STATUTORY RETURN ENDPOINTS
# ============================================================================

@router.post("/statutory", response_model=StatutoryReturnResponse)
def create_statutory_return(
    data: StatutoryReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create statutory return"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    statutory_return = service.create_statutory_return(data)
    return statutory_return


@router.get("/statutory", response_model=List[StatutoryReturnResponse])
def list_statutory_returns(
    return_type: Optional[str] = None,
    financial_year: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List statutory returns"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    returns = service.list_statutory_returns(
        return_type=return_type,
        financial_year=financial_year,
        status=status,
        skip=skip,
        limit=limit
    )
    return returns


@router.get("/statutory/{return_id}", response_model=StatutoryReturnResponse)
def get_statutory_return(
    return_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statutory return details"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    statutory_return = service.get_statutory_return(return_id)
    
    if not statutory_return:
        raise HTTPException(status_code=404, detail="Statutory return not found")
    
    return statutory_return


@router.post("/statutory/{return_id}/validate")
def validate_statutory_return(
    return_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate statutory return data"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    validation_result = service.validate_statutory_return(return_id)
    return validation_result


# ============================================================================
# XBRL DOCUMENT ENDPOINTS
# ============================================================================

@router.post("/xbrl/generate", response_model=XBRLDocumentResponse)
def generate_xbrl_document(
    request: XBRLGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate XBRL document from return data"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    xbrl_doc = service.generate_xbrl_document(request)
    return xbrl_doc


@router.get("/xbrl/{document_id}", response_model=XBRLDocumentResponse)
def get_xbrl_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get XBRL document details"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    xbrl_doc = service.get_xbrl_document(document_id)
    
    if not xbrl_doc:
        raise HTTPException(status_code=404, detail="XBRL document not found")
    
    return xbrl_doc


@router.get("/xbrl/{document_id}/download")
def download_xbrl_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download XBRL document XML"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    xbrl_doc = service.get_xbrl_document(document_id)
    
    if not xbrl_doc or not xbrl_doc.xbrl_content:
        raise HTTPException(status_code=404, detail="XBRL content not found")
    
    return Response(
        content=xbrl_doc.xbrl_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={xbrl_doc.document_number}.xml"
        }
    )


# ============================================================================
# COMPLIANCE CALENDAR ENDPOINTS
# ============================================================================

@router.post("/calendar", response_model=ComplianceCalendarResponse)
def create_calendar_event(
    data: ComplianceCalendarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create compliance calendar event"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    event = service.create_calendar_event(data)
    return event


@router.get("/calendar", response_model=List[ComplianceCalendarResponse])
def list_calendar_events(
    event_type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    assigned_to: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List compliance calendar events"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    events = service.list_calendar_events(
        event_type=event_type,
        priority=priority,
        status=status,
        from_date=from_date,
        to_date=to_date,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit
    )
    return events


@router.get("/calendar/{event_id}", response_model=ComplianceCalendarResponse)
def get_calendar_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calendar event details"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    event = service.get_calendar_event(event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    return event


@router.put("/calendar/{event_id}", response_model=ComplianceCalendarResponse)
def update_calendar_event(
    event_id: UUID,
    data: ComplianceCalendarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update calendar event"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    event = service.update_calendar_event(event_id, data)
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    return event


@router.post("/calendar/{event_id}/complete", response_model=ComplianceCalendarResponse)
def complete_calendar_event(
    event_id: UUID,
    request: ComplianceCalendarCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark calendar event as completed"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    event = service.complete_calendar_event(
        event_id,
        completion_notes=request.completion_notes,
        actual_effort_hours=request.actual_effort_hours
    )
    
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    return event


@router.get("/calendar/upcoming/deadlines", response_model=List[ComplianceCalendarResponse])
def get_upcoming_deadlines(
    days_ahead: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming compliance deadlines"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    deadlines = service.get_upcoming_deadlines(days_ahead=days_ahead, limit=limit)
    return deadlines


# ============================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard/stats", response_model=RBIReturnsDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get RBI returns dashboard statistics"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    stats = service.get_returns_dashboard_stats()
    return stats


@router.get("/dashboard/calendar-summary", response_model=ComplianceCalendarSummary)
def get_calendar_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compliance calendar summary"""
    service = RBIReturnsService(db, current_user.tenant_id, current_user.id)
    summary = service.get_compliance_calendar_summary()
    return summary
