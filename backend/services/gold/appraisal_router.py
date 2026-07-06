"""
Appraisal Router
API endpoints for ornament appraisal
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.gold.appraisal_service import AppraisalService
from backend.services.gold.schemas import (
    AppraisalReportCreateRequest,
    AppraisalReportUpdateRequest,
    AppraisalReportResponse
)

router = APIRouter(prefix="/appraisals", tags=["Appraisal"])


@router.post("/", response_model=AppraisalReportResponse)
async def create_appraisal(
    appraisal_data: AppraisalReportCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create comprehensive appraisal report"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.create_appraisal(appraisal_data)
    return AppraisalReportResponse.from_orm(appraisal)


@router.put("/{appraisal_id}", response_model=AppraisalReportResponse)
async def update_appraisal(
    appraisal_id: str,
    appraisal_data: AppraisalReportUpdateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Update appraisal report"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.update_appraisal(appraisal_id, appraisal_data)
    return AppraisalReportResponse.from_orm(appraisal)


@router.get("/{appraisal_id}", response_model=AppraisalReportResponse)
async def get_appraisal(
    appraisal_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get appraisal by ID"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.get_appraisal(appraisal_id)
    
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    
    return AppraisalReportResponse.from_orm(appraisal)


@router.get("/", response_model=List[AppraisalReportResponse])
async def list_appraisals(
    customer_id: Optional[str] = Query(None),
    loan_id: Optional[str] = Query(None),
    ornament_id: Optional[str] = Query(None),
    appraisal_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List appraisals with filters"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisals = service.list_appraisals(
        customer_id, loan_id, ornament_id, appraisal_type, status, start_date, end_date
    )
    return [AppraisalReportResponse.from_orm(appraisal) for appraisal in appraisals]


@router.post("/{appraisal_id}/submit", response_model=AppraisalReportResponse)
async def submit_appraisal(
    appraisal_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Submit appraisal for verification"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.submit_appraisal(appraisal_id)
    return AppraisalReportResponse.from_orm(appraisal)


@router.post("/{appraisal_id}/verify", response_model=AppraisalReportResponse)
async def verify_appraisal(
    appraisal_id: str,
    verification_status: str = Query(..., description="Approved or Rejected"),
    remarks: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Verify/approve or reject appraisal"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.verify_appraisal(appraisal_id, verification_status, remarks)
    return AppraisalReportResponse.from_orm(appraisal)


@router.post("/{appraisal_id}/certificate", response_model=AppraisalReportResponse)
async def generate_appraisal_certificate(
    appraisal_id: str,
    valid_days: int = Query(default=180, ge=1),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Generate appraisal certificate"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.generate_certificate(appraisal_id, valid_days)
    return AppraisalReportResponse.from_orm(appraisal)


@router.post("/{previous_appraisal_id}/reappraise", response_model=AppraisalReportResponse)
async def create_reappraisal(
    previous_appraisal_id: str,
    appraisal_type: str = Query(default="Re-appraisal"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create re-appraisal based on previous appraisal"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisal = service.create_reappraisal(previous_appraisal_id, appraisal_type)
    return AppraisalReportResponse.from_orm(appraisal)


@router.get("/ornament/{ornament_id}/history", response_model=List[AppraisalReportResponse])
async def get_appraisal_history(
    ornament_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get complete appraisal history for an ornament"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisals = service.get_appraisal_history(ornament_id)
    return [AppraisalReportResponse.from_orm(appraisal) for appraisal in appraisals]


@router.get("/due-for-renewal", response_model=List[AppraisalReportResponse])
async def get_appraisals_due_for_renewal(
    days_ahead: int = Query(default=30, ge=1),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get appraisals due for renewal"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    appraisals = service.get_appraisals_due_for_renewal(days_ahead)
    return [AppraisalReportResponse.from_orm(appraisal) for appraisal in appraisals]


@router.get("/compare/{appraisal_id1}/{appraisal_id2}")
async def compare_appraisals(
    appraisal_id1: str,
    appraisal_id2: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Compare two appraisals"""
    service = AppraisalService(db, tenant_id, current_user.get("user_id"))
    return service.compare_appraisals(appraisal_id1, appraisal_id2)
