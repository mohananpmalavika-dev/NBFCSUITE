"""
Dashboard Router
API endpoints for executive dashboards
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
import math

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.reporting_models import Dashboard, DashboardWidget
from backend.services.reporting import schemas


router = APIRouter(prefix="/dashboards", tags=["Reporting - Dashboards"])


@router.get("", response_model=dict)
async def list_dashboards(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    dashboard_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all dashboards"""
    try:
        query = select(Dashboard).where(
            Dashboard.tenant_id == current_user["tenant_id"],
            Dashboard.is_deleted == False
        )
        
        if dashboard_type:
            query = query.where(Dashboard.dashboard_type == dashboard_type)
        
        if is_active is not None:
            query = query.where(Dashboard.is_active == is_active)
        
        # Count
        count_query = select(func.count()).select_from(Dashboard).where(
            Dashboard.tenant_id == current_user["tenant_id"],
            Dashboard.is_deleted == False
        )
        if dashboard_type:
            count_query = count_query.where(Dashboard.dashboard_type == dashboard_type)
        if is_active is not None:
            count_query = count_query.where(Dashboard.is_active == is_active)
        
        total = await db.scalar(count_query)
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(Dashboard.is_default.desc(), Dashboard.dashboard_name)
        
        result = await db.execute(query)
        dashboards = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.DashboardResponse.model_validate(d) for d in dashboards],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} dashboards"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{dashboard_id}", response_model=dict)
async def get_dashboard(
    dashboard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard with all widgets"""
    try:
        result = await db.execute(
            select(Dashboard).where(
                Dashboard.id == dashboard_id,
                Dashboard.tenant_id == current_user["tenant_id"],
                Dashboard.is_deleted == False
            )
        )
        dashboard = result.scalar_one_or_none()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Get widgets
        widgets_result = await db.execute(
            select(DashboardWidget).where(
                DashboardWidget.dashboard_id == dashboard_id,
                DashboardWidget.is_active == True,
                DashboardWidget.is_deleted == False
            )
        )
        widgets = widgets_result.scalars().all()
        
        return success_response(
            data={
                "dashboard": schemas.DashboardResponse.model_validate(dashboard),
                "widgets": [schemas.DashboardWidgetResponse.model_validate(w) for w in widgets]
            },
            message="Dashboard retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    data: schemas.DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new dashboard"""
    try:
        dashboard = Dashboard(
            tenant_id=current_user["tenant_id"],
            **data.model_dump(),
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)
        
        return success_response(
            data=schemas.DashboardResponse.model_validate(dashboard),
            message="Dashboard created successfully"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/widgets", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_widget(
    data: schemas.DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add widget to dashboard"""
    try:
        # Verify dashboard exists
        result = await db.execute(
            select(Dashboard).where(
                Dashboard.id == data.dashboard_id,
                Dashboard.tenant_id == current_user["tenant_id"],
                Dashboard.is_deleted == False
            )
        )
        dashboard = result.scalar_one_or_none()
        
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        widget = DashboardWidget(
            tenant_id=current_user["tenant_id"],
            **data.model_dump(),
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(widget)
        await db.commit()
        await db.refresh(widget)
        
        return success_response(
            data=schemas.DashboardWidgetResponse.model_validate(widget),
            message="Widget added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/executive/summary", response_model=dict)
async def get_executive_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get executive dashboard summary data
    
    Returns key metrics for executive decision making
    """
    try:
        from backend.shared.database.loan_models import LoanAccount
        from backend.shared.database.customer_models import Customer
        
        # Portfolio metrics
        portfolio_result = await db.execute(
            select(
                func.count(LoanAccount.id).label('total_loans'),
                func.sum(LoanAccount.sanctioned_amount).label('total_sanctioned'),
                func.sum(LoanAccount.principal_outstanding).label('outstanding')
            ).where(
                LoanAccount.tenant_id == current_user["tenant_id"],
                LoanAccount.is_deleted == False
            )
        )
        portfolio = portfolio_result.first()
        
        # Customer count
        customer_count = await db.scalar(
            select(func.count(Customer.id)).where(
                Customer.tenant_id == current_user["tenant_id"],
                Customer.is_deleted == False
            )
        )
        
        data = {
            "portfolio": {
                "total_loans": portfolio.total_loans or 0,
                "total_sanctioned": float(portfolio.total_sanctioned or 0),
                "outstanding": float(portfolio.outstanding or 0),
                "avg_ticket_size": float(portfolio.total_sanctioned or 0) / max(portfolio.total_loans or 1, 1)
            },
            "customers": {
                "total_customers": customer_count or 0,
                "new_this_month": 0,  # TODO: Calculate
                "active_customers": customer_count or 0
            },
            "collections": {
                "collection_efficiency": 92.5,  # TODO: Calculate
                "overdue_amount": 0,  # TODO: Calculate
                "overdue_accounts": 0  # TODO: Calculate
            },
            "risk": {
                "npa_ratio": 2.3,  # TODO: Calculate
                "portfolio_at_risk": 5.8,  # TODO: Calculate
                "high_risk_accounts": 0  # TODO: Calculate
            }
        }
        
        return success_response(
            data=data,
            message="Executive dashboard data retrieved"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
