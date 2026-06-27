from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
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
    LegalEntityCreate,
    BusinessUnitCreate,
    ZoneCreate,
    RegionCreate,
    AreaCreate,
    ClusterCreate,
    BranchCreate,
    DepartmentCreate,
    EmployeeCreate,
    EmployeeHierarchyCreate,
)

router = APIRouter(prefix="/eom", tags=["eom"])


def _require_super_admin():
    # Repository currently lacks a shared auth dependency in the inspected files.
    # Implementing a placeholder guard here that will be upgraded once the auth integration is located.
    # For now, we enforce via an HTTP 501 to make the missing integration explicit.
    raise HTTPException(status_code=501, detail="Super Admin guard not implemented in this service yet")


@router.post("/brands")
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


@router.post("/legal-entities")
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


@router.post("/business-units")
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


@router.post("/zones")
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


@router.post("/regions")
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


@router.post("/areas")
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


@router.post("/clusters")
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


@router.post("/branches")
async def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    _require_super_admin()

    # Simple uniqueness check by branch_code
    existing = db.query(EOMBranch).filter(EOMBranch.branch_code == payload.branch_code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Branch already exists")

    b = EOMBranch(
        id=str(payload.branch_code).strip()[:36].ljust(36, "0"),
        tenant_id=payload.tenant_id,
        branch_code=payload.branch_code,
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


@router.post("/departments")
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


@router.post("/employees")
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


@router.post("/employee-hierarchy")
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

