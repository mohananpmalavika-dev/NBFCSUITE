"""add grievance tables

Revision ID: 006_add_grievance_tables
Revises: 005_add_insurance_tables
Create Date: 2026-07-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_grievance_tables'
down_revision = '005_add_insurance_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create complaints table
    op.create_table(
        'complaints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('complaint_number', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(length=200), nullable=True),
        sa.Column('customer_email', sa.String(length=100), nullable=True),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.Enum('PRODUCT_SERVICE', 'ACCOUNT_MANAGEMENT', 'LOAN_DISBURSEMENT', 'COLLECTION_HARASSMENT', 'INTEREST_CHARGES', 'DOCUMENT_ISSUES', 'BRANCH_SERVICE', 'DIGITAL_BANKING', 'STAFF_BEHAVIOR', 'FRAUD_SECURITY', 'REGULATORY', 'OTHER', name='complaintcategory'), nullable=False),
        sa.Column('sub_category', sa.String(length=100), nullable=True),
        sa.Column('subject', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('channel', sa.Enum('EMAIL', 'PHONE', 'WEB_PORTAL', 'MOBILE_APP', 'BRANCH_VISIT', 'SOCIAL_MEDIA', 'LETTER', 'SMS', 'WHATSAPP', 'CHATBOT', name='channeltype'), nullable=False),
        sa.Column('source_reference', sa.String(length=200), nullable=True),
        sa.Column('status', sa.Enum('REGISTERED', 'ACKNOWLEDGED', 'IN_PROGRESS', 'UNDER_REVIEW', 'RESOLVED', 'CLOSED', 'REOPENED', 'ESCALATED', 'REJECTED', name='complaintstatus'), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'URGENT', name='complaintpriority'), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('assigned_department', sa.String(length=100), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('registered_date', sa.DateTime(), nullable=False),
        sa.Column('acknowledged_date', sa.DateTime(), nullable=True),
        sa.Column('target_resolution_date', sa.DateTime(), nullable=True),
        sa.Column('actual_resolution_date', sa.DateTime(), nullable=True),
        sa.Column('closed_date', sa.DateTime(), nullable=True),
        sa.Column('sla_hours', sa.Integer(), nullable=True),
        sa.Column('sla_breach', sa.Boolean(), nullable=True),
        sa.Column('sla_breach_hours', sa.Integer(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolution_remarks', sa.Text(), nullable=True),
        sa.Column('customer_satisfaction', sa.Integer(), nullable=True),
        sa.Column('compensation_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('compensation_paid', sa.Boolean(), nullable=True),
        sa.Column('escalation_level', sa.Enum('LEVEL_0', 'LEVEL_1', 'LEVEL_2', 'LEVEL_3', 'LEVEL_4', 'LEVEL_5', 'OMBUDSMAN', name='escalationlevel'), nullable=True),
        sa.Column('escalated_to_ombudsman', sa.Boolean(), nullable=True),
        sa.Column('is_regulatory', sa.Boolean(), nullable=True),
        sa.Column('is_repeat', sa.Boolean(), nullable=True),
        sa.Column('previous_complaint_id', sa.Integer(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('attachments', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['previous_complaint_id'], ['complaints.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_assigned_to'), 'complaints', ['assigned_to'], unique=False)
    op.create_index(op.f('ix_complaints_category'), 'complaints', ['category'], unique=False)
    op.create_index(op.f('ix_complaints_channel'), 'complaints', ['channel'], unique=False)
    op.create_index(op.f('ix_complaints_complaint_number'), 'complaints', ['complaint_number'], unique=True)
    op.create_index(op.f('ix_complaints_customer_id'), 'complaints', ['customer_id'], unique=False)
    op.create_index(op.f('ix_complaints_id'), 'complaints', ['id'], unique=False)
    op.create_index(op.f('ix_complaints_priority'), 'complaints', ['priority'], unique=False)
    op.create_index(op.f('ix_complaints_status'), 'complaints', ['status'], unique=False)
    op.create_index('idx_complaint_customer_status', 'complaints', ['customer_id', 'status'], unique=False)
    op.create_index('idx_complaint_assigned_status', 'complaints', ['assigned_to', 'status'], unique=False)
    op.create_index('idx_complaint_category_status', 'complaints', ['category', 'status'], unique=False)
    op.create_index('idx_complaint_sla_breach', 'complaints', ['sla_breach', 'status'], unique=False)
    op.create_index('idx_complaint_registered_date', 'complaints', ['registered_date'], unique=False)

    # Create complaint_channels table
    op.create_table(
        'complaint_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('complaint_id', sa.Integer(), nullable=False),
        sa.Column('channel_type', sa.Enum('EMAIL', 'PHONE', 'WEB_PORTAL', 'MOBILE_APP', 'BRANCH_VISIT', 'SOCIAL_MEDIA', 'LETTER', 'SMS', 'WHATSAPP', 'CHATBOT', name='channeltype'), nullable=False),
        sa.Column('communication_date', sa.DateTime(), nullable=False),
        sa.Column('direction', sa.String(length=20), nullable=True),
        sa.Column('subject', sa.String(length=300), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('from_address', sa.String(length=200), nullable=True),
        sa.Column('to_address', sa.String(length=200), nullable=True),
        sa.Column('is_customer_initiated', sa.Boolean(), nullable=True),
        sa.Column('requires_response', sa.Boolean(), nullable=True),
        sa.Column('response_sent', sa.Boolean(), nullable=True),
        sa.Column('attachments', sa.Text(), nullable=True),
        sa.Column('handled_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['handled_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_channels_complaint_id'), 'complaint_channels', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_complaint_channels_id'), 'complaint_channels', ['id'], unique=False)

    # Create complaint_escalations table
    op.create_table(
        'complaint_escalations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('complaint_id', sa.Integer(), nullable=False),
        sa.Column('escalation_level', sa.Enum('LEVEL_0', 'LEVEL_1', 'LEVEL_2', 'LEVEL_3', 'LEVEL_4', 'LEVEL_5', 'OMBUDSMAN', name='escalationlevel'), nullable=False),
        sa.Column('escalation_number', sa.Integer(), nullable=True),
        sa.Column('escalation_reason', sa.String(length=50), nullable=True),
        sa.Column('reason_details', sa.Text(), nullable=True),
        sa.Column('is_auto_escalated', sa.Boolean(), nullable=True),
        sa.Column('escalated_from', sa.Integer(), nullable=True),
        sa.Column('escalated_to', sa.Integer(), nullable=True),
        sa.Column('escalated_to_department', sa.String(length=100), nullable=True),
        sa.Column('escalated_at', sa.DateTime(), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('escalation_sla_hours', sa.Integer(), nullable=True),
        sa.Column('escalation_sla_breach', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('action_taken', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['escalated_from'], ['users.id'], ),
        sa.ForeignKeyConstraint(['escalated_to'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_escalations_complaint_id'), 'complaint_escalations', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_complaint_escalations_escalated_to'), 'complaint_escalations', ['escalated_to'], unique=False)
    op.create_index(op.f('ix_complaint_escalations_escalation_level'), 'complaint_escalations', ['escalation_level'], unique=False)
    op.create_index(op.f('ix_complaint_escalations_id'), 'complaint_escalations', ['id'], unique=False)
    op.create_index('idx_escalation_complaint_level', 'complaint_escalations', ['complaint_id', 'escalation_level'], unique=False)
    op.create_index('idx_escalation_assigned_to', 'complaint_escalations', ['escalated_to', 'status'], unique=False)

    # Create complaint_sla table
    op.create_table(
        'complaint_sla',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('PRODUCT_SERVICE', 'ACCOUNT_MANAGEMENT', 'LOAN_DISBURSEMENT', 'COLLECTION_HARASSMENT', 'INTEREST_CHARGES', 'DOCUMENT_ISSUES', 'BRANCH_SERVICE', 'DIGITAL_BANKING', 'STAFF_BEHAVIOR', 'FRAUD_SECURITY', 'REGULATORY', 'OTHER', name='complaintcategory'), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'URGENT', name='complaintpriority'), nullable=True),
        sa.Column('channel', sa.Enum('EMAIL', 'PHONE', 'WEB_PORTAL', 'MOBILE_APP', 'BRANCH_VISIT', 'SOCIAL_MEDIA', 'LETTER', 'SMS', 'WHATSAPP', 'CHATBOT', name='channeltype'), nullable=True),
        sa.Column('acknowledgement_hours', sa.Integer(), nullable=True),
        sa.Column('resolution_hours', sa.Integer(), nullable=True),
        sa.Column('escalation_hours', sa.Integer(), nullable=True),
        sa.Column('auto_escalate', sa.Boolean(), nullable=True),
        sa.Column('escalation_level_1_hours', sa.Integer(), nullable=True),
        sa.Column('escalation_level_2_hours', sa.Integer(), nullable=True),
        sa.Column('escalation_level_3_hours', sa.Integer(), nullable=True),
        sa.Column('send_reminder_before_hours', sa.Integer(), nullable=True),
        sa.Column('notify_customer', sa.Boolean(), nullable=True),
        sa.Column('notify_manager', sa.Boolean(), nullable=True),
        sa.Column('is_regulatory_complaint', sa.Boolean(), nullable=True),
        sa.Column('regulatory_timeline_days', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_sla_category'), 'complaint_sla', ['category'], unique=False)
    op.create_index(op.f('ix_complaint_sla_id'), 'complaint_sla', ['id'], unique=False)
    op.create_index(op.f('ix_complaint_sla_priority'), 'complaint_sla', ['priority'], unique=False)
    op.create_index('idx_sla_category_priority', 'complaint_sla', ['category', 'priority', 'is_active'], unique=False)

    # Create ombudsman_cases table
    op.create_table(
        'ombudsman_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('complaint_id', sa.Integer(), nullable=False),
        sa.Column('ombudsman_case_number', sa.String(length=100), nullable=True),
        sa.Column('ombudsman_office', sa.String(length=200), nullable=True),
        sa.Column('submitted_date', sa.DateTime(), nullable=True),
        sa.Column('submission_reference', sa.String(length=100), nullable=True),
        sa.Column('grounds_of_complaint', sa.Text(), nullable=True),
        sa.Column('documents_submitted', sa.Text(), nullable=True),
        sa.Column('supporting_evidence', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SUBMITTED', 'UNDER_REVIEW', 'HEARING_SCHEDULED', 'AWARD_ISSUED', 'CLOSED', 'WITHDRAWN', name='ombudsmanstatus'), nullable=True),
        sa.Column('acknowledgement_date', sa.DateTime(), nullable=True),
        sa.Column('hearing_date', sa.DateTime(), nullable=True),
        sa.Column('award_date', sa.DateTime(), nullable=True),
        sa.Column('closure_date', sa.DateTime(), nullable=True),
        sa.Column('award_details', sa.Text(), nullable=True),
        sa.Column('compensation_awarded', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('compensation_paid', sa.Boolean(), nullable=True),
        sa.Column('compensation_paid_date', sa.DateTime(), nullable=True),
        sa.Column('bank_response', sa.Text(), nullable=True),
        sa.Column('bank_response_date', sa.DateTime(), nullable=True),
        sa.Column('bank_representative', sa.String(length=200), nullable=True),
        sa.Column('is_appealed', sa.Boolean(), nullable=True),
        sa.Column('appeal_filed_by', sa.String(length=50), nullable=True),
        sa.Column('appeal_date', sa.DateTime(), nullable=True),
        sa.Column('appeal_outcome', sa.Text(), nullable=True),
        sa.Column('rbi_guidelines_followed', sa.Boolean(), nullable=True),
        sa.Column('resolution_within_30_days', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('internal_remarks', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('complaint_id')
    )
    op.create_index(op.f('ix_ombudsman_cases_id'), 'ombudsman_cases', ['id'], unique=False)
    op.create_index(op.f('ix_ombudsman_cases_ombudsman_case_number'), 'ombudsman_cases', ['ombudsman_case_number'], unique=True)
    op.create_index(op.f('ix_ombudsman_cases_status'), 'ombudsman_cases', ['status'], unique=False)
    op.create_index('idx_ombudsman_status', 'ombudsman_cases', ['status'], unique=False)
    op.create_index('idx_ombudsman_submitted_date', 'ombudsman_cases', ['submitted_date'], unique=False)


def downgrade():
    # Drop indexes and tables in reverse order
    op.drop_index('idx_ombudsman_submitted_date', table_name='ombudsman_cases')
    op.drop_index('idx_ombudsman_status', table_name='ombudsman_cases')
    op.drop_index(op.f('ix_ombudsman_cases_status'), table_name='ombudsman_cases')
    op.drop_index(op.f('ix_ombudsman_cases_ombudsman_case_number'), table_name='ombudsman_cases')
    op.drop_index(op.f('ix_ombudsman_cases_id'), table_name='ombudsman_cases')
    op.drop_table('ombudsman_cases')
    
    op.drop_index('idx_sla_category_priority', table_name='complaint_sla')
    op.drop_index(op.f('ix_complaint_sla_priority'), table_name='complaint_sla')
    op.drop_index(op.f('ix_complaint_sla_id'), table_name='complaint_sla')
    op.drop_index(op.f('ix_complaint_sla_category'), table_name='complaint_sla')
    op.drop_table('complaint_sla')
    
    op.drop_index('idx_escalation_assigned_to', table_name='complaint_escalations')
    op.drop_index('idx_escalation_complaint_level', table_name='complaint_escalations')
    op.drop_index(op.f('ix_complaint_escalations_id'), table_name='complaint_escalations')
    op.drop_index(op.f('ix_complaint_escalations_escalation_level'), table_name='complaint_escalations')
    op.drop_index(op.f('ix_complaint_escalations_escalated_to'), table_name='complaint_escalations')
    op.drop_index(op.f('ix_complaint_escalations_complaint_id'), table_name='complaint_escalations')
    op.drop_table('complaint_escalations')
    
    op.drop_index(op.f('ix_complaint_channels_id'), table_name='complaint_channels')
    op.drop_index(op.f('ix_complaint_channels_complaint_id'), table_name='complaint_channels')
    op.drop_table('complaint_channels')
    
    op.drop_index('idx_complaint_registered_date', table_name='complaints')
    op.drop_index('idx_complaint_sla_breach', table_name='complaints')
    op.drop_index('idx_complaint_category_status', table_name='complaints')
    op.drop_index('idx_complaint_assigned_status', table_name='complaints')
    op.drop_index('idx_complaint_customer_status', table_name='complaints')
    op.drop_index(op.f('ix_complaints_status'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_priority'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_id'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_customer_id'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_complaint_number'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_channel'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_category'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_assigned_to'), table_name='complaints')
    op.drop_table('complaints')
    
    # Drop enums
    sa.Enum(name='ombudsmanstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='escalationlevel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='complaintpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='complaintstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='channeltype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='complaintcategory').drop(op.get_bind(), checkfirst=True)
