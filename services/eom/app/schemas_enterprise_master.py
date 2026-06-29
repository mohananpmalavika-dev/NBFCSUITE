from pydantic import BaseModel, Field
from typing import Optional


class EnterpriseBrandingPayload(BaseModel):
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    theme: Optional[str] = None
    website: Optional[str] = None
    email_domain: Optional[str] = None
    mobile_app_name: Optional[str] = None
    portal_name: Optional[str] = None


class EnterpriseLegalPayload(BaseModel):
    country: Optional[str] = None
    registration_number: Optional[str] = None
    incorporation_date: Optional[str] = None
    tax_number: Optional[str] = None
    gst_vat_number: Optional[str] = None
    pan: Optional[str] = None
    corporate_identity_number: Optional[str] = None
    regulatory_license: Optional[str] = None


class EnterpriseFinancePayload(BaseModel):
    base_currency: Optional[str] = None
    financial_year: Optional[str] = None
    accounting_standard: Optional[str] = None
    tax_system: Optional[str] = None
    default_gl: Optional[str] = None
    default_cost_center: Optional[str] = None
    default_profit_center: Optional[str] = None


class EnterpriseLocalizationPayload(BaseModel):
    language: Optional[str] = None
    time_zone: Optional[str] = None
    date_format: Optional[str] = None
    number_format: Optional[str] = None
    fiscal_calendar: Optional[str] = None
    holiday_calendar: Optional[str] = None


class EnterpriseContactPayload(BaseModel):
    corporate_address: Optional[str] = None
    head_office: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    support_contact: Optional[str] = None


class EnterpriseCompliancePayload(BaseModel):
    aml_enabled: bool = False
    kyc_policy: Optional[str] = None
    data_retention: Optional[str] = None
    audit_retention: Optional[str] = None
    password_policy: Optional[str] = None
    session_policy: Optional[str] = None


class EnterpriseIntegrationPayload(BaseModel):
    integration_type: str
    provider: Optional[str] = None
    status: str = 'planned'


class EnterpriseDocumentPayload(BaseModel):
    document_type: str
    name: str
    status: str = 'pending'
    ocr_metadata: Optional[str] = None


class EnterpriseSettingPayload(BaseModel):
    setting_group: str
    setting_key: str
    setting_value: Optional[str] = None
    inherited: bool = True


class EnterpriseProfilePayload(BaseModel):
    branding: EnterpriseBrandingPayload = Field(default_factory=EnterpriseBrandingPayload)
    legal: EnterpriseLegalPayload = Field(default_factory=EnterpriseLegalPayload)
    finance: EnterpriseFinancePayload = Field(default_factory=EnterpriseFinancePayload)
    localization: EnterpriseLocalizationPayload = Field(default_factory=EnterpriseLocalizationPayload)
    contact: EnterpriseContactPayload = Field(default_factory=EnterpriseContactPayload)
    compliance: EnterpriseCompliancePayload = Field(default_factory=EnterpriseCompliancePayload)
    integrations: list[EnterpriseIntegrationPayload] = Field(default_factory=list)
    documents: list[EnterpriseDocumentPayload] = Field(default_factory=list)
    settings: list[EnterpriseSettingPayload] = Field(default_factory=list)
