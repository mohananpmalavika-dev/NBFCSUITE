from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class LegalEntityRegistrationCreate(BaseModel):
    registration_type: str
    registration_number: Optional[str] = None
    registrar: Optional[str] = None
    incorporation_date: Optional[date] = None
    corporate_office: Optional[str] = None
    authorized_capital: Optional[float] = None
    paid_up_capital: Optional[float] = None


class LegalEntityLicenseCreate(BaseModel):
    license_type: str
    license_number: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_reminder_days: Optional[date] = None
    status: Optional[str] = None


class LegalEntityTaxCreate(BaseModel):
    tax_type: str
    registration_number: Optional[str] = None
    effective_date: Optional[date] = None
    status: Optional[str] = None


class LegalEntityBankCreate(BaseModel):
    bank_name: str
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    routing_code: Optional[str] = None
    currency: Optional[str] = None


class LegalEntityContactCreate(BaseModel):
    contact_type: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LegalEntityDocumentCreate(BaseModel):
    document_type: str
    document_name: Optional[str] = None
    file_reference: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None


class LegalEntityComplianceCreate(BaseModel):
    category: str
    status: Optional[str] = None
    notes: Optional[str] = None


class LegalEntityCreate(BaseModel):
    code: str
    name: str
    display_name: Optional[str] = None
    legal_type: Optional[str] = None
    status: Optional[str] = 'draft'
    country: Optional[str] = None
    incorporation_date: Optional[date] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    gst: Optional[str] = None
    tan: Optional[str] = None
    vat: Optional[str] = None
    service_tax: Optional[str] = None
    iec: Optional[str] = None
    primary_bank: Optional[str] = None
    settlement_bank: Optional[str] = None
    escrow_account: Optional[str] = None
    registered_office: Optional[str] = None
    corporate_office: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    compliance_status: Optional[str] = None
    risk_rating: Optional[str] = None
    description: Optional[str] = None
    registrations: Optional[List[LegalEntityRegistrationCreate]] = None
    licenses: Optional[List[LegalEntityLicenseCreate]] = None
    taxes: Optional[List[LegalEntityTaxCreate]] = None
    banks: Optional[List[LegalEntityBankCreate]] = None
    contacts: Optional[List[LegalEntityContactCreate]] = None
    documents: Optional[List[LegalEntityDocumentCreate]] = None
    compliances: Optional[List[LegalEntityComplianceCreate]] = None


class LegalEntityResponse(BaseModel):
    id: str
    code: str
    name: str
    display_name: Optional[str]
    legal_type: Optional[str]
    status: str
    country: Optional[str]
    incorporation_date: Optional[date]
    cin: Optional[str]
    pan: Optional[str]
    gst: Optional[str]
    tan: Optional[str]
    vat: Optional[str]
    service_tax: Optional[str]
    iec: Optional[str]
    primary_bank: Optional[str]
    settlement_bank: Optional[str]
    escrow_account: Optional[str]
    registered_office: Optional[str]
    corporate_office: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    compliance_status: Optional[str]
    risk_rating: Optional[str]
    description: Optional[str]
    registrations: Optional[List['LegalEntityRegistrationResponse']] = None
    licenses: Optional[List['LegalEntityLicenseResponse']] = None
    taxes: Optional[List['LegalEntityTaxResponse']] = None
    banks: Optional[List['LegalEntityBankResponse']] = None
    contacts: Optional[List['LegalEntityContactResponse']] = None
    documents: Optional[List['LegalEntityDocumentResponse']] = None
    compliances: Optional[List['LegalEntityComplianceResponse']] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class LegalEntityUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    legal_type: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    incorporation_date: Optional[date] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    gst: Optional[str] = None
    tan: Optional[str] = None
    vat: Optional[str] = None
    service_tax: Optional[str] = None
    iec: Optional[str] = None
    primary_bank: Optional[str] = None
    settlement_bank: Optional[str] = None
    escrow_account: Optional[str] = None
    registered_office: Optional[str] = None
    corporate_office: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    compliance_status: Optional[str] = None
    risk_rating: Optional[str] = None
    description: Optional[str] = None
    registrations: Optional[List[LegalEntityRegistrationCreate]] = None
    licenses: Optional[List[LegalEntityLicenseCreate]] = None
    taxes: Optional[List[LegalEntityTaxCreate]] = None
    banks: Optional[List[LegalEntityBankCreate]] = None
    contacts: Optional[List[LegalEntityContactCreate]] = None
    documents: Optional[List[LegalEntityDocumentCreate]] = None
    compliances: Optional[List[LegalEntityComplianceCreate]] = None


class LegalEntityRegistrationResponse(BaseModel):
    id: str
    registration_type: str
    registration_number: Optional[str]
    registrar: Optional[str]
    incorporation_date: Optional[date]
    corporate_office: Optional[str]
    authorized_capital: Optional[float]
    paid_up_capital: Optional[float]

    class Config:
        orm_mode = True


class LegalEntityLicenseResponse(BaseModel):
    id: str
    license_type: str
    license_number: Optional[str]
    issuer: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]
    renewal_reminder_days: Optional[date]
    status: Optional[str]

    class Config:
        orm_mode = True


class LegalEntityTaxResponse(BaseModel):
    id: str
    tax_type: str
    registration_number: Optional[str]
    effective_date: Optional[date]
    status: Optional[str]

    class Config:
        orm_mode = True


class LegalEntityBankResponse(BaseModel):
    id: str
    bank_name: str
    account_type: Optional[str]
    account_number: Optional[str]
    routing_code: Optional[str]
    currency: Optional[str]

    class Config:
        orm_mode = True


class LegalEntityContactResponse(BaseModel):
    id: str
    contact_type: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    role: Optional[str]

    class Config:
        orm_mode = True


class LegalEntityDocumentResponse(BaseModel):
    id: str
    document_type: str
    document_name: Optional[str]
    file_reference: Optional[str]
    issue_date: Optional[date]
    expiry_date: Optional[date]

    class Config:
        orm_mode = True


class LegalEntityComplianceResponse(BaseModel):
    id: str
    category: str
    status: Optional[str]
    notes: Optional[str]

    class Config:
        orm_mode = True


class LegalEntityHealthResponse(BaseModel):
    health_score: int
    missing_registrations: int
    expired_licenses: int
    missing_bank_accounts: int
    compliance_issues: int
    audit_pending: int


class LegalEntityTimelineResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: Optional[str]
    action: str
    payload: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class LegalEntityTimelineListResponse(BaseModel):
    total: int
    items: List[LegalEntityTimelineResponse]


class LegalEntityListResponse(BaseModel):
    total: int
    items: List[LegalEntityResponse]
