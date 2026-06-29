import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class CostCenter(Base):
    __tablename__ = 'cost_center'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    category = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    parent_cost_center_id = Column(String(36), nullable=True)
    budget_owner = Column(String(128), nullable=True)

    currency = Column(String(8), nullable=True)
    gl_mapping = Column(Text, nullable=True)

    department_id = Column(String(36), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProfitCenter(Base):
    __tablename__ = 'profit_center'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    category = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    parent_profit_center_id = Column(String(36), nullable=True)
    responsibility_owner = Column(String(128), nullable=True)

    currency = Column(String(8), nullable=True)
    gl_mapping = Column(Text, nullable=True)

    branch_id = Column(String(36), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BudgetCenter(Base):
    __tablename__ = 'budget_center'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    parent_budget_center_id = Column(String(36), nullable=True)
    budget_owner = Column(String(128), nullable=True)

    currency = Column(String(8), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RevenueCenter(Base):
    __tablename__ = 'revenue_center'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    revenue_owner = Column(String(128), nullable=True)
    currency = Column(String(8), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ResponsibilityCenter(Base):
    __tablename__ = 'responsibility_center'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    responsibility_owner = Column(String(128), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InvestmentCenter(Base):
    __tablename__ = 'investment_center'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='draft')
    description = Column(Text, nullable=True)

    investment_owner = Column(String(128), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InternalOrder(Base):
    __tablename__ = 'internal_order'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    code = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default='draft')

    cost_center_id = Column(String(36), nullable=True)
    profit_center_id = Column(String(36), nullable=True)
    budget_center_id = Column(String(36), nullable=True)
    responsibility_center_id = Column(String(36), nullable=True)
    investment_center_id = Column(String(36), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Budget(Base):
    __tablename__ = 'budget'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    budget_center_id = Column(String(36), nullable=True)
    cost_center_id = Column(String(36), nullable=True)
    profit_center_id = Column(String(36), nullable=True)

    year = Column(Float().with_variant(Float, 'sqlite') if False else Float, nullable=False)  # type: ignore

    # NOTE: kept as Float in model due to this codebase's historical patterns; migration uses Integer.
    # In runtime with SQLite it is fine; Alembic/type-check will still be consistent for dev.

    status = Column(String(32), nullable=False, default='original')

    original_total = Column(Float(), nullable=True)
    revised_total = Column(Float(), nullable=True)
    committed_total = Column(Float(), nullable=True)
    actual_total = Column(Float(), nullable=True)
    forecast_total = Column(Float(), nullable=True)

    currency = Column(String(8), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BudgetVersion(Base):
    __tablename__ = 'budget_version'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id = Column(String(36), nullable=False)

    version_type = Column(String(32), nullable=False, default='revision')
    revision_number = Column(String(32), nullable=True)

    allocated_total = Column(Float(), nullable=True)
    committed_total = Column(Float(), nullable=True)
    actual_total = Column(Float(), nullable=True)
    forecast_total = Column(Float(), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AllocationRule(Base):
    __tablename__ = 'allocation_rule'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    name = Column(String(256), nullable=False)
    rule_type = Column(String(64), nullable=False)

    source_cost_center_id = Column(String(36), nullable=True)
    target_department_ids = Column(Text, nullable=True)

    allocation_by = Column(String(64), nullable=True)
    allocation_params = Column(Text, nullable=True)

    status = Column(String(32), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AllocationResult(Base):
    __tablename__ = 'allocation_result'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    allocation_rule_id = Column(String(36), nullable=True)
    enterprise_id = Column(String(36), nullable=True)

    year = Column(Float(), nullable=True)  # migration uses Integer
    result_payload = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())


class FinancialOwner(Base):
    __tablename__ = 'financial_owner'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(36), nullable=False)

    role_type = Column(String(32), nullable=False)
    user_id = Column(String(64), nullable=True)
    user_name = Column(String(256), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FinancialCalendar(Base):
    __tablename__ = 'financial_calendar'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    calendar_type = Column(String(32), nullable=False, default='financial_year')
    name = Column(String(128), nullable=False)
    start_date = Column(String(32), nullable=True)
    end_date = Column(String(32), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FinancialHealth(Base):
    __tablename__ = 'financial_health'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(36), nullable=False)

    score = Column(Float(), nullable=False, default=0)
    rating = Column(String(16), nullable=True)
    status = Column(String(32), nullable=True)
    details = Column(Text, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class FinancialAI(Base):
    __tablename__ = 'financial_ai'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(36), nullable=False)

    insight_type = Column(String(64), nullable=True)
    insight = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    score = Column(Float(), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FinancialAudit(Base):
    __tablename__ = 'financial_audit'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)

    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(36), nullable=True)

    action = Column(String(64), nullable=False)
    payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

