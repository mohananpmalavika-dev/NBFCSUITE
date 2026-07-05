"""
Deposit Account Service

Handles all business logic for deposit accounts including:
- Account opening
- Deposits and withdrawals
- Account management
- Maturity processing
- Account closure
- Passbook management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.shared.database.deposit_models import (
    DepositAccount, DepositProduct, DepositTransaction,
    DepositMaturityQueue, DepositPassbookEntry
)
from backend.shared.common.response import CustomException
from .product_service import DepositProductService


class DepositAccountService:
    """Service for managing deposit accounts"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.product_service = DepositProductService(db, tenant_id, user_id)
    
    # ==================== ACCOUNT OPENING ====================
    
    def open_account(self, account_data: Dict[str, Any]) -> DepositAccount:
        """
        Open new deposit account
        
        Args:
            account_data: Account configuration including customer_id, product_id, amount, etc.
            
        Returns:
            Created account
        """
        # Get product
        product = self.product_service.get_product(account_data['deposit_product_id'])
        
        # Validate eligibility
        principal_amount = account_data['principal_amount']
        tenure_days = account_data.get('tenure_days')
        
        eligibility = self.product_service.validate_eligibility(
            product.id, principal_amount, tenure_days
        )
        
        if not eligibility['eligible']:
            raise CustomException(
                status_code=400,
                message=f"Eligibility check failed: {', '.join(eligibility['errors'])}"
            )
        
        # Generate account number
        account_number = self._generate_account_number()
        
        # Calculate maturity details if applicable
        opening_date = account_data.get('opening_date') or date.today()
        maturity_date = None
        maturity_amount = None
        
        if product.product_type in ['fd', 'rd', 'mis']:
            if not tenure_days:
                raise CustomException(
                    status_code=400,
                    message="Tenure is required for this product type"
                )
            
            maturity_date = opening_date + timedelta(days=tenure_days)
            
            # Calculate maturity amount
            if product.product_type == 'fd':
                calc = self.product_service.calculate_fd_maturity(
                    product.id, principal_amount, tenure_days
                )
                maturity_amount = calc['maturity_amount']
            
            elif product.product_type == 'rd':
                installment_amount = account_data.get('installment_amount')
                if not installment_amount:
                    raise CustomException(
                        status_code=400,
                        message="Installment amount is required for RD"
                    )
                
                # Calculate total installments based on frequency
                if product.installment_frequency == 'monthly':
                    total_installments = tenure_days // 30
                elif product.installment_frequency == 'quarterly':
                    total_installments = tenure_days // 90
                else:
                    total_installments = tenure_days // 30  # Default monthly
                
                calc = self.product_service.calculate_rd_maturity(
                    product.id, installment_amount, total_installments
                )
                maturity_amount = calc['maturity_amount']
            
            elif product.product_type == 'mis':
                # For MIS, maturity amount is principal (interest paid monthly)
                maturity_amount = principal_amount
        
        # Calculate next interest date
        next_interest_date = self._calculate_next_interest_date(
            opening_date, product.interest_payout_frequency
        )
        
        # Create account
        account = DepositAccount(
            tenant_id=self.tenant_id,
            account_number=account_number,
            customer_id=account_data['customer_id'],
            deposit_product_id=product.id,
            account_type=product.product_type,
            principal_amount=principal_amount,
            current_balance=principal_amount if product.product_type == 'savings' else Decimal('0'),
            interest_rate=product.interest_rate,
            opening_date=opening_date,
            tenure_days=tenure_days,
            maturity_date=maturity_date,
            maturity_amount=maturity_amount,
            next_interest_date=next_interest_date,
            installment_amount=account_data.get('installment_amount'),
            total_installments=account_data.get('total_installments'),
            next_installment_date=account_data.get('next_installment_date'),
            auto_renewal=account_data.get('auto_renewal', False),
            nominee_name=account_data.get('nominee_name'),
            nominee_relationship=account_data.get('nominee_relationship'),
            nominee_dob=account_data.get('nominee_dob'),
            nominee_percentage=account_data.get('nominee_percentage', Decimal('100')),
            nominee_address=account_data.get('nominee_address'),
            nominee_id_proof=account_data.get('nominee_id_proof'),
            linked_account_number=account_data.get('linked_account_number'),
            status='active',
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(account)
        self.db.flush()
        
        # Create opening transaction
        opening_txn = self._create_transaction(
            account_id=account.id,
            transaction_type='opening',
            amount=principal_amount,
            balance_before=Decimal('0'),
            balance_after=principal_amount if product.product_type == 'savings' else Decimal('0'),
            transaction_date=opening_date,
            payment_mode=account_data.get('payment_mode', 'cash'),
            reference_number=account_data.get('reference_number'),
            remarks=f"Account opened with {product.product_name}"
        )
        
        # Create passbook entry
        self._create_passbook_entry(
            account.id,
            opening_date,
            f"Account Opening - {product.product_name}",
            opening_txn.id,
            deposit_amount=principal_amount if product.product_type == 'savings' else Decimal('0'),
            balance=account.current_balance
        )
        
        # Add to maturity queue if applicable
        if maturity_date:
            self._add_to_maturity_queue(account)
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def _generate_account_number(self) -> str:
        """Generate unique account number in format DEP-YYYYMM-XXXX"""
        today = date.today()
        prefix = f"DEP-{today.strftime('%Y%m')}"
        
        # Get last account number for this month
        last_account = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_number.like(f"{prefix}%")
            )
        ).order_by(DepositAccount.id.desc()).first()
        
        if last_account:
            last_number = int(last_account.account_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def _calculate_next_interest_date(
        self,
        from_date: date,
        frequency: Optional[str]
    ) -> Optional[date]:
        """Calculate next interest posting date"""
        if not frequency or frequency == 'on_demand':
            return None
        
        if frequency == 'daily':
            return from_date + timedelta(days=1)
        elif frequency == 'monthly':
            return from_date + timedelta(days=30)
        elif frequency == 'quarterly':
            return from_date + timedelta(days=90)
        elif frequency == 'maturity':
            return None
        
        return None
    
    # ==================== ACCOUNT QUERIES ====================
    
    def get_account(self, account_id: int) -> DepositAccount:
        """Get account by ID"""
        account = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.id == account_id,
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).first()
        
        if not account:
            raise CustomException(status_code=404, message="Account not found")
        
        return account
    
    def get_account_by_number(self, account_number: str) -> DepositAccount:
        """Get account by account number"""
        account = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.account_number == account_number,
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).first()
        
        if not account:
            raise CustomException(status_code=404, message="Account not found")
        
        return account
    
    def list_accounts(
        self,
        customer_id: Optional[int] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DepositAccount]:
        """List accounts with filters"""
        query = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        )
        
        if customer_id:
            query = query.filter(DepositAccount.customer_id == customer_id)
        
        if account_type:
            query = query.filter(DepositAccount.account_type == account_type)
        
        if status:
            query = query.filter(DepositAccount.status == status)
        
        accounts = query.order_by(DepositAccount.created_at.desc()).offset(skip).limit(limit).all()
        return accounts
    
    def get_accounts_due_for_maturity(self, days_ahead: int = 7) -> List[DepositAccount]:
        """Get accounts maturing in next N days"""
        end_date = date.today() + timedelta(days=days_ahead)
        
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date <= end_date,
                DepositAccount.maturity_date >= date.today(),
                DepositAccount.is_deleted == False
            )
        ).all()
        
        return accounts
    
    # ==================== DEPOSITS & WITHDRAWALS ====================
    
    def make_deposit(
        self,
        account_id: int,
        amount: Decimal,
        payment_mode: str = 'cash',
        reference_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> DepositTransaction:
        """Make deposit to account"""
        account = self.get_account(account_id)
        
        # Validate account status
        if account.status != 'active':
            raise CustomException(
                status_code=400,
                message=f"Cannot deposit to {account.status} account"
            )
        
        # Only savings accounts allow additional deposits
        if account.account_type != 'savings':
            raise CustomException(
                status_code=400,
                message="Additional deposits only allowed for savings accounts"
            )
        
        # Update balance
        balance_before = account.current_balance
        balance_after = balance_before + amount
        
        # Create transaction
        transaction = self._create_transaction(
            account_id=account.id,
            transaction_type='deposit',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_date=date.today(),
            payment_mode=payment_mode,
            reference_number=reference_number,
            remarks=remarks
        )
        
        # Update account
        account.current_balance = balance_after
        account.total_deposits += amount
        account.updated_by = self.user_id
        
        # Create passbook entry
        self._create_passbook_entry(
            account.id,
            date.today(),
            f"Deposit - {payment_mode.upper()}",
            transaction.id,
            deposit_amount=amount,
            balance=balance_after
        )
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def make_withdrawal(
        self,
        account_id: int,
        amount: Decimal,
        payment_mode: str = 'cash',
        reference_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> DepositTransaction:
        """Make withdrawal from account"""
        account = self.get_account(account_id)
        product = account.product
        
        # Validate account status
        if account.status != 'active':
            raise CustomException(
                status_code=400,
                message=f"Cannot withdraw from {account.status} account"
            )
        
        # Only savings accounts allow withdrawals
        if account.account_type != 'savings':
            raise CustomException(
                status_code=400,
                message="Regular withdrawals only allowed for savings accounts. Use premature closure for other types."
            )
        
        # Check balance
        if account.current_balance < amount:
            raise CustomException(
                status_code=400,
                message="Insufficient balance"
            )
        
        # Check minimum balance
        balance_after = account.current_balance - amount
        if product.min_balance and balance_after < product.min_balance:
            raise CustomException(
                status_code=400,
                message=f"Withdrawal would breach minimum balance of ₹{product.min_balance:,.2f}"
            )
        
        # Check monthly withdrawal limit
        if product.max_withdrawals_per_month:
            month_start = date.today().replace(day=1)
            withdrawal_count = self.db.query(func.count(DepositTransaction.id)).filter(
                and_(
                    DepositTransaction.deposit_account_id == account.id,
                    DepositTransaction.transaction_type == 'withdrawal',
                    DepositTransaction.transaction_date >= month_start
                )
            ).scalar()
            
            if withdrawal_count >= product.max_withdrawals_per_month:
                raise CustomException(
                    status_code=400,
                    message=f"Monthly withdrawal limit of {product.max_withdrawals_per_month} reached"
                )
        
        # Calculate withdrawal charge
        withdrawal_charge = product.withdrawal_charge or Decimal('0')
        total_deduction = amount + withdrawal_charge
        
        if account.current_balance < total_deduction:
            raise CustomException(
                status_code=400,
                message=f"Insufficient balance including withdrawal charge of ₹{withdrawal_charge}"
            )
        
        balance_before = account.current_balance
        balance_after = balance_before - total_deduction
        
        # Create withdrawal transaction
        transaction = self._create_transaction(
            account_id=account.id,
            transaction_type='withdrawal',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_date=date.today(),
            payment_mode=payment_mode,
            reference_number=reference_number,
            remarks=remarks
        )
        
        # Create charge transaction if applicable
        if withdrawal_charge > 0:
            self._create_transaction(
                account_id=account.id,
                transaction_type='charge',
                amount=withdrawal_charge,
                balance_before=balance_after + withdrawal_charge,
                balance_after=balance_after,
                transaction_date=date.today(),
                remarks="Withdrawal charge"
            )
        
        # Update account
        account.current_balance = balance_after
        account.total_withdrawals += amount
        account.updated_by = self.user_id
        
        # Create passbook entries
        self._create_passbook_entry(
            account.id,
            date.today(),
            f"Withdrawal - {payment_mode.upper()}",
            transaction.id,
            withdrawal_amount=amount,
            balance=balance_after + withdrawal_charge if withdrawal_charge > 0 else balance_after
        )
        
        if withdrawal_charge > 0:
            self._create_passbook_entry(
                account.id,
                date.today(),
                "Withdrawal Charge",
                None,
                withdrawal_amount=withdrawal_charge,
                balance=balance_after
            )
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    # ==================== RD INSTALLMENTS ====================
    
    def pay_rd_installment(
        self,
        account_id: int,
        amount: Decimal,
        payment_mode: str = 'cash',
        reference_number: Optional[str] = None
    ) -> DepositTransaction:
        """Pay RD installment"""
        account = self.get_account(account_id)
        
        if account.account_type != 'rd':
            raise CustomException(
                status_code=400,
                message="This is not a Recurring Deposit account"
            )
        
        if account.status != 'active':
            raise CustomException(
                status_code=400,
                message=f"Cannot pay installment to {account.status} account"
            )
        
        # Validate installment amount
        if amount != account.installment_amount:
            raise CustomException(
                status_code=400,
                message=f"Installment amount must be ₹{account.installment_amount:,.2f}"
            )
        
        # Check if already paid all installments
        if account.installments_paid >= account.total_installments:
            raise CustomException(
                status_code=400,
                message="All installments already paid"
            )
        
        balance_before = account.current_balance
        balance_after = balance_before + amount
        
        # Create transaction
        transaction = self._create_transaction(
            account_id=account.id,
            transaction_type='installment',
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_date=date.today(),
            payment_mode=payment_mode,
            reference_number=reference_number,
            remarks=f"RD Installment {account.installments_paid + 1}/{account.total_installments}"
        )
        
        # Update account
        account.current_balance = balance_after
        account.total_deposits += amount
        account.installments_paid += 1
        
        # Update next installment date
        if account.installments_paid < account.total_installments:
            frequency_days = 30 if account.product.installment_frequency == 'monthly' else 90
            account.next_installment_date = date.today() + timedelta(days=frequency_days)
        else:
            account.next_installment_date = None
        
        account.updated_by = self.user_id
        
        # Create passbook entry
        self._create_passbook_entry(
            account.id,
            date.today(),
            f"RD Installment {account.installments_paid}/{account.total_installments}",
            transaction.id,
            deposit_amount=amount,
            balance=balance_after
        )
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    # ==================== ACCOUNT CLOSURE ====================
    
    def close_account_at_maturity(self, account_id: int) -> Dict[str, Any]:
        """Close account at maturity"""
        account = self.get_account(account_id)
        
        if account.status != 'active':
            raise CustomException(
                status_code=400,
                message=f"Account is already {account.status}"
            )
        
        if not account.maturity_date:
            raise CustomException(
                status_code=400,
                message="This account does not have a maturity date"
            )
        
        if date.today() < account.maturity_date:
            raise CustomException(
                status_code=400,
                message=f"Account not yet matured. Maturity date: {account.maturity_date}"
            )
        
        # Calculate final amount
        closure_amount = account.maturity_amount or account.current_balance
        
        # Update account
        account.status = 'matured'
        account.closure_date = date.today()
        account.closure_amount = closure_amount
        account.updated_by = self.user_id
        
        # Create closure transaction
        transaction = self._create_transaction(
            account_id=account.id,
            transaction_type='closure',
            amount=closure_amount,
            balance_before=account.current_balance,
            balance_after=Decimal('0'),
            transaction_date=date.today(),
            remarks="Maturity closure"
        )
        
        # Create passbook entry
        self._create_passbook_entry(
            account.id,
            date.today(),
            "Account Closure - Maturity",
            transaction.id,
            withdrawal_amount=closure_amount,
            balance=Decimal('0')
        )
        
        self.db.commit()
        
        return {
            "account_number": account.account_number,
            "status": "matured",
            "closure_amount": float(closure_amount),
            "closure_date": account.closure_date.isoformat()
        }
    
    def close_account_prematurely(
        self,
        account_id: int,
        closure_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Close account before maturity"""
        account = self.get_account(account_id)
        product = account.product
        
        if account.status != 'active':
            raise CustomException(
                status_code=400,
                message=f"Account is already {account.status}"
            )
        
        if not product.premature_withdrawal_allowed:
            raise CustomException(
                status_code=400,
                message="Premature closure not allowed for this product"
            )
        
        # Calculate days held
        days_held = (date.today() - account.opening_date).days
        
        # Calculate closure amount with penalty
        closure_calc = self.product_service.calculate_premature_closure(
            product.id,
            account.principal_amount,
            days_held,
            account.interest_rate
        )
        
        closure_amount = closure_calc['closure_amount']
        penalty_amount = closure_calc['penalty_amount']
        
        # Update account
        account.status = 'premature_closed'
        account.closure_date = date.today()
        account.closure_amount = closure_amount
        account.premature_closure = True
        account.penalty_amount = penalty_amount
        account.closure_reason = closure_reason
        account.updated_by = self.user_id
        
        # Create penalty transaction if applicable
        if penalty_amount > 0:
            self._create_transaction(
                account_id=account.id,
                transaction_type='penalty',
                amount=penalty_amount,
                balance_before=account.current_balance,
                balance_after=account.current_balance - penalty_amount,
                transaction_date=date.today(),
                remarks="Premature closure penalty"
            )
        
        # Create closure transaction
        transaction = self._create_transaction(
            account_id=account.id,
            transaction_type='closure',
            amount=closure_amount,
            balance_before=account.current_balance - penalty_amount if penalty_amount > 0 else account.current_balance,
            balance_after=Decimal('0'),
            transaction_date=date.today(),
            remarks=f"Premature closure - {closure_reason or 'Customer request'}"
        )
        
        # Create passbook entries
        if penalty_amount > 0:
            self._create_passbook_entry(
                account.id,
                date.today(),
                "Premature Closure Penalty",
                None,
                withdrawal_amount=penalty_amount,
                balance=account.current_balance - penalty_amount
            )
        
        self._create_passbook_entry(
            account.id,
            date.today(),
            "Account Closure - Premature",
            transaction.id,
            withdrawal_amount=closure_amount,
            balance=Decimal('0')
        )
        
        self.db.commit()
        
        return {
            "account_number": account.account_number,
            "status": "premature_closed",
            "days_held": days_held,
            "penalty_amount": float(penalty_amount),
            "closure_amount": float(closure_amount),
            "closure_date": account.closure_date.isoformat()
        }
    
    # ==================== HELPER METHODS ====================
    
    def _create_transaction(
        self,
        account_id: int,
        transaction_type: str,
        amount: Decimal,
        balance_before: Decimal,
        balance_after: Decimal,
        transaction_date: date,
        payment_mode: Optional[str] = None,
        reference_number: Optional[str] = None,
        remarks: Optional[str] = None,
        interest_period_start: Optional[date] = None,
        interest_period_end: Optional[date] = None,
        interest_rate: Optional[Decimal] = None,
        tds_amount: Optional[Decimal] = None
    ) -> DepositTransaction:
        """Create transaction record"""
        # Generate transaction number
        today = datetime.now()
        prefix = f"TXN-{today.strftime('%Y%m%d')}"
        
        last_txn = self.db.query(DepositTransaction).filter(
            and_(
                DepositTransaction.tenant_id == self.tenant_id,
                DepositTransaction.transaction_number.like(f"{prefix}%")
            )
        ).order_by(DepositTransaction.id.desc()).first()
        
        if last_txn:
            last_number = int(last_txn.transaction_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        transaction_number = f"{prefix}-{new_number:04d}"
        
        transaction = DepositTransaction(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            transaction_number=transaction_number,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_date=transaction_date,
            value_date=transaction_date,
            payment_mode=payment_mode,
            reference_number=reference_number,
            remarks=remarks,
            interest_period_start=interest_period_start,
            interest_period_end=interest_period_end,
            interest_rate=interest_rate,
            tds_amount=tds_amount or Decimal('0'),
            processed_by=self.user_id,
            created_by=self.user_id
        )
        
        self.db.add(transaction)
        self.db.flush()
        
        return transaction
    
    def _create_passbook_entry(
        self,
        account_id: int,
        entry_date: date,
        particulars: str,
        transaction_id: Optional[int],
        deposit_amount: Decimal = Decimal('0'),
        withdrawal_amount: Decimal = Decimal('0'),
        balance: Decimal = Decimal('0')
    ) -> DepositPassbookEntry:
        """Create passbook entry"""
        entry = DepositPassbookEntry(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            entry_date=entry_date,
            particulars=particulars,
            transaction_id=transaction_id,
            deposit_amount=deposit_amount,
            withdrawal_amount=withdrawal_amount,
            balance=balance
        )
        
        self.db.add(entry)
        self.db.flush()
        
        return entry
    
    def _add_to_maturity_queue(self, account: DepositAccount) -> None:
        """Add account to maturity processing queue"""
        queue_entry = DepositMaturityQueue(
            tenant_id=self.tenant_id,
            deposit_account_id=account.id,
            maturity_date=account.maturity_date,
            maturity_amount=account.maturity_amount,
            principal_amount=account.principal_amount,
            interest_amount=account.maturity_amount - account.principal_amount,
            auto_renewal=account.auto_renewal,
            status='pending'
        )
        
        self.db.add(queue_entry)
        self.db.flush()
    
    # ==================== STATISTICS ====================
    
    def get_account_summary(self, account_id: int) -> Dict[str, Any]:
        """Get comprehensive account summary"""
        account = self.get_account(account_id)
        
        # Get transaction count
        txn_count = self.db.query(func.count(DepositTransaction.id)).filter(
            DepositTransaction.deposit_account_id == account_id
        ).scalar()
        
        # Get last transaction
        last_txn = self.db.query(DepositTransaction).filter(
            DepositTransaction.deposit_account_id == account_id
        ).order_by(DepositTransaction.created_at.desc()).first()
        
        return {
            "account": {
                "account_number": account.account_number,
                "account_type": account.account_type,
                "status": account.status,
                "opening_date": account.opening_date.isoformat(),
                "maturity_date": account.maturity_date.isoformat() if account.maturity_date else None
            },
            "balances": {
                "principal_amount": float(account.principal_amount),
                "current_balance": float(account.current_balance),
                "interest_earned": float(account.interest_earned),
                "maturity_amount": float(account.maturity_amount) if account.maturity_amount else None
            },
            "transactions": {
                "total_deposits": float(account.total_deposits),
                "total_withdrawals": float(account.total_withdrawals),
                "transaction_count": txn_count,
                "last_transaction_date": last_txn.transaction_date.isoformat() if last_txn else None
            },
            "product": {
                "product_code": account.product.product_code,
                "product_name": account.product.product_name,
                "interest_rate": float(account.interest_rate)
            }
        }
