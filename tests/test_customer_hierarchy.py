import asyncio
import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/customer_hierarchy_test.db"

db_path = Path("C:/tmp/customer_hierarchy_test.db")
if db_path.exists():
    db_path.unlink()

from services.customer.app.db import SessionLocal, init_db
from services.customer.app.routers.branch import (
    assign_customer_branch,
    create_branch,
    get_branch_scope,
)
from services.customer.app.routers.customer import create_customer
from services.customer.app.routers.customer import get_customer_360, validate_customer_kyc
from services.customer.app.routers.office import (
    create_area,
    create_organization,
    create_region,
    create_zone,
    get_organization_hierarchy,
)
from services.customer.app.schemas import (
    AreaCreate,
    AssignBranchRequest,
    BranchOfficeCreate,
    CustomerCreate,
    KYCValidationRequest,
    OrganizationCreate,
    RegionCreate,
    ZoneCreate,
)


def run(coro):
    return asyncio.run(coro)


def test_customer_hierarchy_chain_and_branch_scope():
    init_db()
    db = SessionLocal()
    try:
        organization = run(
            create_organization(
                OrganizationCreate(name="Acme NBFC", code="ACME"),
                db,
            )
        )

        zone = run(
            create_zone(
                ZoneCreate(
                    organization_id=organization.id,
                    name="South Zone",
                    code="SOUTH",
                ),
                db,
            )
        )

        region = run(
            create_region(
                RegionCreate(
                    zone_id=zone.id,
                    name="Karnataka Region",
                    code="KA",
                ),
                db,
            )
        )

        area = run(
            create_area(
                AreaCreate(
                    region_id=region.id,
                    name="Bengaluru Area",
                    code="BLR-A",
                ),
                db,
            )
        )

        branch = run(
            create_branch(
                BranchOfficeCreate(
                    area_id=area.id,
                    name="Indiranagar Branch",
                    code="BLR-IND",
                    branch_type="retail",
                ),
                db,
            )
        )
        assert branch.area_id == area.id

        scope = run(get_branch_scope(branch.id, db))
        assert scope == {
            "organization_id": organization.id,
            "organization_name": "Acme NBFC",
            "zone_id": zone.id,
            "zone_name": "South Zone",
            "region_id": region.id,
            "region_name": "Karnataka Region",
            "area_id": area.id,
            "area_name": "Bengaluru Area",
            "branch_id": branch.id,
            "branch_name": "Indiranagar Branch",
        }

        hierarchy = run(get_organization_hierarchy(db))
        assert hierarchy[0].zones[0].regions[0].areas[0].branches[0].id == branch.id

        customer = run(
            create_customer(
                CustomerCreate(
                    first_name="Test",
                    last_name="Customer",
                    email="test.customer@example.com",
                    phone="9999999001",
                    dob="1990-01-01",
                    gender="F",
                ),
                db,
            )
        )

        assignment = run(
            assign_customer_branch(
                customer.id,
                AssignBranchRequest(branch_id=branch.id),
                None,
                db,
            )
        )
        assert assignment["branch_id"] == branch.id

        kyc = run(
            validate_customer_kyc(
                customer.id,
                KYCValidationRequest(pan="ABCDE1234F", aadhar="234567890123"),
                db,
            )
        )
        assert kyc["kyc_status"] == "verified"

        customer_360 = run(get_customer_360(customer.id, db))
        assert customer_360["customer"].id == customer.id
        assert customer_360["branch_scope"]["branch_id"] == branch.id
    finally:
        db.close()
