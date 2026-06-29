import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship
from .db import Base


class EnterpriseBranding(Base):
    __tablename__ = 'enterprise_branding'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), unique=True, nullable=False)
    logo_url = Column(String(512), nullable=True)
    primary_color = Column(String(32), nullable=True)
    secondary_color = Column(String(32), nullable=True)
    theme = Column(String(64), nullable=True)
    website = Column(String(256), nullable=True)
    email_domain = Column(String(128), nullable=True)
    mobile_app_name = Column(String(128), nullable=True)
    portal_name = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnterpriseLegal(Base):
    __tablename__ = 'enterprise_legal'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), unique=True, nullable=False)
    country = Column(String(128), nullable=True)
    registration_number = Column(String(128), nullable=True)
    incorporation_date = Column(String(32), nullable=True)
    tax_number = Column(String(128), nullable=True)
    gst_vat_number = Column(String(128), nullable=True)
    pan = Column(String(64), nullable=True)
    corporate_identity_number = Column(String(128), nullable=True)
    regulatory_license = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnterpriseFinance(Base):
    __tablename__ = 'enterprise_finance'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), unique=True, nullable=False)
    base_currency = Column(String(8), nullable=True)
    financial_year = Column(String(64), nullable=True)
    accounting_standard = Column(String(64), nullable=True)
    tax_system = Column(String(64), nullable=True)
    default_gl = Column(String(128), nullable=True)
    default_cost_center = Column(String(128), nullable=True)
    default_profit_center = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnterpriseLocalization(Base):
    __tablename__ = 'enterprise_localization'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), unique=True, nullable=False)
    language = Column(String(32), nullable=True)
    time_zone = Column(String(128), nullable=True)
    date_format = Column(String(32), nullable=True)
    number_format = Column(String(32), nullable=True)
    fiscal_calendar = Column(String(128), nullable=True)
    holiday_calendar = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnterpriseContact(Base):
    __tablename__ = 'enterprise_contacts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), unique=True, nullable=False)
    corporate_address = Column(Text, nullable=True)
    head_office = Column(Text, nullable=True)
    email = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    website = Column(String(256), nullable=True)
    support_contact = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnterpriseCompliance(Base):
    __tablename__ = 'enterprise_compliance'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), unique=True, nullable=False)
    aml_enabled = Column(Boolean, nullable=False, default=False)
    kyc_policy = Column(String(128), nullable=True)
    data_retention = Column(String(128), nullable=True)
    audit_retention = Column(String(128), nullable=True)
    password_policy = Column(String(128), nullable=True)
    session_policy = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnterpriseIntegration(Base):
    __tablename__ = 'enterprise_integrations'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), nullable=False)
    integration_type = Column(String(64), nullable=False)
    provider = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default='planned')
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EnterpriseDocument(Base):
    __tablename__ = 'enterprise_documents'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), nullable=False)
    document_type = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='pending')
    ocr_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EnterpriseSetting(Base):
    __tablename__ = 'enterprise_settings'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), ForeignKey('enterprise.id'), nullable=False)
    setting_group = Column(String(64), nullable=False)
    setting_key = Column(String(128), nullable=False)
    setting_value = Column(Text, nullable=True)
    inherited = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


EnterpriseBranding.enterprise = relationship('Enterprise')
EnterpriseLegal.enterprise = relationship('Enterprise')
EnterpriseFinance.enterprise = relationship('Enterprise')
EnterpriseLocalization.enterprise = relationship('Enterprise')
EnterpriseContact.enterprise = relationship('Enterprise')
EnterpriseCompliance.enterprise = relationship('Enterprise')
EnterpriseIntegration.enterprise = relationship('Enterprise')
EnterpriseDocument.enterprise = relationship('Enterprise')
EnterpriseSetting.enterprise = relationship('Enterprise')
