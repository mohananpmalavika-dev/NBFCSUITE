from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .db import Base


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(String, primary_key=True)

    status = Column(String, nullable=False, default="lead")
    source = Column(String, nullable=True)
    campaign = Column(String, nullable=True)

    branch_id = Column(String, nullable=True)
    assigned_rm = Column(String, nullable=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    phone = Column(String, nullable=False, unique=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)

    pan_number = Column(String, nullable=True, unique=True)
    aadhar_number = Column(String, nullable=True, unique=True)
    passport_number = Column(String, nullable=True, unique=True)
    voter_id = Column(String, nullable=True, unique=True)
    driving_licence = Column(String, nullable=True, unique=True)
    gstin = Column(String, nullable=True, unique=True)
    cin = Column(String, nullable=True, unique=True)
    nationality = Column(String, nullable=True)
    resident_status = Column(String, nullable=True)
    customer_type = Column(String, nullable=True, default="individual")
    occupation = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    education = Column(String, nullable=True)
    annual_income = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    contact_profile = Column(JSON, nullable=True)
    family_profile = Column(JSON, nullable=True)
    employment_profile = Column(JSON, nullable=True)
    business_profile = Column(JSON, nullable=True)
    financial_profile = Column(JSON, nullable=True)
    banking_profile = Column(JSON, nullable=True)
    compliance_profile = Column(JSON, nullable=True)
    behavior_profile = Column(JSON, nullable=True)
    relationship_profile = Column(JSON, nullable=True)

    kyc_status = Column(String, nullable=True, default="pending")
    risk_level = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    customer_id = Column(String, nullable=True)


class ProspectAddress(Base):
    __tablename__ = "prospect_addresses"

    id = Column(String, primary_key=True)
    prospect_id = Column(String, ForeignKey("prospects.id"), nullable=False)

    address_type = Column(String, nullable=True)
    street_address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    is_primary = Column(String, nullable=True, default="false")

    created_at = Column(DateTime, default=datetime.utcnow)


class ProspectKYCDocument(Base):
    __tablename__ = "prospect_kyc_documents"

    id = Column(String, primary_key=True)
    prospect_id = Column(String, ForeignKey("prospects.id"), nullable=False)

    document_type = Column(String, nullable=True)
    document_number = Column(String, nullable=True)
    document_url = Column(String, nullable=True)
    verification_status = Column(String, nullable=True, default="pending")
    verified_at = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

