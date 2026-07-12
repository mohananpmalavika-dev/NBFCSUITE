"""
Item Master Service
Business logic for item management
"""

from typing import Optional, List, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from uuid import UUID
import uuid

from backend.shared.database.inventory_models import (
    ItemMaster, ItemType, ItemStatus, UnitOfMeasure
)
from backend.services.inventory import schemas


class ItemMasterService:
    """Service for item master operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_item_code(self) -> str:
        """Generate unique item code"""
        # Get count of items
        query = select(func.count(ItemMaster.id)).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        # Generate code: ITM-XXXX
        return f"ITM-{(count + 1):04d}"
    
    async def create_item(self, item_data: schemas.ItemMasterCreate) -> ItemMaster:
        """Create new item"""
        # Check if item code already exists
        existing = await self.db.execute(
            select(ItemMaster).where(
                and_(
                    ItemMaster.tenant_id == self.tenant_id,
                    ItemMaster.item_code == item_data.item_code,
                    ItemMaster.is_deleted == False
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Item code {item_data.item_code} already exists")
        
        # Check barcode uniqueness if provided
        if item_data.barcode:
            existing_barcode = await self.db.execute(
                select(ItemMaster).where(
                    and_(
                        ItemMaster.tenant_id == self.tenant_id,
                        ItemMaster.barcode == item_data.barcode,
                        ItemMaster.is_deleted == False
                    )
                )
            )
            if existing_barcode.scalar_one_or_none():
                raise ValueError(f"Barcode {item_data.barcode} already exists")
        
        # Create item
        item = ItemMaster(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            **item_data.model_dump(),
            current_stock=Decimal("0.000"),
            reserved_stock=Decimal("0.000"),
            available_stock=Decimal("0.000"),
            average_cost=Decimal("0.00"),
            last_purchase_price=Decimal("0.00"),
            total_value=Decimal("0.00"),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def get_item(self, item_id: UUID) -> Optional[ItemMaster]:
        """Get item by ID"""
        result = await self.db.execute(
            select(ItemMaster).where(
                and_(
                    ItemMaster.id == item_id,
                    ItemMaster.tenant_id == self.tenant_id,
                    ItemMaster.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_item_by_code(self, item_code: str) -> Optional[ItemMaster]:
        """Get item by code"""
        result = await self.db.execute(
            select(ItemMaster).where(
                and_(
                    ItemMaster.item_code == item_code,
                    ItemMaster.tenant_id == self.tenant_id,
                    ItemMaster.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_items(
        self,
        item_type: Optional[ItemType] = None,
        item_status: Optional[ItemStatus] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ItemMaster], int]:
        """List items with filters"""
        query = select(ItemMaster).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False
            )
        )
        
        # Apply filters
        if item_type:
            query = query.where(ItemMaster.item_type == item_type)
        if item_status:
            query = query.where(ItemMaster.item_status == item_status)
        if category:
            query = query.where(ItemMaster.category == category)
        if search:
            search_filter = or_(
                ItemMaster.item_code.ilike(f"%{search}%"),
                ItemMaster.item_name.ilike(f"%{search}%"),
                ItemMaster.barcode.ilike(f"%{search}%"),
                ItemMaster.sku.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        if low_stock_only:
            query = query.where(ItemMaster.current_stock <= ItemMaster.reorder_level)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get items with pagination
        query = query.order_by(ItemMaster.item_code).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total
    
    async def update_item(
        self, 
        item_id: UUID, 
        item_data: schemas.ItemMasterUpdate
    ) -> ItemMaster:
        """Update item"""
        item = await self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        
        # Check barcode uniqueness if changed
        if item_data.barcode and item_data.barcode != item.barcode:
            existing = await self.db.execute(
                select(ItemMaster).where(
                    and_(
                        ItemMaster.tenant_id == self.tenant_id,
                        ItemMaster.barcode == item_data.barcode,
                        ItemMaster.id != item_id,
                        ItemMaster.is_deleted == False
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Barcode {item_data.barcode} already exists")
        
        # Update fields
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_by = self.user_id
        item.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def delete_item(self, item_id: UUID) -> None:
        """Soft delete item"""
        item = await self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        
        # Check if item has stock
        if item.current_stock > 0:
            raise ValueError("Cannot delete item with existing stock")
        
        item.is_deleted = True
        item.updated_by = self.user_id
        item.updated_at = datetime.utcnow()
        
        await self.db.commit()
    
    async def update_stock(
        self, 
        item_id: UUID, 
        quantity_change: Decimal,
        value_change: Decimal
    ) -> ItemMaster:
        """Update item stock (called by transaction service)"""
        item = await self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        
        # Update stock
        item.current_stock += quantity_change
        item.available_stock = item.current_stock - item.reserved_stock
        
        # Update value
        item.total_value += value_change
        
        # Update average cost
        if item.current_stock > 0:
            item.average_cost = item.total_value / item.current_stock
        else:
            item.average_cost = Decimal("0.00")
        
        item.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def get_low_stock_items(self) -> List[ItemMaster]:
        """Get items below reorder level"""
        result = await self.db.execute(
            select(ItemMaster).where(
                and_(
                    ItemMaster.tenant_id == self.tenant_id,
                    ItemMaster.is_deleted == False,
                    ItemMaster.item_status == ItemStatus.ACTIVE,
                    ItemMaster.current_stock <= ItemMaster.reorder_level
                )
            ).order_by(ItemMaster.item_code)
        )
        return list(result.scalars().all())
    
    async def get_stock_summary(self) -> dict:
        """Get stock summary statistics"""
        # Total items
        total_query = select(func.count(ItemMaster.id)).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_items = total_result.scalar() or 0
        
        # Active items
        active_query = select(func.count(ItemMaster.id)).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False,
                ItemMaster.item_status == ItemStatus.ACTIVE
            )
        )
        active_result = await self.db.execute(active_query)
        active_items = active_result.scalar() or 0
        
        # Total value
        value_query = select(func.sum(ItemMaster.total_value)).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False
            )
        )
        value_result = await self.db.execute(value_query)
        total_value = value_result.scalar() or Decimal("0.00")
        
        # Low stock items
        low_stock_query = select(func.count(ItemMaster.id)).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False,
                ItemMaster.item_status == ItemStatus.ACTIVE,
                ItemMaster.current_stock <= ItemMaster.reorder_level,
                ItemMaster.current_stock > 0
            )
        )
        low_stock_result = await self.db.execute(low_stock_query)
        low_stock_items = low_stock_result.scalar() or 0
        
        # Out of stock items
        out_of_stock_query = select(func.count(ItemMaster.id)).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False,
                ItemMaster.item_status == ItemStatus.ACTIVE,
                ItemMaster.current_stock == 0
            )
        )
        out_of_stock_result = await self.db.execute(out_of_stock_query)
        out_of_stock_items = out_of_stock_result.scalar() or 0
        
        return {
            "total_items": total_items,
            "active_items": active_items,
            "total_stock_value": float(total_value),
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items
        }
