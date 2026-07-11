"""
Property & Rent Management Database Models

This module contains all database models for property and rent management including:
- Property Master
- Lease Agreements
- Rent Collection
- Utility Management
- Space Allocation

All models follow multi-tenant architecture with soft delete pattern.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base


class Property(Base):
    """
    Property Master
    
    Master data for all properties owned or managed by the organization.
    Includes commercial properties, residential properties, office spaces, etc.
    """
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Property Identification
    property_code = Column(String(50), unique=True, nullable=False, index=True)
    property_name = Column(String(200), nullable=False)
    property_type = Column(String(50), nullable=False, index=True)
    # Types: office, residential, commercial, warehouse, land, mixed_use
    
    # Location Details
    address_line1 = Column(String(500), nullable=False)
    address_line2 = Column(String(500))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default='India')
    pincode = Column(String(20), nullable=False)
    landmark = Column(String(200))
    
    # Property Specifications
    total_area = Column(Numeric(15, 2), nullable=False)  # Total area in sq ft
    area_unit = Column(String(20), default='sq_ft')  # sq_ft, sq_m, acres
    built_up_area = Column(Numeric(15, 2))  # Built-up area
    carpet_area = Column(Numeric(15, 2))  # Usable carpet area
    
    # Building Details
    floors_count = Column(Integer)  # Number of floors
    year_built = Column(Integer)  # Construction year
    
    # Ownership Details
    ownership_type = Column(String(50), nullable=False)
    # Types: owned, leased, managed
    owner_name = Column(String(200))
    owner_contact = Column(String(20))
    owner_email = Column(String(100))
    purchase_date = Column(Date)
    purchase_value = Column(Numeric(15, 2))
    current_market_value = Column(Numeric(15, 2))
    
    # Legal Information
    registration_number = Column(String(100))
    survey_number = Column(String(100))
    khata_number = Column(String(100))
    
    # Utility Connections
    electricity_connection = Column(Boolean, default=False)
    electricity_consumer_number = Column(String(100))
    water_connection = Column(Boolean, default=False)
    water_consumer_number = Column(String(100))
    gas_connection = Column(Boolean, default=False)
    gas_consumer_number = Column(String(100))
    
    # Amenities & Features
    amenities = Column(JSON)  # List of amenities (parking, lift, security, etc.)
    features = Column(JSON)  # Additional features
    
    # Financial Details
    annual_property_tax = Column(Numeric(15, 2))
    annual_maintenance = Column(Numeric(15, 2))
    insurance_premium = Column(Numeric(15, 2))
    insurance_policy_number = Column(String(100))
    insurance_expiry_date = Column(Date)
    
    # Status & Usage
    status = Column(String(50), nullable=False, default='active', index=True)
    # Status: active, inactive, under_maintenance, under_construction, sold
    occupancy_status = Column(String(50), default='vacant', index=True)
    # Status: vacant, occupied, partially_occupied
    
    # Management Details
    property_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    caretaker_name = Column(String(200))
    caretaker_contact = Column(String(20))
    
    # Documents & Photos
    documents = Column(JSON)  # List of document references
    photos = Column(JSON)  # List of photo references
    
    # Additional Information
    description = Column(Text)
    remarks = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    spaces = relationship("PropertySpace", back_populates="property", cascade="all, delete-orphan")
    leases = relationship("Lease", back_populates="property", cascade="all, delete-orphan")
    utilities = relationship("UtilityBill", back_populates="property", cascade="all, delete-orphan")
    maintenance_records = relationship("PropertyMaintenance", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property {self.property_code} - {self.property_name}>"


class PropertySpace(Base):
    """
    Property Space/Unit
    
    Individual units/spaces within a property that can be leased separately.
    Examples: floors, rooms, shops, apartments, parking slots
    """
    __tablename__ = "property_spaces"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Space Identification
    space_code = Column(String(50), unique=True, nullable=False, index=True)
    space_name = Column(String(200), nullable=False)
    space_type = Column(String(50), nullable=False)
    # Types: floor, room, shop, apartment, cabin, parking, warehouse
    
    # Space Details
    floor_number = Column(Integer)
    unit_number = Column(String(50))
    area = Column(Numeric(15, 2), nullable=False)  # Area in sq ft
    area_unit = Column(String(20), default='sq_ft')
    
    # Rent Configuration
    base_rent = Column(Numeric(15, 2), nullable=False)  # Monthly base rent
    maintenance_charges = Column(Numeric(10, 2))  # Monthly maintenance
    security_deposit = Column(Numeric(15, 2))  # Required security deposit
    
    # Features
    furnishing_status = Column(String(50))  # unfurnished, semi_furnished, fully_furnished
    amenities = Column(JSON)  # List of amenities
    
    # Status
    status = Column(String(50), nullable=False, default='available', index=True)
    # Status: available, occupied, reserved, under_maintenance
    
    # Current Occupancy
    current_lease_id = Column(Integer, ForeignKey("leases.id"))
    occupancy_start_date = Column(Date)
    
    # Additional Information
    description = Column(Text)
    photos = Column(JSON)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    property = relationship("Property", back_populates="spaces")
    current_lease = relationship("Lease", foreign_keys=[current_lease_id])
    allocations = relationship("SpaceAllocation", back_populates="space", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PropertySpace {self.space_code} - {self.space_name}>"


class Lease(Base):
    """
    Lease Agreement
    
    Lease/rental agreements between property owner and tenants.
    Tracks lease terms, rent, deposits, and agreement details.
    """
    __tablename__ = "leases"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    
    # Lease Identification
    lease_number = Column(String(50), unique=True, nullable=False, index=True)
    lease_type = Column(String(50), nullable=False)
    # Types: commercial, residential, office, warehouse
    
    # Tenant Information (Customer or External)
    lessee_type = Column(String(50), nullable=False)  # customer, employee, external
    lessee_customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    lessee_employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    lessee_name = Column(String(200), nullable=False)
    lessee_contact = Column(String(20), nullable=False)
    lessee_email = Column(String(100))
    lessee_address = Column(Text)
    lessee_id_proof_type = Column(String(50))
    lessee_id_proof_number = Column(String(100))
    
    # Lease Period
    lease_start_date = Column(Date, nullable=False, index=True)
    lease_end_date = Column(Date, nullable=False, index=True)
    lease_duration_months = Column(Integer, nullable=False)
    notice_period_days = Column(Integer, default=30)
    
    # Rent Details
    monthly_rent = Column(Numeric(15, 2), nullable=False)
    maintenance_charges = Column(Numeric(10, 2))
    other_charges = Column(Numeric(10, 2))
    total_monthly_payment = Column(Numeric(15, 2), nullable=False)
    
    # Payment Terms
    rent_due_day = Column(Integer, default=5)  # Day of month rent is due
    payment_frequency = Column(String(50), default='monthly')
    # Frequency: monthly, quarterly, annually
    advance_months = Column(Integer, default=0)  # Advance rent paid
    
    # Deposit Details
    security_deposit = Column(Numeric(15, 2), nullable=False)
    deposit_paid_date = Column(Date)
    deposit_refundable = Column(Boolean, default=True)
    
    # Rent Escalation
    escalation_applicable = Column(Boolean, default=False)
    escalation_percentage = Column(Numeric(5, 2))  # Annual escalation %
    escalation_frequency_months = Column(Integer)  # Escalation every X months
    next_escalation_date = Column(Date)
    
    # Agreement Details
    agreement_date = Column(Date, nullable=False)
    registration_number = Column(String(100))
    registration_date = Column(Date)
    stamp_duty_paid = Column(Numeric(10, 2))
    
    # Terms & Conditions
    terms_conditions = Column(Text)
    special_clauses = Column(Text)
    
    # Renewal
    auto_renewal = Column(Boolean, default=False)
    renewal_count = Column(Integer, default=0)
    parent_lease_id = Column(Integer, ForeignKey("leases.id"))
    
    # Status
    status = Column(String(50), nullable=False, default='draft', index=True)
    # Status: draft, active, expired, terminated, renewed
    
    # Termination Details
    termination_date = Column(Date)
    termination_reason = Column(String(500))
    termination_initiated_by = Column(String(50))  # lessee, lessor
    notice_given_date = Column(Date)
    
    # Lock-in Period
    lock_in_period_months = Column(Integer)
    lock_in_end_date = Column(Date)
    
    # Utilities
    electricity_included = Column(Boolean, default=False)
    water_included = Column(Boolean, default=False)
    gas_included = Column(Boolean, default=False)
    
    # Documents
    agreement_document = Column(String(500))  # Document reference
    documents = Column(JSON)  # Additional documents
    
    # Additional Information
    remarks = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    property = relationship("Property", back_populates="leases")
    lessee_customer = relationship("Customer", foreign_keys=[lessee_customer_id])
    lessee_employee = relationship("Employee", foreign_keys=[lessee_employee_id])
    rent_payments = relationship("RentPayment", back_populates="lease", cascade="all, delete-orphan")
    space_allocations = relationship("SpaceAllocation", back_populates="lease", cascade="all, delete-orphan")
    renewed_leases = relationship("Lease", foreign_keys=[parent_lease_id])
    
    def __repr__(self):
        return f"<Lease {self.lease_number} - {self.lessee_name}>"


class SpaceAllocation(Base):
    """
    Space Allocation
    
    Maps which spaces are allocated to which lease.
    Supports multiple spaces per lease (e.g., office + parking).
    """
    __tablename__ = "space_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"), nullable=False, index=True)
    space_id = Column(Integer, ForeignKey("property_spaces.id"), nullable=False, index=True)
    
    # Allocation Details
    allocation_date = Column(Date, nullable=False)
    allocation_type = Column(String(50), default='primary')
    # Types: primary, additional, temporary
    
    # Rent Allocation
    allocated_rent = Column(Numeric(15, 2))  # Portion of rent for this space
    
    # Status
    status = Column(String(50), nullable=False, default='active', index=True)
    # Status: active, inactive, vacated
    
    # Vacation Details
    vacated_date = Column(Date)
    vacate_remarks = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    lease = relationship("Lease", back_populates="space_allocations")
    space = relationship("PropertySpace", back_populates="allocations")
    
    def __repr__(self):
        return f"<SpaceAllocation Lease:{self.lease_id} Space:{self.space_id}>"


class RentPayment(Base):
    """
    Rent Payment
    
    Records rent payments made against lease agreements.
    Tracks payment schedules, actual payments, and outstanding amounts.
    """
    __tablename__ = "rent_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"), nullable=False, index=True)
    
    # Payment Identification
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    receipt_number = Column(String(50))
    
    # Payment Period
    payment_period_start = Column(Date, nullable=False)
    payment_period_end = Column(Date, nullable=False)
    payment_month = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    due_date = Column(Date, nullable=False, index=True)
    
    # Amount Details
    rent_amount = Column(Numeric(15, 2), nullable=False)
    maintenance_amount = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    late_fee = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment Status
    payment_status = Column(String(50), nullable=False, default='pending', index=True)
    # Status: pending, partial, paid, overdue, waived
    
    # Actual Payment
    paid_amount = Column(Numeric(15, 2), default=0)
    outstanding_amount = Column(Numeric(15, 2))
    payment_date = Column(Date, index=True)
    
    # Payment Details
    payment_mode = Column(String(50))
    # Modes: cash, cheque, neft, rtgs, imps, upi, online
    payment_reference = Column(String(100))  # Transaction ID, Cheque number
    bank_name = Column(String(200))
    
    # Late Payment
    days_overdue = Column(Integer, default=0)
    late_fee_rate = Column(Numeric(5, 2))  # Percentage per day/month
    
    # TDS Deduction
    tds_applicable = Column(Boolean, default=False)
    tds_percentage = Column(Numeric(5, 2))
    tds_amount = Column(Numeric(10, 2))
    tds_deducted = Column(Boolean, default=False)
    
    # Additional Information
    remarks = Column(Text)
    internal_notes = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    collected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    lease = relationship("Lease", back_populates="rent_payments")
    
    def __repr__(self):
        return f"<RentPayment {self.payment_number} - {self.payment_month}>"


class UtilityBill(Base):
    """
    Utility Bill
    
    Tracks utility bills (electricity, water, gas) for properties.
    Can be allocated to tenants based on lease agreements or meter readings.
    """
    __tablename__ = "utility_bills"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"), index=True)  # Optional: if allocated to tenant
    
    # Bill Identification
    bill_number = Column(String(50), unique=True, nullable=False, index=True)
    utility_type = Column(String(50), nullable=False, index=True)
    # Types: electricity, water, gas, sewage, maintenance, others
    
    # Bill Period
    bill_period_start = Column(Date, nullable=False)
    bill_period_end = Column(Date, nullable=False)
    bill_month = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    
    # Utility Provider Details
    provider_name = Column(String(200))
    consumer_number = Column(String(100))
    
    # Meter Reading (if applicable)
    previous_reading = Column(Numeric(15, 2))
    current_reading = Column(Numeric(15, 2))
    consumption_units = Column(Numeric(15, 2))  # Units consumed
    
    # Amount Details
    fixed_charges = Column(Numeric(10, 2), default=0)
    consumption_charges = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    late_fee = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment Status
    payment_status = Column(String(50), nullable=False, default='pending', index=True)
    # Status: pending, paid, partial, overdue
    
    # Payment Details
    paid_amount = Column(Numeric(15, 2), default=0)
    payment_date = Column(Date)
    payment_mode = Column(String(50))
    payment_reference = Column(String(100))
    
    # Allocation to Tenant
    allocated_to_tenant = Column(Boolean, default=False)
    tenant_share_percentage = Column(Numeric(5, 2))  # % allocated to tenant
    tenant_share_amount = Column(Numeric(10, 2))
    tenant_payment_received = Column(Boolean, default=False)
    
    # Bill Document
    bill_document = Column(String(500))  # Document reference
    
    # Additional Information
    remarks = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    property = relationship("Property", back_populates="utilities")
    lease = relationship("Lease")
    
    def __repr__(self):
        return f"<UtilityBill {self.bill_number} - {self.utility_type}>"


class PropertyMaintenance(Base):
    """
    Property Maintenance
    
    Tracks maintenance activities, repairs, and service requests for properties.
    """
    __tablename__ = "property_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    space_id = Column(Integer, ForeignKey("property_spaces.id"))  # Optional: specific space
    
    # Maintenance Identification
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    maintenance_type = Column(String(50), nullable=False, index=True)
    # Types: repair, inspection, cleaning, painting, electrical, plumbing, others
    
    # Request Details
    request_date = Column(Date, nullable=False)
    requested_by = Column(String(200))
    priority = Column(String(50), default='medium')
    # Priority: low, medium, high, urgent
    
    # Description
    issue_description = Column(Text, nullable=False)
    category = Column(String(50))
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_date = Column(Date)
    
    # Vendor Details (if outsourced)
    vendor_name = Column(String(200))
    vendor_contact = Column(String(20))
    vendor_amount = Column(Numeric(15, 2))
    
    # Schedule
    scheduled_date = Column(Date)
    completed_date = Column(Date)
    
    # Status
    status = Column(String(50), nullable=False, default='open', index=True)
    # Status: open, assigned, in_progress, completed, cancelled
    
    # Cost Details
    estimated_cost = Column(Numeric(15, 2))
    actual_cost = Column(Numeric(15, 2))
    
    # Resolution
    resolution_notes = Column(Text)
    customer_satisfaction = Column(Integer)  # Rating 1-5
    
    # Documents & Photos
    before_photos = Column(JSON)
    after_photos = Column(JSON)
    documents = Column(JSON)
    
    # Additional Information
    remarks = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    property = relationship("Property", back_populates="maintenance_records")
    space = relationship("PropertySpace")
    
    def __repr__(self):
        return f"<PropertyMaintenance {self.ticket_number} - {self.maintenance_type}>"
