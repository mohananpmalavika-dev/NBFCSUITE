"""
Advanced Account Operations Service

Handles advanced operations including:
- Account freezing/unfreezing
- Lien marking and release
- Account transfer between customers
- Joint account management
- Account linking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, Text, ForeignKey
from backend.shared.database.deposit_models import DepositAccount
from backend.shared.database.models import Base
from backend.shared.common.response import CustomException


# Additional models (to be added to deposit_models.py)
class AccountFreeze(Base):
    """Account freeze record"""
    __tablename__ = "deposit_account_freezes"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False)
    
    freeze_type = Column(String(50), nullable=False)  # debit, credit, full
    freeze_reason = Column(Text, nullable=False)
    freeze_date = Column(Date, nullable=False)
    freeze_by = Column(String(50))
    
    unfreeze_date = Column(Date)
    unfreeze_by = Column(String(50))
    unfreeze_reason = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountLien(Base):
    """Account lien record"""
    __tablename__ = "deposit_account_liens"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False)
    
    lien_amount = Column(Numeric(15, 2), nullable=False)
    lien_reason = Column(Text, nullable=False)
    lien_reference = Column(String(100))  # Loan/facility reference
    
    marked_date = Column(Date, nullable=False)
    marked_by = Column(String(50))
    
    release_date = Column(Date)
    release_by = Column(String(50))
    release_reason = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class JointAccountHolder(Base):
    """Joint account holder"""
    __tablename__ = "deposit_joint_holders"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False)
    customer_id = Column(String(50), nullable=False)  # Additional holder
    
    holder_type = Column(String(50), nullable=False)  # primary, joint, either_or_survivor
    operation_mode = Column(String(50))  # single, joint, either_or
    signature_required = Column(Boolean, default=True)
    
    added_date = Column(Date, nullable=False)
    added_by = Column(String(50))
    
    removed_date = Column(Date)
    removed_by = Column(String(50))
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdvancedOperationsService:
    """Service for advanced account operations"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== FREEZE OPERATIONS ====================
    
    def freeze_account(
        self,
        account_id: int,
        freeze_type: str,  # debit, credit, full
        reason: str
    ) -> Dict[str, Any]:
        """Freeze account"""
        account = self._get_account(account_id)
        
        if freeze_type not in ['debit', 'credit', 'full']:
            raise CustomException(
                status_code=400,
                message="Invalid freeze type. Must be: debit, credit, or full"
            )
        
        # Check if already frozen
        existing_freeze = self.db.query(AccountFreeze).filter(
            and_(
                AccountFreeze.deposit_account_id == account_id,
                AccountFreeze.is_active == True
            )
        ).first()
        
        if existing_freeze:
            raise CustomException(
                status_code=400,
                message="Account is already frozen"
            )
        
        # Create freeze record
        freeze = AccountFreeze(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            freeze_type=freeze_type,
            freeze_reason=reason,
            freeze_date=date.today(),
            freeze_by=str(self.user_id),
            is_active=True
        )
        
        self.db.add(freeze)
        self.db.commit()
        
        return {
            "freeze_id": freeze.id,
            "account_number": account.account_number,
            "freeze_type": freeze_type,
            "freeze_date": freeze.freeze_date.isoformat(),
            "reason": reason,
            "status": "frozen"
        }
    
    def unfreeze_account(
        self,
        freeze_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Unfreeze account"""
        freeze = self.db.query(AccountFreeze).filter(
            and_(
                AccountFreeze.id == freeze_id,
                AccountFreeze.tenant_id == self.tenant_id,
                AccountFreeze.is_active == True
            )
        ).first()
        
        if not freeze:
            raise CustomException(status_code=404, message="Freeze record not found")
        
        freeze.unfreeze_date = date.today()
        freeze.unfreeze_by = str(self.user_id)
        freeze.unfreeze_reason = reason
        freeze.is_active = False
        
        self.db.commit()
        
        account = self._get_account(freeze.deposit_account_id)
        
        return {
            "freeze_id": freeze_id,
            "account_number": account.account_number,
            "unfreeze_date": freeze.unfreeze_date.isoformat(),
            "reason": reason,
            "status": "active"
        }
    
    def get_account_freezes(
        self,
        account_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get account freeze history"""
        query = self.db.query(AccountFreeze).filter(
            and_(
                AccountFreeze.deposit_account_id == account_id,
                AccountFreeze.tenant_id == self.tenant_id
            )
        )
        
        if active_only:
            query = query.filter(AccountFreeze.is_active == True)
        
        freezes = query.all()
        
        return [
            {
                "freeze_id": f.id,
                "freeze_type": f.freeze_type,
                "freeze_reason": f.freeze_reason,
                "freeze_date": f.freeze_date.isoformat(),
                "unfreeze_date": f.unfreeze_date.isoformat() if f.unfreeze_date else None,
                "is_active": f.is_active
            }
            for f in freezes
        ]
    
    # ==================== LIEN OPERATIONS ====================
    
    def mark_lien(
        self,
        account_id: int,
        lien_amount: Decimal,
        reason: str,
        reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark lien on account"""
        account = self._get_account(account_id)
        
        # Validate lien amount
        if lien_amount > account.current_balance:
            raise CustomException(
                status_code=400,
                message=f"Lien amount cannot exceed current balance of ₹{account.current_balance:,.2f}"
            )
        
        # Create lien record
        lien = AccountLien(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            lien_amount=lien_amount,
            lien_reason=reason,
            lien_reference=reference,
            marked_date=date.today(),
            marked_by=str(self.user_id),
            is_active=True
        )
        
        self.db.add(lien)
        self.db.commit()
        
        # Calculate available balance
        total_lien = self._get_total_lien_amount(account_id)
        available_balance = account.current_balance - total_lien
        
        return {
            "lien_id": lien.id,
            "account_number": account.account_number,
            "lien_amount": float(lien_amount),
            "total_lien": float(total_lien),
            "current_balance": float(account.current_balance),
            "available_balance": float(available_balance),
            "marked_date": lien.marked_date.isoformat()
        }
    
    def release_lien(
        self,
        lien_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Release lien"""
        lien = self.db.query(AccountLien).filter(
            and_(
                AccountLien.id == lien_id,
                AccountLien.tenant_id == self.tenant_id,
                AccountLien.is_active == True
            )
        ).first()
        
        if not lien:
            raise CustomException(status_code=404, message="Lien record not found")
        
        lien.release_date = date.today()
        lien.release_by = str(self.user_id)
        lien.release_reason = reason
        lien.is_active = False
        
        self.db.commit()
        
        account = self._get_account(lien.deposit_account_id)
        total_lien = self._get_total_lien_amount(lien.deposit_account_id)
        available_balance = account.current_balance - total_lien
        
        return {
            "lien_id": lien_id,
            "account_number": account.account_number,
            "released_amount": float(lien.lien_amount),
            "remaining_lien": float(total_lien),
            "available_balance": float(available_balance),
            "release_date": lien.release_date.isoformat()
        }
    
    def get_account_liens(
        self,
        account_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get account lien details"""
        query = self.db.query(AccountLien).filter(
            and_(
                AccountLien.deposit_account_id == account_id,
                AccountLien.tenant_id == self.tenant_id
            )
        )
        
        if active_only:
            query = query.filter(AccountLien.is_active == True)
        
        liens = query.all()
        
        return [
            {
                "lien_id": l.id,
                "lien_amount": float(l.lien_amount),
                "lien_reason": l.lien_reason,
                "lien_reference": l.lien_reference,
                "marked_date": l.marked_date.isoformat(),
                "release_date": l.release_date.isoformat() if l.release_date else None,
                "is_active": l.is_active
            }
            for l in liens
        ]
    
    def _get_total_lien_amount(self, account_id: int) -> Decimal:
        """Calculate total active lien amount"""
        from sqlalchemy import func
        
        total = self.db.query(func.sum(AccountLien.lien_amount)).filter(
            and_(
                AccountLien.deposit_account_id == account_id,
                AccountLien.is_active == True
            )
        ).scalar()
        
        return total or Decimal('0')
    
    # ==================== ACCOUNT TRANSFER ====================
    
    def transfer_account(
        self,
        account_id: int,
        new_customer_id: str,
        reason: str,
        transfer_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Transfer account to another customer"""
        account = self._get_account(account_id)
        
        if not transfer_date:
            transfer_date = date.today()
        
        # Store old customer
        old_customer_id = account.customer_id
        
        # Update account
        account.customer_id = new_customer_id
        account.updated_by = self.user_id
        
        # Create audit trail (would use a separate transfer_history table in production)
        self.db.commit()
        
        return {
            "account_number": account.account_number,
            "old_customer_id": str(old_customer_id),
            "new_customer_id": new_customer_id,
            "transfer_date": transfer_date.isoformat(),
            "reason": reason,
            "status": "transferred"
        }
    
    # ==================== JOINT ACCOUNT ====================
    
    def add_joint_holder(
        self,
        account_id: int,
        customer_id: str,
        holder_type: str,
        operation_mode: str = 'joint'
    ) -> Dict[str, Any]:
        """Add joint account holder"""
        account = self._get_account(account_id)
        
        # Check if already a holder
        existing = self.db.query(JointAccountHolder).filter(
            and_(
                JointAccountHolder.deposit_account_id == account_id,
                JointAccountHolder.customer_id == customer_id,
                JointAccountHolder.is_active == True
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message="Customer is already a joint holder"
            )
        
        holder = JointAccountHolder(
            tenant_id=self.tenant_id,
            deposit_account_id=account_id,
            customer_id=customer_id,
            holder_type=holder_type,
            operation_mode=operation_mode,
            added_date=date.today(),
            added_by=str(self.user_id),
            is_active=True
        )
        
        self.db.add(holder)
        self.db.commit()
        
        return {
            "holder_id": holder.id,
            "account_number": account.account_number,
            "customer_id": customer_id,
            "holder_type": holder_type,
            "operation_mode": operation_mode,
            "added_date": holder.added_date.isoformat()
        }
    
    def remove_joint_holder(
        self,
        holder_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Remove joint account holder"""
        holder = self.db.query(JointAccountHolder).filter(
            and_(
                JointAccountHolder.id == holder_id,
                JointAccountHolder.tenant_id == self.tenant_id,
                JointAccountHolder.is_active == True
            )
        ).first()
        
        if not holder:
            raise CustomException(status_code=404, message="Joint holder not found")
        
        holder.removed_date = date.today()
        holder.removed_by = str(self.user_id)
        holder.is_active = False
        
        self.db.commit()
        
        return {
            "holder_id": holder_id,
            "customer_id": holder.customer_id,
            "removed_date": holder.removed_date.isoformat(),
            "status": "removed"
        }
    
    def get_joint_holders(
        self,
        account_id: int
    ) -> List[Dict[str, Any]]:
        """Get all joint holders for account"""
        holders = self.db.query(JointAccountHolder).filter(
            and_(
                JointAccountHolder.deposit_account_id == account_id,
                JointAccountHolder.tenant_id == self.tenant_id,
                JointAccountHolder.is_active == True
            )
        ).all()
        
        return [
            {
                "holder_id": h.id,
                "customer_id": h.customer_id,
                "holder_type": h.holder_type,
                "operation_mode": h.operation_mode,
                "added_date": h.added_date.isoformat()
            }
            for h in holders
        ]
    
    # ==================== HELPER METHODS ====================
    
    def _get_account(self, account_id: int) -> DepositAccount:
        """Get and verify account"""
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
    
    def check_transaction_allowed(
        self,
        account_id: int,
        transaction_type: str  # debit or credit
    ) -> Dict[str, Any]:
        """Check if transaction is allowed (considering freeze/lien)"""
        account = self._get_account(account_id)
        
        # Check for active freeze
        freeze = self.db.query(AccountFreeze).filter(
            and_(
                AccountFreeze.deposit_account_id == account_id,
                AccountFreeze.is_active == True
            )
        ).first()
        
        if freeze:
            if freeze.freeze_type == 'full':
                return {
                    "allowed": False,
                    "reason": f"Account is fully frozen: {freeze.freeze_reason}"
                }
            elif freeze.freeze_type == 'debit' and transaction_type == 'debit':
                return {
                    "allowed": False,
                    "reason": f"Debit transactions frozen: {freeze.freeze_reason}"
                }
            elif freeze.freeze_type == 'credit' and transaction_type == 'credit':
                return {
                    "allowed": False,
                    "reason": f"Credit transactions frozen: {freeze.freeze_reason}"
                }
        
        # Check lien for debits
        if transaction_type == 'debit':
            total_lien = self._get_total_lien_amount(account_id)
            available_balance = account.current_balance - total_lien
            
            return {
                "allowed": True,
                "available_balance": float(available_balance),
                "lien_amount": float(total_lien)
            }
        
        return {"allowed": True}
