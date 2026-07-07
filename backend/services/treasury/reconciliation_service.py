"""
Treasury - Bank Reconciliation Service
Business logic for bank reconciliation, statement import, and matching
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from backend.shared.database.treasury_models import (
    BankStatement, BankReconciliation, ReconciliationItem,
    TreasuryBankAccount, ReconciliationStatus as DBReconciliationStatus,
    ReconciliationItemType as DBReconciliationItemType
)
from backend.services.treasury.reconciliation_schemas import (
    BankStatementCreate, BankStatementUpdate, BankStatementResponse,
    BankStatementBulkImport, BankReconciliationCreate, BankReconciliationUpdate,
    BankReconciliationResponse, BankReconciliationDetail, ReconciliationItemCreate,
    ReconciliationItemUpdate, ReconciliationItemResponse, MatchTransactionRequest,
    UnmatchTransactionRequest, AutoMatchRequest, ReconciliationStatistics,
    BankStatementSummary, ReconciliationDifference, ReconciliationStatus,
    ReconciliationItemType
)


class ReconciliationService:
    """Service for bank reconciliation operations"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    # ============================================================================
    # BANK STATEMENT MANAGEMENT
    # ============================================================================
    
    def create_bank_statement(self, data: BankStatementCreate) -> BankStatementResponse:
        """Create a new bank statement entry"""
        # Verify bank account exists and belongs to tenant
        bank_account = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == data.bank_account_id,
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        ).first()
        
        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )
        
        # Create statement
        statement = BankStatement(
            tenant_id=self.tenant_id,
            bank_account_id=data.bank_account_id,
            transaction_date=data.transaction_date,
            value_date=data.value_date,
            transaction_reference=data.transaction_reference,
            description=data.description,
            cheque_number=data.cheque_number,
            debit_amount=data.debit_amount,
            credit_amount=data.credit_amount,
            balance=data.balance,
            import_batch_id=data.import_batch_id,
            import_date=datetime.utcnow(),
            imported_by=self.user_id
        )
        
        self.db.add(statement)
        self.db.commit()
        self.db.refresh(statement)

        
        return BankStatementResponse.model_validate(statement)
    
    def bulk_import_statements(self, data: BankStatementBulkImport) -> List[BankStatementResponse]:
        """Bulk import bank statements"""
        # Verify bank account
        bank_account = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == data.bank_account_id,
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        ).first()
        
        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )
        
        statements = []
        for stmt_data in data.statements:
            statement = BankStatement(
                tenant_id=self.tenant_id,
                bank_account_id=data.bank_account_id,
                transaction_date=stmt_data.transaction_date,
                value_date=stmt_data.value_date,
                transaction_reference=stmt_data.transaction_reference,
                description=stmt_data.description,
                cheque_number=stmt_data.cheque_number,
                debit_amount=stmt_data.debit_amount,
                credit_amount=stmt_data.credit_amount,
                balance=stmt_data.balance,
                import_batch_id=data.import_batch_id,
                import_date=datetime.utcnow(),
                imported_by=self.user_id
            )
            statements.append(statement)
        
        self.db.bulk_save_objects(statements, return_defaults=True)
        self.db.commit()
        
        return [BankStatementResponse.model_validate(s) for s in statements]

    
    def get_bank_statement(self, statement_id: int) -> BankStatementResponse:
        """Get bank statement by ID"""
        statement = self.db.query(BankStatement).filter(
            BankStatement.id == statement_id,
            BankStatement.tenant_id == self.tenant_id
        ).first()
        
        if not statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank statement not found"
            )
        
        return BankStatementResponse.model_validate(statement)
    
    def list_bank_statements(
        self,
        bank_account_id: Optional[int] = None,
        is_matched: Optional[bool] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[BankStatementResponse], int]:
        """List bank statements with filters"""
        query = self.db.query(BankStatement).filter(
            BankStatement.tenant_id == self.tenant_id
        )
        
        if bank_account_id:
            query = query.filter(BankStatement.bank_account_id == bank_account_id)
        
        if is_matched is not None:
            query = query.filter(BankStatement.is_matched == is_matched)
        
        if start_date:
            query = query.filter(BankStatement.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(BankStatement.transaction_date <= end_date)
        
        total = query.count()
        statements = query.order_by(desc(BankStatement.transaction_date)).offset(skip).limit(limit).all()
        
        return [BankStatementResponse.model_validate(s) for s in statements], total

    
    def update_bank_statement(self, statement_id: int, data: BankStatementUpdate) -> BankStatementResponse:
        """Update bank statement"""
        statement = self.db.query(BankStatement).filter(
            BankStatement.id == statement_id,
            BankStatement.tenant_id == self.tenant_id
        ).first()
        
        if not statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank statement not found"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(statement, field, value)
        
        self.db.commit()
        self.db.refresh(statement)
        
        return BankStatementResponse.model_validate(statement)
    
    def delete_bank_statement(self, statement_id: int) -> bool:
        """Delete bank statement"""
        statement = self.db.query(BankStatement).filter(
            BankStatement.id == statement_id,
            BankStatement.tenant_id == self.tenant_id
        ).first()
        
        if not statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank statement not found"
            )
        
        # Check if matched - prevent deletion of matched statements
        if statement.is_matched:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete matched statement. Unmatch first."
            )
        
        self.db.delete(statement)
        self.db.commit()
        
        return True

    
    # ============================================================================
    # BANK RECONCILIATION MANAGEMENT
    # ============================================================================
    
    def create_reconciliation(self, data: BankReconciliationCreate) -> BankReconciliationResponse:
        """Create a new bank reconciliation"""
        # Verify bank account
        bank_account = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == data.bank_account_id,
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        ).first()
        
        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )
        
        # Generate reconciliation number
        recon_number = self._generate_reconciliation_number(data.bank_account_id, data.reconciliation_date)
        
        # Calculate difference
        difference = data.bank_balance - data.book_balance
        
        # Create reconciliation
        reconciliation = BankReconciliation(
            tenant_id=self.tenant_id,
            reconciliation_number=recon_number,
            reconciliation_date=data.reconciliation_date,
            bank_account_id=data.bank_account_id,
            period_start_date=data.period_start_date,
            period_end_date=data.period_end_date,
            book_balance=data.book_balance,
            bank_balance=data.bank_balance,
            difference=difference,
            status=DBReconciliationStatus.DRAFT,
            notes=data.notes,
            created_by=self.user_id
        )
        
        self.db.add(reconciliation)
        self.db.commit()
        self.db.refresh(reconciliation)
        
        return BankReconciliationResponse.model_validate(reconciliation)

    
    def _generate_reconciliation_number(self, bank_account_id: int, recon_date: date) -> str:
        """Generate unique reconciliation number"""
        prefix = f"RECON-{bank_account_id}-{recon_date.strftime('%Y%m%d')}"
        
        # Find existing count for this prefix
        count = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.reconciliation_number.like(f"{prefix}%")
        ).scalar() or 0
        
        return f"{prefix}-{count + 1:03d}"
    
    def get_reconciliation(self, reconciliation_id: int) -> BankReconciliationDetail:
        """Get reconciliation with items"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )
        
        # Get items
        items = self.db.query(ReconciliationItem).filter(
            ReconciliationItem.reconciliation_id == reconciliation_id,
            ReconciliationItem.tenant_id == self.tenant_id
        ).all()
        
        result = BankReconciliationDetail.model_validate(reconciliation)
        result.items = [ReconciliationItemResponse.model_validate(item) for item in items]
        
        return result

    
    def list_reconciliations(
        self,
        bank_account_id: Optional[int] = None,
        status: Optional[ReconciliationStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[BankReconciliationResponse], int]:
        """List reconciliations with filters"""
        query = self.db.query(BankReconciliation).filter(
            BankReconciliation.tenant_id == self.tenant_id
        )
        
        if bank_account_id:
            query = query.filter(BankReconciliation.bank_account_id == bank_account_id)
        
        if status:
            query = query.filter(BankReconciliation.status == status.value)
        
        if start_date:
            query = query.filter(BankReconciliation.reconciliation_date >= start_date)
        
        if end_date:
            query = query.filter(BankReconciliation.reconciliation_date <= end_date)
        
        total = query.count()
        reconciliations = query.order_by(desc(BankReconciliation.reconciliation_date)).offset(skip).limit(limit).all()
        
        return [BankReconciliationResponse.model_validate(r) for r in reconciliations], total
    
    def update_reconciliation(self, reconciliation_id: int, data: BankReconciliationUpdate) -> BankReconciliationResponse:
        """Update reconciliation"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )

        
        # Prevent updates to approved reconciliations
        if reconciliation.status == DBReconciliationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update approved reconciliation"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reconciliation, field, value)
        
        # Recalculate difference if balances changed
        if 'book_balance' in update_data or 'bank_balance' in update_data:
            reconciliation.difference = reconciliation.bank_balance - reconciliation.book_balance
        
        reconciliation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(reconciliation)
        
        return BankReconciliationResponse.model_validate(reconciliation)
    
    def delete_reconciliation(self, reconciliation_id: int) -> bool:
        """Delete reconciliation"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )
        
        # Prevent deletion of approved reconciliations
        if reconciliation.status == DBReconciliationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete approved reconciliation"
            )
        
        self.db.delete(reconciliation)
        self.db.commit()
        
        return True

    
    # ============================================================================
    # RECONCILIATION ITEMS
    # ============================================================================
    
    def add_reconciliation_item(self, reconciliation_id: int, data: ReconciliationItemCreate) -> ReconciliationItemResponse:
        """Add item to reconciliation"""
        # Verify reconciliation exists
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )
        
        # Prevent adding to approved reconciliations
        if reconciliation.status == DBReconciliationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add items to approved reconciliation"
            )
        
        # Create item
        item = ReconciliationItem(
            tenant_id=self.tenant_id,
            reconciliation_id=reconciliation_id,
            item_type=data.item_type.value,
            item_date=data.item_date,
            description=data.description,
            reference_number=data.reference_number,
            amount=data.amount,
            is_debit=data.is_debit,
            bank_statement_id=data.bank_statement_id,
            gl_entry_id=data.gl_entry_id,
            notes=data.notes,
            created_by=self.user_id
        )
        
        self.db.add(item)

        
        # Update reconciliation summary
        self._update_reconciliation_summary(reconciliation_id)
        
        self.db.commit()
        self.db.refresh(item)
        
        return ReconciliationItemResponse.model_validate(item)
    
    def update_reconciliation_item(self, item_id: int, data: ReconciliationItemUpdate) -> ReconciliationItemResponse:
        """Update reconciliation item"""
        item = self.db.query(ReconciliationItem).filter(
            ReconciliationItem.id == item_id,
            ReconciliationItem.tenant_id == self.tenant_id
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation item not found"
            )
        
        # Check reconciliation status
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == item.reconciliation_id
        ).first()
        
        if reconciliation.status == DBReconciliationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update items in approved reconciliation"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'item_type' and value:
                setattr(item, field, value.value)
            else:
                setattr(item, field, value)
        
        # Update reconciliation summary
        self._update_reconciliation_summary(item.reconciliation_id)
        
        self.db.commit()
        self.db.refresh(item)
        
        return ReconciliationItemResponse.model_validate(item)

    
    def delete_reconciliation_item(self, item_id: int) -> bool:
        """Delete reconciliation item"""
        item = self.db.query(ReconciliationItem).filter(
            ReconciliationItem.id == item_id,
            ReconciliationItem.tenant_id == self.tenant_id
        ).first()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation item not found"
            )
        
        # Check reconciliation status
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == item.reconciliation_id
        ).first()
        
        if reconciliation.status == DBReconciliationStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete items from approved reconciliation"
            )
        
        reconciliation_id = item.reconciliation_id
        self.db.delete(item)
        
        # Update reconciliation summary
        self._update_reconciliation_summary(reconciliation_id)
        
        self.db.commit()
        
        return True
    
    def _update_reconciliation_summary(self, reconciliation_id: int):
        """Update reconciliation matched/unmatched summary"""
        items = self.db.query(ReconciliationItem).filter(
            ReconciliationItem.reconciliation_id == reconciliation_id,
            ReconciliationItem.tenant_id == self.tenant_id
        ).all()

        
        total_matched = sum(1 for item in items if item.is_matched)
        total_unmatched = len(items) - total_matched
        matched_amount = sum(item.amount for item in items if item.is_matched)
        unmatched_amount = sum(item.amount for item in items if not item.is_matched)
        
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id
        ).first()
        
        reconciliation.total_matched = total_matched
        reconciliation.total_unmatched = total_unmatched
        reconciliation.matched_amount = matched_amount
        reconciliation.unmatched_amount = unmatched_amount
        
        # Update status based on matching
        if total_matched > 0 and total_unmatched == 0:
            reconciliation.status = DBReconciliationStatus.MATCHED
        elif total_matched > 0:
            reconciliation.status = DBReconciliationStatus.IN_PROGRESS
    
    # ============================================================================
    # MATCHING OPERATIONS
    # ============================================================================
    
    def match_transaction(self, data: MatchTransactionRequest) -> BankStatementResponse:
        """Match bank statement with GL entry"""
        statement = self.db.query(BankStatement).filter(
            BankStatement.id == data.bank_statement_id,
            BankStatement.tenant_id == self.tenant_id
        ).first()
        
        if not statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank statement not found"
            )
        
        statement.is_matched = True
        statement.matched_gl_entry_id = data.gl_entry_id
        statement.matched_at = datetime.utcnow()
        statement.matched_by = self.user_id
        
        self.db.commit()
        self.db.refresh(statement)
        
        return BankStatementResponse.model_validate(statement)

    
    def unmatch_transaction(self, data: UnmatchTransactionRequest) -> BankStatementResponse:
        """Unmatch a bank statement transaction"""
        statement = self.db.query(BankStatement).filter(
            BankStatement.id == data.bank_statement_id,
            BankStatement.tenant_id == self.tenant_id
        ).first()
        
        if not statement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank statement not found"
            )
        
        statement.is_matched = False
        statement.matched_gl_entry_id = None
        statement.matched_at = None
        statement.matched_by = None
        
        self.db.commit()
        self.db.refresh(statement)
        
        return BankStatementResponse.model_validate(statement)
    
    def auto_match_transactions(self, data: AutoMatchRequest) -> dict:
        """Automatically match transactions based on criteria"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == data.reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )
        
        # Get unmatched bank statements for this account and period
        statements = self.db.query(BankStatement).filter(
            BankStatement.bank_account_id == reconciliation.bank_account_id,
            BankStatement.tenant_id == self.tenant_id,
            BankStatement.is_matched == False,
            BankStatement.transaction_date >= reconciliation.period_start_date,
            BankStatement.transaction_date <= reconciliation.period_end_date
        ).all()
        
        matched_count = 0
        # Auto-matching logic would go here
        # This is a placeholder - real implementation would match against GL entries
        
        return {
            "reconciliation_id": data.reconciliation_id,
            "total_statements": len(statements),
            "matched_count": matched_count,
            "message": f"Auto-matched {matched_count} out of {len(statements)} transactions"
        }

    
    # ============================================================================
    # APPROVAL WORKFLOW
    # ============================================================================
    
    def submit_for_approval(self, reconciliation_id: int) -> BankReconciliationResponse:
        """Submit reconciliation for approval"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )
        
        if reconciliation.status not in [DBReconciliationStatus.DRAFT, DBReconciliationStatus.IN_PROGRESS, DBReconciliationStatus.MATCHED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reconciliation cannot be submitted for approval in current status"
            )
        
        reconciliation.status = DBReconciliationStatus.PENDING_APPROVAL
        reconciliation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(reconciliation)
        
        return BankReconciliationResponse.model_validate(reconciliation)
    
    def approve_reconciliation(self, reconciliation_id: int, approval_notes: Optional[str] = None) -> BankReconciliationResponse:
        """Approve reconciliation"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )

        
        if reconciliation.status != DBReconciliationStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending approval reconciliations can be approved"
            )
        
        reconciliation.status = DBReconciliationStatus.APPROVED
        reconciliation.approved_by = self.user_id
        reconciliation.approved_at = datetime.utcnow()
        reconciliation.approval_notes = approval_notes
        reconciliation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(reconciliation)
        
        return BankReconciliationResponse.model_validate(reconciliation)
    
    def reject_reconciliation(self, reconciliation_id: int, approval_notes: str) -> BankReconciliationResponse:
        """Reject reconciliation"""
        reconciliation = self.db.query(BankReconciliation).filter(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        if not reconciliation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reconciliation not found"
            )
        
        if reconciliation.status != DBReconciliationStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending approval reconciliations can be rejected"
            )
        
        reconciliation.status = DBReconciliationStatus.REJECTED
        reconciliation.approval_notes = approval_notes
        reconciliation.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(reconciliation)
        
        return BankReconciliationResponse.model_validate(reconciliation)

    
    # ============================================================================
    # STATISTICS & REPORTS
    # ============================================================================
    
    def get_reconciliation_statistics(self) -> ReconciliationStatistics:
        """Get reconciliation statistics"""
        total = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id
        ).scalar() or 0
        
        draft = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status == DBReconciliationStatus.DRAFT
        ).scalar() or 0
        
        in_progress = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status == DBReconciliationStatus.IN_PROGRESS
        ).scalar() or 0
        
        matched = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status == DBReconciliationStatus.MATCHED
        ).scalar() or 0
        
        pending = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status == DBReconciliationStatus.PENDING_APPROVAL
        ).scalar() or 0
        
        approved = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status == DBReconciliationStatus.APPROVED
        ).scalar() or 0
        
        rejected = self.db.query(func.count(BankReconciliation.id)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status == DBReconciliationStatus.REJECTED
        ).scalar() or 0

        
        # Amounts
        amounts = self.db.query(
            func.sum(BankReconciliation.matched_amount),
            func.sum(BankReconciliation.unmatched_amount),
            func.avg(BankReconciliation.difference)
        ).filter(
            BankReconciliation.tenant_id == self.tenant_id
        ).first()
        
        total_matched_amount = amounts[0] or Decimal("0.00")
        total_unmatched_amount = amounts[1] or Decimal("0.00")
        avg_difference = amounts[2] or Decimal("0.00")
        
        # Oldest unreconciled
        oldest = self.db.query(func.min(BankReconciliation.reconciliation_date)).filter(
            BankReconciliation.tenant_id == self.tenant_id,
            BankReconciliation.status != DBReconciliationStatus.APPROVED
        ).scalar()
        
        return ReconciliationStatistics(
            total_reconciliations=total,
            draft_count=draft,
            in_progress_count=in_progress,
            matched_count=matched,
            pending_approval_count=pending,
            approved_count=approved,
            rejected_count=rejected,
            total_matched_amount=total_matched_amount,
            total_unmatched_amount=total_unmatched_amount,
            average_difference=avg_difference,
            oldest_unreconciled_date=oldest
        )
    
    def get_bank_statement_summary(self, bank_account_id: int) -> BankStatementSummary:
        """Get bank statement summary for an account"""
        total = self.db.query(func.count(BankStatement.id)).filter(
            BankStatement.bank_account_id == bank_account_id,
            BankStatement.tenant_id == self.tenant_id
        ).scalar() or 0
        
        matched = self.db.query(func.count(BankStatement.id)).filter(
            BankStatement.bank_account_id == bank_account_id,
            BankStatement.tenant_id == self.tenant_id,
            BankStatement.is_matched == True
        ).scalar() or 0

        
        unmatched = total - matched
        
        amounts = self.db.query(
            func.sum(BankStatement.debit_amount),
            func.sum(BankStatement.credit_amount)
        ).filter(
            BankStatement.bank_account_id == bank_account_id,
            BankStatement.tenant_id == self.tenant_id
        ).first()
        
        total_debit = amounts[0] or Decimal("0.00")
        total_credit = amounts[1] or Decimal("0.00")
        
        oldest = self.db.query(func.min(BankStatement.transaction_date)).filter(
            BankStatement.bank_account_id == bank_account_id,
            BankStatement.tenant_id == self.tenant_id,
            BankStatement.is_matched == False
        ).scalar()
        
        return BankStatementSummary(
            bank_account_id=bank_account_id,
            statement_count=total,
            matched_count=matched,
            unmatched_count=unmatched,
            total_debit=total_debit,
            total_credit=total_credit,
            oldest_unmatched_date=oldest
        )
    
    def get_reconciliation_difference_breakdown(self, reconciliation_id: int) -> ReconciliationDifference:
        """Get breakdown of reconciliation differences by type"""
        items = self.db.query(ReconciliationItem).filter(
            ReconciliationItem.reconciliation_id == reconciliation_id,
            ReconciliationItem.tenant_id == self.tenant_id
        ).all()
        
        result = ReconciliationDifference()
        
        for item in items:
            item_type = item.item_type
            amount = item.amount if item.is_debit else -item.amount

            
            if item_type == DBReconciliationItemType.OUTSTANDING_CHEQUE:
                result.outstanding_cheques_amount += amount
                result.outstanding_cheques_count += 1
            elif item_type == DBReconciliationItemType.DEPOSIT_IN_TRANSIT:
                result.deposits_in_transit_amount += amount
                result.deposits_in_transit_count += 1
            elif item_type == DBReconciliationItemType.BANK_CHARGES:
                result.bank_charges_amount += amount
                result.bank_charges_count += 1
            elif item_type == DBReconciliationItemType.INTEREST_EARNED:
                result.interest_earned_amount += amount
                result.interest_earned_count += 1
            elif item_type == DBReconciliationItemType.DIRECT_DEBIT:
                result.direct_debits_amount += amount
                result.direct_debits_count += 1
            elif item_type == DBReconciliationItemType.DIRECT_CREDIT:
                result.direct_credits_amount += amount
                result.direct_credits_count += 1
            elif item_type == DBReconciliationItemType.ERROR_CORRECTION:
                result.error_corrections_amount += amount
                result.error_corrections_count += 1
            else:
                result.other_amount += amount
                result.other_count += 1
            
            result.total_difference += amount
            result.total_items += 1
        
        return result
