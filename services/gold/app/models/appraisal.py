"""
Gold Appraisal Engine Models
Phase 3: Advanced Ornament Cataloging & Valuation
"""
from datetime import datetime, date
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Date, Text
from sqlalchemy.orm import relationship
from .product import Base


class GoldOrnamentType(Base):
    __tablename__ = "gold_ornament_types"

    id = Column(String, primary_key=True)
    type_code = Column(String(40), unique=True, nullable=False, index=True)
    type_name = Column(String(120), nullable=False)
    category = Column(String(60))
    typical_stone_percentage = Column(Float, default=0)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldPurityTest(Base):
    __tablename__ = "gold_purity_tests"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id"), nullable=False, index=True)
    test_number = Column(Integer, nullable=False)
    test_method = Column(String(60), nullable=False)
    tested_karat = Column(Float, nullable=False)
    tested_purity_percent = Column(Float, nullable=False)
    test_equipment = Column(String(120))
    test_location = Column(String(120))
    tested_by_user_id = Column(String)
    tested_at = Column(DateTime, default=datetime.utcnow, index=True)
    test_results = Column(JSON)
    test_certificate_url = Column(String(255))
    is_verified = Column(Boolean, default=False)
    verified_by_user_id = Column(String)
    verified_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldMarketRate(Base):
    __tablename__ = "gold_market_rates"

    id = Column(String, primary_key=True)
    rate_date = Column(Date, nullable=False, index=True)
    rate_source = Column(String(80), nullable=False)
    purity_karat = Column(Float, nullable=False, index=True)
    rate_per_gram = Column(Float, nullable=False)
    rate_per_10gram = Column(Float)
    currency = Column(String(10), default="INR")
    city = Column(String(120))
    branch_id = Column(String, index=True)
    is_active = Column(Boolean, default=True, index=True)
    effective_from = Column(DateTime, nullable=False, index=True)
    effective_to = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    created_by_user_id = Column(String)
    rate_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldAppraisalSession(Base):
    __tablename__ = "gold_appraisal_sessions"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("gold_loan_applications.id"), nullable=False, index=True)
    session_number = Column(String(40), unique=True, nullable=False)
    customer_id = Column(String, nullable=False, index=True)
    appraiser_user_id = Column(String)
    session_status = Column(String(40), default="in_progress", index=True)
    total_ornaments = Column(Integer, default=0)
    total_gross_weight = Column(Float, default=0)
    total_net_weight = Column(Float, default=0)
    total_appraised_value = Column(Float, default=0)
    average_purity_karat = Column(Float)
    gold_rate_id = Column(String, ForeignKey("gold_market_rates.id"))
    ltv_percent = Column(Float)
    eligible_loan_amount = Column(Float)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    verified_at = Column(DateTime)
    verified_by_user_id = Column(String)
    session_notes = Column(Text)
    session_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    gold_rate = relationship("GoldMarketRate")


class GoldOrnamentValuation(Base):
    __tablename__ = "gold_ornament_valuations"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id"), nullable=False, index=True)
    valuation_date = Column(Date, nullable=False, index=True)
    valuation_type = Column(String(60), nullable=False)
    gold_rate_per_gram = Column(Float, nullable=False)
    purity_percent = Column(Float, nullable=False)
    net_weight_grams = Column(Float, nullable=False)
    calculated_value = Column(Float, nullable=False)
    market_value = Column(Float)
    forced_sale_value = Column(Float)
    valued_by_user_id = Column(String)
    valuation_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldWeightVerification(Base):
    __tablename__ = "gold_weight_verifications"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id"), nullable=False, index=True)
    measurement_type = Column(String(60), nullable=False)
    measured_by_user_id = Column(String, nullable=False)
    measured_weight = Column(Float, nullable=False)
    weighing_scale_id = Column(String(120))
    measurement_timestamp = Column(DateTime, default=datetime.utcnow)
    verified_by_user_id = Column(String, index=True)
    verified_weight = Column(Float)
    verification_timestamp = Column(DateTime)
    variance_grams = Column(Float)
    is_accepted = Column(Boolean)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldAppraisalAnomaly(Base):
    __tablename__ = "gold_appraisal_anomalies"

    id = Column(String, primary_key=True)
    appraisal_session_id = Column(String, ForeignKey("gold_appraisal_sessions.id"), index=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id"), index=True)
    anomaly_type = Column(String(80), nullable=False)
    severity = Column(String(40), nullable=False, index=True)
    anomaly_description = Column(Text, nullable=False)
    detected_by = Column(String(60))
    detection_data = Column(JSON)
    status = Column(String(40), default="open", index=True)
    resolution_notes = Column(Text)
    resolved_by_user_id = Column(String)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
