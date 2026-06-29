from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .db import SessionLocal
from .auth import require_role
from .audit import record_audit
from .events import publish_event

from . import models_financial_organization as m
from . import schemas_financial_organization as s


router = APIRouter(prefix='/api/v1/finance', tags=['finance'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _code_unique_error(entity: str, code: str) -> HTTPException:
    return HTTPException(status_code=400, detail=f'{entity} code already exists: {code}')


def _cost_center_or_404(db: Session, id: str) -> m.CostCenter:
    row = db.query(m.CostCenter).filter(m.CostCenter.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Cost center not found')
    return row


def _profit_center_or_404(db: Session, id: str) -> m.ProfitCenter:
    row = db.query(m.ProfitCenter).filter(m.ProfitCenter.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Profit center not found')
    return row


def _budget_or_404(db: Session, id: str) -> m.Budget:
    row = db.query(m.Budget).filter(m.Budget.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Budget not found')
    return row


def _internal_order_or_404(db: Session, id: str) -> m.InternalOrder:
    row = db.query(m.InternalOrder).filter(m.InternalOrder.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail='Internal order not found')
    return row


_ALLOWED_COST_CENTER_TRANSITIONS = {
    'draft': ['active', 'inactive'],
    'active': ['inactive'],
    'inactive': [],
}

_ALLOWED_PROFIT_CENTER_TRANSITIONS = {
    'draft': ['active', 'inactive'],
    'active': ['inactive'],
    'inactive': [],
}

_ALLOWED_INTERNAL_ORDER_TRANSITIONS = {
    'draft': ['approved'],
    'approved': ['open'],
    'open': ['active'],
    'active': ['closed'],
    'closed': ['archived'],
    'archived': [],
}


# -----------------------------
# Cost centers
# -----------------------------
@router.get('/cost-centers', response_model=s.CostCenterListResponse)
def list_cost_centers(
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(m.CostCenter)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(m.CostCenter.name.ilike(like), m.CostCenter.code.ilike(like)))
    if status:
        query = query.filter(m.CostCenter.status == status)

    total = query.count()
    rows = query.order_by(m.CostCenter.created_at.desc()).limit(limit).offset(offset).all()

    return {
        'total': total,
        'items': [s.CostCenterResponse.model_validate(r) for r in rows],
    }


@router.post('/cost-centers', response_model=s.CostCenterResponse, status_code=status.HTTP_201_CREATED)
def create_cost_center(payload: s.CostCenterCreate, db: Session = Depends(get_db)):
    existing = db.query(m.CostCenter).filter(m.CostCenter.code == payload.code).first()
    if existing:
        raise _code_unique_error('Cost center', payload.code)

    row = m.CostCenter(
        enterprise_id=payload.enterprise_id,
        code=payload.code,
        name=payload.name,
        category=payload.category,
        status=payload.status or 'draft',
        description=payload.description,
        parent_cost_center_id=payload.parent_cost_center_id,
        budget_owner=payload.budget_owner,
        currency=payload.currency,
        gl_mapping=payload.gl_mapping,
        department_id=payload.department_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        record_audit(db, 'cost_center', row.id, 'created', {'code': row.code, 'name': row.name})
    except Exception:
        pass

    try:
        publish_event('COST_CENTER_CREATED', {'id': row.id, 'code': row.code, 'name': row.name})
    except Exception:
        pass

    return row


@router.get('/cost-centers/{id}', response_model=s.CostCenterResponse)
def get_cost_center(id: str, db: Session = Depends(get_db)):
    return _cost_center_or_404(db, id)


@router.put('/cost-centers/{id}', response_model=s.CostCenterResponse)
def update_cost_center(
    id: str,
    payload: s.CostCenterUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _cost_center_or_404(db, id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch('/cost-centers/{id}/status')
def set_cost_center_status(
    id: str,
    status_body: dict,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _cost_center_or_404(db, id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')

    allowed = _ALLOWED_COST_CENTER_TRANSITIONS.get(row.status, [])
    if new_status not in allowed and new_status != row.status:
        raise HTTPException(status_code=400, detail=f'Invalid status transition from {row.status} to {new_status}')

    row.status = new_status
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        record_audit(db, 'cost_center', row.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    try:
        publish_event('COST_CENTER_UPDATED', {'id': row.id, 'status': new_status})
    except Exception:
        pass

    return {'id': row.id, 'status': row.status}


# -----------------------------
# Profit centers
# -----------------------------
@router.get('/profit-centers', response_model=s.ProfitCenterListResponse)
def list_profit_centers(
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(m.ProfitCenter)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(m.ProfitCenter.name.ilike(like), m.ProfitCenter.code.ilike(like)))
    if status:
        query = query.filter(m.ProfitCenter.status == status)

    total = query.count()
    rows = query.order_by(m.ProfitCenter.created_at.desc()).limit(limit).offset(offset).all()

    return {'total': total, 'items': [s.ProfitCenterResponse.model_validate(r) for r in rows]}


@router.post('/profit-centers', response_model=s.ProfitCenterResponse, status_code=status.HTTP_201_CREATED)
def create_profit_center(payload: s.ProfitCenterCreate, db: Session = Depends(get_db)):
    existing = db.query(m.ProfitCenter).filter(m.ProfitCenter.code == payload.code).first()
    if existing:
        raise _code_unique_error('Profit center', payload.code)

    row = m.ProfitCenter(
        enterprise_id=payload.enterprise_id,
        code=payload.code,
        name=payload.name,
        category=payload.category,
        status=payload.status or 'draft',
        description=payload.description,
        parent_profit_center_id=payload.parent_profit_center_id,
        responsibility_owner=payload.responsibility_owner,
        currency=payload.currency,
        gl_mapping=payload.gl_mapping,
        branch_id=payload.branch_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        record_audit(db, 'profit_center', row.id, 'created', {'code': row.code, 'name': row.name})
    except Exception:
        pass
    try:
        publish_event('PROFIT_CENTER_CREATED', {'id': row.id, 'code': row.code, 'name': row.name})
    except Exception:
        pass

    return row


@router.get('/profit-centers/{id}', response_model=s.ProfitCenterResponse)
def get_profit_center(id: str, db: Session = Depends(get_db)):
    return _profit_center_or_404(db, id)


@router.put('/profit-centers/{id}', response_model=s.ProfitCenterResponse)
def update_profit_center(
    id: str,
    payload: s.ProfitCenterUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _profit_center_or_404(db, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch('/profit-centers/{id}/status')
def set_profit_center_status(
    id: str,
    status_body: dict,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _profit_center_or_404(db, id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')

    allowed = _ALLOWED_PROFIT_CENTER_TRANSITIONS.get(row.status, [])
    if new_status not in allowed and new_status != row.status:
        raise HTTPException(status_code=400, detail=f'Invalid status transition from {row.status} to {new_status}')

    row.status = new_status
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        record_audit(db, 'profit_center', row.id, 'status_changed', {'status': new_status})
    except Exception:
        pass
    try:
        publish_event('PROFIT_CENTER_UPDATED', {'id': row.id, 'status': new_status})
    except Exception:
        pass

    return {'id': row.id, 'status': row.status}


# -----------------------------
# Budgets (MVP)
# -----------------------------
@router.get('/budgets', response_model=s.BudgetListResponse)
def list_budgets(
    budget_center_id: Optional[str] = None,
    profit_center_id: Optional[str] = None,
    cost_center_id: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(m.Budget)
    if budget_center_id:
        query = query.filter(m.Budget.budget_center_id == budget_center_id)
    if profit_center_id:
        query = query.filter(m.Budget.profit_center_id == profit_center_id)
    if cost_center_id:
        query = query.filter(m.Budget.cost_center_id == cost_center_id)
    if year is not None:
        query = query.filter(m.Budget.year == year)

    total = query.count()
    rows = query.order_by(m.Budget.created_at.desc()).limit(limit).offset(offset).all()

    return {'total': total, 'items': [s.BudgetResponse.model_validate(r) for r in rows]}


@router.post('/budgets', response_model=s.BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(payload: s.BudgetCreate, db: Session = Depends(get_db)):
    row = m.Budget(
        enterprise_id=payload.enterprise_id,
        budget_center_id=payload.budget_center_id,
        cost_center_id=payload.cost_center_id,
        profit_center_id=payload.profit_center_id,
        year=payload.year,
        status=payload.status or 'original',
        original_total=payload.original_total,
        revised_total=payload.revised_total,
        committed_total=payload.committed_total,
        actual_total=payload.actual_total,
        forecast_total=payload.forecast_total,
        currency=payload.currency,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    publish_event('BUDGET_CREATED', {'id': row.id})
    try:
        record_audit(db, 'budget', row.id, 'created', payload.model_dump())
    except Exception:
        pass

    return row


@router.get('/budgets/{id}', response_model=s.BudgetResponse)
def get_budget(id: str, db: Session = Depends(get_db)):
    return _budget_or_404(db, id)


@router.put('/budgets/{id}', response_model=s.BudgetResponse)
def update_budget(
    id: str,
    payload: s.BudgetUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _budget_or_404(db, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    try:
        record_audit(db, 'budget', row.id, 'updated', payload.model_dump())
    except Exception:
        pass
    publish_event('BUDGET_REVISED', {'id': row.id})
    return row


# -----------------------------
# Internal orders
# -----------------------------
@router.get('/internal-orders', response_model=s.InternalOrderListResponse)
def list_internal_orders(
    q: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(m.InternalOrder)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(m.InternalOrder.name.ilike(like), m.InternalOrder.code.ilike(like)))
    if status:
        query = query.filter(m.InternalOrder.status == status)

    total = query.count()
    rows = query.order_by(m.InternalOrder.created_at.desc()).limit(limit).offset(offset).all()

    return {'total': total, 'items': [s.InternalOrderResponse.model_validate(r) for r in rows]}


@router.post('/internal-orders', response_model=s.InternalOrderResponse, status_code=status.HTTP_201_CREATED)
def create_internal_order(payload: s.InternalOrderCreate, db: Session = Depends(get_db)):
    existing = db.query(m.InternalOrder).filter(m.InternalOrder.code == payload.code).first()
    if existing:
        raise _code_unique_error('Internal order', payload.code)

    row = m.InternalOrder(
        enterprise_id=payload.enterprise_id,
        code=payload.code,
        name=payload.name,
        description=payload.description,
        status=payload.status or 'draft',
        cost_center_id=payload.cost_center_id,
        profit_center_id=payload.profit_center_id,
        budget_center_id=payload.budget_center_id,
        responsibility_center_id=payload.responsibility_center_id,
        investment_center_id=payload.investment_center_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        record_audit(db, 'internal_order', row.id, 'created', payload.model_dump())
    except Exception:
        pass
    try:
        publish_event('INTERNAL_ORDER_OPENED', {'id': row.id, 'status': row.status})
    except Exception:
        pass

    return row


@router.get('/internal-orders/{id}', response_model=s.InternalOrderResponse)
def get_internal_order(id: str, db: Session = Depends(get_db)):
    return _internal_order_or_404(db, id)


@router.put('/internal-orders/{id}', response_model=s.InternalOrderResponse)
def update_internal_order(
    id: str,
    payload: s.InternalOrderUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _internal_order_or_404(db, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch('/internal-orders/{id}/status')
def set_internal_order_status(
    id: str,
    status_body: dict,
    db: Session = Depends(get_db),
    _=Depends(require_role('enterprise.admin')),
):
    row = _internal_order_or_404(db, id)
    new_status = status_body.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail='status required')

    allowed = _ALLOWED_INTERNAL_ORDER_TRANSITIONS.get(row.status, [])
    if new_status not in allowed and new_status != row.status:
        raise HTTPException(status_code=400, detail=f'Invalid status transition from {row.status} to {new_status}')

    row.status = new_status
    db.add(row)
    db.commit()
    db.refresh(row)

    try:
        record_audit(db, 'internal_order', row.id, 'status_changed', {'status': new_status})
    except Exception:
        pass

    try:
        publish_event('INTERNAL_ORDER_CLOSED' if new_status in ['closed', 'archived'] else 'INTERNAL_ORDER_UPDATED', {'id': row.id, 'status': new_status})
    except Exception:
        pass

    return {'id': row.id, 'status': row.status}


# -----------------------------
# Allocations (stub)
# -----------------------------
@router.get('/allocations')
def list_allocations():
    return {'items': [], 'total': 0}


@router.post('/allocations')
def execute_allocation(payload: dict):
    return {'executed': False, 'message': 'Allocation engine not implemented in MVP', 'payload': payload}


# -----------------------------
# Dashboard (MVP)
# -----------------------------
@router.get('/dashboard')
def finance_dashboard(db: Session = Depends(get_db)):
    cost_centers = db.query(func.count(m.CostCenter.id)).scalar() or 0
    profit_centers = db.query(func.count(m.ProfitCenter.id)).scalar() or 0
    internal_orders = db.query(func.count(m.InternalOrder.id)).scalar() or 0
    budgets = db.query(func.count(m.Budget.id)).scalar() or 0

    # health score heuristic
    score = min(100, int((cost_centers + profit_centers + internal_orders + budgets) * 10)) if (cost_centers + profit_centers + internal_orders + budgets) else 0
    rating = '★★★★★' if score >= 90 else '★★★★☆' if score >= 75 else '★★★☆☆' if score >= 60 else '★★☆☆☆' if score >= 45 else '★☆☆☆☆'

    return {
        'kpis': {
            'cost_centers': cost_centers,
            'profit_centers': profit_centers,
            'budgets': budgets,
            'internal_orders': internal_orders,
            'health_score': score,
            'health_rating': rating,
        },
        'summary': {
            'status': 'setup-required' if score < 60 else 'attention' if score < 85 else 'strong',
        },
    }

