from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas
from .. import models_legal, schemas_legal
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event
from typing import Optional

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/legal-entities', response_model=schemas_legal.LegalEntityResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_legal(payload: schemas_legal.LegalEntityCreate, db: Session = Depends(get_db)):
    existing = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Legal entity code already exists')
    le = models_legal.LegalEntity(
        code=payload.code,
        name=payload.name,
        display_name=payload.display_name,
        legal_type=payload.legal_type,
        country=payload.country,
        incorporation_date=payload.incorporation_date,
        cin=payload.cin,
        pan=payload.pan,
        gst=payload.gst,
        description=payload.description,
        status='draft',
    )
    db.add(le)
    db.commit()
    db.refresh(le)
    try:
        record_audit(db, 'legal_entity', le.id, 'created', {'code': le.code, 'name': le.name})
    except Exception:
        pass
    publish_event('LEGAL_ENTITY_CREATED', {'id': le.id, 'code': le.code, 'name': le.name})
    return le


@router.get('/legal-entities', response_model=schemas_legal.LegalEntityListResponse)
def list_legal(q: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_legal.LegalEntity)
    if q:
        like = f"%{q}%"
        query = query.filter((models_legal.LegalEntity.name.ilike(like)) | (models_legal.LegalEntity.code.ilike(like)))
    total = query.count()
    items = query.order_by(models_legal.LegalEntity.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/legal-entities/{id}', response_model=schemas_legal.LegalEntityResponse)
def get_legal(id: str, db: Session = Depends(get_db)):
    le = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == id).first()
    if not le:
        raise HTTPException(status_code=404, detail='Legal entity not found')
    return le


@router.patch('/legal-entities/{id}', response_model=schemas_legal.LegalEntityResponse)
def update_legal(id: str, payload: schemas_legal.LegalEntityUpdate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    le = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == id).first()
    if not le:
        raise HTTPException(status_code=404, detail='Legal entity not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(le, field, value)
    db.add(le)
    db.commit()
    db.refresh(le)
    try:
        record_audit(db, 'legal_entity', le.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('LEGAL_ENTITY_UPDATED', {'id': le.id})
    return le


@router.delete('/legal-entities/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_legal(id: str, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    le = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == id).first()
    if not le:
        raise HTTPException(status_code=404, detail='Legal entity not found')
    db.delete(le)
    db.commit()
    try:
        record_audit(db, 'legal_entity', id, 'deleted', None)
    except Exception:
        pass
    publish_event('LEGAL_ENTITY_DELETED', {'id': id})
    return None
