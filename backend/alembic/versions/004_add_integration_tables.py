"""Add integration tables for bureau, bank statement, OCR, and eKYC

Revision ID: 004
Revises: 003
Create Date: 2026-01-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Bureau Reports Table
    op.create_table(
        'bureau_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('bureau_name', sa.String(50), nullable=False),
        sa.Column('report_type', sa.String(50)),
        sa.Column('score', sa.Integer()),
        sa.Column('score_date', sa.Date()),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('report_json', postgresql.JSON()),
        sa.Column('report_pdf_url', sa.String(500)),
        sa.Column('consent_id', sa.Integer()),
        sa.Column('pulled_by', sa.Integer()),
        sa.Column('pulled_at', sa.DateTime()),
        sa.Column('risk_factors', postgresql.JSON()),
        sa.Column('positive_factors', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['consent_id'], ['bureau_consents.id'])
    )
    op.create_index('ix_bureau_reports_tenant_id', 'bureau_reports', ['tenant_id'])
    op.create_index('ix_bureau_reports_customer_id', 'bureau_reports', ['customer_id'])
    op.create_index('ix_bureau_reports_bureau_name', 'bureau_reports', ['bureau_name'])
    op.create_index('ix_bureau_reports_report_date', 'bureau_reports', ['report_date'])
    
    # Bureau Consents Table
    op.create_table(
        'bureau_consents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('consent_type', sa.String(50)),
        sa.Column('consent_given', sa.Boolean(), default=False),
        sa.Column('consent_date', sa.Date()),
        sa.Column('consent_document_url', sa.String(500)),
        sa.Column('valid_until', sa.Date()),
        sa.Column('revoked', sa.Boolean(), default=False),
        sa.Column('revoked_date', sa.Date()),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'])
    )
    op.create_index('ix_bureau_consents_tenant_id', 'bureau_consents', ['tenant_id'])
    op.create_index('ix_bureau_consents_customer_id', 'bureau_consents', ['customer_id'])
    
    # Bank Statement Analyses Table
    op.create_table(
        'bank_statement_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer()),
        sa.Column('bank_name', sa.String(200)),
        sa.Column('account_number', sa.String(50)),
        sa.Column('account_type', sa.String(50)),
        sa.Column('ifsc_code', sa.String(20)),
        sa.Column('statement_period_from', sa.Date()),
        sa.Column('statement_period_to', sa.Date()),
        sa.Column('number_of_months', sa.Integer()),
        sa.Column('avg_monthly_income', sa.DECIMAL(15, 2)),
        sa.Column('total_credits', sa.DECIMAL(15, 2)),
        sa.Column('salary_credits_count', sa.Integer()),
        sa.Column('salary_credits_amount', sa.DECIMAL(15, 2)),
        sa.Column('irregular_income', sa.Boolean(), default=False),
        sa.Column('income_stability_score', sa.Integer()),
        sa.Column('avg_monthly_expenses', sa.DECIMAL(15, 2)),
        sa.Column('total_debits', sa.DECIMAL(15, 2)),
        sa.Column('emi_obligations', sa.DECIMAL(15, 2)),
        sa.Column('loan_payments', sa.DECIMAL(15, 2)),
        sa.Column('credit_card_payments', sa.DECIMAL(15, 2)),
        sa.Column('avg_balance', sa.DECIMAL(15, 2)),
        sa.Column('min_balance', sa.DECIMAL(15, 2)),
        sa.Column('max_balance', sa.DECIMAL(15, 2)),
        sa.Column('bounced_transactions', sa.Integer(), default=0),
        sa.Column('bounced_amount', sa.DECIMAL(15, 2)),
        sa.Column('overdraft_instances', sa.Integer(), default=0),
        sa.Column('net_monthly_surplus', sa.DECIMAL(15, 2)),
        sa.Column('disposable_income', sa.DECIMAL(15, 2)),
        sa.Column('cash_deposit_frequency', sa.Integer()),
        sa.Column('cash_deposit_amount', sa.DECIMAL(15, 2)),
        sa.Column('risk_score', sa.Integer()),
        sa.Column('risk_level', sa.String(50)),
        sa.Column('red_flags', postgresql.JSON()),
        sa.Column('analysis_json', postgresql.JSON()),
        sa.Column('transaction_categories', postgresql.JSON()),
        sa.Column('statement_file_url', sa.String(500)),
        sa.Column('analyzed_by', sa.String(50)),
        sa.Column('analyzed_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['application_id'], ['loan_applications.id'])
    )
    op.create_index('ix_bank_statement_analyses_tenant_id', 'bank_statement_analyses', ['tenant_id'])
    op.create_index('ix_bank_statement_analyses_customer_id', 'bank_statement_analyses', ['customer_id'])
    op.create_index('ix_bank_statement_analyses_application_id', 'bank_statement_analyses', ['application_id'])
    
    # Document OCR Results Table
    op.create_table(
        'document_ocr_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer()),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(100)),
        sa.Column('ocr_status', sa.String(50), default='pending'),
        sa.Column('ocr_provider', sa.String(50)),
        sa.Column('extracted_data', postgresql.JSON()),
        sa.Column('full_name', sa.String(300)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('document_number', sa.String(100)),
        sa.Column('address', sa.Text()),
        sa.Column('aadhaar_number', sa.String(20)),
        sa.Column('gender', sa.String(20)),
        sa.Column('pan_number', sa.String(20)),
        sa.Column('father_name', sa.String(300)),
        sa.Column('issue_date', sa.Date()),
        sa.Column('expiry_date', sa.Date()),
        sa.Column('photo_url', sa.String(500)),
        sa.Column('face_extracted', sa.Boolean(), default=False),
        sa.Column('confidence_score', sa.DECIMAL(5, 2)),
        sa.Column('auto_verified', sa.Boolean(), default=False),
        sa.Column('verification_status', sa.String(50)),
        sa.Column('matches_customer_data', sa.Boolean()),
        sa.Column('mismatch_fields', postgresql.JSON()),
        sa.Column('processed_at', sa.DateTime()),
        sa.Column('processing_time_ms', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['document_id'], ['customer_documents.id'])
    )
    op.create_index('ix_document_ocr_results_tenant_id', 'document_ocr_results', ['tenant_id'])
    op.create_index('ix_document_ocr_results_customer_id', 'document_ocr_results', ['customer_id'])
    op.create_index('ix_document_ocr_results_document_id', 'document_ocr_results', ['document_id'])
    
    # eKYC Records Table
    op.create_table(
        'ekyc_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('kyc_type', sa.String(50)),
        sa.Column('aadhaar_number', sa.String(20)),
        sa.Column('transaction_id', sa.String(100)),
        sa.Column('otp_sent', sa.Boolean(), default=False),
        sa.Column('otp_verified', sa.Boolean(), default=False),
        sa.Column('kyc_data', postgresql.JSON()),
        sa.Column('full_name', sa.String(300)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('gender', sa.String(20)),
        sa.Column('address', sa.Text()),
        sa.Column('photo_base64', sa.Text()),
        sa.Column('verification_status', sa.String(50)),
        sa.Column('verification_timestamp', sa.DateTime()),
        sa.Column('error_message', sa.Text()),
        sa.Column('consent_given', sa.Boolean(), default=False),
        sa.Column('consent_timestamp', sa.DateTime()),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'])
    )
    op.create_index('ix_ekyc_records_tenant_id', 'ekyc_records', ['tenant_id'])
    op.create_index('ix_ekyc_records_customer_id', 'ekyc_records', ['customer_id'])
    
    # DigiLocker Documents Table
    op.create_table(
        'digilocker_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('digilocker_id', sa.String(100)),
        sa.Column('document_type', sa.String(100)),
        sa.Column('document_name', sa.String(300)),
        sa.Column('document_url', sa.String(500)),
        sa.Column('document_data', postgresql.JSON()),
        sa.Column('issuer_name', sa.String(200)),
        sa.Column('issue_date', sa.Date()),
        sa.Column('is_verified', sa.Boolean(), default=True),
        sa.Column('verified_by_govt', sa.Boolean(), default=True),
        sa.Column('fetched_at', sa.DateTime()),
        sa.Column('access_token', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'])
    )
    op.create_index('ix_digilocker_documents_tenant_id', 'digilocker_documents', ['tenant_id'])
    op.create_index('ix_digilocker_documents_customer_id', 'digilocker_documents', ['customer_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('digilocker_documents')
    op.drop_table('ekyc_records')
    op.drop_table('document_ocr_results')
    op.drop_table('bank_statement_analyses')
    op.drop_table('bureau_reports')
    op.drop_table('bureau_consents')
