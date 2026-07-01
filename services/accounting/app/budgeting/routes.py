from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.budgeting.models import Budget, BudgetForecast, BudgetVersion
from app.budgeting.schemas import (
    BudgetApproveRequest,
    BudgetAvailabilityRequest,
    BudgetAvailabilityResponse,
    BudgetCreate,
    BudgetDashboardResponse,
    BudgetForecastCreate,
    BudgetForecastResponse,
    BudgetResponse,
    BudgetRevisionCreate,
    BudgetVersionResponse,
    BudgetUpdate,
)
from app.db import get_db


router = APIRouter(prefix="/api/v1/budgets", tags=["budgeting"])


def _budget_response(budget: Budget) -> BudgetResponse:
    return BudgetResponse(
        id=budget.id,
        tenant_id=budget.tenant_id,
        budget_name=budget.budget_name,
        description=budget.description,
        financial_year=budget.financial_year,
        currency=budget.currency,
        status=budget.status,
        scope_level=budget.scope_level,
        scope_id=budget.scope_id,
        metadata=budget.metadata_json,
        created_by=budget.created_by,
        created_at=budget.created_at,
        updated_at=budget.updated_at,
        versions=[_version_response(version) for version in budget.versions],
        forecasts=[_forecast_response(forecast) for forecast in budget.forecasts],
    )


def _version_response(version: BudgetVersion) -> BudgetVersionResponse:
    return BudgetVersionResponse(
        id=version.id,
        version_name=version.version_name,
        amount=version.amount,
        status=version.status,
        period=version.period,
        metadata=version.metadata_json,
        created_at=version.created_at,
    )


def _forecast_response(forecast: BudgetForecast) -> BudgetForecastResponse:
    return BudgetForecastResponse(
        id=forecast.id,
        forecast_name=forecast.forecast_name,
        forecast_amount=forecast.forecast_amount,
        forecast_date=forecast.forecast_date,
        status=forecast.status,
        metadata=forecast.metadata_json,
        created_at=forecast.created_at,
    )


@router.post("/", response_model=BudgetResponse)
async def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    budget = Budget(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        budget_name=payload.budget_name,
        description=payload.description,
        financial_year=payload.financial_year,
        currency=payload.currency or "INR",
        status=payload.status or "draft",
        scope_level=payload.scope_level,
        scope_id=payload.scope_id,
        metadata_json=payload.metadata,
        created_by=payload.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(budget)
    if payload.initial_amount is not None:
        version = BudgetVersion(
            id=str(uuid4()),
            tenant_id=payload.tenant_id,
            budget_id=budget.id,
            version_name=payload.initial_version_name or "Original",
            amount=payload.initial_amount,
            status="active",
            period=payload.initial_period,
            metadata_json=None,
            created_at=datetime.utcnow(),
        )
        db.add(version)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    db.refresh(budget)
    return _budget_response(budget)


@router.get("/", response_model=Dict[str, object])
async def list_budgets(
    tenant_id: str = Query(...),
    scope_level: Optional[str] = Query(None),
    scope_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    query = db.query(Budget).filter(Budget.tenant_id == tenant_id)
    if scope_level:
        query = query.filter(Budget.scope_level == scope_level)
    if scope_id:
        query = query.filter(Budget.scope_id == scope_id)
    if status:
        query = query.filter(Budget.status == status)
    total = query.count()
    items = query.order_by(Budget.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_budget_response(item) for item in items]}


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.tenant_id == tenant_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return _budget_response(budget)


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: str, payload: BudgetUpdate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.tenant_id == tenant_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if payload.budget_name:
        budget.budget_name = payload.budget_name
    if payload.description is not None:
        budget.description = payload.description
    if payload.status:
        budget.status = payload.status
    if payload.currency:
        budget.currency = payload.currency
    if payload.scope_level is not None:
        budget.scope_level = payload.scope_level
    if payload.scope_id is not None:
        budget.scope_id = payload.scope_id
    if payload.metadata is not None:
        budget.metadata_json = payload.metadata
    budget.updated_at = datetime.utcnow()
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _budget_response(budget)


@router.post("/{budget_id}/approve", response_model=BudgetResponse)
async def approve_budget(budget_id: str, payload: BudgetApproveRequest, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.tenant_id == tenant_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    budget.status = payload.status or "approved"
    budget.updated_at = datetime.utcnow()
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _budget_response(budget)


@router.post("/{budget_id}/forecast", response_model=BudgetForecastResponse)
async def create_budget_forecast(budget_id: str, payload: BudgetForecastCreate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.tenant_id == tenant_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    forecast = BudgetForecast(
        id=str(uuid4()),
        tenant_id=tenant_id,
        budget_id=budget.id,
        forecast_name=payload.forecast_name,
        forecast_amount=payload.forecast_amount,
        forecast_date=payload.forecast_date,
        status=payload.status or "pending",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    return _forecast_response(forecast)


@router.post("/{budget_id}/revision", response_model=BudgetVersionResponse)
async def create_budget_revision(budget_id: str, payload: BudgetRevisionCreate, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.tenant_id == tenant_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    version = BudgetVersion(
        id=str(uuid4()),
        tenant_id=tenant_id,
        budget_id=budget.id,
        version_name=payload.version_name,
        amount=payload.amount,
        status=payload.status or "active",
        period=payload.period,
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return _version_response(version)


@router.post("/check-availability", response_model=BudgetAvailabilityResponse)
async def check_budget_availability(payload: BudgetAvailabilityRequest, db: Session = Depends(get_db)):
    query = db.query(Budget).filter(Budget.tenant_id == payload.tenant_id, Budget.status == "approved")
    if payload.scope_level:
        query = query.filter(Budget.scope_level == payload.scope_level)
    if payload.scope_id:
        query = query.filter(Budget.scope_id == payload.scope_id)
    approved_budgets = query.all()
    total_budget = round(sum(item.versions[0].amount if item.versions else 0.0 for item in approved_budgets), 2)
    total_committed = 0.0
    available_amount = round(total_budget - total_committed - payload.requested_amount, 2)
    status = "available" if available_amount >= 0 else "exceeded"
    return BudgetAvailabilityResponse(
        tenant_id=payload.tenant_id,
        available_amount=available_amount,
        total_committed=total_committed,
        total_budget=total_budget,
        status=status,
    )


@router.get("/dashboard", response_model=BudgetDashboardResponse)
async def budget_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    budgets = db.query(Budget).filter(Budget.tenant_id == tenant_id).all()
    total_budgets = len(budgets)
    total_budget_amount = round(sum((budget.versions[0].amount if budget.versions else 0.0) for budget in budgets), 2)
    total_forecast_amount = round(sum((forecast.forecast_amount or 0.0) for budget in budgets for forecast in budget.forecasts), 2)
    budgets_by_status: Dict[str, int] = {}
    for budget in budgets:
        budgets_by_status[budget.status] = budgets_by_status.get(budget.status, 0) + 1
    return BudgetDashboardResponse(
        tenant_id=tenant_id,
        total_budgets=total_budgets,
        total_budget_amount=total_budget_amount,
        total_forecast_amount=total_forecast_amount,
        budgets_by_status=budgets_by_status,
    )
