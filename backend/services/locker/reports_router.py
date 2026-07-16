"""
Locker Reports & Analytics API Router
Handles comprehensive reporting and analytics endpoints
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.auth.dependencies import get_current_user
from .reports_service import (
    LockerReportsService,
    ReportType,
    ExportFormat,
    ReportPeriod,
    ReportStatus
)


router = APIRouter(prefix="/api/locker/reports", tags=["Locker Reports & Analytics"])


# ==================== REQUEST MODELS ====================

class AllocationRegisterRequest(BaseModel):
    """Request model for allocation register report"""
    branch_id: Optional[str] = None
    allocation_status: Optional[str] = None
    customer_category: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class RentCollectionRequest(BaseModel):
    """Request model for rent collection report"""
    branch_id: Optional[str] = None
    period: ReportPeriod = ReportPeriod.THIS_MONTH
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None
    payment_mode: Optional[str] = None


class OverdueRentRequest(BaseModel):
    """Request model for overdue rent report"""
    branch_id: Optional[str] = None
    min_overdue_days: Optional[int] = 0
    max_overdue_days: Optional[int] = None


class AccessLogRequest(BaseModel):
    """Request model for access log report"""
    branch_id: Optional[str] = None
    locker_id: Optional[str] = None
    period: ReportPeriod = ReportPeriod.THIS_MONTH
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None


class LockerBreakingRequest(BaseModel):
    """Request model for locker breaking register"""
    branch_id: Optional[str] = None
    period: ReportPeriod = ReportPeriod.THIS_YEAR
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None


class RevenueReportRequest(BaseModel):
    """Request model for revenue report"""
    branch_id: Optional[str] = None
    period: ReportPeriod = ReportPeriod.THIS_MONTH
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None
    group_by: Optional[str] = "month"


class OccupancyRateRequest(BaseModel):
    """Request model for occupancy rate report"""
    branch_id: Optional[str] = None
    period: ReportPeriod = ReportPeriod.THIS_YEAR
    custom_start: Optional[datetime] = None
    custom_end: Optional[datetime] = None


class ExportRequest(BaseModel):
    """Request model for exporting reports"""
    report_type: ReportType
    format: ExportFormat
    filters: dict = {}


# ==================== DASHBOARD ENDPOINTS ====================

@router.get("/dashboard")
async def get_dashboard(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive dashboard with all KPIs
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    dashboard = await service.get_dashboard(branch_id=branch_id)
    
    return dashboard


# ==================== REPORT GENERATION ENDPOINTS ====================

@router.post("/allocation-register")
async def generate_allocation_register(
    request: AllocationRegisterRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate locker allocation register report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.generate_allocation_register(
        filters=request.dict()
    )
    
    return report


@router.get("/available-occupied")
async def generate_available_occupied_report(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate available/occupied lockers report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.generate_available_occupied_report(
        branch_id=branch_id
    )
    
    return report


@router.get("/waiting-list")
async def generate_waiting_list_report(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate waiting list report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.generate_waiting_list_report(
        branch_id=branch_id
    )
    
    return report


@router.post("/rent-collection")
async def generate_rent_collection_report(
    request: RentCollectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate rent collection report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    date_range = service._get_date_range(
        period=request.period,
        custom_start=request.custom_start,
        custom_end=request.custom_end
    )
    
    report = await service.generate_rent_collection_report(
        period=date_range
    )
    
    return report


@router.post("/overdue-rent")
async def generate_overdue_rent_report(
    request: OverdueRentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate overdue rent report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.generate_overdue_rent_report(
        branch_id=request.branch_id
    )
    
    return report


@router.post("/access-log")
async def generate_access_log_report(
    request: AccessLogRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate access log report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    date_range = service._get_date_range(
        period=request.period,
        custom_start=request.custom_start,
        custom_end=request.custom_end
    )
    
    report = await service.generate_access_log_report(
        period=date_range,
        branch_id=request.branch_id
    )
    
    return report


@router.post("/locker-breaking")
async def generate_locker_breaking_register(
    request: LockerBreakingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate locker breaking register
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    date_range = service._get_date_range(
        period=request.period,
        custom_start=request.custom_start,
        custom_end=request.custom_end
    )
    
    report = await service.generate_locker_breaking_register(
        period=date_range
    )
    
    return report


@router.get("/branch-wise")
async def generate_branch_wise_report(
    include_details: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate branch-wise locker report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.generate_branch_wise_report(
        include_details=include_details
    )
    
    return report


@router.post("/revenue")
async def generate_revenue_report(
    request: RevenueReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate revenue from lockers report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    date_range = service._get_date_range(
        period=request.period,
        custom_start=request.custom_start,
        custom_end=request.custom_end
    )
    
    report = await service.generate_revenue_report(
        period=date_range,
        branch_id=request.branch_id
    )
    
    return report


@router.post("/occupancy-rate")
async def generate_occupancy_rate_report(
    request: OccupancyRateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate occupancy rate report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    date_range = service._get_date_range(
        period=request.period,
        custom_start=request.custom_start,
        custom_end=request.custom_end
    )
    
    report = await service.generate_occupancy_rate_report(
        period=date_range
    )
    
    return report


@router.get("/customer-demographics")
async def generate_customer_demographics_report(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate customer demographics report
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.generate_customer_demographics_report(
        branch_id=branch_id
    )
    
    return report


# ==================== REPORT MANAGEMENT ENDPOINTS ====================

@router.get("/list")
async def get_report_list(
    report_type: Optional[ReportType] = Query(None),
    status: Optional[ReportStatus] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of generated reports
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    reports = await service.get_report_list(
        report_type=report_type,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    
    return {"reports": reports}


@router.get("/{report_id}")
async def get_report_details(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed report by ID
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    report = await service.get_report_details(report_id=report_id)
    
    return report


# ==================== EXPORT ENDPOINTS ====================

@router.post("/export")
async def export_report(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Export report to specified format (PDF, Excel, CSV, JSON)
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    # Generate the report based on type
    if request.report_type == ReportType.ALLOCATION_REGISTER:
        report_data = await service.generate_allocation_register(request.filters)
    elif request.report_type == ReportType.AVAILABLE_OCCUPIED:
        report_data = await service.generate_available_occupied_report()
    elif request.report_type == ReportType.RENT_COLLECTION:
        period = service._get_date_range(ReportPeriod.THIS_MONTH)
        report_data = await service.generate_rent_collection_report(period)
    else:
        raise HTTPException(status_code=400, detail="Report type not supported for export")
    
    # Export the report
    export_result = await service.export_report(
        report_data=report_data,
        format=request.format
    )
    
    return export_result


# ==================== STATISTICS ENDPOINTS ====================

@router.get("/statistics/{metric}")
async def get_statistics(
    metric: str,
    period: ReportPeriod = Query(ReportPeriod.THIS_MONTH),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific statistics
    """
    service = LockerReportsService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"]
    )
    
    stats = await service.get_statistics(
        metric=metric,
        period=period
    )
    
    return stats
