"""
Notification Service

Handles all deposit-related notifications including:
- Maturity reminders
- RD installment due notices
- Minimum balance alerts
- Interest credit notifications
- Dormancy warnings
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from backend.shared.database.deposit_models import (
    DepositAccount, DepositProduct, DepositTransaction
)
from backend.shared.database.customer_models import Customer
from backend.shared.common.response import CustomException


class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def send_maturity_reminders(
        self,
        days_before: int = 30
    ) -> Dict[str, Any]:
        """Send maturity reminders"""
        reminder_date = date.today() + timedelta(days=days_before)
        
        # Get accounts maturing soon
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.status == 'active',
                DepositAccount.maturity_date == reminder_date,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        sent_count = 0
        notifications = []
        
        for account in accounts:
            customer = self.db.query(Customer).filter(
                Customer.id == account.customer_id
            ).first()
            
            if customer and customer.email:
                notification = {
                    "type": "maturity_reminder",
                    "account_number": account.account_number,
                    "customer_email": customer.email,
                    "customer_phone": customer.phone,
                    "maturity_date": account.maturity_date.isoformat(),
                    "maturity_amount": float(account.maturity_amount or account.current_balance),
                    "auto_renewal": account.auto_renewal,
                    "days_to_maturity": days_before,
                    "message": self._generate_maturity_message(account, customer, days_before)
                }
                
                # TODO: Send via email/SMS service
                notifications.append(notification)
                sent_count += 1
        
        return {
            "notification_type": "maturity_reminder",
            "days_before": days_before,
            "accounts_notified": sent_count,
            "notifications": notifications
        }
    
    def send_rd_installment_reminders(
        self,
        days_before: int = 3
    ) -> Dict[str, Any]:
        """Send RD installment due reminders"""
        reminder_date = date.today() + timedelta(days=days_before)
        
        # Get RD accounts with installment due
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_type == 'rd',
                DepositAccount.status == 'active',
                DepositAccount.next_installment_date == reminder_date,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        sent_count = 0
        notifications = []
        
        for account in accounts:
            customer = self.db.query(Customer).filter(
                Customer.id == account.customer_id
            ).first()
            
            if customer:
                notification = {
                    "type": "rd_installment_reminder",
                    "account_number": account.account_number,
                    "customer_email": customer.email,
                    "customer_phone": customer.phone,
                    "due_date": account.next_installment_date.isoformat(),
                    "installment_amount": float(account.installment_amount),
                    "installment_number": account.installments_paid + 1,
                    "total_installments": account.total_installments,
                    "days_to_due": days_before,
                    "message": self._generate_rd_reminder_message(account, customer, days_before)
                }
                
                notifications.append(notification)
                sent_count += 1
        
        return {
            "notification_type": "rd_installment_reminder",
            "days_before": days_before,
            "accounts_notified": sent_count,
            "notifications": notifications
        }
    
    def send_minimum_balance_alerts(self) -> Dict[str, Any]:
        """Send minimum balance violation alerts"""
        # Get savings accounts below minimum balance
        accounts = self.db.query(DepositAccount).join(
            DepositProduct
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_type == 'savings',
                DepositAccount.status == 'active',
                DepositAccount.current_balance < DepositProduct.min_balance,
                DepositAccount.is_deleted == False
            )
        ).all()
        
        sent_count = 0
        notifications = []
        
        for account in accounts:
            customer = self.db.query(Customer).filter(
                Customer.id == account.customer_id
            ).first()
            
            if customer:
                shortage = account.product.min_balance - account.current_balance
                
                notification = {
                    "type": "minimum_balance_alert",
                    "account_number": account.account_number,
                    "customer_email": customer.email,
                    "customer_phone": customer.phone,
                    "current_balance": float(account.current_balance),
                    "minimum_balance": float(account.product.min_balance),
                    "shortage": float(shortage),
                    "penalty": float(account.product.min_balance_penalty or 0),
                    "message": self._generate_min_balance_message(account, customer, shortage)
                }
                
                notifications.append(notification)
                sent_count += 1
        
        return {
            "notification_type": "minimum_balance_alert",
            "accounts_notified": sent_count,
            "notifications": notifications
        }
    
    def send_interest_credit_notifications(
        self,
        posting_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Send interest credit notifications"""
        if not posting_date:
            posting_date = date.today()
        
        # Get interest transactions for the date
        transactions = self.db.query(DepositTransaction).join(
            DepositAccount
        ).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositTransaction.transaction_type == 'interest_credit',
                DepositTransaction.transaction_date == posting_date
            )
        ).all()
        
        sent_count = 0
        notifications = []
        
        for txn in transactions:
            account = txn.account
            customer = self.db.query(Customer).filter(
                Customer.id == account.customer_id
            ).first()
            
            if customer:
                notification = {
                    "type": "interest_credit",
                    "account_number": account.account_number,
                    "customer_email": customer.email,
                    "customer_phone": customer.phone,
                    "interest_amount": float(txn.amount),
                    "tds_amount": float(txn.tds_amount or 0),
                    "net_amount": float(txn.amount - (txn.tds_amount or 0)),
                    "new_balance": float(txn.balance_after),
                    "posting_date": posting_date.isoformat(),
                    "message": self._generate_interest_credit_message(account, customer, txn)
                }
                
                notifications.append(notification)
                sent_count += 1
        
        return {
            "notification_type": "interest_credit",
            "posting_date": posting_date.isoformat(),
            "accounts_notified": sent_count,
            "notifications": notifications
        }
    
    def send_dormancy_warnings(
        self,
        inactive_months: int = 18
    ) -> Dict[str, Any]:
        """Send dormancy warning notifications"""
        cutoff_date = date.today() - timedelta(days=inactive_months * 30)
        
        accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.tenant_id == self.tenant_id,
                DepositAccount.account_type == 'savings',
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).all()
        
        sent_count = 0
        notifications = []
        
        for account in accounts:
            # Get last transaction
            last_txn = self.db.query(DepositTransaction).filter(
                and_(
                    DepositTransaction.deposit_account_id == account.id,
                    DepositTransaction.transaction_type.in_(['deposit', 'withdrawal'])
                )
            ).order_by(DepositTransaction.transaction_date.desc()).first()
            
            if last_txn and last_txn.transaction_date < cutoff_date:
                customer = self.db.query(Customer).filter(
                    Customer.id == account.customer_id
                ).first()
                
                if customer:
                    days_inactive = (date.today() - last_txn.transaction_date).days
                    
                    notification = {
                        "type": "dormancy_warning",
                        "account_number": account.account_number,
                        "customer_email": customer.email,
                        "customer_phone": customer.phone,
                        "last_transaction_date": last_txn.transaction_date.isoformat(),
                        "days_inactive": days_inactive,
                        "days_to_dormant": (730 - days_inactive) if days_inactive < 730 else 0,
                        "message": self._generate_dormancy_warning_message(account, customer, days_inactive)
                    }
                    
                    notifications.append(notification)
                    sent_count += 1
        
        return {
            "notification_type": "dormancy_warning",
            "inactive_months": inactive_months,
            "accounts_notified": sent_count,
            "notifications": notifications
        }
    
    def send_custom_notification(
        self,
        account_ids: List[int],
        subject: str,
        message: str,
        channels: List[str] = ['email', 'sms']
    ) -> Dict[str, Any]:
        """Send custom notification to specific accounts"""
        sent_count = 0
        notifications = []
        
        for account_id in account_ids:
            account = self.db.query(DepositAccount).filter(
                and_(
                    DepositAccount.id == account_id,
                    DepositAccount.tenant_id == self.tenant_id,
                    DepositAccount.is_deleted == False
                )
            ).first()
            
            if account:
                customer = self.db.query(Customer).filter(
                    Customer.id == account.customer_id
                ).first()
                
                if customer:
                    notification = {
                        "type": "custom",
                        "account_number": account.account_number,
                        "customer_email": customer.email if 'email' in channels else None,
                        "customer_phone": customer.phone if 'sms' in channels else None,
                        "subject": subject,
                        "message": message
                    }
                    
                    notifications.append(notification)
                    sent_count += 1
        
        return {
            "notification_type": "custom",
            "accounts_notified": sent_count,
            "notifications": notifications
        }
    
    # Message generators
    
    def _generate_maturity_message(
        self,
        account: DepositAccount,
        customer: Customer,
        days_before: int
    ) -> str:
        """Generate maturity reminder message"""
        return f"""
Dear {customer.first_name} {customer.last_name},

Your {account.account_type.upper()} account {account.account_number} will mature in {days_before} days on {account.maturity_date.strftime('%d-%b-%Y')}.

Maturity Amount: ₹{account.maturity_amount:,.2f}
{'This account will be automatically renewed.' if account.auto_renewal else 'Please visit the branch to claim your maturity amount.'}

Thank you for banking with us.
        """.strip()
    
    def _generate_rd_reminder_message(
        self,
        account: DepositAccount,
        customer: Customer,
        days_before: int
    ) -> str:
        """Generate RD installment reminder message"""
        return f"""
Dear {customer.first_name} {customer.last_name},

This is a reminder that your RD installment of ₹{account.installment_amount:,.2f} is due in {days_before} days on {account.next_installment_date.strftime('%d-%b-%Y')}.

Account Number: {account.account_number}
Installment: {account.installments_paid + 1} of {account.total_installments}

Please ensure timely payment to avoid penalties.

Thank you.
        """.strip()
    
    def _generate_min_balance_message(
        self,
        account: DepositAccount,
        customer: Customer,
        shortage: Decimal
    ) -> str:
        """Generate minimum balance alert message"""
        return f"""
Dear {customer.first_name} {customer.last_name},

Your savings account {account.account_number} has fallen below the minimum balance requirement.

Current Balance: ₹{account.current_balance:,.2f}
Minimum Required: ₹{account.product.min_balance:,.2f}
Shortage: ₹{shortage:,.2f}

Please deposit ₹{shortage:,.2f} to avoid penalty charges of ₹{account.product.min_balance_penalty:,.2f}.

Thank you.
        """.strip()
    
    def _generate_interest_credit_message(
        self,
        account: DepositAccount,
        customer: Customer,
        txn: DepositTransaction
    ) -> str:
        """Generate interest credit notification message"""
        return f"""
Dear {customer.first_name} {customer.last_name},

Interest has been credited to your account {account.account_number}.

Gross Interest: ₹{txn.amount:,.2f}
TDS Deducted: ₹{txn.tds_amount or 0:,.2f}
Net Interest: ₹{txn.amount - (txn.tds_amount or 0):,.2f}
New Balance: ₹{txn.balance_after:,.2f}

Thank you for banking with us.
        """.strip()
    
    def _generate_dormancy_warning_message(
        self,
        account: DepositAccount,
        customer: Customer,
        days_inactive: int
    ) -> str:
        """Generate dormancy warning message"""
        return f"""
Dear {customer.first_name} {customer.last_name},

Your savings account {account.account_number} has been inactive for {days_inactive} days.

Please make a transaction soon to keep your account active. Accounts with no transactions for 24 months may be marked as dormant.

Current Balance: ₹{account.current_balance:,.2f}

Thank you.
        """.strip()
