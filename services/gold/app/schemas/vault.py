"""
Vault & Packet Management Schemas
Phase 5: Hierarchical vault structure with QR codes and security management
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal


# ============================================================================
# VAULT HIERARCHY SCHEMAS
# ============================================================================

class VaultCreate(BaseModel):
    vault_code: str = Field(..., max_length=20)
    vault_name: str = Field(..., max_length=100)
    branch_id: str
    location_description: Optional[str] = None
    vault_type: str = Field(..., description="main, satellite, temporary")
    security_level: str = Field(..., description="high, medium, standard")
    capacity_packets: int = Field(default=0, ge=0)
    temperature_controlled: bool = False
    humidity_controlled: bool = False
    installed_date: Optional[date] = None
    created_by_user_id: Optional[str] = None


class VaultUpdate(BaseModel):
    vault_name: Optional[str] = None
    location_description: Optional[str] = None
    capacity_packets: Optional[int] = None
    is_active: Optional[bool] = None
    last_audit_date: Optional[date] = None


class VaultResponse(BaseModel):
    id: str
    vault_code: str
    vault_name: str
    branch_id: str
    location_description: Optional[str]
    vault_type: str
    security_level: str
    capacity_packets: int
    current_occupancy: int
    temperature_controlled: bool
    humidity_controlled: bool
    is_active: bool
    installed_date: Optional[date]
    last_audit_date: Optional[date]
    created_at: datetime
    occupancy_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class RackCreate(BaseModel):
    vault_id: str
    rack_code: str = Field(..., max_length=20)
    rack_number: int = Field(..., ge=1)
    capacity_lockers: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class RackResponse(BaseModel):
    id: str
    vault_id: str
    rack_code: str
    rack_number: int
    capacity_lockers: int
    current_occupancy: int
    is_active: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LockerCreate(BaseModel):
    rack_id: str
    locker_code: str = Field(..., max_length=20)
    locker_number: int = Field(..., ge=1)
    capacity_trays: int = Field(default=0, ge=0)
    lock_type: Optional[str] = Field(None, description="key, combination, electronic, biometric")
    lock_serial_number: Optional[str] = None
    notes: Optional[str] = None


class LockerResponse(BaseModel):
    id: str
    rack_id: str
    locker_code: str
    locker_number: int
    capacity_trays: int
    current_occupancy: int
    lock_type: Optional[str]
    lock_serial_number: Optional[str]
    is_active: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TrayCreate(BaseModel):
    locker_id: str
    tray_code: str = Field(..., max_length=20)
    tray_number: int = Field(..., ge=1)
    capacity_packets: int = Field(default=0, ge=0)
    tray_size: Optional[str] = Field(None, description="small, medium, large")
    notes: Optional[str] = None


class TrayResponse(BaseModel):
    id: str
    locker_id: str
    tray_code: str
    tray_number: int
    capacity_packets: int
    current_occupancy: int
    tray_size: Optional[str]
    is_active: bool
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PACKET MANAGEMENT SCHEMAS
# ============================================================================

class PacketCreate(BaseModel):
    appraisal_session_id: Optional[str] = None
    customer_id: str
    branch_id: str
    ornament_ids: List[str] = Field(default_factory=list)
    created_by_user_id: Optional[str] = None


class PacketSeal(BaseModel):
    seal_number: str
    seal_type: str = Field(..., description="paper, plastic, electronic, tamper_evident")
    sealed_by_user_id: str


class PacketVerifySeal(BaseModel):
    seal_verified_by_user_id: str
    seal_status: str = Field(..., description="intact, broken, tampered, missing")


class PacketAssignLocation(BaseModel):
    vault_id: str
    rack_id: str
    locker_id: str
    tray_id: str
    assigned_by_user_id: str


class PacketResponse(BaseModel):
    id: str
    packet_number: str
    appraisal_session_id: Optional[str]
    customer_id: str
    branch_id: str
    current_location_type: str
    vault_id: Optional[str]
    rack_id: Optional[str]
    locker_id: Optional[str]
    tray_id: Optional[str]
    total_ornaments: int
    total_weight_grams: Optional[Decimal]
    total_value: Optional[Decimal]
    qr_code: str
    qr_generated_at: Optional[datetime]
    seal_number: Optional[str]
    seal_type: Optional[str]
    sealed_by_user_id: Optional[str]
    sealed_at: Optional[datetime]
    seal_verified_by_user_id: Optional[str]
    seal_verified_at: Optional[datetime]
    seal_status: Optional[str]
    packet_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PacketWithLocation(BaseModel):
    """Packet with full location details"""
    packet: PacketResponse
    vault_code: Optional[str] = None
    vault_name: Optional[str] = None
    rack_code: Optional[str] = None
    locker_code: Optional[str] = None
    tray_code: Optional[str] = None
    full_location: Optional[str] = None


# ============================================================================
# PACKET MOVEMENT SCHEMAS
# ============================================================================

class PacketMovementCreate(BaseModel):
    packet_id: str
    movement_type: str = Field(..., description="vault_in, vault_out, transfer, inspection, audit")
    
    # From location (optional for initial vault_in)
    from_location_type: Optional[str] = None
    from_vault_id: Optional[str] = None
    from_rack_id: Optional[str] = None
    from_locker_id: Optional[str] = None
    from_tray_id: Optional[str] = None
    
    # To location
    to_location_type: str
    to_vault_id: Optional[str] = None
    to_rack_id: Optional[str] = None
    to_locker_id: Optional[str] = None
    to_tray_id: Optional[str] = None
    
    # Movement details
    moved_by_user_id: str
    qr_scanned: bool = False
    seal_checked: bool = False
    seal_status_at_movement: Optional[str] = None
    
    # GPS
    gps_latitude: Optional[Decimal] = None
    gps_longitude: Optional[Decimal] = None
    device_info: Optional[str] = None
    
    # Notes
    movement_reason: Optional[str] = None
    movement_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PacketMovementVerify(BaseModel):
    verified_by_user_id: str


class PacketMovementResponse(BaseModel):
    id: str
    packet_id: str
    movement_type: str
    from_location_type: Optional[str]
    from_vault_id: Optional[str]
    to_location_type: Optional[str]
    to_vault_id: Optional[str]
    moved_by_user_id: str
    verified_by_user_id: Optional[str]
    movement_timestamp: datetime
    verification_timestamp: Optional[datetime]
    qr_scanned: bool
    seal_checked: bool
    seal_status_at_movement: Optional[str]
    gps_latitude: Optional[Decimal]
    gps_longitude: Optional[Decimal]
    movement_reason: Optional[str]
    movement_notes: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# VAULT AUDIT SCHEMAS
# ============================================================================

class VaultAuditCreate(BaseModel):
    vault_id: str
    audit_type: str = Field(..., description="scheduled, surprise, regulatory, internal")
    audit_date: date
    lead_auditor_user_id: str
    auditor_team: Optional[List[str]] = None


class VaultAuditStart(BaseModel):
    total_packets_expected: int


class VaultAuditComplete(BaseModel):
    total_packets_found: int
    discrepancies_found: int = 0
    audit_result: str = Field(..., description="clean, minor_issues, major_issues, critical")
    findings_summary: Optional[str] = None
    recommendations: Optional[str] = None


class VaultAuditReview(BaseModel):
    reviewed_by_user_id: str


class VaultAuditApprove(BaseModel):
    approved_by_user_id: str


class VaultAuditResponse(BaseModel):
    id: str
    audit_number: str
    vault_id: str
    audit_type: str
    audit_date: date
    audit_started_at: Optional[datetime]
    audit_completed_at: Optional[datetime]
    lead_auditor_user_id: str
    auditor_team: Optional[List[str]]
    total_packets_expected: Optional[int]
    total_packets_found: Optional[int]
    discrepancies_found: int
    audit_status: str
    audit_result: Optional[str]
    findings_summary: Optional[str]
    recommendations: Optional[str]
    reviewed_by_user_id: Optional[str]
    reviewed_at: Optional[datetime]
    approved_by_user_id: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditFindingCreate(BaseModel):
    audit_id: str
    packet_id: Optional[str] = None
    finding_type: str = Field(..., description="missing, damaged, seal_broken, location_mismatch, weight_variance")
    severity: str = Field(..., description="low, medium, high, critical")
    finding_description: str
    expected_location: Optional[str] = None
    actual_location: Optional[str] = None
    expected_seal_number: Optional[str] = None
    actual_seal_number: Optional[str] = None
    photo_urls: Optional[List[str]] = None


class AuditFindingResolve(BaseModel):
    resolution_status: str = Field(..., description="resolved, escalated")
    resolution_notes: str
    resolved_by_user_id: str


class AuditFindingResponse(BaseModel):
    id: str
    audit_id: str
    packet_id: Optional[str]
    finding_type: str
    severity: str
    finding_description: str
    expected_location: Optional[str]
    actual_location: Optional[str]
    expected_seal_number: Optional[str]
    actual_seal_number: Optional[str]
    resolution_status: str
    resolution_notes: Optional[str]
    resolved_by_user_id: Optional[str]
    resolved_at: Optional[datetime]
    photo_urls: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ACCESS LOG SCHEMAS
# ============================================================================

class VaultAccessCreate(BaseModel):
    vault_id: str
    access_type: str = Field(..., description="entry, exit, inspection, maintenance")
    user_id: str
    authorized_by_user_id: Optional[str] = None
    authorization_reason: Optional[str] = None
    biometric_verified: bool = False
    access_card_number: Optional[str] = None
    purpose: Optional[str] = None
    gps_latitude: Optional[Decimal] = None
    gps_longitude: Optional[Decimal] = None
    device_info: Optional[str] = None


class VaultAccessExit(BaseModel):
    notes: Optional[str] = None


class VaultAccessResponse(BaseModel):
    id: str
    vault_id: str
    access_type: str
    user_id: str
    access_timestamp: datetime
    authorized_by_user_id: Optional[str]
    authorization_reason: Optional[str]
    biometric_verified: bool
    access_card_number: Optional[str]
    access_granted: bool
    access_denied_reason: Optional[str]
    exit_timestamp: Optional[datetime]
    duration_minutes: Optional[int]
    purpose: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# SEAL MANAGEMENT SCHEMAS
# ============================================================================

class SealCreate(BaseModel):
    seal_number: str
    seal_type: str
    seal_batch_number: Optional[str] = None


class SealIssue(BaseModel):
    issued_to_branch_id: str
    issued_to_user_id: str


class SealDispose(BaseModel):
    disposed_by_user_id: str
    disposal_reason: str


class SealResponse(BaseModel):
    id: str
    seal_number: str
    seal_type: str
    seal_batch_number: Optional[str]
    seal_status: str
    issued_to_branch_id: Optional[str]
    issued_to_user_id: Optional[str]
    issued_at: Optional[datetime]
    used_on_packet_id: Optional[str]
    used_at: Optional[datetime]
    used_by_user_id: Optional[str]
    disposed_at: Optional[datetime]
    disposed_by_user_id: Optional[str]
    disposal_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMPLEX RESPONSE SCHEMAS
# ============================================================================

class VaultHierarchy(BaseModel):
    """Complete vault hierarchy with all levels"""
    vault: VaultResponse
    racks: List[Dict[str, Any]]
    total_capacity: int
    current_occupancy: int
    occupancy_percentage: float


class PacketAuditTrail(BaseModel):
    """Complete audit trail for a packet"""
    packet: PacketResponse
    movements: List[PacketMovementResponse]
    current_location: Optional[str]
    total_movements: int
    days_in_vault: Optional[int]
    seal_changes: int
