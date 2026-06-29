"""create designation supporting tables

Revision ID: 018
Revises: 017
Create Date: 2026-06-29
"""

from alembic import op
import sqlalchemy as sa

revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    # Competency
    op.create_table(
        'designation_competency',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False),
        sa.Column('competency_type', sa.String(length=64), nullable=False),
        sa.Column('required_level', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Responsibilities (primary/secondary rows)
    op.create_table(
        'designation_responsibility',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False),
        sa.Column('responsibility_type', sa.String(length=32), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Recruitment (one-to-one)
    op.create_table(
        'designation_recruitment',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False, unique=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('certification', sa.Text(), nullable=True),
        sa.Column('languages', sa.Text(), nullable=True),
        sa.Column('mandatory_skills', sa.Text(), nullable=True),
        sa.Column('preferred_skills', sa.Text(), nullable=True),
        sa.Column('background_verification', sa.Text(), nullable=True),
        sa.Column('medical_check', sa.Text(), nullable=True),
        sa.Column('interview_panel', sa.Text(), nullable=True),
        sa.Column('assessment', sa.Text(), nullable=True),
        sa.Column('offer_workflow', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # KPI (many)
    op.create_table(
        'designation_kpi',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False),
        sa.Column('kpi_type', sa.String(length=64), nullable=True),
        sa.Column('kpi_name', sa.String(length=256), nullable=True),
        sa.Column('target', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=64), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Approval (one-to-one)
    op.create_table(
        'designation_approval',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False, unique=True),
        sa.Column('loan_limit', sa.Float(), nullable=True),
        sa.Column('expense_limit', sa.Float(), nullable=True),
        sa.Column('purchase_limit', sa.Float(), nullable=True),
        sa.Column('hr_approval', sa.String(length=64), nullable=True),
        sa.Column('vendor_approval', sa.String(length=64), nullable=True),
        sa.Column('travel_approval', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Career (one-to-one)
    op.create_table(
        'designation_career',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False, unique=True),
        sa.Column('entry', sa.Text(), nullable=True),
        sa.Column('promotion', sa.Text(), nullable=True),
        sa.Column('succession', sa.Text(), nullable=True),
        sa.Column('retirement', sa.Text(), nullable=True),
        sa.Column('career_path', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Training (many)
    op.create_table(
        'designation_training',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False),
        sa.Column('training_name', sa.String(length=256), nullable=False),
        sa.Column('mandatory', sa.String(length=32), nullable=True),
        sa.Column('required_level', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Documents (many)
    op.create_table(
        'designation_document',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False),
        sa.Column('document_type', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=True),
        sa.Column('file_reference', sa.String(length=256), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Health (one-to-one)
    op.create_table(
        'designation_health',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('designation_id', sa.String(length=36), sa.ForeignKey('designation.id'), nullable=False, unique=True),
        sa.Column('score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('rating', sa.String(length=16), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True),
        sa.Column('vacancies', sa.Float(), nullable=True, server_default='0'),
        sa.Column('training_compliance_pct', sa.Float(), nullable=True),
        sa.Column('competency_gap_pct', sa.Float(), nullable=True),
        sa.Column('recruitment_time_days', sa.Float(), nullable=True),
        sa.Column('performance_score_pct', sa.Float(), nullable=True),
        sa.Column('succession_readiness_pct', sa.Float(), nullable=True),
        sa.Column('issues', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )


def downgrade():
    op.drop_table('designation_health')
    op.drop_table('designation_document')
    op.drop_table('designation_training')
    op.drop_table('designation_career')
    op.drop_table('designation_approval')
    op.drop_table('designation_kpi')
    op.drop_table('designation_recruitment')
    op.drop_table('designation_responsibility')
    op.drop_table('designation_competency')

