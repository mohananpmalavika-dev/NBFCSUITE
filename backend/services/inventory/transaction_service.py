"""
Stock Transaction Service
Business logic for stock movements
"""

from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from uuid import UUID
import uuid

from backend.shared.database.inventory_models import (
    StockTransaction, StockLedger, ItemMaster,
    TransactionType, TransactionStatus, ValuationMethod
)
from backend.services.inventory import schemas
from backend.services.inventory.item_service import ItemMasterService


class StockTransactionService:
    """Service for stock transaction operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.item_service = ItemMasterService(db, tenant_id, user_id)
    
    async def generate_transaction_number(self, transaction_type: TransactionType) -> str:
        """Generate unique transaction number"""
        # Prefix based on type
        prefix_map = {
            TransactionType.PURCHASE_RECEIPT: "PR",
            TransactionType.SALES_ISSUE: "SI",
            TransactionType.STOCK_TRANSFER_IN: "STI",
            TransactionType.STOCK_TRANSFER_OUT: "STO",
            TransactionType.STOCK_ADJUSTMENT_IN: "SAI",
            TransactionType.STOCK_ADJUSTMENT_OUT: "SAO",
            TransactionType.OPENING_STOCK: "OS",
        }
        prefix = prefix_map.get(transaction_type, "TXN")
        
        # Get count
        query = select(func.count(StockTransaction.id)).where(
            and_(
                StockTransaction.tenant_id == self.tenant_id,
                StockTransaction.transaction_type == transaction_type,
                StockTransaction.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return f"{prefix}-{(count + 1):06d}"
    
    def _is_inward_transaction(self, transaction_type: TransactionType) -> bool:
        """Check if transaction increases stock"""
        inward_types = [
            TransactionType.PURCHASE_RECEIPT,
            TransactionType.STOCK_TRANSFER_IN,
            TransactionType.STOCK_ADJUSTMENT_IN,
            TransactionType.PRODUCTION_RECEIPT,
            TransactionType.RETURN_FROM_CUSTOMER,
            TransactionType.OPENING_STOCK
        ]
        return transaction_type in inward_types
    
    async def create_transaction(
        self, 
        txn_data: schemas.StockTransactionCreate
    ) -> StockTransaction:
        """Create stock transaction"""
        # Get item
        item = await self.item_service.get_item(txn_data.item_id)
        if not item:
            raise ValueError("Item not found")
        
        # Check if outward transaction has sufficient stock
        if not self._is_inward_transaction(txn_data.transaction_type):
            if item.available_stock < txn_data.quantity:
                raise ValueError(f"Insufficient stock. Available: {item.available_stock}")
        
        # Generate transaction number
        txn_number = await self.generate_transaction_number(txn_data.transaction_type)
        
        # Calculate amount
        amount = txn_data.quantity * txn_data.rate
        
        # Create transaction
        transaction = StockTransaction(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            transaction_number=txn_number,
            **txn_data.model_dump(),
            amount=amount,
            transaction_status=TransactionStatus.DRAFT,
            is_posted=False,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def get_transaction(self, txn_id: UUID) -> Optional[StockTransaction]:
        """Get transaction by ID"""
        result = await self.db.execute(
            select(StockTransaction).where(
                and_(
                    StockTransaction.id == txn_id,
                    StockTransaction.tenant_id == self.tenant_id,
                    StockTransaction.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_transactions(
        self,
        transaction_type: Optional[TransactionType] = None,
        transaction_status: Optional[TransactionStatus] = None,
        item_id: Optional[UUID] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[StockTransaction], int]:
        """List transactions with filters"""
        query = select(StockTransaction).where(
            and_(
                StockTransaction.tenant_id == self.tenant_id,
                StockTransaction.is_deleted == False
            )
        )
        
        # Apply filters
        if transaction_type:
            query = query.where(StockTransaction.transaction_type == transaction_type)
        if transaction_status:
            query = query.where(StockTransaction.transaction_status == transaction_status)
        if item_id:
            query = query.where(StockTransaction.item_id == item_id)
        if from_date:
            query = query.where(StockTransaction.transaction_date >= from_date)
        if to_date:
            query = query.where(StockTransaction.transaction_date <= to_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get transactions with pagination
        query = query.order_by(StockTransaction.transaction_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        transactions = result.scalars().all()
        
        return list(transactions), total
    
    async def approve_transaction(self, txn_id: UUID) -> StockTransaction:
        """Approve transaction"""
        transaction = await self.get_transaction(txn_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        if transaction.transaction_status != TransactionStatus.SUBMITTED:
            raise ValueError("Transaction must be in SUBMITTED status to approve")
        
        transaction.transaction_status = TransactionStatus.APPROVED
        transaction.approved_by = self.user_id
        transaction.approved_at = datetime.utcnow()
        transaction.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def post_transaction(self, txn_id: UUID) -> StockTransaction:
        """Post transaction to update stock"""
        transaction = await self.get_transaction(txn_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        if transaction.is_posted:
            raise ValueError("Transaction already posted")
        
        if transaction.transaction_status != TransactionStatus.APPROVED:
            raise ValueError("Transaction must be APPROVED before posting")
        
        # Get item
        item = await self.item_service.get_item(transaction.item_id)
        if not item:
            raise ValueError("Item not found")
        
        # Determine quantity change (+ for inward, - for outward)
        is_inward = self._is_inward_transaction(transaction.transaction_type)
        quantity_change = transaction.quantity if is_inward else -transaction.quantity
        value_change = transaction.amount if is_inward else -transaction.amount
        
        # Get opening balance
        opening_quantity = item.current_stock
        opening_value = item.total_value
        
        # Update item stock
        await self.item_service.update_stock(item.id, quantity_change, value_change)
        
        # Refresh item to get updated values
        await self.db.refresh(item)
        
        # Create ledger entry
        ledger_entry = StockLedger(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            item_id=item.id,
            transaction_id=transaction.id,
            transaction_date=transaction.transaction_date,
            opening_quantity=opening_quantity,
            opening_value=opening_value,
            in_quantity=transaction.quantity if is_inward else Decimal("0.000"),
            out_quantity=transaction.quantity if not is_inward else Decimal("0.000"),
            in_value=transaction.amount if is_inward else Decimal("0.00"),
            out_value=transaction.amount if not is_inward else Decimal("0.00"),
            closing_quantity=item.current_stock,
            closing_value=item.total_value,
            rate=transaction.rate,
            warehouse=transaction.to_warehouse if is_inward else transaction.from_warehouse,
            location=transaction.to_location if is_inward else transaction.from_location,
            batch_number=transaction.batch_number,
            serial_number=transaction.serial_number,
            valuation_method=item.valuation_method,
            created_by=self.user_id
        )
        
        self.db.add(ledger_entry)
        
        # Update transaction
        transaction.is_posted = True
        transaction.posted_by = self.user_id
        transaction.posted_at = datetime.utcnow()
        transaction.transaction_status = TransactionStatus.POSTED
        transaction.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def cancel_transaction(self, txn_id: UUID, reason: str) -> StockTransaction:
        """Cancel transaction"""
        transaction = await self.get_transaction(txn_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        if transaction.is_posted:
            raise ValueError("Cannot cancel posted transaction. Create reversal instead.")
        
        transaction.transaction_status = TransactionStatus.CANCELLED
        transaction.rejection_reason = reason
        transaction.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def get_stock_ledger(
        self, 
        item_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[StockLedger]:
        """Get stock ledger for an item"""
        query = select(StockLedger).where(
            and_(
                StockLedger.tenant_id == self.tenant_id,
                StockLedger.item_id == item_id
            )
        )
        
        if from_date:
            query = query.where(StockLedger.transaction_date >= from_date)
        if to_date:
            query = query.where(StockLedger.transaction_date <= to_date)
        
        query = query.order_by(StockLedger.transaction_date)
        result = await self.db.execute(query)
        
        return list(result.scalars().all())
