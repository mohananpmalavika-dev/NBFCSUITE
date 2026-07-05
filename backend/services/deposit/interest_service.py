"""
Interest Calculation Service

Handles all interest calculation and posting logic including:
- Multiple calculation methods (simple, compound, daily balance, monthly average)
- Interest posting to accounts
- TDS calculation and deduction
- Batch interest processing
- Interest certificates
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import calendar

from backend.shared.database.deposit_models import (
    DepositAccount, DepositProduct, DepositTransaction,
    DepositInterestCalculation, DepositPassbookEntry
)
from backend.shared.common.response import CustomException


class InterestCalculationService:
    """Service for interest calculation and posting"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== INTEREST CALCULATION ====================
    
    def calculate_simple_interest(
        self,
        principal: Decimal,
        rate: Decimal,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """
        Calculate simple interest for a period
        
        Formula: Interest = Principal × Rate × Days / (100 × 365)
        """
        days = (to_date - from_date).days
        
        if days <= 0:
            return {
                "interest": Decimal('0'),
                "days": 0,
                "rate": rate,
                "principal": principal
            }
        
        interest = (principal * rate * days) / (Decimal('100') * Decimal('365'))
        interest = interest.quantize(Decimal('0.01'))
        
        return {
            "interest": interest,
            "days": days,
            "rate": rate,
            "principal": principal,
            "from_date": from_date,
            "to_date": to_date
        }
    
    def calculate_compound_interest(
        self,
        principal: Decimal,
        rate: Decimal,
        from_date: date,
        to_date: date,
        frequency: str = 'quarterly'
    ) -> Dict[str, Any]:
        """
        Calculate compound interest for a period
        
        Formula: A = P × (1 + r/n)^(n×t)
        """
        import math
        
        days = (to_date - from_date).days
        
        if days <= 0:
            return {
                "interest": Decimal('0'),
                "days": 0,
                "rate": rate,
                "principal": principal
            }
        
        # Frequency mapping
        frequency_map = {
            'daily': 365,
            'monthly': 12,
            'quarterly': 4,
            'half_yearly': 2,
            'yearly': 1
        }
        
        n = frequency_map.get(frequency, 4)
        r = float(rate) / 100
        t = days / 365.0
        
        # Calculate compound interest
        amount = float(principal) * math.pow((1 + r / n), (n * t))
        amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        
        interest = amount - principal
        
        return {
            "interest": interest,
            "maturity_amount": amount,
            "days": days,
            "rate": rate,
            "principal": principal,
            "frequency": frequency,
            "from_date": from_date,
            "to_date": to_date
        }
    
    def calculate_daily_balance_interest(
        self,
        account_id: int,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """
        Calculate interest using daily balance method
        
        Formula: Interest = Σ(Daily Balance × Rate × 1 / 36500)
        """
        account = self._get_account(account_id)
        
        # Get all transactions in the period
        transactions = self.db.query(DepositTransaction).filter(
            and_(
                DepositTransaction.deposit_account_id == account_id,
                DepositTransaction.transaction_date >= from_date,
                DepositTransaction.transaction_date <= to_date
            )
        ).order_by(DepositTransaction.transaction_date).all()
        
        # Calculate daily interest
        total_interest = Decimal('0')
        current_date = from_date
        current_balance = self._get_balance_on_date(account_id, from_date)
        
        daily_details = []
        
        while current_date <= to_date:
            # Check if balance changed on this date
            for txn in transactions:
                if txn.transaction_date == current_date:
                    current_balance = txn.balance_after
            
            # Calculate interest for this day
            daily_interest = (current_balance * account.interest_rate) / (Decimal('100') * Decimal('365'))
            daily_interest = daily_interest.quantize(Decimal('0.01'))
            total_interest += daily_interest
            
            daily_details.append({
                "date": current_date,
                "balance": float(current_balance),
                "interest": float(daily_interest)
            })
            
            current_date += timedelta(days=1)
        
        return {
            "interest": total_interest,
            "days": (to_date - from_date).days + 1,
            "rate": account.interest_rate,
            "method": "daily_balance",
            "from_date": from_date,
            "to_date": to_date,
            "daily_details": daily_details[:10]  # Return first 10 days for reference
        }
    
    def calculate_monthly_average_balance_interest(
        self,
        account_id: int,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """
        Calculate interest using monthly average balance
        
        Formula: 
        Average Balance = Sum of Daily Balances / Days in Month
        Interest = Average Balance × Rate × Days / (100 × 365)
        """
        account = self._get_account(account_id)
        
        # Get month boundaries
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        
        # Get all transactions in the month
        transactions = self.db.query(DepositTransaction).filter(
            and_(
                DepositTransaction.deposit_account_id == account_id,
                DepositTransaction.transaction_date >= first_day,
                DepositTransaction.transaction_date <= last_day
            )
        ).order_by(DepositTransaction.transaction_date).all()
        
        # Calculate daily balances
        total_balance = Decimal('0')
        current_date = first_day
        current_balance = self._get_balance_on_date(account_id, first_day)
        days = 0
        
        while current_date <= last_day:
            # Check if balance changed on this date
            for txn in transactions:
                if txn.transaction_date == current_date:
                    current_balance = txn.balance_after
            
            total_balance += current_balance
            days += 1
            current_date += timedelta(days=1)
        
        # Calculate average balance
        average_balance = total_balance / Decimal(str(days))
        average_balance = average_balance.quantize(Decimal('0.01'))
        
        # Calculate interest on average balance
        interest = (average_balance * account.interest_rate * days) / (Decimal('100') * Decimal('365'))
        interest = interest.quantize(Decimal('0.01'))
        
        return {
            "interest": interest,
            "average_balance": average_balance,
            "days": days,
            "rate": account.interest_rate,
            "method": "monthly_average",
            "month": month,
            "year": year
        }
    
    def calculate_account_interest(
        self,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate interest for account based on product configuration
        """
        account = self._get_account(account_id)
        product = account.product
        
        # Determine period
        if not from_date:
            from_date = account.last_interest_date or account.opening_date
        
        if not to_date:
            to_date = date.today()
        
        # Validate period
        if to_date <= from_date:
            raise CustomException(
                status_code=400,
                message="To date must be after from date"
            )
        
        # Calculate based on product configuration
        calculation_method = product.interest_calculation_method
        calculation_frequency = product.interest_calculation_frequency
        
        if calculation_frequency == 'daily':
            result = self.calculate_daily_balance_interest(account_id, from_date, to_date)
        elif calculation_frequency == 'monthly':
            # Use monthly average if it's end of month
            if to_date.day == calendar.monthrange(to_date.year, to_date.month)[1]:
                result = self.calculate_monthly_average_balance_interest(
                    account_id, to_date.month, to_date.year
                )
            else:
                result = self.calculate_simple_interest(
                    account.current_balance, account.interest_rate, from_date, to_date
                )
        else:
            # Use product calculation method
            if calculation_method == 'simple':
                result = self.calculate_simple_interest(
                    account.current_balance, account.interest_rate, from_date, to_date
                )
            else:
                result = self.calculate_compound_interest(
                    account.current_balance, account.interest_rate, from_date, to_date,
                    calculation_frequency
                )
        
        # Calculate TDS if applicable
        tds_details = self._calculate_tds(
            account_id, result['interest'], product.tds_rate, product.tds_threshold
        )
        
        return {
            **result,
            "tds_details": tds_details,
            "net_interest": result['interest'] - tds_details['tds_amount']
        }
    
    # ==================== TDS CALCULATION ====================
    
    def _calculate_tds(
        self,
        account_id: int,
        interest_amount: Decimal,
        tds_rate: Decimal,
        tds_threshold: Decimal
    ) -> Dict[str, Any]:
        """Calculate TDS on interest"""
        # Get total interest for financial year
        today = date.today()
        fy_start = date(today.year if today.month >= 4 else today.year - 1, 4, 1)
        fy_end = date(today.year + 1 if today.month >= 4 else today.year, 3, 31)
        
        # Get total interest earned in FY
        total_interest_fy = self.db.query(
            func.sum(DepositInterestCalculation.interest_amount)
        ).filter(
            and_(
                DepositInterestCalculation.deposit_account_id == account_id,
                DepositInterestCalculation.posted == True,
                DepositInterestCalculation.calculation_period_end >= fy_start,
                DepositInterestCalculation.calculation_period_end <= fy_end
            )
        ).scalar() or Decimal('0')
        
        # Add current interest
        projected_interest = total_interest_fy + interest_amount
        
        # Check if TDS applicable
        tds_applicable = projected_interest > tds_threshold
        tds_amount = Decimal('0')
        
        if tds_applicable:
            tds_amount = (interest_amount * tds_rate / Decimal('100')).quantize(Decimal('0.01'))
        
        return {
            "tds_applicable": tds_applicable,
            "tds_rate": float(tds_rate),
            "tds_amount": tds_amount,
            "gross_interest": interest_amount,
            "net_interest": interest_amount - tds_amount,
            "fy_total_interest": float(projected_interest),
            "tds_threshold": float(tds_threshold)
        }
    
    # ==================== INTEREST POSTING ====================
    
    def post_interest(
        self,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calculate and post interest to account"""
        account = self._get_account(account_id)
        
        if account.status != 'active':
            raise CustomException(
                status_code=400,
                message=f"Cannot post interest to {account.status} account"
            )
        
        # Calculate interest
        interest_calc = self.calculate_account_interest(account_id, from_date, to_date)
        
        if interest_calc['interest'] <= 0:
            raise CustomException(
                status_code=400,
                message="No interest to post"
            )
        
        # Create interest calculation record
        calc_record = DepositInterestCalculation(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            calculation_period_start=interest_calc.get('from_date', from_date),
            calculation_period_end=interest_calc.get('to_date', to_date),
            opening_balance=account.current_balance,
            closing_balance=account.current_balance,
            average_balance=interest_calc.get('average_balance'),
            interest_rate=interest_calc['rate'],
            days_in_period=interest_calc['days'],
            interest_amount=interest_calc['interest'],
            calculation_method=interest_calc.get('method', account.product.interest_calculation_method),
            tds_applicable=interest_calc['tds_details']['tds_applicable'],
            tds_amount=interest_calc['tds_details']['tds_amount'],
            tds_rate=interest_calc['tds_details']['tds_rate'],
            net_interest=interest_calc['net_interest'],
            posted=True,
            posted_date=date.today(),
            calculated_by=self.user_id
        )
        
        self.db.add(calc_record)
        self.db.flush()
        
        # Credit interest to account
        from .account_service import DepositAccountService
        account_service = DepositAccountService(self.db, self.tenant_id, self.user_id)
        
        balance_before = account.current_balance
        balance_after = balance_before + interest_calc['net_interest']
        
        interest_txn = account_service._create_transaction(
            account_id=account_id,
            transaction_type='interest_credit',
            amount=interest_calc['interest'],
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_date=date.today(),
            interest_period_start=calc_record.calculation_period_start,
            interest_period_end=calc_record.calculation_period_end,
            interest_rate=interest_calc['rate'],
            remarks=f"Interest credit for period {calc_record.calculation_period_start} to {calc_record.calculation_period_end}"
        )
        
        # Deduct TDS if applicable
        if interest_calc['tds_details']['tds_amount'] > 0:
            tds_txn = account_service._create_transaction(
                account_id=account_id,
                transaction_type='interest_tds',
                amount=interest_calc['tds_details']['tds_amount'],
                balance_before=balance_after,
                balance_after=balance_after,  # TDS doesn't affect balance (deducted from credit)
                transaction_date=date.today(),
                tds_amount=interest_calc['tds_details']['tds_amount'],
                remarks=f"TDS @ {interest_calc['tds_details']['tds_rate']}% on interest"
            )
        
        # Update calculation record with transaction ID
        calc_record.transaction_id = interest_txn.id
        
        # Update account
        account.current_balance = balance_after
        account.interest_earned += interest_calc['net_interest']
        account.total_interest_posted += interest_calc['net_interest']
        account.last_interest_date = calc_record.calculation_period_end
        
        # Update next interest date
        account.next_interest_date = self._calculate_next_interest_date(
            calc_record.calculation_period_end,
            account.product.interest_payout_frequency
        )
        
        account.updated_by = self.user_id
        
        # Create passbook entries
        account_service._create_passbook_entry(
            account_id,
            date.today(),
            f"Interest Credit ({calc_record.calculation_period_start} to {calc_record.calculation_period_end})",
            interest_txn.id,
            deposit_amount=interest_calc['interest'],
            balance=balance_after
        )
        
        if interest_calc['tds_details']['tds_amount'] > 0:
            account_service._create_passbook_entry(
                account_id,
                date.today(),
                f"TDS Deducted @ {interest_calc['tds_details']['tds_rate']}%",
                None,
                withdrawal_amount=interest_calc['tds_details']['tds_amount'],
                balance=balance_after
            )
        
        self.db.commit()
        
        return {
            "account_number": account.account_number,
            "interest_posted": float(interest_calc['interest']),
            "tds_deducted": float(interest_calc['tds_details']['tds_amount']),
            "net_interest": float(interest_calc['net_interest']),
            "period_start": calc_record.calculation_period_start.isoformat(),
            "period_end": calc_record.calculation_period_end.isoformat(),
            "new_balance": float(balance_after),
            "calculation_id": calc_record.id
        }
    
    # ==================== BATCH PROCESSING ====================
    
    def batch_calculate_interest(
        self,
        account_type: Optional[str] = None,
        product_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Batch calculate interest for multiple accounts"""
        # Get eligible accounts
        query = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        )
        
        if account_type:
            query = query.filter(DepositAccount.account_type == account_type)
        
        if product_id:
            query = query.filter(DepositAccount.deposit_product_id == product_id)
        
        # Filter accounts due for interest
        query = query.filter(
            and_(
                DepositAccount.next_interest_date.isnot(None),
                DepositAccount.next_interest_date <= date.today()
            )
        )
        
        accounts = query.all()
        
        results = {
            "total_accounts": len(accounts),
            "successful": 0,
            "failed": 0,
            "total_interest": Decimal('0'),
            "total_tds": Decimal('0'),
            "errors": []
        }
        
        for account in accounts:
            try:
                result = self.post_interest(account.id)
                results["successful"] += 1
                results["total_interest"] += Decimal(str(result["interest_posted"]))
                results["total_tds"] += Decimal(str(result["tds_deducted"]))
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "account_number": account.account_number,
                    "error": str(e)
                })
        
        return {
            **results,
            "total_interest": float(results["total_interest"]),
            "total_tds": float(results["total_tds"])
        }
    
    # ==================== INTEREST CERTIFICATE ====================
    
    def generate_interest_certificate(
        self,
        account_id: int,
        financial_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate interest certificate for financial year"""
        account = self._get_account(account_id)
        
        # Determine financial year
        if not financial_year:
            today = date.today()
            if today.month >= 4:
                fy_start_year = today.year
            else:
                fy_start_year = today.year - 1
            financial_year = f"{fy_start_year}-{fy_start_year + 1}"
        
        # Parse FY
        fy_parts = financial_year.split('-')
        fy_start = date(int(fy_parts[0]), 4, 1)
        fy_end = date(int(fy_parts[1]), 3, 31)
        
        # Get all interest calculations for FY
        calculations = self.db.query(DepositInterestCalculation).filter(
            and_(
                DepositInterestCalculation.deposit_account_id == account_id,
                DepositInterestCalculation.posted == True,
                DepositInterestCalculation.calculation_period_end >= fy_start,
                DepositInterestCalculation.calculation_period_end <= fy_end
            )
        ).order_by(DepositInterestCalculation.calculation_period_start).all()
        
        # Calculate totals
        total_interest = sum(calc.interest_amount for calc in calculations)
        total_tds = sum(calc.tds_amount for calc in calculations)
        net_interest = total_interest - total_tds
        
        # Build certificate
        certificate = {
            "account": {
                "account_number": account.account_number,
                "account_type": account.account_type,
                "customer_id": account.customer_id
            },
            "financial_year": financial_year,
            "period": {
                "from": fy_start.isoformat(),
                "to": fy_end.isoformat()
            },
            "summary": {
                "total_interest_earned": float(total_interest),
                "total_tds_deducted": float(total_tds),
                "net_interest": float(net_interest)
            },
            "calculations": [
                {
                    "period_start": calc.calculation_period_start.isoformat(),
                    "period_end": calc.calculation_period_end.isoformat(),
                    "interest": float(calc.interest_amount),
                    "tds": float(calc.tds_amount),
                    "net": float(calc.net_interest),
                    "posted_date": calc.posted_date.isoformat() if calc.posted_date else None
                }
                for calc in calculations
            ],
            "certificate_date": date.today().isoformat()
        }
        
        return certificate
    
    # ==================== HELPER METHODS ====================
    
    def _get_account(self, account_id: int) -> DepositAccount:
        """Get account with validation"""
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
    
    def _get_balance_on_date(self, account_id: int, on_date: date) -> Decimal:
        """Get account balance on specific date"""
        # Get last transaction on or before date
        last_txn = self.db.query(DepositTransaction).filter(
            and_(
                DepositTransaction.deposit_account_id == account_id,
                DepositTransaction.transaction_date <= on_date
            )
        ).order_by(DepositTransaction.transaction_date.desc()).first()
        
        if last_txn:
            return last_txn.balance_after
        
        # If no transaction, account not yet opened or balance is 0
        return Decimal('0')
    
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
            # Next month same date
            if from_date.month == 12:
                return date(from_date.year + 1, 1, from_date.day)
            else:
                return date(from_date.year, from_date.month + 1, from_date.day)
        elif frequency == 'quarterly':
            # Next quarter
            month = from_date.month + 3
            year = from_date.year
            if month > 12:
                month -= 12
                year += 1
            return date(year, month, from_date.day)
        elif frequency == 'maturity':
            return None
        
        return None
    
    # ==================== INTEREST HISTORY ====================
    
    def get_interest_history(
        self,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get interest calculation history"""
        query = self.db.query(DepositInterestCalculation).filter(
            and_(
                DepositInterestCalculation.deposit_account_id == account_id,
                DepositInterestCalculation.posted == True
            )
        )
        
        if from_date:
            query = query.filter(DepositInterestCalculation.calculation_period_start >= from_date)
        
        if to_date:
            query = query.filter(DepositInterestCalculation.calculation_period_end <= to_date)
        
        calculations = query.order_by(
            DepositInterestCalculation.calculation_period_start.desc()
        ).offset(skip).limit(limit).all()
        
        return [
            {
                "id": calc.id,
                "period_start": calc.calculation_period_start.isoformat(),
                "period_end": calc.calculation_period_end.isoformat(),
                "days": calc.days_in_period,
                "interest_rate": float(calc.interest_rate),
                "interest_amount": float(calc.interest_amount),
                "tds_amount": float(calc.tds_amount),
                "net_interest": float(calc.net_interest),
                "posted_date": calc.posted_date.isoformat() if calc.posted_date else None,
                "calculation_method": calc.calculation_method
            }
            for calc in calculations
        ]
