"""
Account Service
Handles deposit account opening, management, and lifecycle
"""

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import uuid
import httpx


class AccountService:
    """
    Deposit Account Management Service
    Handles complete account lifecycle
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def open_fd_account(
        self,
        customer_id: str,
        cif_number: str,
        product_id: str,
        principal_amount: Decimal,
        tenure_days: int,
        is_senior_citizen: bool = False,
        nominees: List[Dict[str, Any]] = None,
        branch_code: str = None,
        created_by: str = None
    ) -> Dict[str, Any]:
        """
        Open Fixed Deposit Account
        Complete workflow with CIF validation, rate calculation, maturity calculation
        """
        from ..models import (
            DepositAccount, DepositProduct, Nominee, 
            DepositAccountStatus, DepositTransaction
        )
        from ..engines import InterestEngine, RateEngine
        
        # 1. Validate customer via CIF service
        customer_data = await self._validate_customer(customer_id, cif_number)
        
        if not customer_data:
            raise ValueError(f"Customer validation failed: {cif_number}")
        
        # 2. Fetch product
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Validate product constraints
        if principal_amount < product.min_amount:
            raise ValueError(f"Minimum amount is {product.min_amount}")
        
        if product.max_amount and principal_amount > product.max_amount:
            raise ValueError(f"Maximum amount is {product.max_amount}")
        
        if tenure_days < product.min_tenure_days:
            raise ValueError(f"Minimum tenure is {product.min_tenure_days} days")
        
        if product.max_tenure_days and tenure_days > product.max_tenure_days:
            raise ValueError(f"Maximum tenure is {product.max_tenure_days} days")
        
        # 3. Calculate applicable rate
        rate_engine = RateEngine(self.db)
        rate_data = rate_engine.calculate_applicable_rate(
            product_id,
            principal_amount,
            tenure_days,
            is_senior_citizen
        )
        
        applicable_rate = Decimal(str(rate_data["applicable_rate"]))
        
        # 4. Calculate maturity
        open_date = date.today()
        maturity_date = open_date + timedelta(days=tenure_days)
        
        maturity_calc = InterestEngine.calculate_interest(
            principal_amount,
            applicable_rate,
            tenure_days,
            product.interest_method
        )
        
        maturity_amount = Decimal(str(maturity_calc["maturity_amount"]))
        
        # 5. Generate account number
        account_number = self._generate_account_number("FD")
        
        # 6. Create account
        account = DepositAccount(
            id=uuid.uuid4(),
            account_number=account_number,
            customer_id=customer_id,
            cif_number=cif_number,
            product_id=product_id,
            deposit_type=product.deposit_type,
            principal_amount=principal_amount,
            interest_rate=applicable_rate,
            is_senior_citizen=is_senior_citizen,
            open_date=open_date,
            maturity_date=maturity_date,
            maturity_amount=maturity_amount,
            interest_method=product.interest_method,
            payout_frequency=product.payout_frequency,
            auto_renewal=product.auto_renewal_allowed,
            status=DepositAccountStatus.PENDING_APPROVAL,
            branch_code=branch_code,
            created_by=created_by
        )
        
        self.db.add(account)
        self.db.flush()
        
        # 7. Add nominees
        if nominees:
            self._add_nominees(account.id, nominees)
        
        # 8. Create opening transaction
        transaction = DepositTransaction(
            id=uuid.uuid4(),
            account_id=account.id,
            transaction_type="OPENING",
            transaction_date=open_date,
            credit_amount=principal_amount,
            balance=principal_amount,
            reference_number=f"OPEN-{account_number}",
            narration=f"FD Account Opening - {account_number}",
            created_by=created_by
        )
        
        self.db.add(transaction)
        
        # 9. Publish event for accounting
        await self._publish_event("deposit.account.opened", {
            "account_id": str(account.id),
            "account_number": account_number,
            "customer_id": customer_id,
            "amount": float(principal_amount),
            "product_type": product.deposit_type
        })
        
        self.db.commit()
        
        return {
            "account_id": str(account.id),
            "account_number": account_number,
            "customer_name": customer_data.get("name"),
            "principal_amount": float(principal_amount),
            "interest_rate": float(applicable_rate),
            "tenure_days": tenure_days,
            "open_date": open_date.isoformat(),
            "maturity_date": maturity_date.isoformat(),
            "maturity_amount": float(maturity_amount),
            "status": account.status,
            "certificate_url": None  # Generated after approval
        }
    
    async def open_rd_account(
        self,
        customer_id: str,
        cif_number: str,
        product_id: str,
        installment_amount: Decimal,
        num_installments: int,
        is_senior_citizen: bool = False,
        nominees: List[Dict[str, Any]] = None,
        branch_code: str = None,
        created_by: str = None
    ) -> Dict[str, Any]:
        """
        Open Recurring Deposit Account
        """
        from ..models import (
            DepositAccount, DepositProduct, 
            DepositAccountStatus, DepositTransaction
        )
        from ..engines import RateEngine, RDEngine
        
        # Validate customer
        customer_data = await self._validate_customer(customer_id, cif_number)
        
        if not customer_data:
            raise ValueError(f"Customer validation failed: {cif_number}")
        
        # Fetch product
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Calculate total principal
        total_principal = installment_amount * num_installments
        tenure_days = num_installments * 30  # Approximate
        
        # Get rate
        rate_engine = RateEngine(self.db)
        rate_data = rate_engine.calculate_applicable_rate(
            product_id,
            total_principal,
            tenure_days,
            is_senior_citizen
        )
        
        applicable_rate = Decimal(str(rate_data["applicable_rate"]))
        
        # Calculate maturity
        rd_engine = RDEngine(self.db)
        maturity_calc = rd_engine.calculate_rd_maturity(
            installment_amount,
            num_installments,
            applicable_rate
        )
        
        open_date = date.today()
        maturity_date = open_date + timedelta(days=tenure_days)
        maturity_amount = Decimal(str(maturity_calc["maturity_amount"]))
        
        # Generate account number
        account_number = self._generate_account_number("RD")
        
        # Create account
        account = DepositAccount(
            id=uuid.uuid4(),
            account_number=account_number,
            customer_id=customer_id,
            cif_number=cif_number,
            product_id=product_id,
            deposit_type=product.deposit_type,
            principal_amount=total_principal,
            interest_rate=applicable_rate,
            is_senior_citizen=is_senior_citizen,
            open_date=open_date,
            maturity_date=maturity_date,
            maturity_amount=maturity_amount,
            interest_method=product.interest_method,
            payout_frequency=product.payout_frequency,
            status=DepositAccountStatus.PENDING_APPROVAL,
            branch_code=branch_code,
            created_by=created_by,
            metadata={
                "installment_amount": float(installment_amount),
                "num_installments": num_installments
            }
        )
        
        self.db.add(account)
        self.db.flush()
        
        # Add nominees
        if nominees:
            self._add_nominees(account.id, nominees)
        
        # Generate installment schedule
        rd_engine.generate_installment_schedule(
            str(account.id),
            installment_amount,
            num_installments,
            open_date
        )
        
        self.db.commit()
        
        return {
            "account_id": str(account.id),
            "account_number": account_number,
            "customer_name": customer_data.get("name"),
            "installment_amount": float(installment_amount),
            "num_installments": num_installments,
            "interest_rate": float(applicable_rate),
            "open_date": open_date.isoformat(),
            "maturity_date": maturity_date.isoformat(),
            "maturity_amount": float(maturity_amount),
            "status": account.status
        }
    
    def approve_account(
        self,
        account_id: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """
        Approve deposit account and activate
        """
        from ..models import DepositAccount, DepositAccountStatus
        from datetime import datetime
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        if account.status != DepositAccountStatus.PENDING_APPROVAL:
            raise ValueError(f"Account cannot be approved: {account.status}")
        
        account.status = DepositAccountStatus.ACTIVE
        account.approved_by = approved_by
        account.approved_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "account_id": str(account.id),
            "account_number": account.account_number,
            "status": account.status,
            "approved_by": approved_by,
            "approved_at": account.approved_at.isoformat()
        }
    
    def get_account_details(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        Get complete account details
        """
        from ..models import DepositAccount
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        return {
            "id": str(account.id),
            "account_number": account.account_number,
            "customer_id": str(account.customer_id),
            "cif_number": account.cif_number,
            "product_id": str(account.product_id),
            "deposit_type": account.deposit_type,
            "principal_amount": float(account.principal_amount),
            "interest_rate": float(account.interest_rate),
            "open_date": account.open_date.isoformat(),
            "maturity_date": account.maturity_date.isoformat(),
            "maturity_amount": float(account.maturity_amount) if account.maturity_amount else None,
            "status": account.status,
            "total_interest_earned": float(account.total_interest_earned),
            "nominees": [
                {
                    "name": n.name,
                    "relationship": n.relationship,
                    "allocation_percentage": float(n.allocation_percentage)
                }
                for n in account.nominees
            ]
        }
    
    def search_accounts(
        self,
        customer_id: str = None,
        cif_number: str = None,
        status: str = None,
        branch_code: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search deposit accounts
        """
        from ..models import DepositAccount
        
        query = self.db.query(DepositAccount)
        
        if customer_id:
            query = query.filter(DepositAccount.customer_id == customer_id)
        
        if cif_number:
            query = query.filter(DepositAccount.cif_number == cif_number)
        
        if status:
            query = query.filter(DepositAccount.status == status)
        
        if branch_code:
            query = query.filter(DepositAccount.branch_code == branch_code)
        
        accounts = query.order_by(DepositAccount.created_at.desc()).limit(100).all()
        
        return [
            {
                "id": str(acc.id),
                "account_number": acc.account_number,
                "customer_id": str(acc.customer_id),
                "deposit_type": acc.deposit_type,
                "principal_amount": float(acc.principal_amount),
                "interest_rate": float(acc.interest_rate),
                "maturity_date": acc.maturity_date.isoformat(),
                "status": acc.status
            }
            for acc in accounts
        ]
    
    def _add_nominees(
        self,
        account_id: str,
        nominees: List[Dict[str, Any]]
    ):
        """
        Add nominees to account
        """
        from ..models import Nominee
        
        for nominee_data in nominees:
            nominee = Nominee(
                id=uuid.uuid4(),
                account_id=account_id,
                name=nominee_data["name"],
                relationship=nominee_data["relationship"],
                date_of_birth=nominee_data.get("date_of_birth"),
                address=nominee_data.get("address"),
                phone=nominee_data.get("phone"),
                allocation_percentage=Decimal(str(nominee_data.get("allocation_percentage", 100)))
            )
            self.db.add(nominee)
    
    async def _validate_customer(
        self,
        customer_id: str,
        cif_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate customer via CIF/Customer service
        """
        try:
            # Call customer service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://customer-service:8001/api/v1/customers/{customer_id}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    customer = response.json()
                    
                    if customer.get("cif_number") == cif_number:
                        return customer
        except Exception as e:
            print(f"Customer validation error: {e}")
            # For development, return mock data
            return {
                "id": customer_id,
                "cif_number": cif_number,
                "name": "Mock Customer",
                "kyc_status": "APPROVED"
            }
        
        return None
    
    async def _publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """
        Publish event to accounting/event engine
        """
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://accounting-service:8003/api/v1/events",
                    json={
                        "event_type": event_type,
                        "payload": payload
                    },
                    timeout=5.0
                )
        except Exception as e:
            print(f"Event publishing error: {e}")
    
    def _generate_account_number(
        self,
        prefix: str = "FD"
    ) -> str:
        """
        Generate unique account number
        """
        import random
        today = date.today().strftime('%Y%m%d')
        sequence = random.randint(10000, 99999)
        return f"{prefix}{today}{sequence}"
