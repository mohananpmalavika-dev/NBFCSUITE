"""
Statutory Compliance Service
Handles PF, ESI, PT, TDS compliance record management and reporting
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import select, and_, or_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.payroll_models import (
    StatutoryCompliance, StatutoryType, PaymentStatus
)
from backend.services.payroll.schemas import (
    StatutoryComplianceCreate, StatutoryComplianceUpdate,
    StatutoryComplianceResponse, StatutoryComplianceList
)


class StatutoryComplianceService:
    """Service for statutory compliance management"""
    
    @staticmethod
    async def create_compliance(
        db: AsyncSession,
        tenant_id: str,
        compliance_data: StatutoryComplianceCreate,
        user_id: str
    ) -> StatutoryComplianceResponse:
        """Create a new compliance record"""
        
        # Generate compliance code
        current_month = datetime.now().strftime("%Y%m")
        result = await db.execute(
            select(func.count(StatutoryCompliance.id))
            .where(
                and_(
                    StatutoryCompliance.tenant_id == tenant_id,
                    StatutoryCompliance.compliance_code.like(f"COMP-{current_month}-%"),
                    StatutoryCompliance.is_deleted == False
                )
            )
        )
        count = result.scalar() or 0
        compliance_code = f"COMP-{current_month}-{str(count + 1).zfill(4)}"
        
        # Create compliance record
        compliance = StatutoryCompliance(
            tenant_id=tenant_id,
            compliance_code=compliance_code,
            statutory_type=compliance_data.statutory_type,
            month=compliance_data.month,
            year=compliance_data.year,
            payroll_run_id=compliance_data.payroll_run_id,
            employee_contribution=compliance_data.employee_contribution,
            employer_contribution=compliance_data.employer_contribution,
            total_amount=compliance_data.total_amount,
            challan_number=compliance_data.challan_number,
            payment_date=compliance_data.payment_date,
            payment_status=compliance_data.payment_status or PaymentStatus.PENDING,
            due_date=compliance_data.due_date,
            bank_name=compliance_data.bank_name,
            bank_branch=compliance_data.bank_branch,
            remarks=compliance_data.remarks,
            created_by=user_id,
            updated_by=user_id
        )
        
        db.add(compliance)
        await db.commit()
        await db.refresh(compliance)
        
        return StatutoryComplianceResponse.model_validate(compliance)
    
    @staticmethod
    async def get_compliance(
        db: AsyncSession,
        tenant_id: str,
        compliance_id: int
    ) -> Optional[StatutoryComplianceResponse]:
        """Get compliance record by ID"""
        
        result = await db.execute(
            select(StatutoryCompliance)
            .where(
                and_(
                    StatutoryCompliance.id == compliance_id,
                    StatutoryCompliance.tenant_id == tenant_id,
                    StatutoryCompliance.is_deleted == False
                )
            )
        )
        compliance = result.scalar_one_or_none()
        
        if not compliance:
            return None
        
        return StatutoryComplianceResponse.model_validate(compliance)
    
    @staticmethod
    async def list_compliance(
        db: AsyncSession,
        tenant_id: str,
        statutory_type: Optional[StatutoryType] = None,
        payment_status: Optional[PaymentStatus] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        payroll_run_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50
    ) -> StatutoryComplianceList:
        """List compliance records with filters"""
        
        # Build query
        query = select(StatutoryCompliance).where(
            and_(
                StatutoryCompliance.tenant_id == tenant_id,
                StatutoryCompliance.is_deleted == False
            )
        )
        
        # Apply filters
        if statutory_type:
            query = query.where(StatutoryCompliance.statutory_type == statutory_type)
        
        if payment_status:
            query = query.where(StatutoryCompliance.payment_status == payment_status)
        
        if month:
            query = query.where(StatutoryCompliance.month == month)
        
        if year:
            query = query.where(StatutoryCompliance.year == year)
        
        if payroll_run_id:
            query = query.where(StatutoryCompliance.payroll_run_id == payroll_run_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.order_by(StatutoryCompliance.year.desc(), StatutoryCompliance.month.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        compliance_records = result.scalars().all()
        
        return StatutoryComplianceList(
            items=[StatutoryComplianceResponse.model_validate(c) for c in compliance_records],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )
    
    @staticmethod
    async def update_compliance(
        db: AsyncSession,
        tenant_id: str,
        compliance_id: int,
        compliance_data: StatutoryComplianceUpdate,
        user_id: str
    ) -> Optional[StatutoryComplianceResponse]:
        """Update compliance record"""
        
        result = await db.execute(
            select(StatutoryCompliance)
            .where(
                and_(
                    StatutoryCompliance.id == compliance_id,
                    StatutoryCompliance.tenant_id == tenant_id,
                    StatutoryCompliance.is_deleted == False
                )
            )
        )
        compliance = result.scalar_one_or_none()
        
        if not compliance:
            return None
        
        # Update fields
        update_data = compliance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(compliance, field, value)
        
        compliance.updated_by = user_id
        compliance.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(compliance)
        
        return StatutoryComplianceResponse.model_validate(compliance)
    
    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        tenant_id: str,
        compliance_id: int,
        challan_number: str,
        payment_date: date,
        payment_status: PaymentStatus,
        bank_name: Optional[str] = None,
        bank_branch: Optional[str] = None,
        remarks: Optional[str] = None,
        user_id: str = None
    ) -> Optional[StatutoryComplianceResponse]:
        """Update payment details and status"""
        
        result = await db.execute(
            select(StatutoryCompliance)
            .where(
                and_(
                    StatutoryCompliance.id == compliance_id,
                    StatutoryCompliance.tenant_id == tenant_id,
                    StatutoryCompliance.is_deleted == False
                )
            )
        )
        compliance = result.scalar_one_or_none()
        
        if not compliance:
            return None
        
        # Update payment details
        compliance.challan_number = challan_number
        compliance.payment_date = payment_date
        compliance.payment_status = payment_status
        
        if bank_name:
            compliance.bank_name = bank_name
        if bank_branch:
            compliance.bank_branch = bank_branch
        if remarks:
            compliance.remarks = remarks
        
        compliance.updated_by = user_id
        compliance.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(compliance)
        
        return StatutoryComplianceResponse.model_validate(compliance)
    
    @staticmethod
    async def get_compliance_summary(
        db: AsyncSession,
        tenant_id: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get compliance summary for a month"""
        
        result = await db.execute(
            select(
                StatutoryCompliance.statutory_type,
                StatutoryCompliance.payment_status,
                func.sum(StatutoryCompliance.employee_contribution).label('total_employee'),
                func.sum(StatutoryCompliance.employer_contribution).label('total_employer'),
                func.sum(StatutoryCompliance.total_amount).label('total_amount'),
                func.count(StatutoryCompliance.id).label('count')
            )
            .where(
                and_(
                    StatutoryCompliance.tenant_id == tenant_id,
                    StatutoryCompliance.month == month,
                    StatutoryCompliance.year == year,
                    StatutoryCompliance.is_deleted == False
                )
            )
            .group_by(StatutoryCompliance.statutory_type, StatutoryCompliance.payment_status)
        )
        
        summary_data = result.all()
        
        # Build summary by statutory type
        summary = {}
        for row in summary_data:
            stat_type = row.statutory_type.value
            if stat_type not in summary:
                summary[stat_type] = {
                    'total_employee_contribution': Decimal('0.00'),
                    'total_employer_contribution': Decimal('0.00'),
                    'total_amount': Decimal('0.00'),
                    'payment_status': {}
                }
            
            summary[stat_type]['total_employee_contribution'] += (row.total_employee or Decimal('0.00'))
            summary[stat_type]['total_employer_contribution'] += (row.total_employer or Decimal('0.00'))
            summary[stat_type]['total_amount'] += (row.total_amount or Decimal('0.00'))
            
            status = row.payment_status.value
            summary[stat_type]['payment_status'][status] = {
                'count': row.count,
                'amount': float(row.total_amount or Decimal('0.00'))
            }
        
        return {
            'month': month,
            'year': year,
            'summary': summary
        }
    
    @staticmethod
    async def get_pending_payments(
        db: AsyncSession,
        tenant_id: str,
        due_before: Optional[date] = None
    ) -> List[StatutoryComplianceResponse]:
        """Get pending compliance payments"""
        
        query = select(StatutoryCompliance).where(
            and_(
                StatutoryCompliance.tenant_id == tenant_id,
                StatutoryCompliance.payment_status == PaymentStatus.PENDING,
                StatutoryCompliance.is_deleted == False
            )
        )
        
        if due_before:
            query = query.where(StatutoryCompliance.due_date <= due_before)
        
        query = query.order_by(StatutoryCompliance.due_date.asc())
        
        result = await db.execute(query)
        compliance_records = result.scalars().all()
        
        return [StatutoryComplianceResponse.model_validate(c) for c in compliance_records]
    
    @staticmethod
    async def delete_compliance(
        db: AsyncSession,
        tenant_id: str,
        compliance_id: int,
        user_id: str
    ) -> bool:
        """Soft delete compliance record"""
        
        result = await db.execute(
            select(StatutoryCompliance)
            .where(
                and_(
                    StatutoryCompliance.id == compliance_id,
                    StatutoryCompliance.tenant_id == tenant_id,
                    StatutoryCompliance.is_deleted == False
                )
            )
        )
        compliance = result.scalar_one_or_none()
        
        if not compliance:
            return False
        
        # Can only delete if payment is not completed
        if compliance.payment_status == PaymentStatus.PAID:
            return False
        
        compliance.is_deleted = True
        compliance.updated_by = user_id
        compliance.updated_at = datetime.utcnow()
        
        await db.commit()
        return True
