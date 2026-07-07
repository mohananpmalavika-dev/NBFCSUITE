"""add rbi returns automation module

Revision ID: 011_add_rbi_returns_module
Revises: 010_add_alm_module
Create Date: 2026-07-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011_add_rbi_returns_module'
down_revision = '010_add_alm_module'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================================================
    # RBI RETURN MASTER
    # ========================================================================
    op.create_table(
        'rbi_return_master',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('return_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('return_name', sa.String(300), nullable=False),
        sa.Column('return_type', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('applicable_to', postgresql.JSON),
        sa.Column('is_mandatory', sa.Boolean, default=True),
        sa.Column('effective_from', sa.Date),
        sa.Column('effective_to', sa.Date),
        sa.Column('frequency', sa.String(50), nullable=False),
        sa.Column('due_day_of_month', sa.Integer),
        sa.Column('due_days_after_period', sa.Integer),
        sa.Column('grace_period_days', sa.Integer, default=0),
        sa.Column('file_formats', postgresql.JSON),
        sa.Column('has_xbrl', sa.Boolean, default=False),
        sa.Column('xbrl_taxonomy', sa.String(50)),
        sa.Column('submission_portal', sa.String(500)),
        sa.Column('submission_method', sa.String(100)),
        sa.Column('template_file_path', sa.String(500)),
        sa.Column('template_file_url', sa.String(500)),
        sa.Column('instructions_file_path', sa.String(500)),
        sa.Column('instructions_url', sa.String(500)),
        sa.Column('validation_rules', postgresql.JSON),
        sa.Column('is_active', sa.Boolean, default=True, index=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False)
    )
    
    op.create_index('idx_return_type_active', 'rbi_return_master', ['tenant_id', 'return_type', 'is_active'])
    op.create_index('idx_return_frequency', 'rbi_return_master', ['tenant_id', 'frequency'])
    
    # ========================================================================
    # NBS-7 RETURNS
    # ========================================================================
    op.create_table(
        'nbs7_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('return_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('return_master_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rbi_return_master.id')),
        
        # Period Details
        sa.Column('reporting_period', sa.String(20), nullable=False, index=True),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('as_on_date', sa.Date, nullable=False),
        sa.Column('financial_year', sa.String(10), nullable=False, index=True),
        sa.Column('quarter', sa.String(5)),
        sa.Column('status', sa.String(50), default='draft', index=True),
        
        # Asset Side - Loans
        sa.Column('term_loans', sa.Numeric(20, 2), default=0),
        sa.Column('hire_purchase', sa.Numeric(20, 2), default=0),
        sa.Column('leasing', sa.Numeric(20, 2), default=0),
        sa.Column('bills_discounted', sa.Numeric(20, 2), default=0),
        sa.Column('other_loans', sa.Numeric(20, 2), default=0),
        sa.Column('total_loans', sa.Numeric(20, 2), default=0),
        
        # Provisions
        sa.Column('provision_standard_assets', sa.Numeric(20, 2), default=0),
        sa.Column('provision_npa', sa.Numeric(20, 2), default=0),
        sa.Column('total_provisions', sa.Numeric(20, 2), default=0),
        sa.Column('net_loans_advances', sa.Numeric(20, 2), default=0),
        
        # Investments
        sa.Column('government_securities', sa.Numeric(20, 2), default=0),
        sa.Column('corporate_bonds', sa.Numeric(20, 2), default=0),
        sa.Column('mutual_funds', sa.Numeric(20, 2), default=0),
        sa.Column('shares_equity', sa.Numeric(20, 2), default=0),
        sa.Column('other_investments', sa.Numeric(20, 2), default=0),
        sa.Column('total_investments', sa.Numeric(20, 2), default=0),
        
        # Fixed Assets
        sa.Column('fixed_assets_gross', sa.Numeric(20, 2), default=0),
        sa.Column('accumulated_depreciation', sa.Numeric(20, 2), default=0),
        sa.Column('fixed_assets_net', sa.Numeric(20, 2), default=0),
        
        # Other Assets
        sa.Column('cash_bank_balances', sa.Numeric(20, 2), default=0),
        sa.Column('other_assets', sa.Numeric(20, 2), default=0),
        sa.Column('total_assets', sa.Numeric(20, 2), default=0),
        
        # Liability Side - Capital & Reserves
        sa.Column('share_capital', sa.Numeric(20, 2), default=0),
        sa.Column('reserves_surplus', sa.Numeric(20, 2), default=0),
        sa.Column('total_capital_reserves', sa.Numeric(20, 2), default=0),
        
        # Borrowings
        sa.Column('bank_borrowings', sa.Numeric(20, 2), default=0),
        sa.Column('debentures', sa.Numeric(20, 2), default=0),
        sa.Column('commercial_paper', sa.Numeric(20, 2), default=0),
        sa.Column('subordinated_debt', sa.Numeric(20, 2), default=0),
        sa.Column('other_borrowings', sa.Numeric(20, 2), default=0),
        sa.Column('total_borrowings', sa.Numeric(20, 2), default=0),
        
        # Deposits & Other Liabilities
        sa.Column('public_deposits', sa.Numeric(20, 2), default=0),
        sa.Column('other_liabilities', sa.Numeric(20, 2), default=0),
        sa.Column('provisions_liabilities', sa.Numeric(20, 2), default=0),
        sa.Column('total_liabilities', sa.Numeric(20, 2), default=0),
        
        # Income Statement
        sa.Column('interest_income', sa.Numeric(20, 2), default=0),
        sa.Column('other_income', sa.Numeric(20, 2), default=0),
        sa.Column('total_income', sa.Numeric(20, 2), default=0),
        sa.Column('interest_expenditure', sa.Numeric(20, 2), default=0),
        sa.Column('operating_expenses', sa.Numeric(20, 2), default=0),
        sa.Column('provisions_write_offs', sa.Numeric(20, 2), default=0),
        sa.Column('total_expenditure', sa.Numeric(20, 2), default=0),
        sa.Column('profit_before_tax', sa.Numeric(20, 2), default=0),
        sa.Column('tax_provision', sa.Numeric(20, 2), default=0),
        sa.Column('profit_after_tax', sa.Numeric(20, 2), default=0),
        
        # NPA & Prudential
        sa.Column('gross_npa', sa.Numeric(20, 2), default=0),
        sa.Column('net_npa', sa.Numeric(20, 2), default=0),
        sa.Column('npa_ratio', sa.Numeric(10, 4), default=0),
        sa.Column('crar_percentage', sa.Numeric(10, 4), default=0),
        sa.Column('tier1_capital', sa.Numeric(20, 2), default=0),
        sa.Column('tier2_capital', sa.Numeric(20, 2), default=0),
        sa.Column('total_capital', sa.Numeric(20, 2), default=0),
        sa.Column('risk_weighted_assets', sa.Numeric(20, 2), default=0),
        
        # Additional Data
        sa.Column('sectoral_deployment', postgresql.JSON),
        sa.Column('geographic_distribution', postgresql.JSON),
        sa.Column('detailed_data', postgresql.JSON),
        
        # Files
        sa.Column('excel_file_path', sa.String(500)),
        sa.Column('excel_file_url', sa.String(500)),
        sa.Column('pdf_file_path', sa.String(500)),
        sa.Column('pdf_file_url', sa.String(500)),
        
        # Workflow
        sa.Column('prepared_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('prepared_date', sa.DateTime),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_date', sa.DateTime),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_date', sa.DateTime),
        
        # Submission
        sa.Column('submitted_date', sa.DateTime, index=True),
        sa.Column('submission_reference', sa.String(100)),
        sa.Column('acknowledgement_number', sa.String(100)),
        sa.Column('acknowledgement_date', sa.DateTime),
        
        # Due Date
        sa.Column('due_date', sa.Date, nullable=False, index=True),
        sa.Column('is_overdue', sa.Boolean, default=False, index=True),
        sa.Column('days_overdue', sa.Integer, default=0),
        
        # Remarks
        sa.Column('remarks', sa.Text),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('internal_notes', sa.Text),
        
        # Audit
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False)
    )
    
    op.create_index('idx_nbs7_period', 'nbs7_returns', ['tenant_id', 'reporting_period'])
    op.create_index('idx_nbs7_status', 'nbs7_returns', ['tenant_id', 'status'])
    op.create_index('idx_nbs7_fy', 'nbs7_returns', ['tenant_id', 'financial_year'])
    op.create_index('idx_nbs7_due', 'nbs7_returns', ['tenant_id', 'due_date', 'is_overdue'])
    
    # ========================================================================
    # STATUTORY RETURNS
    # ========================================================================
    op.create_table(
        'statutory_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('return_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('return_master_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rbi_return_master.id')),
        sa.Column('return_type', sa.String(50), nullable=False, index=True),
        sa.Column('reporting_period', sa.String(20), nullable=False, index=True),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('as_on_date', sa.Date, nullable=False),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('status', sa.String(50), default='draft', index=True),
        sa.Column('return_data', postgresql.JSON, nullable=False),
        sa.Column('schedules', postgresql.JSON),
        sa.Column('summary_data', postgresql.JSON),
        sa.Column('validation_status', sa.String(50), default='pending'),
        sa.Column('validation_errors', postgresql.JSON),
        sa.Column('validation_warnings', postgresql.JSON),
        sa.Column('excel_file_path', sa.String(500)),
        sa.Column('excel_file_url', sa.String(500)),
        sa.Column('pdf_file_path', sa.String(500)),
        sa.Column('pdf_file_url', sa.String(500)),
        sa.Column('prepared_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('prepared_date', sa.DateTime),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_date', sa.DateTime),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_date', sa.DateTime),
        sa.Column('submitted_date', sa.DateTime, index=True),
        sa.Column('submission_reference', sa.String(100)),
        sa.Column('acknowledgement_number', sa.String(100)),
        sa.Column('acknowledgement_date', sa.DateTime),
        sa.Column('due_date', sa.Date, nullable=False, index=True),
        sa.Column('is_overdue', sa.Boolean, default=False, index=True),
        sa.Column('days_overdue', sa.Integer, default=0),
        sa.Column('remarks', sa.Text),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('internal_notes', sa.Text),
        sa.Column('revision_number', sa.Integer, default=1),
        sa.Column('parent_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('statutory_returns.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False)
    )
    
    op.create_index('idx_statutory_period', 'statutory_returns', ['tenant_id', 'reporting_period'])
    op.create_index('idx_statutory_type_status', 'statutory_returns', ['tenant_id', 'return_type', 'status'])
    op.create_index('idx_statutory_due', 'statutory_returns', ['tenant_id', 'due_date', 'is_overdue'])
    
    # ========================================================================
    # XBRL DOCUMENTS
    # ========================================================================
    op.create_table(
        'xbrl_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('document_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('document_name', sa.String(300), nullable=False),
        sa.Column('return_type', sa.String(50), nullable=False),
        sa.Column('nbs7_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('nbs7_returns.id')),
        sa.Column('statutory_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('statutory_returns.id')),
        sa.Column('taxonomy_version', sa.String(50), nullable=False),
        sa.Column('taxonomy_url', sa.String(500)),
        sa.Column('schema_version', sa.String(50)),
        sa.Column('reporting_period', sa.String(20), nullable=False),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('xbrl_content', sa.Text),
        sa.Column('instance_document', sa.Text),
        sa.Column('is_valid', sa.Boolean, default=False),
        sa.Column('validation_errors', postgresql.JSON),
        sa.Column('validation_date', sa.DateTime),
        sa.Column('xbrl_file_path', sa.String(500)),
        sa.Column('xbrl_file_url', sa.String(500)),
        sa.Column('xbrl_file_size', sa.Integer),
        sa.Column('entity_identifier', sa.String(100)),
        sa.Column('entity_name', sa.String(300)),
        sa.Column('status', sa.String(50), default='draft', index=True),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('generated_date', sa.DateTime),
        sa.Column('submitted_date', sa.DateTime),
        sa.Column('submission_reference', sa.String(100)),
        sa.Column('remarks', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False)
    )
    
    op.create_index('idx_xbrl_period', 'xbrl_documents', ['tenant_id', 'reporting_period'])
    op.create_index('idx_xbrl_status', 'xbrl_documents', ['tenant_id', 'status'])
    op.create_index('idx_xbrl_return_type', 'xbrl_documents', ['tenant_id', 'return_type'])
    
    # ========================================================================
    # COMPLIANCE CALENDAR
    # ========================================================================
    op.create_table(
        'compliance_calendar',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('event_code', sa.String(50), index=True),
        sa.Column('event_title', sa.String(300), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('requirements', sa.Text),
        sa.Column('event_date', sa.Date, nullable=False, index=True),
        sa.Column('event_time', sa.String(20)),
        sa.Column('due_date', sa.Date, index=True),
        sa.Column('priority', sa.String(20), default='medium', index=True),
        sa.Column('category', sa.String(100)),
        sa.Column('return_master_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rbi_return_master.id')),
        sa.Column('nbs7_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('nbs7_returns.id')),
        sa.Column('statutory_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('statutory_returns.id')),
        sa.Column('is_recurring', sa.Boolean, default=False),
        sa.Column('recurrence_pattern', sa.String(50)),
        sa.Column('recurrence_day', sa.Integer),
        sa.Column('status', sa.String(50), default='pending', index=True),
        sa.Column('completion_date', sa.DateTime),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('assigned_date', sa.DateTime),
        sa.Column('reminder_enabled', sa.Boolean, default=True),
        sa.Column('reminder_days_before', postgresql.JSON),
        sa.Column('last_reminder_sent', sa.DateTime),
        sa.Column('notification_sent', sa.Boolean, default=False),
        sa.Column('notification_date', sa.DateTime),
        sa.Column('attachments', postgresql.JSON),
        sa.Column('notes', sa.Text),
        sa.Column('internal_comments', sa.Text),
        sa.Column('start_date', sa.DateTime),
        sa.Column('estimated_effort_hours', sa.Numeric(10, 2)),
        sa.Column('actual_effort_hours', sa.Numeric(10, 2)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False)
    )
    
    op.create_index('idx_calendar_date', 'compliance_calendar', ['tenant_id', 'event_date'])
    op.create_index('idx_calendar_due', 'compliance_calendar', ['tenant_id', 'due_date'])
    op.create_index('idx_calendar_status', 'compliance_calendar', ['tenant_id', 'status'])
    op.create_index('idx_calendar_priority', 'compliance_calendar', ['tenant_id', 'priority'])
    op.create_index('idx_calendar_assigned', 'compliance_calendar', ['tenant_id', 'assigned_to'])
    
    # ========================================================================
    # RETURN SUBMISSION HISTORY
    # ========================================================================
    op.create_table(
        'return_submission_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('return_type', sa.String(50), nullable=False, index=True),
        sa.Column('nbs7_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('nbs7_returns.id')),
        sa.Column('statutory_return_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('statutory_returns.id')),
        sa.Column('xbrl_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('xbrl_documents.id')),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('previous_status', sa.String(50)),
        sa.Column('new_status', sa.String(50)),
        sa.Column('action_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action_date', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('action_details', postgresql.JSON),
        sa.Column('comments', sa.Text),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False)
    )
    
    op.create_index('idx_history_return', 'return_submission_history', ['tenant_id', 'return_type', 'action_date'])
    op.create_index('idx_history_user', 'return_submission_history', ['tenant_id', 'action_by'])


def downgrade():
    op.drop_table('return_submission_history')
    op.drop_table('compliance_calendar')
    op.drop_table('xbrl_documents')
    op.drop_table('statutory_returns')
    op.drop_table('nbs7_returns')
    op.drop_table('rbi_return_master')
