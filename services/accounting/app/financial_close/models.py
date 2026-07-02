from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String

from app.db import Base


class CloseCycle(Base):
    __tablename__ = "close_cycles"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_name = Column(String, nullable=False)
    close_type = Column(String, nullable=True)
    period = Column(String, nullable=True)
    stage = Column(String, nullable=False, default="planning")
    status = Column(String, nullable=False, default="started")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CloseTask(Base):
    __tablename__ = "close_tasks"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_id = Column(String, ForeignKey("close_cycles.id"), nullable=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    due_date = Column(String, nullable=True)
    dependency = Column(String, nullable=True)
    priority = Column(String, default="medium")
    status = Column(String, default="pending", index=True)
    evidence = Column(String, nullable=True)
    approval_status = Column(String, default="pending")
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CloseReconciliation(Base):
    __tablename__ = "close_reconciliations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_id = Column(String, ForeignKey("close_cycles.id"), nullable=True, index=True)
    source = Column(String, nullable=True)
    target = Column(String, nullable=True)
    difference_amount = Column(Float, default=0.0)
    status = Column(String, default="completed", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CloseConsolidation(Base):
    __tablename__ = "close_consolidations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_id = Column(String, ForeignKey("close_cycles.id"), nullable=True, index=True)
    entity_from = Column(String, nullable=True)
    entity_to = Column(String, nullable=True)
    result_summary = Column(String, nullable=True)
    status = Column(String, default="completed", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CloseElimination(Base):
    __tablename__ = "close_eliminations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_id = Column(String, ForeignKey("close_cycles.id"), nullable=True, index=True)
    description = Column(String, nullable=True)
    amount = Column(Float, default=0.0)
    status = Column(String, default="completed", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BoardPack(Base):
    __tablename__ = "board_packs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_id = Column(String, ForeignKey("close_cycles.id"), nullable=True, index=True)
    report_type = Column(String, nullable=False)
    status = Column(String, default="generated", index=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column("metadata", JSON, nullable=True)


class RegulatoryReturn(Base):
    __tablename__ = "regulatory_returns"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    cycle_id = Column(String, ForeignKey("close_cycles.id"), nullable=True, index=True)
    return_type = Column(String, nullable=False)
    status = Column(String, default="generated", index=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column("metadata", JSON, nullable=True)
