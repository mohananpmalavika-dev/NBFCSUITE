"""
Reports and Analytics Router

API endpoints for deposit reports and dashboards
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["Deposit Reports"])


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get deposit dashboard
    
    Returns comprehensive overview of all deposit operations.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    dashboard = service.get_dashboard()
    
    return {
        "success": True,
        "data": dashboard
    }


@router.get("/summary")
def get_deposit_summary(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    account_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get deposit summary report
    
    Aggregated view of deposits by type, status, etc.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    summary = service.get_deposit_summary(
        from_date=from_date,
        to_date=to_date,
        account_type=account_type
    )
    
    return {
        "success": True,
        "data": summary
    }


@router.get("/maturity-calendar")
def get_maturity_calendar(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get maturity calendar
    
    Shows all accounts maturing in the specified period.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    calendar = service.get_maturity_calendar(
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "success": True,
        "data": calendar
    }


@router.get("/interest-accrual")
def get_interest_accrual_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    account_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get interest accrual report
    
    Shows interest accrued/posted for the period.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    report = service.get_interest_accrual_report(
        from_date=from_date,
        to_date=to_date,
        account_type=account_type
    )
    
    return {
        "success": True,
        "data": report
    }


@router.get("/aging-analysis")
def get_aging_analysis(
    as_of_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get deposit aging analysis
    
    Shows age distribution of deposits.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    analysis = service.get_aging_analysis(as_of_date=as_of_date)
    
    return {
        "success": True,
        "data": analysis
    }


@router.get("/product-performance")
def get_product_performance(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get product performance report
    
    Shows performance metrics for each deposit product.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    performance = service.get_product_performance(
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "success": True,
        "data": performance
    }


@router.get("/dormancy-report")
def get_dormancy_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get dormancy report
    
    Shows dormant and near-dormant accounts.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    report = service.get_dormancy_report()
    
    return {
        "success": True,
        "data": report
    }


@router.get("/tds-summary")
def get_tds_summary(
    financial_year: str = Query(..., description="FY in format YYYY-YYYY"),
    quarter: Optional[int] = Query(None, ge=1, le=4),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get TDS summary report
    
    Shows TDS deducted for the period.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    summary = service.get_tds_summary(
        financial_year=financial_year,
        quarter=quarter
    )
    
    return {
        "success": True,
        "data": summary
    }


@router.get("/transaction-volume")
def get_transaction_volume_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    group_by: str = Query("day", description="Group by: day, week, month"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get transaction volume report
    
    Shows transaction counts and volumes over time.
    """
    service = ReportsService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    report = service.get_transaction_volume_report(
        from_date=from_date,
        to_date=to_date,
        group_by=group_by
    )
    
    return {
        "success": True,
        "data": report
    }
