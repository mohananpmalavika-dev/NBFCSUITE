"""add procurement module

Revision ID: 013_add_procurement_module
Revises: 012_add_hrms_loans_module
Create Date: 2026-07-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '013_add_procurement_module'
down_revision = '012_add_hrms_loans_module'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    vendor_type_enum = postgresql.ENUM(
        'supplier', 'contractor', 'service_provider', 'manufacturer',
        'wholesaler', 'retailer', 'consultant',
        name='vendortype'
    )
    vendor_type_enum.create(op.get_bind(), checkfirst=True)
    
    vendor_status_enum = postgresql.ENUM(
        'active', 'inactive', 'blacklisted', 'suspended', 'under_review',
        name='vendorstatus'
    )
    vendor_status_enum.create(op.get_bind(), checkfirst=True)
    
    payment_terms_enum = postgresql.ENUM(
        'immediate', 'net_15', 'net_30', 'net_45', 'net_60', 'net_90',
        'advance', 'cod', 'custom',
        name='paymentterms'
    )
    payment_terms_enum.create(op.get_bind(), checkfirst=True)
    
    requisition_status_enum = postgresql.ENUM(
        'draft', 'submitted', 'approved', 'rejected', 'cancelled',
        'converted_to_po', 'partially_converted',
        name='requisitionstatus'
    )
    requisition_status_enum.create(op.get_bind(), checkfirst=True)
    
    requisition_priority_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'urgent',
        name='requisitionpriority'
    )
    requisition_priority_enum.create(op.get_bind(), checkfirst=True)
    
    rfq_status_enum = postgresql.ENUM(
        'draft', 'sent', 'response_received', 'closed', 'cancelled',
        name='rfqstatus'
    )
    rfq_status_enum.create(op.get_bind(), checkfirst=True)
    
    po_status_enum = postgresql.ENUM(
        'draft', 'approved', 'sent_to_vendor', 'acknowledged', 'in_progress',
        'partially_received', 'fully_received', 'closed', 'cancelled',
        name='postatus'
    )
    po_status_enum.create(op.get_bind(), checkfirst=True)
    
    grn_status_enum = postgresql.ENUM(
        'draft', 'received', 'quality_check_pending', 'quality_check_passed',
        'quality_check_failed', 'accepted', 'rejected', 'partially_accepted',
        name='grnstatus'
    )
    grn_status_enum.create(op.get_bind(), checkfirst=True)
    
    invoice_status_enum = postgresql.ENUM(
        'draft', 'submitted', 'under_verification', 'matched', 'mismatch',
        'approved', 'rejected', 'paid', 'partially_paid',
        name='invoicestatus'
    )
    invoice_status_enum.create(op.get_bind(), checkfirst=True)
    
    invoice_matching_status_enum = postgresql.ENUM(
        'not_matched', 'two_way_matched', 'three_way_matched',
        'price_mismatch', 'quantity_mismatch', 'tolerance_mismatch',
        name='invoicematchingstatus'
    )
    invoice_matching_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('vendor_code', sa.String(50), nullable=False),
        sa.Column('vendor_name', sa.String(200), nullable=False),
        sa.Column('vendor_type', vendor_type_enum, nullable=False),
        sa.Column('status', vendor_status_enum, nullable=False),
        sa.Column('contact_person', sa.String(100), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('website', sa.String(200), nullable=True),
        sa.Column('address_line1', sa.String(200), nullable=True),
        sa.Column('address_line2', sa.String(200), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), default='India'),
        sa.Column('pan_number', sa.String(10), nullable=True),
        sa.Column('gst_number', sa.String(15), nullable=True),
        sa.Column('tan_number', sa.String(10), nullable=True),
        sa.Column('msme_registration', sa.String(50), nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('bank_branch', sa.String(100), nullable=True),
        sa.Column('account_number', sa.String(50), nullable=True),
        sa.Column('ifsc_code', sa.String(11), nullable=True),
        sa.Column('account_holder_name', sa.String(100), nullable=True),
        sa.Column('payment_terms', payment_terms_enum, nullable=False),
        sa.Column('credit_limit', sa.Numeric(15, 2), default=0.00),
        sa.Column('credit_period_days', sa.Integer(), default=30),
        sa.Column('overall_rating', sa.Numeric(3, 2), default=0.00),
        sa.Column('quality_rating', sa.Numeric(3, 2), default=0.00),
        sa.Column('delivery_rating', sa.Numeric(3, 2), default=0.00),
        sa.Column('price_rating', sa.Numeric(3, 2), default=0.00),
        sa.Column('service_rating', sa.Numeric(3, 2), default=0.00),
        sa.Column('total_orders', sa.Integer(), default=0),
        sa.Column('on_time_deliveries', sa.Integer(), default=0),
        sa.Column('products_services', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('blacklist_reason', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vendor_tenant_code', 'vendors', ['tenant_id', 'vendor_code'], unique=True)
    op.create_index('ix_vendor_status', 'vendors', ['status'])
    op.create_index('ix_vendor_gst', 'vendors', ['gst_number'])
    
    # Create purchase_requisitions table
    op.create_table(
        'purchase_requisitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('requisition_number', sa.String(50), nullable=False),
        sa.Column('requisition_date', sa.Date(), nullable=False),
        sa.Column('required_by_date', sa.Date(), nullable=False),
        sa.Column('status', requisition_status_enum, nullable=False),
        sa.Column('priority', requisition_priority_enum, nullable=False),
        sa.Column('department', sa.String(100), nullable=False),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requester_name', sa.String(100), nullable=False),
        sa.Column('purpose', sa.Text(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('budget_code', sa.String(50), nullable=True),
        sa.Column('estimated_total', sa.Numeric(15, 2), default=0.00),
        sa.Column('preferred_vendor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['preferred_vendor_id'], ['vendors.id'])
    )
    op.create_index('ix_pr_tenant_number', 'purchase_requisitions', ['tenant_id', 'requisition_number'], unique=True)
    op.create_index('ix_pr_status', 'purchase_requisitions', ['status'])
    op.create_index('ix_pr_date', 'purchase_requisitions', ['requisition_date'])
    
    # Create purchase_requisition_items table
    op.create_table(
        'purchase_requisition_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requisition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(50), nullable=True),
        sa.Column('item_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('specification', sa.Text(), nullable=True),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit_of_measure', sa.String(20), nullable=False),
        sa.Column('estimated_unit_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('estimated_total_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('quantity_converted', sa.Numeric(10, 2), default=0.00),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['requisition_id'], ['purchase_requisitions.id'])
    )
    op.create_index('ix_pri_requisition', 'purchase_requisition_items', ['requisition_id'])
    
    # Create rfqs table
    op.create_table(
        'rfqs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('rfq_number', sa.String(50), nullable=False),
        sa.Column('rfq_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', rfq_status_enum, nullable=False),
        sa.Column('requisition_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['requisition_id'], ['purchase_requisitions.id'])
    )
    op.create_index('ix_rfq_tenant_number', 'rfqs', ['tenant_id', 'rfq_number'], unique=True)
    op.create_index('ix_rfq_status', 'rfqs', ['status'])
    
    # Create rfq_items table
    op.create_table(
        'rfq_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rfq_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(50), nullable=True),
        sa.Column('item_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('specification', sa.Text(), nullable=True),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit_of_measure', sa.String(20), nullable=False),
        sa.Column('requisition_item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rfq_id'], ['rfqs.id'])
    )
    op.create_index('ix_rfq_item_rfq', 'rfq_items', ['rfq_id'])
    
    # Create rfq_vendors table
    op.create_table(
        'rfq_vendors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rfq_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invited_at', sa.DateTime(), nullable=False),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.Column('is_responded', sa.Boolean(), default=False),
        sa.Column('is_selected', sa.Boolean(), default=False),
        sa.Column('selection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rfq_id'], ['rfqs.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'])
    )
    op.create_index('ix_rfq_vendor_rfq', 'rfq_vendors', ['rfq_id'])
    op.create_index('ix_rfq_vendor_vendor', 'rfq_vendors', ['vendor_id'])
    
    # Create vendor_quotes table
    op.create_table(
        'vendor_quotes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rfq_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('delivery_days', sa.Integer(), nullable=True),
        sa.Column('warranty_months', sa.Integer(), nullable=True),
        sa.Column('tax_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('tax_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('total_with_tax', sa.Numeric(15, 2), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('attachments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['rfq_item_id'], ['rfq_items.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'])
    )
    op.create_index('ix_vendor_quote_rfq_item', 'vendor_quotes', ['rfq_item_id'])
    op.create_index('ix_vendor_quote_vendor', 'vendor_quotes', ['vendor_id'])
    
    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('po_number', sa.String(50), nullable=False),
        sa.Column('po_date', sa.Date(), nullable=False),
        sa.Column('expected_delivery_date', sa.Date(), nullable=False),
        sa.Column('status', po_status_enum, nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rfq_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('requisition_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('delivery_address_line1', sa.String(200), nullable=True),
        sa.Column('delivery_address_line2', sa.String(200), nullable=True),
        sa.Column('delivery_city', sa.String(100), nullable=True),
        sa.Column('delivery_state', sa.String(100), nullable=True),
        sa.Column('delivery_pincode', sa.String(10), nullable=True),
        sa.Column('delivery_country', sa.String(100), default='India'),
        sa.Column('delivery_contact_person', sa.String(100), nullable=True),
        sa.Column('delivery_contact_phone', sa.String(20), nullable=True),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('discount_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('payment_terms', payment_terms_enum, nullable=False),
        sa.Column('advance_payment_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('advance_payment_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_by_vendor', sa.Boolean(), default=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['rfq_id'], ['rfqs.id'])
    )
    op.create_index('ix_po_tenant_number', 'purchase_orders', ['tenant_id', 'po_number'], unique=True)
    op.create_index('ix_po_vendor', 'purchase_orders', ['vendor_id'])
    op.create_index('ix_po_status', 'purchase_orders', ['status'])
    op.create_index('ix_po_date', 'purchase_orders', ['po_date'])
    
    # Create purchase_order_items table
    op.create_table(
        'purchase_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('po_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(50), nullable=True),
        sa.Column('item_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('specification', sa.Text(), nullable=True),
        sa.Column('ordered_quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('received_quantity', sa.Numeric(10, 2), default=0.00),
        sa.Column('unit_of_measure', sa.String(20), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('tax_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('discount_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('discount_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('rfq_item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('requisition_item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id'])
    )
    op.create_index('ix_po_item_po', 'purchase_order_items', ['po_id'])
    
    # Create goods_receipt_notes table
    op.create_table(
        'goods_receipt_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('grn_number', sa.String(50), nullable=False),
        sa.Column('grn_date', sa.Date(), nullable=False),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('status', grn_status_enum, nullable=False),
        sa.Column('po_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('challan_number', sa.String(50), nullable=True),
        sa.Column('challan_date', sa.Date(), nullable=True),
        sa.Column('transporter_name', sa.String(100), nullable=True),
        sa.Column('vehicle_number', sa.String(20), nullable=True),
        sa.Column('lr_number', sa.String(50), nullable=True),
        sa.Column('quality_check_required', sa.Boolean(), default=True),
        sa.Column('quality_checked_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quality_checked_at', sa.DateTime(), nullable=True),
        sa.Column('quality_remarks', sa.Text(), nullable=True),
        sa.Column('received_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('warehouse_location', sa.String(100), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id'])
    )
    op.create_index('ix_grn_tenant_number', 'goods_receipt_notes', ['tenant_id', 'grn_number'], unique=True)
    op.create_index('ix_grn_po', 'goods_receipt_notes', ['po_id'])
    op.create_index('ix_grn_status', 'goods_receipt_notes', ['status'])
    op.create_index('ix_grn_date', 'goods_receipt_notes', ['grn_date'])
    
    # Create grn_items table
    op.create_table(
        'grn_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('grn_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('po_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(50), nullable=True),
        sa.Column('item_name', sa.String(200), nullable=False),
        sa.Column('ordered_quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('received_quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('accepted_quantity', sa.Numeric(10, 2), default=0.00),
        sa.Column('rejected_quantity', sa.Numeric(10, 2), default=0.00),
        sa.Column('unit_of_measure', sa.String(20), nullable=False),
        sa.Column('quality_status', sa.String(20), nullable=True),
        sa.Column('quality_remarks', sa.Text(), nullable=True),
        sa.Column('batch_number', sa.String(50), nullable=True),
        sa.Column('serial_numbers', sa.Text(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['grn_id'], ['goods_receipt_notes.id']),
        sa.ForeignKeyConstraint(['po_item_id'], ['purchase_order_items.id'])
    )
    op.create_index('ix_grn_item_grn', 'grn_items', ['grn_id'])
    op.create_index('ix_grn_item_po_item', 'grn_items', ['po_item_id'])
    
    # Create vendor_invoices table
    op.create_table(
        'vendor_invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('vendor_invoice_number', sa.String(50), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', invoice_status_enum, nullable=False),
        sa.Column('matching_status', invoice_matching_status_enum, nullable=False),
        sa.Column('po_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('grn_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('other_charges', sa.Numeric(15, 2), default=0.00),
        sa.Column('discount_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('balance_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('gst_number', sa.String(15), nullable=True),
        sa.Column('cgst_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('sgst_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('igst_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('po_amount_variance', sa.Numeric(15, 2), default=0.00),
        sa.Column('grn_quantity_variance', sa.Numeric(10, 2), default=0.00),
        sa.Column('tolerance_percentage', sa.Numeric(5, 2), default=5.00),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('invoice_file_url', sa.String(500), nullable=True),
        sa.Column('supporting_documents', sa.Text(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id']),
        sa.ForeignKeyConstraint(['grn_id'], ['goods_receipt_notes.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'])
    )
    op.create_index('ix_vendor_invoice_tenant_number', 'vendor_invoices', ['tenant_id', 'invoice_number'], unique=True)
    op.create_index('ix_vendor_invoice_vendor_number', 'vendor_invoices', ['vendor_id', 'vendor_invoice_number'])
    op.create_index('ix_vendor_invoice_po', 'vendor_invoices', ['po_id'])
    op.create_index('ix_vendor_invoice_status', 'vendor_invoices', ['status'])
    op.create_index('ix_vendor_invoice_date', 'vendor_invoices', ['invoice_date'])
    
    # Create vendor_invoice_items table
    op.create_table(
        'vendor_invoice_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('po_item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('item_code', sa.String(50), nullable=True),
        sa.Column('item_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit_of_measure', sa.String(20), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('tax_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('discount_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('discount_amount', sa.Numeric(15, 2), default=0.00),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['invoice_id'], ['vendor_invoices.id']),
        sa.ForeignKeyConstraint(['po_item_id'], ['purchase_order_items.id'])
    )
    op.create_index('ix_vendor_invoice_item_invoice', 'vendor_invoice_items', ['invoice_id'])
    
    # Create vendor_ratings table
    op.create_table(
        'vendor_ratings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('po_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rating_date', sa.Date(), nullable=False),
        sa.Column('rating_period_start', sa.Date(), nullable=True),
        sa.Column('rating_period_end', sa.Date(), nullable=True),
        sa.Column('quality_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('delivery_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('price_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('service_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('communication_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('overall_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('delivery_status', sa.String(20), nullable=True),
        sa.Column('days_late', sa.Integer(), default=0),
        sa.Column('defect_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('rejection_percentage', sa.Numeric(5, 2), default=0.00),
        sa.Column('positive_points', sa.Text(), nullable=True),
        sa.Column('improvement_areas', sa.Text(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('rated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rated_by_name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.id']),
        sa.CheckConstraint('quality_rating >= 0 AND quality_rating <= 5', name='check_quality_rating'),
        sa.CheckConstraint('delivery_rating >= 0 AND delivery_rating <= 5', name='check_delivery_rating'),
        sa.CheckConstraint('price_rating >= 0 AND price_rating <= 5', name='check_price_rating'),
        sa.CheckConstraint('service_rating >= 0 AND service_rating <= 5', name='check_service_rating'),
        sa.CheckConstraint('communication_rating >= 0 AND communication_rating <= 5', name='check_communication_rating'),
        sa.CheckConstraint('overall_rating >= 0 AND overall_rating <= 5', name='check_overall_rating')
    )
    op.create_index('ix_vendor_rating_vendor', 'vendor_ratings', ['vendor_id'])
    op.create_index('ix_vendor_rating_date', 'vendor_ratings', ['rating_date'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('vendor_ratings')
    op.drop_table('vendor_invoice_items')
    op.drop_table('vendor_invoices')
    op.drop_table('grn_items')
    op.drop_table('goods_receipt_notes')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('vendor_quotes')
    op.drop_table('rfq_vendors')
    op.drop_table('rfq_items')
    op.drop_table('rfqs')
    op.drop_table('purchase_requisition_items')
    op.drop_table('purchase_requisitions')
    op.drop_table('vendors')
    
    # Drop enums
    postgresql.ENUM(name='invoicematchingstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='invoicestatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='grnstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='postatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='rfqstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='requisitionpriority').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='requisitionstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='paymentterms').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='vendorstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='vendortype').drop(op.get_bind(), checkfirst=True)
