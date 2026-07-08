"""
Payroll API Router
FastAPI endpoints for payroll management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.services.payroll.schemas import (
    SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse, SalaryComponentListResponse,
    SalaryStructureCreate, SalaryStructureUpdate, SalaryStructureResponse, SalaryStructureListResponse,
    EmployeeSalaryCreate, EmployeeSalaryUpdate, EmployeeSalaryResponse, EmployeeSalaryListResponse,
    PayrollRunCreate, PayrollRunResponse, PayrollRunListResponse,
    PayrollRunProcessRequest, PayrollRunApproveRequest,
    PayslipListResponse, PayslipResponse,
    PayrollDashboardStats, PayrollSummary,
    ComponentType, PayrollStatus, StatutoryType, PaymentStatus, PaymentMode
)
from backend.services.payroll.salary_component_service import SalaryComponentService
from backend.services.payroll.salary_structure_service import SalaryStructureService
from backend.services.payroll.employee_salary_service import EmployeeSalaryService
from backend.services.payroll.payroll_processing_service import PayrollProcessingService
from backend.services.payroll.statutory_compliance_service import StatutoryComplianceService
from backend.services.payroll.form16_service import Form16Service
from backend.services.payroll.payment_file_service import PaymentFileService
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



# ============ Salary Structure Endpoints ============

@router.post("/structures", response_model=SalaryStructureResponse)
async def create_salary_structure(
    structure: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new salary structure"""
    try:
        result = await SalaryStructureService.create_structure(
            db, current_user["tenant_id"], structure, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/structures", response_model=SalaryStructureListResponse)
async def list_salary_structures(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List salary structures with filters"""
    return await SalaryStructureService.list_structures(
        db, current_user["tenant_id"], is_active, search, page, page_size
    )


@router.get("/structures/{structure_id}", response_model=SalaryStructureResponse)
async def get_salary_structure(
    structure_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a salary structure by ID"""
    result = await SalaryStructureService.get_structure(
        db, current_user["tenant_id"], structure_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Salary structure not found")
    return result


@router.put("/structures/{structure_id}", response_model=SalaryStructureResponse)
async def update_salary_structure(
    structure_id: int,
    structure: SalaryStructureUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a salary structure"""
    try:
        result = await SalaryStructureService.update_structure(
            db, current_user["tenant_id"], structure_id, structure, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Salary structure not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/structures/{structure_id}")
async def delete_salary_structure(
    structure_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a salary structure"""
    success = await SalaryStructureService.delete_structure(
        db, current_user["tenant_id"], structure_id, current_user["id"]
    )
    if not success:
        raise HTTPException(status_code=404, detail="Salary structure not found or already in use")
    return {"message": "Salary structure deleted successfully"}


# ============ Employee Salary Endpoints ============

@router.post("/employee-salaries", response_model=EmployeeSalaryResponse)
async def assign_employee_salary(
    salary: EmployeeSalaryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Assign salary structure to an employee"""
    try:
        result = await EmployeeSalaryService.assign_salary(
            db, current_user["tenant_id"], salary, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/employee-salaries", response_model=EmployeeSalaryListResponse)
async def list_employee_salaries(
    employee_id: Optional[int] = None,
    structure_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List employee salary assignments with filters"""
    return await EmployeeSalaryService.list_employee_salaries(
        db, current_user["tenant_id"], employee_id, structure_id, 
        is_active, page, page_size
    )


@router.get("/employee-salaries/{salary_id}", response_model=EmployeeSalaryResponse)
async def get_employee_salary(
    salary_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get an employee salary assignment by ID"""
    result = await EmployeeSalaryService.get_employee_salary(
        db, current_user["tenant_id"], salary_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Employee salary not found")
    return result


@router.get("/employees/{employee_id}/salary", response_model=EmployeeSalaryResponse)
async def get_employee_current_salary(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current active salary for an employee"""
    result = await EmployeeSalaryService.get_employee_active_salary(
        db, current_user["tenant_id"], employee_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="No active salary found for employee")
    return result


@router.put("/employee-salaries/{salary_id}", response_model=EmployeeSalaryResponse)
async def update_employee_salary(
    salary_id: int,
    salary: EmployeeSalaryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update employee salary assignment"""
    try:
        result = await EmployeeSalaryService.update_employee_salary(
            db, current_user["tenant_id"], salary_id, salary, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Employee salary not found")
        return result
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
        SalaryStructure, EmployeeSalary
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


# ============ Statutory Compliance Endpoints ============

@router.post("/compliance", response_model=StatutoryComplianceResponse)
async def create_statutory_compliance(
    compliance: StatutoryComplianceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new statutory compliance record"""
    try:
        result = await StatutoryComplianceService.create_compliance(
            db, current_user["tenant_id"], compliance, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compliance", response_model=StatutoryComplianceList)
async def list_statutory_compliance(
    statutory_type: Optional[StatutoryType] = None,
    payment_status: Optional[PaymentStatus] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    payroll_run_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List statutory compliance records with filters"""
    return await StatutoryComplianceService.list_compliance(
        db, current_user["tenant_id"], statutory_type, payment_status,
        month, year, payroll_run_id, page, page_size
    )


@router.get("/compliance/{compliance_id}", response_model=StatutoryComplianceResponse)
async def get_statutory_compliance(
    compliance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a statutory compliance record by ID"""
    result = await StatutoryComplianceService.get_compliance(
        db, current_user["tenant_id"], compliance_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Compliance record not found")
    return result


@router.put("/compliance/{compliance_id}", response_model=StatutoryComplianceResponse)
async def update_statutory_compliance(
    compliance_id: int,
    compliance: StatutoryComplianceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update statutory compliance record"""
    try:
        result = await StatutoryComplianceService.update_compliance(
            db, current_user["tenant_id"], compliance_id, compliance, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Compliance record not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/compliance/{compliance_id}/payment")
async def update_compliance_payment(
    compliance_id: int,
    challan_number: str,
    payment_date: str,
    payment_status: PaymentStatus,
    bank_name: Optional[str] = None,
    bank_branch: Optional[str] = None,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update compliance payment details"""
    from datetime import datetime
    try:
        result = await StatutoryComplianceService.update_payment_status(
            db, current_user["tenant_id"], compliance_id,
            challan_number, datetime.strptime(payment_date, "%Y-%m-%d").date(),
            payment_status, bank_name, bank_branch, remarks, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Compliance record not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compliance/summary/{year}/{month}")
async def get_compliance_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get statutory compliance summary for a month"""
    result = await StatutoryComplianceService.get_compliance_summary(
        db, current_user["tenant_id"], month, year
    )
    return result


@router.get("/compliance/pending-payments")
async def get_pending_compliance_payments(
    due_before: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending statutory compliance payments"""
    from datetime import datetime
    due_date = None
    if due_before:
        due_date = datetime.strptime(due_before, "%Y-%m-%d").date()
    
    result = await StatutoryComplianceService.get_pending_payments(
        db, current_user["tenant_id"], due_date
    )
    return {"items": result, "total": len(result)}


@router.delete("/compliance/{compliance_id}")
async def delete_statutory_compliance(
    compliance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete statutory compliance record"""
    success = await StatutoryComplianceService.delete_compliance(
        db, current_user["tenant_id"], compliance_id, current_user["id"]
    )
    if not success:
        raise HTTPException(status_code=404, detail="Compliance record not found or cannot be deleted")
    return {"message": "Compliance record deleted successfully"}


# ============ Form 16 Endpoints ============

@router.post("/form16", response_model=Form16Response)
async def create_form16(
    form16: Form16Create,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new Form 16 record"""
    try:
        result = await Form16Service.create_form16(
            db, current_user["tenant_id"], form16, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/form16", response_model=Form16List)
async def list_form16(
    employee_id: Optional[int] = None,
    financial_year: Optional[str] = None,
    status: Optional[Form16Status] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List Form 16 records with filters"""
    return await Form16Service.list_form16(
        db, current_user["tenant_id"], employee_id, financial_year,
        status, page, page_size
    )


@router.get("/form16/{form16_id}", response_model=Form16Response)
async def get_form16(
    form16_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a Form 16 record by ID"""
    result = await Form16Service.get_form16(
        db, current_user["tenant_id"], form16_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Form 16 not found")
    return result


@router.put("/form16/{form16_id}", response_model=Form16Response)
async def update_form16(
    form16_id: int,
    form16: Form16Update,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update Form 16 record"""
    try:
        result = await Form16Service.update_form16(
            db, current_user["tenant_id"], form16_id, form16, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Form 16 not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/form16/generate")
async def generate_form16(
    employee_id: int,
    financial_year: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate Form 16 for an employee"""
    try:
        result = await Form16Service.generate_form16(
            db, current_user["tenant_id"], employee_id, 
            financial_year, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/form16/{form16_id}/issue")
async def issue_form16(
    form16_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Issue Form 16 to employee"""
    result = await Form16Service.issue_form16(
        db, current_user["tenant_id"], form16_id, current_user["id"]
    )
    if not result:
        raise HTTPException(status_code=404, detail="Form 16 not found")
    return result


@router.get("/form16/{form16_id}/download")
async def download_form16(
    form16_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download Form 16 PDF"""
    result = await Form16Service.get_form16(
        db, current_user["tenant_id"], form16_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Form 16 not found")
    
    # TODO: Implement PDF generation
    return {"message": "PDF generation not implemented", "form16": result}


@router.delete("/form16/{form16_id}")
async def delete_form16(
    form16_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete Form 16 record"""
    success = await Form16Service.delete_form16(
        db, current_user["tenant_id"], form16_id, current_user["id"]
    )
    if not success:
        raise HTTPException(status_code=404, detail="Form 16 not found or cannot be deleted")
    return {"message": "Form 16 deleted successfully"}


# ============ Payment File Endpoints ============

@router.post("/payment-files", response_model=PaymentFileResponse)
async def create_payment_file(
    payment_file: PaymentFileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new payment file record"""
    try:
        result = await PaymentFileService.create_payment_file(
            db, current_user["tenant_id"], payment_file, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payment-files", response_model=PaymentFileList)
async def list_payment_files(
    payroll_run_id: Optional[int] = None,
    file_format: Optional[PaymentFileFormat] = None,
    status: Optional[PaymentFileStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List payment files with filters"""
    return await PaymentFileService.list_payment_files(
        db, current_user["tenant_id"], payroll_run_id, file_format,
        status, page, page_size
    )


@router.get("/payment-files/{payment_file_id}", response_model=PaymentFileResponse)
async def get_payment_file(
    payment_file_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a payment file by ID"""
    result = await PaymentFileService.get_payment_file(
        db, current_user["tenant_id"], payment_file_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Payment file not found")
    return result


@router.put("/payment-files/{payment_file_id}", response_model=PaymentFileResponse)
async def update_payment_file(
    payment_file_id: int,
    payment_file: PaymentFileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update payment file record"""
    try:
        result = await PaymentFileService.update_payment_file(
            db, current_user["tenant_id"], payment_file_id, 
            payment_file, current_user["id"]
        )
        if not result:
            raise HTTPException(status_code=404, detail="Payment file not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payment-files/generate")
async def generate_payment_file(
    payroll_run_id: int,
    file_format: PaymentFileFormat,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate payment file for a payroll run"""
    try:
        result = await PaymentFileService.generate_payment_file(
            db, current_user["tenant_id"], payroll_run_id, 
            file_format, current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payment-files/{payment_file_id}/upload")
async def update_payment_file_status(
    payment_file_id: int,
    status: PaymentFileStatus,
    uploaded_by: Optional[str] = None,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update payment file upload status"""
    result = await PaymentFileService.update_upload_status(
        db, current_user["tenant_id"], payment_file_id,
        status, uploaded_by, remarks, current_user["id"]
    )
    if not result:
        raise HTTPException(status_code=404, detail="Payment file not found")
    return result


@router.get("/payment-files/{payment_file_id}/download")
async def download_payment_file(
    payment_file_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download payment file"""
    result = await PaymentFileService.get_payment_file(
        db, current_user["tenant_id"], payment_file_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Payment file not found")
    
    # TODO: Implement file download from storage
    return {"message": "File download not implemented", "file_path": result.file_path}


@router.delete("/payment-files/{payment_file_id}")
async def delete_payment_file(
    payment_file_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete payment file"""
    success = await PaymentFileService.delete_payment_file(
        db, current_user["tenant_id"], payment_file_id, current_user["id"]
    )
    if not success:
        raise HTTPException(status_code=404, detail="Payment file not found or cannot be deleted")
    return {"message": "Payment file deleted successfully"}
