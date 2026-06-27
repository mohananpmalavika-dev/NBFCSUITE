from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    dob: str
    gender: str
    branch_id: Optional[str] = None
    pan: Optional[str] = None
    aadhar: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    customer_type: Optional[str] = "individual"


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pan: Optional[str] = None
    aadhar: Optional[str] = None
    branch_id: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    lifecycle_status: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    kyc_status: str
    pan: Optional[str] = None
    aadhar: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    branch_id: Optional[str] = None
    customer_type: Optional[str] = None
    lifecycle_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    skip: int
    limit: int


class AddressResponse(BaseModel):
    id: str
    customer_id: str
    address_type: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    is_primary: bool = False

    @field_validator("is_primary", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "active"}

    class Config:
        from_attributes = True


class AddressCreate(BaseModel):
    address_type: str
    street: str
    city: str
    state: str
    postal_code: str
    is_primary: bool = False


class DocumentResponse(BaseModel):
    id: str
    customer_id: str
    document_type: str
    document_number: str
    document_url: str
    verification_status: str
    expiry_date: Optional[datetime] = None

    class Config:
        from_attributes = True



class OfficeCreateBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool = True


class OfficeUpdateBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class OfficeResponseBase(BaseModel):
    id: str
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    @field_validator("is_active", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "active"}

    class Config:
        from_attributes = True


class KYCValidationRequest(BaseModel):
    pan: Optional[str] = None
    aadhar: Optional[str] = None


class KYCValidationResponse(BaseModel):
    customer_id: str
    kyc_status: str
    pan_valid: bool
    aadhar_valid: bool
    checks: dict


class KYCValidationUpdateResponse(KYCValidationResponse):
    pan: Optional[str] = None
    aadhar: Optional[str] = None


class Customer360Response(BaseModel):
    customer: CustomerResponse
    branch_scope: Optional["BranchScopeResponse"] = None
    addresses: list[AddressResponse] = Field(default_factory=list)
    kyc_documents: list[DocumentResponse] = Field(default_factory=list)
    financial_profile: Optional["FinancialProfileResponse"] = None
    timeline: list["CustomerTimelineResponse"] = Field(default_factory=list)
    consents: list["CustomerConsentResponse"] = Field(default_factory=list)
    party: Optional["CustomerPartyResponse"] = None
    onboarding_gaps: list[str] = Field(default_factory=list)


class OrganizationCreate(OfficeCreateBase):
    pass


class OrganizationUpdate(OfficeUpdateBase):
    pass


class OrganizationResponse(OfficeResponseBase):
    pass


class ZoneCreate(OfficeCreateBase):
    organization_id: str


class ZoneUpdate(OfficeUpdateBase):
    pass


class ZoneResponse(OfficeResponseBase):
    organization_id: str


class RegionCreate(OfficeCreateBase):
    zone_id: str


class RegionUpdate(OfficeUpdateBase):
    pass


class RegionResponse(OfficeResponseBase):
    zone_id: str


class AreaCreate(OfficeCreateBase):
    region_id: str


class AreaUpdate(OfficeUpdateBase):
    pass


class AreaResponse(OfficeResponseBase):
    region_id: str


class HeadOfficeCreate(OfficeCreateBase):
    pass


class ZonalOfficeCreate(OfficeCreateBase):
    head_office_id: str


class RegionalOfficeCreate(OfficeCreateBase):
    zonal_office_id: str


class AreaOfficeCreate(OfficeCreateBase):
    regional_office_id: str


class BranchOfficeCreate(OfficeCreateBase):
    area_office_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_type: Optional[str] = None
    postal_code: Optional[str] = None

    @model_validator(mode="after")
    def require_area(self):
        if not self.area_office_id and self.area_id:
            self.area_office_id = self.area_id
        if not self.area_office_id:
            raise ValueError("area_id or area_office_id is required")
        return self


class BranchCreate(OfficeCreateBase):
    area_id: str
    branch_type: Optional[str] = None
    postal_code: Optional[str] = None


class BranchUpdate(OfficeUpdateBase):
    branch_type: Optional[str] = None
    postal_code: Optional[str] = None
    area_id: Optional[str] = None


class BranchTransactionCreate(BaseModel):
    transaction_type: str
    amount: float
    currency: Optional[str] = "INR"
    status: Optional[str] = "completed"
    metadata: Optional[dict] = None


class BranchResponse(BaseModel):
    id: str
    area_office_id: str
    area_id: str
    name: str
    code: str
    branch_type: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    is_active: bool
    created_at: datetime

    @field_validator("is_active", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "active"}

    class Config:
        from_attributes = True


class BranchHierarchyResponse(OfficeResponseBase):
    area_id: str
    branch_type: Optional[str] = None
    postal_code: Optional[str] = None


class AssignBranchRequest(BaseModel):
    branch_id: str


class BranchScopeResponse(BaseModel):
    organization_id: str
    organization_name: str
    zone_id: str
    zone_name: str
    region_id: str
    region_name: str
    area_id: str
    area_name: str
    branch_id: str
    branch_name: str


class AreaTreeResponse(AreaResponse):
    branches: list[BranchHierarchyResponse] = Field(default_factory=list)


class RegionTreeResponse(RegionResponse):
    areas: list[AreaTreeResponse] = Field(default_factory=list)


class ZoneTreeResponse(ZoneResponse):
    regions: list[RegionTreeResponse] = Field(default_factory=list)


class OrganizationTreeResponse(OrganizationResponse):
    zones: list[ZoneTreeResponse] = Field(default_factory=list)



class BranchTransactionResponse(BaseModel):
    id: str
    customer_id: str
    branch_id: str
    transaction_type: str
    amount: float
    currency: str
    status: str
    metadata: Optional[dict] = Field(default=None, validation_alias="metadata_")
    created_at: datetime

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value):
        return float(value or 0)

    class Config:
        from_attributes = True



class FinancialProfileUpdate(BaseModel):
    annual_income: Optional[str] = None
    employment_type: Optional[str] = None
    employer: Optional[str] = None
    occupation: Optional[str] = None
    assets: Optional[dict] = None
    liabilities: Optional[dict] = None
    credit_score: Optional[int] = None
    behavior_score: Optional[str] = None
    risk_level: Optional[str] = None


class FinancialProfileResponse(BaseModel):
    id: str
    customer_id: str
    annual_income: Optional[str] = None
    employment_type: Optional[str] = None
    employer: Optional[str] = None
    occupation: Optional[str] = None
    assets: Optional[dict] = None
    liabilities: Optional[dict] = None
    credit_score: Optional[int] = None
    behavior_score: Optional[str] = None
    risk_level: Optional[str] = None
    last_updated: datetime

    class Config:
        from_attributes = True


class CustomerTimelineCreate(BaseModel):
    event_type: str
    event_description: Optional[str] = None
    triggered_by: Optional[str] = None
    event_metadata: Optional[dict] = None
    document_reference_id: Optional[str] = None
    related_product_id: Optional[str] = None


class CustomerTimelineResponse(BaseModel):
    id: str
    customer_id: str
    event_type: str
    event_description: Optional[str] = None
    event_timestamp: datetime
    triggered_by: Optional[str] = None
    event_metadata: Optional[dict] = None
    document_reference_id: Optional[str] = None
    related_product_id: Optional[str] = None

    class Config:
        from_attributes = True


class CustomerConsentCreate(BaseModel):
    consent_type: str
    consent_given: bool = True
    consent_version: str = "1.0"
    consent_document_url: Optional[str] = None
    consent_expiry_date: Optional[datetime] = None


class CustomerConsentResponse(BaseModel):
    id: str
    customer_id: str
    consent_type: str
    consent_status: str
    consent_date: datetime
    consent_version: Optional[str] = None
    consent_document_url: Optional[str] = None
    consent_expiry_date: Optional[datetime] = None
    withdrawn_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerPartyUpsert(BaseModel):
    party_type: str
    party_name: str
    party_code: Optional[str] = None
    registration_number: Optional[str] = None
    registration_authority: Optional[str] = None
    party_status: str = "active"
    tax_id: Optional[str] = None


class CustomerPartyResponse(CustomerPartyUpsert):
    id: str
    customer_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OnboardingWorkflowCreate(BaseModel):
    workflow_name: str
    product_type: str
    customer_type: Optional[str] = None
    workflow_stages: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    required_compliance_checks: list[str] = Field(default_factory=list)
    approval_levels: int = 1
    is_active: bool = True


class OnboardingWorkflowResponse(BaseModel):
    id: str
    workflow_name: str
    product_type: str
    customer_type: Optional[str] = None
    workflow_stages: Optional[list[str]] = None
    required_documents: Optional[list[str]] = None
    required_compliance_checks: Optional[list[str]] = None
    approval_levels: Optional[int] = None
    is_active: bool
    created_at: datetime

    @field_validator("is_active", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "active"}

    class Config:
        from_attributes = True


class OnboardingReadinessResponse(BaseModel):
    customer_id: str
    ready: bool
    completion_percentage: int
    missing_fields: list[str]
    missing_documents: list[str]
    missing_compliance_checks: list[str]
    workflow: Optional[OnboardingWorkflowResponse] = None
