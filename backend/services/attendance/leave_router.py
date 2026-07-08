"""
Leave Management Router
FastAPI endpoints for leave policies, applications, and balance
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.dependencies.auth import get_current_user, get_tenant_id
from .leave_service import LeavePolicyService, LeaveBalanceService, LeaveApplicationService
from .schemas import (
    LeavePolicyCreate, LeavePolicyUpdate, LeavePolicyResponse, LeavePolicyListResponse,
    LeaveBalanceResponse, EmployeeLeaveBalanceSummary,
    LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationResponse,
    LeaveApplicationListResponse, LeaveApprovalAction, LeaveCancellationRequest,
    LeaveDashboardStats, LeaveEncashmentRequest, LeaveEncashmentResponse
)


router = APIRouter()


def get_policy_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get leave policy service instance"""
    return LeavePolicyService(db, tenant_id, user_id)


def get_balance_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get leave balance service instance"""
    return LeaveBalanceService(db, tenant_id, user_id)


def get_application_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get leave application service instance"""
    return LeaveApplicationService(db, tenant_id, user_id)


# ============================================================================
# LEAVE POLICY ENDPOINTS
# ============================================================================

@router.post("/policies", response_model=LeavePolicyResponse, status_code=201)
async def create_policy(
    data: LeavePolicyCreate,
    service: LeavePolicyService = Depends(get_policy_service)
):
    """Create new leave policy"""
    try:
        policy = await service.create_policy(data)
        return policy
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policies", response_model=LeavePolicyListResponse)
async def get_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    leave_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: LeavePolicyService = Depends(get_policy_service)
):
    """Get paginated list of leave policies"""
    try:
        policies, total = await service.get_policies(
            page=page,
            page_size=page_size,
            search=search,
            leave_type=leave_type,
            is_active=is_active
        )
        
        return {
            "items": policies,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policies/{policy_id}", response_model=LeavePolicyResponse)
async def get_policy(
    policy_id: str,
    service: LeavePolicyService = Depends(get_policy_service)
):
    """Get leave policy by ID"""
    policy = await service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Leave policy not found")
    return policy


@router.put("/policies/{policy_id}", response_model=LeavePolicyResponse)
async def update_policy(
    policy_id: str,
    data: LeavePolicyUpdate,
    service: LeavePolicyService = Depends(get_policy_service)
):
    """Update leave policy"""
    try:
        policy = await service.update_policy(policy_id, data)
        return policy
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/policies/{policy_id}", status_code=204)
async def delete_policy(
    policy_id: str,
    service: LeavePolicyService = Depends(get_policy_service)
):
    """Delete leave policy (soft delete)"""
    try:
        await service.delete_policy(policy_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# LEAVE BALANCE ENDPOINTS
# ============================================================================

@router.get("/balance/{employee_id}/{financial_year}", response_model=EmployeeLeaveBalanceSummary)
async def get_employee_balance(
    employee_id: str,
    financial_year: str,
    service: LeaveBalanceService = Depends(get_balance_service)
):
    """Get employee's leave balance for financial year"""
    try:
        balances = await service.get_employee_balance(employee_id, financial_year)
        return {
            "employee_id": employee_id,
            "financial_year": financial_year,
            "balances": balances
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/balance/initialize")
async def initialize_balance(
    employee_id: str = Query(...),
    policy_id: str = Query(...),
    financial_year: str = Query(...),
    service: LeaveBalanceService = Depends(get_balance_service)
):
    """Initialize leave balance for employee"""
    try:
        balance = await service.initialize_employee_balance(
            employee_id, policy_id, financial_year
        )
        return {
            "message": "Leave balance initialized successfully",
            "balance_id": balance.id,
            "current_balance": balance.current_balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/balance/accrue")
async def accrue_leave(
    employee_id: str = Query(...),
    leave_type: str = Query(...),
    financial_year: str = Query(...),
    accrual_amount: float = Query(..., ge=0),
    service: LeaveBalanceService = Depends(get_balance_service)
):
    """Accrue leave for employee"""
    try:
        from backend.shared.database.attendance_models import LeaveType
        balance = await service.accrue_leave(
            employee_id, LeaveType(leave_type), financial_year, accrual_amount
        )
        return {
            "message": "Leave accrued successfully",
            "current_balance": balance.current_balance,
            "accrued_amount": accrual_amount
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# LEAVE APPLICATION ENDPOINTS
# ============================================================================

@router.post("/applications", response_model=LeaveApplicationResponse, status_code=201)
async def create_application(
    data: LeaveApplicationCreate,
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Create new leave application"""
    try:
        application = await service.create_application(data)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications", response_model=LeaveApplicationListResponse)
async def get_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    leave_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Get paginated list of leave applications"""
    try:
        applications, total = await service.get_applications(
            page=page,
            page_size=page_size,
            employee_id=employee_id,
            status=status,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date
        )
        
        return {
            "items": applications,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/dashboard/stats", response_model=LeaveDashboardStats)
async def get_dashboard_stats(
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Get leave dashboard statistics"""
    try:
        stats = await service.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{application_id}", response_model=LeaveApplicationResponse)
async def get_application(
    application_id: str,
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Get leave application by ID"""
    application = await service.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Leave application not found")
    return application


@router.put("/applications/{application_id}", response_model=LeaveApplicationResponse)
async def update_application(
    application_id: str,
    data: LeaveApplicationUpdate,
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Update leave application (only in DRAFT status)"""
    try:
        application = await service.update_application(application_id, data)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/submit", response_model=LeaveApplicationResponse)
async def submit_application(
    application_id: str,
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Submit leave application for approval"""
    try:
        application = await service.submit_application(application_id)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/approve", response_model=LeaveApplicationResponse)
async def approve_application(
    application_id: str,
    action: LeaveApprovalAction,
    approver_level: str = Query(..., regex="^(REPORTING_MANAGER|HR|FINAL)$"),
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Approve leave application"""
    try:
        if action.action.upper() == "APPROVE":
            application = await service.approve_application(
                application_id, approver_level, action.remarks
            )
        elif action.action.upper() == "REJECT":
            application = await service.reject_application(
                application_id, action.remarks or "No reason provided"
            )
        else:
            raise ValueError("Invalid action. Must be APPROVE or REJECT")
        
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/cancel", response_model=LeaveApplicationResponse)
async def cancel_application(
    application_id: str,
    request: LeaveCancellationRequest,
    service: LeaveApplicationService = Depends(get_application_service)
):
    """Cancel leave application"""
    try:
        application = await service.cancel_application(
            application_id, request.cancellation_reason
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LEAVE ENCASHMENT ENDPOINTS (Future Enhancement)
# ============================================================================

@router.post("/encashment", response_model=LeaveEncashmentResponse, status_code=201)
async def request_encashment(
    data: LeaveEncashmentRequest,
    service: LeaveBalanceService = Depends(get_balance_service)
):
    """Request leave encashment"""
    # TODO: Implement leave encashment logic
    raise HTTPException(status_code=501, detail="Leave encashment feature coming soon")


@router.get("/encashment/{encashment_id}", response_model=LeaveEncashmentResponse)
async def get_encashment(
    encashment_id: str,
    service: LeaveBalanceService = Depends(get_balance_service)
):
    """Get leave encashment by ID"""
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Leave encashment feature coming soon")
