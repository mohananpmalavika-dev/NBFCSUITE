import re
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Header
import jwt
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..models import (
    AreaOffice,
    BranchOffice,
    Customer,
    CustomerAddress,
    CustomerConsent,
    CustomerFinancialProfile,
    CustomerParty,
    CustomerTimeline,
    KYCDocument,
    OnboardingWorkflow,
    RegionalOffice,
    ZonalOffice,
)
from ..schemas import (
    CustomerCreate, CustomerResponse, CustomerUpdate, AddressCreate,
    Customer360Response, CustomerListResponse, FinancialProfileUpdate,
    FinancialProfileResponse, KYCValidationRequest, KYCValidationResponse,
    KYCValidationUpdateResponse, CustomerTimelineCreate, CustomerTimelineResponse,
    CustomerConsentCreate, CustomerConsentResponse, CustomerPartyUpsert,
    CustomerPartyResponse, OnboardingWorkflowCreate, OnboardingWorkflowResponse,
    OnboardingReadinessResponse
)
from ..db import get_db
from uuid import uuid4

router = APIRouter(prefix="/customers", tags=["customers"])

PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
AADHAR_PATTERN = re.compile(r"^[2-9][0-9]{11}$")
AUTH_SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
AUTH_ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")


class PrincipalScope:
    def __init__(
        self,
        organization_id: str | None = None,
        zone_id: str | None = None,
        region_id: str | None = None,
        area_id: str | None = None,
        branch_id: str | None = None,
    ):
        self.organization_id = organization_id
        self.zone_id = zone_id
        self.region_id = region_id
        self.area_id = area_id
        self.branch_id = branch_id

    @property
    def is_scoped(self) -> bool:
        return any([self.organization_id, self.zone_id, self.region_id, self.area_id, self.branch_id])


def get_principal_scope(
    authorization: str | None = Header(default=None),
    organization_id: str | None = Header(default=None, alias="X-Scope-Organization-Id"),
    zone_id: str | None = Header(default=None, alias="X-Scope-Zone-Id"),
    region_id: str | None = Header(default=None, alias="X-Scope-Region-Id"),
    area_id: str | None = Header(default=None, alias="X-Scope-Area-Id"),
    branch_id: str | None = Header(default=None, alias="X-Scope-Branch-Id"),
    legacy_branch_id: str | None = Header(default=None, alias="X-Branch-Id"),
) -> PrincipalScope:
    if authorization:
        if not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        try:
            payload = jwt.decode(authorization.split(" ", 1)[1], AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return PrincipalScope(
            organization_id=payload.get("organization_id"),
            zone_id=payload.get("zone_id"),
            region_id=payload.get("region_id"),
            area_id=payload.get("area_id"),
            branch_id=payload.get("branch_id"),
        )
    return PrincipalScope(
        organization_id=organization_id,
        zone_id=zone_id,
        region_id=region_id,
        area_id=area_id,
        branch_id=branch_id or legacy_branch_id,
    )


def _allowed_branch_ids(db: Session, scope: PrincipalScope) -> set[str] | None:
    if not isinstance(scope, PrincipalScope) or not scope.is_scoped:
        return None
    if scope.branch_id:
        return {scope.branch_id}

    query = db.query(BranchOffice.id)
    if scope.area_id:
        query = query.filter(BranchOffice.area_office_id == scope.area_id)
    elif scope.region_id:
        query = query.join(AreaOffice).filter(AreaOffice.regional_office_id == scope.region_id)
    elif scope.zone_id:
        query = query.join(AreaOffice).join(RegionalOffice).filter(RegionalOffice.zonal_office_id == scope.zone_id)
    elif scope.organization_id:
        query = (
            query.join(AreaOffice)
            .join(RegionalOffice)
            .join(ZonalOffice)
            .filter(ZonalOffice.head_office_id == scope.organization_id)
        )
    return {row[0] for row in query.all()}


def _assert_customer_in_scope(customer: Customer, db: Session, scope: PrincipalScope) -> None:
    allowed = _allowed_branch_ids(db, scope)
    if allowed is None:
        return
    if customer.branch_id not in allowed:
        raise HTTPException(status_code=403, detail="Customer is outside the caller's branch scope")


def _assert_branch_in_scope(branch_id: str | None, db: Session, scope: PrincipalScope) -> None:
    if not branch_id:
        return
    allowed = _allowed_branch_ids(db, scope)
    if allowed is not None and branch_id not in allowed:
        raise HTTPException(status_code=403, detail="Branch is outside the caller's hierarchy scope")


def _get_customer_or_404(customer_id: str, db: Session) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def _ensure_branch_exists(branch_id: str | None, db: Session) -> None:
    if not branch_id:
        return
    branch = db.query(BranchOffice).filter(BranchOffice.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")


def _build_branch_scope(customer: Customer):
    if not customer.branch:
        return None
    area = customer.branch.area_office
    region = area.regional_office
    zone = region.zonal_office
    organization = zone.head_office
    return {
        "organization_id": organization.id,
        "organization_name": organization.name,
        "zone_id": zone.id,
        "zone_name": zone.name,
        "region_id": region.id,
        "region_name": region.name,
        "area_id": area.id,
        "area_name": area.name,
        "branch_id": customer.branch.id,
        "branch_name": customer.branch.name,
    }


def _validate_pan(pan: str | None) -> bool:
    return bool(pan and PAN_PATTERN.match(pan.upper()))


def _validate_aadhar(aadhar: str | None) -> bool:
    normalized = re.sub(r"\D", "", aadhar or "")
    return bool(AADHAR_PATTERN.match(normalized))


def _kyc_status(pan_valid: bool, aadhar_valid: bool) -> str:
    if pan_valid and aadhar_valid:
        return "verified"
    if pan_valid or aadhar_valid:
        return "partially_verified"
    return "pending"


def _generate_cif_id(db: Session) -> str:
    sequence = db.query(Customer).count() + 1
    while True:
        cif_id = f"CIF{sequence:012d}"
        if not db.query(Customer).filter(Customer.id == cif_id).first():
            return cif_id
        sequence += 1


def _normalize_identity(value: str | None, uppercase: bool = True) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    return normalized.upper() if uppercase else normalized


def _normalize_aadhar(aadhar: str | None) -> str | None:
    return re.sub(r"\D", "", aadhar or "") or None


def _customer_duplicate_filter(customer: CustomerCreate):
    filters = []
    values = {
        "email": customer.email,
        "phone": customer.phone,
        "pan": _normalize_identity(customer.pan),
        "aadhar": _normalize_aadhar(customer.aadhar),
        "passport": _normalize_identity(customer.passport),
        "voter_id": _normalize_identity(customer.voter_id),
        "driving_licence": _normalize_identity(customer.driving_licence),
        "gstin": _normalize_identity(customer.gstin),
        "cin": _normalize_identity(customer.cin),
    }
    for field, value in values.items():
        if value:
            filters.append(getattr(Customer, field) == value)
    return filters, values


def _log_customer_event(
    db: Session,
    customer_id: str,
    event_type: str,
    event_description: str | None = None,
    triggered_by: str | None = None,
    event_metadata: dict | None = None,
    document_reference_id: str | None = None,
    related_product_id: str | None = None,
) -> CustomerTimeline:
    event = CustomerTimeline(
        id=str(uuid4()),
        customer_id=customer_id,
        event_type=event_type,
        event_description=event_description,
        triggered_by=triggered_by,
        event_metadata=event_metadata,
        document_reference_id=document_reference_id,
        related_product_id=related_product_id,
    )
    db.add(event)
    return event


def _active_workflow(db: Session, product_type: str | None, customer_type: str | None) -> OnboardingWorkflow | None:
    if not product_type:
        return None
    query = db.query(OnboardingWorkflow).filter(
        OnboardingWorkflow.product_type == product_type,
        OnboardingWorkflow.is_active == "true",
    )
    if customer_type:
        specific = query.filter(OnboardingWorkflow.customer_type == customer_type).first()
        if specific:
            return specific
    return query.filter(OnboardingWorkflow.customer_type.is_(None)).first()


def _customer_onboarding_readiness(
    customer: Customer,
    db: Session,
    product_type: str | None = None,
) -> dict:
    workflow = _active_workflow(db, product_type, customer.customer_type)
    missing_fields = []
    for field in ["first_name", "last_name", "email", "phone", "dob", "gender"]:
        if not getattr(customer, field):
            missing_fields.append(field)
    if not any([customer.pan, customer.aadhar, customer.passport, customer.voter_id, customer.driving_licence, customer.gstin, customer.cin]):
        missing_fields.append("identity_document")

    documents = db.query(KYCDocument).filter(KYCDocument.customer_id == customer.id).all()
    document_types = {document.document_type for document in documents}
    required_documents = list(workflow.required_documents or []) if workflow else ["pan", "aadhar"]
    missing_documents = [document_type for document_type in required_documents if document_type not in document_types]

    missing_compliance_checks = []
    required_checks = list(workflow.required_compliance_checks or []) if workflow else ["kyc"]
    if "kyc" in required_checks and customer.kyc_status not in {"verified", "approved"}:
        missing_compliance_checks.append("kyc")
    if "pan" in required_checks and not _validate_pan(customer.pan):
        missing_compliance_checks.append("pan")
    if "aadhar" in required_checks and not _validate_aadhar(customer.aadhar):
        missing_compliance_checks.append("aadhar")

    issue_count = len(missing_fields) + len(missing_documents) + len(missing_compliance_checks)
    completion_percentage = max(0, min(100, int(round(100 - issue_count * 12.5))))
    return {
        "customer_id": customer.id,
        "ready": issue_count == 0,
        "completion_percentage": completion_percentage,
        "missing_fields": missing_fields,
        "missing_documents": missing_documents,
        "missing_compliance_checks": missing_compliance_checks,
        "workflow": workflow,
    }


@router.post("", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    filters, identity_values = _customer_duplicate_filter(customer)
    existing = db.query(Customer).filter(or_(*filters)).first() if filters else None
    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists")
    selected_branch_id = customer.branch_id or (scope.branch_id if isinstance(scope, PrincipalScope) else None)
    _ensure_branch_exists(selected_branch_id, db)
    _assert_branch_in_scope(selected_branch_id, db, scope)

    new_customer = Customer(
        id=_generate_cif_id(db),
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        phone=customer.phone,
        dob=customer.dob,
        gender=customer.gender,
        pan=identity_values["pan"],
        aadhar=identity_values["aadhar"],
        passport=identity_values["passport"],
        voter_id=identity_values["voter_id"],
        driving_licence=identity_values["driving_licence"],
        gstin=identity_values["gstin"],
        cin=identity_values["cin"],
        customer_type=customer.customer_type or "individual",
        branch_id=selected_branch_id,
    )
    db.add(new_customer)
    _log_customer_event(
        db,
        new_customer.id,
        "customer_created",
        "Customer master record created",
        event_metadata={"branch_id": selected_branch_id, "customer_type": new_customer.customer_type},
    )
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.post("/search")
async def search_customers(
    phone: str | None = Query(None),
    email: str | None = Query(None),
    pan: str | None = Query(None),
    aadhar: str | None = Query(None),
    passport: str | None = Query(None),
    voter_id: str | None = Query(None),
    driving_licence: str | None = Query(None),
    gstin: str | None = Query(None),
    cin: str | None = Query(None),
    customer_id: str | None = Query(None),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    filters = []
    if customer_id:
        filters.append(Customer.id == customer_id)
    identity_values = {
        "phone": phone,
        "email": email,
        "pan": _normalize_identity(pan),
        "aadhar": _normalize_aadhar(aadhar),
        "passport": _normalize_identity(passport),
        "voter_id": _normalize_identity(voter_id),
        "driving_licence": _normalize_identity(driving_licence),
        "gstin": _normalize_identity(gstin),
        "cin": _normalize_identity(cin),
    }
    for field, value in identity_values.items():
        if value:
            filters.append(getattr(Customer, field) == value)
    if not filters:
        raise HTTPException(status_code=400, detail="At least one search parameter required")

    query = db.query(Customer).filter(or_(*filters))
    allowed = _allowed_branch_ids(db, scope)
    if allowed is not None:
        query = query.filter(Customer.branch_id.in_(allowed))
    matches = query.limit(10).all()
    return {
        "found": bool(matches),
        "match_count": len(matches),
        "matches": [
            {
                "customer_id": customer.id,
                "name": " ".join(part for part in [customer.first_name, customer.last_name] if part),
                "phone": customer.phone,
                "email": customer.email,
                "kyc_status": customer.kyc_status,
                "branch_id": customer.branch_id,
                "customer_type": customer.customer_type,
                "lifecycle_status": customer.lifecycle_status,
            }
            for customer in matches
        ],
    }


@router.post("/onboarding-workflows", response_model=OnboardingWorkflowResponse)
async def create_onboarding_workflow(
    payload: OnboardingWorkflowCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(OnboardingWorkflow)
        .filter(
            OnboardingWorkflow.product_type == payload.product_type,
            OnboardingWorkflow.customer_type == payload.customer_type,
            OnboardingWorkflow.is_active == "true",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Active onboarding workflow already exists for product/customer type")
    workflow = OnboardingWorkflow(
        id=str(uuid4()),
        workflow_name=payload.workflow_name,
        product_type=payload.product_type,
        customer_type=payload.customer_type,
        workflow_stages=payload.workflow_stages,
        required_documents=payload.required_documents,
        required_compliance_checks=payload.required_compliance_checks,
        approval_levels=payload.approval_levels,
        is_active="true" if payload.is_active else "false",
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


@router.get("/onboarding-workflows", response_model=list[OnboardingWorkflowResponse])
async def list_onboarding_workflows(
    product_type: str | None = Query(None),
    customer_type: str | None = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    query = db.query(OnboardingWorkflow)
    if product_type:
        query = query.filter(OnboardingWorkflow.product_type == product_type)
    if customer_type:
        query = query.filter(OnboardingWorkflow.customer_type == customer_type)
    if active_only:
        query = query.filter(OnboardingWorkflow.is_active == "true")
    return query.order_by(OnboardingWorkflow.created_at.desc()).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    return customer


@router.get("/{customer_id}/360", response_model=Customer360Response)
async def get_customer_360(
    customer_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    addresses = db.query(CustomerAddress).filter(CustomerAddress.customer_id == customer_id).all()
    documents = db.query(KYCDocument).filter(KYCDocument.customer_id == customer_id).all()
    profile = db.query(CustomerFinancialProfile).filter(
        CustomerFinancialProfile.customer_id == customer_id
    ).first()
    timeline = (
        db.query(CustomerTimeline)
        .filter(CustomerTimeline.customer_id == customer_id)
        .order_by(CustomerTimeline.event_timestamp.desc())
        .limit(25)
        .all()
    )
    consents = db.query(CustomerConsent).filter(CustomerConsent.customer_id == customer_id).all()
    party = db.query(CustomerParty).filter(CustomerParty.customer_id == customer_id).first()
    readiness = _customer_onboarding_readiness(customer, db)
    return {
        "customer": customer,
        "branch_scope": _build_branch_scope(customer),
        "addresses": addresses,
        "kyc_documents": documents,
        "financial_profile": profile,
        "timeline": timeline,
        "consents": consents,
        "party": party,
        "onboarding_gaps": (
            readiness["missing_fields"]
            + readiness["missing_documents"]
            + readiness["missing_compliance_checks"]
        ),
    }


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    update_data: CustomerUpdate,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    update_fields = update_data.model_dump(exclude_unset=True)
    _ensure_branch_exists(update_fields.get("branch_id"), db)
    _assert_branch_in_scope(update_fields.get("branch_id"), db, scope)
    for field, value in update_fields.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/{customer_id}/timeline", response_model=CustomerTimelineResponse)
async def add_customer_timeline_event(
    customer_id: str,
    payload: CustomerTimelineCreate,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    event = _log_customer_event(
        db,
        customer_id,
        payload.event_type,
        payload.event_description,
        payload.triggered_by,
        payload.event_metadata,
        payload.document_reference_id,
        payload.related_product_id,
    )
    db.commit()
    db.refresh(event)
    return event


@router.get("/{customer_id}/timeline", response_model=list[CustomerTimelineResponse])
async def list_customer_timeline(
    customer_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    return (
        db.query(CustomerTimeline)
        .filter(CustomerTimeline.customer_id == customer_id)
        .order_by(CustomerTimeline.event_timestamp.desc())
        .limit(limit)
        .all()
    )


@router.post("/{customer_id}/consents", response_model=CustomerConsentResponse)
async def record_customer_consent(
    customer_id: str,
    payload: CustomerConsentCreate,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    consent = CustomerConsent(
        id=str(uuid4()),
        customer_id=customer_id,
        consent_type=payload.consent_type,
        consent_status="given" if payload.consent_given else "withdrawn",
        consent_date=datetime.utcnow(),
        consent_version=payload.consent_version,
        consent_document_url=payload.consent_document_url,
        consent_expiry_date=payload.consent_expiry_date,
        withdrawn_date=datetime.utcnow() if not payload.consent_given else None,
    )
    db.add(consent)
    _log_customer_event(
        db,
        customer_id,
        "consent_recorded",
        f"{payload.consent_type} consent {consent.consent_status}",
        event_metadata={"consent_type": payload.consent_type, "status": consent.consent_status},
    )
    db.commit()
    db.refresh(consent)
    return consent


@router.get("/{customer_id}/consents", response_model=list[CustomerConsentResponse])
async def list_customer_consents(
    customer_id: str,
    consent_type: str | None = Query(None),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    query = db.query(CustomerConsent).filter(CustomerConsent.customer_id == customer_id)
    if consent_type:
        query = query.filter(CustomerConsent.consent_type == consent_type)
    return query.order_by(CustomerConsent.consent_date.desc()).all()


@router.post("/{customer_id}/consents/{consent_type}/withdraw", response_model=CustomerConsentResponse)
async def withdraw_customer_consent(
    customer_id: str,
    consent_type: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    consent = (
        db.query(CustomerConsent)
        .filter(CustomerConsent.customer_id == customer_id, CustomerConsent.consent_type == consent_type)
        .order_by(CustomerConsent.consent_date.desc())
        .first()
    )
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    consent.consent_status = "withdrawn"
    consent.withdrawn_date = datetime.utcnow()
    consent.updated_at = datetime.utcnow()
    _log_customer_event(
        db,
        customer_id,
        "consent_withdrawn",
        f"{consent_type} consent withdrawn",
        event_metadata={"consent_type": consent_type},
    )
    db.commit()
    db.refresh(consent)
    return consent


@router.put("/{customer_id}/party", response_model=CustomerPartyResponse)
async def upsert_customer_party(
    customer_id: str,
    payload: CustomerPartyUpsert,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    party = db.query(CustomerParty).filter(CustomerParty.customer_id == customer_id).first()
    if not party:
        party = CustomerParty(id=str(uuid4()), customer_id=customer_id)
        db.add(party)
    for key, value in payload.model_dump().items():
        setattr(party, key, value)
    party.updated_at = datetime.utcnow()
    _log_customer_event(
        db,
        customer_id,
        "party_updated",
        f"Party profile set to {payload.party_type}",
        event_metadata={"party_type": payload.party_type, "party_name": payload.party_name},
    )
    db.commit()
    db.refresh(party)
    return party


@router.get("/{customer_id}/party", response_model=CustomerPartyResponse)
async def get_customer_party(
    customer_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    party = db.query(CustomerParty).filter(CustomerParty.customer_id == customer_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party profile not found")
    return party


@router.get("/{customer_id}/onboarding-readiness", response_model=OnboardingReadinessResponse)
async def get_onboarding_readiness(
    customer_id: str,
    product_type: str | None = Query(None),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    customer = _get_customer_or_404(customer_id, db)
    _assert_customer_in_scope(customer, db, scope)
    return _customer_onboarding_readiness(customer, db, product_type)


@router.post("/{customer_id}/validate-kyc", response_model=KYCValidationUpdateResponse)
async def validate_customer_kyc(
    customer_id: str,
    validation: KYCValidationRequest,
    db: Session = Depends(get_db),
):
    customer = _get_customer_or_404(customer_id, db)
    pan = validation.pan or customer.pan
    aadhar = validation.aadhar or customer.aadhar
    pan_valid = _validate_pan(pan)
    aadhar_valid = _validate_aadhar(aadhar)

    if validation.pan is not None:
        customer.pan = validation.pan.upper()
    if validation.aadhar is not None:
        customer.aadhar = re.sub(r"\D", "", validation.aadhar)

    customer.kyc_status = _kyc_status(pan_valid, aadhar_valid)
    _log_customer_event(
        db,
        customer.id,
        "kyc_validated",
        f"KYC status updated to {customer.kyc_status}",
        event_metadata={"pan_valid": pan_valid, "aadhar_valid": aadhar_valid},
    )
    db.commit()
    db.refresh(customer)

    return {
        "customer_id": customer.id,
        "kyc_status": customer.kyc_status,
        "pan": customer.pan,
        "aadhar": customer.aadhar,
        "pan_valid": pan_valid,
        "aadhar_valid": aadhar_valid,
        "checks": {
            "pan_format": "valid" if pan_valid else "invalid_or_missing",
            "aadhar_format": "valid" if aadhar_valid else "invalid_or_missing",
            "provider": "mock_phase1_rules",
        },
    }


@router.post("/{customer_id}/kyc/validate", response_model=KYCValidationUpdateResponse)
async def validate_customer_kyc_alias(
    customer_id: str,
    validation: KYCValidationRequest,
    db: Session = Depends(get_db),
):
    return await validate_customer_kyc(customer_id, validation, db)


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    kyc_status: str | None = None,
    branch_id: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    query = db.query(Customer)
    if kyc_status:
        query = query.filter(Customer.kyc_status == kyc_status)
    if branch_id:
        _assert_branch_in_scope(branch_id, db, scope)
        query = query.filter(Customer.branch_id == branch_id)
    else:
        allowed = _allowed_branch_ids(db, scope)
        if allowed is not None:
            query = query.filter(Customer.branch_id.in_(allowed))
    if q:
        search = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Customer.first_name.ilike(search),
                Customer.last_name.ilike(search),
                Customer.email.ilike(search),
                Customer.phone.ilike(search),
            )
        )
    total = query.count()
    customers = query.offset(skip).limit(limit).all()
    return {"items": customers, "total": total, "skip": skip, "limit": limit}


@router.post("/{customer_id}/addresses")
async def add_address(customer_id: str, address: AddressCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    new_address = CustomerAddress(
        id=str(uuid4()),
        customer_id=customer_id,
        address_type=address.address_type,
        street=address.street,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        is_primary=address.is_primary,
    )
    db.add(new_address)
    _log_customer_event(
        db,
        customer_id,
        "address_added",
        f"{address.address_type} address added",
        event_metadata={"city": address.city, "state": address.state},
    )
    db.commit()
    return {"message": "Address added successfully"}


@router.get("/{customer_id}/addresses")
async def get_addresses(customer_id: str, db: Session = Depends(get_db)):
    addresses = db.query(CustomerAddress).filter(CustomerAddress.customer_id == customer_id).all()
    return {"addresses": addresses}


@router.post("/{customer_id}/kyc-documents")
async def upload_kyc_document(customer_id: str, document_type: str, document_number: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    document_url = f"s3://nbfcsuite-kyc/{customer_id}/{file.filename}"
    kyc_doc = KYCDocument(
        id=str(uuid4()),
        customer_id=customer_id,
        document_type=document_type,
        document_number=document_number,
        document_url=document_url,
        verification_status="pending",
    )
    db.add(kyc_doc)
    _log_customer_event(
        db,
        customer_id,
        "document_uploaded",
        f"{document_type} document uploaded",
        document_reference_id=kyc_doc.id,
        event_metadata={"document_type": document_type},
    )
    db.commit()
    all_docs = db.query(KYCDocument).filter(KYCDocument.customer_id == customer_id).count()
    if all_docs >= 2:
        customer.kyc_status = "submitted"
        db.commit()
    return {"message": "Document uploaded successfully", "document_url": document_url, "kyc_status": customer.kyc_status}


@router.get("/{customer_id}/kyc-documents")
async def get_kyc_documents(customer_id: str, db: Session = Depends(get_db)):
    documents = db.query(KYCDocument).filter(KYCDocument.customer_id == customer_id).all()
    return {"customer_id": customer_id, "documents": documents}


@router.get("/{customer_id}/financial-profile", response_model=FinancialProfileResponse)
async def get_financial_profile(customer_id: str, db: Session = Depends(get_db)):
    profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return profile


@router.post("/{customer_id}/financial-profile", response_model=FinancialProfileResponse)
async def create_or_update_financial_profile(customer_id: str, profile_data: FinancialProfileUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
    if not profile:
        profile = CustomerFinancialProfile(id=str(uuid4()), customer_id=customer_id)
        db.add(profile)

    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    _log_customer_event(
        db,
        customer_id,
        "financial_profile_updated",
        "Customer financial profile updated",
        event_metadata={"updated_fields": sorted(update_data.keys())},
    )
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{customer_id}/risk-profile", response_model=FinancialProfileResponse)
async def get_risk_profile(customer_id: str, db: Session = Depends(get_db)):
    profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return profile






@router.put("/{customer_id}/risk-profile", response_model=FinancialProfileResponse)
async def update_risk_profile(customer_id: str, profile_data: FinancialProfileUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    update_data = profile_data.model_dump(exclude_unset=True)
    allowed_fields = {"assets", "liabilities", "behavior_score", "risk_level", "credit_score"}
    unexpected_fields = set(update_data) - allowed_fields
    if unexpected_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Risk profile only accepts: {', '.join(sorted(allowed_fields))}",
        )

    risk_level = update_data.get("risk_level")
    if risk_level and risk_level not in {"low", "medium", "high", "critical"}:
        raise HTTPException(
            status_code=422,
            detail="risk_level must be one of low, medium, high, critical",
        )

    credit_score = update_data.get("credit_score")
    if credit_score is not None and not 300 <= credit_score <= 900:
        raise HTTPException(status_code=422, detail="credit_score must be between 300 and 900")

    try:
        profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == customer_id).first()
        if not profile:
            profile = CustomerFinancialProfile(id=str(uuid4()), customer_id=customer_id)
            db.add(profile)

        for key, value in update_data.items():
            setattr(profile, key, value)
        profile.last_updated = datetime.utcnow()

        db.commit()
        db.refresh(profile)
    except Exception:
        db.rollback()
        raise

    return profile

