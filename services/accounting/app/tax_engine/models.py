from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String

from app.db import Base


class TaxMaster(Base):
    __tablename__ = "tax_master"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    tax_code = Column(String, nullable=False, index=True)
    tax_type = Column(String, nullable=False, index=True)
    jurisdiction = Column(String, nullable=True)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxJurisdiction(Base):
    __tablename__ = "tax_jurisdiction"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    city = Column(String, nullable=True)
    branch_id = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxRate(Base):
    __tablename__ = "tax_rate"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    tax_master_id = Column(String, ForeignKey("tax_master.id"), nullable=True, index=True)
    tax_type = Column(String, nullable=False, index=True)
    rate = Column(Float, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GSTTransaction(Base):
    __tablename__ = "gst_transaction"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    transaction_id = Column(String, nullable=False)
    invoice_number = Column(String, nullable=True)
    base_amount = Column(Float, nullable=False)
    cgst_amount = Column(Float, default=0.0)
    sgst_amount = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    cess_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TDSOption(Base):
    __tablename__ = "tds_transaction"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    transaction_id = Column(String, nullable=False)
    section = Column(String, nullable=False)
    base_amount = Column(Float, nullable=False)
    tds_amount = Column(Float, default=0.0)
    status = Column(String, default="pending", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TCSOption(Base):
    __tablename__ = "tcs_transaction"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    transaction_id = Column(String, nullable=False)
    section = Column(String, nullable=False)
    base_amount = Column(Float, nullable=False)
    tcs_amount = Column(Float, default=0.0)
    status = Column(String, default="pending", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxLedger(Base):
    __tablename__ = "tax_ledger"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    reference_id = Column(String, nullable=True)
    entry_type = Column(String, nullable=False)
    amount = Column(Float, default=0.0)
    tax_type = Column(String, nullable=True)
    entry_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="posted", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxReturn(Base):
    __tablename__ = "tax_return"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    return_type = Column(String, nullable=False)
    period = Column(String, nullable=False)
    status = Column(String, default="draft", index=True)
    details_json = Column("details", JSON, nullable=True)
    filed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxReconciliation(Base):
    __tablename__ = "tax_reconciliation"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    reference_id = Column(String, nullable=True)
    difference_amount = Column(Float, default=0.0)
    status = Column(String, default="completed", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EInvoice(Base):
    __tablename__ = "einvoice"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    invoice_id = Column(String, nullable=False)
    irn = Column(String, nullable=False)
    qr_code = Column(String, nullable=True)
    status = Column(String, default="generated", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EWayBill(Base):
    __tablename__ = "eway_bill"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    ewaybill_number = Column(String, nullable=False)
    vehicle_number = Column(String, nullable=True)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TaxCalendar(Base):
    __tablename__ = "tax_calendar"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    event_name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="scheduled", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
