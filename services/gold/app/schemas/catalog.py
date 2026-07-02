"""
Gold Ornament Catalog Schemas
Phase 4: Enhanced Ornament Lifecycle & Management
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Photo Management
class OrnamentPhotoCreate(BaseModel):
    ornament_id: str
    photo_url: str
    photo_type: str = Field(..., description="general, hallmark, close_up, damage, stone, certificate")
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    uploaded_by_user_id: Optional[str] = None
    photo_order: int = 0
    is_primary: bool = False
    metadata: Optional[Dict[str, Any]] = None


class OrnamentPhotoResponse(BaseModel):
    id: str
    ornament_id: str
    photo_url: str
    photo_type: str
    file_name: Optional[str]
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    width_pixels: Optional[int]
    height_pixels: Optional[int]
    uploaded_by_user_id: Optional[str]
    uploaded_at: datetime
    photo_order: int
    is_primary: bool
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Stone Catalog
class StoneCreate(BaseModel):
    ornament_id: str
    stone_number: int
    stone_type: str = Field(..., description="diamond, ruby, emerald, sapphire, pearl, etc.")
    stone_shape: Optional[str] = Field(None, description="round, oval, square, pear, marquise")
    stone_cut: Optional[str] = Field(None, description="brilliant, princess, emerald, cushion")
    stone_color: Optional[str] = None
    stone_clarity: Optional[str] = None
    carat_weight: Optional[float] = None
    gram_weight: Optional[float] = None
    count: int = 1
    estimated_value: Optional[float] = None
    is_certified: bool = False
    certificate_number: Optional[str] = None
    certificate_authority: Optional[str] = None
    certificate_url: Optional[str] = None
    stone_quality: Optional[str] = Field(None, description="precious, semi_precious, synthetic")
    stone_notes: Optional[str] = None


class StoneResponse(BaseModel):
    id: str
    ornament_id: str
    stone_number: int
    stone_type: str
    stone_shape: Optional[str]
    stone_cut: Optional[str]
    stone_color: Optional[str]
    stone_clarity: Optional[str]
    carat_weight: Optional[float]
    gram_weight: Optional[float]
    count: int
    estimated_value: Optional[float]
    is_certified: bool
    certificate_number: Optional[str]
    certificate_authority: Optional[str]
    certificate_url: Optional[str]
    stone_quality: Optional[str]
    stone_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Status History
class StatusChangeCreate(BaseModel):
    ornament_id: str
    to_status: str
    status_reason: Optional[str] = None
    changed_by_user_id: str
    location: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StatusHistoryResponse(BaseModel):
    id: str
    ornament_id: str
    from_status: Optional[str]
    to_status: str
    status_reason: Optional[str]
    changed_by_user_id: str
    changed_at: datetime
    location: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# Movement Tracking
class MovementCreate(BaseModel):
    ornament_id: str
    movement_type: str = Field(..., description="received, appraised, vaulted, inspected, released, auctioned")
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    moved_by_user_id: str
    qr_scanned: bool = False
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    device_info: Optional[str] = None
    movement_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MovementVerify(BaseModel):
    verified_by_user_id: str


class MovementResponse(BaseModel):
    id: str
    ornament_id: str
    movement_type: str
    from_location: Optional[str]
    to_location: Optional[str]
    moved_by_user_id: str
    verified_by_user_id: Optional[str]
    movement_timestamp: datetime
    verification_timestamp: Optional[datetime]
    qr_scanned: bool
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    device_info: Optional[str]
    movement_notes: Optional[str]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# Condition Inspection
class ConditionInspectionCreate(BaseModel):
    ornament_id: str
    inspector_user_id: str
    overall_condition: str = Field(..., description="excellent, good, fair, poor, damaged")
    has_damage: bool = False
    damage_description: Optional[str] = None
    damage_photos: Optional[List[str]] = None
    has_repair: bool = False
    repair_description: Optional[str] = None
    has_missing_parts: bool = False
    missing_parts_description: Optional[str] = None
    stone_condition: Optional[str] = None
    clasp_condition: Optional[str] = None
    polish_level: Optional[str] = None
    weight_verified: bool = False
    weight_variance_grams: Optional[float] = None
    condition_notes: Optional[str] = None
    next_inspection_date: Optional[date] = None


class ConditionInspectionResponse(BaseModel):
    id: str
    ornament_id: str
    inspection_date: datetime
    inspector_user_id: str
    overall_condition: str
    has_damage: bool
    damage_description: Optional[str]
    damage_photos: Optional[List[str]]
    has_repair: bool
    repair_description: Optional[str]
    has_missing_parts: bool
    missing_parts_description: Optional[str]
    stone_condition: Optional[str]
    clasp_condition: Optional[str]
    polish_level: Optional[str]
    weight_verified: bool
    weight_variance_grams: Optional[float]
    condition_notes: Optional[str]
    next_inspection_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# Tags
class TagCreate(BaseModel):
    ornament_id: str
    tag_category: str = Field(..., description="occasion, style, region, era, metal_work")
    tag_value: str
    tag_confidence: Optional[float] = None
    tagged_by: str = Field(default="user", description="user, ai, system")


class TagResponse(BaseModel):
    id: str
    ornament_id: str
    tag_category: str
    tag_value: str
    tag_confidence: Optional[float]
    tagged_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# Comparison (Fraud Detection)
class ComparisonCreate(BaseModel):
    ornament_id_1: str
    ornament_id_2: str
    comparison_type: str = Field(..., description="duplicate_detection, similar_pattern, same_customer")
    similarity_score: Optional[float] = None
    matching_attributes: Optional[Dict[str, Any]] = None
    compared_by: str = Field(default="system")


class ComparisonResponse(BaseModel):
    id: str
    ornament_id_1: str
    ornament_id_2: str
    comparison_type: str
    similarity_score: Optional[float]
    matching_attributes: Optional[Dict[str, Any]]
    compared_by: str
    comparison_date: datetime
    is_flagged: bool
    investigation_status: Optional[str]
    investigation_notes: Optional[str]
    resolved_by_user_id: Optional[str]
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# Certificates
class CertificateCreate(BaseModel):
    ornament_id: str
    certificate_type: str = Field(..., description="hallmark, bis, purity_test, valuation, insurance")
    certificate_number: str
    issuing_authority: str
    issued_date: date
    expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    certificate_hash: Optional[str] = None
    certificate_data: Optional[Dict[str, Any]] = None


class CertificateVerify(BaseModel):
    is_verified: bool
    verified_by_user_id: str
    verification_method: str = Field(..., description="manual, api, qr_scan, blockchain")


class CertificateResponse(BaseModel):
    id: str
    ornament_id: str
    certificate_type: str
    certificate_number: str
    issuing_authority: str
    issued_date: date
    expiry_date: Optional[date]
    certificate_url: Optional[str]
    certificate_hash: Optional[str]
    is_verified: bool
    verified_by_user_id: Optional[str]
    verified_at: Optional[datetime]
    verification_method: Optional[str]
    certificate_data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Insurance
class InsuranceCreate(BaseModel):
    ornament_id: str
    policy_number: str
    insurance_provider: str
    insured_value: float = Field(..., gt=0)
    premium_amount: Optional[float] = None
    policy_start_date: date
    policy_end_date: date
    coverage_type: Optional[str] = Field(None, description="comprehensive, theft, damage, loss")
    policy_document_url: Optional[str] = None


class InsuranceUpdate(BaseModel):
    insured_value: Optional[float] = None
    premium_amount: Optional[float] = None
    policy_end_date: Optional[date] = None
    is_active: Optional[bool] = None
    claim_history: Optional[List[Dict[str, Any]]] = None


class InsuranceResponse(BaseModel):
    id: str
    ornament_id: str
    policy_number: str
    insurance_provider: str
    insured_value: float
    premium_amount: Optional[float]
    policy_start_date: date
    policy_end_date: date
    coverage_type: Optional[str]
    is_active: bool
    policy_document_url: Optional[str]
    claim_history: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Ornament Groups
class GroupCreate(BaseModel):
    group_name: str
    group_type: Optional[str] = Field(None, description="set, collection, inherited, gifted")
    description: Optional[str] = None
    customer_id: Optional[str] = None


class GroupAddOrnament(BaseModel):
    ornament_id: str
    sequence_number: Optional[int] = None


class GroupResponse(BaseModel):
    id: str
    group_name: str
    group_type: Optional[str]
    description: Optional[str]
    total_ornaments: int
    total_weight_grams: Optional[float]
    total_value: Optional[float]
    customer_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Complete Ornament Profile
class OrnamentCompleteProfile(BaseModel):
    """Complete ornament information with all related data"""
    ornament: Dict[str, Any]  # Base ornament data
    photos: List[OrnamentPhotoResponse]
    stones: List[StoneResponse]
    status_history: List[StatusHistoryResponse]
    movements: List[MovementResponse]
    conditions: List[ConditionInspectionResponse]
    tags: List[TagResponse]
    certificates: List[CertificateResponse]
    insurance: Optional[InsuranceResponse]
    groups: List[GroupResponse]
    
    # Calculated fields
    total_photos: int
    total_stones: int
    total_stone_weight: float
    current_condition: Optional[str]
    last_movement: Optional[MovementResponse]
    days_in_vault: Optional[int]
