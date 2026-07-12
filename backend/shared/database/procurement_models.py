"""
Procurement & Vendor Management Database Models
Vendor Master, Purchase Requisitions, RFQ, PO, GRN, Invoice Processing, Vendor Rating
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
class VendorType(str, enum.Enum):
    """Types of vendors"""
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE_PROVIDER = "service_provider"
    MANUFACTURER = "manufacturer"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    CONSULTANT = "consultant"


class VendorStatus(str, enum.Enum):
    """Vendor status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"


class PaymentTerms(str, enum.Enum):
    """Payment terms"""
    IMMEDIATE = "immediate"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    NET_90 = "net_90"
    ADVANCE = "advance"
    COD = "cod"
    CUSTOM = "custom"


class RequisitionStatus(str, enum.Enum):
    """Purchase requisition status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    CONVERTED_TO_PO = "converted_to_po"
    PARTIALLY_CONVERTED = "partially_converted"


class RequisitionPriority(str, enum.Enum):
    """Requisition priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RFQStatus(str, enum.Enum):
    """RFQ status"""
    DRAFT = "draft"
    SENT = "sent"
    RESPONSE_RECEIVED = "response_received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class POStatus(str, enum.Enum):
    """Purchase order status"""
    DRAFT = "draft"
    APPROVED = "approved"
    SENT_TO_VENDOR = "sent_to_vendor"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    PARTIALLY_RECEIVED = "partially_received"
    FULLY_RECEIVED = "fully_received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class GRNStatus(str, enum.Enum):
    """Goods Receipt Note status"""
    DRAFT = "draft"
    RECEIVED = "received"
    QUALITY_CHECK_PENDING = "quality_check_pending"
    QUALITY_CHECK_PASSED = "quality_check_passed"
    QUALITY_CHECK_FAILED = "quality_check_failed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIALLY_ACCEPTED = "partially_accepted"


class InvoiceStatus(str, enum.Enum):
    """Vendor invoice status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_VERIFICATION = "under_verification"
    MATCHED = "matched"
    MISMATCH = "mismatch"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"


class InvoiceMatchingStatus(str, enum.Enum):
    """3-way matching status"""
    NOT_MATCHED = "not_matched"
    TWO_WAY_MATCHED = "two_way_matched"  # Invoice vs PO
    THREE_WAY_MATCHED = "three_way_matched"  # Invoice vs PO vs GRN
    PRICE_MISMATCH = "price_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    TOLERANCE_MISMATCH = "tolerance_mismatch"


# Models
class Vendor(Base):
    """
    Vendor Master
    Central repository of vendor information
    """
    __tablename__ = "vendors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Basic Information
    vendor_code = Column(String(50), nullable=False, unique=True, index=True)
    vendor_name = Column(String(200), nullable=False)
    vendor_type = Column(Enum(VendorType), nullable=False)
    status = Column(Enum(VendorStatus), nullable=False, default=VendorStatus.ACTIVE)
    
    # Contact Information
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Tax Information
    pan_number = Column(String(10), nullable=True)
    gst_number = Column(String(15), nullable=True, index=True)
    tan_number = Column(String(10), nullable=True)
    msme_registration = Column(String(50), nullable=True)
    
    # Banking Details
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(11), nullable=True)
    account_holder_name = Column(String(100), nullable=True)
    
    # Payment Terms
    payment_terms = Column(Enum(PaymentTerms), nullable=False, default=PaymentTerms.NET_30)
    credit_limit = Column(Numeric(15, 2), default=0.00)
    credit_period_days = Column(Integer, default=30)
    
    # Rating & Performance
    overall_rating = Column(Numeric(3, 2), default=0.00)  # 0.00 to 5.00
    quality_rating = Column(Numeric(3, 2), default=0.00)
    delivery_rating = Column(Numeric(3, 2), default=0.00)
    price_rating = Column(Numeric(3, 2), default=0.00)
    service_rating = Column(Numeric(3, 2), default=0.00)
    total_orders = Column(Integer, default=0)
    on_time_deliveries = Column(Integer, default=0)
    
    # Additional Information
    products_services = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    blacklist_reason = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    purchase_requisitions = relationship("PurchaseRequisition", back_populates="preferred_vendor")
    rfq_vendors = relationship("RFQVendor", back_populates="vendor")
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")
    vendor_ratings = relationship("VendorRating", back_populates="vendor")
    
    __table_args__ = (
        Index("ix_vendor_tenant_code", "tenant_id", "vendor_code", unique=True),
        Index("ix_vendor_status", "status"),
    )



class PurchaseRequisition(Base):
    """
    Purchase Requisition
    Internal request for procurement
    """
    __tablename__ = "purchase_requisitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Requisition Details
    requisition_number = Column(String(50), nullable=False, unique=True, index=True)
    requisition_date = Column(Date, nullable=False, default=date.today)
    required_by_date = Column(Date, nullable=False)
    status = Column(Enum(RequisitionStatus), nullable=False, default=RequisitionStatus.DRAFT)
    priority = Column(Enum(RequisitionPriority), nullable=False, default=RequisitionPriority.MEDIUM)
    
    # Department & Requester
    department = Column(String(100), nullable=False)
    requester_id = Column(UUID(as_uuid=True), nullable=False)
    requester_name = Column(String(100), nullable=False)
    
    # Purpose
    purpose = Column(Text, nullable=False)
    justification = Column(Text, nullable=True)
    
    # Budget
    budget_code = Column(String(50), nullable=True)
    estimated_total = Column(Numeric(15, 2), default=0.00)
    
    # Preferred Vendor
    preferred_vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    
    # Approval Workflow
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    items = relationship("PurchaseRequisitionItem", back_populates="requisition", cascade="all, delete-orphan")
    preferred_vendor = relationship("Vendor", back_populates="purchase_requisitions")
    rfqs = relationship("RFQ", back_populates="requisition")
    
    __table_args__ = (
        Index("ix_pr_tenant_number", "tenant_id", "requisition_number", unique=True),
        Index("ix_pr_status", "status"),
        Index("ix_pr_date", "requisition_date"),
    )



class PurchaseRequisitionItem(Base):
    """
    Purchase Requisition Line Items
    """
    __tablename__ = "purchase_requisition_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    requisition_id = Column(UUID(as_uuid=True), ForeignKey("purchase_requisitions.id"), nullable=False)
    
    # Item Details
    item_code = Column(String(50), nullable=True)
    item_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    specification = Column(Text, nullable=True)
    
    # Quantity
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_of_measure = Column(String(20), nullable=False)  # pcs, kg, ltr, box, etc.
    
    # Pricing
    estimated_unit_price = Column(Numeric(15, 2), nullable=True)
    estimated_total_price = Column(Numeric(15, 2), nullable=True)
    
    # Conversion Tracking
    quantity_converted = Column(Numeric(10, 2), default=0.00)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requisition = relationship("PurchaseRequisition", back_populates="items")
    
    __table_args__ = (
        Index("ix_pri_requisition", "requisition_id"),
    )


class RFQ(Base):
    """
    Request for Quotation
    """
    __tablename__ = "rfqs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # RFQ Details
    rfq_number = Column(String(50), nullable=False, unique=True, index=True)
    rfq_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(RFQStatus), nullable=False, default=RFQStatus.DRAFT)
    
    # Reference
    requisition_id = Column(UUID(as_uuid=True), ForeignKey("purchase_requisitions.id"), nullable=True)
    
    # Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    requisition = relationship("PurchaseRequisition", back_populates="rfqs")
    items = relationship("RFQItem", back_populates="rfq", cascade="all, delete-orphan")
    vendors = relationship("RFQVendor", back_populates="rfq", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_rfq_tenant_number", "tenant_id", "rfq_number", unique=True),
        Index("ix_rfq_status", "status"),
    )


class RFQItem(Base):
    """
    RFQ Line Items
    """
    __tablename__ = "rfq_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)
    
    # Item Details
    item_code = Column(String(50), nullable=True)
    item_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    specification = Column(Text, nullable=True)
    
    # Quantity
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    
    # Reference to requisition item (optional)
    requisition_item_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rfq = relationship("RFQ", back_populates="items")
    vendor_quotes = relationship("VendorQuote", back_populates="rfq_item")
    
    __table_args__ = (
        Index("ix_rfq_item_rfq", "rfq_id"),
    )



class RFQVendor(Base):
    """
    Vendors invited for RFQ
    """
    __tablename__ = "rfq_vendors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    
    # Response tracking
    invited_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    is_responded = Column(Boolean, default=False)
    
    # Selection
    is_selected = Column(Boolean, default=False)
    selection_reason = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rfq = relationship("RFQ", back_populates="vendors")
    vendor = relationship("Vendor", back_populates="rfq_vendors")
    
    __table_args__ = (
        Index("ix_rfq_vendor_rfq", "rfq_id"),
        Index("ix_rfq_vendor_vendor", "vendor_id"),
    )


class VendorQuote(Base):
    """
    Vendor quotations against RFQ items
    """
    __tablename__ = "vendor_quotes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rfq_item_id = Column(UUID(as_uuid=True), ForeignKey("rfq_items.id"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    
    # Quote Details
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    delivery_days = Column(Integer, nullable=True)
    warranty_months = Column(Integer, nullable=True)
    
    # Tax
    tax_percentage = Column(Numeric(5, 2), default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    total_with_tax = Column(Numeric(15, 2), nullable=False)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    attachments = Column(Text, nullable=True)  # JSON array of file URLs
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rfq_item = relationship("RFQItem", back_populates="vendor_quotes")
    
    __table_args__ = (
        Index("ix_vendor_quote_rfq_item", "rfq_item_id"),
        Index("ix_vendor_quote_vendor", "vendor_id"),
    )



class PurchaseOrder(Base):
    """
    Purchase Order
    """
    __tablename__ = "purchase_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # PO Details
    po_number = Column(String(50), nullable=False, unique=True, index=True)
    po_date = Column(Date, nullable=False, default=date.today)
    expected_delivery_date = Column(Date, nullable=False)
    status = Column(Enum(POStatus), nullable=False, default=POStatus.DRAFT)
    
    # Vendor
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    
    # Reference
    rfq_id = Column(UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=True)
    requisition_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Delivery Address
    delivery_address_line1 = Column(String(200), nullable=True)
    delivery_address_line2 = Column(String(200), nullable=True)
    delivery_city = Column(String(100), nullable=True)
    delivery_state = Column(String(100), nullable=True)
    delivery_pincode = Column(String(10), nullable=True)
    delivery_country = Column(String(100), default="India")
    
    # Contact
    delivery_contact_person = Column(String(100), nullable=True)
    delivery_contact_phone = Column(String(20), nullable=True)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Payment Terms
    payment_terms = Column(Enum(PaymentTerms), nullable=False, default=PaymentTerms.NET_30)
    advance_payment_percentage = Column(Numeric(5, 2), default=0.00)
    advance_payment_amount = Column(Numeric(15, 2), default=0.00)
    
    # Terms & Conditions
    terms_and_conditions = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Vendor Acknowledgment
    acknowledged_by_vendor = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    grns = relationship("GoodsReceiptNote", back_populates="purchase_order")
    invoices = relationship("VendorInvoice", back_populates="purchase_order")
    
    __table_args__ = (
        Index("ix_po_tenant_number", "tenant_id", "po_number", unique=True),
        Index("ix_po_vendor", "vendor_id"),
        Index("ix_po_status", "status"),
        Index("ix_po_date", "po_date"),
    )


class PurchaseOrderItem(Base):
    """
    Purchase Order Line Items
    """
    __tablename__ = "purchase_order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    
    # Item Details
    item_code = Column(String(50), nullable=True)
    item_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    specification = Column(Text, nullable=True)
    
    # Quantity
    ordered_quantity = Column(Numeric(10, 2), nullable=False)
    received_quantity = Column(Numeric(10, 2), default=0.00)
    unit_of_measure = Column(String(20), nullable=False)
    
    # Pricing
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # Tax
    tax_percentage = Column(Numeric(5, 2), default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0.00)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    
    # Net Amount
    net_amount = Column(Numeric(15, 2), nullable=False)
    
    # Reference
    rfq_item_id = Column(UUID(as_uuid=True), nullable=True)
    requisition_item_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    grn_items = relationship("GRNItem", back_populates="po_item")
    
    __table_args__ = (
        Index("ix_po_item_po", "po_id"),
    )


class GoodsReceiptNote(Base):
    """
    Goods Receipt Note (GRN)
    Records receipt of goods from vendor
    """
    __tablename__ = "goods_receipt_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # GRN Details
    grn_number = Column(String(50), nullable=False, unique=True, index=True)
    grn_date = Column(Date, nullable=False, default=date.today)
    receipt_date = Column(Date, nullable=False, default=date.today)
    status = Column(Enum(GRNStatus), nullable=False, default=GRNStatus.DRAFT)
    
    # Reference
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    
    # Delivery Details
    challan_number = Column(String(50), nullable=True)
    challan_date = Column(Date, nullable=True)
    transporter_name = Column(String(100), nullable=True)
    vehicle_number = Column(String(20), nullable=True)
    lr_number = Column(String(50), nullable=True)  # Lorry Receipt
    
    # Quality Check
    quality_check_required = Column(Boolean, default=True)
    quality_checked_by = Column(UUID(as_uuid=True), nullable=True)
    quality_checked_at = Column(DateTime, nullable=True)
    quality_remarks = Column(Text, nullable=True)
    
    # Receiving Details
    received_by = Column(UUID(as_uuid=True), nullable=True)
    warehouse_location = Column(String(100), nullable=True)
    
    # Notes
    remarks = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="grns")
    items = relationship("GRNItem", back_populates="grn", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_grn_tenant_number", "tenant_id", "grn_number", unique=True),
        Index("ix_grn_po", "po_id"),
        Index("ix_grn_status", "status"),
        Index("ix_grn_date", "grn_date"),
    )


class GRNItem(Base):
    """
    GRN Line Items
    """
    __tablename__ = "grn_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    grn_id = Column(UUID(as_uuid=True), ForeignKey("goods_receipt_notes.id"), nullable=False)
    po_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_items.id"), nullable=False)
    
    # Item Details
    item_code = Column(String(50), nullable=True)
    item_name = Column(String(200), nullable=False)
    
    # Quantity
    ordered_quantity = Column(Numeric(10, 2), nullable=False)
    received_quantity = Column(Numeric(10, 2), nullable=False)
    accepted_quantity = Column(Numeric(10, 2), default=0.00)
    rejected_quantity = Column(Numeric(10, 2), default=0.00)
    unit_of_measure = Column(String(20), nullable=False)
    
    # Quality Check
    quality_status = Column(String(20), nullable=True)  # passed, failed, pending
    quality_remarks = Column(Text, nullable=True)
    
    # Batch/Serial Numbers
    batch_number = Column(String(50), nullable=True)
    serial_numbers = Column(Text, nullable=True)  # JSON array for multiple serial numbers
    
    # Notes
    remarks = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grn = relationship("GoodsReceiptNote", back_populates="items")
    po_item = relationship("PurchaseOrderItem", back_populates="grn_items")
    
    __table_args__ = (
        Index("ix_grn_item_grn", "grn_id"),
        Index("ix_grn_item_po_item", "po_item_id"),
    )


class VendorInvoice(Base):
    """
    Vendor Invoice
    Invoice received from vendor
    """
    __tablename__ = "vendor_invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Invoice Details
    invoice_number = Column(String(50), nullable=False, index=True)
    vendor_invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    matching_status = Column(Enum(InvoiceMatchingStatus), nullable=False, default=InvoiceMatchingStatus.NOT_MATCHED)
    
    # Reference
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False)
    grn_id = Column(UUID(as_uuid=True), ForeignKey("goods_receipt_notes.id"), nullable=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    
    # Financial
    subtotal = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    other_charges = Column(Numeric(15, 2), default=0.00)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment Tracking
    paid_amount = Column(Numeric(15, 2), default=0.00)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax Details
    gst_number = Column(String(15), nullable=True)
    cgst_amount = Column(Numeric(15, 2), default=0.00)
    sgst_amount = Column(Numeric(15, 2), default=0.00)
    igst_amount = Column(Numeric(15, 2), default=0.00)
    
    # Matching Details
    po_amount_variance = Column(Numeric(15, 2), default=0.00)
    grn_quantity_variance = Column(Numeric(10, 2), default=0.00)
    tolerance_percentage = Column(Numeric(5, 2), default=5.00)  # Acceptable variance
    
    # Approval
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Attachments
    invoice_file_url = Column(String(500), nullable=True)
    supporting_documents = Column(Text, nullable=True)  # JSON array
    
    # Notes
    remarks = Column(Text, nullable=True)
    
    # Audit fields
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="invoices")
    vendor = relationship("Vendor")
    items = relationship("VendorInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_vendor_invoice_tenant_number", "tenant_id", "invoice_number", unique=True),
        Index("ix_vendor_invoice_vendor_number", "vendor_id", "vendor_invoice_number"),
        Index("ix_vendor_invoice_po", "po_id"),
        Index("ix_vendor_invoice_status", "status"),
        Index("ix_vendor_invoice_date", "invoice_date"),
    )



class VendorInvoiceItem(Base):
    """
    Vendor Invoice Line Items
    """
    __tablename__ = "vendor_invoice_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("vendor_invoices.id"), nullable=False)
    po_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_items.id"), nullable=True)
    
    # Item Details
    item_code = Column(String(50), nullable=True)
    item_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Quantity
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    
    # Pricing
    unit_price = Column(Numeric(15, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    
    # Tax
    tax_percentage = Column(Numeric(5, 2), default=0.00)
    tax_amount = Column(Numeric(15, 2), default=0.00)
    
    # Discount
    discount_percentage = Column(Numeric(5, 2), default=0.00)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    
    # Net Amount
    net_amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("VendorInvoice", back_populates="items")
    
    __table_args__ = (
        Index("ix_vendor_invoice_item_invoice", "invoice_id"),
    )


class VendorRating(Base):
    """
    Vendor Performance Rating
    """
    __tablename__ = "vendor_ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=True)
    
    # Rating Date
    rating_date = Column(Date, nullable=False, default=date.today)
    rating_period_start = Column(Date, nullable=True)
    rating_period_end = Column(Date, nullable=True)
    
    # Rating Criteria (1-5 scale)
    quality_rating = Column(Numeric(3, 2), nullable=False)  # Product/Service quality
    delivery_rating = Column(Numeric(3, 2), nullable=False)  # On-time delivery
    price_rating = Column(Numeric(3, 2), nullable=False)  # Price competitiveness
    service_rating = Column(Numeric(3, 2), nullable=False)  # Customer service
    communication_rating = Column(Numeric(3, 2), nullable=False)  # Communication
    
    # Overall Rating (average)
    overall_rating = Column(Numeric(3, 2), nullable=False)
    
    # Performance Metrics
    delivery_status = Column(String(20), nullable=True)  # on_time, late, early
    days_late = Column(Integer, default=0)
    defect_percentage = Column(Numeric(5, 2), default=0.00)
    rejection_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Feedback
    positive_points = Column(Text, nullable=True)
    improvement_areas = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Rated By
    rated_by = Column(UUID(as_uuid=True), nullable=False)
    rated_by_name = Column(String(100), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="vendor_ratings")
    
    __table_args__ = (
        Index("ix_vendor_rating_vendor", "vendor_id"),
        Index("ix_vendor_rating_date", "rating_date"),
        CheckConstraint("quality_rating >= 0 AND quality_rating <= 5", name="check_quality_rating"),
        CheckConstraint("delivery_rating >= 0 AND delivery_rating <= 5", name="check_delivery_rating"),
        CheckConstraint("price_rating >= 0 AND price_rating <= 5", name="check_price_rating"),
        CheckConstraint("service_rating >= 0 AND service_rating <= 5", name="check_service_rating"),
        CheckConstraint("communication_rating >= 0 AND communication_rating <= 5", name="check_communication_rating"),
        CheckConstraint("overall_rating >= 0 AND overall_rating <= 5", name="check_overall_rating"),
    )
