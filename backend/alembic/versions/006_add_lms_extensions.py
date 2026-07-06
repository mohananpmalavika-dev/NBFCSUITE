"""add lms extension tables

Revision ID: 006
Revises: 005
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Add LMS extension tables: NACH, Restructuring, and Insurance"""
    
    # ============================================
    # NACH MANDATE MANAGEMENT TABLES
    # ============================================
    
    # NACH Mandates Table
    op.create_table(
        'nach_mandates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('loan_account_id', sa.Integer(), nullable=False),
        sa.Column('mandate_number', sa.String(50), nullable=False),
        sa.Column('mandate_type', sa.String(20), nullable=False),
        sa.Column('bank_account_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('frequency', sa.String(20), nullable=False),
        sa.Column('max_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        
        # Physical NACH fields
        sa.Column('physical_form_received', sa.Boolean(), default=False),
        sa.Column('physical_form_number', sa.String(50)),
        
        # eNACH fields
        sa.Column('enach_request_id', sa.String(100)),
        sa.Column('enach_authentication_url', sa.String(500)),
        sa.Column('enach_authenticated_at', sa.DateTime(timezone=True)),
        
        # Bank details
        sa.Column('umrn', sa.String(50)),
        sa.Column('sponsor_bank_code', sa.String(20)),
        sa.Column('utility_code', sa.String(50)),
        sa.Column('category_code', sa.String(20)),
        sa.Column('debit_type', sa.String(20)),
        
        # Status tracking
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('approved_by', sa.Integer()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('cancellation_reason', sa.Text()),
        sa.Column('suspension_reason', sa.Text()),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id']),
        sa.UniqueConstraint('mandate_number'),
        sa.UniqueConstraint('umrn')
    )
    op.create_index('idx_nach_mandate_tenant_loan', 'nach_mandates', ['tenant_id', 'loan_account_id'])
    op.create_index('idx_nach_mandate_status', 'nach_mandates', ['tenant_id', 'status'])
    op.create_index('idx_nach_mandate_expiry', 'nach_mandates', ['tenant_id', 'end_date', 'status'])

    
    # NACH Debit Transactions Table
    op.create_table(
        'nach_debit_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('mandate_id', sa.Integer(), nullable=False),
        sa.Column('loan_account_id', sa.Integer(), nullable=False),
        sa.Column('repayment_schedule_id', sa.Integer(), nullable=False),
        sa.Column('transaction_reference', sa.String(100), nullable=False),
        sa.Column('debit_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('debit_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), default='initiated'),
        sa.Column('purpose', sa.String(200)),
        
        # Bank response fields
        sa.Column('bank_reference', sa.String(100)),
        sa.Column('utr_number', sa.String(50)),
        sa.Column('processed_date', sa.Date()),
        
        # Failure handling
        sa.Column('failure_reason', sa.String(100)),
        sa.Column('failure_remarks', sa.Text()),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('max_retry_attempts', sa.Integer(), default=3),
        sa.Column('next_retry_date', sa.Date()),
        
        # NPCI fields
        sa.Column('npci_transaction_id', sa.String(100)),
        sa.Column('settlement_date', sa.Date()),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('initiated_by', sa.Integer(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['mandate_id'], ['nach_mandates.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id']),
        sa.ForeignKeyConstraint(['repayment_schedule_id'], ['repayment_schedules.id']),
        sa.UniqueConstraint('transaction_reference')
    )
    op.create_index('idx_nach_debit_tenant_mandate', 'nach_debit_transactions', ['tenant_id', 'mandate_id'])
    op.create_index('idx_nach_debit_loan', 'nach_debit_transactions', ['tenant_id', 'loan_account_id'])
    op.create_index('idx_nach_debit_status', 'nach_debit_transactions', ['tenant_id', 'status'])
    op.create_index('idx_nach_debit_date', 'nach_debit_transactions', ['tenant_id', 'debit_date'])
    op.create_index('idx_nach_debit_retry', 'nach_debit_transactions', ['tenant_id', 'next_retry_date', 'status'])

    
    # ============================================
    # LOAN RESTRUCTURING TABLES
    # ============================================
    
    # Loan Restructurings Table
    op.create_table(
        'loan_restructurings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('loan_account_id', sa.Integer(), nullable=False),
        sa.Column('restructuring_number', sa.String(50), nullable=False),
        sa.Column('restructuring_type', sa.String(50), nullable=False),
        sa.Column('reason', sa.String(50), nullable=False),
        sa.Column('reason_details', sa.Text(), nullable=False),
        sa.Column('status', sa.String(50), default='draft'),
        
        # Current loan details
        sa.Column('current_emi', sa.Numeric(15, 2), nullable=False),
        sa.Column('current_outstanding', sa.Numeric(15, 2), nullable=False),
        sa.Column('current_tenure_remaining', sa.Integer(), nullable=False),
        
        # Proposed parameters
        sa.Column('proposed_emi', sa.Numeric(15, 2)),
        sa.Column('proposed_tenure', sa.Integer()),
        sa.Column('proposed_interest_rate', sa.Numeric(5, 2)),
        sa.Column('moratorium_months', sa.Integer()),
        
        # Approved parameters
        sa.Column('approved_emi', sa.Numeric(15, 2)),
        sa.Column('approved_tenure', sa.Integer()),
        sa.Column('approved_interest_rate', sa.Numeric(5, 2)),
        sa.Column('approved_moratorium_months', sa.Integer()),
        
        # Implemented parameters
        sa.Column('final_emi', sa.Numeric(15, 2)),
        sa.Column('final_tenure', sa.Integer()),
        sa.Column('final_interest_rate', sa.Numeric(5, 2)),
        sa.Column('final_outstanding', sa.Numeric(15, 2)),
        
        # Financial details
        sa.Column('customer_income', sa.Numeric(15, 2)),
        sa.Column('customer_obligations', sa.Numeric(15, 2)),
        sa.Column('waiver_amount', sa.Numeric(15, 2)),
        sa.Column('waiver_type', sa.String(50)),
        sa.Column('estimated_loss', sa.Numeric(15, 2)),
        sa.Column('recovery_probability', sa.Numeric(5, 2)),
        
        # Supporting information
        sa.Column('supporting_documents', postgresql.JSONB()),
        
        # Approval details
        sa.Column('approval_remarks', sa.Text()),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('approved_by', sa.Integer()),
        sa.Column('credit_committee_approval', sa.Boolean(), default=False),
        sa.Column('risk_assessment', sa.Text()),
        
        # Rejection details
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('rejected_at', sa.DateTime(timezone=True)),
        sa.Column('rejected_by', sa.Integer()),
        sa.Column('alternative_suggestions', sa.Text()),
        sa.Column('can_reapply', sa.Boolean(), default=True),
        sa.Column('reapply_after_days', sa.Integer()),
        
        # Implementation details
        sa.Column('implementation_date', sa.Date()),
        sa.Column('first_emi_date', sa.Date()),
        sa.Column('moratorium_start_date', sa.Date()),
        sa.Column('moratorium_end_date', sa.Date()),
        sa.Column('implemented_at', sa.DateTime(timezone=True)),
        sa.Column('implemented_by', sa.Integer()),
        sa.Column('implementation_remarks', sa.Text()),
        
        # Customer contact
        sa.Column('customer_mobile', sa.String(15)),
        sa.Column('customer_email', sa.String(100)),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id']),
        sa.UniqueConstraint('restructuring_number')
    )
    op.create_index('idx_restructuring_tenant_loan', 'loan_restructurings', ['tenant_id', 'loan_account_id'])
    op.create_index('idx_restructuring_status', 'loan_restructurings', ['tenant_id', 'status'])
    op.create_index('idx_restructuring_type', 'loan_restructurings', ['tenant_id', 'restructuring_type'])

    
    # ============================================
    # LOAN INSURANCE TRACKING TABLES
    # ============================================
    
    # Loan Insurance Policies Table
    op.create_table(
        'loan_insurance_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('loan_account_id', sa.Integer(), nullable=False),
        sa.Column('insurance_type', sa.String(50), nullable=False),
        sa.Column('insurance_provider', sa.String(100), nullable=False),
        sa.Column('policy_number', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='active'),
        
        # Coverage details
        sa.Column('sum_assured', sa.Numeric(15, 2), nullable=False),
        sa.Column('premium_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('premium_frequency', sa.String(20), nullable=False),
        
        # Policy period
        sa.Column('policy_start_date', sa.Date(), nullable=False),
        sa.Column('policy_end_date', sa.Date(), nullable=False),
        
        # Beneficiary details
        sa.Column('nominee_name', sa.String(100)),
        sa.Column('nominee_relationship', sa.String(50)),
        sa.Column('nominee_contact', sa.String(15)),
        
        # Policy terms
        sa.Column('is_mandatory', sa.Boolean(), default=False),
        sa.Column('is_bundled', sa.Boolean(), default=False),
        sa.Column('cover_percentage', sa.Numeric(5, 2)),
        
        # Renewal tracking
        sa.Column('last_renewal_date', sa.Date()),
        sa.Column('next_renewal_date', sa.Date()),
        sa.Column('renewal_reminder_sent', sa.Boolean(), default=False),
        sa.Column('renewal_reminder_sent_at', sa.DateTime(timezone=True)),
        
        # Cancellation
        sa.Column('cancelled_at', sa.DateTime(timezone=True)),
        sa.Column('cancellation_reason', sa.Text()),
        
        # Additional details
        sa.Column('policy_document_url', sa.String(500)),
        sa.Column('agent_name', sa.String(100)),
        sa.Column('agent_contact', sa.String(15)),
        sa.Column('remarks', sa.Text()),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id']),
        sa.UniqueConstraint('policy_number')
    )
    op.create_index('idx_insurance_tenant_loan', 'loan_insurance_policies', ['tenant_id', 'loan_account_id'])
    op.create_index('idx_insurance_status', 'loan_insurance_policies', ['tenant_id', 'status'])
    op.create_index('idx_insurance_expiry', 'loan_insurance_policies', ['tenant_id', 'policy_end_date', 'status'])
    op.create_index('idx_insurance_type', 'loan_insurance_policies', ['tenant_id', 'insurance_type'])

    
    # Insurance Premium Payments Table
    op.create_table(
        'insurance_premium_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('insurance_policy_id', sa.Integer(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('premium_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_frequency', sa.String(20), nullable=False),
        sa.Column('payment_status', sa.String(50), default='pending'),
        
        # Payment details
        sa.Column('payment_date', sa.Date()),
        sa.Column('amount_paid', sa.Numeric(15, 2)),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('transaction_reference', sa.String(100)),
        sa.Column('receipt_url', sa.String(500)),
        
        # Overdue tracking
        sa.Column('is_overdue', sa.Boolean(), default=False),
        sa.Column('overdue_days', sa.Integer()),
        
        # Waiver
        sa.Column('is_waived', sa.Boolean(), default=False),
        sa.Column('waiver_reason', sa.Text()),
        sa.Column('waived_amount', sa.Numeric(15, 2)),
        
        sa.Column('remarks', sa.Text()),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['insurance_policy_id'], ['loan_insurance_policies.id'])
    )
    op.create_index('idx_premium_tenant_policy', 'insurance_premium_payments', ['tenant_id', 'insurance_policy_id'])
    op.create_index('idx_premium_status', 'insurance_premium_payments', ['tenant_id', 'payment_status'])
    op.create_index('idx_premium_due_date', 'insurance_premium_payments', ['tenant_id', 'due_date', 'payment_status'])
    op.create_index('idx_premium_overdue', 'insurance_premium_payments', ['tenant_id', 'is_overdue'])

    
    # Insurance Claims Table
    op.create_table(
        'insurance_claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('insurance_policy_id', sa.Integer(), nullable=False),
        sa.Column('loan_account_id', sa.Integer(), nullable=False),
        sa.Column('claim_number', sa.String(50), nullable=False),
        sa.Column('claim_type', sa.String(50), nullable=False),
        sa.Column('claim_status', sa.String(50), default='draft'),
        
        # Claim details
        sa.Column('claim_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('incident_date', sa.Date(), nullable=False),
        sa.Column('incident_description', sa.Text(), nullable=False),
        sa.Column('incident_location', sa.String(200)),
        
        # Supporting documents
        sa.Column('supporting_documents', postgresql.JSONB()),
        sa.Column('police_report_number', sa.String(50)),
        sa.Column('medical_report_reference', sa.String(100)),
        
        # Claimant details
        sa.Column('claimant_name', sa.String(100), nullable=False),
        sa.Column('claimant_relationship', sa.String(50), nullable=False),
        sa.Column('claimant_contact', sa.String(15), nullable=False),
        sa.Column('claimant_address', sa.Text()),
        
        # Review details
        sa.Column('approved_amount', sa.Numeric(15, 2)),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('review_remarks', sa.Text()),
        sa.Column('surveyor_name', sa.String(200)),
        sa.Column('surveyor_report_url', sa.String(500)),
        
        # Payment details
        sa.Column('payment_date', sa.Date()),
        sa.Column('amount_paid', sa.Numeric(15, 2)),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('payee_name', sa.String(200)),
        sa.Column('bank_name', sa.String(100)),
        
        # Workflow tracking
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
        sa.Column('reviewed_at', sa.DateTime(timezone=True)),
        sa.Column('reviewed_by', sa.Integer()),
        sa.Column('paid_at', sa.DateTime(timezone=True)),
        
        sa.Column('remarks', sa.Text()),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['insurance_policy_id'], ['loan_insurance_policies.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id']),
        sa.UniqueConstraint('claim_number')
    )
    op.create_index('idx_claim_tenant_policy', 'insurance_claims', ['tenant_id', 'insurance_policy_id'])
    op.create_index('idx_claim_tenant_loan', 'insurance_claims', ['tenant_id', 'loan_account_id'])
    op.create_index('idx_claim_status', 'insurance_claims', ['tenant_id', 'claim_status'])
    op.create_index('idx_claim_type', 'insurance_claims', ['tenant_id', 'claim_type'])


def downgrade():
    """Drop LMS extension tables"""
    
    # Drop Insurance Tables
    op.drop_table('insurance_claims')
    op.drop_table('insurance_premium_payments')
    op.drop_table('loan_insurance_policies')
    
    # Drop Restructuring Tables
    op.drop_table('loan_restructurings')
    
    # Drop NACH Tables
    op.drop_table('nach_debit_transactions')
    op.drop_table('nach_mandates')
