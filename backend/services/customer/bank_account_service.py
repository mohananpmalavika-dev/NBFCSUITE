"""
Customer Bank Account Service
Business logic for customer bank account operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import List, Optional
from datetime import datetime

from backend.shared.database.customer_models import CustomerBankAccount
from .schemas import CustomerBankAccountCreate, CustomerBankAccountUpdate


class CustomerBankAccountService:
    """Service for customer bank account operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_bank_account(self, data: CustomerBankAccountCreate) -> CustomerBankAccount:
        """Add bank account to customer"""
        
        # Check if account already exists
        existing = await self.get_by_account_number(
            data.customer_id, 
            data.account_number
        )
        
        if existing:
            raise ValueError("Account number already exists for this customer")
        
        # If this is primary account, unset other primary accounts
        if data.is_primary:
            await self._unset_primary_accounts(data.customer_id)
        
        # Create account
        account = CustomerBankAccount(
            tenant_id=self.tenant_id,
            customer_id=data.customer_id,
            bank_id=data.bank_id,
            account_number=data.account_number,
            account_holder_name=data.account_holder_name,
            account_type=data.account_type,
            ifsc_code=data.ifsc_code,
            is_primary=data.is_primary,
            use_for_disbursement=data.use_for_disbursement,
            use_for_collection=data.use_for_collection,
            is_verified=False,
            is_active=True,
            created_by=self.user_id
        )
        
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def get_customer_accounts(
        self, 
        customer_id: int,
        is_primary: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> List[CustomerBankAccount]:
        """Get all bank accounts for a customer"""
        
        query = select(CustomerBankAccount).where(
            and_(
                CustomerBankAccount.customer_id == customer_id,
                CustomerBankAccount.tenant_id == self.tenant_id,
                CustomerBankAccount.is_deleted == False
            )
        )
        
        if is_primary is not None:
            query = query.where(CustomerBankAccount.is_primary == is_primary)
        
        if is_active is not None:
            query = query.where(CustomerBankAccount.is_active == is_active)
        
        query = query.order_by(
            CustomerBankAccount.is_primary.desc(),
            CustomerBankAccount.created_at.desc()
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_bank_account(self, account_id: int) -> Optional[CustomerBankAccount]:
        """Get bank account by ID"""
        query = select(CustomerBankAccount).where(
            and_(
                CustomerBankAccount.id == account_id,
                CustomerBankAccount.tenant_id == self.tenant_id,
                CustomerBankAccount.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_account_number(
        self, 
        customer_id: int, 
        account_number: str
    ) -> Optional[CustomerBankAccount]:
        """Check if account exists"""
        query = select(CustomerBankAccount).where(
            and_(
                CustomerBankAccount.customer_id == customer_id,
                CustomerBankAccount.account_number == account_number,
                CustomerBankAccount.tenant_id == self.tenant_id,
                CustomerBankAccount.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_primary_account(self, customer_id: int) -> Optional[CustomerBankAccount]:
        """Get primary bank account for customer"""
        accounts = await self.get_customer_accounts(customer_id, is_primary=True)
        return accounts[0] if accounts else None
    
    async def update_bank_account(
        self, 
        account_id: int, 
        data: CustomerBankAccountUpdate
    ) -> Optional[CustomerBankAccount]:
        """Update bank account details"""
        account = await self.get_bank_account(account_id)
        if not account:
            return None
        
        # If setting as primary, unset other primary accounts
        if data.is_primary and not account.is_primary:
            await self._unset_primary_accounts(account.customer_id)
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(account, field, value)
        
        account.updated_by = self.user_id
        account.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def set_primary_account(
        self, 
        account_id: int
    ) -> Optional[CustomerBankAccount]:
        """Set account as primary"""
        account = await self.get_bank_account(account_id)
        if not account:
            return None
        
        # Unset other primary accounts
        await self._unset_primary_accounts(account.customer_id)
        
        # Set this as primary
        account.is_primary = True
        account.updated_by = self.user_id
        account.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def verify_account(
        self, 
        account_id: int, 
        verification_method: str,
        remarks: Optional[str] = None
    ) -> Optional[CustomerBankAccount]:
        """Verify bank account (e.g., after penny drop)"""
        account = await self.get_bank_account(account_id)
        if not account:
            return None
        
        account.is_verified = True
        account.verification_method = verification_method
        account.verified_date = datetime.utcnow()
        account.verification_remarks = remarks
        account.updated_by = self.user_id
        account.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def penny_drop_verification(
        self, 
        account_id: int, 
        amount: float,
        reference: str,
        status: str
    ) -> Optional[CustomerBankAccount]:
        """Record penny drop verification attempt"""
        account = await self.get_bank_account(account_id)
        if not account:
            return None
        
        account.penny_drop_amount = amount
        account.penny_drop_reference = reference
        account.penny_drop_status = status
        
        if status.lower() == "success":
            account.is_verified = True
            account.verification_method = "Penny Drop"
            account.verified_date = datetime.utcnow()
        
        account.updated_by = self.user_id
        account.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def delete_bank_account(self, account_id: int) -> bool:
        """Soft delete bank account"""
        account = await self.get_bank_account(account_id)
        if not account:
            return False
        
        # Don't allow deleting primary account if there are other accounts
        if account.is_primary:
            other_accounts = await self.get_customer_accounts(
                account.customer_id, 
                is_primary=False
            )
            if other_accounts:
                raise ValueError("Cannot delete primary account. Set another account as primary first.")
        
        account.is_deleted = True
        account.is_active = False
        account.updated_by = self.user_id
        account.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def _unset_primary_accounts(self, customer_id: int):
        """Unset all primary accounts for a customer"""
        await self.db.execute(
            update(CustomerBankAccount)
            .where(
                and_(
                    CustomerBankAccount.customer_id == customer_id,
                    CustomerBankAccount.tenant_id == self.tenant_id,
                    CustomerBankAccount.is_primary == True
                )
            )
            .values(
                is_primary=False,
                updated_by=self.user_id,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
