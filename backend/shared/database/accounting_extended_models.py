"""
Accounting Extended Database Models
TDS, GST, Asset Management, Accounts Payable, Accounts Receivable
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text,
    ForeignKey, Enum, Index, CheckConstraint, DECIMAL
)
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.connection import Base


# ============================================================================
# TDS (Tax Deducted at Source) Models
# ============================================================================

class TDSSection(str, enum.Enum):
    """TDS Section Codes"""
    SECTION_194A = "194A"  # Interest other than securities
    SECTION_194C = "194C"  # Contractors/Sub-contractors
    SECTION_194H = "194H"  # Commission/Brokerage
    SECTION_194I = "194I"  # Rent
    SECTION_194J = "194J"  # Professional/Technical Services
    SECTION_194K = "194K"  # Income from units
    SECTION_194LA = "194LA"  # Compensation on land acquisition
    SECTION_194M = "194M"  # Payment to contractors/professionals
    SECTION_192 = "192"    # Salary
    SECTION_193 = "193"    # Interest on securities
    SECTION_194B = "194B"  # Lottery/Crossword/Game show winnings
    SECTION_194D = "194D"  # Insurance commission
    SECTION_195 = "195"    # Non-resident payments


class TDSPaymentStatus(str, enum.Enum):
    """TDS Payment Status"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    REVERSED = "reversed"


class TDSReturnType(str, enum.Enum):
    """TDS Return Types"""
    FORM_24Q = "24Q"  # Salary TDS
    FORM_26Q = "26Q"  # Non-salary TDS
    FORM_27Q = "27Q"  # Non-resident TDS
    FORM_27EQ = "27EQ"  # TCS return


class TDSReturnStatus(str, enum.Enum):
    """TDS Return Filing Status"""
    DRAFT = "draft"
    FILED = "filed"
    ACKNOWLEDGED = "acknowledged"
    REVISED = "revised"
    DEFECTIVE = "defective"


class TDSCertificateStatus(str, enum.Enum):
    """TDS Certificate Status"""
    GENERATED = "generated"
    ISSUED = "issued"
    CANCELLED = "cancelled"


class TDSSectionMaster(Base):
    """TDS Section Master - Configuration"""
    __tablename__ = "tds_section_master"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Section details
    section_code = Column(Enum(TDSSection), nullable=False, index=True)
    section_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rate configuration
    financial_year = Column(Integer, nullable=False, index=True)
    tds_rate = Column(Numeric(5, 2), nullable=False)  # e.g., 10.00 for 10%
    surcharge_rate = Column(Numeric(5, 2), default=0.00)
    cess_rate = Column(Numeric(5, 2), default=0.00)
    
    # Threshold limits
    threshold_limit = Column(Numeric(15, 2), nullable=True)  # Annual threshold
    single_transaction_limit = Column(Numeric(15, 2), nullable=True)
    
    # PAN requirements
    rate_without_pan = Column(Numeric(5, 2), nullable=True)  # Higher rate if no PAN
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index("ix_tds_section_tenant_fy", "tenant_id", "section_code", "financial_year", unique=True),
    )


class TDSDeduction(Base):
    """TDS Deduction Records"""
    __tablename__ = "tds_deductions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Deduction details
    deduction_number = Column(String(50), nullable=False, unique=True, index=True)
    deduction_date = Column(Date, nullable=False, index=True)
    financial_year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=False)  # 1, 2, 3, 4
    
    # Section
    section_id = Column(Integer, ForeignKey("tds_section_master.id"), nullable=False)
    section_code = Column(Enum(TDSSection), nullable=False, index=True)
    
    # Deductee details
    deductee_type = Column(String(50), nullable=False)  # vendor, customer, employee
    deductee_id = Column(Integer, nullable=False)
    deductee_name = Column(String(200), nullable=False)
    deductee_pan = Column(String(10), nullable=True, index=True)
    
    # Transaction reference
    transaction_type = Column(String(50), nullable=False)  # payment, interest, etc.
    transaction_id = Column(Integer, nullable=False)
    transaction_date = Column(Date, nullable=False)
    invoice_number = Column(String(100), nullable=True)
    
    # Amounts
    gross_amount = Column(Numeric(15, 2), nullable=False)
    tds_rate = Column(Numeric(5, 2), nullable=False)
    tds_amount = Column(Numeric(15, 2), nullable=False)
    surcharge = Column(Numeric(15, 2), default=0.00)
    cess = Column(Numeric(15, 2), default=0.00)
    total_tds = Column(Numeric(15, 2), nullable=False)
    net_amount = Column(Numeric(15, 2), nullable=False)  # gross - total_tds
    
    # Challan reference
    challan_id = Column(Integer, ForeignKey("tds_challans.id"), nullable=True)
    
    # Certificate reference
    certificate_id = Column(Integer, ForeignKey("tds_certificates.id"), nullable=True)
    
    # Status
    payment_status = Column(Enum(TDSPaymentStatus), default=TDSPaymentStatus.PENDING)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    section = relationship("TDSSectionMaster")
    challan = relationship("TDSChallan", back_populates="deductions")
    certificate = relationship("TDSCertificate", back_populates="deductions")
    
    __table_args__ = (
        Index("ix_tds_deduction_tenant_date", "tenant_id", "deduction_date"),
        Index("ix_tds_deduction_deductee", "deductee_type", "deductee_id"),
        Index("ix_tds_deduction_transaction", "transaction_type", "transaction_id"),
    )


class TDSChallan(Base):
    """TDS Payment Challans (Form 281)"""
    __tablename__ = "tds_challans"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Challan details
    challan_number = Column(String(50), nullable=False, unique=True, index=True)
    bsr_code = Column(String(7), nullable=False)  # Bank branch code
    challan_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date, nullable=False)
    
    # Period
    financial_year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=False)
    assessment_year = Column(String(10), nullable=False)  # e.g., "2026-27"
    
    # Section
    section_code = Column(Enum(TDSSection), nullable=False)
    
    # Bank details
    bank_name = Column(String(200), nullable=False)
    branch_name = Column(String(200), nullable=True)
    
    # Amounts
    total_tds_amount = Column(Numeric(15, 2), nullable=False)
    interest_amount = Column(Numeric(15, 2), default=0.00)
    penalty_amount = Column(Numeric(15, 2), default=0.00)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment details
    payment_mode = Column(String(50), nullable=False)  # online, cheque, cash
    cheque_number = Column(String(50), nullable=True)
    transaction_reference = Column(String(100), nullable=True)
    
    # Status
    payment_status = Column(Enum(TDSPaymentStatus), default=TDSPaymentStatus.PAID)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    deductions = relationship("TDSDeduction", back_populates="challan")
    
    __table_args__ = (
        Index("ix_tds_challan_tenant_fy", "tenant_id", "financial_year", "quarter"),
    )


class TDSCertificate(Base):
    """TDS Certificates (Form 16A)"""
    __tablename__ = "tds_certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Certificate details
    certificate_number = Column(String(50), nullable=False, unique=True, index=True)
    issue_date = Column(Date, nullable=False)
    
    # Period
    financial_year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    
    # Deductee details
    deductee_type = Column(String(50), nullable=False)
    deductee_id = Column(Integer, nullable=False, index=True)
    deductee_name = Column(String(200), nullable=False)
    deductee_pan = Column(String(10), nullable=False)
    deductee_address = Column(Text, nullable=True)
    
    # Deductor details (company)
    deductor_tan = Column(String(10), nullable=False)
    deductor_pan = Column(String(10), nullable=False)
    deductor_name = Column(String(200), nullable=False)
    
    # Amounts
    total_gross_amount = Column(Numeric(15, 2), nullable=False)
    total_tds_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(Enum(TDSCertificateStatus), default=TDSCertificateStatus.GENERATED)
    
    # Digital signature
    is_digitally_signed = Column(Boolean, default=False)
    signature_date = Column(DateTime, nullable=True)
    
    # File storage
    certificate_file_path = Column(String(500), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    deductions = relationship("TDSDeduction", back_populates="certificate")
    
    __table_args__ = (
        Index("ix_tds_cert_tenant_deductee", "tenant_id", "deductee_id", "financial_year"),
    )


class TDSReturn(Base):
    """TDS Return Filing Records"""
    __tablename__ = "tds_returns"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Return details
    return_number = Column(String(50), nullable=False, unique=True, index=True)
    return_type = Column(Enum(TDSReturnType), nullable=False)
    
    # Period
    financial_year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    
    # Filing details
    filing_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=False)
    acknowledgement_number = Column(String(50), nullable=True)
    acknowledgement_date = Column(Date, nullable=True)
    
    # Amounts summary
    total_deductions = Column(Integer, default=0)
    total_gross_amount = Column(Numeric(15, 2), default=0.00)
    total_tds_amount = Column(Numeric(15, 2), default=0.00)
    
    # Status
    status = Column(Enum(TDSReturnStatus), default=TDSReturnStatus.DRAFT)
    
    # File reference
    return_file_path = Column(String(500), nullable=True)
    
    # Revision details
    original_return_id = Column(Integer, ForeignKey("tds_returns.id"), nullable=True)
    revision_number = Column(Integer, default=0)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    original_return = relationship("TDSReturn", remote_side=[id])
    
    __table_args__ = (
        Index("ix_tds_return_tenant_period", "tenant_id", "financial_year", "quarter"),
    )


# ============================================================================
# GST (Goods & Services Tax) Models
# ============================================================================

class GSTType(str, enum.Enum):
    """GST Type"""
    CGST = "cgst"  # Central GST
    SGST = "sgst"  # State GST
    IGST = "igst"  # Integrated GST
    CESS = "cess"  # Compensation Cess


class GSTTransactionType(str, enum.Enum):
    """GST Transaction Type"""
    SALE = "sale"
    PURCHASE = "purchase"
    EXPENSE = "expense"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"


class GSTReturnType(str, enum.Enum):
    """GST Return Types"""
    GSTR1 = "GSTR-1"  # Outward supplies
    GSTR3B = "GSTR-3B"  # Summary return
    GSTR9 = "GSTR-9"  # Annual return
    GSTR9C = "GSTR-9C"  # Audit report


class GSTReturnStatus(str, enum.Enum):
    """GST Return Status"""
    DRAFT = "draft"
    FILED = "filed"
    ACKNOWLEDGED = "acknowledged"
    REVISED = "revised"


class GSTConfiguration(Base):
    """GST Configuration - GSTIN details"""
    __tablename__ = "gst_configuration"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # GSTIN details
    gstin = Column(String(15), nullable=False, unique=True, index=True)
    legal_name = Column(String(200), nullable=False)
    trade_name = Column(String(200), nullable=True)
    
    # Address
    state_code = Column(String(2), nullable=False)  # First 2 digits of GSTIN
    state_name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    pincode = Column(String(6), nullable=False)
    
    # Registration details
    registration_date = Column(Date, nullable=False)
    registration_type = Column(String(50), nullable=False)  # regular, composite
    
    # GST type
    is_regular = Column(Boolean, default=True)
    is_composition = Column(Boolean, default=False)
    
    # Contact
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)


class HSNSACMaster(Base):
    """HSN/SAC Code Master"""
    __tablename__ = "hsn_sac_master"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Code details
    code = Column(String(10), nullable=False, index=True)
    code_type = Column(String(10), nullable=False)  # HSN or SAC
    description = Column(Text, nullable=False)
    
    # GST rates
    cgst_rate = Column(Numeric(5, 2), nullable=False)
    sgst_rate = Column(Numeric(5, 2), nullable=False)
    igst_rate = Column(Numeric(5, 2), nullable=False)
    cess_rate = Column(Numeric(5, 2), default=0.00)
    
    # Category
    category = Column(String(100), nullable=True)
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_hsn_sac_tenant_code", "tenant_id", "code", unique=True),
    )


class GSTTransaction(Base):
    """GST Transaction Records"""
    __tablename__ = "gst_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Transaction details
    transaction_number = Column(String(50), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(Enum(GSTTransactionType), nullable=False)
    
    # Reference
    reference_type = Column(String(50), nullable=False)  # invoice, payment, etc.
    reference_id = Column(Integer, nullable=False)
    invoice_number = Column(String(100), nullable=True)
    
    # Party details
    party_gstin = Column(String(15), nullable=True, index=True)
    party_name = Column(String(200), nullable=False)
    party_state = Column(String(100), nullable=True)
    
    # HSN/SAC
    hsn_sac_code = Column(String(10), nullable=True)
    
    # Amounts
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), default=0.00)
    cgst_amount = Column(Numeric(15, 2), default=0.00)
    sgst_rate = Column(Numeric(5, 2), default=0.00)
    sgst_amount = Column(Numeric(15, 2), default=0.00)
    igst_rate = Column(Numeric(5, 2), default=0.00)
    igst_amount = Column(Numeric(15, 2), default=0.00)
    cess_amount = Column(Numeric(15, 2), default=0.00)
    total_gst = Column(Numeric(15, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Reverse charge
    is_reverse_charge = Column(Boolean, default=False)
    
    # Place of supply
    place_of_supply = Column(String(100), nullable=True)
    is_inter_state = Column(Boolean, default=False)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    __table_args__ = (
        Index("ix_gst_trans_tenant_date", "tenant_id", "transaction_date"),
        Index("ix_gst_trans_reference", "reference_type", "reference_id"),
    )


class GSTInputCredit(Base):
    """GST Input Tax Credit Records"""
    __tablename__ = "gst_input_credit"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Invoice details
    supplier_gstin = Column(String(15), nullable=False, index=True)
    supplier_name = Column(String(200), nullable=False)
    invoice_number = Column(String(100), nullable=False)
    invoice_date = Column(Date, nullable=False, index=True)
    
    # Reference
    transaction_id = Column(Integer, ForeignKey("gst_transactions.id"), nullable=True)
    
    # Amounts
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    cgst_amount = Column(Numeric(15, 2), default=0.00)
    sgst_amount = Column(Numeric(15, 2), default=0.00)
    igst_amount = Column(Numeric(15, 2), default=0.00)
    cess_amount = Column(Numeric(15, 2), default=0.00)
    total_itc = Column(Numeric(15, 2), nullable=False)
    
    # ITC claimed
    itc_claimed = Column(Numeric(15, 2), default=0.00)
    itc_reversed = Column(Numeric(15, 2), default=0.00)
    itc_available = Column(Numeric(15, 2), nullable=False)
    
    # Period
    financial_year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    
    # GSTR-2A/2B reconciliation
    is_in_gstr2a = Column(Boolean, default=False)
    is_matched = Column(Boolean, default=False)
    mismatch_reason = Column(String(200), nullable=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_gst_itc_tenant_supplier", "tenant_id", "supplier_gstin"),
        Index("ix_gst_itc_period", "financial_year", "month"),
    )


class GSTReturn(Base):
    """GST Return Filing Records"""
    __tablename__ = "gst_returns"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Return details
    return_type = Column(Enum(GSTReturnType), nullable=False)
    return_period = Column(String(20), nullable=False)  # MMYYYY or YYYY
    financial_year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)  # For monthly returns
    
    # GSTIN
    gstin = Column(String(15), nullable=False)
    
    # Filing details
    filing_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=False)
    arn = Column(String(50), nullable=True)  # Application Reference Number
    
    # Summary amounts (outward)
    outward_taxable = Column(Numeric(15, 2), default=0.00)
    outward_cgst = Column(Numeric(15, 2), default=0.00)
    outward_sgst = Column(Numeric(15, 2), default=0.00)
    outward_igst = Column(Numeric(15, 2), default=0.00)
    
    # Summary amounts (inward/ITC)
    inward_taxable = Column(Numeric(15, 2), default=0.00)
    itc_cgst = Column(Numeric(15, 2), default=0.00)
    itc_sgst = Column(Numeric(15, 2), default=0.00)
    itc_igst = Column(Numeric(15, 2), default=0.00)
    
    # Net liability
    net_cgst = Column(Numeric(15, 2), default=0.00)
    net_sgst = Column(Numeric(15, 2), default=0.00)
    net_igst = Column(Numeric(15, 2), default=0.00)
    total_liability = Column(Numeric(15, 2), default=0.00)
    
    # Status
    status = Column(Enum(GSTReturnStatus), default=GSTReturnStatus.DRAFT)
    
    # File reference
    return_file_path = Column(String(500), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    __table_args__ = (
        Index("ix_gst_return_tenant_period", "tenant_id", "return_period", "return_type"),
    )



# ============================================================================
# Fixed Asset Management Models
# ============================================================================
# NOTE: FixedAsset models are now defined in asset_models.py
# This section is commented out to avoid duplicate table definition
# The comprehensive asset management models should be imported from:
# backend.shared.database.asset_models

# Keeping enums for backward compatibility


class AssetCategory(str, enum.Enum):
    """Asset Categories"""
    LAND = "land"
    BUILDING = "building"
    PLANT_MACHINERY = "plant_machinery"
    FURNITURE_FIXTURES = "furniture_fixtures"
    OFFICE_EQUIPMENT = "office_equipment"
    COMPUTERS = "computers"
    VEHICLES = "vehicles"
    SOFTWARE = "software"
    INTANGIBLE = "intangible"


class DepreciationMethod(str, enum.Enum):
    """Depreciation Methods"""
    STRAIGHT_LINE = "straight_line"  # SLM
    WRITTEN_DOWN_VALUE = "written_down_value"  # WDV
    DOUBLE_DECLINING = "double_declining"
    SUM_OF_YEARS_DIGITS = "sum_of_years_digits"
    UNITS_OF_PRODUCTION = "units_of_production"


class AssetStatus(str, enum.Enum):
    """Asset Status"""
    ACTIVE = "active"
    UNDER_MAINTENANCE = "under_maintenance"
    DISPOSED = "disposed"
    SCRAPPED = "scrapped"
    LOST = "lost"
    SOLD = "sold"


# DEPRECATED: These models have been moved to backend.shared.database.asset_models
# Commenting out to avoid duplicate table definitions
# Import from asset_models instead:
# from backend.shared.database.asset_models import FixedAsset, AssetDepreciationSchedule, AssetTransfer, AssetMaintenance

# class FixedAsset(Base):
#     """Fixed Asset Register"""
#     __tablename__ = "fixed_assets"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, nullable=False, index=True)
#     
#     # Asset identification
#     asset_code = Column(String(50), nullable=False, unique=True, index=True)
#     asset_name = Column(String(200), nullable=False)
#     description = Column(Text, nullable=True)
#     
#     # Category
#     category = Column(Enum(AssetCategory), nullable=False, index=True)
#     sub_category = Column(String(100), nullable=True)
#     
#     # Purchase details
#     purchase_date = Column(Date, nullable=False, index=True)
#     purchase_cost = Column(Numeric(15, 2), nullable=False)
#     vendor_name = Column(String(200), nullable=True)
#     invoice_number = Column(String(100), nullable=True)
#     invoice_date = Column(Date, nullable=True)
#     
#     # Location and allocation
#     location = Column(String(200), nullable=True)
#     department = Column(String(100), nullable=True)
#     custodian = Column(String(200), nullable=True)
#     
#     # Depreciation configuration
#     depreciation_method = Column(Enum(DepreciationMethod), nullable=False)
#     depreciation_rate = Column(Numeric(5, 2), nullable=False)  # Annual rate %
#     useful_life_years = Column(Integer, nullable=False)
#     useful_life_months = Column(Integer, default=0)
#     salvage_value = Column(Numeric(15, 2), default=0.00)
#     
#     # Current values
#     accumulated_depreciation = Column(Numeric(15, 2), default=0.00)
#     written_down_value = Column(Numeric(15, 2), nullable=False)
#     last_depreciation_date = Column(Date, nullable=True)
#     
#     # Status
#     status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE, index=True)
#     
#     # Warranty
#     warranty_expiry_date = Column(Date, nullable=True)
#     
#     # Insurance
#     is_insured = Column(Boolean, default=False)
#     insurance_policy_number = Column(String(100), nullable=True)
#     insurance_expiry_date = Column(Date, nullable=True)
#     
#     # Disposal details
#     disposal_date = Column(Date, nullable=True)
#     disposal_amount = Column(Numeric(15, 2), nullable=True)
#     gain_loss_on_disposal = Column(Numeric(15, 2), nullable=True)
#     
#     # Notes
#     notes = Column(Text, nullable=True)
#     
#     # Audit
#     is_deleted = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     created_by = Column(Integer, nullable=False)
#     
#     # Relationships
#     depreciation_schedule = relationship("AssetDepreciationSchedule", back_populates="asset")
#     transfers = relationship("AssetTransfer", back_populates="asset")
#     maintenance_records = relationship("AssetMaintenance", back_populates="asset")
#     
#     __table_args__ = (
#         Index("ix_asset_tenant_category", "tenant_id", "category"),
#         Index("ix_asset_status", "status"),
#     )


# class AssetDepreciationSchedule(Base):
#     """Asset Depreciation Schedule"""
#     __tablename__ = "asset_depreciation_schedule"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, nullable=False, index=True)
#     
#     # Asset reference
#     asset_id = Column(Integer, ForeignKey("fixed_assets.id"), nullable=False, index=True)
#     
#     # Period
#     depreciation_date = Column(Date, nullable=False, index=True)
#     financial_year = Column(Integer, nullable=False)
#     month = Column(Integer, nullable=False)
#     
#     # Amounts
#     opening_wdv = Column(Numeric(15, 2), nullable=False)
#     depreciation_amount = Column(Numeric(15, 2), nullable=False)
#     accumulated_depreciation = Column(Numeric(15, 2), nullable=False)
#     closing_wdv = Column(Numeric(15, 2), nullable=False)
#     
#     # Posting reference
#     journal_entry_id = Column(Integer, nullable=True)
#     is_posted = Column(Boolean, default=False)
#     
#     # Audit
#     created_at = Column(DateTime, default=datetime.utcnow)
#     created_by = Column(Integer, nullable=False)
#     
#     # Relationships
#     asset = relationship("FixedAsset", back_populates="depreciation_schedule")
#     
#     __table_args__ = (
#         Index("ix_asset_dep_tenant_date", "tenant_id", "depreciation_date"),
#         Index("ix_asset_dep_asset_date", "asset_id", "depreciation_date", unique=True),
#     )


# class AssetTransfer(Base):
#     """Asset Transfer Records"""
#     __tablename__ = "asset_transfers"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, nullable=False, index=True)
#     
#     # Asset reference
#     asset_id = Column(Integer, ForeignKey("fixed_assets.id"), nullable=False, index=True)
#     
#     # Transfer details
#     transfer_number = Column(String(50), nullable=False, unique=True)
#     transfer_date = Column(Date, nullable=False, index=True)
#     
#     # From
#     from_location = Column(String(200), nullable=True)
#     from_department = Column(String(100), nullable=True)
#     from_custodian = Column(String(200), nullable=True)
#     
#     # To
#     to_location = Column(String(200), nullable=True)
#     to_department = Column(String(100), nullable=True)
#     to_custodian = Column(String(200), nullable=True)
#     
#     # Reason
#     transfer_reason = Column(Text, nullable=True)
#     
#     # Approval
#     approved_by = Column(Integer, nullable=True)
#     approved_at = Column(DateTime, nullable=True)
#     
#     # Audit
#     created_at = Column(DateTime, default=datetime.utcnow)
#     created_by = Column(Integer, nullable=False)
#     
#     # Relationships
#     asset = relationship("FixedAsset", back_populates="transfers")
#     
#     __table_args__ = (
#         Index("ix_asset_transfer_asset_date", "asset_id", "transfer_date"),
#     )


# class AssetMaintenance(Base):
#     """Asset Maintenance Records"""
#     __tablename__ = "asset_maintenance"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, nullable=False, index=True)
#     
#     # Asset reference
#     asset_id = Column(Integer, ForeignKey("fixed_assets.id"), nullable=False, index=True)
#     
#     # Maintenance details
#     maintenance_date = Column(Date, nullable=False, index=True)
#     maintenance_type = Column(String(50), nullable=False)  # routine, breakdown, preventive
#     description = Column(Text, nullable=False)
#     
#     # Service provider
#     vendor_name = Column(String(200), nullable=True)
#     vendor_contact = Column(String(100), nullable=True)
#     
#     # Cost
#     maintenance_cost = Column(Numeric(15, 2), nullable=False)
#     
#     # Status
#     is_completed = Column(Boolean, default=True)
#     completion_date = Column(Date, nullable=True)
#     
#     # Next maintenance
#     next_maintenance_date = Column(Date, nullable=True)
#     
#     # Remarks
#     remarks = Column(Text, nullable=True)
#     
#     # Audit
#     created_at = Column(DateTime, default=datetime.utcnow)
#     created_by = Column(Integer, nullable=False)
#     
#     # Relationships
#     asset = relationship("FixedAsset", back_populates="maintenance_records")
#     
#     __table_args__ = (
#         Index("ix_asset_maint_asset_date", "asset_id", "maintenance_date"),
#     )



# ============================================================================
# Accounts Payable Models
# ============================================================================

class VendorType(str, enum.Enum):
    """Vendor Type"""
    SUPPLIER = "supplier"
    CONTRACTOR = "contractor"
    SERVICE_PROVIDER = "service_provider"
    CONSULTANT = "consultant"
    UTILITY = "utility"
    OTHER = "other"


class PaymentTerms(str, enum.Enum):
    """Payment Terms"""
    IMMEDIATE = "immediate"
    NET_7 = "net_7"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    NET_90 = "net_90"


class InvoiceStatus(str, enum.Enum):
    """Invoice Status"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment Status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Vendor(Base):
    """Vendor Master"""
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Vendor identification
    vendor_code = Column(String(50), nullable=False, unique=True, index=True)
    vendor_name = Column(String(200), nullable=False)
    vendor_type = Column(Enum(VendorType), nullable=False)
    
    # Contact details
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Tax details
    pan = Column(String(10), nullable=True, index=True)
    gstin = Column(String(15), nullable=True, index=True)
    tan = Column(String(10), nullable=True)
    
    # Bank details
    bank_name = Column(String(200), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_ifsc = Column(String(11), nullable=True)
    bank_branch = Column(String(200), nullable=True)
    
    # Payment terms
    payment_terms = Column(Enum(PaymentTerms), default=PaymentTerms.NET_30)
    credit_days = Column(Integer, default=30)
    credit_limit = Column(Numeric(15, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_msme = Column(Boolean, default=False)
    
    # Rating
    vendor_rating = Column(Integer, nullable=True)  # 1-5
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    invoices = relationship("PurchaseInvoice", back_populates="vendor")
    payments = relationship("VendorPayment", back_populates="vendor")
    
    __table_args__ = (
        Index("ix_vendor_tenant_name", "tenant_id", "vendor_name"),
    )


class PurchaseInvoice(Base):
    """Purchase Invoice / Bill"""
    __tablename__ = "purchase_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Invoice details
    invoice_number = Column(String(100), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    
    # Vendor reference
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    vendor_code = Column(String(50), nullable=False)
    vendor_name = Column(String(200), nullable=False)
    
    # Purchase order reference
    po_number = Column(String(100), nullable=True)
    po_date = Column(Date, nullable=True)
    
    # Amounts
    gross_amount = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    
    # GST
    cgst_amount = Column(Numeric(15, 2), default=0.00)
    sgst_amount = Column(Numeric(15, 2), default=0.00)
    igst_amount = Column(Numeric(15, 2), default=0.00)
    gst_total = Column(Numeric(15, 2), default=0.00)
    
    # TDS
    tds_section = Column(String(10), nullable=True)
    tds_rate = Column(Numeric(5, 2), default=0.00)
    tds_amount = Column(Numeric(15, 2), default=0.00)
    
    # Total
    total_amount = Column(Numeric(15, 2), nullable=False)
    net_payable = Column(Numeric(15, 2), nullable=False)  # After TDS deduction
    
    # Payment tracking
    paid_amount = Column(Numeric(15, 2), default=0.00)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING, index=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Approval
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Accounting
    journal_entry_id = Column(Integer, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    payments = relationship("VendorPayment", secondary="vendor_payment_allocations")
    
    __table_args__ = (
        Index("ix_pi_tenant_vendor", "tenant_id", "vendor_id"),
        Index("ix_pi_status_due", "status", "due_date"),
    )


class VendorPayment(Base):
    """Vendor Payments"""
    __tablename__ = "vendor_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Payment details
    payment_number = Column(String(50), nullable=False, unique=True, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    
    # Vendor reference
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    vendor_code = Column(String(50), nullable=False)
    vendor_name = Column(String(200), nullable=False)
    
    # Amount
    payment_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment method
    payment_mode = Column(String(50), nullable=False)  # cash, cheque, neft, rtgs, imps, upi
    cheque_number = Column(String(50), nullable=True)
    cheque_date = Column(Date, nullable=True)
    transaction_reference = Column(String(100), nullable=True)
    
    # Bank details
    bank_name = Column(String(200), nullable=True)
    bank_account = Column(String(50), nullable=True)
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.COMPLETED, index=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Accounting
    journal_entry_id = Column(Integer, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    allocations = relationship("VendorPaymentAllocation", back_populates="payment")
    
    __table_args__ = (
        Index("ix_vp_tenant_vendor", "tenant_id", "vendor_id"),
        Index("ix_vp_date_status", "payment_date", "status"),
    )


class VendorPaymentAllocation(Base):
    """Payment Allocation to Invoices"""
    __tablename__ = "vendor_payment_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Payment reference
    payment_id = Column(Integer, ForeignKey("vendor_payments.id"), nullable=False, index=True)
    
    # Invoice reference
    invoice_id = Column(Integer, ForeignKey("purchase_invoices.id"), nullable=False, index=True)
    
    # Allocation amount
    allocated_amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    payment = relationship("VendorPayment", back_populates="allocations")
    invoice = relationship("PurchaseInvoice")
    
    __table_args__ = (
        Index("ix_vpa_payment_invoice", "payment_id", "invoice_id"),
    )


# ============================================================================
# Accounts Receivable Models
# ============================================================================

class CustomerType(str, enum.Enum):
    """Customer Type"""
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    OTHER = "other"


class ReceiptStatus(str, enum.Enum):
    """Receipt Status"""
    PENDING = "pending"
    CLEARED = "cleared"
    BOUNCED = "bounced"
    CANCELLED = "cancelled"


class CustomerMaster(Base):
    """Customer Master (Non-Loan Customers)"""
    __tablename__ = "customer_master"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Customer identification
    customer_code = Column(String(50), nullable=False, unique=True, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_type = Column(Enum(CustomerType), nullable=False)
    
    # Contact details
    contact_person = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Tax details
    pan = Column(String(10), nullable=True, index=True)
    gstin = Column(String(15), nullable=True, index=True)
    
    # Credit terms
    payment_terms = Column(Enum(PaymentTerms), default=PaymentTerms.NET_30)
    credit_limit = Column(Numeric(15, 2), nullable=True)
    credit_days = Column(Integer, default=30)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    invoices = relationship("SalesInvoice", back_populates="customer")
    receipts = relationship("CustomerReceipt", back_populates="customer")
    
    __table_args__ = (
        Index("ix_customer_tenant_name", "tenant_id", "customer_name"),
    )


class SalesInvoice(Base):
    """Sales Invoice"""
    __tablename__ = "sales_invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Invoice details
    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    
    # Customer reference
    customer_id = Column(Integer, ForeignKey("customer_master.id"), nullable=False, index=True)
    customer_code = Column(String(50), nullable=False)
    customer_name = Column(String(200), nullable=False)
    
    # Amounts
    gross_amount = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), default=0.00)
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    
    # GST
    cgst_amount = Column(Numeric(15, 2), default=0.00)
    sgst_amount = Column(Numeric(15, 2), default=0.00)
    igst_amount = Column(Numeric(15, 2), default=0.00)
    gst_total = Column(Numeric(15, 2), default=0.00)
    
    # TDS (if applicable)
    tds_amount = Column(Numeric(15, 2), default=0.00)
    
    # Total
    total_amount = Column(Numeric(15, 2), nullable=False)
    net_receivable = Column(Numeric(15, 2), nullable=False)
    
    # Receipt tracking
    received_amount = Column(Numeric(15, 2), default=0.00)
    balance_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING, index=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Accounting
    journal_entry_id = Column(Integer, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    customer = relationship("CustomerMaster", back_populates="invoices")
    receipts = relationship("CustomerReceipt", secondary="customer_receipt_allocations")
    
    __table_args__ = (
        Index("ix_si_tenant_customer", "tenant_id", "customer_id"),
        Index("ix_si_status_due", "status", "due_date"),
    )


class CustomerReceipt(Base):
    """Customer Receipts"""
    __tablename__ = "customer_receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Receipt details
    receipt_number = Column(String(50), nullable=False, unique=True, index=True)
    receipt_date = Column(Date, nullable=False, index=True)
    
    # Customer reference
    customer_id = Column(Integer, ForeignKey("customer_master.id"), nullable=False, index=True)
    customer_code = Column(String(50), nullable=False)
    customer_name = Column(String(200), nullable=False)
    
    # Amount
    receipt_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment method
    payment_mode = Column(String(50), nullable=False)  # cash, cheque, neft, rtgs, imps, upi
    cheque_number = Column(String(50), nullable=True)
    cheque_date = Column(Date, nullable=True)
    transaction_reference = Column(String(100), nullable=True)
    
    # Bank details
    bank_name = Column(String(200), nullable=True)
    bank_account = Column(String(50), nullable=True)
    
    # Status
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.CLEARED, index=True)
    clearance_date = Column(Date, nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Accounting
    journal_entry_id = Column(Integer, nullable=True)
    
    # Audit
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    customer = relationship("CustomerMaster", back_populates="receipts")
    allocations = relationship("CustomerReceiptAllocation", back_populates="receipt")
    
    __table_args__ = (
        Index("ix_cr_tenant_customer", "tenant_id", "customer_id"),
        Index("ix_cr_date_status", "receipt_date", "status"),
    )


class CustomerReceiptAllocation(Base):
    """Receipt Allocation to Invoices"""
    __tablename__ = "customer_receipt_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Receipt reference
    receipt_id = Column(Integer, ForeignKey("customer_receipts.id"), nullable=False, index=True)
    
    # Invoice reference
    invoice_id = Column(Integer, ForeignKey("sales_invoices.id"), nullable=False, index=True)
    
    # Allocation amount
    allocated_amount = Column(Numeric(15, 2), nullable=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    receipt = relationship("CustomerReceipt", back_populates="allocations")
    invoice = relationship("SalesInvoice")
    
    __table_args__ = (
        Index("ix_cra_receipt_invoice", "receipt_id", "invoice_id"),
    )
