from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String

from app.db import Base


class CostCenter(Base):
    __tablename__ = "cost_centers"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    cost_center_type = Column(String, nullable=True, index=True)
    budget_amount = Column(Float, default=0.0)
    actual_amount = Column(Float, default=0.0)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProfitCenter(Base):
    __tablename__ = "profit_centers"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    profit_center_type = Column(String, nullable=True, index=True)
    manager = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AllocationRun(Base):
    __tablename__ = "allocation_runs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    source_cost_center_id = Column(String, ForeignKey("cost_centers.id"), nullable=False, index=True)
    amount = Column(Float, default=0.0)
    allocation_rule_type = Column(String, default="percentage")
    status = Column(String, default="completed", index=True)
    results_json = Column("results", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
