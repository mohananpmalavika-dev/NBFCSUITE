"""
Gold Appraisal Engine Schemas
Phase 3: Advanced Ornament Cataloging & Valuation
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Ornament Type Schemas
class OrnamentTypeResponse(BaseModel):
    id: str
    type_code: str
    type_name: str
    category: Optional[str]
    typical_stone_percentage: float
    description: Optional[str]
    is_active: bool
    display_order: int

    class Config:
        from_attributes = True


# Gold Market Rate Schemas
class MarketRateCreate(BaseModel):
    rate_date: date
    rate_source: str = Field(..., description="india_bullion, mcx, international, manual")
    purity_karat: float = Field(..., gt=0, le=24)
    rate_per_gram: float = Field(..., gt=0)
    rate_per_10gram: Optional[float] = None
    currency: str = Field(default="INR")
    city: Optional[str] = None
    branch_id: Optional[str] = None
    effective_from: datetime
    effective_to: Optional[datetime] = None
    rate_metadata: Optional[Dict[str, Any]] = None


class MarketRateResponse(BaseModel):
    id: str
    rate_date: date
    rate_source: str
    purity_karat: float
    rate_per_gram: float
    rate_per_10gram: Optional[float]
    currency: str
    city: Optional[str]
    branch_id: Optional[str]
    is_active: bool
    effective_from: datetime
    effective_to: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Appraisal Session Schemas
class AppraisalSessionCreate(BaseModel):
    application_id: str
    customer_id: str
    appraiser_user_id: Optional[str] = None
    gold_rate_id: Optional[str] = None
    ltv_percent: Optional[float] = None
    session_notes: Optional[str] = None


class AppraisalSessionUpdate(BaseModel):
    session_status: Optional[str] = None
    appraiser_user_id: Optional[str] = None
    gold_rate_id: Optional[str] = None
    ltv_percent: Optional[float] = None
    session_notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class AppraisalSessionResponse(BaseModel):
    id: str
    application_id: str
    session_number: str
    customer_id: str
    appraiser_user_id: Optional[str]
    session_status: str
    total_ornaments: int
    total_gross_weight: float
    total_net_weight: float
    total_appraised_value: float
    average_purity_karat: Optional[float]
    gold_rate_id: Optional[str]
    ltv_percent: Optional[float]
    eligible_loan_amount: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    verified_at: Optional[datetime]
    verified_by_user_id: Optional[str]
    session_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Enhanced Ornament Schemas
class OrnamentCreate(BaseModel):
    ornament_type: str  # For backward compatibility
    ornament_type_id: Optional[str] = None
    description: Optional[str] = None
    gross_weight_grams: float = Field(..., gt=0)
    stone_weight_grams: float = Field(default=0, ge=0)
    purity_karat: float = Field(default=22, gt=0, le=24)
    is_hallmarked: bool = False
    hallmark_id: Optional[str] = None
    hallmark_center: Optional[str] = None
    making_charges: Optional[float] = None
    wastage_grams: float = Field(default=0, ge=0)
    stone_details: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None


class OrnamentPhotoUpload(BaseModel):
    ornament_id: str
    photo_url: str
    photo_type: str = Field(default="general", description="general, hallmark, close_up, damage")


class OrnamentResponse(BaseModel):
    id: str
    application_id: str
    appraisal_session_id: Optional[str]
    ornament_type: str
    ornament_type_id: Optional[str]
    description: Optional[str]
    barcode: Optional[str]
    qr_code: Optional[str]
    photo_urls: Optional[List[str]]
    photo_count: int
    gross_weight_grams: float
    stone_weight_grams: float
    net_weight_grams: float
    purity_karat: float
    purity_percent: float
    is_hallmarked: bool
    hallmark_id: Optional[str]
    hallmark_center: Optional[str]
    making_charges: Optional[float]
    wastage_grams: float
    appraised_value: float
    stone_details: Optional[Dict[str, Any]]
    status: str
    appraised_by_user_id: Optional[str]
    verified_by_user_id: Optional[str]
    tags: Optional[Dict[str, Any]]
    cataloged_at: datetime

    class Config:
        from_attributes = True


# Purity Test Schemas
class PurityTestCreate(BaseModel):
    ornament_id: str
    test_number: int
    test_method: str = Field(..., description="touchstone, xrf, fire_assay, acid_test")
    tested_karat: float = Field(..., gt=0, le=24)
    test_equipment: Optional[str] = None
    test_location: Optional[str] = Field(None, description="Which part of ornament")
    tested_by_user_id: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    test_certificate_url: Optional[str] = None
    notes: Optional[str] = None


class PurityTestVerify(BaseModel):
    is_verified: bool
    verified_by_user_id: str
    notes: Optional[str] = None


class PurityTestResponse(BaseModel):
    id: str
    ornament_id: str
    test_number: int
    test_method: str
    tested_karat: float
    tested_purity_percent: float
    test_equipment: Optional[str]
    test_location: Optional[str]
    tested_by_user_id: Optional[str]
    tested_at: datetime
    test_results: Optional[Dict[str, Any]]
    test_certificate_url: Optional[str]
    is_verified: bool
    verified_by_user_id: Optional[str]
    verified_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Weight Verification Schemas
class WeightMeasurement(BaseModel):
    ornament_id: str
    measurement_type: str = Field(..., description="gross_weight, net_weight, stone_weight")
    measured_weight: float = Field(..., gt=0)
    weighing_scale_id: Optional[str] = None
    measured_by_user_id: str


class WeightVerificationSubmit(BaseModel):
    verified_weight: float = Field(..., gt=0)
    is_accepted: bool
    rejection_reason: Optional[str] = None


class WeightVerificationResponse(BaseModel):
    id: str
    ornament_id: str
    measurement_type: str
    measured_by_user_id: str
    measured_weight: float
    weighing_scale_id: Optional[str]
    measurement_timestamp: datetime
    verified_by_user_id: Optional[str]
    verified_weight: Optional[float]
    verification_timestamp: Optional[datetime]
    variance_grams: Optional[float]
    is_accepted: Optional[bool]
    rejection_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Valuation Schemas
class ValuationCreate(BaseModel):
    ornament_id: str
    valuation_type: str = Field(..., description="initial, periodic, pre_auction, release")
    gold_rate_per_gram: float = Field(..., gt=0)
    market_value: Optional[float] = None
    forced_sale_value: Optional[float] = None
    valued_by_user_id: Optional[str] = None
    valuation_notes: Optional[str] = None


class ValuationResponse(BaseModel):
    id: str
    ornament_id: str
    valuation_date: date
    valuation_type: str
    gold_rate_per_gram: float
    purity_percent: float
    net_weight_grams: float
    calculated_value: float
    market_value: Optional[float]
    forced_sale_value: Optional[float]
    valued_by_user_id: Optional[str]
    valuation_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Anomaly Schemas
class AnomalyCreate(BaseModel):
    appraisal_session_id: Optional[str] = None
    ornament_id: Optional[str] = None
    anomaly_type: str = Field(..., description="weight_mismatch, purity_variance, hallmark_fake, duplicate_barcode, suspicious_pattern")
    severity: str = Field(..., description="low, medium, high, critical")
    anomaly_description: str
    detected_by: str = Field(..., description="system, user, ai")
    detection_data: Optional[Dict[str, Any]] = None


class AnomalyResolve(BaseModel):
    status: str = Field(..., description="resolved, false_positive")
    resolution_notes: str
    resolved_by_user_id: str


class AnomalyResponse(BaseModel):
    id: str
    appraisal_session_id: Optional[str]
    ornament_id: Optional[str]
    anomaly_type: str
    severity: str
    anomaly_description: str
    detected_by: str
    detection_data: Optional[Dict[str, Any]]
    status: str
    resolution_notes: Optional[str]
    resolved_by_user_id: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Complete Appraisal Summary
class AppraisalSummary(BaseModel):
    """Complete appraisal summary for an application"""
    session: AppraisalSessionResponse
    ornaments: List[OrnamentResponse]
    purity_tests: List[PurityTestResponse]
    anomalies: List[AnomalyResponse]
    gold_rate: Optional[MarketRateResponse]
    total_stats: Dict[str, Any]


# Quick Appraisal (for instant loans)
class QuickAppraisal(BaseModel):
    """Simplified appraisal for instant gold loans"""
    customer_id: str
    ornament_type: str
    gross_weight_grams: float
    estimated_purity_karat: float = Field(default=22)
    photo_url: Optional[str] = None


class QuickAppraisalResult(BaseModel):
    estimated_value: float
    eligible_loan_amount: float
    gold_rate_used: float
    ltv_applied: float
    instant_approval: bool
    approval_limit: float
    requires_full_appraisal: bool
