from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class ProspectSearchResult(BaseModel):
    found: bool
    match_type: Optional[str] = None
    customer_id: Optional[str] = None
    customer_exists: Optional[bool] = None
    customer_name: Optional[str] = None

    prospect_id: Optional[str] = None
    prospect_status: Optional[str] = None
    prospect_name: Optional[str] = None


class CustomerSearchRequest(BaseModel):
    customer_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    pan: Optional[str] = None
    aadhar: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None


class ProspectCreate(BaseModel):
    source: Optional[str] = None
    campaign: Optional[str] = None
    branch_id: Optional[str] = None
    assigned_rm: Optional[str] = None

    first_name: str
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None

    nationality: Optional[str] = None
    resident_status: Optional[str] = None

    pan: Optional[str] = None
    aadhar: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    customer_type: Optional[str] = "individual"
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    education: Optional[str] = None
    annual_income: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    contact_profile: Optional[dict] = None
    family_profile: Optional[dict] = None
    employment_profile: Optional[dict] = None
    business_profile: Optional[dict] = None
    financial_profile: Optional[dict] = None
    banking_profile: Optional[dict] = None
    compliance_profile: Optional[dict] = None
    behavior_profile: Optional[dict] = None
    relationship_profile: Optional[dict] = None


class ProspectResponse(BaseModel):
    id: str
    status: str
    phone: str
    email: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    voter_id: Optional[str] = None
    driving_licence: Optional[str] = None
    gstin: Optional[str] = None
    cin: Optional[str] = None
    customer_type: Optional[str] = None
    branch_id: Optional[str] = None
    assigned_rm: Optional[str] = None
    customer_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProspectApproveResponse(BaseModel):
    prospect_id: str
    customer_id: str
    cif_id: str
    reused_existing_customer: bool = False


class ProspectApproveRequest(BaseModel):
    # allow passing any overrides; minimal for now
    pan: Optional[str] = None
    aadhar: Optional[str] = None

