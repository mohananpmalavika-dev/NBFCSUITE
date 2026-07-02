from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.cost_accounting.models import AllocationRun, CostCenter, ProfitCenter
from app.cost_accounting.schemas import (
    AllocationReceiver,
    AllocationRunCreate,
    AllocationRunResponse,
    AllocationResultItem,
    CostCenterCreate,
    CostCenterResponse,
    CostDashboardResponse,
    CostReportItem,
    CostReportsResponse,
    CostSimulationResponse,
    ProfitCenterCreate,
    ProfitCenterResponse,
    ProfitabilityItem,
    ProfitabilityResponse,
)
from app.db import get_db

router = APIRouter(prefix="/api/v1", tags=["cost-accounting"])


def _cost_center_response(cost_center: CostCenter) -> CostCenterResponse:
    return CostCenterResponse(
        id=cost_center.id,
        tenant_id=cost_center.tenant_id,
        code=cost_center.code,
        name=cost_center.name,
        cost_center_type=cost_center.cost_center_type,
        budget_amount=cost_center.budget_amount or 0.0,
        actual_amount=cost_center.actual_amount or 0.0,
        status=cost_center.status or "active",
        metadata=cost_center.metadata_json,
        created_at=cost_center.created_at,
    )


def _profit_center_response(profit_center: ProfitCenter) -> ProfitCenterResponse:
    return ProfitCenterResponse(
        id=profit_center.id,
        tenant_id=profit_center.tenant_id,
        code=profit_center.code,
        name=profit_center.name,
        profit_center_type=profit_center.profit_center_type,
        manager=profit_center.manager,
        status=profit_center.status or "active",
        metadata=profit_center.metadata_json,
        created_at=profit_center.created_at,
    )


@router.post("/cost-centers", response_model=CostCenterResponse)
async def create_cost_center(payload: CostCenterCreate, db: Session = Depends(get_db)):
    cost_center = CostCenter(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        code=payload.code,
        name=payload.name,
        cost_center_type=payload.cost_center_type,
        budget_amount=payload.budget_amount or 0.0,
        actual_amount=payload.actual_amount or 0.0,
        status=payload.status or "active",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(cost_center)
    db.commit()
    db.refresh(cost_center)
    return _cost_center_response(cost_center)


@router.post("/profit-centers", response_model=ProfitCenterResponse)
async def create_profit_center(payload: ProfitCenterCreate, db: Session = Depends(get_db)):
    profit_center = ProfitCenter(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        code=payload.code,
        name=payload.name,
        profit_center_type=payload.profit_center_type,
        manager=payload.manager,
        status=payload.status or "active",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(profit_center)
    db.commit()
    db.refresh(profit_center)
    return _profit_center_response(profit_center)


@router.post("/allocations/run", response_model=AllocationRunResponse)
async def run_allocation(payload: AllocationRunCreate, db: Session = Depends(get_db)):
    receivers = payload.receivers or []
    if not receivers:
        receivers = [AllocationReceiver(receiver_id="default", receiver_name="Default", receiver_type="branch", allocation_percentage=100.0)]

    results = []
    total_allocated = 0.0
    for receiver in receivers:
        allocated_amount = round(payload.amount * (receiver.allocation_percentage / 100.0), 2)
        total_allocated += allocated_amount
        results.append(
            AllocationResultItem(
                receiver_id=receiver.receiver_id,
                receiver_name=receiver.receiver_name,
                receiver_type=receiver.receiver_type,
                allocation_percentage=receiver.allocation_percentage,
                allocated_amount=allocated_amount,
            )
        )

    allocation_run = AllocationRun(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        source_cost_center_id=payload.source_cost_center_id,
        amount=payload.amount,
        allocation_rule_type=payload.allocation_rule_type or "percentage",
        status="completed",
        results_json=[item.dict() for item in results],
        created_at=datetime.utcnow(),
    )
    db.add(allocation_run)
    db.commit()
    db.refresh(allocation_run)
    return AllocationRunResponse(
        id=allocation_run.id,
        tenant_id=allocation_run.tenant_id,
        source_cost_center_id=allocation_run.source_cost_center_id,
        amount=allocation_run.amount,
        allocation_rule_type=allocation_run.allocation_rule_type,
        status=allocation_run.status,
        results=results,
        created_at=allocation_run.created_at,
    )


@router.get("/profitability/products", response_model=ProfitabilityResponse)
async def get_product_profitability(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    items = [ProfitabilityItem(metric_type="product", name="Consumer Loans", amount=125000.0)]
    return ProfitabilityResponse(tenant_id=tenant_id, items=items)


@router.get("/profitability/customers", response_model=ProfitabilityResponse)
async def get_customer_profitability(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    items = [ProfitabilityItem(metric_type="customer", name="Retail Segment", amount=98000.0)]
    return ProfitabilityResponse(tenant_id=tenant_id, items=items)


@router.get("/profitability/branches", response_model=ProfitabilityResponse)
async def get_branch_profitability(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    items = [ProfitabilityItem(metric_type="branch", name="North Branch", amount=76000.0)]
    return ProfitabilityResponse(tenant_id=tenant_id, items=items)


@router.get("/cost/dashboard", response_model=CostDashboardResponse)
async def get_cost_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    cost_centers = db.query(CostCenter).filter(CostCenter.tenant_id == tenant_id).all()
    profit_centers = db.query(ProfitCenter).filter(ProfitCenter.tenant_id == tenant_id).all()
    total_budget_amount = sum(center.budget_amount or 0.0 for center in cost_centers)
    total_allocated_amount = sum(run.amount for run in db.query(AllocationRun).filter(AllocationRun.tenant_id == tenant_id).all())
    return CostDashboardResponse(
        tenant_id=tenant_id,
        total_cost_centers=len(cost_centers),
        total_profit_centers=len(profit_centers),
        total_allocated_amount=total_allocated_amount,
        total_budget_amount=total_budget_amount,
    )


@router.post("/cost/simulate", response_model=CostSimulationResponse)
async def simulate_costs(payload: dict, db: Session = Depends(get_db)):
    tenant_id = payload.get("tenant_id")
    adjustment_percent = float(payload.get("adjustment_percent", 0.0))
    cost_centers = db.query(CostCenter).filter(CostCenter.tenant_id == tenant_id).all()
    base_total = sum(center.actual_amount or 0.0 for center in cost_centers)
    projected_total_cost = base_total * (1 + (adjustment_percent / 100.0))
    return CostSimulationResponse(
        tenant_id=tenant_id or "",
        adjustment_percent=adjustment_percent,
        projected_total_cost=projected_total_cost,
    )


@router.get("/cost/reports", response_model=CostReportsResponse)
async def get_cost_reports(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    reports = [CostReportItem(report_type="allocation", title="Allocation Summary", amount=100000.0)]
    return CostReportsResponse(tenant_id=tenant_id, total_reports=len(reports), reports=reports)
