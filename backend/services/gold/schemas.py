"""
Gold Loan Schemas
Pydantic models for gold loan operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================
# Gold Loan Product Schemas
# ============================================

class GoldLoanProductBase(BaseModel):
    product_code: str = Field(..., description="Product code")
    product_name: str = Field(..., description="Product name")
    description: Optional[str] = None
    interest_rate_min: Decimal = Field(..., ge=0, le=100)
    interest_rate_max: Decimal = Field(..., ge=0, le=100)
    default_interest_rate: Decimal = Field(..., ge=0, le=100)
    ltv_ratio: Decimal = Field(..., ge=0, le=100, description="Loan-to-Value ratio %")
    max_ltv_ratio: Decimal = Field(default=75.00, ge=0, le=100)
    min_loan_amount: Decimal = Field(..., gt=0)
    max_loan_amount: Decimal = Field(..., gt=0)
    min_tenure_months: int = Field(..., ge=1)
    max_tenure_months: int = Field(..., ge=1)
    default_tenure_months: int = Field(..., ge=1)
    processing_fee_percentage: Optional[Decimal] = Field(default=0.00, ge=0)
    processing_fee_flat: Optional[Decimal] = Field(default=0.00, ge=0)
    valuation_charges: Optional[Decimal] = Field(default=0.00, ge=0)
    documentation_charges: Optional[Decimal] = Field(default=0.00, ge=0)
    storage_charges_monthly: Optional[Decimal] = Field(default=0.00, ge=0)
    penal_interest_rate: Optional[Decimal] = Field(default=2.00, ge=0)
    repayment_frequency: str = Field(default="Monthly")
    partial_release_allowed: bool = True
    top_up_allowed: bool = True
    is_active: bool = True


class GoldLoanProductCreate(GoldLoanProductBase):
    pass


class GoldLoanProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    interest_rate_min: Optional[Decimal] = None
    interest_rate_max: Optional[Decimal] = None
    default_interest_rate: Optional[Decimal] = None
    ltv_ratio: Optional[Decimal] = None
    is_active: Optional[bool] = None


class GoldLoanProductResponse(GoldLoanProductBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Gold Ornament Schemas
# ============================================

class GoldOrnamentBase(BaseModel):
    ornament_type: str = Field(..., description="Type of ornament (Ring, Chain, Bangle, etc.)")
    ornament_description: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    purity_karat: int = Field(..., description="Gold purity in karats (18K, 22K, 24K)")
    purity_percentage: Decimal = Field(..., ge=0, le=100, description="Actual purity percentage")
    gross_weight_grams: Decimal = Field(..., gt=0, description="Total weight including stones")
    stone_weight_grams: Decimal = Field(default=0.000, ge=0, description="Weight of stones")
    net_weight_grams: Decimal = Field(..., gt=0, description="Pure gold weight")
    gold_rate_per_gram: Decimal = Field(..., gt=0, description="Gold rate per gram")
    market_value: Decimal = Field(..., gt=0, description="Market value")
    appraised_value: Decimal = Field(..., gt=0, description="Final appraised value")
    hallmark_available: bool = False
    hallmark_number: Optional[str] = None
    photo_url: Optional[str] = None
    remarks: Optional[str] = None


class GoldOrnamentCreate(GoldOrnamentBase):
    gold_loan_id: str


class GoldOrnamentUpdate(BaseModel):
    ornament_description: Optional[str] = None
    remarks: Optional[str] = None
    status: Optional[str] = None


class GoldOrnamentResponse(GoldOrnamentBase):
    id: str
    gold_loan_id: str
    item_number: int
    status: str
    released_weight_grams: Decimal
    remaining_weight_grams: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Gold Loan Account Schemas
# ============================================

class GoldLoanAccountCreate(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    product_id: str = Field(..., description="Gold loan product ID")
    loan_amount: Decimal = Field(..., gt=0, description="Requested loan amount")
    tenure_months: int = Field(..., ge=1, description="Loan tenure in months")
    repayment_frequency: str = Field(default="Monthly", description="Repayment frequency")
    ornaments: List[GoldOrnamentBase] = Field(..., min_items=1, description="List of gold ornaments")
    branch_id: Optional[str] = None
    remarks: Optional[str] = None

    @validator('repayment_frequency')
    def validate_frequency(cls, v):
        allowed = ['Monthly', 'Quarterly', 'Bullet']
        if v not in allowed:
            raise ValueError(f'Repayment frequency must be one of: {", ".join(allowed)}')
        return v


class GoldLoanAccountResponse(BaseModel):
    id: str
    loan_account_number: str
    customer_id: str
    product_id: str
    application_id: Optional[str]
    application_date: datetime
    
    # Loan details
    loan_amount: Decimal
    sanctioned_amount: Decimal
    disbursed_amount: Decimal
    
    # Gold details
    total_gold_weight_grams: Decimal
    total_gold_value: Decimal
    average_gold_rate: Decimal
    ltv_ratio: Decimal
    
    # Interest details
    interest_rate: Decimal
    penal_interest_rate: Decimal
    
    # Tenure
    tenure_months: int
    start_date: datetime
    maturity_date: datetime
    repayment_frequency: str
    emi_amount: Optional[Decimal]
    
    # Charges
    processing_fee: Decimal
    valuation_charges: Decimal
    documentation_charges: Decimal
    insurance_charges: Decimal
    
    # Outstanding
    principal_outstanding: Decimal
    interest_outstanding: Decimal
    penal_interest_outstanding: Decimal
    total_outstanding: Decimal
    
    # Status
    status: str
    days_past_due: int
    overdue_amount: Decimal
    is_npa: bool
    
    # Dates
    approval_date: Optional[datetime]
    disbursement_date: Optional[datetime]
    closure_date: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoldLoanAccountDetail(GoldLoanAccountResponse):
    """Extended response with ornament details"""
    ornaments: List[GoldOrnamentResponse] = []


# ============================================
# Gold Loan Transaction Schemas
# ============================================

class GoldLoanTransactionCreate(BaseModel):
    gold_loan_id: str
    transaction_type: str = Field(..., description="Transaction type")
    amount: Decimal = Field(..., gt=0)
    principal_amount: Decimal = Field(default=0.00, ge=0)
    interest_amount: Decimal = Field(default=0.00, ge=0)
    penal_interest_amount: Decimal = Field(default=0.00, ge=0)
    charges_amount: Decimal = Field(default=0.00, ge=0)
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    bank_name: Optional[str] = None
    cheque_number: Optional[str] = None
    transaction_id: Optional[str] = None
    remarks: Optional[str] = None

    @validator('transaction_type')
    def validate_transaction_type(cls, v):
        allowed = ['Disbursement', 'Payment', 'Interest', 'Charges', 'Penalty', 'Reversal', 'Release', 'TopUp']
        if v not in allowed:
            raise ValueError(f'Transaction type must be one of: {", ".join(allowed)}')
        return v


class GoldLoanTransactionResponse(BaseModel):
    id: str
    transaction_number: str
    gold_loan_id: str
    transaction_date: datetime
    transaction_type: str
    amount: Decimal
    principal_amount: Decimal
    interest_amount: Decimal
    penal_interest_amount: Decimal
    charges_amount: Decimal
    payment_mode: Optional[str]
    payment_reference: Optional[str]
    principal_balance: Decimal
    interest_balance: Decimal
    total_balance: Decimal
    status: str
    created_by: str
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Gold Release Schemas
# ============================================

class GoldReleaseRequestCreate(BaseModel):
    gold_loan_id: str
    release_type: str = Field(..., description="Release type: Partial, Full, Closure")
    ornament_ids: List[str] = Field(..., min_items=1, description="IDs of ornaments to release")
    payment_amount: Decimal = Field(default=0.00, ge=0, description="Payment amount for partial release")
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    remarks: Optional[str] = None

    @validator('release_type')
    def validate_release_type(cls, v):
        allowed = ['Partial', 'Full', 'Closure']
        if v not in allowed:
            raise ValueError(f'Release type must be one of: {", ".join(allowed)}')
        return v


class GoldReleaseRequestResponse(BaseModel):
    id: str
    request_number: str
    gold_loan_id: str
    customer_id: str
    release_type: str
    total_release_weight_grams: Decimal
    total_release_value: Decimal
    payment_amount: Decimal
    new_loan_amount: Optional[Decimal]
    new_ltv_ratio: Optional[Decimal]
    request_date: datetime
    requested_by: str
    approval_status: str
    approved_by: Optional[str]
    approval_date: Optional[datetime]
    approval_remarks: Optional[str]
    status: str
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Gold Auction Schemas
# ============================================

class GoldAuctionCreate(BaseModel):
    gold_loan_id: str
    auction_date: datetime
    reserve_price: Decimal = Field(..., gt=0)
    auction_venue: Optional[str] = None
    remarks: Optional[str] = None


class GoldAuctionResponse(BaseModel):
    id: str
    auction_number: str
    gold_loan_id: str
    customer_id: str
    total_gold_weight_grams: Decimal
    total_gold_value: Decimal
    total_outstanding: Decimal
    reserve_price: Decimal
    auction_date: datetime
    notice_sent_date: Optional[datetime]
    auction_status: str
    highest_bid_amount: Optional[Decimal]
    winning_bidder_name: Optional[str]
    sale_amount: Optional[Decimal]
    sale_date: Optional[datetime]
    refund_amount: Decimal
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Dashboard & Statistics Schemas
# ============================================

class GoldLoanStatistics(BaseModel):
    total_loans: int
    active_loans: int
    total_disbursed: Decimal
    total_outstanding: Decimal
    total_gold_weight_kg: Decimal
    average_ltv_ratio: Decimal
    npa_count: int
    npa_amount: Decimal
    overdue_count: int
    overdue_amount: Decimal


class GoldPriceUpdate(BaseModel):
    gold_rate_24k: Decimal = Field(..., gt=0, description="24K gold rate per gram")
    gold_rate_22k: Decimal = Field(..., gt=0, description="22K gold rate per gram")
    gold_rate_18k: Decimal = Field(..., gt=0, description="18K gold rate per gram")
    effective_date: datetime
    source: str = Field(default="Manual")


# ============================================
# List & Filter Schemas
# ============================================

class GoldLoanListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)
    status: Optional[str] = None
    customer_id: Optional[str] = None
    branch_id: Optional[str] = None
    is_npa: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    search: Optional[str] = None


# ============================================
# Gold Rate Schemas
# ============================================

class GoldRateCreateRequest(BaseModel):
    rate_date: Optional[datetime] = None
    gold_rate_24k: Decimal = Field(..., gt=0, description="24K gold rate per gram")
    gold_rate_22k: Decimal = Field(..., gt=0, description="22K gold rate per gram")
    gold_rate_18k: Decimal = Field(..., gt=0, description="18K gold rate per gram")
    silver_rate: Optional[Decimal] = Field(None, ge=0, description="Silver rate per gram")
    source: Optional[str] = Field(default="Manual", description="Rate source")
    source_reference: Optional[str] = None
    market_name: Optional[str] = None
    currency: Optional[str] = Field(default="INR")
    is_active: bool = True
    is_current: bool = False
    applied_from: Optional[datetime] = None
    applied_to: Optional[datetime] = None
    remarks: Optional[str] = None


class GoldRateUpdateRequest(BaseModel):
    gold_rate_24k: Optional[Decimal] = Field(None, gt=0)
    gold_rate_22k: Optional[Decimal] = Field(None, gt=0)
    gold_rate_18k: Optional[Decimal] = Field(None, gt=0)
    silver_rate: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_current: Optional[bool] = None
    remarks: Optional[str] = None


class GoldRateHistoryResponse(BaseModel):
    id: str
    rate_date: datetime
    gold_rate_24k: Decimal
    gold_rate_22k: Decimal
    gold_rate_18k: Decimal
    silver_rate: Optional[Decimal]
    source: str
    source_reference: Optional[str]
    market_name: Optional[str]
    currency: str
    is_active: bool
    is_current: bool
    fetched_at: Optional[datetime]
    applied_from: Optional[datetime]
    applied_to: Optional[datetime]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CurrentGoldRatesResponse(BaseModel):
    gold_rate_24k: Decimal
    gold_rate_22k: Decimal
    gold_rate_18k: Decimal
    silver_rate: Optional[Decimal]
    rate_date: datetime
    source: str
    market_name: Optional[str]
    last_updated: datetime


# ============================================
# Vault Location Schemas
# ============================================

class VaultLocationCreateRequest(BaseModel):
    vault_code: str = Field(..., description="Unique vault code")
    vault_name: str = Field(..., description="Vault name")
    branch_id: str
    location_type: str = Field(..., description="Main Vault, Branch Vault, Safe, Locker")
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    rack_number: Optional[str] = None
    shelf_number: Optional[str] = None
    max_capacity_items: Optional[int] = Field(None, ge=0)
    max_capacity_weight_kg: Optional[Decimal] = Field(None, ge=0)
    security_level: Optional[str] = Field(default="High")
    access_control: Optional[str] = None
    surveillance: bool = True
    insured: bool = True
    insurance_value: Optional[Decimal] = Field(None, ge=0)
    custodian_name: Optional[str] = None
    custodian_contact: Optional[str] = None
    remarks: Optional[str] = None


class VaultLocationUpdateRequest(BaseModel):
    vault_name: Optional[str] = None
    location_type: Optional[str] = None
    max_capacity_items: Optional[int] = None
    max_capacity_weight_kg: Optional[Decimal] = None
    status: Optional[str] = None
    custodian_name: Optional[str] = None
    custodian_contact: Optional[str] = None
    remarks: Optional[str] = None


class VaultLocationResponse(BaseModel):
    id: str
    vault_code: str
    vault_name: str
    branch_id: str
    location_type: str
    building: Optional[str]
    floor: Optional[str]
    room: Optional[str]
    rack_number: Optional[str]
    shelf_number: Optional[str]
    max_capacity_items: Optional[int]
    max_capacity_weight_kg: Optional[Decimal]
    current_items_count: int
    current_weight_kg: Decimal
    security_level: str
    access_control: Optional[str]
    surveillance: bool
    insured: bool
    insurance_value: Optional[Decimal]
    status: str
    is_active: bool
    custodian_name: Optional[str]
    custodian_contact: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Vault Inventory Schemas
# ============================================

class VaultInventoryCreateRequest(BaseModel):
    vault_location_id: str
    gold_loan_id: str
    customer_id: str
    ornament_id: str
    package_number: Optional[str] = None
    seal_number: Optional[str] = None
    barcode: Optional[str] = None
    rfid_tag: Optional[str] = None
    rack_position: Optional[str] = None
    shelf_position: Optional[str] = None
    slot_position: Optional[str] = None
    verified_by: Optional[str] = None
    photo_url: Optional[str] = None
    remarks: Optional[str] = None


class VaultInventoryResponse(BaseModel):
    id: str
    inventory_number: str
    vault_location_id: str
    gold_loan_id: str
    customer_id: str
    ornament_id: str
    package_number: Optional[str]
    seal_number: Optional[str]
    barcode: Optional[str]
    rfid_tag: Optional[str]
    rack_position: Optional[str]
    shelf_position: Optional[str]
    slot_position: Optional[str]
    item_description: str
    total_weight_grams: Decimal
    total_value: Decimal
    check_in_date: datetime
    check_in_by: str
    check_in_verified_by: Optional[str]
    check_out_date: Optional[datetime]
    check_out_by: Optional[str]
    status: str
    last_audit_date: Optional[datetime]
    audit_status: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Vault Transfer Schemas
# ============================================

class VaultTransferCreateRequest(BaseModel):
    from_vault_id: str
    to_vault_id: str
    inventory_ids: List[str] = Field(..., min_items=1)
    transfer_date: Optional[datetime] = None
    seal_number: Optional[str] = None
    transport_mode: Optional[str] = Field(None, description="Courier, Personal, Security Van")
    remarks: Optional[str] = None


class VaultTransferResponse(BaseModel):
    id: str
    transfer_number: str
    transfer_date: datetime
    from_vault_id: str
    to_vault_id: str
    total_items_count: int
    total_weight_grams: Decimal
    total_value: Decimal
    initiated_by: str
    approved_by: Optional[str]
    dispatched_date: Optional[datetime]
    dispatched_by: Optional[str]
    received_date: Optional[datetime]
    received_by: Optional[str]
    verified_by: Optional[str]
    verification_status: Optional[str]
    status: str
    seal_number: Optional[str]
    transport_mode: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Purity Test Schemas
# ============================================

class PurityTestCreateRequest(BaseModel):
    gold_loan_id: str
    ornament_id: str
    test_method: str = Field(..., description="XRF, Touchstone, Fire Assay, Acid Test, Electronic Tester")
    test_date: Optional[datetime] = None
    claimed_purity_karat: int = Field(..., ge=1, le=24)
    claimed_purity_percentage: Decimal = Field(..., ge=0, le=100)
    tested_purity_karat: int = Field(..., ge=1, le=24)
    tested_purity_percentage: Decimal = Field(..., ge=0, le=100)
    equipment_id: Optional[str] = None
    equipment_name: Optional[str] = None
    equipment_calibration_date: Optional[datetime] = None
    sample_weight: Optional[Decimal] = Field(None, ge=0)
    test_temperature: Optional[Decimal] = None
    tester_name: str
    tester_license: Optional[str] = None
    verified_by: Optional[str] = None
    test_photo_url: Optional[str] = None
    remarks: Optional[str] = None
    auto_update_ornament: bool = False

    @validator('test_method')
    def validate_test_method(cls, v):
        allowed = ['XRF', 'Touchstone', 'Fire Assay', 'Acid Test', 'Electronic Tester']
        if v not in allowed:
            raise ValueError(f'Test method must be one of: {", ".join(allowed)}')
        return v


class PurityTestUpdateRequest(BaseModel):
    tested_purity_karat: Optional[int] = Field(None, ge=1, le=24)
    tested_purity_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    action_taken: Optional[str] = Field(None, description="Accepted, Rejected, Value Adjusted, Re-test Required")
    adjusted_value: Optional[Decimal] = Field(None, ge=0)
    certificate_number: Optional[str] = None
    certificate_url: Optional[str] = None
    report_url: Optional[str] = None
    remarks: Optional[str] = None


class PurityTestResponse(BaseModel):
    id: str
    test_number: str
    test_date: datetime
    gold_loan_id: str
    ornament_id: str
    customer_id: str
    test_method: str
    claimed_purity_karat: int
    claimed_purity_percentage: Decimal
    tested_purity_karat: int
    tested_purity_percentage: Decimal
    purity_variance: Decimal
    equipment_id: Optional[str]
    equipment_name: Optional[str]
    test_result: str
    tested_by: str
    tester_name: str
    tester_license: Optional[str]
    verified_by: Optional[str]
    certificate_number: Optional[str]
    certificate_url: Optional[str]
    certificate_issued_date: Optional[datetime]
    certificate_valid_until: Optional[datetime]
    action_taken: Optional[str]
    adjusted_value: Optional[Decimal]
    test_photo_url: Optional[str]
    report_url: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Appraisal Report Schemas
# ============================================

class AppraisalReportCreateRequest(BaseModel):
    appraisal_type: str = Field(..., description="Initial, Re-appraisal, Top-up, Audit, Dispute Resolution")
    appraisal_date: Optional[datetime] = None
    gold_loan_id: Optional[str] = None
    ornament_id: Optional[str] = None
    customer_id: str
    ornament_type: str
    ornament_description: str
    quantity: int = Field(default=1, ge=1)
    claimed_karat: int = Field(..., ge=1, le=24)
    verified_karat: int = Field(..., ge=1, le=24)
    purity_percentage: Decimal = Field(..., ge=0, le=100)
    gross_weight_grams: Decimal = Field(..., gt=0)
    stone_weight_grams: Decimal = Field(default=0.000, ge=0)
    other_deductions_grams: Decimal = Field(default=0.000, ge=0)
    hallmark_present: bool = False
    hallmark_number: Optional[str] = None
    hallmark_center: Optional[str] = None
    manufacturer_mark: Optional[str] = None
    condition: str = Field(..., description="Excellent, Good, Fair, Poor, Damaged")
    wear_and_tear: Optional[str] = None
    defects: Optional[str] = None
    condition_adjustment_percentage: Decimal = Field(default=0.00)
    market_adjustment_percentage: Decimal = Field(default=0.00)
    comparable_items: Optional[str] = None
    market_reference: Optional[str] = None
    appraiser_name: str
    appraiser_license: Optional[str] = None
    appraiser_experience_years: Optional[int] = Field(None, ge=0)
    photo_urls: Optional[List[str]] = None
    video_url: Optional[str] = None
    previous_appraisal_id: Optional[str] = None
    remarks: Optional[str] = None

    @validator('appraisal_type')
    def validate_appraisal_type(cls, v):
        allowed = ['Initial', 'Re-appraisal', 'Top-up', 'Audit', 'Dispute Resolution']
        if v not in allowed:
            raise ValueError(f'Appraisal type must be one of: {", ".join(allowed)}')
        return v

    @validator('condition')
    def validate_condition(cls, v):
        allowed = ['Excellent', 'Good', 'Fair', 'Poor', 'Damaged']
        if v not in allowed:
            raise ValueError(f'Condition must be one of: {", ".join(allowed)}')
        return v


class AppraisalReportUpdateRequest(BaseModel):
    verified_karat: Optional[int] = Field(None, ge=1, le=24)
    purity_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    gross_weight_grams: Optional[Decimal] = Field(None, gt=0)
    stone_weight_grams: Optional[Decimal] = Field(None, ge=0)
    other_deductions_grams: Optional[Decimal] = Field(None, ge=0)
    condition: Optional[str] = None
    condition_adjustment_percentage: Optional[Decimal] = None
    market_adjustment_percentage: Optional[Decimal] = None
    appraised_value: Optional[Decimal] = Field(None, ge=0)
    remarks: Optional[str] = None


class AppraisalReportResponse(BaseModel):
    id: str
    appraisal_number: str
    appraisal_date: datetime
    appraisal_type: str
    gold_loan_id: Optional[str]
    ornament_id: Optional[str]
    customer_id: str
    ornament_type: str
    ornament_description: str
    quantity: int
    claimed_karat: int
    verified_karat: int
    purity_percentage: Decimal
    gross_weight_grams: Decimal
    stone_weight_grams: Decimal
    other_deductions_grams: Decimal
    net_gold_weight_grams: Decimal
    hallmark_present: bool
    hallmark_number: Optional[str]
    condition: str
    wear_and_tear: Optional[str]
    defects: Optional[str]
    current_gold_rate_24k: Decimal
    applied_gold_rate: Decimal
    base_value: Decimal
    condition_adjustment_percentage: Decimal
    market_adjustment_percentage: Decimal
    market_value: Decimal
    appraised_value: Decimal
    forced_sale_value: Optional[Decimal]
    appraised_by: str
    appraiser_name: str
    appraiser_license: Optional[str]
    verified_by: Optional[str]
    verification_date: Optional[datetime]
    verification_status: Optional[str]
    certificate_number: Optional[str]
    certificate_issued_date: Optional[datetime]
    certificate_valid_until: Optional[datetime]
    status: str
    previous_appraisal_id: Optional[str]
    next_appraisal_due_date: Optional[datetime]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Auction Schemas (Enhanced)
# ============================================

class GoldAuctionCreateRequest(BaseModel):
    gold_loan_id: str
    auction_date: datetime
    reserve_price: Optional[Decimal] = Field(None, gt=0)
    auction_venue: Optional[str] = None
    notice_period_days: Optional[int] = Field(default=30, ge=1)
    remarks: Optional[str] = None


class AuctionBidCreateRequest(BaseModel):
    auction_id: str
    bidder_name: str
    bidder_contact: str = Field(..., max_length=20)
    bidder_email: Optional[str] = None
    bidder_pan: Optional[str] = None
    bidder_address: Optional[str] = None
    bidder_registration_number: Optional[str] = None
    registration_date: Optional[datetime] = None
    deposit_amount: Optional[Decimal] = Field(None, ge=0)
    bid_amount: Decimal = Field(..., gt=0)
    bid_type: Optional[str] = Field(default="Regular", description="Regular, Online, Proxy")
    remarks: Optional[str] = None


class AuctionBidResponse(BaseModel):
    id: str
    bid_number: str
    auction_id: str
    bid_date: datetime
    bidder_name: str
    bidder_contact: str
    bidder_email: Optional[str]
    bidder_registration_number: Optional[str]
    bid_amount: Decimal
    bid_type: str
    bid_rank: Optional[int]
    bid_status: str
    is_winning_bid: bool
    won_date: Optional[datetime]
    payment_amount: Optional[Decimal]
    payment_date: Optional[datetime]
    payment_status: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuctionNoticeCreateRequest(BaseModel):
    auction_id: str
    notice_type: str = Field(..., description="Default Notice, Auction Notice, Final Notice, Public Notice")
    notice_date: datetime
    notice_period_days: int = Field(..., ge=1)
    delivery_method: str = Field(..., description="Registered Post, Email, SMS, Personal, Publication")
    delivery_address: Optional[str] = None
    delivery_email: Optional[str] = None
    delivery_phone: Optional[str] = None
    remarks: Optional[str] = None

    @validator('notice_type')
    def validate_notice_type(cls, v):
        allowed = ['Default Notice', 'Auction Notice', 'Final Notice', 'Public Notice']
        if v not in allowed:
            raise ValueError(f'Notice type must be one of: {", ".join(allowed)}')
        return v

    @validator('delivery_method')
    def validate_delivery_method(cls, v):
        allowed = ['Registered Post', 'Email', 'SMS', 'Personal', 'Publication']
        if v not in allowed:
            raise ValueError(f'Delivery method must be one of: {", ".join(allowed)}')
        return v


class AuctionNoticeResponse(BaseModel):
    id: str
    notice_number: str
    auction_id: str
    gold_loan_id: str
    customer_id: str
    notice_type: str
    notice_date: datetime
    notice_period_days: int
    response_due_date: datetime
    delivery_method: str
    sent_date: Optional[datetime]
    delivered_date: Optional[datetime]
    delivery_status: str
    delivery_address: Optional[str]
    delivery_email: Optional[str]
    tracking_number: Optional[str]
    response_received: bool
    response_date: Optional[datetime]
    response_type: Optional[str]
    notice_document_url: Optional[str]
    proof_of_delivery_url: Optional[str]
    legal_requirement_met: bool
    verified_by: Optional[str]
    verification_date: Optional[datetime]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
