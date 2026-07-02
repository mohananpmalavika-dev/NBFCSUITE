"""
Gold Ornament Catalog Models
Phase 4: Enhanced Ornament Lifecycle & Management
"""
from datetime import datetime, date
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Date, Text, BigInteger
from sqlalchemy.orm import relationship
from .product import Base


class GoldOrnamentPhoto(Base):
    __tablename__ = "gold_ornament_photos"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    photo_url = Column(String(500), nullable=False)
    photo_type = Column(String(60), nullable=False, index=True)
    file_name = Column(String(255))
    file_size_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    width_pixels = Column(Integer)
    height_pixels = Column(Integer)
    uploaded_by_user_id = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    photo_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False, index=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldOrnamentStone(Base):
    __tablename__ = "gold_ornament_stones"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    stone_number = Column(Integer, nullable=False)
    stone_type = Column(String(80), nullable=False, index=True)
    stone_shape = Column(String(60))
    stone_cut = Column(String(60))
    stone_color = Column(String(60))
    stone_clarity = Column(String(60))
    carat_weight = Column(Float)
    gram_weight = Column(Float)
    count = Column(Integer, default=1)
    estimated_value = Column(Float)
    is_certified = Column(Boolean, default=False, index=True)
    certificate_number = Column(String(120))
    certificate_authority = Column(String(120))
    certificate_url = Column(String(500))
    stone_quality = Column(String(60))
    stone_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GoldOrnamentStatusHistory(Base):
    __tablename__ = "gold_ornament_status_history"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = Column(String(40))
    to_status = Column(String(40), nullable=False, index=True)
    status_reason = Column(Text)
    changed_by_user_id = Column(String, nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)
    location = Column(String(255))
    notes = Column(Text)
    metadata = Column(JSON)


class GoldOrnamentMovement(Base):
    __tablename__ = "gold_ornament_movements"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    movement_type = Column(String(60), nullable=False, index=True)
    from_location = Column(String(255))
    to_location = Column(String(255))
    moved_by_user_id = Column(String, nullable=False)
    verified_by_user_id = Column(String)
    movement_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    verification_timestamp = Column(DateTime)
    qr_scanned = Column(Boolean, default=False)
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    device_info = Column(String(255))
    movement_notes = Column(Text)
    metadata = Column(JSON)


class GoldOrnamentCondition(Base):
    __tablename__ = "gold_ornament_conditions"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    inspection_date = Column(DateTime, nullable=False, index=True)
    inspector_user_id = Column(String, nullable=False)
    overall_condition = Column(String(60), nullable=False, index=True)
    has_damage = Column(Boolean, default=False)
    damage_description = Column(Text)
    damage_photos = Column(JSON)
    has_repair = Column(Boolean, default=False)
    repair_description = Column(Text)
    has_missing_parts = Column(Boolean, default=False)
    missing_parts_description = Column(Text)
    stone_condition = Column(String(60))
    clasp_condition = Column(String(60))
    polish_level = Column(String(60))
    weight_verified = Column(Boolean, default=False)
    weight_variance_grams = Column(Float)
    condition_notes = Column(Text)
    next_inspection_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldOrnamentTag(Base):
    __tablename__ = "gold_ornament_tags"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_category = Column(String(80), nullable=False, index=True)
    tag_value = Column(String(120), nullable=False, index=True)
    tag_confidence = Column(Float)
    tagged_by = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldOrnamentComparison(Base):
    __tablename__ = "gold_ornament_comparisons"

    id = Column(String, primary_key=True)
    ornament_id_1 = Column(String, ForeignKey("gold_ornaments.id"), nullable=False, index=True)
    ornament_id_2 = Column(String, ForeignKey("gold_ornaments.id"), nullable=False, index=True)
    comparison_type = Column(String(60), nullable=False)
    similarity_score = Column(Float)
    matching_attributes = Column(JSON)
    compared_by = Column(String(60))
    comparison_date = Column(DateTime, default=datetime.utcnow)
    is_flagged = Column(Boolean, default=False, index=True)
    investigation_status = Column(String(40))
    investigation_notes = Column(Text)
    resolved_by_user_id = Column(String)
    resolved_at = Column(DateTime)


class GoldOrnamentCertificate(Base):
    __tablename__ = "gold_ornament_certificates"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    certificate_type = Column(String(80), nullable=False, index=True)
    certificate_number = Column(String(120), unique=True, index=True)
    issuing_authority = Column(String(200), nullable=False)
    issued_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    certificate_url = Column(String(500))
    certificate_hash = Column(String(255))
    is_verified = Column(Boolean, default=False)
    verified_by_user_id = Column(String)
    verified_at = Column(DateTime)
    verification_method = Column(String(60))
    certificate_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldOrnamentInsurance(Base):
    __tablename__ = "gold_ornament_insurance"

    id = Column(String, primary_key=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_number = Column(String(120), unique=True, nullable=False, index=True)
    insurance_provider = Column(String(200), nullable=False)
    insured_value = Column(Float, nullable=False)
    premium_amount = Column(Float)
    policy_start_date = Column(Date, nullable=False)
    policy_end_date = Column(Date, nullable=False)
    coverage_type = Column(String(80))
    is_active = Column(Boolean, default=True, index=True)
    policy_document_url = Column(String(500))
    claim_history = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GoldOrnamentGroup(Base):
    __tablename__ = "gold_ornament_groups"

    id = Column(String, primary_key=True)
    group_name = Column(String(200), nullable=False)
    group_type = Column(String(60))
    description = Column(Text)
    total_ornaments = Column(Integer, default=0)
    total_weight_grams = Column(Float)
    total_value = Column(Float)
    customer_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldOrnamentGroupMember(Base):
    __tablename__ = "gold_ornament_group_members"

    id = Column(String, primary_key=True)
    group_id = Column(String, ForeignKey("gold_ornament_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    ornament_id = Column(String, ForeignKey("gold_ornaments.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_number = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("GoldOrnamentGroup")
