import asyncio
import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/eom_foundation_test.db"

db_path = Path("C:/tmp/eom_foundation_test.db")
if db_path.exists():
    db_path.unlink()

from services.customer.app.db import Base, SessionLocal, engine, init_db
from services.customer.app.routers.customer import create_customer
from services.customer.app.routers.eom import (
    create_area,
    create_asset,
    create_branch,
    create_brand,
    create_business_unit,
    create_cluster,
    create_customer_branch_mapping,
    create_department,
    create_division,
    create_enterprise,
    create_legal_entity,
    create_position,
    create_region,
    create_team,
    create_vendor,
    create_zone,
    get_eom_summary,
    get_hierarchy_tree,
)
from services.customer.app.schemas import CustomerCreate
from services.customer.app.schemas_eom import (
    AreaCreate,
    AssetCreate,
    BranchCreate,
    BrandCreate,
    BusinessUnitCreate,
    ClusterCreate,
    CustomerBranchMappingCreate,
    DepartmentCreate,
    DivisionCreate,
    EnterpriseCreate,
    LegalEntityCreate,
    PositionCreate,
    RegionCreate,
    TeamCreate,
    VendorCreate,
    ZoneCreate,
)


def run(coro):
    return asyncio.run(coro)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    init_db()


def test_eom_enterprise_foundation_chain_summary_and_tree():
    reset_db()
    db = SessionLocal()
    try:
        enterprise = run(
            create_enterprise(
                EnterpriseCreate(
                    tenant_id="default",
                    enterprise_code="FINDNA-GROUP",
                    enterprise_name="FinDNA Group",
                    corporate_office="Bengaluru",
                    country="India",
                    currency="INR",
                    timezone="Asia/Kolkata",
                ),
                db,
            )
        )
        brand = run(
            create_brand(
                BrandCreate(
                    tenant_id="default",
                    enterprise_id=enterprise.id,
                    brand_code="FINDNA-FIN",
                    brand_name="FinDNA Finance",
                ),
                db,
            )
        )
        legal_entity = run(
            create_legal_entity(
                LegalEntityCreate(
                    tenant_id="default",
                    brand_id=brand.id,
                    entity_code="FINDNA-PVT",
                    entity_name="FinDNA Finance Pvt Ltd",
                ),
                db,
            )
        )
        business_unit = run(
            create_business_unit(
                BusinessUnitCreate(
                    tenant_id="default",
                    legal_entity_id=legal_entity.id,
                    business_unit_code="LENDING",
                    business_unit_name="Retail Lending",
                ),
                db,
            )
        )
        division = run(
            create_division(
                DivisionCreate(
                    tenant_id="default",
                    business_unit_id=business_unit.id,
                    division_code="GOLD",
                    division_name="Gold Loan Division",
                ),
                db,
            )
        )
        zone = run(
            create_zone(
                ZoneCreate(
                    tenant_id="default",
                    business_unit_id=business_unit.id,
                    division_id=division.id,
                    zone_code="SOUTH",
                    zone_name="South Zone",
                ),
                db,
            )
        )
        region = run(
            create_region(
                RegionCreate(
                    tenant_id="default",
                    zone_id=zone.id,
                    region_code="KA",
                    region_name="Karnataka Region",
                ),
                db,
            )
        )
        area = run(
            create_area(
                AreaCreate(
                    tenant_id="default",
                    region_id=region.id,
                    area_code="BLR",
                    area_name="Bengaluru Area",
                ),
                db,
            )
        )
        cluster = run(
            create_cluster(
                ClusterCreate(
                    tenant_id="default",
                    area_id=area.id,
                    cluster_code="BLR-EAST",
                    cluster_name="Bengaluru East Cluster",
                ),
                db,
            )
        )
        branch = run(
            create_branch(
                BranchCreate(
                    tenant_id="default",
                    area_id=area.id,
                    zone_id=zone.id,
                    region_id=region.id,
                    cluster_id=cluster.id,
                    branch_code="IND",
                    branch_name="Indiranagar Branch",
                ),
                db,
            )
        )
        department = run(
            create_department(
                DepartmentCreate(
                    tenant_id="default",
                    branch_id=branch.id,
                    department_code="OPS",
                    department_name="Operations",
                ),
                db,
            )
        )
        team = run(
            create_team(
                TeamCreate(
                    tenant_id="default",
                    department_id=department.id,
                    team_code="CREDIT",
                    team_name="Credit Desk",
                ),
                db,
            )
        )
        position = run(
            create_position(
                PositionCreate(
                    tenant_id="default",
                    department_id=department.id,
                    team_id=team.id,
                    position_code="BM-IND",
                    position_title="Branch Manager",
                ),
                db,
            )
        )
        vendor = run(
            create_vendor(
                VendorCreate(
                    tenant_id="default",
                    vendor_code="SEC-VENDOR",
                    vendor_name="Secure Services",
                    vendor_type="security",
                ),
                db,
            )
        )
        asset = run(
            create_asset(
                AssetCreate(
                    tenant_id="default",
                    vendor_id=vendor.id,
                    branch_id=branch.id,
                    department_id=department.id,
                    asset_code="VAULT-1",
                    asset_name="Gold Vault",
                    asset_type="security",
                    purchase_value=100000,
                ),
                db,
            )
        )
        customer = run(
            create_customer(
                CustomerCreate(
                    first_name="Eom",
                    last_name="Customer",
                    email="eom.customer@example.com",
                    phone="9999999011",
                    dob="1990-01-01",
                    gender="F",
                ),
                db,
            )
        )
        mapping = run(
            create_customer_branch_mapping(
                CustomerBranchMappingCreate(
                    tenant_id="default",
                    customer_id=customer.id,
                    branch_id=branch.id,
                    transferred_by="tester",
                ),
                db,
            )
        )

        assert position.team_id == team.id
        assert asset.vendor_id == vendor.id
        assert mapping.branch_id == branch.id

        summary = run(get_eom_summary(db))
        assert summary.enterprises == 1
        assert summary.divisions == 1
        assert summary.teams == 1
        assert summary.positions == 1
        assert summary.vendors == 1
        assert summary.assets == 1
        assert summary.customer_branch_mappings == 1

        tree = run(get_hierarchy_tree(db))
        enterprise_node = tree["items"][0]
        assert enterprise_node["name"] == "FinDNA Group"
        assert enterprise_node["brands"][0]["legal_entities"][0]["business_units"][0]["divisions"][0]["zones"][0]["regions"][0]["areas"][0]["clusters"][0]["branches"][0]["id"] == branch.id
    finally:
        db.close()
