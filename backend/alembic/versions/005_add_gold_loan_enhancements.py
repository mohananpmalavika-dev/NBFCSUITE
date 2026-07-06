"""add gold loan enhancements

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 10:00:00.000000

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
    """
    Add tables for:
    - Gold rate history and live rates
    - Vault management (locations, inventory, transfers)
    - Purity testing
    - Appraisal reports
    - Enhanced auction features (bids, notices)
    """
    
    # ==================== Gold Rate History ====================
    op.create_table(
        'gold_rate_history',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Rate details
        sa.Column('rate_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('gold_rate_24k', sa.Numeric(10, 2), nullable=False),
        sa.Column('gold_rate_22k', sa.Numeric(10, 2), nullable=False),
        sa.Column('gold_rate_18k', sa.Numeric(10, 2), nullable=False),
        
        # Source information
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('source_reference', sa.String(200), nullable=True),
        
        # Market info
        sa.Column('market_name', sa.String(100), nullable=True),
        sa.Column('currency', sa.String(10), default='INR'),
        
        # Additional rates
        sa.Column('silver_rate', sa.Numeric(10, 2), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_current', sa.Boolean, default=False, nullable=False, index=True),
        
        # Metadata
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('applied_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('applied_to', sa.DateTime(timezone=True), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_gold_rate_date', 'gold_rate_history', ['tenant_id', 'rate_date'])
    op.create_index('idx_gold_rate_current', 'gold_rate_history', ['tenant_id', 'is_current'])
    op.create_index('idx_gold_rate_source', 'gold_rate_history', ['tenant_id', 'source'])
    
    # ==================== Vault Locations ====================
    op.create_table(
        'vault_locations',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Location details
        sa.Column('vault_code', sa.String(50), nullable=False, index=True),
        sa.Column('vault_name', sa.String(200), nullable=False),
        
        # Hierarchy
        sa.Column('branch_id', sa.String(50), nullable=False, index=True),
        sa.Column('location_type', sa.String(50), nullable=False),
        
        # Physical location
        sa.Column('building', sa.String(200), nullable=True),
        sa.Column('floor', sa.String(50), nullable=True),
        sa.Column('room', sa.String(50), nullable=True),
        sa.Column('rack_number', sa.String(50), nullable=True),
        sa.Column('shelf_number', sa.String(50), nullable=True),
        
        # Capacity
        sa.Column('max_capacity_items', sa.Integer, nullable=True),
        sa.Column('max_capacity_weight_kg', sa.Numeric(10, 3), nullable=True),
        sa.Column('current_items_count', sa.Integer, default=0),
        sa.Column('current_weight_kg', sa.Numeric(10, 3), default=0.000),
        
        # Security
        sa.Column('security_level', sa.String(50), default='High'),
        sa.Column('access_control', sa.String(100), nullable=True),
        sa.Column('surveillance', sa.Boolean, default=True),
        
        # Insurance
        sa.Column('insured', sa.Boolean, default=True),
        sa.Column('insurance_value', sa.Numeric(15, 2), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), default='Active', index=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        
        # Contact
        sa.Column('custodian_name', sa.String(200), nullable=True),
        sa.Column('custodian_contact', sa.String(20), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_vault_code', 'vault_locations', ['tenant_id', 'vault_code'], unique=True)
    op.create_index('idx_vault_branch', 'vault_locations', ['tenant_id', 'branch_id'])
    op.create_index('idx_vault_status', 'vault_locations', ['tenant_id', 'status'])
    
    # ==================== Vault Inventory ====================
    op.create_table(
        'vault_inventory',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Inventory details
        sa.Column('inventory_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('vault_location_id', sa.String(50), nullable=False, index=True),
        
        # Gold loan reference
        sa.Column('gold_loan_id', sa.String(50), nullable=False, index=True),
        sa.Column('customer_id', sa.String(50), nullable=False, index=True),
        sa.Column('ornament_id', sa.String(50), nullable=False, index=True),
        
        # Storage details
        sa.Column('package_number', sa.String(50), nullable=True),
        sa.Column('seal_number', sa.String(50), nullable=True),
        sa.Column('barcode', sa.String(100), nullable=True, index=True),
        sa.Column('rfid_tag', sa.String(100), nullable=True, index=True),
        
        # Physical location
        sa.Column('rack_position', sa.String(50), nullable=True),
        sa.Column('shelf_position', sa.String(50), nullable=True),
        sa.Column('slot_position', sa.String(50), nullable=True),
        
        # Item details
        sa.Column('item_description', sa.Text, nullable=False),
        sa.Column('total_weight_grams', sa.Numeric(10, 3), nullable=False),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False),
        
        # Check-in details
        sa.Column('check_in_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('check_in_by', sa.String(50), nullable=False),
        sa.Column('check_in_verified_by', sa.String(50), nullable=True),
        sa.Column('check_in_photo_url', sa.String(500), nullable=True),
        
        # Check-out details
        sa.Column('check_out_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('check_out_by', sa.String(50), nullable=True),
        sa.Column('check_out_verified_by', sa.String(50), nullable=True),
        sa.Column('check_out_photo_url', sa.String(500), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), default='In Vault', index=True),
        
        # Audit trail
        sa.Column('last_audit_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_audit_by', sa.String(50), nullable=True),
        sa.Column('audit_status', sa.String(50), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_vault_inv_vault', 'vault_inventory', ['tenant_id', 'vault_location_id'])
    op.create_index('idx_vault_inv_loan', 'vault_inventory', ['tenant_id', 'gold_loan_id'])
    op.create_index('idx_vault_inv_status', 'vault_inventory', ['tenant_id', 'status'])
    op.create_index('idx_vault_inv_barcode', 'vault_inventory', ['tenant_id', 'barcode'])
    
    # ==================== Vault Transfers ====================
    op.create_table(
        'vault_transfers',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Transfer details
        sa.Column('transfer_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('transfer_date', sa.DateTime(timezone=True), nullable=False),
        
        # Source and destination
        sa.Column('from_vault_id', sa.String(50), nullable=False, index=True),
        sa.Column('to_vault_id', sa.String(50), nullable=False, index=True),
        
        # Items
        sa.Column('inventory_ids', sa.Text, nullable=False),
        sa.Column('total_items_count', sa.Integer, nullable=False),
        sa.Column('total_weight_grams', sa.Numeric(10, 3), nullable=False),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False),
        
        # Transfer tracking
        sa.Column('initiated_by', sa.String(50), nullable=False),
        sa.Column('approved_by', sa.String(50), nullable=True),
        
        # Dispatch
        sa.Column('dispatched_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dispatched_by', sa.String(50), nullable=True),
        sa.Column('dispatch_reference', sa.String(100), nullable=True),
        
        # Receipt
        sa.Column('received_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('received_by', sa.String(50), nullable=True),
        sa.Column('receipt_reference', sa.String(100), nullable=True),
        
        # Verification
        sa.Column('verified_by', sa.String(50), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_status', sa.String(50), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), default='Pending', index=True),
        
        # Security
        sa.Column('seal_number', sa.String(50), nullable=True),
        sa.Column('transport_mode', sa.String(50), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_vault_transfer_from', 'vault_transfers', ['tenant_id', 'from_vault_id'])
    op.create_index('idx_vault_transfer_to', 'vault_transfers', ['tenant_id', 'to_vault_id'])
    op.create_index('idx_vault_transfer_status', 'vault_transfers', ['tenant_id', 'status'])
    
    # ==================== Purity Tests ====================
    op.create_table(
        'purity_tests',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Test details
        sa.Column('test_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('test_date', sa.DateTime(timezone=True), nullable=False),
        
        # Item reference
        sa.Column('gold_loan_id', sa.String(50), nullable=False, index=True),
        sa.Column('ornament_id', sa.String(50), nullable=False, index=True),
        sa.Column('customer_id', sa.String(50), nullable=False, index=True),
        
        # Test method
        sa.Column('test_method', sa.String(50), nullable=False),
        
        # Claimed details
        sa.Column('claimed_purity_karat', sa.Integer, nullable=False),
        sa.Column('claimed_purity_percentage', sa.Numeric(5, 2), nullable=False),
        
        # Test results
        sa.Column('tested_purity_karat', sa.Integer, nullable=False),
        sa.Column('tested_purity_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('purity_variance', sa.Numeric(5, 2), nullable=False),
        
        # Equipment
        sa.Column('equipment_id', sa.String(50), nullable=True),
        sa.Column('equipment_name', sa.String(200), nullable=True),
        sa.Column('equipment_calibration_date', sa.DateTime(timezone=True), nullable=True),
        
        # Testing details
        sa.Column('sample_weight', sa.Numeric(10, 3), nullable=True),
        sa.Column('test_temperature', sa.Numeric(6, 2), nullable=True),
        
        # Result
        sa.Column('test_result', sa.String(50), nullable=False, index=True),
        
        # Tester
        sa.Column('tested_by', sa.String(50), nullable=False),
        sa.Column('tester_name', sa.String(200), nullable=False),
        sa.Column('tester_license', sa.String(100), nullable=True),
        sa.Column('verified_by', sa.String(50), nullable=True),
        
        # Certificate
        sa.Column('certificate_number', sa.String(100), nullable=True, index=True),
        sa.Column('certificate_url', sa.String(500), nullable=True),
        sa.Column('certificate_issued_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('certificate_valid_until', sa.DateTime(timezone=True), nullable=True),
        
        # Action
        sa.Column('action_taken', sa.String(50), nullable=True),
        sa.Column('adjusted_value', sa.Numeric(15, 2), nullable=True),
        
        # Photos/evidence
        sa.Column('test_photo_url', sa.String(500), nullable=True),
        sa.Column('report_url', sa.String(500), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_purity_test_loan', 'purity_tests', ['tenant_id', 'gold_loan_id'])
    op.create_index('idx_purity_test_ornament', 'purity_tests', ['tenant_id', 'ornament_id'])
    op.create_index('idx_purity_test_result', 'purity_tests', ['tenant_id', 'test_result'])
    op.create_index('idx_purity_test_date', 'purity_tests', ['tenant_id', 'test_date'])
    
    # ==================== Appraisal Reports ====================
    op.create_table(
        'appraisal_reports',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Report details
        sa.Column('appraisal_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('appraisal_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('appraisal_type', sa.String(50), nullable=False),
        
        # Item reference
        sa.Column('gold_loan_id', sa.String(50), nullable=True, index=True),
        sa.Column('ornament_id', sa.String(50), nullable=True, index=True),
        sa.Column('customer_id', sa.String(50), nullable=False, index=True),
        
        # Ornament details
        sa.Column('ornament_type', sa.String(100), nullable=False),
        sa.Column('ornament_description', sa.Text, nullable=False),
        sa.Column('quantity', sa.Integer, default=1),
        
        # Gold details
        sa.Column('claimed_karat', sa.Integer, nullable=False),
        sa.Column('verified_karat', sa.Integer, nullable=False),
        sa.Column('purity_percentage', sa.Numeric(5, 2), nullable=False),
        
        # Weight
        sa.Column('gross_weight_grams', sa.Numeric(10, 3), nullable=False),
        sa.Column('stone_weight_grams', sa.Numeric(10, 3), default=0.000),
        sa.Column('other_deductions_grams', sa.Numeric(10, 3), default=0.000),
        sa.Column('net_gold_weight_grams', sa.Numeric(10, 3), nullable=False),
        
        # Identification
        sa.Column('hallmark_present', sa.Boolean, default=False),
        sa.Column('hallmark_number', sa.String(100), nullable=True),
        sa.Column('hallmark_center', sa.String(200), nullable=True),
        sa.Column('manufacturer_mark', sa.String(200), nullable=True),
        
        # Condition
        sa.Column('condition', sa.String(50), nullable=False),
        sa.Column('wear_and_tear', sa.Text, nullable=True),
        sa.Column('defects', sa.Text, nullable=True),
        
        # Market valuation
        sa.Column('current_gold_rate_24k', sa.Numeric(10, 2), nullable=False),
        sa.Column('applied_gold_rate', sa.Numeric(10, 2), nullable=False),
        sa.Column('base_value', sa.Numeric(15, 2), nullable=False),
        
        # Adjustments
        sa.Column('condition_adjustment_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('market_adjustment_percentage', sa.Numeric(5, 2), default=0.00),
        
        # Final valuation
        sa.Column('market_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('appraised_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('forced_sale_value', sa.Numeric(15, 2), nullable=True),
        
        # Comparable
        sa.Column('comparable_items', sa.Text, nullable=True),
        sa.Column('market_reference', sa.Text, nullable=True),
        
        # Appraiser
        sa.Column('appraised_by', sa.String(50), nullable=False),
        sa.Column('appraiser_name', sa.String(200), nullable=False),
        sa.Column('appraiser_license', sa.String(100), nullable=True),
        sa.Column('appraiser_experience_years', sa.Integer, nullable=True),
        
        # Verification
        sa.Column('verified_by', sa.String(50), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_status', sa.String(50), nullable=True),
        
        # Documentation
        sa.Column('photo_urls', sa.Text, nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('report_pdf_url', sa.String(500), nullable=True),
        
        # Certificate
        sa.Column('certificate_number', sa.String(100), nullable=True, index=True),
        sa.Column('certificate_issued_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('certificate_valid_until', sa.DateTime(timezone=True), nullable=True),
        
        # Status
        sa.Column('status', sa.String(50), default='Draft', index=True),
        
        # Re-appraisal
        sa.Column('previous_appraisal_id', sa.String(50), nullable=True, index=True),
        sa.Column('next_appraisal_due_date', sa.DateTime(timezone=True), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_appraisal_loan', 'appraisal_reports', ['tenant_id', 'gold_loan_id'])
    op.create_index('idx_appraisal_customer', 'appraisal_reports', ['tenant_id', 'customer_id'])
    op.create_index('idx_appraisal_date', 'appraisal_reports', ['tenant_id', 'appraisal_date'])
    op.create_index('idx_appraisal_status', 'appraisal_reports', ['tenant_id', 'status'])
    
    # ==================== Auction Bids ====================
    op.create_table(
        'auction_bids',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Bid details
        sa.Column('bid_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('auction_id', sa.String(50), nullable=False, index=True),
        sa.Column('bid_date', sa.DateTime(timezone=True), nullable=False),
        
        # Bidder
        sa.Column('bidder_name', sa.String(200), nullable=False),
        sa.Column('bidder_contact', sa.String(20), nullable=False),
        sa.Column('bidder_email', sa.String(200), nullable=True),
        sa.Column('bidder_pan', sa.String(20), nullable=True),
        sa.Column('bidder_address', sa.Text, nullable=True),
        
        # Registration
        sa.Column('bidder_registration_number', sa.String(50), nullable=True, index=True),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deposit_amount', sa.Numeric(15, 2), nullable=True),
        
        # Bid
        sa.Column('bid_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('bid_type', sa.String(50), default='Regular'),
        sa.Column('bid_rank', sa.Integer, nullable=True),
        
        # Status
        sa.Column('bid_status', sa.String(50), default='Submitted', index=True),
        
        # Winner
        sa.Column('is_winning_bid', sa.Boolean, default=False, index=True),
        sa.Column('won_date', sa.DateTime(timezone=True), nullable=True),
        
        # Payment
        sa.Column('payment_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_reference', sa.String(100), nullable=True),
        sa.Column('payment_status', sa.String(50), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_auction_bid_auction', 'auction_bids', ['tenant_id', 'auction_id'])
    op.create_index('idx_auction_bid_status', 'auction_bids', ['tenant_id', 'bid_status'])
    op.create_index('idx_auction_bid_winner', 'auction_bids', ['tenant_id', 'is_winning_bid'])
    
    # ==================== Auction Notices ====================
    op.create_table(
        'auction_notices',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Notice details
        sa.Column('notice_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('auction_id', sa.String(50), nullable=False, index=True),
        sa.Column('gold_loan_id', sa.String(50), nullable=False, index=True),
        sa.Column('customer_id', sa.String(50), nullable=False, index=True),
        
        # Notice type
        sa.Column('notice_type', sa.String(50), nullable=False),
        
        # Notice details
        sa.Column('notice_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notice_period_days', sa.Integer, nullable=False),
        sa.Column('response_due_date', sa.DateTime(timezone=True), nullable=False),
        
        # Delivery
        sa.Column('delivery_method', sa.String(50), nullable=False),
        
        # Delivery tracking
        sa.Column('sent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivery_status', sa.String(50), default='Pending', index=True),
        
        # Contact details
        sa.Column('delivery_address', sa.Text, nullable=True),
        sa.Column('delivery_email', sa.String(200), nullable=True),
        sa.Column('delivery_phone', sa.String(20), nullable=True),
        
        # Tracking
        sa.Column('tracking_number', sa.String(100), nullable=True),
        sa.Column('postal_reference', sa.String(100), nullable=True),
        
        # Response
        sa.Column('response_received', sa.Boolean, default=False),
        sa.Column('response_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_type', sa.String(50), nullable=True),
        
        # Document
        sa.Column('notice_document_url', sa.String(500), nullable=True),
        sa.Column('proof_of_delivery_url', sa.String(500), nullable=True),
        
        # Legal compliance
        sa.Column('legal_requirement_met', sa.Boolean, default=False),
        sa.Column('verified_by', sa.String(50), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        
        # Remarks
        sa.Column('remarks', sa.Text, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    op.create_index('idx_auction_notice_auction', 'auction_notices', ['tenant_id', 'auction_id'])
    op.create_index('idx_auction_notice_loan', 'auction_notices', ['tenant_id', 'gold_loan_id'])
    op.create_index('idx_auction_notice_status', 'auction_notices', ['tenant_id', 'delivery_status'])


def downgrade():
    """Remove all gold loan enhancement tables"""
    
    # Drop tables in reverse order
    op.drop_table('auction_notices')
    op.drop_table('auction_bids')
    op.drop_table('appraisal_reports')
    op.drop_table('purity_tests')
    op.drop_table('vault_transfers')
    op.drop_table('vault_inventory')
    op.drop_table('vault_locations')
    op.drop_table('gold_rate_history')
