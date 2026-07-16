"""create credit policy tables

Revision ID: 001_credit_policy
Revises: 
Create Date: 2024-12-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001_credit_policy'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create credit_policies table
    op.create_table(
        'credit_policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('product_id', UUID(as_uuid=True), index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('version', sa.String(20), default='1.0'),
        sa.Column('status', sa.String(20), default='DRAFT'),
        sa.Column('is_active', sa.Boolean, default=False),
        sa.Column('effective_from', sa.DateTime),
        sa.Column('effective_to', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True))
    )

    # Create risk_based_pricing table
    op.create_table(
        'risk_based_pricing',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('base_interest_rate', sa.Float, nullable=False),
        sa.Column('min_interest_rate', sa.Float, nullable=False),
        sa.Column('max_interest_rate', sa.Float, nullable=False),
        sa.Column('credit_score_weight', sa.Float, default=0.4),
        sa.Column('ltv_weight', sa.Float, default=0.3),
        sa.Column('dti_weight', sa.Float, default=0.2),
        sa.Column('other_factors_weight', sa.Float, default=0.1),
        sa.Column('processing_fee_range', JSON),
        sa.Column('risk_premium_range', JSON),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create score_based_rates table
    op.create_table(
        'score_based_rates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('min_score', sa.Integer, nullable=False),
        sa.Column('max_score', sa.Integer, nullable=False),
        sa.Column('pricing_tier', sa.String(20), nullable=False),
        sa.Column('base_rate', sa.Float, nullable=False),
        sa.Column('rate_adjustment', sa.Float, default=0.0),
        sa.Column('processing_fee_percent', sa.Float),
        sa.Column('risk_premium_percent', sa.Float),
        sa.Column('max_loan_amount', sa.Float),
        sa.Column('max_ltv_ratio', sa.Float),
        sa.Column('priority', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )

    # Create ltv_ratios table
    op.create_table(
        'ltv_ratios',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('collateral_type', sa.String(100), nullable=False),
        sa.Column('collateral_subtype', sa.String(100)),
        sa.Column('max_ltv_ratio', sa.Float, nullable=False),
        sa.Column('preferred_ltv_ratio', sa.Float),
        sa.Column('ltv_rate_adjustments', JSON),
        sa.Column('requires_insurance', sa.Boolean, default=False),
        sa.Column('requires_guarantor', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )

    # Create exposure_limits table
    op.create_table(
        'exposure_limits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('exposure_type', sa.String(20), nullable=False),
        sa.Column('exposure_name', sa.String(255), nullable=False),
        sa.Column('max_exposure_amount', sa.Float, nullable=False),
        sa.Column('max_exposure_percentage', sa.Float),
        sa.Column('max_single_obligor_amount', sa.Float),
        sa.Column('max_single_obligor_percentage', sa.Float),
        sa.Column('warning_threshold_percentage', sa.Float, default=80.0),
        sa.Column('current_exposure', sa.Float, default=0.0),
        sa.Column('last_calculated_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create concentration_limits table
    op.create_table(
        'concentration_limits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('parameter_name', sa.String(100), nullable=False),
        sa.Column('parameter_type', sa.String(50), nullable=False),
        sa.Column('max_concentration_percentage', sa.Float, nullable=False),
        sa.Column('target_concentration_percentage', sa.Float),
        sa.Column('calculation_criteria', JSON),
        sa.Column('current_concentration', sa.Float, default=0.0),
        sa.Column('breach_count', sa.Integer, default=0),
        sa.Column('last_breach_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create sectoral_caps table
    op.create_table(
        'sectoral_caps',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('sector_code', sa.String(50), nullable=False),
        sa.Column('sector_name', sa.String(255), nullable=False),
        sa.Column('subsector', sa.String(255)),
        sa.Column('max_sector_percentage', sa.Float, nullable=False),
        sa.Column('max_sector_amount', sa.Float),
        sa.Column('min_sector_percentage', sa.Float),
        sa.Column('is_priority_sector', sa.Boolean, default=False),
        sa.Column('priority_sector_category', sa.String(100)),
        sa.Column('current_allocation_percentage', sa.Float, default=0.0),
        sa.Column('current_allocation_amount', sa.Float, default=0.0),
        sa.Column('is_compliant', sa.Boolean, default=True),
        sa.Column('compliance_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create auto_approval_criteria table
    op.create_table(
        'auto_approval_criteria',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('min_credit_score', sa.Integer),
        sa.Column('credit_score_source', sa.String(50)),
        sa.Column('min_monthly_income', sa.Float),
        sa.Column('max_dti_ratio', sa.Float),
        sa.Column('allowed_employment_types', JSON),
        sa.Column('min_employment_months', sa.Integer),
        sa.Column('max_loan_amount', sa.Float),
        sa.Column('max_ltv_ratio', sa.Float),
        sa.Column('allowed_loan_purposes', JSON),
        sa.Column('max_active_loans', sa.Integer),
        sa.Column('max_dpd_days', sa.Integer),
        sa.Column('allow_restructured_accounts', sa.Boolean, default=False),
        sa.Column('allowed_residence_types', JSON),
        sa.Column('min_residence_months', sa.Integer),
        sa.Column('allowed_geographies', JSON),
        sa.Column('required_document_types', JSON),
        sa.Column('require_bank_statement_analysis', sa.Boolean, default=True),
        sa.Column('min_bank_statement_months', sa.Integer, default=6),
        sa.Column('require_dedupe_check', sa.Boolean, default=True),
        sa.Column('require_fraud_check', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create manual_review_triggers table
    op.create_table(
        'manual_review_triggers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('trigger_type', sa.String(50), nullable=False),
        sa.Column('trigger_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('condition_field', sa.String(100), nullable=False),
        sa.Column('condition_operator', sa.String(20), nullable=False),
        sa.Column('condition_value', JSON, nullable=False),
        sa.Column('review_level', sa.String(50)),
        sa.Column('priority', sa.String(20), default='NORMAL'),
        sa.Column('additional_checks', JSON),
        sa.Column('additional_documents', JSON),
        sa.Column('reviewer_instructions', sa.Text),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create decision_matrix table
    op.create_table(
        'decision_matrix',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('rule_name', sa.String(255), nullable=False),
        sa.Column('rule_priority', sa.Integer, default=0),
        sa.Column('credit_score_range', JSON),
        sa.Column('loan_amount_range', JSON),
        sa.Column('ltv_range', JSON),
        sa.Column('dti_range', JSON),
        sa.Column('employment_types', JSON),
        sa.Column('income_range', JSON),
        sa.Column('bureau_conditions', JSON),
        sa.Column('custom_conditions', JSON),
        sa.Column('decision_outcome', sa.String(20), nullable=False),
        sa.Column('decline_reason', sa.String(50)),
        sa.Column('decline_message', sa.Text),
        sa.Column('review_level', sa.String(50)),
        sa.Column('review_instructions', sa.Text),
        sa.Column('allow_counter_offer', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create counter_offer_rules table
    op.create_table(
        'counter_offer_rules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('policy_id', UUID(as_uuid=True), sa.ForeignKey('credit_policies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('rule_name', sa.String(255), nullable=False),
        sa.Column('rule_priority', sa.Integer, default=0),
        sa.Column('trigger_conditions', JSON, nullable=False),
        sa.Column('loan_amount_adjustment', JSON),
        sa.Column('interest_rate_adjustment', JSON),
        sa.Column('tenure_adjustment', JSON),
        sa.Column('require_guarantor', sa.Boolean, default=False),
        sa.Column('require_collateral', sa.Boolean, default=False),
        sa.Column('additional_documents', JSON),
        sa.Column('processing_fee_adjustment', JSON),
        sa.Column('counter_offer_message', sa.Text),
        sa.Column('terms_and_conditions', sa.Text),
        sa.Column('offer_validity_days', sa.Integer, default=7),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )

    # Create indexes
    op.create_index('idx_policies_tenant_active', 'credit_policies', ['tenant_id', 'is_active'])
    op.create_index('idx_policies_product', 'credit_policies', ['product_id'])
    op.create_index('idx_score_rates_policy', 'score_based_rates', ['policy_id'])
    op.create_index('idx_exposure_policy', 'exposure_limits', ['policy_id'])
    op.create_index('idx_triggers_policy', 'manual_review_triggers', ['policy_id'])
    op.create_index('idx_matrix_policy', 'decision_matrix', ['policy_id', 'rule_priority'])


def downgrade():
    # Drop tables in reverse order (handle foreign key constraints)
    op.drop_table('counter_offer_rules')
    op.drop_table('decision_matrix')
    op.drop_table('manual_review_triggers')
    op.drop_table('auto_approval_criteria')
    op.drop_table('sectoral_caps')
    op.drop_table('concentration_limits')
    op.drop_table('exposure_limits')
    op.drop_table('ltv_ratios')
    op.drop_table('score_based_rates')
    op.drop_table('risk_based_pricing')
    op.drop_table('credit_policies')
