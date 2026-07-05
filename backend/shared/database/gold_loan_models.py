"""
Gold Loan Models
Database models for gold loan management
"""

from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from backend.shared.database.connection import Base
from backend.shared.database.models import TenantMixin, TimestampMixin


class GoldLoanProduct(Base, TenantMixin, TimestampMixin):
    """
    Gold Loan Product Model
    Defines gold loan schemes
    """
    __tablename__ = "gold_loan_products"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Product details
    product_code = Column(String(50), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Interest rates
    interest_rate_min = Column(Numeric(5, 2), nullable=False)  # Min annual rate %
    interest_rate_max = Column(Numeric(5, 2), nullable=False)  # Max annual rate %
    default_interest_rate = Column(Numeric(5, 2), nullable=False)
    
    # Loan-to-Value (LTV) ratio
    ltv_ratio = Column(Numeric(5, 2), nullable=False)  # LTV percentage (e.g., 75%)
    max_ltv_ratio = Column(Numeric(5, 2), nullable=False, default=75.00)
    
    # Loan amount limits
    min_loan_amount = Column(Numeric(15, 2), nullable=False)
    max_loan_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tenure (in months)
    min_tenure_months = Column(Integer, nullable=False)
    max_tenure_months = Column(Integer, nullable=False)
    default_tenure_months = Column(Integer, nullable=False)
    
    # Fees and charges
    processing_fee_percentage = Column(Numeric(5, 2), default=0.00)
    processing_fee_flat = Column(Numeric(10, 2), default=0.00)
    valuation_charges = Column(Numeric(10, 2), default=0.00)
    documentation_charges = Column(Numeric(10, 2), default=0.00)
    storage_charges_monthly = Column(Numeric(10, 2), default=0.00)
    
    # Penalty charges
    penal_interest_rate = Column(Numeric(5, 2), default=2.00)  # Additional rate on overdue
    bounce_charges = Column(Numeric(10, 2), default=500.00)
    
    # Gold valuation
    gold_rate_source = Column(String(100), default="Manual")  # Manual, API, Market
    purity_check_required = Column(Boolean, default=True)
    minimum_gold_purity = Column(Integer, default=18)  # Minimum karat (18K, 22K, 24K)
    
    # Repayment options
    repayment_frequency = Column(String(50), default="Monthly")  # Monthly, Quarterly, Bullet
    interest_calculation_method = Column(String(50), default="Reducing Balance")
    partial_release_allowed = Column(Boolean, default=True)
    top_up_allowed = Column(Boolean, default=True)
    
    # Insurance
    insurance_required = Column(Boolean, default=True)
    insurance_percentage = Column(Numeric(5, 2), default=0.50)
    
    # Auction details (for defaults)
    auction_notice_days = Column(Integer, default=30)
    auction_reserve_price_percentage = Column(Numeric(5, 2), default=90.00)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_product_code', 'tenant_id', 'product_code', unique=True),
        Index('idx_gold_product_active', 'tenant_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<GoldLoanProduct(id={self.id}, product_name={self.product_name})>"


class GoldOrnament(Base, TenantMixin, TimestampMixin):
    """
    Gold Ornament Model
    Details of pledged gold items
    """
    __tablename__ = "gold_ornaments"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Loan reference
    gold_loan_id = Column(String(50), nullable=False, index=True)
    
    # Ornament details
    item_number = Column(Integer, nullable=False)  # Sequential number within loan
    ornament_type = Column(String(100), nullable=False)  # Ring, Chain, Bangle, Earring, etc.
    ornament_description = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    
    # Gold details
    purity_karat = Column(Integer, nullable=False)  # 18K, 22K, 24K
    purity_percentage = Column(Numeric(5, 2), nullable=False)  # Actual purity %
    
    # Weight details
    gross_weight_grams = Column(Numeric(10, 3), nullable=False)  # Total weight
    stone_weight_grams = Column(Numeric(10, 3), default=0.000)  # Weight of stones
    net_weight_grams = Column(Numeric(10, 3), nullable=False)  # Pure gold weight
    
    # Valuation
    gold_rate_per_gram = Column(Numeric(10, 2), nullable=False)  # Rate at valuation
    market_value = Column(Numeric(15, 2), nullable=False)  # Calculated value
    appraised_value = Column(Numeric(15, 2), nullable=False)  # Final appraised value
    
    # Identification
    hallmark_available = Column(Boolean, default=False)
    hallmark_number = Column(String(100), nullable=True)
    photo_url = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), default="Pledged")  # Pledged, Released, Partially Released, Auctioned
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Release tracking
    released_weight_grams = Column(Numeric(10, 3), default=0.000)
    remaining_weight_grams = Column(Numeric(10, 3), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_ornament_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_gold_ornament_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<GoldOrnament(id={self.id}, type={self.ornament_type}, weight={self.net_weight_grams}g)>"


class GoldLoanAccount(Base, TenantMixin, TimestampMixin):
    """
    Gold Loan Account Model
    Main gold loan account
    """
    __tablename__ = "gold_loan_accounts"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Account details
    loan_account_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    product_id = Column(String(50), nullable=False, index=True)
    
    # Application reference
    application_id = Column(String(50), nullable=True, index=True)
    application_date = Column(DateTime(timezone=True), nullable=False)
    
    # Loan details
    loan_amount = Column(Numeric(15, 2), nullable=False)
    sanctioned_amount = Column(Numeric(15, 2), nullable=False)
    disbursed_amount = Column(Numeric(15, 2), nullable=False)
    
    # Gold valuation
    total_gold_weight_grams = Column(Numeric(10, 3), nullable=False)
    total_gold_value = Column(Numeric(15, 2), nullable=False)
    average_gold_rate = Column(Numeric(10, 2), nullable=False)
    ltv_ratio = Column(Numeric(5, 2), nullable=False)
    
    # Interest details
    interest_rate = Column(Numeric(5, 2), nullable=False)
    interest_calculation_method = Column(String(50), default="Reducing Balance")
    penal_interest_rate = Column(Numeric(5, 2), nullable=False)
    
    # Tenure
    tenure_months = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    maturity_date = Column(DateTime(timezone=True), nullable=False)
    
    # Repayment details
    repayment_frequency = Column(String(50), default="Monthly")
    emi_amount = Column(Numeric(15, 2), nullable=True)  # Null for bullet payment
    
    # Charges
    processing_fee = Column(Numeric(10, 2), default=0.00)
    valuation_charges = Column(Numeric(10, 2), default=0.00)
    documentation_charges = Column(Numeric(10, 2), default=0.00)
    insurance_charges = Column(Numeric(10, 2), default=0.00)
    other_charges = Column(Numeric(10, 2), default=0.00)
    
    # Outstanding details
    principal_outstanding = Column(Numeric(15, 2), nullable=False)
    interest_outstanding = Column(Numeric(15, 2), default=0.00)
    penal_interest_outstanding = Column(Numeric(15, 2), default=0.00)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    
    # Payment tracking
    last_payment_date = Column(DateTime(timezone=True), nullable=True)
    last_payment_amount = Column(Numeric(15, 2), nullable=True)
    next_payment_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Overdue tracking
    days_past_due = Column(Integer, default=0)
    overdue_amount = Column(Numeric(15, 2), default=0.00)
    
    # Status
    status = Column(String(50), default="Active", index=True)
    # Active, Overdue, NPA, Closed, Foreclosed, Auctioned
    
    # Branch and user
    branch_id = Column(String(50), nullable=True, index=True)
    loan_officer_id = Column(String(50), nullable=True)
    approved_by = Column(String(50), nullable=True)
    disbursed_by = Column(String(50), nullable=True)
    
    # Dates
    approval_date = Column(DateTime(timezone=True), nullable=True)
    disbursement_date = Column(DateTime(timezone=True), nullable=True)
    closure_date = Column(DateTime(timezone=True), nullable=True)
    
    # Flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_npa = Column(Boolean, default=False, nullable=False, index=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_loan_customer', 'tenant_id', 'customer_id'),
        Index('idx_gold_loan_status', 'tenant_id', 'status'),
        Index('idx_gold_loan_npa', 'tenant_id', 'is_npa'),
        Index('idx_gold_loan_branch', 'tenant_id', 'branch_id'),
    )
    
    def __repr__(self):
        return f"<GoldLoanAccount(id={self.id}, account_number={self.loan_account_number})>"


class GoldLoanTransaction(Base, TenantMixin, TimestampMixin):
    """
    Gold Loan Transaction Model
    All financial transactions
    """
    __tablename__ = "gold_loan_transactions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Transaction details
    transaction_number = Column(String(50), nullable=False, unique=True, index=True)
    gold_loan_id = Column(String(50), nullable=False, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Transaction type
    transaction_type = Column(String(50), nullable=False, index=True)
    # Disbursement, Payment, Interest, Charges, Penalty, Reversal, Release, TopUp
    
    # Amount details
    amount = Column(Numeric(15, 2), nullable=False)
    principal_amount = Column(Numeric(15, 2), default=0.00)
    interest_amount = Column(Numeric(15, 2), default=0.00)
    penal_interest_amount = Column(Numeric(15, 2), default=0.00)
    charges_amount = Column(Numeric(15, 2), default=0.00)
    
    # Payment details (for payments)
    payment_mode = Column(String(50), nullable=True)  # Cash, Cheque, NEFT, RTGS, UPI
    payment_reference = Column(String(100), nullable=True)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    
    # Bank details (for payments)
    bank_name = Column(String(200), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    # Balance after transaction
    principal_balance = Column(Numeric(15, 2), nullable=False)
    interest_balance = Column(Numeric(15, 2), nullable=False)
    total_balance = Column(Numeric(15, 2), nullable=False)
    
    # User tracking
    created_by = Column(String(50), nullable=False)
    approved_by = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(50), default="Completed")  # Pending, Completed, Failed, Reversed
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_txn_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_gold_txn_date', 'tenant_id', 'transaction_date'),
        Index('idx_gold_txn_type', 'tenant_id', 'transaction_type'),
    )
    
    def __repr__(self):
        return f"<GoldLoanTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class GoldReleaseRequest(Base, TenantMixin, TimestampMixin):
    """
    Gold Release Request Model
    Tracks partial/full gold release requests
    """
    __tablename__ = "gold_release_requests"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Request details
    request_number = Column(String(50), nullable=False, unique=True, index=True)
    gold_loan_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    
    # Release type
    release_type = Column(String(50), nullable=False)  # Partial, Full, Closure
    
    # Ornaments to release
    ornament_ids = Column(Text, nullable=False)  # JSON array of ornament IDs
    total_release_weight_grams = Column(Numeric(10, 3), nullable=False)
    total_release_value = Column(Numeric(15, 2), nullable=False)
    
    # Payment details (for partial release)
    payment_amount = Column(Numeric(15, 2), default=0.00)
    payment_mode = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    
    # New loan details (after partial release)
    new_gold_weight_grams = Column(Numeric(10, 3), nullable=True)
    new_gold_value = Column(Numeric(15, 2), nullable=True)
    new_loan_amount = Column(Numeric(15, 2), nullable=True)
    new_ltv_ratio = Column(Numeric(5, 2), nullable=True)
    
    # Request tracking
    request_date = Column(DateTime(timezone=True), nullable=False)
    requested_by = Column(String(50), nullable=False)
    
    # Approval workflow
    approval_status = Column(String(50), default="Pending", index=True)
    # Pending, Approved, Rejected, Completed
    approved_by = Column(String(50), nullable=True)
    approval_date = Column(DateTime(timezone=True), nullable=True)
    approval_remarks = Column(Text, nullable=True)
    
    # Release execution
    released_date = Column(DateTime(timezone=True), nullable=True)
    released_by = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(50), default="Pending")
    # Pending, In Progress, Completed, Cancelled
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_release_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_gold_release_status', 'tenant_id', 'approval_status'),
    )
    
    def __repr__(self):
        return f"<GoldReleaseRequest(id={self.id}, request_number={self.request_number})>"


class GoldAuction(Base, TenantMixin, TimestampMixin):
    """
    Gold Auction Model
    Tracks gold auctions for defaulted loans
    """
    __tablename__ = "gold_auctions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Auction details
    auction_number = Column(String(50), nullable=False, unique=True, index=True)
    gold_loan_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    
    # Gold details
    total_gold_weight_grams = Column(Numeric(10, 3), nullable=False)
    total_gold_value = Column(Numeric(15, 2), nullable=False)
    
    # Outstanding amount
    outstanding_principal = Column(Numeric(15, 2), nullable=False)
    outstanding_interest = Column(Numeric(15, 2), nullable=False)
    outstanding_charges = Column(Numeric(15, 2), nullable=False)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    
    # Auction details
    reserve_price = Column(Numeric(15, 2), nullable=False)
    auction_date = Column(DateTime(timezone=True), nullable=False)
    auction_venue = Column(String(500), nullable=True)
    
    # Notice details
    notice_sent_date = Column(DateTime(timezone=True), nullable=True)
    notice_period_days = Column(Integer, default=30)
    
    # Auction result
    auction_status = Column(String(50), default="Scheduled", index=True)
    # Scheduled, Completed, Cancelled, Failed
    
    highest_bid_amount = Column(Numeric(15, 2), nullable=True)
    winning_bidder_name = Column(String(200), nullable=True)
    winning_bidder_contact = Column(String(20), nullable=True)
    
    # Settlement
    sale_amount = Column(Numeric(15, 2), nullable=True)
    sale_date = Column(DateTime(timezone=True), nullable=True)
    
    # Customer refund (if sale > outstanding)
    refund_amount = Column(Numeric(15, 2), default=0.00)
    refund_status = Column(String(50), nullable=True)  # Pending, Completed
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_auction_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_gold_auction_status', 'tenant_id', 'auction_status'),
        Index('idx_gold_auction_date', 'tenant_id', 'auction_date'),
    )
    
    def __repr__(self):
        return f"<GoldAuction(id={self.id}, auction_number={self.auction_number})>"
