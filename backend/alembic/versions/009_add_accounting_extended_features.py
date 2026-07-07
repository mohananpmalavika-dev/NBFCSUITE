"""add accounting extended features

Revision ID: 009_add_accounting_extended
Revises: 008_add_treasury_module
Create Date: 2025-01-07 10:00:00.000000

Adds TDS, GST, Asset Management, Accounts Payable, and Accounts Receivable tables
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_accounting_extended'
down_revision = '008_add_treasury_module'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================================================
    # TDS Tables
    # ========================================================================
    
    # TDS Section Master
    op.create_table(
        'tds_section_master',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('section_code', sa.String(10), nullable=False),
        sa.Column('section_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('tds_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('surcharge_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('cess_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('threshold_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('single_transaction_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('rate_without_pan', sa.Numeric(5, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tds_section_tenant_fy', 'tds_section_master', ['tenant_id', 'section_code', 'financial_year'], unique=True)
    
    # TDS Deductions
    op.create_table(
        'tds_deductions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('deduction_number', sa.String(50), nullable=False),
        sa.Column('deduction_date', sa.Date(), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('quarter', sa.Integer(), nullable=False),
        sa.Column('section_id', sa.Integer(), nullable=False),
        sa.Column('section_code', sa.String(10), nullable=False),
        sa.Column('deductee_type', sa.String(50), nullable=False),
        sa.Column('deductee_id', sa.Integer(), nullable=False),
        sa.Column('deductee_name', sa.String(200), nullable=False),
        sa.Column('deductee_pan', sa.String(10), nullable=True),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('gross_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('tds_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('tds_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('surcharge', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('cess', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_tds', sa.Numeric(15, 2), nullable=False),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('challan_id', sa.Integer(), nullable=True),
        sa.Column('certificate_id', sa.Integer(), nullable=True),
        sa.Column('payment_status', sa.String(20), server_default='pending'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['section_id'], ['tds_section_master.id'])
    )
    op.create_index('ix_tds_deduction_number', 'tds_deductions', ['deduction_number'], unique=True)
    op.create_index('ix_tds_deduction_tenant_date', 'tds_deductions', ['tenant_id', 'deduction_date'])
    op.create_index('ix_tds_deduction_deductee', 'tds_deductions', ['deductee_type', 'deductee_id'])
    
    # TDS Challans
    op.create_table(
        'tds_challans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('challan_number', sa.String(50), nullable=False),
        sa.Column('bsr_code', sa.String(7), nullable=False),
        sa.Column('challan_date', sa.Date(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('quarter', sa.Integer(), nullable=False),
        sa.Column('assessment_year', sa.String(10), nullable=False),
        sa.Column('section_code', sa.String(10), nullable=False),
        sa.Column('bank_name', sa.String(200), nullable=False),
        sa.Column('branch_name', sa.String(200), nullable=True),
        sa.Column('total_tds_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('interest_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('penalty_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_mode', sa.String(50), nullable=False),
        sa.Column('cheque_number', sa.String(50), nullable=True),
        sa.Column('transaction_reference', sa.String(100), nullable=True),
        sa.Column('payment_status', sa.String(20), server_default='paid'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tds_challan_number', 'tds_challans', ['challan_number'], unique=True)
    op.create_index('ix_tds_challan_tenant_fy', 'tds_challans', ['tenant_id', 'financial_year', 'quarter'])
    
    # TDS Certificates
    op.create_table(
        'tds_certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('certificate_number', sa.String(50), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('quarter', sa.Integer(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('deductee_type', sa.String(50), nullable=False),
        sa.Column('deductee_id', sa.Integer(), nullable=False),
        sa.Column('deductee_name', sa.String(200), nullable=False),
        sa.Column('deductee_pan', sa.String(10), nullable=False),
        sa.Column('deductee_address', sa.Text(), nullable=True),
        sa.Column('deductor_tan', sa.String(10), nullable=False),
        sa.Column('deductor_pan', sa.String(10), nullable=False),
        sa.Column('deductor_name', sa.String(200), nullable=False),
        sa.Column('total_gross_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_tds_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(20), server_default='generated'),
        sa.Column('is_digitally_signed', sa.Boolean(), server_default='false'),
        sa.Column('signature_date', sa.DateTime(), nullable=True),
        sa.Column('certificate_file_path', sa.String(500), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tds_cert_number', 'tds_certificates', ['certificate_number'], unique=True)
    op.create_index('ix_tds_cert_tenant_deductee', 'tds_certificates', ['tenant_id', 'deductee_id', 'financial_year'])
    
    # TDS Returns
    op.create_table(
        'tds_returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('return_number', sa.String(50), nullable=False),
        sa.Column('return_type', sa.String(10), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('quarter', sa.Integer(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('acknowledgement_number', sa.String(50), nullable=True),
        sa.Column('acknowledgement_date', sa.Date(), nullable=True),
        sa.Column('total_deductions', sa.Integer(), server_default='0'),
        sa.Column('total_gross_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_tds_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('return_file_path', sa.String(500), nullable=True),
        sa.Column('original_return_id', sa.Integer(), nullable=True),
        sa.Column('revision_number', sa.Integer(), server_default='0'),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['original_return_id'], ['tds_returns.id'])
    )
    op.create_index('ix_tds_return_number', 'tds_returns', ['return_number'], unique=True)
    op.create_index('ix_tds_return_tenant_period', 'tds_returns', ['tenant_id', 'financial_year', 'quarter'])
    
    # Add foreign keys for TDS deductions
    op.create_foreign_key('fk_tds_deduction_challan', 'tds_deductions', 'tds_challans', ['challan_id'], ['id'])
    op.create_foreign_key('fk_tds_deduction_certificate', 'tds_deductions', 'tds_certificates', ['certificate_id'], ['id'])


def downgrade():
    # Drop TDS tables in reverse order
    op.drop_table('tds_returns')
    op.drop_table('tds_certificates')
    op.drop_table('tds_challans')
    op.drop_table('tds_deductions')
    op.drop_table('tds_section_master')
    
    # Drop GST tables
    op.drop_table('gst_returns')
    op.drop_table('gst_input_credit')
    op.drop_table('gst_transactions')
    op.drop_table('hsn_sac_master')
    op.drop_table('gst_configuration')
    
    # Drop Asset tables
    op.drop_table('asset_maintenance')
    op.drop_table('asset_transfers')
    op.drop_table('asset_depreciation_schedule')
    op.drop_table('fixed_assets')
    
    # Drop AP tables
    op.drop_table('vendor_payment_allocations')
    op.drop_table('vendor_payments')
    op.drop_table('purchase_invoices')
    op.drop_table('vendors')
    
    # Drop AR tables
    op.drop_table('customer_receipt_allocations')
    op.drop_table('customer_receipts')
    op.drop_table('sales_invoices')
    op.drop_table('customer_master')
    
    # ========================================================================
    # GST Tables
    # ========================================================================
    
    # GST Configuration
    op.create_table(
        'gst_configuration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('gstin', sa.String(15), nullable=False),
        sa.Column('legal_name', sa.String(200), nullable=False),
        sa.Column('trade_name', sa.String(200), nullable=True),
        sa.Column('state_code', sa.String(2), nullable=False),
        sa.Column('state_name', sa.String(100), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('pincode', sa.String(6), nullable=False),
        sa.Column('registration_date', sa.Date(), nullable=False),
        sa.Column('registration_type', sa.String(50), nullable=False),
        sa.Column('is_regular', sa.Boolean(), server_default='true'),
        sa.Column('is_composition', sa.Boolean(), server_default='false'),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_gst_config_gstin', 'gst_configuration', ['gstin'], unique=True)
    
    # HSN/SAC Master
    op.create_table(
        'hsn_sac_master',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('code_type', sa.String(10), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('cgst_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('sgst_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('igst_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('cess_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_hsn_sac_tenant_code', 'hsn_sac_master', ['tenant_id', 'code'], unique=True)
    
    # GST Transactions
    op.create_table(
        'gst_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('transaction_number', sa.String(50), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('reference_type', sa.String(50), nullable=False),
        sa.Column('reference_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('party_gstin', sa.String(15), nullable=True),
        sa.Column('party_name', sa.String(200), nullable=False),
        sa.Column('party_state', sa.String(100), nullable=True),
        sa.Column('hsn_sac_code', sa.String(10), nullable=True),
        sa.Column('taxable_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('cgst_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('cgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('sgst_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('sgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('igst_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('igst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('cess_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_gst', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('is_reverse_charge', sa.Boolean(), server_default='false'),
        sa.Column('place_of_supply', sa.String(100), nullable=True),
        sa.Column('is_inter_state', sa.Boolean(), server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_gst_trans_number', 'gst_transactions', ['transaction_number'])
    op.create_index('ix_gst_trans_tenant_date', 'gst_transactions', ['tenant_id', 'transaction_date'])
    
    # GST Input Credit
    op.create_table(
        'gst_input_credit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('supplier_gstin', sa.String(15), nullable=False),
        sa.Column('supplier_name', sa.String(200), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('taxable_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('cgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('sgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('igst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('cess_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_itc', sa.Numeric(15, 2), nullable=False),
        sa.Column('itc_claimed', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('itc_reversed', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('itc_available', sa.Numeric(15, 2), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('is_in_gstr2a', sa.Boolean(), server_default='false'),
        sa.Column('is_matched', sa.Boolean(), server_default='false'),
        sa.Column('mismatch_reason', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['transaction_id'], ['gst_transactions.id'])
    )
    op.create_index('ix_gst_itc_tenant_supplier', 'gst_input_credit', ['tenant_id', 'supplier_gstin'])
    
    # GST Returns
    op.create_table(
        'gst_returns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('return_type', sa.String(20), nullable=False),
        sa.Column('return_period', sa.String(20), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=False),
        sa.Column('filing_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('arn', sa.String(50), nullable=True),
        sa.Column('outward_taxable', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('outward_cgst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('outward_sgst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('outward_igst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('inward_taxable', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('itc_cgst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('itc_sgst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('itc_igst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('net_cgst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('net_sgst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('net_igst', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_liability', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('return_file_path', sa.String(500), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_gst_return_tenant_period', 'gst_returns', ['tenant_id', 'return_period', 'return_type'])
    
    # ========================================================================
    # Fixed Asset Tables
    # ========================================================================
    
    # Fixed Assets
    op.create_table(
        'fixed_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('asset_code', sa.String(50), nullable=False),
        sa.Column('asset_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('sub_category', sa.String(100), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('purchase_cost', sa.Numeric(15, 2), nullable=False),
        sa.Column('vendor_name', sa.String(200), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('invoice_date', sa.Date(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('custodian', sa.String(200), nullable=True),
        sa.Column('depreciation_method', sa.String(50), nullable=False),
        sa.Column('depreciation_rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('useful_life_years', sa.Integer(), nullable=False),
        sa.Column('useful_life_months', sa.Integer(), server_default='0'),
        sa.Column('salvage_value', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('accumulated_depreciation', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('written_down_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('last_depreciation_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('warranty_expiry_date', sa.Date(), nullable=True),
        sa.Column('is_insured', sa.Boolean(), server_default='false'),
        sa.Column('insurance_policy_number', sa.String(100), nullable=True),
        sa.Column('insurance_expiry_date', sa.Date(), nullable=True),
        sa.Column('disposal_date', sa.Date(), nullable=True),
        sa.Column('disposal_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('gain_loss_on_disposal', sa.Numeric(15, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_asset_code', 'fixed_assets', ['asset_code'], unique=True)
    op.create_index('ix_asset_tenant_category', 'fixed_assets', ['tenant_id', 'category'])
    
    # Asset Depreciation Schedule
    op.create_table(
        'asset_depreciation_schedule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('depreciation_date', sa.Date(), nullable=False),
        sa.Column('financial_year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('opening_wdv', sa.Numeric(15, 2), nullable=False),
        sa.Column('depreciation_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('accumulated_depreciation', sa.Numeric(15, 2), nullable=False),
        sa.Column('closing_wdv', sa.Numeric(15, 2), nullable=False),
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_posted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id'])
    )
    op.create_index('ix_asset_dep_asset_date', 'asset_depreciation_schedule', ['asset_id', 'depreciation_date'], unique=True)
    
    # Asset Transfers
    op.create_table(
        'asset_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('transfer_number', sa.String(50), nullable=False),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('from_location', sa.String(200), nullable=True),
        sa.Column('from_department', sa.String(100), nullable=True),
        sa.Column('from_custodian', sa.String(200), nullable=True),
        sa.Column('to_location', sa.String(200), nullable=True),
        sa.Column('to_department', sa.String(100), nullable=True),
        sa.Column('to_custodian', sa.String(200), nullable=True),
        sa.Column('transfer_reason', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id'])
    )
    op.create_index('ix_asset_transfer_number', 'asset_transfers', ['transfer_number'], unique=True)
    
    # Asset Maintenance
    op.create_table(
        'asset_maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_date', sa.Date(), nullable=False),
        sa.Column('maintenance_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('vendor_name', sa.String(200), nullable=True),
        sa.Column('vendor_contact', sa.String(100), nullable=True),
        sa.Column('maintenance_cost', sa.Numeric(15, 2), nullable=False),
        sa.Column('is_completed', sa.Boolean(), server_default='true'),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('next_maintenance_date', sa.Date(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id'])
    )
    op.create_index('ix_asset_maint_asset_date', 'asset_maintenance', ['asset_id', 'maintenance_date'])
    
    # ========================================================================
    # Accounts Payable Tables
    # ========================================================================
    
    # Vendors
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(50), nullable=False),
        sa.Column('vendor_name', sa.String(200), nullable=False),
        sa.Column('vendor_type', sa.String(50), nullable=False),
        sa.Column('contact_person', sa.String(100), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('address_line1', sa.String(200), nullable=True),
        sa.Column('address_line2', sa.String(200), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), server_default='India'),
        sa.Column('pan', sa.String(10), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=True),
        sa.Column('tan', sa.String(10), nullable=True),
        sa.Column('bank_name', sa.String(200), nullable=True),
        sa.Column('bank_account_number', sa.String(50), nullable=True),
        sa.Column('bank_ifsc', sa.String(11), nullable=True),
        sa.Column('bank_branch', sa.String(200), nullable=True),
        sa.Column('payment_terms', sa.String(20), server_default='net_30'),
        sa.Column('credit_days', sa.Integer(), server_default='30'),
        sa.Column('credit_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_msme', sa.Boolean(), server_default='false'),
        sa.Column('vendor_rating', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vendor_code', 'vendors', ['vendor_code'], unique=True)
    op.create_index('ix_vendor_tenant_name', 'vendors', ['tenant_id', 'vendor_name'])
    op.create_index('ix_vendor_pan', 'vendors', ['pan'])
    op.create_index('ix_vendor_gstin', 'vendors', ['gstin'])
    
    # Purchase Invoices
    op.create_table(
        'purchase_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(50), nullable=False),
        sa.Column('vendor_name', sa.String(200), nullable=False),
        sa.Column('po_number', sa.String(100), nullable=True),
        sa.Column('po_date', sa.Date(), nullable=True),
        sa.Column('gross_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('taxable_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('cgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('sgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('igst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('gst_total', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('tds_section', sa.String(10), nullable=True),
        sa.Column('tds_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('tds_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('net_payable', sa.Numeric(15, 2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('balance_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'])
    )
    op.create_index('ix_pi_invoice_number', 'purchase_invoices', ['invoice_number'])
    op.create_index('ix_pi_tenant_vendor', 'purchase_invoices', ['tenant_id', 'vendor_id'])
    op.create_index('ix_pi_status_due', 'purchase_invoices', ['status', 'due_date'])
    
    # Vendor Payments
    op.create_table(
        'vendor_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('payment_number', sa.String(50), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(50), nullable=False),
        sa.Column('vendor_name', sa.String(200), nullable=False),
        sa.Column('payment_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_mode', sa.String(50), nullable=False),
        sa.Column('cheque_number', sa.String(50), nullable=True),
        sa.Column('cheque_date', sa.Date(), nullable=True),
        sa.Column('transaction_reference', sa.String(100), nullable=True),
        sa.Column('bank_name', sa.String(200), nullable=True),
        sa.Column('bank_account', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), server_default='completed'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'])
    )
    op.create_index('ix_vp_payment_number', 'vendor_payments', ['payment_number'], unique=True)
    op.create_index('ix_vp_tenant_vendor', 'vendor_payments', ['tenant_id', 'vendor_id'])
    
    # Vendor Payment Allocations
    op.create_table(
        'vendor_payment_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('allocated_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['payment_id'], ['vendor_payments.id']),
        sa.ForeignKeyConstraint(['invoice_id'], ['purchase_invoices.id'])
    )
    op.create_index('ix_vpa_payment_invoice', 'vendor_payment_allocations', ['payment_id', 'invoice_id'])
    
    # ========================================================================
    # Accounts Receivable Tables
    # ========================================================================
    
    # Customer Master
    op.create_table(
        'customer_master',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(50), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('customer_type', sa.String(50), nullable=False),
        sa.Column('contact_person', sa.String(100), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('address_line1', sa.String(200), nullable=True),
        sa.Column('address_line2', sa.String(200), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), server_default='India'),
        sa.Column('pan', sa.String(10), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=True),
        sa.Column('payment_terms', sa.String(20), server_default='net_30'),
        sa.Column('credit_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('credit_days', sa.Integer(), server_default='30'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_customer_code', 'customer_master', ['customer_code'], unique=True)
    op.create_index('ix_customer_tenant_name', 'customer_master', ['tenant_id', 'customer_name'])
    op.create_index('ix_customer_pan', 'customer_master', ['pan'])
    op.create_index('ix_customer_gstin', 'customer_master', ['gstin'])
    
    # Sales Invoices
    op.create_table(
        'sales_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(50), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('gross_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('taxable_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('cgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('sgst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('igst_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('gst_total', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('tds_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('net_receivable', sa.Numeric(15, 2), nullable=False),
        sa.Column('received_amount', sa.Numeric(15, 2), server_default='0.00'),
        sa.Column('balance_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customer_master.id'])
    )
    op.create_index('ix_si_invoice_number', 'sales_invoices', ['invoice_number'], unique=True)
    op.create_index('ix_si_tenant_customer', 'sales_invoices', ['tenant_id', 'customer_id'])
    op.create_index('ix_si_status_due', 'sales_invoices', ['status', 'due_date'])
    
    # Customer Receipts
    op.create_table(
        'customer_receipts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('receipt_number', sa.String(50), nullable=False),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('customer_code', sa.String(50), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('receipt_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_mode', sa.String(50), nullable=False),
        sa.Column('cheque_number', sa.String(50), nullable=True),
        sa.Column('cheque_date', sa.Date(), nullable=True),
        sa.Column('transaction_reference', sa.String(100), nullable=True),
        sa.Column('bank_name', sa.String(200), nullable=True),
        sa.Column('bank_account', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), server_default='cleared'),
        sa.Column('clearance_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('journal_entry_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['customer_id'], ['customer_master.id'])
    )
    op.create_index('ix_cr_receipt_number', 'customer_receipts', ['receipt_number'], unique=True)
    op.create_index('ix_cr_tenant_customer', 'customer_receipts', ['tenant_id', 'customer_id'])
    
    # Customer Receipt Allocations
    op.create_table(
        'customer_receipt_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('receipt_id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('allocated_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['receipt_id'], ['customer_receipts.id']),
        sa.ForeignKeyConstraint(['invoice_id'], ['sales_invoices.id'])
    )
    op.create_index('ix_cra_receipt_invoice', 'customer_receipt_allocations', ['receipt_id', 'invoice_id'])
