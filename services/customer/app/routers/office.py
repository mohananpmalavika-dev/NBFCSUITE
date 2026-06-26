from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import uuid4

from ..db import get_db
from ..models import AreaOffice, HeadOffice, RegionalOffice, ZonalOffice
from ..schemas import (
    AreaCreate,
    AreaOfficeCreate,
    AreaResponse,
    AreaUpdate,
    HeadOfficeCreate,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationTreeResponse,
    OrganizationUpdate,
    RegionCreate,
    RegionResponse,
    RegionUpdate,
    RegionalOfficeCreate,
    ZonalOfficeCreate,
    ZoneCreate,
    ZoneResponse,
    ZoneUpdate,
)

router = APIRouter(prefix="", tags=["hierarchy"])


def _office_fields(payload):
    return {
        "name": payload.name,
        "code": payload.code,
        "address": payload.address,
        "city": payload.city,
        "state": payload.state,
        "country": payload.country,
        "contact_email": payload.contact_email,
        "contact_phone": payload.contact_phone,
        "is_active": str(payload.is_active).lower(),
    }


def _apply_update(entity, payload):
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "is_active" and value is not None:
            value = str(value).lower()
        setattr(entity, field, value)
    return entity


def _get_or_404(db: Session, model, entity_id: str, label: str):
    entity = db.query(model).filter(model.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return entity


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(organization: OrganizationCreate, db: Session = Depends(get_db)):
    entity = HeadOffice(id=str(uuid4()), **_office_fields(organization))
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/head-offices", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_head_office(office: HeadOfficeCreate, db: Session = Depends(get_db)):
    return await create_organization(OrganizationCreate(**office.model_dump()), db)


@router.get("/organizations", response_model=list[OrganizationResponse])
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return db.query(HeadOffice).offset(skip).limit(limit).all()


@router.get("/organizations/hierarchy", response_model=list[OrganizationTreeResponse])
async def get_organization_hierarchy(db: Session = Depends(get_db)):
    return db.query(HeadOffice).all()


@router.get("/organizations/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, HeadOffice, organization_id, "Organization")


@router.put("/organizations/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    update: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    entity = _get_or_404(db, HeadOffice, organization_id, "Organization")
    _apply_update(entity, update)
    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/organizations/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(organization_id: str, db: Session = Depends(get_db)):
    entity = _get_or_404(db, HeadOffice, organization_id, "Organization")
    db.delete(entity)
    db.commit()
    return None


@router.post("/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(zone: ZoneCreate, db: Session = Depends(get_db)):
    _get_or_404(db, HeadOffice, zone.organization_id, "Organization")
    entity = ZonalOffice(id=str(uuid4()), head_office_id=zone.organization_id, **_office_fields(zone))
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/zonal-offices", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zonal_office(office: ZonalOfficeCreate, db: Session = Depends(get_db)):
    return await create_zone(
        ZoneCreate(organization_id=office.head_office_id, **_office_fields(office)),
        db,
    )


@router.get("/zones", response_model=list[ZoneResponse])
async def list_zones(
    organization_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(ZonalOffice)
    if organization_id:
        query = query.filter(ZonalOffice.head_office_id == organization_id)
    return query.offset(skip).limit(limit).all()


@router.get("/zones/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, ZonalOffice, zone_id, "Zone")


@router.put("/zones/{zone_id}", response_model=ZoneResponse)
async def update_zone(zone_id: str, update: ZoneUpdate, db: Session = Depends(get_db)):
    entity = _get_or_404(db, ZonalOffice, zone_id, "Zone")
    _apply_update(entity, update)
    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/zones/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(zone_id: str, db: Session = Depends(get_db)):
    entity = _get_or_404(db, ZonalOffice, zone_id, "Zone")
    db.delete(entity)
    db.commit()
    return None


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
async def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    _get_or_404(db, ZonalOffice, region.zone_id, "Zone")
    entity = RegionalOffice(id=str(uuid4()), zonal_office_id=region.zone_id, **_office_fields(region))
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/regional-offices", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
async def create_regional_office(office: RegionalOfficeCreate, db: Session = Depends(get_db)):
    return await create_region(
        RegionCreate(zone_id=office.zonal_office_id, **_office_fields(office)),
        db,
    )


@router.get("/regions", response_model=list[RegionResponse])
async def list_regions(
    zone_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(RegionalOffice)
    if zone_id:
        query = query.filter(RegionalOffice.zonal_office_id == zone_id)
    return query.offset(skip).limit(limit).all()


@router.get("/regions/{region_id}", response_model=RegionResponse)
async def get_region(region_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, RegionalOffice, region_id, "Region")


@router.put("/regions/{region_id}", response_model=RegionResponse)
async def update_region(region_id: str, update: RegionUpdate, db: Session = Depends(get_db)):
    entity = _get_or_404(db, RegionalOffice, region_id, "Region")
    _apply_update(entity, update)
    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/regions/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_region(region_id: str, db: Session = Depends(get_db)):
    entity = _get_or_404(db, RegionalOffice, region_id, "Region")
    db.delete(entity)
    db.commit()
    return None


@router.post("/areas", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
async def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    _get_or_404(db, RegionalOffice, area.region_id, "Region")
    entity = AreaOffice(id=str(uuid4()), regional_office_id=area.region_id, **_office_fields(area))
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/area-offices", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
async def create_area_office(office: AreaOfficeCreate, db: Session = Depends(get_db)):
    return await create_area(
        AreaCreate(region_id=office.regional_office_id, **_office_fields(office)),
        db,
    )


@router.get("/areas", response_model=list[AreaResponse])
async def list_areas(
    region_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(AreaOffice)
    if region_id:
        query = query.filter(AreaOffice.regional_office_id == region_id)
    return query.offset(skip).limit(limit).all()


@router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area(area_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, AreaOffice, area_id, "Area")


@router.put("/areas/{area_id}", response_model=AreaResponse)
async def update_area(area_id: str, update: AreaUpdate, db: Session = Depends(get_db)):
    entity = _get_or_404(db, AreaOffice, area_id, "Area")
    _apply_update(entity, update)
    db.commit()
    db.refresh(entity)
    return entity


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_area(area_id: str, db: Session = Depends(get_db)):
    entity = _get_or_404(db, AreaOffice, area_id, "Area")
    db.delete(entity)
    db.commit()
    return None
