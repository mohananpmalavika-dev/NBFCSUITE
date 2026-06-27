from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

# Prospect models live in models_prospect.py (loaded by init_db via imports in routers)



class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    dob = Column(String)
    gender = Column(String)
    kyc_status = Column(String, default="pending")
    pan = Column(String, unique=True, nullable=True)
    aadhar = Column(String, unique=True, nullable=True)
    passport = Column(String, unique=True, nullable=True)
    voter_id = Column(String, unique=True, nullable=True)
    driving_licence = Column(String, unique=True, nullable=True)
    gstin = Column(String, unique=True, nullable=True)
    cin = Column(String, unique=True, nullable=True)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=True)
    customer_type = Column(String, default="individual")
    lifecycle_status = Column(String, default="active")
    source_prospect_id = Column(String, nullable=True)
    onboarding_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("BranchOffice", back_populates="customers")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    address_type = Column(String)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    is_primary = Column(String, default=False)


class KYCDocument(Base):
    __tablename__ = "kyc_documents"

    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    document_type = Column(String)
    document_number = Column(String)
    document_url = Column(String)
    verification_status = Column(String, default="pending")
    expiry_date = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class CustomerFinancialProfile(Base):
    __tablename__ = "customer_financial_profiles"

    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"), unique=True)
    annual_income = Column(String)
    employment_type = Column(String)
    employer = Column(String)
    occupation = Column(String)
    assets = Column(JSON, nullable=True)
    liabilities = Column(JSON, nullable=True)
    credit_score = Column(Integer, nullable=True)
    behavior_score = Column(String, nullable=True)
    risk_level = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)


class HeadOffice(Base):
    __tablename__ = "head_offices"

    id = Column(String, primary_key=True)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)

    zonal_offices = relationship("ZonalOffice", back_populates="head_office")

    @property
    def zones(self):
        return self.zonal_offices


class ZonalOffice(Base):
    __tablename__ = "zonal_offices"

    id = Column(String, primary_key=True)
    head_office_id = Column(String, ForeignKey("head_offices.id"), nullable=False)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)

    head_office = relationship("HeadOffice", back_populates="zonal_offices")
    regional_offices = relationship("RegionalOffice", back_populates="zonal_office")

    @property
    def organization_id(self):
        return self.head_office_id

    @property
    def regions(self):
        return self.regional_offices


class RegionalOffice(Base):
    __tablename__ = "regional_offices"

    id = Column(String, primary_key=True)
    zonal_office_id = Column(String, ForeignKey("zonal_offices.id"), nullable=False)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)

    zonal_office = relationship("ZonalOffice", back_populates="regional_offices")
    area_offices = relationship("AreaOffice", back_populates="regional_office")

    @property
    def zone_id(self):
        return self.zonal_office_id

    @property
    def areas(self):
        return self.area_offices


class AreaOffice(Base):
    __tablename__ = "area_offices"

    id = Column(String, primary_key=True)
    regional_office_id = Column(String, ForeignKey("regional_offices.id"), nullable=False)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)

    regional_office = relationship("RegionalOffice", back_populates="area_offices")
    branches = relationship("BranchOffice", back_populates="area_office")

    @property
    def region_id(self):
        return self.regional_office_id


class BranchOffice(Base):
    __tablename__ = "branches"

    id = Column(String, primary_key=True)
    area_office_id = Column(String, ForeignKey("area_offices.id"), nullable=False)
    name = Column(String)
    code = Column(String, unique=True, index=True)
    branch_type = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)

    area_office = relationship("AreaOffice", back_populates="branches")
    customers = relationship("Customer", back_populates="branch")
    transactions = relationship("CustomerBranchTransaction", back_populates="branch")

    @property
    def area_id(self):
        return self.area_office_id


class CustomerBranchTransaction(Base):
    __tablename__ = "customer_branch_transactions"

    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=False)
    transaction_type = Column(String)
    amount = Column(String)
    currency = Column(String, default="INR")
    status = Column(String, default="completed")
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("BranchOffice", back_populates="transactions")
    customer = relationship("Customer")
