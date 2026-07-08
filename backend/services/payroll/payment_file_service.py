"""
Payment File Service
Handles bank payment file generation (NEFT, RTGS, CSV, Excel)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import csv
import io
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.shared.database.payroll_models import (
    PaymentFile, PaymentFileFormat, PaymentFileStatus, PayrollRun, Payslip
)
from backend.shared.database.hrms_models import Employee
from backend.services.payroll.schemas import (
    PaymentFileCreate, PaymentFileUpdate, PaymentFileResponse, PaymentFileList
)


class PaymentFileService:
    """Service for payment file generation and management"""
    
    @staticmethod
    async def create_payment_file(
        db: AsyncSession,
        tenant_id: str,
        payment_file_data: PaymentFileCreate,
        user_id: str
    ) -> PaymentFileResponse:
        """Create a new payment file record"""
        
        # Generate payment file code
        current_month = datetime.now().strftime("%Y%m")
        result = await db.execute(
            select(func.count(PaymentFile.id))
            .where(
                and_(
                    PaymentFile.tenant_id == tenant_id,
                    PaymentFile.payment_file_code.like(f"PAY-{current_month}-%"),
                    PaymentFile.is_deleted == False
                )
            )
        )
        count = result.scalar() or 0
        payment_file_code = f"PAY-{current_month}-{str(count + 1).zfill(4)}"
        
        # Create payment file
        payment_file = PaymentFile(
            tenant_id=tenant_id,
            payment_file_code=payment_file_code,
            payroll_run_id=payment_file_data.payroll_run_id,
            file_format=payment_file_data.file_format,
            total_employees=payment_file_data.total_employees,
            total_amount=payment_file_data.total_amount,
            file_path=payment_file_data.file_path,
            file_name=payment_file_data.file_name,
            status=payment_file_data.status or PaymentFileStatus.GENERATED,
            uploaded_date=payment_file_data.uploaded_date,
            uploaded_by=payment_file_data.uploaded_by,
            remarks=payment_file_data.remarks,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(payment_file)
        await db.commit()
        await db.refresh(payment_file)
        
        return PaymentFileResponse.model_validate(payment_file)
    
    @staticmethod
    async def get_payment_file(
        db: AsyncSession,
        tenant_id: str,
        payment_file_id: int
    ) -> Optional[PaymentFileResponse]:
        """Get payment file by ID"""
        
        result = await db.execute(
            select(PaymentFile)
            .options(selectinload(PaymentFile.payroll_run))
            .where(
                and_(
                    PaymentFile.id == payment_file_id,
                    PaymentFile.tenant_id == tenant_id,
                    PaymentFile.is_deleted == False
                )
            )
        )
        payment_file = result.scalar_one_or_none()
        
        if not payment_file:
            return None
        
        return PaymentFileResponse.model_validate(payment_file)
    
    @staticmethod
    async def list_payment_files(
        db: AsyncSession,
        tenant_id: str,
        payroll_run_id: Optional[int] = None,
        file_format: Optional[PaymentFileFormat] = None,
        status: Optional[PaymentFileStatus] = None,
        page: int = 1,
        page_size: int = 50
    ) -> PaymentFileList:
        """List payment files with filters"""
        
        # Build query
        query = select(PaymentFile).where(
            and_(
                PaymentFile.tenant_id == tenant_id,
                PaymentFile.is_deleted == False
            )
        )
        
        # Apply filters
        if payroll_run_id:
            query = query.where(PaymentFile.payroll_run_id == payroll_run_id)
        
        if file_format:
            query = query.where(PaymentFile.file_format == file_format)
        
        if status:
            query = query.where(PaymentFile.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(PaymentFile.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        payment_files = result.scalars().all()
        
        return PaymentFileList(
            items=[PaymentFileResponse.model_validate(pf) for pf in payment_files],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    @staticmethod
    async def update_payment_file(
        db: AsyncSession,
        tenant_id: str,
        payment_file_id: int,
        payment_file_data: PaymentFileUpdate,
        user_id: str
    ) -> Optional[PaymentFileResponse]:
        """Update payment file record"""
        
        result = await db.execute(
            select(PaymentFile)
            .where(
                and_(
                    PaymentFile.id == payment_file_id,
                    PaymentFile.tenant_id == tenant_id,
                    PaymentFile.is_deleted == False
                )
            )
        )
        payment_file = result.scalar_one_or_none()
        
        if not payment_file:
            return None
        
        # Update fields
        update_data = payment_file_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment_file, field, value)
        
        payment_file.updated_by = user_id
        payment_file.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(payment_file)
        
        return PaymentFileResponse.model_validate(payment_file)
    
    @staticmethod
    async def generate_payment_file(
        db: AsyncSession,
        tenant_id: str,
        payroll_run_id: int,
        file_format: PaymentFileFormat,
        user_id: str
    ) -> PaymentFileResponse:
        """Generate payment file for a payroll run"""
        
        # Get payroll run
        run_result = await db.execute(
            select(PayrollRun)
            .where(
                and_(
                    PayrollRun.id == payroll_run_id,
                    PayrollRun.tenant_id == tenant_id,
                    PayrollRun.is_deleted == False
                )
            )
        )
        payroll_run = run_result.scalar_one_or_none()
        
        if not payroll_run:
            raise ValueError("Payroll run not found")
        
        # Get all payslips for this run with employee details
        payslip_result = await db.execute(
            select(Payslip, Employee)
            .join(Employee, Payslip.employee_id == Employee.id)
            .where(
                and_(
                    Payslip.payroll_run_id == payroll_run_id,
                    Payslip.tenant_id == tenant_id,
                    Payslip.is_deleted == False,
                    Employee.is_deleted == False
                )
            )
        )
        payslip_data = payslip_result.all()
        
        # Generate file content based on format
        if file_format == PaymentFileFormat.NEFT:
            file_content = PaymentFileService._generate_neft_format(payslip_data)
            file_extension = "txt"
        elif file_format == PaymentFileFormat.RTGS:
            file_content = PaymentFileService._generate_rtgs_format(payslip_data)
            file_extension = "txt"
        elif file_format == PaymentFileFormat.CSV:
            file_content = PaymentFileService._generate_csv_format(payslip_data)
            file_extension = "csv"
        elif file_format == PaymentFileFormat.EXCEL:
            file_content = PaymentFileService._generate_excel_format(payslip_data)
            file_extension = "xlsx"
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        # Generate file name
        month_year = f"{payroll_run.month:02d}{payroll_run.year}"
        file_name = f"salary_payment_{month_year}_{file_format.value}.{file_extension}"
        
        # Calculate totals
        total_employees = len(payslip_data)
        total_amount = sum(p[0].net_salary for p in payslip_data)
        
        # In a real implementation, you would save the file to storage
        # For now, we'll just store the file path
        file_path = f"/payments/{file_name}"
        
        # Create payment file record
        payment_file_data = PaymentFileCreate(
            payroll_run_id=payroll_run_id,
            file_format=file_format,
            total_employees=total_employees,
            total_amount=total_amount,
            file_path=file_path,
            file_name=file_name,
            status=PaymentFileStatus.GENERATED
        )
        
        return await PaymentFileService.create_payment_file(
            db, tenant_id, payment_file_data, user_id
        )
    
    @staticmethod
    def _generate_neft_format(payslip_data: List[tuple]) -> str:
        """Generate NEFT format file content"""
        lines = []
        
        # Header
        lines.append("H|NEFT|SALARY_PAYMENT|" + datetime.now().strftime("%Y%m%d"))
        
        # Detail lines
        for idx, (payslip, employee) in enumerate(payslip_data, 1):
            # NEFT format: D|SeqNo|BenefName|BenefAccNo|BenefIFSC|Amount|Remarks
            line = f"D|{idx}|{employee.first_name} {employee.last_name}|{employee.bank_account_number}|{employee.bank_ifsc}|{payslip.net_salary}|SALARY_{payslip.payslip_code}"
            lines.append(line)
        
        # Trailer
        total_amount = sum(p[0].net_salary for p in payslip_data)
        lines.append(f"T|{len(payslip_data)}|{total_amount}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _generate_rtgs_format(payslip_data: List[tuple]) -> str:
        """Generate RTGS format file content"""
        lines = []
        
        # RTGS is similar to NEFT but with higher transaction amounts
        # Header
        lines.append("H|RTGS|SALARY_PAYMENT|" + datetime.now().strftime("%Y%m%d"))
        
        # Detail lines
        for idx, (payslip, employee) in enumerate(payslip_data, 1):
            # Only include employees with net salary >= 2 lakhs (RTGS minimum)
            if payslip.net_salary >= 200000:
                line = f"D|{idx}|{employee.first_name} {employee.last_name}|{employee.bank_account_number}|{employee.bank_ifsc}|{payslip.net_salary}|SALARY_{payslip.payslip_code}"
                lines.append(line)
        
        # Trailer
        rtgs_payslips = [p for p in payslip_data if p[0].net_salary >= 200000]
        total_amount = sum(p[0].net_salary for p in rtgs_payslips)
        lines.append(f"T|{len(rtgs_payslips)}|{total_amount}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _generate_csv_format(payslip_data: List[tuple]) -> str:
        """Generate CSV format file content"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Employee Code', 'Employee Name', 'Bank Account Number', 
            'Bank IFSC', 'Bank Name', 'Net Salary', 'Payslip Code', 'Remarks'
        ])
        
        # Data rows
        for payslip, employee in payslip_data:
            writer.writerow([
                employee.employee_code,
                f"{employee.first_name} {employee.last_name}",
                employee.bank_account_number,
                employee.bank_ifsc,
                employee.bank_name,
                float(payslip.net_salary),
                payslip.payslip_code,
                f"Salary for {payslip.month}/{payslip.year}"
            ])
        
        return output.getvalue()
    
    @staticmethod
    def _generate_excel_format(payslip_data: List[tuple]) -> bytes:
        """Generate Excel format file content"""
        # In a real implementation, you would use openpyxl or xlsxwriter
        # For now, returning CSV content as placeholder
        csv_content = PaymentFileService._generate_csv_format(payslip_data)
        return csv_content.encode('utf-8')
    
    @staticmethod
    async def update_upload_status(
        db: AsyncSession,
        tenant_id: str,
        payment_file_id: int,
        status: PaymentFileStatus,
        uploaded_by: Optional[str] = None,
        remarks: Optional[str] = None,
        user_id: str = None
    ) -> Optional[PaymentFileResponse]:
        """Update payment file upload status"""
        
        result = await db.execute(
            select(PaymentFile)
            .where(
                and_(
                    PaymentFile.id == payment_file_id,
                    PaymentFile.tenant_id == tenant_id,
                    PaymentFile.is_deleted == False
                )
            )
        )
        payment_file = result.scalar_one_or_none()
        
        if not payment_file:
            return None
        
        # Update status
        payment_file.status = status
        
        if status == PaymentFileStatus.UPLOADED:
            payment_file.uploaded_date = datetime.utcnow().date()
            if uploaded_by:
                payment_file.uploaded_by = uploaded_by
        
        if remarks:
            payment_file.remarks = remarks
        
        payment_file.updated_by = user_id
        payment_file.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(payment_file)
        
        return PaymentFileResponse.model_validate(payment_file)
    
    @staticmethod
    async def delete_payment_file(
        db: AsyncSession,
        tenant_id: str,
        payment_file_id: int,
        user_id: str
    ) -> bool:
        """Soft delete payment file"""
        
        result = await db.execute(
            select(PaymentFile)
            .where(
                and_(
                    PaymentFile.id == payment_file_id,
                    PaymentFile.tenant_id == tenant_id,
                    PaymentFile.is_deleted == False
                )
            )
        )
        payment_file = result.scalar_one_or_none()
        
        if not payment_file:
            return False
        
        # Can only delete if not uploaded
        if payment_file.status == PaymentFileStatus.UPLOADED:
            return False
        
        payment_file.is_deleted = True
        payment_file.updated_by = user_id
        payment_file.updated_at = datetime.utcnow()
        
        await db.commit()
        return True
