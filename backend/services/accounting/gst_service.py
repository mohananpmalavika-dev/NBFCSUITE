"""
GST Service
Goods & Services Tax - Calculation, ITC, Returns (GSTR-1, GSTR-3B)
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.accounting_extended_models import (
    GSTConfiguration,
    GSTTransaction,
    GSTInputCredit,
    GSTReturn,
    HSNSACMaster,
    GSTTransactionType,
    GSTReturnType,
    GSTReturnStatus
)


class GSTService:
    """Service for GST operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # GST Configuration
    # ========================================================================
    
    async def create_gst_configuration(
        self,
        gstin: str,
        legal_name: str,
        state_code: str,
        state_name: str,
        address: str,
        pincode: str,
        registration_date: date,
        registration_type: str = "regular",
        trade_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> GSTConfiguration:
        """Create GST configuration"""
        
        # Check if GSTIN exists
        query = select(GSTConfiguration).where(
            GSTConfiguration.gstin == gstin
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"GSTIN {gstin} already registered")
        
        config = GSTConfiguration(
            tenant_id=self.tenant_id,
            gstin=gstin,
            legal_name=legal_name,
            trade_name=trade_name,
            state_code=state_code,
            state_name=state_name,
            address=address,
            pincode=pincode,
            registration_date=registration_date,
            registration_type=registration_type,
            is_regular=registration_type == "regular",
            is_composition=registration_type == "composition",
            email=email,
            phone=phone,
            created_by=self.user_id
        )
        
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config
    
    async def get_gst_configuration(self, gstin: str) -> Optional[GSTConfiguration]:
        """Get GST configuration by GSTIN"""
        query = select(GSTConfiguration).where(
            and_(
                GSTConfiguration.tenant_id == self.tenant_id,
                GSTConfiguration.gstin == gstin,
                GSTConfiguration.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    # ========================================================================
    # HSN/SAC Master
    # ========================================================================
    
    async def create_hsn_sac(
        self,
        code: str,
        code_type: str,
        description: str,
        cgst_rate: Decimal,
        sgst_rate: Decimal,
        igst_rate: Decimal,
        cess_rate: Decimal = Decimal("0.00"),
        category: Optional[str] = None
    ) -> HSNSACMaster:
        """Create HSN/SAC code"""
        
        # Check if exists
        query = select(HSNSACMaster).where(
            and_(
                HSNSACMaster.tenant_id == self.tenant_id,
                HSNSACMaster.code == code
            )
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update
            existing.description = description
            existing.cgst_rate = cgst_rate
            existing.sgst_rate = sgst_rate
            existing.igst_rate = igst_rate
            existing.cess_rate = cess_rate
            existing.category = category
            existing.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        
        hsn_sac = HSNSACMaster(
            tenant_id=self.tenant_id,
            code=code,
            code_type=code_type,
            description=description,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate,
            cess_rate=cess_rate,
            category=category
        )
        
        self.db.add(hsn_sac)
        await self.db.commit()
        await self.db.refresh(hsn_sac)
        return hsn_sac
    
    async def get_hsn_sac(self, code: str) -> Optional[HSNSACMaster]:
        """Get HSN/SAC by code"""
        query = select(HSNSACMaster).where(
            and_(
                HSNSACMaster.tenant_id == self.tenant_id,
                HSNSACMaster.code == code,
                HSNSACMaster.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    # ========================================================================
    # GST Calculation
    # ========================================================================
    
    async def calculate_gst(
        self,
        taxable_amount: Decimal,
        hsn_sac_code: str,
        is_inter_state: bool,
        is_reverse_charge: bool = False
    ) -> Dict[str, Any]:
        """Calculate GST amounts"""
        
        # Get HSN/SAC rates
        hsn_sac = await self.get_hsn_sac(hsn_sac_code)
        if not hsn_sac:
            raise ValueError(f"HSN/SAC code {hsn_sac_code} not found")
        
        if is_inter_state:
            # IGST applies for inter-state transactions
            igst_amount = (taxable_amount * hsn_sac.igst_rate / Decimal("100")).quantize(Decimal("0.01"))
            cgst_amount = Decimal("0.00")
            sgst_amount = Decimal("0.00")
        else:
            # CGST + SGST for intra-state
            cgst_amount = (taxable_amount * hsn_sac.cgst_rate / Decimal("100")).quantize(Decimal("0.01"))
            sgst_amount = (taxable_amount * hsn_sac.sgst_rate / Decimal("100")).quantize(Decimal("0.01"))
            igst_amount = Decimal("0.00")
        
        cess_amount = (taxable_amount * hsn_sac.cess_rate / Decimal("100")).quantize(Decimal("0.01"))
        total_gst = cgst_amount + sgst_amount + igst_amount + cess_amount
        total_amount = taxable_amount + total_gst
        
        return {
            "taxable_amount": float(taxable_amount),
            "cgst_rate": float(hsn_sac.cgst_rate),
            "cgst_amount": float(cgst_amount),
            "sgst_rate": float(hsn_sac.sgst_rate),
            "sgst_amount": float(sgst_amount),
            "igst_rate": float(hsn_sac.igst_rate),
            "igst_amount": float(igst_amount),
            "cess_amount": float(cess_amount),
            "total_gst": float(total_gst),
            "total_amount": float(total_amount),
            "is_inter_state": is_inter_state,
            "is_reverse_charge": is_reverse_charge
        }
    
    # ========================================================================
    # GST Transaction Recording
    # ========================================================================
    
    async def generate_transaction_number(self) -> str:
        """Generate unique GST transaction number"""
        now = datetime.now()
        prefix = f"GST-{now.year}{now.month:02d}"
        
        query = select(GSTTransaction).where(
            and_(
                GSTTransaction.tenant_id == self.tenant_id,
                GSTTransaction.transaction_number.like(f"{prefix}-%")
            )
        ).order_by(desc(GSTTransaction.transaction_number)).limit(1)
        
        result = await self.db.execute(query)
        last_txn = result.scalar_one_or_none()
        
        if last_txn:
            last_number = int(last_txn.transaction_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:05d}"
    
    async def record_gst_transaction(
        self,
        transaction_date: date,
        transaction_type: GSTTransactionType,
        reference_type: str,
        reference_id: int,
        party_name: str,
        taxable_amount: Decimal,
        cgst_amount: Decimal,
        sgst_amount: Decimal,
        igst_amount: Decimal,
        cess_amount: Decimal = Decimal("0.00"),
        party_gstin: Optional[str] = None,
        party_state: Optional[str] = None,
        hsn_sac_code: Optional[str] = None,
        invoice_number: Optional[str] = None,
        place_of_supply: Optional[str] = None,
        is_reverse_charge: bool = False
    ) -> GSTTransaction:
        """Record GST transaction"""
        
        transaction_number = await self.generate_transaction_number()
        
        total_gst = cgst_amount + sgst_amount + igst_amount + cess_amount
        total_amount = taxable_amount + total_gst
        is_inter_state = igst_amount > 0
        
        transaction = GSTTransaction(
            tenant_id=self.tenant_id,
            transaction_number=transaction_number,
            transaction_date=transaction_date,
            transaction_type=transaction_type,
            reference_type=reference_type,
            reference_id=reference_id,
            invoice_number=invoice_number,
            party_gstin=party_gstin,
            party_name=party_name,
            party_state=party_state,
            hsn_sac_code=hsn_sac_code,
            taxable_amount=taxable_amount,
            cgst_rate=Decimal("0.00") if cgst_amount == 0 else (cgst_amount / taxable_amount * 100).quantize(Decimal("0.01")),
            cgst_amount=cgst_amount,
            sgst_rate=Decimal("0.00") if sgst_amount == 0 else (sgst_amount / taxable_amount * 100).quantize(Decimal("0.01")),
            sgst_amount=sgst_amount,
            igst_rate=Decimal("0.00") if igst_amount == 0 else (igst_amount / taxable_amount * 100).quantize(Decimal("0.01")),
            igst_amount=igst_amount,
            cess_amount=cess_amount,
            total_gst=total_gst,
            total_amount=total_amount,
            is_reverse_charge=is_reverse_charge,
            place_of_supply=place_of_supply,
            is_inter_state=is_inter_state,
            created_by=self.user_id
        )
        
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    # ========================================================================
    # Input Tax Credit (ITC)
    # ========================================================================
    
    async def record_input_credit(
        self,
        supplier_gstin: str,
        supplier_name: str,
        invoice_number: str,
        invoice_date: date,
        taxable_amount: Decimal,
        cgst_amount: Decimal,
        sgst_amount: Decimal,
        igst_amount: Decimal,
        cess_amount: Decimal = Decimal("0.00"),
        transaction_id: Optional[int] = None
    ) -> GSTInputCredit:
        """Record input tax credit"""
        
        financial_year = invoice_date.year if invoice_date.month >= 4 else invoice_date.year - 1
        month = invoice_date.month
        
        total_itc = cgst_amount + sgst_amount + igst_amount + cess_amount
        
        itc = GSTInputCredit(
            tenant_id=self.tenant_id,
            supplier_gstin=supplier_gstin,
            supplier_name=supplier_name,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            transaction_id=transaction_id,
            taxable_amount=taxable_amount,
            cgst_amount=cgst_amount,
            sgst_amount=sgst_amount,
            igst_amount=igst_amount,
            cess_amount=cess_amount,
            total_itc=total_itc,
            itc_claimed=Decimal("0.00"),
            itc_reversed=Decimal("0.00"),
            itc_available=total_itc,
            financial_year=financial_year,
            month=month
        )
        
        self.db.add(itc)
        await self.db.commit()
        await self.db.refresh(itc)
        return itc
    
    # ========================================================================
    # GST Returns
    # ========================================================================
    
    async def prepare_gstr1(
        self,
        gstin: str,
        financial_year: int,
        month: int
    ) -> GSTReturn:
        """Prepare GSTR-1 (Outward supplies)"""
        
        # Get all outward transactions for the month
        from_date = date(financial_year if month >= 4 else financial_year + 1, month, 1)
        
        # Calculate last day of month
        if month == 12:
            to_date = date(financial_year + 1, 1, 1)
        else:
            to_date = date(financial_year if month >= 4 else financial_year + 1, month + 1, 1)
        
        from dateutil.relativedelta import relativedelta
        to_date = to_date - relativedelta(days=1)
        
        # Query outward transactions
        query = select(
            func.sum(GSTTransaction.taxable_amount).label("taxable"),
            func.sum(GSTTransaction.cgst_amount).label("cgst"),
            func.sum(GSTTransaction.sgst_amount).label("sgst"),
            func.sum(GSTTransaction.igst_amount).label("igst")
        ).where(
            and_(
                GSTTransaction.tenant_id == self.tenant_id,
                GSTTransaction.transaction_date >= from_date,
                GSTTransaction.transaction_date <= to_date,
                GSTTransaction.transaction_type.in_([
                    GSTTransactionType.SALE
                ]),
                GSTTransaction.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        totals = result.first()
        
        # Due date (typically 11th of next month)
        due_date = to_date + relativedelta(days=11)
        
        return_period = f"{month:02d}{financial_year}"
        
        gst_return = GSTReturn(
            tenant_id=self.tenant_id,
            return_type=GSTReturnType.GSTR1,
            return_period=return_period,
            financial_year=financial_year,
            month=month,
            gstin=gstin,
            due_date=due_date,
            outward_taxable=totals.taxable or Decimal("0.00"),
            outward_cgst=totals.cgst or Decimal("0.00"),
            outward_sgst=totals.sgst or Decimal("0.00"),
            outward_igst=totals.igst or Decimal("0.00"),
            status=GSTReturnStatus.DRAFT,
            created_by=self.user_id
        )
        
        self.db.add(gst_return)
        await self.db.commit()
        await self.db.refresh(gst_return)
        return gst_return
    
    async def prepare_gstr3b(
        self,
        gstin: str,
        financial_year: int,
        month: int
    ) -> GSTReturn:
        """Prepare GSTR-3B (Summary return with tax payment)"""
        
        from_date = date(financial_year if month >= 4 else financial_year + 1, month, 1)
        
        if month == 12:
            to_date = date(financial_year + 1, 1, 1)
        else:
            to_date = date(financial_year if month >= 4 else financial_year + 1, month + 1, 1)
        
        from dateutil.relativedelta import relativedelta
        to_date = to_date - relativedelta(days=1)
        
        # Get outward supplies
        outward_query = select(
            func.sum(GSTTransaction.taxable_amount).label("taxable"),
            func.sum(GSTTransaction.cgst_amount).label("cgst"),
            func.sum(GSTTransaction.sgst_amount).label("sgst"),
            func.sum(GSTTransaction.igst_amount).label("igst")
        ).where(
            and_(
                GSTTransaction.tenant_id == self.tenant_id,
                GSTTransaction.transaction_date >= from_date,
                GSTTransaction.transaction_date <= to_date,
                GSTTransaction.transaction_type == GSTTransactionType.SALE,
                GSTTransaction.is_deleted == False
            )
        )
        
        outward_result = await self.db.execute(outward_query)
        outward = outward_result.first()
        
        # Get ITC
        itc_query = select(
            func.sum(GSTInputCredit.taxable_amount).label("taxable"),
            func.sum(GSTInputCredit.cgst_amount).label("cgst"),
            func.sum(GSTInputCredit.sgst_amount).label("sgst"),
            func.sum(GSTInputCredit.igst_amount).label("igst")
        ).where(
            and_(
                GSTInputCredit.tenant_id == self.tenant_id,
                GSTInputCredit.invoice_date >= from_date,
                GSTInputCredit.invoice_date <= to_date
            )
        )
        
        itc_result = await self.db.execute(itc_query)
        itc = itc_result.first()
        
        # Calculate net liability
        net_cgst = (outward.cgst or Decimal("0.00")) - (itc.cgst or Decimal("0.00"))
        net_sgst = (outward.sgst or Decimal("0.00")) - (itc.sgst or Decimal("0.00"))
        net_igst = (outward.igst or Decimal("0.00")) - (itc.igst or Decimal("0.00"))
        total_liability = net_cgst + net_sgst + net_igst
        
        due_date = to_date + relativedelta(days=20)
        return_period = f"{month:02d}{financial_year}"
        
        gst_return = GSTReturn(
            tenant_id=self.tenant_id,
            return_type=GSTReturnType.GSTR3B,
            return_period=return_period,
            financial_year=financial_year,
            month=month,
            gstin=gstin,
            due_date=due_date,
            outward_taxable=outward.taxable or Decimal("0.00"),
            outward_cgst=outward.cgst or Decimal("0.00"),
            outward_sgst=outward.sgst or Decimal("0.00"),
            outward_igst=outward.igst or Decimal("0.00"),
            inward_taxable=itc.taxable or Decimal("0.00"),
            itc_cgst=itc.cgst or Decimal("0.00"),
            itc_sgst=itc.sgst or Decimal("0.00"),
            itc_igst=itc.igst or Decimal("0.00"),
            net_cgst=net_cgst,
            net_sgst=net_sgst,
            net_igst=net_igst,
            total_liability=total_liability,
            status=GSTReturnStatus.DRAFT,
            created_by=self.user_id
        )
        
        self.db.add(gst_return)
        await self.db.commit()
        await self.db.refresh(gst_return)
        return gst_return
    
    # ========================================================================
    # Reporting
    # ========================================================================
    
    async def get_gst_summary(
        self,
        financial_year: int,
        month: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get GST summary"""
        conditions = [
            GSTTransaction.tenant_id == self.tenant_id,
            GSTTransaction.is_deleted == False
        ]
        
        if month:
            from_date = date(financial_year if month >= 4 else financial_year + 1, month, 1)
            if month == 12:
                to_date = date(financial_year + 1, 1, 1)
            else:
                to_date = date(financial_year if month >= 4 else financial_year + 1, month + 1, 1)
            
            from dateutil.relativedelta import relativedelta
            to_date = to_date - relativedelta(days=1)
            
            conditions.extend([
                GSTTransaction.transaction_date >= from_date,
                GSTTransaction.transaction_date <= to_date
            ])
        
        # Outward summary
        outward_query = select(
            func.sum(GSTTransaction.taxable_amount).label("taxable"),
            func.sum(GSTTransaction.total_gst).label("gst")
        ).where(
            and_(*conditions, GSTTransaction.transaction_type == GSTTransactionType.SALE)
        )
        
        outward_result = await self.db.execute(outward_query)
        outward = outward_result.first()
        
        # Inward summary (from ITC)
        itc_conditions = [
            GSTInputCredit.tenant_id == self.tenant_id
        ]
        
        if month:
            itc_conditions.extend([
                GSTInputCredit.invoice_date >= from_date,
                GSTInputCredit.invoice_date <= to_date
            ])
        
        itc_query = select(
            func.sum(GSTInputCredit.taxable_amount).label("taxable"),
            func.sum(GSTInputCredit.total_itc).label("itc")
        ).where(and_(*itc_conditions))
        
        itc_result = await self.db.execute(itc_query)
        inward = itc_result.first()
        
        return {
            "financial_year": financial_year,
            "month": month,
            "outward_supplies": {
                "taxable_amount": float(outward.taxable or 0),
                "total_gst": float(outward.gst or 0)
            },
            "inward_supplies": {
                "taxable_amount": float(inward.taxable or 0),
                "total_itc": float(inward.itc or 0)
            },
            "net_liability": float((outward.gst or 0) - (inward.itc or 0))
        }
