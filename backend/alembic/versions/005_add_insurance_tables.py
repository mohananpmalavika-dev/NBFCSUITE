"""Add insurance and bancassurance tables

Revision ID: 005
Revises: 004
Create Date: 2026-01-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Insurance Agents Table
    op.create_table(
        'insurance_agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('agent_code', sa.String(50), nullable=False),
        sa.Column('agent_name', sa.String(200), nullable=False),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('mobile', sa.String(20)),
        sa.Column('address_line1', sa.String(200)),
        sa.Column('address_line2', sa.String(200)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(100)),
        sa.Column('pincode', sa.String(10)),
        sa.Column('license_number', sa.String(100)),
        sa.Column('license_valid_from', sa.DateTime(timezone=True)),
        sa.Column('license_valid_till', sa.DateTime(timezone=True)),
        sa.Column('certifications', postgresql.JSONB),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('branch_name', sa.String(200)),
        sa.Column('team_id', postgresql.UUID(as_uuid=True)),
        sa.Column('team_name', sa.String(200)),
        sa.Column('reporting_manager_id', postgresql.UUID(as_uuid=True)),
        sa.Column('commission_structure', postgresql.JSONB),
        sa.Column('default_commission_rate', sa.Numeric(5, 2)),
        sa.Column('bank_name', sa.String(200)),
        sa.Column('account_number', sa.String(50)),
        sa.Column('ifsc_code', sa.String(20)),
        sa.Column('account_holder_name', sa.String(200)),
        sa.Column('pan_number', sa.String(20)),
        sa.Column('gst_number', sa.String(20)),
        sa.Column('tds_applicable', sa.Boolean(), default=True),
        sa.Column('total_policies_sold', sa.Integer(), default=0),
        sa.Column('total_premium_collected', sa.Numeric(15, 2), default=0),
        sa.Column('total_commission_earned', sa.Numeric(15, 2), default=0),
        sa.Column('active_policies_count', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('joining_date', sa.DateTime(timezone=True)),
        sa.Column('exit_date', sa.DateTime(timezone=True)),
        sa.Column('remarks', sa.Text()),
        sa.Column('additional_data', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'agent_code', name='uq_agent_code')
    )
    op.create_index('ix_insurance_agents_tenant_id', 'insurance_agents', ['tenant_id'])
    op.create_index('idx_agent_type', 'insurance_agents', ['tenant_id', 'agent_type'])
    op.create_index('idx_agent_branch', 'insurance_agents', ['tenant_id', 'branch_id'])
    op.create_index('idx_agent_status', 'insurance_agents', ['tenant_id', 'is_active'])
    
    # Insurance Policies Table
    op.create_table(
        'insurance_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('policy_number', sa.String(50), nullable=False),
        sa.Column('policy_type', sa.String(20), nullable=False),
        sa.Column('policy_status', sa.String(20), nullable=False, default='draft'),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('insured_name', sa.String(200), nullable=False),
        sa.Column('insured_dob', sa.DateTime(timezone=True), nullable=False),
        sa.Column('insured_age', sa.Integer(), nullable=False),
        sa.Column('insured_gender', sa.String(20)),
        sa.Column('insurance_company', sa.String(200), nullable=False),
        sa.Column('insurance_company_code', sa.String(50)),
        sa.Column('product_name', sa.String(200), nullable=False),
        sa.Column('product_code', sa.String(50)),
        sa.Column('sum_assured', sa.Numeric(15, 2), nullable=False),
        sa.Column('policy_term_years', sa.Integer(), nullable=False),
        sa.Column('premium_paying_term_years', sa.Integer(), nullable=False),
        sa.Column('premium_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('premium_frequency', sa.String(20), nullable=False),
        sa.Column('premium_mode', sa.String(50)),
        sa.Column('policy_start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('policy_end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('first_premium_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('next_premium_due_date', sa.DateTime(timezone=True)),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True)),
        sa.Column('agent_name', sa.String(200)),
        sa.Column('agent_code', sa.String(50)),
        sa.Column('channel', sa.String(50), nullable=False, default='bancassurance'),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('branch_name', sa.String(200)),
        sa.Column('nominee_name', sa.String(200)),
        sa.Column('nominee_relationship', sa.String(100)),
        sa.Column('nominee_dob', sa.DateTime(timezone=True)),
        sa.Column('nominee_percentage', sa.Numeric(5, 2), default=100.00),
        sa.Column('total_premium_paid', sa.Numeric(15, 2), nullable=False, default=0),
        sa.Column('total_premium_due', sa.Numeric(15, 2), nullable=False, default=0),
        sa.Column('outstanding_premium', sa.Numeric(15, 2), nullable=False, default=0),
        sa.Column('premiums_paid_count', sa.Integer(), nullable=False, default=0),
        sa.Column('premiums_due_count', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_lapsed', sa.Boolean(), default=False, nullable=False),
        sa.Column('lapsed_date', sa.DateTime(timezone=True)),
        sa.Column('grace_period_days', sa.Integer(), default=30),
        sa.Column('documents', postgresql.JSONB),
        sa.Column('remarks', sa.Text()),
        sa.Column('policy_conditions', sa.Text()),
        sa.Column('surrender_value', sa.Numeric(15, 2)),
        sa.Column('maturity_value', sa.Numeric(15, 2)),
        sa.Column('maturity_date', sa.DateTime(timezone=True)),
        sa.Column('medical_examination_required', sa.Boolean(), default=False),
        sa.Column('medical_examination_status', sa.String(50)),
        sa.Column('rider_details', postgresql.JSONB),
        sa.Column('additional_data', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'policy_number', name='uq_policy_number')
    )
    op.create_index('ix_insurance_policies_tenant_id', 'insurance_policies', ['tenant_id'])
    op.create_index('ix_insurance_policies_policy_number', 'insurance_policies', ['policy_number'])
    op.create_index('idx_insurance_customer', 'insurance_policies', ['tenant_id', 'customer_id'])
    op.create_index('idx_insurance_agent', 'insurance_policies', ['tenant_id', 'agent_id'])
    op.create_index('idx_insurance_status', 'insurance_policies', ['tenant_id', 'policy_status', 'is_active'])
    op.create_index('idx_insurance_dates', 'insurance_policies', ['tenant_id', 'policy_start_date', 'policy_end_date'])
    op.create_index('idx_insurance_company', 'insurance_policies', ['tenant_id', 'insurance_company'])
    
    # Insurance Premiums Table
    op.create_table(
        'insurance_premiums',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_number', sa.String(50), nullable=False),
        sa.Column('premium_number', sa.String(50), nullable=False),
        sa.Column('premium_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('premium_due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('premium_frequency', sa.String(20), nullable=False),
        sa.Column('installment_number', sa.Integer(), nullable=False),
        sa.Column('premium_status', sa.String(20), nullable=False, default='due'),
        sa.Column('payment_date', sa.DateTime(timezone=True)),
        sa.Column('payment_amount', sa.Numeric(12, 2)),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('transaction_id', sa.String(100)),
        sa.Column('receipt_number', sa.String(50)),
        sa.Column('grace_period_end_date', sa.DateTime(timezone=True)),
        sa.Column('late_fee', sa.Numeric(10, 2), default=0),
        sa.Column('late_days', sa.Integer(), default=0),
        sa.Column('discount_amount', sa.Numeric(10, 2), default=0),
        sa.Column('discount_reason', sa.String(200)),
        sa.Column('waived_amount', sa.Numeric(10, 2), default=0),
        sa.Column('waived_reason', sa.String(200)),
        sa.Column('collected_by', postgresql.UUID(as_uuid=True)),
        sa.Column('collected_by_name', sa.String(200)),
        sa.Column('collection_branch', sa.String(200)),
        sa.Column('remarks', sa.Text()),
        sa.Column('additional_data', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id']),
        sa.UniqueConstraint('tenant_id', 'premium_number', name='uq_premium_number')
    )
    op.create_index('ix_insurance_premiums_tenant_id', 'insurance_premiums', ['tenant_id'])
    op.create_index('ix_insurance_premiums_premium_number', 'insurance_premiums', ['premium_number'])
    op.create_index('idx_premium_policy', 'insurance_premiums', ['tenant_id', 'policy_id'])
    op.create_index('idx_premium_status', 'insurance_premiums', ['tenant_id', 'premium_status'])
    op.create_index('idx_premium_due_date', 'insurance_premiums', ['tenant_id', 'premium_due_date'])
    op.create_index('idx_premium_payment_date', 'insurance_premiums', ['tenant_id', 'payment_date'])
    
    # Insurance Claims Table
    op.create_table(
        'insurance_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_number', sa.String(50), nullable=False),
        sa.Column('claim_number', sa.String(50), nullable=False),
        sa.Column('claim_type', sa.String(20), nullable=False),
        sa.Column('claim_status', sa.String(30), nullable=False, default='registered'),
        sa.Column('claim_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('claimed_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('incident_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('incident_description', sa.Text(), nullable=False),
        sa.Column('incident_location', sa.String(500)),
        sa.Column('claimant_name', sa.String(200), nullable=False),
        sa.Column('claimant_relationship', sa.String(100), nullable=False),
        sa.Column('claimant_contact', sa.String(20)),
        sa.Column('claimant_address', sa.Text()),
        sa.Column('assessed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('assessed_by_name', sa.String(200)),
        sa.Column('assessment_date', sa.DateTime(timezone=True)),
        sa.Column('assessed_amount', sa.Numeric(15, 2)),
        sa.Column('assessment_remarks', sa.Text()),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_by_name', sa.String(200)),
        sa.Column('approval_date', sa.DateTime(timezone=True)),
        sa.Column('approved_amount', sa.Numeric(15, 2)),
        sa.Column('approval_remarks', sa.Text()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('rejection_date', sa.DateTime(timezone=True)),
        sa.Column('settlement_date', sa.DateTime(timezone=True)),
        sa.Column('settlement_amount', sa.Numeric(15, 2)),
        sa.Column('settlement_method', sa.String(50)),
        sa.Column('settlement_reference', sa.String(100)),
        sa.Column('settlement_remarks', sa.Text()),
        sa.Column('documents_submitted', postgresql.JSONB),
        sa.Column('documents_verified', sa.Boolean(), default=False),
        sa.Column('documents_verification_date', sa.DateTime(timezone=True)),
        sa.Column('investigation_required', sa.Boolean(), default=False),
        sa.Column('investigation_status', sa.String(50)),
        sa.Column('investigation_remarks', sa.Text()),
        sa.Column('deductions', sa.Numeric(15, 2), default=0),
        sa.Column('deduction_details', postgresql.JSONB),
        sa.Column('net_payable', sa.Numeric(15, 2)),
        sa.Column('target_settlement_date', sa.DateTime(timezone=True)),
        sa.Column('processing_days', sa.Integer()),
        sa.Column('remarks', sa.Text()),
        sa.Column('additional_data', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id']),
        sa.UniqueConstraint('tenant_id', 'claim_number', name='uq_claim_number')
    )
    op.create_index('ix_insurance_claims_tenant_id', 'insurance_claims', ['tenant_id'])
    op.create_index('ix_insurance_claims_claim_number', 'insurance_claims', ['claim_number'])
    op.create_index('idx_claim_policy', 'insurance_claims', ['tenant_id', 'policy_id'])
    op.create_index('idx_claim_status', 'insurance_claims', ['tenant_id', 'claim_status'])
    op.create_index('idx_claim_type', 'insurance_claims', ['tenant_id', 'claim_type'])
    op.create_index('idx_claim_dates', 'insurance_claims', ['tenant_id', 'claimed_date'])
    
    # Insurance Commissions Table
    op.create_table(
        'insurance_commissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('policy_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('policy_number', sa.String(50), nullable=False),
        sa.Column('commission_number', sa.String(50), nullable=False),
        sa.Column('commission_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_name', sa.String(200), nullable=False),
        sa.Column('agent_code', sa.String(50)),
        sa.Column('agent_type', sa.String(50)),
        sa.Column('commission_type', sa.String(50), nullable=False),
        sa.Column('base_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('commission_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('commission_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('commission_period', sa.String(50)),
        sa.Column('calculation_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True)),
        sa.Column('premium_id', postgresql.UUID(as_uuid=True)),
        sa.Column('premium_number', sa.String(50)),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_by_name', sa.String(200)),
        sa.Column('approval_date', sa.DateTime(timezone=True)),
        sa.Column('payment_date', sa.DateTime(timezone=True)),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('paid_amount', sa.Numeric(12, 2)),
        sa.Column('tds_amount', sa.Numeric(12, 2), default=0),
        sa.Column('tds_percentage', sa.Numeric(5, 2), default=0),
        sa.Column('other_deductions', sa.Numeric(12, 2), default=0),
        sa.Column('deduction_details', postgresql.JSONB),
        sa.Column('net_payable', sa.Numeric(12, 2)),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('branch_name', sa.String(200)),
        sa.Column('team_id', postgresql.UUID(as_uuid=True)),
        sa.Column('team_name', sa.String(200)),
        sa.Column('target_achievement_percentage', sa.Numeric(5, 2)),
        sa.Column('bonus_amount', sa.Numeric(12, 2), default=0),
        sa.Column('penalty_amount', sa.Numeric(12, 2), default=0),
        sa.Column('is_clawback', sa.Boolean(), default=False),
        sa.Column('clawback_reason', sa.String(200)),
        sa.Column('clawback_amount', sa.Numeric(12, 2)),
        sa.Column('remarks', sa.Text()),
        sa.Column('additional_data', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id']),
        sa.ForeignKeyConstraint(['agent_id'], ['insurance_agents.id']),
        sa.UniqueConstraint('tenant_id', 'commission_number', name='uq_commission_number')
    )
    op.create_index('ix_insurance_commissions_tenant_id', 'insurance_commissions', ['tenant_id'])
    op.create_index('ix_insurance_commissions_commission_number', 'insurance_commissions', ['commission_number'])
    op.create_index('idx_commission_policy', 'insurance_commissions', ['tenant_id', 'policy_id'])
    op.create_index('idx_commission_agent', 'insurance_commissions', ['tenant_id', 'agent_id'])
    op.create_index('idx_commission_status', 'insurance_commissions', ['tenant_id', 'commission_status'])
    op.create_index('idx_commission_dates', 'insurance_commissions', ['tenant_id', 'calculation_date'])
    op.create_index('idx_commission_payment', 'insurance_commissions', ['tenant_id', 'payment_date'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('insurance_commissions')
    op.drop_table('insurance_claims')
    op.drop_table('insurance_premiums')
    op.drop_table('insurance_policies')
    op.drop_table('insurance_agents')
