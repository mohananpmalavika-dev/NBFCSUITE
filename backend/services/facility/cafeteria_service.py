"""
Cafeteria Management Service
Handles menu, orders, and cafeteria inventory management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date, time

from backend.shared.database.facility_models import (
    CafeteriaMenu, CafeteriaOrder, CafeteriaOrderItem, CafeteriaInventory,
    MealTypeEnum, OrderStatusEnum
)
from backend.shared.exceptions import NotFoundError, ValidationError


class CafeteriaService:
    """Service for cafeteria operations"""
    
    # ============================================================================
    # MENU MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_menu_item(
        db: AsyncSession,
        tenant_id: str,
        menu_data: Dict[str, Any],
        user_id: int
    ) -> CafeteriaMenu:
        """Create a new menu item"""
        
        # Check if item code already exists
        stmt = select(CafeteriaMenu).where(
            and_(
                CafeteriaMenu.tenant_id == tenant_id,
                CafeteriaMenu.item_code == menu_data.get("item_code"),
                CafeteriaMenu.is_deleted == False
            )
        )
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValidationError("Menu item code already exists")
        
        menu_item = CafeteriaMenu(
            tenant_id=tenant_id,
            created_by=user_id,
            **menu_data
        )
        
        db.add(menu_item)
        await db.commit()
        await db.refresh(menu_item)
        
        return menu_item
    
    @staticmethod
    async def list_menu_items(
        db: AsyncSession,
        tenant_id: str,
        meal_type: Optional[str] = None,
        is_available: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[CafeteriaMenu], int]:
        """List menu items with filters"""
        
        query = select(CafeteriaMenu).where(
            and_(
                CafeteriaMenu.tenant_id == tenant_id,
                CafeteriaMenu.is_deleted == False
            )
        )
        
        if meal_type:
            query = query.where(CafeteriaMenu.meal_type == meal_type)
        
        if is_available is not None:
            query = query.where(CafeteriaMenu.is_available == is_available)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(CafeteriaMenu.item_name)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total_count
    
    # ============================================================================
    # ORDER MANAGEMENT
    # ============================================================================
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        tenant_id: str,
        order_data: Dict[str, Any],
        order_items: List[Dict[str, Any]],
        user_id: int
    ) -> CafeteriaOrder:
        """Create a new cafeteria order"""
        
        # Generate order number
        date_str = datetime.now().strftime("%Y%m%d")
        stmt = select(func.count()).select_from(CafeteriaOrder).where(
            CafeteriaOrder.tenant_id == tenant_id
        )
        result = await db.execute(stmt)
        count = result.scalar() + 1
        order_number = f"CAF{date_str}{count:04d}"
        
        # Calculate totals
        total_amount = 0
        
        # Create order
        order = CafeteriaOrder(
            tenant_id=tenant_id,
            order_number=order_number,
            order_time=datetime.now().time(),
            created_by=user_id,
            **order_data
        )
        
        db.add(order)
        await db.flush()  # Get order ID
        
        # Add order items
        for item_data in order_items:
            menu_item_id = item_data.get("menu_item_id")
            quantity = item_data.get("quantity", 1)
            
            # Get menu item
            menu_stmt = select(CafeteriaMenu).where(
                and_(
                    CafeteriaMenu.tenant_id == tenant_id,
                    CafeteriaMenu.id == menu_item_id,
                    CafeteriaMenu.is_deleted == False
                )
            )
            menu_result = await db.execute(menu_stmt)
            menu_item = menu_result.scalar_one_or_none()
            
            if not menu_item:
                raise NotFoundError(f"Menu item with ID {menu_item_id} not found")
            
            # Use employee price if available
            unit_price = menu_item.employee_price or menu_item.price
            total_price = unit_price * quantity
            total_amount += total_price
            
            order_item = CafeteriaOrderItem(
                tenant_id=tenant_id,
                order_id=order.id,
                menu_item_id=menu_item_id,
                item_name=menu_item.item_name,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                special_instructions=item_data.get("special_instructions")
            )
            
            db.add(order_item)
        
        # Update order totals
        order.total_amount = total_amount
        order.net_amount = total_amount - order.discount_amount
        
        await db.commit()
        await db.refresh(order)
        
        return order
    
    @staticmethod
    async def list_orders(
        db: AsyncSession,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        employee_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> tuple[List[CafeteriaOrder], int]:
        """List orders with filters"""
        
        query = select(CafeteriaOrder).where(
            and_(
                CafeteriaOrder.tenant_id == tenant_id,
                CafeteriaOrder.is_deleted == False
            )
        )
        
        if status:
            query = query.where(CafeteriaOrder.status == status)
        
        if employee_id:
            query = query.where(CafeteriaOrder.employee_id == employee_id)
        
        if from_date:
            query = query.where(CafeteriaOrder.order_date >= from_date)
        
        if to_date:
            query = query.where(CafeteriaOrder.order_date <= to_date)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(
            CafeteriaOrder.order_date.desc(),
            CafeteriaOrder.order_time.desc()
        )
        
        result = await db.execute(query)
        orders = result.scalars().all()
        
        return orders, total_count
    
    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        tenant_id: str,
        order_id: int,
        status: OrderStatusEnum,
        user_id: int
    ) -> CafeteriaOrder:
        """Update order status"""
        
        stmt = select(CafeteriaOrder).where(
            and_(
                CafeteriaOrder.tenant_id == tenant_id,
                CafeteriaOrder.id == order_id,
                CafeteriaOrder.is_deleted == False
            )
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise NotFoundError(f"Order with ID {order_id} not found")
        
        order.status = status
        order.updated_by = user_id
        order.updated_at = datetime.utcnow()
        
        if status == OrderStatusEnum.PREPARING and not order.preparation_started_at:
            order.preparation_started_at = datetime.utcnow()
        elif status == OrderStatusEnum.READY and not order.ready_at:
            order.ready_at = datetime.utcnow()
        elif status == OrderStatusEnum.SERVED and not order.served_at:
            order.served_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(order)
        
        return order
