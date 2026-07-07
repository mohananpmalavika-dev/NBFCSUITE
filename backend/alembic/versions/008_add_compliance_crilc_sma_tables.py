"""add_compliance_crilc_sma_tables

Revision ID: 008
Revises: 007
Create Date: 2024-01-20 10:00:00.000000

CRILC & SMA Compliance Reporting Tables
- Large credit identification and tracking
- Special Mention Account (SMA) classification
- Quarterly regulatory returns
- Compliance alerts
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
    # ========================================================================
    # CRILC BORROWERS TABLE
    # ========================================================================
    op.create_table(
        'crilc_borrowers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('borrower_code', sa.String(50), nullable=False),
        sa.Column('borrower_name', sa.String(500), nullable=False),
        sa.Column('borrower_type', sa.String(50), nullable=False),
        sa.Column('pan_number', sa.String(10)),
        sa.Column('cin_number', sa.String(21)),
        sa.Column('gstin', sa.String(15)),
        sa.Column('registered_address', sa.Text()),
        sa.Column('city', sa.String(200)),
        sa.Column('state', sa.String(100)),
        sa.Column('pincode', sa.String(10)),
        sa.Column('country', sa.String(100), server_default='India'),
        sa.Column('industry_code', sa.String(20)),
        sa.Column('industry_name', sa.String(200)),
        sa.Column('nature_of_business', sa.String(500)),
        sa.Column('year_of_incorporation', sa.Integer()),
        sa.Column('annual_turnover', sa.Numeric(20, 2)),
        sa.Column('net_worth', sa.Numeric(20, 2)),
        sa.Column('financial_year', sa.String(10)),
        sa.Column('total_credit_exposure', sa.Numeric(20, 2), nullable=False),
        sa.Column('funded_exposure', sa.Numeric(20, 2)),
        sa.Column('non_funded_exposure', sa.Numeric(20, 2)),
        sa.Column('is_large_credit', sa.Boolean(), server_default='false'),
        sa.Column('large_credit_since', sa.Date()),
        sa.Column('is_part_of_group', sa.Boolean(), server_default='false'),
        sa.Column('group_name', sa.String(300)),
        sa.Column('group_exposure', sa.Numeric(20, 2)),
        sa.Column('related_party_ids', postgresql.JSON()),
        sa.Column('current_sma_status', sa.String(50), server_default='standard'),
        sa.Column('current_asset_classification', sa.String(50), server_default='standard'),
        sa.Column('days_past_due', sa.Integer(), server_default='0'),
        sa.Column('internal_rating', sa.String(20)),
        sa.Column('external_rating', sa.String(20)),
        sa.Column('rating_agency', sa.String(100)),
        sa.Column('rating_date', sa.Date()),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_reported_quarter', sa.String(10)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'])
    )
    
    op.create_index('idx_crilc_borrower_code', 'crilc_borrowers', ['tenant_id', 'borrower_code'], unique=True)
    op.create_index('idx_crilc_borrower_pan', 'crilc_borrowers', ['tenant_id', 'pan_number'])
    op.create_index('idx_crilc_large_credit', 'crilc_borrowers', ['tenant_id', 'is_large_credit'])
    op.create_index('idx_crilc_sma', 'crilc_borrowers', ['tenant_id', 'current_sma_status'])
    
    # ========================================================================
    # CRILC FACILITIES TABLE
    # ========================================================================
    op.create_table(
        'crilc_facilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('borrower_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_account_id', postgresql.UUID(as_uuid=True)),
        sa.Column('facility_id', sa.String(100), nullable=False),
        sa.Column('facility_type', sa.String(50), nullable=False),
        sa.Column('exposure_type', sa.String(50), nullable=False),
        sa.Column('sanctioned_amount', sa.Numeric(20, 2), nullable=False),
        sa.Column('outstanding_amount', sa.Numeric(20, 2), nullable=False),
        sa.Column('overdue_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sanction_date', sa.Date(), nullable=False),
        sa.Column('disbursement_date', sa.Date()),
        sa.Column('maturity_date', sa.Date()),
        sa.Column('security_type', sa.String(100)),
        sa.Column('security_value', sa.Numeric(20, 2)),
        sa.Column('collateral_details', postgresql.JSON()),
        sa.Column('days_past_due', sa.Integer(), server_default='0'),
        sa.Column('asset_classification', sa.String(50), server_default='standard'),
        sa.Column('interest_rate', sa.Numeric(5, 2)),
        sa.Column('interest_overdue', sa.Numeric(15, 2), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('closure_date', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['borrower_id'], ['crilc_borrowers.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id'])
    )
    
    op.create_index('idx_facility_id', 'crilc_facilities', ['facility_id'], unique=True)
    op.create_index('idx_facility_borrower', 'crilc_facilities', ['tenant_id', 'borrower_id'])
    op.create_index('idx_facility_dpd', 'crilc_facilities', ['tenant_id', 'days_past_due'])
    
    # ========================================================================
    # SMA TRACKING TABLE
    # ========================================================================
    op.create_table(
        'sma_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('borrower_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('as_on_date', sa.Date(), nullable=False),
        sa.Column('reporting_quarter', sa.String(10)),
        sa.Column('current_sma_status', sa.String(50), nullable=False),
        sa.Column('previous_sma_status', sa.String(50)),
        sa.Column('status_change_date', sa.Date()),
        sa.Column('days_past_due', sa.Integer(), server_default='0'),
        sa.Column('days_in_current_status', sa.Integer(), server_default='0'),
        sa.Column('principal_outstanding', sa.Numeric(20, 2), nullable=False),
        sa.Column('interest_outstanding', sa.Numeric(20, 2), server_default='0'),
        sa.Column('total_outstanding', sa.Numeric(20, 2), nullable=False),
        sa.Column('principal_overdue', sa.Numeric(20, 2), server_default='0'),
        sa.Column('interest_overdue', sa.Numeric(20, 2), server_default='0'),
        sa.Column('total_overdue', sa.Numeric(20, 2), server_default='0'),
        sa.Column('installment_amount', sa.Numeric(15, 2)),
        sa.Column('last_payment_date', sa.Date()),
        sa.Column('last_payment_amount', sa.Numeric(15, 2)),
        sa.Column('next_due_date', sa.Date()),
        sa.Column('asset_classification', sa.String(50), server_default='standard'),
        sa.Column('provision_required', sa.Numeric(15, 2), server_default='0'),
        sa.Column('provision_percentage', sa.Numeric(5, 2), server_default='0'),
        sa.Column('alert_triggered', sa.Boolean(), server_default='false'),
        sa.Column('alert_date', sa.DateTime(timezone=True)),
        sa.Column('action_taken', sa.Text()),
        sa.Column('follow_up_required', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['borrower_id'], ['crilc_borrowers.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id'])
    )
    
    op.create_index('idx_sma_loan_date', 'sma_tracking', ['tenant_id', 'loan_account_id', 'as_on_date'])
    op.create_index('idx_sma_status', 'sma_tracking', ['tenant_id', 'current_sma_status', 'as_on_date'])
    op.create_index('idx_sma_quarter', 'sma_tracking', ['tenant_id', 'reporting_quarter'])
    
    # ========================================================================
    # SMA STATUS HISTORY TABLE
    # ========================================================================
    op.create_table(
        'sma_status_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('borrower_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loan_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_status', sa.String(50), nullable=False),
        sa.Column('to_status', sa.String(50), nullable=False),
        sa.Column('change_date', sa.Date(), nullable=False),
        sa.Column('dpd_at_change', sa.Integer()),
        sa.Column('outstanding_at_change', sa.Numeric(20, 2)),
        sa.Column('overdue_at_change', sa.Numeric(20, 2)),
        sa.Column('change_reason', sa.Text()),
        sa.Column('triggered_by', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['borrower_id'], ['crilc_borrowers.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id'])
    )
    
    op.create_index('idx_history_loan', 'sma_status_history', ['tenant_id', 'loan_account_id', 'change_date'])
    
    # ========================================================================
    # CRILC QUARTERLY RETURNS TABLE
    # ========================================================================
    op.create_table(
        'crilc_quarterly_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('return_number', sa.String(50), nullable=False),
        sa.Column('reporting_quarter', sa.String(10), nullable=False),
        sa.Column('reporting_year', sa.String(10), nullable=False),
        sa.Column('as_on_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('total_large_borrowers', sa.Integer(), server_default='0'),
        sa.Column('total_funded_exposure', sa.Numeric(20, 2), server_default='0'),
        sa.Column('total_non_funded_exposure', sa.Numeric(20, 2), server_default='0'),
        sa.Column('total_exposure', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sma_0_count', sa.Integer(), server_default='0'),
        sa.Column('sma_0_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sma_1_count', sa.Integer(), server_default='0'),
        sa.Column('sma_1_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sma_2_count', sa.Integer(), server_default='0'),
        sa.Column('sma_2_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('npa_count', sa.Integer(), server_default='0'),
        sa.Column('npa_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('report_file_path', sa.String(500)),
        sa.Column('report_file_url', sa.String(500)),
        sa.Column('report_format', sa.String(20)),
        sa.Column('prepared_by', postgresql.UUID(as_uuid=True)),
        sa.Column('prepared_date', sa.DateTime(timezone=True)),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('reviewed_date', sa.DateTime(timezone=True)),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_date', sa.DateTime(timezone=True)),
        sa.Column('submitted_date', sa.DateTime(timezone=True)),
        sa.Column('submission_reference', sa.String(100)),
        sa.Column('remarks', sa.Text()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('data_snapshot', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['prepared_by'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'])
    )
    
    op.create_index('idx_return_number', 'crilc_quarterly_returns', ['return_number'], unique=True)
    op.create_index('idx_return_quarter', 'crilc_quarterly_returns', ['tenant_id', 'reporting_quarter'])
    op.create_index('idx_return_status', 'crilc_quarterly_returns', ['tenant_id', 'status'])
    
    # ========================================================================
    # SMA QUARTERLY REPORTS TABLE
    # ========================================================================
    op.create_table(
        'sma_quarterly_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('report_number', sa.String(50), nullable=False),
        sa.Column('reporting_quarter', sa.String(10), nullable=False),
        sa.Column('reporting_year', sa.String(10), nullable=False),
        sa.Column('as_on_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('sma_0_accounts', sa.Integer(), server_default='0'),
        sa.Column('sma_0_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sma_0_new_additions', sa.Integer(), server_default='0'),
        sa.Column('sma_0_regularized', sa.Integer(), server_default='0'),
        sa.Column('sma_0_upgraded_to_sma1', sa.Integer(), server_default='0'),
        sa.Column('sma_1_accounts', sa.Integer(), server_default='0'),
        sa.Column('sma_1_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sma_1_new_additions', sa.Integer(), server_default='0'),
        sa.Column('sma_1_regularized', sa.Integer(), server_default='0'),
        sa.Column('sma_1_upgraded_to_sma2', sa.Integer(), server_default='0'),
        sa.Column('sma_2_accounts', sa.Integer(), server_default='0'),
        sa.Column('sma_2_amount', sa.Numeric(20, 2), server_default='0'),
        sa.Column('sma_2_new_additions', sa.Integer(), server_default='0'),
        sa.Column('sma_2_regularized', sa.Integer(), server_default='0'),
        sa.Column('sma_2_slipped_to_npa', sa.Integer(), server_default='0'),
        sa.Column('sectoral_breakdown', postgresql.JSON()),
        sa.Column('geographic_breakdown', postgresql.JSON()),
        sa.Column('report_file_path', sa.String(500)),
        sa.Column('report_file_url', sa.String(500)),
        sa.Column('prepared_by', postgresql.UUID(as_uuid=True)),
        sa.Column('prepared_date', sa.DateTime(timezone=True)),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_date', sa.DateTime(timezone=True)),
        sa.Column('submitted_date', sa.DateTime(timezone=True)),
        sa.Column('remarks', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['prepared_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'])
    )
    
    op.create_index('idx_sma_report_number', 'sma_quarterly_reports', ['report_number'], unique=True)
    op.create_index('idx_sma_report_quarter', 'sma_quarterly_reports', ['tenant_id', 'reporting_quarter'])
    
    # ========================================================================
    # COMPLIANCE ALERTS TABLE
    # ========================================================================
    op.create_table(
        'compliance_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('alert_category', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), server_default='medium'),
        sa.Column('borrower_id', postgresql.UUID(as_uuid=True)),
        sa.Column('loan_account_id', postgresql.UUID(as_uuid=True)),
        sa.Column('alert_message', sa.Text(), nullable=False),
        sa.Column('alert_details', postgresql.JSON()),
        sa.Column('status', sa.String(50), server_default='open'),
        sa.Column('acknowledged_by', postgresql.UUID(as_uuid=True)),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True)),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('resolution_notes', sa.Text()),
        sa.Column('due_date', sa.Date()),
        sa.Column('is_overdue', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['borrower_id'], ['crilc_borrowers.id']),
        sa.ForeignKeyConstraint(['loan_account_id'], ['loan_accounts.id']),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'])
    )
    
    op.create_index('idx_alert_status', 'compliance_alerts', ['tenant_id', 'status'])
    op.create_index('idx_alert_type', 'compliance_alerts', ['tenant_id', 'alert_type'])


def downgrade() -> None:
    op.drop_table('compliance_alerts')
    op.drop_table('sma_quarterly_reports')
    op.drop_table('crilc_quarterly_returns')
    op.drop_table('sma_status_history')
    op.drop_table('sma_tracking')
    op.drop_table('crilc_facilities')
    op.drop_table('crilc_borrowers')
