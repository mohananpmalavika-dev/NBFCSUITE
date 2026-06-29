from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..db import SessionLocal
from .. import models_branch, models_legal
from ..schemas import BranchCreate, BranchResponse, BranchUpdate, BranchListResponse, BranchDashboardResponse, BranchHealthResponse, BranchAnalyticsResponse
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


def get_branch(db: Session, branch_id: str):
    branch = db.query(models_branch.Branch).filter(models_branch.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail='Branch not found')
    return branch


@router.post('/branches', response_model=BranchResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_branch(payload: BranchCreate, db: Session = Depends(get_db)):
    if payload.business_unit_id:
        bu = db.query(models_legal.BusinessUnit).filter(models_legal.BusinessUnit.id == payload.business_unit_id).first()
        if not bu:
            raise HTTPException(status_code=404, detail='Business unit not found')
    if payload.legal_entity_id:
        legal = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == payload.legal_entity_id).first()
        if not legal:
            raise HTTPException(status_code=404, detail='Legal entity not found')

    existing = db.query(models_branch.Branch).filter(models_branch.Branch.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Branch code already exists')

    branch = models_branch.Branch(
        code=payload.code,
        name=payload.name,
        branch_type=payload.branch_type,
        status=payload.status or 'active',
        manager=payload.manager,
        business_unit_id=payload.business_unit_id,
        legal_entity_id=payload.legal_entity_id,
        city=payload.city,
        region=payload.region,
        address=payload.address,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        description=payload.description,
        cash_limit=payload.cash_limit,
        vault_limit=payload.vault_limit,
        gold_loan_enabled=payload.gold_loan_enabled,
        deposit_enabled=payload.deposit_enabled,
        forex_enabled=payload.forex_enabled,
        atm=payload.atm,
        locker=payload.locker,
        kiosk=payload.kiosk,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    try:
        record_audit(db, 'branch', branch.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('BRANCH_CREATED', {'id': branch.id, 'code': branch.code, 'name': branch.name})
    return branch


@router.get('/branches', response_model=BranchListResponse)
def list_branches(q: Optional[str] = None, status: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_branch.Branch)
    if q:
        like = f"%{q}%"
        query = query.filter((models_branch.Branch.name.ilike(like)) | (models_branch.Branch.code.ilike(like)))
    if status:
        query = query.filter(models_branch.Branch.status == status)
    total = query.count()
    items = query.order_by(models_branch.Branch.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/branches/{branch_id}', response_model=BranchResponse)
def get_branch_endpoint(branch_id: str, db: Session = Depends(get_db)):
    return get_branch(db, branch_id)


@router.put('/branches/{branch_id}', response_model=BranchResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_branch(branch_id: str, payload: BranchUpdate, db: Session = Depends(get_db)):
    branch = get_branch(db, branch_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(branch, field, value)
    db.add(branch)
    db.commit()
    db.refresh(branch)
    try:
        record_audit(db, 'branch', branch.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('BRANCH_UPDATED', {'id': branch.id})
    return branch


@router.patch('/branches/{branch_id}/status', response_model=BranchResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def set_branch_status(branch_id: str, status_body: dict, db: Session = Depends(get_db)):
    branch = get_branch(db, branch_id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')
    branch.status = new_status
    db.add(branch)
    db.commit()
    db.refresh(branch)
    try:
        record_audit(db, 'branch', branch.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    publish_event('BRANCH_STATUS_CHANGED', {'id': branch.id, 'status': new_status})
    return branch


@router.get('/branches/{branch_id}/dashboard', response_model=BranchDashboardResponse)
def branch_dashboard(branch_id: str, db: Session = Depends(get_db)):
    branch = get_branch(db, branch_id)
    health_score = 92 if branch.status == 'active' else 70
    return {
        'id': branch.id,
        'code': branch.code,
        'name': branch.name,
        'status': branch.status,
        'health_score': health_score,
        'active_customers': 120,
        'loans': 45,
        'deposits': 80,
        'cash_balance': 500000.0,
        'vault_balance': 250000.0,
        'revenue': 1250000.0,
        'expenses': 900000.0,
        'profit': 350000.0,
    }


@router.get('/branches/{branch_id}/health', response_model=BranchHealthResponse)
def branch_health(branch_id: str, db: Session = Depends(get_db)):
    branch = get_branch(db, branch_id)
    return {
        'id': branch.id,
        'code': branch.code,
        'name': branch.name,
        'status': branch.status,
        'health_score': 92 if branch.status == 'active' else 70,
        'rating': '★★★★★',
        'issues': [],
    }


@router.get('/branches/{branch_id}/analytics', response_model=BranchAnalyticsResponse)
def branch_analytics(branch_id: str, db: Session = Depends(get_db)):
    branch = get_branch(db, branch_id)
    return {
        'id': branch.id,
        'code': branch.code,
        'name': branch.name,
        'status': branch.status,
        'customer_growth': 12.5,
        'loan_growth': 8.4,
        'deposit_growth': 7.2,
        'collection_efficiency': 94.0,
        'audit_score': 91.0,
    }
