import re
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session
from uuid import uuid4

from ..db import get_db
from ..models import Customer, CustomerAddress, CustomerFinancialProfile, KYCDocument
from ..models_prospect import Prospect, ProspectKYCDocument, ProspectAddress
from ..schemas_prospect import (
    CustomerSearchRequest,
    ProspectCreate,
    ProspectResponse,
    ProspectApproveRequest,
    ProspectApproveResponse,
    ProspectSearchResult,
)

router = APIRouter(prefix="/prospects", tags=["prospects"])

PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
AADHAR_PATTERN = re.compile(r"^[2-9][0-9]{11}$")


def _normalize_pan(pan: str | None) -> str | None:
    if not pan:
        return None
    return pan.strip().upper()


def _normalize_aadhar(aadhar: str | None) -> str | None:
    if not aadhar:
        return None
    return re.sub(r"\D", "", aadhar)


def _normalize_text(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().upper()


def _validate_pan(pan: str | None) -> bool:
    pan = _normalize_pan(pan)
    return bool(pan and PAN_PATTERN.match(pan))


def _validate_aadhar(aadhar: str | None) -> bool:
    aadhar = _normalize_aadhar(aadhar)
    return bool(aadhar and AADHAR_PATTERN.match(aadhar))


def _generate_cif_id(db: Session) -> str:
    sequence = db.query(Customer).count() + 1
    while True:
        cif_id = f"CIF{sequence:012d}"
        if not db.query(Customer).filter(Customer.id == cif_id).first():
            return cif_id
        sequence += 1


def _identity_values(
    phone: str | None = None,
    email: str | None = None,
    pan: str | None = None,
    aadhar: str | None = None,
    passport: str | None = None,
    voter_id: str | None = None,
    driving_licence: str | None = None,
    gstin: str | None = None,
    cin: str | None = None,
) -> dict:
    return {
        "phone": phone,
        "email": email,
        "pan": _normalize_pan(pan),
        "aadhar": _normalize_aadhar(aadhar),
        "passport": _normalize_text(passport),
        "voter_id": _normalize_text(voter_id),
        "driving_licence": _normalize_text(driving_licence),
        "gstin": _normalize_text(gstin),
        "cin": _normalize_text(cin),
    }


def _filters(model, values: dict):
    filters = []
    field_map = {
        Customer: {
            "phone": "phone",
            "email": "email",
            "pan": "pan",
            "aadhar": "aadhar",
            "passport": "passport",
            "voter_id": "voter_id",
            "driving_licence": "driving_licence",
            "gstin": "gstin",
            "cin": "cin",
        },
        Prospect: {
            "phone": "phone",
            "email": "email",
            "pan": "pan_number",
            "aadhar": "aadhar_number",
            "passport": "passport_number",
            "voter_id": "voter_id",
            "driving_licence": "driving_licence",
            "gstin": "gstin",
            "cin": "cin",
        },
    }[model]
    for key, field_name in field_map.items():
        value = values.get(key)
        if value:
            filters.append(getattr(model, field_name) == value)
    return filters


def _dedupe_customer(
    db: Session,
    phone: str | None = None,
    email: str | None = None,
    pan: str | None = None,
    aadhar: str | None = None,
    passport: str | None = None,
    voter_id: str | None = None,
    driving_licence: str | None = None,
    gstin: str | None = None,
    cin: str | None = None,
):
    values = _identity_values(phone, email, pan, aadhar, passport, voter_id, driving_licence, gstin, cin)
    filters = _filters(Customer, values)
    if not filters:
        return None
    return db.query(Customer).filter(or_(*filters)).first()


def _dedupe_prospect(db: Session, values: dict):
    filters = _filters(Prospect, values)
    if not filters:
        return None
    return db.query(Prospect).filter(or_(*filters)).first()


def _customer_name(customer: Customer) -> str:
    return " ".join(part for part in [customer.first_name, customer.last_name] if part)


def _prospect_name(prospect: Prospect) -> str:
    return " ".join(part for part in [prospect.first_name, prospect.last_name] if part)


@router.post("/search", response_model=ProspectSearchResult)
async def search_customer_or_prospect(payload: CustomerSearchRequest, db: Session = Depends(get_db)):
    if payload.customer_id:
        customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
        if customer:
            return ProspectSearchResult(
                found=True,
                match_type="customer",
                customer_exists=True,
                customer_id=customer.id,
                customer_name=_customer_name(customer),
            )

    values = _identity_values(
        phone=payload.phone,
        email=payload.email,
        pan=payload.pan,
        aadhar=payload.aadhar,
        passport=payload.passport,
        voter_id=payload.voter_id,
        driving_licence=payload.driving_licence,
        gstin=payload.gstin,
        cin=payload.cin,
    )
    customer = _dedupe_customer(db, **values)
    if customer:
        return ProspectSearchResult(
            found=True,
            match_type="customer",
            customer_exists=True,
            customer_id=customer.id,
            customer_name=_customer_name(customer),
        )

    prospect = _dedupe_prospect(db, values)
    if prospect:
        return ProspectSearchResult(
            found=True,
            match_type="prospect",
            customer_exists=False,
            prospect_id=prospect.id,
            prospect_status=prospect.status,
            prospect_name=_prospect_name(prospect),
        )

    return ProspectSearchResult(found=False, customer_exists=False)


@router.post("", response_model=ProspectResponse)
async def create_prospect(
    payload: ProspectCreate,
    db: Session = Depends(get_db),
):
    values = _identity_values(
        phone=payload.phone,
        email=payload.email,
        pan=payload.pan,
        aadhar=payload.aadhar,
        passport=payload.passport,
        voter_id=payload.voter_id,
        driving_licence=payload.driving_licence,
        gstin=payload.gstin,
        cin=payload.cin,
    )
    # Dedup during prospect creation: if we already have customer, return it as "found" would be handled by /customers/search.
    # For now, do a hard guard so we never create duplicates via this endpoint.
    existing = _dedupe_customer(db, **values)
    if existing:
        raise HTTPException(status_code=409, detail=f"Customer already exists: {existing.id}")
    existing_prospect = _dedupe_prospect(db, values)
    if existing_prospect:
        raise HTTPException(status_code=409, detail=f"Prospect already exists: {existing_prospect.id}")

    selected_dob = payload.dob

    prospect = Prospect(
        id=str(uuid4()),
        status="lead",
        source=payload.source,
        campaign=payload.campaign,
        branch_id=payload.branch_id,
        assigned_rm=payload.assigned_rm,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=selected_dob,
        gender=payload.gender,
        nationality=payload.nationality,
        resident_status=payload.resident_status,
        pan_number=values["pan"],
        aadhar_number=values["aadhar"],
        passport_number=values["passport"],
        voter_id=values["voter_id"],
        driving_licence=values["driving_licence"],
        gstin=values["gstin"],
        cin=values["cin"],
        customer_type=payload.customer_type,
        occupation=payload.occupation,
        marital_status=payload.marital_status,
        education=payload.education,
        annual_income=payload.annual_income,
        company_name=payload.company_name,
        industry=payload.industry,
        contact_profile=payload.contact_profile,
        family_profile=payload.family_profile,
        employment_profile=payload.employment_profile,
        business_profile=payload.business_profile,
        financial_profile=payload.financial_profile,
        banking_profile=payload.banking_profile,
        compliance_profile=payload.compliance_profile,
        behavior_profile=payload.behavior_profile,
        relationship_profile=payload.relationship_profile,
        kyc_status="pending",
        risk_level=None,
        customer_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(prospect)
    db.commit()
    db.refresh(prospect)
    return prospect


@router.post("/{prospect_id}/approve", response_model=ProspectApproveResponse)
async def approve_prospect(
    prospect_id: str,
    request: ProspectApproveRequest,
    db: Session = Depends(get_db),
):
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")

    if prospect.status == "customer" and prospect.customer_id:
        return {
            "prospect_id": prospect.id,
            "customer_id": prospect.customer_id,
            "cif_id": prospect.customer_id,
        }

    # apply overrides
    pan = _normalize_pan(request.pan) if request.pan is not None else prospect.pan_number
    aadhar = _normalize_aadhar(request.aadhar) if request.aadhar is not None else prospect.aadhar_number

    # dedupe again before generating CIF
    existing = _dedupe_customer(
        db,
        phone=prospect.phone,
        email=prospect.email,
        pan=pan,
        aadhar=aadhar,
        passport=prospect.passport_number,
        voter_id=prospect.voter_id,
        driving_licence=prospect.driving_licence,
        gstin=prospect.gstin,
        cin=prospect.cin,
    )
    if existing:
        prospect.customer_id = existing.id
        prospect.status = "customer"
        prospect.updated_at = datetime.utcnow()
        db.commit()
        return {"prospect_id": prospect.id, "customer_id": existing.id, "cif_id": existing.id, "reused_existing_customer": True}

    cif_id = _generate_cif_id(db)

    pan_valid = _validate_pan(pan)
    aadhar_valid = _validate_aadhar(aadhar)

    if request.pan is not None:
        prospect.pan_number = pan
    if request.aadhar is not None:
        prospect.aadhar_number = aadhar

    # derive kyc_status similar to existing logic
    if pan_valid and aadhar_valid:
        kyc_status = "verified"
    elif pan_valid or aadhar_valid:
        kyc_status = "partially_verified"
    else:
        kyc_status = "pending"

    customer = Customer(
        id=cif_id,
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        email=prospect.email,
        phone=prospect.phone,
        dob=str(prospect.date_of_birth) if prospect.date_of_birth else None,
        gender=prospect.gender,
        pan=pan,
        aadhar=aadhar,
        passport=prospect.passport_number,
        voter_id=prospect.voter_id,
        driving_licence=prospect.driving_licence,
        gstin=prospect.gstin,
        cin=prospect.cin,
        kyc_status=kyc_status,
        branch_id=prospect.branch_id,
        customer_type=prospect.customer_type or "individual",
        lifecycle_status="active",
        source_prospect_id=prospect.id,
        onboarding_metadata={
            "source": prospect.source,
            "campaign": prospect.campaign,
            "assigned_rm": prospect.assigned_rm,
            "company_name": prospect.company_name,
            "industry": prospect.industry,
            "contact_profile": prospect.contact_profile,
            "family_profile": prospect.family_profile,
            "employment_profile": prospect.employment_profile,
            "business_profile": prospect.business_profile,
            "banking_profile": prospect.banking_profile,
            "compliance_profile": prospect.compliance_profile,
            "behavior_profile": prospect.behavior_profile,
            "relationship_profile": prospect.relationship_profile,
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(customer)
    for address in db.query(ProspectAddress).filter(ProspectAddress.prospect_id == prospect.id).all():
        db.add(
            CustomerAddress(
                id=str(uuid4()),
                customer_id=cif_id,
                address_type=address.address_type,
                street=address.street_address,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                is_primary=address.is_primary,
            )
        )
    for document in db.query(ProspectKYCDocument).filter(ProspectKYCDocument.prospect_id == prospect.id).all():
        db.add(
            KYCDocument(
                id=str(uuid4()),
                customer_id=cif_id,
                document_type=document.document_type,
                document_number=document.document_number,
                document_url=document.document_url,
                verification_status=document.verification_status,
                expiry_date=document.expiry_date,
                uploaded_at=document.created_at,
            )
        )
    if prospect.financial_profile or prospect.annual_income or prospect.occupation or prospect.employment_profile or prospect.behavior_profile:
        financial_profile = dict(prospect.financial_profile or {})
        db.add(
            CustomerFinancialProfile(
                id=str(uuid4()),
                customer_id=cif_id,
                annual_income=prospect.annual_income or financial_profile.get("annual_income"),
                employment_type=financial_profile.get("employment_type") or (prospect.employment_profile or {}).get("employment_type"),
                employer=financial_profile.get("employer") or (prospect.employment_profile or {}).get("employer"),
                occupation=prospect.occupation or financial_profile.get("occupation"),
                assets=financial_profile.get("assets"),
                liabilities=financial_profile.get("liabilities"),
                credit_score=financial_profile.get("credit_score"),
                behavior_score=str((prospect.behavior_profile or {}).get("behavior_score")) if (prospect.behavior_profile or {}).get("behavior_score") is not None else None,
                risk_level=prospect.risk_level or financial_profile.get("risk_level"),
                last_updated=datetime.utcnow(),
            )
        )

    prospect.customer_id = cif_id
    prospect.status = "customer"
    prospect.updated_at = datetime.utcnow()
    db.commit()

    return {
        "prospect_id": prospect.id,
        "customer_id": cif_id,
        "cif_id": cif_id,
        "reused_existing_customer": False,
    }

