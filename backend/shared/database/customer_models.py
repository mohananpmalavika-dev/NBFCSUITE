"""
Customer Management Database Models
Comprehensive customer, KYC, documents, family, and bank account models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Numeric, Text,
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
import enum

from .base import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class CustomerType(str, enum.Enum):
    INDIVIDUAL = "individual"
    PROPRIETORSHIP = "proprietorship"
    PARTNERSHIP = "partnership"
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    TRUST = "trust"
    SOCIETY = "society"
    HUF = "huf"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MaritalStatus(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AccountType(str, enum.Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    OVERDRAFT = "overdraft"
    CASH_CREDIT = "cash_credit"


class RiskRating(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ============================================================================
# CUSTOMER MODEL
# ============================================================================

class Customer(BaseModel):
    """Main customer/borrower entity"""
    __tablename__ = "customers"

    # Basic Information
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    customer_type = Column(SQLEnum(CustomerType), nullable=False, default=CustomerType.INDIVIDUAL)
    
    # Personal Information (for individuals)
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(300), index=True)  # Computed/stored full name
    
    # Business Information (for entities)
    business_name = Column(String(300))
    business_pan = Column(String(10))
    business_registration_number = Column(String(100))
    
    # Contact Information
    email = Column(String(255), index=True)
    mobile = Column(String(20), nullable=False, index=True)
    alternate_mobile = Column(String(20))
    landline = Column(String(20))
    
    # Identity Information
    pan_number = Column(String(10), unique=True, index=True)
    aadhaar_number = Column(String(12), unique=True, index=True)  # Encrypted in production
    voter_id = Column(String(20))
    passport_number = Column(String(20))
    driving_license = Column(String(20))

    
    # Personal Details
    date_of_birth = Column(Date)
    age = Column(Integer)
    gender = Column(SQLEnum(Gender))
    marital_status = Column(SQLEnum(MaritalStatus))
    father_name = Column(String(200))
    mother_name = Column(String(200))
    spouse_name = Column(String(200))
    
    # Occupation & Income
    occupation_id = Column(Integer, ForeignKey("occupations.id"))
    industry_id = Column(Integer, ForeignKey("industries.id"))
    employer_name = Column(String(300))
    employment_type = Column(String(50))  # Permanent, Contract, Self-Employed
    years_in_business = Column(Integer)
    monthly_income = Column(Numeric(15, 2))
    annual_income = Column(Numeric(15, 2))
    income_proof_type = Column(String(100))
    
    # Address Information
    current_address_line1 = Column(String(500))
    current_address_line2 = Column(String(500))
    current_city_id = Column(Integer, ForeignKey("cities.id"))
    current_state_id = Column(Integer, ForeignKey("states.id"))
    current_pincode = Column(String(6))
    current_address_type = Column(String(50))  # Owned, Rented, Company Provided
    years_at_current_address = Column(Integer)
    
    permanent_address_line1 = Column(String(500))
    permanent_address_line2 = Column(String(500))
    permanent_city_id = Column(Integer, ForeignKey("cities.id"))
    permanent_state_id = Column(Integer, ForeignKey("states.id"))
    permanent_pincode = Column(String(6))
    is_permanent_same_as_current = Column(Boolean, default=False)
    
    # KYC & Verification
    kyc_status = Column(SQLEnum(KYCStatus), default=KYCStatus.PENDING)
    kyc_completed_date = Column(DateTime)
    kyc_verified_by = Column(Integer, ForeignKey("users.id"))
    kyc_remarks = Column(Text)
    is_kyc_verified = Column(Boolean, default=False)
    
    # Risk & Compliance
    risk_rating = Column(SQLEnum(RiskRating), default=RiskRating.MEDIUM)
    risk_score = Column(Integer)  # 0-100
    cibil_score = Column(Integer)  # 300-900
    cibil_last_checked = Column(DateTime)
    is_politically_exposed = Column(Boolean, default=False)
    aml_check_status = Column(String(50))
    aml_last_checked = Column(DateTime)
    
    # Banking Preferences
    preferred_bank_id = Column(Integer, ForeignKey("banks.id"))
    preferred_branch_id = Column(Integer, ForeignKey("bank_branches.id"))
    
    # Status & Flags
    is_active = Column(Boolean, default=True)
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(Text)
    blacklist_date = Column(DateTime)
    
    # Additional Information
    profile_photo_url = Column(String(500))
    signature_url = Column(String(500))
    remarks = Column(Text)
    tags = Column(JSON)  # ["vip", "regular-payer", etc.]
    custom_fields = Column(JSON)  # Flexible additional fields
    
    # Relationships
    occupation = relationship("Occupation", foreign_keys=[occupation_id])
    industry = relationship("Industry", foreign_keys=[industry_id])
    current_city = relationship("City", foreign_keys=[current_city_id])
    current_state = relationship("State", foreign_keys=[current_state_id])
    permanent_city = relationship("City", foreign_keys=[permanent_city_id])
    permanent_state = relationship("State", foreign_keys=[permanent_state_id])
    
    # Child relationships
    documents = relationship("CustomerDocument", back_populates="customer", cascade="all, delete-orphan")
    family_members = relationship("CustomerFamily", back_populates="customer", cascade="all, delete-orphan")
    bank_accounts = relationship("CustomerBankAccount", back_populates="customer", cascade="all, delete-orphan")
    references = relationship("CustomerReference", back_populates="customer", cascade="all, delete-orphan")
    kyc_details = relationship("CustomerKYC", back_populates="customer", cascade="all, delete-orphan")
    
    # Loan relationships
    loan_applications = relationship("LoanApplication", back_populates="customer")
    loan_accounts = relationship("LoanAccount", back_populates="customer")
    
    # Indexes
    __table_args__ = (
        Index('idx_customer_tenant_code', 'tenant_id', 'customer_code'),
        Index('idx_customer_tenant_mobile', 'tenant_id', 'mobile'),
        Index('idx_customer_tenant_pan', 'tenant_id', 'pan_number'),
        Index('idx_customer_kyc_status', 'tenant_id', 'kyc_status'),
        Index('idx_customer_risk_rating', 'tenant_id', 'risk_rating'),
    )


# ============================================================================
# KYC DETAILS MODEL
# ============================================================================

class CustomerKYC(BaseModel):
    """Detailed KYC information and verification history"""
    __tablename__ = "customer_kyc"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Aadhaar Verification
    aadhaar_verified = Column(Boolean, default=False)
    aadhaar_verified_date = Column(DateTime)
    aadhaar_verification_method = Column(String(50))  # eKYC, Physical
    aadhaar_name = Column(String(300))
    aadhaar_address = Column(Text)
    
    # PAN Verification
    pan_verified = Column(Boolean, default=False)
    pan_verified_date = Column(DateTime)
    pan_name = Column(String(300))
    pan_dob = Column(Date)
    
    # Bank Account Verification
    bank_account_verified = Column(Boolean, default=False)
    bank_verification_date = Column(DateTime)
    bank_verification_method = Column(String(50))  # Penny Drop, Statement
    
    # Video KYC
    video_kyc_done = Column(Boolean, default=False)
    video_kyc_date = Column(DateTime)
    video_kyc_recording_url = Column(String(500))
    video_kyc_agent_id = Column(Integer, ForeignKey("users.id"))
    
    # Biometric
    biometric_captured = Column(Boolean, default=False)
    biometric_capture_date = Column(DateTime)
    fingerprint_data = Column(Text)  # Encrypted
    
    # In-Person Verification
    in_person_verification_done = Column(Boolean, default=False)
    in_person_verification_date = Column(DateTime)
    verified_by_agent_id = Column(Integer, ForeignKey("users.id"))
    verification_location = Column(String(500))
    
    # CIBIL/Credit Bureau
    cibil_report_url = Column(String(500))
    cibil_fetched_date = Column(DateTime)
    cibil_consent_given = Column(Boolean, default=False)
    cibil_consent_date = Column(DateTime)
    
    # Overall Status
    overall_kyc_status = Column(SQLEnum(KYCStatus), default=KYCStatus.PENDING)
    kyc_completion_percentage = Column(Integer, default=0)  # 0-100
    kyc_remarks = Column(Text)
    
    # Relationship
    customer = relationship("Customer", back_populates="kyc_details")


# ============================================================================
# CUSTOMER DOCUMENTS MODEL
# ============================================================================

class CustomerDocument(BaseModel):
    """Customer documents (Aadhaar, PAN, Bank statements, etc.)"""
    __tablename__ = "customer_documents"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    
    # Document Details
    document_number = Column(String(100))
    document_name = Column(String(300))
    document_url = Column(String(500), nullable=False)
    document_size_kb = Column(Integer)
    document_format = Column(String(10))  # PDF, JPG, PNG
    
    # Verification
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_date = Column(DateTime)
    verification_remarks = Column(Text)
    
    # Expiry
    issue_date = Column(Date)
    expiry_date = Column(Date)
    is_expired = Column(Boolean, default=False)
    
    # OCR/Extracted Data
    ocr_data = Column(JSON)  # Extracted text/data from document
    extracted_name = Column(String(300))
    extracted_dob = Column(Date)
    extracted_address = Column(Text)
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_date = Column(DateTime, default=datetime.utcnow)
    file_hash = Column(String(64))  # For duplicate detection
    
    # Relationships
    customer = relationship("Customer", back_populates="documents")
    document_type = relationship("DocumentType")
    
    __table_args__ = (
        Index('idx_doc_customer_type', 'customer_id', 'document_type_id'),
        Index('idx_doc_status', 'tenant_id', 'status'),
    )



# ============================================================================
# CUSTOMER FAMILY MODEL
# ============================================================================

class CustomerFamily(BaseModel):
    """Customer family members and dependents"""
    __tablename__ = "customer_family"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    relationship_type_id = Column(Integer, ForeignKey("relationship_types.id"))
    
    # Member Details
    name = Column(String(300), nullable=False)
    date_of_birth = Column(Date)
    age = Column(Integer)
    gender = Column(SQLEnum(Gender))
    
    # Contact
    mobile = Column(String(20))
    email = Column(String(255))
    
    # Identity
    aadhaar_number = Column(String(12))
    pan_number = Column(String(10))
    
    # Occupation & Income
    occupation = Column(String(200))
    monthly_income = Column(Numeric(15, 2))
    is_dependent = Column(Boolean, default=True)
    is_co_applicant = Column(Boolean, default=False)
    is_guarantor = Column(Boolean, default=False)
    
    # Emergency Contact
    is_emergency_contact = Column(Boolean, default=False)
    emergency_contact_priority = Column(Integer)  # 1, 2, 3
    
    # Nominee
    is_nominee = Column(Boolean, default=False)
    nominee_percentage = Column(Numeric(5, 2))  # 0-100
    
    # Additional
    remarks = Column(Text)
    photo_url = Column(String(500))
    
    # Relationships
    customer = relationship("Customer", back_populates="family_members")
    relationship_type = relationship("RelationshipType")


# ============================================================================
# CUSTOMER BANK ACCOUNTS MODEL
# ============================================================================

class CustomerBankAccount(BaseModel):
    """Customer bank accounts for disbursement and collections"""
    __tablename__ = "customer_bank_accounts"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    bank_id = Column(Integer, ForeignKey("banks.id"))
    bank_branch_id = Column(Integer, ForeignKey("bank_branches.id"))
    
    # Account Details
    account_number = Column(String(50), nullable=False)
    account_holder_name = Column(String(300), nullable=False)
    account_type = Column(SQLEnum(AccountType), default=AccountType.SAVINGS)
    ifsc_code = Column(String(11), nullable=False)
    micr_code = Column(String(9))
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50))  # Penny Drop, Statement, Passbook
    verified_date = Column(DateTime)
    verification_remarks = Column(Text)
    
    # Penny Drop Details
    penny_drop_amount = Column(Numeric(10, 2))
    penny_drop_reference = Column(String(100))
    penny_drop_status = Column(String(50))
    
    # Usage
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    use_for_disbursement = Column(Boolean, default=True)
    use_for_collection = Column(Boolean, default=True)
    
    # Additional
    branch_name = Column(String(300))
    branch_address = Column(Text)
    account_opening_date = Column(Date)
    remarks = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="bank_accounts")
    bank = relationship("Bank")
    bank_branch = relationship("BankBranch")
    
    __table_args__ = (
        Index('idx_bank_account_customer', 'customer_id', 'is_primary'),
        Index('idx_bank_account_ifsc', 'ifsc_code'),
    )


# ============================================================================
# CUSTOMER REFERENCES MODEL
# ============================================================================

class CustomerReference(BaseModel):
    """Customer references and guarantors"""
    __tablename__ = "customer_references"
    
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    relationship_type_id = Column(Integer, ForeignKey("relationship_types.id"))
    
    # Reference Details
    name = Column(String(300), nullable=False)
    mobile = Column(String(20), nullable=False)
    alternate_mobile = Column(String(20))
    email = Column(String(255))
    
    # Address
    address_line1 = Column(String(500))
    address_line2 = Column(String(500))
    city_id = Column(Integer, ForeignKey("cities.id"))
    state_id = Column(Integer, ForeignKey("states.id"))
    pincode = Column(String(6))
    
    # Occupation
    occupation = Column(String(200))
    employer_name = Column(String(300))
    
    # Reference Type
    is_guarantor = Column(Boolean, default=False)
    is_family_member = Column(Boolean, default=False)
    reference_priority = Column(Integer)  # 1, 2, 3
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_date = Column(DateTime)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verification_method = Column(String(50))  # Phone, In-Person, Document
    verification_remarks = Column(Text)
    
    # Additional
    remarks = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="references")
    relationship_type = relationship("RelationshipType")
    city = relationship("City")
    state = relationship("State")
