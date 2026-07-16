"""
Locker Management Database Models

This module contains all database models for locker management including:
- Locker Master (inventory, location, specifications)
- Locker Allocation (customer assignments)
- Locker Rent Payments
- Locker Maintenance Records
- Locker Access Log

All models follow multi-tenant architecture with soft delete pattern.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import BaseModel


class LockerMaster(BaseModel):
    """
    Locker Master
    
    Defines individual locker units with specifications, location, and status.
    Tracks physical inventory and availability.
    """
    __tablename__ = "locker_master"
    
    # Locker Identification
    locker_number = Column(String(50), nullable=False, index=True)
    locker_id = Column(String(50), nullable=False, index=True)  # Branch-specific ID
    
    # Physical Specifications
    locker_size = Column(String(50), nullable=False, index=True)
    # Options: small (5"x5"x20"), medium (5"x10"x20"), large (10"x10"x20"), extra-large (10"x20"x20")
    
    dimensions_height = Column(Numeric(10, 2))  # in inches
    dimensions_width = Column(Numeric(10, 2))   # in inches
    dimensions_depth = Column(Numeric(10, 2))   # in inches
    
    # Location Details
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Links to branch
    branch_name = Column(String(200))  # Denormalized for quick access
    
    vault_room = Column(String(100), nullable=False)
    floor = Column(String(50))
    rack_number = Column(String(50))
    position = Column(String(50))  # Position in rack (top, middle, bottom, etc.)
    
    # Locker Type & Security
    locker_type = Column(String(50), nullable=False, default='dual_key')
    # Options: single_key, dual_key (bank key + customer key)
    
    lock_type = Column(String(100))  # mechanical, electronic, biometric
    lock_serial_number = Column(String(100))
    
    # Financial Details
    annual_rent = Column(Numeric(10, 2), nullable=False)
    security_deposit = Column(Numeric(10, 2), nullable=False)
    initial_rent = Column(Numeric(10, 2))  # First year rent (may differ)
    
    # Pricing based on size
    base_rent = Column(Numeric(10, 2))
    gst_rate = Column(Numeric(5, 2), default=18.0)  # GST percentage
    
    # Status Management
    status = Column(String(50), nullable=False, default='available', index=True)
    # Options: available, allocated, under_maintenance, blocked, damaged, retired
    
    is_available = Column(Boolean, default=True, index=True)
    
    # Maintenance Tracking
    installation_date = Column(Date)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    maintenance_frequency_days = Column(Integer, default=180)  # 6 months default
    
    # Additional Features
    features = Column(Text)  # JSON string: fire_proof, water_proof, additional_security
    special_notes = Column(Text)
    
    # Insurance
    insurance_covered = Column(Boolean, default=True)
    insurance_amount = Column(Numeric(15, 2))
    
    # Audit Fields (inherited from BaseModel)
    # tenant_id, created_at, updated_at, created_by, updated_by, is_deleted
    
    # Relationships
    allocations = relationship("LockerAllocation", back_populates="locker", cascade="all, delete-orphan")
    maintenance_records = relationship("LockerMaintenance", back_populates="locker", cascade="all, delete-orphan")
    access_logs = relationship("LockerAccessLog", back_populates="locker", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LockerMaster {self.locker_number} - {self.locker_size} - {self.status}>"


class LockerAllocation(BaseModel):
    """
    Locker Allocation
    
    Records customer locker assignments with agreement details.
    Tracks allocation lifecycle from assignment to closure.
    """
    __tablename__ = "locker_allocations"
    
    # Reference Numbers
    allocation_number = Column(String(50), unique=True, nullable=False, index=True)
    agreement_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Allocation Details
    allocation_date = Column(Date, nullable=False, index=True)
    agreement_start_date = Column(Date, nullable=False)
    agreement_end_date = Column(Date, nullable=False, index=True)
    
    # Financial Terms
    annual_rent = Column(Numeric(10, 2), nullable=False)
    security_deposit = Column(Numeric(10, 2), nullable=False)
    
    rent_frequency = Column(String(50), nullable=False, default='annual')
    # Options: annual, semi_annual, quarterly, monthly
    
    gst_applicable = Column(Boolean, default=True)
    gst_rate = Column(Numeric(5, 2), default=18.0)
    
    # Payment Status
    security_deposit_paid = Column(Boolean, default=False)
    security_deposit_paid_date = Column(Date)
    security_deposit_receipt_number = Column(String(100))
    
    # Rent Tracking
    rent_paid_upto_date = Column(Date)  # Last date till rent is paid
    next_rent_due_date = Column(Date, index=True)
    outstanding_rent = Column(Numeric(10, 2), default=0)
    
    total_rent_paid = Column(Numeric(15, 2), default=0)
    total_penalties_paid = Column(Numeric(10, 2), default=0)
    
    # Keys Management
    customer_key_number = Column(String(50))
    bank_key_number = Column(String(50))
    duplicate_key_issued = Column(Boolean, default=False)
    duplicate_key_charges = Column(Numeric(10, 2))
    
    # Nominee Details
    nominee_name = Column(String(200))
    nominee_relationship = Column(String(100))
    nominee_dob = Column(Date)
    nominee_address = Column(Text)
    nominee_id_proof_type = Column(String(50))
    nominee_id_proof_number = Column(String(100))
    nominee_percentage = Column(Numeric(5, 2), default=100)
    
    # Joint Holders (for multiple customers)
    joint_holder_1_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    joint_holder_2_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    operation_mode = Column(String(50), default='single')  # single, either_or_survivor, joint
    
    # Status Management
    status = Column(String(50), nullable=False, default='active', index=True)
    # Options: active, expired, closed, surrendered, transferred
    
    # Renewal Tracking
    auto_renewal = Column(Boolean, default=False)
    renewal_count = Column(Integer, default=0)
    parent_allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"))
    
    # Closure Details
    closure_date = Column(Date)
    closure_reason = Column(String(200))
    security_deposit_refunded = Column(Boolean, default=False)
    security_deposit_refund_date = Column(Date)
    security_deposit_refund_amount = Column(Numeric(10, 2))
    closure_charges = Column(Numeric(10, 2), default=0)
    
    # Notifications
    reminder_sent = Column(Boolean, default=False)
    last_reminder_date = Column(Date)
    reminder_count = Column(Integer, default=0)
    
    # Documents
    agreement_document_path = Column(String(500))
    kyc_document_path = Column(String(500))
    nominee_document_path = Column(String(500))
    
    # Special Instructions
    special_instructions = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    locker = relationship("LockerMaster", back_populates="allocations")
    customer = relationship("Customer", foreign_keys=[customer_id])
    joint_holder_1 = relationship("Customer", foreign_keys=[joint_holder_1_id])
    joint_holder_2 = relationship("Customer", foreign_keys=[joint_holder_2_id])
    rent_payments = relationship("LockerRentPayment", back_populates="allocation", cascade="all, delete-orphan")
    access_logs = relationship("LockerAccessLog", back_populates="allocation", cascade="all, delete-orphan")
    renewed_allocations = relationship("LockerAllocation", foreign_keys=[parent_allocation_id])
    
    def __repr__(self):
        return f"<LockerAllocation {self.allocation_number} - {self.status}>"


class LockerRentPayment(BaseModel):
    """
    Locker Rent Payment
    
    Records all rent payments including regular rent, penalties, and charges.
    Tracks payment history and outstanding dues.
    """
    __tablename__ = "locker_rent_payments"
    
    # Reference Numbers
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    transaction_id = Column(String(100), index=True)
    
    # Links
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Payment Details
    payment_date = Column(Date, nullable=False, index=True)
    payment_type = Column(String(50), nullable=False)
    # Options: rent, security_deposit, penalty, late_fee, duplicate_key_charge, miscellaneous
    
    # Period Covered
    period_from = Column(Date)
    period_to = Column(Date)
    
    # Amount Breakdown
    rent_amount = Column(Numeric(10, 2), default=0)
    gst_amount = Column(Numeric(10, 2), default=0)
    penalty_amount = Column(Numeric(10, 2), default=0)
    late_fee_amount = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Payment Method
    payment_mode = Column(String(50), nullable=False)
    # Options: cash, cheque, neft, rtgs, imps, upi, card, online
    
    # Payment Instrument Details
    cheque_number = Column(String(50))
    cheque_date = Column(Date)
    bank_name = Column(String(200))
    bank_branch = Column(String(200))
    
    transaction_reference = Column(String(200))
    utr_number = Column(String(100))  # For NEFT/RTGS/IMPS
    
    # Payment Status
    payment_status = Column(String(50), nullable=False, default='completed')
    # Options: pending, completed, failed, cancelled, refunded
    
    clearance_date = Column(Date)  # For cheque clearance
    
    # Adjustments
    adjusted_against = Column(String(200))  # If adjusting advance/excess payment
    adjustment_amount = Column(Numeric(10, 2), default=0)
    
    # Additional Info
    received_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    collected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    remarks = Column(Text)
    
    # Receipt Generation
    receipt_generated = Column(Boolean, default=False)
    receipt_generated_date = Column(DateTime)
    receipt_file_path = Column(String(500))
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    allocation = relationship("LockerAllocation", back_populates="rent_payments")
    customer = relationship("Customer")
    received_by_user = relationship("User", foreign_keys=[received_by])
    collected_by_user = relationship("User", foreign_keys=[collected_by])
    
    def __repr__(self):
        return f"<LockerRentPayment {self.receipt_number} - ₹{self.total_amount}>"


class LockerMaintenance(BaseModel):
    """
    Locker Maintenance
    
    Tracks maintenance activities including preventive and corrective maintenance.
    Records service history and costs.
    """
    __tablename__ = "locker_maintenance"
    
    # Reference Numbers
    maintenance_number = Column(String(50), unique=True, nullable=False, index=True)
    work_order_number = Column(String(50), index=True)
    
    # Links
    locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"), nullable=False, index=True)
    
    # Maintenance Details
    maintenance_type = Column(String(50), nullable=False)
    # Options: preventive, corrective, emergency, inspection, upgrade
    
    maintenance_date = Column(Date, nullable=False, index=True)
    scheduled_date = Column(Date)
    completion_date = Column(Date)
    
    # Issue Details
    issue_reported = Column(Text)
    issue_category = Column(String(100))  # lock_issue, key_issue, structural_damage, etc.
    priority = Column(String(50), default='medium')  # low, medium, high, urgent
    
    # Work Performed
    work_description = Column(Text, nullable=False)
    parts_replaced = Column(Text)  # JSON string with parts list
    service_provider = Column(String(200))
    technician_name = Column(String(200))
    technician_contact = Column(String(20))
    
    # Status
    status = Column(String(50), nullable=False, default='scheduled')
    # Options: scheduled, in_progress, completed, cancelled, pending_parts
    
    # Cost Details
    labor_cost = Column(Numeric(10, 2), default=0)
    parts_cost = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    total_cost = Column(Numeric(10, 2), default=0)
    
    # Billing
    invoice_number = Column(String(100))
    invoice_date = Column(Date)
    payment_status = Column(String(50), default='pending')  # pending, paid
    
    # Downtime Tracking
    locker_unavailable_from = Column(DateTime)
    locker_unavailable_to = Column(DateTime)
    downtime_hours = Column(Numeric(10, 2))
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    follow_up_notes = Column(Text)
    
    # Documents
    before_photos = Column(Text)  # JSON array of file paths
    after_photos = Column(Text)   # JSON array of file paths
    invoice_document_path = Column(String(500))
    
    # Quality Check
    quality_check_done = Column(Boolean, default=False)
    quality_check_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    quality_check_date = Column(Date)
    quality_rating = Column(Integer)  # 1-5 stars
    
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    locker = relationship("LockerMaster", back_populates="maintenance_records")
    quality_checker = relationship("User", foreign_keys=[quality_check_by])
    
    def __repr__(self):
        return f"<LockerMaintenance {self.maintenance_number} - {self.maintenance_type}>"


class LockerAccessLog(BaseModel):
    """
    Locker Access Log
    
    Records every locker access for security and audit purposes.
    Tracks who accessed, when, and authorization details.
    """
    __tablename__ = "locker_access_logs"
    
    # Reference Numbers
    access_log_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"), nullable=False, index=True)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)
    
    # Access Details
    access_date = Column(Date, nullable=False, index=True)
    access_time_in = Column(DateTime, nullable=False)
    access_time_out = Column(DateTime)
    
    # Person Accessing
    accessor_type = Column(String(50), nullable=False)
    # Options: customer, nominee, joint_holder, bank_staff, maintenance, legal
    
    accessor_name = Column(String(200), nullable=False)
    accessor_id_type = Column(String(50))
    accessor_id_number = Column(String(100))
    
    # Authorization
    authorized_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    authorization_document = Column(String(500))  # For nominee/legal access
    
    # Witnesses
    witness_1_name = Column(String(200))
    witness_1_employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    witness_2_name = Column(String(200))
    witness_2_employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Purpose
    purpose = Column(String(200), nullable=False)
    # Options: regular_access, deposit_items, retrieve_items, inspection, surrender
    
    # Items Activity
    items_deposited = Column(Text)  # JSON description
    items_retrieved = Column(Text)  # JSON description
    
    # Security
    biometric_verified = Column(Boolean, default=False)
    photo_captured = Column(Boolean, default=False)
    photo_path = Column(String(500))
    
    signature_captured = Column(Boolean, default=False)
    signature_path = Column(String(500))
    
    # Special Cases
    emergency_access = Column(Boolean, default=False)
    court_order = Column(Boolean, default=False)
    court_order_number = Column(String(100))
    
    # Status
    access_type = Column(String(50), default='normal')  # normal, emergency, forced_opening
    
    remarks = Column(Text)
    special_notes = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    locker = relationship("LockerMaster", back_populates="access_logs")
    allocation = relationship("LockerAllocation", back_populates="access_logs")
    customer = relationship("Customer")
    authorized_by_user = relationship("User", foreign_keys=[authorized_by])
    witness_1_user = relationship("User", foreign_keys=[witness_1_employee_id])
    witness_2_user = relationship("User", foreign_keys=[witness_2_employee_id])
    
    def __repr__(self):
        return f"<LockerAccessLog {self.access_log_number} - {self.access_date}>"



class LockerCustomer(BaseModel):
    """
    Locker Customer
    
    Extended customer details specific to locker operations.
    Stores locker-specific customer information, KYC, and documentation.
    """
    __tablename__ = "locker_customers"
    
    # Reference Numbers
    locker_customer_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), index=True)
    
    # Customer Type
    customer_type = Column(String(50), nullable=False, default='primary')
    # Options: primary, joint_holder, nominee, authorized_signatory
    
    # Personal Details
    title = Column(String(10))  # Mr, Mrs, Ms, Dr
    full_name = Column(String(200), nullable=False)
    date_of_birth = Column(Date)
    age = Column(Integer)
    gender = Column(String(20))
    
    # Contact Information
    mobile_number = Column(String(20), nullable=False)
    alternate_mobile = Column(String(20))
    email = Column(String(200))
    
    # Address
    current_address_line1 = Column(String(500))
    current_address_line2 = Column(String(500))
    current_city = Column(String(100))
    current_state = Column(String(100))
    current_pincode = Column(String(10))
    current_country = Column(String(100), default='India')
    
    permanent_address_line1 = Column(String(500))
    permanent_address_line2 = Column(String(500))
    permanent_city = Column(String(100))
    permanent_state = Column(String(100))
    permanent_pincode = Column(String(10))
    permanent_country = Column(String(100), default='India')
    
    address_same_as_current = Column(Boolean, default=True)
    
    # Identification
    pan_number = Column(String(20), index=True)
    aadhar_number = Column(String(20), index=True)
    passport_number = Column(String(20))
    driving_license_number = Column(String(30))
    voter_id_number = Column(String(30))
    
    # Employment/Business
    occupation = Column(String(100))
    employer_name = Column(String(200))
    employer_address = Column(Text)
    annual_income = Column(Numeric(15, 2))
    income_source = Column(String(100))
    
    # Banking Details
    bank_account_number = Column(String(50))
    bank_name = Column(String(200))
    bank_branch = Column(String(200))
    bank_ifsc = Column(String(20))
    
    # Purpose of Locker
    locker_purpose = Column(String(200))
    # Options: jewelry_storage, document_storage, valuables, investment_items, other
    locker_purpose_details = Column(Text)
    
    # Estimated Value
    estimated_value_of_contents = Column(Numeric(15, 2))
    insurance_required = Column(Boolean, default=False)
    insurance_amount = Column(Numeric(15, 2))
    
    # Customer Category
    customer_category = Column(String(50), default='regular')
    # Options: regular, premium, senior_citizen, staff, vip
    
    is_senior_citizen = Column(Boolean, default=False)
    is_staff_member = Column(Boolean, default=False)
    is_premium_customer = Column(Boolean, default=False)
    
    # Photo & Signature
    photo_path = Column(String(500))
    signature_path = Column(String(500))
    
    # Relationship Status (for joint accounts)
    relationship_with_primary = Column(String(100))  # spouse, parent, child, sibling, business_partner
    
    # Communication Preferences
    preferred_language = Column(String(50), default='English')
    sms_alerts = Column(Boolean, default=True)
    email_alerts = Column(Boolean, default=True)
    whatsapp_alerts = Column(Boolean, default=False)
    
    # Status
    status = Column(String(50), nullable=False, default='active')
    # Options: active, inactive, blocked, deceased
    
    verification_status = Column(String(50), default='pending')
    # Options: pending, verified, rejected
    
    verification_date = Column(Date)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Special Notes
    special_instructions = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    customer = relationship("Customer")
    allocation = relationship("LockerAllocation")
    kyc_documents = relationship("LockerKYC", back_populates="locker_customer", cascade="all, delete-orphan")
    nominees = relationship("LockerNominee", back_populates="locker_customer", cascade="all, delete-orphan")
    authorizations = relationship("LockerAuthorization", back_populates="locker_customer", cascade="all, delete-orphan")
    verifier = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<LockerCustomer {self.locker_customer_id} - {self.full_name}>"


class LockerJointHolder(BaseModel):
    """
    Locker Joint Holder
    
    Manages joint locker holders with operating instructions.
    Supports multiple holders with different operation modes.
    """
    __tablename__ = "locker_joint_holders"
    
    # Reference Numbers
    joint_holder_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), nullable=False, index=True)
    locker_customer_id = Column(UUID(as_uuid=True), ForeignKey("locker_customers.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Holder Details
    holder_type = Column(String(50), nullable=False)
    # Options: primary, secondary, tertiary
    
    holder_sequence = Column(Integer, nullable=False)  # 1 for primary, 2, 3... for others
    
    # Operation Mode
    operation_mode = Column(String(50), nullable=False)
    # Options: either_or_survivor, former_or_survivor, latter_or_survivor, joint, anyone
    
    # Authority
    can_operate_alone = Column(Boolean, default=False)
    requires_joint_operation = Column(Boolean, default=False)
    
    # Specific Permissions
    can_deposit = Column(Boolean, default=True)
    can_retrieve = Column(Boolean, default=True)
    can_make_payments = Column(Boolean, default=True)
    can_surrender = Column(Boolean, default=False)
    can_add_nominee = Column(Boolean, default=False)
    
    # Agreement
    agreement_accepted = Column(Boolean, default=False)
    agreement_accepted_date = Column(Date)
    agreement_document_path = Column(String(500))
    
    # Signature & Photo
    signature_path = Column(String(500))
    photo_path = Column(String(500))
    specimen_signature_verified = Column(Boolean, default=False)
    
    # Rights in Case of Death
    survivorship_rights = Column(Boolean, default=True)
    inheritance_percentage = Column(Numeric(5, 2), default=0)
    
    # Status
    status = Column(String(50), nullable=False, default='active')
    # Options: active, inactive, deceased, removed
    
    activation_date = Column(Date)
    deactivation_date = Column(Date)
    deactivation_reason = Column(String(200))
    
    # Death Record (if applicable)
    is_deceased = Column(Boolean, default=False)
    date_of_death = Column(Date)
    death_certificate_path = Column(String(500))
    legal_heir_claim_path = Column(String(500))
    
    # Special Instructions
    special_instructions = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    allocation = relationship("LockerAllocation")
    locker_customer = relationship("LockerCustomer")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<LockerJointHolder {self.joint_holder_id} - {self.holder_type}>"



class LockerKYC(BaseModel):
    """
    Locker KYC Documents
    
    Stores all KYC and identity verification documents for locker customers.
    Tracks document validity and verification status.
    """
    __tablename__ = "locker_kyc_documents"
    
    # Reference Numbers
    kyc_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    locker_customer_id = Column(UUID(as_uuid=True), ForeignKey("locker_customers.id"), nullable=False, index=True)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), index=True)
    
    # Document Type
    document_type = Column(String(100), nullable=False)
    # Options: pan_card, aadhar_card, passport, voter_id, driving_license, 
    #          bank_statement, utility_bill, rent_agreement, salary_slip, 
    #          income_tax_return, photo, signature, address_proof, identity_proof
    
    document_category = Column(String(50), nullable=False)
    # Options: identity_proof, address_proof, income_proof, photo, signature, other
    
    # Document Details
    document_number = Column(String(100), index=True)
    document_name = Column(String(200))
    
    issuing_authority = Column(String(200))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    
    is_expired = Column(Boolean, default=False, index=True)
    
    # Document Storage
    document_file_path = Column(String(500), nullable=False)
    document_file_type = Column(String(20))  # pdf, jpg, png
    document_file_size = Column(Integer)  # in KB
    
    original_filename = Column(String(200))
    
    # Verification Status
    verification_status = Column(String(50), nullable=False, default='pending')
    # Options: pending, verified, rejected, expired, resubmission_required
    
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verification_date = Column(Date)
    verification_remarks = Column(Text)
    
    rejection_reason = Column(Text)
    
    # Compliance
    kyc_compliance = Column(Boolean, default=False)
    aml_checked = Column(Boolean, default=False)
    aml_check_date = Column(Date)
    aml_status = Column(String(50))  # clear, flagged, under_review
    
    # Version Control
    version_number = Column(Integer, default=1)
    previous_version_id = Column(UUID(as_uuid=True), ForeignKey("locker_kyc_documents.id"))
    is_latest_version = Column(Boolean, default=True)
    
    # Mandatory Check
    is_mandatory = Column(Boolean, default=True)
    
    # Audit Trail
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    locker_customer = relationship("LockerCustomer", back_populates="kyc_documents")
    allocation = relationship("LockerAllocation")
    verifier = relationship("User", foreign_keys=[verified_by])
    uploader = relationship("User", foreign_keys=[uploaded_by])
    previous_version = relationship("LockerKYC", remote_side=[BaseModel.id], foreign_keys=[previous_version_id])
    
    def __repr__(self):
        return f"<LockerKYC {self.kyc_id} - {self.document_type}>"


class LockerNominee(BaseModel):
    """
    Locker Nominee
    
    Manages nominee details for locker access in case of customer's demise.
    Supports multiple nominees with different percentages.
    """
    __tablename__ = "locker_nominees"
    
    # Reference Numbers
    nominee_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    locker_customer_id = Column(UUID(as_uuid=True), ForeignKey("locker_customers.id"), nullable=False, index=True)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), nullable=False, index=True)
    
    # Nominee Priority
    nominee_sequence = Column(Integer, nullable=False)  # 1 for primary, 2, 3... for others
    is_primary_nominee = Column(Boolean, default=False)
    
    # Personal Details
    title = Column(String(10))
    full_name = Column(String(200), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    
    # Relationship
    relationship_with_customer = Column(String(100), nullable=False)
    # Options: spouse, son, daughter, father, mother, brother, sister, other
    
    # Contact Information
    mobile_number = Column(String(20))
    email = Column(String(200))
    
    # Address
    address_line1 = Column(String(500), nullable=False)
    address_line2 = Column(String(500))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    country = Column(String(100), default='India')
    
    # Identification
    id_proof_type = Column(String(50), nullable=False)
    # Options: aadhar, pan, passport, voter_id, driving_license
    id_proof_number = Column(String(100), nullable=False)
    id_proof_document_path = Column(String(500))
    
    # Photo
    photo_path = Column(String(500))
    
    # Share Percentage
    nominee_percentage = Column(Numeric(5, 2), nullable=False, default=100)
    # Total of all nominees should be 100%
    
    # Minor Nominee
    is_minor = Column(Boolean, default=False)
    
    # Guardian Details (if nominee is minor)
    guardian_name = Column(String(200))
    guardian_relationship = Column(String(100))
    guardian_id_proof_type = Column(String(50))
    guardian_id_proof_number = Column(String(100))
    guardian_address = Column(Text)
    guardian_mobile = Column(String(20))
    guardian_document_path = Column(String(500))
    
    # Nomination Agreement
    nomination_form_path = Column(String(500))
    nomination_date = Column(Date, nullable=False)
    nomination_accepted = Column(Boolean, default=False)
    nomination_accepted_date = Column(Date)
    
    # Status
    status = Column(String(50), nullable=False, default='active')
    # Options: active, inactive, revoked, deceased, expired
    
    activation_date = Column(Date)
    deactivation_date = Column(Date)
    deactivation_reason = Column(String(200))
    
    # Verification
    verification_status = Column(String(50), default='pending')
    # Options: pending, verified, rejected
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verification_date = Column(Date)
    
    # Special Instructions
    special_instructions = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    locker_customer = relationship("LockerCustomer", back_populates="nominees")
    allocation = relationship("LockerAllocation")
    verifier = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<LockerNominee {self.nominee_id} - {self.full_name}>"


class LockerRentStructure(BaseModel):
    """
    Locker Rent Structure
    
    Defines rent pricing based on size, location, and customer category.
    Supports dynamic pricing with GST and penalty calculations.
    """
    __tablename__ = "locker_rent_structures"
    
    # Reference Numbers
    rent_structure_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Applicability
    branch_id = Column(UUID(as_uuid=True), index=True)  # Null means all branches
    branch_name = Column(String(200))
    
    locker_size = Column(String(50), nullable=False, index=True)
    # Options: small, medium, large, extra_large
    
    location_type = Column(String(50), default='standard')
    # Options: standard, premium, high_security, vault
    
    # Customer Category
    customer_category = Column(String(50), default='regular', index=True)
    # Options: regular, premium, senior_citizen, staff, vip
    
    # Rent Components
    base_rent_annual = Column(Numeric(10, 2), nullable=False)
    base_rent_semi_annual = Column(Numeric(10, 2))
    base_rent_quarterly = Column(Numeric(10, 2))
    base_rent_monthly = Column(Numeric(10, 2))
    
    # Location Premium
    location_premium_percentage = Column(Numeric(5, 2), default=0)
    location_premium_amount = Column(Numeric(10, 2), default=0)
    
    # Security Deposit
    security_deposit_amount = Column(Numeric(10, 2), nullable=False)
    security_deposit_refundable = Column(Boolean, default=True)
    
    # GST
    gst_applicable = Column(Boolean, default=True)
    gst_rate = Column(Numeric(5, 2), default=18.0)
    gst_on_rent = Column(Boolean, default=True)
    gst_on_deposit = Column(Boolean, default=False)
    
    # Discounts
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    discount_reason = Column(String(200))
    
    # Advance Payment Discount
    advance_payment_discount = Column(Numeric(5, 2), default=0)
    # e.g., 5% discount for annual advance payment
    
    # Late Payment Penalty
    late_payment_penalty_applicable = Column(Boolean, default=True)
    late_payment_grace_days = Column(Integer, default=15)
    late_payment_penalty_percentage = Column(Numeric(5, 2), default=2.0)
    # e.g., 2% per month on overdue amount
    
    late_payment_penalty_flat_amount = Column(Numeric(10, 2), default=0)
    penalty_calculation_method = Column(String(50), default='percentage')
    # Options: percentage, flat_amount, both
    
    # Other Charges
    duplicate_key_charges = Column(Numeric(10, 2), default=500)
    locker_breaking_charges = Column(Numeric(10, 2), default=2000)
    transfer_charges = Column(Numeric(10, 2), default=500)
    closure_charges = Column(Numeric(10, 2), default=0)
    
    # Minimum & Maximum
    minimum_rent_period_months = Column(Integer, default=12)
    maximum_rent_advance_years = Column(Integer, default=3)
    
    # Validity Period
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approval_date = Column(Date)
    approval_remarks = Column(Text)
    
    # Version Control
    version_number = Column(Integer, default=1)
    supersedes_structure_id = Column(UUID(as_uuid=True), ForeignKey("locker_rent_structures.id"))
    
    # Special Rules
    rent_waiver_applicable = Column(Boolean, default=False)
    rent_waiver_conditions = Column(Text)
    # e.g., "Free for staff members", "50% discount for senior citizens"
    
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    approver = relationship("User", foreign_keys=[approved_by])
    superseded_structure = relationship("LockerRentStructure", remote_side=[BaseModel.id], foreign_keys=[supersedes_structure_id])
    
    def __repr__(self):
        return f"<LockerRentStructure {self.rent_structure_id} - {self.locker_size}>"


class LockerAuthorization(BaseModel):
    """
    Locker Authorization
    
    Manages authorized signatories and their access permissions.
    Tracks who can operate the locker on behalf of the customer.
    """
    __tablename__ = "locker_authorizations"
    
    # Reference Numbers
    authorization_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    locker_customer_id = Column(UUID(as_uuid=True), ForeignKey("locker_customers.id"), nullable=False, index=True)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), nullable=False, index=True)
    
    # Authorized Person
    authorized_person_type = Column(String(50), nullable=False)
    # Options: customer, joint_holder, nominee, power_of_attorney, legal_heir, court_appointed
    
    authorized_person_name = Column(String(200), nullable=False)
    authorized_person_customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    
    # Personal Details
    mobile_number = Column(String(20), nullable=False)
    email = Column(String(200))
    
    # Identification
    id_proof_type = Column(String(50), nullable=False)
    id_proof_number = Column(String(100), nullable=False)
    id_proof_document_path = Column(String(500))
    
    # Address
    address = Column(Text, nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Authorization Details
    authorization_type = Column(String(50), nullable=False)
    # Options: full_access, limited_access, emergency_access, temporary_access
    
    # Specific Permissions
    can_deposit_items = Column(Boolean, default=True)
    can_retrieve_items = Column(Boolean, default=True)
    can_view_contents = Column(Boolean, default=True)
    can_make_rent_payments = Column(Boolean, default=True)
    can_renew_locker = Column(Boolean, default=False)
    can_surrender_locker = Column(Boolean, default=False)
    can_add_joint_holder = Column(Boolean, default=False)
    can_change_nominee = Column(Boolean, default=False)
    
    # Time Restrictions
    authorization_valid_from = Column(Date, nullable=False)
    authorization_valid_to = Column(Date)
    is_permanent = Column(Boolean, default=False)
    
    # Day/Time Restrictions
    access_days_allowed = Column(String(100))  # JSON: ["monday", "tuesday", ...]
    access_time_from = Column(String(10))  # e.g., "09:00"
    access_time_to = Column(String(10))    # e.g., "17:00"
    
    # Legal Documents
    authorization_document_type = Column(String(100))
    # Options: power_of_attorney, court_order, succession_certificate, will, letter_of_authority
    
    authorization_document_path = Column(String(500), nullable=False)
    authorization_document_number = Column(String(100))
    authorization_document_date = Column(Date)
    
    # Signature & Photo
    signature_specimen_path = Column(String(500))
    photo_path = Column(String(500))
    signature_verified = Column(Boolean, default=False)
    
    # Witness Details
    witness_1_name = Column(String(200))
    witness_1_id_proof = Column(String(100))
    witness_1_signature_path = Column(String(500))
    
    witness_2_name = Column(String(200))
    witness_2_id_proof = Column(String(100))
    witness_2_signature_path = Column(String(500))
    
    # Approval & Verification
    approval_status = Column(String(50), nullable=False, default='pending')
    # Options: pending, approved, rejected, revoked, expired
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approval_date = Column(Date)
    approval_remarks = Column(Text)
    
    rejection_reason = Column(Text)
    
    # Status
    status = Column(String(50), nullable=False, default='active')
    # Options: active, inactive, suspended, revoked, expired
    
    activation_date = Column(Date)
    deactivation_date = Column(Date)
    deactivation_reason = Column(String(200))
    
    # Revocation
    revoked_by_customer = Column(Boolean, default=False)
    revocation_date = Column(Date)
    revocation_reason = Column(Text)
    revocation_document_path = Column(String(500))
    
    # Usage Tracking
    last_used_date = Column(Date)
    total_access_count = Column(Integer, default=0)
    
    # Emergency Contact
    emergency_contact_name = Column(String(200))
    emergency_contact_mobile = Column(String(20))
    emergency_contact_relationship = Column(String(100))
    
    # Special Instructions
    special_conditions = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    locker_customer = relationship("LockerCustomer", back_populates="authorizations")
    allocation = relationship("LockerAllocation")
    authorized_customer = relationship("Customer", foreign_keys=[authorized_person_customer_id])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<LockerAuthorization {self.authorization_id} - {self.authorized_person_name}>"



class LockerApplication(BaseModel):
    """
    Locker Application
    
    Manages locker rental applications from customers with approval workflow.
    Tracks application status from submission to allocation or rejection.
    """
    __tablename__ = "locker_applications"
    
    # Reference Numbers
    application_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    locker_customer_id = Column(UUID(as_uuid=True), ForeignKey("locker_customers.id"), index=True)
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Application Details
    application_date = Column(Date, nullable=False, index=True)
    application_type = Column(String(50), nullable=False, default='new')
    # Options: new, renewal, transfer, additional
    
    # Locker Preferences
    preferred_locker_size = Column(String(50), nullable=False)
    # Options: small, medium, large, extra_large, any
    alternate_size_1 = Column(String(50))
    alternate_size_2 = Column(String(50))
    
    preferred_location = Column(String(200))  # Specific vault room/floor preference
    preferred_locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"))  # Specific locker
    
    # Purpose
    purpose_of_locker = Column(String(200), nullable=False)
    # Options: jewelry, documents, valuables, securities, other
    purpose_details = Column(Text)
    
    estimated_value_of_contents = Column(Numeric(15, 2))
    insurance_required = Column(Boolean, default=False)
    insurance_coverage_amount = Column(Numeric(15, 2))
    
    # Financial Details
    proposed_rent_frequency = Column(String(50), default='annual')
    # Options: monthly, quarterly, semi_annual, annual
    willing_to_pay_advance = Column(Boolean, default=False)
    advance_payment_months = Column(Integer, default=12)
    
    # Priority Scoring
    is_existing_customer = Column(Boolean, default=False)
    existing_customer_since = Column(Date)
    relationship_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    customer_category = Column(String(50), default='regular')
    # Options: regular, premium, senior_citizen, staff, vip
    
    priority_score = Column(Integer, default=0)  # Auto-calculated based on rules
    priority_reason = Column(Text)
    
    deposit_with_bank = Column(Numeric(15, 2), default=0)  # Total deposits
    loan_accounts = Column(Integer, default=0)
    credit_score = Column(Integer)
    
    # Application Status
    status = Column(String(50), nullable=False, default='submitted', index=True)
    # Options: submitted, under_review, pending_documents, pending_approval, 
    #          approved, rejected, waiting_list, allocated, cancelled, expired
    
    current_stage = Column(String(50), default='document_verification')
    # Options: document_verification, credit_check, manager_review, final_approval, allocation
    
    # Approval Workflow
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_date = Column(Date)
    review_remarks = Column(Text)
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approval_date = Column(Date)
    approval_remarks = Column(Text)
    approval_level = Column(Integer, default=0)  # Multi-level approval tracking
    
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rejection_date = Column(Date)
    rejection_reason = Column(Text)
    
    # Waiting List
    added_to_waiting_list = Column(Boolean, default=False)
    waiting_list_date = Column(Date)
    waiting_list_position = Column(Integer)
    expected_availability_date = Column(Date)
    
    # Allocation
    allocated_locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"))
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"))
    allocation_date = Column(Date)
    
    # Documents
    application_form_path = Column(String(500))
    supporting_documents_path = Column(Text)  # JSON array of document paths
    kyc_verified = Column(Boolean, default=False)
    kyc_verification_date = Column(Date)
    
    # Communication
    notification_sent = Column(Boolean, default=False)
    last_notification_date = Column(Date)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    
    # Validity
    application_valid_till = Column(Date)
    is_expired = Column(Boolean, default=False)
    
    # Special Notes
    special_requirements = Column(Text)
    internal_notes = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    locker_customer = relationship("LockerCustomer", foreign_keys=[locker_customer_id])
    preferred_locker = relationship("LockerMaster", foreign_keys=[preferred_locker_id])
    allocated_locker = relationship("LockerMaster", foreign_keys=[allocated_locker_id])
    allocation = relationship("LockerAllocation", foreign_keys=[allocation_id])
    submitted_by_user = relationship("User", foreign_keys=[submitted_by])
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    rejected_by_user = relationship("User", foreign_keys=[rejected_by])
    
    def __repr__(self):
        return f"<LockerApplication {self.application_number} - {self.status}>"


class LockerWaitingList(BaseModel):
    """
    Locker Waiting List
    
    Manages queue of customers waiting for locker allocation.
    Tracks priority order and automatic allocation triggers.
    """
    __tablename__ = "locker_waiting_list"
    
    # Reference Numbers
    waiting_list_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    application_id = Column(UUID(as_uuid=True), ForeignKey("locker_applications.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    branch_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Waiting List Details
    added_date = Column(Date, nullable=False, index=True)
    locker_size_requested = Column(String(50), nullable=False)
    position_in_queue = Column(Integer, nullable=False, index=True)
    
    # Priority Calculation
    priority_score = Column(Integer, nullable=False, default=0, index=True)
    priority_factors = Column(Text)  # JSON: factors contributing to score
    
    base_priority = Column(Integer, default=0)
    existing_customer_bonus = Column(Integer, default=0)
    deposit_size_bonus = Column(Integer, default=0)
    senior_citizen_bonus = Column(Integer, default=0)
    staff_bonus = Column(Integer, default=0)
    waiting_time_bonus = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), nullable=False, default='active', index=True)
    # Options: active, notified, accepted, declined, expired, allocated, cancelled
    
    # Notification Management
    notification_sent = Column(Boolean, default=False)
    notification_sent_date = Column(Date)
    notification_method = Column(String(50))  # email, sms, both
    
    response_deadline = Column(Date)
    customer_response = Column(String(50))  # accepted, declined, no_response
    customer_response_date = Column(Date)
    
    # Offer Details
    locker_offered_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"))
    offer_made_date = Column(Date)
    offer_valid_till = Column(Date)
    offer_declined_reason = Column(Text)
    
    # Allocation
    allocated = Column(Boolean, default=False)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"))
    allocation_date = Column(Date)
    
    removed_date = Column(Date)
    removal_reason = Column(String(200))
    
    # Estimated Waiting Time
    estimated_wait_days = Column(Integer)
    estimated_allocation_date = Column(Date)
    average_turnover_rate = Column(Numeric(5, 2))  # Historical data
    
    # Auto-Allocation Settings
    auto_allocate_enabled = Column(Boolean, default=True)
    accept_alternate_size = Column(Boolean, default=False)
    max_rent_willing = Column(Numeric(10, 2))
    
    # Contact Preferences
    preferred_contact_method = Column(String(50), default='email')
    preferred_contact_time = Column(String(50))
    contact_mobile = Column(String(20))
    contact_email = Column(String(200))
    
    # Special Notes
    special_requirements = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    application = relationship("LockerApplication", foreign_keys=[application_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    locker_offered = relationship("LockerMaster", foreign_keys=[locker_offered_id])
    allocation = relationship("LockerAllocation", foreign_keys=[allocation_id])
    
    def __repr__(self):
        return f"<LockerWaitingList {self.waiting_list_id} - Position: {self.position_in_queue}>"


class LockerKeyHandover(BaseModel):
    """
    Locker Key Handover
    
    Tracks dual key system (customer key + bank master key).
    Records key issuance, return, replacement, and access control.
    """
    __tablename__ = "locker_key_handovers"
    
    # Reference Numbers
    handover_id = Column(String(50), unique=True, nullable=False, index=True)
    key_register_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Links
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), nullable=False, index=True)
    locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Handover Type
    handover_type = Column(String(50), nullable=False)
    # Options: initial_issue, replacement, duplicate, return, surrender
    
    handover_date = Column(Date, nullable=False, index=True)
    
    # Customer Key Details
    customer_key_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_key_type = Column(String(50), default='physical')  # physical, digital
    customer_key_issued = Column(Boolean, default=False)
    customer_key_issue_date = Column(Date)
    
    customer_key_returned = Column(Boolean, default=False)
    customer_key_return_date = Column(Date)
    customer_key_condition = Column(String(50))  # good, damaged, lost
    
    # Bank Master Key Details
    bank_key_number = Column(String(50), nullable=False, index=True)
    bank_key_location = Column(String(200))  # Storage location
    bank_key_custodian = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    bank_key_status = Column(String(50), default='available')  # available, in_use, maintenance
    
    # Dual Key Operation
    requires_dual_key = Column(Boolean, default=True)
    dual_key_policy = Column(Text)  # Policy document reference
    
    # Duplicate Keys
    duplicate_key_issued = Column(Boolean, default=False)
    duplicate_key_number = Column(String(50))
    duplicate_key_reason = Column(String(200))
    duplicate_key_charges = Column(Numeric(10, 2))
    duplicate_key_authorization = Column(String(200))
    
    number_of_duplicate_keys = Column(Integer, default=0)
    duplicate_keys_list = Column(Text)  # JSON array of duplicate key numbers
    
    # Key Recipient
    received_by = Column(String(200), nullable=False)
    received_by_relation = Column(String(100))  # self, joint_holder, nominee, authorized_person
    received_by_id_proof = Column(String(100), nullable=False)
    received_by_id_number = Column(String(100), nullable=False)
    
    # Witness & Verification
    witness_1_name = Column(String(200), nullable=False)
    witness_1_employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    witness_1_signature_path = Column(String(500))
    
    witness_2_name = Column(String(200))
    witness_2_employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    witness_2_signature_path = Column(String(500))
    
    issued_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    issued_by_name = Column(String(200))
    
    # Photo & Signature
    recipient_photo_path = Column(String(500))
    recipient_signature_path = Column(String(500), nullable=False)
    
    biometric_captured = Column(Boolean, default=False)
    biometric_type = Column(String(50))  # fingerprint, iris, face
    biometric_reference = Column(String(200))
    
    # Key Condition & Testing
    key_tested = Column(Boolean, default=False)
    key_working_condition = Column(String(50))  # good, needs_adjustment, defective
    lock_tested = Column(Boolean, default=False)
    lock_condition = Column(String(50))
    
    # Lost Key Handling
    key_lost = Column(Boolean, default=False)
    key_lost_date = Column(Date)
    key_lost_reported_date = Column(Date)
    fir_number = Column(String(100))  # Police FIR if applicable
    indemnity_bond_executed = Column(Boolean, default=False)
    indemnity_bond_path = Column(String(500))
    
    locker_breaking_required = Column(Boolean, default=False)
    locker_breaking_date = Column(Date)
    locker_breaking_charges = Column(Numeric(10, 2))
    
    # Security Deposit
    key_security_deposit = Column(Numeric(10, 2), default=0)
    deposit_refunded = Column(Boolean, default=False)
    deposit_refund_date = Column(Date)
    deposit_refund_amount = Column(Numeric(10, 2))
    
    # Acknowledgment
    acknowledgment_form_path = Column(String(500))
    customer_acknowledgment = Column(Boolean, default=False)
    acknowledgment_date = Column(Date)
    
    # Status
    status = Column(String(50), nullable=False, default='active')
    # Options: active, returned, lost, replaced, cancelled
    
    # Special Instructions
    special_instructions = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    allocation = relationship("LockerAllocation", foreign_keys=[allocation_id])
    locker = relationship("LockerMaster", foreign_keys=[locker_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    bank_key_custodian_user = relationship("User", foreign_keys=[bank_key_custodian])
    witness_1_user = relationship("User", foreign_keys=[witness_1_employee_id])
    witness_2_user = relationship("User", foreign_keys=[witness_2_employee_id])
    issued_by_user = relationship("User", foreign_keys=[issued_by])
    
    def __repr__(self):
        return f"<LockerKeyHandover {self.handover_id} - {self.customer_key_number}>"


class LockerAgreement(BaseModel):
    """
    Locker Agreement
    
    Manages locker rental agreements with terms, conditions, and digital signatures.
    Tracks agreement lifecycle from execution to renewal.
    """
    __tablename__ = "locker_agreements"
    
    # Reference Numbers
    agreement_number = Column(String(50), unique=True, nullable=False, index=True)
    agreement_version = Column(String(20), default='1.0')
    
    # Links
    allocation_id = Column(UUID(as_uuid=True), ForeignKey("locker_allocations.id"), nullable=False, index=True)
    locker_id = Column(UUID(as_uuid=True), ForeignKey("locker_master.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("locker_applications.id"), index=True)
    
    # Agreement Type
    agreement_type = Column(String(50), nullable=False, default='new')
    # Options: new, renewal, modification, transfer
    
    parent_agreement_id = Column(UUID(as_uuid=True), ForeignKey("locker_agreements.id"))
    
    # Agreement Dates
    agreement_date = Column(Date, nullable=False, index=True)
    agreement_start_date = Column(Date, nullable=False)
    agreement_end_date = Column(Date, nullable=False, index=True)
    agreement_duration_months = Column(Integer, nullable=False)
    
    # Template
    template_id = Column(String(50))
    template_name = Column(String(200))
    template_version = Column(String(20))
    
    # Terms & Conditions
    terms_and_conditions = Column(Text, nullable=False)
    dos_and_donts = Column(Text, nullable=False)
    bank_liability_clause = Column(Text, nullable=False)
    insurance_clause = Column(Text)
    access_rules = Column(Text, nullable=False)
    
    # Custom Clauses
    special_terms = Column(Text)
    additional_conditions = Column(Text)
    
    # Financial Terms
    annual_rent = Column(Numeric(10, 2), nullable=False)
    security_deposit = Column(Numeric(10, 2), nullable=False)
    rent_frequency = Column(String(50), default='annual')
    
    rent_escalation_clause = Column(Text)
    rent_escalation_percentage = Column(Numeric(5, 2), default=0)
    rent_escalation_frequency_years = Column(Integer, default=3)
    
    # Signatures
    customer_signature_path = Column(String(500))
    customer_signed = Column(Boolean, default=False)
    customer_signature_date = Column(Date)
    customer_signature_type = Column(String(50))  # physical, digital, e-sign
    customer_digital_signature_id = Column(String(200))
    customer_ip_address = Column(String(50))
    
    joint_holder_signature_required = Column(Boolean, default=False)
    joint_holder_1_signature_path = Column(String(500))
    joint_holder_1_signed = Column(Boolean, default=False)
    joint_holder_1_signature_date = Column(Date)
    
    joint_holder_2_signature_path = Column(String(500))
    joint_holder_2_signed = Column(Boolean, default=False)
    joint_holder_2_signature_date = Column(Date)
    
    bank_authorized_signatory = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    bank_signature_path = Column(String(500))
    bank_signed = Column(Boolean, default=False)
    bank_signature_date = Column(Date)
    bank_official_stamp = Column(Boolean, default=False)
    
    # Witness
    witness_1_name = Column(String(200))
    witness_1_signature_path = Column(String(500))
    witness_1_signature_date = Column(Date)
    
    witness_2_name = Column(String(200))
    witness_2_signature_path = Column(String(500))
    witness_2_signature_date = Column(Date)
    
    # Document Management
    agreement_document_path = Column(String(500), nullable=False)
    agreement_document_type = Column(String(20), default='pdf')  # pdf, docx
    agreement_file_size = Column(Integer)
    
    original_document_location = Column(String(200))  # Physical storage location
    scanned_copy_path = Column(String(500))
    
    # Execution
    is_executed = Column(Boolean, default=False)
    execution_date = Column(Date)
    execution_location = Column(String(200))
    
    all_signatures_complete = Column(Boolean, default=False)
    signatures_completed_date = Column(Date)
    
    # Stamp & Notary
    stamp_paper_required = Column(Boolean, default=False)
    stamp_paper_value = Column(Numeric(10, 2))
    stamp_paper_number = Column(String(100))
    stamp_paper_date = Column(Date)
    
    notarized = Column(Boolean, default=False)
    notary_name = Column(String(200))
    notary_registration_number = Column(String(100))
    notary_date = Column(Date)
    
    # Status
    status = Column(String(50), nullable=False, default='draft', index=True)
    # Options: draft, pending_signature, partially_signed, executed, active, expired, terminated, renewed
    
    # Renewal
    auto_renewal_enabled = Column(Boolean, default=False)
    renewal_notice_period_days = Column(Integer, default=30)
    renewal_notice_sent = Column(Boolean, default=False)
    renewal_notice_date = Column(Date)
    
    renewed = Column(Boolean, default=False)
    renewed_agreement_id = Column(UUID(as_uuid=True), ForeignKey("locker_agreements.id"))
    renewal_date = Column(Date)
    
    # Termination
    terminated = Column(Boolean, default=False)
    termination_date = Column(Date)
    termination_reason = Column(Text)
    termination_initiated_by = Column(String(50))  # customer, bank
    
    notice_period_days = Column(Integer, default=30)
    termination_notice_date = Column(Date)
    
    # Compliance
    kyc_verified_at_execution = Column(Boolean, default=False)
    aml_check_done = Column(Boolean, default=False)
    legal_review_done = Column(Boolean, default=False)
    legal_reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    legal_review_date = Column(Date)
    
    # Amendments
    amendment_count = Column(Integer, default=0)
    last_amendment_date = Column(Date)
    amendment_details = Column(Text)  # JSON array of amendments
    
    # Communication
    customer_copy_sent = Column(Boolean, default=False)
    customer_copy_sent_date = Column(Date)
    customer_copy_delivery_method = Column(String(50))  # email, post, hand_delivery
    
    # Special Notes
    special_instructions = Column(Text)
    internal_notes = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields (inherited from BaseModel)
    
    # Relationships
    allocation = relationship("LockerAllocation", foreign_keys=[allocation_id])
    locker = relationship("LockerMaster", foreign_keys=[locker_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    application = relationship("LockerApplication", foreign_keys=[application_id])
    parent_agreement = relationship("LockerAgreement", remote_side=[BaseModel.id], foreign_keys=[parent_agreement_id])
    renewed_agreement = relationship("LockerAgreement", remote_side=[BaseModel.id], foreign_keys=[renewed_agreement_id])
    bank_signatory = relationship("User", foreign_keys=[bank_authorized_signatory])
    legal_reviewer = relationship("User", foreign_keys=[legal_reviewed_by])
    
    def __repr__(self):
        return f"<LockerAgreement {self.agreement_number} - {self.status}>"
