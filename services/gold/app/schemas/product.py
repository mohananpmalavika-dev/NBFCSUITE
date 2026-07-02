"""
Gold Product Configuration Schemas
Phase 1: Product Engine
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Interest Configuration
class InterestConfig(BaseModel):
    interest_type: str = Field(..., description="flat, reducing, simple")
    rate_type: str = Field(..., description="fixed, floating, tiered")
    base_rate: float = Field(..., gt=0, description="Annual interest rate percentage")
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    penal_interest: float = Field(default=0, ge=0)
    compounding_frequency: Optional[str] = Field(None, description="daily, monthly, quarterly, none")

    class Config:
        from_attributes = True


class InterestConfigResponse(InterestConfig):
    id: str
    product_id: str
    created_at: datetime


# Tenure Configuration
class TenureConfig(BaseModel):
    min_tenure_months: int = Field(..., gt=0)
    max_tenure_months: int = Field(..., gt=0)
    default_tenure_months: int = Field(..., gt=0)
    tenure_unit: str = Field(default="months", description="days, months, years")
    renewal_allowed: bool = True
    max_renewals: Optional[int] = None
    auto_renewal: bool = False

    class Config:
        from_attributes = True


class TenureConfigResponse(TenureConfig):
    id: str
    product_id: str
    created_at: datetime


# Limits Configuration
class LimitsConfig(BaseModel):
    min_loan_amount: float = Field(..., gt=0)
    max_loan_amount: float = Field(..., gt=0)
    ltv_percent: float = Field(default=75.0, gt=0, le=90)
    min_ltv: Optional[float] = Field(None, ge=0, le=90)
    max_ltv: Optional[float] = Field(None, ge=0, le=90)
    min_gold_weight_grams: float = Field(default=5.0, gt=0)
    max_gold_weight_grams: Optional[float] = None
    purity_threshold_karat: float = Field(default=18.0, gt=0, le=24)

    class Config:
        from_attributes = True


class LimitsConfigResponse(LimitsConfig):
    id: str
    product_id: str
    created_at: datetime


# Charges Configuration
class ChargeConfig(BaseModel):
    charge_code: str = Field(..., description="processing, appraisal, vault, insurance, documentation")
    charge_name: str
    charge_type: str = Field(..., description="flat, percentage, slab")
    charge_amount: Optional[float] = None
    charge_percentage: Optional[float] = None
    min_charge: Optional[float] = None
    max_charge: Optional[float] = None
    charge_frequency: Optional[str] = Field(None, description="one_time, monthly, quarterly, yearly")
    is_mandatory: bool = True
    is_refundable: bool = False
    tax_applicable: bool = True

    class Config:
        from_attributes = True


class ChargeConfigResponse(ChargeConfig):
    id: str
    product_id: str
    created_at: datetime


# Document Configuration
class DocumentConfig(BaseModel):
    document_type: str
    document_name: str
    is_mandatory: bool = True
    verification_required: bool = True
    document_category: Optional[str] = Field(None, description="kyc, income, property, others")

    class Config:
        from_attributes = True


class DocumentConfigResponse(DocumentConfig):
    id: str
    product_id: str
    created_at: datetime


# Eligibility Rules
class EligibilityRule(BaseModel):
    rule_type: str = Field(..., description="customer_segment, age, income, cibil, branch_type, geography")
    rule_name: str
    rule_operator: str = Field(..., description="eq, ne, gt, lt, gte, lte, in, not_in, contains")
    rule_value: Dict[str, Any]
    is_mandatory: bool = True
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class EligibilityRuleResponse(EligibilityRule):
    id: str
    product_id: str
    created_at: datetime


# Workflow Configuration
class WorkflowStage(BaseModel):
    stage_order: int = Field(..., ge=1)
    stage_name: str
    stage_type: str = Field(..., description="system, user, role, ai")
    approver_role: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    sla_hours: Optional[int] = None
    is_parallel: bool = False
    auto_approve_conditions: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class WorkflowStageResponse(WorkflowStage):
    id: str
    product_id: str
    created_at: datetime


# Channel Configuration
class ChannelConfig(BaseModel):
    channel_type: str = Field(..., description="branch, mobile, web, partner, dsa")
    is_enabled: bool = True
    requires_verification: bool = True
    instant_approval_limit: Optional[float] = None

    class Config:
        from_attributes = True


class ChannelConfigResponse(ChannelConfig):
    id: str
    product_id: str
    created_at: datetime


# Tax Configuration
class TaxConfig(BaseModel):
    tax_type: str = Field(..., description="gst, service_tax, stamp_duty")
    tax_name: str
    tax_percentage: float = Field(..., ge=0)
    tax_category: Optional[str] = Field(None, description="interest, charges, both")
    hsn_sac_code: Optional[str] = None
    is_active: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    class Config:
        from_attributes = True


class TaxConfigResponse(TaxConfig):
    id: str
    product_id: str
    created_at: datetime


# Main Product Schema
class GoldProductCreate(BaseModel):
    product_code: str = Field(..., min_length=3, max_length=40)
    product_name: str = Field(..., min_length=3, max_length=120)
    product_type: str = Field(..., description="jewel_loan, bullet_loan, od, sme, agri, digital, instant")
    description: Optional[str] = None
    is_active: bool = True
    display_order: int = 0
    
    # Embedded configurations (optional during creation)
    interest: Optional[InterestConfig] = None
    tenure: Optional[TenureConfig] = None
    limits: Optional[LimitsConfig] = None
    charges: Optional[List[ChargeConfig]] = None
    documents: Optional[List[DocumentConfig]] = None
    eligibility: Optional[List[EligibilityRule]] = None
    workflow: Optional[List[WorkflowStage]] = None
    channels: Optional[List[ChannelConfig]] = None
    taxes: Optional[List[TaxConfig]] = None


class GoldProductUpdate(BaseModel):
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class GoldProductResponse(BaseModel):
    id: str
    product_code: str
    product_name: str
    product_type: str
    description: Optional[str]
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    # Relationships
    interest: Optional[InterestConfigResponse] = None
    tenure: Optional[TenureConfigResponse] = None
    limits: Optional[LimitsConfigResponse] = None
    charges: List[ChargeConfigResponse] = []
    documents: List[DocumentConfigResponse] = []
    eligibility: List[EligibilityRuleResponse] = []
    workflow: List[WorkflowStageResponse] = []
    channels: List[ChannelConfigResponse] = []
    taxes: List[TaxConfigResponse] = []

    class Config:
        from_attributes = True


class GoldProductSummary(BaseModel):
    """Lightweight product summary for listings"""
    id: str
    product_code: str
    product_name: str
    product_type: str
    is_active: bool
    base_rate: Optional[float] = None
    ltv_percent: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None

    class Config:
        from_attributes = True
