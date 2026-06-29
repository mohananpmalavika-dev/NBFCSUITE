from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..db import SessionLocal
from .. import models_section
from ..schemas_section import SectionCreate, SectionResponse, SectionUpdate, SectionListResponse, SectionDashboardResponse, SectionHealthResponse
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


def get_section(db: Session, section_id: str):
    section = db.query(models_section.Section).filter(models_section.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail='Section not found')
    return section


@router.post('/sections', response_model=SectionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_section(payload: SectionCreate, db: Session = Depends(get_db)):
    existing = db.query(models_section.Section).filter(models_section.Section.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Section code already exists')

    section = models_section.Section(**payload.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    try:
        record_audit(db, 'section', section.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('SECTION_CREATED', {'id': section.id, 'code': section.code, 'name': section.name})
    return section


@router.get('/sections', response_model=SectionListResponse)
def list_sections(q: Optional[str] = None, status: Optional[str] = None, department_id: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_section.Section)
    if q:
        like = f"%{q}%"
        query = query.filter((models_section.Section.name.ilike(like)) | (models_section.Section.code.ilike(like)))
    if status:
        query = query.filter(models_section.Section.status == status)
    if department_id:
        query = query.filter(models_section.Section.department_id == department_id)
    total = query.count()
    items = query.order_by(models_section.Section.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/sections/{section_id}', response_model=SectionResponse)
def get_section_endpoint(section_id: str, db: Session = Depends(get_db)):
    return get_section(db, section_id)


@router.put('/sections/{section_id}', response_model=SectionResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_section(section_id: str, payload: SectionUpdate, db: Session = Depends(get_db)):
    section = get_section(db, section_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.add(section)
    db.commit()
    db.refresh(section)
    try:
        record_audit(db, 'section', section.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('SECTION_UPDATED', {'id': section.id})
    return section


@router.patch('/sections/{section_id}/status', response_model=SectionResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_section_status(section_id: str, status_body: dict, db: Session = Depends(get_db)):
    section = get_section(db, section_id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    section.status = new_status
    db.add(section)
    db.commit()
    db.refresh(section)
    try:
        record_audit(db, 'section', section.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('SECTION_STATUS_CHANGED', {'id': section.id, 'status': new_status})
    return section


@router.get('/sections/{section_id}/dashboard', response_model=SectionDashboardResponse)
def section_dashboard(section_id: str, db: Session = Depends(get_db)):
    section = get_section(db, section_id)
    team_count = db.query(models_section.Section).filter(models_section.Section.id == section_id).count()  # placeholder
    try:
        from .. import models_team
        team_count = db.query(models_team.Team).filter(models_team.Team.section_id == section_id).count()
    except Exception:
        pass
    health_score = 90 if section.status == 'active' else 60
    return {
        'id': section.id,
        'code': section.code,
        'name': section.name,
        'status': section.status,
        'section_type': section.section_type,
        'section_head': section.section_head,
        'employees': 0,
        'teams': team_count,
        'projects': 0,
        'health_score': health_score,
    }


@router.get('/sections/{section_id}/health', response_model=SectionHealthResponse)
def section_health(section_id: str, db: Session = Depends(get_db)):
    section = get_section(db, section_id)
    score = 90 if section.status == 'active' else 60
    return {
        'id': section.id,
        'code': section.code,
        'name': section.name,
        'status': section.status,
        'health_score': score,
        'rating': '★★★★★' if score >= 85 else '★★★★☆' if score >= 70 else '★★★☆☆',
        'issues': [],
    }
