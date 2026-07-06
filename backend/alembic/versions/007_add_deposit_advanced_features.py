"""Add deposit advanced features tables

Revision ID: 007
Revises: 006
Create Date: 2026-01-07

This migration adds support for advanced deposit features:
- Standing Instructions (auto-debit, sweep-in/out)
- Account Freeze Management
- Lien Marking (loan collateral)
- Joint Account Holders
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add deposit advanced features tables"""
    
    # 1. Standing Instructions Table
    op.create_table(
        'deposit_standing_instructions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('deposit_account_id', sa.Integer(), nullable=False),
        
        # Instruction Details
        sa.Column('instruction_type', sa.String(length=50), nullable=False),
        # Types: auto_debit, sweep_in, sweep_out, recurring_transfer
        sa.Column('instruction_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Source/Target Accounts
        sa.Column('source_account', sa.String(length=50), nullable=True),
        sa.Column('target_account', sa.String(length=50), nullable=True),
        
        # Amount Details
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('min_balance_threshold', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('max_balance_threshold', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Execution Details
        sa.Column('frequency', sa.String(length=50), nullable=False),
        # Frequencies: daily, weekly, monthly, on_threshold
        sa.Column('execution_day', sa.Integer(), nullable=True),  # Day of month (1-31)
        sa.Column('next_execution_date', sa.Date(), nullable=True),
        sa.Column('last_execution_date', sa.Date(), nullable=True),
        sa.Column('execution_count', sa.Integer(), default=0),
        
        # Status
        sa.Column('status', sa.String(length=50), default='active', nullable=False),
        # Status: active, suspended, cancelled, completed
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        
        # Execution History
        sa.Column('last_execution_status', sa.String(length=50), nullable=True),
        sa.Column('last_error_message', sa.Text(), nullable=True),
        sa.Column('success_count', sa.Integer(), default=0),
        sa.Column('failure_count', sa.Integer(), default=0),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['deposit_account_id'], ['deposit_accounts.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    
    # Create indexes for standing instructions
    op.create_index('ix_standing_instructions_tenant', 'deposit_standing_instructions', ['tenant_id'])
    op.create_index('ix_standing_instructions_account', 'deposit_standing_instructions', ['deposit_account_id'])
    op.create_index('ix_standing_instructions_status', 'deposit_standing_instructions', ['status'])
    op.create_index('ix_standing_instructions_next_exec', 'deposit_standing_instructions', ['next_execution_date'])
    
    # 2. Account Freeze Table
    op.create_table(
        'deposit_account_freezes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('deposit_account_id', sa.Integer(), nullable=False),
        
        # Freeze Details
        sa.Column('freeze_type', sa.String(length=50), nullable=False),
        # Types: debit_freeze, credit_freeze, full_freeze
        sa.Column('freeze_reason', sa.String(length=500), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        
        # Status
        sa.Column('status', sa.String(length=50), default='active', nullable=False),
        # Status: active, released
        sa.Column('freeze_date', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('release_date', sa.DateTime(), nullable=True),
        sa.Column('release_reason', sa.String(length=500), nullable=True),
        
        # Authorization
        sa.Column('frozen_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('released_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Additional Details
        sa.Column('remarks', sa.Text(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['deposit_account_id'], ['deposit_accounts.id']),
        sa.ForeignKeyConstraint(['frozen_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['released_by'], ['users.id'])
    )
    
    # Create indexes for account freezes
    op.create_index('ix_account_freezes_tenant', 'deposit_account_freezes', ['tenant_id'])
    op.create_index('ix_account_freezes_account', 'deposit_account_freezes', ['deposit_account_id'])
    op.create_index('ix_account_freezes_status', 'deposit_account_freezes', ['status'])
    
    # 3. Account Lien Table
    op.create_table(
        'deposit_account_liens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('deposit_account_id', sa.Integer(), nullable=False),
        
        # Lien Details
        sa.Column('lien_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('lien_reason', sa.String(length=500), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=False),
        # Types: loan, legal, court_order, other
        sa.Column('reference_number', sa.String(length=100), nullable=False),
        sa.Column('reference_id', sa.Integer(), nullable=True),  # Loan ID or other reference
        
        # Status
        sa.Column('status', sa.String(length=50), default='active', nullable=False),
        # Status: active, released, partial_released
        sa.Column('lien_date', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('release_date', sa.DateTime(), nullable=True),
        sa.Column('released_amount', sa.Numeric(precision=15, scale=2), default=0),
        
        # Authorization
        sa.Column('marked_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('released_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Additional Details
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['deposit_account_id'], ['deposit_accounts.id']),
        sa.ForeignKeyConstraint(['marked_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['released_by'], ['users.id'])
    )
    
    # Create indexes for account liens
    op.create_index('ix_account_liens_tenant', 'deposit_account_liens', ['tenant_id'])
    op.create_index('ix_account_liens_account', 'deposit_account_liens', ['deposit_account_id'])
    op.create_index('ix_account_liens_status', 'deposit_account_liens', ['status'])
    op.create_index('ix_account_liens_reference', 'deposit_account_liens', ['reference_number'])
    
    # 4. Joint Account Holders Table
    op.create_table(
        'deposit_joint_holders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('deposit_account_id', sa.Integer(), nullable=False),
        
        # Holder Details
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('holder_type', sa.String(length=50), default='joint', nullable=False),
        # Types: primary, joint, guardian, power_of_attorney
        sa.Column('holder_name', sa.String(length=200), nullable=False),
        sa.Column('relationship', sa.String(length=100), nullable=True),
        
        # Operating Mode
        sa.Column('operation_mode', sa.String(length=50), nullable=False),
        # Modes: either_or_survivor, jointly, anyone, former_or_survivor
        sa.Column('sequence_number', sa.Integer(), default=1),
        sa.Column('share_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        
        # Authority
        sa.Column('can_operate', sa.Boolean(), default=True),
        sa.Column('can_nominate', sa.Boolean(), default=False),
        sa.Column('can_close', sa.Boolean(), default=False),
        
        # KYC Details
        sa.Column('id_proof_type', sa.String(length=100), nullable=True),
        sa.Column('id_proof_number', sa.String(length=100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        
        # Status
        sa.Column('status', sa.String(length=50), default='active', nullable=False),
        # Status: active, inactive, removed
        sa.Column('added_date', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('removed_date', sa.DateTime(), nullable=True),
        sa.Column('removal_reason', sa.String(length=500), nullable=True),
        
        # Authorization
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('removed_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Audit Fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['deposit_account_id'], ['deposit_accounts.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['added_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['removed_by'], ['users.id'])
    )
    
    # Create indexes for joint holders
    op.create_index('ix_joint_holders_tenant', 'deposit_joint_holders', ['tenant_id'])
    op.create_index('ix_joint_holders_account', 'deposit_joint_holders', ['deposit_account_id'])
    op.create_index('ix_joint_holders_customer', 'deposit_joint_holders', ['customer_id'])
    op.create_index('ix_joint_holders_status', 'deposit_joint_holders', ['status'])


def downgrade() -> None:
    """Remove deposit advanced features tables"""
    
    # Drop tables in reverse order
    op.drop_table('deposit_joint_holders')
    op.drop_table('deposit_account_liens')
    op.drop_table('deposit_account_freezes')
    op.drop_table('deposit_standing_instructions')
