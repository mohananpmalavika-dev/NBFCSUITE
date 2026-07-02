"""
Gold Product Configuration Models
Phase 1: Product Engine
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Date, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class GoldProduct(Base):
    __tablename__ = "gold_products"

    id = Column(String, primary_key=True)
    product_code = Column(String(40), unique=True, nullable=False, index=True)
    product_name = Column(String(120), nullable=False)
    product_type = Column(String(60), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String)
    updated_by = Column(String)

    # Relationships
    interest = relationship("GoldProductInterest", back_populates="product", uselist=False, cascade="all, delete-orphan")
    tenure = relationship("GoldProductTenure", back_populates="product", uselist=False, cascade="all, delete-orphan")
    limits = relationship("GoldProductLimits", back_populates="product", uselist=False, cascade="all, delete-orphan")
    charges = relationship("GoldProductCharge", back_populates="product", cascade="all, delete-orphan")
    documents = relationship("GoldProductDocument", back_populates="product", cascade="all, delete-orphan")
    eligibility = relationship("GoldProductEligibility", back_populates="product", cascade="all, delete-orphan")
    workflow = relationship("GoldProductWorkflow", back_populates="product", cascade="all, delete-orphan")
    channels = relationship("GoldProductChannel", back_populates="product", cascade="all, delete-orphan")
    taxes = relationship("GoldProductTax", back_populates="product", cascade="all, delete-orphan")


class GoldProductInterest(Base):
    __tablename__ = "gold_product_interest"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, unique=True)
    interest_type = Column(String(40), nullable=False)  # flat, reducing, simple
    rate_type = Column(String(40), nullable=False)  # fixed, floating, tiered
    base_rate = Column(Float, nullable=False)
    min_rate = Column(Float)
    max_rate = Column(Float)
    penal_interest = Column(Float, default=0)
    compounding_frequency = Column(String(40))  # daily, monthly, quarterly, none
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="interest")


class GoldProductTenure(Base):
    __tablename__ = "gold_product_tenure"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, unique=True)
    min_tenure_months = Column(Integer, nullable=False)
    max_tenure_months = Column(Integer, nullable=False)
    default_tenure_months = Column(Integer, nullable=False)
    tenure_unit = Column(String(20), default="months")
    renewal_allowed = Column(Boolean, default=True)
    max_renewals = Column(Integer)
    auto_renewal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="tenure")


class GoldProductLimits(Base):
    __tablename__ = "gold_product_limits"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, unique=True)
    min_loan_amount = Column(Float, nullable=False)
    max_loan_amount = Column(Float, nullable=False)
    ltv_percent = Column(Float, nullable=False, default=75.0)
    min_ltv = Column(Float)
    max_ltv = Column(Float)
    min_gold_weight_grams = Column(Float, nullable=False, default=5.0)
    max_gold_weight_grams = Column(Float)
    purity_threshold_karat = Column(Float, default=18.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="limits")


class GoldProductCharge(Base):
    __tablename__ = "gold_product_charges"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, index=True)
    charge_code = Column(String(40), nullable=False, index=True)
    charge_name = Column(String(120), nullable=False)
    charge_type = Column(String(40), nullable=False)  # flat, percentage, slab
    charge_amount = Column(Float)
    charge_percentage = Column(Float)
    min_charge = Column(Float)
    max_charge = Column(Float)
    charge_frequency = Column(String(40))  # one_time, monthly, quarterly, yearly
    is_mandatory = Column(Boolean, default=True)
    is_refundable = Column(Boolean, default=False)
    tax_applicable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="charges")


class GoldProductDocument(Base):
    __tablename__ = "gold_product_documents"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(80), nullable=False)
    document_name = Column(String(120), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    verification_required = Column(Boolean, default=True)
    document_category = Column(String(60))  # kyc, income, property, others
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="documents")


class GoldProductEligibility(Base):
    __tablename__ = "gold_product_eligibility"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_type = Column(String(60), nullable=False, index=True)
    rule_name = Column(String(120), nullable=False)
    rule_operator = Column(String(40), nullable=False)  # eq, ne, gt, lt, gte, lte, in, not_in, contains
    rule_value = Column(JSON, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="eligibility")


class GoldProductWorkflow(Base):
    __tablename__ = "gold_product_workflow"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, index=True)
    stage_order = Column(Integer, nullable=False)
    stage_name = Column(String(120), nullable=False)
    stage_type = Column(String(60), nullable=False)  # system, user, role, ai
    approver_role = Column(String(80))
    amount_min = Column(Float)
    amount_max = Column(Float)
    sla_hours = Column(Integer)
    is_parallel = Column(Boolean, default=False)
    auto_approve_conditions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="workflow")


class GoldProductChannel(Base):
    __tablename__ = "gold_product_channel"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_type = Column(String(60), nullable=False)  # branch, mobile, web, partner, dsa
    is_enabled = Column(Boolean, default=True)
    requires_verification = Column(Boolean, default=True)
    instant_approval_limit = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="channels")


class GoldProductTax(Base):
    __tablename__ = "gold_product_tax"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("gold_products.id", ondelete="CASCADE"), nullable=False, index=True)
    tax_type = Column(String(60), nullable=False)  # gst, service_tax, stamp_duty
    tax_name = Column(String(120), nullable=False)
    tax_percentage = Column(Float, nullable=False)
    tax_category = Column(String(60))  # interest, charges, both
    hsn_sac_code = Column(String(40))
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date)
    effective_to = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product = relationship("GoldProduct", back_populates="taxes")
