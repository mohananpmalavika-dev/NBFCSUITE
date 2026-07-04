"""
Master Data Models
Reference data used across the platform
"""

from sqlalchemy import Column, String, Boolean, Integer, Float, Date, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from shared.database.models import BaseModel


# ============================================
# GEOGRAPHY MASTER DATA
# ============================================

class Country(BaseModel):
    """Country master data"""
    __tablename__ = "countries"
    
    code = Column(String(3), nullable=False)  # ISO 3166-1 alpha-3
    name = Column(String(200), nullable=False)
    phone_code = Column(String(10), nullable=True)
    currency_code = Column(String(3), nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_country_code', 'tenant_id', 'code', unique=True),
    )


class State(BaseModel):
    """State/Province master data"""
    __tablename__ = "states"
    
    country_code = Column(String(3), nullable=False)
    code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_state_code', 'tenant_id', 'code', unique=True),
    )


class City(BaseModel):
    """City master data"""
    __tablename__ = "cities"
    
    state_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_state_city', 'tenant_id', 'state_code', 'name'),
    )


class Pincode(BaseModel):
    """Pincode/ZIP code master data"""
    __tablename__ = "pincodes"
    
    pincode = Column(String(10), nullable=False)
    city = Column(String(200), nullable=False)
    state_code = Column(String(10), nullable=False)
    district = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_pincode', 'tenant_id', 'pincode'),
    )


# ============================================
# BANKING MASTER DATA
# ============================================

class Bank(BaseModel):
    """Bank master data"""
    __tablename__ = "banks"
    
    code = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    short_name = Column(String(100), nullable=True)
    bank_type = Column(String(50), nullable=True)  # Public, Private, Foreign
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_bank_code', 'tenant_id', 'code', unique=True),
    )


class BankBranch(BaseModel):
    """Bank branch master data"""
    __tablename__ = "bank_branches"
    
    bank_code = Column(String(20), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    micr_code = Column(String(20), nullable=True)
    branch_name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    city = Column(String(200), nullable=True)
    state_code = Column(String(10), nullable=True)
    pincode = Column(String(10), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_ifsc', 'tenant_id', 'ifsc_code', unique=True),
    )


# ============================================
# FINANCIAL MASTER DATA
# ============================================

class Currency(BaseModel):
    """Currency master data"""
    __tablename__ = "currencies"
    
    code = Column(String(3), nullable=False)  # ISO 4217
    name = Column(String(100), nullable=False)
    symbol = Column(String(10), nullable=True)
    decimal_places = Column(Integer, default=2)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_currency_code', 'tenant_id', 'code', unique=True),
    )


class InterestRateType(BaseModel):
    """Interest rate type master data"""
    __tablename__ = "interest_rate_types"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    calculation_method = Column(String(50), nullable=True)  # Simple, Compound, Flat
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_rate_type', 'tenant_id', 'code', unique=True),
    )


class LoanProductType(BaseModel):
    """Loan product type master data"""
    __tablename__ = "loan_product_types"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)  # Personal, Business, Gold, Vehicle, etc.
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_product_type', 'tenant_id', 'code', unique=True),
    )


# ============================================
# CONFIGURATION MASTER DATA
# ============================================

class DocumentType(BaseModel):
    """Document type master data"""
    __tablename__ = "document_types"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)  # Identity, Address, Income, etc.
    is_mandatory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_doc_type', 'tenant_id', 'code', unique=True),
    )


class Occupation(BaseModel):
    """Occupation master data"""
    __tablename__ = "occupations"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)  # Salaried, Self-Employed, Professional, etc.
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_occupation', 'tenant_id', 'code', unique=True),
    )


class Industry(BaseModel):
    """Industry master data"""
    __tablename__ = "industries"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_industry', 'tenant_id', 'code', unique=True),
    )


class LoanPurpose(BaseModel):
    """Loan purpose master data"""
    __tablename__ = "loan_purposes"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_purpose', 'tenant_id', 'code', unique=True),
    )


class RelationshipType(BaseModel):
    """Relationship type master data (for nominees, co-applicants)"""
    __tablename__ = "relationship_types"
    
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_relation', 'tenant_id', 'code', unique=True),
    )


class Holiday(BaseModel):
    """Holiday calendar"""
    __tablename__ = "holidays"
    
    date = Column(Date, nullable=False)
    name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=True)  # National, Regional, Bank
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_holiday_date', 'tenant_id', 'date'),
    )


class FinancialYear(BaseModel):
    """Financial year master data"""
    __tablename__ = "financial_years"
    
    code = Column(String(20), nullable=False)  # e.g., FY2024
    name = Column(String(100), nullable=False)  # e.g., "2024-2025"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_tenant_fy_code', 'tenant_id', 'code', unique=True),
    )
