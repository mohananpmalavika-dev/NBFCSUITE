"""
HRMS Employee Self-Service (ESS) Service Layer
Business logic for employee self-service operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from backend.shared.database.hrms_models import (
    Employee, LeaveBalance, LeaveApplication, 
    InvestmentDeclaration, InvestmentDeclarationItem,
    ReimbursementClaim, LeaveType, LeaveStatus,
    InvestmentSection, InvestmentStatus, 
    ReimbursementType, ReimbursementStatus
)
from backend.shared.database.payroll_models import Payslip, PayslipComponent
from .ess_schemas import (
    LeaveApplicationCreate, LeaveApplicationUpdate,
    InvestmentDeclarationCreate, InvestmentDeclarationUpdate,
    ReimbursementClaimCreate, ReimbursementClaimUpdate,
    EmployeeProfileUpdateRequest, ESSDashboardStats
)


class ESSService:
    """Service for Employee Self-Service operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str, employee_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.employee_id = employee_id
    
    # ========================================================================
    # PAYSLIP OPERATIONS
    # ========================================================================
    
    async def get_employee_payslips(
        self, 
        page: int = 1, 
        page_size: int = 12
    ) -> Tuple[List[Payslip], int]:
        """Get employee's payslips with pagination"""
        
        # Base query
        query = select(Payslip).where(
            and_(
                Payslip.tenant_id == self.tenant_id,
                Payslip.employee_id == self.employee_id,
                Payslip.is_deleted == False
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and sorting
        query = query.order_by(desc(Payslip.year), desc(Payslip.month))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        payslips = result.scalars().all()
        
        return payslips, total
    
    async def get_payslip_by_month_year(
        self, 
        month: int, 
        year: int
    ) -> Optional[Payslip]:
        """Get specific payslip by month and year"""
        query = select(Payslip).where(
            and_(
                Payslip.tenant_id == self.tenant_id,
                Payslip.employee_id == self.employee_id,
                Payslip.month == month,
                Payslip.year == year,
                Payslip.is_deleted == False
            )
        ).options(selectinload(Payslip.components))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def generate_payslip_pdf(
        self, 
        payslip_id: str
    ) -> BytesIO:
        """Generate PDF for payslip"""
        
        # Get payslip with components and employee details
        query = select(Payslip).where(
            and_(
                Payslip.id == payslip_id,
                Payslip.tenant_id == self.tenant_id,
                Payslip.employee_id == self.employee_id,
                Payslip.is_deleted == False
            )
        ).options(
            selectinload(Payslip.components),
            selectinload(Payslip.employee).selectinload(Employee.department),
            selectinload(Payslip.employee).selectinload(Employee.designation)
        )
        
        result = await self.db.execute(query)
        payslip = result.scalar_one_or_none()
        
        if not payslip:
            raise ValueError("Payslip not found")
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Title
        elements.append(Paragraph("PAYSLIP", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Employee details table
        emp_data = [
            ['Employee Code:', payslip.employee.employee_code, 'Month/Year:', f"{payslip.month}/{payslip.year}"],
            ['Employee Name:', payslip.employee.full_name, 'Payslip No:', payslip.payslip_number],
            ['Department:', payslip.employee.department.department_name if payslip.employee.department else 'N/A', 
             'Designation:', payslip.employee.designation.designation_name if payslip.employee.designation else 'N/A'],
            ['Days Worked:', str(payslip.days_worked), 'Days in Month:', str(payslip.days_in_month)]
        ]
        
        emp_table = Table(emp_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(emp_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Earnings and Deductions table
        salary_data = [['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)']]
        
        earnings = [c for c in payslip.components if c.component_type == 'earning']
        deductions = [c for c in payslip.components if c.component_type == 'deduction']
        
        max_rows = max(len(earnings), len(deductions))
        
        for i in range(max_rows):
            earning_name = earnings[i].component_name if i < len(earnings) else ''
            earning_amt = f"{earnings[i].amount:,.2f}" if i < len(earnings) else ''
            deduction_name = deductions[i].component_name if i < len(deductions) else ''
            deduction_amt = f"{deductions[i].amount:,.2f}" if i < len(deductions) else ''
            
            salary_data.append([earning_name, earning_amt, deduction_name, deduction_amt])
        
        # Totals
        salary_data.append(['GROSS EARNINGS', f"{payslip.gross_earnings:,.2f}", 
                           'TOTAL DEDUCTIONS', f"{payslip.total_deductions:,.2f}"])
        
        salary_table = Table(salary_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch, 1.5*inch])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f5f5f5')),
        ]))
        
        elements.append(salary_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Net Salary
        net_data = [['NET SALARY (Gross Earnings - Total Deductions)', f"₹ {payslip.net_salary:,.2f}"]]
        net_table = Table(net_data, colWidths=[5*inch, 2.5*inch])
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#c8e6c9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(net_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                     textColor=colors.grey, alignment=TA_CENTER)
        elements.append(Paragraph("This is a system generated payslip and does not require signature.", footer_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
    
    # ========================================================================
    # LEAVE MANAGEMENT OPERATIONS
    # ========================================================================
    
    async def get_leave_balances(self, financial_year: Optional[str] = None) -> List[LeaveBalance]:
        """Get employee's leave balances"""
        if not financial_year:
            # Get current financial year (Apr-Mar)
            today = date.today()
            if today.month >= 4:
                financial_year = f"{today.year}-{str(today.year + 1)[2:]}"
            else:
                financial_year = f"{today.year - 1}-{str(today.year)[2:]}"
        
        query = select(LeaveBalance).where(
            and_(
                LeaveBalance.tenant_id == self.tenant_id,
                LeaveBalance.employee_id == self.employee_id,
                LeaveBalance.financial_year == financial_year,
                LeaveBalance.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _generate_leave_application_code(self) -> str:
        """Generate unique leave application code"""
        year_month = datetime.now().strftime("%Y%m")
        
        # Get count of applications this month
        count_query = select(func.count(LeaveApplication.id)).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.application_code.like(f"LV-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"LV-{year_month}-{sequence}"
    
    def _calculate_leave_days(self, from_date: date, to_date: date, is_half_day: bool) -> Decimal:
        """Calculate number of leave days"""
        if is_half_day:
            return Decimal("0.5")
        
        delta = to_date - from_date
        return Decimal(str(delta.days + 1))
    
    async def create_leave_application(self, data: LeaveApplicationCreate) -> LeaveApplication:
        """Create new leave application"""
        
        # Get employee with reporting manager
        emp_query = select(Employee).where(
            and_(
                Employee.id == self.employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        result = await self.db.execute(emp_query)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValueError("Employee not found")
        
        # Calculate number of days
        number_of_days = self._calculate_leave_days(data.from_date, data.to_date, data.is_half_day)
        
        # Generate application code
        application_code = await self._generate_leave_application_code()
        
        # Create leave application
        leave_app = LeaveApplication(
            tenant_id=self.tenant_id,
            application_code=application_code,
            employee_id=self.employee_id,
            leave_type=data.leave_type,
            from_date=data.from_date,
            to_date=data.to_date,
            number_of_days=number_of_days,
            is_half_day=data.is_half_day,
            half_day_session=data.half_day_session,
            reason=data.reason,
            contact_number_during_leave=data.contact_number_during_leave,
            contact_address_during_leave=data.contact_address_during_leave,
            status=LeaveStatus.DRAFT,
            approver1_id=employee.reporting_manager_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(leave_app)
        await self.db.commit()
        await self.db.refresh(leave_app)
        
        return leave_app
    
    async def submit_leave_application(self, application_id: str) -> LeaveApplication:
        """Submit leave application for approval"""
        query = select(LeaveApplication).where(
            and_(
                LeaveApplication.id == application_id,
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.employee_id == self.employee_id,
                LeaveApplication.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        leave_app = result.scalar_one_or_none()
        
        if not leave_app:
            raise ValueError("Leave application not found")
        
        if leave_app.status != LeaveStatus.DRAFT:
            raise ValueError("Only draft applications can be submitted")
        
        leave_app.status = LeaveStatus.PENDING_APPROVAL
        leave_app.submitted_date = datetime.utcnow()
        leave_app.approver1_status = "pending"
        leave_app.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(leave_app)
        
        return leave_app
    
    async def get_leave_applications(
        self, 
        status: Optional[LeaveStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[LeaveApplication], int]:
        """Get employee's leave applications"""
        
        query = select(LeaveApplication).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.employee_id == self.employee_id,
                LeaveApplication.is_deleted == False
            )
        ).options(
            selectinload(LeaveApplication.approver1)
        )
        
        if status:
            query = query.where(LeaveApplication.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(desc(LeaveApplication.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        applications = result.scalars().all()
        
        return applications, total
    
    async def cancel_leave_application(self, application_id: str, reason: str) -> LeaveApplication:
        """Cancel leave application"""
        query = select(LeaveApplication).where(
            and_(
                LeaveApplication.id == application_id,
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.employee_id == self.employee_id,
                LeaveApplication.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        leave_app = result.scalar_one_or_none()
        
        if not leave_app:
            raise ValueError("Leave application not found")
        
        if leave_app.status in [LeaveStatus.CANCELLED, LeaveStatus.REJECTED]:
            raise ValueError("Application cannot be cancelled")
        
        leave_app.status = LeaveStatus.CANCELLED
        leave_app.is_cancelled = True
        leave_app.cancelled_date = datetime.utcnow()
        leave_app.cancellation_reason = reason
        leave_app.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(leave_app)
        
        return leave_app
    
    # ========================================================================
    # INVESTMENT DECLARATION OPERATIONS
    # ========================================================================
    
    async def _generate_investment_declaration_code(self) -> str:
        """Generate unique investment declaration code"""
        year = datetime.now().year
        
        count_query = select(func.count(InvestmentDeclaration.id)).where(
            and_(
                InvestmentDeclaration.tenant_id == self.tenant_id,
                InvestmentDeclaration.declaration_code.like(f"INV-{year}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"INV-{year}-{sequence}"
    
    async def create_investment_declaration(
        self, 
        data: InvestmentDeclarationCreate
    ) -> InvestmentDeclaration:
        """Create new investment declaration"""
        
        # Check if declaration already exists for the financial year
        existing_query = select(InvestmentDeclaration).where(
            and_(
                InvestmentDeclaration.tenant_id == self.tenant_id,
                InvestmentDeclaration.employee_id == self.employee_id,
                InvestmentDeclaration.financial_year == data.financial_year,
                InvestmentDeclaration.is_deleted == False
            )
        )
        result = await self.db.execute(existing_query)
        existing = result.scalar_one_or_none()
        
        if existing and existing.is_locked:
            raise ValueError("Declaration for this financial year is locked")
        
        # Generate declaration code
        declaration_code = await self._generate_investment_declaration_code()
        
        # Calculate total declared amount
        total_declared = sum(item.declared_amount for item in data.items)
        
        # Create declaration
        declaration = InvestmentDeclaration(
            tenant_id=self.tenant_id,
            declaration_code=declaration_code,
            employee_id=self.employee_id,
            financial_year=data.financial_year,
            tax_regime=data.tax_regime,
            status=InvestmentStatus.DRAFT,
            total_declared_amount=total_declared,
            total_approved_amount=Decimal("0"),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(declaration)
        await self.db.flush()
        
        # Create line items
        for item_data in data.items:
            item = InvestmentDeclarationItem(
                tenant_id=self.tenant_id,
                declaration_id=declaration.id,
                section=item_data.section,
                investment_type=item_data.investment_type,
                description=item_data.description,
                declared_amount=item_data.declared_amount,
                policy_number=item_data.policy_number,
                proof_document_name=item_data.proof_document_name,
                proof_document_url=item_data.proof_document_url,
                is_verified=False,
                created_by=self.user_id,
                updated_by=self.user_id
            )
            self.db.add(item)
        
        await self.db.commit()
        await self.db.refresh(declaration)
        
        return declaration
    
    async def submit_investment_declaration(self, declaration_id: str) -> InvestmentDeclaration:
        """Submit investment declaration"""
        query = select(InvestmentDeclaration).where(
            and_(
                InvestmentDeclaration.id == declaration_id,
                InvestmentDeclaration.tenant_id == self.tenant_id,
                InvestmentDeclaration.employee_id == self.employee_id,
                InvestmentDeclaration.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        declaration = result.scalar_one_or_none()
        
        if not declaration:
            raise ValueError("Declaration not found")
        
        if declaration.status != InvestmentStatus.DRAFT:
            raise ValueError("Only draft declarations can be submitted")
        
        if declaration.is_locked:
            raise ValueError("Declaration is locked")
        
        declaration.status = InvestmentStatus.SUBMITTED
        declaration.submitted_date = datetime.utcnow()
        declaration.submitted_by_employee = True
        declaration.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(declaration)
        
        return declaration
    
    async def get_investment_declarations(
        self,
        financial_year: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InvestmentDeclaration], int]:
        """Get employee's investment declarations"""
        
        query = select(InvestmentDeclaration).where(
            and_(
                InvestmentDeclaration.tenant_id == self.tenant_id,
                InvestmentDeclaration.employee_id == self.employee_id,
                InvestmentDeclaration.is_deleted == False
            )
        ).options(selectinload(InvestmentDeclaration.line_items))
        
        if financial_year:
            query = query.where(InvestmentDeclaration.financial_year == financial_year)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(desc(InvestmentDeclaration.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        declarations = result.scalars().all()
        
        return declarations, total
    
    # ========================================================================
    # REIMBURSEMENT CLAIM OPERATIONS
    # ========================================================================
    
    async def _generate_reimbursement_claim_code(self) -> str:
        """Generate unique reimbursement claim code"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(ReimbursementClaim.id)).where(
            and_(
                ReimbursementClaim.tenant_id == self.tenant_id,
                ReimbursementClaim.claim_code.like(f"REIMB-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"REIMB-{year_month}-{sequence}"
    
    async def create_reimbursement_claim(
        self, 
        data: ReimbursementClaimCreate
    ) -> ReimbursementClaim:
        """Create new reimbursement claim"""
        
        # Get employee with reporting manager
        emp_query = select(Employee).where(
            and_(
                Employee.id == self.employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        )
        result = await self.db.execute(emp_query)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValueError("Employee not found")
        
        # Generate claim code
        claim_code = await self._generate_reimbursement_claim_code()
        
        # Convert attachment_urls list to JSON string if provided
        import json
        attachment_urls_json = json.dumps(data.attachment_urls) if data.attachment_urls else None
        
        # Create reimbursement claim
        claim = ReimbursementClaim(
            tenant_id=self.tenant_id,
            claim_code=claim_code,
            claim_title=data.claim_title,
            employee_id=self.employee_id,
            reimbursement_type=data.reimbursement_type,
            claim_description=data.claim_description,
            expense_date=data.expense_date,
            claim_amount=data.claim_amount,
            bill_number=data.bill_number,
            vendor_name=data.vendor_name,
            attachment_urls=attachment_urls_json,
            status=ReimbursementStatus.DRAFT,
            approver_id=employee.reporting_manager_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(claim)
        await self.db.commit()
        await self.db.refresh(claim)
        
        return claim
    
    async def submit_reimbursement_claim(self, claim_id: str) -> ReimbursementClaim:
        """Submit reimbursement claim for approval"""
        query = select(ReimbursementClaim).where(
            and_(
                ReimbursementClaim.id == claim_id,
                ReimbursementClaim.tenant_id == self.tenant_id,
                ReimbursementClaim.employee_id == self.employee_id,
                ReimbursementClaim.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        claim = result.scalar_one_or_none()
        
        if not claim:
            raise ValueError("Claim not found")
        
        if claim.status != ReimbursementStatus.DRAFT:
            raise ValueError("Only draft claims can be submitted")
        
        claim.status = ReimbursementStatus.PENDING_APPROVAL
        claim.submitted_date = datetime.utcnow()
        claim.approver_status = "pending"
        claim.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(claim)
        
        return claim
    
    async def get_reimbursement_claims(
        self,
        status: Optional[ReimbursementStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ReimbursementClaim], int]:
        """Get employee's reimbursement claims"""
        
        query = select(ReimbursementClaim).where(
            and_(
                ReimbursementClaim.tenant_id == self.tenant_id,
                ReimbursementClaim.employee_id == self.employee_id,
                ReimbursementClaim.is_deleted == False
            )
        ).options(selectinload(ReimbursementClaim.approver))
        
        if status:
            query = query.where(ReimbursementClaim.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(desc(ReimbursementClaim.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        claims = result.scalars().all()
        
        return claims, total
    
    # ========================================================================
    # PROFILE UPDATE OPERATIONS
    # ========================================================================
    
    async def get_employee_profile(self) -> Employee:
        """Get employee profile"""
        query = select(Employee).where(
            and_(
                Employee.id == self.employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_deleted == False
            )
        ).options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.reporting_manager)
        )
        
        result = await self.db.execute(query)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValueError("Employee not found")
        
        return employee
    
    async def update_employee_profile(
        self, 
        data: EmployeeProfileUpdateRequest
    ) -> Employee:
        """Update employee profile (limited fields)"""
        
        employee = await self.get_employee_profile()
        
        # Update allowed fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(employee, field):
                setattr(employee, field, value)
        
        employee.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(employee)
        
        return employee
    
    # ========================================================================
    # DASHBOARD OPERATIONS
    # ========================================================================
    
    async def get_ess_dashboard_stats(self) -> ESSDashboardStats:
        """Get ESS dashboard statistics"""
        
        stats = ESSDashboardStats()
        
        # Leave balance summary
        leave_balances = await self.get_leave_balances()
        stats.total_leave_balance = sum(lb.current_balance for lb in leave_balances)
        
        # Pending leave applications
        pending_leaves_query = select(func.count(LeaveApplication.id)).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.employee_id == self.employee_id,
                LeaveApplication.status == LeaveStatus.PENDING_APPROVAL,
                LeaveApplication.is_deleted == False
            )
        )
        result = await self.db.execute(pending_leaves_query)
        stats.pending_leave_applications = result.scalar() or 0
        
        return stats
