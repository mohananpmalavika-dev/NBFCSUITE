"""
Gold Customer Journey Schemas
Phase 2: Customer Journey & CIF Integration
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Customer Session Schemas
class CustomerSessionCreate(BaseModel):
    customer_id: Optional[str] = None
    branch_id: Optional[str] = None
    channel: str = Field(default="branch", description="branch, mobile, web, partner")
    session_type: str = Field(default="new_loan", description="new_loan, renewal, release, inquiry")
    initiated_by_user_id: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None


class CustomerSessionUpdate(BaseModel):
    customer_id: Optional[str] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    abandoned_at: Optional[datetime] = None
    abandonment_reason: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None


class CustomerSessionResponse(BaseModel):
    id: str
    session_number: str
    customer_id: Optional[str]
    branch_id: Optional[str]
    channel: str
    session_type: str
    status: str
    initiated_by_user_id: Optional[str]
    initiated_at: datetime
    completed_at: Optional[datetime]
    abandoned_at: Optional[datetime]
    abandonment_reason: Optional[str]
    session_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Customer Search Schemas
class CustomerSearchRequest(BaseModel):
    session_id: str
    phone: Optional[str] = None
    aadhar: Optional[str] = None
    pan: Optional[str] = None
    customer_id: Optional[str] = None
    name: Optional[str] = None
    searched_by_user_id: Optional[str] = None


class CustomerSearchLogResponse(BaseModel):
    id: str
    session_id: str
    search_criteria: Dict[str, Any]
    results_found: int
    selected_customer_id: Optional[str]
    searched_at: datetime
    searched_by_user_id: Optional[str]

    class Config:
        from_attributes = True


# Product Selection Schemas
class ProductSelectionCreate(BaseModel):
    session_id: str
    product_id: str
    customer_id: Optional[str] = None
    requested_amount: Optional[float] = None
    estimated_gold_weight: Optional[float] = None
    selection_source: Optional[str] = Field(None, description="customer_choice, ai_recommendation, officer_suggestion")
    recommendation_score: Optional[float] = None


class ProductSelectionResponse(BaseModel):
    id: str
    session_id: str
    product_id: str
    customer_id: Optional[str]
    requested_amount: Optional[float]
    estimated_gold_weight: Optional[float]
    selected_at: datetime
    selection_source: Optional[str]
    recommendation_score: Optional[float]
    is_converted: bool
    application_id: Optional[str]

    class Config:
        from_attributes = True


# Eligibility Check Schemas
class EligibilityCheckCreate(BaseModel):
    session_id: str
    customer_id: str
    product_id: str
    check_type: str = Field(..., description="age, income, cibil, existing_loans, geographic, segment")
    rule_id: Optional[str] = None
    is_passed: bool
    check_value: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None


class EligibilityCheckResponse(BaseModel):
    id: str
    session_id: str
    customer_id: str
    product_id: str
    check_type: str
    rule_id: Optional[str]
    is_passed: bool
    check_value: Optional[Dict[str, Any]]
    failure_reason: Optional[str]
    checked_at: datetime

    class Config:
        from_attributes = True


class EligibilityResult(BaseModel):
    """Aggregated eligibility result for a product"""
    product_id: str
    product_name: str
    is_eligible: bool
    passed_checks: int
    total_checks: int
    failed_checks: List[EligibilityCheckResponse] = []
    can_proceed: bool


# KYC Verification Schemas
class KYCVerificationCreate(BaseModel):
    session_id: str
    customer_id: str
    document_type: str = Field(..., description="aadhar, pan, address_proof, photo")
    document_number: Optional[str] = None
    verification_method: Optional[str] = Field(None, description="manual, aadhaar_otp, digilocker, api, offline")
    verification_status: str = Field(..., description="pending, verified, failed, expired")
    verified_by_user_id: Optional[str] = None
    verification_response: Optional[Dict[str, Any]] = None
    expiry_date: Optional[date] = None


class KYCVerificationResponse(BaseModel):
    id: str
    session_id: str
    customer_id: str
    document_type: str
    document_number: Optional[str]
    verification_method: Optional[str]
    verification_status: str
    verified_by_user_id: Optional[str]
    verified_at: Optional[datetime]
    verification_response: Optional[Dict[str, Any]]
    expiry_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# Journey Step Schemas
class JourneyStepCreate(BaseModel):
    session_id: str
    step_number: int
    step_name: str = Field(..., description="customer_search, cif_creation, kyc, product_selection, eligibility_check, application_creation")
    step_status: str = Field(..., description="started, completed, failed, skipped")
    step_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JourneyStepUpdate(BaseModel):
    step_status: str
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    step_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class JourneyStepResponse(BaseModel):
    id: str
    session_id: str
    step_number: int
    step_name: str
    step_status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    step_data: Optional[Dict[str, Any]]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# Customer Interaction Schemas
class CustomerInteractionCreate(BaseModel):
    session_id: str
    customer_id: Optional[str] = None
    interaction_type: str = Field(..., description="inquiry, objection, documentation, negotiation, feedback")
    interaction_category: Optional[str] = Field(None, description="product_query, rate_negotiation, tenure_discussion")
    notes: str
    officer_user_id: Optional[str] = None
    sentiment: Optional[str] = Field(None, description="positive, neutral, negative")
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None


class CustomerInteractionResponse(BaseModel):
    id: str
    session_id: str
    customer_id: Optional[str]
    interaction_type: str
    interaction_category: Optional[str]
    notes: str
    officer_user_id: Optional[str]
    interaction_at: datetime
    sentiment: Optional[str]
    follow_up_required: bool
    follow_up_date: Optional[date]

    class Config:
        from_attributes = True


# Complete Journey Response
class CompleteJourneyResponse(BaseModel):
    """Complete journey with all related data"""
    session: CustomerSessionResponse
    search_logs: List[CustomerSearchLogResponse] = []
    product_selections: List[ProductSelectionResponse] = []
    eligibility_checks: List[EligibilityCheckResponse] = []
    kyc_verifications: List[KYCVerificationResponse] = []
    journey_steps: List[JourneyStepResponse] = []
    interactions: List[CustomerInteractionResponse] = []
    customer_data: Optional[Dict[str, Any]] = None  # From customer service


# Customer Search Result (from customer service)
class CustomerSearchResult(BaseModel):
    customer_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    pan: Optional[str]
    aadhar_masked: Optional[str]
    customer_segment: Optional[str]
    kyc_status: Optional[str]
    existing_gold_loans: int = 0
    total_outstanding: float = 0


# Product Recommendation
class ProductRecommendation(BaseModel):
    product_id: str
    product_code: str
    product_name: str
    recommendation_score: float
    recommendation_reason: str
    suggested_amount: Optional[float] = None
    is_eligible: bool
