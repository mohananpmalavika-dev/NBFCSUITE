"""
CRM Sales Automation Models
Product Catalog, Quote Generation, Order Management
"""

from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, Index, Enum as SQLEnum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class ProductCategory(str, enum.Enum):
    """Product category enumeration"""
    GOODS = "goods"
    SERVICES = "services"
    SOFTWARE = "software"
    SUBSCRIPTION = "subscription"
    CONSULTING = "consulting"
    OTHER = "other"


class ProductStatus(str, enum.Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"


class QuoteStatus(str, enum.Enum):
    """Quote status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    OVERDUE = "overdue"


class TaxType(str, enum.Enum):
    """Tax type enumeration"""
    GST = "gst"
    CGST_SGST = "cgst_sgst"
    IGST = "igst"
    VAT = "vat"
    NONE = "none"


# ============================================================================
# PRODUCT MODEL
# ============================================================================

class Product(BaseModel):
    """
    Product Catalog Model
    Manages products and services for quotes and orders
    """
    __tablename__ = "crm_products"
    
    # Basic Information
    product_code = Column(String(50), nullable=False, index=True)
    product_name = Column(String(200), nullable=False, index=True)
    product_category = Column(SQLEnum(ProductCategory), nullable=False, default=ProductCategory.GOODS)
    status = Column(SQLEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE, index=True)
    
    # Description
    short_description = Column(String(500))
    detailed_description = Column(Text)
    
    # Pricing
    unit_price = Column(Numeric(15, 2), nullable=False)
    cost_price = Column(Numeric(15, 2))
    currency = Column(String(3), default="INR")
    
    # Tax
    tax_type = Column(SQLEnum(TaxType), default=TaxType.GST)
    tax_rate = Column(Numeric(5, 2), default=18.00)  # Percentage
    hsn_code = Column(String(20))  # HSN/SAC code for GST
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer)
    unit_of_measure = Column(String(20), default="Unit")  # Unit, Kg, Liter, Hour, etc.
    
    # Additional Information
    manufacturer = Column(String(200))
    brand = Column(String(200))
    model_number = Column(String(100))
    barcode = Column(String(100))
    sku = Column(String(100))
    
    # Images and Documents
    image_url = Column(String(500))
    specification_url = Column(String(500))
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    
    # Status Flags
    is_taxable = Column(String(10), default="yes")
    is_discountable = Column(String(10), default="yes")
    is_returnable = Column(String(10), default="yes")
    
    # Relationships
    quote_items = relationship("QuoteItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_tenant_product_code', 'tenant_id', 'product_code', unique=True),
        Index('idx_product_category', 'tenant_id', 'product_category'),
        Index('idx_product_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, code={self.product_code}, name={self.product_name})>"


# ============================================================================
# QUOTE MODEL
# ============================================================================

class Quote(BaseModel):
    """
    Sales Quote Model
    Manages price quotations for customers
    """
    __tablename__ = "crm_quotes"
    
    # Basic Information
    quote_number = Column(String(50), nullable=False, index=True)
    quote_title = Column(String(200), nullable=False)
    status = Column(SQLEnum(QuoteStatus), nullable=False, default=QuoteStatus.DRAFT, index=True)
    
    # Customer Information
    account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey('crm_contacts.id'), index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey('crm_opportunities.id'), index=True)
    
    # Dates
    quote_date = Column(Date, nullable=False, index=True)
    valid_until = Column(Date, nullable=False)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    shipping_charges = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Currency
    currency = Column(String(3), default="INR")
    
    # Terms & Conditions
    payment_terms = Column(Text)
    delivery_terms = Column(Text)
    terms_and_conditions = Column(Text)
    notes = Column(Text)
    
    # Shipping Address
    shipping_address_line1 = Column(String(200))
    shipping_address_line2 = Column(String(200))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_pincode = Column(String(10))
    shipping_country = Column(String(100), default="India")
    
    # Tracking
    viewed_count = Column(Integer, default=0)
    viewed_date = Column(Date)
    accepted_date = Column(Date)
    rejected_date = Column(Date)
    rejection_reason = Column(Text)
    
    # Owner
    quote_owner_id = Column(UUID(as_uuid=True), index=True)
    
    # Relationships
    account = relationship("CRMAccount", foreign_keys=[account_id])
    contact = relationship("CRMContact", foreign_keys=[contact_id])
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="quote")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_tenant_quote_number', 'tenant_id', 'quote_number', unique=True),
        Index('idx_quote_account', 'tenant_id', 'account_id'),
        Index('idx_quote_status', 'tenant_id', 'status'),
        Index('idx_quote_date', 'tenant_id', 'quote_date'),
    )
    
    def __repr__(self):
        return f"<Quote(id={self.id}, number={self.quote_number}, status={self.status})>"


# ============================================================================
# QUOTE ITEM MODEL
# ============================================================================

class QuoteItem(BaseModel):
    """
    Quote Line Items Model
    Individual products/services in a quote
    """
    __tablename__ = "crm_quote_items"
    
    # Quote Reference
    quote_id = Column(UUID(as_uuid=True), ForeignKey('crm_quotes.id'), nullable=False, index=True)
    
    # Product Reference
    product_id = Column(UUID(as_uuid=True), ForeignKey('crm_products.id'), nullable=False, index=True)
    
    # Line Item Details
    line_number = Column(Integer, nullable=False)
    product_name = Column(String(200), nullable=False)  # Snapshot of product name
    description = Column(Text)
    
    # Quantity and Pricing
    quantity = Column(Numeric(10, 2), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    unit_of_measure = Column(String(20), default="Unit")
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    
    # Tax
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Calculated Amounts
    line_total = Column(Numeric(15, 2), nullable=False)  # Before tax and discount
    net_amount = Column(Numeric(15, 2), nullable=False)  # After discount and tax
    
    # Relationships
    quote = relationship("Quote", back_populates="items")
    product = relationship("Product", back_populates="quote_items")
    
    __table_args__ = (
        Index('idx_quote_item_quote', 'quote_id', 'line_number'),
        Index('idx_quote_item_product', 'product_id'),
    )
    
    def __repr__(self):
        return f"<QuoteItem(id={self.id}, quote_id={self.quote_id}, product={self.product_name})>"


# ============================================================================
# ORDER MODEL
# ============================================================================

class Order(BaseModel):
    """
    Sales Order Model
    Manages customer orders
    """
    __tablename__ = "crm_orders"
    
    # Basic Information
    order_number = Column(String(50), nullable=False, index=True)
    order_status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True)
    payment_status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.UNPAID, index=True)
    
    # Customer Information
    account_id = Column(UUID(as_uuid=True), ForeignKey('crm_accounts.id'), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey('crm_contacts.id'), index=True)
    quote_id = Column(UUID(as_uuid=True), ForeignKey('crm_quotes.id'), index=True)
    
    # Dates
    order_date = Column(Date, nullable=False, index=True)
    expected_delivery_date = Column(Date)
    actual_delivery_date = Column(Date)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    shipping_charges = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0)
    balance_amount = Column(Numeric(15, 2), default=0)
    
    # Currency
    currency = Column(String(3), default="INR")
    
    # Shipping Information
    shipping_address_line1 = Column(String(200))
    shipping_address_line2 = Column(String(200))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_pincode = Column(String(10))
    shipping_country = Column(String(100), default="India")
    
    shipping_method = Column(String(100))
    tracking_number = Column(String(100))
    carrier = Column(String(100))
    
    # Billing Information
    billing_address_line1 = Column(String(200))
    billing_address_line2 = Column(String(200))
    billing_city = Column(String(100))
    billing_state = Column(String(100))
    billing_pincode = Column(String(10))
    billing_country = Column(String(100), default="India")
    
    # Terms
    payment_terms = Column(Text)
    delivery_terms = Column(Text)
    notes = Column(Text)
    internal_notes = Column(Text)
    
    # Owner
    order_owner_id = Column(UUID(as_uuid=True), index=True)
    
    # Fulfillment
    is_fulfilled = Column(String(10), default="no")
    fulfilled_date = Column(Date)
    
    # Cancellation
    cancellation_reason = Column(Text)
    cancelled_date = Column(Date)
    
    # Relationships
    account = relationship("CRMAccount", foreign_keys=[account_id])
    contact = relationship("CRMContact", foreign_keys=[contact_id])
    quote = relationship("Quote", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    # Unique constraint
    __table_args__ = (
        Index('idx_tenant_order_number', 'tenant_id', 'order_number', unique=True),
        Index('idx_order_account', 'tenant_id', 'account_id'),
        Index('idx_order_status', 'tenant_id', 'order_status'),
        Index('idx_order_payment_status', 'tenant_id', 'payment_status'),
        Index('idx_order_date', 'tenant_id', 'order_date'),
    )
    
    def __repr__(self):
        return f"<Order(id={self.id}, number={self.order_number}, status={self.order_status})>"


# ============================================================================
# ORDER ITEM MODEL
# ============================================================================

class OrderItem(BaseModel):
    """
    Order Line Items Model
    Individual products/services in an order
    """
    __tablename__ = "crm_order_items"
    
    # Order Reference
    order_id = Column(UUID(as_uuid=True), ForeignKey('crm_orders.id'), nullable=False, index=True)
    
    # Product Reference
    product_id = Column(UUID(as_uuid=True), ForeignKey('crm_products.id'), nullable=False, index=True)
    
    # Line Item Details
    line_number = Column(Integer, nullable=False)
    product_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Quantity and Pricing
    quantity = Column(Numeric(10, 2), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)
    unit_of_measure = Column(String(20), default="Unit")
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    
    # Tax
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    
    # Calculated Amounts
    line_total = Column(Numeric(15, 2), nullable=False)
    net_amount = Column(Numeric(15, 2), nullable=False)
    
    # Fulfillment
    quantity_shipped = Column(Numeric(10, 2), default=0)
    quantity_delivered = Column(Numeric(10, 2), default=0)
    is_fulfilled = Column(String(10), default="no")
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    __table_args__ = (
        Index('idx_order_item_order', 'order_id', 'line_number'),
        Index('idx_order_item_product', 'product_id'),
    )
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product={self.product_name})>"
