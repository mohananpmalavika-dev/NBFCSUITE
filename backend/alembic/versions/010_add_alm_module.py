"""add alm module

Revision ID: 010_add_alm_module
Revises: 009_add_accounting_extended_features
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_add_alm_module'
down_revision = '009_add_accounting_extended_features'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    maturity_bucket_enum = postgresql.ENUM(
        'upto_1_day', 'upto_7_days', 'upto_14_days', 'upto_1_month',
        'upto_2_months', 'upto_3_months', 'upto_6_months', 'upto_1_year',
        'upto_2_years', 'upto_3_years', 'upto_5_years', 'above_5_years',
        name='maturitybucket'
    )
    maturity_bucket_enum.create(op.get_bind(), checkfirst=True)
    
    gap_type_enum = postgresql.ENUM(
        'liquidity_gap', 'interest_rate_gap', 'maturity_gap', 'duration_gap',
        name='gaptype'
    )
    gap_type_enum.create(op.get_bind(), checkfirst=True)
    
    risk_level_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='risklevel'
    )
    risk_level_enum.create(op.get_bind(), checkfirst=True)
    
    interest_rate_scenario_enum = postgresql.ENUM(
        'base', 'parallel_up_100', 'parallel_down_100',
        'parallel_up_200', 'parallel_down_200', 'steepening', 'flattening',
        name='interestratescenario'
    )
    interest_rate_scenario_enum.create(op.get_bind(), checkfirst=True)
    
    # Create alm_maturity_ladder table
    op.create_table(
        'alm_maturity_ladder',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('bucket', maturity_bucket_enum, nullable=False),
        sa.Column('cash_and_bank_balance', sa.Numeric(18, 2), default=0.00),
        sa.Column('investments', sa.Numeric(18, 2), default=0.00),
        sa.Column('loans_and_advances', sa.Numeric(18, 2), default=0.00),
        sa.Column('fixed_assets', sa.Numeric(18, 2), default=0.00),
        sa.Column('other_assets', sa.Numeric(18, 2), default=0.00),
        sa.Column('total_assets', sa.Numeric(18, 2), nullable=False),
        sa.Column('deposits', sa.Numeric(18, 2), default=0.00),
        sa.Column('borrowings', sa.Numeric(18, 2), default=0.00),
        sa.Column('debt_securities', sa.Numeric(18, 2), default=0.00),
        sa.Column('other_liabilities', sa.Numeric(18, 2), default=0.00),
        sa.Column('total_liabilities', sa.Numeric(18, 2), nullable=False),
        sa.Column('gap_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('cumulative_gap', sa.Numeric(18, 2), nullable=False),
        sa.Column('gap_percentage', sa.Numeric(10, 4), nullable=True),
        sa.Column('interest_sensitive_assets', sa.Numeric(18, 2), default=0.00),
        sa.Column('interest_sensitive_liabilities', sa.Numeric(18, 2), default=0.00),
        sa.Column('interest_rate_gap', sa.Numeric(18, 2), nullable=True),
        sa.Column('avg_asset_duration', sa.Numeric(10, 4), nullable=True),
        sa.Column('avg_liability_duration', sa.Numeric(10, 4), nullable=True),
        sa.Column('duration_gap', sa.Numeric(10, 4), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ml_tenant_date_bucket', 'alm_maturity_ladder', ['tenant_id', 'report_date', 'bucket'], unique=True)
    
    # Create alm_gap_analysis table
    op.create_table(
        'alm_gap_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('analysis_type', gap_type_enum, nullable=False),
        sa.Column('bucket', maturity_bucket_enum, nullable=False),
        sa.Column('total_inflows', sa.Numeric(18, 2), nullable=False),
        sa.Column('contractual_inflows', sa.Numeric(18, 2), default=0.00),
        sa.Column('behavioral_inflows', sa.Numeric(18, 2), default=0.00),
        sa.Column('total_outflows', sa.Numeric(18, 2), nullable=False),
        sa.Column('contractual_outflows', sa.Numeric(18, 2), default=0.00),
        sa.Column('behavioral_outflows', sa.Numeric(18, 2), default=0.00),
        sa.Column('gap_amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('cumulative_gap', sa.Numeric(18, 2), nullable=False),
        sa.Column('gap_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('risk_level', risk_level_enum, nullable=True),
        sa.Column('risk_score', sa.Numeric(10, 2), nullable=True),
        sa.Column('mitigation_required', sa.Boolean(), default=False),
        sa.Column('mitigation_strategy', sa.Text(), nullable=True),
        sa.Column('limit_breach', sa.Boolean(), default=False),
        sa.Column('limit_value', sa.Numeric(18, 2), nullable=True),
        sa.Column('actual_value', sa.Numeric(18, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ga_tenant_date_type', 'alm_gap_analysis', ['tenant_id', 'report_date', 'analysis_type'])
    op.create_index('ix_ga_risk', 'alm_gap_analysis', ['risk_level'])
    op.create_index('ix_ga_breach', 'alm_gap_analysis', ['limit_breach'])
    
    # Create alm_liquidity_ratios table
    op.create_table(
        'alm_liquidity_ratios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('current_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('quick_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('cash_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('liquidity_coverage_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('net_stable_funding_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('liquid_assets_to_total_assets', sa.Numeric(10, 4), nullable=True),
        sa.Column('liquid_assets_to_deposits', sa.Numeric(10, 4), nullable=True),
        sa.Column('liquid_assets_to_short_term_liabilities', sa.Numeric(10, 4), nullable=True),
        sa.Column('slr_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('slr_requirement', sa.Numeric(10, 4), nullable=True),
        sa.Column('slr_compliance', sa.Boolean(), default=True),
        sa.Column('loan_to_deposit_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('deposit_concentration_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('large_deposits_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('stable_funding_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('core_deposit_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('volatile_liability_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('liquidity_stress_index', sa.Numeric(10, 4), nullable=True),
        sa.Column('funding_gap_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('high_quality_liquid_assets', sa.Numeric(18, 2), nullable=True),
        sa.Column('total_net_cash_outflows', sa.Numeric(18, 2), nullable=True),
        sa.Column('available_stable_funding', sa.Numeric(18, 2), nullable=True),
        sa.Column('required_stable_funding', sa.Numeric(18, 2), nullable=True),
        sa.Column('all_ratios_compliant', sa.Boolean(), default=True),
        sa.Column('breached_ratios', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lr_tenant_date', 'alm_liquidity_ratios', ['tenant_id', 'report_date'], unique=True)
    op.create_index('ix_lr_compliance', 'alm_liquidity_ratios', ['all_ratios_compliant'])
    
    # Create alm_interest_rate_risk table
    op.create_table(
        'alm_interest_rate_risk',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('scenario', interest_rate_scenario_enum, nullable=False),
        sa.Column('net_interest_income_base', sa.Numeric(18, 2), nullable=False),
        sa.Column('market_value_equity_base', sa.Numeric(18, 2), nullable=False),
        sa.Column('interest_rate_change_bps', sa.Integer(), nullable=False),
        sa.Column('net_interest_income_change', sa.Numeric(18, 2), nullable=True),
        sa.Column('net_interest_income_change_pct', sa.Numeric(10, 4), nullable=True),
        sa.Column('market_value_equity_change', sa.Numeric(18, 2), nullable=True),
        sa.Column('market_value_equity_change_pct', sa.Numeric(10, 4), nullable=True),
        sa.Column('modified_duration_assets', sa.Numeric(10, 4), nullable=True),
        sa.Column('modified_duration_liabilities', sa.Numeric(10, 4), nullable=True),
        sa.Column('duration_gap', sa.Numeric(10, 4), nullable=True),
        sa.Column('repricing_gap_1_month', sa.Numeric(18, 2), nullable=True),
        sa.Column('repricing_gap_3_months', sa.Numeric(18, 2), nullable=True),
        sa.Column('repricing_gap_6_months', sa.Numeric(18, 2), nullable=True),
        sa.Column('repricing_gap_1_year', sa.Numeric(18, 2), nullable=True),
        sa.Column('cumulative_repricing_gap', sa.Numeric(18, 2), nullable=True),
        sa.Column('rate_sensitive_assets', sa.Numeric(18, 2), nullable=True),
        sa.Column('rate_sensitive_liabilities', sa.Numeric(18, 2), nullable=True),
        sa.Column('rate_sensitive_gap', sa.Numeric(18, 2), nullable=True),
        sa.Column('earnings_at_risk', sa.Numeric(18, 2), nullable=True),
        sa.Column('value_at_risk', sa.Numeric(18, 2), nullable=True),
        sa.Column('risk_level', risk_level_enum, nullable=True),
        sa.Column('risk_score', sa.Numeric(10, 2), nullable=True),
        sa.Column('limit_breach', sa.Boolean(), default=False),
        sa.Column('hedging_required', sa.Boolean(), default=False),
        sa.Column('hedging_strategy', sa.Text(), nullable=True),
        sa.Column('hedge_effectiveness', sa.Numeric(10, 4), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_irr_tenant_date_scenario', 'alm_interest_rate_risk', ['tenant_id', 'report_date', 'scenario'])
    op.create_index('ix_irr_risk', 'alm_interest_rate_risk', ['risk_level'])
    op.create_index('ix_irr_breach', 'alm_interest_rate_risk', ['limit_breach'])
    
    # Create alm_quarterly_returns table
    op.create_table(
        'alm_quarterly_returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('return_number', sa.String(50), nullable=False),
        sa.Column('quarter', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('sls_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('irs_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('behavioral_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_assets', sa.Numeric(18, 2), nullable=False),
        sa.Column('total_liabilities', sa.Numeric(18, 2), nullable=False),
        sa.Column('net_worth', sa.Numeric(18, 2), nullable=False),
        sa.Column('liquidity_coverage_ratio', sa.Numeric(10, 4), nullable=True),
        sa.Column('cumulative_gap_1_year', sa.Numeric(18, 2), nullable=True),
        sa.Column('cumulative_gap_1_year_pct', sa.Numeric(10, 4), nullable=True),
        sa.Column('interest_rate_shock_impact_100bps', sa.Numeric(18, 2), nullable=True),
        sa.Column('interest_rate_shock_impact_200bps', sa.Numeric(18, 2), nullable=True),
        sa.Column('earnings_at_risk', sa.Numeric(18, 2), nullable=True),
        sa.Column('is_compliant', sa.Boolean(), default=True),
        sa.Column('compliance_issues', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('prepared_by', sa.Integer(), nullable=False),
        sa.Column('prepared_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('filed_to_regulator', sa.Boolean(), default=False),
        sa.Column('filing_date', sa.Date(), nullable=True),
        sa.Column('filing_reference', sa.String(100), nullable=True),
        sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_qr_tenant_quarter', 'alm_quarterly_returns', ['tenant_id', 'year', 'quarter'], unique=True)
    op.create_index('ix_qr_filing', 'alm_quarterly_returns', ['filed_to_regulator', 'filing_date'])
    
    # Create alm_limits table
    op.create_table(
        'alm_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('limit_name', sa.String(200), nullable=False),
        sa.Column('limit_type', sa.String(100), nullable=False),
        sa.Column('maturity_bucket', maturity_bucket_enum, nullable=True),
        sa.Column('minimum_value', sa.Numeric(18, 4), nullable=True),
        sa.Column('maximum_value', sa.Numeric(18, 4), nullable=True),
        sa.Column('target_value', sa.Numeric(18, 4), nullable=True),
        sa.Column('warning_threshold_lower', sa.Numeric(18, 4), nullable=True),
        sa.Column('warning_threshold_upper', sa.Numeric(18, 4), nullable=True),
        sa.Column('is_regulatory', sa.Boolean(), default=False),
        sa.Column('regulatory_reference', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alm_limits_tenant_active', 'alm_limits', ['tenant_id', 'is_active'])
    op.create_index('ix_alm_limits_effective', 'alm_limits', ['effective_from', 'effective_to'])
    
    # Create alm_alerts table
    op.create_table(
        'alm_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('alert_date', sa.Date(), nullable=False),
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', risk_level_enum, nullable=False),
        sa.Column('metric_name', sa.String(200), nullable=False),
        sa.Column('metric_value', sa.Numeric(18, 4), nullable=False),
        sa.Column('limit_value', sa.Numeric(18, 4), nullable=True),
        sa.Column('deviation', sa.Numeric(18, 4), nullable=True),
        sa.Column('deviation_percentage', sa.Numeric(10, 4), nullable=True),
        sa.Column('maturity_ladder_id', sa.Integer(), nullable=True),
        sa.Column('gap_analysis_id', sa.Integer(), nullable=True),
        sa.Column('liquidity_ratio_id', sa.Integer(), nullable=True),
        sa.Column('interest_rate_risk_id', sa.Integer(), nullable=True),
        sa.Column('alert_message', sa.Text(), nullable=False),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('is_acknowledged', sa.Boolean(), default=False),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('is_resolved', sa.Boolean(), default=False),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), default=False),
        sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
        sa.Column('recipients', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['maturity_ladder_id'], ['alm_maturity_ladder.id']),
        sa.ForeignKeyConstraint(['gap_analysis_id'], ['alm_gap_analysis.id']),
        sa.ForeignKeyConstraint(['liquidity_ratio_id'], ['alm_liquidity_ratios.id']),
        sa.ForeignKeyConstraint(['interest_rate_risk_id'], ['alm_interest_rate_risk.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alm_alerts_tenant_date', 'alm_alerts', ['tenant_id', 'alert_date'])
    op.create_index('ix_alm_alerts_severity', 'alm_alerts', ['severity'])
    op.create_index('ix_alm_alerts_status', 'alm_alerts', ['is_resolved'])


def downgrade():
    # Drop tables
    op.drop_table('alm_alerts')
    op.drop_table('alm_limits')
    op.drop_table('alm_quarterly_returns')
    op.drop_table('alm_interest_rate_risk')
    op.drop_table('alm_liquidity_ratios')
    op.drop_table('alm_gap_analysis')
    op.drop_table('alm_maturity_ladder')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS interestratescenario')
    op.execute('DROP TYPE IF EXISTS risklevel')
    op.execute('DROP TYPE IF EXISTS gaptype')
    op.execute('DROP TYPE IF EXISTS maturitybucket')
