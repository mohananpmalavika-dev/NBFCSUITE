"""
Inventory Management Pydantic Schemas
Request/Response models for API validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID

from backend.shared.database.inventory_models import (
    ItemType, ItemStatus, UnitOfMeasure, TransactionType, TransactionStatus,
    ValuationMethod, VerificationStatus
)


# ============================================================================
# Item Master Schemas
# ============================================================================

class ItemMasterBase(BaseModel):
    """Base schema for Item Master"""
    item_name: str = Field(..., min_length=1, max_length=200)
    item_description: Optional[str] = None
    item_type: ItemType
    item_status: ItemStatus = ItemStatus.ACTIVE
    
    # Category
    category: Optional[str] = None
    sub_category: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    
    # Unit
    base_unit: UnitOfMeasure
    alternate_unit: Optional[UnitOfMeasure] = None
    conversion_factor: Decimal = Decimal("1.0")
    
    # Barcode & SKU
    barcode: Optional[str] = None
    sku: Optional[str] = None
    hsn_code: Optional[str] = None
    
    # Pricing
    standard_cost: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    
    # Stock Levels
    minimum_stock: Decimal = Decimal("0.000")
    maximum_stock: Decimal = Decimal("0.000")
    reorder_level: Decimal = Decimal("0.000")
    reorder_quantity: Decimal = Decimal("0.000")
    
    # Valuation
    valuation_method: ValuationMethod = ValuationMethod.WEIGHTED_AVERAGE
    
    # Storage
    warehouse_location: Optional[str] = None
    rack_number: Optional[str] = None
    bin_number: Optional[str] = None
    
    # Supplier
    preferred_supplier_id: Optional[UUID] = None
    lead_time_days: int = 0
    
    # Tax
    is_taxable: bool = True
    gst_rate: Decimal = Decimal("0.00")
    
    # Tracking
    is_batch_tracked: bool = False
    is_serial_tracked: bool = False
    is_expiry_tracked: bool = False
    shelf_life_days: Optional[int] = None
    
    # Additional
    specification: Optional[str] = None
    remarks: Optional[str] = None
    image_url: Optional[str] = None


class ItemMasterCreate(ItemMasterBase):
    """Schema for creating item"""
    item_code: str = Field(..., min_length=1, max_length=50)


class ItemMasterUpdate(ItemMasterBase):
    """Schema for updating item"""
    item_name: Optional[str] = Field(None, min_length=1, max_length=200)
    item_type: Optional[ItemType] = None
    base_unit: Optional[UnitOfMeasure] = None


class ItemMasterResponse(ItemMasterBase):
    """Schema for item response"""
    id: UUID
    item_code: str
    tenant_id: int
    current_stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    average_cost: Decimal
    last_purchase_price: Decimal
    total_value: Decimal
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemMasterListResponse(BaseModel):
    """Schema for item list response"""
    items: List[ItemMasterResponse]
    total: int
    page: int
    page_size: int



# ============================================================================
# Stock Transaction Schemas
# ============================================================================

class StockTransactionBase(BaseModel):
    """Base schema for Stock Transaction"""
    transaction_date: date
    transaction_type: TransactionType
    item_id: UUID
    quantity: Decimal = Field(..., gt=0)
    unit: UnitOfMeasure
    rate: Decimal = Decimal("0.00")
    
    # Location
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    
    # Batch & Serial
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    expiry_date: Optional[date] = None
    
    # Reference
    reference_type: Optional[str] = None
    reference_number: Optional[str] = None
    reference_id: Optional[UUID] = None
    
    # Purpose
    purpose: Optional[str] = None
    remarks: Optional[str] = None


class StockTransactionCreate(StockTransactionBase):
    """Schema for creating stock transaction"""
    pass


class StockTransactionUpdate(BaseModel):
    """Schema for updating stock transaction"""
    transaction_date: Optional[date] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    rate: Optional[Decimal] = None
    remarks: Optional[str] = None


class StockTransactionResponse(StockTransactionBase):
    """Schema for stock transaction response"""
    id: UUID
    transaction_number: str
    transaction_status: TransactionStatus
    amount: Decimal
    is_posted: bool
    posted_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockTransactionListResponse(BaseModel):
    """Schema for transaction list response"""
    transactions: List[StockTransactionResponse]
    total: int
    page: int
    page_size: int



# ============================================================================
# Stock Verification Schemas
# ============================================================================

class StockVerificationItemBase(BaseModel):
    """Base schema for verification item"""
    item_id: UUID
    system_quantity: Decimal
    physical_quantity: Optional[Decimal] = None
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    remarks: Optional[str] = None


class StockVerificationItemCreate(StockVerificationItemBase):
    """Schema for creating verification item"""
    pass


class StockVerificationItemUpdate(BaseModel):
    """Schema for updating verification item"""
    physical_quantity: Decimal
    remarks: Optional[str] = None


class StockVerificationItemResponse(StockVerificationItemBase):
    """Schema for verification item response"""
    id: UUID
    verification_id: UUID
    system_rate: Decimal
    system_value: Decimal
    physical_rate: Optional[Decimal]
    physical_value: Optional[Decimal]
    variance_quantity: Decimal
    variance_value: Decimal
    variance_percentage: Decimal
    is_verified: bool
    has_variance: bool
    is_reconciled: bool
    verified_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StockVerificationBase(BaseModel):
    """Base schema for Stock Verification"""
    verification_date: date
    scheduled_date: date
    warehouse: Optional[str] = None
    location: Optional[str] = None
    item_category: Optional[str] = None
    supervisor_id: Optional[UUID] = None
    supervisor_name: Optional[str] = None
    purpose: Optional[str] = None
    remarks: Optional[str] = None


class StockVerificationCreate(StockVerificationBase):
    """Schema for creating verification"""
    items: List[StockVerificationItemCreate] = []


class StockVerificationUpdate(BaseModel):
    """Schema for updating verification"""
    verification_date: Optional[date] = None
    scheduled_date: Optional[date] = None
    verification_status: Optional[VerificationStatus] = None
    remarks: Optional[str] = None



class StockVerificationResponse(StockVerificationBase):
    """Schema for verification response"""
    id: UUID
    verification_number: str
    verification_status: VerificationStatus
    completed_date: Optional[date]
    total_items: int
    items_verified: int
    items_with_variance: int
    total_variance_value: Decimal
    items: List[StockVerificationItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockVerificationListResponse(BaseModel):
    """Schema for verification list response"""
    verifications: List[StockVerificationResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Inventory Valuation Schemas
# ============================================================================

class InventoryValuationItemResponse(BaseModel):
    """Schema for valuation item response"""
    id: UUID
    valuation_id: UUID
    item_id: UUID
    item_code: str
    item_name: str
    item_type: ItemType
    quantity: Decimal
    unit: UnitOfMeasure
    rate: Decimal
    value: Decimal
    valuation_method: ValuationMethod
    warehouse: Optional[str]
    location: Optional[str]
    batch_number: Optional[str]
    serial_number: Optional[str]
    
    class Config:
        from_attributes = True


class InventoryValuationBase(BaseModel):
    """Base schema for Inventory Valuation"""
    valuation_date: date
    financial_year: int
    financial_period: Optional[str] = None
    warehouse: Optional[str] = None
    item_category: Optional[str] = None
    item_type: Optional[ItemType] = None
    valuation_method: ValuationMethod
    remarks: Optional[str] = None


class InventoryValuationCreate(InventoryValuationBase):
    """Schema for creating valuation"""
    pass



class InventoryValuationUpdate(BaseModel):
    """Schema for updating valuation"""
    valuation_date: Optional[date] = None
    remarks: Optional[str] = None


class InventoryValuationResponse(InventoryValuationBase):
    """Schema for valuation response"""
    id: UUID
    valuation_number: str
    total_items: int
    total_quantity: Decimal
    total_value: Decimal
    raw_material_value: Decimal
    finished_goods_value: Decimal
    wip_value: Decimal
    consumables_value: Decimal
    other_value: Decimal
    is_finalized: bool
    finalized_at: Optional[datetime]
    items: List[InventoryValuationItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryValuationListResponse(BaseModel):
    """Schema for valuation list response"""
    valuations: List[InventoryValuationResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Dashboard & Reports Schemas
# ============================================================================

class InventoryDashboardMetrics(BaseModel):
    """Schema for inventory dashboard metrics"""
    total_items: int
    active_items: int
    total_stock_value: Decimal
    low_stock_items: int
    out_of_stock_items: int
    pending_transactions: int
    pending_verifications: int
    
    # Value by type
    raw_material_value: Decimal
    finished_goods_value: Decimal
    wip_value: Decimal
    consumables_value: Decimal
    
    # Recent activity
    transactions_today: int
    transactions_this_week: int
    transactions_this_month: int


class StockSummaryByItem(BaseModel):
    """Schema for stock summary by item"""
    item_id: UUID
    item_code: str
    item_name: str
    item_type: ItemType
    current_stock: Decimal
    unit: UnitOfMeasure
    average_cost: Decimal
    total_value: Decimal
    warehouse_location: Optional[str]
    is_low_stock: bool
    is_out_of_stock: bool



class StockLedgerEntry(BaseModel):
    """Schema for stock ledger entry"""
    transaction_date: date
    transaction_number: str
    transaction_type: TransactionType
    opening_quantity: Decimal
    in_quantity: Decimal
    out_quantity: Decimal
    closing_quantity: Decimal
    rate: Decimal
    opening_value: Decimal
    in_value: Decimal
    out_value: Decimal
    closing_value: Decimal
    
    class Config:
        from_attributes = True


class StockLedgerResponse(BaseModel):
    """Schema for stock ledger response"""
    item_id: UUID
    item_code: str
    item_name: str
    entries: List[StockLedgerEntry]
    opening_stock: Decimal
    closing_stock: Decimal
    opening_value: Decimal
    closing_value: Decimal


class LowStockAlert(BaseModel):
    """Schema for low stock alert"""
    item_id: UUID
    item_code: str
    item_name: str
    current_stock: Decimal
    minimum_stock: Decimal
    reorder_level: Decimal
    reorder_quantity: Decimal
    unit: UnitOfMeasure
    warehouse_location: Optional[str]
    preferred_supplier_id: Optional[UUID]
    lead_time_days: int


class StockMovementReport(BaseModel):
    """Schema for stock movement report"""
    item_id: UUID
    item_code: str
    item_name: str
    opening_stock: Decimal
    total_in: Decimal
    total_out: Decimal
    closing_stock: Decimal
    unit: UnitOfMeasure
    opening_value: Decimal
    total_in_value: Decimal
    total_out_value: Decimal
    closing_value: Decimal
