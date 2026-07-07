"""
Treasury Bank Account Service
Business logic for bank account management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import HTTPException
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
import logging

from backend.shared.database.treasury_models import (
    TreasuryBankAccount,
    BankAccountStatus,
    BankAccountType,
    BankAccountPurpose
)
from backend.shared.database.accounting_models import JournalEntry, JournalEntryLine
from . import bank_account_schemas as schemas

logger = logging.getLogger(__name__)


class BankAccountService:
    """Service for treasury bank account operations"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def create_bank_account(self, data: schemas.TreasuryBankAccountCreate) -> TreasuryBankAccount:
        """Create new treasury bank account"""
        try:
            # Check if account number already exists for tenant
            existing = self.db.query(TreasuryBankAccount).filter(
                TreasuryBankAccount.tenant_id == self.tenant_id,
                TreasuryBankAccount.account_number == data.account_number,
                TreasuryBankAccount.is_deleted == False
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Bank account with number {data.account_number} already exists"
                )
            
            # Create bank account
            db_account = TreasuryBankAccount(
                tenant_id=self.tenant_id,
                created_by=self.user_id,
                current_balance=data.opening_balance,
                available_balance=data.opening_balance,
                last_updated_at=datetime.utcnow(),
                status=BankAccountStatus.ACTIVE,
                **data.model_dump()
            )
            
            self.db.add(db_account)
            self.db.commit()
            self.db.refresh(db_account)
            
            logger.info(f"Created bank account: {db_account.id} - {db_account.account_number}")
            return db_account
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating bank account: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create bank account: {str(e)}")
    
    def get_bank_account(self, account_id: int) -> TreasuryBankAccount:
        """Get bank account by ID"""
        account = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == account_id,
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Bank account not found")
        
        return account
    
    def list_bank_accounts(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[BankAccountStatus] = None,
        account_type: Optional[BankAccountType] = None,
        account_purpose: Optional[BankAccountPurpose] = None,
        branch_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> schemas.TreasuryBankAccountListResponse:
        """List bank accounts with filters and pagination"""
        
        query = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        )
        
        # Apply filters
        if status:
            query = query.filter(TreasuryBankAccount.status == status)
        
        if account_type:
            query = query.filter(TreasuryBankAccount.account_type == account_type)
        
        if account_purpose:
            query = query.filter(TreasuryBankAccount.account_purpose == account_purpose)
        
        if branch_id:
            query = query.filter(TreasuryBankAccount.branch_id == branch_id)
        
        if search:
            search_filter = or_(
                TreasuryBankAccount.account_number.ilike(f"%{search}%"),
                TreasuryBankAccount.account_name.ilike(f"%{search}%"),
                TreasuryBankAccount.bank_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        accounts = query.order_by(TreasuryBankAccount.created_at.desc()).offset(skip).limit(limit).all()
        
        return schemas.TreasuryBankAccountListResponse(
            accounts=accounts,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit if limit > 0 else 1
        )
    
    def update_bank_account(
        self,
        account_id: int,
        data: schemas.TreasuryBankAccountUpdate
    ) -> TreasuryBankAccount:
        """Update bank account details"""
        try:
            account = self.get_bank_account(account_id)
            
            # Update fields
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(account, field, value)
            
            account.updated_by = self.user_id
            account.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(f"Updated bank account: {account_id}")
            return account
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating bank account {account_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update bank account: {str(e)}")
    
    def delete_bank_account(self, account_id: int) -> Dict[str, Any]:
        """Soft delete bank account"""
        try:
            account = self.get_bank_account(account_id)
            
            # Check if account has balance
            if account.current_balance != Decimal("0.00"):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete account with non-zero balance"
                )
            
            # Soft delete
            account.is_deleted = True
            account.status = BankAccountStatus.CLOSED
            account.closing_date = date.today()
            account.updated_by = self.user_id
            account.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Deleted bank account: {account_id}")
            return {"message": "Bank account deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting bank account {account_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete bank account: {str(e)}")
    
    def get_active_accounts(self) -> List[TreasuryBankAccount]:
        """Get all active bank accounts"""
        return self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.status == BankAccountStatus.ACTIVE,
            TreasuryBankAccount.is_deleted == False
        ).all()
    
    def get_account_balance(self, account_id: int) -> schemas.BankAccountBalanceResponse:
        """Get current balance of bank account"""
        account = self.get_bank_account(account_id)
        
        return schemas.BankAccountBalanceResponse(
            account_id=account.id,
            account_number=account.account_number,
            account_name=account.account_name,
            current_balance=account.current_balance,
            available_balance=account.available_balance,
            minimum_balance=account.minimum_balance,
            last_updated_at=account.last_updated_at,
            status=account.status
        )
    
    def update_account_balance(
        self,
        account_id: int,
        data: schemas.BankAccountBalanceUpdate
    ) -> schemas.BankAccountBalanceResponse:
        """Update bank account balance"""
        try:
            account = self.get_bank_account(account_id)
            
            # Update balance
            old_balance = account.current_balance
            account.current_balance = data.new_balance
            account.available_balance = data.new_balance
            account.last_updated_at = datetime.utcnow()
            account.updated_by = self.user_id
            account.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(
                f"Updated balance for account {account_id}: "
                f"{old_balance} -> {data.new_balance}"
            )
            
            return self.get_account_balance(account_id)
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating account balance {account_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update balance: {str(e)}")
    
    def get_accounts_by_branch(self, branch_id: int) -> List[TreasuryBankAccount]:
        """Get all accounts for a specific branch"""
        return self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.branch_id == branch_id,
            TreasuryBankAccount.is_deleted == False
        ).all()
    
    def get_statistics(self) -> schemas.BankAccountStatistics:
        """Get bank account statistics"""
        
        # Total accounts
        total_accounts = self.db.query(func.count(TreasuryBankAccount.id)).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        ).scalar()
        
        # Active accounts
        active_accounts = self.db.query(func.count(TreasuryBankAccount.id)).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.status == BankAccountStatus.ACTIVE,
            TreasuryBankAccount.is_deleted == False
        ).scalar()
        
        # Inactive accounts
        inactive_accounts = total_accounts - active_accounts
        
        # Total balance across all accounts
        total_balance = self.db.query(func.sum(TreasuryBankAccount.current_balance)).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.status == BankAccountStatus.ACTIVE,
            TreasuryBankAccount.is_deleted == False
        ).scalar() or Decimal("0.00")
        
        # Accounts below minimum balance
        accounts_below_minimum = self.db.query(func.count(TreasuryBankAccount.id)).filter(
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.status == BankAccountStatus.ACTIVE,
            TreasuryBankAccount.current_balance < TreasuryBankAccount.minimum_balance,
            TreasuryBankAccount.is_deleted == False
        ).scalar()
        
        # Accounts by type
        accounts_by_type = {}
        for account_type in BankAccountType:
            count = self.db.query(func.count(TreasuryBankAccount.id)).filter(
                TreasuryBankAccount.tenant_id == self.tenant_id,
                TreasuryBankAccount.account_type == account_type,
                TreasuryBankAccount.is_deleted == False
            ).scalar()
            accounts_by_type[account_type.value] = count
        
        # Accounts by purpose
        accounts_by_purpose = {}
        for purpose in BankAccountPurpose:
            count = self.db.query(func.count(TreasuryBankAccount.id)).filter(
                TreasuryBankAccount.tenant_id == self.tenant_id,
                TreasuryBankAccount.account_purpose == purpose,
                TreasuryBankAccount.is_deleted == False
            ).scalar()
            accounts_by_purpose[purpose.value] = count
        
        return schemas.BankAccountStatistics(
            total_accounts=total_accounts,
            active_accounts=active_accounts,
            inactive_accounts=inactive_accounts,
            total_balance=total_balance,
            accounts_below_minimum=accounts_below_minimum,
            accounts_by_type=accounts_by_type,
            accounts_by_purpose=accounts_by_purpose
        )
    
    def bulk_create_accounts(
        self,
        data: schemas.BankAccountBulkCreate
    ) -> schemas.BankAccountBulkCreateResponse:
        """Bulk create bank accounts"""
        created_accounts = []
        errors = []
        
        for account_data in data.accounts:
            try:
                account = self.create_bank_account(account_data)
                created_accounts.append(account)
            except Exception as e:
                errors.append({
                    "account_number": account_data.account_number,
                    "error": str(e)
                })
        
        return schemas.BankAccountBulkCreateResponse(
            created_count=len(created_accounts),
            failed_count=len(errors),
            created_accounts=created_accounts,
            errors=errors
        )
    
    def get_account_history(
        self,
        account_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get account balance history (from cash positions or transactions)"""
        account = self.get_bank_account(account_id)
        
        # This would query cash_positions table for historical data
        # For now, return current balance only
        history = [{
            "date": date.today(),
            "balance": account.current_balance,
            "available_balance": account.available_balance
        }]
        
        return history
