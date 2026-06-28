from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas
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


@router.post('/brands', response_model=schemas.BrandResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_brand(payload: schemas.BrandCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Brand).filter(models.Brand.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Brand code already exists')
    b = models.Brand(code=payload.code, name=payload.name, description=payload.description, status='active')
    db.add(b)
    db.commit()
    db.refresh(b)
    try:
        record_audit(db, 'brand', b.id, 'created', {'code': b.code, 'name': b.name})
    except Exception:
        pass
    publish_event('BRAND_CREATED', {'id': b.id, 'code': b.code, 'name': b.name})
    return b


@router.get('/brands', response_model=schemas.BrandListResponse)
def list_brands(q: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models.Brand)
    if q:
        like = f"%{q}%"
        query = query.filter((models.Brand.name.ilike(like)) | (models.Brand.code.ilike(like)))
    total = query.count()
    items = query.order_by(models.Brand.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/brands/{id}', response_model=schemas.BrandResponse)
def get_brand(id: str, db: Session = Depends(get_db)):
    b = db.query(models.Brand).filter(models.Brand.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail='Brand not found')
    return b


@router.patch('/brands/{id}', response_model=schemas.BrandResponse)
def update_brand(id: str, payload: schemas.BrandUpdate, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    b = db.query(models.Brand).filter(models.Brand.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail='Brand not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(b, field, value)
    db.add(b)
    db.commit()
    db.refresh(b)
    try:
        record_audit(db, 'brand', b.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('BRAND_UPDATED', {'id': b.id})
    return b


@router.delete('/brands/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(id: str, db: Session = Depends(get_db), _=Depends(require_role('enterprise.admin'))):
    b = db.query(models.Brand).filter(models.Brand.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail='Brand not found')
    db.delete(b)
    db.commit()
    try:
        record_audit(db, 'brand', id, 'deleted', None)
    except Exception:
        pass
    publish_event('BRAND_DELETED', {'id': id})
    return None


@router.get('/brands/{id}/audit', response_model=schemas.AuditListResponse)
def brand_audit(id: str, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models.AuditEntry).filter(models.AuditEntry.entity_type == 'brand', models.AuditEntry.entity_id == id)
    total = query.count()
    items = query.order_by(models.AuditEntry.created_at.desc()).limit(limit).offset(offset).all()
    # Convert payloads to strings (they are stored as JSON strings)
    return {'total': total, 'items': items}
