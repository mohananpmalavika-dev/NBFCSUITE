"""
TDS Service
Tax Deducted at Source - Calculation, Deduction, Challan, Certificate, Returns
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.accounting_extended_models import (
    TDSSectionMaster,
    TDSDeduction,
    TDSChallan,
    TDSCertificate,
    TDSReturn,
    TDSSection,
    TDSPaymentStatus,
    TDSReturnStatus,
    TDSCertificateStatus,
    TDSReturnType
)


class TDSService:
    """Service for TDS operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # TDS Section Master Management
    # ========================================================================
    
    async def create_tds_section(
        self,
        section_code: TDSSection,
        section_name: str,
        financial_year: int,
        tds_rate: Decimal,
        threshold_limit: Optional[Decimal] = None,
        rate_without_pan: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> TDSSectionMaster:
        """Create or update TDS section configuration"""
        
        # Check if exists
        query = select(TDSSectionMaster).where(
            and_(
                TDSSectionMaster.tenant_id == self.tenant_id,
                TDSSectionMaster.section_code == section_code,
                TDSSectionMaster.financial_year == financial_year
            )
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
    
    async def generate_deduction_number(self) -> str:
        """Generate unique TDS deduction number"""
        now = datetime.now()
        prefix = f"TDS-{now.year}{now.month:02d}"
        
        query = select(TDSDeduction).where(
            and_(
                TDSDeduction.tenant_id == self.tenant_id,
                TDSDeduction.deduction_number.like(f"{prefix}-%")
            )
        ).order_by(desc(TDSDeduction.deduction_number)).limit(1)
        
        result = await self.db.execute(query)
        last_deduction = result.scalar_one_or_none()
        
        if last_deduction:
            last_number = int(last_deduction.deduction_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:05d}"
    
    async def record_tds_deduction(
        self,
        section_code: TDSSection,
        deduction_date: date,
        deductee_type: str,
        deductee_id: int,
        deductee_name: str,
        deductee_pan: Optional[str],
        transaction_type: str,
        transaction_id: int,
        gross_amount: Decimal,
        invoice_number: Optional[str] = None
    ) -> TDSDeduction:
        """Record TDS deduction"""
        
        # Get financial year and quarter
        financial_year = deduction_date.year if deduction_date.month >= 4 else deduction_date.year - 1
        
        # Determine quarter
        month = deduction_date.month
        if 4 <= month <= 6:
            quarter = 1
        elif 7 <= month <= 9:
            quarter = 2
        elif 10 <= month <= 12:
            quarter = 3
        else:
            quarter = 4
        
        # Calculate TDS
        tds_calc = await self.calculate_tds(
            section_code=section_code,
            gross_amount=gross_amount,
            financial_year=financial_year,
            has_pan=bool(deductee_pan)
        )
        
        # Skip if below threshold
        if tds_calc["below_threshold"]:
            return None
        
        # Get section master
        section = await self.get_tds_section(section_code, financial_year)
        
        # Generate deduction number
        deduction_number = await self.generate_deduction_number()
        
        # Create deduction record
        deduction = TDSDeduction(
            tenant_id=self.tenant_id,
            deduction_number=deduction_number,
            deduction_date=deduction_date,
            financial_year=financial_year,
            quarter=quarter,
            section_id=section.id,
            section_code=section_code,
            deductee_type=deductee_type,
            deductee_id=deductee_id,
            deductee_name=deductee_name,
            deductee_pan=deductee_pan,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            transaction_date=deduction_date,
            invoice_number=invoice_number,
            gross_amount=gross_amount,
            tds_rate=Decimal(str(tds_calc["tds_rate"])),
            tds_amount=Decimal(str(tds_calc["tds_amount"])),
            surcharge=Decimal(str(tds_calc["surcharge"])),
            cess=Decimal(str(tds_calc["cess"])),
            total_tds=Decimal(str(tds_calc["total_tds"])),
            net_amount=Decimal(str(tds_calc["net_amount"])),
            payment_status=TDSPaymentStatus.PENDING,
            created_by=self.user_id
        )
        
        self.db.add(deduction)
        await self.db.commit()
        await self.db.refresh(deduction)
        
        return deduction
    
    async def list_tds_deductions(
        self,
        financial_year: Optional[int] = None,
        quarter: Optional[int] = None,
        section_code: Optional[TDSSection] = None,
        payment_status: Optional[TDSPaymentStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[TDSDeduction], int]:
        """List TDS deductions"""
        conditions = [
            TDSDeduction.tenant_id == self.tenant_id,
            TDSDeduction.is_deleted == False
        ]
        
        if financial_year:
            conditions.append(TDSDeduction.financial_year == financial_year)
        if quarter:
            conditions.append(TDSDeduction.quarter == quarter)
        if section_code:
            conditions.append(TDSDeduction.section_code == section_code)
        if payment_status:
            conditions.append(TDSDeduction.payment_status == payment_status)
        if from_date:
            conditions.append(TDSDeduction.deduction_date >= from_date)
        if to_date:
            conditions.append(TDSDeduction.deduction_date <= to_date)
        
        # Count
        count_query = select(func.count(TDSDeduction.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get deductions
        query = select(TDSDeduction).where(and_(*conditions)).order_by(
            desc(TDSDeduction.deduction_date)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        deductions = result.scalars().all()
        
        return deductions, total
    
    # ========================================================================
    # TDS Challan Management
    # ========================================================================
    
    async def generate_challan_number(self) -> str:
        """Generate unique challan number"""
        now = datetime.now()
        prefix = f"CHAL-{now.year}"
        
        query = select(TDSChallan).where(
            and_(
                TDSChallan.tenant_id == self.tenant_id,
                TDSChallan.challan_number.like(f"{prefix}-%")
            )
        ).order_by(desc(TDSChallan.challan_number)).limit(1)
        
        result = await self.db.execute(query)
        last_challan = result.scalar_one_or_none()
        
        if last_challan:
            last_number = int(last_challan.challan_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:05d}"
    
    async def create_tds_challan(
        self,
        financial_year: int,
        quarter: int,
        section_code: TDSSection,
        payment_date: date,
        bsr_code: str,
        bank_name: str,
        total_tds_amount: Decimal,
        payment_mode: str = "online",
        cheque_number: Optional[str] = None,
        transaction_reference: Optional[str] = None,
        deduction_ids: Optional[List[int]] = None
    ) -> TDSChallan:
        """Create TDS payment challan"""
        
        # Generate challan number
        challan_number = await self.generate_challan_number()
        
        # Calculate assessment year
        assessment_year = f"{financial_year + 1}-{str(financial_year + 2)[-2:]}"
        
        # Create challan
        challan = TDSChallan(
            tenant_id=self.tenant_id,
            challan_number=challan_number,
            bsr_code=bsr_code,
            challan_date=payment_date,
            payment_date=payment_date,
            financial_year=financial_year,
            quarter=quarter,
            assessment_year=assessment_year,
            section_code=section_code,
            bank_name=bank_name,
            total_tds_amount=total_tds_amount,
            interest_amount=Decimal("0.00"),
            penalty_amount=Decimal("0.00"),
            total_amount=total_tds_amount,
            payment_mode=payment_mode,
            cheque_number=cheque_number,
            transaction_reference=transaction_reference,
            payment_status=TDSPaymentStatus.PAID,
            created_by=self.user_id
        )
        
        self.db.add(challan)
        await self.db.flush()
        
        # Link deductions to challan
        if deduction_ids:
            for deduction_id in deduction_ids:
                deduction_query = select(TDSDeduction).where(
                    and_(
                        TDSDeduction.id == deduction_id,
                        TDSDeduction.tenant_id == self.tenant_id
                    )
                )
                result = await self.db.execute(deduction_query)
                deduction = result.scalar_one_or_none()
                
                if deduction:
                    deduction.challan_id = challan.id
                    deduction.payment_status = TDSPaymentStatus.PAID
        
        await self.db.commit()
        await self.db.refresh(challan)
        
        return challan
    
    async def get_pending_deductions_for_challan(
        self,
        financial_year: int,
        quarter: int,
        section_code: Optional[TDSSection] = None
    ) -> List[TDSDeduction]:
        """Get pending TDS deductions for challan payment"""
        conditions = [
            TDSDeduction.tenant_id == self.tenant_id,
            TDSDeduction.financial_year == financial_year,
            TDSDeduction.quarter == quarter,
            TDSDeduction.payment_status == TDSPaymentStatus.PENDING,
            TDSDeduction.is_deleted == False
        ]
        
        if section_code:
            conditions.append(TDSDeduction.section_code == section_code)
        
        query = select(TDSDeduction).where(and_(*conditions)).order_by(
            TDSDeduction.deduction_date
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # ========================================================================
    # TDS Certificate Generation (Form 16A)
    # ========================================================================
    
    async def generate_certificate_number(self) -> str:
        """Generate unique certificate number"""
        now = datetime.now()
        prefix = f"CERT-{now.year}"
        
        query = select(TDSCertificate).where(
            and_(
                TDSCertificate.tenant_id == self.tenant_id,
                TDSCertificate.certificate_number.like(f"{prefix}-%")
            )
        ).order_by(desc(TDSCertificate.certificate_number)).limit(1)
        
        result = await self.db.execute(query)
        last_cert = result.scalar_one_or_none()
        
        if last_cert:
            last_number = int(last_cert.certificate_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:06d}"
    
    async def generate_tds_certificate(
        self,
        financial_year: int,
        quarter: int,
        deductee_id: int,
        deductee_type: str,
        deductee_name: str,
        deductee_pan: str,
        deductee_address: Optional[str],
        deductor_tan: str,
        deductor_pan: str,
        deductor_name: str
    ) -> TDSCertificate:
        """Generate TDS Certificate (Form 16A)"""
        
        # Determine period dates
        if quarter == 1:
            from_date = date(financial_year, 4, 1)
            to_date = date(financial_year, 6, 30)
        elif quarter == 2:
            from_date = date(financial_year, 7, 1)
            to_date = date(financial_year, 9, 30)
        elif quarter == 3:
            from_date = date(financial_year, 10, 1)
            to_date = date(financial_year, 12, 31)
        else:  # quarter 4
            from_date = date(financial_year + 1, 1, 1)
            to_date = date(financial_year + 1, 3, 31)
        
        # Get all deductions for this deductee in this quarter
        query = select(TDSDeduction).where(
            and_(
                TDSDeduction.tenant_id == self.tenant_id,
                TDSDeduction.financial_year == financial_year,
                TDSDeduction.quarter == quarter,
                TDSDeduction.deductee_id == deductee_id,
                TDSDeduction.deductee_type == deductee_type,
                TDSDeduction.payment_status == TDSPaymentStatus.PAID,
                TDSDeduction.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        deductions = result.scalars().all()
        
        if not deductions:
            raise ValueError("No paid TDS deductions found for certificate generation")
        
        # Calculate totals
        total_gross = sum(d.gross_amount for d in deductions)
        total_tds = sum(d.total_tds for d in deductions)
        
        # Generate certificate number
        certificate_number = await self.generate_certificate_number()
        
        # Create certificate
        certificate = TDSCertificate(
            tenant_id=self.tenant_id,
            certificate_number=certificate_number,
            issue_date=date.today(),
            financial_year=financial_year,
            quarter=quarter,
            from_date=from_date,
            to_date=to_date,
            deductee_type=deductee_type,
            deductee_id=deductee_id,
            deductee_name=deductee_name,
            deductee_pan=deductee_pan,
            deductee_address=deductee_address,
            deductor_tan=deductor_tan,
            deductor_pan=deductor_pan,
            deductor_name=deductor_name,
            total_gross_amount=total_gross,
            total_tds_amount=total_tds,
            status=TDSCertificateStatus.GENERATED,
            created_by=self.user_id
        )
        
        self.db.add(certificate)
        await self.db.flush()
        
        # Link deductions to certificate
        for deduction in deductions:
            deduction.certificate_id = certificate.id
        
        await self.db.commit()
        await self.db.refresh(certificate)
        
        return certificate
    
    # ========================================================================
    # TDS Return Preparation (Form 26Q)
    # ========================================================================
    
    async def prepare_tds_return(
        self,
        financial_year: int,
        quarter: int,
        return_type: TDSReturnType = TDSReturnType.FORM_26Q
    ) -> TDSReturn:
        """Prepare TDS return for filing"""
        
        # Determine period dates
        if quarter == 1:
            from_date = date(financial_year, 4, 1)
            to_date = date(financial_year, 6, 30)
        elif quarter == 2:
            from_date = date(financial_year, 7, 1)
            to_date = date(financial_year, 9, 30)
        elif quarter == 3:
            from_date = date(financial_year, 10, 1)
            to_date = date(financial_year, 12, 31)
        else:  # quarter 4
            from_date = date(financial_year + 1, 1, 1)
            to_date = date(financial_year + 1, 3, 31)
        
        # Calculate due date (typically 31 days after quarter end)
        from dateutil.relativedelta import relativedelta
        due_date = to_date + relativedelta(days=31)
        
        # Get all deductions for this quarter
        query = select(TDSDeduction).where(
            and_(
                TDSDeduction.tenant_id == self.tenant_id,
                TDSDeduction.financial_year == financial_year,
                TDSDeduction.quarter == quarter,
                TDSDeduction.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        deductions = result.scalars().all()
        
        # Calculate totals
        total_deductions_count = len(deductions)
        total_gross = sum(d.gross_amount for d in deductions)
        total_tds = sum(d.total_tds for d in deductions)
        
        # Generate return number
        return_number = f"TDS-RET-{financial_year}-Q{quarter}"
        
        # Create return
        tds_return = TDSReturn(
            tenant_id=self.tenant_id,
            return_number=return_number,
            return_type=return_type,
            financial_year=financial_year,
            quarter=quarter,
            from_date=from_date,
            to_date=to_date,
            due_date=due_date,
            total_deductions=total_deductions_count,
            total_gross_amount=total_gross,
            total_tds_amount=total_tds,
            status=TDSReturnStatus.DRAFT,
            created_by=self.user_id
        )
        
        self.db.add(tds_return)
        await self.db.commit()
        await self.db.refresh(tds_return)
        
        return tds_return
    
    # ========================================================================
    # Reporting
    # ========================================================================
    
    async def get_tds_summary(
        self,
        financial_year: int,
        quarter: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get TDS summary for a period"""
        conditions = [
            TDSDeduction.tenant_id == self.tenant_id,
            TDSDeduction.financial_year == financial_year,
            TDSDeduction.is_deleted == False
        ]
        
        if quarter:
            conditions.append(TDSDeduction.quarter == quarter)
        
        # Get section-wise summary
        query = select(
            TDSDeduction.section_code,
            func.count(TDSDeduction.id).label("count"),
            func.sum(TDSDeduction.gross_amount).label("total_gross"),
            func.sum(TDSDeduction.total_tds).label("total_tds")
        ).where(and_(*conditions)).group_by(TDSDeduction.section_code)
        
        result = await self.db.execute(query)
        section_wise = []
        
        for row in result:
            section_wise.append({
                "section_code": row.section_code,
                "deduction_count": row.count,
                "total_gross_amount": float(row.total_gross or 0),
                "total_tds_amount": float(row.total_tds or 0)
            })
        
        # Get overall totals
        total_query = select(
            func.count(TDSDeduction.id).label("count"),
            func.sum(TDSDeduction.gross_amount).label("total_gross"),
            func.sum(TDSDeduction.total_tds).label("total_tds")
        ).where(and_(*conditions))
        
        total_result = await self.db.execute(total_query)
        totals = total_result.first()
        
        # Get payment status summary
        status_query = select(
            TDSDeduction.payment_status,
            func.count(TDSDeduction.id).label("count"),
            func.sum(TDSDeduction.total_tds).label("total_tds")
        ).where(and_(*conditions)).group_by(TDSDeduction.payment_status)
        
        status_result = await self.db.execute(status_query)
        payment_status = []
        
        for row in status_result:
            payment_status.append({
                "status": row.payment_status,
                "count": row.count,
                "amount": float(row.total_tds or 0)
            })
        
        return {
            "financial_year": financial_year,
            "quarter": quarter,
            "total_deductions": totals.count or 0,
            "total_gross_amount": float(totals.total_gross or 0),
            "total_tds_amount": float(totals.total_tds or 0),
            "section_wise_summary": section_wise,
            "payment_status_summary": payment_status
        }
