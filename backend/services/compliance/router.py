"""
Compliance & Regulatory Reporting Router
CRILC & SMA Reporting APIs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, require_permissions
from backend.shared.database.models import User

from .schemas import (
    # CRILC Schemas
    CRILCBorrowerCreate, CRILCBorrowerUpdate, CRILCBorrowerResponse,
    CRILCFacilityCreate, CRILCFacilityUpdate, CRILCFacilityResponse,
    CRILCQuarterlyReturnCreate, CRILCQuarterlyReturnResponse,
    LargeCreditIdentificationRequest,
    
    # SMA Schemas
    SMATrackingCreate, SMATrackingResponse,
    SMAStatusHistoryResponse,
    SMAQuarterlyReportCreate, SMAQuarterlyReportResponse,
    SMACalculationRequest, SMADashboardStats,
    
    # Alert Schemas
    ComplianceAlertCreate, ComplianceAlertResponse,
    
    # Filter Schemas
    LargeCreditFilter
)
from .crilc_service import CRILCService
from .sma_service import SMAService
from .alert_service import ComplianceAlertService


router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


# ============================================================================
# CRILC BORROWER ENDPOINTS
# ============================================================================

@router.post("/crilc/borrowers", response_model=CRILCBorrowerResponse)
def create_crilc_borrower(
    data: CRILCBorrowerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Create CRILC borrower for large credit tracking"""
    service = CRILCService(db, current_user.tenant_id)
    borrower = service.create_borrower(data, current_user.id)
    return borrower


@router.get("/crilc/borrowers/{borrower_id}", response_model=CRILCBorrowerResponse)
def get_crilc_borrower(
    borrower_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get CRILC borrower details"""
    service = CRILCService(db, current_user.tenant_id)
    borrower = service.get_borrower(borrower_id)
    
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    return borrower


@router.put("/crilc/borrowers/{borrower_id}", response_model=CRILCBorrowerResponse)
def update_crilc_borrower(
    borrower_id: UUID,
    data: CRILCBorrowerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Update CRILC borrower"""
    service = CRILCService(db, current_user.tenant_id)
    borrower = service.update_borrower(borrower_id, data, current_user.id)
    
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    
    return borrower


@router.get("/crilc/borrowers", response_model=List[CRILCBorrowerResponse])
def list_crilc_borrowers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_large_credit: Optional[bool] = None,
    sma_status: Optional[str] = None,
    industry_code: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """List CRILC borrowers with filters"""
    service = CRILCService(db, current_user.tenant_id)
    borrowers = service.list_borrowers(
        skip=skip,
        limit=limit,
        is_large_credit=is_large_credit,
        sma_status=sma_status,
        industry_code=industry_code,
        state=state
    )
    return borrowers


# ============================================================================
# CRILC FACILITY ENDPOINTS
# ============================================================================

@router.post("/crilc/facilities", response_model=CRILCFacilityResponse)
def add_crilc_facility(
    data: CRILCFacilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Add facility to CRILC borrower"""
    service = CRILCService(db, current_user.tenant_id)
    facility = service.add_facility(data, current_user.id)
    return facility


@router.put("/crilc/facilities/{facility_id}", response_model=CRILCFacilityResponse)
def update_crilc_facility(
    facility_id: UUID,
    data: CRILCFacilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Update CRILC facility"""
    service = CRILCService(db, current_user.tenant_id)
    facility = service.update_facility(facility_id, data, current_user.id)
    
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    return facility


@router.get("/crilc/borrowers/{borrower_id}/facilities", response_model=List[CRILCFacilityResponse])
def get_borrower_facilities(
    borrower_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get all facilities for a borrower"""
    service = CRILCService(db, current_user.tenant_id)
    facilities = service.get_borrower_facilities(borrower_id)
    return facilities


# ============================================================================
# LARGE CREDIT IDENTIFICATION
# ============================================================================

@router.post("/crilc/identify-large-credits")
def identify_large_credits(
    request: LargeCreditIdentificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Identify large credits based on threshold (₹5 Crore default)"""
    service = CRILCService(db, current_user.tenant_id)
    result = service.identify_large_credits(request)
    return result


# ============================================================================
# CRILC QUARTERLY RETURNS
# ============================================================================

@router.post("/crilc/quarterly-returns", response_model=CRILCQuarterlyReturnResponse)
def generate_crilc_quarterly_return(
    data: CRILCQuarterlyReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Generate CRILC quarterly return"""
    service = CRILCService(db, current_user.tenant_id)
    report = service.generate_quarterly_return(data, current_user.id)
    return report


@router.get("/crilc/quarterly-returns/{return_id}", response_model=CRILCQuarterlyReturnResponse)
def get_crilc_quarterly_return(
    return_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get CRILC quarterly return"""
    service = CRILCService(db, current_user.tenant_id)
    report = service.get_quarterly_return(return_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Return not found")
    
    return report


@router.get("/crilc/quarterly-returns", response_model=List[CRILCQuarterlyReturnResponse])
def list_crilc_quarterly_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """List CRILC quarterly returns"""
    service = CRILCService(db, current_user.tenant_id)
    reports = service.list_quarterly_returns(skip=skip, limit=limit)
    return reports


@router.post("/crilc/quarterly-returns/{return_id}/approve", response_model=CRILCQuarterlyReturnResponse)
def approve_crilc_quarterly_return(
    return_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.approve"]))
):
    """Approve CRILC quarterly return"""
    service = CRILCService(db, current_user.tenant_id)
    report = service.approve_quarterly_return(return_id, current_user.id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Return not found")
    
    return report


@router.post("/crilc/quarterly-returns/{return_id}/submit", response_model=CRILCQuarterlyReturnResponse)
def submit_crilc_quarterly_return(
    return_id: UUID,
    submission_reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.submit"]))
):
    """Submit CRILC quarterly return to RBI"""
    service = CRILCService(db, current_user.tenant_id)
    report = service.submit_quarterly_return(return_id, submission_reference, current_user.id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Return not found or not approved")
    
    return report


# ============================================================================
# SMA TRACKING ENDPOINTS
# ============================================================================

@router.post("/sma/calculate")
def calculate_sma_status(
    request: SMACalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Calculate SMA status for loan accounts"""
    service = SMAService(db, current_user.tenant_id)
    result = service.calculate_sma_status(request, current_user.id)
    return result


@router.get("/sma/tracking/{tracking_id}", response_model=SMATrackingResponse)
def get_sma_tracking(
    tracking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get SMA tracking record"""
    service = SMAService(db, current_user.tenant_id)
    tracking = service.get_sma_tracking(tracking_id)
    
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    
    return tracking


@router.get("/sma/tracking", response_model=List[SMATrackingResponse])
def list_sma_tracking(
    as_on_date: Optional[date] = None,
    sma_status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """List SMA tracking records"""
    service = SMAService(db, current_user.tenant_id)
    tracking = service.list_sma_tracking(
        as_on_date=as_on_date,
        sma_status=sma_status,
        skip=skip,
        limit=limit
    )
    return tracking


@router.get("/sma/loan/{loan_account_id}/history", response_model=List[SMATrackingResponse])
def get_loan_sma_history(
    loan_account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get SMA history for a loan account"""
    service = SMAService(db, current_user.tenant_id)
    history = service.get_loan_sma_history(loan_account_id)
    return history


@router.get("/sma/status-changes", response_model=List[SMAStatusHistoryResponse])
def get_sma_status_changes(
    loan_account_id: Optional[UUID] = None,
    borrower_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get SMA status change history"""
    service = SMAService(db, current_user.tenant_id)
    history = service.get_status_change_history(
        loan_account_id=loan_account_id,
        borrower_id=borrower_id,
        skip=skip,
        limit=limit
    )
    return history


@router.get("/sma/dashboard", response_model=SMADashboardStats)
def get_sma_dashboard(
    as_on_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """Get SMA dashboard statistics"""
    service = SMAService(db, current_user.tenant_id)
    stats = service.get_dashboard_stats(as_on_date)
    return stats


# ============================================================================
# SMA QUARTERLY REPORTS
# ============================================================================

@router.post("/sma/quarterly-reports", response_model=SMAQuarterlyReportResponse)
def generate_sma_quarterly_report(
    data: SMAQuarterlyReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Generate SMA quarterly report"""
    service = SMAService(db, current_user.tenant_id)
    report = service.generate_quarterly_report(data, current_user.id)
    return report


# ============================================================================
# COMPLIANCE ALERTS
# ============================================================================

@router.get("/alerts", response_model=List[ComplianceAlertResponse])
def list_compliance_alerts(
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.read"]))
):
    """List compliance alerts"""
    service = ComplianceAlertService(db, current_user.tenant_id)
    alerts = service.list_alerts(
        status=status,
        alert_type=alert_type,
        severity=severity,
        skip=skip,
        limit=limit
    )
    return alerts


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Acknowledge compliance alert"""
    service = ComplianceAlertService(db, current_user.tenant_id)
    alert = service.acknowledge_alert(alert_id, current_user.id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert acknowledged", "alert_id": str(alert.id)}


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: UUID,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["compliance.write"]))
):
    """Resolve compliance alert"""
    service = ComplianceAlertService(db, current_user.tenant_id)
    alert = service.resolve_alert(alert_id, resolution_notes, current_user.id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved", "alert_id": str(alert.id)}
