"""
Dashboard and Analytics Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from decimal import Decimal
from ..database import get_db
from ..models import DepositAccount, DepositAccountStatus, DepositProduct

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(
    branch_code: str = None,
    db: Session = Depends(get_db)
):
    """Get deposit dashboard summary"""
    
    query = db.query(DepositAccount)
    
    if branch_code:
        query = query.filter(DepositAccount.branch_code == branch_code)
    
    # Total active deposits
    active_accounts = query.filter(
        DepositAccount.status == DepositAccountStatus.ACTIVE
    ).all()
    
    total_deposits = sum(acc.principal_amount for acc in active_accounts)
    total_accounts = len(active_accounts)
    
    # Average interest rate
    avg_rate = sum(acc.interest_rate for acc in active_accounts) / total_accounts if total_accounts > 0 else 0
    
    # Today's deposits
    today_accounts = query.filter(
        DepositAccount.open_date == date.today(),
        DepositAccount.status == DepositAccountStatus.ACTIVE
    ).all()
    deposits_today = sum(acc.principal_amount for acc in today_accounts)
    
    # Upcoming maturities
    next_30_days = date.today() + timedelta(days=30)
    maturing_accounts = query.filter(
        DepositAccount.maturity_date <= next_30_days,
        DepositAccount.maturity_date >= date.today(),
        DepositAccount.status == DepositAccountStatus.ACTIVE
    ).all()
    
    maturities_count = len(maturing_accounts)
    maturity_amount = sum(acc.maturity_amount or 0 for acc in maturing_accounts)
    
    # Renewals this month
    first_day_month = date.today().replace(day=1)
    renewals_count = query.filter(
        DepositAccount.status == DepositAccountStatus.RENEWED,
        DepositAccount.actual_closure_date >= first_day_month
    ).count()
    
    # Premature closures this month
    premature_count = query.filter(
        DepositAccount.status == DepositAccountStatus.PREMATURELY_CLOSED,
        DepositAccount.actual_closure_date >= first_day_month
    ).count()
    
    # Interest liability
    total_interest_liability = sum(
        (acc.maturity_amount or 0) - acc.principal_amount 
        for acc in active_accounts
    )
    
    return {
        "total_deposits": float(total_deposits),
        "total_accounts": total_accounts,
        "active_accounts": total_accounts,
        "total_interest_liability": float(total_interest_liability),
        "avg_interest_rate": float(avg_rate),
        "deposits_today": float(deposits_today),
        "maturities_next_30_days": maturities_count,
        "maturity_amount_next_30_days": float(maturity_amount),
        "renewals_this_month": renewals_count,
        "premature_closures_this_month": premature_count
    }


@router.get("/treasury")
def get_treasury_view(
    db: Session = Depends(get_db)
):
    """Treasury deposit analytics"""
    
    active_accounts = db.query(DepositAccount).filter(
        DepositAccount.status == DepositAccountStatus.ACTIVE
    ).all()
    
    total_deposit_base = sum(acc.principal_amount for acc in active_accounts)
    
    # Calculate weighted average cost of funds
    if active_accounts:
        total_interest = sum(
            acc.principal_amount * acc.interest_rate 
            for acc in active_accounts
        )
        cost_of_funds = total_interest / total_deposit_base
    else:
        cost_of_funds = Decimal('0')
    
    # Maturity pipeline
    today = date.today()
    
    pipeline_7 = sum(
        acc.maturity_amount or 0
        for acc in active_accounts
        if acc.maturity_date <= today + timedelta(days=7)
    )
    
    pipeline_30 = sum(
        acc.maturity_amount or 0
        for acc in active_accounts
        if acc.maturity_date <= today + timedelta(days=30)
    )
    
    pipeline_90 = sum(
        acc.maturity_amount or 0
        for acc in active_accounts
        if acc.maturity_date <= today + timedelta(days=90)
    )
    
    # Branch-wise distribution
    branch_wise = {}
    for acc in active_accounts:
        branch = acc.branch_code or "HEAD_OFFICE"
        branch_wise[branch] = branch_wise.get(branch, Decimal('0')) + acc.principal_amount
    
    # Product-wise distribution
    product_wise = {}
    for acc in active_accounts:
        ptype = acc.deposit_type
        product_wise[ptype] = product_wise.get(ptype, Decimal('0')) + acc.principal_amount
    
    return {
        "total_deposit_base": float(total_deposit_base),
        "cost_of_funds": float(cost_of_funds),
        "liquidity_position": float(total_deposit_base - pipeline_7),
        "maturity_pipeline_7_days": float(pipeline_7),
        "maturity_pipeline_30_days": float(pipeline_30),
        "maturity_pipeline_90_days": float(pipeline_90),
        "branch_wise_deposits": {k: float(v) for k, v in branch_wise.items()},
        "product_wise_deposits": {k: float(v) for k, v in product_wise.items()}
    }


@router.get("/customer-portfolio/{customer_id}")
def get_customer_portfolio(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Customer deposit portfolio"""
    
    accounts = db.query(DepositAccount).filter(
        DepositAccount.customer_id == customer_id
    ).all()
    
    if not accounts:
        return {
            "customer_id": customer_id,
            "message": "No deposits found"
        }
    
    total_deposits = sum(
        acc.principal_amount 
        for acc in accounts 
        if acc.status == DepositAccountStatus.ACTIVE
    )
    
    total_interest_earned = sum(acc.total_interest_earned for acc in accounts)
    
    # Get AI insights
    from ..services import AIIntelligenceService
    ai_service = AIIntelligenceService(db)
    
    try:
        ai_insights = ai_service.analyze_customer_behavior(customer_id)
    except Exception:
        ai_insights = None
    
    return {
        "customer_id": customer_id,
        "cif_number": accounts[0].cif_number if accounts else None,
        "total_deposits": float(total_deposits),
        "num_accounts": len(accounts),
        "active_accounts": sum(1 for a in accounts if a.status == DepositAccountStatus.ACTIVE),
        "total_interest_earned": float(total_interest_earned),
        "accounts": [
            {
                "account_number": acc.account_number,
                "deposit_type": acc.deposit_type,
                "principal_amount": float(acc.principal_amount),
                "interest_rate": float(acc.interest_rate),
                "maturity_date": acc.maturity_date.isoformat(),
                "status": acc.status
            }
            for acc in accounts
        ],
        "ai_insights": ai_insights
    }


@router.get("/analytics/trends")
def get_deposit_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Deposit growth trends"""
    
    cutoff_date = date.today() - timedelta(days=days)
    
    accounts = db.query(DepositAccount).filter(
        DepositAccount.open_date >= cutoff_date
    ).order_by(DepositAccount.open_date).all()
    
    # Daily aggregation
    daily_data = {}
    
    for acc in accounts:
        day_key = acc.open_date.isoformat()
        
        if day_key not in daily_data:
            daily_data[day_key] = {
                "date": day_key,
                "count": 0,
                "amount": Decimal('0')
            }
        
        daily_data[day_key]["count"] += 1
        daily_data[day_key]["amount"] += acc.principal_amount
    
    trend_data = [
        {
            "date": v["date"],
            "count": v["count"],
            "amount": float(v["amount"])
        }
        for v in sorted(daily_data.values(), key=lambda x: x["date"])
    ]
    
    return {
        "period_days": days,
        "total_new_accounts": len(accounts),
        "total_new_deposits": float(sum(acc.principal_amount for acc in accounts)),
        "trends": trend_data
    }
