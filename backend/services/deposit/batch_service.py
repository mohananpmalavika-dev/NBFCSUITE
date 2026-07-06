"""
Batch Processing Service

Handles all batch operations including:
- Maturity processing
- TDS calculations
- Dormancy checks
- Penalty application
- MIS payouts
- Bulk operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.shared.database.deposit_models import (
    DepositAccount, DepositProduct, DepositTransaction,
    DepositMaturityQueue, DepositInterestCalculation
)
from backend.shared.common.response import CustomException
from .account_service import DepositAccountService
from .interest_service import InterestCalculationService


class BatchProcessingService:
    """Service for batch operations"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.account_service = DepositAccountService(db, tenant_id, user_id)
        self.interest_service = InterestCalculationService(db, tenant_id, user_id)
    
    def process_maturity_batch(
        self,
        maturity_date: Optional[date] = None,
        days_ahead: int = 0
    ) -> Dict[str, Any]:
        """Process maturity batch"""
        if not maturity_date:
            maturity_date = date.today() + timedelta(days=days_ahead)
        
        # Get accounts due for maturity
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date <= maturity_date,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        processed = 0
        renewed = 0
        closed = 0
        errors = []
        
        for account in accounts:
            try:
                if account.auto_renewal:
                    # Auto-renew the account
                    self._renew_account(account)
                    renewed += 1
                else:
                    # Close at maturity
                    self.account_service.close_account_at_maturity(account.id)
                    closed += 1
                
                processed += 1
                
            except Exception as e:
                errors.append({
                    "account_number": account.account_number,
                    "error": str(e)
                })
        
        return {
            "total_accounts": len(accounts),
            "processed": processed,
            "renewed": renewed,
            "closed": closed,
            "errors": errors,
            "maturity_date": maturity_date.isoformat()
        }
    
    def _renew_account(self, account: DepositAccount) -> DepositAccount:
        """Renew an account at maturity"""
        # Create new account with same parameters
        new_account_data = {
            "customer_id": account.customer_id,
            "deposit_product_id": account.deposit_product_id,
            "principal_amount": account.maturity_amount or account.current_balance,
            "tenure_days": account.tenure_days,
            "auto_renewal": account.auto_renewal,
            "nominee_name": account.nominee_name,
            "nominee_relationship": account.nominee_relationship,
            "nominee_dob": account.nominee_dob,
            "nominee_percentage": account.nominee_percentage,
            "linked_account_number": account.linked_account_number
        }
        
        # Open new account
        new_account = self.account_service.open_account(new_account_data)
        
        # Update old account
        account.status = 'matured'
        account.closure_date = date.today()
        account.renewal_count += 1
        
        # Link accounts
        new_account.parent_account_id = account.id
        
        self.db.commit()
        
        return new_account
    
    def calculate_tds_batch(
        self,
        financial_year: str,
        quarter: int
    ) -> Dict[str, Any]:
        """Calculate TDS for quarter"""
        # Parse FY
        fy_start_year, fy_end_year = map(int, financial_year.split('-'))
        
        # Quarter dates
        quarter_dates = {
            1: (date(fy_start_year, 4, 1), date(fy_start_year, 6, 30)),
            2: (date(fy_start_year, 7, 1), date(fy_start_year, 9, 30)),
            3: (date(fy_start_year, 10, 1), date(fy_start_year, 12, 31)),
            4: (date(fy_end_year, 1, 1), date(fy_end_year, 3, 31))
        }
        period_start, period_end = quarter_dates[quarter]
        
        # Get all accounts with interest above threshold
        accounts = self.db.query(DepositAccount).join(
            DepositProduct
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositProduct.tds_applicable == True,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        processed = 0
        total_tds = Decimal('0')
        errors = []
        
        for account in accounts:
            try:
                # Calculate interest for quarter
                calculations = self.db.query(DepositInterestCalculation).filter(
                    and_(
                        DepositInterestCalculation.deposit_account_id == account.id,
                        DepositInterestCalculation.calculation_period_end >= period_start,
                        DepositInterestCalculation.calculation_period_start <= period_end
                    )
                ).all()
                
                quarter_interest = sum(calc.interest_amount for calc in calculations)
                
                # Check if above threshold
                if quarter_interest >= account.product.tds_threshold:
                    tds_amount = quarter_interest * (account.product.tds_rate / Decimal('100'))
                    
                    # Create TDS transaction
                    # This would be done when interest is posted
                    total_tds += tds_amount
                    processed += 1
                
            except Exception as e:
                errors.append({
                    "account_number": account.account_number,
                    "error": str(e)
                })
        
        return {
            "financial_year": financial_year,
            "quarter": quarter,
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat()
            },
            "accounts_processed": processed,
            "total_tds": float(total_tds),
            "errors": errors
        }
    
    def check_dormant_accounts(
        self,
        inactive_months: int = 24
    ) -> Dict[str, Any]:
        """Check and mark dormant accounts"""
        cutoff_date = date.today() - timedelta(days=inactive_months * 30)
        
        # Get accounts with no recent transactions
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.account_type == 'savings',  # Only savings can be dormant
                DepositAccount.is_deleted == False
            )
        ).all()
        
        marked_count = 0
        
        for account in accounts:
            # Get last transaction
            last_txn = self.db.query(DepositTransaction).filter(
                and_(
                    DepositTransaction.deposit_account_id == account.id,
                    DepositTransaction.transaction_type.in_(['deposit', 'withdrawal'])
                )
            ).order_by(DepositTransaction.transaction_date.desc()).first()
            
            if not last_txn or last_txn.transaction_date < cutoff_date:
                # Mark as dormant
                account.status = 'dormant'
                account.updated_by = self.user_id
                marked_count += 1
        
        self.db.commit()
        
        return {
            "inactive_months": inactive_months,
            "cutoff_date": cutoff_date.isoformat(),
            "accounts_checked": len(accounts),
            "marked_count": marked_count
        }
    
    def reactivate_dormant_account(self, account_id: int) -> Dict[str, Any]:
        """Reactivate a dormant account"""
        account = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.id == account_id,
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.is_deleted == False
            )
        ).first()
        
        if not account:
            raise CustomException(status_code=404, message="Account not found")
        
        if account.status != 'dormant':
            raise CustomException(
                status_code=400,
                message="Account is not dormant"
            )
        
        account.status = 'active'
        account.updated_by = self.user_id
        
        self.db.commit()
        
        return {
            "account_number": account.account_number,
            "status": "active",
            "reactivated_date": datetime.utcnow().isoformat()
        }
    
    def apply_penalties_batch(
        self,
        penalty_type: str
    ) -> Dict[str, Any]:
        """Apply penalties in batch"""
        if penalty_type == 'rd_missed':
            return self._apply_rd_missed_installment_penalties()
        elif penalty_type == 'min_balance':
            return self._apply_min_balance_penalties()
        elif penalty_type == 'late_payment':
            return self._apply_late_payment_penalties()
        else:
            raise CustomException(
                status_code=400,
                message=f"Unknown penalty type: {penalty_type}"
            )
    
    def _apply_rd_missed_installment_penalties(self) -> Dict[str, Any]:
        """Apply penalties for missed RD installments"""
        today = date.today()
        
        # Get RD accounts with missed installments
        accounts = self.db.query(DepositAccount).join(
            DepositProduct
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_type == 'rd',
                DepositAccount.status == 'active',
                DepositAccount.next_installment_date < today,
                DepositProduct.missed_installment_penalty > 0,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        applied_count = 0
        total_penalty = Decimal('0')
        
        for account in accounts:
            # Calculate days overdue
            days_overdue = (today - account.next_installment_date).days
            
            if days_overdue > 0:
                # Calculate penalty
                penalty_rate = account.product.missed_installment_penalty
                penalty_amount = (account.installment_amount * penalty_rate) / Decimal('100')
                
                # Create penalty transaction
                self.account_service._create_transaction(
                    account_id=account.id,
                    transaction_type='penalty',
                    amount=penalty_amount,
                    balance_before=account.current_balance,
                    balance_after=account.current_balance - penalty_amount,
                    transaction_date=today,
                    remarks=f"Missed installment penalty - {days_overdue} days overdue"
                )
                
                # Update account
                account.current_balance -= penalty_amount
                account.missed_installments += 1
                
                applied_count += 1
                total_penalty += penalty_amount
        
        self.db.commit()
        
        return {
            "penalty_type": "rd_missed",
            "accounts_processed": len(accounts),
            "penalties_applied": applied_count,
            "total_penalty": float(total_penalty)
        }
    
    def _apply_min_balance_penalties(self) -> Dict[str, Any]:
        """Apply minimum balance penalties"""
        # Get savings accounts below minimum balance
        accounts = self.db.query(DepositAccount).join(
            DepositProduct
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_type == 'savings',
                DepositAccount.status == 'active',
                DepositAccount.current_balance < DepositProduct.min_balance,
                DepositProduct.min_balance_penalty > 0,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        applied_count = 0
        total_penalty = Decimal('0')
        
        for account in accounts:
            penalty_amount = account.product.min_balance_penalty
            
            # Create penalty transaction
            self.account_service._create_transaction(
                account_id=account.id,
                transaction_type='penalty',
                amount=penalty_amount,
                balance_before=account.current_balance,
                balance_after=account.current_balance - penalty_amount,
                transaction_date=date.today(),
                remarks=f"Minimum balance penalty"
            )
            
            # Update account
            account.current_balance -= penalty_amount
            
            applied_count += 1
            total_penalty += penalty_amount
        
        self.db.commit()
        
        return {
            "penalty_type": "min_balance",
            "accounts_processed": len(accounts),
            "penalties_applied": applied_count,
            "total_penalty": float(total_penalty)
        }
    
    def _apply_late_payment_penalties(self) -> Dict[str, Any]:
        """Apply late payment penalties"""
        # Similar to RD missed installments
        return self._apply_rd_missed_installment_penalties()
    
    def process_mis_payout_batch(
        self,
        payout_month: Optional[date] = None
    ) -> Dict[str, Any]:
        """Process MIS monthly payouts"""
        if not payout_month:
            payout_month = date.today().replace(day=1)
        
        # Get active MIS accounts
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_type == 'mis',
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).all()
        
        processed = 0
        total_payout = Decimal('0')
        errors = []
        
        for account in accounts:
            try:
                # Calculate monthly payout
                annual_interest = account.principal_amount * account.interest_rate / Decimal('100')
                monthly_payout = annual_interest / Decimal('12')
                
                # Calculate TDS if applicable
                tds_amount = Decimal('0')
                if account.product.tds_applicable:
                    # Check annual threshold
                    # For simplicity, deduct TDS if monthly payout * 12 > threshold
                    annual_interest_total = monthly_payout * Decimal('12')
                    if annual_interest_total >= account.product.tds_threshold:
                        tds_amount = monthly_payout * (account.product.tds_rate / Decimal('100'))
                
                net_payout = monthly_payout - tds_amount
                
                # Create interest credit transaction
                self.account_service._create_transaction(
                    account_id=account.id,
                    transaction_type='interest_credit',
                    amount=net_payout,
                    balance_before=account.current_balance,
                    balance_after=account.current_balance + net_payout,
                    transaction_date=payout_month,
                    remarks=f"MIS monthly payout for {payout_month.strftime('%B %Y')}",
                    interest_period_start=payout_month,
                    interest_period_end=payout_month,
                    interest_rate=account.interest_rate,
                    tds_amount=tds_amount
                )
                
                # Update account
                account.interest_earned += monthly_payout
                account.total_interest_posted += net_payout
                
                if account.linked_account_number:
                    # TODO: Transfer to linked account
                    pass
                
                processed += 1
                total_payout += net_payout
                
            except Exception as e:
                errors.append({
                    "account_number": account.account_number,
                    "error": str(e)
                })
        
        self.db.commit()
        
        return {
            "payout_month": payout_month.isoformat(),
            "accounts_processed": processed,
            "total_payout": float(total_payout),
            "errors": errors
        }
    
    def bulk_close_accounts(
        self,
        account_ids: List[int],
        closure_reason: str
    ) -> Dict[str, Any]:
        """Close multiple accounts"""
        success_count = 0
        failed_count = 0
        errors = []
        
        for account_id in account_ids:
            try:
                self.account_service.close_account_prematurely(
                    account_id=account_id,
                    closure_reason=closure_reason
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({
                    "account_id": account_id,
                    "error": str(e)
                })
        
        return {
            "total_count": len(account_ids),
            "success_count": success_count,
            "failed_count": failed_count,
            "errors": errors
        }
    
    def schedule_interest_posting(
        self,
        posting_date: date,
        account_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule interest posting"""
        # Get accounts due for interest posting
        query = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.next_interest_date <= posting_date,
                DepositAccount.is_deleted == False
            )
        )
        
        if account_type:
            query = query.filter(DepositAccount.account_type == account_type)
        
        accounts = query.all()
        
        processed = 0
        total_interest = Decimal('0')
        errors = []
        
        for account in accounts:
            try:
                # Calculate and post interest
                result = self.interest_service.post_interest(
                    account_id=account.id,
                    to_date=posting_date
                )
                
                processed += 1
                total_interest += Decimal(str(result['interest_posted']))
                
            except Exception as e:
                errors.append({
                    "account_number": account.account_number,
                    "error": str(e)
                })
        
        return {
            "posting_date": posting_date.isoformat(),
            "accounts_processed": processed,
            "total_interest": float(total_interest),
            "errors": errors
        }
