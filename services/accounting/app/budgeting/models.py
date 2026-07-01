from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "budget_name", "scope_level", "scope_id",
            name="uq_budgets_name_scope",
        ),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    budget_name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    financial_year = Column(String, nullable=False, index=True)
    currency = Column(String, default="INR")
    status = Column(String, default="draft", index=True)
    scope_level = Column(String, nullable=True, index=True)
    scope_id = Column(String, nullable=True, index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    versions = relationship("BudgetVersion", back_populates="budget", cascade="all, delete-orphan")
    forecasts = relationship("BudgetForecast", back_populates="budget", cascade="all, delete-orphan")


class BudgetVersion(Base):
    __tablename__ = "budget_versions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False, index=True)
    version_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="active", index=True)
    period = Column(String, nullable=True, index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="versions")


class BudgetForecast(Base):
    __tablename__ = "budget_forecasts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False, index=True)
    forecast_name = Column(String, nullable=False)
    forecast_amount = Column(Float, nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    status = Column(String, default="pending", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="forecasts")
