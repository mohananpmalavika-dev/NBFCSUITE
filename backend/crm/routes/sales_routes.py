"""
CRM Sales Automation Routes
FastAPI endpoints for products, quotes, and orders
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.schemas.crm_sales_schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    QuoteCreate, QuoteUpdate, QuoteResponse,
    OrderCreate, OrderUpdate, OrderResponse
)
from backend.crm.services.sales_service import (
    ProductService, QuoteService, OrderService
)

# Create separate routers for better organization
product_router = APIRouter(prefix="/crm/products", tags=["CRM - Product Catalog"])
quote_router = APIRouter(prefix="/crm/quotes", tags=["CRM - Quote Generation"])
order_router = APIRouter(prefix="/crm/orders", tags=["CRM - Order Management"])


# ============================================================================
# PRODUCT ROUTES
# ============================================================================

@product_router.post("", response_model=dict, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new product in the catalog
    
    - **product_code**: Unique product code (required)
    - **product_name**: Product name (required)
    - **unit_price**: Product price (required)
    - **product_category**: goods, services, software, subscription, consulting, other
    - **status**: active, inactive, discontinued, out_of_stock
    """
    tenant_id = "default"
    user_id = None
    
    result = ProductService.create_product(db.sync_session, product_data, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to create product")
        )
    
    return result


@product_router.get("", response_model=dict)
async def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in product name, code, SKU, barcode"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all products with pagination and filters
    
    Supports:
    - Pagination with skip/limit
    - Search by name, code, SKU, barcode
    - Filter by category and status
    """
    tenant_id = "default"
    
    result = ProductService.list_products(
        db.sync_session, tenant_id, skip, limit, search, category, status
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to list products")
        )
    
    return result


@product_router.get("/{product_id}", response_model=dict)
async def get_product(
    product_id: UUID = Path(..., description="Product ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get product details by ID"""
    tenant_id = "default"
    
    result = ProductService.get_product(db.sync_session, product_id, tenant_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "PRODUCT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@product_router.put("/{product_id}", response_model=dict)
async def update_product(
    product_id: UUID = Path(..., description="Product ID"),
    product_data: ProductUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update product details"""
    tenant_id = "default"
    user_id = None
    
    result = ProductService.update_product(
        db.sync_session, product_id, product_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "PRODUCT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@product_router.delete("/{product_id}", response_model=dict)
async def delete_product(
    product_id: UUID = Path(..., description="Product ID"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a product (soft delete)"""
    tenant_id = "default"
    user_id = None
    
    result = ProductService.delete_product(db.sync_session, product_id, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "PRODUCT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


# ============================================================================
# QUOTE ROUTES
# ============================================================================

@quote_router.post("", response_model=dict, status_code=201)
async def create_quote(
    quote_data: QuoteCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new sales quote
    
    - **quote_title**: Title of the quote (required)
    - **account_id**: Customer account ID (required)
    - **quote_date**: Date of quotation (required)
    - **valid_until**: Quote validity date (required)
    - **items**: List of quote line items
    """
    tenant_id = "default"
    user_id = None
    
    result = QuoteService.create_quote(db.sync_session, quote_data, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to create quote")
        )
    
    return result


@quote_router.get("", response_model=dict)
async def list_quotes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in quote number, title"),
    status: Optional[str] = Query(None, description="Filter by status"),
    account_id: Optional[UUID] = Query(None, description="Filter by account"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all quotes with pagination and filters
    
    Supports:
    - Pagination with skip/limit
    - Search by number, title
    - Filter by status and account
    """
    tenant_id = "default"
    
    result = QuoteService.list_quotes(
        db.sync_session, tenant_id, skip, limit, search, status, account_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to list quotes")
        )
    
    return result


@quote_router.get("/{quote_id}", response_model=dict)
async def get_quote(
    quote_id: UUID = Path(..., description="Quote ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get quote details by ID with all line items"""
    tenant_id = "default"
    
    result = QuoteService.get_quote(db.sync_session, quote_id, tenant_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "QUOTE_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@quote_router.put("/{quote_id}", response_model=dict)
async def update_quote(
    quote_id: UUID = Path(..., description="Quote ID"),
    quote_data: QuoteUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """Update quote details"""
    tenant_id = "default"
    user_id = None
    
    result = QuoteService.update_quote(
        db.sync_session, quote_id, quote_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "QUOTE_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@quote_router.post("/{quote_id}/status", response_model=dict)
async def update_quote_status(
    quote_id: UUID = Path(..., description="Quote ID"),
    new_status: str = Query(..., description="New status: draft, sent, viewed, accepted, rejected, expired"),
    db: AsyncSession = Depends(get_db)
):
    """Update quote status"""
    tenant_id = "default"
    user_id = None
    
    result = QuoteService.update_quote_status(
        db.sync_session, quote_id, new_status, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "QUOTE_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


# ============================================================================
# ORDER ROUTES
# ============================================================================

@order_router.post("", response_model=dict, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new sales order
    
    - **account_id**: Customer account ID (required)
    - **order_date**: Date of order (required)
    - **items**: List of order line items
    """
    tenant_id = "default"
    user_id = None
    
    result = OrderService.create_order(db.sync_session, order_data, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to create order")
        )
    
    return result


@order_router.get("", response_model=dict)
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in order number"),
    order_status: Optional[str] = Query(None, description="Filter by order status"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    account_id: Optional[UUID] = Query(None, description="Filter by account"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all orders with pagination and filters
    
    Supports:
    - Pagination with skip/limit
    - Search by order number
    - Filter by order status, payment status, account
    """
    tenant_id = "default"
    
    result = OrderService.list_orders(
        db.sync_session, tenant_id, skip, limit, search, order_status, payment_status, account_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to list orders")
        )
    
    return result


@order_router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: UUID = Path(..., description="Order ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get order details by ID with all line items"""
    tenant_id = "default"
    
    result = OrderService.get_order(db.sync_session, order_id, tenant_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "ORDER_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@order_router.put("/{order_id}", response_model=dict)
async def update_order(
    order_id: UUID = Path(..., description="Order ID"),
    order_data: OrderUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """
    Update order details
    
    Can update:
    - Order status (pending, confirmed, processing, shipped, delivered, cancelled)
    - Payment status (unpaid, partial, paid, refunded)
    - Shipping details
    - Payment information
    """
    tenant_id = "default"
    user_id = None
    
    result = OrderService.update_order(
        db.sync_session, order_id, order_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "ORDER_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result
