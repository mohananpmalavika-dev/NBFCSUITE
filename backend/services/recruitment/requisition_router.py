"""
Job Requisition Router
FastAPI endpoints for job requisition operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .requisition_service import RequisitionService
from .schemas import (
    JobRequisitionCreate, JobRequisitionUpdate, JobRequisitionResponse,
    PaginatedRequisitionResponse, RequisitionStatusEnum, JobRequisitionApproval,
    RecruitmentDashboardStats as RequisitionDashboardStats
)
from backend.shared.database.recruitment_models import JobRequisition


router = APIRouter()


def get_requisition_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get requisition service instance"""
    return RequisitionService(db, tenant_id, user_id)


@router.post("/", response_model=JobRequisitionResponse, status_code=201)
async def create_requisition(
    data: JobRequisitionCreate,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Create new job requisition"""
    try:
        requisition = await service.create_requisition(data)
        return requisition
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedRequisitionResponse)
async def get_requisitions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[RequisitionStatusEnum] = Query(None),
    department_id: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    service: RequisitionService = Depends(get_requisition_service)
):
    """Get paginated list of requisitions with filters"""
    try:
        requisitions, total = await service.get_requisitions(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            department_id=department_id,
            priority=priority
        )
        
        return {
            "items": requisitions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard/stats", response_model=RequisitionDashboardStats)
async def get_dashboard_stats(
    service: RequisitionService = Depends(get_requisition_service)
):
    """Get requisition dashboard statistics"""
    try:
        from sqlalchemy import select, func, and_
        from backend.shared.database.recruitment_models import RequisitionStatus
        
        db = service.db
        tenant_id = service.tenant_id
        
        # Total requisitions
        total_query = select(func.count(JobRequisition.id)).where(
            and_(
                JobRequisition.tenant_id == tenant_id,
                JobRequisition.is_deleted == False
            )
        )
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 0
        
        # By status
        status_query = select(
            JobRequisition.status,
            func.count(JobRequisition.id)
        ).where(
            and_(
                JobRequisition.tenant_id == tenant_id,
                JobRequisition.is_deleted == False
            )
        ).group_by(JobRequisition.status)
        
        status_result = await db.execute(status_query)
        status_counts = dict(status_result.all())
        
        return {
            "total_requisitions": total,
            "draft": status_counts.get(RequisitionStatus.DRAFT, 0),
            "pending_approval": status_counts.get(RequisitionStatus.PENDING_APPROVAL, 0),
            "approved": status_counts.get(RequisitionStatus.APPROVED, 0),
            "rejected": status_counts.get(RequisitionStatus.REJECTED, 0),
            "closed": status_counts.get(RequisitionStatus.CLOSED, 0),
            "by_status": {
                status.value: count 
                for status, count in status_counts.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{requisition_id}", response_model=JobRequisitionResponse)
async def get_requisition(
    requisition_id: str,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Get requisition by ID"""
    requisition = await service.get_requisition(requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return requisition


@router.put("/{requisition_id}", response_model=JobRequisitionResponse)
async def update_requisition(
    requisition_id: str,
    data: JobRequisitionUpdate,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Update requisition"""
    try:
        requisition = await service.update_requisition(requisition_id, data)
        return requisition
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{requisition_id}/submit", response_model=JobRequisitionResponse)
async def submit_requisition(
    requisition_id: str,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Submit requisition for approval"""
    try:
        requisition = await service.submit_for_approval(requisition_id)
        return requisition
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{requisition_id}/approve", response_model=JobRequisitionResponse)
async def approve_requisition(
    requisition_id: str,
    approval: JobRequisitionApproval,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Approve or reject requisition"""
    try:
        requisition = await service.approve_requisition(requisition_id, approval)
        return requisition
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{requisition_id}/close", response_model=JobRequisitionResponse)
async def close_requisition(
    requisition_id: str,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Close requisition"""
    try:
        requisition = await service.close_requisition(requisition_id)
        return requisition
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{requisition_id}", status_code=204)
async def delete_requisition(
    requisition_id: str,
    service: RequisitionService = Depends(get_requisition_service)
):
    """Delete requisition (soft delete)"""
    try:
        await service.delete_requisition(requisition_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
