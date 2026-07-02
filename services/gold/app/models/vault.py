"""
Vault & Packet Management Models
Phase 5: Hierarchical vault structure with QR codes and security management
"""
from datetime import datetime, date
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Date, Text, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from .product import Base


class GoldVault(Base):
    __tablename__ = "gold_vaults"

    id = Column(String, primary_key=True)
    vault_code = Column(String(20), unique=True, nullable=False, index=True)
    vault_name = Column(String(100), nullable=False)
    branch_id = Column(String(50), nullable=False, index=True)
    location_description = Column(Text)
    vault_type = Column(String(30), nullable=False, index=True)
    security_level = Column(String(30), nullable=False)
    capacity_packets = Column(Integer, default=0)
    current_occupancy = Column(Integer, default=0)
    temperature_controlled = Column(Boolean, default=False)
    humidity_controlled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    installed_date = Column(Date)
    last_audit_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))


class GoldVaultRack(Base):
    __tablename__ = "gold_vault_racks"

    id = Column(String, primary_key=True)
    vault_id = Column(String(50), ForeignKey("gold_vaults.id", ondelete="CASCADE"), nullable=False, index=True)
    rack_code = Column(String(20), nullable=False)
    rack_number = Column(Integer, nullable=False)
    capacity_lockers = Column(Integer, default=0)
    current_occupancy = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldVaultLocker(Base):
    __tablename__ = "gold_vault_lockers"

    id = Column(String, primary_key=True)
    rack_id = Column(String(50), ForeignKey("gold_vault_racks.id", ondelete="CASCADE"), nullable=False, index=True)
    locker_code = Column(String(20), nullable=False)
    locker_number = Column(Integer, nullable=False)
    capacity_trays = Column(Integer, default=0)
    current_occupancy = Column(Integer, default=0)
    lock_type = Column(String(30))
    lock_serial_number = Column(String(50))
    is_active = Column(Boolean, default=True, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldVaultTray(Base):
    __tablename__ = "gold_vault_trays"

    id = Column(String, primary_key=True)
    locker_id = Column(String(50), ForeignKey("gold_vault_lockers.id", ondelete="CASCADE"), nullable=False, index=True)
    tray_code = Column(String(20), nullable=False)
    tray_number = Column(Integer, nullable=False)
    capacity_packets = Column(Integer, default=0)
    current_occupancy = Column(Integer, default=0)
    tray_size = Column(String(20))
    is_active = Column(Boolean, default=True, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldPacket(Base):
    __tablename__ = "gold_packets"

    id = Column(String, primary_key=True)
    packet_number = Column(String(50), unique=True, nullable=False, index=True)
    appraisal_session_id = Column(String(50))
    customer_id = Column(String(50), nullable=False, index=True)
    branch_id = Column(String(50), nullable=False, index=True)
    
    # Current location
    current_location_type = Column(String(30), nullable=False, index=True)
    vault_id = Column(String(50), ForeignKey("gold_vaults.id", ondelete="SET NULL"), index=True)
    rack_id = Column(String(50), ForeignKey("gold_vault_racks.id", ondelete="SET NULL"))
    locker_id = Column(String(50), ForeignKey("gold_vault_lockers.id", ondelete="SET NULL"))
    tray_id = Column(String(50), ForeignKey("gold_vault_trays.id", ondelete="SET NULL"))
    
    # Packet details
    total_ornaments = Column(Integer, default=0)
    total_weight_grams = Column(DECIMAL(10, 3))
    total_value = Column(DECIMAL(15, 2))
    
    # QR code
    qr_code = Column(String(100), unique=True, nullable=False, index=True)
    qr_generated_at = Column(DateTime)
    
    # Security seal
    seal_number = Column(String(50), unique=True)
    seal_type = Column(String(30))
    sealed_by_user_id = Column(String(50))
    sealed_at = Column(DateTime)
    seal_verified_by_user_id = Column(String(50))
    seal_verified_at = Column(DateTime)
    seal_status = Column(String(30))
    
    # Status
    packet_status = Column(String(30), nullable=False, default='created', index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))


class GoldPacketOrnament(Base):
    __tablename__ = "gold_packet_ornaments"

    id = Column(String, primary_key=True)
    packet_id = Column(String(50), ForeignKey("gold_packets.id", ondelete="CASCADE"), nullable=False, index=True)
    ornament_id = Column(String(50), nullable=False, index=True)
    sequence_number = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    added_by_user_id = Column(String(50))


class GoldPacketMovement(Base):
    __tablename__ = "gold_packet_movements"

    id = Column(String, primary_key=True)
    packet_id = Column(String(50), ForeignKey("gold_packets.id", ondelete="CASCADE"), nullable=False, index=True)
    movement_type = Column(String(40), nullable=False, index=True)
    
    # Location details
    from_location_type = Column(String(30))
    from_vault_id = Column(String(50), index=True)
    from_rack_id = Column(String(50))
    from_locker_id = Column(String(50))
    from_tray_id = Column(String(50))
    
    to_location_type = Column(String(30))
    to_vault_id = Column(String(50), index=True)
    to_rack_id = Column(String(50))
    to_locker_id = Column(String(50))
    to_tray_id = Column(String(50))
    
    # Movement details
    moved_by_user_id = Column(String(50), nullable=False)
    verified_by_user_id = Column(String(50))
    movement_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    verification_timestamp = Column(DateTime)
    
    # Security
    qr_scanned = Column(Boolean, default=False)
    seal_checked = Column(Boolean, default=False)
    seal_status_at_movement = Column(String(30))
    
    # GPS and device
    gps_latitude = Column(DECIMAL(10, 8))
    gps_longitude = Column(DECIMAL(11, 8))
    device_info = Column(String(255))
    
    # Notes
    movement_reason = Column(Text)
    movement_notes = Column(Text)
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldVaultAudit(Base):
    __tablename__ = "gold_vault_audits"

    id = Column(String, primary_key=True)
    audit_number = Column(String(50), unique=True, nullable=False)
    vault_id = Column(String(50), ForeignKey("gold_vaults.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Audit details
    audit_type = Column(String(30), nullable=False, index=True)
    audit_date = Column(Date, nullable=False, index=True)
    audit_started_at = Column(DateTime)
    audit_completed_at = Column(DateTime)
    
    # Team
    lead_auditor_user_id = Column(String(50), nullable=False)
    auditor_team = Column(JSON)
    
    # Findings
    total_packets_expected = Column(Integer)
    total_packets_found = Column(Integer)
    discrepancies_found = Column(Integer, default=0)
    
    # Status
    audit_status = Column(String(30), nullable=False, default='scheduled', index=True)
    
    # Results
    audit_result = Column(String(30))
    findings_summary = Column(Text)
    recommendations = Column(Text)
    
    # Approvals
    reviewed_by_user_id = Column(String(50))
    reviewed_at = Column(DateTime)
    approved_by_user_id = Column(String(50))
    approved_at = Column(DateTime)
    
    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GoldAuditFinding(Base):
    __tablename__ = "gold_audit_findings"

    id = Column(String, primary_key=True)
    audit_id = Column(String(50), ForeignKey("gold_vault_audits.id", ondelete="CASCADE"), nullable=False, index=True)
    packet_id = Column(String(50), ForeignKey("gold_packets.id", ondelete="SET NULL"), index=True)
    
    # Finding details
    finding_type = Column(String(40), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    finding_description = Column(Text, nullable=False)
    
    # Expected vs actual
    expected_location = Column(String(255))
    actual_location = Column(String(255))
    expected_seal_number = Column(String(50))
    actual_seal_number = Column(String(50))
    
    # Resolution
    resolution_status = Column(String(30), default='open', index=True)
    resolution_notes = Column(Text)
    resolved_by_user_id = Column(String(50))
    resolved_at = Column(DateTime)
    
    # Photos
    photo_urls = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GoldVaultAccessLog(Base):
    __tablename__ = "gold_vault_access_log"

    id = Column(String, primary_key=True)
    vault_id = Column(String(50), ForeignKey("gold_vaults.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Access details
    access_type = Column(String(30), nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    access_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Authorization
    authorized_by_user_id = Column(String(50))
    authorization_reason = Column(Text)
    
    # Security
    biometric_verified = Column(Boolean, default=False)
    access_card_number = Column(String(50))
    access_granted = Column(Boolean, default=True)
    access_denied_reason = Column(Text)
    
    # Duration
    exit_timestamp = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # GPS and device
    gps_latitude = Column(DECIMAL(10, 8))
    gps_longitude = Column(DECIMAL(11, 8))
    device_info = Column(String(255))
    
    # Notes
    purpose = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class GoldSecuritySeal(Base):
    __tablename__ = "gold_security_seals"

    id = Column(String, primary_key=True)
    seal_number = Column(String(50), unique=True, nullable=False, index=True)
    seal_type = Column(String(30), nullable=False)
    seal_batch_number = Column(String(50))
    
    # Status
    seal_status = Column(String(30), nullable=False, default='available', index=True)
    
    # Assignment
    issued_to_branch_id = Column(String(50), index=True)
    issued_to_user_id = Column(String(50))
    issued_at = Column(DateTime)
    
    # Usage
    used_on_packet_id = Column(String(50), ForeignKey("gold_packets.id", ondelete="SET NULL"), index=True)
    used_at = Column(DateTime)
    used_by_user_id = Column(String(50))
    
    # Disposal
    disposed_at = Column(DateTime)
    disposed_by_user_id = Column(String(50))
    disposal_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
