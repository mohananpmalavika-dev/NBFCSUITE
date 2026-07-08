"""
Form 16 Service
Handles Form 16 generation, issuance, and management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.shared.database.payroll_models import (
    Form16, Form16Status, PayrollRun, Payslip, StatutoryCompliance, StatutoryType
)
from backend.shared.database.hrms_models import Employee
from backend.services.payroll.schemas import (
    Form16Create, Form16Update, Form16Response, Form16List
)


class Form16Service:
    """Service for Form 16 management"""
    
    @staticmethod
    async def create_form16(
        db: AsyncSession,
        tenant_id: str,
        form16_data: Form16Create,
        user_id: str
    ) -> Form16Response:
        """Create a new Form 16 record"""
        
        # Generate Form 16 code
        financial_year = form16_data.financial_year.replace("-", "")
        result = await db.execute(
            select(func.count(Form16.id))
            .where(
                and_(
                    Form16.tenant_id == tenant_id,
                    Form16.form16_code.like(f"F16-{financial_year}-%"),
                    Form16.is_deleted == False
                )
            )
        )
        count = result.scalar() or 0
        form16_code = f"F16-{financial_year}-{str(count + 1).zfill(4)}"
        
        # Create Form 16
        form16 = Form16(
            tenant_id=tenant_id,
            form16_code=form16_code,
            employee_id=form16_data.employee_id,
            financial_year=form16_data.financial_year,
            gross_salary=form16_data.gross_salary,
            standard_deduction=form16_data.standard_deduction,
            professional_tax=form16_data.professional_tax,
            chapter_vi_a_deductions=form16_data.chapter_vi_a_deductions,
            total_income=form16_data.total_income,
            taxable_income=form16_data.taxable_income,
            tax_on_income=form16_data.tax_on_income,
            education_cess=form16_data.education_cess,
            total_tax=form16_data.total_tax,
            tax_deducted=form16_data.tax_deducted,
            tax_refund=form16_data.tax_refund,
            tax_payable=form16_data.tax_payable,
            status=form16_data.status or Form16Status.DRAFT,
            issued_date=form16_data.issued_date,
            remarks=form16_data.remarks,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(form16)
        await db.commit()
        await db.refresh(form16)
        
        return Form16Response.model_validate(form16)
    
    @staticmethod
    async def get_form16(
        db: AsyncSession,
        tenant_id: str,
        form16_id: int
    ) -> Optional[Form16Response]:
        """Get Form 16 by ID"""
        
        result = await db.execute(
            select(Form16)
            .options(selectinload(Form16.employee))
            .where(
                and_(
                    Form16.id == form16_id,
                    Form16.tenant_id == tenant_id,
                    Form16.is_deleted == False
                )
            )
        )
        form16 = result.scalar_one_or_none()
        
        if not form16:
            return None
        
        return Form16Response.model_validate(form16)
    
    @staticmethod
    async def list_form16(
        db: AsyncSession,
        tenant_id: str,
        employee_id: Optional[int] = None,
        financial_year: Optional[str] = None,
        status: Optional[Form16Status] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Form16List:
        """List Form 16 records with filters"""
        
        # Build query
        query = select(Form16).where(
            and_(
                Form16.tenant_id == tenant_id,
                Form16.is_deleted == False
            )
        )
        
        # Apply filters
        if employee_id:
            query = query.where(Form16.employee_id == employee_id)
        
        if financial_year:
            query = query.where(Form16.financial_year == financial_year)
        
        if status:
            query = query.where(Form16.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(Form16.financial_year.desc(), Form16.form16_code.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        form16_records = result.scalars().all()
        
        return Form16List(
            items=[Form16Response.model_validate(f) for f in form16_records],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    @staticmethod
    async def update_form16(
        db: AsyncSession,
        tenant_id: str,
        form16_id: int,
        form16_data: Form16Update,
        user_id: str
    ) -> Optional[Form16Response]:
        """Update Form 16 record"""
        
        result = await db.execute(
            select(Form16)
            .where(
                and_(
                    Form16.id == form16_id,
                    Form16.tenant_id == tenant_id,
                    Form16.is_deleted == False
                )
            )
        )
        form16 = result.scalar_one_or_none()
        
        if not form16:
            return None
        
        # Update fields
        update_data = form16_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(form16, field, value)
        
        form16.updated_by = user_id
        form16.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(form16)
        
        return Form16Response.model_validate(form16)
    
    @staticmethod
    async def generate_form16(
        db: AsyncSession,
        tenant_id: str,
        employee_id: int,
        financial_year: str,
        user_id: str
    ) -> Form16Response:
        """Generate Form 16 for an employee for a financial year"""
        
        # Get employee details
        employee_result = await db.execute(
            select(Employee)
            .where(
                and_(
                    Employee.id == employee_id,
                    Employee.tenant_id == tenant_id,
                    Employee.is_deleted == False
                )
            )
        )
        employee = employee_result.scalar_one_or_none()
        
        if not employee:
            raise ValueError("Employee not found")
        
        # Parse financial year (e.g., "2023-2024")
        fy_parts = financial_year.split("-")
        start_year = int(fy_parts[0])
        end_year = int(fy_parts[1])
        
        # Get all payslips for the financial year (April to March)
        payslip_result = await db.execute(
            select(Payslip)
            .join(PayrollRun)
            .where(
                and_(
                    Payslip.tenant_id == tenant_id,
                    Payslip.employee_id == employee_id,
                    or_(
                        and_(
                            PayrollRun.year == start_year,
                            PayrollRun.month >= 4  # April onwards
                        ),
                        and_(
                            PayrollRun.year == end_year,
                            PayrollRun.month <= 3  # Up to March
                        )
                    ),
                    Payslip.is_deleted == False
                )
            )
        )
        payslips = payslip_result.scalars().all()
        
        # Calculate totals from payslips
        gross_salary = sum(p.gross_salary for p in payslips)
        professional_tax = sum(p.professional_tax for p in payslips)
        tax_deducted = sum(p.tds for p in payslips)
        
        # Standard deduction (₹50,000 as per current rules)
        standard_deduction = Decimal('50000.00')
        
        # Chapter VI-A deductions (simplified - should be from employee declarations)
        # For now, using a default value
        chapter_vi_a_deductions = Decimal('150000.00')  # 80C limit
        
        # Calculate taxable income
        total_income = gross_salary
        taxable_income = max(
            total_income - standard_deduction - professional_tax - chapter_vi_a_deductions,
            Decimal('0.00')
        )
        
        # Calculate tax (simplified old regime calculation)
        tax_on_income = Form16Service._calculate_income_tax(taxable_income)
        
        # Education cess (4% on income tax)
        education_cess = tax_on_income * Decimal('0.04')
        
        # Total tax
        total_tax = tax_on_income + education_cess
        
        # Tax refund or payable
        tax_refund = Decimal('0.00')
        tax_payable = Decimal('0.00')
        
        if tax_deducted > total_tax:
            tax_refund = tax_deducted - total_tax
        else:
            tax_payable = total_tax - tax_deducted
        
        # Create Form 16 data
        form16_data = Form16Create(
            employee_id=employee_id,
            financial_year=financial_year,
            gross_salary=gross_salary,
            standard_deduction=standard_deduction,
            professional_tax=professional_tax,
            chapter_vi_a_deductions=chapter_vi_a_deductions,
            total_income=total_income,
            taxable_income=taxable_income,
            tax_on_income=tax_on_income,
            education_cess=education_cess,
            total_tax=total_tax,
            tax_deducted=tax_deducted,
            tax_refund=tax_refund,
            tax_payable=tax_payable,
            status=Form16Status.DRAFT
        )
        
        return await Form16Service.create_form16(db, tenant_id, form16_data, user_id)
    
    @staticmethod
    def _calculate_income_tax(taxable_income: Decimal) -> Decimal:
        """Calculate income tax based on old regime slabs"""
        
        tax = Decimal('0.00')
        
        # Tax slabs (Old Regime FY 2023-24)
        if taxable_income <= 250000:
            tax = Decimal('0.00')
        elif taxable_income <= 500000:
            tax = (taxable_income - Decimal('250000')) * Decimal('0.05')
        elif taxable_income <= 1000000:
            tax = Decimal('12500') + (taxable_income - Decimal('500000')) * Decimal('0.20')
        else:
            tax = Decimal('112500') + (taxable_income - Decimal('1000000')) * Decimal('0.30')
        
        return tax
    
    @staticmethod
    async def issue_form16(
        db: AsyncSession,
        tenant_id: str,
        form16_id: int,
        user_id: str
    ) -> Optional[Form16Response]:
        """Issue Form 16 to employee"""
        
        result = await db.execute(
            select(Form16)
            .where(
                and_(
                    Form16.id == form16_id,
                    Form16.tenant_id == tenant_id,
                    Form16.is_deleted == False
                )
            )
        )
        form16 = result.scalar_one_or_none()
        
        if not form16:
            return None
        
        # Update status to issued
        form16.status = Form16Status.ISSUED
        form16.issued_date = datetime.utcnow().date()
        form16.updated_by = user_id
        form16.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(form16)
        
        return Form16Response.model_validate(form16)
    
    @staticmethod
    async def delete_form16(
        db: AsyncSession,
        tenant_id: str,
        form16_id: int,
        user_id: str
    ) -> bool:
        """Soft delete Form 16"""
        
        result = await db.execute(
            select(Form16)
            .where(
                and_(
                    Form16.id == form16_id,
                    Form16.tenant_id == tenant_id,
                    Form16.is_deleted == False
                )
            )
        )
        form16 = result.scalar_one_or_none()
        
        if not form16:
            return False
        
        # Can only delete draft Form 16
        if form16.status != Form16Status.DRAFT:
            return False
        
        form16.is_deleted = True
        form16.updated_by = user_id
        form16.updated_at = datetime.utcnow()
        
        await db.commit()
        return True
