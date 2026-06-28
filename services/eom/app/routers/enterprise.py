from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import SessionLocal, engine
from .. import models, schemas
from ..events import publish_event

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/enterprises', response_model=schemas.EnterpriseResponse, status_code=status.HTTP_201_CREATED)
def create_enterprise(payload: schemas.EnterpriseCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Enterprise).filter(models.Enterprise.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Enterprise code already exists')
    ent = models.Enterprise(
        code=payload.code,
        name=payload.name,
        display_name=payload.display_name,
        short_name=payload.short_name,
        currency_code=payload.currency_code,
        timezone=payload.timezone,
        language=payload.language,
        fiscal_year_start=payload.fiscal_year_start,
        description=payload.description,
        status='active'
    )
    db.add(ent)
    db.commit()
    db.refresh(ent)

    # publish domain event (placeholder)
    try:
        publish_event('ENTERPRISE_CREATED', {'id': ent.id, 'code': ent.code, 'name': ent.name})
    except Exception:
        pass

    return ent


@router.get('/enterprises', response_model=list[schemas.EnterpriseResponse])
def list_enterprises(db: Session = Depends(get_db)):
    ents = db.query(models.Enterprise).order_by(models.Enterprise.created_at.desc()).all()
    return ents


@router.get('/enterprises/{id}', response_model=schemas.EnterpriseResponse)
def get_enterprise(id: str, db: Session = Depends(get_db)):
    ent = db.query(models.Enterprise).filter(models.Enterprise.id == id).first()
    if not ent:
        raise HTTPException(status_code=404, detail='Enterprise not found')
    return ent


@router.patch('/enterprises/{id}', response_model=schemas.EnterpriseResponse)
def update_enterprise(id: str, payload: schemas.EnterpriseUpdate, db: Session = Depends(get_db)):
    ent = db.query(models.Enterprise).filter(models.Enterprise.id == id).first()
    if not ent:
        raise HTTPException(status_code=404, detail='Enterprise not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ent, field, value)
    db.add(ent)
    db.commit()
    db.refresh(ent)
    publish_event('ENTERPRISE_UPDATED', {'id': ent.id})
    return ent


@router.delete('/enterprises/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_enterprise(id: str, db: Session = Depends(get_db)):
    ent = db.query(models.Enterprise).filter(models.Enterprise.id == id).first()
    if not ent:
        raise HTTPException(status_code=404, detail='Enterprise not found')
    db.delete(ent)
    db.commit()
    publish_event('ENTERPRISE_DELETED', {'id': id})
    return None


@router.post('/enterprises/{id}/status')
def set_enterprise_status(id: str, status_body: dict, db: Session = Depends(get_db)):
    ent = db.query(models.Enterprise).filter(models.Enterprise.id == id).first()
    if not ent:
        raise HTTPException(status_code=404, detail='Enterprise not found')
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    ent.status = new_status
    db.add(ent)
    db.commit()
    db.refresh(ent)
    publish_event('ENTERPRISE_STATUS_CHANGED', {'id': id, 'status': new_status})
    return {'id': id, 'status': new_status}


@router.get('/enterprises/{id}/health')
def enterprise_health(id: str, db: Session = Depends(get_db)):
    ent = db.query(models.Enterprise).filter(models.Enterprise.id == id).first()
    if not ent:
        raise HTTPException(status_code=404, detail='Enterprise not found')
    # lightweight health summary
    return {
        'id': ent.id,
        'status': ent.status,
        'ready': ent.status == 'active',
    }


@router.get('/enterprises/{id}/timeline')
def enterprise_timeline(id: str):
    # placeholder timeline; in prod this should read audit/event store
    return [
        {'when': '2026-01-01T00:00:00Z', 'event': 'created'},
    ]
