"""
Cafeteria Management API Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.schemas import SuccessResponse, PaginatedResponse
from .cafeteria_service import CafeteriaService
from .schemas import (
    MenuItemCreate, MenuItemResponse,
    CafeteriaOrderCreate, CafeteriaOrderResponse,
    OrderStatusUpdate
)

router = APIRouter(prefix="/facility/cafeteria", tags=["Facility - Cafeteria"])


# ============================================================================
# MENU ENDPOINTS
# ============================================================================

@router.post("/menu", response_model=SuccessResponse[MenuItemResponse])
async def create_menu_item(
    menu_item: MenuItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new menu item"""
    result = await CafeteriaService.create_menu_item(
        db, tenant_id, menu_item.dict(), current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/menu", response_model=SuccessResponse[PaginatedResponse[MenuItemResponse]])
async def list_menu_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    meal_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List menu items with filters"""
    items, total = await CafeteriaService.list_menu_items(
        db, tenant_id, meal_type, is_available, skip, limit
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    )


# ============================================================================
# ORDER ENDPOINTS
# ============================================================================

@router.post("/orders", response_model=SuccessResponse[CafeteriaOrderResponse])
async def create_order(
    order: CafeteriaOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new cafeteria order"""
    order_data = order.dict(exclude={"items"})
    order_items = [item.dict() for item in order.items]
    
    result = await CafeteriaService.create_order(
        db, tenant_id, order_data, order_items, current_user["id"]
    )
    return SuccessResponse(data=result)


@router.get("/orders", response_model=SuccessResponse[PaginatedResponse[CafeteriaOrderResponse]])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    employee_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id)
):
    """List orders with filters"""
    orders, total = await CafeteriaService.list_orders(
        db, tenant_id, skip, limit, status, employee_id, from_date, to_date
    )
    return SuccessResponse(
        data=PaginatedResponse(
            items=orders,
            total=total,
            skip=skip,
            limit=limit
        )
    )


@router.patch("/orders/{order_id}/status", response_model=SuccessResponse[CafeteriaOrderResponse])
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update order status"""
    result = await CafeteriaService.update_order_status(
        db, tenant_id, order_id, status_update.status, current_user["id"]
    )
    return SuccessResponse(data=result)
