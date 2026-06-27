import os
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Customer
from ..models_eom import (
    Brand,
    LegalEntity,
    BusinessUnit,
    EOMZone,
    EOMRegion,
    EOMArea,
    EOMCluster,
    EOMBranch,
    Department,
    Employee,
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
    EmployeeCreate,
    EmployeeHierarchyCreate,
    EmployeeHierarchyResponse,
    EmployeeResponse,
    LegalEntityCreate,
    LegalEntityResponse,
    RegionCreate,
    RegionResponse,
    AreaCreate,
    AreaResponse,
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


@router.post("/brands", response_model=BrandResponse)
async def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    # Super Admin only
    _require_super_admin()

    # Ensure idempotency by unique constraint on brand_code
    existing = db.query(Brand).filter(Brand.brand_code == payload.brand_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Brand already exists")

    brand = Brand(
        id=str(payload.brand_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
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

    existing = db.query(LegalEntity).filter(
        LegalEntity.brand_id == payload.brand_id,
        LegalEntity.entity_code == payload.entity_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Legal entity already exists")

    entity = LegalEntity(
        id=str(payload.entity_code).strip()[:36].ljust(36, "0"),
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

    existing = db.query(BusinessUnit).filter(
        BusinessUnit.legal_entity_id == payload.legal_entity_id,
        BusinessUnit.business_unit_code == payload.business_unit_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Business unit already exists")

    bu = BusinessUnit(
        id=str(payload.business_unit_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        legal_entity_id=payload.legal_entity_id,
        business_unit_code=payload.business_unit_code,
        business_unit_name=payload.business_unit_name,
        head=payload.head,
        status="active",
    )
    db.add(bu)
    db.commit()
    db.refresh(bu)
    return bu


@router.post("/zones", response_model=ZoneResponse)
async def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(EOMZone).filter(
        EOMZone.business_unit_id == payload.business_unit_id,
        EOMZone.zone_code == payload.zone_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Zone already exists")

    z = EOMZone(
        id=str(payload.zone_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        business_unit_id=payload.business_unit_id,
        zone_code=payload.zone_code,
        zone_name=payload.zone_name,
        zone_head=payload.zone_head,
        status="active",
    )
    db.add(z)
    db.commit()
    db.refresh(z)
    return z


@router.post("/regions", response_model=RegionResponse)
async def create_region(payload: RegionCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(EOMRegion).filter(
        EOMRegion.zone_id == payload.zone_id,
        EOMRegion.region_code == payload.region_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Region already exists")

    r = EOMRegion(
        id=str(payload.region_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        zone_id=payload.zone_id,
        region_code=payload.region_code,
        region_name=payload.region_name,
        regional_manager=payload.regional_manager,
        office_address=payload.office_address,
        status="active",
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.post("/areas", response_model=AreaResponse)
async def create_area(payload: AreaCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(EOMArea).filter(
        EOMArea.region_id == payload.region_id,
        EOMArea.area_code == payload.area_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Area already exists")

    a = EOMArea(
        id=str(payload.area_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        region_id=payload.region_id,
        area_code=payload.area_code,
        area_name=payload.area_name,
        area_manager=payload.area_manager,
        office_address=payload.office_address,
        status="active",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.post("/clusters", response_model=ClusterResponse)
async def create_cluster(payload: ClusterCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    existing = db.query(EOMCluster).filter(
        EOMCluster.area_id == payload.area_id,
        EOMCluster.cluster_code == payload.cluster_code,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Cluster already exists")

    c = EOMCluster(
        id=str(payload.cluster_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        area_id=payload.area_id,
        cluster_code=payload.cluster_code,
        cluster_name=payload.cluster_name,
        cluster_manager=payload.cluster_manager,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.post("/branches", response_model=BranchResponse)
async def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    branch_code = payload.branch_code
    if not branch_code:
        branch_code = payload.branch_name.strip().upper().replace(" ", "-")[:32]
    existing = db.query(EOMBranch).filter(EOMBranch.branch_code == branch_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Branch already exists")

    branch_id = str(branch_code).strip()[:36].ljust(36, "0") if branch_code else str(uuid4())
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

