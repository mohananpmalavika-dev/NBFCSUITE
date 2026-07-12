"""
Procurement Module - Pydantic Schemas
Request/Response models for Vendor Management, Purchase Requisitions, RFQ, PO, GRN, and Invoices
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator, UUID4
from enum import Enum


# Enums
class VendorTypeEnum(str, Enum):
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE_PROVIDER = "service_provider"
    MANUFACTURER = "manufacturer"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    CONSULTANT = "consultant"


class VendorStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"


class PaymentTermsEnum(str, Enum):
    IMMEDIATE = "immediate"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    NET_90 = "net_90"
    ADVANCE = "advance"
    COD = "cod"
    CUSTOM = "custom"


class RequisitionStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    CONVERTED_TO_PO = "converted_to_po"
    PARTIALLY_CONVERTED = "partially_converted"


class RequisitionPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"



class RFQStatusEnum(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    RESPONSE_RECEIVED = "response_received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class POStatusEnum(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SENT_TO_VENDOR = "sent_to_vendor"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    PARTIALLY_RECEIVED = "partially_received"
    FULLY_RECEIVED = "fully_received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class GRNStatusEnum(str, Enum):
    DRAFT = "draft"
    RECEIVED = "received"
    QUALITY_CHECK_PENDING = "quality_check_pending"
    QUALITY_CHECK_PASSED = "quality_check_passed"
    QUALITY_CHECK_FAILED = "quality_check_failed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIALLY_ACCEPTED = "partially_accepted"


class InvoiceStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_VERIFICATION = "under_verification"
    MATCHED = "matched"
    MISMATCH = "mismatch"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"


class InvoiceMatchingStatusEnum(str, Enum):
    NOT_MATCHED = "not_matched"
    TWO_WAY_MATCHED = "two_way_matched"
    THREE_WAY_MATCHED = "three_way_matched"
    PRICE_MISMATCH = "price_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    TOLERANCE_MISMATCH = "tolerance_mismatch"



# ============================================
# VENDOR SCHEMAS
# ============================================

class VendorBase(BaseModel):
    vendor_name: str = Field(..., min_length=1, max_length=200)
    vendor_type: VendorTypeEnum
    status: VendorStatusEnum = VendorStatusEnum.ACTIVE
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="India", max_length=100)
    pan_number: Optional[str] = Field(None, max_length=10)
    gst_number: Optional[str] = Field(None, max_length=15)
    tan_number: Optional[str] = Field(None, max_length=10)
    msme_registration: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    ifsc_code: Optional[str] = Field(None, max_length=11)
    account_holder_name: Optional[str] = Field(None, max_length=100)
    payment_terms: PaymentTermsEnum = PaymentTermsEnum.NET_30
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_period_days: int = Field(default=30, ge=0)
    products_services: Optional[str] = None
    notes: Optional[str] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    vendor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    vendor_type: Optional[VendorTypeEnum] = None
    status: Optional[VendorStatusEnum] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    pan_number: Optional[str] = Field(None, max_length=10)
    gst_number: Optional[str] = Field(None, max_length=15)
    tan_number: Optional[str] = Field(None, max_length=10)
    msme_registration: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    ifsc_code: Optional[str] = Field(None, max_length=11)
    account_holder_name: Optional[str] = Field(None, max_length=100)
    payment_terms: Optional[PaymentTermsEnum] = None
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    credit_period_days: Optional[int] = Field(None, ge=0)
    products_services: Optional[str] = None
    notes: Optional[str] = None
    blacklist_reason: Optional[str] = None


class VendorResponse(VendorBase):
    id: UUID4
    vendor_code: str
    overall_rating: Decimal
    quality_rating: Decimal
    delivery_rating: Decimal
    price_rating: Decimal
    service_rating: Decimal
    total_orders: int
    on_time_deliveries: int
    blacklist_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    vendors: List[VendorResponse]
    total: int
    page: int
    page_size: int



# ============================================
# PURCHASE REQUISITION SCHEMAS
# ============================================

class PurchaseRequisitionItemBase(BaseModel):
    item_code: Optional[str] = Field(None, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    specification: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    estimated_unit_price: Optional[Decimal] = Field(None, ge=0)
    estimated_total_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class PurchaseRequisitionItemCreate(PurchaseRequisitionItemBase):
    pass


class PurchaseRequisitionItemResponse(PurchaseRequisitionItemBase):
    id: UUID4
    requisition_id: UUID4
    quantity_converted: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseRequisitionBase(BaseModel):
    required_by_date: date
    priority: RequisitionPriorityEnum = RequisitionPriorityEnum.MEDIUM
    department: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=1)
    justification: Optional[str] = None
    budget_code: Optional[str] = Field(None, max_length=50)
    estimated_total: Decimal = Field(default=Decimal("0.00"), ge=0)
    preferred_vendor_id: Optional[UUID4] = None


class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    items: List[PurchaseRequisitionItemCreate] = Field(..., min_items=1)


class PurchaseRequisitionUpdate(BaseModel):
    required_by_date: Optional[date] = None
    priority: Optional[RequisitionPriorityEnum] = None
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    purpose: Optional[str] = Field(None, min_length=1)
    justification: Optional[str] = None
    budget_code: Optional[str] = Field(None, max_length=50)
    estimated_total: Optional[Decimal] = Field(None, ge=0)
    preferred_vendor_id: Optional[UUID4] = None



class PurchaseRequisitionResponse(PurchaseRequisitionBase):
    id: UUID4
    requisition_number: str
    requisition_date: date
    status: RequisitionStatusEnum
    requester_id: UUID4
    requester_name: str
    approved_by: Optional[UUID4] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    items: List[PurchaseRequisitionItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseRequisitionListResponse(BaseModel):
    requisitions: List[PurchaseRequisitionResponse]
    total: int
    page: int
    page_size: int


class PurchaseRequisitionApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None


# ============================================
# RFQ SCHEMAS
# ============================================

class RFQItemBase(BaseModel):
    item_code: Optional[str] = Field(None, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    specification: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    requisition_item_id: Optional[UUID4] = None


class RFQItemCreate(RFQItemBase):
    pass


class RFQItemResponse(RFQItemBase):
    id: UUID4
    rfq_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True


class RFQVendorBase(BaseModel):
    vendor_id: UUID4


class RFQVendorCreate(RFQVendorBase):
    pass



class RFQVendorResponse(RFQVendorBase):
    id: UUID4
    rfq_id: UUID4
    invited_at: datetime
    responded_at: Optional[datetime] = None
    is_responded: bool
    is_selected: bool
    selection_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class VendorQuoteBase(BaseModel):
    unit_price: Decimal = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0)
    delivery_days: Optional[int] = Field(None, ge=0)
    warranty_months: Optional[int] = Field(None, ge=0)
    tax_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_with_tax: Decimal = Field(..., gt=0)
    remarks: Optional[str] = None
    attachments: Optional[str] = None


class VendorQuoteCreate(VendorQuoteBase):
    rfq_item_id: UUID4
    vendor_id: UUID4


class VendorQuoteResponse(VendorQuoteBase):
    id: UUID4
    rfq_item_id: UUID4
    vendor_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RFQBase(BaseModel):
    due_date: date
    requisition_id: Optional[UUID4] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class RFQCreate(RFQBase):
    items: List[RFQItemCreate] = Field(..., min_items=1)
    vendor_ids: List[UUID4] = Field(..., min_items=1)


class RFQUpdate(BaseModel):
    due_date: Optional[date] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None



class RFQResponse(RFQBase):
    id: UUID4
    rfq_number: str
    rfq_date: date
    status: RFQStatusEnum
    items: List[RFQItemResponse] = []
    vendors: List[RFQVendorResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RFQListResponse(BaseModel):
    rfqs: List[RFQResponse]
    total: int
    page: int
    page_size: int


# ============================================
# PURCHASE ORDER SCHEMAS
# ============================================

class PurchaseOrderItemBase(BaseModel):
    item_code: Optional[str] = Field(None, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    specification: Optional[str] = None
    ordered_quantity: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    unit_price: Decimal = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0)
    tax_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    net_amount: Decimal = Field(..., gt=0)
    rfq_item_id: Optional[UUID4] = None
    requisition_item_id: Optional[UUID4] = None


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: UUID4
    po_id: UUID4
    received_quantity: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



class PurchaseOrderBase(BaseModel):
    expected_delivery_date: date
    vendor_id: UUID4
    rfq_id: Optional[UUID4] = None
    requisition_id: Optional[UUID4] = None
    delivery_address_line1: Optional[str] = Field(None, max_length=200)
    delivery_address_line2: Optional[str] = Field(None, max_length=200)
    delivery_city: Optional[str] = Field(None, max_length=100)
    delivery_state: Optional[str] = Field(None, max_length=100)
    delivery_pincode: Optional[str] = Field(None, max_length=10)
    delivery_country: str = Field(default="India", max_length=100)
    delivery_contact_person: Optional[str] = Field(None, max_length=100)
    delivery_contact_phone: Optional[str] = Field(None, max_length=20)
    subtotal: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_amount: Decimal = Field(..., gt=0)
    payment_terms: PaymentTermsEnum = PaymentTermsEnum.NET_30
    advance_payment_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    advance_payment_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    terms_and_conditions: Optional[str] = None
    special_instructions: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate] = Field(..., min_items=1)


class PurchaseOrderUpdate(BaseModel):
    expected_delivery_date: Optional[date] = None
    delivery_address_line1: Optional[str] = Field(None, max_length=200)
    delivery_address_line2: Optional[str] = Field(None, max_length=200)
    delivery_city: Optional[str] = Field(None, max_length=100)
    delivery_state: Optional[str] = Field(None, max_length=100)
    delivery_pincode: Optional[str] = Field(None, max_length=10)
    delivery_country: Optional[str] = Field(None, max_length=100)
    delivery_contact_person: Optional[str] = Field(None, max_length=100)
    delivery_contact_phone: Optional[str] = Field(None, max_length=20)
    terms_and_conditions: Optional[str] = None
    special_instructions: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    id: UUID4
    po_number: str
    po_date: date
    status: POStatusEnum
    approved_by: Optional[UUID4] = None
    approved_at: Optional[datetime] = None
    acknowledged_by_vendor: bool
    acknowledged_at: Optional[datetime] = None
    items: List[PurchaseOrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseOrderListResponse(BaseModel):
    purchase_orders: List[PurchaseOrderResponse]
    total: int
    page: int
    page_size: int



# ============================================
# GRN SCHEMAS
# ============================================

class GRNItemBase(BaseModel):
    po_item_id: UUID4
    item_code: Optional[str] = Field(None, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    ordered_quantity: Decimal = Field(..., gt=0)
    received_quantity: Decimal = Field(..., ge=0)
    accepted_quantity: Decimal = Field(default=Decimal("0.00"), ge=0)
    rejected_quantity: Decimal = Field(default=Decimal("0.00"), ge=0)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    quality_status: Optional[str] = Field(None, max_length=20)
    quality_remarks: Optional[str] = None
    batch_number: Optional[str] = Field(None, max_length=50)
    serial_numbers: Optional[str] = None
    remarks: Optional[str] = None


class GRNItemCreate(GRNItemBase):
    pass


class GRNItemResponse(GRNItemBase):
    id: UUID4
    grn_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoodsReceiptNoteBase(BaseModel):
    po_id: UUID4
    receipt_date: date
    challan_number: Optional[str] = Field(None, max_length=50)
    challan_date: Optional[date] = None
    transporter_name: Optional[str] = Field(None, max_length=100)
    vehicle_number: Optional[str] = Field(None, max_length=20)
    lr_number: Optional[str] = Field(None, max_length=50)
    quality_check_required: bool = True
    warehouse_location: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None


class GoodsReceiptNoteCreate(GoodsReceiptNoteBase):
    items: List[GRNItemCreate] = Field(..., min_items=1)


class GoodsReceiptNoteUpdate(BaseModel):
    receipt_date: Optional[date] = None
    challan_number: Optional[str] = Field(None, max_length=50)
    challan_date: Optional[date] = None
    transporter_name: Optional[str] = Field(None, max_length=100)
    vehicle_number: Optional[str] = Field(None, max_length=20)
    lr_number: Optional[str] = Field(None, max_length=50)
    quality_check_required: Optional[bool] = None
    warehouse_location: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None



class GoodsReceiptNoteResponse(GoodsReceiptNoteBase):
    id: UUID4
    grn_number: str
    grn_date: date
    status: GRNStatusEnum
    quality_checked_by: Optional[UUID4] = None
    quality_checked_at: Optional[datetime] = None
    quality_remarks: Optional[str] = None
    received_by: Optional[UUID4] = None
    rejection_reason: Optional[str] = None
    items: List[GRNItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoodsReceiptNoteListResponse(BaseModel):
    grns: List[GoodsReceiptNoteResponse]
    total: int
    page: int
    page_size: int


class QualityCheckRequest(BaseModel):
    passed: bool
    quality_remarks: Optional[str] = None
    items: List[dict]  # List of {grn_item_id, accepted_quantity, rejected_quantity, quality_status}


# ============================================
# VENDOR INVOICE SCHEMAS
# ============================================

class VendorInvoiceItemBase(BaseModel):
    po_item_id: Optional[UUID4] = None
    item_code: Optional[str] = Field(None, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(..., min_length=1, max_length=20)
    unit_price: Decimal = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0)
    tax_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    net_amount: Decimal = Field(..., gt=0)


class VendorInvoiceItemCreate(VendorInvoiceItemBase):
    pass


class VendorInvoiceItemResponse(VendorInvoiceItemBase):
    id: UUID4
    invoice_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True



class VendorInvoiceBase(BaseModel):
    vendor_invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: date
    due_date: date
    po_id: UUID4
    grn_id: Optional[UUID4] = None
    vendor_id: UUID4
    subtotal: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    other_charges: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_amount: Decimal = Field(..., gt=0)
    gst_number: Optional[str] = Field(None, max_length=15)
    cgst_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    sgst_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    igst_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    tolerance_percentage: Decimal = Field(default=Decimal("5.00"), ge=0, le=100)
    invoice_file_url: Optional[str] = Field(None, max_length=500)
    supporting_documents: Optional[str] = None
    remarks: Optional[str] = None


class VendorInvoiceCreate(VendorInvoiceBase):
    items: List[VendorInvoiceItemCreate] = Field(..., min_items=1)


class VendorInvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    other_charges: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    invoice_file_url: Optional[str] = Field(None, max_length=500)
    supporting_documents: Optional[str] = None
    remarks: Optional[str] = None


class VendorInvoiceResponse(VendorInvoiceBase):
    id: UUID4
    invoice_number: str
    status: InvoiceStatusEnum
    matching_status: InvoiceMatchingStatusEnum
    paid_amount: Decimal
    balance_amount: Decimal
    po_amount_variance: Decimal
    grn_quantity_variance: Decimal
    verified_by: Optional[UUID4] = None
    verified_at: Optional[datetime] = None
    approved_by: Optional[UUID4] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    items: List[VendorInvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorInvoiceListResponse(BaseModel):
    invoices: List[VendorInvoiceResponse]
    total: int
    page: int
    page_size: int


class InvoiceMatchingResult(BaseModel):
    matched: bool
    matching_status: InvoiceMatchingStatusEnum
    po_amount_variance: Decimal
    grn_quantity_variance: Decimal
    issues: List[str] = []



# ============================================
# VENDOR RATING SCHEMAS
# ============================================

class VendorRatingBase(BaseModel):
    vendor_id: UUID4
    po_id: Optional[UUID4] = None
    rating_period_start: Optional[date] = None
    rating_period_end: Optional[date] = None
    quality_rating: Decimal = Field(..., ge=0, le=5)
    delivery_rating: Decimal = Field(..., ge=0, le=5)
    price_rating: Decimal = Field(..., ge=0, le=5)
    service_rating: Decimal = Field(..., ge=0, le=5)
    communication_rating: Decimal = Field(..., ge=0, le=5)
    delivery_status: Optional[str] = Field(None, max_length=20)
    days_late: int = Field(default=0, ge=0)
    defect_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    rejection_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    positive_points: Optional[str] = None
    improvement_areas: Optional[str] = None
    remarks: Optional[str] = None


class VendorRatingCreate(VendorRatingBase):
    
    @validator('quality_rating', 'delivery_rating', 'price_rating', 'service_rating', 'communication_rating')
    def validate_rating(cls, v):
        if v < 0 or v > 5:
            raise ValueError('Rating must be between 0 and 5')
        return v


class VendorRatingUpdate(BaseModel):
    quality_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    delivery_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    price_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    service_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    communication_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    delivery_status: Optional[str] = Field(None, max_length=20)
    days_late: Optional[int] = Field(None, ge=0)
    defect_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    rejection_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    positive_points: Optional[str] = None
    improvement_areas: Optional[str] = None
    remarks: Optional[str] = None


class VendorRatingResponse(VendorRatingBase):
    id: UUID4
    rating_date: date
    overall_rating: Decimal
    rated_by: UUID4
    rated_by_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorRatingListResponse(BaseModel):
    ratings: List[VendorRatingResponse]
    total: int
    page: int
    page_size: int


class VendorPerformanceMetrics(BaseModel):
    vendor_id: UUID4
    vendor_name: str
    total_orders: int
    on_time_deliveries: int
    on_time_percentage: Decimal
    average_rating: Decimal
    quality_rating: Decimal
    delivery_rating: Decimal
    price_rating: Decimal
    service_rating: Decimal



# ============================================
# DASHBOARD & STATISTICS SCHEMAS
# ============================================

class ProcurementDashboardMetrics(BaseModel):
    total_vendors: int
    active_vendors: int
    total_requisitions: int
    pending_approvals: int
    active_rfqs: int
    open_purchase_orders: int
    pending_grns: int
    pending_invoices: int
    total_procurement_value: Decimal
    monthly_procurement_value: Decimal


class VendorStatistics(BaseModel):
    vendor_id: UUID4
    vendor_name: str
    total_orders: int
    total_order_value: Decimal
    pending_orders: int
    completed_orders: int
    average_delivery_time: int
    on_time_delivery_rate: Decimal
    overall_rating: Decimal


class RequisitionStatistics(BaseModel):
    total_requisitions: int
    draft_count: int
    submitted_count: int
    approved_count: int
    rejected_count: int
    converted_count: int
    average_approval_time: int  # in hours


class PurchaseOrderStatistics(BaseModel):
    total_pos: int
    draft_count: int
    approved_count: int
    in_progress_count: int
    completed_count: int
    cancelled_count: int
    total_po_value: Decimal
    average_po_value: Decimal


class ProcurementTrendData(BaseModel):
    month: str
    requisitions: int
    purchase_orders: int
    grns: int
    invoices: int
    total_value: Decimal


# ============================================
# COMMON RESPONSE SCHEMAS
# ============================================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    success: bool = False
