"""
Treasury - Fund Transfer Service
Business logic for internal and external fund transfers
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from backend.shared.database.treasury_models import (
    FundTransfer, TreasuryBankAccount,
    FundTransferType as DBFundTransferType,
    FundTransferStatus as DBFundTransferStatus
)
from backend.services.treasury.fund_transfer_schemas import (
    FundTransferCreate, FundTransferUpdate, FundTransferResponse,
    FundTransferApprove, FundTransferReject, FundTransferExecute,
    FundTransferCancel, FundTransferStatistics, FundTransferSummary,
    FundTransferSchedule, FundTransferType, FundTransferStatus
)


class FundTransferService:
    """Service for fund transfer operations"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def _generate_transfer_number(self, transfer_date: date) -> str:
        """Generate unique transfer number"""
        prefix = f"TRF-{transfer_date.strftime('%Y%m%d')}"
        
        count = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.transfer_number.like(f"{prefix}%")
        ).scalar() or 0
        
        return f"{prefix}-{count + 1:05d}"

    
    # ============================================================================
    # FUND TRANSFER MANAGEMENT
    # ============================================================================
    
    def create_transfer(self, data: FundTransferCreate) -> FundTransferResponse:
        """Create a new fund transfer"""
        # Verify source account
        source_account = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == data.source_account_id,
            TreasuryBankAccount.tenant_id == self.tenant_id,
            TreasuryBankAccount.is_deleted == False
        ).first()
        
        if not source_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found"
            )
        
        # Verify destination account for internal transfers
        if data.transfer_type == FundTransferType.INTERNAL:
            if not data.destination_account_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Destination account required for internal transfers"
                )
            
            dest_account = self.db.query(TreasuryBankAccount).filter(
                TreasuryBankAccount.id == data.destination_account_id,
                TreasuryBankAccount.tenant_id == self.tenant_id,
                TreasuryBankAccount.is_deleted == False
            ).first()
            
            if not dest_account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Destination account not found"
                )
        
        # Check sufficient balance
        if source_account.available_balance < data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: {source_account.available_balance}"
            )
        
        # Generate transfer number
        transfer_number = self._generate_transfer_number(date.today())
        
        # Create transfer
        transfer = FundTransfer(
            tenant_id=self.tenant_id,
            transfer_number=transfer_number,
            transfer_date=date.today(),
            transfer_type=data.transfer_type.value,
            source_account_id=data.source_account_id,
            source_account_number=source_account.account_number,
            destination_account_id=data.destination_account_id,
            destination_account_number=data.destination_account_number,
            destination_bank_name=data.destination_bank_name,
            destination_ifsc=data.destination_ifsc,
            destination_account_holder=data.destination_account_holder,
            amount=data.amount,
            currency=data.currency,
            purpose=data.purpose,
            reference_number=data.reference_number,
            is_scheduled=data.is_scheduled,
            scheduled_date=data.scheduled_date,
            status=DBFundTransferStatus.DRAFT,
            requested_by=self.user_id,
            notes=data.notes,
            created_by=self.user_id
        )
        
        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        
        return FundTransferResponse.model_validate(transfer)

    
    def get_transfer(self, transfer_id: int) -> FundTransferResponse:
        """Get transfer by ID"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        return FundTransferResponse.model_validate(transfer)
    
    def list_transfers(
        self,
        source_account_id: Optional[int] = None,
        destination_account_id: Optional[int] = None,
        transfer_type: Optional[FundTransferType] = None,
        status: Optional[FundTransferStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        is_scheduled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[FundTransferResponse], int]:
        """List transfers with filters"""
        query = self.db.query(FundTransfer).filter(
            FundTransfer.tenant_id == self.tenant_id
        )
        
        if source_account_id:
            query = query.filter(FundTransfer.source_account_id == source_account_id)
        
        if destination_account_id:
            query = query.filter(FundTransfer.destination_account_id == destination_account_id)
        
        if transfer_type:
            query = query.filter(FundTransfer.transfer_type == transfer_type.value)
        
        if status:
            query = query.filter(FundTransfer.status == status.value)
        
        if start_date:
            query = query.filter(FundTransfer.transfer_date >= start_date)
        
        if end_date:
            query = query.filter(FundTransfer.transfer_date <= end_date)
        
        if is_scheduled is not None:
            query = query.filter(FundTransfer.is_scheduled == is_scheduled)
        
        total = query.count()
        transfers = query.order_by(desc(FundTransfer.transfer_date)).offset(skip).limit(limit).all()
        
        return [FundTransferResponse.model_validate(t) for t in transfers], total

    
    def update_transfer(self, transfer_id: int, data: FundTransferUpdate) -> FundTransferResponse:
        """Update transfer (draft only)"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != DBFundTransferStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft transfers can be updated"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'transfer_type' and value:
                setattr(transfer, field, value.value)
            else:
                setattr(transfer, field, value)
        
        transfer.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return FundTransferResponse.model_validate(transfer)
    
    def delete_transfer(self, transfer_id: int) -> bool:
        """Delete transfer (draft only)"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status not in [DBFundTransferStatus.DRAFT, DBFundTransferStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft or rejected transfers can be deleted"
            )
        
        self.db.delete(transfer)
        self.db.commit()
        
        return True

    
    # ============================================================================
    # APPROVAL WORKFLOW
    # ============================================================================
    
    def submit_for_approval(self, transfer_id: int) -> FundTransferResponse:
        """Submit transfer for approval"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != DBFundTransferStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft transfers can be submitted"
            )
        
        transfer.status = DBFundTransferStatus.PENDING_APPROVAL
        transfer.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return FundTransferResponse.model_validate(transfer)
    
    def approve_transfer(self, transfer_id: int, approval_notes: Optional[str] = None) -> FundTransferResponse:
        """Approve transfer"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != DBFundTransferStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending transfers can be approved"
            )
        
        # Check if scheduled
        if transfer.is_scheduled:
            transfer.status = DBFundTransferStatus.SCHEDULED
        else:
            transfer.status = DBFundTransferStatus.APPROVED
        
        transfer.approved_by = self.user_id
        transfer.approved_at = datetime.utcnow()
        transfer.approval_notes = approval_notes
        transfer.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return FundTransferResponse.model_validate(transfer)

    
    def reject_transfer(self, transfer_id: int, rejection_reason: str) -> FundTransferResponse:
        """Reject transfer"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != DBFundTransferStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending transfers can be rejected"
            )
        
        transfer.status = DBFundTransferStatus.REJECTED
        transfer.rejected_by = self.user_id
        transfer.rejected_at = datetime.utcnow()
        transfer.rejection_reason = rejection_reason
        transfer.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return FundTransferResponse.model_validate(transfer)
    
    # ============================================================================
    # EXECUTION
    # ============================================================================
    
    def execute_transfer(self, transfer_id: int, transaction_ref: Optional[str] = None) -> FundTransferResponse:
        """Execute approved transfer"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status not in [DBFundTransferStatus.APPROVED, DBFundTransferStatus.SCHEDULED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only approved or scheduled transfers can be executed"
            )
        
        # Check scheduled date
        if transfer.is_scheduled and transfer.scheduled_date and transfer.scheduled_date > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer is scheduled for {transfer.scheduled_date}"
            )
        
        # Update source account balance
        source_account = self.db.query(TreasuryBankAccount).filter(
            TreasuryBankAccount.id == transfer.source_account_id
        ).first()
        
        if source_account.available_balance < transfer.amount:
            transfer.status = DBFundTransferStatus.FAILED
            transfer.failure_reason = "Insufficient balance"
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        try:
            # Deduct from source
            source_account.current_balance -= transfer.amount
            source_account.available_balance -= transfer.amount
            
            # Add to destination (if internal)
            if transfer.transfer_type == DBFundTransferType.INTERNAL and transfer.destination_account_id:
                dest_account = self.db.query(TreasuryBankAccount).filter(
                    TreasuryBankAccount.id == transfer.destination_account_id
                ).first()
                if dest_account:
                    dest_account.current_balance += transfer.amount
                    dest_account.available_balance += transfer.amount
            
            # Update transfer status
            transfer.status = DBFundTransferStatus.COMPLETED
            transfer.executed_by = self.user_id
            transfer.executed_at = datetime.utcnow()
            transfer.transaction_reference = transaction_ref or transfer.transfer_number
            transfer.updated_by = self.user_id
            
            self.db.commit()
            self.db.refresh(transfer)
            
            return FundTransferResponse.model_validate(transfer)
        
        except Exception as e:
            self.db.rollback()
            transfer.status = DBFundTransferStatus.FAILED
            transfer.failure_reason = str(e)
            transfer.retry_count += 1
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transfer execution failed: {str(e)}"
            )

    
    def cancel_transfer(self, transfer_id: int, cancellation_reason: str) -> FundTransferResponse:
        """Cancel transfer"""
        transfer = self.db.query(FundTransfer).filter(
            FundTransfer.id == transfer_id,
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status in [DBFundTransferStatus.COMPLETED, DBFundTransferStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed or cancelled transfers cannot be cancelled"
            )
        
        transfer.status = DBFundTransferStatus.CANCELLED
        transfer.rejection_reason = cancellation_reason
        transfer.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(transfer)
        
        return FundTransferResponse.model_validate(transfer)
    
    # ============================================================================
    # SCHEDULED TRANSFERS
    # ============================================================================
    
    def get_scheduled_transfers(self) -> List[FundTransferResponse]:
        """Get all scheduled transfers"""
        transfers = self.db.query(FundTransfer).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.is_scheduled == True
        ).all()
        
        return [FundTransferResponse.model_validate(t) for t in transfers]
    
    def get_due_scheduled_transfers(self) -> List[FundTransferResponse]:
        """Get scheduled transfers due for execution"""
        transfers = self.db.query(FundTransfer).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.is_scheduled == True,
            FundTransfer.scheduled_date <= date.today()
        ).all()
        
        return [FundTransferResponse.model_validate(t) for t in transfers]
    
    # ============================================================================
    # STATISTICS & REPORTS
    # ============================================================================
    
    def get_statistics(self) -> FundTransferStatistics:
        """Get transfer statistics"""
        total = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id
        ).scalar() or 0
        
        # Count by status
        status_counts = {}
        for status_value in DBFundTransferStatus:
            count = self.db.query(func.count(FundTransfer.id)).filter(
                FundTransfer.tenant_id == self.tenant_id,
                FundTransfer.status == status_value
            ).scalar() or 0
            status_counts[status_value.value] = count
        
        # Amounts
        amounts = self.db.query(
            func.sum(FundTransfer.amount).filter(FundTransfer.status == DBFundTransferStatus.COMPLETED).label('completed'),
            func.sum(FundTransfer.amount).filter(FundTransfer.status.in_([
                DBFundTransferStatus.PENDING_APPROVAL,
                DBFundTransferStatus.APPROVED,
                DBFundTransferStatus.SCHEDULED
            ])).label('pending'),
            func.sum(FundTransfer.amount).filter(FundTransfer.status == DBFundTransferStatus.FAILED).label('failed'),
            func.avg(FundTransfer.amount).label('average'),
            func.max(FundTransfer.amount).label('largest')
        ).filter(
            FundTransfer.tenant_id == self.tenant_id
        ).first()
        
        # By type
        by_type = {}
        for transfer_type in DBFundTransferType:
            count = self.db.query(func.count(FundTransfer.id)).filter(
                FundTransfer.tenant_id == self.tenant_id,
                FundTransfer.transfer_type == transfer_type
            ).scalar() or 0
            by_type[transfer_type.value] = count
        
        # Time-based counts
        today_count = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.transfer_date == date.today()
        ).scalar() or 0
        
        month_start = date.today().replace(day=1)
        month_count = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.transfer_date >= month_start
        ).scalar() or 0
        
        return FundTransferStatistics(
            total_transfers=total,
            draft_count=status_counts.get('draft', 0),
            pending_approval_count=status_counts.get('pending_approval', 0),
            approved_count=status_counts.get('approved', 0),
            rejected_count=status_counts.get('rejected', 0),
            scheduled_count=status_counts.get('scheduled', 0),
            in_progress_count=status_counts.get('in_progress', 0),
            completed_count=status_counts.get('completed', 0),
            failed_count=status_counts.get('failed', 0),
            cancelled_count=status_counts.get('cancelled', 0),
            total_amount_transferred=amounts.completed or Decimal("0.00"),
            total_amount_pending=amounts.pending or Decimal("0.00"),
            total_amount_completed=amounts.completed or Decimal("0.00"),
            total_amount_failed=amounts.failed or Decimal("0.00"),
            avg_transfer_amount=amounts.average or Decimal("0.00"),
            largest_transfer=amounts.largest or Decimal("0.00"),
            by_type=by_type,
            today_transfers=today_count,
            this_month_transfers=month_count
        )
    
    def get_account_summary(self, account_id: int) -> FundTransferSummary:
        """Get transfer summary for an account"""
        # Sent (as source)
        sent = self.db.query(
            func.count(FundTransfer.id),
            func.sum(FundTransfer.amount)
        ).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.source_account_id == account_id,
            FundTransfer.status == DBFundTransferStatus.COMPLETED
        ).first()
        
        sent_count = sent[0] or 0
        sent_amount = sent[1] or Decimal("0.00")
        
        # Received (as destination, internal only)
        received = self.db.query(
            func.sum(FundTransfer.amount)
        ).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.destination_account_id == account_id,
            FundTransfer.status == DBFundTransferStatus.COMPLETED
        ).scalar() or Decimal("0.00")
        
        # Pending
        pending = self.db.query(
            func.count(FundTransfer.id),
            func.sum(FundTransfer.amount)
        ).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.source_account_id == account_id,
            FundTransfer.status.in_([
                DBFundTransferStatus.PENDING_APPROVAL,
                DBFundTransferStatus.APPROVED,
                DBFundTransferStatus.SCHEDULED
            ])
        ).first()
        
        pending_count = pending[0] or 0
        pending_amount = pending[1] or Decimal("0.00")
        
        return FundTransferSummary(
            account_id=account_id,
            total_transfers=sent_count,
            total_sent=sent_amount,
            total_received=received,
            net_position=received - sent_amount,
            pending_transfers=pending_count,
            pending_amount=pending_amount
        )
    
    def get_schedule_summary(self) -> FundTransferSchedule:
        """Get scheduled transfers summary"""
        total = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.is_scheduled == True
        ).scalar() or 0
        
        due_today = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.scheduled_date == date.today()
        ).scalar() or 0
        
        week_end = date.today() + timedelta(days=7)
        due_week = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.scheduled_date.between(date.today(), week_end)
        ).scalar() or 0
        
        month_end = date.today().replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        due_month = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.scheduled_date.between(date.today(), month_end)
        ).scalar() or 0
        
        overdue = self.db.query(func.count(FundTransfer.id)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED,
            FundTransfer.scheduled_date < date.today()
        ).scalar() or 0
        
        scheduled_amount = self.db.query(func.sum(FundTransfer.amount)).filter(
            FundTransfer.tenant_id == self.tenant_id,
            FundTransfer.status == DBFundTransferStatus.SCHEDULED
        ).scalar() or Decimal("0.00")
        
        return FundTransferSchedule(
            total_scheduled=total,
            due_today=due_today,
            due_this_week=due_week,
            due_this_month=due_month,
            overdue=overdue,
            scheduled_amount=scheduled_amount
        )
