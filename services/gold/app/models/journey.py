"""
Gold Customer Journey Models
Phase 2: Customer Journey & CIF Integration
"""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Date, Text
from sqlalchemy.orm import relationship
from .product import Base


class GoldCustomerSession(Base):
    __tablename__ = "gold_customer_sessions"

    id = Column(String, primary_key=True)
    session_number = Column(String(40), unique=True, nullable=False, index=True)
    customer_id = Column(String, index=True)
    branch_id = Column(String, index=True)
    channel = Column(String(40), nullable=False, default="branch")
    session_type = Column(String(40), nullable=False, default="new_loan")
    status = Column(String(40), nullable=False, default="initiated", index=True)
    initiated_by_user_id = Column(String)
    initiated_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    abandoned_at = Column(DateTime)
    abandonment_reason = Column(Text)
    session_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    search_logs = relationship("GoldCustomerSearchLog", back_populates="session", cascade="all, delete-orphan")
    product_selections = relationship("GoldProductSelection", back_populates="session", cascade="all, delete-orphan")
    eligibility_checks = relationship("GoldEligibilityCheck", back_populates="session", cascade="all, delete-orphan")
    kyc_verifications = relationship("GoldKYCVerification", back_populates="session", cascade="all, delete-orphan")
    journey_steps = relationship("GoldJourneyStep", back_populates="session", cascade="all, delete-orphan")
    interactions = relationship("GoldCustomerInteraction", back_populates="session", cascade="all, delete-orphan")


class GoldCustomerSearchLog(Base):
    __tablename__ = "gold_customer_search_log"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("gold_customer_sessions.id"), index=True)
    search_criteria = Column(JSON, nullable=False)
    results_found = Column(Integer, default=0)
    selected_customer_id = Column(String, index=True)
    searched_at = Column(DateTime, default=datetime.utcnow)
    searched_by_user_id = Column(String)

    # Relationship
    session = relationship("GoldCustomerSession", back_populates="search_logs")


class GoldProductSelection(Base):
    __tablename__ = "gold_product_selections"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("gold_customer_sessions.id"), index=True)
    product_id = Column(String, ForeignKey("gold_products.id"), index=True)
    customer_id = Column(String, index=True)
    requested_amount = Column(Float)
    estimated_gold_weight = Column(Float)
    selected_at = Column(DateTime, default=datetime.utcnow)
    selection_source = Column(String(40))
    recommendation_score = Column(Float)
    is_converted = Column(Boolean, default=False)
    application_id = Column(String)

    # Relationships
    session = relationship("GoldCustomerSession", back_populates="product_selections")


class GoldEligibilityCheck(Base):
    __tablename__ = "gold_eligibility_checks"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("gold_customer_sessions.id"), index=True)
    customer_id = Column(String, nullable=False, index=True)
    product_id = Column(String, ForeignKey("gold_products.id"), nullable=False, index=True)
    check_type = Column(String(60), nullable=False)
    rule_id = Column(String)
    is_passed = Column(Boolean, nullable=False)
    check_value = Column(JSON)
    failure_reason = Column(Text)
    checked_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("GoldCustomerSession", back_populates="eligibility_checks")


class GoldKYCVerification(Base):
    __tablename__ = "gold_kyc_verifications"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("gold_customer_sessions.id"), index=True)
    customer_id = Column(String, nullable=False, index=True)
    document_type = Column(String(80), nullable=False)
    document_number = Column(String(120))
    verification_method = Column(String(60))
    verification_status = Column(String(40), nullable=False, index=True)
    verified_by_user_id = Column(String)
    verified_at = Column(DateTime)
    verification_response = Column(JSON)
    expiry_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("GoldCustomerSession", back_populates="kyc_verifications")


class GoldJourneyStep(Base):
    __tablename__ = "gold_journey_steps"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("gold_customer_sessions.id"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(120), nullable=False, index=True)
    step_status = Column(String(40), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    step_data = Column(JSON)
    error_message = Column(Text)

    # Relationship
    session = relationship("GoldCustomerSession", back_populates="journey_steps")


class GoldCustomerInteraction(Base):
    __tablename__ = "gold_customer_interactions"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("gold_customer_sessions.id"), index=True)
    customer_id = Column(String, index=True)
    interaction_type = Column(String(60), nullable=False, index=True)
    interaction_category = Column(String(60))
    notes = Column(Text, nullable=False)
    officer_user_id = Column(String)
    interaction_at = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String(40))
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)

    # Relationship
    session = relationship("GoldCustomerSession", back_populates="interactions")
