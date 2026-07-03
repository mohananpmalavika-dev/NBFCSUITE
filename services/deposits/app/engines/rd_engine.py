"""
Recurring Deposit Engine
Handles RD-specific logic: installments, penalties, collections
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta


class RDEngine:
    """
    Recurring Deposit Engine
    Manages monthly installments, auto-debit, penalties
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_rd_maturity(
        self,
        monthly_installment: Decimal,
        num_months: int,
        annual_rate: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate RD maturity using the formula:
        M = P × n × (n + 1) / 2 × (r / 12) / 100 + (P × n)
        
        Where:
        M = Maturity amount
        P = Monthly installment
        n = Number of months
        r = Annual interest rate
        """
        P = Decimal(str(monthly_installment))
        n = Decimal(str(num_months))
        r = Decimal(str(annual_rate))
        
        # Total principal deposited
        total_principal = P * n
        
        # Interest calculation
        # Each installment earns interest for different periods
        total_interest = Decimal('0')
        
        for month in range(1, int(num_months) + 1):
            months_earning = num_months - month + 1
            installment_interest = P * (r / Decimal('1200')) * Decimal(str(months_earning))
            total_interest += installment_interest
        
        maturity_amount = total_principal + total_interest
        
        # Round to 2 decimal places
        total_interest = total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        maturity_amount = maturity_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            "monthly_installment": float(P),
            "num_months": num_months,
            "annual_rate": float(r),
            "total_principal": float(total_principal),
            "total_interest": float(total_interest),
            "maturity_amount": float(maturity_amount),
            "average_return": float((total_interest / total_principal) * Decimal('100'))
        }
    
    def generate_installment_schedule(
        self,
        account_id: str,
        monthly_installment: Decimal,
        num_installments: int,
        start_date: date,
        installment_day: int = 5  # Default: 5th of every month
    ) -> List[Dict[str, Any]]:
        """
        Generate complete RD installment schedule
        """
        from ..models import RDSchedule, RDInstallmentStatus
        import uuid
        
        schedule = []
        current_date = start_date
        
        for installment_num in range(1, num_installments + 1):
            # Calculate due date
            due_date = current_date + relativedelta(months=installment_num - 1)
            
            # Set to specific day of month
            try:
                due_date = due_date.replace(day=installment_day)
            except ValueError:
                # Handle months with fewer days (e.g., Feb 30)
                due_date = due_date.replace(day=28)
            
            schedule_entry = RDSchedule(
                id=uuid.uuid4(),
                account_id=account_id,
                installment_number=installment_num,
                installment_amount=monthly_installment,
                due_date=due_date,
                status=RDInstallmentStatus.SCHEDULED,
                grace_period_days=7
            )
            
            self.db.add(schedule_entry)
            
            schedule.append({
                "installment_number": installment_num,
                "installment_amount": float(monthly_installment),
                "due_date": due_date.isoformat(),
                "status": "SCHEDULED"
            })
        
        self.db.commit()
        
        return schedule
    
    def process_installment_payment(
        self,
        schedule_id: str,
        amount: Decimal,
        payment_date: date,
        payment_mode: str,
        payment_reference: str = None
    ) -> Dict[str, Any]:
        """
        Process RD installment payment
        Calculate penalty if overdue
        """
        from ..models import RDSchedule, RDInstallmentStatus
        
        schedule = self.db.query(RDSchedule).filter(
            RDSchedule.id == schedule_id
        ).first()
        
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        if schedule.status == RDInstallmentStatus.PAID:
            raise ValueError("Installment already paid")
        
        # Calculate penalty if overdue
        penalty = Decimal('0')
        overdue_days = 0
        
        if payment_date > schedule.due_date + timedelta(days=schedule.grace_period_days):
            overdue_days = (payment_date - schedule.due_date).days - schedule.grace_period_days
            penalty = self._calculate_penalty(
                schedule.installment_amount,
                overdue_days
            )
        
        total_due = schedule.installment_amount + penalty
        
        if amount < total_due:
            raise ValueError(f"Insufficient amount. Required: {total_due}, Provided: {amount}")
        
        # Update schedule
        schedule.paid_amount = amount
        schedule.paid_date = payment_date
        schedule.payment_mode = payment_mode
        schedule.payment_reference = payment_reference
        schedule.penalty_amount = penalty
        schedule.overdue_days = overdue_days
        schedule.status = RDInstallmentStatus.PAID
        
        self.db.commit()
        
        return {
            "schedule_id": str(schedule.id),
            "installment_number": schedule.installment_number,
            "installment_amount": float(schedule.installment_amount),
            "penalty_amount": float(penalty),
            "total_paid": float(amount),
            "payment_date": payment_date.isoformat(),
            "overdue_days": overdue_days,
            "status": "PAID"
        }
    
    def _calculate_penalty(
        self,
        installment_amount: Decimal,
        overdue_days: int,
        penalty_rate: Decimal = Decimal('2.0')  # 2% per month default
    ) -> Decimal:
        """
        Calculate penalty for late payment
        Typically 2% per month on installment amount
        """
        months_overdue = Decimal(str(overdue_days)) / Decimal('30')
        penalty = (installment_amount * penalty_rate * months_overdue) / Decimal('100')
        
        return penalty.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def get_overdue_installments(
        self,
        account_id: str = None,
        customer_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get all overdue RD installments
        For collections and reminder purposes
        """
        from ..models import RDSchedule, RDInstallmentStatus, DepositAccount
        
        query = self.db.query(RDSchedule, DepositAccount).join(
            DepositAccount,
            RDSchedule.account_id == DepositAccount.id
        ).filter(
            RDSchedule.status.in_([
                RDInstallmentStatus.SCHEDULED,
                RDInstallmentStatus.OVERDUE
            ]),
            RDSchedule.due_date < date.today()
        )
        
        if account_id:
            query = query.filter(RDSchedule.account_id == account_id)
        
        if customer_id:
            query = query.filter(DepositAccount.customer_id == customer_id)
        
        results = query.all()
        
        overdue_list = []
        
        for schedule, account in results:
            overdue_days = (date.today() - schedule.due_date).days
            penalty = self._calculate_penalty(schedule.installment_amount, overdue_days)
            
            overdue_list.append({
                "schedule_id": str(schedule.id),
                "account_id": str(account.id),
                "account_number": account.account_number,
                "customer_id": str(account.customer_id),
                "cif_number": account.cif_number,
                "installment_number": schedule.installment_number,
                "installment_amount": float(schedule.installment_amount),
                "due_date": schedule.due_date.isoformat(),
                "overdue_days": overdue_days,
                "penalty_amount": float(penalty),
                "total_due": float(schedule.installment_amount + penalty)
            })
        
        return overdue_list
    
    def waive_penalty(
        self,
        schedule_id: str,
        waiver_reason: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """
        Waive penalty for RD installment
        Requires approval
        """
        from ..models import RDSchedule
        
        schedule = self.db.query(RDSchedule).filter(
            RDSchedule.id == schedule_id
        ).first()
        
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        original_penalty = schedule.penalty_amount
        schedule.penalty_waived = True
        schedule.waiver_reason = waiver_reason
        schedule.penalty_amount = Decimal('0')
        
        self.db.commit()
        
        return {
            "schedule_id": str(schedule.id),
            "original_penalty": float(original_penalty),
            "waived_amount": float(original_penalty),
            "waiver_reason": waiver_reason,
            "approved_by": approved_by,
            "status": "WAIVED"
        }
    
    def auto_debit_setup(
        self,
        account_id: str,
        debit_account_number: str,
        bank_name: str = None,
        ifsc_code: str = None
    ) -> Dict[str, Any]:
        """
        Setup auto-debit for RD installments
        Integrates with payment gateway/NACH
        """
        from ..models import DepositAccount
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        # Store auto-debit details in metadata
        if account.metadata is None:
            account.metadata = {}
        
        account.metadata["auto_debit"] = {
            "enabled": True,
            "debit_account": debit_account_number,
            "bank_name": bank_name,
            "ifsc_code": ifsc_code,
            "setup_date": date.today().isoformat()
        }
        
        self.db.commit()
        
        return {
            "account_id": str(account.id),
            "auto_debit_enabled": True,
            "debit_account": debit_account_number,
            "status": "ACTIVE"
        }
    
    def get_rd_account_summary(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        Get complete RD account summary
        Shows payment status, maturity projection
        """
        from ..models import DepositAccount, RDSchedule, RDInstallmentStatus
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        schedules = self.db.query(RDSchedule).filter(
            RDSchedule.account_id == account_id
        ).order_by(RDSchedule.installment_number).all()
        
        total_installments = len(schedules)
        paid_installments = sum(
            1 for s in schedules if s.status == RDInstallmentStatus.PAID
        )
        overdue_installments = sum(
            1 for s in schedules 
            if s.status == RDInstallmentStatus.SCHEDULED 
            and s.due_date < date.today()
        )
        
        total_paid = sum(
            s.paid_amount for s in schedules 
            if s.status == RDInstallmentStatus.PAID
        ) or Decimal('0')
        
        total_penalties = sum(
            s.penalty_amount for s in schedules 
            if s.penalty_amount
        ) or Decimal('0')
        
        # Calculate projected maturity
        if schedules:
            monthly_installment = schedules[0].installment_amount
            maturity_calc = self.calculate_rd_maturity(
                monthly_installment,
                total_installments,
                account.interest_rate
            )
        else:
            maturity_calc = {}
        
        return {
            "account_id": str(account.id),
            "account_number": account.account_number,
            "customer_id": str(account.customer_id),
            "status": account.status,
            "open_date": account.open_date.isoformat(),
            "maturity_date": account.maturity_date.isoformat(),
            "interest_rate": float(account.interest_rate),
            "installment_summary": {
                "total_installments": total_installments,
                "paid_installments": paid_installments,
                "pending_installments": total_installments - paid_installments,
                "overdue_installments": overdue_installments
            },
            "financial_summary": {
                "total_paid": float(total_paid),
                "total_penalties": float(total_penalties),
                "projected_maturity": maturity_calc.get("maturity_amount")
            },
            "next_due": schedules[paid_installments].due_date.isoformat() if paid_installments < total_installments else None
        }
