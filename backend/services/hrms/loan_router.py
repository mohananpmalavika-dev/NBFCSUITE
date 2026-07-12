"""
HRMS Loan & Advances API Routes
FastAPI endpoints for loan management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_current_active_user
from backend.shared.models.user import User
from .loan_service import LoanService
from .loan_schemas import (
    LoanApplicationCreate, LoanApplicationUpdate, LoanApprovalAction,
    LoanDisbursementRequest, LoanEligibilityRequest, LoanEligibilityResponse,
    EMICalculationRequest, EMICalculationResponse, LoanResponse,
    LoanListItem, EMIScheduleResponse, LoanTransactionCreate,
    LoanClosureRequest, EmployeeLoanSummary, LoanDashboardStats,
    LoanApprovalListItem
)

router = APIRouter(prefix="/api/v1/hrms/loans", tags=["HRMS - Loans & Advances"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_loan_service(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> LoanService:
    """Get loan service instance"""
    # Assuming employee_id is stored in user context or fetch from employee table
    employee_id = getattr(current_user, 'employee_id', None)
    return LoanService(db, current_user.tenant_id, str(current_user.id), employee_id)


# ============================================================================
# ELIGIBILITY & CALCULATION
# ============================================================================

@router.post("/check-eligibility", response_model=LoanEligibilityResponse)
async def check_loan_eligibility(
    request: LoanEligibilityRequest,
    service: LoanService = Depends(get_loan_service)
):
    """Check loan eligibility for employee"""
    try:
        return await service.check_eligibility(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculate-emi", response_model=EMICalculationResponse)
async def calculate_emi(request: EMICalculationRequest):
    """Calculate EMI for given loan parameters"""
    try:
        emi, total_interest, total_amount = LoanService.calculate_emi(
            request.principal_amount,
            request.interest_rate,
            request.tenure_months
        )
        
        return EMICalculationResponse(
            emi_amount=emi,
            total_interest=total_interest,
            total_repayment_amount=total_amount,
            monthly_emi=emi,
            effective_rate=request.interest_rate
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============================================================================
# LOAN APPLICATION (EMPLOYEE SELF-SERVICE)
# ============================================================================

@router.post("/applications", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_application(
    data: LoanApplicationCreate,
    service: LoanService = Depends(get_loan_service)
):
    """Create new loan application"""
    try:
        loan = await service.create_loan_application(data)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications", response_model=dict)
async def get_my_loan_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: LoanService = Depends(get_loan_service)
):
    """Get employee's loan applications"""
    try:
        from backend.shared.database.loan_models import LoanStatus
        
        status_enum = None
        if status_filter:
            try:
                status_enum = LoanStatus(status_filter)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
        
        loans, total = await service.get_employee_loans(status_enum, page, page_size)
        
        return {
            "items": loans,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications/{loan_id}", response_model=LoanResponse)
async def get_loan_application(
    loan_id: str,
    service: LoanService = Depends(get_loan_service)
):
    """Get loan application details"""
    try:
        loan = await service.get_loan_by_id(loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/applications/{loan_id}", response_model=LoanResponse)
async def update_loan_application(
    loan_id: str,
    data: LoanApplicationUpdate,
    service: LoanService = Depends(get_loan_service)
):
    """Update draft loan application"""
    try:
        loan = await service.update_loan_application(loan_id, data)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{loan_id}/submit", response_model=LoanResponse)
async def submit_loan_application(
    loan_id: str,
    service: LoanService = Depends(get_loan_service)
):
    """Submit loan application for approval"""
    try:
        loan = await service.submit_loan_application(loan_id)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{loan_id}/cancel", response_model=LoanResponse)
async def cancel_loan_application(
    loan_id: str,
    service: LoanService = Depends(get_loan_service)
):
    """Cancel loan application"""
    try:
        loan = await service.cancel_loan_application(loan_id)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# LOAN APPROVAL WORKFLOW
# ============================================================================

@router.post("/approvals/{loan_id}/manager", response_model=LoanResponse)
async def manager_approval(
    loan_id: str,
    action: LoanApprovalAction,
    service: LoanService = Depends(get_loan_service)
):
    """Manager approval/rejection"""
    try:
        loan = await service.approve_by_manager(loan_id, action)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{loan_id}/hr", response_model=LoanResponse)
async def hr_approval(
    loan_id: str,
    action: LoanApprovalAction,
    service: LoanService = Depends(get_loan_service)
):
    """HR approval/rejection"""
    try:
        loan = await service.approve_by_hr(loan_id, action)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approvals/{loan_id}/finance", response_model=LoanResponse)
async def finance_approval(
    loan_id: str,
    action: LoanApprovalAction,
    service: LoanService = Depends(get_loan_service)
):
    """Finance approval/rejection (final)"""
    try:
        loan = await service.approve_by_finance(loan_id, action)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LOAN DISBURSEMENT
# ============================================================================

@router.post("/disbursements/{loan_id}", response_model=LoanResponse)
async def disburse_loan(
    loan_id: str,
    data: LoanDisbursementRequest,
    service: LoanService = Depends(get_loan_service)
):
    """Disburse approved loan"""
    try:
        loan = await service.disburse_loan(loan_id, data)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EMI SCHEDULE & TRACKING
# ============================================================================

@router.get("/applications/{loan_id}/emi-schedule", response_model=EMIScheduleResponse)
async def get_emi_schedule(
    loan_id: str,
    service: LoanService = Depends(get_loan_service)
):
    """Get EMI schedule for a loan"""
    try:
        loan = await service.get_loan_by_id(loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        schedule = await service.get_emi_schedule(loan_id)
        
        from .loan_schemas import EMIScheduleItem, EMIStatusEnum
        
        schedule_items = [
            EMIScheduleItem(
                emi_number=emi.emi_number,
                emi_due_date=emi.emi_due_date,
                emi_amount=emi.emi_amount,
                principal_component=emi.principal_component,
                interest_component=emi.interest_component,
                opening_balance=emi.opening_principal_balance,
                closing_balance=emi.closing_principal_balance,
                status=EMIStatusEnum(emi.status.value),
                payment_date=emi.payment_date,
                amount_paid=emi.amount_paid,
                is_overdue=emi.is_overdue,
                days_overdue=emi.days_overdue
            )
            for emi in schedule
        ]
        
        paid_count = len([s for s in schedule if s.status.value == "paid"])
        pending_count = len([s for s in schedule if s.status.value == "pending"])
        overdue_count = len([s for s in schedule if s.is_overdue])
        
        return EMIScheduleResponse(
            loan_id=str(loan.id),
            loan_code=loan.loan_code,
            total_emis=len(schedule),
            schedule=schedule_items,
            total_principal=loan.loan_amount,
            total_interest=loan.total_interest,
            total_amount=loan.total_repayment_amount,
            paid_emis=paid_count,
            pending_emis=pending_count,
            overdue_emis=overdue_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# LOAN CLOSURE & SETTLEMENT
# ============================================================================

@router.post("/applications/{loan_id}/foreclose", response_model=LoanResponse)
async def foreclose_loan(
    loan_id: str,
    data: LoanClosureRequest,
    service: LoanService = Depends(get_loan_service)
):
    """Foreclose loan (early settlement)"""
    try:
        loan = await service.foreclose_loan(loan_id, data)
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EMPLOYEE DASHBOARD
# ============================================================================

@router.get("/my-summary", response_model=EmployeeLoanSummary)
async def get_my_loan_summary(
    service: LoanService = Depends(get_loan_service)
):
    """Get employee's loan summary"""
    try:
        return await service.get_employee_loan_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMIN/HR ROUTES
# ============================================================================

@router.get("/all", response_model=dict)
async def get_all_loans(
    status_filter: Optional[str] = Query(None, alias="status"),
    loan_type: Optional[str] = Query(None),
    employee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all loans (admin/HR view)"""
    try:
        from sqlalchemy import select, and_, desc, func
        from backend.shared.database.loan_models import EmployeeLoan, LoanStatus
        
        query = select(EmployeeLoan).where(
            and_(
                EmployeeLoan.tenant_id == current_user.tenant_id,
                EmployeeLoan.is_deleted == False
            )
        )
        
        if status_filter:
            try:
                status_enum = LoanStatus(status_filter)
                query = query.where(EmployeeLoan.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
        
        if employee_id:
            query = query.where(EmployeeLoan.employee_id == employee_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(desc(EmployeeLoan.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        loans = result.scalars().all()
        
        return {
            "items": loans,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard-stats", response_model=LoanDashboardStats)
async def get_loan_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get loan dashboard statistics"""
    try:
        from sqlalchemy import select, func, and_
        from backend.shared.database.loan_models import EmployeeLoan, LoanStatus
        from decimal import Decimal
        
        # Active loans count and amounts
        active_query = select(
            func.count(EmployeeLoan.id),
            func.sum(EmployeeLoan.disbursed_amount),
            func.sum(EmployeeLoan.total_outstanding),
            func.sum(EmployeeLoan.total_paid)
        ).where(
            and_(
                EmployeeLoan.tenant_id == current_user.tenant_id,
                EmployeeLoan.status == LoanStatus.ACTIVE,
                EmployeeLoan.is_deleted == False
            )
        )
        
        result = await db.execute(active_query)
        active_count, disbursed_amt, outstanding_amt, collected_amt = result.first()
        
        # Pending approvals
        pending_query = select(func.count(EmployeeLoan.id)).where(
            and_(
                EmployeeLoan.tenant_id == current_user.tenant_id,
                EmployeeLoan.status == LoanStatus.PENDING_APPROVAL,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await db.execute(pending_query)
        pending_count = result.scalar()
        
        # Overdue loans
        overdue_query = select(
            func.count(EmployeeLoan.id),
            func.sum(EmployeeLoan.total_outstanding)
        ).where(
            and_(
                EmployeeLoan.tenant_id == current_user.tenant_id,
                EmployeeLoan.is_overdue == True,
                EmployeeLoan.is_deleted == False
            )
        )
        result = await db.execute(overdue_query)
        overdue_count, overdue_amt = result.first()
        
        return LoanDashboardStats(
            total_active_loans=active_count or 0,
            total_disbursed_amount=disbursed_amt or Decimal("0.00"),
            total_outstanding_amount=outstanding_amt or Decimal("0.00"),
            total_collected_amount=collected_amt or Decimal("0.00"),
            pending_approvals=pending_count or 0,
            overdue_loans=overdue_count or 0,
            total_overdue_amount=overdue_amt or Decimal("0.00"),
            loans_this_month=0,  # TODO: Calculate
            disbursements_this_month=Decimal("0.00"),  # TODO: Calculate
            collections_this_month=Decimal("0.00")  # TODO: Calculate
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
