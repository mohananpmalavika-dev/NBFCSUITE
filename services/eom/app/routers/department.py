from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..db import SessionLocal
from .. import models_branch, models_legal, models_department
from ..schemas_department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    DepartmentListResponse,
    DepartmentDashboardResponse,
    DepartmentHealthResponse,
    DepartmentAnalyticsResponse,
)
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


def get_department(db: Session, department_id: str):
    department = db.query(models_department.Department).filter(models_department.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail='Department not found')
    return department


@router.post('/departments', response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    if payload.branch_id:
        branch = db.query(models_branch.Branch).filter(models_branch.Branch.id == payload.branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail='Branch not found')
    if payload.business_unit_id:
        bu = db.query(models_legal.BusinessUnit).filter(models_legal.BusinessUnit.id == payload.business_unit_id).first()
        if not bu:
            raise HTTPException(status_code=404, detail='Business unit not found')
    if payload.legal_entity_id:
        legal = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == payload.legal_entity_id).first()
        if not legal:
            raise HTTPException(status_code=404, detail='Legal entity not found')

    existing = db.query(models_department.Department).filter(models_department.Department.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Department code already exists')

    department = models_department.Department(
        code=payload.code,
        name=payload.name,
        status=payload.status or 'active',
        department_head=payload.department_head,
        branch_id=payload.branch_id,
        business_unit_id=payload.business_unit_id,
        legal_entity_id=payload.legal_entity_id,
        city=payload.city,
        region=payload.region,
        address=payload.address,
        phone=payload.phone,
        email=payload.email,
        description=payload.description,
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    try:
        record_audit(db, 'department', department.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('DEPARTMENT_CREATED', {'id': department.id, 'code': department.code, 'name': department.name})
    return department


@router.get('/departments', response_model=DepartmentListResponse)
def list_departments(q: Optional[str] = None, status: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_department.Department)
    if q:
        like = f"%{q}%"
        query = query.filter((models_department.Department.name.ilike(like)) | (models_department.Department.code.ilike(like)))
    if status:
        query = query.filter(models_department.Department.status == status)
    total = query.count()
    items = query.order_by(models_department.Department.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/departments/{department_id}', response_model=DepartmentResponse)
def get_department_endpoint(department_id: str, db: Session = Depends(get_db)):
    return get_department(db, department_id)


@router.put('/departments/{department_id}', response_model=DepartmentResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_department(department_id: str, payload: DepartmentUpdate, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    db.add(department)
    db.commit()
    db.refresh(department)
    try:
        record_audit(db, 'department', department.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('DEPARTMENT_UPDATED', {'id': department.id})
    return department


@router.patch('/departments/{department_id}/status', response_model=DepartmentResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_department_status(department_id: str, status_body: dict, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    department.status = new_status
    db.add(department)
    db.commit()
    db.refresh(department)
    try:
        record_audit(db, 'department', department.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('DEPARTMENT_STATUS_CHANGED', {'id': department.id, 'status': new_status})
    return department


@router.get('/departments/{department_id}/dashboard', response_model=DepartmentDashboardResponse)
def department_dashboard(department_id: str, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    health_score = 90 if department.status == 'active' else 65
    return {
        'id': department.id,
        'code': department.code,
        'name': department.name,
        'status': department.status,
        'department_head': department.department_head,
        'health_score': health_score,
        'active_personnel': 24,
        'teams': 4,
        'open_requests': 7,
        'budget_utilization': 72.5,
        'productivity_index': 84.3,
    }


@router.get('/departments/{department_id}/health', response_model=DepartmentHealthResponse)
def department_health(department_id: str, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    return {
        'id': department.id,
        'code': department.code,
        'name': department.name,
        'status': department.status,
        'health_score': 90 if department.status == 'active' else 65,
        'rating': '★★★★☆',
        'issues': [],
    }


@router.get('/departments/{department_id}/analytics', response_model=DepartmentAnalyticsResponse)
def department_analytics(department_id: str, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    return {
        'id': department.id,
        'code': department.code,
        'name': department.name,
        'status': department.status,
        'department_head': department.department_head,
        'headcount_growth': 4.2,
        'cost_variance': 1.8,
        'efficiency': 88.1,
        'compliance_score': 95.0,
    }
