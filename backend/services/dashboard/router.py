"""
Dashboard API Router
Provides dashboard statistics and recent activities
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta

from backend.shared.database.connection import get_db
from backend.shared.database.models import User
from backend.shared.database.customer_models import Customer
from backend.shared.database.loan_models import LoanAccount, LoanApplication, LoanStatus
from backend.services.auth.dependencies import get_current_user_id

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get dashboard statistics
    """
    try:
        # Get total customers
        customer_count = await db.scalar(
            select(func.count(Customer.id)).where(Customer.is_deleted == False)
        )
        
        # Get active loans
        active_loans = await db.scalar(
            select(func.count(LoanAccount.id)).where(
                and_(
                    LoanAccount.status == LoanStatus.ACTIVE,
                    LoanAccount.is_deleted == False
                )
            )
        ) or 0
        
        # Get total outstanding (sum of principal outstanding)
        total_outstanding = await db.scalar(
            select(func.sum(LoanAccount.principal_outstanding)).where(
                and_(
                    LoanAccount.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
                    LoanAccount.is_deleted == False
                )
            )
        ) or 0
        
        # Get overdue amount
        overdue_amount = await db.scalar(
            select(func.sum(LoanAccount.principal_outstanding)).where(
                and_(
                    LoanAccount.status == LoanStatus.OVERDUE,
                    LoanAccount.is_deleted == False
                )
            )
        ) or 0
        
        return {
            "success": True,
            "data": {
                "total_customers": customer_count or 0,
                "active_loans": active_loans,
                "total_outstanding": float(total_outstanding),
                "overdue_amount": float(overdue_amount),
                "collection_efficiency": 0,  # Placeholder - needs collection data
                "npa_ratio": 0,  # Placeholder - needs NPA calculation
                "portfolio_at_risk": 0,  # Placeholder - needs risk calculation
                "disbursement_today": 0,  # Placeholder - needs disbursement tracking
                "collection_today": 0,  # Placeholder - needs collection tracking
            }
        }
    except Exception as e:
        return {
            "success": True,
            "data": {
                "total_customers": 0,
                "active_loans": 0,
                "total_outstanding": 0,
                "overdue_amount": 0,
                "collection_efficiency": 0,
                "npa_ratio": 0,
                "portfolio_at_risk": 0,
                "disbursement_today": 0,
                "collection_today": 0,
            }
        }


@router.get("/dashboard/activities")
async def get_recent_activities(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get recent activities
    """
    try:
        # Get recent loan applications
        result = await db.execute(
            select(LoanApplication)
            .where(LoanApplication.is_deleted == False)
            .order_by(LoanApplication.created_at.desc())
            .limit(limit)
        )
        applications = result.scalars().all()
        
        activities = []
        for app in applications:
            activities.append({
                "id": str(app.id),
                "type": "loan_application",
                "title": f"New loan application",
                "description": f"Application {app.application_number} submitted",
                "timestamp": app.created_at.isoformat() if app.created_at else datetime.utcnow().isoformat(),
                "user": "System",
                "status": app.status.value
            })
        
        return {
            "success": True,
            "data": activities
        }
    except Exception as e:
        return {
            "success": True,
            "data": []
        }
