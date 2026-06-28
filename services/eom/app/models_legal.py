import uuid
from sqlalchemy import Column, String, Date, DateTime, Text, Boolean, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class LegalEntity(Base):
    __tablename__ = 'legal_entity'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    display_name = Column(String(256), nullable=True)
    legal_type = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    country = Column(String(64), nullable=True)
    incorporation_date = Column(Date, nullable=True)
    cin = Column(String(64), nullable=True)
    pan = Column(String(32), nullable=True)
    gst = Column(String(64), nullable=True)
    tan = Column(String(64), nullable=True)
    vat = Column(String(64), nullable=True)
    service_tax = Column(String(64), nullable=True)
    iec = Column(String(64), nullable=True)
    primary_bank = Column(String(128), nullable=True)
    settlement_bank = Column(String(128), nullable=True)
    escrow_account = Column(String(128), nullable=True)
    registered_office = Column(Text, nullable=True)
    corporate_office = Column(Text, nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    website = Column(String(256), nullable=True)
    compliance_status = Column(String(64), nullable=True)
    risk_rating = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    registrations = relationship('LegalEntityRegistration', cascade='all, delete-orphan', back_populates='legal_entity')
    licenses = relationship('LegalEntityLicense', cascade='all, delete-orphan', back_populates='legal_entity')
    taxes = relationship('LegalEntityTax', cascade='all, delete-orphan', back_populates='legal_entity')
    banks = relationship('LegalEntityBank', cascade='all, delete-orphan', back_populates='legal_entity')
    contacts = relationship('LegalEntityContact', cascade='all, delete-orphan', back_populates='legal_entity')
    documents = relationship('LegalEntityDocument', cascade='all, delete-orphan', back_populates='legal_entity')
    compliances = relationship('LegalEntityCompliance', cascade='all, delete-orphan', back_populates='legal_entity')


class LegalEntityRegistration(Base):
    __tablename__ = 'legal_entity_registration'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    registration_type = Column(String(64), nullable=False)
    registration_number = Column(String(128), nullable=True)
    registrar = Column(String(128), nullable=True)
    incorporation_date = Column(Date, nullable=True)
    corporate_office = Column(Text, nullable=True)
    authorized_capital = Column(Float, nullable=True)
    paid_up_capital = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='registrations')


class LegalEntityLicense(Base):
    __tablename__ = 'legal_entity_license'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    license_type = Column(String(128), nullable=False)
    license_number = Column(String(128), nullable=True)
    issuer = Column(String(128), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    renewal_reminder_days = Column(Date, nullable=True)
    status = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='licenses')


class LegalEntityTax(Base):
    __tablename__ = 'legal_entity_tax'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    tax_type = Column(String(64), nullable=False)
    registration_number = Column(String(128), nullable=True)
    effective_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='taxes')


class LegalEntityBank(Base):
    __tablename__ = 'legal_entity_bank'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    bank_name = Column(String(128), nullable=False)
    account_type = Column(String(64), nullable=True)
    account_number = Column(String(128), nullable=True)
    routing_code = Column(String(64), nullable=True)
    currency = Column(String(16), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='banks')


class LegalEntityContact(Base):
    __tablename__ = 'legal_entity_contact'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    contact_type = Column(String(64), nullable=True)
    name = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    role = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='contacts')


class LegalEntityDocument(Base):
    __tablename__ = 'legal_entity_document'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    document_type = Column(String(128), nullable=False)
    document_name = Column(String(256), nullable=True)
    file_reference = Column(String(256), nullable=True)
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='documents')


class LegalEntityCompliance(Base):
    __tablename__ = 'legal_entity_compliance'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=False)
    category = Column(String(128), nullable=False)
    status = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    legal_entity = relationship('LegalEntity', back_populates='compliances')
