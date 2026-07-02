from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.financial_close.models import (
    BoardPack,
    CloseCycle,
    CloseConsolidation,
    CloseElimination,
    CloseReconciliation,
    CloseTask,
    RegulatoryReturn,
)
from app.financial_close.schemas import (
    BoardPackRequest,
    BoardPackResponse,
    CloseCompleteRequest,
    CloseCompleteResponse,
    CloseConsolidationRequest,
    CloseConsolidationResponse,
    CloseDashboardResponse,
    CloseEliminationRequest,
    CloseEliminationResponse,
    CloseReconciliationRequest,
    CloseReconciliationResponse,
    CloseStartRequest,
    CloseStartResponse,
    CloseStatusResponse,
    CloseTaskCreate,
    CloseTaskListResponse,
    CloseTaskResponse,
    RbiReportRequest,
    RbiReportResponse,
)

router = APIRouter(prefix="/api/v1/close", tags=["financial-close"])


def _get_cycle(db: Session, tenant_id: str, cycle_id: Optional[str] = None) -> Optional[CloseCycle]:
    if cycle_id:
        return db.query(CloseCycle).filter(CloseCycle.id == cycle_id, CloseCycle.tenant_id == tenant_id).first()
    return db.query(CloseCycle).filter(CloseCycle.tenant_id == tenant_id).order_by(CloseCycle.started_at.desc()).first()


def _task_to_response(task: CloseTask) -> CloseTaskResponse:
    return CloseTaskResponse(
        id=task.id,
        tenant_id=task.tenant_id,
        cycle_id=task.cycle_id,
        name=task.name,
        owner=task.owner,
        due_date=task.due_date,
        dependency=task.dependency,
        priority=task.priority,
        status=task.status,
        evidence=task.evidence,
        approval_status=task.approval_status,
        metadata=task.metadata_json,
        created_at=task.created_at,
    )


@router.get("/dashboard", response_model=CloseDashboardResponse)
async def get_close_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    cycle = _get_cycle(db, tenant_id)
    open_tasks = db.query(CloseTask).filter(CloseTask.tenant_id == tenant_id, CloseTask.status != "completed").count()
    blocked_tasks = db.query(CloseTask).filter(CloseTask.tenant_id == tenant_id, CloseTask.dependency.isnot(None), CloseTask.status != "completed").count()
    reconciliation_issues = db.query(CloseReconciliation).filter(CloseReconciliation.tenant_id == tenant_id, CloseReconciliation.status != "completed").count()
    total_consolidations = db.query(CloseConsolidation).filter(CloseConsolidation.tenant_id == tenant_id).count() or 1
    completed_consolidations = db.query(CloseConsolidation).filter(CloseConsolidation.tenant_id == tenant_id, CloseConsolidation.status == "completed").count()
    completed_ratio = int((completed_consolidations / total_consolidations) * 100)
    board_reports = db.query(BoardPack).filter(BoardPack.tenant_id == tenant_id).all()
    board_pack_status = "ready" if board_reports else "pending"
    rbi_reports = db.query(RegulatoryReturn).filter(RegulatoryReturn.tenant_id == tenant_id).all()
    rbi_status = "submitted" if rbi_reports else "pending"
    return CloseDashboardResponse(
        tenant_id=tenant_id,
        close_readiness=92,
        open_tasks=open_tasks,
        blocked_tasks=blocked_tasks,
        reconciliation_issues=reconciliation_issues,
        consolidation_progress=completed_ratio,
        board_pack_status=board_pack_status,
        rbi_status=rbi_status,
        audit_ready=bool(cycle and cycle.status == "closed" and completed_ratio >= 80),
        health_score=90,
    )


@router.post("/start", response_model=CloseStartResponse)
async def start_close_cycle(payload: CloseStartRequest, db: Session = Depends(get_db)):
    cycle = CloseCycle(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_name=payload.cycle_name,
        close_type=payload.close_type or "monthly",
        period=payload.period,
        stage="planning",
        status="started",
        started_at=datetime.utcnow(),
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return CloseStartResponse(
        id=cycle.id,
        tenant_id=cycle.tenant_id,
        cycle_name=cycle.cycle_name,
        period=cycle.period,
        stage=cycle.stage,
        status=cycle.status,
        started_at=cycle.started_at,
    )


@router.post("/tasks", response_model=CloseTaskResponse)
async def create_close_task(payload: CloseTaskCreate, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    if not cycle and payload.cycle_id:
        raise HTTPException(status_code=404, detail="Close cycle not found")
    task = CloseTask(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_id=cycle.id if cycle else None,
        name=payload.name,
        owner=payload.owner,
        due_date=payload.due_date,
        dependency=payload.dependency,
        priority=payload.priority or "medium",
        status=payload.status or "pending",
        evidence=payload.evidence,
        approval_status="pending" if payload.approval_required else "not_required",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_response(task)


@router.get("/tasks", response_model=CloseTaskListResponse)
async def list_close_tasks(tenant_id: str = Query(...), status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(CloseTask).filter(CloseTask.tenant_id == tenant_id)
    if status:
        query = query.filter(CloseTask.status == status)
    tasks = query.order_by(CloseTask.created_at.desc()).all()
    return CloseTaskListResponse(tenant_id=tenant_id, total=len(tasks), items=[_task_to_response(task) for task in tasks])


@router.post("/reconciliation", response_model=CloseReconciliationResponse)
async def record_reconciliation(payload: CloseReconciliationRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    reconciliation = CloseReconciliation(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_id=cycle.id if cycle else None,
        source=payload.source,
        target=payload.target,
        difference_amount=payload.difference_amount,
        status="completed" if payload.difference_amount == 0 else "investigating",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(reconciliation)
    db.commit()
    db.refresh(reconciliation)
    return CloseReconciliationResponse(
        id=reconciliation.id,
        tenant_id=reconciliation.tenant_id,
        cycle_id=reconciliation.cycle_id,
        source=reconciliation.source,
        target=reconciliation.target,
        difference_amount=reconciliation.difference_amount,
        status=reconciliation.status,
    )


@router.post("/consolidate", response_model=CloseConsolidationResponse)
async def run_consolidation(payload: CloseConsolidationRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    consolidation = CloseConsolidation(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_id=cycle.id if cycle else None,
        entity_from=payload.entity_from,
        entity_to=payload.entity_to,
        result_summary=payload.result_summary or "Consolidation completed",
        status="completed",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(consolidation)
    db.commit()
    db.refresh(consolidation)
    return CloseConsolidationResponse(
        id=consolidation.id,
        tenant_id=consolidation.tenant_id,
        cycle_id=consolidation.cycle_id,
        entity_from=consolidation.entity_from,
        entity_to=consolidation.entity_to,
        result_summary=consolidation.result_summary,
        status=consolidation.status,
    )


@router.post("/eliminate", response_model=CloseEliminationResponse)
async def run_elimination(payload: CloseEliminationRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    elimination = CloseElimination(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_id=cycle.id if cycle else None,
        description=payload.description,
        amount=payload.amount,
        status="completed",
        metadata_json=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(elimination)
    db.commit()
    db.refresh(elimination)
    return CloseEliminationResponse(
        id=elimination.id,
        tenant_id=elimination.tenant_id,
        cycle_id=elimination.cycle_id,
        description=elimination.description,
        amount=elimination.amount,
        status=elimination.status,
    )


@router.post("/generate-board-pack", response_model=BoardPackResponse)
async def generate_board_pack(payload: BoardPackRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    board_pack = BoardPack(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_id=cycle.id if cycle else None,
        report_type=payload.report_type or "board_pack",
        status="generated",
        metadata_json={},
        generated_at=datetime.utcnow(),
    )
    db.add(board_pack)
    db.commit()
    db.refresh(board_pack)
    return BoardPackResponse(
        id=board_pack.id,
        tenant_id=board_pack.tenant_id,
        cycle_id=board_pack.cycle_id,
        report_type=board_pack.report_type,
        status=board_pack.status,
    )


@router.post("/generate-rbi-report", response_model=RbiReportResponse)
async def generate_rbi_report(payload: RbiReportRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    rbi_report = RegulatoryReturn(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        cycle_id=cycle.id if cycle else None,
        return_type=payload.return_type or "NBS",
        status="generated",
        metadata_json={},
        generated_at=datetime.utcnow(),
    )
    db.add(rbi_report)
    db.commit()
    db.refresh(rbi_report)
    return RbiReportResponse(
        id=rbi_report.id,
        tenant_id=rbi_report.tenant_id,
        cycle_id=rbi_report.cycle_id,
        return_type=rbi_report.return_type,
        status=rbi_report.status,
    )


@router.post("/complete", response_model=CloseCompleteResponse)
async def complete_close_cycle(payload: CloseCompleteRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Close cycle not found")
    cycle.status = "closed"
    cycle.stage = "completed"
    cycle.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(cycle)
    return CloseCompleteResponse(
        id=str(uuid4()),
        tenant_id=cycle.tenant_id,
        cycle_id=cycle.id,
        status=cycle.status,
        completed_at=cycle.completed_at,
        final_notes=payload.final_notes,
    )


@router.post("/status", response_model=CloseStatusResponse)
async def get_close_status(payload: CloseCompleteRequest, db: Session = Depends(get_db)):
    cycle = _get_cycle(db, payload.tenant_id, payload.cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Close cycle not found")
    return CloseStatusResponse(message="Close cycle status retrieved", status=cycle.status)
