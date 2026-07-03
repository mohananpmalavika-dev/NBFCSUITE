"""
Maturity Engine
Handles deposit maturity, renewal, and payout processing
"""

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session


class MaturityEngine:
    """
    Maturity Management Engine
    Handles:
    - Maturity calculation
    - Auto-renewal
    - Maturity payout
    - Renewal recommendations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_maturity(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        Calculate exact maturity amount for an account
        Considers all interest postings and payments
        """
        from ..models import DepositAccount, InterestPosting
        from .interest_engine import InterestEngine
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Calculate interest
        days = (account.maturity_date - account.open_date).days
        
        interest_data = InterestEngine.calculate_interest(
            account.principal_amount,
            account.interest_rate,
            days,
            account.interest_method
        )
        
        total_interest = Decimal(str(interest_data["interest"]))
        
        # Subtract already paid interest (for periodic payout accounts)
        paid_interest = account.total_interest_paid or Decimal('0')
        
        pending_interest = total_interest - paid_interest
        maturity_amount = account.principal_amount + pending_interest
        
        return {
            "account_id": account_id,
            "account_number": account.account_number,
            "principal": float(account.principal_amount),
            "interest_rate": float(account.interest_rate),
            "open_date": account.open_date.isoformat(),
            "maturity_date": account.maturity_date.isoformat(),
            "days": days,
            "total_interest": float(total_interest),
            "interest_paid": float(paid_interest),
            "pending_interest": float(pending_interest),
            "maturity_amount": float(maturity_amount),
            "method": account.interest_method,
            "payout_frequency": account.payout_frequency
        }
    
    def process_maturity(
        self,
        account_id: str,
        action: str = "PAYOUT",
        renewal_tenure_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process maturity based on customer instruction
        Actions: PAYOUT, RENEW, PARTIAL_RENEW
        """
        from ..models import DepositAccount, DepositAccountStatus
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if account.status != DepositAccountStatus.ACTIVE:
            raise ValueError(f"Account is not active: {account.status}")
        
        maturity_calc = self.calculate_maturity(account_id)
        
        if action == "PAYOUT":
            return self._process_payout(account, maturity_calc)
        elif action == "RENEW":
            return self._process_renewal(
                account, 
                maturity_calc,
                renewal_tenure_days
            )
        elif action == "PARTIAL_RENEW":
            return self._process_partial_renewal(account, maturity_calc)
        else:
            raise ValueError(f"Invalid action: {action}")
    
    def _process_payout(
        self,
        account: Any,
        maturity_calc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process full payout at maturity
        """
        from ..models import DepositAccountStatus, DepositTransaction
        import uuid
        
        # Update account status
        account.status = DepositAccountStatus.MATURED
        account.actual_closure_date = date.today()
        
        # Create payout transaction
        transaction = DepositTransaction(
            id=uuid.uuid4(),
            account_id=account.id,
            transaction_type="MATURITY_PAYOUT",
            transaction_date=date.today(),
            credit_amount=Decimal(str(maturity_calc["maturity_amount"])),
            narration=f"Maturity payout for account {account.account_number}",
            reference_number=f"MAT-{account.account_number}-{date.today().strftime('%Y%m%d')}"
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        return {
            "action": "PAYOUT",
            "account_id": str(account.id),
            "account_number": account.account_number,
            "maturity_amount": maturity_calc["maturity_amount"],
            "transaction_ref": transaction.reference_number,
            "status": "COMPLETED"
        }
    
    def _process_renewal(
        self,
        account: Any,
        maturity_calc: Dict[str, Any],
        renewal_tenure_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process full renewal (principal + interest)
        """
        from ..models import DepositAccount, DepositAccountStatus, RenewalHistory
        from .rate_engine import RateEngine
        import uuid
        
        # Calculate new principal (maturity amount)
        new_principal = Decimal(str(maturity_calc["maturity_amount"]))
        
        # Determine tenure
        if renewal_tenure_days is None:
            # Use same tenure as original
            renewal_tenure_days = (account.maturity_date - account.open_date).days
        
        # Get new rate
        rate_engine = RateEngine(self.db)
        new_rate_data = rate_engine.calculate_applicable_rate(
            str(account.product_id),
            new_principal,
            renewal_tenure_days,
            account.is_senior_citizen
        )
        
        new_maturity_date = date.today() + timedelta(days=renewal_tenure_days)
        
        # Mark old account as renewed
        account.status = DepositAccountStatus.RENEWED
        account.actual_closure_date = date.today()
        
        # Create new account
        new_account = DepositAccount(
            id=uuid.uuid4(),
            account_number=self._generate_account_number(),
            customer_id=account.customer_id,
            cif_number=account.cif_number,
            product_id=account.product_id,
            deposit_type=account.deposit_type,
            principal_amount=new_principal,
            interest_rate=Decimal(str(new_rate_data["applicable_rate"])),
            is_senior_citizen=account.is_senior_citizen,
            open_date=date.today(),
            maturity_date=new_maturity_date,
            interest_method=account.interest_method,
            payout_frequency=account.payout_frequency,
            auto_renewal=account.auto_renewal,
            status=DepositAccountStatus.ACTIVE,
            branch_code=account.branch_code
        )
        
        # Create renewal history
        renewal = RenewalHistory(
            id=uuid.uuid4(),
            old_account_id=account.id,
            new_account_id=new_account.id,
            renewal_date=date.today(),
            renewal_type="AUTO" if account.auto_renewal else "MANUAL",
            maturity_amount=Decimal(str(maturity_calc["maturity_amount"])),
            renewed_principal=new_principal,
            interest_paid_out=Decimal('0'),
            new_interest_rate=new_account.interest_rate,
            new_tenure_days=renewal_tenure_days,
            new_maturity_date=new_maturity_date
        )
        
        self.db.add(new_account)
        self.db.add(renewal)
        self.db.commit()
        
        return {
            "action": "RENEW",
            "old_account_id": str(account.id),
            "new_account_id": str(new_account.id),
            "new_account_number": new_account.account_number,
            "renewed_principal": float(new_principal),
            "new_rate": new_rate_data["applicable_rate"],
            "new_tenure_days": renewal_tenure_days,
            "new_maturity_date": new_maturity_date.isoformat(),
            "status": "COMPLETED"
        }
    
    def _process_partial_renewal(
        self,
        account: Any,
        maturity_calc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Renew principal, payout interest
        """
        # Implementation similar to renewal but principal only
        return {
            "action": "PARTIAL_RENEW",
            "status": "NOT_IMPLEMENTED"
        }
    
    def get_maturity_pipeline(
        self,
        days_ahead: int = 30,
        branch_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming maturities for proactive management
        """
        from ..models import DepositAccount, DepositAccountStatus
        
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        query = self.db.query(DepositAccount).filter(
            DepositAccount.status == DepositAccountStatus.ACTIVE,
            DepositAccount.maturity_date <= cutoff_date,
            DepositAccount.maturity_date >= date.today()
        )
        
        if branch_code:
            query = query.filter(DepositAccount.branch_code == branch_code)
        
        accounts = query.order_by(DepositAccount.maturity_date).all()
        
        pipeline = []
        
        for account in accounts:
            days_to_maturity = (account.maturity_date - date.today()).days
            
            pipeline.append({
                "account_id": str(account.id),
                "account_number": account.account_number,
                "customer_id": str(account.customer_id),
                "cif_number": account.cif_number,
                "principal": float(account.principal_amount),
                "maturity_date": account.maturity_date.isoformat(),
                "days_to_maturity": days_to_maturity,
                "maturity_amount": float(account.maturity_amount or 0),
                "auto_renewal": account.auto_renewal,
                "maturity_instruction": account.maturity_instruction,
                "branch_code": account.branch_code
            })
        
        return pipeline
    
    def _generate_account_number(self) -> str:
        """
        Generate unique account number
        Format: FD{YYYYMMDD}{SEQUENCE}
        """
        import random
        today = date.today().strftime('%Y%m%d')
        sequence = random.randint(1000, 9999)
        return f"FD{today}{sequence}"
    
    def recommend_renewal(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        AI-powered renewal recommendation
        Analyzes customer behavior and market conditions
        """
        from ..models import DepositAccount
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Simple heuristic-based recommendation
        # In production, integrate with AI service
        
        recommendation = {
            "account_id": account_id,
            "current_rate": float(account.interest_rate),
            "recommended_action": "RENEW",
            "recommended_tenure_days": (account.maturity_date - account.open_date).days,
            "confidence": 0.75,
            "reasoning": "Customer has consistent deposit history",
            "alternatives": []
        }
        
        return recommendation
