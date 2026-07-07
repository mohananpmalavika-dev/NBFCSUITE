"""Add treasury and cash management module

Revision ID: 008
Revises: 007
Create Date: 2026-01-07

This migration adds support for complete Treasury & Cash Management:
- Treasury Bank Accounts Master
- Cash Position Tracking
- Bank Statements Import
- Bank Reconciliation
- Fund Transfer Management
- Liquidity Position Tracking
- Investment Portfolio Management
- Cash Flow Forecasting
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add treasury and cash management tables"""
    
    # 1. Treasury Bank Accounts Table
    op.create_table(
        'treasury_bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Bank Details
        sa.Column('bank_name', sa.String(length=200), nullable=False),
        sa.Column('branch_name', sa.String(length=200), nullable=True),
        sa.Column('ifsc_code', sa.String(length=20), nullable=True),
        sa.Column('swift_code', sa.String(length=20), nullable=True),
        
        # Account Details
        sa.Column('account_number', sa.String(length=50), nullable=False),
        sa.Column('account_name', sa.String(length=200), nullable=False),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        # Types: savings, current, cash_credit, overdraft, fixed_deposit
        sa.Column('account_purpose', sa.String(length=50), nullable=False),
        # Purpose: operational, disbursement, collection, payroll, tax, reserve, investment
        sa.Column('currency', sa.String(length=3), default='INR'),
        
        # Branch/Location
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        
        # Balance Tracking
        sa.Column('opening_balance', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('available_balance', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('last_updated_at', sa.DateTime(), nullable=True),
        
        # Limits and Controls
        sa.Column('minimum_balance', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maximum_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('daily_withdrawal_limit', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('monthly_withdrawal_limit', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # GL Integration
        sa.Column('gl_account_id', sa.Integer(), nullable=True),
        sa.Column('gl_account_code', sa.String(length=20), nullable=True),
        
        # Contact and Documentation
        sa.Column('contact_person', sa.String(length=200), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=200), nullable=True),
        sa.Column('documentation', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Status
        sa.Column('status', sa.String(length=50), default='active', nullable=False),
        # Status: active, inactive, dormant, closed, frozen
        sa.Column('opening_date', sa.Date(), nullable=True),
        sa.Column('closing_date', sa.Date(), nullable=True),
        
        # Audit Fields
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['gl_account_id'], ['chart_of_accounts.id'])
    )
    
    # Indexes for treasury_bank_accounts
    op.create_index('ix_tba_tenant_account', 'treasury_bank_accounts', ['tenant_id', 'account_number'], unique=True)
    op.create_index('ix_tba_tenant', 'treasury_bank_accounts', ['tenant_id'])
    op.create_index('ix_tba_status', 'treasury_bank_accounts', ['status'])
    op.create_index('ix_tba_branch', 'treasury_bank_accounts', ['branch_id'])
    op.create_index('ix_tba_account_number', 'treasury_bank_accounts', ['account_number'])
    
    # 2. Cash Position Table
    op.create_table(
        'cash_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Position Date and Location
        sa.Column('position_date', sa.Date(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        
        # Bank Account (if applicable)
        sa.Column('bank_account_id', sa.Integer(), nullable=True),
        
        # Cash Type
        sa.Column('is_physical_cash', sa.Boolean(), default=False),
        
        # Balances
        sa.Column('opening_balance', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('receipts', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('payments', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('closing_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        
        # Denomination Details (for physical cash)
        sa.Column('denomination_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Cash Movements
        sa.Column('cash_in_transit', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('cash_transfers_out', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('cash_transfers_in', sa.Numeric(precision=15, scale=2), default=0.00),
        
        # Reconciliation
        sa.Column('is_reconciled', sa.Boolean(), default=False),
        sa.Column('reconciled_by', sa.Integer(), nullable=True),
        sa.Column('reconciled_at', sa.DateTime(), nullable=True),
        
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['bank_account_id'], ['treasury_bank_accounts.id'])
    )
    
    # Indexes for cash_positions
    op.create_index('ix_cp_tenant_date', 'cash_positions', ['tenant_id', 'position_date'])
    op.create_index('ix_cp_tenant', 'cash_positions', ['tenant_id'])
    op.create_index('ix_cp_branch', 'cash_positions', ['branch_id'])
    op.create_index('ix_cp_bank_account', 'cash_positions', ['bank_account_id'])
    op.create_index('ix_cp_date', 'cash_positions', ['position_date'])
    
    # 3. Bank Statements Table
    op.create_table(
        'bank_statements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Bank Account
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        
        # Transaction Details
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('value_date', sa.Date(), nullable=True),
        sa.Column('transaction_reference', sa.String(length=100), nullable=True),
        
        # Transaction Description
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('cheque_number', sa.String(length=50), nullable=True),
        
        # Amounts
        sa.Column('debit_amount', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('credit_amount', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Import Details
        sa.Column('import_batch_id', sa.String(length=50), nullable=True),
        sa.Column('import_date', sa.DateTime(), default=sa.func.now()),
        sa.Column('imported_by', sa.Integer(), nullable=False),
        
        # Matching Status
        sa.Column('is_matched', sa.Boolean(), default=False),
        sa.Column('matched_gl_entry_id', sa.Integer(), nullable=True),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.Column('matched_by', sa.Integer(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['bank_account_id'], ['treasury_bank_accounts.id'])
    )
    
    # Indexes for bank_statements
    op.create_index('ix_bs_account_date', 'bank_statements', ['bank_account_id', 'transaction_date'])
    op.create_index('ix_bs_tenant', 'bank_statements', ['tenant_id'])
    op.create_index('ix_bs_reference', 'bank_statements', ['transaction_reference'])
    op.create_index('ix_bs_matched', 'bank_statements', ['is_matched'])
    op.create_index('ix_bs_date', 'bank_statements', ['transaction_date'])
    
    # 4. Bank Reconciliation Table
    op.create_table(
        'bank_reconciliations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Reconciliation Identification
        sa.Column('reconciliation_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('reconciliation_date', sa.Date(), nullable=False),
        
        # Bank Account
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        
        # Period
        sa.Column('period_start_date', sa.Date(), nullable=False),
        sa.Column('period_end_date', sa.Date(), nullable=False),
        
        # Balances
        sa.Column('book_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('bank_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('difference', sa.Numeric(precision=15, scale=2), nullable=False),
        
        # Matching Summary
        sa.Column('total_matched', sa.Integer(), default=0),
        sa.Column('total_unmatched', sa.Integer(), default=0),
        sa.Column('matched_amount', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('unmatched_amount', sa.Numeric(precision=15, scale=2), default=0.00),
        
        # Status
        sa.Column('status', sa.String(length=50), default='draft', nullable=False),
        # Status: draft, in_progress, matched, pending_approval, approved, rejected
        
        # Approval
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['bank_account_id'], ['treasury_bank_accounts.id'])
    )
    
    # Indexes for bank_reconciliations
    op.create_index('ix_br_tenant_date', 'bank_reconciliations', ['tenant_id', 'reconciliation_date'])
    op.create_index('ix_br_tenant', 'bank_reconciliations', ['tenant_id'])
    op.create_index('ix_br_account', 'bank_reconciliations', ['bank_account_id'])
    op.create_index('ix_br_status', 'bank_reconciliations', ['status'])
    op.create_index('ix_br_number', 'bank_reconciliations', ['reconciliation_number'])
    
    # 5. Reconciliation Items Table
    op.create_table(
        'reconciliation_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Reconciliation Link
        sa.Column('reconciliation_id', sa.Integer(), nullable=False),
        
        # Item Details
        sa.Column('item_type', sa.String(length=50), nullable=False),
        # Types: outstanding_cheque, deposit_in_transit, bank_charges, interest_earned, 
        #        direct_debit, direct_credit, error_correction, other
        sa.Column('item_date', sa.Date(), nullable=False),
        
        # Description
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        
        # Amount
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('is_debit', sa.Boolean(), default=True),
        
        # Matching
        sa.Column('bank_statement_id', sa.Integer(), nullable=True),
        sa.Column('gl_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_matched', sa.Boolean(), default=False),
        
        # Clearance
        sa.Column('is_cleared', sa.Boolean(), default=False),
        sa.Column('cleared_date', sa.Date(), nullable=True),
        
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['reconciliation_id'], ['bank_reconciliations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bank_statement_id'], ['bank_statements.id'])
    )
    
    # Indexes for reconciliation_items
    op.create_index('ix_ri_reconciliation', 'reconciliation_items', ['reconciliation_id'])
    op.create_index('ix_ri_tenant', 'reconciliation_items', ['tenant_id'])
    op.create_index('ix_ri_type', 'reconciliation_items', ['item_type'])
    op.create_index('ix_ri_cleared', 'reconciliation_items', ['is_cleared'])
    
    # 6. Fund Transfers Table
    op.create_table(
        'fund_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Transfer Identification
        sa.Column('transfer_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        
        # Transfer Type
        sa.Column('transfer_type', sa.String(length=50), nullable=False),
        # Types: internal, neft, rtgs, imps, upi, cheque, demand_draft
        
        # Source Account
        sa.Column('source_account_id', sa.Integer(), nullable=False),
        sa.Column('source_account_number', sa.String(length=50), nullable=True),
        
        # Destination Account
        sa.Column('destination_account_id', sa.Integer(), nullable=True),
        sa.Column('destination_account_number', sa.String(length=50), nullable=True),
        sa.Column('destination_bank_name', sa.String(length=200), nullable=True),
        sa.Column('destination_ifsc', sa.String(length=20), nullable=True),
        sa.Column('destination_account_holder', sa.String(length=200), nullable=True),
        
        # Amount
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), default='INR'),
        
        # Purpose and Reference
        sa.Column('purpose', sa.String(length=500), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        
        # Scheduling
        sa.Column('is_scheduled', sa.Boolean(), default=False),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        
        # Status Tracking
        sa.Column('status', sa.String(length=50), default='draft', nullable=False),
        # Status: draft, pending_approval, approved, rejected, scheduled, 
        #         in_progress, completed, failed, cancelled
        
        # Approval Workflow
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        
        # Rejection
        sa.Column('rejected_by', sa.Integer(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        
        # Execution
        sa.Column('executed_by', sa.Integer(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('transaction_reference', sa.String(length=100), nullable=True),
        
        # Failure Handling
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        
        # GL Integration
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_account_id'], ['treasury_bank_accounts.id']),
        sa.ForeignKeyConstraint(['destination_account_id'], ['treasury_bank_accounts.id']),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'])
    )
    
    # Indexes for fund_transfers
    op.create_index('ix_ft_tenant_date', 'fund_transfers', ['tenant_id', 'transfer_date'])
    op.create_index('ix_ft_tenant', 'fund_transfers', ['tenant_id'])
    op.create_index('ix_ft_status', 'fund_transfers', ['status'])
    op.create_index('ix_ft_source', 'fund_transfers', ['source_account_id'])
    op.create_index('ix_ft_scheduled', 'fund_transfers', ['is_scheduled', 'scheduled_date'])
    op.create_index('ix_ft_number', 'fund_transfers', ['transfer_number'])
    op.create_index('ix_ft_reference', 'fund_transfers', ['reference_number'])
    
    # 7. Liquidity Position Table
    op.create_table(
        'liquidity_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Position Date
        sa.Column('position_date', sa.Date(), nullable=False),
        
        # Total Positions
        sa.Column('total_cash', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('total_bank_balance', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('total_liquid_assets', sa.Numeric(precision=15, scale=2), default=0.00),
        
        # Maturity Bucket Analysis
        sa.Column('maturity_0_7_days', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maturity_8_14_days', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maturity_15_30_days', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maturity_1_3_months', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maturity_3_6_months', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maturity_6_12_months', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('maturity_above_12_months', sa.Numeric(precision=15, scale=2), default=0.00),
        
        # Liquidity Ratios
        sa.Column('current_ratio', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('quick_ratio', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('cash_ratio', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('liquidity_coverage_ratio', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('net_stable_funding_ratio', sa.Numeric(precision=10, scale=4), nullable=True),
        
        # Funding Gap
        sa.Column('funding_gap', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('cumulative_gap', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Limits and Alerts
        sa.Column('minimum_liquidity_required', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('liquidity_buffer', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_below_threshold', sa.Boolean(), default=False),
        
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for liquidity_positions
    op.create_index('ix_lp_tenant_date', 'liquidity_positions', ['tenant_id', 'position_date'], unique=True)
    op.create_index('ix_lp_tenant', 'liquidity_positions', ['tenant_id'])
    op.create_index('ix_lp_date', 'liquidity_positions', ['position_date'])
    
    # 8. Investments Table
    op.create_table(
        'investments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Investment Identification
        sa.Column('investment_number', sa.String(length=50), nullable=False, unique=True),
        
        # Investment Details
        sa.Column('investment_type', sa.String(length=50), nullable=False),
        # Types: fixed_deposit, government_securities, corporate_bonds, mutual_funds,
        #        commercial_paper, certificate_of_deposit, treasury_bills, equity, other
        sa.Column('investment_name', sa.String(length=200), nullable=False),
        sa.Column('issuer_name', sa.String(length=200), nullable=True),
        
        # Dates
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('maturity_date', sa.Date(), nullable=True),
        
        # Amounts
        sa.Column('face_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('current_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('maturity_value', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Returns
        sa.Column('interest_rate', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('interest_frequency', sa.String(length=20), nullable=True),
        sa.Column('total_interest_earned', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('total_dividends_earned', sa.Numeric(precision=15, scale=2), default=0.00),
        
        # Performance
        sa.Column('book_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('market_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('unrealized_gain_loss', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('realized_gain_loss', sa.Numeric(precision=15, scale=2), default=0.00),
        
        # Bank Account
        sa.Column('bank_account_id', sa.Integer(), nullable=True),
        
        # Status
        sa.Column('status', sa.String(length=50), default='active', nullable=False),
        # Status: active, matured, sold, cancelled
        
        # Documentation
        sa.Column('certificate_number', sa.String(length=100), nullable=True),
        sa.Column('documentation', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Approval
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['bank_account_id'], ['treasury_bank_accounts.id'])
    )
    
    # Indexes for investments
    op.create_index('ix_inv_tenant_type', 'investments', ['tenant_id', 'investment_type'])
    op.create_index('ix_inv_tenant', 'investments', ['tenant_id'])
    op.create_index('ix_inv_status', 'investments', ['status'])
    op.create_index('ix_inv_maturity', 'investments', ['maturity_date'])
    op.create_index('ix_inv_number', 'investments', ['investment_number'])
    
    # 9. Investment Transactions Table
    op.create_table(
        'investment_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Investment Link
        sa.Column('investment_id', sa.Integer(), nullable=False),
        
        # Transaction Details
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        # Types: purchase, sale, interest_income, dividend_income, mtm_adjustment, maturity
        
        # Amount
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('units', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('price_per_unit', sa.Numeric(precision=15, scale=4), nullable=True),
        
        # Description
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        
        # GL Integration
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['investment_id'], ['investments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id'])
    )
    
    # Indexes for investment_transactions
    op.create_index('ix_it_investment', 'investment_transactions', ['investment_id'])
    op.create_index('ix_it_tenant', 'investment_transactions', ['tenant_id'])
    op.create_index('ix_it_type', 'investment_transactions', ['transaction_type'])
    op.create_index('ix_it_date', 'investment_transactions', ['transaction_date'])
    
    # 10. Cash Flow Forecasts Table
    op.create_table(
        'cash_flow_forecasts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        
        # Forecast Identification
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('forecast_period', sa.String(length=20), nullable=False),
        sa.Column('period_start_date', sa.Date(), nullable=False),
        sa.Column('period_end_date', sa.Date(), nullable=False),
        
        # Opening and Closing
        sa.Column('opening_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('closing_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        
        # Expected Inflows
        sa.Column('expected_loan_repayments', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_deposit_collections', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_fee_income', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_investment_income', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_other_income', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('total_expected_inflows', sa.Numeric(precision=15, scale=2), nullable=False),
        
        # Expected Outflows
        sa.Column('expected_loan_disbursements', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_deposit_withdrawals', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_operating_expenses', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_interest_payments', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_tax_payments', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('expected_other_expenses', sa.Numeric(precision=15, scale=2), default=0.00),
        sa.Column('total_expected_outflows', sa.Numeric(precision=15, scale=2), nullable=False),
        
        # Net Cash Flow
        sa.Column('net_cash_flow', sa.Numeric(precision=15, scale=2), nullable=False),
        
        # Variance (Actual vs Forecast)
        sa.Column('actual_inflows', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('actual_outflows', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('actual_net_cash_flow', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('variance_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('variance_percentage', sa.Numeric(precision=10, scale=2), nullable=True),
        
        # Scenario
        sa.Column('scenario', sa.String(length=50), default='expected'),
        sa.Column('confidence_level', sa.Numeric(precision=5, scale=2), nullable=True),
        
        # Notes
        sa.Column('assumptions', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for cash_flow_forecasts
    op.create_index('ix_cff_tenant_date', 'cash_flow_forecasts', ['tenant_id', 'forecast_date'])
    op.create_index('ix_cff_tenant', 'cash_flow_forecasts', ['tenant_id'])
    op.create_index('ix_cff_period', 'cash_flow_forecasts', ['period_start_date', 'period_end_date'])
    op.create_index('ix_cff_scenario', 'cash_flow_forecasts', ['scenario'])


def downgrade() -> None:
    """Remove treasury and cash management tables"""
    
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('cash_flow_forecasts')
    op.drop_table('investment_transactions')
    op.drop_table('investments')
    op.drop_table('liquidity_positions')
    op.drop_table('fund_transfers')
    op.drop_table('reconciliation_items')
    op.drop_table('bank_reconciliations')
    op.drop_table('bank_statements')
    op.drop_table('cash_positions')
    op.drop_table('treasury_bank_accounts')
