"""
Locker Management Pydantic Schemas

Comprehensive schemas for all locker operations including:
- Locker master management
- Allocation and customer assignment
- Rent payment processing
- Maintenance tracking
- Access logging
- Analytics and reporting
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import uuid


# ==================== ENUMS ====================

class LockerSize(str, Enum):
    """Locker size categories"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


class LockerType(str, Enum):
    """Locker security types"""
    SINGLE_KEY = "single_key"
    DUAL_KEY = "dual_key"


class LockType(str, Enum):
    """Lock mechanism types"""
    MECHANICAL = "mechanical"
    ELECTRONIC = "electronic"
    BIOMETRIC = "biometric"
    COMBINATION = "combination"


class LockerStatus(str, Enum):
    """Locker availability status"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    UNDER_MAINTENANCE = "under_maintenance"
    BLOCKED = "blocked"
    DAMAGED = "damaged"
    RETIRED = "retired"


class AllocationStatus(str, Enum):
    """Allocation lifecycle status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLOSED = "closed"
    SURRENDERED = "surrendered"
    TRANSFERRED = "transferred"


class RentFrequency(str, Enum):
    """Rent payment frequency"""
    ANNUAL = "annual"
    SEMI_ANNUAL = "semi_annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"


class PaymentType(str, Enum):
    """Payment types"""
    RENT = "rent"
    SECURITY_DEPOSIT = "security_deposit"
    PENALTY = "penalty"
    LATE_FEE = "late_fee"
    DUPLICATE_KEY_CHARGE = "duplicate_key_charge"
    MISCELLANEOUS = "miscellaneous"


class PaymentMode(str, Enum):
    """Payment methods"""
    CASH = "cash"
    CHEQUE = "cheque"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CARD = "card"
    ONLINE = "online"


class PaymentStatus(str, Enum):
    """Payment processing status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class MaintenanceType(str, Enum):
    """Maintenance activity types"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    INSPECTION = "inspection"
    UPGRADE = "upgrade"


class MaintenanceStatus(str, Enum):
    """Maintenance task status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PENDING_PARTS = "pending_parts"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AccessorType(str, Enum):
    """Person accessing locker"""
    CUSTOMER = "customer"
    NOMINEE = "nominee"
    JOINT_HOLDER = "joint_holder"
    BANK_STAFF = "bank_staff"
    MAINTENANCE = "maintenance"
    LEGAL = "legal"


class AccessType(str, Enum):
    """Access scenario"""
    NORMAL = "normal"
    EMERGENCY = "emergency"
    FORCED_OPENING = "forced_opening"


class OperationMode(str, Enum):
    """Joint account operation mode"""
    SINGLE = "single"
    EITHER_OR_SURVIVOR = "either_or_survivor"
    JOINT = "joint"


# ==================== LOCKER MASTER SCHEMAS ====================

class LockerMasterBase(BaseModel):
    """Base schema for locker master"""
    locker_number: str = Field(..., min_length=1, max_length=50)
    locker_id: str = Field(..., min_length=1, max_length=50)
    locker_size: LockerSize
    
    # Dimensions
    dimensions_height: Optional[Decimal] = Field(None, ge=0)
    dimensions_width: Optional[Decimal] = Field(None, ge=0)
    dimensions_depth: Optional[Decimal] = Field(None, ge=0)
    
    # Location
    branch_id: uuid.UUID
    branch_name: Optional[str] = Field(None, max_length=200)
    vault_room: str = Field(..., min_length=1, max_length=100)
    floor: Optional[str] = Field(None, max_length=50)
    rack_number: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=50)
    
    # Type & Security
    locker_type: LockerType = LockerType.DUAL_KEY
    lock_type: Optional[LockType] = None
    lock_serial_number: Optional[str] = Field(None, max_length=100)
    
    # Financial
    annual_rent: Decimal = Field(..., gt=0)
    security_deposit: Decimal = Field(..., gt=0)
    initial_rent: Optional[Decimal] = Field(None, ge=0)
    base_rent: Optional[Decimal] = Field(None, ge=0)
    gst_rate: Decimal = Field(18.0, ge=0, le=100)
    
    # Status
    status: LockerStatus = LockerStatus.AVAILABLE
    is_available: bool = True
    
    # Maintenance
    installation_date: Optional[date] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_frequency_days: int = Field(180, ge=1)
    
    # Additional
    features: Optional[str] = None
    special_notes: Optional[str] = None
    
    # Insurance
    insurance_covered: bool = True
    insurance_amount: Optional[Decimal] = Field(None, ge=0)


class LockerMasterCreate(LockerMasterBase):
    """Schema for creating locker"""
    pass


class LockerMasterUpdate(BaseModel):
    """Schema for updating locker"""
    locker_number: Optional[str] = Field(None, min_length=1, max_length=50)
    locker_size: Optional[LockerSize] = None
    vault_room: Optional[str] = Field(None, min_length=1, max_length=100)
    floor: Optional[str] = None
    rack_number: Optional[str] = None
    position: Optional[str] = None
    lock_type: Optional[LockType] = None
    lock_serial_number: Optional[str] = None
    annual_rent: Optional[Decimal] = Field(None, gt=0)
    security_deposit: Optional[Decimal] = Field(None, gt=0)
    status: Optional[LockerStatus] = None
    is_available: Optional[bool] = None
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    special_notes: Optional[str] = None


class LockerMasterResponse(LockerMasterBase):
    """Schema for locker response"""
    id: uuid.UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class LockerMasterFilter(BaseModel):
    """Schema for filtering lockers"""
    locker_size: Optional[LockerSize] = None
    branch_id: Optional[uuid.UUID] = None
    vault_room: Optional[str] = None
    status: Optional[LockerStatus] = None
    is_available: Optional[bool] = None
    min_rent: Optional[Decimal] = None
    max_rent: Optional[Decimal] = None


# ==================== LOCKER ALLOCATION SCHEMAS ====================

class NomineeDetailsSchema(BaseModel):
    """Nominee information"""
    nominee_name: str = Field(..., min_length=2, max_length=200)
    nominee_relationship: str = Field(..., min_length=2, max_length=100)
    nominee_dob: date
    nominee_address: Optional[str] = None
    nominee_id_proof_type: Optional[str] = Field(None, max_length=50)
    nominee_id_proof_number: Optional[str] = Field(None, max_length=100)
    nominee_percentage: Decimal = Field(100.0, ge=0, le=100)


class LockerAllocationBase(BaseModel):
    """Base schema for locker allocation"""
    allocation_number: str = Field(..., min_length=1, max_length=50)
    agreement_number: str = Field(..., min_length=1, max_length=50)
    
    locker_id: uuid.UUID
    customer_id: uuid.UUID
    
    # Dates
    allocation_date: date
    agreement_start_date: date
    agreement_end_date: date
    
    # Financial
    annual_rent: Decimal = Field(..., gt=0)
    security_deposit: Decimal = Field(..., gt=0)
    rent_frequency: RentFrequency = RentFrequency.ANNUAL
    gst_applicable: bool = True
    gst_rate: Decimal = Field(18.0, ge=0, le=100)
    
    # Keys
    customer_key_number: Optional[str] = Field(None, max_length=50)
    bank_key_number: Optional[str] = Field(None, max_length=50)
    
    # Joint Holders
    joint_holder_1_id: Optional[uuid.UUID] = None
    joint_holder_2_id: Optional[uuid.UUID] = None
    operation_mode: OperationMode = OperationMode.SINGLE
    
    # Status
    status: AllocationStatus = AllocationStatus.ACTIVE
    auto_renewal: bool = False
    
    # Additional
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class LockerAllocationCreate(LockerAllocationBase):
    """Schema for creating allocation"""
    nominee_details: Optional[NomineeDetailsSchema] = None


class LockerAllocationUpdate(BaseModel):
    """Schema for updating allocation"""
    agreement_end_date: Optional[date] = None
    annual_rent: Optional[Decimal] = Field(None, gt=0)
    rent_frequency: Optional[RentFrequency] = None
    status: Optional[AllocationStatus] = None
    auto_renewal: Optional[bool] = None
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class LockerAllocationResponse(LockerAllocationBase):
    """Schema for allocation response"""
    id: uuid.UUID
    tenant_id: str
    
    # Payment Status
    security_deposit_paid: bool
    security_deposit_paid_date: Optional[date]
    security_deposit_receipt_number: Optional[str]
    
    # Rent Tracking
    rent_paid_upto_date: Optional[date]
    next_rent_due_date: Optional[date]
    outstanding_rent: Decimal
    total_rent_paid: Decimal
    total_penalties_paid: Decimal
    
    # Nominee
    nominee_name: Optional[str]
    nominee_relationship: Optional[str]
    nominee_dob: Optional[date]
    
    # Renewal
    renewal_count: int
    parent_allocation_id: Optional[uuid.UUID]
    
    # Closure
    closure_date: Optional[date]
    closure_reason: Optional[str]
    security_deposit_refunded: bool
    
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class LockerAllocationFilter(BaseModel):
    """Schema for filtering allocations"""
    customer_id: Optional[uuid.UUID] = None
    locker_id: Optional[uuid.UUID] = None
    status: Optional[AllocationStatus] = None
    branch_id: Optional[uuid.UUID] = None
    allocation_date_from: Optional[date] = None
    allocation_date_to: Optional[date] = None
    expiring_within_days: Optional[int] = None


class AllocationClosureRequest(BaseModel):
    """Request for closing allocation"""
    closure_date: date
    closure_reason: str = Field(..., min_length=5, max_length=200)
    refund_security_deposit: bool = True
    closure_charges: Decimal = Field(0, ge=0)
    final_settlement_amount: Optional[Decimal] = None
    remarks: Optional[str] = None


class AllocationRenewalRequest(BaseModel):
    """Request for renewing allocation"""
    new_end_date: date
    annual_rent: Decimal = Field(..., gt=0)
    adjust_security_deposit: bool = False
    additional_deposit: Decimal = Field(0, ge=0)
    remarks: Optional[str] = None


# ==================== RENT PAYMENT SCHEMAS ====================

class LockerRentPaymentBase(BaseModel):
    """Base schema for rent payment"""
    receipt_number: str = Field(..., min_length=1, max_length=50)
    transaction_id: Optional[str] = Field(None, max_length=100)
    
    allocation_id: uuid.UUID
    customer_id: uuid.UUID
    
    payment_date: date
    payment_type: PaymentType
    
    # Period
    period_from: Optional[date] = None
    period_to: Optional[date] = None
    
    # Amounts
    rent_amount: Decimal = Field(0, ge=0)
    gst_amount: Decimal = Field(0, ge=0)
    penalty_amount: Decimal = Field(0, ge=0)
    late_fee_amount: Decimal = Field(0, ge=0)
    other_charges: Decimal = Field(0, ge=0)
    total_amount: Decimal = Field(..., gt=0)
    
    # Payment Method
    payment_mode: PaymentMode
    
    # Instrument Details
    cheque_number: Optional[str] = Field(None, max_length=50)
    cheque_date: Optional[date] = None
    bank_name: Optional[str] = Field(None, max_length=200)
    bank_branch: Optional[str] = Field(None, max_length=200)
    transaction_reference: Optional[str] = Field(None, max_length=200)
    utr_number: Optional[str] = Field(None, max_length=100)
    
    # Status
    payment_status: PaymentStatus = PaymentStatus.COMPLETED
    
    remarks: Optional[str] = None


class LockerRentPaymentCreate(LockerRentPaymentBase):
    """Schema for creating rent payment"""
    pass


class LockerRentPaymentUpdate(BaseModel):
    """Schema for updating rent payment"""
    payment_status: Optional[PaymentStatus] = None
    clearance_date: Optional[date] = None
    remarks: Optional[str] = None


class LockerRentPaymentResponse(LockerRentPaymentBase):
    """Schema for rent payment response"""
    id: uuid.UUID
    tenant_id: str
    
    clearance_date: Optional[date]
    adjusted_against: Optional[str]
    adjustment_amount: Decimal
    
    received_by: Optional[uuid.UUID]
    collected_by: Optional[uuid.UUID]
    
    receipt_generated: bool
    receipt_generated_date: Optional[datetime]
    receipt_file_path: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class RentPaymentFilter(BaseModel):
    """Schema for filtering rent payments"""
    allocation_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    payment_type: Optional[PaymentType] = None
    payment_mode: Optional[PaymentMode] = None
    payment_status: Optional[PaymentStatus] = None
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None


class RentCalculationRequest(BaseModel):
    """Request for rent calculation"""
    allocation_id: uuid.UUID
    period_from: date
    period_to: date
    include_gst: bool = True
    include_penalty: bool = True


class RentCalculationResponse(BaseModel):
    """Response for rent calculation"""
    allocation_number: str
    period_from: date
    period_to: date
    days: int
    
    base_rent: float
    prorated_rent: float
    gst_amount: float
    penalty_amount: float
    late_fee: float
    
    total_amount: float
    
    gst_rate: float
    penalty_rate: float
    days_overdue: int


# ==================== MAINTENANCE SCHEMAS ====================

class LockerMaintenanceBase(BaseModel):
    """Base schema for maintenance"""
    maintenance_number: str = Field(..., min_length=1, max_length=50)
    work_order_number: Optional[str] = Field(None, max_length=50)
    
    locker_id: uuid.UUID
    
    maintenance_type: MaintenanceType
    maintenance_date: date
    scheduled_date: Optional[date] = None
    
    # Issue
    issue_reported: Optional[str] = None
    issue_category: Optional[str] = Field(None, max_length=100)
    priority: Priority = Priority.MEDIUM
    
    # Work
    work_description: str = Field(..., min_length=5)
    parts_replaced: Optional[str] = None
    service_provider: Optional[str] = Field(None, max_length=200)
    technician_name: Optional[str] = Field(None, max_length=200)
    technician_contact: Optional[str] = Field(None, max_length=20)
    
    # Status
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    
    # Costs
    labor_cost: Decimal = Field(0, ge=0)
    parts_cost: Decimal = Field(0, ge=0)
    other_charges: Decimal = Field(0, ge=0)
    total_cost: Decimal = Field(0, ge=0)
    
    # Follow-up
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None
    
    remarks: Optional[str] = None


class LockerMaintenanceCreate(LockerMaintenanceBase):
    """Schema for creating maintenance record"""
    pass


class LockerMaintenanceUpdate(BaseModel):
    """Schema for updating maintenance"""
    completion_date: Optional[date] = None
    status: Optional[MaintenanceStatus] = None
    work_description: Optional[str] = None
    labor_cost: Optional[Decimal] = Field(None, ge=0)
    parts_cost: Optional[Decimal] = Field(None, ge=0)
    other_charges: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    remarks: Optional[str] = None


class LockerMaintenanceResponse(LockerMaintenanceBase):
    """Schema for maintenance response"""
    id: uuid.UUID
    tenant_id: str
    
    completion_date: Optional[date]
    
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    payment_status: Optional[str]
    
    locker_unavailable_from: Optional[datetime]
    locker_unavailable_to: Optional[datetime]
    downtime_hours: Optional[Decimal]
    
    quality_check_done: bool
    quality_check_by: Optional[uuid.UUID]
    quality_check_date: Optional[date]
    quality_rating: Optional[int]
    
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class MaintenanceFilter(BaseModel):
    """Schema for filtering maintenance records"""
    locker_id: Optional[uuid.UUID] = None
    maintenance_type: Optional[MaintenanceType] = None
    status: Optional[MaintenanceStatus] = None
    priority: Optional[Priority] = None
    maintenance_date_from: Optional[date] = None
    maintenance_date_to: Optional[date] = None


# ==================== ACCESS LOG SCHEMAS ====================

class LockerAccessLogBase(BaseModel):
    """Base schema for access log"""
    access_log_number: str = Field(..., min_length=1, max_length=50)
    
    locker_id: uuid.UUID
    allocation_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    
    access_date: date
    access_time_in: datetime
    access_time_out: Optional[datetime] = None
    
    accessor_type: AccessorType
    accessor_name: str = Field(..., min_length=2, max_length=200)
    accessor_id_type: Optional[str] = Field(None, max_length=50)
    accessor_id_number: Optional[str] = Field(None, max_length=100)
    
    authorized_by: uuid.UUID
    
    purpose: str = Field(..., min_length=5, max_length=200)
    
    # Items
    items_deposited: Optional[str] = None
    items_retrieved: Optional[str] = None
    
    # Security
    biometric_verified: bool = False
    photo_captured: bool = False
    signature_captured: bool = False
    
    # Special
    emergency_access: bool = False
    court_order: bool = False
    court_order_number: Optional[str] = Field(None, max_length=100)
    
    access_type: AccessType = AccessType.NORMAL
    
    remarks: Optional[str] = None
    special_notes: Optional[str] = None


class LockerAccessLogCreate(LockerAccessLogBase):
    """Schema for creating access log"""
    pass


class LockerAccessLogUpdate(BaseModel):
    """Schema for updating access log"""
    access_time_out: Optional[datetime] = None
    items_deposited: Optional[str] = None
    items_retrieved: Optional[str] = None
    remarks: Optional[str] = None


class LockerAccessLogResponse(LockerAccessLogBase):
    """Schema for access log response"""
    id: uuid.UUID
    tenant_id: str
    
    witness_1_name: Optional[str]
    witness_1_employee_id: Optional[uuid.UUID]
    witness_2_name: Optional[str]
    witness_2_employee_id: Optional[uuid.UUID]
    
    photo_path: Optional[str]
    signature_path: Optional[str]
    authorization_document: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class AccessLogFilter(BaseModel):
    """Schema for filtering access logs"""
    locker_id: Optional[uuid.UUID] = None
    allocation_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    accessor_type: Optional[AccessorType] = None
    access_date_from: Optional[date] = None
    access_date_to: Optional[date] = None
    emergency_access: Optional[bool] = None


# ==================== ANALYTICS & DASHBOARD SCHEMAS ====================

class LockerOccupancyStats(BaseModel):
    """Locker occupancy statistics"""
    total_lockers: int
    available_lockers: int
    allocated_lockers: int
    under_maintenance: int
    blocked: int
    
    occupancy_rate: float  # Percentage
    
    by_size: Dict[str, int]
    by_branch: Dict[str, int]


class LockerRevenueStats(BaseModel):
    """Locker revenue statistics"""
    total_revenue: float
    rent_revenue: float
    deposit_revenue: float
    penalty_revenue: float
    other_revenue: float
    
    outstanding_rent: float
    expected_annual_revenue: float
    
    revenue_by_month: List[Dict[str, Any]]
    revenue_by_branch: List[Dict[str, Any]]


class LockerExpiringAllocations(BaseModel):
    """Expiring allocations alert"""
    allocation_id: uuid.UUID
    allocation_number: str
    customer_name: str
    locker_number: str
    agreement_end_date: date
    days_to_expiry: int
    outstanding_rent: float
    auto_renewal: bool


class LockerMaintenanceDue(BaseModel):
    """Maintenance due alert"""
    locker_id: uuid.UUID
    locker_number: str
    locker_size: str
    location: str
    last_maintenance_date: Optional[date]
    next_maintenance_date: date
    days_overdue: int


class LockerDashboardResponse(BaseModel):
    """Comprehensive locker dashboard"""
    occupancy: LockerOccupancyStats
    revenue: LockerRevenueStats
    expiring_allocations: List[LockerExpiringAllocations]
    maintenance_due: List[LockerMaintenanceDue]
    recent_allocations: int
    recent_payments: int
    recent_access_logs: int


class AvailabilityCheckRequest(BaseModel):
    """Request to check locker availability"""
    branch_id: Optional[uuid.UUID] = None
    locker_size: Optional[LockerSize] = None
    vault_room: Optional[str] = None
    max_rent: Optional[Decimal] = None


class AvailabilityCheckResponse(BaseModel):
    """Response with available lockers"""
    available_count: int
    available_lockers: List[LockerMasterResponse]


class BulkAllocationRequest(BaseModel):
    """Request for bulk locker allocation"""
    allocations: List[LockerAllocationCreate]


class BulkPaymentRequest(BaseModel):
    """Request for bulk rent payment"""
    payments: List[LockerRentPaymentCreate]


class CustomerType(str, Enum):
    """Customer relationship type"""
    PRIMARY = "primary"
    JOINT_HOLDER = "joint_holder"
    NOMINEE = "nominee"
    AUTHORIZED_SIGNATORY = "authorized_signatory"


class CustomerCategory(str, Enum):
    """Customer category for pricing"""
    REGULAR = "regular"
    PREMIUM = "premium"
    SENIOR_CITIZEN = "senior_citizen"
    STAFF = "staff"
    VIP = "vip"


class OperationMode(str, Enum):
    """Joint holder operation mode"""
    EITHER_OR_SURVIVOR = "either_or_survivor"
    FORMER_OR_SURVIVOR = "former_or_survivor"
    LATTER_OR_SURVIVOR = "latter_or_survivor"
    JOINT = "joint"
    ANYONE = "anyone"


class HolderType(str, Enum):
    """Joint holder hierarchy"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class KYCDocumentType(str, Enum):
    """KYC document types"""
    PAN_CARD = "pan_card"
    AADHAR_CARD = "aadhar_card"
    PASSPORT = "passport"
    VOTER_ID = "voter_id"
    DRIVING_LICENSE = "driving_license"
    BANK_STATEMENT = "bank_statement"
    UTILITY_BILL = "utility_bill"
    RENT_AGREEMENT = "rent_agreement"
    SALARY_SLIP = "salary_slip"
    INCOME_TAX_RETURN = "income_tax_return"
    PHOTO = "photo"
    SIGNATURE = "signature"
    ADDRESS_PROOF = "address_proof"
    IDENTITY_PROOF = "identity_proof"
    OTHER = "other"


class KYCDocumentCategory(str, Enum):
    """KYC document category"""
    IDENTITY_PROOF = "identity_proof"
    ADDRESS_PROOF = "address_proof"
    INCOME_PROOF = "income_proof"
    PHOTO = "photo"
    SIGNATURE = "signature"
    OTHER = "other"


class VerificationStatus(str, Enum):
    """Verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    RESUBMISSION_REQUIRED = "resubmission_required"


class AuthorizationType(str, Enum):
    """Authorization access type"""
    FULL_ACCESS = "full_access"
    LIMITED_ACCESS = "limited_access"
    EMERGENCY_ACCESS = "emergency_access"
    TEMPORARY_ACCESS = "temporary_access"


class AuthorizationDocumentType(str, Enum):
    """Legal authorization documents"""
    POWER_OF_ATTORNEY = "power_of_attorney"
    COURT_ORDER = "court_order"
    SUCCESSION_CERTIFICATE = "succession_certificate"
    WILL = "will"
    LETTER_OF_AUTHORITY = "letter_of_authority"


class ApprovalStatus(str, Enum):
    """Approval workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"
    EXPIRED = "expired"


# ==================== LOCKER CUSTOMER SCHEMAS ====================

class LockerCustomerBase(BaseModel):
    """Base schema for locker customer"""
    customer_id: uuid.UUID
    allocation_id: Optional[uuid.UUID] = None
    customer_type: CustomerType = CustomerType.PRIMARY
    
    # Personal details
    title: Optional[str] = None
    full_name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    
    # Contact
    mobile_number: str = Field(..., min_length=10, max_length=20)
    alternate_mobile: Optional[str] = None
    email: Optional[str] = None
    
    # Address
    current_address_line1: Optional[str] = None
    current_address_line2: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    current_country: str = "India"
    
    permanent_address_line1: Optional[str] = None
    permanent_address_line2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_pincode: Optional[str] = None
    permanent_country: str = "India"
    address_same_as_current: bool = True
    
    # Identification
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license_number: Optional[str] = None
    voter_id_number: Optional[str] = None
    
    # Employment
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    employer_address: Optional[str] = None
    annual_income: Optional[Decimal] = None
    income_source: Optional[str] = None
    
    # Banking
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_ifsc: Optional[str] = None
    
    # Purpose
    locker_purpose: Optional[str] = None
    locker_purpose_details: Optional[str] = None
    estimated_value_of_contents: Optional[Decimal] = None
    insurance_required: bool = False
    insurance_amount: Optional[Decimal] = None
    
    # Category
    customer_category: CustomerCategory = CustomerCategory.REGULAR
    is_senior_citizen: bool = False
    is_staff_member: bool = False
    is_premium_customer: bool = False
    
    # Relationship
    relationship_with_primary: Optional[str] = None
    
    # Communication
    preferred_language: str = "English"
    sms_alerts: bool = True
    email_alerts: bool = True
    whatsapp_alerts: bool = False
    
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class LockerCustomerCreate(LockerCustomerBase):
    """Schema for creating locker customer"""
    pass


class LockerCustomerUpdate(BaseModel):
    """Schema for updating locker customer"""
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    current_address_line1: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[Decimal] = None
    customer_category: Optional[CustomerCategory] = None
    remarks: Optional[str] = None


class LockerCustomerResponse(LockerCustomerBase):
    """Schema for locker customer response"""
    id: uuid.UUID
    locker_customer_id: str
    status: str
    verification_status: VerificationStatus
    verification_date: Optional[date] = None
    photo_path: Optional[str] = None
    signature_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== JOINT HOLDER SCHEMAS ====================

class LockerJointHolderBase(BaseModel):
    """Base schema for joint holder"""
    allocation_id: uuid.UUID
    locker_customer_id: uuid.UUID
    customer_id: uuid.UUID
    
    holder_type: HolderType
    holder_sequence: int = Field(..., ge=1)
    operation_mode: OperationMode
    
    # Authority
    can_operate_alone: bool = False
    requires_joint_operation: bool = False
    
    # Permissions
    can_deposit: bool = True
    can_retrieve: bool = True
    can_make_payments: bool = True
    can_surrender: bool = False
    can_add_nominee: bool = False
    
    # Agreement
    agreement_accepted: bool = False
    agreement_accepted_date: Optional[date] = None
    
    # Survivorship
    survivorship_rights: bool = True
    inheritance_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class LockerJointHolderCreate(LockerJointHolderBase):
    """Schema for creating joint holder"""
    pass


class LockerJointHolderUpdate(BaseModel):
    """Schema for updating joint holder"""
    operation_mode: Optional[OperationMode] = None
    can_operate_alone: Optional[bool] = None
    can_deposit: Optional[bool] = None
    can_retrieve: Optional[bool] = None
    can_make_payments: Optional[bool] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class LockerJointHolderResponse(LockerJointHolderBase):
    """Schema for joint holder response"""
    id: uuid.UUID
    joint_holder_id: str
    status: str
    activation_date: Optional[date] = None
    deactivation_date: Optional[date] = None
    signature_path: Optional[str] = None
    photo_path: Optional[str] = None
    specimen_signature_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== KYC DOCUMENT SCHEMAS ====================

class LockerKYCBase(BaseModel):
    """Base schema for KYC document"""
    locker_customer_id: uuid.UUID
    allocation_id: Optional[uuid.UUID] = None
    
    document_type: KYCDocumentType
    document_category: KYCDocumentCategory
    document_number: Optional[str] = None
    document_name: Optional[str] = None
    
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    
    document_file_path: str
    document_file_type: Optional[str] = None
    document_file_size: Optional[int] = None
    original_filename: Optional[str] = None
    
    is_mandatory: bool = True
    remarks: Optional[str] = None


class LockerKYCCreate(LockerKYCBase):
    """Schema for uploading KYC document"""
    pass


class LockerKYCUpdate(BaseModel):
    """Schema for updating KYC document"""
    document_number: Optional[str] = None
    expiry_date: Optional[date] = None
    verification_status: Optional[VerificationStatus] = None
    verification_remarks: Optional[str] = None
    remarks: Optional[str] = None


class LockerKYCResponse(LockerKYCBase):
    """Schema for KYC document response"""
    id: uuid.UUID
    kyc_id: str
    verification_status: VerificationStatus
    verified_by: Optional[uuid.UUID] = None
    verification_date: Optional[date] = None
    verification_remarks: Optional[str] = None
    is_expired: bool
    kyc_compliance: bool
    aml_checked: bool
    aml_status: Optional[str] = None
    version_number: int
    is_latest_version: bool
    upload_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== NOMINEE SCHEMAS ====================

class LockerNomineeBase(BaseModel):
    """Base schema for nominee"""
    locker_customer_id: uuid.UUID
    allocation_id: uuid.UUID
    
    nominee_sequence: int = Field(..., ge=1)
    is_primary_nominee: bool = False
    
    # Personal details
    title: Optional[str] = None
    full_name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: date
    gender: Optional[str] = None
    relationship_with_customer: str
    
    # Contact
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    
    # Address
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"
    
    # Identification
    id_proof_type: str
    id_proof_number: str
    
    # Share
    nominee_percentage: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    
    # Minor details
    is_minor: bool = False
    guardian_name: Optional[str] = None
    guardian_relationship: Optional[str] = None
    guardian_id_proof_type: Optional[str] = None
    guardian_id_proof_number: Optional[str] = None
    guardian_address: Optional[str] = None
    guardian_mobile: Optional[str] = None
    
    nomination_date: date
    
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class LockerNomineeCreate(LockerNomineeBase):
    """Schema for creating nominee"""
    pass


class LockerNomineeUpdate(BaseModel):
    """Schema for updating nominee"""
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    nominee_percentage: Optional[Decimal] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class LockerNomineeResponse(LockerNomineeBase):
    """Schema for nominee response"""
    id: uuid.UUID
    nominee_id: str
    status: str
    verification_status: VerificationStatus
    verified_by: Optional[uuid.UUID] = None
    verification_date: Optional[date] = None
    id_proof_document_path: Optional[str] = None
    photo_path: Optional[str] = None
    nomination_form_path: Optional[str] = None
    nomination_accepted: bool
    nomination_accepted_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



# ==================== RENT STRUCTURE SCHEMAS ====================

class LockerRentStructureBase(BaseModel):
    """Base schema for rent structure"""
    branch_id: Optional[uuid.UUID] = None
    branch_name: Optional[str] = None
    locker_size: LockerSize
    location_type: str = "standard"
    customer_category: CustomerCategory = CustomerCategory.REGULAR
    
    # Rent components
    base_rent_annual: Decimal = Field(..., gt=0)
    base_rent_semi_annual: Optional[Decimal] = None
    base_rent_quarterly: Optional[Decimal] = None
    base_rent_monthly: Optional[Decimal] = None
    
    # Location premium
    location_premium_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    location_premium_amount: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Security deposit
    security_deposit_amount: Decimal = Field(..., gt=0)
    security_deposit_refundable: bool = True
    
    # GST
    gst_applicable: bool = True
    gst_rate: Decimal = Field(default=Decimal("18.0"), ge=0, le=100)
    gst_on_rent: bool = True
    gst_on_deposit: bool = False
    
    # Discounts
    discount_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    discount_reason: Optional[str] = None
    advance_payment_discount: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    
    # Penalties
    late_payment_penalty_applicable: bool = True
    late_payment_grace_days: int = Field(default=15, ge=0)
    late_payment_penalty_percentage: Decimal = Field(default=Decimal("2.0"), ge=0)
    late_payment_penalty_flat_amount: Decimal = Field(default=Decimal("0"), ge=0)
    penalty_calculation_method: str = "percentage"
    
    # Other charges
    duplicate_key_charges: Decimal = Field(default=Decimal("500"), ge=0)
    locker_breaking_charges: Decimal = Field(default=Decimal("2000"), ge=0)
    transfer_charges: Decimal = Field(default=Decimal("500"), ge=0)
    closure_charges: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Limits
    minimum_rent_period_months: int = Field(default=12, ge=1)
    maximum_rent_advance_years: int = Field(default=3, ge=1)
    
    # Validity
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True
    
    # Special rules
    rent_waiver_applicable: bool = False
    rent_waiver_conditions: Optional[str] = None
    
    remarks: Optional[str] = None


class LockerRentStructureCreate(LockerRentStructureBase):
    """Schema for creating rent structure"""
    pass


class LockerRentStructureUpdate(BaseModel):
    """Schema for updating rent structure"""
    base_rent_annual: Optional[Decimal] = None
    security_deposit_amount: Optional[Decimal] = None
    gst_rate: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    late_payment_penalty_percentage: Optional[Decimal] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class LockerRentStructureResponse(LockerRentStructureBase):
    """Schema for rent structure response"""
    id: uuid.UUID
    rent_structure_id: str
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[date] = None
    approval_remarks: Optional[str] = None
    version_number: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RentCalculationRequest(BaseModel):
    """Schema for rent calculation request"""
    locker_size: LockerSize
    branch_id: Optional[uuid.UUID] = None
    customer_category: CustomerCategory = CustomerCategory.REGULAR
    rent_frequency: RentFrequency = RentFrequency.ANNUAL
    advance_payment: bool = False
    period_from: date
    period_to: date


class RentCalculationResponse(BaseModel):
    """Schema for rent calculation response"""
    base_rent: Decimal
    location_premium: Decimal
    discount_amount: Decimal
    subtotal: Decimal
    gst_amount: Decimal
    total_amount: Decimal
    security_deposit: Decimal
    total_payable: Decimal
    rent_frequency: RentFrequency
    period_months: int
    gst_rate: Decimal
    discount_percentage: Decimal


# ==================== AUTHORIZATION SCHEMAS ====================

class LockerAuthorizationBase(BaseModel):
    """Base schema for authorization"""
    locker_customer_id: uuid.UUID
    allocation_id: uuid.UUID
    
    authorized_person_type: str
    authorized_person_name: str
    authorized_person_customer_id: Optional[uuid.UUID] = None
    
    # Contact
    mobile_number: str
    email: Optional[str] = None
    
    # Identification
    id_proof_type: str
    id_proof_number: str
    
    # Address
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    
    # Authorization details
    authorization_type: AuthorizationType
    
    # Permissions
    can_deposit_items: bool = True
    can_retrieve_items: bool = True
    can_view_contents: bool = True
    can_make_rent_payments: bool = True
    can_renew_locker: bool = False
    can_surrender_locker: bool = False
    can_add_joint_holder: bool = False
    can_change_nominee: bool = False
    
    # Time restrictions
    authorization_valid_from: date
    authorization_valid_to: Optional[date] = None
    is_permanent: bool = False
    access_days_allowed: Optional[str] = None
    access_time_from: Optional[str] = None
    access_time_to: Optional[str] = None
    
    # Legal documents
    authorization_document_type: Optional[AuthorizationDocumentType] = None
    authorization_document_path: str
    authorization_document_number: Optional[str] = None
    authorization_document_date: Optional[date] = None
    
    # Witness
    witness_1_name: Optional[str] = None
    witness_1_id_proof: Optional[str] = None
    witness_2_name: Optional[str] = None
    witness_2_id_proof: Optional[str] = None
    
    # Emergency contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_mobile: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    
    special_conditions: Optional[str] = None
    remarks: Optional[str] = None


class LockerAuthorizationCreate(LockerAuthorizationBase):
    """Schema for creating authorization"""
    pass


class LockerAuthorizationUpdate(BaseModel):
    """Schema for updating authorization"""
    authorization_type: Optional[AuthorizationType] = None
    can_deposit_items: Optional[bool] = None
    can_retrieve_items: Optional[bool] = None
    can_make_rent_payments: Optional[bool] = None
    authorization_valid_to: Optional[date] = None
    approval_status: Optional[ApprovalStatus] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class LockerAuthorizationResponse(LockerAuthorizationBase):
    """Schema for authorization response"""
    id: uuid.UUID
    authorization_id: str
    approval_status: ApprovalStatus
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[date] = None
    approval_remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    status: str
    signature_specimen_path: Optional[str] = None
    photo_path: Optional[str] = None
    signature_verified: bool
    last_used_date: Optional[date] = None
    total_access_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuthorizationApprovalRequest(BaseModel):
    """Schema for approving/rejecting authorization"""
    approval_status: ApprovalStatus
    approval_remarks: Optional[str] = None
    rejection_reason: Optional[str] = None


class AuthorizationRevokeRequest(BaseModel):
    """Schema for revoking authorization"""
    revocation_reason: str
    revocation_document_path: Optional[str] = None


# ==================== CUSTOMER ALLOCATION REQUEST ====================

class CustomerAllocationRequest(BaseModel):
    """Complete customer allocation request with all details"""
    # Locker selection
    locker_id: uuid.UUID
    
    # Primary customer
    primary_customer: LockerCustomerCreate
    
    # Joint holders (optional)
    joint_holders: Optional[List[LockerJointHolderCreate]] = []
    
    # Nominees
    nominees: List[LockerNomineeCreate] = []
    
    # KYC documents
    kyc_documents: Optional[List[str]] = []  # Document paths
    
    # Agreement terms
    allocation_date: date
    agreement_start_date: date
    agreement_end_date: date
    rent_frequency: RentFrequency
    annual_rent: Decimal
    security_deposit: Decimal
    
    # Keys
    customer_key_number: Optional[str] = None
    bank_key_number: Optional[str] = None
    
    # Special terms
    auto_renewal: bool = False
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class CustomerAllocationResponse(BaseModel):
    """Complete allocation response"""
    allocation_id: uuid.UUID
    allocation_number: str
    locker_customer: LockerCustomerResponse
    joint_holders: List[LockerJointHolderResponse] = []
    nominees: List[LockerNomineeResponse] = []
    kyc_status: str
    approval_status: str
    created_at: datetime


# ==================== BULK OPERATIONS ====================

class BulkKYCUploadRequest(BaseModel):
    """Schema for bulk KYC upload"""
    locker_customer_id: uuid.UUID
    documents: List[LockerKYCCreate]


class BulkKYCUploadResponse(BaseModel):
    """Schema for bulk KYC upload response"""
    total_uploaded: int
    successful: int
    failed: int
    kyc_documents: List[LockerKYCResponse]
    errors: Optional[List[Dict[str, Any]]] = []


class NomineePercentageValidation(BaseModel):
    """Schema for validating nominee percentages"""
    allocation_id: uuid.UUID
    nominees: List[Dict[str, Any]]
    
    @root_validator
    def validate_total_percentage(cls, values):
        """Validate that total nominee percentage equals 100"""
        nominees = values.get('nominees', [])
        if nominees:
            total = sum(n.get('nominee_percentage', 0) for n in nominees)
            if total != 100:
                raise ValueError(f"Total nominee percentage must be 100%, got {total}%")
        return values


# ==================== CUSTOMER SEARCH & FILTER ====================

class LockerCustomerSearchRequest(BaseModel):
    """Schema for searching locker customers"""
    search_query: Optional[str] = None
    customer_category: Optional[CustomerCategory] = None
    verification_status: Optional[VerificationStatus] = None
    status: Optional[str] = None
    is_senior_citizen: Optional[bool] = None
    is_premium_customer: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class LockerCustomerListResponse(BaseModel):
    """Schema for customer list response"""
    total: int
    page: int
    page_size: int
    customers: List[LockerCustomerResponse]


# ==================== ANALYTICS & REPORTS ====================

class CustomerAnalytics(BaseModel):
    """Customer analytics summary"""
    total_customers: int
    by_category: Dict[str, int]
    by_verification_status: Dict[str, int]
    senior_citizens: int
    premium_customers: int
    kyc_pending: int
    kyc_completed: int


class JointHolderAnalytics(BaseModel):
    """Joint holder analytics"""
    total_joint_accounts: int
    by_operation_mode: Dict[str, int]
    active_joint_holders: int
    inactive_joint_holders: int


class NomineeAnalytics(BaseModel):
    """Nominee analytics"""
    total_nominees: int
    allocations_with_nominees: int
    allocations_without_nominees: int
    minor_nominees: int
    verified_nominees: int
    pending_verification: int


# ==================== LOCKER APPLICATION ENUMS ====================

class ApplicationType(str, Enum):
    """Locker application type"""
    NEW = "new"
    RENEWAL = "renewal"
    TRANSFER = "transfer"
    ADDITIONAL = "additional"


class ApplicationStatus(str, Enum):
    """Application lifecycle status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    PENDING_DOCUMENTS = "pending_documents"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    WAITING_LIST = "waiting_list"
    ALLOCATED = "allocated"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApplicationStage(str, Enum):
    """Application processing stage"""
    DOCUMENT_VERIFICATION = "document_verification"
    CREDIT_CHECK = "credit_check"
    MANAGER_REVIEW = "manager_review"
    FINAL_APPROVAL = "final_approval"
    ALLOCATION = "allocation"


class WaitingListStatus(str, Enum):
    """Waiting list entry status"""
    ACTIVE = "active"
    NOTIFIED = "notified"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    ALLOCATED = "allocated"
    CANCELLED = "cancelled"


class HandoverType(str, Enum):
    """Key handover type"""
    INITIAL_ISSUE = "initial_issue"
    REPLACEMENT = "replacement"
    DUPLICATE = "duplicate"
    RETURN = "return"
    SURRENDER = "surrender"


class KeyType(str, Enum):
    """Key physical type"""
    PHYSICAL = "physical"
    DIGITAL = "digital"


class KeyStatus(str, Enum):
    """Key status"""
    ACTIVE = "active"
    RETURNED = "returned"
    LOST = "lost"
    REPLACED = "replaced"
    CANCELLED = "cancelled"


class AgreementType(str, Enum):
    """Agreement type"""
    NEW = "new"
    RENEWAL = "renewal"
    MODIFICATION = "modification"
    TRANSFER = "transfer"


class AgreementStatus(str, Enum):
    """Agreement lifecycle status"""
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    PARTIALLY_SIGNED = "partially_signed"
    EXECUTED = "executed"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class SignatureType(str, Enum):
    """Signature capture type"""
    PHYSICAL = "physical"
    DIGITAL = "digital"
    E_SIGN = "e_sign"


# ==================== LOCKER APPLICATION SCHEMAS ====================

class LockerApplicationBase(BaseModel):
    """Base schema for locker application"""
    customer_id: uuid.UUID
    locker_customer_id: Optional[uuid.UUID] = None
    branch_id: uuid.UUID
    
    application_date: date
    application_type: ApplicationType = ApplicationType.NEW
    
    # Locker preferences
    preferred_locker_size: LockerSize
    alternate_size_1: Optional[LockerSize] = None
    alternate_size_2: Optional[LockerSize] = None
    preferred_location: Optional[str] = None
    preferred_locker_id: Optional[uuid.UUID] = None
    
    # Purpose
    purpose_of_locker: str = Field(..., min_length=2)
    purpose_details: Optional[str] = None
    estimated_value_of_contents: Optional[Decimal] = None
    insurance_required: bool = False
    insurance_coverage_amount: Optional[Decimal] = None
    
    # Financial
    proposed_rent_frequency: RentFrequency = RentFrequency.ANNUAL
    willing_to_pay_advance: bool = False
    advance_payment_months: int = Field(default=12, ge=1)
    
    # Priority factors
    is_existing_customer: bool = False
    existing_customer_since: Optional[date] = None
    customer_category: CustomerCategory = CustomerCategory.REGULAR
    deposit_with_bank: Decimal = Field(default=Decimal("0"), ge=0)
    loan_accounts: int = Field(default=0, ge=0)
    credit_score: Optional[int] = None
    
    # Special requirements
    special_requirements: Optional[str] = None
    remarks: Optional[str] = None


class LockerApplicationCreate(LockerApplicationBase):
    """Schema for creating locker application"""
    pass


class LockerApplicationUpdate(BaseModel):
    """Schema for updating application"""
    preferred_locker_size: Optional[LockerSize] = None
    alternate_size_1: Optional[LockerSize] = None
    alternate_size_2: Optional[LockerSize] = None
    purpose_details: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    current_stage: Optional[ApplicationStage] = None
    special_requirements: Optional[str] = None
    remarks: Optional[str] = None


class LockerApplicationResponse(LockerApplicationBase):
    """Schema for application response"""
    id: uuid.UUID
    application_number: str
    status: ApplicationStatus
    current_stage: ApplicationStage
    
    # Priority scoring
    priority_score: int
    priority_reason: Optional[str] = None
    
    # Workflow tracking
    submitted_by: Optional[uuid.UUID] = None
    reviewed_by: Optional[uuid.UUID] = None
    review_date: Optional[date] = None
    review_remarks: Optional[str] = None
    
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[date] = None
    approval_remarks: Optional[str] = None
    approval_level: int
    
    rejected_by: Optional[uuid.UUID] = None
    rejection_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    
    # Waiting list
    added_to_waiting_list: bool
    waiting_list_date: Optional[date] = None
    waiting_list_position: Optional[int] = None
    expected_availability_date: Optional[date] = None
    
    # Allocation
    allocated_locker_id: Optional[uuid.UUID] = None
    allocation_id: Optional[uuid.UUID] = None
    allocation_date: Optional[date] = None
    
    # Documents
    application_form_path: Optional[str] = None
    supporting_documents_path: Optional[str] = None
    kyc_verified: bool
    kyc_verification_date: Optional[date] = None
    
    # Communication
    notification_sent: bool
    last_notification_date: Optional[date] = None
    follow_up_required: bool
    follow_up_date: Optional[date] = None
    
    # Validity
    application_valid_till: Optional[date] = None
    is_expired: bool
    
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationReviewRequest(BaseModel):
    """Schema for application review"""
    review_remarks: str
    kyc_verified: bool = False
    credit_check_done: bool = False
    move_to_stage: Optional[ApplicationStage] = None


class ApplicationApprovalRequest(BaseModel):
    """Schema for application approval"""
    approved: bool
    approval_remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    add_to_waiting_list: bool = False


class ApplicationAllocationRequest(BaseModel):
    """Schema for allocating locker to application"""
    locker_id: uuid.UUID
    allocation_date: date
    agreement_start_date: date
    agreement_end_date: date
    annual_rent: Decimal
    security_deposit: Decimal


class ApplicationFilter(BaseModel):
    """Schema for filtering applications"""
    customer_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None
    application_type: Optional[ApplicationType] = None
    status: Optional[ApplicationStatus] = None
    current_stage: Optional[ApplicationStage] = None
    preferred_locker_size: Optional[LockerSize] = None
    application_date_from: Optional[date] = None
    application_date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ==================== WAITING LIST SCHEMAS ====================

class LockerWaitingListBase(BaseModel):
    """Base schema for waiting list entry"""
    application_id: uuid.UUID
    customer_id: uuid.UUID
    branch_id: uuid.UUID
    
    added_date: date
    locker_size_requested: LockerSize
    
    # Priority calculation
    base_priority: int = Field(default=0, ge=0)
    existing_customer_bonus: int = Field(default=0, ge=0)
    deposit_size_bonus: int = Field(default=0, ge=0)
    senior_citizen_bonus: int = Field(default=0, ge=0)
    staff_bonus: int = Field(default=0, ge=0)
    waiting_time_bonus: int = Field(default=0, ge=0)
    
    # Auto-allocation settings
    auto_allocate_enabled: bool = True
    accept_alternate_size: bool = False
    max_rent_willing: Optional[Decimal] = None
    
    # Contact preferences
    preferred_contact_method: str = "email"
    preferred_contact_time: Optional[str] = None
    contact_mobile: Optional[str] = None
    contact_email: Optional[str] = None
    
    special_requirements: Optional[str] = None
    remarks: Optional[str] = None


class LockerWaitingListCreate(LockerWaitingListBase):
    """Schema for creating waiting list entry"""
    pass


class LockerWaitingListUpdate(BaseModel):
    """Schema for updating waiting list entry"""
    status: Optional[WaitingListStatus] = None
    auto_allocate_enabled: Optional[bool] = None
    accept_alternate_size: Optional[bool] = None
    max_rent_willing: Optional[Decimal] = None
    preferred_contact_method: Optional[str] = None
    remarks: Optional[str] = None


class LockerWaitingListResponse(LockerWaitingListBase):
    """Schema for waiting list response"""
    id: uuid.UUID
    waiting_list_id: str
    position_in_queue: int
    priority_score: int
    priority_factors: Optional[str] = None
    status: WaitingListStatus
    
    # Notification tracking
    notification_sent: bool
    notification_sent_date: Optional[date] = None
    notification_method: Optional[str] = None
    response_deadline: Optional[date] = None
    customer_response: Optional[str] = None
    customer_response_date: Optional[date] = None
    
    # Offer details
    locker_offered_id: Optional[uuid.UUID] = None
    offer_made_date: Optional[date] = None
    offer_valid_till: Optional[date] = None
    offer_declined_reason: Optional[str] = None
    
    # Allocation
    allocated: bool
    allocation_id: Optional[uuid.UUID] = None
    allocation_date: Optional[date] = None
    removed_date: Optional[date] = None
    removal_reason: Optional[str] = None
    
    # Estimated waiting
    estimated_wait_days: Optional[int] = None
    estimated_allocation_date: Optional[date] = None
    average_turnover_rate: Optional[Decimal] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WaitingListOfferRequest(BaseModel):
    """Schema for making offer to waiting list customer"""
    locker_id: uuid.UUID
    offer_valid_days: int = Field(default=7, ge=1)
    notification_method: str = "email"


class WaitingListOfferResponse(BaseModel):
    """Schema for customer response to offer"""
    accepted: bool
    response_date: date
    declined_reason: Optional[str] = None


class WaitingListFilter(BaseModel):
    """Schema for filtering waiting list"""
    branch_id: Optional[uuid.UUID] = None
    locker_size_requested: Optional[LockerSize] = None
    status: Optional[WaitingListStatus] = None
    min_priority_score: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class WaitingListAnalytics(BaseModel):
    """Waiting list analytics"""
    total_waiting: int
    by_size: Dict[str, int]
    by_branch: Dict[str, int]
    average_wait_days: int
    longest_wait_days: int
    offers_made: int
    offers_accepted: int
    offers_declined: int


# ==================== KEY HANDOVER SCHEMAS ====================

class LockerKeyHandoverBase(BaseModel):
    """Base schema for key handover"""
    allocation_id: uuid.UUID
    locker_id: uuid.UUID
    customer_id: uuid.UUID
    
    handover_type: HandoverType
    handover_date: date
    
    # Customer key
    customer_key_number: str = Field(..., min_length=1)
    customer_key_type: KeyType = KeyType.PHYSICAL
    
    # Bank master key
    bank_key_number: str = Field(..., min_length=1)
    bank_key_location: Optional[str] = None
    bank_key_custodian: Optional[uuid.UUID] = None
    
    # Dual key policy
    requires_dual_key: bool = True
    dual_key_policy: Optional[str] = None
    
    # Duplicate keys
    duplicate_key_issued: bool = False
    duplicate_key_number: Optional[str] = None
    duplicate_key_reason: Optional[str] = None
    duplicate_key_charges: Decimal = Field(default=Decimal("0"), ge=0)
    duplicate_key_authorization: Optional[str] = None
    number_of_duplicate_keys: int = Field(default=0, ge=0)
    
    # Key recipient
    received_by: str = Field(..., min_length=2)
    received_by_relation: str
    received_by_id_proof: str
    received_by_id_number: str
    
    # Witness
    witness_1_name: str
    witness_1_employee_id: uuid.UUID
    witness_2_name: Optional[str] = None
    witness_2_employee_id: Optional[uuid.UUID] = None
    
    issued_by: uuid.UUID
    issued_by_name: Optional[str] = None
    
    # Biometric & photos
    biometric_captured: bool = False
    biometric_type: Optional[str] = None
    biometric_reference: Optional[str] = None
    
    # Key testing
    key_tested: bool = False
    key_working_condition: Optional[str] = None
    lock_tested: bool = False
    lock_condition: Optional[str] = None
    
    # Security deposit
    key_security_deposit: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Acknowledgment
    customer_acknowledgment: bool = False
    acknowledgment_date: Optional[date] = None
    
    special_instructions: Optional[str] = None
    remarks: Optional[str] = None


class LockerKeyHandoverCreate(LockerKeyHandoverBase):
    """Schema for creating key handover"""
    pass


class LockerKeyHandoverUpdate(BaseModel):
    """Schema for updating key handover"""
    customer_key_returned: bool = False
    customer_key_return_date: Optional[date] = None
    customer_key_condition: Optional[str] = None
    status: Optional[KeyStatus] = None
    remarks: Optional[str] = None


class LockerKeyHandoverResponse(LockerKeyHandoverBase):
    """Schema for key handover response"""
    id: uuid.UUID
    handover_id: str
    key_register_number: str
    status: KeyStatus
    
    # Key status
    customer_key_issued: bool
    customer_key_issue_date: Optional[date] = None
    customer_key_returned: bool
    customer_key_return_date: Optional[date] = None
    customer_key_condition: Optional[str] = None
    
    bank_key_status: str
    
    # Duplicate keys tracking
    duplicate_keys_list: Optional[str] = None
    
    # Documents
    recipient_photo_path: Optional[str] = None
    recipient_signature_path: Optional[str] = None
    witness_1_signature_path: Optional[str] = None
    witness_2_signature_path: Optional[str] = None
    acknowledgment_form_path: Optional[str] = None
    
    # Lost key handling
    key_lost: bool
    key_lost_date: Optional[date] = None
    key_lost_reported_date: Optional[date] = None
    fir_number: Optional[str] = None
    indemnity_bond_executed: bool
    indemnity_bond_path: Optional[str] = None
    locker_breaking_required: bool
    locker_breaking_date: Optional[date] = None
    locker_breaking_charges: Optional[Decimal] = None
    
    # Deposit refund
    deposit_refunded: bool
    deposit_refund_date: Optional[date] = None
    deposit_refund_amount: Optional[Decimal] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KeyLostReportRequest(BaseModel):
    """Schema for reporting lost key"""
    key_lost_date: date
    fir_number: Optional[str] = None
    indemnity_bond_path: str
    duplicate_key_required: bool = True
    locker_breaking_required: bool = False


class KeyReturnRequest(BaseModel):
    """Schema for key return"""
    return_date: date
    key_condition: str
    all_duplicate_keys_returned: bool = True
    remarks: Optional[str] = None


class KeyHandoverFilter(BaseModel):
    """Schema for filtering key handovers"""
    allocation_id: Optional[uuid.UUID] = None
    locker_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    handover_type: Optional[HandoverType] = None
    status: Optional[KeyStatus] = None
    key_lost: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ==================== AGREEMENT SCHEMAS ====================

class LockerAgreementBase(BaseModel):
    """Base schema for locker agreement"""
    allocation_id: uuid.UUID
    locker_id: uuid.UUID
    customer_id: uuid.UUID
    application_id: Optional[uuid.UUID] = None
    
    agreement_type: AgreementType = AgreementType.NEW
    parent_agreement_id: Optional[uuid.UUID] = None
    
    agreement_date: date
    agreement_start_date: date
    agreement_end_date: date
    agreement_duration_months: int = Field(..., ge=1)
    
    # Template
    template_id: Optional[str] = None
    template_name: Optional[str] = None
    template_version: Optional[str] = None
    
    # Terms & conditions
    terms_and_conditions: str = Field(..., min_length=10)
    dos_and_donts: str = Field(..., min_length=10)
    bank_liability_clause: str = Field(..., min_length=10)
    insurance_clause: Optional[str] = None
    access_rules: str = Field(..., min_length=10)
    
    # Custom clauses
    special_terms: Optional[str] = None
    additional_conditions: Optional[str] = None
    
    # Financial terms
    annual_rent: Decimal = Field(..., gt=0)
    security_deposit: Decimal = Field(..., gt=0)
    rent_frequency: RentFrequency = RentFrequency.ANNUAL
    rent_escalation_clause: Optional[str] = None
    rent_escalation_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    rent_escalation_frequency_years: int = Field(default=3, ge=1)
    
    # Signatures required
    joint_holder_signature_required: bool = False
    bank_authorized_signatory: uuid.UUID
    
    # Witness
    witness_1_name: Optional[str] = None
    witness_2_name: Optional[str] = None
    
    # Document
    agreement_document_path: str
    agreement_document_type: str = "pdf"
    
    # Execution
    execution_location: Optional[str] = None
    
    # Stamp & notary
    stamp_paper_required: bool = False
    stamp_paper_value: Optional[Decimal] = None
    stamp_paper_number: Optional[str] = None
    stamp_paper_date: Optional[date] = None
    notarized: bool = False
    notary_name: Optional[str] = None
    notary_registration_number: Optional[str] = None
    notary_date: Optional[date] = None
    
    # Renewal
    auto_renewal_enabled: bool = False
    renewal_notice_period_days: int = Field(default=30, ge=1)
    
    # Termination
    notice_period_days: int = Field(default=30, ge=1)
    
    special_instructions: Optional[str] = None
    internal_notes: Optional[str] = None
    remarks: Optional[str] = None


class LockerAgreementCreate(LockerAgreementBase):
    """Schema for creating locker agreement"""
    pass


class LockerAgreementUpdate(BaseModel):
    """Schema for updating agreement"""
    agreement_end_date: Optional[date] = None
    annual_rent: Optional[Decimal] = None
    special_terms: Optional[str] = None
    status: Optional[AgreementStatus] = None
    remarks: Optional[str] = None


class LockerAgreementResponse(LockerAgreementBase):
    """Schema for agreement response"""
    id: uuid.UUID
    agreement_number: str
    agreement_version: str
    status: AgreementStatus
    
    # Signatures
    customer_signature_path: Optional[str] = None
    customer_signed: bool
    customer_signature_date: Optional[date] = None
    customer_signature_type: Optional[SignatureType] = None
    customer_digital_signature_id: Optional[str] = None
    customer_ip_address: Optional[str] = None
    
    joint_holder_1_signature_path: Optional[str] = None
    joint_holder_1_signed: bool
    joint_holder_1_signature_date: Optional[date] = None
    
    joint_holder_2_signature_path: Optional[str] = None
    joint_holder_2_signed: bool
    joint_holder_2_signature_date: Optional[date] = None
    
    bank_signature_path: Optional[str] = None
    bank_signed: bool
    bank_signature_date: Optional[date] = None
    bank_official_stamp: bool
    
    witness_1_signature_path: Optional[str] = None
    witness_1_signature_date: Optional[date] = None
    witness_2_signature_path: Optional[str] = None
    witness_2_signature_date: Optional[date] = None
    
    # Execution
    is_executed: bool
    execution_date: Optional[date] = None
    all_signatures_complete: bool
    signatures_completed_date: Optional[date] = None
    
    # Document management
    original_document_location: Optional[str] = None
    scanned_copy_path: Optional[str] = None
    agreement_file_size: Optional[int] = None
    
    # Renewal
    renewal_notice_sent: bool
    renewal_notice_date: Optional[date] = None
    renewed: bool
    renewed_agreement_id: Optional[uuid.UUID] = None
    renewal_date: Optional[date] = None
    
    # Termination
    terminated: bool
    termination_date: Optional[date] = None
    termination_reason: Optional[str] = None
    termination_initiated_by: Optional[str] = None
    termination_notice_date: Optional[date] = None
    
    # Compliance
    kyc_verified_at_execution: bool
    aml_check_done: bool
    legal_review_done: bool
    legal_reviewed_by: Optional[uuid.UUID] = None
    legal_review_date: Optional[date] = None
    
    # Amendments
    amendment_count: int
    last_amendment_date: Optional[date] = None
    amendment_details: Optional[str] = None
    
    # Communication
    customer_copy_sent: bool
    customer_copy_sent_date: Optional[date] = None
    customer_copy_delivery_method: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgreementSignatureRequest(BaseModel):
    """Schema for signing agreement"""
    signer_type: str  # customer, joint_holder_1, joint_holder_2, bank
    signature_type: SignatureType
    signature_path: str
    signature_date: date
    digital_signature_id: Optional[str] = None
    ip_address: Optional[str] = None


class AgreementExecutionRequest(BaseModel):
    """Schema for executing agreement"""
    execution_date: date
    execution_location: str
    stamp_paper_details: Optional[Dict[str, Any]] = None
    notary_details: Optional[Dict[str, Any]] = None


class AgreementRenewalRequest(BaseModel):
    """Schema for renewing agreement"""
    new_end_date: date
    annual_rent: Decimal
    rent_escalation_applied: bool = False
    special_terms: Optional[str] = None


class AgreementTerminationRequest(BaseModel):
    """Schema for terminating agreement"""
    termination_date: date
    termination_reason: str
    initiated_by: str  # customer, bank
    notice_given: bool = True
    notice_date: Optional[date] = None


class AgreementAmendmentRequest(BaseModel):
    """Schema for amending agreement"""
    amendment_details: str
    amendment_date: date
    amended_clauses: List[str]
    requires_new_signatures: bool = False


class AgreementFilter(BaseModel):
    """Schema for filtering agreements"""
    allocation_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    agreement_type: Optional[AgreementType] = None
    status: Optional[AgreementStatus] = None
    expiring_within_days: Optional[int] = None
    renewal_due: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ==================== ALLOCATION PROCESS ANALYTICS ====================

class ApplicationAnalytics(BaseModel):
    """Application statistics"""
    total_applications: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    pending_review: int
    pending_approval: int
    approved_count: int
    rejected_count: int
    average_processing_days: int


class WaitingListStatistics(BaseModel):
    """Waiting list statistics"""
    total_waiting: int
    by_size: Dict[str, int]
    average_wait_days: int
    longest_wait_customer: Optional[Dict[str, Any]] = None
    expected_allocations_30_days: int


class KeyHandoverStatistics(BaseModel):
    """Key handover statistics"""
    total_handovers: int
    active_keys: int
    lost_keys: int
    duplicate_keys_issued: int
    keys_returned: int
    pending_returns: int


class AgreementStatistics(BaseModel):
    """Agreement statistics"""
    total_agreements: int
    by_status: Dict[str, int]
    expiring_30_days: int
    expiring_60_days: int
    expiring_90_days: int
    pending_signatures: int
    fully_executed: int
    renewal_due: int


class AllocationProcessDashboard(BaseModel):
    """Complete allocation process dashboard"""
    applications: ApplicationAnalytics
    waiting_list: WaitingListStatistics
    key_handovers: KeyHandoverStatistics
    agreements: AgreementStatistics
    recent_allocations: int
    allocation_success_rate: float
