"""
Inventory & Store Management Database Models
Item Master, Stock Transactions, Stock Verification, Inventory Valuation
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text,
    ForeignKey, Enum, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid

from backend.shared.database.connection import Base


# Enums
class ItemType(str, enum.Enum):
    """Types of inventory items"""
    RAW_MATERIAL = "raw_material"
    FINISHED_GOODS = "finished_goods"
    WORK_IN_PROGRESS = "work_in_progress"
    CONSUMABLES = "consumables"
    SPARE_PARTS = "spare_parts"
    TRADING_GOODS = "trading_goods"
    PACKING_MATERIAL = "packing_material"
    TOOLS = "tools"
    ASSETS = "assets"
    OTHER = "other"


class ItemStatus(str, enum.Enum):
    """Item master status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OBSOLETE = "obsolete"


class UnitOfMeasure(str, enum.Enum):
    """Standard units of measure"""
    PIECE = "piece"
    KG = "kg"
    GRAM = "gram"
    LITER = "liter"
    MILLILITER = "milliliter"
    METER = "meter"
    CENTIMETER = "centimeter"
    SQUARE_METER = "square_meter"
    CUBIC_METER = "cubic_meter"
    BOX = "box"
    CARTON = "carton"
    PALLET = "pallet"
    DOZEN = "dozen"
    PAIR = "pair"
    SET = "set"
    UNIT = "unit"


class TransactionType(str, enum.Enum):
    """Stock transaction types"""
    PURCHASE_RECEIPT = "purchase_receipt"
    SALES_ISSUE = "sales_issue"
    STOCK_TRANSFER_IN = "stock_transfer_in"
    STOCK_TRANSFER_OUT = "stock_transfer_out"
    STOCK_ADJUSTMENT_IN = "stock_adjustment_in"
    STOCK_ADJUSTMENT_OUT = "stock_adjustment_out"
    PRODUCTION_RECEIPT = "production_receipt"
    PRODUCTION_ISSUE = "production_issue"
    RETURN_FROM_CUSTOMER = "return_from_customer"
    RETURN_TO_SUPPLIER = "return_to_supplier"
    OPENING_STOCK = "opening_stock"
    PHYSICAL_VERIFICATION = "physical_verification"
    DAMAGE = "damage"
    WASTAGE = "wastage"
    THEFT = "theft"


class TransactionStatus(str, enum.Enum):
    """Transaction status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"
    CANCELLED = "cancelled"


class ValuationMethod(str, enum.Enum):
    """Inventory valuation methods"""
    FIFO = "fifo"  # First In First Out
    LIFO = "lifo"  # Last In First Out
    WEIGHTED_AVERAGE = "weighted_average"
    MOVING_AVERAGE = "moving_average"
    STANDARD_COST = "standard_cost"
    SPECIFIC_IDENTIFICATION = "specific_identification"


class VerificationStatus(str, enum.Enum):
    """Physical verification status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VARIANCE_FOUND = "variance_found"
    RECONCILED = "reconciled"
    CANCELLED = "cancelled"


# ============================================================================
# Item Master
# ============================================================================

class ItemMaster(Base):
    """
    Item Master - Central repository of inventory items
    """
    __tablename__ = "inventory_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Basic Information
    item_code = Column(String(50), nullable=False, unique=True, index=True)
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text, nullable=True)
    item_type = Column(Enum(ItemType), nullable=False)
    item_status = Column(Enum(ItemStatus), nullable=False, default=ItemStatus.ACTIVE)
    
    # Category & Classification
    category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    
    # Unit & Packaging
    base_unit = Column(Enum(UnitOfMeasure), nullable=False)
    alternate_unit = Column(Enum(UnitOfMeasure), nullable=True)
    conversion_factor = Column(Numeric(10, 4), default=1.0)  # Base to alternate
    
    # Barcode & SKU
    barcode = Column(String(100), nullable=True, unique=True)
    sku = Column(String(100), nullable=True, unique=True)
    hsn_code = Column(String(20), nullable=True)  # HSN/SAC for GST
    
    # Pricing
    standard_cost = Column(Numeric(15, 2), default=0.00)
    average_cost = Column(Numeric(15, 2), default=0.00)
    last_purchase_price = Column(Numeric(15, 2), default=0.00)
    selling_price = Column(Numeric(15, 2), default=0.00)
    
    # Stock Levels
    minimum_stock = Column(Numeric(15, 3), default=0.000)
    maximum_stock = Column(Numeric(15, 3), default=0.000)
    reorder_level = Column(Numeric(15, 3), default=0.000)
    reorder_quantity = Column(Numeric(15, 3), default=0.000)
    
    # Current Stock
    current_stock = Column(Numeric(15, 3), default=0.000)
    reserved_stock = Column(Numeric(15, 3), default=0.000)
    available_stock = Column(Numeric(15, 3), default=0.000)  # current - reserved
    
    # Valuation
    valuation_method = Column(Enum(ValuationMethod), nullable=False, default=ValuationMethod.WEIGHTED_AVERAGE)
    total_value = Column(Numeric(18, 2), default=0.00)
    
    # Storage
    warehouse_location = Column(String(100), nullable=True)
    rack_number = Column(String(50), nullable=True)
    bin_number = Column(String(50), nullable=True)
    
    # Supplier Information
    preferred_supplier_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    lead_time_days = Column(Integer, default=0)
    
    # Tax Information
    is_taxable = Column(Boolean, default=True)
    gst_rate = Column(Numeric(5, 2), default=0.00)
    
    # Tracking
    is_batch_tracked = Column(Boolean, default=False)
    is_serial_tracked = Column(Boolean, default=False)
    is_expiry_tracked = Column(Boolean, default=False)
    shelf_life_days = Column(Integer, nullable=True)
    
    # Additional Information
    specification = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    stock_transactions = relationship("StockTransaction", back_populates="item")
    stock_ledger = relationship("StockLedger", back_populates="item")
    verifications = relationship("StockVerificationItem", back_populates="item")
    
    __table_args__ = (
        Index("ix_item_tenant_code", "tenant_id", "item_code", unique=True),
        Index("ix_item_status", "item_status"),
        Index("ix_item_type", "item_type"),
    )



# ============================================================================
# Stock Transactions
# ============================================================================

class StockTransaction(Base):
    """
    Stock Transactions - All stock movements
    """
    __tablename__ = "stock_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Transaction Details
    transaction_number = Column(String(50), nullable=False, unique=True, index=True)
    transaction_date = Column(Date, nullable=False, default=date.today)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.DRAFT)
    
    # Item Reference
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    
    # Quantity
    quantity = Column(Numeric(15, 3), nullable=False)
    unit = Column(Enum(UnitOfMeasure), nullable=False)
    
    # Rate & Value
    rate = Column(Numeric(15, 2), default=0.00)
    amount = Column(Numeric(18, 2), default=0.00)
    
    # Location
    from_warehouse = Column(String(100), nullable=True)
    to_warehouse = Column(String(100), nullable=True)
    from_location = Column(String(100), nullable=True)
    to_location = Column(String(100), nullable=True)
    
    # Batch & Serial
    batch_number = Column(String(50), nullable=True)
    serial_number = Column(String(50), nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # Reference Documents
    reference_type = Column(String(50), nullable=True)  # PO, SO, GRN, etc.
    reference_number = Column(String(50), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Purpose & Notes
    purpose = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Posting
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime, nullable=True)
    posted_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    item = relationship("ItemMaster", back_populates="stock_transactions")
    
    __table_args__ = (
        Index("ix_stock_txn_tenant_number", "tenant_id", "transaction_number", unique=True),
        Index("ix_stock_txn_date", "transaction_date"),
        Index("ix_stock_txn_type", "transaction_type"),
        Index("ix_stock_txn_item", "item_id"),
    )


# ============================================================================
# Stock Ledger
# ============================================================================

class StockLedger(Base):
    """
    Stock Ledger - Running balance of stock
    """
    __tablename__ = "stock_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Item & Transaction Reference
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("stock_transactions.id"), nullable=True)
    transaction_date = Column(Date, nullable=False)
    
    # Opening Balance
    opening_quantity = Column(Numeric(15, 3), nullable=False, default=0.000)
    opening_value = Column(Numeric(18, 2), nullable=False, default=0.00)
    
    # Transaction
    in_quantity = Column(Numeric(15, 3), default=0.000)
    out_quantity = Column(Numeric(15, 3), default=0.000)
    in_value = Column(Numeric(18, 2), default=0.00)
    out_value = Column(Numeric(18, 2), default=0.00)
    
    # Closing Balance
    closing_quantity = Column(Numeric(15, 3), nullable=False)
    closing_value = Column(Numeric(18, 2), nullable=False)
    
    # Rate
    rate = Column(Numeric(15, 2), default=0.00)
    
    # Location
    warehouse = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Batch & Serial
    batch_number = Column(String(50), nullable=True)
    serial_number = Column(String(50), nullable=True)
    
    # Valuation Method Used
    valuation_method = Column(Enum(ValuationMethod), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    item = relationship("ItemMaster", back_populates="stock_ledger")
    
    __table_args__ = (
        Index("ix_stock_ledger_tenant_item", "tenant_id", "item_id"),
        Index("ix_stock_ledger_date", "transaction_date"),
    )


# ============================================================================
# Stock Verification
# ============================================================================

class StockVerification(Base):
    """
    Stock Verification Header - Physical verification campaigns
    """
    __tablename__ = "stock_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Verification Details
    verification_number = Column(String(50), nullable=False, unique=True, index=True)
    verification_date = Column(Date, nullable=False, default=date.today)
    verification_status = Column(Enum(VerificationStatus), nullable=False, default=VerificationStatus.PLANNED)
    
    # Schedule
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    
    # Scope
    warehouse = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    item_category = Column(String(100), nullable=True)
    
    # Team
    verification_team = Column(Text, nullable=True)  # JSON array of user IDs
    supervisor_id = Column(UUID(as_uuid=True), nullable=True)
    supervisor_name = Column(String(100), nullable=True)
    
    # Summary
    total_items = Column(Integer, default=0)
    items_verified = Column(Integer, default=0)
    items_with_variance = Column(Integer, default=0)
    total_variance_value = Column(Numeric(18, 2), default=0.00)
    
    # Notes
    purpose = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    items = relationship("StockVerificationItem", back_populates="verification", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_verification_tenant_number", "tenant_id", "verification_number", unique=True),
        Index("ix_verification_date", "verification_date"),
        Index("ix_verification_status", "verification_status"),
    )


class StockVerificationItem(Base):
    """
    Stock Verification Items - Line items for each verification
    """
    __tablename__ = "stock_verification_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("stock_verifications.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    
    # System Stock
    system_quantity = Column(Numeric(15, 3), nullable=False)
    system_rate = Column(Numeric(15, 2), default=0.00)
    system_value = Column(Numeric(18, 2), default=0.00)
    
    # Physical Stock
    physical_quantity = Column(Numeric(15, 3), nullable=True)
    physical_rate = Column(Numeric(15, 2), nullable=True)
    physical_value = Column(Numeric(18, 2), nullable=True)
    
    # Variance
    variance_quantity = Column(Numeric(15, 3), default=0.000)
    variance_value = Column(Numeric(18, 2), default=0.00)
    variance_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Status
    is_verified = Column(Boolean, default=False)
    has_variance = Column(Boolean, default=False)
    
    # Batch & Serial
    batch_number = Column(String(50), nullable=True)
    serial_number = Column(String(50), nullable=True)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciliation_notes = Column(Text, nullable=True)
    reconciled_by = Column(UUID(as_uuid=True), nullable=True)
    reconciled_at = Column(DateTime, nullable=True)
    
    # Audit fields
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Relationships
    verification = relationship("StockVerification", back_populates="items")
    item = relationship("ItemMaster", back_populates="verifications")
    
    __table_args__ = (
        Index("ix_verification_item_verification", "verification_id"),
        Index("ix_verification_item_item", "item_id"),
    )


# ============================================================================
# Inventory Valuation
# ============================================================================

class InventoryValuation(Base):
    """
    Inventory Valuation - Snapshot of inventory value at a point in time
    """
    __tablename__ = "inventory_valuations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Valuation Details
    valuation_number = Column(String(50), nullable=False, unique=True, index=True)
    valuation_date = Column(Date, nullable=False)
    financial_year = Column(Integer, nullable=False)
    financial_period = Column(String(20), nullable=True)
    
    # Scope
    warehouse = Column(String(100), nullable=True)
    item_category = Column(String(100), nullable=True)
    item_type = Column(Enum(ItemType), nullable=True)
    
    # Valuation Method
    valuation_method = Column(Enum(ValuationMethod), nullable=False)
    
    # Summary
    total_items = Column(Integer, default=0)
    total_quantity = Column(Numeric(18, 3), default=0.000)
    total_value = Column(Numeric(18, 2), default=0.00)
    
    # Breakdown by Type
    raw_material_value = Column(Numeric(18, 2), default=0.00)
    finished_goods_value = Column(Numeric(18, 2), default=0.00)
    wip_value = Column(Numeric(18, 2), default=0.00)
    consumables_value = Column(Numeric(18, 2), default=0.00)
    other_value = Column(Numeric(18, 2), default=0.00)
    
    # Status
    is_finalized = Column(Boolean, default=False)
    finalized_by = Column(UUID(as_uuid=True), nullable=True)
    finalized_at = Column(DateTime, nullable=True)
    
    # Notes
    remarks = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    items = relationship("InventoryValuationItem", back_populates="valuation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_valuation_tenant_number", "tenant_id", "valuation_number", unique=True),
        Index("ix_valuation_date", "valuation_date"),
        Index("ix_valuation_year", "financial_year"),
    )


class InventoryValuationItem(Base):
    """
    Inventory Valuation Items - Line items for each valuation
    """
    __tablename__ = "inventory_valuation_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    valuation_id = Column(UUID(as_uuid=True), ForeignKey("inventory_valuations.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    
    # Item Details (snapshot)
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    
    # Quantity
    quantity = Column(Numeric(15, 3), nullable=False)
    unit = Column(Enum(UnitOfMeasure), nullable=False)
    
    # Valuation
    rate = Column(Numeric(15, 2), nullable=False)
    value = Column(Numeric(18, 2), nullable=False)
    valuation_method = Column(Enum(ValuationMethod), nullable=False)
    
    # Location
    warehouse = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Batch & Serial
    batch_number = Column(String(50), nullable=True)
    serial_number = Column(String(50), nullable=True)
    
    # Relationships
    valuation = relationship("InventoryValuation", back_populates="items")
    
    __table_args__ = (
        Index("ix_valuation_item_valuation", "valuation_id"),
        Index("ix_valuation_item_item", "item_id"),
    )
