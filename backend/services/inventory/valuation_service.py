"""
Inventory Valuation Service
Business logic for inventory valuation
"""

from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from uuid import UUID
import uuid

from backend.shared.database.inventory_models import (
    InventoryValuation, InventoryValuationItem, ItemMaster,
    ItemType, ValuationMethod
)
from backend.services.inventory import schemas


class InventoryValuationService:
    """Service for inventory valuation operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_valuation_number(self) -> str:
        """Generate unique valuation number"""
        query = select(func.count(InventoryValuation.id)).where(
            and_(
                InventoryValuation.tenant_id == self.tenant_id,
                InventoryValuation.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return f"VAL-{(count + 1):06d}"
    
    async def create_valuation(
        self, 
        valuation_data: schemas.InventoryValuationCreate
    ) -> InventoryValuation:
        """Create inventory valuation"""
        # Generate valuation number
        valuation_number = await self.generate_valuation_number()
        
        # Create valuation header
        valuation = InventoryValuation(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            valuation_number=valuation_number,
            valuation_date=valuation_data.valuation_date,
            financial_year=valuation_data.financial_year,
            financial_period=valuation_data.financial_period,
            warehouse=valuation_data.warehouse,
            item_category=valuation_data.item_category,
            item_type=valuation_data.item_type,
            valuation_method=valuation_data.valuation_method,
            remarks=valuation_data.remarks,
            total_items=0,
            total_quantity=Decimal("0.000"),
            total_value=Decimal("0.00"),
            raw_material_value=Decimal("0.00"),
            finished_goods_value=Decimal("0.00"),
            wip_value=Decimal("0.00"),
            consumables_value=Decimal("0.00"),
            other_value=Decimal("0.00"),
            is_finalized=False,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(valuation)
        await self.db.flush()
        
        # Build query for items to include
        items_query = select(ItemMaster).where(
            and_(
                ItemMaster.tenant_id == self.tenant_id,
                ItemMaster.is_deleted == False,
                ItemMaster.current_stock > 0
            )
        )
        
        # Apply filters
        if valuation_data.warehouse:
            items_query = items_query.where(ItemMaster.warehouse_location == valuation_data.warehouse)
        if valuation_data.item_category:
            items_query = items_query.where(ItemMaster.category == valuation_data.item_category)
        if valuation_data.item_type:
            items_query = items_query.where(ItemMaster.item_type == valuation_data.item_type)
        
        items_result = await self.db.execute(items_query)
        items = items_result.scalars().all()
        
        # Create valuation items
        total_items = 0
        total_quantity = Decimal("0.000")
        total_value = Decimal("0.00")
        raw_material_value = Decimal("0.00")
        finished_goods_value = Decimal("0.00")
        wip_value = Decimal("0.00")
        consumables_value = Decimal("0.00")
        other_value = Decimal("0.00")
        
        for item in items:
            # Determine rate based on valuation method
            if valuation_data.valuation_method == ValuationMethod.WEIGHTED_AVERAGE:
                rate = item.average_cost
            elif valuation_data.valuation_method == ValuationMethod.STANDARD_COST:
                rate = item.standard_cost
            else:
                rate = item.average_cost
            
            item_value = item.current_stock * rate
            
            valuation_item = InventoryValuationItem(
                id=uuid.uuid4(),
                valuation_id=valuation.id,
                item_id=item.id,
                item_code=item.item_code,
                item_name=item.item_name,
                item_type=item.item_type,
                quantity=item.current_stock,
                unit=item.base_unit,
                rate=rate,
                value=item_value,
                valuation_method=valuation_data.valuation_method,
                warehouse=item.warehouse_location,
                location=item.rack_number
            )
            self.db.add(valuation_item)
            
            # Accumulate totals
            total_items += 1
            total_quantity += item.current_stock
            total_value += item_value
            
            # Categorize by type
            if item.item_type == ItemType.RAW_MATERIAL:
                raw_material_value += item_value
            elif item.item_type == ItemType.FINISHED_GOODS:
                finished_goods_value += item_value
            elif item.item_type == ItemType.WORK_IN_PROGRESS:
                wip_value += item_value
            elif item.item_type == ItemType.CONSUMABLES:
                consumables_value += item_value
            else:
                other_value += item_value
        
        # Update valuation summary
        valuation.total_items = total_items
        valuation.total_quantity = total_quantity
        valuation.total_value = total_value
        valuation.raw_material_value = raw_material_value
        valuation.finished_goods_value = finished_goods_value
        valuation.wip_value = wip_value
        valuation.consumables_value = consumables_value
        valuation.other_value = other_value
        
        await self.db.commit()
        await self.db.refresh(valuation)
        
        return valuation
    
    async def get_valuation(self, valuation_id: UUID) -> Optional[InventoryValuation]:
        """Get valuation by ID"""
        result = await self.db.execute(
            select(InventoryValuation)
            .options(selectinload(InventoryValuation.items))
            .where(
                and_(
                    InventoryValuation.id == valuation_id,
                    InventoryValuation.tenant_id == self.tenant_id,
                    InventoryValuation.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_valuations(
        self,
        financial_year: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[InventoryValuation], int]:
        """List valuations with filters"""
        query = select(InventoryValuation).where(
            and_(
                InventoryValuation.tenant_id == self.tenant_id,
                InventoryValuation.is_deleted == False
            )
        )
        
        if financial_year:
            query = query.where(InventoryValuation.financial_year == financial_year)
        if from_date:
            query = query.where(InventoryValuation.valuation_date >= from_date)
        if to_date:
            query = query.where(InventoryValuation.valuation_date <= to_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get valuations with pagination
        query = query.order_by(InventoryValuation.valuation_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        valuations = result.scalars().all()
        
        return list(valuations), total
    
    async def finalize_valuation(self, valuation_id: UUID) -> InventoryValuation:
        """Finalize valuation"""
        valuation = await self.get_valuation(valuation_id)
        if not valuation:
            raise ValueError("Valuation not found")
        
        if valuation.is_finalized:
            raise ValueError("Valuation already finalized")
        
        valuation.is_finalized = True
        valuation.finalized_by = self.user_id
        valuation.finalized_at = datetime.utcnow()
        valuation.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(valuation)
        
        return valuation
    
    async def get_valuation_summary(self, financial_year: int) -> dict:
        """Get valuation summary for a financial year"""
        query = select(InventoryValuation).where(
            and_(
                InventoryValuation.tenant_id == self.tenant_id,
                InventoryValuation.financial_year == financial_year,
                InventoryValuation.is_finalized == True,
                InventoryValuation.is_deleted == False
            )
        ).order_by(InventoryValuation.valuation_date.desc())
        
        result = await self.db.execute(query)
        valuations = result.scalars().all()
        
        if not valuations:
            return {
                "financial_year": financial_year,
                "total_valuations": 0,
                "latest_valuation": None
            }
        
        latest = valuations[0]
        
        return {
            "financial_year": financial_year,
            "total_valuations": len(valuations),
            "latest_valuation": {
                "valuation_date": latest.valuation_date,
                "total_value": float(latest.total_value),
                "raw_material_value": float(latest.raw_material_value),
                "finished_goods_value": float(latest.finished_goods_value),
                "wip_value": float(latest.wip_value),
                "consumables_value": float(latest.consumables_value)
            }
        }
