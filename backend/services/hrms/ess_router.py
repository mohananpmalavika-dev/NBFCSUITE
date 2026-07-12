"""
HRMS Employee Self-Service (ESS) Router
API endpoints for employee self-service features
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, require_employee
from backend.shared.schemas import SuccessResponse, ErrorResponse
from backend.shared.database.hrms_models import InvestmentDeclaration, ReimbursementClaim
from .ess_service import ESSService
from .ess_schemas import (
    PayslipDownloadRequest, PayslipResponse,
    LeaveBalanceResponse, LeaveApplicationCreate, LeaveApplicationUpdate,
    LeaveApplicationResponse, LeaveApplicationListItem, PaginatedLeaveApplicationResponse,
    InvestmentDeclarationCreate, InvestmentDeclarationUpdate,
    InvestmentDeclarationResponse, InvestmentDeclarationListItem, PaginatedInvestmentDeclarationResponse,
    ReimbursementClaimCreate, ReimbursementClaimUpdate,
    ReimbursementClaimResponse, ReimbursementClaimListItem, PaginatedReimbursementClaimResponse,
    EmployeeProfileUpdateRequest, EmployeeProfileResponse,
    ESSDashboardStats,
    LeaveStatusEnum, InvestmentStatusEnum, ReimbursementStatusEnum
)

router = APIRouter(prefix="/api/hrms/ess", tags=["HRMS - Employee Self Service"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_ess_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> ESSService:
    """Get ESS service instance"""
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")
    employee_id = current_user.get("employee_id")
    
    if not employee_id:
        raise HTTPException(status_code=403, detail="User is not linked to an employee record")
    
    return ESSService(db=db, tenant_id=tenant_id, user_id=user_id, employee_id=employee_id)


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=ESSDashboardStats)
async def get_ess_dashboard(
    service: ESSService = Depends(get_ess_service)
):
    """Get employee self-service dashboard statistics"""
    try:
        stats = await service.get_ess_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PAYSLIP ENDPOINTS
# ============================================================================

@router.get("/payslips", response_model=List[PayslipResponse])
async def get_my_payslips(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    service: ESSService = Depends(get_ess_service)
):
    """Get employee's payslips"""
    try:
        payslips, total = await service.get_employee_payslips(page=page, page_size=page_size)
        return payslips
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payslips/{month}/{year}", response_model=PayslipResponse)
async def get_payslip_by_month(
    month: int,
    year: int,
    service: ESSService = Depends(get_ess_service)
):
    """Get specific payslip by month and year"""
    try:
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Invalid month")
        
        payslip = await service.get_payslip_by_month_year(month=month, year=year)
        
        if not payslip:
            raise HTTPException(status_code=404, detail="Payslip not found for this month/year")
        
        return payslip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payslips/{payslip_id}/download")
async def download_payslip(
    payslip_id: str,
    service: ESSService = Depends(get_ess_service)
):
    """Download payslip as PDF"""
    try:
        pdf_buffer = await service.generate_payslip_pdf(payslip_id=payslip_id)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=payslip_{payslip_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LEAVE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/leave/balances", response_model=List[LeaveBalanceResponse])
async def get_leave_balances(
    financial_year: Optional[str] = None,
    service: ESSService = Depends(get_ess_service)
):
    """Get employee's leave balances"""
    try:
        balances = await service.get_leave_balances(financial_year=financial_year)
        return balances
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leave/applications", response_model=LeaveApplicationResponse, status_code=201)
async def create_leave_application(
    data: LeaveApplicationCreate,
    service: ESSService = Depends(get_ess_service)
):
    """Create new leave application"""
    try:
        application = await service.create_leave_application(data=data)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leave/applications/{application_id}/submit", response_model=LeaveApplicationResponse)
async def submit_leave_application(
    application_id: str,
    service: ESSService = Depends(get_ess_service)
):
    """Submit leave application for approval"""
    try:
        application = await service.submit_leave_application(application_id=application_id)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leave/applications", response_model=PaginatedLeaveApplicationResponse)
async def get_leave_applications(
    status: Optional[LeaveStatusEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ESSService = Depends(get_ess_service)
):
    """Get employee's leave applications"""
    try:
        applications, total = await service.get_leave_applications(
            status=status, page=page, page_size=page_size
        )
        
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": applications,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leave/applications/{application_id}/cancel", response_model=LeaveApplicationResponse)
async def cancel_leave_application(
    application_id: str,
    reason: str = Query(..., min_length=10),
    service: ESSService = Depends(get_ess_service)
):
    """Cancel leave application"""
    try:
        application = await service.cancel_leave_application(
            application_id=application_id, reason=reason
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INVESTMENT DECLARATION ENDPOINTS
# ============================================================================

@router.post("/investment/declarations", response_model=InvestmentDeclarationResponse, status_code=201)
async def create_investment_declaration(
    data: InvestmentDeclarationCreate,
    service: ESSService = Depends(get_ess_service)
):
    """Create new investment declaration"""
    try:
        declaration = await service.create_investment_declaration(data=data)
        return declaration
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investment/declarations/{declaration_id}/submit", response_model=InvestmentDeclarationResponse)
async def submit_investment_declaration(
    declaration_id: str,
    service: ESSService = Depends(get_ess_service)
):
    """Submit investment declaration"""
    try:
        declaration = await service.submit_investment_declaration(declaration_id=declaration_id)
        return declaration
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/investment/declarations", response_model=PaginatedInvestmentDeclarationResponse)
async def get_investment_declarations(
    financial_year: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ESSService = Depends(get_ess_service)
):
    """Get employee's investment declarations"""
    try:
        declarations, total = await service.get_investment_declarations(
            financial_year=financial_year, page=page, page_size=page_size
        )
        
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": declarations,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/investment/declarations/{declaration_id}", response_model=InvestmentDeclarationResponse)
async def get_investment_declaration(
    declaration_id: str,
    service: ESSService = Depends(get_ess_service)
):
    """Get specific investment declaration"""
    try:
        query = select(InvestmentDeclaration).where(
            and_(
                InvestmentDeclaration.id == declaration_id,
                InvestmentDeclaration.tenant_id == service.tenant_id,
                InvestmentDeclaration.employee_id == service.employee_id,
                InvestmentDeclaration.is_deleted == False
            )
        ).options(selectinload(InvestmentDeclaration.line_items))
        
        result = await service.db.execute(query)
        declaration = result.scalar_one_or_none()
        
        if not declaration:
            raise HTTPException(status_code=404, detail="Declaration not found")
        
        return declaration
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# REIMBURSEMENT CLAIM ENDPOINTS
# ============================================================================

@router.post("/reimbursement/claims", response_model=ReimbursementClaimResponse, status_code=201)
async def create_reimbursement_claim(
    data: ReimbursementClaimCreate,
    service: ESSService = Depends(get_ess_service)
):
    """Create new reimbursement claim"""
    try:
        claim = await service.create_reimbursement_claim(data=data)
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reimbursement/claims/{claim_id}/submit", response_model=ReimbursementClaimResponse)
async def submit_reimbursement_claim(
    claim_id: str,
    service: ESSService = Depends(get_ess_service)
):
    """Submit reimbursement claim for approval"""
    try:
        claim = await service.submit_reimbursement_claim(claim_id=claim_id)
        return claim
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reimbursement/claims", response_model=PaginatedReimbursementClaimResponse)
async def get_reimbursement_claims(
    status: Optional[ReimbursementStatusEnum] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ESSService = Depends(get_ess_service)
):
    """Get employee's reimbursement claims"""
    try:
        claims, total = await service.get_reimbursement_claims(
            status=status, page=page, page_size=page_size
        )
        
        pages = (total + page_size - 1) // page_size
        
        return {
            "items": claims,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reimbursement/claims/{claim_id}", response_model=ReimbursementClaimResponse)
async def get_reimbursement_claim(
    claim_id: str,
    service: ESSService = Depends(get_ess_service)
):
    """Get specific reimbursement claim"""
    try:
        query = select(ReimbursementClaim).where(
            and_(
                ReimbursementClaim.id == claim_id,
                ReimbursementClaim.tenant_id == service.tenant_id,
                ReimbursementClaim.employee_id == service.employee_id,
                ReimbursementClaim.is_deleted == False
            )
        ).options(selectinload(ReimbursementClaim.approver))
        
        result = await service.db.execute(query)
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        return claim
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@router.get("/profile", response_model=EmployeeProfileResponse)
async def get_my_profile(
    service: ESSService = Depends(get_ess_service)
):
    """Get employee profile"""
    try:
        employee = await service.get_employee_profile()
        return employee
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=EmployeeProfileResponse)
async def update_my_profile(
    data: EmployeeProfileUpdateRequest,
    service: ESSService = Depends(get_ess_service)
):
    """Update employee profile (limited fields)"""
    try:
        employee = await service.update_employee_profile(data=data)
        return employee
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
