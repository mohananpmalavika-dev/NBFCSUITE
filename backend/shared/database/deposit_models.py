"""
Deposit Management Database Models

This module contains all database models for deposit management including:
- Deposit Products (Savings, FD, RD, MIS)
- Deposit Accounts
- Deposit Transactions
- Interest Calculations

All models follow multi-tenant architecture with soft delete pattern.
"""

from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base


class DepositProduct(Base):
    """
    Deposit Product Master
    
    Defines deposit schemes offered by the NBFC/Nidhi company.
    Supports: Savings, Fixed Deposits (FD), Recurring Deposits (RD), Monthly Income Scheme (MIS)
    """
    __tablename__ = "deposit_products"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Product Details
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(50), nullable=False, index=True)  # savings, fd, rd, mis
    description = Column(Text)
    
    # Interest Configuration
    interest_rate = Column(Numeric(5, 2), nullable=False)  # Annual rate in percentage
    interest_calculation_method = Column(String(50), nullable=False)  # simple, compound
    interest_calculation_frequency = Column(String(50), nullable=False)  # daily, monthly, quarterly
    interest_payout_frequency = Column(String(50))  # monthly, quarterly, maturity, on_demand
    
    # Tenure Configuration (for FD/RD/MIS)
    min_tenure_days = Column(Integer)  # Minimum tenure in days
    max_tenure_days = Column(Integer)  # Maximum tenure in days
    tenure_unit = Column(String(20))  # days, months, years
    
    # Amount Configuration
    min_deposit_amount = Column(Numeric(15, 2), nullable=False)
    max_deposit_amount = Column(Numeric(15, 2))
    
    # Savings Account Specific
    min_balance = Column(Numeric(15, 2))  # Minimum balance requirement
    min_balance_penalty = Column(Numeric(10, 2))  # Penalty for falling below min balance
    
    # Recurring Deposit Specific
    installment_amount = Column(Numeric(15, 2))  # Fixed monthly installment for RD
    installment_frequency = Column(String(50))  # monthly, quarterly
    missed_installment_penalty = Column(Numeric(5, 2))  # Penalty percentage for missed RD installments
    
    # Withdrawal Rules
    premature_withdrawal_allowed = Column(Boolean, default=False)
    premature_withdrawal_penalty = Column(Numeric(5, 2))  # Penalty percentage
    max_withdrawals_per_month = Column(Integer)  # For savings accounts
    withdrawal_charge = Column(Numeric(10, 2))  # Per withdrawal charge
    
    # Renewal Configuration
    auto_renewal_allowed = Column(Boolean, default=False)
    
    # Tax Configuration
    tds_applicable = Column(Boolean, default=True)
    tds_rate = Column(Numeric(5, 2), default=10.0)  # TDS rate percentage
    tds_threshold = Column(Numeric(15, 2), default=40000.0)  # Annual interest threshold for TDS
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    accounts = relationship("DepositAccount", back_populates="product")
    
    def __repr__(self):
        return f"<DepositProduct {self.product_code} - {self.product_name}>"


class DepositAccount(Base):
    """
    Deposit Account
    
    Individual deposit accounts opened by customers.
    Tracks balance, interest, transactions, and maturity details.
    """
    __tablename__ = "deposit_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    account_number = Column(String(50), unique=True, nullable=False, index=True)  # DEP-YYYYMM-XXXX
    
    # Links
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    deposit_product_id = Column(Integer, ForeignKey("deposit_products.id"), nullable=False, index=True)
    
    # Account Details
    account_type = Column(String(50), nullable=False, index=True)  # savings, fd, rd, mis
    principal_amount = Column(Numeric(15, 2), nullable=False)  # Initial deposit amount
    current_balance = Column(Numeric(15, 2), nullable=False)  # Current balance
    interest_earned = Column(Numeric(15, 2), default=0)  # Total interest earned
    total_deposits = Column(Numeric(15, 2), default=0)  # Total deposits made
    total_withdrawals = Column(Numeric(15, 2), default=0)  # Total withdrawals made
    
    # Interest Details
    interest_rate = Column(Numeric(5, 2), nullable=False)  # Rate at account opening
    last_interest_date = Column(Date)  # Last interest calculation date
    next_interest_date = Column(Date)  # Next scheduled interest date
    total_interest_posted = Column(Numeric(15, 2), default=0)  # Total interest posted to account
    
    # Tenure (for FD/RD/MIS)
    tenure_days = Column(Integer)  # Total tenure in days
    opening_date = Column(Date, nullable=False, index=True)
    maturity_date = Column(Date, index=True)  # Expected maturity date
    maturity_amount = Column(Numeric(15, 2))  # Expected maturity amount
    
    # Recurring Deposit Specific
    installment_amount = Column(Numeric(15, 2))  # Monthly installment amount
    installments_paid = Column(Integer, default=0)  # Number of installments paid
    total_installments = Column(Integer)  # Total installments required
    next_installment_date = Column(Date)  # Next installment due date
    missed_installments = Column(Integer, default=0)  # Count of missed installments
    
    # Status
    status = Column(String(50), nullable=False, default='active', index=True)
    # Status values: active, matured, closed, premature_closed, dormant
    
    # Renewal
    auto_renewal = Column(Boolean, default=False)
    renewal_count = Column(Integer, default=0)  # Number of times renewed
    parent_account_id = Column(Integer, ForeignKey("deposit_accounts.id"))  # For renewed accounts
    
    # Closure Details
    closure_date = Column(Date)
    closure_amount = Column(Numeric(15, 2))  # Final settlement amount
    premature_closure = Column(Boolean, default=False)
    penalty_amount = Column(Numeric(10, 2))  # Penalty charged on premature closure
    closure_reason = Column(String(200))
    
    # Nomination Details
    nominee_name = Column(String(200))
    nominee_relationship = Column(String(100))
    nominee_dob = Column(Date)
    nominee_percentage = Column(Numeric(5, 2), default=100)  # Percentage share
    nominee_address = Column(Text)
    nominee_id_proof = Column(String(200))  # Document reference
    
    # Linked Account (for auto-debit/credit)
    linked_account_number = Column(String(50))  # For auto-debit of RD installments
    
    # Flags
    passbook_issued = Column(Boolean, default=False)
    certificate_issued = Column(Boolean, default=False)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    product = relationship("DepositProduct", back_populates="accounts")
    customer = relationship("Customer")
    transactions = relationship("DepositTransaction", back_populates="account", cascade="all, delete-orphan")
    interest_calculations = relationship("DepositInterestCalculation", back_populates="account", cascade="all, delete-orphan")
    renewed_accounts = relationship("DepositAccount", foreign_keys=[parent_account_id])
    
    def __repr__(self):
        return f"<DepositAccount {self.account_number} - {self.customer_id}>"


class DepositTransaction(Base):
    """
    Deposit Transaction
    
    Records all transactions on deposit accounts including:
    - Deposits
    - Withdrawals
    - Interest credits
    - Penalties
    - Charges
    """
    __tablename__ = "deposit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False, index=True)
    
    # Transaction Identification
    transaction_number = Column(String(50), unique=True, nullable=False, index=True)  # TXN-YYYYMMDD-XXXX
    transaction_type = Column(String(50), nullable=False, index=True)
    # Types: deposit, withdrawal, interest_credit, interest_tds, penalty, charge, opening, closure, installment
    
    # Amount Details
    amount = Column(Numeric(15, 2), nullable=False)  # Transaction amount
    balance_before = Column(Numeric(15, 2), nullable=False)  # Balance before transaction
    balance_after = Column(Numeric(15, 2), nullable=False)  # Balance after transaction
    
    # Dates
    transaction_date = Column(Date, nullable=False, index=True)  # Transaction posting date
    value_date = Column(Date, nullable=False)  # Value date for interest calculation
    
    # Payment Details
    payment_mode = Column(String(50))  # cash, cheque, neft, rtgs, imps, upi, internal_transfer
    reference_number = Column(String(100))  # Cheque number, UTR, etc.
    bank_name = Column(String(200))  # For cheque/NEFT/RTGS
    branch_name = Column(String(200))
    
    # Interest Related (if transaction is interest credit)
    interest_period_start = Column(Date)
    interest_period_end = Column(Date)
    interest_rate = Column(Numeric(5, 2))
    tds_amount = Column(Numeric(10, 2), default=0)  # TDS deducted
    
    # Additional Details
    remarks = Column(Text)
    reversal_flag = Column(Boolean, default=False)  # True if transaction is reversed
    reversed_transaction_id = Column(Integer, ForeignKey("deposit_transactions.id"))  # Link to reversed transaction
    
    # Processed By
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # User who processed the transaction
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # For high-value transactions
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    account = relationship("DepositAccount", back_populates="transactions")
    reversed_transaction = relationship("DepositTransaction", remote_side=[id])
    
    def __repr__(self):
        return f"<DepositTransaction {self.transaction_number} - {self.transaction_type}>"


class DepositInterestCalculation(Base):
    """
    Interest Calculation Record
    
    Stores interest calculation details for each period.
    Used for audit trail and interest certificate generation.
    """
    __tablename__ = "deposit_interest_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False, index=True)
    
    # Calculation Period
    calculation_period_start = Column(Date, nullable=False)
    calculation_period_end = Column(Date, nullable=False)
    
    # Balance Information
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    average_balance = Column(Numeric(15, 2))  # For monthly average balance method
    
    # Interest Calculation
    interest_rate = Column(Numeric(5, 2), nullable=False)
    days_in_period = Column(Integer, nullable=False)
    interest_amount = Column(Numeric(10, 2), nullable=False)  # Gross interest
    
    # Calculation Method
    calculation_method = Column(String(50), nullable=False)
    # Methods: simple, compound, daily_balance, monthly_average
    
    # TDS Details
    tds_applicable = Column(Boolean, default=False)
    tds_amount = Column(Numeric(10, 2), default=0)
    tds_rate = Column(Numeric(5, 2))
    net_interest = Column(Numeric(10, 2))  # Interest after TDS
    
    # Posting Details
    posted = Column(Boolean, default=False, index=True)  # Whether interest is posted to account
    posted_date = Column(Date)
    transaction_id = Column(Integer, ForeignKey("deposit_transactions.id"))  # Link to transaction
    
    # Calculation Metadata
    calculation_date = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # System or user who triggered calculation
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount", back_populates="interest_calculations")
    transaction = relationship("DepositTransaction")
    
    def __repr__(self):
        return f"<InterestCalculation {self.deposit_account_id} - {self.calculation_period_start} to {self.calculation_period_end}>"


class DepositMaturityQueue(Base):
    """
    Maturity Processing Queue
    
    Tracks accounts due for maturity and their processing status.
    Used for automated maturity processing and renewal.
    """
    __tablename__ = "deposit_maturity_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False, index=True)
    
    # Maturity Details
    maturity_date = Column(Date, nullable=False, index=True)
    maturity_amount = Column(Numeric(15, 2), nullable=False)
    principal_amount = Column(Numeric(15, 2), nullable=False)
    interest_amount = Column(Numeric(15, 2), nullable=False)
    
    # Processing Status
    status = Column(String(50), default='pending', index=True)
    # Status: pending, processed, renewed, failed
    
    # Auto-Renewal
    auto_renewal = Column(Boolean, default=False)
    renewal_product_id = Column(Integer, ForeignKey("deposit_products.id"))
    renewal_tenure_days = Column(Integer)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_date = Column(DateTime)
    
    # Processing Details
    processed_date = Column(DateTime)
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    processing_remarks = Column(Text)
    error_message = Column(Text)
    
    # Payout Details
    payout_mode = Column(String(50))  # cash, cheque, transfer
    payout_account = Column(String(50))  # Bank account for transfer
    payout_reference = Column(String(100))
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount")
    renewal_product = relationship("DepositProduct")
    
    def __repr__(self):
        return f"<MaturityQueue {self.deposit_account_id} - {self.maturity_date}>"


class DepositPassbookEntry(Base):
    """
    Passbook Entry
    
    Formatted entries for passbook printing.
    Separate from transactions for better passbook management.
    """
    __tablename__ = "deposit_passbook_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    deposit_account_id = Column(Integer, ForeignKey("deposit_accounts.id"), nullable=False, index=True)
    
    # Entry Details
    entry_date = Column(Date, nullable=False, index=True)
    particulars = Column(String(500), nullable=False)  # Description for passbook
    
    # Transaction Reference
    transaction_id = Column(Integer, ForeignKey("deposit_transactions.id"), index=True)
    
    # Amounts
    withdrawal_amount = Column(Numeric(15, 2), default=0)
    deposit_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2), nullable=False)
    
    # Printing
    printed = Column(Boolean, default=False)
    print_date = Column(DateTime)
    page_number = Column(Integer)
    line_number = Column(Integer)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount")
    transaction = relationship("DepositTransaction")
    
    def __repr__(self):
        return f"<PassbookEntry {self.deposit_account_id} - {self.entry_date}>"
