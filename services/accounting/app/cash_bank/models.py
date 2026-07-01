from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class CashDrawer(Base):
    __tablename__ = "cash_drawers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "drawer_code", name="uq_cash_drawers_tenant_drawer"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    branch_id = Column(String, index=True, nullable=False)
    drawer_code = Column(String, index=True, nullable=False)
    drawer_name = Column(String, nullable=False)
    capacity = Column(Float, nullable=True)
    status = Column(String, default="open", index=True)
    opening_balance = Column(Float, default=0.0)
    closing_balance = Column(Float, default=0.0)
    currency = Column(String, default="INR")
    custodian = Column(String, nullable=True)
    approval_limit = Column(Float, default=0.0)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CashTransaction(Base):
    __tablename__ = "cash_transactions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "transaction_reference", name="uq_cash_transactions_tenant_reference"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    branch_id = Column(String, index=True, nullable=False)
    drawer_id = Column(String, ForeignKey("cash_drawers.id"), nullable=False, index=True)
    transaction_reference = Column(String, index=True, nullable=False)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    payment_channel = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="posted", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    drawer = relationship("CashDrawer")


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "account_number", name="uq_bank_accounts_tenant_number"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    bank_name = Column(String, nullable=False)
    branch_name = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    swift_code = Column(String, nullable=True)
    account_number = Column(String, nullable=False, index=True)
    account_type = Column(String, nullable=False)
    currency = Column(String, default="INR")
    balance = Column(Float, default=0.0)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CashTransfer(Base):
    __tablename__ = "cash_transfers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "transfer_reference", name="uq_cash_transfers_tenant_reference"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    source_drawer_id = Column(String, ForeignKey("cash_drawers.id"), nullable=True, index=True)
    destination_drawer_id = Column(String, ForeignKey("cash_drawers.id"), nullable=True, index=True)
    source_bank_account_id = Column(String, ForeignKey("bank_accounts.id"), nullable=True, index=True)
    destination_bank_account_id = Column(String, ForeignKey("bank_accounts.id"), nullable=True, index=True)
    transfer_type = Column(String, nullable=False)
    transfer_reference = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="completed", index=True)
    description = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source_drawer = relationship("CashDrawer", foreign_keys=[source_drawer_id])
    destination_drawer = relationship("CashDrawer", foreign_keys=[destination_drawer_id])
    source_bank_account = relationship("BankAccount", foreign_keys=[source_bank_account_id])
    destination_bank_account = relationship("BankAccount", foreign_keys=[destination_bank_account_id])
