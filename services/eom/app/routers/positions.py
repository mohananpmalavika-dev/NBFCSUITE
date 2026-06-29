from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional

from ..db import SessionLocal
from .. import models_position
from ..schemas_position import PositionCreate, PositionResponse, PositionUpdate, PositionListResponse
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


def get_position(db: Session, position_id: str):
    position = db.query(models_position.Position).filter(models_position.Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail='Position not found')
    return position


@router.post('/positions', response_model=PositionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_position(payload: PositionCreate, db: Session = Depends(get_db)):
    existing = db.query(models_position.Position).filter(models_position.Position.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Position code already exists')

    if payload.grade_id:
        from .. import models_grade
        grade = db.query(models_grade.Grade).filter(models_grade.Grade.id == payload.grade_id).first()
        if not grade:
            raise HTTPException(status_code=404, detail='Grade not found')
    if payload.team_id:
        from .. import models_team
        team = db.query(models_team.Team).filter(models_team.Team.id == payload.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail='Team not found')
    if payload.reports_to_position_id:
        existing_parent = db.query(models_position.Position).filter(models_position.Position.id == payload.reports_to_position_id).first()
        if not existing_parent:
            raise HTTPException(status_code=404, detail='Related position not found')

    position = models_position.Position(**payload.model_dump())
    db.add(position)
    db.commit()
    db.refresh(position)
    try:
        record_audit(db, 'position', position.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('POSITION_CREATED', {'id': position.id, 'code': position.code, 'title': position.title})
    return position


@router.get('/positions', response_model=PositionListResponse)
def list_positions(
    q: Optional[str] = None,
    status: Optional[str] = None,
    grade_id: Optional[str] = None,
    team_id: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(models_position.Position)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models_position.Position.code.ilike(like),
                models_position.Position.title.ilike(like),
            )
        )
    if status:
        query = query.filter(models_position.Position.status == status)
    if grade_id:
        query = query.filter(models_position.Position.grade_id == grade_id)
    if team_id:
        query = query.filter(models_position.Position.team_id == team_id)

    total = query.count()
    items = query.order_by(models_position.Position.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/positions/{position_id}', response_model=PositionResponse)
def get_position_endpoint(position_id: str, db: Session = Depends(get_db)):
    return get_position(db, position_id)


@router.put('/positions/{position_id}', response_model=PositionResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_position(position_id: str, payload: PositionUpdate, db: Session = Depends(get_db)):
    position = get_position(db, position_id)

    if payload.grade_id:
        from .. import models_grade
        grade = db.query(models_grade.Grade).filter(models_grade.Grade.id == payload.grade_id).first()
        if not grade:
            raise HTTPException(status_code=404, detail='Grade not found')
    if payload.team_id:
        from .. import models_team
        team = db.query(models_team.Team).filter(models_team.Team.id == payload.team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail='Team not found')
    if payload.reports_to_position_id:
        existing_parent = db.query(models_position.Position).filter(models_position.Position.id == payload.reports_to_position_id).first()
        if not existing_parent:
            raise HTTPException(status_code=404, detail='Related position not found')

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(position, field, value)
    db.add(position)
    db.commit()
    db.refresh(position)
    try:
        record_audit(db, 'position', position.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('POSITION_UPDATED', {'id': position.id})
    return position


@router.patch('/positions/{position_id}/status', response_model=PositionResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_position_status(position_id: str, status_body: dict, db: Session = Depends(get_db)):
    position = get_position(db, position_id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    position.status = new_status
    db.add(position)
    db.commit()
    db.refresh(position)
    try:
        record_audit(db, 'position', position.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('POSITION_STATUS_CHANGED', {'id': position.id, 'status': new_status})
    return position
