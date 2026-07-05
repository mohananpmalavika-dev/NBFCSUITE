"""
Accounting Service
Core business logic for accounting operations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.shared.database.accounting_models import (
    ChartOfAccounts,
    JournalEntry,
    JournalEntryLine,
    GeneralLedger,
    TrialBalance,
    AccountingPeriod,
    AccountType,
    AccountSubType,
    JournalEntryStatus,
    JournalEntryType
)


class AccountingService:
    """Service for managing accounting operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # Chart of Accounts Management
    # ========================================================================
    
    async def create_account(
        self,
        account_code: str,
        account_name: str,
        account_type: AccountType,
        account_sub_type: AccountSubType,
        parent_account_id: Optional[int] = None,
        level: int = 1,
        is_group: bool = False,
        allow_manual_entry: bool = True,
        opening_balance: Decimal = Decimal("0.00"),
        description: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ChartOfAccounts:
        """Create new account in chart of accounts"""
        
        # Check if account code already exists
        existing_query = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.account_code == account_code,
                ChartOfAccounts.is_deleted == False
            )
        )
        result = await self.db.execute(existing_query)
        if result.scalar_one_or_none():
            raise ValueError(f"Account code {account_code} already exists")
        
        # Validate parent account if provided
        if parent_account_id:
            parent_query = select(ChartOfAccounts).where(
                and_(
                    ChartOfAccounts.id == parent_account_id,
                    ChartOfAccounts.tenant_id == self.tenant_id
                )
            )
            parent_result = await self.db.execute(parent_query)
            parent = parent_result.scalar_one_or_none()
            if not parent:
                raise ValueError("Parent account not found")
            if not parent.is_group:
                raise ValueError("Parent account must be a group account")
        
        # Create account
        account = ChartOfAccounts(
            tenant_id=self.tenant_id,
            account_code=account_code,
            account_name=account_name,
            account_type=account_type,
            account_sub_type=account_sub_type,
            parent_account_id=parent_account_id,
            level=level,
            is_group=is_group,
            allow_manual_entry=allow_manual_entry,
            opening_balance=opening_balance,
            current_balance=opening_balance,
            description=description,
            notes=notes,
            created_by=self.user_id
        )
        
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def get_account(
        self,
        account_id: Optional[int] = None,
        account_code: Optional[str] = None
    ) -> Optional[ChartOfAccounts]:
        """Get account by ID or code"""
        conditions = [
            ChartOfAccounts.tenant_id == self.tenant_id,
            ChartOfAccounts.is_deleted == False
        ]
        
        if account_id:
            conditions.append(ChartOfAccounts.id == account_id)
        if account_code:
            conditions.append(ChartOfAccounts.account_code == account_code)
        
        query = select(ChartOfAccounts).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_accounts(
        self,
        account_type: Optional[AccountType] = None,
        is_active: bool = True,
        is_group: Optional[bool] = None,
        parent_account_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ChartOfAccounts], int]:
        """List accounts with filters"""
        conditions = [
            ChartOfAccounts.tenant_id == self.tenant_id,
            ChartOfAccounts.is_deleted == False
        ]
        
        if account_type:
            conditions.append(ChartOfAccounts.account_type == account_type)
        if is_active is not None:
            conditions.append(ChartOfAccounts.is_active == is_active)
        if is_group is not None:
            conditions.append(ChartOfAccounts.is_group == is_group)
        if parent_account_id is not None:
            conditions.append(ChartOfAccounts.parent_account_id == parent_account_id)
        
        # Count total
        count_query = select(func.count(ChartOfAccounts.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get accounts
        query = select(ChartOfAccounts).where(and_(*conditions)).order_by(
            ChartOfAccounts.account_code
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        return accounts, total
    
    async def update_account(
        self,
        account_id: int,
        **kwargs
    ) -> Optional[ChartOfAccounts]:
        """Update account"""
        account = await self.get_account(account_id=account_id)
        if not account:
            raise ValueError("Account not found")
        
        if account.is_system:
            raise ValueError("Cannot update system account")
        
        # Update allowed fields
        allowed_fields = [
            "account_name", "account_sub_type", "allow_manual_entry",
            "is_active", "description", "notes"
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(account, field, value)
        
        account.updated_at = datetime.utcnow()
        account.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(account)
        
        return account
    
    async def get_account_hierarchy(self) -> List[Dict[str, Any]]:
        """Get account hierarchy tree"""
        query = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.is_deleted == False,
                ChartOfAccounts.is_active == True
            )
        ).order_by(ChartOfAccounts.account_code)
        
        result = await self.db.execute(query)
        all_accounts = result.scalars().all()
        
        # Build hierarchy
        account_map = {acc.id: acc for acc in all_accounts}
        root_accounts = [acc for acc in all_accounts if acc.parent_account_id is None]
        
        def build_tree(account):
            children = [
                build_tree(child) for child in all_accounts
                if child.parent_account_id == account.id
            ]
            return {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "is_group": account.is_group,
                "level": account.level,
                "current_balance": float(account.current_balance),
                "children": children
            }
        
        return [build_tree(acc) for acc in root_accounts]
    
    # ========================================================================
    # Journal Entry Management
    # ========================================================================
    
    async def generate_entry_number(self) -> str:
        """Generate unique journal entry number: JE-YYYYMM-XXXX"""
        now = datetime.now()
        prefix = f"JE-{now.year}{now.month:02d}"
        
        query = select(JournalEntry).where(
            and_(
                JournalEntry.tenant_id == self.tenant_id,
                JournalEntry.entry_number.like(f"{prefix}-%")
            )
        ).order_by(desc(JournalEntry.entry_number)).limit(1)
        
        result = await self.db.execute(query)
        last_entry = result.scalar_one_or_none()
        
        if last_entry:
            last_number = int(last_entry.entry_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    async def create_journal_entry(
        self,
        entry_date: date,
        narration: str,
        line_items: List[Dict[str, Any]],
        entry_type: JournalEntryType = JournalEntryType.MANUAL,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        reference_number: Optional[str] = None,
        internal_notes: Optional[str] = None,
        auto_post: bool = False
    ) -> JournalEntry:
        """Create new journal entry"""
        
        # Validate line items
        if len(line_items) < 2:
            raise ValueError("At least 2 line items required")
        
        # Calculate totals
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        
        for item in line_items:
            total_debit += item.get("debit_amount", Decimal("0.00"))
            total_credit += item.get("credit_amount", Decimal("0.00"))
        
        # Validate balanced entry
        if abs(total_debit - total_credit) > Decimal("0.01"):
            raise ValueError(f"Debits ({total_debit}) must equal credits ({total_credit})")
        
        # Generate entry number
        entry_number = await self.generate_entry_number()
        
        # Create journal entry
        journal_entry = JournalEntry(
            tenant_id=self.tenant_id,
            entry_number=entry_number,
            entry_date=entry_date,
            entry_type=entry_type,
            status=JournalEntryStatus.DRAFT,
            narration=narration,
            internal_notes=internal_notes,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            total_debit=total_debit,
            total_credit=total_credit,
            created_by=self.user_id
        )
        
        self.db.add(journal_entry)
        await self.db.flush()
        
        # Create line items
        for idx, item in enumerate(line_items, 1):
            account = await self.get_account(account_id=item["account_id"])
            if not account:
                raise ValueError(f"Account {item['account_id']} not found")
            
            if not account.allow_manual_entry and entry_type == JournalEntryType.MANUAL:
                raise ValueError(f"Manual entries not allowed for account {account.account_code}")
            
            line = JournalEntryLine(
                tenant_id=self.tenant_id,
                journal_entry_id=journal_entry.id,
                line_number=idx,
                account_id=account.id,
                account_code=account.account_code,
                debit_amount=item.get("debit_amount", Decimal("0.00")),
                credit_amount=item.get("credit_amount", Decimal("0.00")),
                description=item.get("description"),
                cost_center=item.get("cost_center"),
                department=item.get("department"),
                transaction_type=reference_type,
                transaction_id=reference_id
            )
            self.db.add(line)
        
        await self.db.commit()
        await self.db.refresh(journal_entry)
        
        # Auto-post if requested
        if auto_post:
            await self.post_journal_entry(journal_entry.id, entry_date)
        
        return journal_entry
    
    async def get_journal_entry(
        self,
        entry_id: Optional[int] = None,
        entry_number: Optional[str] = None
    ) -> Optional[JournalEntry]:
        """Get journal entry with line items"""
        conditions = [
            JournalEntry.tenant_id == self.tenant_id,
            JournalEntry.is_deleted == False
        ]
        
        if entry_id:
            conditions.append(JournalEntry.id == entry_id)
        if entry_number:
            conditions.append(JournalEntry.entry_number == entry_number)
        
        query = select(JournalEntry).options(
            joinedload(JournalEntry.line_items)
        ).where(and_(*conditions))
        
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def post_journal_entry(
        self,
        entry_id: int,
        posting_date: Optional[date] = None
    ) -> JournalEntry:
        """Post journal entry to general ledger"""
        entry = await self.get_journal_entry(entry_id=entry_id)
        if not entry:
            raise ValueError("Journal entry not found")
        
        if entry.status != JournalEntryStatus.DRAFT:
            raise ValueError(f"Cannot post entry with status {entry.status}")
        
        posting_date = posting_date or entry.entry_date
        
        # Determine financial period
        financial_year = posting_date.year
        financial_period = f"{posting_date.year}{posting_date.month:02d}"
        
        # Post each line to general ledger
        for line in entry.line_items:
            # Get current balance
            account = await self.get_account(account_id=line.account_id)
            
            # Calculate new balance based on account type
            if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                # Debit increases, credit decreases
                balance_change = line.debit_amount - line.credit_amount
            else:
                # Credit increases, debit decreases (LIABILITY, EQUITY, INCOME)
                balance_change = line.credit_amount - line.debit_amount
            
            new_balance = account.current_balance + balance_change
            
            # Create GL entry
            gl_entry = GeneralLedger(
                tenant_id=self.tenant_id,
                account_id=line.account_id,
                account_code=line.account_code,
                transaction_date=entry.entry_date,
                posting_date=posting_date,
                journal_entry_id=entry.id,
                journal_entry_number=entry.entry_number,
                line_item_id=line.id,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
                balance=new_balance,
                description=line.description,
                narration=entry.narration,
                reference_type=entry.reference_type,
                reference_id=entry.reference_id,
                reference_number=entry.reference_number,
                financial_year=financial_year,
                financial_period=financial_period,
                cost_center=line.cost_center,
                department=line.department,
                created_by=self.user_id
            )
            self.db.add(gl_entry)
            
            # Update account balances
            account.current_balance = new_balance
            account.debit_balance += line.debit_amount
            account.credit_balance += line.credit_amount
        
        # Update journal entry status
        entry.status = JournalEntryStatus.POSTED
        entry.posting_date = posting_date
        entry.updated_at = datetime.utcnow()
        entry.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(entry)
        
        return entry
    
    async def reverse_journal_entry(
        self,
        entry_id: int,
        reversal_date: date,
        narration: str
    ) -> JournalEntry:
        """Reverse a posted journal entry"""
        original_entry = await self.get_journal_entry(entry_id=entry_id)
        if not original_entry:
            raise ValueError("Journal entry not found")
        
        if original_entry.status != JournalEntryStatus.POSTED:
            raise ValueError("Can only reverse posted entries")
        
        if original_entry.is_reversal:
            raise ValueError("Cannot reverse a reversal entry")
        
        # Create reversal entry (swap debits and credits)
        reversal_lines = []
        for line in original_entry.line_items:
            reversal_lines.append({
                "account_id": line.account_id,
                "debit_amount": line.credit_amount,  # Swap
                "credit_amount": line.debit_amount,  # Swap
                "description": f"Reversal of {original_entry.entry_number}",
                "cost_center": line.cost_center,
                "department": line.department
            })
        
        reversal_entry = await self.create_journal_entry(
            entry_date=reversal_date,
            narration=f"Reversal: {narration}",
            line_items=reversal_lines,
            entry_type=JournalEntryType.REVERSAL,
            reference_type=original_entry.reference_type,
            reference_id=original_entry.reference_id,
            reference_number=original_entry.reference_number,
            auto_post=True
        )
        
        # Mark as reversal
        reversal_entry.is_reversal = True
        reversal_entry.reversed_entry_id = original_entry.id
        
        # Mark original as reversed
        original_entry.status = JournalEntryStatus.REVERSED
        original_entry.reversal_date = reversal_date
        
        await self.db.commit()
        await self.db.refresh(reversal_entry)
        
        return reversal_entry
    
    async def list_journal_entries(
        self,
        status: Optional[JournalEntryStatus] = None,
        entry_type: Optional[JournalEntryType] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        reference_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[JournalEntry], int]:
        """List journal entries with filters"""
        conditions = [
            JournalEntry.tenant_id == self.tenant_id,
            JournalEntry.is_deleted == False
        ]
        
        if status:
            conditions.append(JournalEntry.status == status)
        if entry_type:
            conditions.append(JournalEntry.entry_type == entry_type)
        if from_date:
            conditions.append(JournalEntry.entry_date >= from_date)
        if to_date:
            conditions.append(JournalEntry.entry_date <= to_date)
        if reference_type:
            conditions.append(JournalEntry.reference_type == reference_type)
        
        # Count total
        count_query = select(func.count(JournalEntry.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get entries
        query = select(JournalEntry).options(
            joinedload(JournalEntry.line_items)
        ).where(and_(*conditions)).order_by(
            desc(JournalEntry.entry_date),
            desc(JournalEntry.entry_number)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        entries = result.unique().scalars().all()
        
        return entries, total
    
    # ========================================================================
    # General Ledger Operations
    # ========================================================================
    
    async def get_general_ledger_entries(
        self,
        account_id: Optional[int] = None,
        account_code: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        financial_year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[GeneralLedger], int]:
        """Get general ledger entries"""
        conditions = [GeneralLedger.tenant_id == self.tenant_id]
        
        if account_id:
            conditions.append(GeneralLedger.account_id == account_id)
        if account_code:
            conditions.append(GeneralLedger.account_code == account_code)
        if from_date:
            conditions.append(GeneralLedger.transaction_date >= from_date)
        if to_date:
            conditions.append(GeneralLedger.transaction_date <= to_date)
        if financial_year:
            conditions.append(GeneralLedger.financial_year == financial_year)
        
        # Count total
        count_query = select(func.count(GeneralLedger.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get entries
        query = select(GeneralLedger).where(and_(*conditions)).order_by(
            GeneralLedger.transaction_date,
            GeneralLedger.id
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        entries = result.scalars().all()
        
        return entries, total
    
    async def get_account_statement(
        self,
        account_id: int,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """Generate account statement"""
        account = await self.get_account(account_id=account_id)
        if not account:
            raise ValueError("Account not found")
        
        # Get opening balance
        opening_query = select(func.sum(GeneralLedger.debit_amount - GeneralLedger.credit_amount)).where(
            and_(
                GeneralLedger.account_id == account_id,
                GeneralLedger.tenant_id == self.tenant_id,
                GeneralLedger.transaction_date < from_date
            )
        )
        opening_result = await self.db.execute(opening_query)
        opening_balance = opening_result.scalar() or Decimal("0.00")
        
        # Get entries for period
        entries, _ = await self.get_general_ledger_entries(
            account_id=account_id,
            from_date=from_date,
            to_date=to_date,
            limit=10000
        )
        
        # Calculate totals
        total_debit = sum(e.debit_amount for e in entries)
        total_credit = sum(e.credit_amount for e in entries)
        
        closing_balance = opening_balance + total_debit - total_credit
        
        return {
            "account_id": account.id,
            "account_code": account.account_code,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "from_date": from_date,
            "to_date": to_date,
            "opening_balance": float(opening_balance),
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "closing_balance": float(closing_balance),
            "entries": entries
        }
    
    # ========================================================================
    # Trial Balance
    # ========================================================================
    
    async def generate_trial_balance(
        self,
        balance_date: date,
        account_type: Optional[AccountType] = None
    ) -> Dict[str, Any]:
        """Generate trial balance"""
        
        # Get all active accounts
        conditions = [
            ChartOfAccounts.tenant_id == self.tenant_id,
            ChartOfAccounts.is_deleted == False,
            ChartOfAccounts.is_active == True,
            ChartOfAccounts.is_group == False  # Only leaf accounts
        ]
        
        if account_type:
            conditions.append(ChartOfAccounts.account_type == account_type)
        
        accounts_query = select(ChartOfAccounts).where(and_(*conditions)).order_by(
            ChartOfAccounts.account_code
        )
        accounts_result = await self.db.execute(accounts_query)
        accounts = accounts_result.scalars().all()
        
        trial_balance_entries = []
        total_debit_balance = Decimal("0.00")
        total_credit_balance = Decimal("0.00")
        
        for account in accounts:
            # Get GL entries up to balance date
            gl_query = select(
                func.sum(GeneralLedger.debit_amount).label("total_debit"),
                func.sum(GeneralLedger.credit_amount).label("total_credit")
            ).where(
                and_(
                    GeneralLedger.account_id == account.id,
                    GeneralLedger.tenant_id == self.tenant_id,
                    GeneralLedger.transaction_date <= balance_date
                )
            )
            gl_result = await self.db.execute(gl_query)
            gl_data = gl_result.first()
            
            total_debit = gl_data.total_debit or Decimal("0.00")
            total_credit = gl_data.total_credit or Decimal("0.00")
            
            # Calculate balance based on account type
            if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                # Normal debit balance
                closing_balance = account.opening_balance + total_debit - total_credit
                debit_balance = closing_balance if closing_balance > 0 else Decimal("0.00")
                credit_balance = abs(closing_balance) if closing_balance < 0 else Decimal("0.00")
            else:
                # Normal credit balance (LIABILITY, EQUITY, INCOME)
                closing_balance = account.opening_balance + total_credit - total_debit
                credit_balance = closing_balance if closing_balance > 0 else Decimal("0.00")
                debit_balance = abs(closing_balance) if closing_balance < 0 else Decimal("0.00")
            
            trial_balance_entries.append({
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "opening_balance": float(account.opening_balance),
                "total_debit": float(total_debit),
                "total_credit": float(total_credit),
                "closing_balance": float(closing_balance),
                "debit_balance": float(debit_balance),
                "credit_balance": float(credit_balance)
            })
            
            total_debit_balance += debit_balance
            total_credit_balance += credit_balance
        
        is_balanced = abs(total_debit_balance - total_credit_balance) < Decimal("0.01")
        
        return {
            "balance_date": balance_date,
            "financial_year": balance_date.year,
            "financial_period": f"{balance_date.year}{balance_date.month:02d}",
            "entries": trial_balance_entries,
            "summary": {
                "total_debit_balance": float(total_debit_balance),
                "total_credit_balance": float(total_credit_balance),
                "difference": float(total_debit_balance - total_credit_balance)
            },
            "is_balanced": is_balanced
        }
    
    # ========================================================================
    # Financial Statements
    # ========================================================================
    
    async def generate_profit_loss(
        self,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """Generate Profit & Loss statement"""
        
        # Get income accounts
        income_query = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.account_type == AccountType.INCOME,
                ChartOfAccounts.is_deleted == False,
                ChartOfAccounts.is_group == False
            )
        )
        income_result = await self.db.execute(income_query)
        income_accounts = income_result.scalars().all()
        
        # Get expense accounts
        expense_query = select(ChartOfAccounts).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.account_type == AccountType.EXPENSE,
                ChartOfAccounts.is_deleted == False,
                ChartOfAccounts.is_group == False
            )
        )
        expense_result = await self.db.execute(expense_query)
        expense_accounts = expense_result.scalars().all()
        
        income_items = []
        total_income = Decimal("0.00")
        
        for account in income_accounts:
            # Get credit minus debit (income is credit)
            gl_query = select(
                func.sum(GeneralLedger.credit_amount - GeneralLedger.debit_amount)
            ).where(
                and_(
                    GeneralLedger.account_id == account.id,
                    GeneralLedger.tenant_id == self.tenant_id,
                    GeneralLedger.transaction_date >= from_date,
                    GeneralLedger.transaction_date <= to_date
                )
            )
            gl_result = await self.db.execute(gl_query)
            amount = gl_result.scalar() or Decimal("0.00")
            
            if amount != 0:
                income_items.append({
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "amount": float(amount)
                })
                total_income += amount
        
        expense_items = []
        total_expenses = Decimal("0.00")
        
        for account in expense_accounts:
            # Get debit minus credit (expense is debit)
            gl_query = select(
                func.sum(GeneralLedger.debit_amount - GeneralLedger.credit_amount)
            ).where(
                and_(
                    GeneralLedger.account_id == account.id,
                    GeneralLedger.tenant_id == self.tenant_id,
                    GeneralLedger.transaction_date >= from_date,
                    GeneralLedger.transaction_date <= to_date
                )
            )
            gl_result = await self.db.execute(gl_query)
            amount = gl_result.scalar() or Decimal("0.00")
            
            if amount != 0:
                expense_items.append({
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "amount": float(amount)
                })
                total_expenses += amount
        
        net_profit = total_income - total_expenses
        profit_margin = (net_profit / total_income * 100) if total_income > 0 else Decimal("0.00")
        
        return {
            "from_date": from_date,
            "to_date": to_date,
            "income": income_items,
            "expenses": expense_items,
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "gross_profit": float(total_income - total_expenses),
            "operating_profit": float(total_income - total_expenses),
            "net_profit": float(net_profit),
            "profit_margin": float(profit_margin)
        }
    
    async def generate_balance_sheet(
        self,
        as_of_date: date
    ) -> Dict[str, Any]:
        """Generate Balance Sheet"""
        
        result = {
            "as_of_date": as_of_date,
            "assets": [],
            "liabilities": [],
            "equity": [],
            "total_assets": Decimal("0.00"),
            "total_liabilities": Decimal("0.00"),
            "total_equity": Decimal("0.00")
        }
        
        # Get accounts for each category
        for account_type in [AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY]:
            accounts_query = select(ChartOfAccounts).where(
                and_(
                    ChartOfAccounts.tenant_id == self.tenant_id,
                    ChartOfAccounts.account_type == account_type,
                    ChartOfAccounts.is_deleted == False,
                    ChartOfAccounts.is_group == False
                )
            )
            accounts_result = await self.db.execute(accounts_query)
            accounts = accounts_result.scalars().all()
            
            for account in accounts:
                # Calculate balance up to date
                gl_query = select(
                    func.sum(GeneralLedger.debit_amount).label("total_debit"),
                    func.sum(GeneralLedger.credit_amount).label("total_credit")
                ).where(
                    and_(
                        GeneralLedger.account_id == account.id,
                        GeneralLedger.tenant_id == self.tenant_id,
                        GeneralLedger.transaction_date <= as_of_date
                    )
                )
                gl_result = await self.db.execute(gl_query)
                gl_data = gl_result.first()
                
                total_debit = gl_data.total_debit or Decimal("0.00")
                total_credit = gl_data.total_credit or Decimal("0.00")
                
                if account_type == AccountType.ASSET:
                    balance = account.opening_balance + total_debit - total_credit
                else:
                    balance = account.opening_balance + total_credit - total_debit
                
                if balance != 0:
                    item = {
                        "account_code": account.account_code,
                        "account_name": account.account_name,
                        "amount": float(abs(balance))
                    }
                    
                    if account_type == AccountType.ASSET:
                        result["assets"].append(item)
                        result["total_assets"] += balance
                    elif account_type == AccountType.LIABILITY:
                        result["liabilities"].append(item)
                        result["total_liabilities"] += balance
                    else:  # EQUITY
                        result["equity"].append(item)
                        result["total_equity"] += balance
        
        # Convert decimals to float
        result["total_assets"] = float(result["total_assets"])
        result["total_liabilities"] = float(result["total_liabilities"])
        result["total_equity"] = float(result["total_equity"])
        result["is_balanced"] = abs(
            result["total_assets"] - (result["total_liabilities"] + result["total_equity"])
        ) < 0.01
        
        return result
    
    # ========================================================================
    # Event-driven Accounting Integration
    # ========================================================================
    
    async def record_loan_disbursement(
        self,
        loan_account_id: int,
        disbursement_amount: Decimal,
        disbursement_date: date,
        processing_fee: Decimal = Decimal("0.00"),
        documentation_charges: Decimal = Decimal("0.00"),
        insurance_premium: Decimal = Decimal("0.00"),
        net_disbursement: Decimal = None
    ) -> JournalEntry:
        """Record loan disbursement accounting entry"""
        
        if net_disbursement is None:
            net_disbursement = disbursement_amount - processing_fee - documentation_charges - insurance_premium
        
        line_items = [
            # Debit: Loan Asset (disbursement amount)
            {
                "account_id": await self._get_system_account("LOAN_ASSET"),
                "debit_amount": disbursement_amount,
                "credit_amount": Decimal("0.00"),
                "description": f"Loan disbursement - Account #{loan_account_id}"
            },
            # Credit: Cash/Bank (net disbursement)
            {
                "account_id": await self._get_system_account("CASH_BANK"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": net_disbursement,
                "description": f"Net disbursement to customer"
            }
        ]
        
        # Add fee income if any
        if processing_fee > 0:
            line_items.append({
                "account_id": await self._get_system_account("FEE_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": processing_fee,
                "description": "Processing fee income"
            })
        
        if documentation_charges > 0:
            line_items.append({
                "account_id": await self._get_system_account("FEE_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": documentation_charges,
                "description": "Documentation charges"
            })
        
        if insurance_premium > 0:
            line_items.append({
                "account_id": await self._get_system_account("FEE_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": insurance_premium,
                "description": "Insurance premium"
            })
        
        return await self.create_journal_entry(
            entry_date=disbursement_date,
            narration=f"Loan disbursement - Loan Account #{loan_account_id}",
            line_items=line_items,
            entry_type=JournalEntryType.LOAN_DISBURSEMENT,
            reference_type="loan_account",
            reference_id=loan_account_id,
            auto_post=True
        )
    
    async def record_loan_repayment(
        self,
        loan_account_id: int,
        repayment_id: int,
        payment_date: date,
        principal_amount: Decimal,
        interest_amount: Decimal,
        penal_interest: Decimal = Decimal("0.00"),
        charges: Decimal = Decimal("0.00"),
        total_amount: Decimal = None
    ) -> JournalEntry:
        """Record loan repayment accounting entry"""
        
        if total_amount is None:
            total_amount = principal_amount + interest_amount + penal_interest + charges
        
        line_items = [
            # Debit: Cash/Bank (total payment received)
            {
                "account_id": await self._get_system_account("CASH_BANK"),
                "debit_amount": total_amount,
                "credit_amount": Decimal("0.00"),
                "description": f"Loan repayment received - Loan #{loan_account_id}"
            }
        ]
        
        # Credit: Loan Asset (principal recovered)
        if principal_amount > 0:
            line_items.append({
                "account_id": await self._get_system_account("LOAN_ASSET"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": principal_amount,
                "description": "Principal repayment"
            })
        
        # Credit: Interest Income
        if interest_amount > 0:
            line_items.append({
                "account_id": await self._get_system_account("INTEREST_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": interest_amount,
                "description": "Interest income"
            })
        
        # Credit: Penal Interest Income
        if penal_interest > 0:
            line_items.append({
                "account_id": await self._get_system_account("INTEREST_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": penal_interest,
                "description": "Penal interest income"
            })
        
        # Credit: Other Income (charges)
        if charges > 0:
            line_items.append({
                "account_id": await self._get_system_account("FEE_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": charges,
                "description": "Charges and fees"
            })
        
        return await self.create_journal_entry(
            entry_date=payment_date,
            narration=f"Loan repayment - Loan Account #{loan_account_id}",
            line_items=line_items,
            entry_type=JournalEntryType.LOAN_REPAYMENT,
            reference_type="loan_repayment",
            reference_id=repayment_id,
            auto_post=True
        )
    
    async def record_interest_accrual(
        self,
        loan_account_id: int,
        accrual_date: date,
        interest_amount: Decimal
    ) -> JournalEntry:
        """Record interest accrual (for accrual accounting)"""
        
        line_items = [
            # Debit: Interest Receivable
            {
                "account_id": await self._get_system_account("INTEREST_RECEIVABLE"),
                "debit_amount": interest_amount,
                "credit_amount": Decimal("0.00"),
                "description": f"Interest accrued - Loan #{loan_account_id}"
            },
            # Credit: Interest Income
            {
                "account_id": await self._get_system_account("INTEREST_INCOME"),
                "debit_amount": Decimal("0.00"),
                "credit_amount": interest_amount,
                "description": "Interest income accrued"
            }
        ]
        
        return await self.create_journal_entry(
            entry_date=accrual_date,
            narration=f"Interest accrual - Loan Account #{loan_account_id}",
            line_items=line_items,
            entry_type=JournalEntryType.INTEREST_ACCRUAL,
            reference_type="loan_account",
            reference_id=loan_account_id,
            auto_post=True
        )
    
    async def _get_system_account(self, account_key: str) -> int:
        """Get system account ID by key (helper method)"""
        # Map of system account keys to codes
        account_map = {
            "CASH_BANK": "1001",
            "LOAN_ASSET": "1100",
            "INTEREST_RECEIVABLE": "1105",
            "INTEREST_INCOME": "4001",
            "FEE_INCOME": "4010"
        }
        
        account_code = account_map.get(account_key)
        if not account_code:
            raise ValueError(f"Unknown system account: {account_key}")
        
        account = await self.get_account(account_code=account_code)
        if not account:
            raise ValueError(f"System account not found: {account_code}")
        
        return account.id
    
    # ========================================================================
    # Statistics and Dashboard
    # ========================================================================
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get accounting module statistics"""
        
        # Count accounts
        accounts_query = select(func.count(ChartOfAccounts.id)).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.is_deleted == False
            )
        )
        accounts_result = await self.db.execute(accounts_query)
        total_accounts = accounts_result.scalar()
        
        active_accounts_query = select(func.count(ChartOfAccounts.id)).where(
            and_(
                ChartOfAccounts.tenant_id == self.tenant_id,
                ChartOfAccounts.is_deleted == False,
                ChartOfAccounts.is_active == True
            )
        )
        active_accounts_result = await self.db.execute(active_accounts_query)
        active_accounts = active_accounts_result.scalar()
        
        # Count journal entries
        entries_query = select(func.count(JournalEntry.id)).where(
            and_(
                JournalEntry.tenant_id == self.tenant_id,
                JournalEntry.is_deleted == False
            )
        )
        entries_result = await self.db.execute(entries_query)
        total_entries = entries_result.scalar()
        
        posted_entries_query = select(func.count(JournalEntry.id)).where(
            and_(
                JournalEntry.tenant_id == self.tenant_id,
                JournalEntry.is_deleted == False,
                JournalEntry.status == JournalEntryStatus.POSTED
            )
        )
        posted_result = await self.db.execute(posted_entries_query)
        posted_entries = posted_result.scalar()
        
        draft_entries = total_entries - posted_entries
        
        # Get account type totals
        totals = {}
        for account_type in AccountType:
            type_query = select(
                func.sum(ChartOfAccounts.current_balance)
            ).where(
                and_(
                    ChartOfAccounts.tenant_id == self.tenant_id,
                    ChartOfAccounts.account_type == account_type,
                    ChartOfAccounts.is_deleted == False
                )
            )
            type_result = await self.db.execute(type_query)
            totals[account_type.value] = float(type_result.scalar() or Decimal("0.00"))
        
        return {
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "total_journal_entries": total_entries,
            "posted_entries": posted_entries,
            "draft_entries": draft_entries,
            "current_period": f"{datetime.now().year}{datetime.now().month:02d}",
            "total_assets": totals.get("asset", 0.0),
            "total_liabilities": totals.get("liability", 0.0),
            "total_equity": totals.get("equity", 0.0),
            "total_income": totals.get("income", 0.0),
            "total_expenses": totals.get("expense", 0.0),
            "net_position": totals.get("asset", 0.0) - totals.get("liability", 0.0)
        }
