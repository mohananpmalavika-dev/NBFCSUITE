"""
Fixed Asset Management Database Models
Comprehensive asset lifecycle management
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, Boolean, Text, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.shared.database.base import Base


class AssetCategory(str, Enum):
    """Asset category classification"""
    LAND = "land"
    BUILDING = "building"
    PLANT_MACHINERY = "plant_machinery"
    FURNITURE_FIXTURES = "furniture_fixtures"
    VEHICLES = "vehicles"
    COMPUTER_EQUIPMENT = "computer_equipment"
    OFFICE_EQUIPMENT = "office_equipment"
    LEASEHOLD_IMPROVEMENTS = "leasehold_improvements"
    INTANGIBLE_ASSETS = "intangible_assets"
    OTHER = "other"


class DepreciationMethod(str, Enum):
    """Depreciation calculation methods"""
    STRAIGHT_LINE = "straight_line"  # SLM
    WRITTEN_DOWN_VALUE = "written_down_value"  # WDV
    DOUBLE_DECLINING = "double_declining"
    SUM_OF_YEARS = "sum_of_years"
    UNITS_OF_PRODUCTION = "units_of_production"
    NO_DEPRECIATION = "no_depreciation"


class AssetStatus(str, Enum):
    """Asset lifecycle status"""
    ACTIVE = "active"
    IN_MAINTENANCE = "in_maintenance"
    UNDER_REPAIR = "under_repair"
    IDLE = "idle"
    DISPOSED = "disposed"
    SOLD = "sold"
    WRITTEN_OFF = "written_off"
    TRANSFERRED = "transferred"
    LOST = "lost"
    STOLEN = "stolen"


class MaintenanceType(str, Enum):
    """Types of maintenance"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    BREAKDOWN = "breakdown"
    SCHEDULED = "scheduled"
    INSPECTION = "inspection"


class MaintenanceStatus(str, Enum):
    """Maintenance request status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransferStatus(str, Enum):
    """Asset transfer status"""
    INITIATED = "initiated"
    APPROVED = "approved"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DisposalMethod(str, Enum):
    """Methods of asset disposal"""
    SALE = "sale"
    SCRAP = "scrap"
    DONATION = "donation"
    TRADE_IN = "trade_in"
    WRITE_OFF = "write_off"
    DESTRUCTION = "destruction"


class VerificationStatus(str, Enum):
    """Physical verification status"""
    FOUND = "found"
    NOT_FOUND = "not_found"
    DAMAGED = "damaged"
    NEEDS_REPAIR = "needs_repair"
    DISCREPANCY = "discrepancy"


# ============================================================================
# Fixed Asset Master
# ============================================================================

class FixedAsset(Base):
    """Fixed asset master register"""
    __tablename__ = "fixed_assets"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    asset_code = Column(String(50), nullable=False, unique=True, index=True)
    asset_name = Column(String(200), nullable=False)
    asset_description = Column(Text)
    
    # Classification
    asset_category = Column(SQLEnum(AssetCategory), nullable=False)
    sub_category = Column(String(100))
    asset_type = Column(String(100))
    asset_class = Column(String(50))  # For grouping and reporting
    
    # Acquisition details
    acquisition_date = Column(Date, nullable=False)
    purchase_date = Column(Date)
    invoice_number = Column(String(100))
    invoice_date = Column(Date)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    supplier_name = Column(String(200))
    
    # Financial details
    purchase_cost = Column(Numeric(18, 2), nullable=False, default=0.00)
    installation_cost = Column(Numeric(18, 2), default=0.00)
    transportation_cost = Column(Numeric(18, 2), default=0.00)
    other_costs = Column(Numeric(18, 2), default=0.00)
    total_cost = Column(Numeric(18, 2), nullable=False)  # Sum of all costs
    
    # Depreciation configuration
    depreciation_method = Column(SQLEnum(DepreciationMethod), nullable=False, default=DepreciationMethod.STRAIGHT_LINE)
    depreciation_rate = Column(Numeric(5, 2))  # Percentage
    useful_life_years = Column(Integer)  # In years
    useful_life_units = Column(Integer)  # For units of production method
    salvage_value = Column(Numeric(18, 2), default=0.00)
    residual_value = Column(Numeric(18, 2), default=0.00)
    
    # Current depreciation status
    accumulated_depreciation = Column(Numeric(18, 2), default=0.00)
    net_book_value = Column(Numeric(18, 2))  # total_cost - accumulated_depreciation
    current_value = Column(Numeric(18, 2))
    last_depreciation_date = Column(Date)
    depreciation_start_date = Column(Date)
    
    # Location and custodian
    location_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    location_name = Column(String(200))
    department_id = Column(Integer)
    department_name = Column(String(100))
    custodian_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    custodian_name = Column(String(200))
    
    # Physical details
    serial_number = Column(String(100))
    model_number = Column(String(100))
    manufacturer = Column(String(200))
    brand = Column(String(100))
    year_of_manufacture = Column(Integer)
    
    # Warranty and insurance
    warranty_expiry_date = Column(Date)
    warranty_provider = Column(String(200))
    insurance_policy_number = Column(String(100))
    insurance_expiry_date = Column(Date)
    insurance_company = Column(String(200))
    insurance_value = Column(Numeric(18, 2))
    
    # Status and lifecycle
    asset_status = Column(SQLEnum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE)
    status_change_date = Column(Date)
    status_reason = Column(Text)
    in_use = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Disposal details (if disposed)
    disposal_date = Column(Date)
    disposal_method = Column(SQLEnum(DisposalMethod))
    disposal_value = Column(Numeric(18, 2))
    disposal_cost = Column(Numeric(18, 2))
    disposal_gain_loss = Column(Numeric(18, 2))
    disposal_approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    disposal_notes = Column(Text)
    
    # Accounting integration
    asset_account_id = Column(Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"))
    depreciation_account_id = Column(Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"))
    expense_account_id = Column(Integer, ForeignKey("chart_of_accounts.id", ondelete="SET NULL"))
    
    # Additional information
    barcode = Column(String(100), unique=True)
    qr_code = Column(String(200))
    rfid_tag = Column(String(100))
    image_url = Column(String(500))
    document_urls = Column(Text)  # JSON array of document URLs
    
    # Tags and metadata
    tags = Column(Text)  # JSON array of tags
    custom_fields = Column(Text)  # JSON object for custom fields
    notes = Column(Text)
    remarks = Column(Text)
    
    # Audit fields
    is_verified = Column(Boolean, default=False)
    last_verification_date = Column(Date)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    depreciation_schedules = relationship("AssetDepreciation", back_populates="asset", cascade="all, delete-orphan")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset", cascade="all, delete-orphan")
    transfer_history = relationship("AssetTransfer", back_populates="asset", cascade="all, delete-orphan")
    verification_history = relationship("AssetVerification", back_populates="asset", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_asset_tenant_code', 'tenant_id', 'asset_code'),
        Index('idx_asset_tenant_status', 'tenant_id', 'asset_status'),
        Index('idx_asset_tenant_category', 'tenant_id', 'asset_category'),
        Index('idx_asset_tenant_location', 'tenant_id', 'location_id'),
        Index('idx_asset_tenant_custodian', 'tenant_id', 'custodian_id'),
        Index('idx_asset_barcode', 'barcode'),
    )


# ============================================================================
# Asset Depreciation Schedule
# ============================================================================

class AssetDepreciation(Base):
    """Asset depreciation schedule and history"""
    __tablename__ = "asset_depreciation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("fixed_assets.id", ondelete="CASCADE"), nullable=False)
    
    # Period information
    financial_year = Column(Integer, nullable=False)
    financial_month = Column(Integer)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    depreciation_date = Column(Date, nullable=False)
    
    # Depreciation details
    depreciation_method = Column(SQLEnum(DepreciationMethod), nullable=False)
    opening_wdv = Column(Numeric(18, 2), nullable=False)  # Written Down Value at start
    depreciation_amount = Column(Numeric(18, 2), nullable=False)
    accumulated_depreciation = Column(Numeric(18, 2), nullable=False)
    closing_wdv = Column(Numeric(18, 2), nullable=False)  # WDV at end
    
    # Calculation details
    depreciation_rate = Column(Numeric(5, 2))
    days_in_period = Column(Integer)
    is_partial_year = Column(Boolean, default=False)
    
    # Status
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime)
    posted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"))
    
    # Reversal
    is_reversed = Column(Boolean, default=False)
    reversed_at = Column(DateTime)
    reversed_by = Column(Integer)
    reversal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="SET NULL"))
    reversal_reason = Column(Text)
    
    # Audit
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="depreciation_schedules")
    
    # Indexes
    __table_args__ = (
        Index('idx_depreciation_tenant_asset', 'tenant_id', 'asset_id'),
        Index('idx_depreciation_tenant_year', 'tenant_id', 'financial_year'),
        Index('idx_depreciation_date', 'depreciation_date'),
    )


# ============================================================================
# Asset Maintenance
# ============================================================================

class AssetMaintenance(Base):
    """Asset maintenance tracking"""
    __tablename__ = "asset_maintenance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("fixed_assets.id", ondelete="CASCADE"), nullable=False)
    
    # Maintenance identification
    maintenance_number = Column(String(50), nullable=False, unique=True, index=True)
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    maintenance_category = Column(String(100))
    
    # Schedule information
    scheduled_date = Column(Date)
    scheduled_time = Column(String(20))
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    next_maintenance_date = Column(Date)
    
    # Status and priority
    status = Column(SQLEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.PENDING)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Service provider details
    is_internal = Column(Boolean, default=True)
    service_provider_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    service_provider_name = Column(String(200))
    technician_name = Column(String(200))
    technician_contact = Column(String(50))
    
    # Work details
    problem_description = Column(Text)
    work_performed = Column(Text)
    parts_replaced = Column(Text)
    recommendations = Column(Text)
    
    # Cost details
    labor_cost = Column(Numeric(18, 2), default=0.00)
    parts_cost = Column(Numeric(18, 2), default=0.00)
    other_charges = Column(Numeric(18, 2), default=0.00)
    total_cost = Column(Numeric(18, 2), default=0.00)
    
    # Asset downtime
    downtime_hours = Column(Numeric(8, 2))
    downtime_cost = Column(Numeric(18, 2))
    
    # Approval workflow
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Documents
    invoice_number = Column(String(100))
    invoice_date = Column(Date)
    invoice_amount = Column(Numeric(18, 2))
    document_urls = Column(Text)  # JSON array
    
    # Additional information
    warranty_claim = Column(Boolean, default=False)
    warranty_claim_number = Column(String(100))
    meter_reading = Column(Integer)
    notes = Column(Text)
    remarks = Column(Text)
    
    # Audit
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="maintenance_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_maintenance_tenant_asset', 'tenant_id', 'asset_id'),
        Index('idx_maintenance_tenant_status', 'tenant_id', 'status'),
        Index('idx_maintenance_scheduled_date', 'scheduled_date'),
    )


# ============================================================================
# Asset Transfer
# ============================================================================

class AssetTransfer(Base):
    """Asset transfer and movement tracking"""
    __tablename__ = "asset_transfers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("fixed_assets.id", ondelete="CASCADE"), nullable=False)
    
    # Transfer identification
    transfer_number = Column(String(50), nullable=False, unique=True, index=True)
    transfer_date = Column(Date, nullable=False)
    transfer_type = Column(String(50), default="internal")  # internal, external, temporary
    
    # Source details
    from_location_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    from_location_name = Column(String(200))
    from_department_id = Column(Integer)
    from_department_name = Column(String(100))
    from_custodian_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    from_custodian_name = Column(String(200))
    
    # Destination details
    to_location_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    to_location_name = Column(String(200))
    to_department_id = Column(Integer)
    to_department_name = Column(String(100))
    to_custodian_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    to_custodian_name = Column(String(200))
    
    # Transfer details
    reason = Column(Text)
    transfer_mode = Column(String(50))  # own_vehicle, third_party, courier, hand_carry
    transport_details = Column(Text)
    estimated_arrival_date = Column(Date)
    actual_arrival_date = Column(Date)
    
    # Status
    status = Column(SQLEnum(TransferStatus), nullable=False, default=TransferStatus.INITIATED)
    status_notes = Column(Text)
    
    # Handover details
    handover_date = Column(Date)
    handover_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    received_date = Column(Date)
    received_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    # Condition at transfer
    condition_at_transfer = Column(String(50))
    condition_at_receipt = Column(String(50))
    condition_notes = Column(Text)
    
    # Cost details
    transfer_cost = Column(Numeric(18, 2), default=0.00)
    insurance_cost = Column(Numeric(18, 2), default=0.00)
    other_charges = Column(Numeric(18, 2), default=0.00)
    total_cost = Column(Numeric(18, 2), default=0.00)
    
    # Approval workflow
    initiated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    rejected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Documents
    document_urls = Column(Text)  # JSON array
    
    # Additional information
    remarks = Column(Text)
    notes = Column(Text)
    
    # Audit
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="transfer_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_transfer_tenant_asset', 'tenant_id', 'asset_id'),
        Index('idx_transfer_tenant_status', 'tenant_id', 'status'),
        Index('idx_transfer_date', 'transfer_date'),
    )


# ============================================================================
# Asset Physical Verification
# ============================================================================

class AssetVerification(Base):
    """Physical verification of assets"""
    __tablename__ = "asset_verifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Verification cycle
    verification_cycle_id = Column(Integer, ForeignKey("asset_verification_cycles.id", ondelete="CASCADE"))
    verification_number = Column(String(50), nullable=False, unique=True, index=True)
    verification_date = Column(Date, nullable=False)
    
    # Asset details
    asset_id = Column(Integer, ForeignKey("fixed_assets.id", ondelete="CASCADE"), nullable=False)
    asset_code = Column(String(50), nullable=False)
    
    # Verification result
    verification_status = Column(SQLEnum(VerificationStatus), nullable=False)
    is_found = Column(Boolean, default=True)
    condition = Column(String(50))  # excellent, good, fair, poor, damaged
    
    # Physical verification details
    location_verified = Column(Boolean, default=True)
    location_remarks = Column(Text)
    custodian_verified = Column(Boolean, default=True)
    custodian_remarks = Column(Text)
    
    # Asset condition assessment
    functional_status = Column(String(50))  # working, not_working, partially_working
    requires_repair = Column(Boolean, default=False)
    requires_maintenance = Column(Boolean, default=False)
    recommended_action = Column(Text)
    
    # Discrepancy details
    has_discrepancy = Column(Boolean, default=False)
    discrepancy_type = Column(String(100))  # location_mismatch, custodian_mismatch, condition_issue, missing, excess
    discrepancy_description = Column(Text)
    discrepancy_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    
    # Expected vs actual
    expected_location_id = Column(Integer)
    expected_location_name = Column(String(200))
    actual_location_id = Column(Integer)
    actual_location_name = Column(String(200))
    
    expected_custodian_id = Column(Integer)
    expected_custodian_name = Column(String(200))
    actual_custodian_id = Column(Integer)
    actual_custodian_name = Column(String(200))
    
    # Verification team
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    verified_by_name = Column(String(200))
    verification_team = Column(Text)  # JSON array of user IDs
    
    # Images and documents
    image_urls = Column(Text)  # JSON array of image URLs
    document_urls = Column(Text)  # JSON array
    
    # GPS location
    gps_latitude = Column(String(50))
    gps_longitude = Column(String(50))
    gps_accuracy = Column(String(20))
    
    # Additional information
    notes = Column(Text)
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    asset = relationship("FixedAsset", back_populates="verification_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_verification_tenant_asset', 'tenant_id', 'asset_id'),
        Index('idx_verification_tenant_cycle', 'tenant_id', 'verification_cycle_id'),
        Index('idx_verification_date', 'verification_date'),
        Index('idx_verification_status', 'verification_status'),
    )


# ============================================================================
# Asset Verification Cycle
# ============================================================================

class AssetVerificationCycle(Base):
    """Asset physical verification cycles"""
    __tablename__ = "asset_verification_cycles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    
    # Cycle identification
    cycle_number = Column(String(50), nullable=False, unique=True, index=True)
    cycle_name = Column(String(200), nullable=False)
    financial_year = Column(Integer, nullable=False)
    
    # Schedule
    planned_start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Scope
    scope = Column(String(50), default="all")  # all, category, location, department
    category_filter = Column(Text)  # JSON array
    location_filter = Column(Text)  # JSON array
    department_filter = Column(Text)  # JSON array
    
    # Team
    team_lead_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    team_lead_name = Column(String(200))
    team_members = Column(Text)  # JSON array of user IDs
    
    # Statistics
    total_assets = Column(Integer, default=0)
    verified_assets = Column(Integer, default=0)
    pending_assets = Column(Integer, default=0)
    found_assets = Column(Integer, default=0)
    not_found_assets = Column(Integer, default=0)
    discrepancy_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="planned")  # planned, in_progress, completed, cancelled
    completion_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Approval
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Report
    report_generated = Column(Boolean, default=False)
    report_url = Column(String(500))
    report_generated_at = Column(DateTime)
    
    # Additional information
    description = Column(Text)
    notes = Column(Text)
    remarks = Column(Text)
    
    # Audit
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Indexes
    __table_args__ = (
        Index('idx_cycle_tenant_year', 'tenant_id', 'financial_year'),
        Index('idx_cycle_status', 'status'),
    )
