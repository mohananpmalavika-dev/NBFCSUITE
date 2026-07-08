"""
Payroll API Router
FastAPI endpoints for payroll management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.services.payroll.schemas import (
    SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse, SalaryComponentListResponse,
    PayrollRunCreate, PayrollRunResponse, PayrollRunListResponse,
    PayrollRunProcessRequest, PayrollRunApproveRequest,
    PayslipListResponse, PayslipResponse,
    PayrollDashboardStats, PayrollSummary,
    ComponentType, PayrollStatus
)
from backend.services.payroll.salary_component_service import SalaryComponentService
from backend.services.payroll.payroll_processing_service import PayrollProcessingService
from backend.shared.database.payroll_models import PayrollRun, Payslip
from sqlalchemy import and_

router = APIRouter(prefix="/payroll", tags=["Payroll Management"])

# Dependency to get DB session (simplified - adjust based on your setup)
def get_db():
    # TODO: Implement your database session management
    pass

# Dependency to get current user and tenant (simplified)
def get_current_user():
    # TODO: Implement your authentication
    return {"id": 1, "tenant_id": 1}


# ============ Salary Component Endpoints ============

@router.post("/components", response_model=SalaryComponentResponse)
async def create_salary_component(
    component: SalaryComponentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new salary component"""
    try:
        result = await SalaryComponentService.create_component(
            db, component, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/components", response_model=SalaryComponentListResponse)
async def list_salary_components(
    component_type: Optional[ComponentType] = None,
    is_active: Optional[bool] = None,
    is_statutory: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List salary components with filters"""
    return await SalaryComponentService.list_components(
        db, current_user["tenant_id"], component_type,
        is_active, is_statutory, search, page, page_size
    )


@router.get("/components/{component_id}", response_model=SalaryComponentResponse)
async def get_salary_component(
    component_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a salary component by ID"""
    result = await SalaryComponentService.get_component(
        db, component_id, current_user["tenant_id"]
    )
    if not result:
        raise HTTPException(status_code=404, detail="Component not found")
    return result


@router.put("/components/{component_id}", response_model=SalaryComponentResponse)
async def update_salary_component(
    component_id: int,
    component: SalaryComponentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a salary component"""
    try:
        result = await SalaryComponentService.update_component(
            db, component_id, current_user["tenant_id"], 
            component, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Component not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/components/{component_id}")
async def delete_salary_component(
    component_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a salary component"""
    try:
        success = await SalaryComponentService.delete_component(
            db, component_id, current_user["tenant_id"], current_user["id"]
        )
        if not success:
            raise HTTPException(status_code=404, detail="Component not found")
        return {"message": "Component deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# ============ Payroll Run Endpoints ============

@router.post("/runs", response_model=PayrollRunResponse)
async def create_payroll_run(
    run_data: PayrollRunCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new payroll run"""
    try:
        result = await PayrollProcessingService.create_payroll_run(
            db, run_data, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs", response_model=PayrollRunListResponse)
async def list_payroll_runs(
    status: Optional[PayrollStatus] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List payroll runs with filters"""
    query = db.query(PayrollRun).filter(
        and_(
            PayrollRun.tenant_id == current_user["tenant_id"],
            PayrollRun.is_deleted == False
        )
    )
    
    if status:
        query = query.filter(PayrollRun.status == status)
    if year:
        query = query.filter(PayrollRun.payroll_year == year)
    if month:
        query = query.filter(PayrollRun.payroll_month == month)
    
    total = query.count()
    runs = query.order_by(PayrollRun.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PayrollRunListResponse(
        items=runs,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/runs/{run_id}", response_model=PayrollRunResponse)
async def get_payroll_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a payroll run by ID"""
    run = db.query(PayrollRun).filter(
        and_(
            PayrollRun.id == run_id,
            PayrollRun.tenant_id == current_user["tenant_id"],
            PayrollRun.is_deleted == False
        )
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    return run


@router.post("/runs/{run_id}/process")
async def process_payroll_run(
    run_id: int,
    request: PayrollRunProcessRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process payroll for a run"""
    try:
        result = await PayrollProcessingService.process_payroll(
            db, run_id, current_user["tenant_id"],
            request.employee_ids, current_user["id"]
        )
        return {"message": "Payroll processed successfully", "run": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/runs/{run_id}/approve")
async def approve_payroll_run(
    run_id: int,
    request: PayrollRunApproveRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve a payroll run"""
    try:
        result = await PayrollProcessingService.approve_payroll(
            db, run_id, current_user["tenant_id"],
            current_user["id"], request.approval_remarks
        )
        return {"message": "Payroll approved successfully", "run": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ Payslip Endpoints ============

@router.get("/payslips", response_model=PayslipListResponse)
async def list_payslips(
    run_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List payslips with filters"""
    query = db.query(Payslip).filter(
        and_(
            Payslip.tenant_id == current_user["tenant_id"],
            Payslip.is_deleted == False
        )
    )
    
    if run_id:
        query = query.filter(Payslip.payroll_run_id == run_id)
    if employee_id:
        query = query.filter(Payslip.employee_id == employee_id)
    if month:
        query = query.filter(Payslip.payroll_month == month)
    if year:
        query = query.filter(Payslip.payroll_year == year)
    
    total = query.count()
    payslips = query.order_by(Payslip.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return PayslipListResponse(
        items=payslips,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/payslips/{payslip_id}", response_model=PayslipResponse)
async def get_payslip(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a payslip by ID"""
    payslip = db.query(Payslip).filter(
        and_(
            Payslip.id == payslip_id,
            Payslip.tenant_id == current_user["tenant_id"],
            Payslip.is_deleted == False
        )
    ).first()
    
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    return payslip


@router.get("/payslips/{payslip_id}/download")
async def download_payslip(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download payslip PDF"""
    payslip = db.query(Payslip).filter(
        and_(
            Payslip.id == payslip_id,
            Payslip.tenant_id == current_user["tenant_id"],
            Payslip.is_deleted == False
        )
    ).first()
    
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    
    # TODO: Implement PDF generation
    return {"message": "PDF generation not implemented", "payslip_pdf_url": payslip.payslip_pdf_url}


# ============ Dashboard & Reports Endpoints ============

@router.get("/dashboard/stats", response_model=PayrollDashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get payroll dashboard statistics"""
    from datetime import datetime
    from sqlalchemy import func
    from backend.shared.database.payroll_models import (
        SalaryStructure, EmployeeSalary, StatutoryCompliance, Form16, PaymentFile
    )
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Total employees with active salary
    total_employees = db.query(func.count(EmployeeSalary.id)).filter(
        and_(
            EmployeeSalary.tenant_id == current_user["tenant_id"],
            EmployeeSalary.is_active == True,
            EmployeeSalary.is_deleted == False
        )
    ).scalar() or 0
    
    # Active salary structures
    active_structures = db.query(func.count(SalaryStructure.id)).filter(
        and_(
            SalaryStructure.tenant_id == current_user["tenant_id"],
            SalaryStructure.is_active == True,
            SalaryStructure.is_deleted == False
        )
    ).scalar() or 0
    
    # Pending payroll runs
    pending_runs = db.query(func.count(PayrollRun.id)).filter(
        and_(
            PayrollRun.tenant_id == current_user["tenant_id"],
            PayrollRun.status.in_([PayrollStatus.DRAFT, PayrollStatus.IN_PROGRESS]),
            PayrollRun.is_deleted == False
        )
    ).scalar() or 0
    
    # Check if current month processed
    current_month_run = db.query(PayrollRun).filter(
        and_(
            PayrollRun.tenant_id == current_user["tenant_id"],
            PayrollRun.payroll_month == current_month,
            PayrollRun.payroll_year == current_year,
            PayrollRun.status == PayrollStatus.COMPLETED,
            PayrollRun.is_deleted == False
        )
    ).first()
    
    current_month_processed = current_month_run is not None
    
    # Total payroll this month
    total_payroll = 0
    if current_month_run:
        total_payroll = current_month_run.total_net_pay
    
    # Pending statutory payments
    pending_statutory = db.query(func.sum(StatutoryCompliance.total_amount)).filter(
        and_(
            StatutoryCompliance.tenant_id == current_user["tenant_id"],
            StatutoryCompliance.is_paid == False,
            StatutoryCompliance.is_deleted == False
        )
    ).scalar() or 0
    
    # Pending Form 16
    pending_form16 = db.query(func.count(Form16.id)).filter(
        and_(
            Form16.tenant_id == current_user["tenant_id"],
            Form16.is_issued == False,
            Form16.is_deleted == False
        )
    ).scalar() or 0
    
    # Pending payment files
    pending_payments = db.query(func.count(PaymentFile.id)).filter(
        and_(
            PaymentFile.tenant_id == current_user["tenant_id"],
            PaymentFile.uploaded_to_bank == False,
            PaymentFile.is_deleted == False
        )
    ).scalar() or 0
    
    return PayrollDashboardStats(
        total_employees=total_employees,
        active_salary_structures=active_structures,
        pending_payroll_runs=pending_runs,
        current_month_processed=current_month_processed,
        total_payroll_this_month=total_payroll,
        total_statutory_pending=pending_statutory,
        pending_form16_count=pending_form16,
        pending_payment_files=pending_payments
    )


@router.get("/summary/{year}/{month}", response_model=PayrollSummary)
async def get_payroll_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get payroll summary for a specific month"""
    result = await PayrollProcessingService.get_payroll_summary(
        db, current_user["tenant_id"], month, year
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="No payroll data found for the specified month")
    
    return result
