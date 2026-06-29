from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..db import SessionLocal
from .. import models_designation
from ..schemas_designation import DesignationCreate, DesignationResponse, DesignationUpdate, DesignationListResponse
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_designation(db: Session, designation_id: str):
    designation = db.query(models_designation.Designation).filter(models_designation.Designation.id == designation_id).first()
    if not designation:
        raise HTTPException(status_code=404, detail='Designation not found')
    return designation


@router.post('/designations', response_model=DesignationResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_designation(payload: DesignationCreate, db: Session = Depends(get_db)):
    existing = db.query(models_designation.Designation).filter(models_designation.Designation.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Designation code already exists')

    designation = models_designation.Designation(**payload.model_dump())
    db.add(designation)
    db.commit()
    db.refresh(designation)
    try:
        record_audit(db, 'designation', designation.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('DESIGNATION_CREATED', {'id': designation.id, 'code': designation.code, 'name': designation.name})
    return designation


@router.get('/designations', response_model=DesignationListResponse)
def list_designations(q: Optional[str] = None, status: Optional[str] = None, job_family_id: Optional[str] = None, grade_id: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_designation.Designation)
    if q:
        like = f"%{q}%"
        query = query.filter((models_designation.Designation.name.ilike(like)) | (models_designation.Designation.code.ilike(like)))
    if status:
        query = query.filter(models_designation.Designation.status == status)
    if job_family_id:
        query = query.filter(models_designation.Designation.job_family_id == job_family_id)
    if grade_id:
        query = query.filter(models_designation.Designation.grade_id == grade_id)
    total = query.count()
    items = query.order_by(models_designation.Designation.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/designations/{designation_id}', response_model=DesignationResponse)
def get_designation_endpoint(designation_id: str, db: Session = Depends(get_db)):
    return get_designation(db, designation_id)


@router.put('/designations/{designation_id}', response_model=DesignationResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_designation(designation_id: str, payload: DesignationUpdate, db: Session = Depends(get_db)):
    designation = get_designation(db, designation_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(designation, field, value)
    db.add(designation)
    db.commit()
    db.refresh(designation)
    try:
        record_audit(db, 'designation', designation.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('DESIGNATION_UPDATED', {'id': designation.id})
    return designation


@router.patch('/designations/{designation_id}/status', response_model=DesignationResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_designation_status(designation_id: str, status_body: dict, db: Session = Depends(get_db)):
    designation = get_designation(db, designation_id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    designation.status = new_status
    db.add(designation)
    db.commit()
    db.refresh(designation)
    try:
        record_audit(db, 'designation', designation.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('DESIGNATION_STATUS_CHANGED', {'id': designation.id, 'status': new_status})
    return designation
