"""
CRM Sales Automation Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class ProductBase(BaseModel):
    """Base Product schema"""
    model_config = ConfigDict(protected_namespaces=())
    
    product_code: str = Field(..., min_length=1, max_length=50)
    product_name: str = Field(..., min_length=1, max_length=200)
    product_category: str = Field(default="goods")
    status: str = Field(default="active")
    
    short_description: Optional[str] = Field(None, max_length=500)
    detailed_description: Optional[str] = None
    
    unit_price: Decimal = Field(..., ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="INR", max_length=3)
    
    tax_type: str = Field(default="gst")
    tax_rate: Decimal = Field(default=18.00, ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=20)
    
    stock_quantity: int = Field(default=0, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    unit_of_measure: str = Field(default="Unit", max_length=20)
    
    manufacturer: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = Field(None, max_length=200)
    model_number: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    
    image_url: Optional[str] = Field(None, max_length=500)
    specification_url: Optional[str] = Field(None, max_length=500)
    
    discount_percentage: Decimal = Field(default=0, ge=0, le=100)
    discount_amount: Decimal = Field(default=0, ge=0)
    
    is_taxable: str = Field(default="yes")
    is_discountable: str = Field(default="yes")
    is_returnable: str = Field(default="yes")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    product_code: Optional[str] = Field(None, min_length=1, max_length=50)
    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    product_category: Optional[str] = None
    status: Optional[str] = None
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    hsn_code: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = None
    unit_of_measure: Optional[str] = None
    manufacturer: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# QUOTE ITEM SCHEMAS
# ============================================================================

class QuoteItemBase(BaseModel):
    """Base Quote Item schema"""
    product_id: UUID
    line_number: int = Field(..., ge=1)
    product_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    unit_of_measure: str = Field(default="Unit", max_length=20)
    discount_percentage: Decimal = Field(default=0, ge=0, le=100)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_rate: Decimal = Field(default=0, ge=0, le=100)
    tax_amount: Decimal = Field(default=0, ge=0)
    line_total: Decimal = Field(..., ge=0)
    net_amount: Decimal = Field(..., ge=0)


class QuoteItemCreate(QuoteItemBase):
    """Schema for creating a quote item"""
    pass


class QuoteItemUpdate(BaseModel):
    """Schema for updating a quote item"""
    product_id: Optional[UUID] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None


class QuoteItemResponse(QuoteItemBase):
    """Schema for quote item response"""
    id: UUID
    quote_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# QUOTE SCHEMAS
# ============================================================================

class QuoteBase(BaseModel):
    """Base Quote schema"""
    quote_title: str = Field(..., min_length=1, max_length=200)
    account_id: UUID
    contact_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    
    quote_date: date
    valid_until: date
    
    subtotal: Decimal = Field(default=0, ge=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    shipping_charges: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="INR", max_length=3)
    
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    
    shipping_address_line1: Optional[str] = Field(None, max_length=200)
    shipping_address_line2: Optional[str] = Field(None, max_length=200)
    shipping_city: Optional[str] = Field(None, max_length=100)
    shipping_state: Optional[str] = Field(None, max_length=100)
    shipping_pincode: Optional[str] = Field(None, max_length=10)
    shipping_country: str = Field(default="India", max_length=100)


class QuoteCreate(QuoteBase):
    """Schema for creating a new quote"""
    items: List[QuoteItemCreate] = []


class QuoteUpdate(BaseModel):
    """Schema for updating a quote"""
    quote_title: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_id: Optional[UUID] = None
    valid_until: Optional[date] = None
    status: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    shipping_address_line1: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_pincode: Optional[str] = None


class QuoteResponse(QuoteBase):
    """Schema for quote response"""
    id: UUID
    quote_number: str
    status: str
    tenant_id: str
    viewed_count: int
    viewed_date: Optional[date] = None
    accepted_date: Optional[date] = None
    rejected_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    quote_owner_id: Optional[UUID] = None
    items: List[QuoteItemResponse] = []
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# ORDER ITEM SCHEMAS
# ============================================================================

class OrderItemBase(BaseModel):
    """Base Order Item schema"""
    product_id: UUID
    line_number: int = Field(..., ge=1)
    product_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    unit_of_measure: str = Field(default="Unit", max_length=20)
    discount_percentage: Decimal = Field(default=0, ge=0, le=100)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_rate: Decimal = Field(default=0, ge=0, le=100)
    tax_amount: Decimal = Field(default=0, ge=0)
    line_total: Decimal = Field(..., ge=0)
    net_amount: Decimal = Field(..., ge=0)
    quantity_shipped: Decimal = Field(default=0, ge=0)
    quantity_delivered: Decimal = Field(default=0, ge=0)
    is_fulfilled: str = Field(default="no")


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item"""
    pass


class OrderItemUpdate(BaseModel):
    """Schema for updating an order item"""
    quantity: Optional[Decimal] = Field(None, gt=0)
    quantity_shipped: Optional[Decimal] = Field(None, ge=0)
    quantity_delivered: Optional[Decimal] = Field(None, ge=0)
    is_fulfilled: Optional[str] = None


class OrderItemResponse(OrderItemBase):
    """Schema for order item response"""
    id: UUID
    order_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ORDER SCHEMAS
# ============================================================================

class OrderBase(BaseModel):
    """Base Order schema"""
    account_id: UUID
    contact_id: Optional[UUID] = None
    quote_id: Optional[UUID] = None
    
    order_date: date
    expected_delivery_date: Optional[date] = None
    
    subtotal: Decimal = Field(default=0, ge=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    shipping_charges: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)
    paid_amount: Decimal = Field(default=0, ge=0)
    balance_amount: Decimal = Field(default=0, ge=0)
    currency: str = Field(default="INR", max_length=3)
    
    shipping_address_line1: Optional[str] = Field(None, max_length=200)
    shipping_address_line2: Optional[str] = Field(None, max_length=200)
    shipping_city: Optional[str] = Field(None, max_length=100)
    shipping_state: Optional[str] = Field(None, max_length=100)
    shipping_pincode: Optional[str] = Field(None, max_length=10)
    shipping_country: str = Field(default="India", max_length=100)
    
    shipping_method: Optional[str] = Field(None, max_length=100)
    tracking_number: Optional[str] = Field(None, max_length=100)
    carrier: Optional[str] = Field(None, max_length=100)
    
    billing_address_line1: Optional[str] = Field(None, max_length=200)
    billing_city: Optional[str] = Field(None, max_length=100)
    billing_state: Optional[str] = Field(None, max_length=100)
    billing_pincode: Optional[str] = Field(None, max_length=10)
    billing_country: str = Field(default="India", max_length=100)
    
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating a new order"""
    items: List[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    is_fulfilled: Optional[str] = None
    cancellation_reason: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order response"""
    id: UUID
    order_number: str
    order_status: str
    payment_status: str
    tenant_id: str
    actual_delivery_date: Optional[date] = None
    is_fulfilled: str
    fulfilled_date: Optional[date] = None
    cancellation_reason: Optional[str] = None
    cancelled_date: Optional[date] = None
    order_owner_id: Optional[UUID] = None
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# LIST RESPONSE SCHEMAS
# ============================================================================

class PaginatedProductList(BaseModel):
    """Paginated product list response"""
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedQuoteList(BaseModel):
    """Paginated quote list response"""
    quotes: List[QuoteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedOrderList(BaseModel):
    """Paginated order list response"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
