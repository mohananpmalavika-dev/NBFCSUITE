from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List, Any
from uuid import uuid4
import ast
import operator
import os

from app.db import engine, Base, SessionLocal, get_db


class GLAccount(Base):
    __tablename__ = "gl_accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "account_code", name="uq_gl_accounts_tenant_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    account_code = Column(String, index=True, nullable=False)
    account_name = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    parent_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=True)
    category = Column(String, nullable=True)
    currency = Column(String, default="INR")
    base_currency = Column(String, default="INR")
    normal_balance = Column(String, nullable=True)
    branch_id = Column(String, nullable=True, index=True)
    branch_specific = Column(String, default="false")
    posting_allowed = Column(String, default="true")
    allow_manual_posting = Column(String, default="true")
    allow_auto_posting = Column(String, default="true")
    requires_approval = Column(String, default="false")
    freeze_status = Column(String, default="open")
    status = Column(String, default="active")
    exchange_gain_loss_account_code = Column(String, nullable=True)
    revaluation_account_code = Column(String, nullable=True)
    opening_balance = Column(Float, default=0.0)
    financial_year = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    parent = relationship("GLAccount", remote_side=[id])


class JournalBatch(Base):
    __tablename__ = "journal_batches"
    __table_args__ = (
        UniqueConstraint("tenant_id", "batch_no", name="uq_journal_batches_tenant_number"),
    )

    id = Column(String, primary_key=True)
    batch_no = Column(String, nullable=False, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    posting_date = Column(DateTime, nullable=False)
    financial_year = Column(String, nullable=False, index=True)
    period = Column(String, nullable=False, index=True)
    status = Column(String, default="draft", index=True)
    created_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class JournalNumberCounter(Base):
    __tablename__ = "journal_number_counters"
    __table_args__ = (
        UniqueConstraint("tenant_id", "financial_year", "sequence_type", name="uq_journal_number_counter_scope"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    financial_year = Column(String, nullable=False)
    sequence_type = Column(String, nullable=False)
    current_value = Column(Integer, default=0)



class JournalEntry(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_journal_entries_tenant_idempotency"),
        UniqueConstraint("tenant_id", "journal_no", name="uq_journal_entries_tenant_number"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    batch_id = Column(String, ForeignKey("journal_batches.id"), nullable=True, index=True)
    journal_no = Column(String, nullable=True, index=True)
    entry_date = Column(DateTime, default=datetime.utcnow)
    voucher_type = Column(String, default="journal", index=True)
    description = Column(String)
    reference = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    posting_status = Column(String, default="posted", index=True)
    idempotency_key = Column(String, nullable=True, index=True)
    source_module = Column(String, nullable=True, index=True)
    source_event = Column(String, nullable=True, index=True)
    source_reference = Column(String, nullable=True, index=True)
    business_date = Column(DateTime, nullable=True)
    financial_year = Column(String, nullable=True)
    period = Column(String, nullable=True, index=True)
    branch_id = Column(String, nullable=True, index=True)
    voucher_id = Column(String, nullable=True, index=True)
    currency = Column(String, default="INR")
    exchange_rate = Column(Float, default=1.0)
    reversal_of = Column(String, ForeignKey("journal_entries.id"), nullable=True, index=True)
    created_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    validation_result = Column(JSON, nullable=True)
    template_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("JournalLine", back_populates="journal_entry")
    attachments = relationship("JournalAttachment", back_populates="journal_entry")
    approvals = relationship("JournalApproval", back_populates="journal_entry")


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id = Column(String, primary_key=True)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"))
    sequence = Column(Integer, default=1)
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"))
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    transaction_currency = Column(String, nullable=True)
    transaction_amount = Column(Float, nullable=True)
    exchange_rate = Column(Float, nullable=True)
    branch_id = Column(String, nullable=True, index=True)
    department_id = Column(String, nullable=True, index=True)
    cost_center = Column(String, nullable=True)
    profit_center = Column(String, nullable=True)
    project_id = Column(String, nullable=True, index=True)
    employee_id = Column(String, nullable=True, index=True)
    product_id = Column(String, nullable=True, index=True)
    business_unit_id = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True)
    journal_entry = relationship("JournalEntry", back_populates="lines")
    gl_account = relationship("GLAccount")


class JournalAttachment(Base):
    __tablename__ = "journal_attachments"

    id = Column(String, primary_key=True)
    journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=False, index=True)
    document_id = Column(String, nullable=True)
    file_name = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    journal_entry = relationship("JournalEntry", back_populates="attachments")


class JournalApproval(Base):
    __tablename__ = "journal_approvals"

    id = Column(String, primary_key=True)
    journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=False, index=True)
    level = Column(String, nullable=False)
    approver = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    remarks = Column(String, nullable=True)
    approved_time = Column(DateTime, default=datetime.utcnow)
    journal_entry = relationship("JournalEntry", back_populates="approvals")


class JournalTemplate(Base):
    __tablename__ = "journal_templates"
    __table_args__ = (
        UniqueConstraint("tenant_id", "template_name", name="uq_journal_templates_tenant_name"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    template_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    voucher_type = Column(String, default="journal")
    currency = Column(String, default="INR")
    lines = Column(JSON, nullable=False)
    status = Column(String, default="active", index=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AccountingDimension(Base):
    __tablename__ = "accounting_dimensions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "dimension_type", "code", name="uq_accounting_dimensions_scope"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    dimension_type = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountingBudget(Base):
    __tablename__ = "accounting_budgets"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "financial_year", "period", "gl_account_id", "cost_center",
            name="uq_accounting_budgets_scope",
        ),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    financial_year = Column(String, nullable=False, index=True)
    period = Column(String, nullable=False, index=True)
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=False, index=True)
    cost_center = Column(String, nullable=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BankStatementTransaction(Base):
    __tablename__ = "bank_statement_transactions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "reference", name="uq_bank_statement_transactions_tenant_reference"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    reference = Column(String, index=True)
    transaction_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String)
    status = Column(String, default="unmatched")
    matched_journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)


class TaxRule(Base):
    __tablename__ = "tax_rules"
    __table_args__ = (
        UniqueConstraint("tenant_id", "tax_code", name="uq_tax_rules_tenant_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    tax_code = Column(String, index=True)
    tax_type = Column(String)
    rate_percent = Column(Float)
    payable_gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=True)
    payable_gl_account_code = Column(String, nullable=True)
    expense_gl_account_code = Column(String, nullable=True)
    is_active = Column(String, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxComputation(Base):
    __tablename__ = "tax_computations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    tax_rule_id = Column(String, ForeignKey("tax_rules.id"))
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    source_module = Column(String)
    source_reference = Column(String)
    taxable_amount = Column(Float)
    tax_amount = Column(Float)
    breakdown = Column(JSON, nullable=True)
    status = Column(String, default="computed")
    created_at = Column(DateTime, default=datetime.utcnow)


class PostingRule(Base):
    __tablename__ = "posting_rules"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    source_module = Column(String, index=True, nullable=False)
    source_event = Column(String, index=True, nullable=False)
    rule_name = Column(String, nullable=True)
    priority = Column(Float, default=100.0)
    status = Column(String, default="active", index=True)
    version = Column(Float, default=1.0)
    supersedes_rule_id = Column(String, nullable=True, index=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    requires_approval = Column(String, default="false")
    approval_status = Column(String, default="draft", index=True)
    maker_by = Column(String, nullable=True)
    checker_by = Column(String, nullable=True)
    finance_head_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    dependency_rule_ids = Column(JSON, nullable=True)
    rollback_strategy = Column(String, default="reverse_journal")
    debit_account_code = Column(String, nullable=True)
    credit_account_code = Column(String, nullable=True)
    posting_lines = Column(JSON, nullable=True)
    conditions = Column(JSON, nullable=True)
    description = Column(String, nullable=True)
    is_active = Column(String, default="true")
    created_by = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class PostingExecutionLog(Base):
    __tablename__ = "posting_execution_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    rule_id = Column(String, ForeignKey("posting_rules.id"), nullable=True, index=True)
    source_module = Column(String, index=True, nullable=False)
    source_event = Column(String, index=True, nullable=False)
    source_reference = Column(String, nullable=True, index=True)
    status = Column(String, default="success", index=True)
    execution_time_ms = Column(Float, default=0.0)
    journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    error_message = Column(String, nullable=True)
    input_payload = Column(JSON, nullable=True)
    generated_lines = Column(JSON, nullable=True)
    rollback_journal_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountingEvent(Base):
    __tablename__ = "accounting_events"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    source_module = Column(String, index=True, nullable=False)
    reference_id = Column(String, index=True, nullable=False)
    reference_number = Column(String, nullable=True, index=True)
    business_date = Column(DateTime, nullable=False, index=True)
    currency = Column(String, default="INR")
    amount = Column(Float, nullable=True)
    priority = Column(String, default="normal", index=True)
    status = Column(String, default="created", index=True)
    queue_status = Column(String, default="normal_queue", index=True)
    validation_status = Column(String, default="pending", index=True)
    validation_result = Column(JSON, nullable=True)
    dimensions = Column(JSON, nullable=True)
    payload = Column(JSON, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    version = Column(Integer, default=1)
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    dead_letter_reason = Column(String, nullable=True)
    posting_rule_id = Column(String, ForeignKey("posting_rules.id"), nullable=True)
    posting_execution_id = Column(String, ForeignKey("posting_execution_logs.id"), nullable=True)
    journal_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    processing_time_ms = Column(Float, default=0.0)
    created_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    performed_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccountingPeriod(Base):
    __tablename__ = "accounting_periods"
    __table_args__ = (
        UniqueConstraint("tenant_id", "financial_year", "period_name", name="uq_accounting_periods_tenant_period"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    financial_year = Column(String, index=True, nullable=False)
    period_name = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    branch_id = Column(String, nullable=True, index=True)
    status = Column(String, default="open", index=True)
    locked_by = Column(String, nullable=True)
    unlocked_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    unlock_requested_by = Column(String, nullable=True)
    lock_reason = Column(String, nullable=True)
    unlock_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class FinancialYear(Base):
    __tablename__ = "financial_years"
    __table_args__ = (
        UniqueConstraint("tenant_id", "year_code", name="uq_financial_years_tenant_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    year_code = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    calendar_type = Column(String, default="fiscal")
    status = Column(String, default="draft", index=True)
    calendars = Column(JSON, nullable=True)
    close_schedule = Column(JSON, nullable=True)
    created_by = Column(String, nullable=True)
    activated_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class SubLedgerEntry(Base):
    __tablename__ = "sub_ledger_entries"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    source_module = Column(String, nullable=False)
    source_event = Column(String, nullable=False)
    source_reference = Column(String, nullable=False)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="active", index=True)
    reversal_entry_id = Column(String, nullable=True, index=True)
    reversed_at = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Vendor(Base):
    __tablename__ = "ap_vendors"
    __table_args__ = (
        UniqueConstraint("tenant_id", "vendor_code", name="uq_ap_vendors_tenant_code"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    vendor_code = Column(String, index=True, nullable=False)
    vendor_name = Column(String, nullable=False)
    vendor_type = Column(String, default="supplier")
    status = Column(String, default="draft")
    payment_terms = Column(String, nullable=True)
    credit_limit = Column(Float, default=0.0)
    gst_number = Column(String, nullable=True)
    currency = Column(String, default="INR")
    branch_id = Column(String, nullable=True, index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class APInvoice(Base):
    __tablename__ = "ap_invoices"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_number", name="uq_ap_invoices_tenant_number"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    vendor_id = Column(String, ForeignKey("ap_vendors.id"), nullable=False, index=True)
    invoice_number = Column(String, index=True, nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    currency = Column(String, default="INR")
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="draft")
    branch_id = Column(String, nullable=True, index=True)
    reference = Column(String, nullable=True)
    description = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    vendor = relationship("Vendor")


class GLBalance(Base):
    __tablename__ = "gl_balances"
    __table_args__ = (
        UniqueConstraint("tenant_id", "gl_account_id", "branch_id", "currency", "financial_year", name="uq_gl_balances_scope"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=False)
    branch_id = Column(String, nullable=True, index=True)
    currency = Column(String, default="INR")
    financial_year = Column(String, nullable=False)
    opening_balance = Column(Float, default=0.0)
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    closing_balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Voucher(Base):
    __tablename__ = "vouchers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "voucher_number", name="uq_vouchers_tenant_number"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    voucher_number = Column(String, nullable=False, index=True)
    voucher_type = Column(String, nullable=False, index=True)
    voucher_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    reference = Column(String, nullable=True)
    branch_id = Column(String, nullable=True, index=True)
    currency = Column(String, default="INR")
    status = Column(String, default="draft", index=True)
    created_by = Column(String, nullable=True)
    verified_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    posted_journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)
    payment_mode = Column(String, nullable=True, index=True)
    payment_reference = Column(String, nullable=True)
    payment_details = Column(JSON, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("VoucherLine", back_populates="voucher")


class VoucherLine(Base):
    __tablename__ = "voucher_lines"

    id = Column(String, primary_key=True)
    voucher_id = Column(String, ForeignKey("vouchers.id"), nullable=False)
    gl_account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    department_id = Column(String, nullable=True)
    cost_center = Column(String, nullable=True)
    profit_center = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    employee_id = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    business_unit_id = Column(String, nullable=True)
    voucher = relationship("Voucher", back_populates="lines")


class DayEndClose(Base):
    __tablename__ = "day_end_closes"
    __table_args__ = (
        UniqueConstraint("tenant_id", "business_date", "branch_id", name="uq_day_end_tenant_date_branch"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    business_date = Column(DateTime, nullable=False)
    branch_id = Column(String, nullable=True, index=True)
    status = Column(String, default="closed")
    trial_balance_debit = Column(Float, default=0.0)
    trial_balance_credit = Column(Float, default=0.0)
    is_balanced = Column(String, default="true")
    checks = Column(JSON, nullable=True)
    closed_by = Column(String, nullable=True)
    closed_at = Column(DateTime, default=datetime.utcnow)


class TrialBalance(Base):
    __tablename__ = "trial_balances"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    scope = Column(String, default="enterprise")
    book = Column(String, default="primary")
    period = Column(String, nullable=True)
    currency = Column(String, default="INR")
    status = Column(String, default="balanced")
    generated_on = Column(DateTime, default=datetime.utcnow)
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    is_balanced = Column(String, default="true")
    validation_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("TrialBalanceLine", back_populates="trial_balance", cascade="all, delete-orphan")


class TrialBalanceLine(Base):
    __tablename__ = "trial_balance_lines"

    id = Column(String, primary_key=True)
    trial_balance_id = Column(String, ForeignKey("trial_balances.id"), nullable=False, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    account_id = Column(String, ForeignKey("gl_accounts.id"), nullable=True, index=True)
    account_code = Column(String, nullable=True, index=True)
    account_name = Column(String, nullable=True)
    account_type = Column(String, nullable=True)
    opening_debit = Column(Float, default=0.0)
    opening_credit = Column(Float, default=0.0)
    period_debit = Column(Float, default=0.0)
    period_credit = Column(Float, default=0.0)
    closing_debit = Column(Float, default=0.0)
    closing_credit = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    trial_balance = relationship("TrialBalance", back_populates="lines")


class TrialBalanceGenerateRequest(BaseModel):
    tenant_id: str
    scope: Optional[str] = "enterprise"
    book: Optional[str] = "primary"
    period: Optional[str] = None
    currency: Optional[str] = "INR"
    business_date: Optional[datetime] = None


class TrialBalanceLineResponse(BaseModel):
    id: str
    account_id: Optional[str] = None
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    opening_debit: float
    opening_credit: float
    period_debit: float
    period_credit: float
    closing_debit: float
    closing_credit: float

    class Config:
        from_attributes = True


class TrialBalanceResponse(BaseModel):
    id: str
    tenant_id: str
    scope: str
    book: str
    period: Optional[str] = None
    currency: str
    status: str
    generated_on: datetime
    total_debit: float
    total_credit: float
    is_balanced: str
    validation_summary: Optional[dict] = None
    rows: List[TrialBalanceLineResponse] = []

    class Config:
        from_attributes = True


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    statement_type = Column(String, nullable=False, index=True)
    scope = Column(String, default="enterprise")
    book = Column(String, default="primary")
    period = Column(String, nullable=True)
    currency = Column(String, default="INR")
    status = Column(String, default="generated")
    generated_on = Column(DateTime, default=datetime.utcnow)
    as_of = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lines = relationship("FinancialStatementLine", back_populates="financial_statement", cascade="all, delete-orphan")
    ratios = relationship("FinancialStatementRatio", back_populates="financial_statement", cascade="all, delete-orphan")


class FinancialStatementLine(Base):
    __tablename__ = "financial_statement_lines"

    id = Column(String, primary_key=True)
    financial_statement_id = Column(String, ForeignKey("financial_statements.id"), nullable=False, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    section = Column(String, nullable=True)
    label = Column(String, nullable=False)
    account_code = Column(String, nullable=True)
    amount = Column(Float, default=0.0)
    line_type = Column(String, default="summary")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    financial_statement = relationship("FinancialStatement", back_populates="lines")


class FinancialStatementRatio(Base):
    __tablename__ = "financial_statement_ratios"

    id = Column(String, primary_key=True)
    financial_statement_id = Column(String, ForeignKey("financial_statements.id"), nullable=False, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    ratio_name = Column(String, nullable=False)
    value = Column(Float, default=0.0)
    interpretation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    financial_statement = relationship("FinancialStatement", back_populates="ratios")


class FinancialStatementGenerateRequest(BaseModel):
    tenant_id: str
    statement_type: Optional[str] = "balance_sheet"
    scope: Optional[str] = "enterprise"
    book: Optional[str] = "primary"
    period: Optional[str] = None
    currency: Optional[str] = "INR"
    as_of: Optional[datetime] = None
    business_date: Optional[datetime] = None


class FinancialStatementLineResponse(BaseModel):
    id: str
    section: Optional[str] = None
    label: str
    account_code: Optional[str] = None
    amount: float
    line_type: Optional[str] = None
    order_index: int = 0

    class Config:
        from_attributes = True


class FinancialStatementRatioResponse(BaseModel):
    id: str
    ratio_name: str
    value: float
    interpretation: Optional[str] = None

    class Config:
        from_attributes = True


class FinancialStatementResponse(BaseModel):
    id: str
    tenant_id: str
    statement_type: str
    scope: str
    book: str
    period: Optional[str] = None
    currency: str
    status: str
    generated_on: datetime
    as_of: Optional[datetime] = None
    lines: List[FinancialStatementLineResponse] = []
    ratios: List[FinancialStatementRatioResponse] = []

    class Config:
        from_attributes = True


class GLAccountResponse(BaseModel):
    id: str
    tenant_id: str
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    base_currency: Optional[str] = None
    normal_balance: Optional[str] = None
    branch_id: Optional[str] = None
    branch_specific: Optional[str] = None
    posting_allowed: Optional[str] = None
    allow_manual_posting: Optional[str] = None
    allow_auto_posting: Optional[str] = None
    requires_approval: Optional[str] = None
    freeze_status: Optional[str] = None
    status: Optional[str] = None
    exchange_gain_loss_account_code: Optional[str] = None
    revaluation_account_code: Optional[str] = None
    opening_balance: Optional[float] = 0.0
    financial_year: Optional[str] = None
    balance: float

    class Config:
        from_attributes = True


class GLAccountCreate(BaseModel):
    tenant_id: str
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = "INR"
    base_currency: Optional[str] = "INR"
    normal_balance: Optional[str] = None
    branch_id: Optional[str] = None
    branch_specific: Optional[str] = "false"
    posting_allowed: Optional[str] = "true"
    allow_manual_posting: Optional[str] = "true"
    allow_auto_posting: Optional[str] = "true"
    requires_approval: Optional[str] = "false"
    freeze_status: Optional[str] = "open"
    status: Optional[str] = "active"
    exchange_gain_loss_account_code: Optional[str] = None
    revaluation_account_code: Optional[str] = None
    opening_balance: Optional[float] = 0.0
    financial_year: Optional[str] = None
    metadata: Optional[dict] = None


class GLAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    parent_account_id: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = None
    base_currency: Optional[str] = None
    normal_balance: Optional[str] = None
    branch_id: Optional[str] = None
    branch_specific: Optional[str] = None
    posting_allowed: Optional[str] = None
    allow_manual_posting: Optional[str] = None
    allow_auto_posting: Optional[str] = None
    requires_approval: Optional[str] = None
    freeze_status: Optional[str] = None
    status: Optional[str] = None
    exchange_gain_loss_account_code: Optional[str] = None
    revaluation_account_code: Optional[str] = None
    opening_balance: Optional[float] = None
    financial_year: Optional[str] = None
    metadata: Optional[dict] = None


class GLAccountStatusUpdate(BaseModel):
    tenant_id: str
    status: str
    performed_by: Optional[str] = None


class COASeedRequest(BaseModel):
    tenant_id: str
    currency: Optional[str] = "INR"
    financial_year: Optional[str] = None


class JournalLineCreate(BaseModel):
    gl_account_id: Optional[str] = None
    account_code: Optional[str] = None
    sequence: Optional[int] = None
    debit: float = 0.0
    credit: float = 0.0
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    transaction_currency: Optional[str] = None
    transaction_amount: Optional[float] = None
    exchange_rate: Optional[float] = None
    department_id: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    project_id: Optional[str] = None
    employee_id: Optional[str] = None
    product_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    tenant_id: str
    entry_date: Optional[datetime] = None
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    lines: List[JournalLineCreate]


class JournalEntryResponse(BaseModel):
    id: str
    tenant_id: str
    entry_date: datetime
    description: str
    reference: Optional[str] = None
    metadata: Optional[dict] = None
    posting_status: str
    idempotency_key: Optional[str] = None
    source_module: Optional[str] = None
    source_event: Optional[str] = None
    source_reference: Optional[str] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    voucher_id: Optional[str] = None
    batch_id: Optional[str] = None
    journal_no: Optional[str] = None
    voucher_type: Optional[str] = None
    period: Optional[str] = None
    currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    reversal_of: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    template_id: Optional[str] = None

    class Config:
        from_attributes = True


class PostingRuleLineCreate(BaseModel):
    account_code: str
    direction: str
    description: Optional[str] = None
    sequence: Optional[float] = None
    amount_source: Optional[str] = None
    percentage: Optional[float] = None
    formula: Optional[str] = None
    currency: Optional[str] = None
    dimension_source: Optional[dict] = None
    transaction_currency_source: Optional[str] = None
    exchange_rate_source: Optional[str] = None


class PostingRuleLineResponse(BaseModel):
    account_code: str
    direction: str
    description: Optional[str] = None
    sequence: Optional[float] = None
    amount_source: Optional[str] = None
    percentage: Optional[float] = None
    formula: Optional[str] = None
    currency: Optional[str] = None
    dimension_source: Optional[dict] = None
    transaction_currency_source: Optional[str] = None
    exchange_rate_source: Optional[str] = None


class PostingRuleConditionCreate(BaseModel):
    field: str
    operator: str
    value: Optional[Any] = None


class PostingRuleConditionResponse(BaseModel):
    field: str
    operator: str
    value: Optional[Any] = None


class PostingRuleCreate(BaseModel):
    tenant_id: str
    source_module: str
    source_event: str
    rule_name: Optional[str] = None
    priority: Optional[float] = 100.0
    status: Optional[str] = "draft"
    version: Optional[float] = 1.0
    supersedes_rule_id: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    requires_approval: Optional[str] = "true"
    dependency_rule_ids: Optional[List[str]] = None
    rollback_strategy: Optional[str] = "reverse_journal"
    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    description: Optional[str] = None
    lines: Optional[List[PostingRuleLineCreate]] = None
    conditions: Optional[List[PostingRuleConditionCreate]] = None
    created_by: Optional[str] = None
    metadata: Optional[dict] = None


class PostingRuleUpdate(BaseModel):
    source_module: Optional[str] = None
    source_event: Optional[str] = None
    rule_name: Optional[str] = None
    priority: Optional[float] = None
    status: Optional[str] = None
    version: Optional[float] = None
    supersedes_rule_id: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    requires_approval: Optional[str] = None
    dependency_rule_ids: Optional[List[str]] = None
    rollback_strategy: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    description: Optional[str] = None
    lines: Optional[List[PostingRuleLineCreate]] = None
    conditions: Optional[List[PostingRuleConditionCreate]] = None
    metadata: Optional[dict] = None
    performed_by: Optional[str] = None


class PostingRuleResponse(BaseModel):
    id: str
    tenant_id: str
    source_module: str
    source_event: str
    rule_name: Optional[str] = None
    priority: float = 100.0
    status: Optional[str] = None
    version: Optional[float] = None
    supersedes_rule_id: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    requires_approval: Optional[str] = None
    approval_status: Optional[str] = None
    maker_by: Optional[str] = None
    checker_by: Optional[str] = None
    finance_head_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    dependency_rule_ids: Optional[List[str]] = None
    rollback_strategy: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    description: Optional[str] = None
    is_active: str
    lines: List[PostingRuleLineResponse] = []
    conditions: List[PostingRuleConditionResponse] = []
    created_by: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class JournalAttachmentCreate(BaseModel):
    document_id: Optional[str] = None
    file_name: str
    uploaded_by: Optional[str] = None


class JournalDocumentCreate(BaseModel):
    tenant_id: str
    batch_id: Optional[str] = None
    posting_date: Optional[datetime] = None
    voucher_type: Optional[str] = "journal"
    source_module: Optional[str] = "manual"
    source_event: Optional[str] = "manual_journal"
    source_reference: Optional[str] = None
    description: str
    reference: Optional[str] = None
    currency: Optional[str] = "INR"
    exchange_rate: Optional[float] = 1.0
    branch_id: Optional[str] = None
    financial_year: Optional[str] = None
    template_id: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Optional[dict] = None
    lines: List[JournalLineCreate]
    attachments: Optional[List[JournalAttachmentCreate]] = None


class JournalDocumentUpdate(BaseModel):
    batch_id: Optional[str] = None
    posting_date: Optional[datetime] = None
    voucher_type: Optional[str] = None
    source_module: Optional[str] = None
    source_event: Optional[str] = None
    source_reference: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    currency: Optional[str] = None
    exchange_rate: Optional[float] = None
    branch_id: Optional[str] = None
    financial_year: Optional[str] = None
    template_id: Optional[str] = None
    metadata: Optional[dict] = None
    lines: Optional[List[JournalLineCreate]] = None
    attachments: Optional[List[JournalAttachmentCreate]] = None
    performed_by: Optional[str] = None


class JournalActionRequest(BaseModel):
    tenant_id: str
    journal_id: Optional[str] = None
    performed_by: Optional[str] = None
    remarks: Optional[str] = None


class JournalApprovalActionRequest(JournalActionRequest):
    level: Optional[str] = "checker"
    decision: Optional[str] = "approved"


class JournalValidationRequest(BaseModel):
    tenant_id: str
    journal_id: Optional[str] = None
    posting_date: Optional[datetime] = None
    source_module: Optional[str] = "manual"
    source_event: Optional[str] = "manual_journal"
    source_reference: Optional[str] = None
    branch_id: Optional[str] = None
    financial_year: Optional[str] = None
    currency: Optional[str] = "INR"
    exchange_rate: Optional[float] = 1.0
    metadata: Optional[dict] = None
    lines: Optional[List[JournalLineCreate]] = None


class JournalSimulationRequest(JournalValidationRequest):
    template_id: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None


class JournalTemplateCreate(BaseModel):
    tenant_id: str
    template_name: str
    description: Optional[str] = None
    voucher_type: Optional[str] = "journal"
    currency: Optional[str] = "INR"
    lines: List[dict]
    created_by: Optional[str] = None


class JournalBatchCreate(BaseModel):
    tenant_id: str
    posting_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    created_by: Optional[str] = None


class AccountingDimensionCreate(BaseModel):
    tenant_id: str
    dimension_type: str
    code: str
    name: str
    status: Optional[str] = "active"


class AccountingBudgetCreate(BaseModel):
    tenant_id: str
    financial_year: str
    period: str
    gl_account_id: str
    cost_center: Optional[str] = None
    amount: float


class PostingRuleSimulationRequest(BaseModel):
    tenant_id: str
    source_module: str
    source_event: str
    source_reference: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    branch_id: Optional[str] = None
    event_data: Optional[dict] = None


class PostingRuleDirectSimulationRequest(BaseModel):
    tenant_id: str
    source_reference: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = "INR"
    branch_id: Optional[str] = None
    event_data: Optional[dict] = None


class PostingRulePublishRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None


class PostingRuleApprovalRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None
    stage: Optional[str] = None
    comment: Optional[str] = None


class PostingRuleVersionRequest(PostingRuleUpdate):
    tenant_id: str


class ExecutionRollbackRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None
    reason: Optional[str] = None


class AccountingPeriodCreate(BaseModel):
    tenant_id: str
    financial_year: str
    period_name: str
    period_start: datetime
    period_end: datetime
    branch_id: Optional[str] = None
    status: Optional[str] = "open"
    performed_by: Optional[str] = None


class FinancialYearCreate(BaseModel):
    tenant_id: str
    year_code: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    calendar_type: Optional[str] = "fiscal"
    status: Optional[str] = "draft"
    calendars: Optional[List[str]] = None
    close_schedule: Optional[dict] = None
    generate_periods: Optional[str] = "true"
    performed_by: Optional[str] = None


class AccountingPeriodActionRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None
    reason: Optional[str] = None


class CalendarCloseExecutionRequest(BaseModel):
    tenant_id: str
    financial_year: Optional[str] = None
    period_id: Optional[str] = None
    business_date: Optional[datetime] = None
    branch_id: Optional[str] = None
    performed_by: Optional[str] = None
    reason: Optional[str] = None


class AccountingEventCreate(BaseModel):
    tenant_id: str
    event_type: str
    source_module: str
    reference_id: str
    reference_number: Optional[str] = None
    business_date: Optional[datetime] = None
    currency: Optional[str] = "INR"
    amount: Optional[float] = None
    priority: Optional[str] = "normal"
    dimensions: Optional[dict] = None
    payload: Optional[dict] = None
    metadata: Optional[dict] = None
    created_by: Optional[str] = None


class AccountingEventActionRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None
    reason: Optional[str] = None


class AccountingPeriodResponse(BaseModel):
    id: str
    tenant_id: str
    financial_year: str
    period_name: str
    period_start: datetime
    period_end: datetime
    branch_id: Optional[str] = None
    status: str
    locked_by: Optional[str] = None
    unlocked_by: Optional[str] = None
    approved_by: Optional[str] = None
    unlock_requested_by: Optional[str] = None
    lock_reason: Optional[str] = None
    unlock_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str
    entity: str
    entity_id: Optional[str] = None
    action: str
    payload: Optional[dict] = None
    performed_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubLedgerEntryResponse(BaseModel):
    id: str
    tenant_id: str
    source_module: str
    source_event: str
    source_reference: str
    journal_entry_id: Optional[str] = None
    amount: float
    status: Optional[str] = None
    reversal_entry_id: Optional[str] = None
    reversed_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubLedgerSummaryItem(BaseModel):
    source_module: str
    ledger_name: str
    transaction_count: int
    total_amount: float
    last_entry_at: Optional[datetime] = None
    rollup_to: str = "General Ledger"


class BankTransactionCreate(BaseModel):
    tenant_id: str
    reference: str
    transaction_date: datetime
    amount: float
    description: str



class AutomatedGLPostingRequest(BaseModel):
    tenant_id: str
    idempotency_key: Optional[str] = None
    source_module: str
    source_event: str
    source_reference: str
    amount: float
    description: Optional[str] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    currency: Optional[str] = "INR"

    debit_account_code: Optional[str] = None
    credit_account_code: Optional[str] = None
    metadata: Optional[dict] = None


class TaxRuleCreate(BaseModel):
    tenant_id: str
    tax_code: str
    tax_type: str
    rate_percent: float
    payable_gl_account_id: Optional[str] = None
    payable_gl_account_code: Optional[str] = None
    expense_gl_account_code: Optional[str] = None


class TaxRuleResponse(BaseModel):
    id: str
    tenant_id: str
    tax_code: str
    tax_type: str
    rate_percent: float
    payable_gl_account_id: Optional[str]
    payable_gl_account_code: Optional[str]
    expense_gl_account_code: Optional[str]
    is_active: str

    class Config:
        from_attributes = True


class TaxComputationRequest(BaseModel):
    tenant_id: str
    tax_code: str
    source_module: str
    source_reference: str
    taxable_amount: float


class TaxComputationResponse(BaseModel):
    id: str
    tenant_id: str
    journal_entry_id: Optional[str]
    source_module: str
    source_reference: str
    taxable_amount: float
    tax_amount: float
    breakdown: Optional[dict]
    status: str

    class Config:
        from_attributes = True


class ReconciliationRequest(BaseModel):
    tenant_id: str
    transaction_id: str
    journal_entry_id: str


class BankStatementResponse(BaseModel):
    id: str
    reference: str
    transaction_date: datetime
    amount: float
    description: str
    status: str

    class Config:
        from_attributes = True


class PostingEngineLine(BaseModel):
    gl_account_id: Optional[str] = None
    account_code: Optional[str] = None
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    transaction_currency: Optional[str] = None
    transaction_amount: Optional[float] = None
    exchange_rate: Optional[float] = None
    department_id: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    project_id: Optional[str] = None
    employee_id: Optional[str] = None
    product_id: Optional[str] = None
    business_unit_id: Optional[str] = None


class PostingValidationRequest(BaseModel):
    tenant_id: str
    source_module: Optional[str] = None
    source_event: Optional[str] = None
    source_reference: Optional[str] = None
    lines: List[PostingEngineLine]


class PostingEngineRequest(BaseModel):
    tenant_id: str
    source_module: str
    source_event: str
    source_reference: str
    description: Optional[str] = None
    idempotency_key: Optional[str] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    currency: Optional[str] = "INR"
    metadata: Optional[dict] = None
    lines: List[PostingEngineLine]


class PostingEnginePostResponse(JournalEntryResponse):
    pipeline: Optional[dict] = None


class VoucherLineCreate(BaseModel):
    gl_account_id: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    department_id: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    project_id: Optional[str] = None
    employee_id: Optional[str] = None
    product_id: Optional[str] = None
    business_unit_id: Optional[str] = None


class VoucherLineResponse(BaseModel):
    gl_account_id: str
    debit: float
    credit: float
    description: Optional[str] = None
    department_id: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    project_id: Optional[str] = None
    employee_id: Optional[str] = None
    product_id: Optional[str] = None
    business_unit_id: Optional[str] = None

    class Config:
        from_attributes = True


class VoucherCreate(BaseModel):
    tenant_id: str
    voucher_type: str
    voucher_date: Optional[datetime] = None
    description: str
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    metadata: Optional[dict] = None
    lines: List[VoucherLineCreate]


class PaymentVoucherCreate(BaseModel):
    tenant_id: str
    payment_category: str
    amount: float
    payee_name: str
    vendor_id: Optional[str] = None
    vendor_code: Optional[str] = None
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    payment_mode: str = "cash"
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class VendorCreate(BaseModel):
    tenant_id: str
    vendor_code: str
    vendor_name: str
    vendor_type: Optional[str] = "supplier"
    status: Optional[str] = "draft"
    payment_terms: Optional[str] = None
    credit_limit: Optional[float] = 0.0
    gst_number: Optional[str] = None
    currency: Optional[str] = "INR"
    branch_id: Optional[str] = None
    metadata: Optional[dict] = None
    created_by: Optional[str] = None


class VendorResponse(BaseModel):
    id: str
    tenant_id: str
    vendor_code: str
    vendor_name: str
    vendor_type: str
    status: str
    payment_terms: Optional[str] = None
    credit_limit: float
    gst_number: Optional[str] = None
    currency: str
    branch_id: Optional[str] = None
    metadata: Optional[dict] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APInvoiceCreate(BaseModel):
    tenant_id: str
    vendor_id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    total_amount: float
    currency: Optional[str] = "INR"
    description: Optional[str] = None
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    status: Optional[str] = "draft"
    created_by: Optional[str] = None
    metadata: Optional[dict] = None


class APInvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    vendor_id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    total_amount: float
    currency: str
    status: str
    description: Optional[str] = None
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APVendorLedgerResponse(BaseModel):
    tenant_id: str
    vendor: VendorResponse
    total_invoices: int
    total_payments: float
    outstanding_balance: float
    invoices: List[APInvoiceResponse]
    subledger_entries: List[SubLedgerEntryResponse]


class ReceiptVoucherCreate(BaseModel):
    tenant_id: str
    receipt_category: str = "customer_payments"
    amount: float
    payer_name: str
    customer_id: Optional[str] = None
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    payment_mode: str = "cash"
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class ContraVoucherCreate(BaseModel):
    tenant_id: str
    transfer_type: str
    amount: float
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    transfer_reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    transfer_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class CreditNoteCreate(BaseModel):
    tenant_id: str
    credit_note_type: str
    amount: float
    customer_name: str
    customer_id: Optional[str] = None
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    credit_note_reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    credit_note_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class DebitNoteCreate(BaseModel):
    tenant_id: str
    debit_note_type: str
    amount: float
    customer_name: str
    customer_id: Optional[str] = None
    voucher_date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    debit_note_reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: Optional[str] = "INR"
    debit_note_details: Optional[dict] = None
    created_by: Optional[str] = None
    debit_account_id: Optional[str] = None
    debit_account_code: Optional[str] = None
    credit_account_id: Optional[str] = None
    credit_account_code: Optional[str] = None
    cost_center: Optional[str] = None
    profit_center: Optional[str] = None
    metadata: Optional[dict] = None


class VoucherActionRequest(BaseModel):
    tenant_id: str
    performed_by: Optional[str] = None


class VoucherResponse(BaseModel):
    id: str
    tenant_id: str
    voucher_number: str
    voucher_type: str
    voucher_date: datetime
    description: str
    reference: Optional[str] = None
    branch_id: Optional[str] = None
    currency: str
    status: str
    posted_journal_entry_id: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_details: Optional[dict] = None
    created_by: Optional[str] = None
    verified_by: Optional[str] = None
    approved_by: Optional[str] = None
    lines: List[VoucherLineResponse] = []
    payment_category: Optional[str] = None
    receipt_category: Optional[str] = None
    contra_transfer_type: Optional[str] = None
    credit_note_type: Optional[str] = None
    debit_note_type: Optional[str] = None
    payee_name: Optional[str] = None
    payer_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    transfer_reference: Optional[str] = None
    credit_note_reference: Optional[str] = None
    debit_note_reference: Optional[str] = None
    amount: Optional[float] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class DayEndCloseRequest(BaseModel):
    tenant_id: str
    business_date: datetime
    branch_id: Optional[str] = None
    closed_by: Optional[str] = None


class DayEndCloseResponse(BaseModel):
    id: str
    tenant_id: str
    business_date: datetime
    branch_id: Optional[str] = None
    status: str
    trial_balance_debit: float
    trial_balance_credit: float
    is_balanced: str
    checks: Optional[dict] = None
    closed_by: Optional[str] = None
    closed_at: datetime

    class Config:
        from_attributes = True


class AccountingQuickActionRequest(BaseModel):
    tenant_id: str
    action_type: str
    amount: float
    description: Optional[str] = None
    party_name: Optional[str] = None
    source_reference: Optional[str] = None
    branch_id: Optional[str] = None
    business_date: Optional[datetime] = None
    currency: Optional[str] = "INR"
    performed_by: Optional[str] = None
    metadata: Optional[dict] = None


from app.accounts_receivable.routes import router as ar_router
from app.budgeting.routes import router as budgeting_router
from app.cash_bank.routes import router as cash_bank_router
from app.fixed_assets.routes import router as fixed_assets_router

app = FastAPI(title="accounting-service", version="0.1.0")
app.include_router(ar_router, prefix="/api/v1/ar")
app.include_router(cash_bank_router, prefix="/api/v1")
app.include_router(fixed_assets_router)
app.include_router(budgeting_router)


def get_db() -> Session:
    from app.db import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DEFAULT_POSTING_MAP = {
    ("loans", "disbursement"): ("1200_LOAN_RECEIVABLE", "1000_CASH"),
    ("loans", "payment"): ("1000_CASH", "1200_LOAN_RECEIVABLE"),
    ("deposits", "deposit"): ("1000_CASH", "2200_CUSTOMER_DEPOSITS"),
    ("deposits", "withdrawal"): ("2200_CUSTOMER_DEPOSITS", "1000_CASH"),
    ("forex", "transaction"): ("1000_CASH", "4100_FOREX_INCOME"),
    ("gold", "disbursement"): ("1210_GOLD_LOAN_RECEIVABLE", "1000_CASH"),
}

SUB_LEDGER_LEDGER_MAP = {
    "loans": "Customer Loan Ledger",
    "deposit": "Deposit Ledger",
    "deposits": "Deposit Ledger",
    "gold": "Gold Loan Ledger",
    "forex": "Forex Ledger",
    "vendor": "Vendor Ledger",
    "employee": "Employee Ledger",
}

DEFAULT_ACCOUNT_NAMES = {
    "1000_CASH": ("Cash", "asset"),
    "1110_BRANCH_CASH": ("Branch Cash", "asset"),
    "1120_BANK": ("Bank Account", "asset"),
    "1130_VAULT_CASH": ("Vault Cash", "asset"),
    "1200_LOAN_RECEIVABLE": ("Loan Receivable", "asset"),
    "1210_GOLD_LOAN_RECEIVABLE": ("Gold Loan Receivable", "asset"),
    "1500_TREASURY": ("Treasury Account", "asset"),
    "2200_CUSTOMER_DEPOSITS": ("Customer Deposit Liability", "liability"),
    "2300_GST_PAYABLE": ("GST Payable", "liability"),
    "2310_TDS_PAYABLE": ("TDS Payable", "liability"),
    "2400_VENDOR_PAYABLE": ("Vendor Payable", "liability"),
    "2500_CUSTOMER_CREDIT_PAYABLE": ("Customer Credit Payable", "liability"),
    "4100_FOREX_INCOME": ("Forex Income", "revenue"),
    "4110_INTEREST_REVERSAL": ("Interest Reversal", "expense"),
    "4120_PENALTY_INCOME": ("Penalty Income", "revenue"),
    "4130_CHARGES_INCOME": ("Charges Income", "revenue"),
    "4140_RECOVERY_INCOME": ("Recovery Income", "revenue"),
    "5100_OPERATING_EXPENSE": ("Operating Expense", "expense"),
    "5110_RENT_EXPENSE": ("Rent Expense", "expense"),
    "5120_ELECTRICITY_EXPENSE": ("Electricity Expense", "expense"),
    "5130_INSURANCE_EXPENSE": ("Insurance Expense", "expense"),
    "5200_TAX_EXPENSE": ("Tax Expense", "expense"),
    "5210_SALARY_EXPENSE": ("Salary Expense", "expense"),
    "5300_REFUND_EXPENSE": ("Refund Expense", "expense"),
    "5400_ADJUSTMENT_EXPENSE": ("Adjustment Expense", "expense"),
    "5500_DISCOUNT_ALLOWED": ("Discount Allowed", "expense"),
}

PAYMENT_VOUCHER_CATEGORIES = {
    "vendor_payments": {
        "label": "Vendor payments",
        "debit_account_code": "2400_VENDOR_PAYABLE",
        "description": "Vendor payment",
    },
    "salary": {
        "label": "Salary",
        "debit_account_code": "5210_SALARY_EXPENSE",
        "description": "Salary payment",
    },
    "rent": {
        "label": "Rent",
        "debit_account_code": "5110_RENT_EXPENSE",
        "description": "Rent payment",
    },
    "electricity": {
        "label": "Electricity",
        "debit_account_code": "5120_ELECTRICITY_EXPENSE",
        "description": "Electricity payment",
    },
    "tax": {
        "label": "Tax",
        "debit_account_code": "2300_GST_PAYABLE",
        "description": "Tax payment",
    },
    "insurance": {
        "label": "Insurance",
        "debit_account_code": "5130_INSURANCE_EXPENSE",
        "description": "Insurance payment",
    },
}

RECEIPT_PAYMENT_MODES = ["cash", "cheque", "upi", "rtgs", "neft", "imps"]

RECEIPT_VOUCHER_CATEGORIES = {
    "customer_payments": {
        "label": "Customer payments",
        "credit_account_code": "1200_LOAN_RECEIVABLE",
        "description": "Customer payment receipt",
    },
}

CONTRA_TRANSFER_TYPES = {
    "cash_to_bank": {
        "label": "Cash to Bank",
        "debit_account_code": "1120_BANK",
        "credit_account_code": "1000_CASH",
        "source_label": "Cash",
        "destination_label": "Bank",
        "description": "Cash deposited to bank",
    },
    "bank_to_cash": {
        "label": "Bank to Cash",
        "debit_account_code": "1000_CASH",
        "credit_account_code": "1120_BANK",
        "source_label": "Bank",
        "destination_label": "Cash",
        "description": "Cash withdrawn from bank",
    },
    "vault_to_branch": {
        "label": "Vault to Branch",
        "debit_account_code": "1110_BRANCH_CASH",
        "credit_account_code": "1130_VAULT_CASH",
        "source_label": "Vault",
        "destination_label": "Branch",
        "description": "Cash moved from vault to branch",
    },
    "branch_to_treasury": {
        "label": "Branch to Treasury",
        "debit_account_code": "1500_TREASURY",
        "credit_account_code": "1110_BRANCH_CASH",
        "source_label": "Branch",
        "destination_label": "Treasury",
        "description": "Cash moved from branch to treasury",
    },
}

CREDIT_NOTE_TYPES = {
    "interest_reversal": {
        "label": "Interest Reversal",
        "debit_account_code": "4110_INTEREST_REVERSAL",
        "credit_account_code": "1200_LOAN_RECEIVABLE",
        "description": "Interest reversal credit note",
    },
    "refund": {
        "label": "Refund",
        "debit_account_code": "5300_REFUND_EXPENSE",
        "credit_account_code": "2500_CUSTOMER_CREDIT_PAYABLE",
        "description": "Customer refund credit note",
    },
    "adjustment": {
        "label": "Adjustment",
        "debit_account_code": "5400_ADJUSTMENT_EXPENSE",
        "credit_account_code": "1200_LOAN_RECEIVABLE",
        "description": "Customer account adjustment credit note",
    },
    "discount": {
        "label": "Discount",
        "debit_account_code": "5500_DISCOUNT_ALLOWED",
        "credit_account_code": "1200_LOAN_RECEIVABLE",
        "description": "Discount allowed credit note",
    },
}

DEBIT_NOTE_TYPES = {
    "penalty": {
        "label": "Penalty",
        "debit_account_code": "1200_LOAN_RECEIVABLE",
        "credit_account_code": "4120_PENALTY_INCOME",
        "description": "Penalty debit note",
    },
    "charges": {
        "label": "Charges",
        "debit_account_code": "1200_LOAN_RECEIVABLE",
        "credit_account_code": "4130_CHARGES_INCOME",
        "description": "Charges debit note",
    },
    "recovery": {
        "label": "Recovery",
        "debit_account_code": "1200_LOAN_RECEIVABLE",
        "credit_account_code": "4140_RECOVERY_INCOME",
        "description": "Recovery debit note",
    },
    "tax_adjustment": {
        "label": "Tax Adjustment",
        "debit_account_code": "1200_LOAN_RECEIVABLE",
        "credit_account_code": "2300_GST_PAYABLE",
        "description": "Tax adjustment debit note",
    },
}

DEFAULT_NBFC_COA = [
    {"account_code": "100000", "account_name": "Assets", "account_type": "asset", "category": "Assets", "posting_allowed": "false"},
    {"account_code": "110000", "account_name": "Cash", "account_type": "asset", "category": "Assets", "parent_code": "100000", "posting_allowed": "false"},
    {"account_code": "111000", "account_name": "Branch Cash", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "1110_BRANCH_CASH", "account_name": "Branch Cash Transfer", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "112000", "account_name": "Vault Cash", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "1130_VAULT_CASH", "account_name": "Vault Cash Transfer", "account_type": "asset", "category": "Assets", "parent_code": "110000"},
    {"account_code": "120000", "account_name": "Loans", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "130000", "account_name": "Gold Loan", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "140000", "account_name": "Deposits", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "150000", "account_name": "Treasury", "account_type": "asset", "category": "Assets", "parent_code": "100000"},
    {"account_code": "1500_TREASURY", "account_name": "Treasury Transfer", "account_type": "asset", "category": "Assets", "parent_code": "150000"},
    {"account_code": "200000", "account_name": "Liabilities", "account_type": "liability", "category": "Liabilities", "posting_allowed": "false"},
    {"account_code": "210000", "account_name": "Customer Deposits", "account_type": "liability", "category": "Liabilities", "parent_code": "200000"},
    {"account_code": "220000", "account_name": "Borrowings", "account_type": "liability", "category": "Liabilities", "parent_code": "200000"},
    {"account_code": "2500_CUSTOMER_CREDIT_PAYABLE", "account_name": "Customer Credit Payable", "account_type": "liability", "category": "Liabilities", "parent_code": "200000"},
    {"account_code": "300000", "account_name": "Capital", "account_type": "equity", "category": "Capital", "posting_allowed": "false"},
    {"account_code": "310000", "account_name": "Share Capital", "account_type": "equity", "category": "Capital", "parent_code": "300000"},
    {"account_code": "400000", "account_name": "Income", "account_type": "revenue", "category": "Income", "posting_allowed": "false"},
    {"account_code": "410000", "account_name": "Interest Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "4120_PENALTY_INCOME", "account_name": "Penalty Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "4130_CHARGES_INCOME", "account_name": "Charges Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "4140_RECOVERY_INCOME", "account_name": "Recovery Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "420000", "account_name": "Processing Fee Income", "account_type": "revenue", "category": "Income", "parent_code": "400000"},
    {"account_code": "500000", "account_name": "Expenses", "account_type": "expense", "category": "Expenses", "posting_allowed": "false"},
    {"account_code": "510000", "account_name": "Operating Expenses", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "5110_RENT_EXPENSE", "account_name": "Rent Expense", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "5120_ELECTRICITY_EXPENSE", "account_name": "Electricity Expense", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "5130_INSURANCE_EXPENSE", "account_name": "Insurance Expense", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "4110_INTEREST_REVERSAL", "account_name": "Interest Reversal", "account_type": "expense", "category": "Expenses", "parent_code": "510000"},
    {"account_code": "520000", "account_name": "Employee Expenses", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "5210_SALARY_EXPENSE", "account_name": "Salary Expense", "account_type": "expense", "category": "Expenses", "parent_code": "520000"},
    {"account_code": "5300_REFUND_EXPENSE", "account_name": "Refund Expense", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "5400_ADJUSTMENT_EXPENSE", "account_name": "Adjustment Expense", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "5500_DISCOUNT_ALLOWED", "account_name": "Discount Allowed", "account_type": "expense", "category": "Expenses", "parent_code": "500000"},
    {"account_code": "900000", "account_name": "Off Balance Sheet", "account_type": "off_balance", "category": "Off Balance Sheet", "posting_allowed": "false"},
    {"account_code": "910000", "account_name": "Guarantees", "account_type": "off_balance", "category": "Off Balance Sheet", "parent_code": "900000"},
    {"account_code": "990000", "account_name": "Memo Accounts", "account_type": "memo", "category": "Memo Accounts", "posting_allowed": "false"},
]


def _current_financial_year(moment: Optional[datetime] = None) -> str:
    value = moment or datetime.utcnow()
    start_year = value.year if value.month >= 4 else value.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _is_truthy(value: Optional[str]) -> bool:
    return str(value or "").lower() in {"true", "1", "yes", "active", "allowed"}


def _json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _period_response(period: AccountingPeriod) -> dict:
    return {
        "id": period.id,
        "tenant_id": period.tenant_id,
        "financial_year": period.financial_year,
        "period_name": period.period_name,
        "period_start": period.period_start,
        "period_end": period.period_end,
        "branch_id": period.branch_id,
        "status": period.status,
        "locked_by": period.locked_by,
        "unlocked_by": period.unlocked_by,
        "approved_by": period.approved_by,
        "unlock_requested_by": period.unlock_requested_by,
        "lock_reason": period.lock_reason,
        "unlock_reason": period.unlock_reason,
        "created_at": period.created_at,
        "updated_at": period.updated_at,
    }


def _financial_year_response(year: FinancialYear) -> dict:
    return {
        "id": year.id,
        "tenant_id": year.tenant_id,
        "year_code": year.year_code,
        "description": year.description,
        "start_date": year.start_date,
        "end_date": year.end_date,
        "calendar_type": year.calendar_type,
        "status": year.status,
        "calendars": year.calendars or [],
        "close_schedule": year.close_schedule or {},
        "created_by": year.created_by,
        "activated_by": year.activated_by,
        "created_at": year.created_at,
        "updated_at": year.updated_at,
    }


def _month_period_bounds(start_date: datetime, end_date: datetime) -> list[tuple[datetime, datetime]]:
    periods: list[tuple[datetime, datetime]] = []
    cursor = start_date
    while cursor <= end_date:
        if cursor.month == 12:
            next_month = datetime(cursor.year + 1, 1, 1)
        else:
            next_month = datetime(cursor.year, cursor.month + 1, 1)
        period_end = min(next_month - timedelta(seconds=1), end_date)
        periods.append((cursor, period_end))
        cursor = next_month
    return periods


def _generate_financial_year_periods(db: Session, year: FinancialYear, performed_by: Optional[str] = None) -> list[AccountingPeriod]:
    created: list[AccountingPeriod] = []
    for start, end in _month_period_bounds(year.start_date, year.end_date):
        period_name = start.strftime("%B %Y")
        existing = (
            db.query(AccountingPeriod)
            .filter(
                AccountingPeriod.tenant_id == year.tenant_id,
                AccountingPeriod.financial_year == year.year_code,
                AccountingPeriod.period_name == period_name,
            )
            .first()
        )
        if existing:
            continue
        status = "open" if start <= datetime.utcnow() <= end else "future"
        period = AccountingPeriod(
            id=str(uuid4()),
            tenant_id=year.tenant_id,
            financial_year=year.year_code,
            period_name=period_name,
            period_start=start,
            period_end=end,
            status=status,
        )
        db.add(period)
        _log_audit(db, year.tenant_id, "accounting_period", period.id, "generate", _period_response(period), performed_by)
        created.append(period)
    return created


def _calendar_period_item(period: AccountingPeriod) -> dict:
    response = _period_response(period)
    response["state"] = period.status
    response["posting_window"] = {
        "posting_allowed_from": period.period_start,
        "posting_allowed_to": period.period_end + timedelta(days=5),
        "late_adjustments_allowed": period.status in {"open", "soft_close"},
    }
    response["close_checklist"] = [
        {"key": "pending_transactions", "label": "Pending Transactions", "status": "passed" if period.status in {"soft_close", "hard_close", "archived", "locked"} else "pending"},
        {"key": "gl_balanced", "label": "GL Balanced", "status": "passed" if period.status in {"hard_close", "archived", "locked"} else "pending"},
        {"key": "approval", "label": "Close Approval", "status": "passed" if period.status in {"hard_close", "archived", "locked"} else "pending"},
    ]
    response["ai"] = {
        "close_readiness": 95 if period.status in {"hard_close", "archived", "locked"} else 72 if period.status == "soft_close" else 48,
        "delay_prediction": "low" if period.status in {"hard_close", "archived", "locked"} else "medium",
        "recommendation": "Proceed to next close stage." if period.status in {"open", "soft_close"} else "Monitor reopen requests and audit exceptions.",
    }
    return response


def _calendar_dashboard_payload(tenant_id: str, db: Session) -> dict:
    now = datetime.utcnow()
    years = db.query(FinancialYear).filter(FinancialYear.tenant_id == tenant_id).all()
    periods = db.query(AccountingPeriod).filter(AccountingPeriod.tenant_id == tenant_id).all()
    closes = db.query(DayEndClose).filter(DayEndClose.tenant_id == tenant_id).all()
    current_year = next((year for year in years if year.start_date <= now <= year.end_date), None)
    if not current_year and years:
        current_year = sorted(years, key=lambda item: item.start_date, reverse=True)[0]
    closed_states = {"soft_close", "hard_close", "archived", "locked", "closed"}
    by_status: dict[str, int] = {}
    for period in periods:
        by_status[period.status or "unknown"] = by_status.get(period.status or "unknown", 0) + 1
    hard_closed = sum(1 for period in periods if (period.status or "").lower() in {"hard_close", "archived", "locked", "closed"})
    health = 0 if not periods else round((hard_closed + sum(1 for period in periods if period.status == "open") * 0.6) / len(periods) * 100)
    return {
        "tenant_id": tenant_id,
        "current_financial_year": _financial_year_response(current_year) if current_year else None,
        "kpis": {
            "current_financial_year": current_year.year_code if current_year else "-",
            "open_periods": sum(1 for period in periods if period.status == "open"),
            "closed_periods": sum(1 for period in periods if period.status in closed_states),
            "pending_eod": max(0, sum(1 for period in periods if period.status == "open") - len(closes)),
            "pending_eom": sum(1 for period in periods if period.status == "open" and period.period_end < now),
            "pending_eoy": 1 if current_year and current_year.end_date < now and current_year.status != "archived" else 0,
            "late_journals": db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id, JournalEntry.posting_status != "posted").count(),
            "calendar_exceptions": sum(1 for period in periods if period.status == "pending_unlock"),
            "calendar_health": health,
        },
        "charts": {
            "period_status": [{"label": key, "value": value} for key, value in sorted(by_status.items())],
            "close_progress": [
                {"label": "Hard Closed", "value": hard_closed},
                {"label": "In Progress", "value": sum(1 for period in periods if period.status in {"open", "soft_close"})},
                {"label": "Future", "value": sum(1 for period in periods if period.status == "future")},
            ],
            "closing_sla": [
                {"label": "On Time", "value": max(0, len(closes) - sum(1 for close in closes if close.status != "closed"))},
                {"label": "Exceptions", "value": sum(1 for close in closes if close.status != "closed")},
            ],
        },
        "summary": {
            "status": "setup-required" if not years else "attention" if health < 70 else "controlled",
            "message": "Create a financial year and generate periods." if not years else "Close orchestration is ready for period governance.",
        },
    }


def _normalize_event_source(event_type: str, source_module: str, payload: Optional[dict] = None) -> tuple[str, str]:
    payload = payload or {}
    module = str(source_module or payload.get("sourceModule") or payload.get("source_module") or "").strip().lower().replace(" ", "_")
    module_aliases = {
        "loan": "loans",
        "lending": "loans",
        "deposit": "deposits",
        "gold_loan": "gold",
        "hr": "hrms",
        "human_resources": "hrms",
    }
    module = module_aliases.get(module, module)
    explicit_event = payload.get("source_event") or payload.get("sourceEvent")
    if explicit_event:
        return module, str(explicit_event).strip().lower().replace(" ", "_")
    normalized_type = str(event_type or "").strip().lower().replace(" ", "_")
    event_aliases = {
        "loan_disbursed": "disbursement",
        "loan_released": "disbursement",
        "emi_paid": "payment",
        "loan_payment": "payment",
        "fd_opened": "deposit",
        "deposit_opened": "deposit",
        "currency_purchased": "transaction",
        "currency_sold": "transaction",
        "gold_loan_released": "disbursement",
        "salary_paid": "salary_payment",
        "salary_processed": "salary_payment",
    }
    return module, event_aliases.get(normalized_type, normalized_type)


def _accounting_event_response(event: AccountingEvent) -> dict:
    return {
        "id": event.id,
        "event_id": event.id,
        "tenant_id": event.tenant_id,
        "event_type": event.event_type,
        "source_module": event.source_module,
        "reference_id": event.reference_id,
        "reference_number": event.reference_number,
        "business_date": event.business_date,
        "currency": event.currency,
        "amount": event.amount,
        "priority": event.priority,
        "status": event.status,
        "queue_status": event.queue_status,
        "validation_status": event.validation_status,
        "validation_result": event.validation_result,
        "dimensions": event.dimensions or {},
        "payload": event.payload or {},
        "metadata": event.metadata_json or {},
        "version": event.version,
        "retry_count": event.retry_count,
        "next_retry_at": event.next_retry_at,
        "dead_letter_reason": event.dead_letter_reason,
        "posting_rule_id": event.posting_rule_id,
        "posting_execution_id": event.posting_execution_id,
        "journal_id": event.journal_id,
        "processing_time_ms": event.processing_time_ms,
        "created_by": event.created_by,
        "approved_by": event.approved_by,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
        "posted_at": event.posted_at,
    }


def _validate_accounting_event(event: AccountingEvent, db: Session) -> dict:
    started_at = datetime.utcnow()
    checks: list[dict] = []
    errors: list[str] = []
    warnings: list[str] = []

    mandatory_fields = {
        "event_type": event.event_type,
        "source_module": event.source_module,
        "reference_id": event.reference_id,
        "business_date": event.business_date,
        "currency": event.currency,
    }
    missing = [field for field, value in mandatory_fields.items() if value in {None, ""}]
    if missing:
        errors.append(f"Missing mandatory fields: {', '.join(missing)}")
    checks.append({"key": "mandatory_fields", "label": "Mandatory fields", "status": "failed" if missing else "passed", "detail": ", ".join(missing) if missing else None})

    if event.amount is not None and event.amount < 0:
        errors.append("amount must not be negative")
    if event.amount is None:
        warnings.append("amount is not supplied; posting simulation may be unavailable")
    checks.append({"key": "amount", "label": "Amount", "status": "failed" if event.amount is not None and event.amount < 0 else "warning" if event.amount is None else "passed"})

    duplicate = (
        db.query(AccountingEvent)
        .filter(
            AccountingEvent.tenant_id == event.tenant_id,
            AccountingEvent.event_type == event.event_type,
            AccountingEvent.source_module == event.source_module,
            AccountingEvent.reference_id == event.reference_id,
            AccountingEvent.id != event.id,
            AccountingEvent.status.notin_(["archived", "cancelled"]),
        )
        .first()
    )
    if duplicate:
        errors.append(f"Duplicate event risk: {duplicate.id}")
    checks.append({"key": "duplicate_detection", "label": "Duplicate detection", "status": "failed" if duplicate else "passed", "detail": duplicate.id if duplicate else None})

    try:
        _assert_period_open(db, event.tenant_id, event.business_date, branch_id=(event.dimensions or {}).get("branch_id"))
        checks.append({"key": "accounting_period", "label": "Accounting period", "status": "passed"})
    except HTTPException as exc:
        errors.append(str(exc.detail))
        checks.append({"key": "accounting_period", "label": "Accounting period", "status": "failed", "detail": exc.detail})

    dimensions = event.dimensions or {}
    recommended_dimensions = ["legal_entity", "business_unit", "branch_id", "cost_center", "product_id", "currency"]
    missing_dimensions = [dimension for dimension in recommended_dimensions if not dimensions.get(dimension) and dimension != "currency"]
    if missing_dimensions:
        warnings.append(f"Missing recommended dimensions: {', '.join(missing_dimensions)}")
    checks.append({"key": "dimensions", "label": "Dimensions", "status": "warning" if missing_dimensions else "passed", "detail": ", ".join(missing_dimensions) if missing_dimensions else None})

    rule_source_module, rule_source_event = _normalize_event_source(event.event_type, event.source_module, event.payload)
    rule_event_data = {"amount": event.amount or 0.0, **(event.payload or {}), **(event.metadata_json or {})}
    rule = _find_posting_rule(db, event.tenant_id, rule_source_module, rule_source_event, rule_event_data)
    default_map_exists = (rule_source_module, rule_source_event) in DEFAULT_POSTING_MAP
    if not rule and not default_map_exists:
        errors.append(f"No posting rule or default map for {rule_source_module}.{rule_source_event}")
    checks.append(
        {
            "key": "posting_rule",
            "label": "Posting rule",
            "status": "passed" if rule or default_map_exists else "failed",
            "detail": rule.rule_name if rule else "Default map" if default_map_exists else f"{rule_source_module}.{rule_source_event}",
        }
    )

    status = "passed" if not errors else "failed"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "normalized_source_module": rule_source_module,
        "normalized_source_event": rule_source_event,
        "posting_rule_id": rule.id if rule else None,
        "processing_time_ms": round((datetime.utcnow() - started_at).total_seconds() * 1000, 2),
    }


def _accounting_events_dashboard_payload(tenant_id: str, db: Session) -> dict:
    today = datetime.utcnow().date()
    events = db.query(AccountingEvent).filter(AccountingEvent.tenant_id == tenant_id).all()
    todays_events = [event for event in events if event.created_at and event.created_at.date() == today]
    by_module: dict[str, int] = {}
    by_status: dict[str, int] = {}
    failure_analysis: dict[str, int] = {}
    for event in events:
        by_module[event.source_module] = by_module.get(event.source_module, 0) + 1
        by_status[event.status] = by_status.get(event.status, 0) + 1
        if event.dead_letter_reason:
            key = event.dead_letter_reason.split(":")[0]
            failure_analysis[key] = failure_analysis.get(key, 0) + 1
    posted = sum(1 for event in events if event.status in {"posted", "completed"})
    failed = sum(1 for event in events if event.status in {"failed", "dead_letter"})
    avg_processing = 0 if not events else round(sum(event.processing_time_ms or 0.0 for event in events) / len(events), 2)
    success_rate = 100 if not events else round((posted / len(events)) * 100, 1)
    event_health = 100 if not events else max(0, round(success_rate - (sum(1 for event in events if event.retry_count) / len(events) * 20) - (failed / len(events) * 30)))
    return {
        "tenant_id": tenant_id,
        "kpis": {
            "todays_events": len(todays_events),
            "pending": sum(1 for event in events if event.status in {"created", "validated", "queued"}),
            "failed": failed,
            "posted": posted,
            "average_processing_time_ms": avg_processing,
            "retry_queue": sum(1 for event in events if event.queue_status == "retry_queue"),
            "dead_letter_queue": sum(1 for event in events if event.queue_status == "dead_letter_queue"),
            "event_health": event_health,
        },
        "charts": {
            "events_by_module": [{"label": key, "value": value} for key, value in sorted(by_module.items())],
            "events_by_status": [{"label": key, "value": value} for key, value in sorted(by_status.items())],
            "success_rate": [{"label": "Success", "value": success_rate}, {"label": "Failed", "value": round(100 - success_rate, 1)}],
            "failure_analysis": [{"label": key, "value": value} for key, value in sorted(failure_analysis.items())],
        },
        "monitoring": {
            "queue_size": sum(1 for event in events if event.queue_status in {"normal_queue", "priority_queue", "retry_queue"}),
            "average_latency_ms": avg_processing,
            "throughput": len(todays_events),
            "success_percent": success_rate,
            "error_percent": round(100 - success_rate, 1),
            "retry_count": sum(event.retry_count or 0 for event in events),
        },
        "summary": {
            "status": "healthy" if event_health >= 90 else "attention" if event_health >= 70 else "critical",
            "message": "Accounting event intake is operating within tolerance." if event_health >= 70 else "Review failed and dead-letter events before close.",
        },
    }


def _event_360_payload(event: AccountingEvent) -> dict:
    response = _accounting_event_response(event)
    response["business_view"] = {
        "source_module": event.source_module,
        "business_transaction": event.event_type,
        "reference_id": event.reference_id,
        "customer": (event.dimensions or {}).get("customer_id") or (event.payload or {}).get("customer_id"),
        "product": (event.dimensions or {}).get("product_id") or (event.payload or {}).get("product_id"),
    }
    response["processing_view"] = {
        "validation_status": event.validation_status,
        "queue_status": event.queue_status,
        "retry_count": event.retry_count,
        "processing_time_ms": event.processing_time_ms,
        "next_retry_at": event.next_retry_at,
    }
    response["financial_view"] = {
        "posting_rule_id": event.posting_rule_id,
        "journal_id": event.journal_id,
        "currency": event.currency,
        "amount": event.amount,
        "financial_period": event.business_date.strftime("%B %Y") if event.business_date else None,
    }
    response["audit_view"] = {
        "created_by": event.created_by,
        "approved_by": event.approved_by,
        "version": event.version,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }
    response["ai_view"] = {
        "failure_prediction": "high" if event.queue_status == "dead_letter_queue" else "medium" if event.retry_count else "low",
        "duplicate_risk": "high" if event.validation_result and any(check.get("key") == "duplicate_detection" and check.get("status") == "failed" for check in event.validation_result.get("checks", [])) else "low",
        "posting_recommendation": "Fix posting rule and replay." if event.queue_status == "dead_letter_queue" else "Ready for posting pipeline.",
        "processing_anomaly": "retry_required" if event.retry_count else "none",
    }
    return response


def _assert_period_open(
    db: Session,
    tenant_id: str,
    posting_date: Optional[datetime],
    branch_id: Optional[str] = None,
) -> None:
    value = posting_date or datetime.utcnow()
    query = db.query(AccountingPeriod).filter(
        AccountingPeriod.tenant_id == tenant_id,
        AccountingPeriod.period_start <= value,
        AccountingPeriod.period_end >= value,
    )
    if branch_id:
        branch_period = query.filter(AccountingPeriod.branch_id == branch_id).first()
        period = branch_period or query.filter(AccountingPeriod.branch_id.is_(None)).first()
    else:
        period = query.filter(AccountingPeriod.branch_id.is_(None)).first()
    if not period:
        return
    if str(period.status or "open").lower() in {"future", "locked", "closed", "pending_unlock", "hard_close", "archived"}:
        raise HTTPException(
            status_code=400,
            detail=f"Accounting period {period.period_name} is {period.status}; posting is blocked",
        )


def _validate_account_for_line(
    account: GLAccount,
    debit: float,
    credit: float,
    posting_mode: str = "manual",
) -> None:
    freeze_status = str(account.freeze_status or "open").lower()
    if freeze_status in {"closed", "freeze_both"}:
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is frozen for posting")
    if (debit or 0.0) > 0 and freeze_status == "freeze_debit":
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is frozen for debit")
    if (credit or 0.0) > 0 and freeze_status == "freeze_credit":
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is frozen for credit")
    if posting_mode == "auto" and not _is_truthy(account.allow_auto_posting):
        raise HTTPException(status_code=400, detail=f"Auto posting is not allowed for GL account {account.account_code}")
    if posting_mode == "manual" and not _is_truthy(account.allow_manual_posting):
        raise HTTPException(status_code=400, detail=f"Manual posting is not allowed for GL account {account.account_code}")


def _get_or_create_account(code: str, tenant_id: str, db: Session) -> GLAccount:
    account = (
        db.query(GLAccount)
        .filter(GLAccount.tenant_id == tenant_id, GLAccount.account_code == code)
        .first()
    )
    if account:
        return account

    name, account_type = DEFAULT_ACCOUNT_NAMES.get(code, (code.replace("_", " ").title(), "asset"))
    account = GLAccount(
        id=str(uuid4()),
        tenant_id=tenant_id,
        account_code=code,
        account_name=name,
        account_type=account_type,
        category=account_type,
        currency="INR",
        base_currency="INR",
        posting_allowed="true",
        allow_manual_posting="true",
        allow_auto_posting="true",
        freeze_status="open",
        status="active",
        balance=0.0,
    )
    db.add(account)
    db.flush()
    return account


def _get_postable_account_by_id(account_id: str, tenant_id: str, db: Session) -> GLAccount:
    account = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail=f"GL account not found for tenant: {account_id}")
    if not _is_truthy(account.posting_allowed):
        raise HTTPException(status_code=400, detail=f"Posting is not allowed for GL account {account.account_code}")
    if str(account.status or "").lower() not in {"active", ""}:
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is not active")
    if str(account.freeze_status or "open").lower() == "closed":
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is closed")
    return account


def _get_postable_account_by_code(account_code: str, tenant_id: str, db: Session) -> GLAccount:
    account = _get_or_create_account(account_code, tenant_id, db)
    if not _is_truthy(account.posting_allowed):
        raise HTTPException(status_code=400, detail=f"Posting is not allowed for GL account {account.account_code}")
    if str(account.status or "").lower() not in {"active", ""}:
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is not active")
    if str(account.freeze_status or "open").lower() == "closed":
        raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is closed")
    return account


def _validate_parent_account(
    db: Session,
    tenant_id: str,
    parent_account_id: Optional[str],
    account_id: Optional[str] = None,
) -> Optional[GLAccount]:
    if not parent_account_id:
        return None
    if account_id and parent_account_id == account_id:
        raise HTTPException(status_code=400, detail="GL account cannot be its own parent")
    parent = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.id == parent_account_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent GL account not found for tenant")
    seen = {account_id} if account_id else set()
    cursor = parent
    while cursor:
        if cursor.id in seen:
            raise HTTPException(status_code=400, detail="Parent GL account would create a cycle")
        seen.add(cursor.id)
        if not cursor.parent_account_id:
            break
        cursor = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.id == cursor.parent_account_id).first()
    return parent


def _account_tree_node(account: GLAccount) -> dict:
    return {
        "id": account.id,
        "account_code": account.account_code,
        "account_name": account.account_name,
        "account_type": account.account_type,
        "category": account.category,
        "currency": account.currency,
        "base_currency": account.base_currency,
        "branch_specific": account.branch_specific,
        "posting_allowed": account.posting_allowed,
        "freeze_status": account.freeze_status,
        "status": account.status,
        "balance": account.balance,
        "children": [],
    }


def _build_coa_tree(accounts: list[GLAccount]) -> list[dict]:
    nodes = {account.id: _account_tree_node(account) for account in accounts}
    roots = []
    for account in accounts:
        node = nodes[account.id]
        if account.parent_account_id and account.parent_account_id in nodes:
            nodes[account.parent_account_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def _gl_account_api_item(account: GLAccount, child_count: int = 0) -> dict:
    metadata = account.metadata_json or {}
    dimensions = metadata.get("dimensions") or []
    reporting = metadata.get("reporting") or {}
    tax = metadata.get("tax") or {}
    product = metadata.get("product") or {}
    workflow = metadata.get("workflow") or {}
    security = metadata.get("security") or {}
    ai = metadata.get("ai") or {}
    return {
        "id": account.id,
        "tenant_id": account.tenant_id,
        "gl_code": account.account_code,
        "account_code": account.account_code,
        "name": account.account_name,
        "account_name": account.account_name,
        "short_name": metadata.get("short_name"),
        "account_type": account.account_type,
        "category": account.category,
        "parent_account_id": account.parent_account_id,
        "posting_allowed": account.posting_allowed,
        "allow_manual_posting": account.allow_manual_posting,
        "allow_auto_posting": account.allow_auto_posting,
        "requires_approval": account.requires_approval,
        "freeze_status": account.freeze_status,
        "currency": account.currency,
        "base_currency": account.base_currency,
        "normal_balance": account.normal_balance,
        "opening_balance": account.opening_balance,
        "balance": account.balance,
        "financial_year": account.financial_year,
        "branch_id": account.branch_id,
        "branch_specific": account.branch_specific,
        "status": account.status,
        "child_count": child_count,
        "dimensions": dimensions,
        "reporting": reporting,
        "tax": tax,
        "product": product,
        "workflow": workflow,
        "security": security,
        "ai": ai,
        "metadata": metadata,
        "created_at": account.created_at,
    }


def _coa_child_counts(accounts: list[GLAccount]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for account in accounts:
        if account.parent_account_id:
            counts[account.parent_account_id] = counts.get(account.parent_account_id, 0) + 1
    return counts


def _ledger_dashboard_payload(tenant_id: str, db: Session) -> dict:
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    balances = db.query(GLBalance).filter(GLBalance.tenant_id == tenant_id).all()
    entries = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id).all()
    posted_entries = sum(1 for entry in entries if str(entry.posting_status or "").lower() == "posted")
    active_accounts = sum(1 for account in accounts if str(account.status or "").lower() == "active")
    currency_counts: dict[str, int] = {}
    for balance in balances:
        currency = balance.currency or "INR"
        currency_counts[currency] = currency_counts.get(currency, 0) + 1
    status_counts: dict[str, int] = {}
    for entry in entries:
        status = str(entry.posting_status or "draft").lower()
        status_counts[status] = status_counts.get(status, 0) + 1
    health_score = 0
    if accounts:
        health_score += 35
    if balances:
        health_score += 25
    if entries:
        health_score += 20
    if posted_entries:
        health_score += 20
    health_score = min(100, health_score)
    summary_status = "healthy" if health_score >= 80 else "attention" if health_score >= 60 else "setup-required"
    return {
        "tenant_id": tenant_id,
        "kpis": {
            "total_accounts": len(accounts),
            "active_accounts": active_accounts,
            "posted_entries": posted_entries,
            "draft_entries": len(entries) - posted_entries,
            "balance_rows": len(balances),
            "health_score": health_score,
        },
        "charts": {
            "accounts_by_currency": [{"label": key, "value": value} for key, value in sorted(currency_counts.items())],
            "entries_by_status": [{"label": key, "value": value} for key, value in sorted(status_counts.items())],
        },
        "summary": {
            "status": summary_status,
            "message": "General ledger posting visibility is active." if health_score >= 80 else "General ledger setup needs additional postings or balances.",
        },
    }


def _ledger_balances_payload(tenant_id: str, db: Session, financial_year: Optional[str] = None, branch_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> dict:
    query = db.query(GLBalance).filter(GLBalance.tenant_id == tenant_id)
    if financial_year:
        query = query.filter(GLBalance.financial_year == financial_year)
    if branch_id:
        query = query.filter(GLBalance.branch_id == branch_id)
    total = query.count()
    rows = query.order_by(GLBalance.updated_at.desc()).offset(offset).limit(limit).all()
    accounts = {account.id: account for account in db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()}
    items = []
    for row in rows:
        account = accounts.get(row.gl_account_id)
        items.append(
            {
                "id": row.id,
                "gl_account_id": row.gl_account_id,
                "account_code": account.account_code if account else None,
                "account_name": account.account_name if account else None,
                "branch_id": row.branch_id,
                "currency": row.currency,
                "financial_year": row.financial_year,
                "opening_balance": row.opening_balance,
                "total_debit": row.total_debit,
                "total_credit": row.total_credit,
                "closing_balance": row.closing_balance,
                "updated_at": row.updated_at,
            }
        )
    return {"tenant_id": tenant_id, "total": total, "items": items}


def _ledger_entries_payload(tenant_id: str, db: Session, limit: int = 50, offset: int = 0, branch_id: Optional[str] = None, source_module: Optional[str] = None) -> dict:
    query = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id)
    if branch_id:
        query = query.filter(JournalEntry.branch_id == branch_id)
    if source_module:
        query = query.filter(JournalEntry.source_module == source_module)
    total = query.count()
    rows = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc()).offset(offset).limit(limit).all()
    items = []
    for row in rows:
        lines = db.query(JournalLine).filter(JournalLine.journal_entry_id == row.id).all()
        total_debit = round(sum(line.debit or 0.0 for line in lines), 2)
        total_credit = round(sum(line.credit or 0.0 for line in lines), 2)
        items.append(
            {
                "id": row.id,
                "entry_date": row.entry_date,
                "description": row.description,
                "reference": row.reference,
                "source_module": row.source_module,
                "source_event": row.source_event,
                "posting_status": row.posting_status,
                "branch_id": row.branch_id,
                "financial_year": row.financial_year,
                "business_date": row.business_date,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "line_count": len(lines),
            }
        )
    return {"tenant_id": tenant_id, "total": total, "items": items}


def _ledger_health_payload(tenant_id: str, db: Session) -> dict:
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    balances = db.query(GLBalance).filter(GLBalance.tenant_id == tenant_id).all()
    entries = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id).all()
    posted_entries = sum(1 for entry in entries if str(entry.posting_status or "").lower() == "posted")
    health_score = min(100, 35 + (25 if balances else 0) + (20 if entries else 0) + (20 if posted_entries else 0))
    status = "healthy" if health_score >= 80 else "attention" if health_score >= 60 else "setup-required"
    return {
        "tenant_id": tenant_id,
        "health_score": health_score,
        "status": status,
        "checks": [
            {"name": "accounts_configured", "passed": bool(accounts), "detail": f"{len(accounts)} GL accounts configured"},
            {"name": "balances_initialized", "passed": bool(balances), "detail": f"{len(balances)} balance rows present"},
            {"name": "posted_entries", "passed": posted_entries > 0, "detail": f"{posted_entries} posted entries"},
        ],
        "summary": "General ledger is operational." if status == "healthy" else "General ledger needs more activity to become fully operational.",
    }


def _coa_dashboard_payload(tenant_id: str, db: Session) -> dict:
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    child_counts = _coa_child_counts(accounts)
    by_type: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for account in accounts:
        by_type[account.account_type or "unclassified"] = by_type.get(account.account_type or "unclassified", 0) + 1
        by_category[account.category or "Uncategorized"] = by_category.get(account.category or "Uncategorized", 0) + 1
        by_status[account.status or "unknown"] = by_status.get(account.status or "unknown", 0) + 1

    active_accounts = sum(1 for account in accounts if (account.status or "").lower() == "active")
    posting_accounts = sum(1 for account in accounts if _is_truthy(account.posting_allowed))
    control_accounts = len(accounts) - posting_accounts
    parent_accounts = len(child_counts)
    inactive_accounts = sum(1 for account in accounts if (account.status or "").lower() in {"inactive", "deactivated", "closed"})
    pending_approvals = sum(1 for account in accounts if (account.status or "").lower() in {"draft", "finance_review", "cfo_review", "approved"})

    complete = 0
    for account in accounts:
        if account.category and account.currency and account.account_type and account.normal_balance is not None:
            complete += 1
    ai_health = 0 if not accounts else round((complete / len(accounts)) * 100)

    return {
        "tenant_id": tenant_id,
        "kpis": {
            "total_accounts": len(accounts),
            "active_accounts": active_accounts,
            "control_accounts": control_accounts,
            "posting_accounts": posting_accounts,
            "parent_accounts": parent_accounts,
            "inactive_accounts": inactive_accounts,
            "pending_approvals": pending_approvals,
            "ai_health": ai_health,
        },
        "charts": {
            "accounts_by_type": [{"label": key, "value": value} for key, value in sorted(by_type.items())],
            "accounts_by_category": [{"label": key, "value": value} for key, value in sorted(by_category.items())],
            "accounts_by_status": [{"label": key, "value": value} for key, value in sorted(by_status.items())],
        },
        "summary": {
            "status": "setup-required" if len(accounts) < 10 else "attention" if ai_health < 75 else "strong",
            "message": "Seed or complete account metadata before production posting." if ai_health < 75 else "Chart of accounts metadata is ready for controlled posting.",
        },
    }


def _validate_double_entry(lines: List[PostingEngineLine]) -> dict:
    if not lines or len(lines) < 2:
        raise HTTPException(status_code=400, detail="Posting must contain at least two lines")
    total_debit = round(sum(line.debit or 0.0 for line in lines), 2)
    total_credit = round(sum(line.credit or 0.0 for line in lines), 2)
    if total_debit <= 0 or total_credit <= 0:
        raise HTTPException(status_code=400, detail="Posting must include debit and credit values")
    if total_debit != total_credit:
        raise HTTPException(status_code=400, detail="Posting must be balanced")
    for line in lines:
        if (line.debit or 0.0) < 0 or (line.credit or 0.0) < 0:
            raise HTTPException(status_code=400, detail="Debit and credit cannot be negative")
        if (line.debit or 0.0) > 0 and (line.credit or 0.0) > 0:
            raise HTTPException(status_code=400, detail="A posting line cannot contain both debit and credit")
        if not line.gl_account_id and not line.account_code:
            raise HTTPException(status_code=400, detail="Each posting line needs gl_account_id or account_code")
    return {"total_debit": total_debit, "total_credit": total_credit, "is_balanced": True}


def _update_gl_balance(
    db: Session,
    tenant_id: str,
    account: GLAccount,
    debit: float,
    credit: float,
    branch_id: Optional[str],
    currency: Optional[str],
    financial_year: Optional[str],
) -> None:
    fy = financial_year or _current_financial_year()
    balance = (
        db.query(GLBalance)
        .filter(
            GLBalance.tenant_id == tenant_id,
            GLBalance.gl_account_id == account.id,
            GLBalance.branch_id == branch_id,
            GLBalance.currency == (currency or account.currency or "INR"),
            GLBalance.financial_year == fy,
        )
        .first()
    )
    if not balance:
        balance = GLBalance(
            id=str(uuid4()),
            tenant_id=tenant_id,
            gl_account_id=account.id,
            branch_id=branch_id,
            currency=currency or account.currency or "INR",
            financial_year=fy,
            opening_balance=account.opening_balance or 0.0,
            total_debit=0.0,
            total_credit=0.0,
            closing_balance=account.opening_balance or 0.0,
        )
        db.add(balance)
    balance.total_debit = round((balance.total_debit or 0.0) + (debit or 0.0), 2)
    balance.total_credit = round((balance.total_credit or 0.0) + (credit or 0.0), 2)
    balance.closing_balance = round((balance.opening_balance or 0.0) + balance.total_debit - balance.total_credit, 2)
    balance.updated_at = datetime.utcnow()


def _post_journal(
    db: Session,
    tenant_id: str,
    description: str,
    lines: List[PostingEngineLine],
    reference: Optional[str] = None,
    metadata: Optional[dict] = None,
    entry_date: Optional[datetime] = None,
    posting_status: str = "posted",
    idempotency_key: Optional[str] = None,
    source_module: Optional[str] = None,
    source_event: Optional[str] = None,
    source_reference: Optional[str] = None,
    branch_id: Optional[str] = None,
    business_date: Optional[datetime] = None,
    financial_year: Optional[str] = None,
    voucher_id: Optional[str] = None,
) -> JournalEntry:
    _validate_double_entry(lines)
    effective_date = business_date or entry_date or datetime.utcnow()
    posting_mode = "auto" if source_module and source_module not in {"manual", "accounting"} else "manual"
    _assert_period_open(db, tenant_id, effective_date, branch_id=branch_id)
    journal_entry = JournalEntry(
        id=str(uuid4()),
        tenant_id=tenant_id,
        entry_date=entry_date or datetime.utcnow(),
        description=description,
        reference=reference,
        metadata_json=metadata,
        posting_status=posting_status,
        idempotency_key=idempotency_key,
        source_module=source_module,
        source_event=source_event,
        source_reference=source_reference,
        business_date=business_date,
        financial_year=financial_year or _current_financial_year(effective_date),
        branch_id=branch_id,
        voucher_id=voucher_id,
    )
    db.add(journal_entry)
    db.flush()

    for line in lines:
        account = (
            _get_postable_account_by_id(line.gl_account_id, tenant_id, db)
            if line.gl_account_id
            else _get_postable_account_by_code(line.account_code or "", tenant_id, db)
        )
        debit = line.debit or 0.0
        credit = line.credit or 0.0
        if line.transaction_amount is not None and line.exchange_rate and not debit and not credit:
            debit = round(line.transaction_amount * line.exchange_rate, 2)
        _validate_account_for_line(account, debit, credit, posting_mode=posting_mode)
        db.add(
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=journal_entry.id,
                gl_account_id=account.id,
                debit=debit,
                credit=credit,
                currency=line.currency or account.base_currency or account.currency or "INR",
                transaction_currency=line.transaction_currency or line.currency or account.currency,
                transaction_amount=line.transaction_amount,
                exchange_rate=line.exchange_rate,
                branch_id=line.branch_id or branch_id,
                department_id=line.department_id,
                cost_center=line.cost_center,
                profit_center=line.profit_center,
                project_id=line.project_id,
                employee_id=line.employee_id,
                product_id=line.product_id,
                business_unit_id=line.business_unit_id,
                description=line.description,
            )
        )
        account.balance += debit
        account.balance -= credit
        _update_gl_balance(
            db=db,
            tenant_id=tenant_id,
            account=account,
            debit=debit,
            credit=credit,
            branch_id=line.branch_id or branch_id,
            currency=line.currency or account.base_currency or account.currency or "INR",
            financial_year=journal_entry.financial_year,
        )
    return journal_entry


def _log_audit(
    db: Session,
    tenant_id: str,
    entity: str,
    entity_id: Optional[str],
    action: str,
    payload: Optional[dict] = None,
    performed_by: Optional[str] = None,
) -> None:
    db.add(
        AuditLog(
            id=str(uuid4()),
            tenant_id=tenant_id,
            entity=entity,
            entity_id=entity_id,
            action=action,
            payload=_json_safe(payload),
            performed_by=performed_by,
        )
    )


def _create_subledger_entry(
    db: Session,
    tenant_id: str,
    source_module: str,
    source_event: str,
    source_reference: str,
    amount: float,
    journal_entry_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    status: str = "active",
    reversal_entry_id: Optional[str] = None,
) -> SubLedgerEntry:
    entry = SubLedgerEntry(
        id=str(uuid4()),
        tenant_id=tenant_id,
        source_module=source_module,
        source_event=source_event,
        source_reference=source_reference,
        journal_entry_id=journal_entry_id,
        amount=amount,
        status=status,
        reversal_entry_id=reversal_entry_id,
        metadata_json=metadata,
    )
    db.add(entry)
    return entry


ALLOWED_FORMULA_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _event_value(event_data: dict, field: Optional[str], default: Any = None) -> Any:
    if not field:
        return default
    cursor: Any = event_data
    for part in field.split("."):
        if isinstance(cursor, dict) and part in cursor:
            cursor = cursor[part]
        else:
            return default
    return cursor


def _safe_formula_value(node: ast.AST, values: dict) -> float:
    if isinstance(node, ast.Expression):
        return _safe_formula_value(node.body, values)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id not in values:
            raise HTTPException(status_code=400, detail=f"Formula field is missing from event data: {node.id}")
        return float(values[node.id] or 0.0)
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_FORMULA_OPERATORS:
        return float(ALLOWED_FORMULA_OPERATORS[type(node.op)](_safe_formula_value(node.left, values), _safe_formula_value(node.right, values)))
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_FORMULA_OPERATORS:
        return float(ALLOWED_FORMULA_OPERATORS[type(node.op)](_safe_formula_value(node.operand, values)))
    raise HTTPException(status_code=400, detail="Formula supports only numeric fields and + - * / operators")


def _evaluate_formula(formula: str, event_data: dict) -> float:
    try:
        parsed = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid posting formula: {formula}") from exc
    flat_values = {
        key: value
        for key, value in event_data.items()
        if isinstance(value, (int, float))
    }
    return round(_safe_formula_value(parsed, flat_values), 2)


def _line_amount(line: dict, base_amount: float, event_data: dict) -> float:
    if line.get("formula"):
        return _evaluate_formula(str(line["formula"]), event_data)
    if line.get("amount_source"):
        value = _event_value(event_data, str(line["amount_source"]), None)
        if value is None:
            raise HTTPException(status_code=400, detail=f"Amount source is missing from event data: {line['amount_source']}")
        return round(float(value or 0.0), 2)
    if line.get("percentage") is not None:
        return round(base_amount * float(line.get("percentage") or 0.0) / 100, 2)
    return round(base_amount, 2)


def _condition_matches(condition: dict, event_data: dict) -> bool:
    field_value = _event_value(event_data, str(condition.get("field") or ""), None)
    operator_name = str(condition.get("operator") or "eq").lower()
    expected = condition.get("value")
    if operator_name in {"exists", "present"}:
        return field_value is not None
    if operator_name in {"not_exists", "missing"}:
        return field_value is None
    if field_value is None:
        return False
    if operator_name in {"eq", "=", "=="}:
        return str(field_value) == str(expected)
    if operator_name in {"ne", "!=", "<>"}:
        return str(field_value) != str(expected)
    if operator_name in {"gt", ">", "gte", ">=", "lt", "<", "lte", "<="}:
        actual_number = float(field_value)
        expected_number = float(expected)
        if operator_name in {"gt", ">"}:
            return actual_number > expected_number
        if operator_name in {"gte", ">="}:
            return actual_number >= expected_number
        if operator_name in {"lt", "<"}:
            return actual_number < expected_number
        return actual_number <= expected_number
    if operator_name == "in":
        values = expected if isinstance(expected, list) else [item.strip() for item in str(expected).split(",")]
        return str(field_value) in {str(item) for item in values}
    if operator_name == "contains":
        return str(expected).lower() in str(field_value).lower()
    raise HTTPException(status_code=400, detail=f"Unsupported posting rule condition operator: {operator_name}")


def _rule_is_effective(rule: PostingRule, moment: Optional[datetime] = None) -> bool:
    value = moment or datetime.utcnow()
    if rule.effective_from and rule.effective_from > value:
        return False
    if rule.effective_to and rule.effective_to < value:
        return False
    return True


def _rule_conditions_match(rule: PostingRule, event_data: dict) -> bool:
    conditions = rule.conditions if isinstance(rule.conditions, list) else []
    return all(_condition_matches(condition, event_data) for condition in conditions)


def _find_posting_rule(
    db: Session,
    tenant_id: str,
    source_module: str,
    source_event: str,
    event_data: Optional[dict] = None,
    active_only: bool = True,
) -> Optional[PostingRule]:
    query = db.query(PostingRule).filter(
        PostingRule.tenant_id == tenant_id,
        PostingRule.source_module == source_module,
        PostingRule.source_event == source_event,
    )
    if active_only:
        query = query.filter(
            PostingRule.is_active.in_(["true", "1", "yes", "active"]),
            PostingRule.status.in_(["active", "published"]),
        )
    candidates = query.order_by(PostingRule.priority.asc(), PostingRule.created_at.desc()).all()
    for rule in candidates:
        if _rule_is_effective(rule) and _rule_conditions_match(rule, event_data or {}):
            return rule
    return None


def _log_posting_execution(
    db: Session,
    tenant_id: str,
    rule_id: Optional[str],
    source_module: str,
    source_event: str,
    source_reference: Optional[str],
    status: str,
    input_payload: Optional[dict] = None,
    generated_lines: Optional[list[dict]] = None,
    journal_id: Optional[str] = None,
    error_message: Optional[str] = None,
    started_at: Optional[datetime] = None,
) -> PostingExecutionLog:
    execution_time_ms = 0.0
    if started_at:
        execution_time_ms = round((datetime.utcnow() - started_at).total_seconds() * 1000, 2)
    log = PostingExecutionLog(
        id=str(uuid4()),
        tenant_id=tenant_id,
        rule_id=rule_id,
        source_module=source_module,
        source_event=source_event,
        source_reference=source_reference,
        status=status,
        execution_time_ms=execution_time_ms,
        journal_id=journal_id,
        error_message=error_message,
        input_payload=input_payload,
        generated_lines=generated_lines,
    )
    db.add(log)
    return log


def _normalize_posting_rule_lines(rule: Optional[PostingRule]) -> List[dict]:
    if not rule:
        return []
    if isinstance(rule.posting_lines, list):
        return [
            {
                "account_code": str(line.get("account_code", "")).strip(),
                "direction": str(line.get("direction", "debit")).strip().lower(),
                "description": line.get("description"),
                "sequence": line.get("sequence"),
                "amount_source": line.get("amount_source"),
                "percentage": line.get("percentage"),
                "formula": line.get("formula"),
                "currency": line.get("currency"),
                "dimension_source": line.get("dimension_source") if isinstance(line.get("dimension_source"), dict) else None,
                "transaction_currency_source": line.get("transaction_currency_source"),
                "exchange_rate_source": line.get("exchange_rate_source"),
            }
            for line in rule.posting_lines
            if line
        ]
    if rule.debit_account_code or rule.credit_account_code:
        return [
            {"account_code": rule.debit_account_code, "direction": "debit"},
            {"account_code": rule.credit_account_code, "direction": "credit"},
        ]
    return []


def _build_posting_lines_from_rule(
    rule: Optional[PostingRule],
    amount: float,
    branch_id: Optional[str] = None,
    currency: Optional[str] = None,
    description_prefix: Optional[str] = None,
    event_data: Optional[dict] = None,
) -> List[PostingEngineLine]:
    normalized_lines = _normalize_posting_rule_lines(rule)
    if not normalized_lines:
        raise HTTPException(status_code=400, detail="Posting rule has no configured lines")

    posting_lines = []
    source_data = {"amount": amount, **(event_data or {})}
    for line in sorted(normalized_lines, key=lambda item: item.get("sequence") or 0):
        account_code = line.get("account_code")
        direction = str(line.get("direction", "debit")).lower()
        if not account_code:
            raise HTTPException(status_code=400, detail="Posting rule line is missing account_code")
        if direction not in {"debit", "credit"}:
            raise HTTPException(status_code=400, detail="Posting rule line direction must be debit or credit")
        line_amount = _line_amount(line, amount, source_data)
        dimension_source = line.get("dimension_source") if isinstance(line.get("dimension_source"), dict) else {}
        line_branch_id = _event_value(source_data, dimension_source.get("branch_id"), branch_id) if dimension_source else branch_id
        line_department_id = _event_value(source_data, dimension_source.get("department_id"), None) if dimension_source else None
        line_cost_center = _event_value(source_data, dimension_source.get("cost_center"), None) if dimension_source else None
        line_profit_center = _event_value(source_data, dimension_source.get("profit_center"), None) if dimension_source else None
        line_project_id = _event_value(source_data, dimension_source.get("project_id"), None) if dimension_source else None
        line_employee_id = _event_value(source_data, dimension_source.get("employee_id"), None) if dimension_source else None
        line_product_id = _event_value(source_data, dimension_source.get("product_id"), None) if dimension_source else None
        line_business_unit_id = _event_value(source_data, dimension_source.get("business_unit_id"), None) if dimension_source else None
        transaction_currency = _event_value(source_data, line.get("transaction_currency_source"), None) or line.get("currency") or currency
        exchange_rate_value = _event_value(source_data, line.get("exchange_rate_source"), None)
        exchange_rate = float(exchange_rate_value) if exchange_rate_value not in {None, ""} else None
        posting_lines.append(
            PostingEngineLine(
                account_code=account_code,
                debit=line_amount if direction == "debit" else 0.0,
                credit=line_amount if direction == "credit" else 0.0,
                currency=line.get("currency") or currency or "INR",
                transaction_currency=transaction_currency,
                transaction_amount=line_amount if transaction_currency and transaction_currency != (line.get("currency") or currency or "INR") else None,
                exchange_rate=exchange_rate,
                branch_id=line_branch_id,
                department_id=line_department_id,
                cost_center=line_cost_center,
                profit_center=line_profit_center,
                project_id=line_project_id,
                employee_id=line_employee_id,
                product_id=line_product_id,
                business_unit_id=line_business_unit_id,
                description=line.get("description") or f"{description_prefix or 'Posting'} {direction}",
            )
        )
    return posting_lines


def _resolve_posting_map(
    posting: AutomatedGLPostingRequest,
    db: Session,
    amount: float,
    branch_id: Optional[str] = None,
    currency: Optional[str] = None,
    description_prefix: Optional[str] = None,
) -> tuple[List[PostingEngineLine], Optional[PostingRule]]:
    if posting.debit_account_code and posting.credit_account_code:
        return [
            PostingEngineLine(
                account_code=posting.debit_account_code,
                debit=amount,
                credit=0.0,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} debit",
            ),
            PostingEngineLine(
                account_code=posting.credit_account_code,
                debit=0.0,
                credit=amount,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} credit",
            ),
        ], None

    event_data = {"amount": amount, **(posting.metadata or {})}
    rule = _find_posting_rule(db, posting.tenant_id, posting.source_module, posting.source_event, event_data)
    if rule:
        return _build_posting_lines_from_rule(rule, amount, branch_id, currency, description_prefix, event_data), rule

    mapped = DEFAULT_POSTING_MAP.get((posting.source_module, posting.source_event))
    if mapped:
        return [
            PostingEngineLine(
                account_code=mapped[0],
                debit=amount,
                credit=0.0,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} debit",
            ),
            PostingEngineLine(
                account_code=mapped[1],
                debit=0.0,
                credit=amount,
                currency=currency or "INR",
                branch_id=branch_id,
                description=f"{description_prefix or 'Posting'} credit",
            ),
        ], None

    raise HTTPException(status_code=400, detail="No GL posting map found for source module/event")


def _posting_rule_line_response(line: dict) -> dict:
    return {
        "account_code": line.get("account_code"),
        "direction": line.get("direction", "debit"),
        "description": line.get("description"),
        "sequence": line.get("sequence"),
        "amount_source": line.get("amount_source"),
        "percentage": line.get("percentage"),
        "formula": line.get("formula"),
        "currency": line.get("currency"),
        "dimension_source": line.get("dimension_source"),
        "transaction_currency_source": line.get("transaction_currency_source"),
        "exchange_rate_source": line.get("exchange_rate_source"),
    }


def _posting_rule_response(rule: PostingRule) -> dict:
    return {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "source_module": rule.source_module,
        "source_event": rule.source_event,
        "rule_name": rule.rule_name,
        "priority": rule.priority or 100.0,
        "status": rule.status,
        "version": rule.version,
        "supersedes_rule_id": rule.supersedes_rule_id,
        "effective_from": rule.effective_from,
        "effective_to": rule.effective_to,
        "requires_approval": rule.requires_approval,
        "approval_status": rule.approval_status,
        "maker_by": rule.maker_by,
        "checker_by": rule.checker_by,
        "finance_head_by": rule.finance_head_by,
        "approved_by": rule.approved_by,
        "approved_at": rule.approved_at,
        "dependency_rule_ids": rule.dependency_rule_ids if isinstance(rule.dependency_rule_ids, list) else [],
        "rollback_strategy": rule.rollback_strategy,
        "debit_account_code": rule.debit_account_code,
        "credit_account_code": rule.credit_account_code,
        "description": rule.description,
        "is_active": rule.is_active,
        "lines": [
            _posting_rule_line_response(line)
            for line in _normalize_posting_rule_lines(rule)
        ],
        "conditions": rule.conditions if isinstance(rule.conditions, list) else [],
        "created_by": rule.created_by,
        "metadata": rule.metadata_json,
    }


def _posting_rule_api_item(rule: PostingRule, executions: Optional[list[PostingExecutionLog]] = None) -> dict:
    base = _posting_rule_response(rule)
    lines = base.get("lines") or []
    debit_lines = [line for line in lines if str(line.get("direction", "")).lower() == "debit"]
    credit_lines = [line for line in lines if str(line.get("direction", "")).lower() == "credit"]
    metadata = base.get("metadata") or {}
    execution_rows = executions or []
    success_count = sum(1 for item in execution_rows if item.status in {"success", "posted", "simulated"})
    failure_count = sum(1 for item in execution_rows if item.status not in {"success", "posted", "simulated"})
    avg_time = 0 if not execution_rows else round(sum(item.execution_time_ms or 0.0 for item in execution_rows) / len(execution_rows), 2)
    return {
        **base,
        "rule_code": metadata.get("rule_code") or f"{rule.source_module}.{rule.source_event}.v{rule.version:g}",
        "accounting_event": rule.source_event,
        "product": metadata.get("product") or metadata.get("product_id"),
        "scope": metadata.get("scope") or {
            "enterprise": metadata.get("enterprise"),
            "legal_entity": metadata.get("legal_entity"),
            "business_unit": metadata.get("business_unit"),
            "product": metadata.get("product"),
            "branch": metadata.get("branch_id"),
        },
        "debit_lines": debit_lines,
        "credit_lines": credit_lines,
        "dimensions": metadata.get("dimensions") or {},
        "taxes": metadata.get("taxes") or [],
        "validation_rules": metadata.get("validation_rules") or ["debits_equal_credits", "currency_exists", "gl_active", "period_open"],
        "workflow": {
            "maker_by": rule.maker_by,
            "checker_by": rule.checker_by,
            "finance_head_by": rule.finance_head_by,
            "approval_status": rule.approval_status,
        },
        "execution_summary": {
            "execution_count": len(execution_rows),
            "success_count": success_count,
            "failure_count": failure_count,
            "average_execution_time_ms": avg_time,
        },
        "ai": {
            "duplicate_risk": "medium" if metadata.get("duplicate_risk") else "low",
            "conflict_detection": "review" if failure_count else "clear",
            "recommendation": "Publish after finance-head approval." if rule.status in {"draft", "pending_approval"} else "Monitor execution performance.",
            "predicted_failure": "medium" if failure_count else "low",
        },
    }


def _posting_rule_dashboard_payload(tenant_id: str, db: Session) -> dict:
    rules = db.query(PostingRule).filter(PostingRule.tenant_id == tenant_id).all()
    executions = db.query(PostingExecutionLog).filter(PostingExecutionLog.tenant_id == tenant_id).all()
    execution_rule_ids = {item.rule_id for item in executions if item.rule_id}
    by_product: dict[str, int] = {}
    by_status: dict[str, int] = {}
    execution_frequency: dict[str, int] = {}
    rule_lookup = {rule.id: rule for rule in rules}
    for rule in rules:
        metadata = rule.metadata_json or {}
        product = metadata.get("product") or metadata.get("product_id") or "Enterprise Default"
        by_product[product] = by_product.get(product, 0) + 1
        by_status[rule.status or "unknown"] = by_status.get(rule.status or "unknown", 0) + 1
    for execution in executions:
        rule = rule_lookup.get(execution.rule_id)
        label = rule.rule_name if rule else f"{execution.source_module}.{execution.source_event}"
        execution_frequency[label] = execution_frequency.get(label, 0) + 1
    active_rules = sum(1 for rule in rules if rule.status in {"active", "published"} or rule.is_active in {"true", "1", "yes", "active"})
    failed_executions = sum(1 for execution in executions if execution.status not in {"success", "posted", "simulated"})
    average_execution = 0 if not executions else round(sum(execution.execution_time_ms or 0.0 for execution in executions) / len(executions), 2)
    event_keys = {(event.source_module, _normalize_event_source(event.event_type, event.source_module, event.payload)[1]) for event in db.query(AccountingEvent).filter(AccountingEvent.tenant_id == tenant_id).all()}
    rule_keys = {(rule.source_module, rule.source_event) for rule in rules}
    coverage = 100 if not event_keys else round((len(event_keys & rule_keys) / len(event_keys)) * 100)
    unused_rules = sum(1 for rule in rules if rule.id not in execution_rule_ids)
    health = 100 if not rules else max(0, round((active_rules / len(rules)) * 70 + (coverage * 0.2) - min(30, failed_executions * 5)))
    return {
        "tenant_id": tenant_id,
        "kpis": {
            "posting_rules": len(rules),
            "active_rules": active_rules,
            "draft_rules": sum(1 for rule in rules if rule.status == "draft"),
            "failed_rules": failed_executions,
            "average_execution_time_ms": average_execution,
            "rule_coverage": coverage,
            "unused_rules": unused_rules,
            "ai_recommendations": failed_executions + unused_rules,
            "rule_health": health,
        },
        "charts": {
            "rules_by_product": [{"label": key, "value": value} for key, value in sorted(by_product.items())],
            "execution_frequency": [{"label": key, "value": value} for key, value in sorted(execution_frequency.items())],
            "rule_success_rate": [
                {"label": "Success", "value": 100 if not executions else round(((len(executions) - failed_executions) / len(executions)) * 100, 1)},
                {"label": "Failed", "value": 0 if not executions else round((failed_executions / len(executions)) * 100, 1)},
            ],
            "rules_by_status": [{"label": key, "value": value} for key, value in sorted(by_status.items())],
        },
        "summary": {
            "status": "healthy" if health >= 90 else "attention" if health >= 70 else "critical",
            "message": "Posting rules are ready for event-driven journal generation." if health >= 70 else "Review coverage, failed executions, and unused rules.",
        },
    }


def _simulate_posting_rule_instance(
    rule: PostingRule,
    request: PostingRuleDirectSimulationRequest,
    db: Session,
) -> dict:
    event_data = {"amount": request.amount or 0.0, **(request.event_data or {})}
    amount = float(request.amount or event_data.get("amount") or event_data.get("loan_amount") or event_data.get("emi_amount") or 0.0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount or event_data.amount must be positive")
    started_at = datetime.utcnow()
    lines = _build_posting_lines_from_rule(
        rule,
        amount,
        branch_id=request.branch_id,
        currency=request.currency,
        description_prefix=f"{rule.source_module}.{rule.source_event}",
        event_data=event_data,
    )
    validation = _validate_double_entry(lines)
    resolved_lines = []
    for line in lines:
        account = _get_postable_account_by_code(line.account_code or "", request.tenant_id, db)
        _validate_account_for_line(account, line.debit or 0.0, line.credit or 0.0, posting_mode="auto")
        resolved_lines.append(
            {
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "direction": "debit" if line.debit else "credit",
                "debit": line.debit,
                "credit": line.credit,
                "description": line.description,
                "branch_id": line.branch_id,
                "department_id": line.department_id,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
                "project_id": line.project_id,
                "employee_id": line.employee_id,
                "product_id": line.product_id,
                "business_unit_id": line.business_unit_id,
                "currency": line.currency,
                "transaction_currency": line.transaction_currency,
                "exchange_rate": line.exchange_rate,
            }
        )
    _log_posting_execution(
        db,
        tenant_id=request.tenant_id,
        rule_id=rule.id,
        source_module=rule.source_module,
        source_event=rule.source_event,
        source_reference=request.source_reference,
        status="simulated",
        input_payload=event_data,
        generated_lines=resolved_lines,
        started_at=started_at,
    )
    db.commit()
    return {
        "rule": _posting_rule_api_item(rule),
        "is_balanced": validation["is_balanced"],
        "total_debit": validation["total_debit"],
        "total_credit": validation["total_credit"],
        "lines": resolved_lines,
        "pipeline": _posting_pipeline(posting_rule_status="simulated", posting_rule=_posting_rule_response(rule)),
        "ai": {
            "impact": f"Rule {rule.rule_name} generates {len(resolved_lines)} journal lines.",
            "risk": "low" if validation["is_balanced"] else "high",
            "recommendation": "Simulation is balanced; proceed to approval workflow." if validation["is_balanced"] else "Fix debit/credit imbalance before publishing.",
        },
    }


def _posting_rule_360_payload(rule: PostingRule, db: Session) -> dict:
    executions = (
        db.query(PostingExecutionLog)
        .filter(PostingExecutionLog.tenant_id == rule.tenant_id, PostingExecutionLog.rule_id == rule.id)
        .order_by(PostingExecutionLog.created_at.desc())
        .all()
    )
    history = (
        db.query(AuditLog)
        .filter(AuditLog.tenant_id == rule.tenant_id, AuditLog.entity == "posting_rule", AuditLog.entity_id == rule.id)
        .order_by(AuditLog.created_at.desc())
        .limit(25)
        .all()
    )
    response = _posting_rule_api_item(rule, executions)
    response["business_view"] = {
        "triggering_events": [f"{rule.source_module}.{rule.source_event}"],
        "supported_products": [response.get("product") or "Enterprise Default"],
        "effective_from": rule.effective_from,
        "effective_to": rule.effective_to,
    }
    response["accounting_view"] = {
        "debit_lines": response["debit_lines"],
        "credit_lines": response["credit_lines"],
        "formula_definitions": [line for line in response["lines"] if line.get("formula") or line.get("amount_source")],
        "validation_rules": response["validation_rules"],
    }
    response["operations_view"] = response["execution_summary"]
    response["governance_view"] = {
        "versions": db.query(PostingRule).filter(PostingRule.tenant_id == rule.tenant_id, (PostingRule.id == rule.id) | (PostingRule.supersedes_rule_id == rule.id)).count(),
        "approval_history": response["workflow"],
        "change_log": [_audit_log_response(item) for item in history],
        "impact_analysis": f"{len(executions)} executions reference this rule.",
    }
    response["ai_view"] = response["ai"]
    response["recent_executions"] = [
        {
            "id": item.id,
            "source_module": item.source_module,
            "source_event": item.source_event,
            "source_reference": item.source_reference,
            "status": item.status,
            "execution_time_ms": item.execution_time_ms,
            "journal_id": item.journal_id,
            "error_message": item.error_message,
            "created_at": item.created_at,
            "generated_lines": item.generated_lines,
        }
        for item in executions[:25]
    ]
    return response


def _audit_log_response(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "tenant_id": log.tenant_id,
        "entity": log.entity,
        "entity_id": log.entity_id,
        "action": log.action,
        "payload": log.payload,
        "performed_by": log.performed_by,
        "created_at": log.created_at,
    }


def _subledger_response(entry: SubLedgerEntry) -> dict:
    return {
        "id": entry.id,
        "tenant_id": entry.tenant_id,
        "source_module": entry.source_module,
        "source_event": entry.source_event,
        "source_reference": entry.source_reference,
        "journal_entry_id": entry.journal_entry_id,
        "amount": entry.amount,
        "status": entry.status,
        "reversal_entry_id": entry.reversal_entry_id,
        "reversed_at": entry.reversed_at,
        "metadata": entry.metadata_json,
        "created_at": entry.created_at,
    }


def _subledger_ledger_name(source_module: str) -> str:
    return SUB_LEDGER_LEDGER_MAP.get(source_module.lower(), f"{source_module.replace('_', ' ').title()} Ledger")


def _financial_rows(accounts: list[GLAccount], account_types: set[str]):
    rows = []
    total = 0.0
    for account in accounts:
        if account.account_type not in account_types:
            continue
        normal_balance = account.balance or 0.0
        if account.account_type in {"liability", "equity", "revenue"}:
            normal_balance = -normal_balance
        total += normal_balance
        rows.append(
            {
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "amount": round(normal_balance, 2),
            }
        )
    return rows, round(total, 2)


def _journal_entry_response(entry: JournalEntry) -> dict:
    return {
        "id": entry.id,
        "tenant_id": entry.tenant_id,
        "entry_date": entry.entry_date,
        "description": entry.description,
        "reference": entry.reference,
        "metadata": entry.metadata_json,
        "posting_status": entry.posting_status,
        "idempotency_key": entry.idempotency_key,
        "source_module": entry.source_module,
        "source_event": entry.source_event,
        "source_reference": entry.source_reference,
        "branch_id": entry.branch_id,
        "business_date": entry.business_date,
        "financial_year": entry.financial_year,
        "voucher_id": entry.voucher_id,
    }


def _journal_document_response(entry: JournalEntry) -> dict:
    total_debit = round(sum(line.debit or 0.0 for line in entry.lines), 2)
    total_credit = round(sum(line.credit or 0.0 for line in entry.lines), 2)
    return {
        **_journal_entry_response(entry),
        "batch_id": entry.batch_id,
        "journal_no": entry.journal_no,
        "posting_date": entry.entry_date,
        "voucher_type": entry.voucher_type,
        "period": entry.period,
        "currency": entry.currency,
        "exchange_rate": entry.exchange_rate,
        "reversal_of": entry.reversal_of,
        "created_by": entry.created_by,
        "approved_by": entry.approved_by,
        "approved_at": entry.approved_at,
        "validation_result": entry.validation_result,
        "template_id": entry.template_id,
        "status": entry.posting_status,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "total_amount": total_debit,
        "lines": [
            {
                "id": line.id,
                "sequence": line.sequence,
                "gl_account_id": line.gl_account_id,
                "account_code": line.gl_account.account_code if line.gl_account else None,
                "account_name": line.gl_account.account_name if line.gl_account else None,
                "debit": line.debit,
                "credit": line.credit,
                "currency": line.currency,
                "transaction_currency": line.transaction_currency,
                "transaction_amount": line.transaction_amount,
                "exchange_rate": line.exchange_rate,
                "branch_id": line.branch_id,
                "department_id": line.department_id,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
                "project_id": line.project_id,
                "employee_id": line.employee_id,
                "product_id": line.product_id,
                "business_unit_id": line.business_unit_id,
                "description": line.description,
                "remarks": line.description,
            }
            for line in sorted(entry.lines, key=lambda item: item.sequence or 0)
        ],
        "attachments": [
            {
                "id": attachment.id,
                "document_id": attachment.document_id,
                "file_name": attachment.file_name,
                "uploaded_by": attachment.uploaded_by,
                "created_at": attachment.created_at,
            }
            for attachment in entry.attachments
        ],
        "approvals": [
            {
                "id": approval.id,
                "level": approval.level,
                "approver": approval.approver,
                "decision": approval.decision,
                "remarks": approval.remarks,
                "approved_time": approval.approved_time,
            }
            for approval in sorted(entry.approvals, key=lambda item: item.approved_time or datetime.min)
        ],
    }


def _journal_api_item(entry: JournalEntry) -> dict:
    response = _journal_document_response(entry)
    metadata = response.get("metadata") or {}
    validation = response.get("validation_result") or {}
    line_count = len(response.get("lines") or [])
    return {
        **response,
        "journal_number": entry.journal_no,
        "business_event": entry.source_event or entry.voucher_type or "manual_journal",
        "journal_type": entry.voucher_type or "journal",
        "amount": response["total_debit"],
        "accounting_date": entry.business_date or entry.entry_date,
        "posting_window": {
            "posting_date": entry.entry_date,
            "period": entry.period,
            "financial_year": entry.financial_year,
            "status": "locked" if entry.posting_status in {"posted", "reversed"} else "editable",
        },
        "legal_entity": metadata.get("legal_entity"),
        "business_unit": metadata.get("business_unit"),
        "approval_state": {
            "status": entry.posting_status,
            "created_by": entry.created_by,
            "approved_by": entry.approved_by,
            "approved_at": entry.approved_at,
            "maker_checker_required": entry.voucher_type in {"manual_journal", "adjustment", "write_off", "intercompany", "journal"},
        },
        "validation_summary": {
            "valid": validation.get("valid"),
            "is_balanced": response["total_debit"] == response["total_credit"],
            "errors": validation.get("errors") or [],
            "warnings": validation.get("warnings") or [],
            "checks": validation.get("checks") or [],
        },
        "ai": {
            "duplicate_risk": "medium" if entry.reference and entry.reference == entry.source_reference else "low",
            "anomaly_score": 8 if response["total_debit"] > 1000000 else 2,
            "fraud_indicators": [],
            "suggested_corrections": [] if validation.get("valid", True) else validation.get("errors") or [],
            "explanation": f"{entry.journal_no or 'Journal'} records {line_count} lines for {entry.description}.",
        },
    }


def _journal_dashboard_payload(tenant_id: str, db: Session) -> dict:
    journals = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id).all()
    today = datetime.utcnow().date()
    status_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    module_counts: dict[str, int] = {}
    volume_by_day: dict[str, float] = {}
    validation_errors = 0
    total_amount = 0.0
    for journal in journals:
        status = journal.posting_status or "draft"
        journal_type = journal.voucher_type or "journal"
        module = journal.source_module or "manual"
        amount = round(sum(line.debit or 0.0 for line in journal.lines), 2)
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[journal_type] = type_counts.get(journal_type, 0) + 1
        module_counts[module] = module_counts.get(module, 0) + 1
        day_key = (journal.entry_date or journal.created_at or datetime.utcnow()).date().isoformat()
        volume_by_day[day_key] = round(volume_by_day.get(day_key, 0.0) + amount, 2)
        total_amount += amount
        validation = journal.validation_result or {}
        validation_errors += len(validation.get("errors") or [])
    reversed_count = status_counts.get("reversed", 0)
    pending_count = status_counts.get("pending", 0) + status_counts.get("approved", 0)
    failed_count = status_counts.get("failed", 0)
    health = 100 if not journals else max(
        0,
        round(
            100
            - min(25, validation_errors * 3)
            - min(20, reversed_count * 4)
            - min(15, pending_count * 2)
            - min(25, failed_count * 5)
        ),
    )
    recurring_count = db.query(JournalTemplate).filter(JournalTemplate.tenant_id == tenant_id, JournalTemplate.status == "active").count()
    return {
        "tenant_id": tenant_id,
        "kpis": {
            "todays_journals": sum(1 for journal in journals if (journal.entry_date or journal.created_at or datetime.utcnow()).date() == today),
            "posted": status_counts.get("posted", 0),
            "draft": status_counts.get("draft", 0),
            "pending_approval": pending_count,
            "rejected": status_counts.get("rejected", 0),
            "reversed": reversed_count,
            "recurring": recurring_count,
            "failed": failed_count,
            "processing_time_ms": 0,
            "journal_health": health,
            "total_journals": len(journals),
            "total_amount": round(total_amount, 2),
        },
        "charts": {
            "journals_by_type": [{"label": key, "value": value} for key, value in sorted(type_counts.items())],
            "posting_volume": [{"label": key, "value": value} for key, value in sorted(volume_by_day.items())[-14:]],
            "approval_status": [{"label": key, "value": value} for key, value in sorted(status_counts.items())],
            "module_distribution": [{"label": key, "value": value} for key, value in sorted(module_counts.items())],
            "daily_throughput": [{"label": key, "value": value} for key, value in sorted(volume_by_day.items())[-14:]],
        },
        "summary": {
            "status": "healthy" if health >= 90 else "attention" if health >= 70 else "critical",
            "message": "Journal engine is ready for balanced, auditable posting." if health >= 70 else "Review failed validations, reversals, and pending approvals.",
        },
    }


def _journal_360_payload(entry: JournalEntry, db: Session) -> dict:
    response = _journal_api_item(entry)
    audit_rows = (
        db.query(AuditLog)
        .filter(AuditLog.tenant_id == entry.tenant_id, AuditLog.entity == "journal", AuditLog.entity_id == entry.id)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    source_event = None
    if entry.source_reference:
        source_event = (
            db.query(AccountingEvent)
            .filter(AccountingEvent.tenant_id == entry.tenant_id, AccountingEvent.reference_id == entry.source_reference)
            .order_by(AccountingEvent.created_at.desc())
            .first()
        )
    response["business_view"] = {
        "source_transaction": entry.source_reference or entry.reference,
        "source_module": entry.source_module or "manual",
        "business_event": entry.source_event or "manual_journal",
        "customer": (entry.metadata_json or {}).get("customer_id"),
        "product": (entry.metadata_json or {}).get("product_id"),
    }
    response["accounting_view"] = {
        "header": {
            "journal_number": entry.journal_no,
            "journal_type": entry.voucher_type,
            "posting_date": entry.entry_date,
            "accounting_date": entry.business_date or entry.entry_date,
            "period": entry.period,
            "financial_year": entry.financial_year,
            "currency": entry.currency,
            "exchange_rate": entry.exchange_rate,
        },
        "lines": response["lines"],
        "posting_rules": [execution.rule_id for execution in db.query(PostingExecutionLog).filter(PostingExecutionLog.tenant_id == entry.tenant_id, PostingExecutionLog.journal_id == entry.id).all() if execution.rule_id],
    }
    response["financial_view"] = {
        "currency": entry.currency,
        "exchange_rate": entry.exchange_rate,
        "total_debit": response["total_debit"],
        "total_credit": response["total_credit"],
        "budget_impact": (entry.validation_result or {}).get("impact", {}).get("gl_accounts", []),
    }
    response["compliance_view"] = {
        "approvals": response["approvals"],
        "attachments": response["attachments"],
        "audit_trail": [_audit_log_response(row) for row in audit_rows],
        "regulatory_references": (entry.metadata_json or {}).get("regulatory_references", []),
    }
    response["timeline"] = [
        {"state": "Created", "at": entry.created_at, "by": entry.created_by},
        *[
            {"state": approval.decision.title(), "at": approval.approved_time, "by": approval.approver, "level": approval.level}
            for approval in sorted(entry.approvals, key=lambda item: item.approved_time or datetime.min)
        ],
        {"state": entry.posting_status.title(), "at": entry.approved_at or entry.entry_date, "by": entry.approved_by},
    ]
    response["source_transaction"] = _accounting_event_response(source_event) if source_event else None
    response["ai_view"] = response["ai"]
    return response


def _journal_batch_response(batch: JournalBatch, journal_count: int = 0) -> dict:
    return {
        "id": batch.id,
        "batch_no": batch.batch_no,
        "tenant_id": batch.tenant_id,
        "posting_date": batch.posting_date,
        "financial_year": batch.financial_year,
        "period": batch.period,
        "status": batch.status,
        "created_by": batch.created_by,
        "approved_by": batch.approved_by,
        "total_amount": round(batch.total_amount or 0.0, 2),
        "journal_count": journal_count,
        "created_at": batch.created_at,
    }


def _journal_template_response(template: JournalTemplate) -> dict:
    return {
        "id": template.id,
        "tenant_id": template.tenant_id,
        "template_name": template.template_name,
        "description": template.description,
        "voucher_type": template.voucher_type,
        "currency": template.currency,
        "lines": template.lines or [],
        "status": template.status,
        "created_by": template.created_by,
        "created_at": template.created_at,
        "updated_at": template.updated_at,
    }


def _posting_pipeline(
    *,
    validation_status: str = "passed",
    validation_balanced: bool = True,
    posting_rule_status: str = "manual",
    posting_rule: Optional[dict] = None,
    subledger_entry_id: Optional[str] = None,
) -> dict:
    return {
        "validation": {"status": validation_status, "is_balanced": validation_balanced},
        "posting_rule": {"status": posting_rule_status, "rule": posting_rule},
        "debit_entry": {"status": "recorded"},
        "credit_entry": {"status": "recorded"},
        "gl_update": {"status": "applied"},
        "audit_log": {"status": "recorded"},
        "subledger": {"status": "recorded", "entry_id": subledger_entry_id},
    }


def _voucher_response(voucher: Voucher) -> dict:
    metadata = voucher.metadata_json or {}
    payment_voucher = metadata.get("payment_voucher") if isinstance(metadata, dict) else None
    payment_voucher = payment_voucher if isinstance(payment_voucher, dict) else {}
    receipt_voucher = metadata.get("receipt_voucher") if isinstance(metadata, dict) else None
    receipt_voucher = receipt_voucher if isinstance(receipt_voucher, dict) else {}
    contra_voucher = metadata.get("contra_voucher") if isinstance(metadata, dict) else None
    contra_voucher = contra_voucher if isinstance(contra_voucher, dict) else {}
    credit_note = metadata.get("credit_note") if isinstance(metadata, dict) else None
    credit_note = credit_note if isinstance(credit_note, dict) else {}
    debit_note = metadata.get("debit_note") if isinstance(metadata, dict) else None
    debit_note = debit_note if isinstance(debit_note, dict) else {}
    return {
        "id": voucher.id,
        "tenant_id": voucher.tenant_id,
        "voucher_number": voucher.voucher_number,
        "voucher_type": voucher.voucher_type,
        "voucher_date": voucher.voucher_date,
        "description": voucher.description,
        "reference": voucher.reference,
        "branch_id": voucher.branch_id,
        "currency": voucher.currency,
        "status": voucher.status,
        "posted_journal_entry_id": voucher.posted_journal_entry_id,
        "created_by": voucher.created_by,
        "verified_by": voucher.verified_by,
        "approved_by": voucher.approved_by,
        "lines": [
            {
                "gl_account_id": line.gl_account_id,
                "debit": line.debit,
                "credit": line.credit,
                "description": line.description,
                "department_id": line.department_id,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
                "project_id": line.project_id,
                "employee_id": line.employee_id,
                "product_id": line.product_id,
                "business_unit_id": line.business_unit_id,
            }
            for line in voucher.lines
        ],
        "payment_mode": voucher.payment_mode,
        "payment_reference": voucher.payment_reference,
        "payment_details": voucher.payment_details,
        "payment_category": payment_voucher.get("category"),
        "receipt_category": receipt_voucher.get("category"),
        "contra_transfer_type": contra_voucher.get("transfer_type"),
        "credit_note_type": credit_note.get("type"),
        "debit_note_type": debit_note.get("type"),
        "payee_name": payment_voucher.get("payee_name"),
        "payer_name": receipt_voucher.get("payer_name"),
        "customer_name": credit_note.get("customer_name") or debit_note.get("customer_name"),
        "customer_id": receipt_voucher.get("customer_id") or credit_note.get("customer_id") or debit_note.get("customer_id"),
        "vendor_id": payment_voucher.get("vendor_id"),
        "vendor_code": payment_voucher.get("vendor_code"),
        "source_location": contra_voucher.get("source_location"),
        "destination_location": contra_voucher.get("destination_location"),
        "transfer_reference": contra_voucher.get("transfer_reference"),
        "credit_note_reference": credit_note.get("credit_note_reference"),
        "debit_note_reference": debit_note.get("debit_note_reference"),
        "amount": payment_voucher.get("amount") or receipt_voucher.get("amount") or contra_voucher.get("amount") or credit_note.get("amount") or debit_note.get("amount"),
        "metadata": metadata,
    }


def _vendor_response(vendor: Vendor) -> dict:
    return {
        "id": vendor.id,
        "tenant_id": vendor.tenant_id,
        "vendor_code": vendor.vendor_code,
        "vendor_name": vendor.vendor_name,
        "vendor_type": vendor.vendor_type,
        "status": vendor.status,
        "payment_terms": vendor.payment_terms,
        "credit_limit": vendor.credit_limit,
        "gst_number": vendor.gst_number,
        "currency": vendor.currency,
        "branch_id": vendor.branch_id,
        "metadata": vendor.metadata_json,
        "created_by": vendor.created_by,
        "created_at": vendor.created_at,
        "updated_at": vendor.updated_at,
    }


def _ap_invoice_response(invoice: APInvoice) -> dict:
    return {
        "id": invoice.id,
        "tenant_id": invoice.tenant_id,
        "vendor_id": invoice.vendor_id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "due_date": invoice.due_date,
        "total_amount": invoice.total_amount,
        "currency": invoice.currency,
        "status": invoice.status,
        "description": invoice.description,
        "reference": invoice.reference,
        "branch_id": invoice.branch_id,
        "created_by": invoice.created_by,
        "created_at": invoice.created_at,
        "updated_at": invoice.updated_at,
        "metadata": invoice.metadata_json,
    }


def _get_vendor_by_id(vendor_id: str, tenant_id: str, db: Session) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id, Vendor.tenant_id == tenant_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found for tenant")
    return vendor


def _get_vendor_by_code(vendor_code: str, tenant_id: str, db: Session) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.vendor_code == vendor_code, Vendor.tenant_id == tenant_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found for tenant")
    return vendor


def _next_voucher_number(tenant_id: str, voucher_type: str, db: Session) -> str:
    prefix = voucher_type.upper().replace("-", "_")[:8]
    count = db.query(Voucher).filter(Voucher.tenant_id == tenant_id, Voucher.voucher_type == voucher_type).count() + 1
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d')}-{count:05d}"


DEFAULT_JOURNAL_TEMPLATES = [
    {
        "template_name": "Salary Payment",
        "description": "Monthly salary expense paid through bank",
        "voucher_type": "payment",
        "lines": [
            {"account_code": "5210_SALARY_EXPENSE", "direction": "debit", "description": "Salary expense"},
            {"account_code": "1120_BANK", "direction": "credit", "description": "Bank payment"},
        ],
    },
    {
        "template_name": "Loan Disbursement",
        "description": "Loan principal disbursed to a customer",
        "voucher_type": "payment",
        "lines": [
            {"account_code": "1200_LOAN_RECEIVABLE", "direction": "debit", "description": "Loan receivable"},
            {"account_code": "1120_BANK", "direction": "credit", "description": "Bank disbursement"},
        ],
    },
    {
        "template_name": "Interest Accrual",
        "description": "Accrue interest receivable and income",
        "voucher_type": "journal",
        "lines": [
            {"account_code": "1200_LOAN_RECEIVABLE", "direction": "debit", "description": "Interest receivable"},
            {"account_code": "4100_INTEREST_INCOME", "direction": "credit", "description": "Interest income"},
        ],
    },
]


def _next_journal_sequence(tenant_id: str, financial_year: str, sequence_type: str, db: Session) -> int:
    counter = (
        db.query(JournalNumberCounter)
        .filter(
            JournalNumberCounter.tenant_id == tenant_id,
            JournalNumberCounter.financial_year == financial_year,
            JournalNumberCounter.sequence_type == sequence_type,
        )
        .with_for_update()
        .first()
    )
    if not counter:
        counter = JournalNumberCounter(
            id=str(uuid4()),
            tenant_id=tenant_id,
            financial_year=financial_year,
            sequence_type=sequence_type,
            current_value=0,
        )
        db.add(counter)
        db.flush()
    counter.current_value = (counter.current_value or 0) + 1
    db.flush()
    return counter.current_value


def _next_journal_number(tenant_id: str, posting_date: datetime, financial_year: str, db: Session) -> str:
    numbering_year = str(posting_date.year)
    sequence = _next_journal_sequence(tenant_id, numbering_year, "journal", db)
    return f"JRN-{posting_date.year}-{sequence:08d}"


def _next_batch_number(tenant_id: str, posting_date: datetime, financial_year: str, db: Session) -> str:
    numbering_year = str(posting_date.year)
    sequence = _next_journal_sequence(tenant_id, numbering_year, "batch", db)
    return f"JBT-{posting_date.year}-{sequence:06d}"


def _journal_period_name(posting_date: datetime) -> str:
    return posting_date.strftime("%B %Y")


def _resolve_journal_account(
    db: Session,
    tenant_id: str,
    gl_account_id: Optional[str] = None,
    account_code: Optional[str] = None,
) -> Optional[GLAccount]:
    query = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id)
    if gl_account_id:
        return query.filter(GLAccount.id == gl_account_id).first()
    if account_code:
        return query.filter(GLAccount.account_code == account_code).first()
    return None


def _engine_lines_from_document(entry: JournalEntry) -> List[PostingEngineLine]:
    return [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit or 0.0,
            credit=line.credit or 0.0,
            description=line.description,
            branch_id=line.branch_id,
            currency=line.currency,
            transaction_currency=line.transaction_currency,
            transaction_amount=line.transaction_amount,
            exchange_rate=line.exchange_rate,
            department_id=line.department_id,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            project_id=line.project_id,
            employee_id=line.employee_id,
            product_id=line.product_id,
            business_unit_id=line.business_unit_id,
        )
        for line in sorted(entry.lines, key=lambda item: item.sequence or 0)
    ]


def _check_dimension(
    db: Session,
    tenant_id: str,
    dimension_type: str,
    code: Optional[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not code:
        return
    configured = db.query(AccountingDimension).filter(
        AccountingDimension.tenant_id == tenant_id,
        AccountingDimension.dimension_type == dimension_type,
    ).count()
    if not configured:
        warning = f"{dimension_type.replace('_', ' ').title()} master is not configured; {code} was accepted"
        if warning not in warnings:
            warnings.append(warning)
        return
    dimension = db.query(AccountingDimension).filter(
        AccountingDimension.tenant_id == tenant_id,
        AccountingDimension.dimension_type == dimension_type,
        AccountingDimension.code == code,
        AccountingDimension.status == "active",
    ).first()
    if not dimension:
        errors.append(f"{dimension_type.replace('_', ' ').title()} does not exist or is inactive: {code}")


def _journal_validation(
    db: Session,
    tenant_id: str,
    lines: List[PostingEngineLine],
    posting_date: datetime,
    source_module: Optional[str] = "manual",
    source_event: Optional[str] = "manual_journal",
    branch_id: Optional[str] = None,
    financial_year: Optional[str] = None,
    currency: Optional[str] = "INR",
    exchange_rate: Optional[float] = 1.0,
    metadata: Optional[dict] = None,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []
    impacts: list[dict] = []
    totals = {"total_debit": 0.0, "total_credit": 0.0, "is_balanced": False}

    try:
        totals = _validate_double_entry(lines)
        checks.append({"key": "double_entry", "label": "Debit equals credit", "status": "passed"})
    except HTTPException as exc:
        errors.append(str(exc.detail))
        checks.append({"key": "double_entry", "label": "Debit equals credit", "status": "failed", "detail": exc.detail})

    try:
        _assert_period_open(db, tenant_id, posting_date, branch_id=branch_id)
        checks.append({"key": "period", "label": "Accounting period is open", "status": "passed"})
    except HTTPException as exc:
        errors.append(str(exc.detail))
        checks.append({"key": "period", "label": "Accounting period is open", "status": "failed", "detail": exc.detail})

    normalized_currency = str(currency or "INR").upper()
    currency_valid = len(normalized_currency) == 3 and normalized_currency.isalpha() and float(exchange_rate or 0.0) > 0
    if not currency_valid:
        errors.append("Currency must be a three-letter code and exchange rate must be positive")
    checks.append({
        "key": "currency",
        "label": "Currency and exchange rate are valid",
        "status": "passed" if currency_valid else "failed",
    })

    rule = None
    if source_module and str(source_module).lower() not in {"manual", "accounting"}:
        rule = _find_posting_rule(db, tenant_id, source_module, source_event or "", metadata or {})
        if not rule:
            errors.append(f"No published posting rule exists for {source_module}.{source_event}")
    checks.append({
        "key": "posting_rule",
        "label": "Posting rule exists",
        "status": "passed" if rule or str(source_module or "manual").lower() in {"manual", "accounting"} else "failed",
        "detail": rule.rule_name if rule else "Manual journal" if str(source_module or "manual").lower() in {"manual", "accounting"} else None,
    })

    account_failures = 0
    budget_failures = 0
    effective_fy = financial_year or _current_financial_year(posting_date)
    period_name = _journal_period_name(posting_date)
    for index, line in enumerate(lines, start=1):
        account = _resolve_journal_account(db, tenant_id, line.gl_account_id, line.account_code)
        if not account:
            errors.append(f"Line {index}: GL account does not exist")
            account_failures += 1
            continue
        try:
            if not _is_truthy(account.posting_allowed) or str(account.status or "").lower() != "active":
                raise HTTPException(status_code=400, detail=f"GL account {account.account_code} is not active for posting")
            _validate_account_for_line(account, line.debit or 0.0, line.credit or 0.0, posting_mode="manual")
        except HTTPException as exc:
            errors.append(f"Line {index}: {exc.detail}")
            account_failures += 1

        line_currency = str(line.currency or normalized_currency).upper()
        if len(line_currency) != 3 or not line_currency.isalpha():
            errors.append(f"Line {index}: invalid currency {line_currency}")
        if line.transaction_currency and line.transaction_currency != line_currency and float(line.exchange_rate or exchange_rate or 0.0) <= 0:
            errors.append(f"Line {index}: exchange rate is required for transaction currency {line.transaction_currency}")

        dimensions = {
            "branch": line.branch_id or branch_id,
            "department": line.department_id,
            "cost_center": line.cost_center,
            "profit_center": line.profit_center,
            "project": line.project_id,
            "employee": line.employee_id,
            "product": line.product_id,
            "business_unit": line.business_unit_id,
        }
        for dimension_type, code in dimensions.items():
            _check_dimension(db, tenant_id, dimension_type, code, errors, warnings)

        budget = db.query(AccountingBudget).filter(
            AccountingBudget.tenant_id == tenant_id,
            AccountingBudget.financial_year == effective_fy,
            AccountingBudget.period == period_name,
            AccountingBudget.gl_account_id == account.id,
            AccountingBudget.cost_center == line.cost_center,
            AccountingBudget.status == "active",
        ).first()
        if budget and (line.debit or 0.0) > 0:
            consumed = db.query(JournalLine).join(JournalEntry).filter(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.posting_status == "posted",
                JournalEntry.financial_year == effective_fy,
                JournalEntry.period == period_name,
                JournalLine.gl_account_id == account.id,
                JournalLine.cost_center == line.cost_center,
            ).all()
            used_amount = round(sum(item.debit or 0.0 for item in consumed), 2)
            if used_amount + (line.debit or 0.0) > budget.amount:
                budget_failures += 1
                errors.append(
                    f"Line {index}: budget exceeded for {account.account_code}; "
                    f"available {round(budget.amount - used_amount, 2):.2f}"
                )

        impacts.append({
            "account_id": account.id,
            "account_code": account.account_code,
            "account_name": account.account_name,
            "debit": round(line.debit or 0.0, 2),
            "credit": round(line.credit or 0.0, 2),
            "current_balance": round(account.balance or 0.0, 2),
            "projected_balance": round((account.balance or 0.0) + (line.debit or 0.0) - (line.credit or 0.0), 2),
        })

    checks.append({
        "key": "accounts",
        "label": "All accounts are active and postable",
        "status": "passed" if account_failures == 0 else "failed",
    })
    checks.append({
        "key": "dimensions",
        "label": "Branch and accounting dimensions exist",
        "status": "passed" if not any("does not exist or is inactive" in error for error in errors) else "failed",
    })

    tax_code = (metadata or {}).get("tax_code")
    tax_valid = True
    if tax_code:
        tax_valid = db.query(TaxRule).filter(
            TaxRule.tenant_id == tenant_id,
            TaxRule.tax_code == tax_code,
            TaxRule.is_active.in_(["true", "1", "yes", "active"]),
        ).first() is not None
        if not tax_valid:
            errors.append(f"Tax rule does not exist or is inactive: {tax_code}")
    checks.append({"key": "tax", "label": "Tax configuration is valid", "status": "passed" if tax_valid else "failed"})
    checks.append({"key": "budget", "label": "Budget is available", "status": "passed" if budget_failures == 0 else "failed"})

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        **totals,
        "impact": {
            "gl_accounts": impacts,
            "trial_balance": {
                "debit_change": totals.get("total_debit", 0.0),
                "credit_change": totals.get("total_credit", 0.0),
                "remains_balanced": totals.get("total_debit") == totals.get("total_credit"),
            },
        },
    }


def _journal_template_lines(template: JournalTemplate, amount: float, tenant_id: str, db: Session) -> List[PostingEngineLine]:
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Template amount must be positive")
    result = []
    for item in template.lines or []:
        account = _resolve_journal_account(db, tenant_id, account_code=item.get("account_code"))
        result.append(
            PostingEngineLine(
                gl_account_id=account.id if account else None,
                account_code=item.get("account_code"),
                debit=amount if item.get("direction") == "debit" else 0.0,
                credit=amount if item.get("direction") == "credit" else 0.0,
                currency=template.currency or "INR",
                description=item.get("description"),
            )
        )
    return result


def _create_voucher_from_journal(entry: JournalEntry, db: Session, reversal: bool = False) -> Voucher:
    voucher_type = "reversal" if reversal else (entry.voucher_type or "journal")
    voucher = Voucher(
        id=str(uuid4()),
        tenant_id=entry.tenant_id,
        voucher_number=_next_voucher_number(entry.tenant_id, voucher_type, db),
        voucher_type=voucher_type,
        voucher_date=entry.entry_date,
        description=entry.description,
        reference=entry.journal_no,
        branch_id=entry.branch_id,
        currency=entry.currency or "INR",
        status="posted",
        created_by=entry.created_by,
        verified_by=entry.approved_by,
        approved_by=entry.approved_by,
        posted_journal_entry_id=entry.id,
        metadata_json={"journal_engine": True, "journal_no": entry.journal_no, "reversal": reversal},
    )
    db.add(voucher)
    db.flush()
    for line in entry.lines:
        db.add(
            VoucherLine(
                id=str(uuid4()),
                voucher_id=voucher.id,
                gl_account_id=line.gl_account_id,
                debit=line.debit or 0.0,
                credit=line.credit or 0.0,
                description=line.description,
                department_id=line.department_id,
                cost_center=line.cost_center,
                profit_center=line.profit_center,
                project_id=line.project_id,
                employee_id=line.employee_id,
                product_id=line.product_id,
                business_unit_id=line.business_unit_id,
            )
        )
    entry.voucher_id = voucher.id
    return voucher


def _apply_journal_document_to_gl(entry: JournalEntry, db: Session) -> None:
    posting_mode = "auto" if entry.source_module and entry.source_module not in {"manual", "accounting"} else "manual"
    for line in entry.lines:
        account = _get_postable_account_by_id(line.gl_account_id, entry.tenant_id, db)
        _validate_account_for_line(account, line.debit or 0.0, line.credit or 0.0, posting_mode=posting_mode)
        account.balance += (line.debit or 0.0) - (line.credit or 0.0)
        _update_gl_balance(
            db=db,
            tenant_id=entry.tenant_id,
            account=account,
            debit=line.debit or 0.0,
            credit=line.credit or 0.0,
            branch_id=line.branch_id or entry.branch_id,
            currency=line.currency or entry.currency or account.base_currency or "INR",
            financial_year=entry.financial_year,
        )


def _journal_request_lines(lines: List[JournalLineCreate], tenant_id: str, db: Session) -> List[PostingEngineLine]:
    result = []
    for index, line in enumerate(lines, start=1):
        account = _resolve_journal_account(db, tenant_id, line.gl_account_id, line.account_code)
        if not account:
            raise HTTPException(status_code=400, detail=f"Line {index}: GL account does not exist for tenant")
        if (line.debit or 0.0) < 0 or (line.credit or 0.0) < 0:
            raise HTTPException(status_code=400, detail=f"Line {index}: debit and credit cannot be negative")
        if (line.debit or 0.0) > 0 and (line.credit or 0.0) > 0:
            raise HTTPException(status_code=400, detail=f"Line {index}: use either debit or credit, not both")
        result.append(
            PostingEngineLine(
                gl_account_id=account.id,
                account_code=account.account_code,
                debit=line.debit or 0.0,
                credit=line.credit or 0.0,
                branch_id=line.branch_id,
                currency=line.currency,
                transaction_currency=line.transaction_currency,
                transaction_amount=line.transaction_amount,
                exchange_rate=line.exchange_rate,
                department_id=line.department_id,
                cost_center=line.cost_center,
                profit_center=line.profit_center,
                project_id=line.project_id,
                employee_id=line.employee_id,
                product_id=line.product_id,
                business_unit_id=line.business_unit_id,
                description=line.description,
            )
        )
    return result


def _get_journal_document(journal_id: str, tenant_id: str, db: Session) -> JournalEntry:
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == journal_id,
        JournalEntry.tenant_id == tenant_id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal not found for tenant")
    return entry


def _refresh_journal_batch(batch_id: Optional[str], db: Session) -> None:
    if not batch_id:
        return
    batch = db.query(JournalBatch).filter(JournalBatch.id == batch_id).first()
    if not batch:
        return
    entries = db.query(JournalEntry).filter(JournalEntry.batch_id == batch_id).all()
    batch.total_amount = round(sum(sum(line.debit or 0.0 for line in entry.lines) for entry in entries), 2)
    statuses = {entry.posting_status for entry in entries}
    if entries and statuses == {"posted"}:
        batch.status = "posted"
    elif "pending" in statuses:
        batch.status = "pending"
    elif statuses and statuses.issubset({"approved", "posted"}):
        batch.status = "approved"
    elif entries and statuses.issubset({"cancelled", "reversed"}):
        batch.status = "closed"
    else:
        batch.status = "draft"


def _normalize_payment_category(category: str) -> str:
    return category.strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_receipt_category(category: str) -> str:
    return category.strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_contra_transfer_type(transfer_type: str) -> str:
    return transfer_type.strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_credit_note_type(credit_note_type: str) -> str:
    return credit_note_type.strip().lower().replace(" ", "_").replace("-", "_")


def _normalize_debit_note_type(debit_note_type: str) -> str:
    return debit_note_type.strip().lower().replace(" ", "_").replace("-", "_")


def _payment_category_options() -> list[dict]:
    return [
        {"key": key, **value}
        for key, value in PAYMENT_VOUCHER_CATEGORIES.items()
    ]


def _receipt_voucher_options() -> dict:
    return {
        "categories": [
            {"key": key, **value}
            for key, value in RECEIPT_VOUCHER_CATEGORIES.items()
        ],
        "payment_modes": RECEIPT_PAYMENT_MODES,
    }


def _contra_voucher_options() -> dict:
    return {
        "transfer_types": [
            {"key": key, **value}
            for key, value in CONTRA_TRANSFER_TYPES.items()
        ]
    }


def _credit_note_options() -> dict:
    return {
        "credit_note_types": [
            {"key": key, **value}
            for key, value in CREDIT_NOTE_TYPES.items()
        ]
    }


def _debit_note_options() -> dict:
    return {
        "debit_note_types": [
            {"key": key, **value}
            for key, value in DEBIT_NOTE_TYPES.items()
        ]
    }


def _payment_credit_account_code(payment_mode: Optional[str]) -> str:
    return "1000_CASH" if str(payment_mode or "").lower() == "cash" else "1120_BANK"


def _receipt_debit_account_code(payment_mode: Optional[str]) -> str:
    return "1000_CASH" if str(payment_mode or "").lower() == "cash" else "1120_BANK"


def _build_credit_note_payload(credit_note: CreditNoteCreate, db: Session) -> VoucherCreate:
    credit_note_key = _normalize_credit_note_type(credit_note.credit_note_type)
    note_type = CREDIT_NOTE_TYPES.get(credit_note_key)
    if not note_type:
        raise HTTPException(status_code=400, detail="Unsupported credit note type")
    if credit_note.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if not credit_note.customer_name.strip():
        raise HTTPException(status_code=400, detail="customer_name is required")

    if credit_note.debit_account_id:
        debit_account = _get_postable_account_by_id(credit_note.debit_account_id, credit_note.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            credit_note.debit_account_code or note_type["debit_account_code"],
            credit_note.tenant_id,
            db,
        )

    if credit_note.credit_account_id:
        credit_account = _get_postable_account_by_id(credit_note.credit_account_id, credit_note.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            credit_note.credit_account_code or note_type["credit_account_code"],
            credit_note.tenant_id,
            db,
        )

    amount = round(credit_note.amount, 2)
    description = credit_note.description or f"{note_type['description']} for {credit_note.customer_name}"
    metadata = {
        **(credit_note.metadata or {}),
        "credit_note": {
            "module": "module_10",
            "type": credit_note_key,
            "type_label": note_type["label"],
            "customer_name": credit_note.customer_name,
            "customer_id": credit_note.customer_id,
            "credit_note_reference": credit_note.credit_note_reference,
            "amount": amount,
        },
    }
    return VoucherCreate(
        tenant_id=credit_note.tenant_id,
        voucher_type="credit_note",
        voucher_date=credit_note.voucher_date,
        description=description,
        reference=credit_note.reference or credit_note.credit_note_reference,
        branch_id=credit_note.branch_id,
        currency=credit_note.currency or "INR",
        payment_reference=credit_note.credit_note_reference,
        payment_details=credit_note.credit_note_details,
        created_by=credit_note.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"{note_type['label']} debit",
                cost_center=credit_note.cost_center,
                profit_center=credit_note.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"{note_type['label']} credit",
                cost_center=credit_note.cost_center,
                profit_center=credit_note.profit_center,
            ),
        ],
    )


def _build_debit_note_payload(debit_note: DebitNoteCreate, db: Session) -> VoucherCreate:
    debit_note_key = _normalize_debit_note_type(debit_note.debit_note_type)
    note_type = DEBIT_NOTE_TYPES.get(debit_note_key)
    if not note_type:
        raise HTTPException(status_code=400, detail="Unsupported debit note type")
    if debit_note.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if not debit_note.customer_name.strip():
        raise HTTPException(status_code=400, detail="customer_name is required")

    if debit_note.debit_account_id:
        debit_account = _get_postable_account_by_id(debit_note.debit_account_id, debit_note.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            debit_note.debit_account_code or note_type["debit_account_code"],
            debit_note.tenant_id,
            db,
        )

    if debit_note.credit_account_id:
        credit_account = _get_postable_account_by_id(debit_note.credit_account_id, debit_note.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            debit_note.credit_account_code or note_type["credit_account_code"],
            debit_note.tenant_id,
            db,
        )

    amount = round(debit_note.amount, 2)
    description = debit_note.description or f"{note_type['description']} for {debit_note.customer_name}"
    metadata = {
        **(debit_note.metadata or {}),
        "debit_note": {
            "module": "module_11",
            "type": debit_note_key,
            "type_label": note_type["label"],
            "customer_name": debit_note.customer_name,
            "customer_id": debit_note.customer_id,
            "debit_note_reference": debit_note.debit_note_reference,
            "amount": amount,
        },
    }
    return VoucherCreate(
        tenant_id=debit_note.tenant_id,
        voucher_type="debit_note",
        voucher_date=debit_note.voucher_date,
        description=description,
        reference=debit_note.reference or debit_note.debit_note_reference,
        branch_id=debit_note.branch_id,
        currency=debit_note.currency or "INR",
        payment_reference=debit_note.debit_note_reference,
        payment_details=debit_note.debit_note_details,
        created_by=debit_note.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"{note_type['label']} debit",
                cost_center=debit_note.cost_center,
                profit_center=debit_note.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"{note_type['label']} credit",
                cost_center=debit_note.cost_center,
                profit_center=debit_note.profit_center,
            ),
        ],
    )


def _build_payment_voucher_payload(payment: PaymentVoucherCreate, db: Session) -> VoucherCreate:
    category_key = _normalize_payment_category(payment.payment_category)
    category = PAYMENT_VOUCHER_CATEGORIES.get(category_key)
    if not category:
        raise HTTPException(status_code=400, detail="Unsupported payment voucher category")
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if not payment.payee_name.strip():
        raise HTTPException(status_code=400, detail="payee_name is required")
    if not payment.payment_mode:
        raise HTTPException(status_code=400, detail="payment_mode is required")
    if payment.payment_mode != "cash" and not payment.payment_reference:
        raise HTTPException(status_code=400, detail="payment_reference is required for non-cash payment vouchers")

    if payment.debit_account_id:
        debit_account = _get_postable_account_by_id(payment.debit_account_id, payment.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            payment.debit_account_code or category["debit_account_code"],
            payment.tenant_id,
            db,
        )

    if payment.credit_account_id:
        credit_account = _get_postable_account_by_id(payment.credit_account_id, payment.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            payment.credit_account_code or _payment_credit_account_code(payment.payment_mode),
            payment.tenant_id,
            db,
        )

    amount = round(payment.amount, 2)
    description = payment.description or f"{category['description']} to {payment.payee_name}"
    metadata = {
        **(payment.metadata or {}),
        "payment_voucher": {
            "module": "module_8",
            "category": category_key,
            "category_label": category["label"],
            "payee_name": payment.payee_name,
            "amount": amount,
        },
    }
    if payment.vendor_id:
        metadata["payment_voucher"]["vendor_id"] = payment.vendor_id
    if payment.vendor_code:
        metadata["payment_voucher"]["vendor_code"] = payment.vendor_code

    return VoucherCreate(
        tenant_id=payment.tenant_id,
        voucher_type="payment",
        voucher_date=payment.voucher_date,
        description=description,
        reference=payment.reference,
        branch_id=payment.branch_id,
        currency=payment.currency or "INR",
        payment_mode=payment.payment_mode,
        payment_reference=payment.payment_reference,
        payment_details=payment.payment_details,
        created_by=payment.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"{category['label']} debit",
                cost_center=payment.cost_center,
                profit_center=payment.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"Payment via {payment.payment_mode.upper()}",
                cost_center=payment.cost_center,
                profit_center=payment.profit_center,
            ),
        ],
    )


def _build_contra_voucher_payload(contra: ContraVoucherCreate, db: Session) -> VoucherCreate:
    transfer_key = _normalize_contra_transfer_type(contra.transfer_type)
    transfer = CONTRA_TRANSFER_TYPES.get(transfer_key)
    if not transfer:
        raise HTTPException(status_code=400, detail="Unsupported contra transfer type")
    if contra.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    if contra.debit_account_id:
        debit_account = _get_postable_account_by_id(contra.debit_account_id, contra.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            contra.debit_account_code or transfer["debit_account_code"],
            contra.tenant_id,
            db,
        )

    if contra.credit_account_id:
        credit_account = _get_postable_account_by_id(contra.credit_account_id, contra.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            contra.credit_account_code or transfer["credit_account_code"],
            contra.tenant_id,
            db,
        )

    amount = round(contra.amount, 2)
    description = contra.description or transfer["description"]
    source_location = contra.source_location or transfer["source_label"]
    destination_location = contra.destination_location or transfer["destination_label"]
    metadata = {
        **(contra.metadata or {}),
        "contra_voucher": {
            "module": "module_9",
            "transfer_type": transfer_key,
            "transfer_label": transfer["label"],
            "source_location": source_location,
            "destination_location": destination_location,
            "transfer_reference": contra.transfer_reference,
            "amount": amount,
        },
    }
    return VoucherCreate(
        tenant_id=contra.tenant_id,
        voucher_type="contra",
        voucher_date=contra.voucher_date,
        description=description,
        reference=contra.reference or contra.transfer_reference,
        branch_id=contra.branch_id,
        currency=contra.currency or "INR",
        payment_reference=contra.transfer_reference,
        payment_details=contra.transfer_details,
        created_by=contra.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"{transfer['label']} debit to {destination_location}",
                cost_center=contra.cost_center,
                profit_center=contra.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"{transfer['label']} credit from {source_location}",
                cost_center=contra.cost_center,
                profit_center=contra.profit_center,
            ),
        ],
    )


def _build_receipt_voucher_payload(receipt: ReceiptVoucherCreate, db: Session) -> VoucherCreate:
    category_key = _normalize_receipt_category(receipt.receipt_category)
    category = RECEIPT_VOUCHER_CATEGORIES.get(category_key)
    if not category:
        raise HTTPException(status_code=400, detail="Unsupported receipt voucher category")
    if receipt.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")
    if not receipt.payer_name.strip():
        raise HTTPException(status_code=400, detail="payer_name is required")

    payment_mode = str(receipt.payment_mode or "").lower()
    if payment_mode not in RECEIPT_PAYMENT_MODES:
        raise HTTPException(status_code=400, detail="Unsupported receipt payment mode")
    if payment_mode != "cash" and not receipt.payment_reference:
        raise HTTPException(status_code=400, detail="payment_reference is required for non-cash receipt vouchers")

    if receipt.debit_account_id:
        debit_account = _get_postable_account_by_id(receipt.debit_account_id, receipt.tenant_id, db)
    else:
        debit_account = _get_postable_account_by_code(
            receipt.debit_account_code or _receipt_debit_account_code(payment_mode),
            receipt.tenant_id,
            db,
        )

    if receipt.credit_account_id:
        credit_account = _get_postable_account_by_id(receipt.credit_account_id, receipt.tenant_id, db)
    else:
        credit_account = _get_postable_account_by_code(
            receipt.credit_account_code or category["credit_account_code"],
            receipt.tenant_id,
            db,
        )

    amount = round(receipt.amount, 2)
    description = receipt.description or f"{category['description']} from {receipt.payer_name}"
    metadata = {
        **(receipt.metadata or {}),
        "receipt_voucher": {
            "module": "module_7",
            "category": category_key,
            "category_label": category["label"],
            "payer_name": receipt.payer_name,
            "customer_id": receipt.customer_id,
            "amount": amount,
            "payment_mode": payment_mode,
        },
    }
    return VoucherCreate(
        tenant_id=receipt.tenant_id,
        voucher_type="receipt",
        voucher_date=receipt.voucher_date,
        description=description,
        reference=receipt.reference,
        branch_id=receipt.branch_id,
        currency=receipt.currency or "INR",
        payment_mode=payment_mode,
        payment_reference=receipt.payment_reference,
        payment_details=receipt.payment_details,
        created_by=receipt.created_by,
        metadata=metadata,
        lines=[
            VoucherLineCreate(
                gl_account_id=debit_account.id,
                debit=amount,
                credit=0.0,
                description=f"Receipt via {payment_mode.upper()}",
                cost_center=receipt.cost_center,
                profit_center=receipt.profit_center,
            ),
            VoucherLineCreate(
                gl_account_id=credit_account.id,
                debit=0.0,
                credit=amount,
                description=f"{category['label']} credit",
                cost_center=receipt.cost_center,
                profit_center=receipt.profit_center,
            ),
        ],
    )


def _period_filter(query, start_date: Optional[datetime], end_date: Optional[datetime]):
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
    return query


def _account_balances(
    tenant_id: str,
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> list[dict]:
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    rows = []
    for account in accounts:
        query = (
            db.query(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .filter(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.posting_status != "failed",
                JournalLine.gl_account_id == account.id,
            )
        )
        query = _period_filter(query, start_date, end_date)
        debit = 0.0
        credit = 0.0
        for line in query.all():
            debit += line.debit or 0.0
            credit += line.credit or 0.0
        rows.append(
            {
                "account": account,
                "debit": round(debit, 2),
                "credit": round(credit, 2),
                "balance": round(debit - credit, 2),
            }
        )
    return rows


def _financial_rows_from_balances(account_balances: list[dict], account_types: set[str]):
    rows = []
    total = 0.0
    for item in account_balances:
        account = item["account"]
        if account.account_type not in account_types:
            continue
        normal_balance = item["balance"]
        if account.account_type in {"liability", "equity", "revenue"}:
            normal_balance = -normal_balance
        total += normal_balance
        rows.append(
            {
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "amount": round(normal_balance, 2),
            }
        )
    return rows, round(total, 2)


def _tax_breakdown(tax_type: str, taxable_amount: float, rate_percent: float) -> dict:
    tax_type_normalized = tax_type.lower()
    tax_amount = round(taxable_amount * rate_percent / 100, 2)
    if tax_type_normalized == "gst":
        component_rate = round(rate_percent / 2, 4)
        component_amount = round(tax_amount / 2, 2)
        return {
            "taxable_amount": taxable_amount,
            "total_rate_percent": rate_percent,
            "total_tax_amount": tax_amount,
            "components": [
                {"name": "CGST", "rate_percent": component_rate, "amount": component_amount},
                {"name": "SGST", "rate_percent": component_rate, "amount": round(tax_amount - component_amount, 2)},
            ],
        }
    return {
        "taxable_amount": taxable_amount,
        "total_rate_percent": rate_percent,
        "total_tax_amount": tax_amount,
        "components": [
            {"name": tax_type.upper(), "rate_percent": rate_percent, "amount": tax_amount},
        ],
    }


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "accounting"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/gl-accounts", response_model=GLAccountResponse)
async def create_gl_account(account: GLAccountCreate, db: Session = Depends(get_db)):

    if not account.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = (
        db.query(GLAccount)
        .filter(
            GLAccount.tenant_id == account.tenant_id,
            GLAccount.account_code == account.account_code,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="GL account code already exists for tenant")

    _validate_parent_account(db, account.tenant_id, account.parent_account_id)

    new_account = GLAccount(
        id=str(uuid4()),
        tenant_id=account.tenant_id,
        account_code=account.account_code,
        account_name=account.account_name,
        account_type=account.account_type,
        parent_account_id=account.parent_account_id,
        category=account.category or account.account_type,
        currency=account.currency or "INR",
        base_currency=account.base_currency or account.currency or "INR",
        normal_balance=account.normal_balance,
        branch_id=account.branch_id,
        branch_specific=account.branch_specific or "false",
        posting_allowed=account.posting_allowed or "true",
        allow_manual_posting=account.allow_manual_posting or "true",
        allow_auto_posting=account.allow_auto_posting or "true",
        requires_approval=account.requires_approval or "false",
        freeze_status=account.freeze_status or "open",
        status=account.status or "active",
        exchange_gain_loss_account_code=account.exchange_gain_loss_account_code,
        revaluation_account_code=account.revaluation_account_code,
        opening_balance=account.opening_balance or 0.0,
        financial_year=account.financial_year,
        metadata_json=account.metadata,
        balance=0.0
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@app.get("/gl-accounts", response_model=List[GLAccountResponse])
async def list_gl_accounts(
    tenant_id: str = Query(...),
    category: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
    posting_allowed: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id)
    if category:
        query = query.filter(GLAccount.category == category)
    if account_type:
        query = query.filter(GLAccount.account_type == account_type)
    if posting_allowed:
        query = query.filter(GLAccount.posting_allowed == posting_allowed)
    if status:
        query = query.filter(GLAccount.status == status)
    return query.order_by(GLAccount.account_code).all()


@app.get("/gl-accounts/summary")
async def gl_account_summary(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    categories: dict[str, dict] = {}
    for account in accounts:
        key = account.category or account.account_type or "Uncategorized"
        if key not in categories:
            categories[key] = {"category": key, "count": 0, "posting_allowed": 0, "control_accounts": 0, "balance": 0.0}
        categories[key]["count"] += 1
        if _is_truthy(account.posting_allowed):
            categories[key]["posting_allowed"] += 1
        else:
            categories[key]["control_accounts"] += 1
        categories[key]["balance"] = round(categories[key]["balance"] + (account.balance or 0.0), 2)
    return {
        "tenant_id": tenant_id,
        "total_accounts": len(accounts),
        "posting_accounts": sum(1 for account in accounts if _is_truthy(account.posting_allowed)),
        "control_accounts": sum(1 for account in accounts if not _is_truthy(account.posting_allowed)),
        "categories": sorted(categories.values(), key=lambda row: row["category"]),
    }


@app.get("/gl-accounts/hierarchy")
async def gl_account_hierarchy(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).order_by(GLAccount.account_code).all()
    return {"tenant_id": tenant_id, "items": _build_coa_tree(accounts)}


@app.post("/gl-accounts/seed-defaults")
async def seed_default_gl_accounts(request: COASeedRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    existing_by_code = {
        account.account_code: account
        for account in db.query(GLAccount).filter(GLAccount.tenant_id == request.tenant_id).all()
    }
    created = []
    for item in DEFAULT_NBFC_COA:
        if item["account_code"] in existing_by_code:
            continue
        parent = existing_by_code.get(item.get("parent_code"))
        account = GLAccount(
            id=str(uuid4()),
            tenant_id=request.tenant_id,
            account_code=item["account_code"],
            account_name=item["account_name"],
            account_type=item["account_type"],
            parent_account_id=parent.id if parent else None,
            category=item["category"],
            currency=request.currency or "INR",
            base_currency=request.currency or "INR",
            branch_specific=item.get("branch_specific", "false"),
            posting_allowed=item.get("posting_allowed", "true"),
            allow_manual_posting="true",
            allow_auto_posting="true",
            freeze_status="open",
            status="active",
            opening_balance=0.0,
            financial_year=request.financial_year,
            balance=0.0,
        )
        db.add(account)
        db.flush()
        existing_by_code[account.account_code] = account
        created.append(account.account_code)
    _log_audit(
        db,
        request.tenant_id,
        "gl_account",
        None,
        "seed_defaults",
        {"created": created, "count": len(created)},
    )
    db.commit()
    return {"tenant_id": request.tenant_id, "created": created, "created_count": len(created)}


@app.put("/gl-accounts/{account_id}", response_model=GLAccountResponse)
async def update_gl_account(account_id: str, payload: GLAccountUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    account = db.query(GLAccount).filter(GLAccount.id == account_id, GLAccount.tenant_id == tenant_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL account not found for tenant")
    if payload.parent_account_id is not None:
        _validate_parent_account(db, tenant_id, payload.parent_account_id, account_id=account.id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(account, "metadata_json" if field == "metadata" else field, value)
    db.commit()
    db.refresh(account)
    return account


@app.get("/api/v1/gl/ledger/dashboard")
async def api_gl_ledger_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _ledger_dashboard_payload(tenant_id, db)


@app.get("/api/v1/gl/ledger/balances")
async def api_gl_ledger_balances(
    tenant_id: str = Query(...),
    financial_year: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return _ledger_balances_payload(tenant_id, db, financial_year=financial_year, branch_id=branch_id, limit=limit, offset=offset)


@app.get("/api/v1/gl/ledger/entries")
async def api_gl_ledger_entries(
    tenant_id: str = Query(...),
    branch_id: Optional[str] = Query(None),
    source_module: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return _ledger_entries_payload(tenant_id, db, limit=limit, offset=offset, branch_id=branch_id, source_module=source_module)


@app.get("/api/v1/gl/ledger/health")
async def api_gl_ledger_health(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _ledger_health_payload(tenant_id, db)


@app.get("/api/v1/gl/dashboard")
async def api_gl_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _coa_dashboard_payload(tenant_id, db)


@app.get("/api/v1/gl/accounts")
async def api_list_gl_accounts(
    tenant_id: str = Query(...),
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    account_type: Optional[str] = Query(None),
    posting_allowed: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    query = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (GLAccount.account_code.ilike(like))
            | (GLAccount.account_name.ilike(like))
            | (GLAccount.category.ilike(like))
            | (GLAccount.account_type.ilike(like))
        )
    if category:
        query = query.filter(GLAccount.category == category)
    if account_type:
        query = query.filter(GLAccount.account_type == account_type)
    if posting_allowed:
        query = query.filter(GLAccount.posting_allowed == posting_allowed)
    if status:
        query = query.filter(GLAccount.status == status)
    total = query.count()
    rows = query.order_by(GLAccount.account_code).offset(offset).limit(limit).all()
    all_accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    child_counts = _coa_child_counts(all_accounts)
    return {
        "tenant_id": tenant_id,
        "total": total,
        "items": [_gl_account_api_item(account, child_counts.get(account.id, 0)) for account in rows],
    }


@app.post("/api/v1/gl/accounts")
async def api_create_gl_account(account: GLAccountCreate, db: Session = Depends(get_db)):
    created = await create_gl_account(account, db)
    _log_audit(db, account.tenant_id, "gl_account", created.id, "api_create", {"account_code": created.account_code})
    db.commit()
    db.refresh(created)
    child_counts = _coa_child_counts(db.query(GLAccount).filter(GLAccount.tenant_id == account.tenant_id).all())
    return _gl_account_api_item(created, child_counts.get(created.id, 0))


@app.post("/api/v1/gl/accounts/seed-defaults")
async def api_seed_default_gl_accounts(request: COASeedRequest, db: Session = Depends(get_db)):
    return await seed_default_gl_accounts(request, db)


@app.get("/api/v1/gl/accounts/tree")
async def api_gl_accounts_tree(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return await gl_account_hierarchy(tenant_id, db)


@app.get("/api/v1/gl/accounts/search")
async def api_search_gl_accounts(
    tenant_id: str = Query(...),
    q: str = Query(""),
    limit: int = Query(20),
    db: Session = Depends(get_db),
):
    query_text = q.lower().strip()
    query = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id)
    if query_text:
        like = f"%{query_text}%"
        query = query.filter(
            (GLAccount.account_code.ilike(like))
            | (GLAccount.account_name.ilike(like))
            | (GLAccount.category.ilike(like))
            | (GLAccount.account_type.ilike(like))
        )
    rows = query.order_by(GLAccount.account_code).limit(limit).all()
    child_counts = _coa_child_counts(db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all())
    return {
        "tenant_id": tenant_id,
        "query": q,
        "items": [_gl_account_api_item(account, child_counts.get(account.id, 0)) for account in rows],
    }


@app.get("/api/v1/gl/accounts/{account_id}")
async def api_get_gl_account(account_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    account = db.query(GLAccount).filter(GLAccount.id == account_id, GLAccount.tenant_id == tenant_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL account not found for tenant")
    child_counts = _coa_child_counts(db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all())
    return _gl_account_api_item(account, child_counts.get(account.id, 0))


@app.put("/api/v1/gl/accounts/{account_id}")
async def api_update_gl_account(
    account_id: str,
    payload: GLAccountUpdate,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    updated = await update_gl_account(account_id, payload, tenant_id, db)
    _log_audit(db, tenant_id, "gl_account", updated.id, "api_update", payload.dict(exclude_unset=True))
    db.commit()
    db.refresh(updated)
    child_counts = _coa_child_counts(db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all())
    return _gl_account_api_item(updated, child_counts.get(updated.id, 0))


@app.patch("/api/v1/gl/accounts/{account_id}/status")
async def api_update_gl_account_status(
    account_id: str,
    payload: GLAccountStatusUpdate,
    db: Session = Depends(get_db),
):
    account = db.query(GLAccount).filter(GLAccount.id == account_id, GLAccount.tenant_id == payload.tenant_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL account not found for tenant")
    allowed = {
        "draft": {"finance_review", "inactive"},
        "finance_review": {"cfo_review", "draft"},
        "cfo_review": {"approved", "finance_review"},
        "approved": {"published", "active"},
        "published": {"active", "inactive"},
        "active": {"inactive"},
        "inactive": {"active"},
    }
    current = (account.status or "active").lower()
    new_status = payload.status.lower()
    if new_status != current and new_status not in allowed.get(current, set()):
        raise HTTPException(status_code=400, detail=f"Invalid status transition from {account.status} to {payload.status}")
    account.status = new_status
    _log_audit(db, payload.tenant_id, "gl_account", account.id, "status_changed", {"status": new_status}, payload.performed_by)
    db.commit()
    db.refresh(account)
    child_counts = _coa_child_counts(db.query(GLAccount).filter(GLAccount.tenant_id == payload.tenant_id).all())
    return _gl_account_api_item(account, child_counts.get(account.id, 0))


@app.get("/api/v1/gl/accounts/{account_id}/usage")
async def api_gl_account_usage(account_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    account = db.query(GLAccount).filter(GLAccount.id == account_id, GLAccount.tenant_id == tenant_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL account not found for tenant")
    lines = (
        db.query(JournalLine)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .filter(JournalEntry.tenant_id == tenant_id, JournalLine.gl_account_id == account_id)
        .order_by(JournalEntry.entry_date.desc())
        .limit(100)
        .all()
    )
    entry_ids = [line.journal_entry_id for line in lines]
    entries = {
        entry.id: entry
        for entry in db.query(JournalEntry).filter(JournalEntry.id.in_(entry_ids)).all()
    } if entry_ids else {}
    total_debit = round(sum(line.debit or 0.0 for line in lines), 2)
    total_credit = round(sum(line.credit or 0.0 for line in lines), 2)
    source_totals: dict[str, float] = {}
    for line in lines:
        entry = entries.get(line.journal_entry_id)
        source = entry.source_module if entry and entry.source_module else "manual"
        source_totals[source] = round(source_totals.get(source, 0.0) + (line.debit or 0.0) + (line.credit or 0.0), 2)
    return {
        "tenant_id": tenant_id,
        "account": _gl_account_api_item(account),
        "summary": {
            "transaction_count": len(lines),
            "total_debit": total_debit,
            "total_credit": total_credit,
            "net_movement": round(total_debit - total_credit, 2),
            "last_activity": entries[lines[0].journal_entry_id].entry_date if lines and lines[0].journal_entry_id in entries else None,
            "ai_summary": f"{account.account_name} has {len(lines)} recent journal lines and net movement {round(total_debit - total_credit, 2)}.",
        },
        "source_modules": [{"source_module": key, "amount": value} for key, value in sorted(source_totals.items())],
        "recent_lines": [
            {
                "journal_entry_id": line.journal_entry_id,
                "entry_date": entries[line.journal_entry_id].entry_date if line.journal_entry_id in entries else None,
                "description": line.description,
                "debit": line.debit,
                "credit": line.credit,
                "currency": line.currency,
                "branch_id": line.branch_id,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
            }
            for line in lines[:25]
        ],
    }


@app.get("/api/v1/accounting/calendar/dashboard")
async def api_accounting_calendar_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _calendar_dashboard_payload(tenant_id, db)


@app.get("/api/v1/accounting/calendar/years")
async def api_list_financial_years(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    years = db.query(FinancialYear).filter(FinancialYear.tenant_id == tenant_id).order_by(FinancialYear.start_date.desc()).all()
    return {"tenant_id": tenant_id, "items": [_financial_year_response(year) for year in years]}


@app.post("/api/v1/accounting/calendar/years")
async def api_create_financial_year(payload: FinancialYearCreate, db: Session = Depends(get_db)):
    if payload.end_date <= payload.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    existing = db.query(FinancialYear).filter(FinancialYear.tenant_id == payload.tenant_id, FinancialYear.year_code == payload.year_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Financial year already exists for tenant")
    year = FinancialYear(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        year_code=payload.year_code,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        calendar_type=payload.calendar_type or "fiscal",
        status=payload.status or "draft",
        calendars=payload.calendars or ["Corporate", "Tax", "Treasury"],
        close_schedule=payload.close_schedule or {"daily_close": "EOD", "month_close": "M+5", "year_close": "Y+30"},
        created_by=payload.performed_by,
        activated_by=payload.performed_by if payload.status == "active" else None,
    )
    db.add(year)
    generated_periods: list[AccountingPeriod] = []
    if _is_truthy(payload.generate_periods):
        generated_periods = _generate_financial_year_periods(db, year, payload.performed_by)
    _log_audit(
        db,
        payload.tenant_id,
        "financial_year",
        year.id,
        "create",
        {"year_code": year.year_code, "generated_periods": len(generated_periods)},
        payload.performed_by,
    )
    db.commit()
    db.refresh(year)
    return {
        "financial_year": _financial_year_response(year),
        "generated_periods": [_calendar_period_item(period) for period in generated_periods],
        "generated_count": len(generated_periods),
    }


@app.get("/api/v1/accounting/calendar/periods")
async def api_list_calendar_periods(
    tenant_id: str = Query(...),
    financial_year: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingPeriod).filter(AccountingPeriod.tenant_id == tenant_id)
    if financial_year:
        query = query.filter(AccountingPeriod.financial_year == financial_year)
    if status:
        query = query.filter(AccountingPeriod.status == status)
    periods = query.order_by(AccountingPeriod.period_start.asc()).all()
    return {"tenant_id": tenant_id, "items": [_calendar_period_item(period) for period in periods]}


def _calendar_period_action(period_id: str, request: AccountingPeriodActionRequest, db: Session, new_status: str, action: str) -> dict:
    period = db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id, AccountingPeriod.tenant_id == request.tenant_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Accounting period not found for tenant")
    period.status = new_status
    if new_status in {"hard_close", "locked"}:
        period.locked_by = request.performed_by
        period.lock_reason = request.reason
    if action == "reopen":
        period.unlocked_by = request.performed_by
        period.unlock_reason = request.reason
    period.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "accounting_period", period.id, action, _period_response(period), request.performed_by)
    db.commit()
    db.refresh(period)
    return _calendar_period_item(period)


@app.post("/api/v1/accounting/calendar/periods/{period_id}/open")
async def api_open_calendar_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    return _calendar_period_action(period_id, request, db, "open", "open")


@app.post("/api/v1/accounting/calendar/periods/{period_id}/soft-close")
async def api_soft_close_calendar_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    return _calendar_period_action(period_id, request, db, "soft_close", "soft_close")


@app.post("/api/v1/accounting/calendar/periods/{period_id}/hard-close")
async def api_hard_close_calendar_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    return _calendar_period_action(period_id, request, db, "hard_close", "hard_close")


@app.post("/api/v1/accounting/calendar/periods/{period_id}/reopen")
async def api_reopen_calendar_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    return _calendar_period_action(period_id, request, db, "open", "reopen")


@app.get("/api/v1/accounting/calendar/eod")
async def api_calendar_eod(tenant_id: str = Query(...), branch_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(DayEndClose).filter(DayEndClose.tenant_id == tenant_id)
    if branch_id:
        query = query.filter(DayEndClose.branch_id == branch_id)
    closes = query.order_by(DayEndClose.business_date.desc()).limit(20).all()
    return {
        "tenant_id": tenant_id,
        "branch_id": branch_id,
        "business_day": {
            "date": datetime.utcnow().date().isoformat(),
            "status": "closed" if closes and closes[0].business_date.date() == datetime.utcnow().date() else "open",
            "lifecycle": ["Open", "Transactions", "Validation", "EOD", "Closed"],
        },
        "items": [
            {
                "id": close.id,
                "business_date": close.business_date,
                "branch_id": close.branch_id,
                "status": close.status,
                "is_balanced": close.is_balanced,
                "closed_by": close.closed_by,
                "closed_at": close.closed_at,
                "checks": close.checks,
            }
            for close in closes
        ],
    }


@app.post("/api/v1/accounting/calendar/eod/execute")
async def api_execute_calendar_eod(request: CalendarCloseExecutionRequest, db: Session = Depends(get_db)):
    close = await close_day(
        DayEndCloseRequest(
            tenant_id=request.tenant_id,
            business_date=request.business_date or datetime.utcnow(),
            branch_id=request.branch_id,
            closed_by=request.performed_by,
        ),
        db,
    )
    return {"event": "EOD_COMPLETED", "close": close}


@app.post("/api/v1/accounting/calendar/eom/execute")
async def api_execute_calendar_eom(request: CalendarCloseExecutionRequest, db: Session = Depends(get_db)):
    if not request.period_id:
        raise HTTPException(status_code=400, detail="period_id is required for EOM execution")
    period = _calendar_period_action(
        request.period_id,
        AccountingPeriodActionRequest(tenant_id=request.tenant_id, performed_by=request.performed_by, reason=request.reason or "EOM close"),
        db,
        "hard_close",
        "eom_execute",
    )
    return {
        "event": "EOM_COMPLETED",
        "period": period,
        "checklist": ["Interest Accrual", "Depreciation", "Provisioning", "GL Reconciliation", "Trial Balance", "Close Month"],
    }


@app.post("/api/v1/accounting/calendar/eoy/execute")
async def api_execute_calendar_eoy(request: CalendarCloseExecutionRequest, db: Session = Depends(get_db)):
    if not request.financial_year:
        raise HTTPException(status_code=400, detail="financial_year is required for EOY execution")
    periods = db.query(AccountingPeriod).filter(AccountingPeriod.tenant_id == request.tenant_id, AccountingPeriod.financial_year == request.financial_year).all()
    closed = 0
    for period in periods:
        if period.status != "archived":
            period.status = "archived"
            period.locked_by = request.performed_by
            period.lock_reason = request.reason or "EOY archive"
            period.updated_at = datetime.utcnow()
            closed += 1
    year = db.query(FinancialYear).filter(FinancialYear.tenant_id == request.tenant_id, FinancialYear.year_code == request.financial_year).first()
    if year:
        year.status = "archived"
        year.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "financial_year", request.financial_year, "eoy_execute", {"periods_archived": closed}, request.performed_by)
    db.commit()
    return {
        "event": "EOY_COMPLETED",
        "financial_year": request.financial_year,
        "periods_archived": closed,
        "checklist": ["Close Journals", "Final Trial Balance", "Profit Transfer", "Opening Balance", "Archive"],
    }


@app.post("/api/v1/accounting/events")
async def api_create_accounting_event(payload: AccountingEventCreate, db: Session = Depends(get_db)):
    event_payload = payload.payload or {}
    amount = payload.amount if payload.amount is not None else event_payload.get("amount")
    event = AccountingEvent(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        event_type=payload.event_type.strip().upper(),
        source_module=payload.source_module.strip(),
        reference_id=payload.reference_id.strip(),
        reference_number=payload.reference_number,
        business_date=payload.business_date or datetime.utcnow(),
        currency=payload.currency or event_payload.get("currency") or "INR",
        amount=float(amount) if amount not in {None, ""} else None,
        priority=(payload.priority or "normal").lower(),
        status="created",
        queue_status="priority_queue" if (payload.priority or "normal").lower() in {"high", "urgent", "priority"} else "normal_queue",
        validation_status="pending",
        dimensions=payload.dimensions or event_payload.get("dimensions") or {},
        payload=event_payload,
        metadata_json=payload.metadata or {},
        created_by=payload.created_by,
    )
    db.add(event)
    _log_audit(
        db,
        payload.tenant_id,
        "accounting_event",
        event.id,
        "create",
        {"event_type": event.event_type, "source_module": event.source_module, "reference_id": event.reference_id},
        payload.created_by,
    )
    db.commit()
    db.refresh(event)
    return _accounting_event_response(event)


@app.get("/api/v1/accounting/events")
async def api_list_accounting_events(
    tenant_id: str = Query(...),
    q: Optional[str] = Query(None),
    source_module: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    queue_status: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingEvent).filter(AccountingEvent.tenant_id == tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (AccountingEvent.event_type.ilike(like))
            | (AccountingEvent.source_module.ilike(like))
            | (AccountingEvent.reference_id.ilike(like))
            | (AccountingEvent.reference_number.ilike(like))
        )
    if source_module:
        query = query.filter(AccountingEvent.source_module == source_module)
    if status:
        query = query.filter(AccountingEvent.status == status)
    if queue_status:
        query = query.filter(AccountingEvent.queue_status == queue_status)
    total = query.count()
    rows = query.order_by(AccountingEvent.created_at.desc()).offset(offset).limit(limit).all()
    return {"tenant_id": tenant_id, "total": total, "items": [_accounting_event_response(event) for event in rows]}


@app.get("/api/v1/accounting/events/dashboard")
async def api_accounting_events_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _accounting_events_dashboard_payload(tenant_id, db)


@app.get("/api/v1/accounting/events/queue")
async def api_accounting_events_queue(
    tenant_id: str = Query(...),
    queue_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingEvent).filter(AccountingEvent.tenant_id == tenant_id)
    if queue_status:
        query = query.filter(AccountingEvent.queue_status == queue_status)
    else:
        query = query.filter(AccountingEvent.queue_status.in_(["priority_queue", "normal_queue", "retry_queue", "dead_letter_queue"]))
    rows = query.order_by(AccountingEvent.priority.desc(), AccountingEvent.created_at.asc()).limit(100).all()
    counts: dict[str, int] = {}
    all_events = db.query(AccountingEvent).filter(AccountingEvent.tenant_id == tenant_id).all()
    for event in all_events:
        counts[event.queue_status] = counts.get(event.queue_status, 0) + 1
    return {
        "tenant_id": tenant_id,
        "queue_status": queue_status,
        "counts": counts,
        "items": [_accounting_event_response(event) for event in rows],
    }


@app.get("/api/v1/accounting/events/{event_id}")
async def api_get_accounting_event(event_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    event = db.query(AccountingEvent).filter(AccountingEvent.id == event_id, AccountingEvent.tenant_id == tenant_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Accounting event not found for tenant")
    return _event_360_payload(event)


@app.post("/api/v1/accounting/events/{event_id}/validate")
async def api_validate_accounting_event(event_id: str, request: AccountingEventActionRequest, db: Session = Depends(get_db)):
    event = db.query(AccountingEvent).filter(AccountingEvent.id == event_id, AccountingEvent.tenant_id == request.tenant_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Accounting event not found for tenant")
    result = _validate_accounting_event(event, db)
    event.validation_result = result
    event.validation_status = result["status"]
    event.processing_time_ms = result["processing_time_ms"]
    event.posting_rule_id = result.get("posting_rule_id")
    event.updated_at = datetime.utcnow()
    if result["status"] == "passed":
        event.status = "queued"
        event.queue_status = "priority_queue" if event.priority in {"high", "urgent", "priority"} else "normal_queue"
        event.dead_letter_reason = None
        action = "validate"
    else:
        event.status = "failed"
        event.queue_status = "dead_letter_queue"
        event.dead_letter_reason = "; ".join(result.get("errors") or ["Validation failed"])
        action = "validate_failed"
    _log_audit(db, request.tenant_id, "accounting_event", event.id, action, result, request.performed_by)
    db.commit()
    db.refresh(event)
    return _event_360_payload(event)


@app.post("/api/v1/accounting/events/{event_id}/retry")
async def api_retry_accounting_event(event_id: str, request: AccountingEventActionRequest, db: Session = Depends(get_db)):
    event = db.query(AccountingEvent).filter(AccountingEvent.id == event_id, AccountingEvent.tenant_id == request.tenant_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Accounting event not found for tenant")
    intervals = [1, 5, 15, 30]
    retry_count = (event.retry_count or 0) + 1
    event.retry_count = retry_count
    event.next_retry_at = datetime.utcnow() + timedelta(minutes=intervals[min(retry_count - 1, len(intervals) - 1)])
    event.status = "queued"
    event.queue_status = "retry_queue"
    event.validation_status = "pending"
    event.dead_letter_reason = None
    event.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "accounting_event", event.id, "retry", {"retry_count": retry_count, "reason": request.reason}, request.performed_by)
    db.commit()
    db.refresh(event)
    return _event_360_payload(event)


@app.post("/api/v1/accounting/events/{event_id}/replay")
async def api_replay_accounting_event(event_id: str, request: AccountingEventActionRequest, db: Session = Depends(get_db)):
    event = db.query(AccountingEvent).filter(AccountingEvent.id == event_id, AccountingEvent.tenant_id == request.tenant_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Accounting event not found for tenant")
    event.version = (event.version or 1) + 1
    event.status = "queued"
    event.queue_status = "priority_queue" if event.priority in {"high", "urgent", "priority"} else "normal_queue"
    event.validation_status = "pending"
    event.dead_letter_reason = None
    event.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "accounting_event", event.id, "replay", {"version": event.version, "reason": request.reason}, request.performed_by)
    db.commit()
    db.refresh(event)
    return _event_360_payload(event)


@app.get("/api/v1/accounting/journals/dashboard")
async def api_journals_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _journal_dashboard_payload(tenant_id, db)


@app.get("/api/v1/accounting/journals/search")
async def api_search_journals(
    tenant_id: str = Query(...),
    q: str = Query(""),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    journal_type: Optional[str] = Query(None),
    source_module: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=250),
    db: Session = Depends(get_db),
):
    query = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (JournalEntry.journal_no.ilike(like))
            | (JournalEntry.description.ilike(like))
            | (JournalEntry.reference.ilike(like))
            | (JournalEntry.source_reference.ilike(like))
            | (JournalEntry.source_event.ilike(like))
            | (JournalEntry.branch_id.ilike(like))
        )
    if status:
        query = query.filter(JournalEntry.posting_status == status)
    if journal_type:
        query = query.filter(JournalEntry.voucher_type == journal_type)
    if source_module:
        query = query.filter(JournalEntry.source_module == source_module)
    rows = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc()).limit(500).all()
    filtered = []
    for journal in rows:
        amount = round(sum(line.debit or 0.0 for line in journal.lines), 2)
        if min_amount is not None and amount < min_amount:
            continue
        if max_amount is not None and amount > max_amount:
            continue
        filtered.append(journal)
        if len(filtered) >= limit:
            break
    return {"tenant_id": tenant_id, "query": q, "total": len(filtered), "items": [_journal_api_item(item) for item in filtered]}


@app.get("/api/v1/accounting/journals")
async def api_list_journals(
    tenant_id: str = Query(...),
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    journal_type: Optional[str] = Query(None),
    source_module: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (JournalEntry.journal_no.ilike(like))
            | (JournalEntry.description.ilike(like))
            | (JournalEntry.reference.ilike(like))
            | (JournalEntry.source_reference.ilike(like))
        )
    if status:
        statuses = [item.strip() for item in status.split(",") if item.strip()]
        query = query.filter(JournalEntry.posting_status.in_(statuses))
    if journal_type:
        query = query.filter(JournalEntry.voucher_type == journal_type)
    if source_module:
        query = query.filter(JournalEntry.source_module == source_module)
    if branch_id:
        query = query.filter(JournalEntry.branch_id == branch_id)
    total = query.count()
    rows = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc()).offset(offset).limit(limit).all()
    status_rows = db.query(JournalEntry.posting_status, JournalEntry.id).filter(JournalEntry.tenant_id == tenant_id).all()
    status_counts: dict[str, int] = {}
    for item_status, _ in status_rows:
        status_counts[item_status or "draft"] = status_counts.get(item_status or "draft", 0) + 1
    return {"tenant_id": tenant_id, "total": total, "status_counts": status_counts, "items": [_journal_api_item(item) for item in rows]}


@app.post("/api/v1/accounting/journals")
async def api_create_journal(request: JournalDocumentCreate, db: Session = Depends(get_db)):
    created = await create_journal_document(request, db)
    persisted = db.query(JournalEntry).filter(JournalEntry.id == created["id"], JournalEntry.tenant_id == request.tenant_id).first()
    return _journal_360_payload(persisted, db) if persisted else created


@app.get("/api/v1/accounting/journals/{journal_id}")
async def api_get_journal(journal_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _journal_360_payload(_get_journal_document(journal_id, tenant_id, db), db)


@app.put("/api/v1/accounting/journals/{journal_id}")
async def api_update_journal(journal_id: str, request: JournalDocumentUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, tenant_id, db)
    if journal.posting_status not in {"draft", "pending"}:
        raise HTTPException(status_code=400, detail="Only draft or pending journals can be updated")
    posting_date = request.posting_date or journal.entry_date or datetime.utcnow()
    financial_year = request.financial_year or journal.financial_year or _current_financial_year(posting_date)
    if request.batch_id is not None:
        journal.batch_id = request.batch_id
    if request.posting_date is not None:
        journal.entry_date = posting_date
        journal.business_date = posting_date
        journal.period = _journal_period_name(posting_date)
    if request.voucher_type is not None:
        journal.voucher_type = request.voucher_type
    if request.source_module is not None:
        journal.source_module = request.source_module
    if request.source_event is not None:
        journal.source_event = request.source_event
    if request.source_reference is not None:
        journal.source_reference = request.source_reference
    if request.description is not None:
        journal.description = request.description
    if request.reference is not None:
        journal.reference = request.reference
    if request.currency is not None:
        journal.currency = str(request.currency or "INR").upper()
    if request.exchange_rate is not None:
        journal.exchange_rate = request.exchange_rate
    if request.branch_id is not None:
        journal.branch_id = request.branch_id
    if request.financial_year is not None:
        journal.financial_year = financial_year
    if request.template_id is not None:
        journal.template_id = request.template_id
    if request.metadata is not None:
        journal.metadata_json = request.metadata
    if request.lines is not None:
        if len(request.lines) < 2:
            raise HTTPException(status_code=400, detail="Journal must contain at least two lines")
        engine_lines = _journal_request_lines(request.lines, tenant_id, db)
        db.query(JournalLine).filter(JournalLine.journal_entry_id == journal.id).delete(synchronize_session=False)
        db.flush()
        for index, line in enumerate(engine_lines, start=1):
            source = request.lines[index - 1]
            db.add(JournalLine(
                id=str(uuid4()), journal_entry_id=journal.id, sequence=source.sequence or index,
                gl_account_id=line.gl_account_id, debit=line.debit, credit=line.credit,
                currency=line.currency or journal.currency, transaction_currency=line.transaction_currency,
                transaction_amount=line.transaction_amount, exchange_rate=line.exchange_rate,
                branch_id=line.branch_id or journal.branch_id, department_id=line.department_id,
                cost_center=line.cost_center, profit_center=line.profit_center, project_id=line.project_id,
                employee_id=line.employee_id, product_id=line.product_id, business_unit_id=line.business_unit_id,
                description=line.description,
            ))
    if request.attachments is not None:
        db.query(JournalAttachment).filter(JournalAttachment.journal_id == journal.id).delete(synchronize_session=False)
        for attachment in request.attachments:
            db.add(JournalAttachment(
                id=str(uuid4()), journal_id=journal.id, document_id=attachment.document_id,
                file_name=attachment.file_name, uploaded_by=attachment.uploaded_by or request.performed_by,
            ))
    db.flush()
    journal.validation_result = _journal_validation(
        db, tenant_id, _engine_lines_from_document(journal), journal.entry_date,
        source_module=journal.source_module, source_event=journal.source_event,
        branch_id=journal.branch_id, financial_year=journal.financial_year,
        currency=journal.currency, exchange_rate=journal.exchange_rate, metadata=journal.metadata_json,
    )
    _refresh_journal_batch(journal.batch_id, db)
    _log_audit(db, tenant_id, "journal", journal.id, "update", {"status": journal.posting_status}, request.performed_by)
    db.commit()
    db.refresh(journal)
    return _journal_360_payload(journal, db)


@app.post("/api/v1/accounting/journals/{journal_id}/approve")
async def api_approve_journal(journal_id: str, request: JournalApprovalActionRequest, db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status == "draft":
        await submit_journal_document(journal_id, JournalActionRequest(tenant_id=request.tenant_id, performed_by=request.performed_by, remarks=request.remarks), db)
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status == "approved":
        return _journal_360_payload(journal, db)
    approved = await approve_journal_document(journal_id, request, db)
    persisted = db.query(JournalEntry).filter(JournalEntry.id == approved["id"], JournalEntry.tenant_id == request.tenant_id).first()
    return _journal_360_payload(persisted, db) if persisted else approved


@app.post("/api/v1/accounting/journals/{journal_id}/post")
async def api_post_journal(journal_id: str, request: JournalActionRequest, db: Session = Depends(get_db)):
    posted = await post_journal_document(journal_id, request, db)
    persisted = db.query(JournalEntry).filter(JournalEntry.id == posted["id"], JournalEntry.tenant_id == request.tenant_id).first()
    return _journal_360_payload(persisted, db) if persisted else posted


@app.post("/api/v1/accounting/journals/{journal_id}/reverse")
async def api_reverse_journal(journal_id: str, request: JournalActionRequest, db: Session = Depends(get_db)):
    result = await reverse_journal_document(journal_id, request, db)
    reversal = db.query(JournalEntry).filter(JournalEntry.id == result["reversal"]["id"], JournalEntry.tenant_id == request.tenant_id).first()
    original = db.query(JournalEntry).filter(JournalEntry.id == journal_id, JournalEntry.tenant_id == request.tenant_id).first()
    return {
        "journal": _journal_360_payload(original, db) if original else result["journal"],
        "reversal": _journal_360_payload(reversal, db) if reversal else result["reversal"],
    }


@app.get("/api/v1/accounting/posting-rules/dashboard")
async def api_posting_rules_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _posting_rule_dashboard_payload(tenant_id, db)


@app.get("/api/v1/accounting/posting-rules")
async def api_list_posting_rules(
    tenant_id: str = Query(...),
    q: Optional[str] = Query(None),
    source_module: Optional[str] = Query(None),
    source_event: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    product: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    query = db.query(PostingRule).filter(PostingRule.tenant_id == tenant_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (PostingRule.rule_name.ilike(like))
            | (PostingRule.source_module.ilike(like))
            | (PostingRule.source_event.ilike(like))
            | (PostingRule.description.ilike(like))
        )
    if source_module:
        query = query.filter(PostingRule.source_module == source_module)
    if source_event:
        query = query.filter(PostingRule.source_event == source_event)
    if status:
        query = query.filter(PostingRule.status == status)
    rows = query.order_by(PostingRule.source_module, PostingRule.source_event, PostingRule.priority.asc()).all()
    if product:
        rows = [rule for rule in rows if (rule.metadata_json or {}).get("product") == product or (rule.metadata_json or {}).get("product_id") == product]
    total = len(rows)
    selected = rows[offset : offset + limit]
    execution_rows = db.query(PostingExecutionLog).filter(PostingExecutionLog.tenant_id == tenant_id).all()
    executions_by_rule: dict[str, list[PostingExecutionLog]] = {}
    for execution in execution_rows:
        if execution.rule_id:
            executions_by_rule.setdefault(execution.rule_id, []).append(execution)
    return {
        "tenant_id": tenant_id,
        "total": total,
        "items": [_posting_rule_api_item(rule, executions_by_rule.get(rule.id, [])) for rule in selected],
    }


@app.post("/api/v1/accounting/posting-rules")
async def api_create_posting_rule(rule: PostingRuleCreate, db: Session = Depends(get_db)):
    created = await create_posting_rule(rule, db)
    persisted = db.query(PostingRule).filter(PostingRule.id == created["id"], PostingRule.tenant_id == rule.tenant_id).first()
    return _posting_rule_api_item(persisted) if persisted else created


@app.get("/api/v1/accounting/posting-rules/{rule_id}")
async def api_get_posting_rule(rule_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    return _posting_rule_360_payload(rule, db)


@app.put("/api/v1/accounting/posting-rules/{rule_id}")
async def api_update_posting_rule(rule_id: str, update: PostingRuleUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    updated = await update_posting_rule(rule_id, update, tenant_id, db)
    persisted = db.query(PostingRule).filter(PostingRule.id == updated["id"], PostingRule.tenant_id == tenant_id).first()
    return _posting_rule_360_payload(persisted, db) if persisted else updated


@app.post("/api/v1/accounting/posting-rules/{rule_id}/simulate")
async def api_simulate_posting_rule_by_id(rule_id: str, request: PostingRuleDirectSimulationRequest, db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == request.tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    return _simulate_posting_rule_instance(rule, request, db)


@app.post("/api/v1/accounting/posting-rules/{rule_id}/publish")
async def api_publish_posting_rule(rule_id: str, request: PostingRulePublishRequest, db: Session = Depends(get_db)):
    published = await publish_posting_rule(rule_id, request, db)
    persisted = db.query(PostingRule).filter(PostingRule.id == published["id"], PostingRule.tenant_id == request.tenant_id).first()
    return _posting_rule_360_payload(persisted, db) if persisted else published


@app.get("/api/v1/accounting/posting-rules/{rule_id}/versions")
async def api_posting_rule_versions(rule_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    root = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == tenant_id).first()
    if not root:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    versions = (
        db.query(PostingRule)
        .filter(PostingRule.tenant_id == tenant_id, (PostingRule.id == rule_id) | (PostingRule.supersedes_rule_id == rule_id))
        .order_by(PostingRule.version.asc(), PostingRule.created_at.asc())
        .all()
    )
    return {"tenant_id": tenant_id, "rule_id": rule_id, "items": [_posting_rule_api_item(rule) for rule in versions]}


@app.post("/accounting-periods", response_model=AccountingPeriodResponse)
async def create_accounting_period(period: AccountingPeriodCreate, db: Session = Depends(get_db)):
    if period.period_end < period.period_start:
        raise HTTPException(status_code=400, detail="period_end must be after period_start")
    existing = (
        db.query(AccountingPeriod)
        .filter(
            AccountingPeriod.tenant_id == period.tenant_id,
            AccountingPeriod.financial_year == period.financial_year,
            AccountingPeriod.period_name == period.period_name,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Accounting period already exists for tenant")
    new_period = AccountingPeriod(
        id=str(uuid4()),
        tenant_id=period.tenant_id,
        financial_year=period.financial_year,
        period_name=period.period_name,
        period_start=period.period_start,
        period_end=period.period_end,
        branch_id=period.branch_id,
        status=period.status or "open",
    )
    db.add(new_period)
    _log_audit(db, period.tenant_id, "accounting_period", new_period.id, "create", _period_response(new_period), period.performed_by)
    db.commit()
    db.refresh(new_period)
    return _period_response(new_period)


@app.get("/accounting-periods", response_model=List[AccountingPeriodResponse])
async def list_accounting_periods(
    tenant_id: str = Query(...),
    financial_year: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingPeriod).filter(AccountingPeriod.tenant_id == tenant_id)
    if financial_year:
        query = query.filter(AccountingPeriod.financial_year == financial_year)
    if status:
        query = query.filter(AccountingPeriod.status == status)
    periods = query.order_by(AccountingPeriod.period_start.desc()).all()
    return [_period_response(period) for period in periods]


@app.post("/accounting-periods/{period_id}/lock", response_model=AccountingPeriodResponse)
async def lock_accounting_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    period = db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id, AccountingPeriod.tenant_id == request.tenant_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Accounting period not found for tenant")
    period.status = "locked"
    period.locked_by = request.performed_by
    period.lock_reason = request.reason
    period.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "accounting_period", period.id, "lock", _period_response(period), request.performed_by)
    db.commit()
    db.refresh(period)
    return _period_response(period)


@app.post("/accounting-periods/{period_id}/request-unlock", response_model=AccountingPeriodResponse)
async def request_unlock_accounting_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    period = db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id, AccountingPeriod.tenant_id == request.tenant_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Accounting period not found for tenant")
    if period.status != "locked":
        raise HTTPException(status_code=400, detail="Only locked periods can be submitted for unlock")
    period.status = "pending_unlock"
    period.unlock_requested_by = request.performed_by
    period.unlock_reason = request.reason
    period.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "accounting_period", period.id, "request_unlock", _period_response(period), request.performed_by)
    db.commit()
    db.refresh(period)
    return _period_response(period)


@app.post("/accounting-periods/{period_id}/approve-unlock", response_model=AccountingPeriodResponse)
async def approve_unlock_accounting_period(period_id: str, request: AccountingPeriodActionRequest, db: Session = Depends(get_db)):
    period = db.query(AccountingPeriod).filter(AccountingPeriod.id == period_id, AccountingPeriod.tenant_id == request.tenant_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Accounting period not found for tenant")
    if period.status != "pending_unlock":
        raise HTTPException(status_code=400, detail="Only pending unlock periods can be approved")
    period.status = "open"
    period.approved_by = request.performed_by
    period.unlocked_by = request.performed_by
    period.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "accounting_period", period.id, "approve_unlock", _period_response(period), request.performed_by)
    db.commit()
    db.refresh(period)
    return _period_response(period)



@app.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(entry: JournalEntryCreate, db: Session = Depends(get_db)):
    if not entry.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    if not entry.lines or len(entry.lines) < 2:
        raise HTTPException(status_code=400, detail="Journal entry must contain at least two lines")

    total_debit = sum(line.debit for line in entry.lines)
    total_credit = sum(line.credit for line in entry.lines)
    if round(total_debit, 2) != round(total_credit, 2):
        raise HTTPException(status_code=400, detail="Journal entry must be balanced")

    posting_lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            branch_id=line.branch_id,
            currency=line.currency,
            transaction_currency=line.transaction_currency,
            transaction_amount=line.transaction_amount,
            exchange_rate=line.exchange_rate,
            department_id=line.department_id,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            project_id=line.project_id,
            employee_id=line.employee_id,
            product_id=line.product_id,
            business_unit_id=line.business_unit_id,
            description=line.description,
        )
        for line in entry.lines
    ]

    journal_entry = _post_journal(
        db=db,
        tenant_id=entry.tenant_id,
        description=entry.description,
        lines=posting_lines,
        entry_date=entry.entry_date or datetime.utcnow(),
        reference=entry.reference,
        metadata=entry.metadata,
        branch_id=entry.branch_id,
        business_date=entry.business_date,
        financial_year=entry.financial_year,
    )

    db.commit()
    db.refresh(journal_entry)
    return _journal_entry_response(journal_entry)


@app.get("/journal-entries")
async def list_journal_entries(
    tenant_id: str = Query(...),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = (
        db.query(JournalEntry)
        .filter(JournalEntry.tenant_id == tenant_id)
        .order_by(JournalEntry.entry_date.desc())
    )
    items = query.offset(skip).limit(limit).all()
    return {
        "items": [_journal_entry_response(item) for item in items],
        "skip": skip,
        "limit": limit,
        "total": query.count(),
    }


@app.post("/journal-batches")
async def create_journal_batch(request: JournalBatchCreate, db: Session = Depends(get_db)):
    posting_date = request.posting_date or datetime.utcnow()
    financial_year = request.financial_year or _current_financial_year(posting_date)
    batch = JournalBatch(
        id=str(uuid4()),
        batch_no=_next_batch_number(request.tenant_id, posting_date, financial_year, db),
        tenant_id=request.tenant_id,
        posting_date=posting_date,
        financial_year=financial_year,
        period=_journal_period_name(posting_date),
        status="draft",
        created_by=request.created_by,
        total_amount=0.0,
    )
    db.add(batch)
    _log_audit(db, request.tenant_id, "journal_batch", batch.id, "create", _journal_batch_response(batch), request.created_by)
    db.commit()
    db.refresh(batch)
    return _journal_batch_response(batch)


@app.get("/journal-batches")
async def list_journal_batches(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(JournalBatch).filter(JournalBatch.tenant_id == tenant_id)
    if status:
        query = query.filter(JournalBatch.status == status.lower())
    batches = query.order_by(JournalBatch.created_at.desc()).all()
    counts = {
        batch.id: db.query(JournalEntry).filter(JournalEntry.batch_id == batch.id).count()
        for batch in batches
    }
    return {"items": [_journal_batch_response(batch, counts[batch.id]) for batch in batches], "total": len(batches)}


@app.post("/journal-templates")
async def create_journal_template(request: JournalTemplateCreate, db: Session = Depends(get_db)):
    if len(request.lines or []) < 2:
        raise HTTPException(status_code=400, detail="Journal template must contain at least two lines")
    existing = db.query(JournalTemplate).filter(
        JournalTemplate.tenant_id == request.tenant_id,
        JournalTemplate.template_name == request.template_name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Journal template name already exists for tenant")
    template = JournalTemplate(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        template_name=request.template_name,
        description=request.description,
        voucher_type=request.voucher_type or "journal",
        currency=str(request.currency or "INR").upper(),
        lines=request.lines,
        status="active",
        created_by=request.created_by,
    )
    db.add(template)
    _log_audit(db, request.tenant_id, "journal_template", template.id, "create", _journal_template_response(template), request.created_by)
    db.commit()
    db.refresh(template)
    return _journal_template_response(template)


@app.get("/journal-templates")
async def list_journal_templates(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    templates = db.query(JournalTemplate).filter(
        JournalTemplate.tenant_id == tenant_id,
        JournalTemplate.status == "active",
    ).order_by(JournalTemplate.template_name).all()
    if not templates:
        for item in DEFAULT_JOURNAL_TEMPLATES:
            db.add(JournalTemplate(
                id=str(uuid4()),
                tenant_id=tenant_id,
                template_name=item["template_name"],
                description=item["description"],
                voucher_type=item["voucher_type"],
                currency="INR",
                lines=item["lines"],
                status="active",
                created_by="system",
            ))
        db.commit()
        templates = db.query(JournalTemplate).filter(
            JournalTemplate.tenant_id == tenant_id,
            JournalTemplate.status == "active",
        ).order_by(JournalTemplate.template_name).all()
    return {"items": [_journal_template_response(template) for template in templates], "total": len(templates)}


@app.post("/accounting-dimensions")
async def create_accounting_dimension(request: AccountingDimensionCreate, db: Session = Depends(get_db)):
    dimension = AccountingDimension(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        dimension_type=request.dimension_type.lower(),
        code=request.code,
        name=request.name,
        status=request.status or "active",
    )
    db.add(dimension)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Accounting dimension already exists for tenant")
    db.refresh(dimension)
    return {
        "id": dimension.id, "tenant_id": dimension.tenant_id, "dimension_type": dimension.dimension_type,
        "code": dimension.code, "name": dimension.name, "status": dimension.status,
    }


@app.get("/accounting-dimensions")
async def list_accounting_dimensions(
    tenant_id: str = Query(...),
    dimension_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingDimension).filter(AccountingDimension.tenant_id == tenant_id)
    if dimension_type:
        query = query.filter(AccountingDimension.dimension_type == dimension_type.lower())
    items = query.order_by(AccountingDimension.dimension_type, AccountingDimension.code).all()
    return {"items": [
        {"id": item.id, "dimension_type": item.dimension_type, "code": item.code, "name": item.name, "status": item.status}
        for item in items
    ], "total": len(items)}


@app.post("/accounting-budgets")
async def create_accounting_budget(request: AccountingBudgetCreate, db: Session = Depends(get_db)):
    _get_postable_account_by_id(request.gl_account_id, request.tenant_id, db)
    budget = AccountingBudget(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        financial_year=request.financial_year,
        period=request.period,
        gl_account_id=request.gl_account_id,
        cost_center=request.cost_center,
        amount=request.amount,
        status="active",
    )
    db.add(budget)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Accounting budget already exists for this scope")
    db.refresh(budget)
    return {
        "id": budget.id, "tenant_id": budget.tenant_id, "financial_year": budget.financial_year,
        "period": budget.period, "gl_account_id": budget.gl_account_id,
        "cost_center": budget.cost_center, "amount": budget.amount, "status": budget.status,
    }


@app.get("/accounting-budgets")
async def list_accounting_budgets(
    tenant_id: str = Query(...),
    financial_year: Optional[str] = Query(None),
    period: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AccountingBudget).filter(AccountingBudget.tenant_id == tenant_id)
    if financial_year:
        query = query.filter(AccountingBudget.financial_year == financial_year)
    if period:
        query = query.filter(AccountingBudget.period == period)
    items = query.order_by(AccountingBudget.created_at.desc()).all()
    return {"items": [
        {"id": item.id, "financial_year": item.financial_year, "period": item.period,
         "gl_account_id": item.gl_account_id, "cost_center": item.cost_center,
         "amount": item.amount, "status": item.status}
        for item in items
    ], "total": len(items)}


@app.post("/journals")
async def create_journal_document(request: JournalDocumentCreate, db: Session = Depends(get_db)):
    if len(request.lines or []) < 2:
        raise HTTPException(status_code=400, detail="Journal must contain at least two lines")
    posting_date = request.posting_date or datetime.utcnow()
    financial_year = request.financial_year or _current_financial_year(posting_date)
    batch = None
    if request.batch_id:
        batch = db.query(JournalBatch).filter(
            JournalBatch.id == request.batch_id,
            JournalBatch.tenant_id == request.tenant_id,
        ).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Journal batch not found for tenant")
        if batch.status in {"posted", "closed", "cancelled"}:
            raise HTTPException(status_code=400, detail="Journal batch no longer accepts entries")
    engine_lines = _journal_request_lines(request.lines, request.tenant_id, db)
    journal = JournalEntry(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        batch_id=request.batch_id,
        journal_no=_next_journal_number(request.tenant_id, posting_date, financial_year, db),
        entry_date=posting_date,
        voucher_type=request.voucher_type or "journal",
        description=request.description,
        reference=request.reference,
        metadata_json=request.metadata,
        posting_status="draft",
        source_module=request.source_module or "manual",
        source_event=request.source_event or "manual_journal",
        source_reference=request.source_reference,
        business_date=posting_date,
        financial_year=financial_year,
        period=_journal_period_name(posting_date),
        branch_id=request.branch_id,
        currency=str(request.currency or "INR").upper(),
        exchange_rate=request.exchange_rate or 1.0,
        created_by=request.created_by,
        template_id=request.template_id,
    )
    db.add(journal)
    db.flush()
    for index, line in enumerate(engine_lines, start=1):
        source = request.lines[index - 1]
        db.add(JournalLine(
            id=str(uuid4()), journal_entry_id=journal.id, sequence=source.sequence or index,
            gl_account_id=line.gl_account_id, debit=line.debit, credit=line.credit,
            currency=line.currency or journal.currency,
            transaction_currency=line.transaction_currency, transaction_amount=line.transaction_amount,
            exchange_rate=line.exchange_rate, branch_id=line.branch_id or request.branch_id,
            department_id=line.department_id, cost_center=line.cost_center, profit_center=line.profit_center,
            project_id=line.project_id, employee_id=line.employee_id, product_id=line.product_id,
            business_unit_id=line.business_unit_id, description=line.description,
        ))
    for attachment in request.attachments or []:
        db.add(JournalAttachment(
            id=str(uuid4()), journal_id=journal.id, document_id=attachment.document_id,
            file_name=attachment.file_name, uploaded_by=attachment.uploaded_by or request.created_by,
        ))
    db.flush()
    journal.validation_result = _journal_validation(
        db, request.tenant_id, engine_lines, posting_date,
        source_module=journal.source_module, source_event=journal.source_event,
        branch_id=journal.branch_id, financial_year=journal.financial_year,
        currency=journal.currency, exchange_rate=journal.exchange_rate, metadata=journal.metadata_json,
    )
    _refresh_journal_batch(journal.batch_id, db)
    _log_audit(db, request.tenant_id, "journal", journal.id, "create", {"journal_no": journal.journal_no, "status": "draft"}, request.created_by)
    db.commit()
    db.refresh(journal)
    return _journal_document_response(journal)


@app.get("/journals")
async def list_journal_documents(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    source_module: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=250),
    db: Session = Depends(get_db),
):
    query = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id)
    if status:
        statuses = [item.strip().lower() for item in status.split(",") if item.strip()]
        query = query.filter(JournalEntry.posting_status.in_(statuses))
    if source_module:
        query = query.filter(JournalEntry.source_module == source_module)
    total = query.count()
    items = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc()).offset(skip).limit(limit).all()
    status_rows = db.query(JournalEntry.posting_status, JournalEntry.id).filter(JournalEntry.tenant_id == tenant_id).all()
    status_counts = {}
    for item_status, _ in status_rows:
        status_counts[item_status or "draft"] = status_counts.get(item_status or "draft", 0) + 1
    return {"items": [_journal_document_response(item) for item in items], "total": total, "status_counts": status_counts}


@app.post("/journals/validate")
async def validate_journal_document(request: JournalValidationRequest, db: Session = Depends(get_db)):
    if request.journal_id:
        journal = _get_journal_document(request.journal_id, request.tenant_id, db)
        lines = _engine_lines_from_document(journal)
        posting_date = journal.entry_date
        result = _journal_validation(
            db, request.tenant_id, lines, posting_date,
            source_module=journal.source_module, source_event=journal.source_event,
            branch_id=journal.branch_id, financial_year=journal.financial_year,
            currency=journal.currency, exchange_rate=journal.exchange_rate, metadata=journal.metadata_json,
        )
        journal.validation_result = result
        _log_audit(db, request.tenant_id, "journal", journal.id, "validate", {"valid": result["valid"], "errors": result["errors"]}, request.tenant_id)
        db.commit()
        return {**result, "journal_id": journal.id, "journal_no": journal.journal_no}
    if not request.lines:
        raise HTTPException(status_code=400, detail="Provide journal_id or journal lines")
    lines = _journal_request_lines(request.lines, request.tenant_id, db)
    return _journal_validation(
        db, request.tenant_id, lines, request.posting_date or datetime.utcnow(),
        source_module=request.source_module, source_event=request.source_event,
        branch_id=request.branch_id, financial_year=request.financial_year,
        currency=request.currency, exchange_rate=request.exchange_rate, metadata=request.metadata,
    )


@app.post("/journals/simulate")
async def simulate_journal_document(request: JournalSimulationRequest, db: Session = Depends(get_db)):
    template = None
    if request.template_id:
        template = db.query(JournalTemplate).filter(
            JournalTemplate.id == request.template_id,
            JournalTemplate.tenant_id == request.tenant_id,
            JournalTemplate.status == "active",
        ).first()
        if not template:
            raise HTTPException(status_code=404, detail="Journal template not found for tenant")
        lines = _journal_template_lines(template, request.amount or 0.0, request.tenant_id, db)
    elif request.lines:
        lines = _journal_request_lines(request.lines, request.tenant_id, db)
    else:
        raise HTTPException(status_code=400, detail="Provide template_id and amount or journal lines")
    posting_date = request.posting_date or datetime.utcnow()
    validation = _journal_validation(
        db, request.tenant_id, lines, posting_date,
        source_module=request.source_module, source_event=request.source_event,
        branch_id=request.branch_id, financial_year=request.financial_year,
        currency=template.currency if template else request.currency,
        exchange_rate=request.exchange_rate, metadata=request.metadata,
    )
    return {
        **validation,
        "template": _journal_template_response(template) if template else None,
        "description": request.description or (template.description if template else "Journal simulation"),
        "lines": [
            {"sequence": index, "gl_account_id": line.gl_account_id, "account_code": line.account_code,
             "debit": line.debit, "credit": line.credit, "currency": line.currency,
             "description": line.description}
            for index, line in enumerate(lines, start=1)
        ],
    }


@app.get("/journals/history")
async def journal_history(
    tenant_id: str = Query(...),
    journal_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id, AuditLog.entity == "journal")
    if journal_id:
        query = query.filter(AuditLog.entity_id == journal_id)
    items = query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return {"items": [_audit_log_response(item) for item in items], "total": len(items)}


@app.post("/journals/{journal_id}/submit")
async def submit_journal_document(journal_id: str, request: JournalActionRequest, db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status != "draft":
        raise HTTPException(status_code=400, detail="Only draft journals can be submitted")
    validation = _journal_validation(
        db, request.tenant_id, _engine_lines_from_document(journal), journal.entry_date,
        source_module=journal.source_module, source_event=journal.source_event, branch_id=journal.branch_id,
        financial_year=journal.financial_year, currency=journal.currency,
        exchange_rate=journal.exchange_rate, metadata=journal.metadata_json,
    )
    journal.validation_result = validation
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={"message": "Journal validation failed", "errors": validation["errors"]})
    journal.posting_status = "pending"
    db.add(JournalApproval(
        id=str(uuid4()), journal_id=journal.id, level="maker",
        approver=request.performed_by or journal.created_by or "maker", decision="submitted", remarks=request.remarks,
    ))
    _refresh_journal_batch(journal.batch_id, db)
    _log_audit(db, request.tenant_id, "journal", journal.id, "submit", {"status": "pending"}, request.performed_by)
    db.commit()
    db.refresh(journal)
    return _journal_document_response(journal)


@app.post("/journals/{journal_id}/approve")
async def approve_journal_document(journal_id: str, request: JournalApprovalActionRequest, db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status != "pending":
        raise HTTPException(status_code=400, detail="Only pending journals can be approved")
    approver = request.performed_by or "checker"
    if journal.created_by and journal.created_by == approver:
        raise HTTPException(status_code=400, detail="Maker cannot approve their own journal")
    decision = str(request.decision or "approved").lower()
    if decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="decision must be approved or rejected")
    db.add(JournalApproval(
        id=str(uuid4()), journal_id=journal.id, level=request.level or "checker",
        approver=approver, decision=decision, remarks=request.remarks,
    ))
    if decision == "approved":
        journal.posting_status = "approved"
        journal.approved_by = approver
        journal.approved_at = datetime.utcnow()
    else:
        journal.posting_status = "draft"
    _refresh_journal_batch(journal.batch_id, db)
    _log_audit(db, request.tenant_id, "journal", journal.id, decision, {"level": request.level or "checker"}, approver)
    db.commit()
    db.refresh(journal)
    return _journal_document_response(journal)


@app.post("/journals/{journal_id}/post")
async def post_journal_document(journal_id: str, request: JournalActionRequest, db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status != "approved":
        raise HTTPException(status_code=400, detail="Only approved journals can be posted")
    validation = _journal_validation(
        db, request.tenant_id, _engine_lines_from_document(journal), journal.entry_date,
        source_module=journal.source_module, source_event=journal.source_event, branch_id=journal.branch_id,
        financial_year=journal.financial_year, currency=journal.currency,
        exchange_rate=journal.exchange_rate, metadata=journal.metadata_json,
    )
    journal.validation_result = validation
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={"message": "Journal validation failed", "errors": validation["errors"]})
    try:
        _apply_journal_document_to_gl(journal, db)
        voucher = _create_voucher_from_journal(journal, db)
        journal.posting_status = "posted"
        if journal.source_module and journal.source_module not in {"manual", "accounting"}:
            _create_subledger_entry(
                db, request.tenant_id, journal.source_module, journal.source_event or "journal_posted",
                journal.source_reference or journal.journal_no, validation["total_debit"], journal.id,
                {"journal_no": journal.journal_no, "voucher_id": voucher.id},
            )
        _refresh_journal_batch(journal.batch_id, db)
        _log_audit(db, request.tenant_id, "journal", journal.id, "post", {"voucher_id": voucher.id, "status": "posted"}, request.performed_by)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Journal posting rolled back: {exc}")
    db.refresh(journal)
    return _journal_document_response(journal)


@app.post("/journals/{journal_id}/reverse")
async def reverse_journal_document(journal_id: str, request: JournalActionRequest, db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status != "posted":
        raise HTTPException(status_code=400, detail="Only posted journals can be reversed")
    posting_date = datetime.utcnow()
    lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id, debit=line.credit or 0.0, credit=line.debit or 0.0,
            branch_id=line.branch_id, currency=line.currency, transaction_currency=line.transaction_currency,
            transaction_amount=line.transaction_amount, exchange_rate=line.exchange_rate,
            department_id=line.department_id, cost_center=line.cost_center, profit_center=line.profit_center,
            project_id=line.project_id, employee_id=line.employee_id, product_id=line.product_id,
            business_unit_id=line.business_unit_id, description=f"Reversal: {line.description or journal.description}",
        )
        for line in journal.lines
    ]
    validation = _journal_validation(
        db, request.tenant_id, lines, posting_date, source_module="accounting", source_event="journal_reversal",
        branch_id=journal.branch_id, financial_year=_current_financial_year(posting_date),
        currency=journal.currency, exchange_rate=journal.exchange_rate,
    )
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={"message": "Reversal validation failed", "errors": validation["errors"]})
    try:
        financial_year = _current_financial_year(posting_date)
        reversal = JournalEntry(
            id=str(uuid4()), tenant_id=request.tenant_id,
            journal_no=_next_journal_number(request.tenant_id, posting_date, financial_year, db),
            entry_date=posting_date, voucher_type="reversal", description=f"Reversal of {journal.journal_no}",
            reference=journal.journal_no, metadata_json={"reversal_reason": request.remarks}, posting_status="posted",
            source_module="accounting", source_event="journal_reversal", source_reference=journal.journal_no,
            business_date=posting_date, financial_year=financial_year, period=_journal_period_name(posting_date),
            branch_id=journal.branch_id, currency=journal.currency, exchange_rate=journal.exchange_rate,
            reversal_of=journal.id, created_by=request.performed_by, approved_by=request.performed_by,
            approved_at=datetime.utcnow(), validation_result=validation,
        )
        db.add(reversal)
        db.flush()
        for index, line in enumerate(lines, start=1):
            db.add(JournalLine(
                id=str(uuid4()), journal_entry_id=reversal.id, sequence=index,
                gl_account_id=line.gl_account_id, debit=line.debit, credit=line.credit,
                currency=line.currency, transaction_currency=line.transaction_currency,
                transaction_amount=line.transaction_amount, exchange_rate=line.exchange_rate,
                branch_id=line.branch_id, department_id=line.department_id, cost_center=line.cost_center,
                profit_center=line.profit_center, project_id=line.project_id, employee_id=line.employee_id,
                product_id=line.product_id, business_unit_id=line.business_unit_id, description=line.description,
            ))
        db.flush()
        _apply_journal_document_to_gl(reversal, db)
        _create_voucher_from_journal(reversal, db, reversal=True)
        journal.posting_status = "reversed"
        _refresh_journal_batch(journal.batch_id, db)
        _log_audit(db, request.tenant_id, "journal", journal.id, "reverse", {"reversal_journal_id": reversal.id}, request.performed_by)
        _log_audit(db, request.tenant_id, "journal", reversal.id, "create_reversal", {"reversal_of": journal.id}, request.performed_by)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Journal reversal rolled back: {exc}")
    db.refresh(reversal)
    return {"journal": _journal_document_response(journal), "reversal": _journal_document_response(reversal)}


@app.post("/journals/{journal_id}/cancel")
async def cancel_journal_document(journal_id: str, request: JournalActionRequest, db: Session = Depends(get_db)):
    journal = _get_journal_document(journal_id, request.tenant_id, db)
    if journal.posting_status not in {"draft", "pending", "approved"}:
        raise HTTPException(status_code=400, detail="Only unposted journals can be cancelled")
    journal.posting_status = "cancelled"
    _refresh_journal_batch(journal.batch_id, db)
    _log_audit(db, request.tenant_id, "journal", journal.id, "cancel", {"remarks": request.remarks}, request.performed_by)
    db.commit()
    db.refresh(journal)
    return _journal_document_response(journal)


@app.post("/journals/post")
async def post_journal(request: JournalActionRequest, db: Session = Depends(get_db)):
    if not request.journal_id:
        raise HTTPException(status_code=400, detail="journal_id is required")
    return await post_journal_document(request.journal_id, request, db)


@app.post("/journals/reverse")
async def reverse_journal(request: JournalActionRequest, db: Session = Depends(get_db)):
    if not request.journal_id:
        raise HTTPException(status_code=400, detail="journal_id is required")
    return await reverse_journal_document(request.journal_id, request, db)


@app.post("/journals/cancel")
async def cancel_journal(request: JournalActionRequest, db: Session = Depends(get_db)):
    if not request.journal_id:
        raise HTTPException(status_code=400, detail="journal_id is required")
    return await cancel_journal_document(request.journal_id, request, db)


@app.get("/journals/{journal_id}")
async def get_journal_document(journal_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _journal_document_response(_get_journal_document(journal_id, tenant_id, db))


@app.post("/posting-rules", response_model=PostingRuleResponse)
async def create_posting_rule(rule: PostingRuleCreate, db: Session = Depends(get_db)):
    if not rule.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if not rule.lines and not (rule.debit_account_code and rule.credit_account_code):
        raise HTTPException(status_code=400, detail="Provide either lines or debit/credit account codes")

    normalized_lines = []
    if rule.lines:
        for index, line in enumerate(rule.lines):
            normalized_lines.append(
                {
                    "account_code": line.account_code,
                    "direction": str(line.direction or "debit").lower(),
                    "description": line.description,
                    "sequence": line.sequence if line.sequence is not None else index + 1,
                    "amount_source": line.amount_source,
                    "percentage": line.percentage,
                    "formula": line.formula,
                    "currency": line.currency,
                    "dimension_source": line.dimension_source,
                    "transaction_currency_source": line.transaction_currency_source,
                    "exchange_rate_source": line.exchange_rate_source,
                }
            )

    debit_account_code = rule.debit_account_code
    credit_account_code = rule.credit_account_code
    if normalized_lines:
        debit_account_code = next((line["account_code"] for line in normalized_lines if line["direction"] == "debit"), None)
        credit_account_code = next((line["account_code"] for line in normalized_lines if line["direction"] == "credit"), None)

    posting_rule = PostingRule(
        id=str(uuid4()),
        tenant_id=rule.tenant_id,
        source_module=rule.source_module,
        source_event=rule.source_event,
        rule_name=rule.rule_name or f"{rule.source_module}.{rule.source_event}",
        priority=rule.priority or 100.0,
        status="draft" if (rule.status or "draft") in {"active", "published"} else (rule.status or "draft"),
        version=rule.version or 1.0,
        supersedes_rule_id=rule.supersedes_rule_id,
        effective_from=rule.effective_from,
        effective_to=rule.effective_to,
        requires_approval=rule.requires_approval or "true",
        approval_status="draft",
        dependency_rule_ids=rule.dependency_rule_ids or [],
        rollback_strategy=rule.rollback_strategy or "reverse_journal",
        debit_account_code=debit_account_code,
        credit_account_code=credit_account_code,
        posting_lines=normalized_lines or None,
        conditions=[condition.dict() for condition in rule.conditions] if rule.conditions else None,
        description=rule.description,
        is_active="false",
        created_by=rule.created_by,
        metadata_json=rule.metadata,
    )
    db.add(posting_rule)
    _log_audit(
        db,
        tenant_id=rule.tenant_id,
        entity="posting_rule",
        entity_id=posting_rule.id,
        action="create",
        payload={
            "source_module": rule.source_module,
            "source_event": rule.source_event,
            "debit_account_code": debit_account_code,
            "credit_account_code": credit_account_code,
            "lines": normalized_lines,
            "conditions": [condition.dict() for condition in rule.conditions] if rule.conditions else [],
            "status": posting_rule.status,
        },
        performed_by=rule.created_by,
    )
    db.commit()
    db.refresh(posting_rule)
    return _posting_rule_response(posting_rule)


@app.get("/posting-rules", response_model=List[PostingRuleResponse])
async def list_posting_rules(
    tenant_id: str = Query(...),
    source_module: Optional[str] = Query(None),
    source_event: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PostingRule).filter(PostingRule.tenant_id == tenant_id)
    if source_module:
        query = query.filter(PostingRule.source_module == source_module)
    if source_event:
        query = query.filter(PostingRule.source_event == source_event)
    if status:
        query = query.filter(PostingRule.status == status)
    rules = query.order_by(PostingRule.source_module, PostingRule.source_event, PostingRule.priority.asc()).all()
    return [_posting_rule_response(rule) for rule in rules]


@app.post("/posting-rules/validate")
async def validate_posting_rule(rule: PostingRuleCreate):
    normalized_lines = rule.lines or []
    if not normalized_lines and not (rule.debit_account_code and rule.credit_account_code):
        raise HTTPException(status_code=400, detail="Provide either lines or debit/credit account codes")
    debit_lines = [line for line in normalized_lines if str(line.direction).lower() == "debit"]
    credit_lines = [line for line in normalized_lines if str(line.direction).lower() == "credit"]
    if normalized_lines and (not debit_lines or not credit_lines):
        raise HTTPException(status_code=400, detail="Rule must contain at least one debit and one credit line")
    return {
        "status": "valid",
        "line_count": len(normalized_lines) or 2,
        "condition_count": len(rule.conditions or []),
        "formula_count": sum(1 for line in normalized_lines if line.formula),
    }


@app.post("/posting-rules/simulate")
async def simulate_posting_rule(request: PostingRuleSimulationRequest, db: Session = Depends(get_db)):
    event_data = {"amount": request.amount or 0.0, **(request.event_data or {})}
    amount = float(request.amount or event_data.get("amount") or event_data.get("loan_amount") or event_data.get("emi_amount") or 0.0)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="amount or event_data.amount must be positive")
    started_at = datetime.utcnow()
    rule = _find_posting_rule(db, request.tenant_id, request.source_module, request.source_event, event_data, active_only=False)
    if not rule:
        _log_posting_execution(
            db,
            tenant_id=request.tenant_id,
            rule_id=None,
            source_module=request.source_module,
            source_event=request.source_event,
            source_reference=request.source_reference,
            status="no_rule",
            input_payload=event_data,
            error_message="No matching posting rule found",
            started_at=started_at,
        )
        db.commit()
        raise HTTPException(status_code=404, detail="No matching posting rule found")
    lines = _build_posting_lines_from_rule(
        rule,
        amount,
        branch_id=request.branch_id,
        currency=request.currency,
        description_prefix=f"{request.source_module}.{request.source_event}",
        event_data=event_data,
    )
    validation = _validate_double_entry(lines)
    resolved_lines = []
    for line in lines:
        account = _get_postable_account_by_code(line.account_code or "", request.tenant_id, db)
        _validate_account_for_line(account, line.debit or 0.0, line.credit or 0.0, posting_mode="auto")
        resolved_lines.append(
            {
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "direction": "debit" if line.debit else "credit",
                "debit": line.debit,
                "credit": line.credit,
                "description": line.description,
                "branch_id": line.branch_id,
                "department_id": line.department_id,
                "cost_center": line.cost_center,
                "profit_center": line.profit_center,
                "project_id": line.project_id,
                "employee_id": line.employee_id,
                "product_id": line.product_id,
                "business_unit_id": line.business_unit_id,
                "currency": line.currency,
                "transaction_currency": line.transaction_currency,
                "exchange_rate": line.exchange_rate,
            }
        )
    _log_posting_execution(
        db,
        tenant_id=request.tenant_id,
        rule_id=rule.id,
        source_module=request.source_module,
        source_event=request.source_event,
        source_reference=request.source_reference,
        status="simulated",
        input_payload=event_data,
        generated_lines=resolved_lines,
        started_at=started_at,
    )
    db.commit()
    return {
        "rule": _posting_rule_response(rule),
        "is_balanced": validation["is_balanced"],
        "total_debit": validation["total_debit"],
        "total_credit": validation["total_credit"],
        "lines": resolved_lines,
        "pipeline": _posting_pipeline(posting_rule_status="simulated", posting_rule=_posting_rule_response(rule)),
    }


@app.put("/posting-rules/{rule_id}", response_model=PostingRuleResponse)
async def update_posting_rule(rule_id: str, update: PostingRuleUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    before = _posting_rule_response(rule)
    update_fields = set(update.dict(exclude_unset=True).keys()) - {"performed_by"}
    if str(rule.status or "").lower() in {"active", "published"} and update_fields:
        raise HTTPException(status_code=400, detail="Published posting rules are immutable; create a new version")
    if update.source_module is not None:
        rule.source_module = update.source_module
    if update.source_event is not None:
        rule.source_event = update.source_event
    if update.rule_name is not None:
        rule.rule_name = update.rule_name
    if update.priority is not None:
        rule.priority = update.priority
    if update.status is not None:
        if update.status in {"active", "published"} and rule.approval_status not in {"finance_head_approved", "published"}:
            raise HTTPException(status_code=400, detail="Posting rule must be approved before activation")
        rule.status = update.status
        rule.is_active = "true" if update.status in {"active", "published"} else "false"
    if update.version is not None:
        rule.version = update.version
    if update.supersedes_rule_id is not None:
        rule.supersedes_rule_id = update.supersedes_rule_id
    if update.effective_from is not None:
        rule.effective_from = update.effective_from
    if update.effective_to is not None:
        rule.effective_to = update.effective_to
    if update.requires_approval is not None:
        rule.requires_approval = update.requires_approval
    if update.dependency_rule_ids is not None:
        rule.dependency_rule_ids = update.dependency_rule_ids
    if update.rollback_strategy is not None:
        rule.rollback_strategy = update.rollback_strategy
    if update.description is not None:
        rule.description = update.description
    if update.debit_account_code is not None:
        rule.debit_account_code = update.debit_account_code
    if update.credit_account_code is not None:
        rule.credit_account_code = update.credit_account_code
    if update.lines is not None:
        rule.posting_lines = [
            {
                "account_code": line.account_code,
                "direction": str(line.direction or "debit").lower(),
                "description": line.description,
                "sequence": line.sequence if line.sequence is not None else index + 1,
                "amount_source": line.amount_source,
                "percentage": line.percentage,
                "formula": line.formula,
                "currency": line.currency,
                "dimension_source": line.dimension_source,
                "transaction_currency_source": line.transaction_currency_source,
                "exchange_rate_source": line.exchange_rate_source,
            }
            for index, line in enumerate(update.lines)
        ]
        rule.debit_account_code = next((line["account_code"] for line in rule.posting_lines if line["direction"] == "debit"), None)
        rule.credit_account_code = next((line["account_code"] for line in rule.posting_lines if line["direction"] == "credit"), None)
    if update.conditions is not None:
        rule.conditions = [condition.dict() for condition in update.conditions]
    if update.metadata is not None:
        rule.metadata_json = update.metadata
    rule.updated_at = datetime.utcnow()
    _log_audit(
        db,
        tenant_id=tenant_id,
        entity="posting_rule",
        entity_id=rule.id,
        action="update",
        payload={"before": before, "after": _posting_rule_response(rule)},
        performed_by=update.performed_by,
    )
    db.commit()
    db.refresh(rule)
    return _posting_rule_response(rule)


@app.delete("/posting-rules/{rule_id}")
async def delete_posting_rule(rule_id: str, tenant_id: str = Query(...), performed_by: Optional[str] = Query(None), db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    rule.status = "archived"
    rule.is_active = "false"
    rule.updated_at = datetime.utcnow()
    _log_audit(db, tenant_id, "posting_rule", rule.id, "archive", _posting_rule_response(rule), performed_by)
    db.commit()
    return {"id": rule.id, "status": rule.status}


@app.post("/posting-rules/{rule_id}/submit", response_model=PostingRuleResponse)
async def submit_posting_rule(rule_id: str, request: PostingRuleApprovalRequest, db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == request.tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    if rule.status in {"active", "published"}:
        raise HTTPException(status_code=400, detail="Active posting rules cannot be resubmitted")
    rule.status = "pending_approval"
    rule.is_active = "false"
    rule.approval_status = "maker_submitted"
    rule.maker_by = request.performed_by
    rule.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "posting_rule", rule.id, "submit", {"comment": request.comment}, request.performed_by)
    db.commit()
    db.refresh(rule)
    return _posting_rule_response(rule)


@app.post("/posting-rules/{rule_id}/approve", response_model=PostingRuleResponse)
async def approve_posting_rule(rule_id: str, request: PostingRuleApprovalRequest, db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == request.tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    stage = str(request.stage or "checker").lower()
    if stage not in {"checker", "finance_head"}:
        raise HTTPException(status_code=400, detail="stage must be checker or finance_head")
    if stage == "checker":
        if rule.approval_status != "maker_submitted":
            raise HTTPException(status_code=400, detail="Rule must be maker-submitted before checker approval")
        rule.approval_status = "checker_approved"
        rule.checker_by = request.performed_by
    else:
        if rule.approval_status != "checker_approved":
            raise HTTPException(status_code=400, detail="Rule must be checker-approved before finance head approval")
        rule.approval_status = "finance_head_approved"
        rule.finance_head_by = request.performed_by
        rule.approved_by = request.performed_by
        rule.approved_at = datetime.utcnow()
    rule.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "posting_rule", rule.id, f"approve_{stage}", {"comment": request.comment}, request.performed_by)
    db.commit()
    db.refresh(rule)
    return _posting_rule_response(rule)


@app.post("/posting-rules/{rule_id}/new-version", response_model=PostingRuleResponse)
async def create_posting_rule_version(rule_id: str, request: PostingRuleVersionRequest, db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == request.tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    clone = PostingRule(
        id=str(uuid4()),
        tenant_id=rule.tenant_id,
        source_module=request.source_module or rule.source_module,
        source_event=request.source_event or rule.source_event,
        rule_name=request.rule_name or rule.rule_name,
        priority=request.priority if request.priority is not None else rule.priority,
        status="draft",
        version=(request.version if request.version is not None else (rule.version or 1.0) + 1.0),
        supersedes_rule_id=rule.id,
        effective_from=request.effective_from if request.effective_from is not None else rule.effective_from,
        effective_to=request.effective_to if request.effective_to is not None else rule.effective_to,
        requires_approval=request.requires_approval or rule.requires_approval or "true",
        approval_status="draft",
        dependency_rule_ids=request.dependency_rule_ids if request.dependency_rule_ids is not None else (rule.dependency_rule_ids or []),
        rollback_strategy=request.rollback_strategy or rule.rollback_strategy or "reverse_journal",
        debit_account_code=request.debit_account_code if request.debit_account_code is not None else rule.debit_account_code,
        credit_account_code=request.credit_account_code if request.credit_account_code is not None else rule.credit_account_code,
        posting_lines=[
            {
                "account_code": line.account_code,
                "direction": str(line.direction or "debit").lower(),
                "description": line.description,
                "sequence": line.sequence if line.sequence is not None else index + 1,
                "amount_source": line.amount_source,
                "percentage": line.percentage,
                "formula": line.formula,
                "currency": line.currency,
                "dimension_source": line.dimension_source,
                "transaction_currency_source": line.transaction_currency_source,
                "exchange_rate_source": line.exchange_rate_source,
            }
            for index, line in enumerate(request.lines)
        ] if request.lines is not None else _normalize_posting_rule_lines(rule),
        conditions=[condition.dict() for condition in request.conditions] if request.conditions is not None else rule.conditions,
        description=request.description if request.description is not None else rule.description,
        is_active="false",
        created_by=request.performed_by or rule.created_by,
        metadata_json=request.metadata if request.metadata is not None else rule.metadata_json,
    )
    if clone.posting_lines:
        clone.debit_account_code = next((line["account_code"] for line in clone.posting_lines if line["direction"] == "debit"), clone.debit_account_code)
        clone.credit_account_code = next((line["account_code"] for line in clone.posting_lines if line["direction"] == "credit"), clone.credit_account_code)
    db.add(clone)
    _log_audit(db, request.tenant_id, "posting_rule", clone.id, "new_version", {"supersedes_rule_id": rule.id}, request.performed_by)
    db.commit()
    db.refresh(clone)
    return _posting_rule_response(clone)


@app.post("/posting-rules/{rule_id}/publish", response_model=PostingRuleResponse)
async def publish_posting_rule(rule_id: str, request: PostingRulePublishRequest, db: Session = Depends(get_db)):
    rule = db.query(PostingRule).filter(PostingRule.id == rule_id, PostingRule.tenant_id == request.tenant_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Posting rule not found for tenant")
    if rule.approval_status != "finance_head_approved":
        raise HTTPException(status_code=400, detail="Posting rule requires maker, checker, and finance head approval before publish")
    dependency_ids = rule.dependency_rule_ids if isinstance(rule.dependency_rule_ids, list) else []
    if dependency_ids:
        active_dependencies = (
            db.query(PostingRule)
            .filter(
                PostingRule.tenant_id == request.tenant_id,
                PostingRule.id.in_(dependency_ids),
                PostingRule.is_active.in_(["true", "1", "yes", "active"]),
            )
            .count()
        )
        if active_dependencies != len(dependency_ids):
            raise HTTPException(status_code=400, detail="All dependent posting rules must be active before publish")
    rule.status = "active"
    rule.is_active = "true"
    rule.approval_status = "published"
    rule.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "posting_rule", rule.id, "publish", _posting_rule_response(rule), request.performed_by)
    db.commit()
    db.refresh(rule)
    return _posting_rule_response(rule)


@app.get("/posting-rules/{rule_id}/history", response_model=List[AuditLogResponse])
async def posting_rule_history(rule_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(AuditLog)
        .filter(AuditLog.tenant_id == tenant_id, AuditLog.entity == "posting_rule", AuditLog.entity_id == rule_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )


@app.get("/posting-rules/{rule_id}/executions")
async def posting_rule_executions(rule_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    items = (
        db.query(PostingExecutionLog)
        .filter(PostingExecutionLog.tenant_id == tenant_id, PostingExecutionLog.rule_id == rule_id)
        .order_by(PostingExecutionLog.created_at.desc())
        .all()
    )
    return {
        "items": [
            {
                "id": item.id,
                "rule_id": item.rule_id,
                "source_module": item.source_module,
                "source_event": item.source_event,
                "source_reference": item.source_reference,
                "status": item.status,
                "execution_time_ms": item.execution_time_ms,
                "journal_id": item.journal_id,
                "rollback_journal_id": item.rollback_journal_id,
                "error_message": item.error_message,
                "generated_lines": item.generated_lines,
                "created_at": item.created_at,
            }
            for item in items
        ],
        "total": len(items),
    }


@app.post("/posting-executions/{execution_id}/rollback")
async def rollback_posting_execution(execution_id: str, request: ExecutionRollbackRequest, db: Session = Depends(get_db)):
    execution = (
        db.query(PostingExecutionLog)
        .filter(PostingExecutionLog.id == execution_id, PostingExecutionLog.tenant_id == request.tenant_id)
        .first()
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Posting execution not found for tenant")
    if execution.status == "rolled_back":
        raise HTTPException(status_code=400, detail="Posting execution is already rolled back")
    if not execution.journal_id:
        raise HTTPException(status_code=400, detail="Posting execution has no journal to rollback")
    reversal_entry = await reverse_gl_posting(execution.journal_id, request.tenant_id, db)
    subledger_entries = (
        db.query(SubLedgerEntry)
        .filter(
            SubLedgerEntry.tenant_id == request.tenant_id,
            SubLedgerEntry.journal_entry_id == execution.journal_id,
            SubLedgerEntry.status.in_(["active", None]),
        )
        .all()
    )
    reversed_subledger_ids = []
    for subledger_entry in subledger_entries:
        subledger_entry.status = "reversed"
        subledger_entry.reversed_at = datetime.utcnow()
        reversal_subledger = _create_subledger_entry(
            db=db,
            tenant_id=request.tenant_id,
            source_module=subledger_entry.source_module,
            source_event=f"{subledger_entry.source_event}.reversal",
            source_reference=subledger_entry.source_reference,
            amount=-(subledger_entry.amount or 0.0),
            journal_entry_id=reversal_entry["id"],
            metadata={
                **(subledger_entry.metadata_json or {}),
                "reverses_subledger_entry_id": subledger_entry.id,
                "rollback_reason": request.reason,
            },
            status="reversal",
            reversal_entry_id=subledger_entry.id,
        )
        db.flush()
        reversed_subledger_ids.append(reversal_subledger.id)
    execution.status = "rolled_back"
    execution.rollback_journal_id = reversal_entry["id"]
    execution.error_message = request.reason
    _log_audit(
        db,
        request.tenant_id,
        "posting_execution",
        execution.id,
        "rollback",
        {
            "journal_id": execution.journal_id,
            "rollback_journal_id": execution.rollback_journal_id,
            "reversed_subledger_ids": reversed_subledger_ids,
            "reason": request.reason,
        },
        request.performed_by,
    )
    db.commit()
    return {
        "id": execution.id,
        "status": execution.status,
        "journal_id": execution.journal_id,
        "rollback_journal_id": execution.rollback_journal_id,
        "reversed_subledger_ids": reversed_subledger_ids,
    }


@app.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    tenant_id: str = Query(...),
    entity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
    if entity:
        query = query.filter(AuditLog.entity == entity)
    return query.order_by(AuditLog.created_at.desc()).all()


@app.get("/sub-ledger-entries", response_model=List[SubLedgerEntryResponse])
async def list_subledger_entries(
    tenant_id: str = Query(...),
    source_module: Optional[str] = Query(None),
    source_event: Optional[str] = Query(None),
    source_reference: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id)
    if source_module:
        query = query.filter(SubLedgerEntry.source_module == source_module)
    if source_event:
        query = query.filter(SubLedgerEntry.source_event == source_event)
    if source_reference:
        query = query.filter(SubLedgerEntry.source_reference == source_reference)
    entries = query.order_by(SubLedgerEntry.created_at.desc()).all()
    return [_subledger_response(entry) for entry in entries]


@app.get("/sub-ledger-summary")
async def subledger_summary(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    entries = db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id).all()
    grouped: dict[str, dict] = {}
    for entry in entries:
        key = entry.source_module.lower()
        summary = grouped.setdefault(
            key,
            {
                "source_module": entry.source_module,
                "ledger_name": _subledger_ledger_name(entry.source_module),
                "transaction_count": 0,
                "total_amount": 0.0,
                "last_entry_at": None,
                "rollup_to": "General Ledger",
            },
        )
        summary["transaction_count"] += 1
        summary["total_amount"] += entry.amount or 0.0
        if summary["last_entry_at"] is None or (entry.created_at and entry.created_at > summary["last_entry_at"]):
            summary["last_entry_at"] = entry.created_at

    items = [
        {
            "source_module": item["source_module"],
            "ledger_name": item["ledger_name"],
            "transaction_count": item["transaction_count"],
            "total_amount": round(item["total_amount"], 2),
            "last_entry_at": item["last_entry_at"],
            "rollup_to": item["rollup_to"],
        }
        for item in grouped.values()
    ]
    items.sort(key=lambda row: (row["ledger_name"].lower(), row["source_module"].lower()))
    return {"items": items, "total": len(items)}


@app.post("/posting-engine/validate")
async def validate_posting(request: PostingValidationRequest, db: Session = Depends(get_db)):
    result = _validate_double_entry(request.lines)
    resolved_accounts = []
    for line in request.lines:
        account = (
            _get_postable_account_by_id(line.gl_account_id, request.tenant_id, db)
            if line.gl_account_id
            else _get_postable_account_by_code(line.account_code or "", request.tenant_id, db)
        )
        posting_mode = "auto" if request.source_module and request.source_module not in {"manual", "accounting"} else "manual"
        _validate_account_for_line(account, line.debit or 0.0, line.credit or 0.0, posting_mode=posting_mode)
        resolved_accounts.append(
            {
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "debit": line.debit,
                "credit": line.credit,
                "freeze_status": account.freeze_status,
            }
        )

    posting_rule = None
    posting_rule_status = "manual"
    if request.source_module and request.source_event:
        rule = (
            db.query(PostingRule)
            .filter(
                PostingRule.tenant_id == request.tenant_id,
                PostingRule.source_module == request.source_module,
                PostingRule.source_event == request.source_event,
                PostingRule.is_active.in_(["true", "1", "yes", "active"]),
            )
            .first()
        )
        if rule:
            posting_rule = _posting_rule_response(rule)
            posting_rule_status = "matched"
        else:
            mapped = DEFAULT_POSTING_MAP.get((request.source_module, request.source_event))
            if mapped:
                posting_rule = {
                    "source_module": request.source_module,
                    "source_event": request.source_event,
                    "debit_account_code": mapped[0],
                    "credit_account_code": mapped[1],
                }
                posting_rule_status = "default_map"

    return {
        **result,
        "lines": resolved_accounts,
        "pipeline": {
            **_posting_pipeline(
                validation_status="passed",
                validation_balanced=result["is_balanced"],
                posting_rule_status=posting_rule_status,
                posting_rule=posting_rule,
            ),
            "debit_entry": {"status": "pending"},
            "credit_entry": {"status": "pending"},
            "gl_update": {"status": "pending"},
            "audit_log": {"status": "pending"},
            "subledger": {"status": "pending"},
        },
    }


@app.post("/posting-engine/post", response_model=PostingEnginePostResponse)
async def post_engine_transaction(request: PostingEngineRequest, db: Session = Depends(get_db)):
    started_at = datetime.utcnow()
    if request.idempotency_key:
        existing = (
            db.query(JournalEntry)
            .filter(JournalEntry.tenant_id == request.tenant_id, JournalEntry.idempotency_key == request.idempotency_key)
            .first()
        )
        if existing:
            return {
                **_journal_entry_response(existing),
                "pipeline": _posting_pipeline(subledger_entry_id=None),
            }

    journal_entry = _post_journal(
        db=db,
        tenant_id=request.tenant_id,
        description=request.description or f"{request.source_module}.{request.source_event}",
        lines=request.lines,
        reference=request.source_reference,
        metadata=request.metadata,
        idempotency_key=request.idempotency_key,
        source_module=request.source_module,
        source_event=request.source_event,
        source_reference=request.source_reference,
        branch_id=request.branch_id,
        business_date=request.business_date,
        financial_year=request.financial_year,
    )
    subledger_entry = _create_subledger_entry(
        db=db,
        tenant_id=request.tenant_id,
        source_module=request.source_module,
        source_event=request.source_event,
        source_reference=request.source_reference,
        amount=sum(line.debit for line in request.lines),
        journal_entry_id=journal_entry.id,
        metadata=request.metadata,
    )
    _log_audit(
        db,
        tenant_id=request.tenant_id,
        entity="posting_engine",
        entity_id=journal_entry.id,
        action="post",
        payload={
            "source_module": request.source_module,
            "source_event": request.source_event,
            "source_reference": request.source_reference,
            "subledger_entry_id": subledger_entry.id,
        },
    )
    matching_rule = _find_posting_rule(
        db,
        request.tenant_id,
        request.source_module,
        request.source_event,
        {"amount": sum(line.debit for line in request.lines), **(request.metadata or {})},
    )
    _log_posting_execution(
        db,
        tenant_id=request.tenant_id,
        rule_id=matching_rule.id if matching_rule else None,
        source_module=request.source_module,
        source_event=request.source_event,
        source_reference=request.source_reference,
        status="posted",
        input_payload=request.metadata,
        generated_lines=[line.dict() for line in request.lines],
        journal_id=journal_entry.id,
        started_at=started_at,
    )
    db.commit()
    db.refresh(journal_entry)
    return {
        **_journal_entry_response(journal_entry),
        "pipeline": _posting_pipeline(
            posting_rule_status="applied",
            posting_rule={
                "source_module": request.source_module,
                "source_event": request.source_event,
                "source_reference": request.source_reference,
            },
            subledger_entry_id=subledger_entry.id,
        ),
    }


@app.post("/vouchers", response_model=VoucherResponse)
async def create_voucher(voucher: VoucherCreate, db: Session = Depends(get_db)):
    if not voucher.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if voucher.voucher_type == "receipt" and not voucher.payment_mode:
        raise HTTPException(status_code=400, detail="payment_mode is required for receipt vouchers")
    if voucher.voucher_type == "receipt" and voucher.payment_mode != "cash" and not voucher.payment_reference:
        raise HTTPException(status_code=400, detail="payment_reference is required for non-cash receipt vouchers")
    engine_lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            description=line.description,
            department_id=line.department_id,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            project_id=line.project_id,
            employee_id=line.employee_id,
            product_id=line.product_id,
            business_unit_id=line.business_unit_id,
            branch_id=voucher.branch_id,
            currency=voucher.currency,
        )
        for line in voucher.lines
    ]
    _validate_double_entry(engine_lines)
    for line in voucher.lines:
        _get_postable_account_by_id(line.gl_account_id, voucher.tenant_id, db)

    new_voucher = Voucher(
        id=str(uuid4()),
        tenant_id=voucher.tenant_id,
        voucher_number=_next_voucher_number(voucher.tenant_id, voucher.voucher_type, db),
        voucher_type=voucher.voucher_type,
        voucher_date=voucher.voucher_date or datetime.utcnow(),
        description=voucher.description,
        reference=voucher.reference,
        branch_id=voucher.branch_id,
        currency=voucher.currency or "INR",
        status="draft",
        created_by=voucher.created_by,
        payment_mode=voucher.payment_mode,
        payment_reference=voucher.payment_reference,
        payment_details=voucher.payment_details,
        metadata_json=voucher.metadata,
    )
    db.add(new_voucher)
    db.flush()
    for line in voucher.lines:
        db.add(
            VoucherLine(
                id=str(uuid4()),
                voucher_id=new_voucher.id,
                gl_account_id=line.gl_account_id,
                debit=line.debit,
                credit=line.credit,
                description=line.description,
                department_id=line.department_id,
                cost_center=line.cost_center,
                profit_center=line.profit_center,
                project_id=line.project_id,
                employee_id=line.employee_id,
                product_id=line.product_id,
                business_unit_id=line.business_unit_id,
            )
        )
    _log_audit(db, voucher.tenant_id, "voucher", new_voucher.id, "create", {"voucher_type": voucher.voucher_type, "payment_mode": voucher.payment_mode}, voucher.created_by)
    db.commit()
    db.refresh(new_voucher)
    return _voucher_response(new_voucher)


@app.get("/payment-vouchers/categories")
async def payment_voucher_categories():
    return {"items": _payment_category_options()}


@app.get("/receipt-vouchers/options")
async def receipt_voucher_options():
    return _receipt_voucher_options()


@app.get("/contra-vouchers/options")
async def contra_voucher_options():
    return _contra_voucher_options()


@app.get("/credit-notes/options")
async def credit_note_options():
    return _credit_note_options()


@app.get("/debit-notes/options")
async def debit_note_options():
    return _debit_note_options()


@app.post("/payment-vouchers", response_model=VoucherResponse)
async def create_payment_voucher(payment: PaymentVoucherCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_payment_voucher_payload(payment, db)
    return await create_voucher(voucher_payload, db)


@app.post("/api/v1/ap/vendors", response_model=VendorResponse)
async def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    if not vendor.vendor_name.strip():
        raise HTTPException(status_code=400, detail="vendor_name is required")
    new_vendor = Vendor(
        id=str(uuid4()),
        tenant_id=vendor.tenant_id,
        vendor_code=vendor.vendor_code,
        vendor_name=vendor.vendor_name,
        vendor_type=vendor.vendor_type or "supplier",
        status=vendor.status or "draft",
        payment_terms=vendor.payment_terms,
        credit_limit=vendor.credit_limit or 0.0,
        gst_number=vendor.gst_number,
        currency=vendor.currency or "INR",
        branch_id=vendor.branch_id,
        metadata_json=vendor.metadata,
        created_by=vendor.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_vendor)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(new_vendor)
    return _vendor_response(new_vendor)


@app.get("/api/v1/ap/vendors", response_model=List[VendorResponse])
async def list_vendors(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    vendors = db.query(Vendor).filter(Vendor.tenant_id == tenant_id).order_by(Vendor.vendor_name).all()
    return [_vendor_response(vendor) for vendor in vendors]


@app.get("/api/v1/ap/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    vendor = _get_vendor_by_id(vendor_id, tenant_id, db)
    return _vendor_response(vendor)


@app.post("/api/v1/ap/invoices", response_model=APInvoiceResponse)
async def create_ap_invoice(invoice: APInvoiceCreate, db: Session = Depends(get_db)):
    if invoice.total_amount <= 0:
        raise HTTPException(status_code=400, detail="total_amount must be positive")
    _get_vendor_by_id(invoice.vendor_id, invoice.tenant_id, db)
    new_invoice = APInvoice(
        id=str(uuid4()),
        tenant_id=invoice.tenant_id,
        vendor_id=invoice.vendor_id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        currency=invoice.currency or "INR",
        total_amount=round(invoice.total_amount, 2),
        status=invoice.status or "draft",
        branch_id=invoice.branch_id,
        reference=invoice.reference,
        description=invoice.description,
        metadata_json=invoice.metadata,
        created_by=invoice.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_invoice)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(new_invoice)
    _create_subledger_entry(
        db=db,
        tenant_id=invoice.tenant_id,
        source_module="vendor",
        source_event="invoice_received",
        source_reference=invoice.invoice_number,
        amount=invoice.total_amount,
        metadata={
            "vendor_id": invoice.vendor_id,
            "invoice_number": invoice.invoice_number,
            "due_date": invoice.due_date.isoformat(),
        },
    )
    db.commit()
    return _ap_invoice_response(new_invoice)


@app.get("/api/v1/ap/invoices", response_model=List[APInvoiceResponse])
async def list_ap_invoices(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    invoices = db.query(APInvoice).filter(APInvoice.tenant_id == tenant_id).order_by(APInvoice.invoice_date.desc()).all()
    return [_ap_invoice_response(invoice) for invoice in invoices]


@app.get("/api/v1/ap/invoices/{invoice_id}", response_model=APInvoiceResponse)
async def get_ap_invoice(invoice_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    invoice = (
        db.query(APInvoice)
        .filter(APInvoice.id == invoice_id, APInvoice.tenant_id == tenant_id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found for tenant")
    return _ap_invoice_response(invoice)


@app.get("/api/v1/ap/vendors/{vendor_id}/ledger", response_model=APVendorLedgerResponse)
async def get_vendor_ledger(vendor_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    vendor = _get_vendor_by_id(vendor_id, tenant_id, db)
    invoices = db.query(APInvoice).filter(APInvoice.vendor_id == vendor_id, APInvoice.tenant_id == tenant_id).order_by(APInvoice.invoice_date.desc()).all()
    payments = []
    for voucher in db.query(Voucher).filter(Voucher.tenant_id == tenant_id, Voucher.voucher_type == "payment").all():
        metadata = voucher.metadata_json or {}
        payment_voucher = metadata.get("payment_voucher") if isinstance(metadata, dict) else {}
        payment_voucher = payment_voucher or {}
        if payment_voucher.get("vendor_id") == vendor_id:
            payments.append(round(payment_voucher.get("amount") or 0.0, 2))
    subledger_entries = (
        db.query(SubLedgerEntry)
        .filter(SubLedgerEntry.tenant_id == tenant_id, SubLedgerEntry.source_module == "vendor")
        .order_by(SubLedgerEntry.created_at.desc())
        .all()
    )
    vendor_subledger = [entry for entry in subledger_entries if (entry.metadata_json or {}).get("vendor_id") == vendor_id or (entry.source_reference and any(invoice.invoice_number == entry.source_reference for invoice in invoices))]
    total_payments = sum(payments)
    outstanding_balance = sum(invoice.total_amount for invoice in invoices) - total_payments
    return {
        "tenant_id": tenant_id,
        "vendor": _vendor_response(vendor),
        "total_invoices": len(invoices),
        "total_payments": round(total_payments, 2),
        "outstanding_balance": round(outstanding_balance, 2),
        "invoices": [_ap_invoice_response(invoice) for invoice in invoices],
        "subledger_entries": [_subledger_response(entry) for entry in vendor_subledger],
    }


@app.get("/api/v1/ap/dashboard")
async def ap_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    vendors = db.query(Vendor).filter(Vendor.tenant_id == tenant_id).all()
    invoices = db.query(APInvoice).filter(APInvoice.tenant_id == tenant_id).all()
    payments = []
    for voucher in db.query(Voucher).filter(Voucher.tenant_id == tenant_id, Voucher.voucher_type == "payment").all():
        metadata = voucher.metadata_json or {}
        payment_voucher = metadata.get("payment_voucher") if isinstance(metadata, dict) else None
        payment_voucher = payment_voucher if isinstance(payment_voucher, dict) else {}
        if payment_voucher.get("vendor_id"):
            payments.append(round(payment_voucher.get("amount") or 0.0, 2))
    outstanding_balance = sum(invoice.total_amount for invoice in invoices) - sum(payments)
    overdue_invoices = sum(1 for invoice in invoices if invoice.due_date and invoice.due_date < datetime.utcnow() and invoice.status != "paid")
    pending_invoices = sum(1 for invoice in invoices if invoice.status not in {"paid", "closed"})
    return {
        "tenant_id": tenant_id,
        "total_vendors": len(vendors),
        "total_invoices": len(invoices),
        "outstanding_payables": round(outstanding_balance, 2),
        "invoices_pending": pending_invoices,
        "invoices_overdue": overdue_invoices,
        "payments_recorded": len(payments),
    }


@app.post("/contra-vouchers", response_model=VoucherResponse)
async def create_contra_voucher(contra: ContraVoucherCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_contra_voucher_payload(contra, db)
    return await create_voucher(voucher_payload, db)


@app.post("/receipt-vouchers", response_model=VoucherResponse)
async def create_receipt_voucher(receipt: ReceiptVoucherCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_receipt_voucher_payload(receipt, db)
    return await create_voucher(voucher_payload, db)


@app.post("/credit-notes", response_model=VoucherResponse)
async def create_credit_note(credit_note: CreditNoteCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_credit_note_payload(credit_note, db)
    return await create_voucher(voucher_payload, db)


@app.post("/debit-notes", response_model=VoucherResponse)
async def create_debit_note(debit_note: DebitNoteCreate, db: Session = Depends(get_db)):
    voucher_payload = _build_debit_note_payload(debit_note, db)
    return await create_voucher(voucher_payload, db)


@app.get("/vouchers")
async def list_vouchers(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    voucher_type: Optional[str] = Query(None),
    payment_category: Optional[str] = Query(None),
    receipt_category: Optional[str] = Query(None),
    contra_transfer_type: Optional[str] = Query(None),
    credit_note_type: Optional[str] = Query(None),
    debit_note_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Voucher).filter(Voucher.tenant_id == tenant_id)
    if status:
        query = query.filter(Voucher.status == status)
    if voucher_type:
        query = query.filter(Voucher.voucher_type == voucher_type)
    items = query.order_by(Voucher.voucher_date.desc()).all()
    if payment_category:
        category_key = _normalize_payment_category(payment_category)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("payment_voucher") or {}).get("category") == category_key
        ]
    if receipt_category:
        category_key = _normalize_receipt_category(receipt_category)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("receipt_voucher") or {}).get("category") == category_key
        ]
    if contra_transfer_type:
        transfer_key = _normalize_contra_transfer_type(contra_transfer_type)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("contra_voucher") or {}).get("transfer_type") == transfer_key
        ]
    if credit_note_type:
        note_type_key = _normalize_credit_note_type(credit_note_type)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("credit_note") or {}).get("type") == note_type_key
        ]
    if debit_note_type:
        note_type_key = _normalize_debit_note_type(debit_note_type)
        items = [
            item
            for item in items
            if ((item.metadata_json or {}).get("debit_note") or {}).get("type") == note_type_key
        ]
    return {"items": [_voucher_response(item) for item in items], "total": len(items)}


@app.post("/vouchers/{voucher_id}/verify", response_model=VoucherResponse)
async def verify_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft vouchers can be verified")
    voucher.status = "verified"
    voucher.verified_by = request.performed_by
    voucher.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "voucher", voucher.id, "verify", None, request.performed_by)
    db.commit()
    db.refresh(voucher)
    return _voucher_response(voucher)


@app.post("/vouchers/{voucher_id}/approve", response_model=VoucherResponse)
async def approve_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "verified":
        raise HTTPException(status_code=400, detail="Only verified vouchers can be approved")
    voucher.status = "approved"
    voucher.approved_by = request.performed_by
    voucher.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "voucher", voucher.id, "approve", None, request.performed_by)
    db.commit()
    db.refresh(voucher)
    return _voucher_response(voucher)


@app.post("/vouchers/{voucher_id}/post", response_model=JournalEntryResponse)
async def post_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved vouchers can be posted")

    lines = [
        PostingEngineLine(
            gl_account_id=line.gl_account_id,
            debit=line.debit,
            credit=line.credit,
            description=line.description,
            branch_id=voucher.branch_id,
            currency=voucher.currency,
            department_id=line.department_id,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            project_id=line.project_id,
            employee_id=line.employee_id,
            product_id=line.product_id,
            business_unit_id=line.business_unit_id,
        )
        for line in voucher.lines
    ]
    journal_entry = _post_journal(
        db=db,
        tenant_id=request.tenant_id,
        description=voucher.description,
        lines=lines,
        reference=voucher.reference or voucher.voucher_number,
        metadata=voucher.metadata_json,
        source_module="accounting",
        source_event=f"{voucher.voucher_type}.voucher",
        source_reference=voucher.voucher_number,
        branch_id=voucher.branch_id,
        business_date=voucher.voucher_date,
        voucher_id=voucher.id,
    )
    voucher.status = "posted"
    voucher.posted_journal_entry_id = journal_entry.id
    voucher.updated_at = datetime.utcnow()
    _log_audit(db, request.tenant_id, "voucher", voucher.id, "post", {"journal_entry_id": journal_entry.id}, request.performed_by)
    db.commit()
    db.refresh(journal_entry)
    return _journal_entry_response(journal_entry)


@app.post("/vouchers/{voucher_id}/reverse", response_model=VoucherResponse)
async def reverse_voucher(voucher_id: str, request: VoucherActionRequest, db: Session = Depends(get_db)):
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id, Voucher.tenant_id == request.tenant_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for tenant")
    if voucher.status != "posted":
        raise HTTPException(status_code=400, detail="Only posted vouchers can be reversed")
    if not voucher.posted_journal_entry_id:
        raise HTTPException(status_code=400, detail="Voucher has no posted journal entry to reverse")

    reversal_entry = await reverse_gl_posting(voucher.posted_journal_entry_id, request.tenant_id, db)
    voucher.status = "reversed"
    voucher.updated_at = datetime.utcnow()
    _log_audit(
        db,
        request.tenant_id,
        "voucher",
        voucher.id,
        "reverse",
        {"reversal_journal_entry_id": reversal_entry["id"]},
        request.performed_by,
    )
    db.commit()
    db.refresh(voucher)
    return _voucher_response(voucher)


@app.get("/gl-balances")
async def gl_balances(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()
    return {"accounts": accounts}


@app.get("/gl-ledger")
async def gl_ledger(
    tenant_id: str = Query(...),
    financial_year: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(GLBalance).filter(GLBalance.tenant_id == tenant_id)
    if financial_year:
        query = query.filter(GLBalance.financial_year == financial_year)
    if branch_id:
        query = query.filter(GLBalance.branch_id == branch_id)
    balances = query.all()
    accounts = {account.id: account for account in db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).all()}
    rows = []
    for balance in balances:
        account = accounts.get(balance.gl_account_id)
        rows.append(
            {
                "gl_account_id": balance.gl_account_id,
                "gl_number": account.account_code if account else None,
                "account_code": account.account_code if account else None,
                "account_name": account.account_name if account else None,
                "branch": balance.branch_id or "all",
                "branch_id": balance.branch_id,
                "currency": balance.currency,
                "financial_year": balance.financial_year,
                "opening_balance": balance.opening_balance,
                "debit": balance.total_debit,
                "credit": balance.total_credit,
                "balance": balance.closing_balance,
                "closing_balance": balance.closing_balance,
            }
        )
    return {"items": rows, "total": len(rows)}


def _trial_balance_line_response(line: TrialBalanceLine) -> dict:
    return {
        "id": line.id,
        "account_id": line.account_id,
        "account_code": line.account_code,
        "account_name": line.account_name,
        "account_type": line.account_type,
        "opening_debit": round(line.opening_debit or 0.0, 2),
        "opening_credit": round(line.opening_credit or 0.0, 2),
        "period_debit": round(line.period_debit or 0.0, 2),
        "period_credit": round(line.period_credit or 0.0, 2),
        "closing_debit": round(line.closing_debit or 0.0, 2),
        "closing_credit": round(line.closing_credit or 0.0, 2),
    }


def _financial_statement_line_response(line: FinancialStatementLine) -> dict:
    return {
        "id": line.id,
        "section": line.section,
        "label": line.label,
        "account_code": line.account_code,
        "amount": round(line.amount or 0.0, 2),
        "line_type": line.line_type,
        "order_index": line.order_index,
    }


def _financial_statement_ratio_response(ratio: FinancialStatementRatio) -> dict:
    return {
        "id": ratio.id,
        "ratio_name": ratio.ratio_name,
        "value": round(ratio.value or 0.0, 2),
        "interpretation": ratio.interpretation,
    }


def _financial_statement_response(statement: FinancialStatement) -> dict:
    return {
        "id": statement.id,
        "tenant_id": statement.tenant_id,
        "statement_type": statement.statement_type,
        "scope": statement.scope,
        "book": statement.book,
        "period": statement.period,
        "currency": statement.currency,
        "status": statement.status,
        "generated_on": statement.generated_on,
        "as_of": statement.as_of,
        "lines": [_financial_statement_line_response(line) for line in statement.lines],
        "ratios": [_financial_statement_ratio_response(ratio) for ratio in statement.ratios],
    }


def _statement_amount_for_account(item: dict, account_types: set[str]) -> float:
    account = item["account"]
    if account.account_type not in account_types:
        return 0.0
    balance = item["balance"]
    if account.account_type in {"liability", "equity", "revenue"}:
        balance = -balance
    return round(balance, 2)


def _build_statement_lines(tenant_id: str, db: Session, statement_type: str, period: Optional[str] = None) -> tuple[list[dict], list[dict]]:
    account_balances = _account_balances(tenant_id, db)
    if statement_type in {"balance_sheet", "balance-sheet", "balancesheet"}:
        assets = _statement_amount_for_account
        asset_total = round(sum(_statement_amount_for_account(item, {"asset"}) for item in account_balances), 2)
        liability_total = round(sum(_statement_amount_for_account(item, {"liability"}) for item in account_balances), 2)
        equity_total = round(sum(_statement_amount_for_account(item, {"equity"}) for item in account_balances), 2)
        lines = [
            {"section": "Assets", "label": "Total Assets", "amount": asset_total, "line_type": "total", "order_index": 10},
            {"section": "Liabilities", "label": "Total Liabilities", "amount": liability_total, "line_type": "total", "order_index": 20},
            {"section": "Equity", "label": "Total Equity", "amount": equity_total, "line_type": "total", "order_index": 30},
            {"section": "Summary", "label": "Net Position", "amount": round(asset_total - (liability_total + equity_total), 2), "line_type": "summary", "order_index": 40},
        ]
        ratios = [
            {"ratio_name": "debt_to_equity", "value": round(liability_total / equity_total, 4) if equity_total else 0.0, "interpretation": "Debt to equity"},
            {"ratio_name": "asset_to_liability", "value": round(asset_total / liability_total, 4) if liability_total else 0.0, "interpretation": "Asset to liability"},
        ]
        return lines, ratios

    if statement_type in {"profit_and_loss", "p_and_l", "pnl", "profit-loss"}:
        revenue_total = round(sum(_statement_amount_for_account(item, {"revenue"}) for item in account_balances), 2)
        expense_total = round(sum(_statement_amount_for_account(item, {"expense"}) for item in account_balances), 2)
        net_profit = round(revenue_total - expense_total, 2)
        lines = [
            {"section": "Revenue", "label": "Total Revenue", "amount": revenue_total, "line_type": "total", "order_index": 10},
            {"section": "Expenses", "label": "Total Expenses", "amount": expense_total, "line_type": "total", "order_index": 20},
            {"section": "Summary", "label": "Net Profit", "amount": net_profit, "line_type": "total", "order_index": 30},
        ]
        ratios = [
            {"ratio_name": "net_profit_margin", "value": round(net_profit / revenue_total, 4) if revenue_total else 0.0, "interpretation": "Net profit margin"},
            {"ratio_name": "expense_ratio", "value": round(expense_total / revenue_total, 4) if revenue_total else 0.0, "interpretation": "Expense ratio"},
        ]
        return lines, ratios

    lines = [{"section": "Summary", "label": f"{statement_type.title()}", "amount": 0.0, "line_type": "summary", "order_index": 10}]
    ratios = []
    return lines, ratios


def _trial_balance_response(trial_balance: TrialBalance, include_lines: bool = False) -> dict:
    payload = {
        "id": trial_balance.id,
        "tenant_id": trial_balance.tenant_id,
        "scope": trial_balance.scope,
        "book": trial_balance.book,
        "period": trial_balance.period,
        "currency": trial_balance.currency,
        "status": trial_balance.status,
        "generated_on": trial_balance.generated_on,
        "total_debit": round(trial_balance.total_debit or 0.0, 2),
        "total_credit": round(trial_balance.total_credit or 0.0, 2),
        "is_balanced": trial_balance.is_balanced,
        "validation_summary": trial_balance.validation_summary,
    }
    if include_lines:
        payload["rows"] = [_trial_balance_line_response(line) for line in trial_balance.lines]
    return payload


@app.post("/api/v1/accounting/trial-balance/generate")
async def generate_trial_balance(request: TrialBalanceGenerateRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    account_balances = _account_balances(request.tenant_id, db)
    rows: List[TrialBalanceLine] = []
    total_debit = 0.0
    total_credit = 0.0
    for item in account_balances:
        account = item["account"]
        balance = item["balance"]
        if balance >= 0:
            period_debit = round(balance, 2)
            period_credit = 0.0
        else:
            period_debit = 0.0
            period_credit = round(abs(balance), 2)
        total_debit += period_debit
        total_credit += period_credit
        rows.append(
            TrialBalanceLine(
                id=str(uuid4()),
                tenant_id=request.tenant_id,
                account_id=account.id,
                account_code=account.account_code,
                account_name=account.account_name,
                account_type=account.account_type,
                opening_debit=0.0,
                opening_credit=0.0,
                period_debit=period_debit,
                period_credit=period_credit,
                closing_debit=period_debit,
                closing_credit=period_credit,
            )
        )

    is_balanced = round(total_debit, 2) == round(total_credit, 2)
    trial_balance = TrialBalance(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        scope=request.scope or "enterprise",
        book=request.book or "primary",
        period=request.period,
        currency=request.currency or "INR",
        status="balanced" if is_balanced else "exception",
        generated_on=datetime.utcnow(),
        total_debit=round(total_debit, 2),
        total_credit=round(total_credit, 2),
        is_balanced="true" if is_balanced else "false",
        validation_summary={
            "debit_credit_match": is_balanced,
            "missing_accounts": 0,
            "inactive_accounts": 0,
            "suspense_accounts": 0,
            "unposted_journals": 0,
            "closed_period_violations": 0,
        },
    )
    db.add(trial_balance)
    db.flush()
    for line in rows:
        line.trial_balance_id = trial_balance.id
        db.add(line)
    db.commit()
    db.refresh(trial_balance)
    return _trial_balance_response(trial_balance, include_lines=True)


@app.get("/api/v1/accounting/trial-balances")
async def list_trial_balances(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    balances = (
        db.query(TrialBalance)
        .filter(TrialBalance.tenant_id == tenant_id)
        .order_by(TrialBalance.generated_on.desc())
        .all()
    )
    return {
        "tenant_id": tenant_id,
        "total": len(balances),
        "items": [_trial_balance_response(balance) for balance in balances],
    }


@app.get("/api/v1/accounting/trial-balances/{trial_balance_id}")
async def get_trial_balance(trial_balance_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    trial_balance = (
        db.query(TrialBalance)
        .filter(TrialBalance.id == trial_balance_id, TrialBalance.tenant_id == tenant_id)
        .first()
    )
    if not trial_balance:
        raise HTTPException(status_code=404, detail="Trial balance not found")
    return _trial_balance_response(trial_balance, include_lines=True)


@app.get("/api/v1/accounting/trial-balances/{trial_balance_id}/lines")
async def get_trial_balance_lines(trial_balance_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    trial_balance = (
        db.query(TrialBalance)
        .filter(TrialBalance.id == trial_balance_id, TrialBalance.tenant_id == tenant_id)
        .first()
    )
    if not trial_balance:
        raise HTTPException(status_code=404, detail="Trial balance not found")
    return {
        "tenant_id": tenant_id,
        "trial_balance_id": trial_balance_id,
        "total": len(trial_balance.lines),
        "items": [_trial_balance_line_response(line) for line in trial_balance.lines],
    }


@app.get("/api/v1/accounting/trial-balance/dashboard")
async def trial_balance_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    balances = (
        db.query(TrialBalance)
        .filter(TrialBalance.tenant_id == tenant_id)
        .order_by(TrialBalance.generated_on.desc())
        .all()
    )
    balanced = sum(1 for item in balances if str(item.status).lower() == "balanced")
    unbalanced = len(balances) - balanced
    kpis = {
        "trial_balances_generated": len(balances),
        "balanced": balanced,
        "unbalanced": unbalanced,
        "pending_adjustments": max(0, unbalanced),
        "suspense_accounts": 0,
        "reconciliation_status": "complete" if balanced else "pending",
        "close_readiness": 100 if balanced else 72,
        "ai_financial_score": 92 if balanced else 74,
    }
    charts = {
        "daily_balance_trend": [{"label": balance.period or "period", "value": round(balance.total_debit or 0.0, 2)} for balance in balances[:6]],
        "debit_vs_credit": [
            {"label": "Debit", "value": round(sum(balance.total_debit or 0.0 for balance in balances), 2)},
            {"label": "Credit", "value": round(sum(balance.total_credit or 0.0 for balance in balances), 2)},
        ],
    }
    summary = {
        "status": "healthy" if unbalanced == 0 else "exception",
        "message": "Trial balance is current and balanced." if unbalanced == 0 else "Trial balance requires review for exceptions.",
    }
    return {"tenant_id": tenant_id, "kpis": kpis, "charts": charts, "summary": summary}


@app.post("/api/v1/financial-statements/generate")
async def generate_financial_statement(request: FinancialStatementGenerateRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    statement_type = (request.statement_type or "balance_sheet").lower().replace(" ", "_")
    lines_payload, ratios_payload = _build_statement_lines(request.tenant_id, db, statement_type, request.period)
    statement = FinancialStatement(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        statement_type=statement_type,
        scope=request.scope or "enterprise",
        book=request.book or "primary",
        period=request.period,
        currency=request.currency or "INR",
        status="generated",
        generated_on=datetime.utcnow(),
        as_of=request.as_of or request.business_date or datetime.utcnow(),
    )
    db.add(statement)
    db.flush()
    for index, line in enumerate(lines_payload):
        db.add(
            FinancialStatementLine(
                id=str(uuid4()),
                financial_statement_id=statement.id,
                tenant_id=request.tenant_id,
                section=line.get("section"),
                label=line.get("label", "Line"),
                account_code=line.get("account_code"),
                amount=line.get("amount", 0.0),
                line_type=line.get("line_type", "summary"),
                order_index=index,
            )
        )
    for ratio in ratios_payload:
        db.add(
            FinancialStatementRatio(
                id=str(uuid4()),
                financial_statement_id=statement.id,
                tenant_id=request.tenant_id,
                ratio_name=ratio.get("ratio_name", "ratio"),
                value=ratio.get("value", 0.0),
                interpretation=ratio.get("interpretation"),
            )
        )
    db.commit()
    db.refresh(statement)
    return _financial_statement_response(statement)


@app.get("/api/v1/financial-statements")
async def list_financial_statements(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    statements = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.tenant_id == tenant_id)
        .order_by(FinancialStatement.generated_on.desc())
        .all()
    )
    return {"tenant_id": tenant_id, "total": len(statements), "items": [_financial_statement_response(statement) for statement in statements]}


@app.get("/api/v1/financial-statements/dashboard")
async def financial_statement_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    statements = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.tenant_id == tenant_id)
        .order_by(FinancialStatement.generated_on.desc())
        .all()
    )
    return {
        "tenant_id": tenant_id,
        "kpis": {
            "statements_generated": len(statements),
            "latest_statement_type": statements[0].statement_type if statements else "balance_sheet",
            "latest_status": statements[0].status if statements else "pending",
        },
        "charts": {
            "statement_types": [{"label": statement.statement_type, "value": 1} for statement in statements[:5]],
        },
        "summary": {"status": "healthy" if statements else "pending", "message": "Financial statements are ready to review." if statements else "No financial statements generated yet."},
    }


@app.get("/api/v1/financial-statements/{statement_id}")
async def get_financial_statement(statement_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    statement = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.id == statement_id, FinancialStatement.tenant_id == tenant_id)
        .first()
    )
    if not statement:
        raise HTTPException(status_code=404, detail="Financial statement not found")
    return _financial_statement_response(statement)


@app.get("/api/v1/financial-statements/{statement_id}/lines")
async def get_financial_statement_lines(statement_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    statement = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.id == statement_id, FinancialStatement.tenant_id == tenant_id)
        .first()
    )
    if not statement:
        raise HTTPException(status_code=404, detail="Financial statement not found")
    return {"tenant_id": tenant_id, "financial_statement_id": statement_id, "total": len(statement.lines), "items": [_financial_statement_line_response(line) for line in statement.lines]}


@app.get("/api/v1/financial-statements/{statement_id}/ratios")
async def get_financial_statement_ratios(statement_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    statement = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.id == statement_id, FinancialStatement.tenant_id == tenant_id)
        .first()
    )
    if not statement:
        raise HTTPException(status_code=404, detail="Financial statement not found")
    return {"tenant_id": tenant_id, "financial_statement_id": statement_id, "total": len(statement.ratios), "items": [_financial_statement_ratio_response(ratio) for ratio in statement.ratios]}


@app.get("/dashboard")
async def accounting_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    trial = await trial_balance(tenant_id=tenant_id, start_date=None, end_date=None, db=db)
    vouchers_pending = (
        db.query(Voucher)
        .filter(Voucher.tenant_id == tenant_id, Voucher.status.in_(["draft", "verified", "approved"]))
        .count()
    )
    return {
        "tenant_id": tenant_id,
        "chart_of_accounts": db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).count(),
        "posting_rules": db.query(PostingRule).filter(PostingRule.tenant_id == tenant_id).count(),
        "journal_entries": db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id).count(),
        "subledger_entries": db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id).count(),
        "pending_vouchers": vouchers_pending,
        "trial_balance": {
            "total_debit": trial["total_debit"],
            "total_credit": trial["total_credit"],
            "is_balanced": trial["is_balanced"],
        },
    }


def _normal_financial_balance(account_type: str, balance: float) -> float:
    value = balance or 0.0
    if account_type in {"liability", "equity", "revenue"}:
        return -value
    return value


def _account_type_totals(account_balances: list[dict]) -> dict:
    totals = {"asset": 0.0, "liability": 0.0, "equity": 0.0, "revenue": 0.0, "expense": 0.0}
    for item in account_balances:
        account = item["account"]
        if account.account_type in totals:
            totals[account.account_type] += _normal_financial_balance(account.account_type, item["balance"])
    return {key: round(value, 2) for key, value in totals.items()}


def _accounting_action_template(action_type: str) -> dict:
    templates = {
        "loan_disbursed": {
            "label": "Loan disbursed",
            "source_module": "loans",
            "source_event": "disbursement",
            "debit_account_code": "1200_LOAN_RECEIVABLE",
            "credit_account_code": "1120_BANK",
            "explanation": "Loan receivable increases and bank reduces automatically.",
        },
        "customer_paid_emi": {
            "label": "Customer paid EMI",
            "source_module": "loans",
            "source_event": "payment",
            "debit_account_code": "1120_BANK",
            "credit_account_code": "1200_LOAN_RECEIVABLE",
            "explanation": "Bank increases and customer loan receivable reduces automatically.",
        },
        "deposit_received": {
            "label": "Deposit received",
            "source_module": "deposits",
            "source_event": "deposit",
            "debit_account_code": "1120_BANK",
            "credit_account_code": "2200_CUSTOMER_DEPOSITS",
            "explanation": "Bank increases and customer deposit liability is created automatically.",
        },
        "expense_paid": {
            "label": "Expense paid",
            "source_module": "expenses",
            "source_event": "payment",
            "debit_account_code": "5120_ELECTRICITY_EXPENSE",
            "credit_account_code": "1120_BANK",
            "explanation": "Expense is recognized and bank is credited automatically.",
        },
        "salary_paid": {
            "label": "Salary paid",
            "source_module": "hrms",
            "source_event": "salary_payment",
            "debit_account_code": "5210_SALARY_EXPENSE",
            "credit_account_code": "1120_BANK",
            "explanation": "Salary expense is recognized and bank payout is posted automatically.",
        },
        "interest_accrued": {
            "label": "Interest accrued",
            "source_module": "loans",
            "source_event": "interest_accrual",
            "debit_account_code": "1200_LOAN_RECEIVABLE",
            "credit_account_code": "410000",
            "explanation": "Customer receivable increases and interest income is recognized automatically.",
        },
    }
    return templates.get(action_type) or templates["expense_paid"]


def _voucher_workflow_counts(tenant_id: str, db: Session) -> dict:
    counts = {"draft": 0, "verified": 0, "approved": 0, "posted": 0, "reversed": 0}
    vouchers = db.query(Voucher).filter(Voucher.tenant_id == tenant_id).all()
    for voucher in vouchers:
        if voucher.status in counts:
            counts[voucher.status] += 1
    return counts


def _recent_journal_items(tenant_id: str, db: Session, limit: int = 8) -> list[dict]:
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.tenant_id == tenant_id)
        .order_by(JournalEntry.entry_date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": entry.id,
            "entry_date": entry.entry_date,
            "description": entry.description,
            "reference": entry.reference,
            "source_module": entry.source_module or "manual",
            "source_event": entry.source_event or "journal",
            "status": entry.posting_status,
        }
        for entry in entries
    ]


@app.get("/accounting-360/dashboard")
async def accounting_360_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    account_balances = _account_balances(tenant_id, db)
    totals = _account_type_totals(account_balances)
    trial = await trial_balance(tenant_id=tenant_id, start_date=None, end_date=None, db=db)
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).order_by(GLAccount.account_code).all()
    posting_rules = db.query(PostingRule).filter(PostingRule.tenant_id == tenant_id).all()
    journals = db.query(JournalEntry).filter(JournalEntry.tenant_id == tenant_id).all()
    subledger_rows = db.query(SubLedgerEntry).filter(SubLedgerEntry.tenant_id == tenant_id).all()
    periods = db.query(AccountingPeriod).filter(AccountingPeriod.tenant_id == tenant_id).all()
    vouchers = (
        db.query(Voucher)
        .filter(Voucher.tenant_id == tenant_id)
        .order_by(Voucher.voucher_date.desc())
        .limit(8)
        .all()
    )

    top_accounts = sorted(
        [
            {
                "id": item["account"].id,
                "account_code": item["account"].account_code,
                "account_name": item["account"].account_name,
                "account_type": item["account"].account_type,
                "balance": round(_normal_financial_balance(item["account"].account_type, item["balance"]), 2),
                "raw_balance": item["balance"],
            }
            for item in account_balances
            if abs(item["balance"]) > 0
        ],
        key=lambda row: abs(row["raw_balance"]),
        reverse=True,
    )[:8]

    module_totals: dict[str, dict] = {}
    for entry in subledger_rows:
        key = entry.source_module or "manual"
        if key not in module_totals:
            module_totals[key] = {"source_module": key, "entries": 0, "amount": 0.0}
        module_totals[key]["entries"] += 1
        module_totals[key]["amount"] = round(module_totals[key]["amount"] + (entry.amount or 0.0), 2)

    net_profit = round(totals["revenue"] - totals["expense"], 2)
    ai_summary = (
        "Trial balance is clean and auto-posting is ready."
        if trial["is_balanced"]
        else "Trial balance variance detected. Review recent manual journals and voucher postings."
    )
    if top_accounts:
        ai_summary += f" Largest movement is {top_accounts[0]['account_name']}."

    return {
        "tenant_id": tenant_id,
        "as_of": datetime.utcnow(),
        "metrics": [
            {"key": "assets", "label": "Assets", "amount": totals["asset"], "tone": "blue"},
            {"key": "liabilities", "label": "Liabilities", "amount": totals["liability"], "tone": "slate"},
            {"key": "revenue", "label": "Revenue", "amount": totals["revenue"], "tone": "emerald"},
            {"key": "expense", "label": "Expense", "amount": totals["expense"], "tone": "amber"},
            {"key": "profit", "label": "Profit", "amount": net_profit, "tone": "emerald" if net_profit >= 0 else "rose"},
        ],
        "trial_balance": trial,
        "posting_health": {
            "posting_rules": len(posting_rules),
            "active_rules": sum(1 for rule in posting_rules if str(rule.status or "").lower() in {"active", "published"}),
            "pending_rule_approvals": sum(1 for rule in posting_rules if str(rule.status or "").lower() == "pending_approval"),
            "journal_entries": len(journals),
            "subledger_entries": len(subledger_rows),
            "automation_rate": 0 if not journals else round((sum(1 for entry in journals if entry.source_module) / len(journals)) * 100, 1),
        },
        "period_controls": {
            "periods": len(periods),
            "open": sum(1 for period in periods if period.status == "open"),
            "locked": sum(1 for period in periods if period.status == "locked"),
            "pending_unlock": sum(1 for period in periods if period.status == "pending_unlock"),
            "latest": _period_response(sorted(periods, key=lambda item: item.period_start, reverse=True)[0]) if periods else None,
        },
        "voucher_workflow": _voucher_workflow_counts(tenant_id, db),
        "gl_tree": _build_coa_tree(accounts),
        "top_accounts": top_accounts,
        "source_modules": sorted(module_totals.values(), key=lambda row: row["amount"], reverse=True),
        "recent_vouchers": [_voucher_response(voucher) for voucher in vouchers],
        "recent_journals": _recent_journal_items(tenant_id, db),
        "ai_summary": ai_summary,
    }


@app.get("/accounting-360/search")
async def accounting_360_search(
    tenant_id: str = Query(...),
    q: str = Query(""),
    db: Session = Depends(get_db),
):
    query_text = q.strip().lower()
    accounts = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id).order_by(GLAccount.account_code).all()
    if query_text:
        accounts = [
            account
            for account in accounts
            if query_text in account.account_code.lower()
            or query_text in account.account_name.lower()
            or query_text in (account.category or "").lower()
            or query_text in (account.account_type or "").lower()
        ]
    return {
        "tenant_id": tenant_id,
        "query": q,
        "items": [
            {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "category": account.category,
                "posting_allowed": account.posting_allowed,
                "freeze_status": account.freeze_status,
                "currency": account.currency,
                "base_currency": account.base_currency,
                "balance": account.balance,
            }
            for account in accounts[:20]
        ],
    }


@app.get("/accounting-360/gl/{account_id}")
async def accounting_360_gl_detail(
    account_id: str,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    account = db.query(GLAccount).filter(GLAccount.id == account_id, GLAccount.tenant_id == tenant_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="GL account not found for tenant")

    lines = (
        db.query(JournalLine)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .filter(JournalEntry.tenant_id == tenant_id, JournalLine.gl_account_id == account_id)
        .order_by(JournalEntry.entry_date.desc())
        .all()
    )
    entry_ids = [line.journal_entry_id for line in lines]
    entries_by_id = {
        entry.id: entry
        for entry in db.query(JournalEntry).filter(JournalEntry.id.in_(entry_ids)).all()
    } if entry_ids else {}

    total_debit = round(sum(line.debit or 0.0 for line in lines), 2)
    total_credit = round(sum(line.credit or 0.0 for line in lines), 2)
    branch_totals: dict[str, float] = {}
    source_totals: dict[str, dict] = {}
    month_totals: dict[str, float] = {}
    for line in lines:
        entry = entries_by_id.get(line.journal_entry_id)
        branch_key = line.branch_id or (entry.branch_id if entry else None) or "all"
        branch_totals[branch_key] = round(branch_totals.get(branch_key, 0.0) + (line.debit or 0.0) - (line.credit or 0.0), 2)
        source_key = (entry.source_module if entry else None) or "manual"
        if source_key not in source_totals:
            source_totals[source_key] = {"source_module": source_key, "entries": 0, "amount": 0.0}
        source_totals[source_key]["entries"] += 1
        source_totals[source_key]["amount"] = round(source_totals[source_key]["amount"] + abs((line.debit or 0.0) - (line.credit or 0.0)), 2)
        month_key = (entry.entry_date if entry else datetime.utcnow()).strftime("%Y-%m")
        month_totals[month_key] = round(month_totals.get(month_key, 0.0) + (line.debit or 0.0) - (line.credit or 0.0), 2)

    children = db.query(GLAccount).filter(GLAccount.tenant_id == tenant_id, GLAccount.parent_account_id == account_id).order_by(GLAccount.account_code).all()
    audit = (
        db.query(AuditLog)
        .filter(AuditLog.tenant_id == tenant_id, AuditLog.entity_id == account_id)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )
    recent_lines = []
    for line in lines[:12]:
        entry = entries_by_id.get(line.journal_entry_id)
        recent_lines.append(
            {
                "journal_entry_id": line.journal_entry_id,
                "entry_date": entry.entry_date if entry else None,
                "description": line.description or (entry.description if entry else None),
                "reference": entry.reference if entry else None,
                "source_module": entry.source_module if entry else None,
                "debit": line.debit,
                "credit": line.credit,
                "branch_id": line.branch_id or (entry.branch_id if entry else None),
            }
        )

    movement = round(total_debit - total_credit, 2)
    ai_summary = f"{account.account_name} has net movement of {movement} across {len(lines)} journal lines."
    if source_totals:
        primary_source = max(source_totals.values(), key=lambda row: row["amount"])
        ai_summary += f" Main source module is {primary_source['source_module']}."
    if not _is_truthy(account.posting_allowed):
        ai_summary += " This is a control account; post through its child ledgers."

    return {
        "account": {
            "id": account.id,
            "account_code": account.account_code,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "category": account.category,
            "currency": account.currency,
            "base_currency": account.base_currency,
            "normal_balance": account.normal_balance,
            "posting_allowed": account.posting_allowed,
            "allow_manual_posting": account.allow_manual_posting,
            "allow_auto_posting": account.allow_auto_posting,
            "freeze_status": account.freeze_status,
            "exchange_gain_loss_account_code": account.exchange_gain_loss_account_code,
            "revaluation_account_code": account.revaluation_account_code,
            "status": account.status,
            "balance": account.balance,
        },
        "summary": {
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance": movement,
            "transaction_count": len(lines),
            "ai_summary": ai_summary,
            "risk": "Review" if abs(movement) > 1000000 else "Normal",
        },
        "branch_wise": [{"branch": key, "amount": value} for key, value in branch_totals.items()],
        "source_modules": sorted(source_totals.values(), key=lambda row: row["amount"], reverse=True),
        "monthly_trend": [{"month": key, "amount": month_totals[key]} for key in sorted(month_totals.keys())[-12:]],
        "children": [_account_tree_node(child) for child in children],
        "recent_entries": recent_lines,
        "audit": [
            {
                "id": item.id,
                "entity": item.entity,
                "action": item.action,
                "payload": item.payload,
                "performed_by": item.performed_by,
                "created_at": item.created_at,
            }
            for item in audit
        ],
    }


@app.post("/accounting-360/quick-action")
async def accounting_360_quick_action(request: AccountingQuickActionRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    template = _accounting_action_template(request.action_type)
    description_parts = [template["label"]]
    if request.party_name:
        description_parts.append(request.party_name)
    if request.description:
        description_parts.append(request.description)
    description = " - ".join(description_parts)
    source_reference = request.source_reference or f"A360-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    metadata = {
        "accounting_360": {
            "action_type": request.action_type,
            "party_name": request.party_name,
            "explanation": template["explanation"],
        },
        **(request.metadata or {}),
    }

    debit_account = _get_postable_account_by_code(template["debit_account_code"], request.tenant_id, db)
    credit_account = _get_postable_account_by_code(template["credit_account_code"], request.tenant_id, db)
    lines = [
        PostingEngineLine(
            gl_account_id=debit_account.id,
            debit=request.amount,
            credit=0.0,
            description=f"{template['label']} debit",
            branch_id=request.branch_id,
            currency=request.currency or "INR",
        ),
        PostingEngineLine(
            gl_account_id=credit_account.id,
            debit=0.0,
            credit=request.amount,
            description=f"{template['label']} credit",
            branch_id=request.branch_id,
            currency=request.currency or "INR",
        ),
    ]
    journal_entry = _post_journal(
        db=db,
        tenant_id=request.tenant_id,
        description=description,
        lines=lines,
        reference=source_reference,
        metadata=metadata,
        idempotency_key=f"{request.tenant_id}:{request.action_type}:{source_reference}",
        source_module=template["source_module"],
        source_event=template["source_event"],
        source_reference=source_reference,
        branch_id=request.branch_id,
        business_date=request.business_date,
    )
    subledger_entry = _create_subledger_entry(
        db=db,
        tenant_id=request.tenant_id,
        source_module=template["source_module"],
        source_event=template["source_event"],
        source_reference=source_reference,
        amount=request.amount,
        journal_entry_id=journal_entry.id,
        metadata=metadata,
    )
    _log_audit(
        db,
        request.tenant_id,
        "accounting_360",
        journal_entry.id,
        "quick_action_post",
        {"action_type": request.action_type, "amount": request.amount, "subledger_entry_id": subledger_entry.id},
        request.performed_by,
    )
    db.commit()
    db.refresh(journal_entry)
    return {
        "journal_entry": _journal_entry_response(journal_entry),
        "explanation": template["explanation"],
        "inferred_lines": [
            {"account_code": debit_account.account_code, "account_name": debit_account.account_name, "direction": "debit", "amount": request.amount},
            {"account_code": credit_account.account_code, "account_name": credit_account.account_name, "direction": "credit", "amount": request.amount},
        ],
        "pipeline": _posting_pipeline(
            posting_rule_status="accounting_360_template",
            posting_rule=template,
            subledger_entry_id=subledger_entry.id,
        ),
    }


@app.post("/day-end/close", response_model=DayEndCloseResponse)
async def close_day(request: DayEndCloseRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(DayEndClose)
        .filter(
            DayEndClose.tenant_id == request.tenant_id,
            DayEndClose.business_date == request.business_date,
            DayEndClose.branch_id == request.branch_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Day end is already closed for this scope")
    trial = await trial_balance(tenant_id=request.tenant_id, start_date=None, end_date=request.business_date, db=db)
    close = DayEndClose(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        business_date=request.business_date,
        branch_id=request.branch_id,
        status="closed" if trial["is_balanced"] else "exception",
        trial_balance_debit=trial["total_debit"],
        trial_balance_credit=trial["total_credit"],
        is_balanced="true" if trial["is_balanced"] else "false",
        checks={"trial_balance_rows": len(trial["rows"])},
        closed_by=request.closed_by,
    )
    db.add(close)
    _log_audit(db, request.tenant_id, "day_end", close.id, "close", close.checks, request.closed_by)
    db.commit()
    db.refresh(close)
    return close


@app.get("/day-end/closes", response_model=List[DayEndCloseResponse])
async def list_day_end_closes(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(DayEndClose).filter(DayEndClose.tenant_id == tenant_id).order_by(DayEndClose.business_date.desc()).all()



@app.get("/reports/trial-balance")
async def trial_balance(
    tenant_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    account_balances = _account_balances(tenant_id, db, start_date, end_date)
    rows = []
    total_debit = 0.0
    total_credit = 0.0
    for item in account_balances:
        account = item["account"]
        balance = item["balance"]
        debit = round(balance, 2) if balance >= 0 else 0.0
        credit = round(abs(balance), 2) if balance < 0 else 0.0
        total_debit += debit
        total_credit += credit
        rows.append(
            {
                "account_id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "debit": debit,
                "credit": credit,
            }
        )

    return {
        "tenant_id": tenant_id,
        "start_date": start_date,
        "end_date": end_date,
        "as_of": end_date or datetime.utcnow(),
        "rows": rows,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "is_balanced": round(total_debit, 2) == round(total_credit, 2),
    }


@app.post("/gl-postings/auto", response_model=JournalEntryResponse)
async def create_automated_gl_posting(posting: AutomatedGLPostingRequest, db: Session = Depends(get_db)):
    started_at = datetime.utcnow()
    if not posting.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    if posting.amount <= 0:
        raise HTTPException(status_code=400, detail="amount must be positive")

    if posting.idempotency_key:
        existing = (
            db.query(JournalEntry)
            .filter(
                JournalEntry.tenant_id == posting.tenant_id,
                JournalEntry.idempotency_key == posting.idempotency_key,
            )
            .first()
        )
        if existing:
            return _journal_entry_response(existing)

    posting_lines, posting_rule = _resolve_posting_map(
        posting,
        db,
        posting.amount,
        branch_id=posting.branch_id,
        currency=posting.currency,
        description_prefix=f"{posting.source_module}.{posting.source_event}",
    )
    journal_entry = _post_journal(
        db=db,
        tenant_id=posting.tenant_id,
        description=posting.description or f"{posting.source_module}.{posting.source_event}",
        reference=posting.source_reference,
        metadata=posting.metadata,
        idempotency_key=posting.idempotency_key,
        source_module=posting.source_module,
        source_event=posting.source_event,
        source_reference=posting.source_reference,
        branch_id=posting.branch_id,
        business_date=posting.business_date,
        financial_year=posting.financial_year,
        lines=posting_lines,
    )

    _create_subledger_entry(
        db=db,
        tenant_id=posting.tenant_id,
        source_module=posting.source_module,
        source_event=posting.source_event,
        source_reference=posting.source_reference,
        amount=posting.amount,
        journal_entry_id=journal_entry.id,
        metadata=posting.metadata,
    )

    _log_audit(
        db,
        tenant_id=posting.tenant_id,
        entity="gl_posting",
        entity_id=journal_entry.id,
        action="create",
        payload={
            "source_module": posting.source_module,
            "source_event": posting.source_event,
            "amount": posting.amount,
            "posting_rule_id": posting_rule.id if posting_rule else None,
            "lines": [line.dict() for line in posting_lines],
        },
    )
    _log_posting_execution(
        db,
        tenant_id=posting.tenant_id,
        rule_id=posting_rule.id if posting_rule else None,
        source_module=posting.source_module,
        source_event=posting.source_event,
        source_reference=posting.source_reference,
        status="posted",
        input_payload={"amount": posting.amount, **(posting.metadata or {})},
        generated_lines=[line.dict() for line in posting_lines],
        journal_id=journal_entry.id,
        started_at=started_at,
    )

    db.commit()
    db.refresh(journal_entry)
    return _journal_entry_response(journal_entry)


@app.post("/gl-postings/{journal_entry_id}/reverse", response_model=JournalEntryResponse)
async def reverse_gl_posting(
    journal_entry_id: str,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    original = (
        db.query(JournalEntry)
        .filter(JournalEntry.id == journal_entry_id, JournalEntry.tenant_id == tenant_id)
        .first()
    )
    if not original:
        raise HTTPException(status_code=404, detail="Journal entry not found for tenant")
    if original.posting_status == "reversed":
        raise HTTPException(status_code=400, detail="Journal entry is already reversed")

    reversal = JournalEntry(
        id=str(uuid4()),
        tenant_id=tenant_id,
        entry_date=datetime.utcnow(),
        description=f"Reversal: {original.description}",
        reference=f"REV-{original.reference or original.id}",
        metadata_json={"reverses_journal_entry_id": original.id},
        posting_status="posted",
        source_module=original.source_module,
        source_event=f"{original.source_event or 'journal'}.reversal",
        source_reference=original.source_reference,
        branch_id=original.branch_id,
        financial_year=original.financial_year or _current_financial_year(original.entry_date),
    )
    db.add(reversal)

    for line in original.lines:
        account = (
            db.query(GLAccount)
            .filter(GLAccount.id == line.gl_account_id, GLAccount.tenant_id == tenant_id)
            .first()
        )
        if not account:
            raise HTTPException(status_code=404, detail="GL account not found for tenant")
        journal_line = JournalLine(
            id=str(uuid4()),
            journal_entry_id=reversal.id,
            gl_account_id=line.gl_account_id,
            debit=line.credit,
            credit=line.debit,
            currency=line.currency or account.currency or "INR",
            transaction_currency=line.transaction_currency,
            transaction_amount=line.transaction_amount,
            exchange_rate=line.exchange_rate,
            branch_id=line.branch_id or original.branch_id,
            department_id=line.department_id,
            cost_center=line.cost_center,
            profit_center=line.profit_center,
            project_id=line.project_id,
            employee_id=line.employee_id,
            product_id=line.product_id,
            business_unit_id=line.business_unit_id,
            description=f"Reversal of {line.id}",
        )
        db.add(journal_line)
        account.balance += (line.credit or 0.0) - (line.debit or 0.0)
        _update_gl_balance(
            db=db,
            tenant_id=tenant_id,
            account=account,
            debit=journal_line.debit or 0.0,
            credit=journal_line.credit or 0.0,
            branch_id=journal_line.branch_id,
            currency=journal_line.currency,
            financial_year=reversal.financial_year,
        )

    original.posting_status = "reversed"
    db.commit()
    db.refresh(reversal)
    return _journal_entry_response(reversal)


@app.get("/reports/profit-loss")
async def profit_loss(
    tenant_id: str = Query(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    account_balances = _account_balances(tenant_id, db, start_date, end_date)
    revenue_rows, total_revenue = _financial_rows_from_balances(account_balances, {"revenue"})
    expense_rows, total_expenses = _financial_rows_from_balances(account_balances, {"expense"})
    return {
        "tenant_id": tenant_id,
        "start_date": start_date,
        "end_date": end_date,
        "as_of": end_date or datetime.utcnow(),
        "revenue": revenue_rows,
        "expenses": expense_rows,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": round(total_revenue - total_expenses, 2),
    }


@app.get("/reports/balance-sheet")
async def balance_sheet(
    tenant_id: str = Query(...),
    as_of: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    statement_date = as_of or datetime.utcnow()
    account_balances = _account_balances(tenant_id, db, None, statement_date)
    asset_rows, total_assets = _financial_rows_from_balances(account_balances, {"asset"})
    liability_rows, total_liabilities = _financial_rows_from_balances(account_balances, {"liability"})
    equity_rows, total_equity = _financial_rows_from_balances(account_balances, {"equity"})
    return {
        "tenant_id": tenant_id,
        "as_of": statement_date,
        "assets": asset_rows,
        "liabilities": liability_rows,
        "equity": equity_rows,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "is_balanced": round(total_assets, 2) == round(total_liabilities + total_equity, 2),
    }


@app.post("/tax-rules", response_model=TaxRuleResponse)
async def create_tax_rule(rule: TaxRuleCreate, db: Session = Depends(get_db)):
    if not rule.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = db.query(TaxRule).filter(TaxRule.tenant_id == rule.tenant_id, TaxRule.tax_code == rule.tax_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tax code already exists")
    if rule.payable_gl_account_id:
        payable_account = (
            db.query(GLAccount)
            .filter(
                GLAccount.id == rule.payable_gl_account_id,
                GLAccount.tenant_id == rule.tenant_id,
            )
            .first()
        )
        if not payable_account:
            raise HTTPException(status_code=404, detail="Payable GL account not found for tenant")

    tax_rule = TaxRule(
        id=str(uuid4()),
        tenant_id=rule.tenant_id,
        tax_code=rule.tax_code,
        tax_type=rule.tax_type,
        rate_percent=rule.rate_percent,
        payable_gl_account_id=rule.payable_gl_account_id,
        payable_gl_account_code=rule.payable_gl_account_code,
        expense_gl_account_code=rule.expense_gl_account_code,
    )
    db.add(tax_rule)
    db.commit()
    db.refresh(tax_rule)
    return tax_rule


@app.get("/tax-rules", response_model=List[TaxRuleResponse])
async def list_tax_rules(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(TaxRule).filter(TaxRule.tenant_id == tenant_id).all()


@app.post("/tax/compute", response_model=TaxComputationResponse)
async def compute_tax(request: TaxComputationRequest, db: Session = Depends(get_db)):
    if not request.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    rule = db.query(TaxRule).filter(TaxRule.tenant_id == request.tenant_id, TaxRule.tax_code == request.tax_code).first()

    if not rule or str(rule.is_active).lower() not in {"true", "1", "yes", "active"}:
        raise HTTPException(status_code=404, detail="Active tax rule not found")
    if request.taxable_amount <= 0:
        raise HTTPException(status_code=400, detail="taxable_amount must be positive")

    breakdown = _tax_breakdown(rule.tax_type, request.taxable_amount, rule.rate_percent)
    tax_amount = breakdown["total_tax_amount"]
    expense_code = rule.expense_gl_account_code or "5200_TAX_EXPENSE"
    if rule.payable_gl_account_id:
        payable_account = (
            db.query(GLAccount)
            .filter(
                GLAccount.id == rule.payable_gl_account_id,
                GLAccount.tenant_id == request.tenant_id,
            )
            .first()
        )
        if not payable_account:
            raise HTTPException(status_code=404, detail="Payable GL account not found for tenant")
    else:
        default_payable_code = "2310_TDS_PAYABLE" if rule.tax_type.lower() == "tds" else "2300_GST_PAYABLE"
        payable_account = _get_or_create_account(
            rule.payable_gl_account_code or default_payable_code,
            request.tenant_id,
            db,
        )
    expense_account = _get_or_create_account(expense_code, request.tenant_id, db)

    journal_entry = JournalEntry(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        entry_date=datetime.utcnow(),
        description=f"Tax computation {request.tax_code} for {request.source_module}",
        reference=request.source_reference,
        metadata_json={"tax_code": request.tax_code, "tax_breakdown": breakdown},
        posting_status="posted",
        source_module=request.source_module,
        source_event="tax_computed",
        source_reference=request.source_reference,
    )
    db.add(journal_entry)
    db.add_all(
        [
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=journal_entry.id,
                gl_account_id=expense_account.id,
                debit=tax_amount,
                credit=0.0,
                description=f"{rule.tax_type.upper()} expense",
            ),
            JournalLine(
                id=str(uuid4()),
                journal_entry_id=journal_entry.id,
                gl_account_id=payable_account.id,
                debit=0.0,
                credit=tax_amount,
                description=f"{rule.tax_type.upper()} payable",
            ),
        ]
    )
    expense_account.balance += tax_amount
    payable_account.balance -= tax_amount

    tax = TaxComputation(
        id=str(uuid4()),
        tenant_id=request.tenant_id,
        tax_rule_id=rule.id,
        journal_entry_id=journal_entry.id,
        source_module=request.source_module,
        source_reference=request.source_reference,
        taxable_amount=request.taxable_amount,
        tax_amount=tax_amount,
        breakdown=breakdown,
        status="posted",
    )
    db.add(tax)
    db.commit()
    db.refresh(tax)
    return tax


@app.post("/bank-transactions", response_model=BankStatementResponse)
async def add_bank_transaction(transaction: BankTransactionCreate, db: Session = Depends(get_db)):
    if not transaction.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    existing = (
        db.query(BankStatementTransaction)
        .filter(
            BankStatementTransaction.tenant_id == transaction.tenant_id,
            BankStatementTransaction.reference == transaction.reference,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Bank transaction reference already exists")

    bank_tx = BankStatementTransaction(
        id=str(uuid4()),
        tenant_id=transaction.tenant_id,
        reference=transaction.reference,
        transaction_date=transaction.transaction_date,
        amount=transaction.amount,
        description=transaction.description,
        status="unmatched"
    )

    db.add(bank_tx)
    db.commit()
    db.refresh(bank_tx)
    return bank_tx


@app.post("/bank-reconciliation")
async def reconcile_bank_transaction(request: ReconciliationRequest, db: Session = Depends(get_db)):
    transaction = (
        db.query(BankStatementTransaction)
        .filter(
            BankStatementTransaction.id == request.transaction_id,
            BankStatementTransaction.tenant_id == request.tenant_id,
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Bank transaction not found for tenant")

    journal_entry = (
        db.query(JournalEntry)
        .filter(
            JournalEntry.id == request.journal_entry_id,
            JournalEntry.tenant_id == request.tenant_id,
        )
        .first()
    )

    if not journal_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found for tenant")

    transaction.matched_journal_id = journal_entry.id
    transaction.status = "matched"
    db.commit()
    return {"transaction_id": transaction.id, "status": transaction.status, "matched_journal_id": transaction.matched_journal_id}



@app.get("/bank-transactions")
async def list_bank_transactions(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    transactions = db.query(BankStatementTransaction).filter(BankStatementTransaction.tenant_id == tenant_id).all()
    return {"transactions": transactions}


@app.get("/")
async def root():
    return {"service": "accounting", "version": "0.1.0"}
