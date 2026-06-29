"""create grade management system tables

Revision ID: 015
Revises: 014
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    # Core grade
    op.create_table(
        'grade',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('business_unit_id', sa.String(length=36), nullable=True),
        sa.Column('department_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('level', sa.String(length=64), nullable=True),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_grade_id', sa.String(length=36), nullable=True),
        sa.Column('promotion_level', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_grade_code', 'grade', ['code'], unique=True)

    # One-to-one helpers
    op.create_table(
        'grade_salary',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('minimum_salary', sa.Float(), nullable=True),
        sa.Column('mid_salary', sa.Float(), nullable=True),
        sa.Column('maximum_salary', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('increment_policy', sa.String(length=256), nullable=True),
        sa.Column('bonus_eligibility', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_benefit',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('medical', sa.String(length=256), nullable=True),
        sa.Column('insurance', sa.String(length=256), nullable=True),
        sa.Column('travel', sa.String(length=256), nullable=True),
        sa.Column('accommodation', sa.String(length=256), nullable=True),
        sa.Column('mobile', sa.String(length=256), nullable=True),
        sa.Column('vehicle_allowance', sa.String(length=256), nullable=True),
        sa.Column('stock_option', sa.String(length=256), nullable=True),
        sa.Column('gratuity', sa.String(length=256), nullable=True),
        sa.Column('laptop', sa.String(length=256), nullable=True),
        sa.Column('wfh', sa.String(length=256), nullable=True),
        sa.Column('relocation', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_leave',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('annual_leave', sa.String(length=256), nullable=True),
        sa.Column('sick_leave', sa.String(length=256), nullable=True),
        sa.Column('casual_leave', sa.String(length=256), nullable=True),
        sa.Column('maternity', sa.String(length=256), nullable=True),
        sa.Column('paternity', sa.String(length=256), nullable=True),
        sa.Column('special_leave', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Collections
    op.create_table(
        'grade_competency',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False),
        sa.Column('competency_type', sa.String(length=64), nullable=False),
        sa.Column('required_level', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_training',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False),
        sa.Column('training_name', sa.String(length=256), nullable=False),
        sa.Column('mandatory', sa.String(length=32), nullable=True),
        sa.Column('required_level', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Approval/career/health/AI/documents
    op.create_table(
        'grade_approval',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('loan_limit', sa.Float(), nullable=True),
        sa.Column('expense_limit', sa.Float(), nullable=True),
        sa.Column('purchase_limit', sa.Float(), nullable=True),
        sa.Column('hr_approval', sa.String(length=64), nullable=True),
        sa.Column('finance_approval', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_career',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('entry', sa.String(length=256), nullable=True),
        sa.Column('promotion', sa.String(length=256), nullable=True),
        sa.Column('succession', sa.String(length=256), nullable=True),
        sa.Column('retirement', sa.String(length=256), nullable=True),
        sa.Column('career_path', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_document',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False),
        sa.Column('document_type', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=True),
        sa.Column('file_reference', sa.String(length=256), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_health',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('rating', sa.String(length=16), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True),
        sa.Column('vacancies', sa.Float(), nullable=True),
        sa.Column('training_completion_pct', sa.Float(), nullable=True),
        sa.Column('competency_gap_pct', sa.Float(), nullable=True),
        sa.Column('promotion_backlog_pct', sa.Float(), nullable=True),
        sa.Column('salary_deviation_pct', sa.Float(), nullable=True),
        sa.Column('succession_readiness_pct', sa.Float(), nullable=True),
        sa.Column('issues', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'grade_ai',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('grade_id', sa.String(length=36), sa.ForeignKey('grade.id'), nullable=False, unique=True),
        sa.Column('insight_type', sa.String(length=64), nullable=True),
        sa.Column('insight', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )


def downgrade():
    op.drop_table('grade_ai')
    op.drop_table('grade_health')
    op.drop_table('grade_document')
    op.drop_table('grade_career')
    op.drop_table('grade_approval')
    op.drop_table('grade_training')
    op.drop_table('grade_competency')
    op.drop_table('grade_leave')
    op.drop_table('grade_benefit')
    op.drop_table('grade_salary')
    op.drop_table('grade')

