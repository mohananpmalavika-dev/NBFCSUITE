"""CRM Customer Service Module - Ticket Management, Knowledge Base, SLA Tracking

Revision ID: 025_crm_customer_service
Revises: 024_previous_migration
Create Date: 2026-07-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '025_crm_customer_service'
down_revision = '024_previous_migration'  # Update with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    ticket_priority_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', 'critical', name='ticketpriority')
    ticket_priority_enum.create(op.get_bind(), checkfirst=True)
    
    ticket_status_enum = postgresql.ENUM('new', 'open', 'in_progress', 'pending_customer', 'pending_internal', 
                                          'resolved', 'closed', 'reopened', 'cancelled', name='ticketstatus')
    ticket_status_enum.create(op.get_bind(), checkfirst=True)
    
    ticket_category_enum = postgresql.ENUM('account', 'loan', 'deposit', 'payment', 'technical', 
                                            'complaint', 'inquiry', 'request', 'feedback', 'other', 
                                            name='ticketcategory')
    ticket_category_enum.create(op.get_bind(), checkfirst=True)
    
    ticket_channel_enum = postgresql.ENUM('phone', 'email', 'web_portal', 'mobile_app', 'chat', 
                                           'social_media', 'walk_in', 'whatsapp', name='ticketchannel')
    ticket_channel_enum.create(op.get_bind(), checkfirst=True)
    
    sla_status_enum = postgresql.ENUM('within_sla', 'approaching_breach', 'breached', 'paused', name='slastatus')
    sla_status_enum.create(op.get_bind(), checkfirst=True)
    
    kb_status_enum = postgresql.ENUM('draft', 'review', 'published', 'archived', name='knowledgebasestatus')
    kb_status_enum.create(op.get_bind(), checkfirst=True)
    
    article_category_enum = postgresql.ENUM('getting_started', 'account_management', 'loan_products', 
                                             'deposit_products', 'payments', 'troubleshooting', 'faq', 
                                             'policies', 'technical', 'other', name='articlecategory')
    article_category_enum.create(op.get_bind(), checkfirst=True)
    
    # Create SLA Policies table
    op.create_table('crm_sla_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('applies_to_priority', sa.JSON(), nullable=True),
        sa.Column('applies_to_category', sa.JSON(), nullable=True),
        sa.Column('applies_to_channel', sa.JSON(), nullable=True),
        sa.Column('first_response_time', sa.Integer(), nullable=False),
        sa.Column('resolution_time', sa.Integer(), nullable=False),
        sa.Column('escalation_time', sa.Integer(), nullable=True),
        sa.Column('business_hours_only', sa.Boolean(), nullable=True, default=True),
        sa.Column('business_start_hour', sa.Integer(), nullable=True, default=9),
        sa.Column('business_end_hour', sa.Integer(), nullable=True, default=18),
        sa.Column('include_weekends', sa.Boolean(), nullable=True, default=False),
        sa.Column('escalation_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('escalate_to_user_id', sa.Integer(), nullable=True),
        sa.Column('escalate_to_team', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('priority_order', sa.Integer(), nullable=True, default=0),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['escalate_to_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sla_policy_tenant', 'crm_sla_policies', ['tenant_id'])

    
    # Create Tickets table
    op.create_table('crm_tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_number', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(length=200), nullable=False),
        sa.Column('customer_email', sa.String(length=200), nullable=True),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', ticket_category_enum, nullable=False),
        sa.Column('priority', ticket_priority_enum, nullable=False),
        sa.Column('status', ticket_status_enum, nullable=False),
        sa.Column('channel', ticket_channel_enum, nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=True),
        sa.Column('assigned_to_team', sa.String(length=100), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('closed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('sla_policy_id', sa.Integer(), nullable=True),
        sa.Column('sla_status', sla_status_enum, nullable=True),
        sa.Column('sla_first_response_due', sa.DateTime(), nullable=True),
        sa.Column('sla_first_response_at', sa.DateTime(), nullable=True),
        sa.Column('sla_resolution_due', sa.DateTime(), nullable=True),
        sa.Column('sla_paused_duration', sa.Integer(), nullable=True, default=0),
        sa.Column('sla_breach_reason', sa.Text(), nullable=True),
        sa.Column('customer_satisfaction_rating', sa.Integer(), nullable=True),
        sa.Column('customer_feedback', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sla_policy_id'], ['crm_sla_policies.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ticket_number', 'crm_tickets', ['ticket_number'], unique=True)
    op.create_index('idx_ticket_customer', 'crm_tickets', ['customer_id'])
    op.create_index('idx_ticket_status', 'crm_tickets', ['status'])
    op.create_index('idx_ticket_priority', 'crm_tickets', ['priority'])
    op.create_index('idx_ticket_category', 'crm_tickets', ['category'])
    op.create_index('idx_ticket_assigned', 'crm_tickets', ['assigned_to_user_id'])
    op.create_index('idx_ticket_assigned_team', 'crm_tickets', ['assigned_to_team'])
    op.create_index('idx_ticket_sla_policy', 'crm_tickets', ['sla_policy_id'])
    op.create_index('idx_ticket_sla_status', 'crm_tickets', ['sla_status'])
    op.create_index('idx_ticket_customer_status', 'crm_tickets', ['customer_id', 'status'])
    op.create_index('idx_ticket_assigned_status', 'crm_tickets', ['assigned_to_user_id', 'status'])
    op.create_index('idx_ticket_priority_status', 'crm_tickets', ['priority', 'status'])
    op.create_index('idx_ticket_category_status', 'crm_tickets', ['category', 'status'])
    op.create_index('idx_ticket_sla_status_combined', 'crm_tickets', ['sla_status', 'status'])
    op.create_index('idx_ticket_created', 'crm_tickets', ['created_at'])
    op.create_index('idx_ticket_tenant', 'crm_tickets', ['tenant_id', 'status'])

    
    # Create Ticket Comments table
    op.create_table('crm_ticket_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_solution', sa.Boolean(), nullable=True, default=False),
        sa.Column('has_attachments', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['crm_tickets.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_comment_ticket', 'crm_ticket_comments', ['ticket_id', 'created_at'])
    
    # Create Ticket Attachments table
    op.create_table('crm_ticket_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('comment_id', sa.Integer(), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('uploaded_by_user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['crm_tickets.id'], ),
        sa.ForeignKeyConstraint(['comment_id'], ['crm_ticket_comments.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_attachment_ticket', 'crm_ticket_attachments', ['ticket_id'])
    op.create_index('idx_attachment_comment', 'crm_ticket_attachments', ['comment_id'])
    
    # Create Ticket Activities table
    op.create_table('crm_ticket_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['crm_tickets.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_activity_ticket', 'crm_ticket_activities', ['ticket_id'])
    op.create_index('idx_activity_created', 'crm_ticket_activities', ['created_at'])

    
    # Create Knowledge Base Articles table
    op.create_table('crm_knowledge_base',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('slug', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('category', article_category_enum, nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('status', kb_status_enum, nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('published_by_user_id', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_internal', sa.Boolean(), nullable=True, default=False),
        sa.Column('related_articles', sa.JSON(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True, default=0),
        sa.Column('helpful_count', sa.Integer(), nullable=True, default=0),
        sa.Column('not_helpful_count', sa.Integer(), nullable=True, default=0),
        sa.Column('average_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('meta_description', sa.String(length=500), nullable=True),
        sa.Column('meta_keywords', sa.String(length=500), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['published_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kb_article_number', 'crm_knowledge_base', ['article_number'], unique=True)
    op.create_index('idx_kb_slug', 'crm_knowledge_base', ['slug'], unique=True)
    op.create_index('idx_kb_category', 'crm_knowledge_base', ['category'])
    op.create_index('idx_kb_status', 'crm_knowledge_base', ['status'])
    op.create_index('idx_kb_status_category', 'crm_knowledge_base', ['status', 'category'])
    op.create_index('idx_kb_published', 'crm_knowledge_base', ['published_at'])
    op.create_index('idx_kb_tenant_status', 'crm_knowledge_base', ['tenant_id', 'status'])
    
    # Create Knowledge Base Feedback table
    op.create_table('crm_kb_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('is_helpful', sa.Boolean(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['crm_knowledge_base.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kb_feedback_article', 'crm_kb_feedback', ['article_id'])
    
    # Create Ticket Templates table
    op.create_table('crm_ticket_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_name', sa.String(length=200), nullable=False),
        sa.Column('template_code', sa.String(length=50), nullable=False),
        sa.Column('subject_template', sa.String(length=500), nullable=True),
        sa.Column('content_template', sa.Text(), nullable=False),
        sa.Column('category', ticket_category_enum, nullable=True),
        sa.Column('usage_type', sa.String(length=50), nullable=True),
        sa.Column('available_variables', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_template_code', 'crm_ticket_templates', ['template_code'], unique=True)
    op.create_index('idx_template_tenant', 'crm_ticket_templates', ['tenant_id'])


def downgrade():
    # Drop tables
    op.drop_table('crm_ticket_templates')
    op.drop_table('crm_kb_feedback')
    op.drop_table('crm_knowledge_base')
    op.drop_table('crm_ticket_activities')
    op.drop_table('crm_ticket_attachments')
    op.drop_table('crm_ticket_comments')
    op.drop_table('crm_tickets')
    op.drop_table('crm_sla_policies')
    
    # Drop enums
    sa.Enum(name='articlecategory').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='knowledgebasestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='slastatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ticketchannel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ticketcategory').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ticketstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ticketpriority').drop(op.get_bind(), checkfirst=True)
