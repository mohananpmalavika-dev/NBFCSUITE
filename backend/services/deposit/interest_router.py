"""
Interest Calculation Router

API endpoints for interest calculation and posting including:
- Interest calculation
- Interest posting
- Batch processing
- Interest certificates
- Interest history
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .interest_service import InterestCalculationService
from .schemas import (
    InterestCalculationRequest,
    InterestCalculationResponse,
    InterestPostRequest,
    InterestPostResponse,
    BatchInterestRequest,
    BatchInterestResponse,
    InterestCertificateRequest,
    InterestCertificateResponse,
    InterestHistoryResponse,
    DepositType
)

router = APIRouter(prefix="/deposit-interest", tags=["Deposit Interest"])


# ==================== INTEREST CALCULATION ====================

@router.post("/calculate", response_model=dict)
def calculate_interest(
    calc_request: InterestCalculationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate interest for account
    
    Calculates interest based on product configuration:
    - **Simple Interest**: For FD, MIS
    - **Compound Interest**: For FD with compounding
    - **Daily Balance**: For savings accounts
    - **Monthly Average**: For savings accounts
    
    TDS calculation included if applicable.
    
    Does NOT post to account - use /post endpoint for posting.
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.calculate_account_interest(
        account_id=calc_request.account_id,
        from_date=calc_request.from_date,
        to_date=calc_request.to_date
    )
    
    return success_response(
        message="Interest calculated successfully",
        data=result
    )


@router.post("/post", response_model=dict)
def post_interest(
    post_request: InterestPostRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate and post interest to account
    
    Process:
    1. Calculates interest for period
    2. Calculates TDS if applicable
    3. Creates interest transaction
    4. Creates TDS transaction (if applicable)
    5. Updates account balance
    6. Creates passbook entries
    7. Updates next interest date
    
    Returns:
    - Gross interest
    - TDS deducted
    - Net interest credited
    - New balance
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.post_interest(
        account_id=post_request.account_id,
        from_date=post_request.from_date,
        to_date=post_request.to_date
    )
    
    return success_response(
        message="Interest posted successfully",
        data=result
    )


# ==================== BATCH PROCESSING ====================

@router.post("/batch-calculate", response_model=dict)
def batch_calculate_interest(
    batch_request: BatchInterestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Batch calculate and post interest for multiple accounts
    
    Processes all accounts due for interest posting:
    - Filters by account type (optional)
    - Filters by product (optional)
    - Only processes accounts with next_interest_date <= today
    
    Returns:
    - Total accounts processed
    - Successful count
    - Failed count
    - Total interest posted
    - Total TDS deducted
    - Error details for failed accounts
    
    Use for automated interest posting (daily/monthly jobs)
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.batch_calculate_interest(
        account_type=batch_request.account_type,
        product_id=batch_request.product_id
    )
    
    return success_response(
        message=f"Batch processing completed: {result['successful']} successful, {result['failed']} failed",
        data=result
    )


@router.post("/batch-calculate-by-type", response_model=dict)
def batch_calculate_by_type(
    account_type: DepositType = Query(..., description="Account type to process"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Batch calculate interest for specific account type
    
    Convenience endpoint for processing by type:
    - savings: Daily or monthly interest
    - fd: Quarterly or maturity interest
    - rd: Quarterly interest
    - mis: Monthly interest payout
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.batch_calculate_interest(account_type=account_type)
    
    return success_response(
        message=f"Batch processing for {account_type} completed",
        data=result
    )


# ==================== INTEREST HISTORY ====================

@router.get("/{account_id}/history", response_model=dict)
def get_interest_history(
    account_id: int,
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get interest calculation history
    
    Returns all posted interest calculations with:
    - Calculation period
    - Interest amount
    - TDS amount
    - Net interest
    - Calculation method
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    history = service.get_interest_history(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(history)} interest calculations",
        data={
            "history": history,
            "total": len(history),
            "skip": skip,
            "limit": limit
        }
    )


# ==================== INTEREST CERTIFICATE ====================

@router.post("/certificate", response_model=dict)
def generate_interest_certificate(
    cert_request: InterestCertificateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Generate interest certificate for financial year
    
    Financial Year: April 1 to March 31
    
    Certificate includes:
    - Account details
    - Financial year period
    - Total interest earned
    - Total TDS deducted
    - Net interest
    - Detailed breakdown by period
    
    Used for:
    - Tax filing (Form 26AS)
    - Income proof
    - Audit purposes
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    certificate = service.generate_interest_certificate(
        account_id=cert_request.account_id,
        financial_year=cert_request.financial_year
    )
    
    return success_response(
        message="Interest certificate generated successfully",
        data=certificate
    )


@router.get("/certificate/{account_id}", response_model=dict)
def get_interest_certificate(
    account_id: int,
    financial_year: Optional[str] = Query(None, pattern="^\\d{4}-\\d{4}$", description="FY (e.g., 2025-2026)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get interest certificate (alternative endpoint using GET)
    
    If financial_year not provided, uses current FY
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    certificate = service.generate_interest_certificate(
        account_id=account_id,
        financial_year=financial_year
    )
    
    return success_response(
        message="Interest certificate retrieved successfully",
        data=certificate
    )


# ==================== CALCULATION METHODS ====================

@router.post("/calculate-simple", response_model=dict)
def calculate_simple_interest(
    principal: float = Query(..., gt=0, description="Principal amount"),
    rate: float = Query(..., ge=0, le=100, description="Annual interest rate (%)"),
    from_date: date = Query(..., description="From date"),
    to_date: date = Query(..., description="To date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate simple interest
    
    Formula: Interest = Principal × Rate × Days / (100 × 365)
    
    Generic calculator - not tied to any account
    """
    from decimal import Decimal
    
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.calculate_simple_interest(
        Decimal(str(principal)),
        Decimal(str(rate)),
        from_date,
        to_date
    )
    
    return success_response(
        message="Simple interest calculated",
        data=result
    )


@router.post("/calculate-compound", response_model=dict)
def calculate_compound_interest(
    principal: float = Query(..., gt=0, description="Principal amount"),
    rate: float = Query(..., ge=0, le=100, description="Annual interest rate (%)"),
    from_date: date = Query(..., description="From date"),
    to_date: date = Query(..., description="To date"),
    frequency: str = Query("quarterly", pattern="^(daily|monthly|quarterly|half_yearly|yearly)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate compound interest
    
    Formula: A = P × (1 + r/n)^(n×t)
    
    Compounding frequencies:
    - daily (365 times/year)
    - monthly (12 times/year)
    - quarterly (4 times/year)
    - half_yearly (2 times/year)
    - yearly (1 time/year)
    """
    from decimal import Decimal
    
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.calculate_compound_interest(
        Decimal(str(principal)),
        Decimal(str(rate)),
        from_date,
        to_date,
        frequency
    )
    
    return success_response(
        message="Compound interest calculated",
        data=result
    )


@router.post("/calculate-daily-balance", response_model=dict)
def calculate_daily_balance_interest(
    account_id: int = Query(..., gt=0, description="Account ID"),
    from_date: date = Query(..., description="From date"),
    to_date: date = Query(..., description="To date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate interest using daily balance method
    
    Formula: Interest = Σ(Daily Balance × Rate × 1 / 36500)
    
    Used for savings accounts with frequent transactions.
    Tracks balance changes daily and calculates interest accordingly.
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.calculate_daily_balance_interest(
        account_id,
        from_date,
        to_date
    )
    
    return success_response(
        message="Daily balance interest calculated",
        data=result
    )


@router.post("/calculate-monthly-average", response_model=dict)
def calculate_monthly_average_interest(
    account_id: int = Query(..., gt=0, description="Account ID"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate interest using monthly average balance
    
    Formula:
    Average Balance = Sum of Daily Balances / Days in Month
    Interest = Average Balance × Rate × Days / (100 × 365)
    
    Used for savings accounts.
    """
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    result = service.calculate_monthly_average_balance_interest(
        account_id,
        month,
        year
    )
    
    return success_response(
        message="Monthly average balance interest calculated",
        data=result
    )


# ==================== TDS INFORMATION ====================

@router.get("/{account_id}/tds-summary", response_model=dict)
def get_tds_summary(
    account_id: int,
    financial_year: Optional[str] = Query(None, pattern="^\\d{4}-\\d{4}$", description="FY (e.g., 2025-2026)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get TDS summary for account
    
    Returns:
    - Total interest earned in FY
    - Total TDS deducted
    - TDS rate applied
    - TDS threshold
    - Quarter-wise breakdown
    
    Useful for Form 26AS reconciliation
    """
    from backend.shared.database.deposit_models import DepositInterestCalculation
    from sqlalchemy import and_, func
    
    service = InterestCalculationService(db, tenant_id, current_user["id"])
    account = service._get_account(account_id)
    
    # Determine financial year
    if not financial_year:
        today = date.today()
        if today.month >= 4:
            fy_start_year = today.year
        else:
            fy_start_year = today.year - 1
        financial_year = f"{fy_start_year}-{fy_start_year + 1}"
    
    # Parse FY
    fy_parts = financial_year.split('-')
    fy_start = date(int(fy_parts[0]), 4, 1)
    fy_end = date(int(fy_parts[1]), 3, 31)
    
    # Get TDS summary
    calculations = db.query(DepositInterestCalculation).filter(
        and_(
            DepositInterestCalculation.deposit_account_id == account_id,
            DepositInterestCalculation.posted == True,
            DepositInterestCalculation.calculation_period_end >= fy_start,
            DepositInterestCalculation.calculation_period_end <= fy_end
        )
    ).all()
    
    total_interest = sum(float(c.interest_amount) for c in calculations)
    total_tds = sum(float(c.tds_amount) for c in calculations)
    
    # Quarter-wise breakdown
    quarters = {
        "Q1 (Apr-Jun)": {"interest": 0.0, "tds": 0.0},
        "Q2 (Jul-Sep)": {"interest": 0.0, "tds": 0.0},
        "Q3 (Oct-Dec)": {"interest": 0.0, "tds": 0.0},
        "Q4 (Jan-Mar)": {"interest": 0.0, "tds": 0.0}
    }
    
    for calc in calculations:
        month = calc.calculation_period_end.month
        if month in [4, 5, 6]:
            quarter = "Q1 (Apr-Jun)"
        elif month in [7, 8, 9]:
            quarter = "Q2 (Jul-Sep)"
        elif month in [10, 11, 12]:
            quarter = "Q3 (Oct-Dec)"
        else:
            quarter = "Q4 (Jan-Mar)"
        
        quarters[quarter]["interest"] += float(calc.interest_amount)
        quarters[quarter]["tds"] += float(calc.tds_amount)
    
    summary = {
        "account_number": account.account_number,
        "financial_year": financial_year,
        "total_interest": total_interest,
        "total_tds": total_tds,
        "net_interest": total_interest - total_tds,
        "tds_rate": float(account.product.tds_rate),
        "tds_threshold": float(account.product.tds_threshold),
        "quarters": quarters,
        "pan_required": total_interest > float(account.product.tds_threshold)
    }
    
    return success_response(
        message="TDS summary retrieved successfully",
        data=summary
    )


# ==================== STATISTICS ====================

@router.get("/statistics", response_model=dict)
def get_interest_statistics(
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    account_type: Optional[DepositType] = Query(None, description="Filter by account type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get interest statistics across all accounts
    
    Returns:
    - Total interest posted
    - Total TDS deducted
    - Account type breakdown
    - Product-wise breakdown
    
    Useful for financial reporting and analytics
    """
    from backend.shared.database.deposit_models import (
        DepositInterestCalculation, DepositAccount
    )
    from sqlalchemy import and_, func
    
    query = db.query(DepositInterestCalculation).join(
        DepositAccount,
        DepositInterestCalculation.deposit_account_id == DepositAccount.id
    ).filter(
        and_(
            DepositInterestCalculation.tenant_id == tenant_id,
            DepositInterestCalculation.posted == True
        )
    )
    
    if from_date:
        query = query.filter(DepositInterestCalculation.calculation_period_start >= from_date)
    
    if to_date:
        query = query.filter(DepositInterestCalculation.calculation_period_end <= to_date)
    
    if account_type:
        query = query.filter(DepositAccount.account_type == account_type)
    
    calculations = query.all()
    
    total_interest = sum(float(c.interest_amount) for c in calculations)
    total_tds = sum(float(c.tds_amount) for c in calculations)
    net_interest = total_interest - total_tds
    
    # Account type breakdown
    type_breakdown = {}
    for calc in calculations:
        acc_type = calc.account.account_type
        if acc_type not in type_breakdown:
            type_breakdown[acc_type] = {"interest": 0.0, "tds": 0.0, "count": 0}
        
        type_breakdown[acc_type]["interest"] += float(calc.interest_amount)
        type_breakdown[acc_type]["tds"] += float(calc.tds_amount)
        type_breakdown[acc_type]["count"] += 1
    
    statistics = {
        "total_calculations": len(calculations),
        "total_interest": total_interest,
        "total_tds": total_tds,
        "net_interest": net_interest,
        "type_breakdown": type_breakdown,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None
    }
    
    return success_response(
        message="Interest statistics retrieved successfully",
        data=statistics
    )
