from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import HeadOffice, ZonalOffice, RegionalOffice, AreaOffice
from ..schemas import HeadOfficeCreate, ZonalOfficeCreate, RegionalOfficeCreate, AreaOfficeCreate
from ..db import get_db
from uuid import uuid4

router = APIRouter(prefix="", tags=["offices"])


@router.post("/head-offices")
async def create_head_office(office: HeadOfficeCreate, db: Session = Depends(get_db)):
    head_office = HeadOffice(
        id=str(uuid4()),
        name=office.name,
        code=office.code,
        address=office.address,
        city=office.city,
        state=office.state,
        country=office.country,
        contact_email=office.contact_email,
        contact_phone=office.contact_phone,
        is_active=str(office.is_active).lower(),
    )
    db.add(head_office)
    db.commit()
    db.refresh(head_office)
    return head_office


@router.post("/zonal-offices")
async def create_zonal_office(office: ZonalOfficeCreate, db: Session = Depends(get_db)):
    head_office = db.query(HeadOffice).filter(HeadOffice.id == office.head_office_id).first()
    if not head_office:
        raise HTTPException(status_code=404, detail="Head office not found")

    zonal = ZonalOffice(
        id=str(uuid4()),
        head_office_id=office.head_office_id,
        name=office.name,
        code=office.code,
        address=office.address,
        city=office.city,
        state=office.state,
        country=office.country,
        contact_email=office.contact_email,
        contact_phone=office.contact_phone,
        is_active=str(office.is_active).lower(),
    )
    db.add(zonal)
    db.commit()
    db.refresh(zonal)
    return zonal


@router.post("/regional-offices")
async def create_regional_office(office: RegionalOfficeCreate, db: Session = Depends(get_db)):
    zonal_office = db.query(ZonalOffice).filter(ZonalOffice.id == office.zonal_office_id).first()
    if not zonal_office:
        raise HTTPException(status_code=404, detail="Zonal office not found")

    regional = RegionalOffice(
        id=str(uuid4()),
        zonal_office_id=office.zonal_office_id,
        name=office.name,
        code=office.code,
        address=office.address,
        city=office.city,
        state=office.state,
        country=office.country,
        contact_email=office.contact_email,
        contact_phone=office.contact_phone,
        is_active=str(office.is_active).lower(),
    )
    db.add(regional)
    db.commit()
    db.refresh(regional)
    return regional


@router.post("/area-offices")
async def create_area_office(office: AreaOfficeCreate, db: Session = Depends(get_db)):
    regional_office = db.query(RegionalOffice).filter(RegionalOffice.id == office.regional_office_id).first()
    if not regional_office:
        raise HTTPException(status_code=404, detail="Regional office not found")

    area = AreaOffice(
        id=str(uuid4()),
        regional_office_id=office.regional_office_id,
        name=office.name,
        code=office.code,
        address=office.address,
        city=office.city,
        state=office.state,
        country=office.country,
        contact_email=office.contact_email,
        contact_phone=office.contact_phone,
        is_active=str(office.is_active).lower(),
    )
    db.add(area)
    db.commit()
    db.refresh(area)
    return area
