"""
Loan Repayment Service
Handles payment recording, allocation, receipt generation, and outstanding calculations
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.loan_models import (
    LoanAccount,
    LoanEMISchedule,
    LoanRepayment,
    LoanProduct
)


class LoanRepaymentService:
    """Service for managing loan repayments and payments"""
    
    # Payment allocation priority
    ALLOCATION_PRIORITY = [
        "penal_interest",
        "interest",
        "principal",
        "charges"
    ]
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_receipt_number(self) -> str:
        """Generate unique receipt number: RCP-YYYYMM-XXXX"""
        now = datetime.now()
        prefix = f"RCP-{now.year}{now.month:02d}"
        
        # Get the last receipt number for this month
        query = select(LoanRepayment).where(
            and_(
                LoanRepayment.tenant_id == self.tenant_id,
                LoanRepayment.receipt_number.like(f"{prefix}-%")
            )
        ).order_by(desc(LoanRepayment.receipt_number)).limit(1)
        
        result = await self.db.execute(query)
        last_receipt = result.scalar_one_or_none()
        
        if last_receipt:
            last_number = int(last_receipt.receipt_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    async def calculate_outstanding(
        self,
        account_id: int
    ) -> Dict[str, Decimal]:
        """
        Calculate current outstanding amounts for a loan account
        
        Args:
            account_id: Loan account ID
            
        Returns:
            Dict with outstanding principal, interest, penal interest, and charges
        """
        # Get loan account
        query = select(LoanAccount).where(
            and_(
                LoanAccount.id == account_id,
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError("Loan account not found")
        
        # Get all pending and overdue EMIs
        emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account_id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
            )
        ).order_by(LoanEMISchedule.installment_number)
        
        emi_result = await self.db.execute(emi_query)
        pending_emis = emi_result.scalars().all()
        
        # Calculate totals
        outstanding_principal = Decimal("0.00")
        outstanding_interest = Decimal("0.00")
        outstanding_penal = Decimal("0.00")
        
        for emi in pending_emis:
            # Unpaid principal and interest
            outstanding_principal += (emi.principal_component - emi.paid_principal)
            outstanding_interest += (emi.interest_component - emi.paid_interest)
            outstanding_penal += emi.penal_interest
        
        return {
            "outstanding_principal": outstanding_principal,
            "outstanding_interest": outstanding_interest,
            "outstanding_penal_interest": outstanding_penal,
            "outstanding_charges": account.outstanding_charges or Decimal("0.00"),
            "total_outstanding": (
                outstanding_principal + 
                outstanding_interest + 
                outstanding_penal + 
                (account.outstanding_charges or Decimal("0.00"))
            )
        }
    
    async def allocate_payment(
        self,
        account_id: int,
        payment_amount: Decimal
    ) -> Dict[str, Any]:
        """
        Allocate payment to outstanding dues with priority
        Priority: Penal Interest → Regular Interest → Principal → Charges
        
        Args:
            account_id: Loan account ID
            payment_amount: Payment amount to allocate
            
        Returns:
            Dict with allocation breakdown and affected EMI IDs
        """
        # Get outstanding amounts
        outstanding = await self.calculate_outstanding(account_id)
        
        # Get pending EMIs in order
        emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account_id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
            )
        ).order_by(LoanEMISchedule.due_date, LoanEMISchedule.installment_number)
        
        emi_result = await self.db.execute(emi_query)
        pending_emis = emi_result.scalars().all()
        
        # Initialize allocation
        remaining_amount = payment_amount
        allocation = {
            "allocated_to_penal_interest": Decimal("0.00"),
            "allocated_to_interest": Decimal("0.00"),
            "allocated_to_principal": Decimal("0.00"),
            "allocated_to_charges": Decimal("0.00"),
            "total_allocated": Decimal("0.00"),
            "remaining_amount": Decimal("0.00")
        }
        
        affected_emis = []
        
        # Step 1: Allocate to penal interest (oldest first)
        for emi in pending_emis:
            if remaining_amount <= 0:
                break
            
            unpaid_penal = emi.penal_interest
            if unpaid_penal > 0:
                allocation_to_penal = min(remaining_amount, unpaid_penal)
                allocation["allocated_to_penal_interest"] += allocation_to_penal
                remaining_amount -= allocation_to_penal
                affected_emis.append(emi.id)
        
        # Step 2: Allocate to regular interest (oldest first)
        for emi in pending_emis:
            if remaining_amount <= 0:
                break
            
            unpaid_interest = emi.interest_component - emi.paid_interest
            if unpaid_interest > 0:
                allocation_to_interest = min(remaining_amount, unpaid_interest)
                allocation["allocated_to_interest"] += allocation_to_interest
                remaining_amount -= allocation_to_interest
                if emi.id not in affected_emis:
                    affected_emis.append(emi.id)
        
        # Step 3: Allocate to principal (oldest first)
        for emi in pending_emis:
            if remaining_amount <= 0:
                break
            
            unpaid_principal = emi.principal_component - emi.paid_principal
            if unpaid_principal > 0:
                allocation_to_principal = min(remaining_amount, unpaid_principal)
                allocation["allocated_to_principal"] += allocation_to_principal
                remaining_amount -= allocation_to_principal
                if emi.id not in affected_emis:
                    affected_emis.append(emi.id)
        
        # Step 4: Allocate to charges (if any)
        if remaining_amount > 0 and outstanding["outstanding_charges"] > 0:
            allocation_to_charges = min(remaining_amount, outstanding["outstanding_charges"])
            allocation["allocated_to_charges"] = allocation_to_charges
            remaining_amount -= allocation_to_charges
        
        # Calculate totals
        allocation["total_allocated"] = (
            allocation["allocated_to_penal_interest"] +
            allocation["allocated_to_interest"] +
            allocation["allocated_to_principal"] +
            allocation["allocated_to_charges"]
        )
        allocation["remaining_amount"] = remaining_amount
        allocation["affected_emi_ids"] = affected_emis
        
        return allocation
    
    async def record_payment(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None,
        payment_amount: Decimal = None,
        payment_date: date = None,
        payment_mode: str = "cash",
        reference_number: Optional[str] = None,
        bank_name: Optional[str] = None,
        transaction_date: Optional[date] = None,
        remarks: Optional[str] = None,
        collected_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Record a payment against a loan account
        
        Args:
            account_id: Loan account ID (either this or account_number required)
            account_number: Loan account number
            payment_amount: Payment amount
            payment_date: Date of payment
            payment_mode: cash, cheque, neft, rtgs, upi, imps
            reference_number: Transaction reference
            bank_name: Bank name (for non-cash payments)
            transaction_date: Transaction date
            remarks: Optional remarks
            collected_by: User ID who collected payment
            
        Returns:
            Payment record with receipt details
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
        
        if account.status == "closed":
            raise ValueError("Cannot record payment for closed loan account")
        
        # Validate payment amount
        if payment_amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        # Calculate allocation
        allocation = await self.allocate_payment(account.id, payment_amount)
        
        # Generate receipt number
        receipt_number = await self.generate_receipt_number()
        
        # Create repayment record
        repayment = LoanRepayment(
            tenant_id=self.tenant_id,
            loan_account_id=account.id,
            receipt_number=receipt_number,
            payment_date=payment_date or date.today(),
            payment_amount=payment_amount,
            payment_mode=payment_mode,
            allocated_to_principal=allocation["allocated_to_principal"],
            allocated_to_interest=allocation["allocated_to_interest"],
            allocated_to_penal_interest=allocation["allocated_to_penal_interest"],
            allocated_to_charges=allocation["allocated_to_charges"],
            reference_number=reference_number,
            bank_name=bank_name,
            transaction_date=transaction_date or payment_date or date.today(),
            status="success",
            receipt_generated=True,
            emi_schedule_ids=allocation["affected_emi_ids"],
            remarks=remarks,
            collected_by=collected_by or self.user_id,
            created_by=self.user_id
        )
        
        self.db.add(repayment)
        await self.db.flush()
        
        # Update EMI schedules
        await self._update_emi_schedules(
            account.id,
            allocation,
            payment_date or date.today()
        )
        
        # Update loan account
        await self._update_loan_account(account.id, allocation, payment_date or date.today())
        
        await self.db.commit()
        await self.db.refresh(repayment)
        
        # Return payment details
        return {
            "payment_id": repayment.id,
            "receipt_number": repayment.receipt_number,
            "loan_account_number": account.loan_account_number,
            "payment_amount": float(payment_amount),
            "payment_date": payment_date.isoformat() if payment_date else date.today().isoformat(),
            "payment_mode": payment_mode,
            "allocation": {
                "penal_interest": float(allocation["allocated_to_penal_interest"]),
                "interest": float(allocation["allocated_to_interest"]),
                "principal": float(allocation["allocated_to_principal"]),
                "charges": float(allocation["allocated_to_charges"]),
                "total": float(allocation["total_allocated"])
            },
            "remaining_amount": float(allocation["remaining_amount"]),
            "emis_updated": len(allocation["affected_emi_ids"]),
            "status": "success",
            "message": "Payment recorded successfully"
        }
    
    async def _update_emi_schedules(
        self,
        account_id: int,
        allocation: Dict[str, Any],
        payment_date: date
    ) -> None:
        """Update EMI schedules with payment allocation"""
        # Get pending EMIs in order
        emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account_id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
            )
        ).order_by(LoanEMISchedule.due_date, LoanEMISchedule.installment_number)
        
        emi_result = await self.db.execute(emi_query)
        pending_emis = emi_result.scalars().all()
        
        remaining_penal = allocation["allocated_to_penal_interest"]
        remaining_interest = allocation["allocated_to_interest"]
        remaining_principal = allocation["allocated_to_principal"]
        
        for emi in pending_emis:
            if remaining_penal <= 0 and remaining_interest <= 0 and remaining_principal <= 0:
                break
            
            # Allocate penal interest
            if remaining_penal > 0 and emi.penal_interest > 0:
                allocation_amount = min(remaining_penal, emi.penal_interest)
                emi.penal_interest -= allocation_amount
                remaining_penal -= allocation_amount
            
            # Allocate interest
            unpaid_interest = emi.interest_component - emi.paid_interest
            if remaining_interest > 0 and unpaid_interest > 0:
                allocation_amount = min(remaining_interest, unpaid_interest)
                emi.paid_interest += allocation_amount
                remaining_interest -= allocation_amount
            
            # Allocate principal
            unpaid_principal = emi.principal_component - emi.paid_principal
            if remaining_principal > 0 and unpaid_principal > 0:
                allocation_amount = min(remaining_principal, unpaid_principal)
                emi.paid_principal += allocation_amount
                remaining_principal -= allocation_amount
            
            # Update paid amount and status
            emi.paid_amount = emi.paid_principal + emi.paid_interest
            
            # Check if EMI is fully paid
            if (emi.paid_amount >= emi.emi_amount and 
                emi.penal_interest <= Decimal("0.01")):  # Allow small rounding difference
                emi.status = "paid"
                emi.payment_date = payment_date
                emi.overdue_days = 0
            elif emi.paid_amount > 0:
                emi.status = "partially_paid"
            
            emi.updated_at = datetime.now()
        
        await self.db.flush()
    
    async def _update_loan_account(
        self,
        account_id: int,
        allocation: Dict[str, Any],
        payment_date: date
    ) -> None:
        """Update loan account with payment details"""
        query = select(LoanAccount).where(
            and_(
                LoanAccount.id == account_id,
                LoanAccount.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            return
        
        # Update outstanding amounts
        account.outstanding_principal -= allocation["allocated_to_principal"]
        account.outstanding_interest -= allocation["allocated_to_interest"]
        account.penal_interest_outstanding -= allocation["allocated_to_penal_interest"]
        account.outstanding_charges -= allocation["allocated_to_charges"]
        
        # Recalculate total outstanding
        account.total_outstanding = (
            account.outstanding_principal +
            account.outstanding_interest +
            account.penal_interest_outstanding +
            account.outstanding_charges
        )
        
        # Update received amounts
        account.principal_received += allocation["allocated_to_principal"]
        account.interest_received += allocation["allocated_to_interest"]
        
        # Update last payment details
        account.last_payment_date = payment_date
        account.last_payment_amount = allocation["total_allocated"]
        
        # Update next due date (get next pending EMI)
        next_emi_query = select(LoanEMISchedule).where(
            and_(
                LoanEMISchedule.loan_account_id == account_id,
                LoanEMISchedule.tenant_id == self.tenant_id,
                LoanEMISchedule.status.in_(["pending", "partially_paid", "overdue"])
            )
        ).order_by(LoanEMISchedule.due_date).limit(1)
        
        next_emi_result = await self.db.execute(next_emi_query)
        next_emi = next_emi_result.scalar_one_or_none()
        
        if next_emi:
            account.next_due_date = next_emi.due_date
            unpaid_amount = next_emi.emi_amount - next_emi.paid_amount
            account.next_due_amount = unpaid_amount + next_emi.penal_interest
        else:
            # All EMIs paid
            account.next_due_date = None
            account.next_due_amount = None
            if account.total_outstanding <= Decimal("0.01"):  # Allow small rounding
                account.status = "closed"
                account.closure_date = payment_date
        
        # Update overdue status
        if account.total_outstanding > 0 and account.next_due_date:
            if account.next_due_date < date.today():
                account.overdue_days = (date.today() - account.next_due_date).days
                account.dpd = account.overdue_days
                if account.overdue_days > 0:
                    account.status = "overdue"
            else:
                account.overdue_days = 0
                account.dpd = 0
                account.status = "active"
        
        account.updated_at = datetime.now()
        account.updated_by = self.user_id
        
        await self.db.flush()
    
    async def get_payment_history(
        self,
        account_id: Optional[int] = None,
        account_number: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get payment history for a loan account
        
        Args:
            account_id: Loan account ID
            account_number: Loan account number
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            Dict with payment history and pagination
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
        
        # Count total payments
        count_query = select(func.count(LoanRepayment.id)).where(
            and_(
                LoanRepayment.loan_account_id == account.id,
                LoanRepayment.tenant_id == self.tenant_id
            )
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get payments
        payment_query = select(LoanRepayment).where(
            and_(
                LoanRepayment.loan_account_id == account.id,
                LoanRepayment.tenant_id == self.tenant_id
            )
        ).order_by(desc(LoanRepayment.payment_date)).offset(skip).limit(limit)
        
        payment_result = await self.db.execute(payment_query)
        payments = payment_result.scalars().all()
        
        # Build response
        payment_list = []
        for payment in payments:
            payment_list.append({
                "id": payment.id,
                "receipt_number": payment.receipt_number,
                "payment_date": payment.payment_date.isoformat(),
                "payment_amount": float(payment.payment_amount),
                "payment_mode": payment.payment_mode,
                "allocated_to_principal": float(payment.allocated_to_principal),
                "allocated_to_interest": float(payment.allocated_to_interest),
                "allocated_to_penal_interest": float(payment.allocated_to_penal_interest),
                "allocated_to_charges": float(payment.allocated_to_charges),
                "reference_number": payment.reference_number,
                "bank_name": payment.bank_name,
                "status": payment.status,
                "receipt_generated": payment.receipt_generated,
                "remarks": payment.remarks,
                "created_at": payment.created_at.isoformat()
            })
        
        return {
            "loan_account_number": account.loan_account_number,
            "payments": payment_list,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }
    
    async def get_receipt(
        self,
        receipt_id: Optional[int] = None,
        receipt_number: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get payment receipt details
        
        Args:
            receipt_id: Payment ID
            receipt_number: Receipt number
            
        Returns:
            Receipt details
        """
        if not receipt_id and not receipt_number:
            raise ValueError("Either receipt_id or receipt_number must be provided")
        
        # Build query
        conditions = [LoanRepayment.tenant_id == self.tenant_id]
        
        if receipt_id:
            conditions.append(LoanRepayment.id == receipt_id)
        if receipt_number:
            conditions.append(LoanRepayment.receipt_number == receipt_number)
        
        query = select(LoanRepayment).where(and_(*conditions))
        result = await self.db.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
        
        # Get loan account
        account_query = select(LoanAccount).where(LoanAccount.id == payment.loan_account_id)
        account_result = await self.db.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        # Build receipt
        receipt = {
            "receipt_number": payment.receipt_number,
            "receipt_date": payment.created_at.date().isoformat(),
            "loan_account_number": account.loan_account_number if account else None,
            "payment_date": payment.payment_date.isoformat(),
            "payment_amount": float(payment.payment_amount),
            "payment_mode": payment.payment_mode,
            "reference_number": payment.reference_number,
            "bank_name": payment.bank_name,
            "transaction_date": payment.transaction_date.isoformat() if payment.transaction_date else None,
            "allocation": {
                "principal": float(payment.allocated_to_principal),
                "interest": float(payment.allocated_to_interest),
                "penal_interest": float(payment.allocated_to_penal_interest),
                "charges": float(payment.allocated_to_charges),
                "total": float(
                    payment.allocated_to_principal +
                    payment.allocated_to_interest +
                    payment.allocated_to_penal_interest +
                    payment.allocated_to_charges
                )
            },
            "status": payment.status,
            "remarks": payment.remarks
        }
        
        return receipt
