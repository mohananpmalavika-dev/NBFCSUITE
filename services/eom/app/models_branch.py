import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class Branch(Base):
    __tablename__ = 'branch'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    branch_type = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='active')
    manager = Column(String(128), nullable=True)
    business_unit_id = Column(String(36), ForeignKey('business_unit.id'), nullable=True)
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=True)
    city = Column(String(128), nullable=True)
    region = Column(String(128), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    website = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    cash_limit = Column(Float, nullable=True)
    vault_limit = Column(Float, nullable=True)
    gold_loan_enabled = Column(Boolean, nullable=True, default=False)
    deposit_enabled = Column(Boolean, nullable=True, default=False)
    forex_enabled = Column(Boolean, nullable=True, default=False)
    atm = Column(Boolean, nullable=True, default=False)
    locker = Column(Boolean, nullable=True, default=False)
    kiosk = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    business_unit = relationship('BusinessUnit', backref='branches')
    legal_entity = relationship('LegalEntity', backref='branches')
