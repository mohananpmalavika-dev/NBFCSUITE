"""create section and team management system tables

Revision ID: 016
Revises: 015
Create Date: 2026-06-29
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    # === SECTION ===
    op.create_table(
        'section',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('section_type', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('department_id', sa.String(length=36), nullable=True),
        sa.Column('section_head', sa.String(length=128), nullable=True),
        sa.Column('deputy_head', sa.String(length=128), nullable=True),
        sa.Column('business_unit_id', sa.String(length=36), nullable=True),
        sa.Column('branch_id', sa.String(length=36), nullable=True),
        sa.Column('reporting_department_id', sa.String(length=36), nullable=True),
        sa.Column('working_calendar', sa.String(length=64), nullable=True),
        sa.Column('shift', sa.String(length=64), nullable=True),
        sa.Column('capacity', sa.String(length=32), nullable=True),
        sa.Column('business_hours', sa.String(length=64), nullable=True),
        sa.Column('sla_profile', sa.String(length=128), nullable=True),
        sa.Column('service_catalog', sa.Text(), nullable=True),
        sa.Column('business_capabilities', sa.Text(), nullable=True),
        sa.Column('workflows', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_section_code', 'section', ['code'], unique=True)

    op.create_table(
        'section_head',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('section_id', sa.String(length=36), sa.ForeignKey('section.id'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=64), nullable=False),
        sa.Column('start_date', sa.String(length=32), nullable=True),
        sa.Column('end_date', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'section_document',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('section_id', sa.String(length=36), sa.ForeignKey('section.id'), nullable=False),
        sa.Column('document_type', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('file_reference', sa.String(length=256), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'section_workflow',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('section_id', sa.String(length=36), sa.ForeignKey('section.id'), nullable=False),
        sa.Column('workflow_type', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('initiated_by', sa.String(length=128), nullable=True),
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
    )

    op.create_table(
        'section_audit',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('section_id', sa.String(length=36), sa.ForeignKey('section.id'), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # === TEAM ===
    op.create_table(
        'team',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('team_type', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('section_id', sa.String(length=36), sa.ForeignKey('section.id'), nullable=True),
        sa.Column('team_lead', sa.String(length=128), nullable=True),
        sa.Column('deputy_lead', sa.String(length=128), nullable=True),
        sa.Column('reporting_manager', sa.String(length=128), nullable=True),
        sa.Column('shift', sa.String(length=64), nullable=True),
        sa.Column('capacity', sa.String(length=32), nullable=True),
        sa.Column('working_days', sa.String(length=128), nullable=True),
        sa.Column('business_calendar', sa.String(length=64), nullable=True),
        sa.Column('location', sa.String(length=256), nullable=True),
        sa.Column('primary_skills', sa.Text(), nullable=True),
        sa.Column('secondary_skills', sa.Text(), nullable=True),
        sa.Column('certifications', sa.Text(), nullable=True),
        sa.Column('required_competencies', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_team_code', 'team', ['code'], unique=True)

    op.create_table(
        'team_member',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), nullable=False),
        sa.Column('employee_name', sa.String(length=256), nullable=True),
        sa.Column('role', sa.String(length=64), nullable=True),
        sa.Column('position_id', sa.String(length=36), nullable=True),
        sa.Column('join_date', sa.String(length=32), nullable=True),
        sa.Column('exit_date', sa.String(length=32), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_skill',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('employee_id', sa.String(length=36), nullable=False),
        sa.Column('skill_name', sa.String(length=128), nullable=False),
        sa.Column('level', sa.String(length=32), nullable=True),
        sa.Column('certification', sa.String(length=128), nullable=True),
        sa.Column('expiry_date', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_capacity',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('total_positions', sa.Float(), nullable=False, server_default='0'),
        sa.Column('filled', sa.Float(), nullable=False, server_default='0'),
        sa.Column('vacant', sa.Float(), nullable=False, server_default='0'),
        sa.Column('available_capacity', sa.Float(), nullable=True),
        sa.Column('utilization_pct', sa.Float(), nullable=True),
        sa.Column('overtime', sa.Float(), nullable=True, server_default='0'),
        sa.Column('idle_pct', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_project',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('project_name', sa.String(length=256), nullable=True),
        sa.Column('product', sa.String(length=128), nullable=True),
        sa.Column('process', sa.String(length=128), nullable=True),
        sa.Column('customer', sa.String(length=256), nullable=True),
        sa.Column('role', sa.String(length=64), nullable=True),
        sa.Column('start_date', sa.String(length=32), nullable=True),
        sa.Column('end_date', sa.String(length=32), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_calendar',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('calendar_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=True),
        sa.Column('event_date', sa.String(length=32), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_asset',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('asset_type', sa.String(length=64), nullable=False),
        sa.Column('asset_name', sa.String(length=256), nullable=True),
        sa.Column('serial_number', sa.String(length=128), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('allocated_to', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_kpi',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('kpi_name', sa.String(length=128), nullable=False),
        sa.Column('target', sa.Float(), nullable=True),
        sa.Column('actual', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=32), nullable=True),
        sa.Column('period', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_health',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('rating', sa.String(length=16), nullable=True),
        sa.Column('capacity_utilization', sa.Float(), nullable=True),
        sa.Column('productivity', sa.Float(), nullable=True),
        sa.Column('sla_compliance', sa.Float(), nullable=True),
        sa.Column('employee_satisfaction', sa.Float(), nullable=True),
        sa.Column('attrition', sa.Float(), nullable=True),
        sa.Column('training_completion', sa.Float(), nullable=True),
        sa.Column('project_delivery', sa.Float(), nullable=True),
        sa.Column('audit_findings', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_ai',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('insight_type', sa.String(length=64), nullable=False),
        sa.Column('insight', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_document',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('document_type', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('file_reference', sa.String(length=256), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'team_audit',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('team_id', sa.String(length=36), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )


def downgrade():
    op.drop_table('team_audit')
    op.drop_table('team_document')
    op.drop_table('team_ai')
    op.drop_table('team_health')
    op.drop_table('team_kpi')
    op.drop_table('team_asset')
    op.drop_table('team_calendar')
    op.drop_table('team_project')
    op.drop_table('team_capacity')
    op.drop_table('team_skill')
    op.drop_table('team_member')
    op.drop_table('team')
    op.drop_table('section_audit')
    op.drop_table('section_workflow')
    op.drop_table('section_document')
    op.drop_table('section_head')
    op.drop_table('section')
