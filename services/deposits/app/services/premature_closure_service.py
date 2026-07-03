"""
Premature Closure Service
Handles premature withdrawal of deposits
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import Dict, Any
from sqlalchemy.orm import Session
import uuid


class PrematureClosureService:
    """
    Premature Deposit Closure Service
    Calculates penalty and processes early withdrawals
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_premature_closure(
        self,
        account_id: str,
        closure_date: date = None
    ) -> Dict[str, Any]:
        """
        Calculate premature closure payout
        Applies reduced interest rate and penalty
        """
        from ..models import DepositAccount, DepositProduct
        from ..engines import InterestEngine
        
        if closure_date is None:
            closure_date = date.today()
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        product = account.product
        
        if not product.premature_allowed:
            raise ValueError("Premature closure not allowed for this product")
        
        # Calculate days completed
        days_completed = (closure_date - account.open_date).days
        
        if days_completed < 30:
            raise ValueError("Minimum 30 days holding required")
        
        # Determine applicable rate (usually 1-2% less than original)
        rate_reduction = Decimal('1.0')  # 1% reduction
        applicable_rate = account.interest_rate - rate_reduction
        
        if applicable_rate < Decimal('4.0'):
            applicable_rate = Decimal('4.0')  # Floor rate
        
        # Calculate interest earned
        interest_calc = InterestEngine.calculate_interest(
            account.principal_amount,
            applicable_rate,
            days_completed,
            account.interest_method
        )
        
        interest_earned = Decimal(str(interest_calc["interest"]))
        
        # Apply penalty
        penalty_percentage = product.premature_penalty_percentage
        penalty_amount = (interest_earned * penalty_percentage / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Calculate TDS
        tds_amount = Decimal('0')
        if product.tds_applicable:
            tds_amount = (interest_earned * product.tds_rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        # Net payout
        net_payout = (
            account.principal_amount + 
            interest_earned - 
            penalty_amount - 
            tds_amount
        )
        
        # Calculate effective yield
        effective_yield = InterestEngine.calculate_effective_yield(
            account.principal_amount,
            account.principal_amount + interest_earned - penalty_amount,
            days_completed
        )
        
        return {
            "account_id": account_id,
            "account_number": account.account_number,
            "principal_amount": float(account.principal_amount),
            "open_date": account.open_date.isoformat(),
            "closure_date": closure_date.isoformat(),
            "days_completed": days_completed,
            "original_rate": float(account.interest_rate),
            "applicable_rate": float(applicable_rate),
            "interest_earned": float(interest_earned),
            "penalty_percentage": float(penalty_percentage),
            "penalty_amount": float(penalty_amount),
            "tds_amount": float(tds_amount),
            "net_payout": float(net_payout),
            "effective_yield": float(effective_yield),
            "foregone_interest": float(
                Decimal(str(account.maturity_amount or 0)) - 
                account.principal_amount - 
                interest_earned + 
                penalty_amount
            )
        }
    
    def request_premature_closure(
        self,
        account_id: str,
        closure_reason: str,
        requested_by: str
    ) -> Dict[str, Any]:
        """
        Create premature closure request
        Requires approval
        """
        from ..models import PrematureClosure
        
        # Calculate closure details
        calculation = self.calculate_premature_closure(account_id)
        
        # Create request
        closure_request = PrematureClosure(
            id=uuid.uuid4(),
            account_id=account_id,
            request_date=date.today(),
            requested_by=requested_by,
            closure_reason=closure_reason,
            principal_amount=Decimal(str(calculation["principal_amount"])),
            days_completed=calculation["days_completed"],
            applicable_interest_rate=Decimal(str(calculation["applicable_rate"])),
            interest_earned=Decimal(str(calculation["interest_earned"])),
            penalty_percentage=Decimal(str(calculation["penalty_percentage"])),
            penalty_amount=Decimal(str(calculation["penalty_amount"])),
            tds_amount=Decimal(str(calculation["tds_amount"])),
            net_payout=Decimal(str(calculation["net_payout"])),
            status="PENDING"
        )
        
        self.db.add(closure_request)
        self.db.commit()
        
        return {
            "closure_id": str(closure_request.id),
            "status": "PENDING",
            "calculation": calculation
        }
    
    def approve_premature_closure(
        self,
        closure_id: str,
        approved_by: str,
        payment_mode: str = "NEFT"
    ) -> Dict[str, Any]:
        """
        Approve and process premature closure
        """
        from ..models import (
            PrematureClosure, DepositAccount, 
            DepositAccountStatus, DepositTransaction
        )
        from datetime import datetime
        
        closure = self.db.query(PrematureClosure).filter(
            PrematureClosure.id == closure_id
        ).first()
        
        if not closure:
            raise ValueError(f"Closure request not found: {closure_id}")
        
        if closure.status != "PENDING":
            raise ValueError(f"Closure already processed: {closure.status}")
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == closure.account_id
        ).first()
        
        # Update closure status
        closure.status = "APPROVED"
        closure.approved_by = approved_by
        closure.approved_at = datetime.utcnow()
        closure.closure_date = date.today()
        closure.payment_mode = payment_mode
        closure.payment_reference = f"PREMATURE-{account.account_number}-{date.today().strftime('%Y%m%d')}"
        
        # Update account status
        account.status = DepositAccountStatus.PREMATURELY_CLOSED
        account.actual_closure_date = date.today()
        
        # Create payout transaction
        transaction = DepositTransaction(
            id=uuid.uuid4(),
            account_id=account.id,
            transaction_type="PREMATURE_CLOSURE",
            transaction_date=date.today(),
            credit_amount=closure.net_payout,
            narration=f"Premature closure payout - {closure.closure_reason}",
            reference_number=closure.payment_reference,
            created_by=approved_by
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        return {
            "closure_id": str(closure.id),
            "account_id": str(account.id),
            "account_number": account.account_number,
            "status": "COMPLETED",
            "net_payout": float(closure.net_payout),
            "payment_reference": closure.payment_reference,
            "processed_date": closure.closure_date.isoformat()
        }
    
    def reject_premature_closure(
        self,
        closure_id: str,
        rejected_by: str,
        rejection_reason: str
    ) -> Dict[str, Any]:
        """
        Reject premature closure request
        """
        from ..models import PrematureClosure
        from datetime import datetime
        
        closure = self.db.query(PrematureClosure).filter(
            PrematureClosure.id == closure_id
        ).first()
        
        if not closure:
            raise ValueError(f"Closure request not found: {closure_id}")
        
        closure.status = "REJECTED"
        closure.approved_by = rejected_by
        closure.approved_at = datetime.utcnow()
        closure.rejection_reason = rejection_reason
        
        self.db.commit()
        
        return {
            "closure_id": str(closure.id),
            "status": "REJECTED",
            "rejection_reason": rejection_reason
        }
    
    def get_pending_closures(
        self,
        branch_code: str = None
    ) -> list[Dict[str, Any]]:
        """
        Get all pending closure requests
        """
        from ..models import PrematureClosure, DepositAccount
        
        query = self.db.query(PrematureClosure, DepositAccount).join(
            DepositAccount,
            PrematureClosure.account_id == DepositAccount.id
        ).filter(
            PrematureClosure.status == "PENDING"
        )
        
        if branch_code:
            query = query.filter(DepositAccount.branch_code == branch_code)
        
        results = query.order_by(PrematureClosure.request_date).all()
        
        return [
            {
                "closure_id": str(closure.id),
                "account_number": account.account_number,
                "customer_id": str(account.customer_id),
                "principal_amount": float(closure.principal_amount),
                "net_payout": float(closure.net_payout),
                "request_date": closure.request_date.isoformat(),
                "closure_reason": closure.closure_reason,
                "days_completed": closure.days_completed
            }
            for closure, account in results
        ]
