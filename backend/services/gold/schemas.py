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
