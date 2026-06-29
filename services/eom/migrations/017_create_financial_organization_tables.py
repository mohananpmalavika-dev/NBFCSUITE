"""create financial organization management (FOM) tables

Revision ID: 017
Revises: 016
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa

revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    # -----------------------------
    # Financial Organizations
    # -----------------------------
    op.create_table(
        'cost_center',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_cost_center_id', sa.String(length=36), nullable=True),
        sa.Column('budget_owner', sa.String(length=128), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('gl_mapping', sa.Text(), nullable=True),
        sa.Column('department_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_cost_center_code', 'cost_center', ['code'], unique=True)

    op.create_table(
        'profit_center',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_profit_center_id', sa.String(length=36), nullable=True),
        sa.Column('responsibility_owner', sa.String(length=128), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('gl_mapping', sa.Text(), nullable=True),
        sa.Column('branch_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_profit_center_code', 'profit_center', ['code'], unique=True)

    op.create_table(
        'budget_center',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_budget_center_id', sa.String(length=36), nullable=True),
        sa.Column('budget_owner', sa.String(length=128), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_budget_center_code', 'budget_center', ['code'], unique=True)

    op.create_table(
        'revenue_center',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('revenue_owner', sa.String(length=128), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_revenue_center_code', 'revenue_center', ['code'], unique=True)

    op.create_table(
        'responsibility_center',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('responsibility_owner', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_responsibility_center_code', 'responsibility_center', ['code'], unique=True)

    op.create_table(
        'investment_center',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('investment_owner', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_investment_center_code', 'investment_center', ['code'], unique=True)

    op.create_table(
        'internal_order',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('cost_center_id', sa.String(length=36), nullable=True),
        sa.Column('profit_center_id', sa.String(length=36), nullable=True),
        sa.Column('budget_center_id', sa.String(length=36), nullable=True),
        sa.Column('responsibility_center_id', sa.String(length=36), nullable=True),
        sa.Column('investment_center_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_internal_order_code', 'internal_order', ['code'], unique=True)

    # -----------------------------
    # Budget + Versioning (MVP)
    # -----------------------------
    op.create_table(
        'budget',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('budget_center_id', sa.String(length=36), nullable=True),
        sa.Column('cost_center_id', sa.String(length=36), nullable=True),
        sa.Column('profit_center_id', sa.String(length=36), nullable=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='original'),
        sa.Column('original_total', sa.Float(), nullable=True),
        sa.Column('revised_total', sa.Float(), nullable=True),
        sa.Column('committed_total', sa.Float(), nullable=True),
        sa.Column('actual_total', sa.Float(), nullable=True),
        sa.Column('forecast_total', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=8), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index('ix_budget_center_year', 'budget', ['budget_center_id', 'year'], unique=False)

    op.create_table(
        'budget_version',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('budget_id', sa.String(length=36), sa.ForeignKey('budget.id'), nullable=False),
        sa.Column('version_type', sa.String(length=32), nullable=False, server_default='revision'),
        sa.Column('revision_number', sa.Integer(), nullable=True),
        sa.Column('allocated_total', sa.Float(), nullable=True),
        sa.Column('committed_total', sa.Float(), nullable=True),
        sa.Column('actual_total', sa.Float(), nullable=True),
        sa.Column('forecast_total', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # -----------------------------
    # Allocation (MVP)
    # -----------------------------
    op.create_table(
        'allocation_rule',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('rule_type', sa.String(length=64), nullable=False),
        sa.Column('source_cost_center_id', sa.String(length=36), nullable=True),
        sa.Column('target_department_ids', sa.Text(), nullable=True),
        sa.Column('allocation_by', sa.String(length=64), nullable=True),
        sa.Column('allocation_params', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'allocation_result',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('allocation_rule_id', sa.String(length=36), sa.ForeignKey('allocation_rule.id'), nullable=True),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('result_payload', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # -----------------------------
    # Ownership, Calendar, Health, AI, Audit (minimal scaffolding)
    # -----------------------------
    op.create_table(
        'financial_owner',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('role_type', sa.String(length=32), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('user_name', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'financial_calendar',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('calendar_type', sa.String(length=32), nullable=False, server_default='financial_year'),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('start_date', sa.String(length=32), nullable=True),
        sa.Column('end_date', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'financial_health',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('rating', sa.String(length=16), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    op.create_table(
        'financial_ai',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('insight_type', sa.String(length=64), nullable=True),
        sa.Column('insight', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # We reuse generic AuditEntry from app/models.py for audit logs, but keep this table for spec completeness.
    op.create_table(
        'financial_audit',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('enterprise_id', sa.String(length=36), nullable=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=True),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )


def downgrade():
    # Drop in reverse order
    op.drop_table('financial_audit')
    op.drop_table('financial_ai')
    op.drop_table('financial_health')
    op.drop_table('financial_calendar')
    op.drop_table('financial_owner')

    op.drop_table('allocation_result')
    op.drop_table('allocation_rule')

    op.drop_table('budget_version')
    op.drop_table('budget')

    op.drop_table('internal_order')
    op.drop_table('investment_center')
    op.drop_table('responsibility_center')
    op.drop_table('revenue_center')
    op.drop_table('budget_center')
    op.drop_table('profit_center')
    op.drop_table('cost_center')

