import asyncio
import os
from datetime import datetime
from pathlib import Path


os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/customer_onboarding_test.db"

db_path = Path("C:/tmp/customer_onboarding_test.db")
if db_path.exists():
    db_path.unlink()

from fastapi import HTTPException

from services.customer.app.db import Base, SessionLocal, engine, init_db
from services.customer.app.models import Customer, CustomerAddress, CustomerFinancialProfile, KYCDocument
from services.customer.app.models_prospect import ProspectAddress, ProspectKYCDocument
from services.customer.app.routers.customer import (
    add_customer_timeline_event,
    create_customer,
    create_onboarding_workflow,
    get_customer_360,
    get_onboarding_readiness,
    list_customer_timeline,
    record_customer_consent,
    search_customers,
    upsert_customer_party,
    validate_customer_kyc,
    withdraw_customer_consent,
)
from services.customer.app.routers.prospect import approve_prospect, create_prospect, search_customer_or_prospect
from services.customer.app.schemas import (
    CustomerConsentCreate,
    CustomerCreate,
    CustomerPartyUpsert,
    CustomerTimelineCreate,
    KYCValidationRequest,
    OnboardingWorkflowCreate,
)
from services.customer.app.schemas_prospect import (
    CustomerSearchRequest,
    ProspectApproveRequest,
    ProspectCreate,
)


def run(coro):
    return asyncio.run(coro)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    init_db()


def test_enterprise_prospect_search_approval_and_customer_360_carryover():
    reset_db()
    db = SessionLocal()
    try:
        empty = run(search_customer_or_prospect(CustomerSearchRequest(phone="9888888888"), db))
        assert empty.found is False

        prospect = run(
            create_prospect(
                ProspectCreate(
                    source="walk_in",
                    campaign="gold-loan-june",
                    branch_id=None,
                    assigned_rm="rm-1",
                    first_name="Meera",
                    last_name="Iyer",
                    phone="9888888888",
                    email="meera.iyer@example.com",
                    dob=datetime(1992, 5, 1).date(),
                    gender="F",
                    pan="fghij1234k",
                    aadhar="2345 6789 0123",
                    passport="z1234567",
                    occupation="Business Owner",
                    annual_income="1800000",
                    financial_profile={
                        "assets": {"property": 2500000},
                        "liabilities": {"existing_loans": 300000},
                        "credit_score": 772,
                        "risk_level": "low",
                    },
                    behavior_profile={"behavior_score": 81},
                    contact_profile={"whatsapp": "9888888888", "preferred_language": "en"},
                ),
                db,
            )
        )
        assert prospect.pan_number == "FGHIJ1234K"
        assert prospect.aadhar_number == "234567890123"
        assert prospect.passport_number == "Z1234567"

        found_prospect = run(search_customer_or_prospect(CustomerSearchRequest(passport="z1234567"), db))
        assert found_prospect.found is True
        assert found_prospect.match_type == "prospect"
        assert found_prospect.prospect_id == prospect.id

        db.add(
            ProspectAddress(
                id="addr-1",
                prospect_id=prospect.id,
                address_type="permanent",
                street_address="12 MG Road",
                city="Bengaluru",
                state="KA",
                postal_code="560001",
                country="IN",
                is_primary="true",
            )
        )
        db.add(
            ProspectKYCDocument(
                id="doc-1",
                prospect_id=prospect.id,
                document_type="pan",
                document_number="FGHIJ1234K",
                document_url="s3://docs/pan.pdf",
                verification_status="verified",
            )
        )
        db.commit()

        approval = run(approve_prospect(prospect.id, ProspectApproveRequest(), db))
        assert approval["customer_id"].startswith("CIF")
        assert approval["customer_id"] == approval["cif_id"]
        assert approval["reused_existing_customer"] is False

        customer = db.query(Customer).filter(Customer.id == approval["customer_id"]).first()
        assert customer is not None
        assert customer.source_prospect_id == prospect.id
        assert customer.passport == "Z1234567"
        assert customer.kyc_status == "verified"
        assert customer.onboarding_metadata["assigned_rm"] == "rm-1"

        customer_360 = run(get_customer_360(approval["customer_id"], db))
        assert customer_360["customer"].id == approval["customer_id"]
        assert db.query(CustomerAddress).filter(CustomerAddress.customer_id == approval["customer_id"]).count() == 1
        assert db.query(KYCDocument).filter(KYCDocument.customer_id == approval["customer_id"]).count() == 1

        profile = db.query(CustomerFinancialProfile).filter(CustomerFinancialProfile.customer_id == approval["customer_id"]).first()
        assert profile.credit_score == 772
        assert profile.behavior_score == "81"

        found_customer = run(search_customer_or_prospect(CustomerSearchRequest(phone="9888888888"), db))
        assert found_customer.match_type == "customer"
        assert found_customer.customer_id == approval["customer_id"]

        try:
            run(
                create_prospect(
                    ProspectCreate(
                        first_name="Duplicate",
                        phone="9888888888",
                        email="duplicate@example.com",
                    ),
                    db,
                )
            )
            raise AssertionError("Expected duplicate prospect creation to fail")
        except HTTPException as exc:
            assert exc.status_code == 409
    finally:
        db.close()


def test_direct_customer_creation_generates_cif_and_checks_extended_ids():
    reset_db()
    db = SessionLocal()
    try:
        customer = run(
            create_customer(
                CustomerCreate(
                    first_name="Asha",
                    last_name="Rao",
                    email="asha.rao@example.com",
                    phone="9777777777",
                    dob="1990-01-01",
                    gender="F",
                    passport="p1234567",
                ),
                db,
            )
        )
        assert customer.id.startswith("CIF")
        assert customer.passport == "P1234567"

        try:
            run(
                create_customer(
                    CustomerCreate(
                        first_name="Asha",
                        last_name="Duplicate",
                        email="asha.duplicate@example.com",
                        phone="9666666666",
                        dob="1991-01-01",
                        gender="F",
                        passport="P1234567",
                    ),
                    db,
                )
            )
            raise AssertionError("Expected duplicate passport to fail")
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()


def test_customer_creation_enterprise_readiness_consent_party_and_timeline():
    reset_db()
    db = SessionLocal()
    try:
        workflow = run(
            create_onboarding_workflow(
                OnboardingWorkflowCreate(
                    workflow_name="Gold Loan Individual Onboarding",
                    product_type="gold_loan",
                    customer_type="individual",
                    workflow_stages=["identity", "documents", "compliance", "approval"],
                    required_documents=["pan", "aadhar"],
                    required_compliance_checks=["kyc", "pan", "aadhar"],
                    approval_levels=3,
                ),
                db,
            )
        )
        assert workflow.product_type == "gold_loan"

        customer = run(
            create_customer(
                CustomerCreate(
                    first_name="Rohan",
                    last_name="Menon",
                    email="rohan.menon@example.com",
                    phone="9555555555",
                    dob="1988-04-12",
                    gender="M",
                    passport="m1234567",
                ),
                db,
            )
        )

        search_result = run(
            search_customers(
                phone=None,
                email=None,
                pan=None,
                aadhar=None,
                passport="m1234567",
                voter_id=None,
                driving_licence=None,
                gstin=None,
                cin=None,
                customer_id=None,
                db=db,
            )
        )
        assert search_result["found"] is True
        assert search_result["matches"][0]["customer_id"] == customer.id

        party = run(
            upsert_customer_party(
                customer.id,
                CustomerPartyUpsert(
                    party_type="individual",
                    party_name="Rohan Menon",
                    party_code="PTY-ROHAN",
                    tax_id="ABCDE1234F",
                ),
                db,
            )
        )
        assert party.party_type == "individual"

        consent = run(
            record_customer_consent(
                customer.id,
                CustomerConsentCreate(consent_type="account_aggregation", consent_given=True),
                db,
            )
        )
        assert consent.consent_status == "given"

        withdrawn = run(withdraw_customer_consent(customer.id, "account_aggregation", db=db))
        assert withdrawn.consent_status == "withdrawn"

        event = run(
            add_customer_timeline_event(
                customer.id,
                CustomerTimelineCreate(
                    event_type="branch_visit",
                    event_description="Customer visited branch for gold loan onboarding",
                    triggered_by="rm-1",
                ),
                db,
            )
        )
        assert event.event_type == "branch_visit"

        not_ready = run(get_onboarding_readiness(customer.id, product_type="gold_loan", db=db))
        assert not_ready["ready"] is False
        assert "pan" in not_ready["missing_documents"]
        assert "kyc" in not_ready["missing_compliance_checks"]

        run(
            validate_customer_kyc(
                customer.id,
                KYCValidationRequest(pan="ABCDE1234F", aadhar="345678901234"),
                db,
            )
        )
        db.add(
            KYCDocument(
                id="enterprise-doc-pan",
                customer_id=customer.id,
                document_type="pan",
                document_number="ABCDE1234F",
                document_url="s3://docs/enterprise-pan.pdf",
                verification_status="verified",
            )
        )
        db.add(
            KYCDocument(
                id="enterprise-doc-aadhar",
                customer_id=customer.id,
                document_type="aadhar",
                document_number="345678901234",
                document_url="s3://docs/enterprise-aadhar.pdf",
                verification_status="verified",
            )
        )
        db.commit()

        ready = run(get_onboarding_readiness(customer.id, product_type="gold_loan", db=db))
        assert ready["ready"] is True

        timeline = run(list_customer_timeline(customer.id, limit=20, db=db))
        event_types = {item.event_type for item in timeline}
        assert {"customer_created", "consent_recorded", "consent_withdrawn", "branch_visit", "kyc_validated"}.issubset(event_types)
    finally:
        db.close()
