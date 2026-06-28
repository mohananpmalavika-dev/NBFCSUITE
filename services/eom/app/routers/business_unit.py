from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..db import SessionLocal
from .. import models_legal, schemas_legal
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


def get_business_unit(db: Session, id: str):
    bu = db.query(models_legal.BusinessUnit).filter(models_legal.BusinessUnit.id == id).first()
    if not bu:
        raise HTTPException(status_code=404, detail='Business unit not found')
    return bu


@router.post('/business-units', response_model=schemas_legal.BusinessUnitResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_business_unit(payload: schemas_legal.BusinessUnitCreate, db: Session = Depends(get_db)):
    legal_entity = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == payload.legal_entity_id).first()
    if not legal_entity:
        raise HTTPException(status_code=404, detail='Legal entity not found')

    existing = db.query(models_legal.BusinessUnit).filter(
        models_legal.BusinessUnit.legal_entity_id == payload.legal_entity_id,
        models_legal.BusinessUnit.business_unit_code == payload.business_unit_code,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail='Business unit code already exists for legal entity')

    bu = models_legal.BusinessUnit(
        legal_entity_id=payload.legal_entity_id,
        business_unit_code=payload.business_unit_code,
        business_unit_name=payload.business_unit_name,
        head=payload.head,
        status=payload.status or 'active',
        description=payload.description,
    )
    db.add(bu)
    db.commit()
    db.refresh(bu)
    try:
        record_audit(db, 'business_unit', bu.id, 'created', {'code': bu.business_unit_code, 'name': bu.business_unit_name})
    except Exception:
        pass
    publish_event('BUSINESS_UNIT_CREATED', {'id': bu.id, 'code': bu.business_unit_code, 'name': bu.business_unit_name})
    return bu


@router.get('/business-units', response_model=schemas_legal.BusinessUnitListResponse)
def list_business_units(q: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_legal.BusinessUnit)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models_legal.BusinessUnit.business_unit_name.ilike(like)) |
            (models_legal.BusinessUnit.business_unit_code.ilike(like))
        )
    total = query.count()
    items = query.order_by(models_legal.BusinessUnit.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/business-units/{id}', response_model=schemas_legal.BusinessUnitResponse)
def get_business_unit_endpoint(id: str, db: Session = Depends(get_db)):
    return get_business_unit(db, id)


@router.patch('/business-units/{id}', response_model=schemas_legal.BusinessUnitResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_business_unit(id: str, payload: schemas_legal.BusinessUnitUpdate, db: Session = Depends(get_db)):
    bu = get_business_unit(db, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bu, field, value)
    db.add(bu)
    db.commit()
    db.refresh(bu)
    try:
        record_audit(db, 'business_unit', bu.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('BUSINESS_UNIT_UPDATED', {'id': bu.id})
    return bu


@router.patch('/business-units/{id}/status', response_model=schemas_legal.BusinessUnitResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_business_unit_status(id: str, status_body: dict, db: Session = Depends(get_db)):
    bu = get_business_unit(db, id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    bu.status = new_status
    db.add(bu)
    db.commit()
    db.refresh(bu)
    try:
        record_audit(db, 'business_unit', bu.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('BUSINESS_UNIT_STATUS_CHANGED', {'id': bu.id, 'status': new_status})
    return bu


@router.get('/business-units/{id}/health', response_model=schemas_legal.BusinessUnitHealthResponse)
def business_unit_health(id: str, db: Session = Depends(get_db)):
    bu = get_business_unit(db, id)
    missing_head = 1 if not bu.head else 0
    health_score = max(0, 100 - missing_head * 25 - (0 if bu.status == 'active' else 20))
    return {
        'health_score': health_score,
        'missing_head': missing_head,
        'status': bu.status,
        'legal_entity_id': bu.legal_entity_id,
    }


@router.get('/business-units/{id}/analytics', response_model=schemas_legal.BusinessUnitAnalyticsResponse)
def business_unit_analytics(id: str, db: Session = Depends(get_db)):
    bu = get_business_unit(db, id)
    return {
        'id': bu.id,
        'business_unit_code': bu.business_unit_code,
        'business_unit_name': bu.business_unit_name,
        'status': bu.status,
        'head': bu.head,
        'legal_entity_id': bu.legal_entity_id,
        'revenue': 0.0,
        'cost': 0.0,
        'margin': 0.0,
        'headcount': 0,
    }


@router.get('/business-units/{id}/kpis', response_model=schemas_legal.BusinessUnitKpisResponse)
def business_unit_kpis(id: str, db: Session = Depends(get_db)):
    get_business_unit(db, id)
    return {
        'id': id,
        'kpis': [
            {
                'key': 'revenue_growth',
                'label': 'Revenue Growth',
                'value': 0.0,
                'target': 0.0,
                'status': 'unknown',
            },
            {
                'key': 'margin',
                'label': 'Margin',
                'value': 0.0,
                'target': 0.0,
                'status': 'unknown',
            },
            {
                'key': 'headcount',
                'label': 'Headcount',
                'value': 0.0,
                'target': 0.0,
                'status': 'unknown',
            },
        ],
    }
