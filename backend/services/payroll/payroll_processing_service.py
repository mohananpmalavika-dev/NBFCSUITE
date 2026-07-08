"""
Payroll Processing Service
Handles monthly payroll execution, payslip generation, and statutory calculations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal
import calendar

from backend.shared.database.payroll_models import (
    PayrollRun, Payslip, PayslipComponent, EmployeeSalary, 
    EmployeeSalaryComponent, SalaryComponent, StatutoryCompliance,
    PayrollStatus, PaymentMode, PaymentStatus, ComponentType, StatutoryType
)
from backend.services.payroll.schemas import (
    PayrollRunCreate, PayrollRunResponse, PayrollSummary
)


class PayrollProcessingService:
    """Service class for payroll processing operations"""
    
    # Statutory calculation limits and rates (for India)
    PF_WAGE_CEILING = Decimal("15000.00")  # PF calculation ceiling
    PF_EMPLOYEE_RATE = Decimal("0.12")  # 12%
    PF_EMPLOYER_RATE = Decimal("0.12")  # 12%
    
    ESI_WAGE_CEILING = Decimal("21000.00")  # ESI calculation ceiling
    ESI_EMPLOYEE_RATE = Decimal("0.0075")  # 0.75%
    ESI_EMPLOYER_RATE = Decimal("0.0325")  # 3.25%
    
    # Professional Tax slabs (Maharashtra example)
    PT_SLABS = [
        (0, 5999, 0),
        (6000, 8999, 175),
        (9000, 9999, 200),
        (10000, float('inf'), 200)
    ]
    
    @staticmethod
    def _generate_run_code(tenant_id: int, month: int, year: int) -> str:
        """Generate unique payroll run code"""
        return f"PR-{tenant_id}-{year}{month:02d}-{datetime.now().strftime('%H%M%S')}"
    
    @staticmethod
    def _generate_payslip_number(tenant_id: int, employee_id: int, month: int, year: int) -> str:
        """Generate unique payslip number"""
        return f"PS-{tenant_id}-{employee_id}-{year}{month:02d}"
    
    @staticmethod
    async def create_payroll_run(
        db: Session,
        run_data: PayrollRunCreate,
        created_by: int
    ) -> PayrollRun:
        """Create a new payroll run"""
        
        # Check if payroll already exists for this month/year
        existing = db.query(PayrollRun).filter(
            and_(
                PayrollRun.tenant_id == run_data.tenant_id,
                PayrollRun.payroll_month == run_data.payroll_month,
                PayrollRun.payroll_year == run_data.payroll_year,
                PayrollRun.is_deleted == False,
                PayrollRun.status != PayrollStatus.CANCELLED
            )
        ).first()
        
        if existing:
            raise ValueError(f"Payroll run already exists for {run_data.payroll_month}/{run_data.payroll_year}")
        
        # Generate run code
        run_code = PayrollProcessingService._generate_run_code(
            run_data.tenant_id, 
            run_data.payroll_month, 
            run_data.payroll_year
        )
        
        # Create payroll run
        payroll_run = PayrollRun(
            **run_data.dict(),
            run_code=run_code,
            status=PayrollStatus.DRAFT,
            created_by=created_by,
            updated_by=created_by
        )
        
        db.add(payroll_run)
        db.commit()
        db.refresh(payroll_run)
        
        return payroll_run

    
    @staticmethod
    def _calculate_pf(basic_salary: Decimal) -> Dict[str, Decimal]:
        """Calculate PF (Provident Fund) contribution"""
        pf_wage = min(basic_salary, PayrollProcessingService.PF_WAGE_CEILING)
        
        employee_pf = (pf_wage * PayrollProcessingService.PF_EMPLOYEE_RATE).quantize(Decimal('0.01'))
        employer_pf = (pf_wage * PayrollProcessingService.PF_EMPLOYER_RATE).quantize(Decimal('0.01'))
        
        return {
            "employee": employee_pf,
            "employer": employer_pf,
            "total": employee_pf + employer_pf
        }
    
    @staticmethod
    def _calculate_esi(gross_salary: Decimal) -> Dict[str, Decimal]:
        """Calculate ESI (Employee State Insurance) contribution"""
        if gross_salary > PayrollProcessingService.ESI_WAGE_CEILING:
            return {"employee": Decimal("0.00"), "employer": Decimal("0.00"), "total": Decimal("0.00")}
        
        employee_esi = (gross_salary * PayrollProcessingService.ESI_EMPLOYEE_RATE).quantize(Decimal('0.01'))
        employer_esi = (gross_salary * PayrollProcessingService.ESI_EMPLOYER_RATE).quantize(Decimal('0.01'))
        
        return {
            "employee": employee_esi,
            "employer": employer_esi,
            "total": employee_esi + employer_esi
        }
    
    @staticmethod
    def _calculate_pt(gross_salary: Decimal) -> Decimal:
        """Calculate PT (Professional Tax) based on slabs"""
        for min_amt, max_amt, pt_amt in PayrollProcessingService.PT_SLABS:
            if min_amt <= gross_salary <= max_amt:
                return Decimal(str(pt_amt))
        return Decimal("0.00")
    
    @staticmethod
    def _calculate_tds(
        gross_annual: Decimal,
        exemptions: Decimal,
        deductions: Decimal,
        months_remaining: int
    ) -> Decimal:
        """Calculate TDS (Tax Deducted at Source) for the month"""
        taxable_income = gross_annual - exemptions - deductions
        
        # Tax calculation based on old regime (simplified)
        tax = Decimal("0.00")
        
        if taxable_income <= 250000:
            tax = Decimal("0.00")
        elif taxable_income <= 500000:
            tax = (taxable_income - 250000) * Decimal("0.05")
        elif taxable_income <= 1000000:
            tax = 12500 + (taxable_income - 500000) * Decimal("0.20")
        else:
            tax = 112500 + (taxable_income - 1000000) * Decimal("0.30")
        
        # Add education cess (4%)
        tax = tax + (tax * Decimal("0.04"))
        
        # Monthly TDS
        if months_remaining > 0:
            monthly_tds = (tax / months_remaining).quantize(Decimal('0.01'))
        else:
            monthly_tds = Decimal("0.00")
        
        return monthly_tds

    
    @staticmethod
    async def process_payroll(
        db: Session,
        payroll_run_id: int,
        tenant_id: int,
        employee_ids: Optional[List[int]] = None,
        processed_by: int = None
    ) -> PayrollRun:
        """Process payroll for all or selected employees"""
        
        # Get payroll run
        payroll_run = db.query(PayrollRun).filter(
            and_(
                PayrollRun.id == payroll_run_id,
                PayrollRun.tenant_id == tenant_id,
                PayrollRun.is_deleted == False
            )
        ).first()
        
        if not payroll_run:
            raise ValueError("Payroll run not found")
        
        if payroll_run.status not in [PayrollStatus.DRAFT, PayrollStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot process payroll in status: {payroll_run.status}")
        
        # Update status
        payroll_run.status = PayrollStatus.IN_PROGRESS
        payroll_run.processing_started_at = datetime.utcnow()
        db.commit()
        
        try:
            # Get active employees with salary assignments
            query = db.query(EmployeeSalary).filter(
                and_(
                    EmployeeSalary.tenant_id == tenant_id,
                    EmployeeSalary.is_active == True,
                    EmployeeSalary.is_deleted == False,
                    EmployeeSalary.effective_from <= payroll_run.period_end_date
                )
            )
            
            # Filter by specific employees if provided
            if employee_ids:
                query = query.filter(EmployeeSalary.employee_id.in_(employee_ids))
            
            # Filter out employees with effective_to before payroll period
            query = query.filter(
                (EmployeeSalary.effective_to.is_(None)) |
                (EmployeeSalary.effective_to >= payroll_run.period_start_date)
            )
            
            employee_salaries = query.all()
            
            payroll_run.total_employees = len(employee_salaries)
            
            total_gross = Decimal("0.00")
            total_deductions = Decimal("0.00")
            total_net = Decimal("0.00")
            
            # Process each employee
            for emp_salary in employee_salaries:
                try:
                    payslip = await PayrollProcessingService._process_employee_payroll(
                        db, payroll_run, emp_salary
                    )
                    
                    total_gross += payslip.gross_earnings
                    total_deductions += payslip.total_deductions
                    total_net += payslip.net_salary
                    
                    payroll_run.processed_employees += 1
                    
                except Exception as e:
                    print(f"Error processing employee {emp_salary.employee_id}: {str(e)}")
                    continue
            
            # Update totals
            payroll_run.total_gross = total_gross
            payroll_run.total_deductions = total_deductions
            payroll_run.total_net_pay = total_net
            payroll_run.status = PayrollStatus.COMPLETED
            payroll_run.processing_completed_at = datetime.utcnow()
            
            # Generate statutory compliance records
            await PayrollProcessingService._generate_statutory_records(db, payroll_run)
            
            db.commit()
            db.refresh(payroll_run)
            
            return payroll_run
            
        except Exception as e:
            payroll_run.status = PayrollStatus.DRAFT
            db.commit()
            raise e

    
    @staticmethod
    async def _process_employee_payroll(
        db: Session,
        payroll_run: PayrollRun,
        emp_salary: EmployeeSalary
    ) -> Payslip:
        """Process payroll for a single employee"""
        
        # Get employee salary components
        components = db.query(EmployeeSalaryComponent).filter(
            and_(
                EmployeeSalaryComponent.employee_salary_id == emp_salary.id,
                EmployeeSalaryComponent.is_deleted == False
            )
        ).all()
        
        # Get days in month
        days_in_month = calendar.monthrange(payroll_run.payroll_year, payroll_run.payroll_month)[1]
        
        # TODO: Get actual attendance data from attendance module
        # For now, assume full month attendance
        days_worked = Decimal(str(days_in_month))
        days_lop = Decimal("0.00")
        
        # Calculate earnings and deductions
        basic_salary = Decimal("0.00")
        gross_earnings = Decimal("0.00")
        total_deductions = Decimal("0.00")
        
        earnings_list = []
        deductions_list = []
        
        for comp in components:
            component_detail = db.query(SalaryComponent).filter(
                SalaryComponent.id == comp.component_id
            ).first()
            
            if not component_detail:
                continue
            
            # Calculate pro-rated amount if LOP days exist
            amount = comp.monthly_amount
            if days_lop > 0:
                amount = (amount / days_in_month) * days_worked
                amount = amount.quantize(Decimal('0.01'))
            
            if component_detail.component_type == ComponentType.EARNING:
                gross_earnings += amount
                earnings_list.append({
                    "component_id": comp.component_id,
                    "component_code": component_detail.component_code,
                    "component_name": component_detail.component_name,
                    "amount": amount
                })
                
                # Identify basic salary
                if "BASIC" in component_detail.component_code.upper():
                    basic_salary = amount
            
            elif component_detail.component_type == ComponentType.DEDUCTION:
                total_deductions += amount
                deductions_list.append({
                    "component_id": comp.component_id,
                    "component_code": component_detail.component_code,
                    "component_name": component_detail.component_name,
                    "amount": amount
                })
        
        # Calculate statutory deductions
        pf_amounts = PayrollProcessingService._calculate_pf(basic_salary)
        esi_amounts = PayrollProcessingService._calculate_esi(gross_earnings)
        pt_amount = PayrollProcessingService._calculate_pt(gross_earnings)
        
        # TDS calculation (simplified - should use employee's tax declarations)
        months_remaining = 12 - payroll_run.payroll_month + 1
        tds_amount = PayrollProcessingService._calculate_tds(
            emp_salary.ctc_annual,
            Decimal("0.00"),  # TODO: Get actual exemptions
            Decimal("50000.00"),  # TODO: Get actual deductions (80C, etc.)
            months_remaining
        )
        
        # Add statutory deductions
        total_deductions += pf_amounts["employee"]
        total_deductions += esi_amounts["employee"]
        total_deductions += pt_amount
        total_deductions += tds_amount
        
        # Calculate net salary
        net_salary = gross_earnings - total_deductions
        
        # Generate payslip number
        payslip_number = PayrollProcessingService._generate_payslip_number(
            payroll_run.tenant_id,
            emp_salary.employee_id,
            payroll_run.payroll_month,
            payroll_run.payroll_year
        )
        
        # Create payslip
        payslip = Payslip(
            tenant_id=payroll_run.tenant_id,
            payroll_run_id=payroll_run.id,
            employee_id=emp_salary.employee_id,
            payslip_number=payslip_number,
            payroll_month=payroll_run.payroll_month,
            payroll_year=payroll_run.payroll_year,
            pay_date=payroll_run.pay_date,
            days_in_month=days_in_month,
            days_worked=days_worked,
            days_lop=days_lop,
            basic_salary=basic_salary,
            gross_earnings=gross_earnings,
            total_deductions=total_deductions,
            net_salary=net_salary,
            pf_employee=pf_amounts["employee"],
            pf_employer=pf_amounts["employer"],
            esi_employee=esi_amounts["employee"],
            esi_employer=esi_amounts["employer"],
            pt_deduction=pt_amount,
            tds_deduction=tds_amount,
            payment_mode=emp_salary.payment_mode,
            payment_status=PaymentStatus.PENDING,
            bank_account_number=emp_salary.bank_account_number,
            bank_ifsc_code=emp_salary.bank_ifsc_code
        )
        
        db.add(payslip)
        db.flush()
        
        # Create payslip components
        for earning in earnings_list:
            component = PayslipComponent(
                tenant_id=payroll_run.tenant_id,
                payslip_id=payslip.id,
                component_id=earning["component_id"],
                component_code=earning["component_code"],
                component_name=earning["component_name"],
                component_type=ComponentType.EARNING,
                amount=earning["amount"]
            )
            db.add(component)
        
        for deduction in deductions_list:
            component = PayslipComponent(
                tenant_id=payroll_run.tenant_id,
                payslip_id=payslip.id,
                component_id=deduction["component_id"],
                component_code=deduction["component_code"],
                component_name=deduction["component_name"],
                component_type=ComponentType.DEDUCTION,
                amount=deduction["amount"]
            )
            db.add(component)
        
        # Add statutory components
        statutory_components = [
            ("PF_EMPLOYEE", "PF Employee Contribution", ComponentType.DEDUCTION, pf_amounts["employee"]),
            ("ESI_EMPLOYEE", "ESI Employee Contribution", ComponentType.DEDUCTION, esi_amounts["employee"]),
            ("PT", "Professional Tax", ComponentType.DEDUCTION, pt_amount),
            ("TDS", "Tax Deducted at Source", ComponentType.DEDUCTION, tds_amount)
        ]
        
        for code, name, comp_type, amount in statutory_components:
            if amount > 0:
                component = PayslipComponent(
                    tenant_id=payroll_run.tenant_id,
                    payslip_id=payslip.id,
                    component_id=0,  # System component
                    component_code=code,
                    component_name=name,
                    component_type=comp_type,
                    amount=amount
                )
                db.add(component)
        
        db.flush()
        
        return payslip

    
    @staticmethod
    async def _generate_statutory_records(
        db: Session,
        payroll_run: PayrollRun
    ) -> None:
        """Generate statutory compliance records (PF, ESI, PT, TDS)"""
        
        # Get all payslips for this run
        payslips = db.query(Payslip).filter(
            Payslip.payroll_run_id == payroll_run.id
        ).all()
        
        # Aggregate statutory amounts
        pf_employee_total = sum(p.pf_employee for p in payslips)
        pf_employer_total = sum(p.pf_employer for p in payslips)
        esi_employee_total = sum(p.esi_employee for p in payslips)
        esi_employer_total = sum(p.esi_employer for p in payslips)
        pt_total = sum(p.pt_deduction for p in payslips)
        tds_total = sum(p.tds_deduction for p in payslips)
        
        # Create statutory compliance records
        statutory_records = [
            (StatutoryType.PF, pf_employee_total, pf_employer_total),
            (StatutoryType.ESI, esi_employee_total, esi_employer_total),
            (StatutoryType.PT, pt_total, Decimal("0.00")),
            (StatutoryType.TDS, tds_total, Decimal("0.00"))
        ]
        
        for stat_type, employee_contrib, employer_contrib in statutory_records:
            if employee_contrib + employer_contrib > 0:
                compliance = StatutoryCompliance(
                    tenant_id=payroll_run.tenant_id,
                    payroll_run_id=payroll_run.id,
                    compliance_month=payroll_run.payroll_month,
                    compliance_year=payroll_run.payroll_year,
                    statutory_type=stat_type,
                    employee_contribution=employee_contrib,
                    employer_contribution=employer_contrib,
                    total_amount=employee_contrib + employer_contrib,
                    is_paid=False,
                    return_filed=False
                )
                db.add(compliance)
        
        db.flush()
    
    @staticmethod
    async def approve_payroll(
        db: Session,
        payroll_run_id: int,
        tenant_id: int,
        approved_by: int,
        remarks: Optional[str] = None
    ) -> PayrollRun:
        """Approve a completed payroll run"""
        
        payroll_run = db.query(PayrollRun).filter(
            and_(
                PayrollRun.id == payroll_run_id,
                PayrollRun.tenant_id == tenant_id,
                PayrollRun.is_deleted == False
            )
        ).first()
        
        if not payroll_run:
            raise ValueError("Payroll run not found")
        
        if payroll_run.status != PayrollStatus.COMPLETED:
            raise ValueError(f"Can only approve completed payroll runs. Current status: {payroll_run.status}")
        
        payroll_run.status = PayrollStatus.APPROVED
        payroll_run.approved_by = approved_by
        payroll_run.approved_at = datetime.utcnow()
        payroll_run.approval_remarks = remarks
        
        db.commit()
        db.refresh(payroll_run)
        
        return payroll_run
    
    @staticmethod
    async def get_payroll_summary(
        db: Session,
        tenant_id: int,
        month: int,
        year: int
    ) -> Optional[PayrollSummary]:
        """Get payroll summary for a specific month"""
        
        payroll_run = db.query(PayrollRun).filter(
            and_(
                PayrollRun.tenant_id == tenant_id,
                PayrollRun.payroll_month == month,
                PayrollRun.payroll_year == year,
                PayrollRun.is_deleted == False
            )
        ).first()
        
        if not payroll_run:
            return None
        
        # Get statutory totals
        pf_total = db.query(func.sum(Payslip.pf_employee + Payslip.pf_employer)).filter(
            Payslip.payroll_run_id == payroll_run.id
        ).scalar() or Decimal("0.00")
        
        esi_total = db.query(func.sum(Payslip.esi_employee + Payslip.esi_employer)).filter(
            Payslip.payroll_run_id == payroll_run.id
        ).scalar() or Decimal("0.00")
        
        pt_total = db.query(func.sum(Payslip.pt_deduction)).filter(
            Payslip.payroll_run_id == payroll_run.id
        ).scalar() or Decimal("0.00")
        
        tds_total = db.query(func.sum(Payslip.tds_deduction)).filter(
            Payslip.payroll_run_id == payroll_run.id
        ).scalar() or Decimal("0.00")
        
        return PayrollSummary(
            month=month,
            year=year,
            total_employees=payroll_run.total_employees,
            total_gross=payroll_run.total_gross,
            total_deductions=payroll_run.total_deductions,
            total_net=payroll_run.total_net_pay,
            pf_total=pf_total,
            esi_total=esi_total,
            pt_total=pt_total,
            tds_total=tds_total
        )
