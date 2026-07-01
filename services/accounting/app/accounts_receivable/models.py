from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class CustomerReceivable(Base):
    __tablename__ = "ar_receivables"
    __table_args__ = (
        UniqueConstraint("tenant_id", "receivable_number", name="uq_ar_receivables_tenant_number"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    receivable_number = Column(String, index=True, nullable=False)
    product_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="pending", index=True)
    due_date = Column(DateTime, nullable=True)
    posted_to_accounting = Column(String, default="false", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ReceivableSchedule(Base):
    __tablename__ = "ar_receivable_schedules"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    receivable_id = Column(String, ForeignKey("ar_receivables.id"), nullable=False, index=True)
    installment_number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="due", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    receivable = relationship("CustomerReceivable")


class ARReceipt(Base):
    __tablename__ = "ar_receipts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    receipt_number = Column(String, index=True, nullable=False)
    payment_method = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    receipt_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="received", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReceiptAllocation(Base):
    __tablename__ = "ar_receipt_allocations"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    receipt_id = Column(String, ForeignKey("ar_receipts.id"), nullable=False, index=True)
    receivable_id = Column(String, ForeignKey("ar_receivables.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    receipt = relationship("ARReceipt")
    receivable = relationship("CustomerReceivable")


class ARSettlement(Base):
    __tablename__ = "ar_settlements"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    receivable_id = Column(String, ForeignKey("ar_receivables.id"), nullable=True, index=True)
    settlement_amount = Column(Float, nullable=False)
    settlement_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ARWriteOff(Base):
    __tablename__ = "ar_writeoffs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    receivable_id = Column(String, ForeignKey("ar_receivables.id"), nullable=True, index=True)
    write_off_amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    write_off_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="approved", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
