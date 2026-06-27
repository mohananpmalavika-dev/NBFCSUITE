import asyncio
import os
from datetime import datetime
from pathlib import Path


os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/customer_onboarding_test.db"

db_path = Path("C:/tmp/customer_onboarding_test.db")
if db_path.exists():
    db_path.unlink()

from fastapi import HTTPException

from services.customer.app.db import SessionLocal, init_db
from services.customer.app.models import Customer, CustomerAddress, CustomerFinancialProfile, KYCDocument
from services.customer.app.models_prospect import ProspectAddress, ProspectKYCDocument
from services.customer.app.routers.customer import create_customer, get_customer_360
from services.customer.app.routers.prospect import approve_prospect, create_prospect, search_customer_or_prospect
from services.customer.app.schemas import CustomerCreate
from services.customer.app.schemas_prospect import (
    CustomerSearchRequest,
    ProspectApproveRequest,
    ProspectCreate,
)


def run(coro):
    return asyncio.run(coro)


def test_enterprise_prospect_search_approval_and_customer_360_carryover():
    init_db()
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
    init_db()
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
