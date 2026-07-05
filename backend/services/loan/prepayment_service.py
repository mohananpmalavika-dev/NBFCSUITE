"""
Loan Prepayment Service
Handles prepayment calculations, partial/full foreclosure, and outstanding calculations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.loan_models import (
    LoanAccount,
    LoanEMISchedule,
    LoanProduct
)


class LoanPrepaymentService:
    """Service for managing loan prepayments and foreclosures"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def calculate_prepayment(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None,
        prepayment_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate prepayment amount and charges for full foreclosure
        
        Args:
            account_id: Loan account ID
            account_number: Loan account number
            prepayment_date: Date of prepayment (default: today)
            
        Returns:
            Prepayment calculation with breakdown
        """
        if not account_id and not account_number:
            raise ValueError("Either account_id or account_number must be provided")
        
        prepayment_date = prepayment_date or date.today()
        
        # Get loan account
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        ]
        
        if account_id:
            conditions.append(LoanAccount.id == account_id)
        if account_number:
            conditions.append(LoanAccount.loan_account_number == account_number)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError("Loan account not found")
        
        if account.status == "closed":
            raise ValueError("Loan account is already closed")
        
        if not account.prepayment_allowed:
            raise ValueError("Prepayment is not allowed for this loan")
        
        # Get all pending EMIs
        emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account.id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
            )
        ).order_by(LoanEMISchedule.installment_number)
        
        emi_result = await self.db.execute(emi_query)
        pending_emis = emi_result.scalars().all()
        
        # Calculate outstanding amounts
        outstanding_principal = Decimal("0.00")
        outstanding_interest = Decimal("0.00")
        outstanding_penal = Decimal("0.00")
        
        # Only include interest up to prepayment date
        for emi in pending_emis:
            # Unpaid principal
            outstanding_principal += (emi.principal_component - emi.paid_principal)
            
            # Interest only if EMI is already due
            if emi.due_date <= prepayment_date:
                outstanding_interest += (emi.interest_component - emi.paid_interest)
                outstanding_penal += emi.penal_interest
        
        # Calculate prepayment charges
        prepayment_charges = Decimal("0.00")
        if account.prepayment_charges_percentage:
            prepayment_charges = (
                outstanding_principal * 
                account.prepayment_charges_percentage / Decimal("100")
            )
        
        # Total amount to be paid
        total_prepayment_amount = (
            outstanding_principal +
            outstanding_interest +
            outstanding_penal +
            account.outstanding_charges +
            prepayment_charges
        )
        
        # Calculate interest waiver (future interest that will be saved)
        future_interest = Decimal("0.00")
        for emi in pending_emis:
            if emi.due_date > prepayment_date:
                future_interest += (emi.interest_component - emi.paid_interest)
        
        return {
            "loan_account_number": account.loan_account_number,
            "prepayment_date": prepayment_date.isoformat(),
            "outstanding_principal": float(outstanding_principal),
            "outstanding_interest": float(outstanding_interest),
            "outstanding_penal_interest": float(outstanding_penal),
            "outstanding_charges": float(account.outstanding_charges),
            "prepayment_charges": float(prepayment_charges),
            "prepayment_charges_percentage": float(account.prepayment_charges_percentage) if account.prepayment_charges_percentage else 0,
            "total_prepayment_amount": float(total_prepayment_amount),
            "interest_savings": float(future_interest),
            "pending_emis_count": len(pending_emis),
            "tenure_remaining": len([e for e in pending_emis if e.status == "pending"]),
            "prepayment_allowed": account.prepayment_allowed,
            "message": "Prepayment calculation completed"
        }
    
    async def process_foreclosure(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None,
        foreclosure_amount: Decimal = None,
        foreclosure_date: Optional[date] = None,
        payment_mode: str = "cash",
        reference_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process full foreclosure of loan account
        
        Args:
            account_id: Loan account ID
            account_number: Loan account number
            foreclosure_amount: Amount paid for foreclosure
            foreclosure_date: Date of foreclosure
            payment_mode: Mode of payment
            reference_number: Payment reference
            remarks: Optional remarks
            
        Returns:
            Foreclosure confirmation with NOC details
        """
        if not account_id and not account_number:
            raise ValueError("Either account_id or account_number must be provided")
        
        foreclosure_date = foreclosure_date or date.today()
        
        # Get prepayment calculation
        prepayment_calc = await self.calculate_prepayment(
            account_id=account_id,
            account_number=account_number,
            prepayment_date=foreclosure_date
        )
        
        required_amount = Decimal(str(prepayment_calc["total_prepayment_amount"]))
        
        if foreclosure_amount < required_amount:
            raise ValueError(
                f"Foreclosure amount (₹{foreclosure_amount}) is less than "
                f"required amount (₹{required_amount})"
            )
        
        # Get loan account
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        ]
        
        if account_id:
            conditions.append(LoanAccount.id == account_id)
        if account_number:
            conditions.append(LoanAccount.loan_account_number == account_number)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError("Loan account not found")
        
        # Cancel all pending EMIs
        emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account.id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
            )
        )
        
        emi_result = await self.db.execute(emi_query)
        pending_emis = emi_result.scalars().all()
        
        cancelled_emis = 0
        for emi in pending_emis:
            emi.status = "cancelled" if emi.due_date > foreclosure_date else "paid"
            if emi.status == "paid":
                emi.paid_amount = emi.emi_amount
                emi.paid_principal = emi.principal_component
                emi.paid_interest = emi.interest_component
                emi.payment_date = foreclosure_date
                emi.penal_interest = Decimal("0.00")
                emi.overdue_days = 0
            else:
                cancelled_emis += 1
            emi.updated_at = datetime.now()
        
        # Update loan account
        account.outstanding_principal = Decimal("0.00")
        account.outstanding_interest = Decimal("0.00")
        account.penal_interest_outstanding = Decimal("0.00")
        account.outstanding_charges = Decimal("0.00")
        account.total_outstanding = Decimal("0.00")
        account.status = "closed"
        account.closure_date = foreclosure_date
        account.overdue_days = 0
        account.dpd = 0
        account.next_due_date = None
        account.next_due_amount = None
        account.last_payment_date = foreclosure_date
        account.last_payment_amount = foreclosure_amount
        account.internal_notes = (
            f"{account.internal_notes or ''}\n"
            f"Foreclosed on {foreclosure_date.isoformat()}. "
            f"Amount: ₹{foreclosure_amount}. {remarks or ''}"
        ).strip()
        account.updated_at = datetime.now()
        account.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(account)
        
        # Generate NOC details
        noc_details = {
            "loan_account_number": account.loan_account_number,
            "customer_id": account.customer_id,
            "foreclosure_date": foreclosure_date.isoformat(),
            "foreclosure_amount": float(foreclosure_amount),
            "payment_mode": payment_mode,
            "reference_number": reference_number,
            "original_loan_amount": float(account.sanctioned_amount),
            "disbursement_date": account.disbursement_date.isoformat(),
            "total_emis_paid": len([e for e in pending_emis if e.status == "paid"]),
            "emis_cancelled": cancelled_emis,
            "interest_savings": float(prepayment_calc["interest_savings"]),
            "status": "closed",
            "noc_generated": True,
            "message": "Loan foreclosed successfully. NOC can be generated."
        }
        
        return noc_details
    
    async def calculate_partial_prepayment(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None,
        prepayment_amount: Decimal = None,
        reduce_emi: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate impact of partial prepayment
        
        Args:
            account_id: Loan account ID
            account_number: Loan account number
            prepayment_amount: Amount to prepay
            reduce_emi: If True, reduce EMI amount; if False, reduce tenure
            
        Returns:
            Partial prepayment impact analysis
        """
        if not account_id and not account_number:
            raise ValueError("Either account_id or account_number must be provided")
        
        if not prepayment_amount or prepayment_amount <= 0:
            raise ValueError("Prepayment amount must be greater than zero")
        
        # Get loan account
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        ]
        
        if account_id:
            conditions.append(LoanAccount.id == account_id)
        if account_number:
            conditions.append(LoanAccount.loan_account_number == account_number)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError("Loan account not found")
        
        if account.status == "closed":
            raise ValueError("Loan account is already closed")
        
        # Calculate prepayment charges
        prepayment_charges = Decimal("0.00")
        if account.prepayment_charges_percentage:
            prepayment_charges = (
                prepayment_amount * 
                account.prepayment_charges_percentage / Decimal("100")
            )
        
        # Net amount going towards principal
        net_prepayment = prepayment_amount - prepayment_charges
        
        if net_prepayment <= 0:
            raise ValueError("Prepayment amount is not sufficient to cover charges")
        
        # Get pending EMIs
        emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account.id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status == "pending"
            )
        ).order_by(LoanEMISchedule.installment_number)
        
        emi_result = await self.db.execute(emi_query)
        pending_emis = emi_result.scalars().all()
        
        if not pending_emis:
            raise ValueError("No pending EMIs found for prepayment")
        
        # Current values
        current_outstanding = account.outstanding_principal
        current_emi = account.emi_amount
        current_tenure_remaining = len(pending_emis)
        
        # New values after prepayment
        new_outstanding = current_outstanding - net_prepayment
        
        if new_outstanding <= 0:
            return {
                "message": "Prepayment amount exceeds outstanding principal. Consider full foreclosure.",
                "suggestion": "Use foreclosure option instead"
            }
        
        # Calculate new EMI or tenure
        interest_rate = account.interest_rate / Decimal("100") / Decimal("12")  # Monthly rate
        
        if reduce_emi:
            # Reduce EMI, keep tenure same
            new_emi = (
                new_outstanding * interest_rate * 
                (Decimal("1") + interest_rate) ** current_tenure_remaining
            ) / (
                (Decimal("1") + interest_rate) ** current_tenure_remaining - Decimal("1")
            )
            new_tenure = current_tenure_remaining
            emi_reduction = current_emi - new_emi
            tenure_reduction = 0
        else:
            # Reduce tenure, keep EMI same
            new_emi = current_emi
            # Calculate new tenure using formula
            if interest_rate > 0:
                new_tenure = int(
                    (Decimal(str(float(new_outstanding) / float(current_emi))) / 
                     (Decimal("1") - (Decimal("1") + interest_rate) ** -current_tenure_remaining)).ln() /
                    (Decimal("1") + interest_rate).ln()
                )
            else:
                new_tenure = int(new_outstanding / current_emi)
            
            emi_reduction = Decimal("0.00")
            tenure_reduction = current_tenure_remaining - new_tenure
        
        # Calculate interest savings
        current_total_payment = current_emi * current_tenure_remaining
        new_total_payment = new_emi * new_tenure + prepayment_amount
        interest_savings = current_total_payment - new_total_payment
        
        return {
            "loan_account_number": account.loan_account_number,
            "prepayment_amount": float(prepayment_amount),
            "prepayment_charges": float(prepayment_charges),
            "net_prepayment_towards_principal": float(net_prepayment),
            "current_values": {
                "outstanding_principal": float(current_outstanding),
                "emi_amount": float(current_emi),
                "tenure_remaining": current_tenure_remaining
            },
            "new_values": {
                "outstanding_principal": float(new_outstanding),
                "emi_amount": float(new_emi),
                "tenure_remaining": new_tenure
            },
            "impact": {
                "emi_reduction": float(emi_reduction) if reduce_emi else 0,
                "tenure_reduction_months": tenure_reduction if not reduce_emi else 0,
                "interest_savings": float(interest_savings)
            },
            "option_selected": "reduce_emi" if reduce_emi else "reduce_tenure",
            "recommendation": "Partial prepayment will save interest" if interest_savings > 0 else "No significant savings"
        }
    
    async def generate_noc(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate No Objection Certificate for closed loan
        
        Args:
            account_id: Loan account ID
            account_number: Loan account number
            
        Returns:
            NOC details
        """
        if not account_id and not account_number:
            raise ValueError("Either account_id or account_number must be provided")
        
        # Get loan account
        conditions = [
            LoanAccount.tenant_id == self.tenant_id,
            LoanAccount.is_deleted == False
        ]
        
        if account_id:
            conditions.append(LoanAccount.id == account_id)
        if account_number:
            conditions.append(LoanAccount.loan_account_number == account_number)
        
        query = select(LoanAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError("Loan account not found")
        
        if account.status != "closed":
            raise ValueError("NOC can only be generated for closed loan accounts")
        
        if account.total_outstanding > Decimal("0.01"):  # Allow small rounding difference
            raise ValueError("Cannot generate NOC. Outstanding amount exists.")
        
        # Generate NOC
        noc = {
            "noc_number": f"NOC-{datetime.now().strftime('%Y%m%d')}-{account.id:06d}",
            "noc_date": date.today().isoformat(),
            "loan_account_number": account.loan_account_number,
            "customer_id": account.customer_id,
            "loan_amount": float(account.sanctioned_amount),
            "disbursement_date": account.disbursement_date.isoformat(),
            "closure_date": account.closure_date.isoformat() if account.closure_date else None,
            "total_amount_paid": float(account.sanctioned_amount + account.interest_received),
            "principal_paid": float(account.principal_received),
            "interest_paid": float(account.interest_received),
            "status": "closed",
            "outstanding_amount": 0.00,
            "declaration": (
                f"This is to certify that loan account {account.loan_account_number} "
                f"has been fully repaid and closed. There are no outstanding dues. "
                f"We have no objection in releasing the documents/security (if any) "
                f"associated with this loan."
            ),
            "generated_date": datetime.now().isoformat()
        }
        
        return noc
