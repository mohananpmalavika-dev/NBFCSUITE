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


class GoldRateHistory(Base, TenantMixin, TimestampMixin):
    """
    Gold Rate History Model
    Tracks historical and current gold rates
    """
    __tablename__ = "gold_rate_history"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Rate details
    rate_date = Column(DateTime(timezone=True), nullable=False, index=True)
    gold_rate_24k = Column(Numeric(10, 2), nullable=False)  # 24K rate per gram
    gold_rate_22k = Column(Numeric(10, 2), nullable=False)  # 22K rate per gram
    gold_rate_18k = Column(Numeric(10, 2), nullable=False)  # 18K rate per gram
    
    # Source information
    source = Column(String(100), nullable=False)  # Manual, IBJA, MCX, API
    source_reference = Column(String(200), nullable=True)  # API endpoint or reference
    
    # Market info
    market_name = Column(String(100), nullable=True)  # Mumbai, Delhi, London
    currency = Column(String(10), default="INR")
    
    # Additional rates (optional)
    silver_rate = Column(Numeric(10, 2), nullable=True)  # Silver rate per gram
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False, index=True)  # Current active rate
    
    # Metadata
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    applied_from = Column(DateTime(timezone=True), nullable=True)
    applied_to = Column(DateTime(timezone=True), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_gold_rate_date', 'tenant_id', 'rate_date'),
        Index('idx_gold_rate_current', 'tenant_id', 'is_current'),
        Index('idx_gold_rate_source', 'tenant_id', 'source'),
    )
    
    def __repr__(self):
        return f"<GoldRateHistory(id={self.id}, 24k={self.gold_rate_24k}, date={self.rate_date})>"


class VaultLocation(Base, TenantMixin, TimestampMixin):
    """
    Vault Location Model
    Physical vault storage locations
    """
    __tablename__ = "vault_locations"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Location details
    vault_code = Column(String(50), nullable=False, index=True)
    vault_name = Column(String(200), nullable=False)
    
    # Hierarchy
    branch_id = Column(String(50), nullable=False, index=True)
    location_type = Column(String(50), nullable=False)  # Main Vault, Branch Vault, Safe, Locker
    
    # Physical location
    building = Column(String(200), nullable=True)
    floor = Column(String(50), nullable=True)
    room = Column(String(50), nullable=True)
    rack_number = Column(String(50), nullable=True)
    shelf_number = Column(String(50), nullable=True)
    
    # Capacity
    max_capacity_items = Column(Integer, nullable=True)
    max_capacity_weight_kg = Column(Numeric(10, 3), nullable=True)
    current_items_count = Column(Integer, default=0)
    current_weight_kg = Column(Numeric(10, 3), default=0.000)
    
    # Security
    security_level = Column(String(50), default="High")  # High, Medium, Low
    access_control = Column(String(100), nullable=True)  # Biometric, Key, Card
    surveillance = Column(Boolean, default=True)
    
    # Insurance
    insured = Column(Boolean, default=True)
    insurance_value = Column(Numeric(15, 2), nullable=True)
    
    # Status
    status = Column(String(50), default="Active", index=True)  # Active, Inactive, Maintenance, Full
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Contact
    custodian_name = Column(String(200), nullable=True)
    custodian_contact = Column(String(20), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_vault_code', 'tenant_id', 'vault_code', unique=True),
        Index('idx_vault_branch', 'tenant_id', 'branch_id'),
        Index('idx_vault_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<VaultLocation(id={self.id}, code={self.vault_code})>"


class VaultInventory(Base, TenantMixin, TimestampMixin):
    """
    Vault Inventory Model
    Tracks gold items in vault
    """
    __tablename__ = "vault_inventory"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Inventory details
    inventory_number = Column(String(50), nullable=False, unique=True, index=True)
    vault_location_id = Column(String(50), nullable=False, index=True)
    
    # Gold loan reference
    gold_loan_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    ornament_id = Column(String(50), nullable=False, index=True)
    
    # Storage details
    package_number = Column(String(50), nullable=True)
    seal_number = Column(String(50), nullable=True)
    barcode = Column(String(100), nullable=True, index=True)
    rfid_tag = Column(String(100), nullable=True, index=True)
    
    # Physical location within vault
    rack_position = Column(String(50), nullable=True)
    shelf_position = Column(String(50), nullable=True)
    slot_position = Column(String(50), nullable=True)
    
    # Item details
    item_description = Column(Text, nullable=False)
    total_weight_grams = Column(Numeric(10, 3), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    
    # Check-in details
    check_in_date = Column(DateTime(timezone=True), nullable=False)
    check_in_by = Column(String(50), nullable=False)
    check_in_verified_by = Column(String(50), nullable=True)
    check_in_photo_url = Column(String(500), nullable=True)
    
    # Check-out details
    check_out_date = Column(DateTime(timezone=True), nullable=True)
    check_out_by = Column(String(50), nullable=True)
    check_out_verified_by = Column(String(50), nullable=True)
    check_out_photo_url = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), default="In Vault", index=True)
    # In Vault, Released, Transferred, Auctioned, Missing
    
    # Audit trail
    last_audit_date = Column(DateTime(timezone=True), nullable=True)
    last_audit_by = Column(String(50), nullable=True)
    audit_status = Column(String(50), nullable=True)  # OK, Discrepancy, Missing
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_vault_inv_vault', 'tenant_id', 'vault_location_id'),
        Index('idx_vault_inv_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_vault_inv_status', 'tenant_id', 'status'),
        Index('idx_vault_inv_barcode', 'tenant_id', 'barcode'),
    )
    
    def __repr__(self):
        return f"<VaultInventory(id={self.id}, inventory_number={self.inventory_number})>"


class VaultTransfer(Base, TenantMixin, TimestampMixin):
    """
    Vault Transfer Model
    Tracks transfers between vaults
    """
    __tablename__ = "vault_transfers"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Transfer details
    transfer_number = Column(String(50), nullable=False, unique=True, index=True)
    transfer_date = Column(DateTime(timezone=True), nullable=False)
    
    # Source and destination
    from_vault_id = Column(String(50), nullable=False, index=True)
    to_vault_id = Column(String(50), nullable=False, index=True)
    
    # Items being transferred
    inventory_ids = Column(Text, nullable=False)  # JSON array of inventory IDs
    total_items_count = Column(Integer, nullable=False)
    total_weight_grams = Column(Numeric(10, 3), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    
    # Transfer tracking
    initiated_by = Column(String(50), nullable=False)
    approved_by = Column(String(50), nullable=True)
    
    # Dispatch details
    dispatched_date = Column(DateTime(timezone=True), nullable=True)
    dispatched_by = Column(String(50), nullable=True)
    dispatch_reference = Column(String(100), nullable=True)
    
    # Receipt details
    received_date = Column(DateTime(timezone=True), nullable=True)
    received_by = Column(String(50), nullable=True)
    receipt_reference = Column(String(100), nullable=True)
    
    # Verification
    verified_by = Column(String(50), nullable=True)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(String(50), nullable=True)  # OK, Discrepancy
    
    # Status
    status = Column(String(50), default="Pending", index=True)
    # Pending, In Transit, Received, Completed, Cancelled
    
    # Security
    seal_number = Column(String(50), nullable=True)
    transport_mode = Column(String(50), nullable=True)  # Courier, Personal, Security Van
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_vault_transfer_from', 'tenant_id', 'from_vault_id'),
        Index('idx_vault_transfer_to', 'tenant_id', 'to_vault_id'),
        Index('idx_vault_transfer_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<VaultTransfer(id={self.id}, transfer_number={self.transfer_number})>"


class PurityTest(Base, TenantMixin, TimestampMixin):
    """
    Purity Test Model
    Records gold purity testing
    """
    __tablename__ = "purity_tests"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Test details
    test_number = Column(String(50), nullable=False, unique=True, index=True)
    test_date = Column(DateTime(timezone=True), nullable=False)
    
    # Item reference
    gold_loan_id = Column(String(50), nullable=False, index=True)
    ornament_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    
    # Test method
    test_method = Column(String(50), nullable=False)
    # XRF (X-Ray Fluorescence), Touchstone, Fire Assay, Acid Test, Electronic Tester
    
    # Claimed details
    claimed_purity_karat = Column(Integer, nullable=False)
    claimed_purity_percentage = Column(Numeric(5, 2), nullable=False)
    
    # Test results
    tested_purity_karat = Column(Integer, nullable=False)
    tested_purity_percentage = Column(Numeric(5, 2), nullable=False)
    purity_variance = Column(Numeric(5, 2), nullable=False)  # Difference
    
    # Test equipment
    equipment_id = Column(String(50), nullable=True)
    equipment_name = Column(String(200), nullable=True)
    equipment_calibration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Testing details
    sample_weight = Column(Numeric(10, 3), nullable=True)  # If sample taken
    test_temperature = Column(Numeric(6, 2), nullable=True)  # For fire assay
    
    # Result classification
    test_result = Column(String(50), nullable=False, index=True)
    # Pass, Fail, Acceptable Variance, Major Discrepancy
    
    # Tester details
    tested_by = Column(String(50), nullable=False)
    tester_name = Column(String(200), nullable=False)
    tester_license = Column(String(100), nullable=True)
    verified_by = Column(String(50), nullable=True)
    
    # Certificate
    certificate_number = Column(String(100), nullable=True, index=True)
    certificate_url = Column(String(500), nullable=True)
    certificate_issued_date = Column(DateTime(timezone=True), nullable=True)
    certificate_valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Action taken
    action_taken = Column(String(50), nullable=True)
    # Accepted, Rejected, Value Adjusted, Re-test Required
    adjusted_value = Column(Numeric(15, 2), nullable=True)
    
    # Photos/evidence
    test_photo_url = Column(String(500), nullable=True)
    report_url = Column(String(500), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_purity_test_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_purity_test_ornament', 'tenant_id', 'ornament_id'),
        Index('idx_purity_test_result', 'tenant_id', 'test_result'),
        Index('idx_purity_test_date', 'tenant_id', 'test_date'),
    )
    
    def __repr__(self):
        return f"<PurityTest(id={self.id}, test_number={self.test_number})>"


class AppraisalReport(Base, TenantMixin, TimestampMixin):
    """
    Appraisal Report Model
    Comprehensive ornament appraisal
    """
    __tablename__ = "appraisal_reports"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Report details
    appraisal_number = Column(String(50), nullable=False, unique=True, index=True)
    appraisal_date = Column(DateTime(timezone=True), nullable=False)
    appraisal_type = Column(String(50), nullable=False)
    # Initial, Re-appraisal, Top-up, Audit, Dispute Resolution
    
    # Item reference
    gold_loan_id = Column(String(50), nullable=True, index=True)  # Null for new applications
    ornament_id = Column(String(50), nullable=True, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    
    # Ornament details
    ornament_type = Column(String(100), nullable=False)
    ornament_description = Column(Text, nullable=False)
    quantity = Column(Integer, default=1)
    
    # Gold details
    claimed_karat = Column(Integer, nullable=False)
    verified_karat = Column(Integer, nullable=False)
    purity_percentage = Column(Numeric(5, 2), nullable=False)
    
    # Weight assessment
    gross_weight_grams = Column(Numeric(10, 3), nullable=False)
    stone_weight_grams = Column(Numeric(10, 3), default=0.000)
    other_deductions_grams = Column(Numeric(10, 3), default=0.000)
    net_gold_weight_grams = Column(Numeric(10, 3), nullable=False)
    
    # Identification marks
    hallmark_present = Column(Boolean, default=False)
    hallmark_number = Column(String(100), nullable=True)
    hallmark_center = Column(String(200), nullable=True)
    manufacturer_mark = Column(String(200), nullable=True)
    
    # Condition assessment
    condition = Column(String(50), nullable=False)  # Excellent, Good, Fair, Poor, Damaged
    wear_and_tear = Column(Text, nullable=True)
    defects = Column(Text, nullable=True)
    
    # Market valuation
    current_gold_rate_24k = Column(Numeric(10, 2), nullable=False)
    applied_gold_rate = Column(Numeric(10, 2), nullable=False)
    base_value = Column(Numeric(15, 2), nullable=False)
    
    # Value adjustments
    condition_adjustment_percentage = Column(Numeric(5, 2), default=0.00)
    market_adjustment_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Final valuation
    market_value = Column(Numeric(15, 2), nullable=False)
    appraised_value = Column(Numeric(15, 2), nullable=False)
    forced_sale_value = Column(Numeric(15, 2), nullable=True)  # Auction scenario
    
    # Comparable analysis
    comparable_items = Column(Text, nullable=True)  # JSON of similar items
    market_reference = Column(Text, nullable=True)
    
    # Appraiser details
    appraised_by = Column(String(50), nullable=False)
    appraiser_name = Column(String(200), nullable=False)
    appraiser_license = Column(String(100), nullable=True)
    appraiser_experience_years = Column(Integer, nullable=True)
    
    # Verification
    verified_by = Column(String(50), nullable=True)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(String(50), nullable=True)  # Approved, Rejected, Pending
    
    # Documentation
    photo_urls = Column(Text, nullable=True)  # JSON array of photo URLs
    video_url = Column(String(500), nullable=True)
    report_pdf_url = Column(String(500), nullable=True)
    
    # Certificate
    certificate_number = Column(String(100), nullable=True, index=True)
    certificate_issued_date = Column(DateTime(timezone=True), nullable=True)
    certificate_valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default="Draft", index=True)
    # Draft, Submitted, Approved, Rejected, Archived
    
    # Re-appraisal tracking
    previous_appraisal_id = Column(String(50), nullable=True, index=True)
    next_appraisal_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_appraisal_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_appraisal_customer', 'tenant_id', 'customer_id'),
        Index('idx_appraisal_date', 'tenant_id', 'appraisal_date'),
        Index('idx_appraisal_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<AppraisalReport(id={self.id}, appraisal_number={self.appraisal_number})>"


class AuctionBid(Base, TenantMixin, TimestampMixin):
    """
    Auction Bid Model
    Records bids in gold auctions
    """
    __tablename__ = "auction_bids"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Bid details
    bid_number = Column(String(50), nullable=False, unique=True, index=True)
    auction_id = Column(String(50), nullable=False, index=True)
    bid_date = Column(DateTime(timezone=True), nullable=False)
    
    # Bidder information
    bidder_name = Column(String(200), nullable=False)
    bidder_contact = Column(String(20), nullable=False)
    bidder_email = Column(String(200), nullable=True)
    bidder_pan = Column(String(20), nullable=True)
    bidder_address = Column(Text, nullable=True)
    
    # Registration
    bidder_registration_number = Column(String(50), nullable=True, index=True)
    registration_date = Column(DateTime(timezone=True), nullable=True)
    deposit_amount = Column(Numeric(15, 2), nullable=True)  # EMD
    
    # Bid details
    bid_amount = Column(Numeric(15, 2), nullable=False)
    bid_type = Column(String(50), default="Regular")  # Regular, Online, Proxy
    bid_rank = Column(Integer, nullable=True)  # Ranking among all bids
    
    # Status
    bid_status = Column(String(50), default="Submitted", index=True)
    # Submitted, Accepted, Rejected, Withdrawn, Winner, Outbid
    
    # Winner details
    is_winning_bid = Column(Boolean, default=False, index=True)
    won_date = Column(DateTime(timezone=True), nullable=True)
    
    # Payment tracking (if winner)
    payment_amount = Column(Numeric(15, 2), nullable=True)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    payment_status = Column(String(50), nullable=True)  # Pending, Partial, Completed
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_auction_bid_auction', 'tenant_id', 'auction_id'),
        Index('idx_auction_bid_status', 'tenant_id', 'bid_status'),
        Index('idx_auction_bid_winner', 'tenant_id', 'is_winning_bid'),
    )
    
    def __repr__(self):
        return f"<AuctionBid(id={self.id}, bid_number={self.bid_number}, amount={self.bid_amount})>"


class AuctionNotice(Base, TenantMixin, TimestampMixin):
    """
    Auction Notice Model
    Legal notices for auctions
    """
    __tablename__ = "auction_notices"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Notice details
    notice_number = Column(String(50), nullable=False, unique=True, index=True)
    auction_id = Column(String(50), nullable=False, index=True)
    gold_loan_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), nullable=False, index=True)
    
    # Notice type
    notice_type = Column(String(50), nullable=False)
    # Default Notice, Auction Notice, Final Notice, Public Notice
    
    # Notice details
    notice_date = Column(DateTime(timezone=True), nullable=False)
    notice_period_days = Column(Integer, nullable=False)
    response_due_date = Column(DateTime(timezone=True), nullable=False)
    
    # Delivery method
    delivery_method = Column(String(50), nullable=False)
    # Registered Post, Email, SMS, Personal, Publication
    
    # Delivery tracking
    sent_date = Column(DateTime(timezone=True), nullable=True)
    delivered_date = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String(50), default="Pending", index=True)
    # Pending, Sent, Delivered, Failed, Bounced
    
    # Contact details used
    delivery_address = Column(Text, nullable=True)
    delivery_email = Column(String(200), nullable=True)
    delivery_phone = Column(String(20), nullable=True)
    
    # Tracking references
    tracking_number = Column(String(100), nullable=True)
    postal_reference = Column(String(100), nullable=True)
    
    # Response tracking
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime(timezone=True), nullable=True)
    response_type = Column(String(50), nullable=True)
    # Payment Made, Extension Request, Dispute, No Response
    
    # Document
    notice_document_url = Column(String(500), nullable=True)
    proof_of_delivery_url = Column(String(500), nullable=True)
    
    # Legal compliance
    legal_requirement_met = Column(Boolean, default=False)
    verified_by = Column(String(50), nullable=True)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_auction_notice_auction', 'tenant_id', 'auction_id'),
        Index('idx_auction_notice_loan', 'tenant_id', 'gold_loan_id'),
        Index('idx_auction_notice_status', 'tenant_id', 'delivery_status'),
    )
    
    def __repr__(self):
        return f"<AuctionNotice(id={self.id}, notice_number={self.notice_number})>"
