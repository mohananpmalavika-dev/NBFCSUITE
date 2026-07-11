"""add crm lead management

Revision ID: crm_lead_001
Revises: 
Create Date: 2026-07-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'crm_lead_001'
down_revision = None  # Update this to point to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Create crm_leads table
    op.create_table(
        'crm_leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('lead_code', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('source_details', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('mobile', sa.String(length=20), nullable=False),
        sa.Column('alternate_mobile', sa.String(length=20), nullable=True),
        sa.Column('city_id', sa.Integer(), nullable=True),
        sa.Column('state_id', sa.Integer(), nullable=True),
        sa.Column('pincode', sa.String(length=10), nullable=True),
        sa.Column('product_interest', sa.String(length=100), nullable=True),
        sa.Column('loan_amount_required', sa.Numeric(15, 2), nullable=True),
        sa.Column('monthly_income', sa.Numeric(15, 2), nullable=True),
        sa.Column('occupation', sa.String(length=100), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('lead_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('score_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('lead_temperature', sa.String(length=20), nullable=False, server_default='cold'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='new'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('is_qualified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('qualification_reason', sa.Text(), nullable=True),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=True),
        sa.Column('assigned_to_branch_id', sa.Integer(), nullable=True),
        sa.Column('assigned_date', sa.DateTime(), nullable=True),
        sa.Column('auto_assigned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('assignment_rules_applied', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('last_contacted_date', sa.DateTime(), nullable=True),
        sa.Column('next_follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('follow_up_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('response_time_hours', sa.Integer(), nullable=True),
        sa.Column('is_converted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('converted_date', sa.DateTime(), nullable=True),
        sa.Column('converted_to_customer_id', sa.Integer(), nullable=True),
        sa.Column('converted_to_loan_application_id', sa.Integer(), nullable=True),
        sa.Column('conversion_time_hours', sa.Integer(), nullable=True),
        sa.Column('is_lost', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('lost_date', sa.DateTime(), nullable=True),
        sa.Column('lost_reason', sa.String(length=255), nullable=True),
        sa.Column('lost_remarks', sa.Text(), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('duplicate_of_lead_id', sa.Integer(), nullable=True),
        sa.Column('duplicate_checked_date', sa.DateTime(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('utm_source', sa.String(length=100), nullable=True),
        sa.Column('utm_medium', sa.String(length=100), nullable=True),
        sa.Column('utm_campaign', sa.String(length=100), nullable=True),
        sa.Column('utm_content', sa.String(length=255), nullable=True),
        sa.Column('referrer_url', sa.String(length=500), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assigned_to_branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['converted_to_customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['duplicate_of_lead_id'], ['crm_leads.id']),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id']),
        sa.ForeignKeyConstraint(['state_id'], ['states.id'])
    )
    
    # Create indexes
    op.create_index('idx_lead_code', 'crm_leads', ['lead_code'], unique=True)
    op.create_index('idx_lead_mobile', 'crm_leads', ['mobile'])
    op.create_index('idx_lead_email', 'crm_leads', ['email'])
    op.create_index('idx_lead_status', 'crm_leads', ['status'])
    op.create_index('idx_lead_score', 'crm_leads', ['lead_score'])
    op.create_index('idx_lead_status_assigned', 'crm_leads', ['status', 'assigned_to_user_id'])
    op.create_index('idx_lead_score_temp', 'crm_leads', ['lead_score', 'lead_temperature'])
    op.create_index('idx_lead_created', 'crm_leads', ['created_at'])
    op.create_index('idx_lead_mobile_email', 'crm_leads', ['mobile', 'email'])
    op.create_index('idx_lead_next_followup', 'crm_leads', ['next_follow_up_date', 'is_active'])
    op.create_index('idx_lead_active', 'crm_leads', ['is_active'])
    op.create_index('idx_lead_deleted', 'crm_leads', ['is_deleted'])
    op.create_index('idx_lead_converted', 'crm_leads', ['is_converted'])
    op.create_index('idx_lead_qualified', 'crm_leads', ['is_qualified'])


    # Create crm_lead_followups table
    op.create_table(
        'crm_lead_followups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('follow_up_type', sa.String(length=50), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(), nullable=False),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('outcome', sa.Text(), nullable=True),
        sa.Column('next_action', sa.Text(), nullable=True),
        sa.Column('customer_interested', sa.Boolean(), nullable=True),
        sa.Column('customer_response', sa.Text(), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reminder_sent_date', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('completed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('is_cancelled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cancellation_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lead_id'], ['crm_leads.id']),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['completed_by_user_id'], ['users.id'])
    )
    
    # Create indexes
    op.create_index('idx_followup_lead', 'crm_lead_followups', ['lead_id'])
    op.create_index('idx_followup_scheduled', 'crm_lead_followups', ['scheduled_date', 'status'])
    op.create_index('idx_followup_assigned', 'crm_lead_followups', ['assigned_to_user_id', 'status'])

    # Create crm_lead_activities table
    op.create_table(
        'crm_lead_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('lead_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('activity_title', sa.String(length=255), nullable=False),
        sa.Column('activity_description', sa.Text(), nullable=True),
        sa.Column('activity_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('performed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('performed_by_name', sa.String(length=255), nullable=True),
        sa.Column('old_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_system_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lead_id'], ['crm_leads.id']),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['users.id'])
    )
    
    # Create indexes
    op.create_index('idx_activity_lead', 'crm_lead_activities', ['lead_id', 'activity_date'])
    op.create_index('idx_activity_date_type', 'crm_lead_activities', ['activity_date', 'activity_type'])
    op.create_index('idx_activity_user', 'crm_lead_activities', ['performed_by_user_id'])

    # Create crm_lead_scoring_rules table
    op.create_table(
        'crm_lead_scoring_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('rule_name', sa.String(length=255), nullable=False),
        sa.Column('rule_description', sa.Text(), nullable=True),
        sa.Column('rule_category', sa.String(length=100), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('operator', sa.String(length=50), nullable=False),
        sa.Column('field_value', sa.String(length=255), nullable=True),
        sa.Column('score_points', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_executed_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_scoring_rule_active', 'crm_lead_scoring_rules', ['is_active', 'priority'])

    # Create crm_lead_assignment_rules table
    op.create_table(
        'crm_lead_assignment_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('rule_name', sa.String(length=255), nullable=False),
        sa.Column('rule_description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('conditions', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('assignment_type', sa.String(length=50), nullable=False),
        sa.Column('assign_to_user_id', sa.Integer(), nullable=True),
        sa.Column('assign_to_branch_id', sa.Integer(), nullable=True),
        sa.Column('assign_to_team', sa.String(length=100), nullable=True),
        sa.Column('max_leads_per_user', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_executed_date', sa.DateTime(), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['assign_to_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['assign_to_branch_id'], ['branches.id'])
    )
    
    # Create indexes
    op.create_index('idx_assignment_rule_active', 'crm_lead_assignment_rules', ['is_active', 'priority'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('crm_lead_assignment_rules')
    op.drop_table('crm_lead_scoring_rules')
    op.drop_table('crm_lead_activities')
    op.drop_table('crm_lead_followups')
    op.drop_table('crm_leads')
