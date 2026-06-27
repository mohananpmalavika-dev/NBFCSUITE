import os
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Customer
from ..models_eom import (
    Enterprise,
    Brand,
    LegalEntity,
    BusinessUnit,
    Division,
    EOMZone,
    EOMRegion,
    EOMArea,
    EOMCluster,
    EOMBranch,
    Department,
    Team,
    Employee,
    Position,
    Vendor,
    Asset,
    EmployeeHierarchy,
    CustomerBranchMapping,
)


from ..schemas_eom import (
    BrandCreate,
    BrandResponse,
    BusinessUnitCreate,
    BusinessUnitResponse,
    ClusterCreate,
    ClusterResponse,
    CustomerBranchMappingCreate,
    CustomerBranchMappingResponse,
    DepartmentCreate,
    DepartmentResponse,
    DivisionCreate,
    DivisionResponse,
    EmployeeCreate,
    EmployeeHierarchyCreate,
    EmployeeHierarchyResponse,
    EmployeeResponse,
    EnterpriseCreate,
    EnterpriseResponse,
    EOMSummaryResponse,
    LegalEntityCreate,
    LegalEntityResponse,
    PositionCreate,
    PositionResponse,
    RegionCreate,
    RegionResponse,
    AreaCreate,
    AreaResponse,
    TeamCreate,
    TeamResponse,
    VendorCreate,
    VendorResponse,
    AssetCreate,
    AssetResponse,
    ZoneCreate,
    ZoneResponse,
    BranchCreate,
    BranchResponse,
)

router = APIRouter(prefix="/eom", tags=["eom"])


def _require_super_admin():
    # Placeholder guard: actual auth integration is not present in this repo.
    # Set REQUIRE_SUPER_ADMIN=true in the environment to enforce the 501 failure mode.
    if os.getenv("REQUIRE_SUPER_ADMIN", "false").lower() in {"1", "true", "yes"}:
        raise HTTPException(status_code=501, detail="Super Admin guard not implemented in this service yet")


def _get_or_404(db: Session, model, entity_id: str, label: str):
    entity = db.query(model).filter(model.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return entity


def _make_id(code: str) -> str:
    cleaned = str(code).strip()
    return cleaned[:36].ljust(36, "0") if cleaned else str(uuid4())


@router.post("/enterprises", response_model=EnterpriseResponse)
async def create_enterprise(payload: EnterpriseCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(Enterprise).filter(
        Enterprise.tenant_id == payload.tenant_id,
        Enterprise.enterprise_code == payload.enterprise_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Enterprise already exists")

    enterprise = Enterprise(
        id=_make_id(payload.enterprise_code),
        tenant_id=payload.tenant_id,
        enterprise_code=payload.enterprise_code,
        enterprise_name=payload.enterprise_name,
        logo_url=payload.logo_url,
        vision=payload.vision,
        mission=payload.mission,
        corporate_address=payload.corporate_address,
        corporate_office=payload.corporate_office,
        country=payload.country,
        currency=payload.currency,
        timezone=payload.timezone,
        financial_year_start=payload.financial_year_start,
        financial_year_end=payload.financial_year_end,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(enterprise)
    db.commit()
    db.refresh(enterprise)
    return enterprise


@router.post("/brands", response_model=BrandResponse)
async def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    # Super Admin only
    _require_super_admin()

    # Ensure idempotency by unique constraint on brand_code
    existing = db.query(Brand).filter(Brand.brand_code == payload.brand_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Brand already exists")

    if payload.enterprise_id:
        _get_or_404(db, Enterprise, payload.enterprise_id, "Enterprise")

    brand = Brand(
        id=_make_id(payload.brand_code),
        tenant_id=payload.tenant_id,
        enterprise_id=payload.enterprise_id,
        brand_code=payload.brand_code,
        brand_name=payload.brand_name,
        legal_name=payload.legal_name,
        short_name=payload.short_name,
        logo_url=payload.logo_url,
        theme_color=payload.theme_color,
        website=payload.website,
        email=payload.email,
        phone=payload.phone,
        gst=payload.gst,
        pan=payload.pan,
        cin=payload.cin,
        license_no=payload.license_no,
        registration_no=payload.registration_no,
        country=payload.country,
        state=payload.state,
        timezone=payload.timezone,
        currency=payload.currency,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.post("/legal-entities", response_model=LegalEntityResponse)
async def create_legal_entity(payload: LegalEntityCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, Brand, payload.brand_id, "Brand")

    existing = db.query(LegalEntity).filter(
        LegalEntity.brand_id == payload.brand_id,
        LegalEntity.entity_code == payload.entity_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Legal entity already exists")

    entity = LegalEntity(
        id=_make_id(payload.entity_code),
        tenant_id=payload.tenant_id,
        brand_id=payload.brand_id,
        entity_code=payload.entity_code,
        entity_name=payload.entity_name,
        entity_type=payload.entity_type,
        gst=payload.gst,
        pan=payload.pan,
        tan=payload.tan,
        cin=payload.cin,
        registered_address=payload.registered_address,
        state=payload.state,
        country=payload.country,
        license=payload.license,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/business-units", response_model=BusinessUnitResponse)
async def create_business_unit(payload: BusinessUnitCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, LegalEntity, payload.legal_entity_id, "Legal Entity")

    existing = db.query(BusinessUnit).filter(
        BusinessUnit.legal_entity_id == payload.legal_entity_id,
        BusinessUnit.business_unit_code == payload.business_unit_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Business unit already exists")

    bu = BusinessUnit(
        id=_make_id(payload.business_unit_code),
        tenant_id=payload.tenant_id,
        legal_entity_id=payload.legal_entity_id,
        business_unit_code=payload.business_unit_code,
        business_unit_name=payload.business_unit_name,
        head=payload.head,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(bu)
    db.commit()
    db.refresh(bu)
    return bu


@router.post("/divisions", response_model=DivisionResponse)
async def create_division(payload: DivisionCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, BusinessUnit, payload.business_unit_id, "Business Unit")

    existing = db.query(Division).filter(
        Division.business_unit_id == payload.business_unit_id,
        Division.division_code == payload.division_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Division already exists")

    division = Division(
        id=_make_id(payload.division_code),
        tenant_id=payload.tenant_id,
        business_unit_id=payload.business_unit_id,
        division_code=payload.division_code,
        division_name=payload.division_name,
        division_head=payload.division_head,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(division)
    db.commit()
    db.refresh(division)
    return division


@router.post("/zones", response_model=ZoneResponse)
async def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, BusinessUnit, payload.business_unit_id, "Business Unit")
    if payload.division_id:
        _get_or_404(db, Division, payload.division_id, "Division")

    existing = db.query(EOMZone).filter(
        EOMZone.business_unit_id == payload.business_unit_id,
        EOMZone.zone_code == payload.zone_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Zone already exists")

    z = EOMZone(
        id=_make_id(payload.zone_code),
        tenant_id=payload.tenant_id,
        business_unit_id=payload.business_unit_id,
        division_id=payload.division_id,
        zone_code=payload.zone_code,
        zone_name=payload.zone_name,
        zone_head=payload.zone_head,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(z)
    db.commit()
    db.refresh(z)
    return z


@router.post("/regions", response_model=RegionResponse)
async def create_region(payload: RegionCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, EOMZone, payload.zone_id, "Zone")

    existing = db.query(EOMRegion).filter(
        EOMRegion.zone_id == payload.zone_id,
        EOMRegion.region_code == payload.region_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Region already exists")

    r = EOMRegion(
        id=_make_id(payload.region_code),
        tenant_id=payload.tenant_id,
        zone_id=payload.zone_id,
        region_code=payload.region_code,
        region_name=payload.region_name,
        regional_manager=payload.regional_manager,
        office_address=payload.office_address,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.post("/areas", response_model=AreaResponse)
async def create_area(payload: AreaCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, EOMRegion, payload.region_id, "Region")

    existing = db.query(EOMArea).filter(
        EOMArea.region_id == payload.region_id,
        EOMArea.area_code == payload.area_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Area already exists")

    a = EOMArea(
        id=_make_id(payload.area_code),
        tenant_id=payload.tenant_id,
        region_id=payload.region_id,
        area_code=payload.area_code,
        area_name=payload.area_name,
        area_manager=payload.area_manager,
        office_address=payload.office_address,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.post("/clusters", response_model=ClusterResponse)
async def create_cluster(payload: ClusterCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, EOMArea, payload.area_id, "Area")

    existing = db.query(EOMCluster).filter(
        EOMCluster.area_id == payload.area_id,
        EOMCluster.cluster_code == payload.cluster_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Cluster already exists")

    c = EOMCluster(
        id=_make_id(payload.cluster_code),
        tenant_id=payload.tenant_id,
        area_id=payload.area_id,
        cluster_code=payload.cluster_code,
        cluster_name=payload.cluster_name,
        cluster_manager=payload.cluster_manager,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.post("/branches", response_model=BranchResponse)
async def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, EOMArea, payload.area_id, "Area")
    if payload.zone_id:
        _get_or_404(db, EOMZone, payload.zone_id, "Zone")
    if payload.region_id:
        _get_or_404(db, EOMRegion, payload.region_id, "Region")
    if payload.cluster_id:
        _get_or_404(db, EOMCluster, payload.cluster_id, "Cluster")

    branch_code = payload.branch_code
    if not branch_code:
        branch_code = payload.branch_name.strip().upper().replace(" ", "-")[:32]
    existing = db.query(EOMBranch).filter(EOMBranch.branch_code == branch_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Branch already exists")

    branch_id = _make_id(branch_code) if branch_code else str(uuid4())
    b = EOMBranch(
        id=branch_id,
        tenant_id=payload.tenant_id,
        branch_code=branch_code,
        zone_id=payload.zone_id,
        region_id=payload.region_id,
        area_id=payload.area_id,
        cluster_id=payload.cluster_id,
        branch_name=payload.branch_name,
        short_name=payload.short_name,
        branch_type=payload.branch_type,
        branch_category=payload.branch_category,
        branch_types=payload.branch_types,
        door_no=payload.door_no,
        building=payload.building,
        street=payload.street,
        village=payload.village,
        city=payload.city,
        district=payload.district,
        state=payload.state,
        country=payload.country,
        pincode=payload.pincode,
        latitude=payload.latitude,
        longitude=payload.longitude,
        contact_phone=payload.contact_phone,
        mobile=payload.mobile,
        email=payload.email,
        whatsapp=payload.whatsapp,
        website=payload.website,
        status="draft",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.post("/departments", response_model=DepartmentResponse)
async def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(Department).filter(
        Department.branch_id == payload.branch_id,
        Department.department_code == payload.department_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Department already exists")

    d = Department(
        id=str(payload.department_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        branch_id=payload.branch_id,
        department_code=payload.department_code,
        department_name=payload.department_name,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.post("/teams", response_model=TeamResponse)
async def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    _get_or_404(db, Department, payload.department_id, "Department")
    if payload.team_lead_employee_id:
        _get_or_404(db, Employee, payload.team_lead_employee_id, "Employee")

    existing = db.query(Team).filter(
        Team.department_id == payload.department_id,
        Team.team_code == payload.team_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Team already exists")

    team = Team(
        id=_make_id(payload.team_code),
        tenant_id=payload.tenant_id,
        department_id=payload.department_id,
        team_code=payload.team_code,
        team_name=payload.team_name,
        team_lead_employee_id=payload.team_lead_employee_id,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    e = Employee(
        id=str(payload.employee_code or payload.employee_name).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        employee_code=payload.employee_code,
        employee_name=payload.employee_name,
        email=payload.email,
        phone=payload.phone,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@router.post("/positions", response_model=PositionResponse)
async def create_position(payload: PositionCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    if payload.department_id:
        _get_or_404(db, Department, payload.department_id, "Department")
    if payload.team_id:
        _get_or_404(db, Team, payload.team_id, "Team")
    if payload.reports_to_position_id:
        _get_or_404(db, Position, payload.reports_to_position_id, "Reporting Position")

    existing = db.query(Position).filter(
        Position.tenant_id == payload.tenant_id,
        Position.position_code == payload.position_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Position already exists")

    position = Position(
        id=_make_id(payload.position_code),
        tenant_id=payload.tenant_id,
        department_id=payload.department_id,
        team_id=payload.team_id,
        position_code=payload.position_code,
        position_title=payload.position_title,
        reports_to_position_id=payload.reports_to_position_id,
        grade=payload.grade,
        employment_type=payload.employment_type,
        status="open",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


@router.post("/vendors", response_model=VendorResponse)
async def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(Vendor).filter(
        Vendor.tenant_id == payload.tenant_id,
        Vendor.vendor_code == payload.vendor_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Vendor already exists")

    vendor = Vendor(
        id=_make_id(payload.vendor_code),
        tenant_id=payload.tenant_id,
        vendor_code=payload.vendor_code,
        vendor_name=payload.vendor_name,
        vendor_type=payload.vendor_type,
        contact_person=payload.contact_person,
        email=payload.email,
        phone=payload.phone,
        gst=payload.gst,
        pan=payload.pan,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.post("/assets", response_model=AssetResponse)
async def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    _require_super_admin()
    if payload.branch_id:
        _get_or_404(db, EOMBranch, payload.branch_id, "Branch")
    if payload.department_id:
        _get_or_404(db, Department, payload.department_id, "Department")
    if payload.assigned_employee_id:
        _get_or_404(db, Employee, payload.assigned_employee_id, "Employee")
    if payload.vendor_id:
        _get_or_404(db, Vendor, payload.vendor_id, "Vendor")

    existing = db.query(Asset).filter(
        Asset.tenant_id == payload.tenant_id,
        Asset.asset_code == payload.asset_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Asset already exists")

    asset = Asset(
        id=_make_id(payload.asset_code),
        tenant_id=payload.tenant_id,
        asset_code=payload.asset_code,
        asset_name=payload.asset_name,
        asset_type=payload.asset_type,
        branch_id=payload.branch_id,
        department_id=payload.department_id,
        assigned_employee_id=payload.assigned_employee_id,
        vendor_id=payload.vendor_id,
        purchase_value=payload.purchase_value or 0,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/employee-hierarchy", response_model=EmployeeHierarchyResponse)
async def create_employee_hierarchy(payload: EmployeeHierarchyCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    eh = EmployeeHierarchy(
        id=str(payload.employee_id).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        employee_id=payload.employee_id,
        brand_id=payload.brand_id,
        legal_entity_id=payload.legal_entity_id,
        business_unit_id=payload.business_unit_id,
        division_id=payload.division_id,
        zone_id=payload.zone_id,
        region_id=payload.region_id,
        area_id=payload.area_id,
        cluster_id=payload.cluster_id,
        branch_id=payload.branch_id,
        department_id=payload.department_id,
        position_title=payload.position_title,
        status="active",
        created_by=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(eh)
    db.commit()
    db.refresh(eh)
    return eh


@router.get("/summary", response_model=EOMSummaryResponse)
async def get_eom_summary(db: Session = Depends(get_db)):
    return EOMSummaryResponse(
        enterprises=db.query(Enterprise).count(),
        brands=db.query(Brand).count(),
        legal_entities=db.query(LegalEntity).count(),
        business_units=db.query(BusinessUnit).count(),
        divisions=db.query(Division).count(),
        zones=db.query(EOMZone).count(),
        regions=db.query(EOMRegion).count(),
        areas=db.query(EOMArea).count(),
        clusters=db.query(EOMCluster).count(),
        branches=db.query(EOMBranch).count(),
        departments=db.query(Department).count(),
        teams=db.query(Team).count(),
        positions=db.query(Position).count(),
        employees=db.query(Employee).count(),
        vendors=db.query(Vendor).count(),
        assets=db.query(Asset).count(),
        customer_branch_mappings=db.query(CustomerBranchMapping).count(),
    )


@router.get("/hierarchy/tree")
async def get_hierarchy_tree(db: Session = Depends(get_db)):
    enterprises = db.query(Enterprise).all()
    brands = db.query(Brand).all()
    legal_entities = db.query(LegalEntity).all()
    business_units = db.query(BusinessUnit).all()
    divisions = db.query(Division).all()
    zones = db.query(EOMZone).all()
    regions = db.query(EOMRegion).all()
    areas = db.query(EOMArea).all()
    clusters = db.query(EOMCluster).all()
    branches = db.query(EOMBranch).all()

    unassigned_enterprise = {
        "id": "unassigned-enterprise",
        "code": "UNASSIGNED",
        "name": "Unassigned Enterprise",
        "type": "enterprise",
        "brands": [],
    }
    enterprise_nodes = {
        enterprise.id: {
            "id": enterprise.id,
            "code": enterprise.enterprise_code,
            "name": enterprise.enterprise_name,
            "type": "enterprise",
            "brands": [],
        }
        for enterprise in enterprises
    }

    brand_nodes = {}
    for brand in brands:
        node = {
            "id": brand.id,
            "code": brand.brand_code,
            "name": brand.brand_name,
            "type": "brand",
            "legal_entities": [],
        }
        brand_nodes[brand.id] = node
        enterprise_node = enterprise_nodes.get(brand.enterprise_id) if brand.enterprise_id else None
        if enterprise_node is None:
            enterprise_node = unassigned_enterprise
        enterprise_node["brands"].append(node)

    legal_entity_nodes = {}
    for entity in legal_entities:
        node = {
            "id": entity.id,
            "code": entity.entity_code,
            "name": entity.entity_name,
            "type": "legal_entity",
            "business_units": [],
        }
        legal_entity_nodes[entity.id] = node
        if entity.brand_id in brand_nodes:
            brand_nodes[entity.brand_id]["legal_entities"].append(node)

    business_unit_nodes = {}
    for unit in business_units:
        node = {
            "id": unit.id,
            "code": unit.business_unit_code,
            "name": unit.business_unit_name,
            "type": "business_unit",
            "divisions": [],
            "zones": [],
        }
        business_unit_nodes[unit.id] = node
        if unit.legal_entity_id in legal_entity_nodes:
            legal_entity_nodes[unit.legal_entity_id]["business_units"].append(node)

    division_nodes = {}
    for division in divisions:
        node = {
            "id": division.id,
            "code": division.division_code,
            "name": division.division_name,
            "type": "division",
            "zones": [],
        }
        division_nodes[division.id] = node
        if division.business_unit_id in business_unit_nodes:
            business_unit_nodes[division.business_unit_id]["divisions"].append(node)

    zone_nodes = {}
    for zone in zones:
        node = {
            "id": zone.id,
            "code": zone.zone_code,
            "name": zone.zone_name,
            "type": "zone",
            "regions": [],
        }
        zone_nodes[zone.id] = node
        if zone.division_id and zone.division_id in division_nodes:
            division_nodes[zone.division_id]["zones"].append(node)
        elif zone.business_unit_id in business_unit_nodes:
            business_unit_nodes[zone.business_unit_id]["zones"].append(node)

    region_nodes = {}
    for region in regions:
        node = {
            "id": region.id,
            "code": region.region_code,
            "name": region.region_name,
            "type": "region",
            "areas": [],
        }
        region_nodes[region.id] = node
        if region.zone_id in zone_nodes:
            zone_nodes[region.zone_id]["regions"].append(node)

    area_nodes = {}
    for area in areas:
        node = {
            "id": area.id,
            "code": area.area_code,
            "name": area.area_name,
            "type": "area",
            "clusters": [],
            "branches": [],
        }
        area_nodes[area.id] = node
        if area.region_id in region_nodes:
            region_nodes[area.region_id]["areas"].append(node)

    cluster_nodes = {}
    for cluster in clusters:
        node = {
            "id": cluster.id,
            "code": cluster.cluster_code,
            "name": cluster.cluster_name,
            "type": "cluster",
            "branches": [],
        }
        cluster_nodes[cluster.id] = node
        if cluster.area_id in area_nodes:
            area_nodes[cluster.area_id]["clusters"].append(node)

    for branch in branches:
        node = {
            "id": branch.id,
            "code": branch.branch_code,
            "name": branch.branch_name,
            "type": "branch",
        }
        if branch.cluster_id and branch.cluster_id in cluster_nodes:
            cluster_nodes[branch.cluster_id]["branches"].append(node)
        elif branch.area_id in area_nodes:
            area_nodes[branch.area_id]["branches"].append(node)

    tree = list(enterprise_nodes.values())
    if unassigned_enterprise["brands"]:
        tree.append(unassigned_enterprise)
    return {"items": tree}


@router.get("/enterprises", response_model=list[EnterpriseResponse])
async def list_enterprises(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Enterprise).offset(skip).limit(limit).all()


@router.get("/enterprises/{enterprise_id}", response_model=EnterpriseResponse)
async def get_enterprise(enterprise_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Enterprise, enterprise_id, "Enterprise")


@router.get("/brands", response_model=list[BrandResponse])
async def list_brands(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Brand).offset(skip).limit(limit).all()


@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Brand, brand_id, "Brand")


@router.get("/legal-entities", response_model=list[LegalEntityResponse])
async def list_legal_entities(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(LegalEntity).offset(skip).limit(limit).all()


@router.get("/legal-entities/{entity_id}", response_model=LegalEntityResponse)
async def get_legal_entity(entity_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, LegalEntity, entity_id, "Legal Entity")


@router.get("/business-units", response_model=list[BusinessUnitResponse])
async def list_business_units(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(BusinessUnit).offset(skip).limit(limit).all()


@router.get("/business-units/{business_unit_id}", response_model=BusinessUnitResponse)
async def get_business_unit(business_unit_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, BusinessUnit, business_unit_id, "Business Unit")


@router.get("/divisions", response_model=list[DivisionResponse])
async def list_divisions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Division).offset(skip).limit(limit).all()


@router.get("/divisions/{division_id}", response_model=DivisionResponse)
async def get_division(division_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Division, division_id, "Division")


@router.get("/zones", response_model=list[ZoneResponse])
async def list_zones(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(EOMZone).offset(skip).limit(limit).all()


@router.get("/zones/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, EOMZone, zone_id, "Zone")


@router.get("/regions", response_model=list[RegionResponse])
async def list_regions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(EOMRegion).offset(skip).limit(limit).all()


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(region_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, EOMRegion, region_id, "Region")


@router.get("/areas", response_model=list[AreaResponse])
async def list_areas(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(EOMArea).offset(skip).limit(limit).all()


@router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area(area_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, EOMArea, area_id, "Area")


@router.get("/clusters", response_model=list[ClusterResponse])
async def list_clusters(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(EOMCluster).offset(skip).limit(limit).all()


@router.get("/clusters/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, EOMCluster, cluster_id, "Cluster")


@router.get("/branches", response_model=list[BranchResponse])
async def list_branches(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(EOMBranch).offset(skip).limit(limit).all()


@router.get("/branches/{branch_id}", response_model=BranchResponse)
async def get_branch(branch_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, EOMBranch, branch_id, "Branch")


@router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Department).offset(skip).limit(limit).all()


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Department, department_id, "Department")


@router.get("/teams", response_model=list[TeamResponse])
async def list_teams(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Team).offset(skip).limit(limit).all()


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Team, team_id, "Team")


@router.get("/employees", response_model=list[EmployeeResponse])
async def list_employees(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Employee).offset(skip).limit(limit).all()


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Employee, employee_id, "Employee")


@router.get("/positions", response_model=list[PositionResponse])
async def list_positions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Position).offset(skip).limit(limit).all()


@router.get("/positions/{position_id}", response_model=PositionResponse)
async def get_position(position_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Position, position_id, "Position")


@router.get("/vendors", response_model=list[VendorResponse])
async def list_vendors(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Vendor).offset(skip).limit(limit).all()


@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Vendor, vendor_id, "Vendor")


@router.get("/assets", response_model=list[AssetResponse])
async def list_assets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(Asset).offset(skip).limit(limit).all()


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, Asset, asset_id, "Asset")


@router.get("/employee-hierarchy", response_model=list[EmployeeHierarchyResponse])
async def list_employee_hierarchy(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return db.query(EmployeeHierarchy).offset(skip).limit(limit).all()


@router.get("/employee-hierarchy/{hierarchy_id}", response_model=EmployeeHierarchyResponse)
async def get_employee_hierarchy(hierarchy_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, EmployeeHierarchy, hierarchy_id, "Employee Hierarchy")


@router.post("/customer-branch-mapping", response_model=CustomerBranchMappingResponse)
async def create_customer_branch_mapping(payload: CustomerBranchMappingCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    branch = db.query(EOMBranch).filter(EOMBranch.id == payload.branch_id).first()
    if branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")

    existing = (
        db.query(CustomerBranchMapping)
        .filter(CustomerBranchMapping.customer_id == customer.id, CustomerBranchMapping.status == "active")
        .order_by(CustomerBranchMapping.effective_from.desc())
        .first()
    )

    if existing and existing.branch_id == branch.id:
        raise HTTPException(status_code=409, detail="Customer is already assigned to this branch")

    mapping = CustomerBranchMapping(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        customer_id=customer.id,
        branch_id=branch.id,
        effective_from=datetime.utcnow(),
        status="active",
        transferred_from_branch_id=existing.branch_id if existing else None,
        transferred_by=payload.transferred_by,
        transferred_at=datetime.utcnow() if existing else None,
    )

    if existing:
        existing.status = "transferred"
        existing.effective_to = mapping.effective_from
        db.add(existing)

    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


@router.get("/customer-branch-mapping/{customer_id}", response_model=list[CustomerBranchMappingResponse])
async def get_customer_branch_mapping(customer_id: str, db: Session = Depends(get_db)):
    _get_or_404(db, Customer, customer_id, "Customer")
    return db.query(CustomerBranchMapping).filter(CustomerBranchMapping.customer_id == customer_id).order_by(CustomerBranchMapping.effective_from.desc()).all()

