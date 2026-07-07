"""
Treasury Cash Position - Business Logic Service
Handles all cash position management operations
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from fastapi import HTTPException, status

from shared.database.treasury_models import (
    CashPosition,
    CashPositionStatus,
    TreasuryBankAccount
)
from .cash_position_schemas import (
    CashPositionCreate,
    CashPositionUpdate,
    CashPositionResponse,
    CashPositionStatistics,
    BranchCashSummary,
    CashMovementSummary,
    CashAlertResponse,
    CashTransferCreate,
    CashTransferResponse
)


class CashPositionService:
    """Service for cash position management"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
    
    # ============================================
    # CRUD Operations
    # ============================================
    
    async def create_cash_position(
        self,
        data: CashPositionCreate,
        user_id: int
    ) -> CashPosition:
        """Create new cash position record"""
        
        # Check if position already exists for this date and branch
        existing = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == data.position_date,
                CashPosition.branch_id == data.branch_id,
                CashPosition.is_deleted == False
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cash position already exists for this date and branch"
            )
        
        # Calculate closing balance
        closing_balance = (
            data.opening_balance +
            data.cash_received +
            data.bank_withdrawal -
            data.cash_paid -
            data.bank_deposit
        )
        
        # Create position record
        position = CashPosition(
            tenant_id=self.tenant_id,
            position_date=data.position_date,
            branch_id=data.branch_id,
            account_id=data.account_id,
            opening_balance=data.opening_balance,
            cash_received=data.cash_received,
            cash_paid=data.cash_paid,
            bank_deposit=data.bank_deposit,
            bank_withdrawal=data.bank_withdrawal,
            closing_balance=closing_balance,
            denomination_details=data.denomination_details,
            vault_location=data.vault_location,
            recorded_by=user_id,
            verified_by=data.verified_by,
            verified_at=data.verified_at,
            discrepancy_amount=data.discrepancy_amount,
            discrepancy_reason=data.discrepancy_reason,
            notes=data.notes,
            status=data.status,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    async def get_cash_position(self, position_id: int) -> CashPosition:
        """Get cash position by ID"""
        position = self.db.query(CashPosition).filter(
            and_(
                CashPosition.id == position_id,
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.is_deleted == False
            )
        ).first()
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cash position not found"
            )
        
        return position
    
    async def list_cash_positions(
        self,
        page: int = 1,
        page_size: int = 50,
        branch_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[CashPosition], int]:
        """List cash positions with filters and pagination"""
        
        query = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.is_deleted == False
            )
        )
        
        # Apply filters
        if branch_id:
            query = query.filter(CashPosition.branch_id == branch_id)
        
        if status_filter:
            query = query.filter(CashPosition.status == status_filter)
        
        if start_date:
            query = query.filter(CashPosition.position_date >= start_date)
        
        if end_date:
            query = query.filter(CashPosition.position_date <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        positions = query.order_by(desc(CashPosition.position_date)).offset(offset).limit(page_size).all()
        
        return positions, total
    
    async def update_cash_position(
        self,
        position_id: int,
        data: CashPositionUpdate,
        user_id: int
    ) -> CashPosition:
        """Update cash position"""
        position = await self.get_cash_position(position_id)
        
        # Check if already finalized
        if position.status == "finalized":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update finalized cash position"
            )
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        
        # Recalculate closing balance if relevant fields changed
        if any(k in update_data for k in [
            'opening_balance', 'cash_received', 'cash_paid', 
            'bank_deposit', 'bank_withdrawal'
        ]):
            opening = update_data.get('opening_balance', position.opening_balance)
            received = update_data.get('cash_received', position.cash_received)
            paid = update_data.get('cash_paid', position.cash_paid)
            deposit = update_data.get('bank_deposit', position.bank_deposit)
            withdrawal = update_data.get('bank_withdrawal', position.bank_withdrawal)
            
            update_data['closing_balance'] = (
                opening + received + withdrawal - paid - deposit
            )
        
        for key, value in update_data.items():
            setattr(position, key, value)
        
        position.updated_by = user_id
        position.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    async def delete_cash_position(self, position_id: int, user_id: int):
        """Soft delete cash position"""
        position = await self.get_cash_position(position_id)
        
        # Check if finalized
        if position.status == "finalized":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete finalized cash position"
            )
        
        position.is_deleted = True
        position.updated_by = user_id
        position.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    # ============================================
    # Business Operations
    # ============================================
    
    async def verify_cash_position(
        self,
        position_id: int,
        user_id: int
    ) -> CashPosition:
        """Verify cash position"""
        position = await self.get_cash_position(position_id)
        
        if position.status == "finalized":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position already finalized"
            )
        
        position.verified_by = user_id
        position.verified_at = datetime.utcnow()
        position.status = "verified"
        position.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    async def finalize_cash_position(
        self,
        position_id: int,
        user_id: int
    ) -> CashPosition:
        """Finalize cash position (cannot be changed after)"""
        position = await self.get_cash_position(position_id)
        
        if position.status != "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position must be verified before finalization"
            )
        
        position.status = "finalized"
        position.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    async def get_current_position(
        self,
        branch_id: Optional[int] = None
    ) -> Optional[CashPosition]:
        """Get current cash position for branch"""
        today = date.today()
        
        query = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(CashPosition.branch_id == branch_id)
        
        return query.first()
    
    async def get_position_by_date(
        self,
        position_date: date,
        branch_id: Optional[int] = None
    ) -> Optional[CashPosition]:
        """Get cash position for specific date"""
        query = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == position_date,
                CashPosition.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(CashPosition.branch_id == branch_id)
        
        return query.first()
    
    # ============================================
    # Statistics & Reports
    # ============================================
    
    async def get_statistics(self) -> CashPositionStatistics:
        """Get cash position statistics"""
        today = date.today()
        
        # Total cash on hand
        total_cash = self.db.query(
            func.sum(CashPosition.closing_balance)
        ).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.is_deleted == False
            )
        ).scalar() or Decimal(0)
        
        # Branch counts
        total_branches = self.db.query(
            func.count(func.distinct(CashPosition.branch_id))
        ).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.is_deleted == False
            )
        ).scalar() or 0
        
        # Low cash branches (< 50,000)
        low_cash_branches = self.db.query(
            func.count(CashPosition.id)
        ).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.closing_balance < 50000,
                CashPosition.is_deleted == False
            )
        ).scalar() or 0
        
        # High cash branches (> 500,000)
        high_cash_branches = self.db.query(
            func.count(CashPosition.id)
        ).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.closing_balance > 500000,
                CashPosition.is_deleted == False
            )
        ).scalar() or 0
        
        # Today's totals
        today_stats = self.db.query(
            func.sum(CashPosition.cash_received),
            func.sum(CashPosition.cash_paid),
            func.sum(CashPosition.bank_deposit)
        ).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.is_deleted == False
            )
        ).first()
        
        # Pending verification
        pending_verification = self.db.query(
            func.count(CashPosition.id)
        ).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.status == "draft",
                CashPosition.is_deleted == False
            )
        ).scalar() or 0
        
        return CashPositionStatistics(
            total_cash_on_hand=total_cash,
            total_branches=total_branches,
            branches_with_low_cash=low_cash_branches,
            branches_with_high_cash=high_cash_branches,
            total_cash_received_today=today_stats[0] or Decimal(0),
            total_cash_paid_today=today_stats[1] or Decimal(0),
            total_bank_deposits_today=today_stats[2] or Decimal(0),
            positions_pending_verification=pending_verification,
            cash_by_branch={}  # TODO: Implement with branch names
        )
    
    async def get_branch_summary(
        self,
        branch_id: int
    ) -> Optional[BranchCashSummary]:
        """Get cash summary for specific branch"""
        today = date.today()
        
        position = await self.get_position_by_date(today, branch_id)
        
        if not position:
            return None
        
        low_cash_threshold = Decimal(50000)
        
        return BranchCashSummary(
            branch_id=branch_id,
            branch_name=f"Branch {branch_id}",  # TODO: Get actual name
            current_cash=position.closing_balance,
            opening_balance=position.opening_balance,
            closing_balance=position.closing_balance,
            last_updated=position.updated_at,
            status=position.status,
            low_cash_alert=position.closing_balance < low_cash_threshold
        )
    
    async def get_cash_movement(
        self,
        start_date: date,
        end_date: date,
        branch_id: Optional[int] = None
    ) -> List[CashMovementSummary]:
        """Get cash movement summary for date range"""
        query = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date >= start_date,
                CashPosition.position_date <= end_date,
                CashPosition.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(CashPosition.branch_id == branch_id)
        
        positions = query.order_by(CashPosition.position_date).all()
        
        summaries = []
        for pos in positions:
            net_movement = (
                pos.cash_received + pos.bank_withdrawal -
                pos.cash_paid - pos.bank_deposit
            )
            
            summaries.append(CashMovementSummary(
                date=pos.position_date,
                opening_balance=pos.opening_balance,
                cash_received=pos.cash_received,
                cash_paid=pos.cash_paid,
                bank_deposit=pos.bank_deposit,
                bank_withdrawal=pos.bank_withdrawal,
                closing_balance=pos.closing_balance,
                net_movement=net_movement
            ))
        
        return summaries
    
    async def get_alerts(self) -> List[CashAlertResponse]:
        """Get cash-related alerts"""
        alerts = []
        today = date.today()
        
        # Low cash alerts
        low_cash = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.closing_balance < 50000,
                CashPosition.is_deleted == False
            )
        ).all()
        
        for pos in low_cash:
            alerts.append(CashAlertResponse(
                alert_type="low_cash",
                severity="warning",
                branch_id=pos.branch_id,
                branch_name=f"Branch {pos.branch_id}",
                message=f"Low cash alert: ₹{pos.closing_balance:,.2f}",
                amount=pos.closing_balance,
                created_at=datetime.utcnow()
            ))
        
        # High cash alerts
        high_cash = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.position_date == today,
                CashPosition.closing_balance > 500000,
                CashPosition.is_deleted == False
            )
        ).all()
        
        for pos in high_cash:
            alerts.append(CashAlertResponse(
                alert_type="high_cash",
                severity="info",
                branch_id=pos.branch_id,
                branch_name=f"Branch {pos.branch_id}",
                message=f"High cash alert: ₹{pos.closing_balance:,.2f}",
                amount=pos.closing_balance,
                created_at=datetime.utcnow()
            ))
        
        # Discrepancy alerts
        discrepancy = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.discrepancy_amount != 0,
                CashPosition.status != "finalized",
                CashPosition.is_deleted == False
            )
        ).all()
        
        for pos in discrepancy:
            alerts.append(CashAlertResponse(
                alert_type="discrepancy",
                severity="warning",
                branch_id=pos.branch_id,
                branch_name=f"Branch {pos.branch_id}",
                message=f"Cash discrepancy: ₹{pos.discrepancy_amount:,.2f}",
                amount=pos.discrepancy_amount,
                created_at=datetime.utcnow()
            ))
        
        # Pending verification
        pending = self.db.query(CashPosition).filter(
            and_(
                CashPosition.tenant_id == self.tenant_id,
                CashPosition.status == "draft",
                CashPosition.is_deleted == False
            )
        ).all()
        
        for pos in pending:
            alerts.append(CashAlertResponse(
                alert_type="pending_verification",
                severity="info",
                branch_id=pos.branch_id,
                branch_name=f"Branch {pos.branch_id}",
                message=f"Position pending verification for {pos.position_date}",
                amount=pos.closing_balance,
                created_at=datetime.utcnow()
            ))
        
        return alerts
    
    # ============================================
    # Bulk Operations
    # ============================================
    
    async def bulk_create_positions(
        self,
        positions: List[CashPositionCreate],
        user_id: int
    ) -> Tuple[List[int], List[Dict]]:
        """Bulk create cash positions"""
        created_ids = []
        errors = []
        
        for idx, pos_data in enumerate(positions):
            try:
                position = await self.create_cash_position(pos_data, user_id)
                created_ids.append(position.id)
            except Exception as e:
                errors.append({
                    "index": idx,
                    "error": str(e),
                    "data": pos_data.dict()
                })
        
        return created_ids, errors
