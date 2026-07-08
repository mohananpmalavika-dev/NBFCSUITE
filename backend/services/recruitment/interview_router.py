"""
Interview Router
FastAPI endpoints for interview scheduling and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.dependencies.auth import get_current_user, get_tenant_id
from .interview_service import InterviewService
from .schemas import (
    InterviewCreate, InterviewUpdate, InterviewResponse,
    InterviewListResponse, InterviewStatusEnum, InterviewTypeEnum,
    InterviewFeedbackSubmit, InterviewReschedule
)


router = APIRouter()


def get_interview_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get interview service instance"""
    return InterviewService(db, tenant_id, user_id)


@router.post("/", response_model=InterviewResponse, status_code=201)
async def create_interview(
    data: InterviewCreate,
    service: InterviewService = Depends(get_interview_service)
):
    """Schedule new interview"""
    try:
        interview = await service.create_interview(data)
        return interview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=InterviewListResponse)
async def get_interviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    application_id: Optional[str] = Query(None),
    interviewer_id: Optional[str] = Query(None),
    status: Optional[InterviewStatusEnum] = Query(None),
    interview_type: Optional[InterviewTypeEnum] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    service: InterviewService = Depends(get_interview_service)
):
    """Get paginated list of interviews with filters"""
    try:
        interviews, total = await service.get_interviews(
            page=page,
            page_size=page_size,
            application_id=application_id,
            interviewer_id=interviewer_id,
            status=status,
            interview_type=interview_type,
            from_date=from_date,
            to_date=to_date
        )
        
        return {
            "items": interviews,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/calendar")
async def get_interview_calendar(
    from_date: date = Query(...),
    to_date: date = Query(...),
    interviewer_id: Optional[str] = Query(None),
    service: InterviewService = Depends(get_interview_service)
):
    """Get interviews for calendar view"""
    try:
        interviews = await service.get_interviews_for_calendar(
            from_date=from_date,
            to_date=to_date,
            interviewer_id=interviewer_id
        )
        return interviews
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    service: InterviewService = Depends(get_interview_service)
):
    """Get interview by ID"""
    interview = await service.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    data: InterviewUpdate,
    service: InterviewService = Depends(get_interview_service)
):
    """Update interview"""
    try:
        interview = await service.update_interview(interview_id, data)
        return interview
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/reschedule", response_model=InterviewResponse)
async def reschedule_interview(
    interview_id: str,
    reschedule: InterviewReschedule,
    service: InterviewService = Depends(get_interview_service)
):
    """Reschedule interview"""
    try:
        interview = await service.reschedule_interview(
            interview_id,
            reschedule.new_scheduled_date,
            reschedule.new_start_time,
            reschedule.new_end_time,
            reschedule.reschedule_reason
        )
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
async def complete_interview(
    interview_id: str,
    service: InterviewService = Depends(get_interview_service)
):
    """Mark interview as completed"""
    try:
        interview = await service.complete_interview(interview_id)
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/cancel", response_model=InterviewResponse)
async def cancel_interview(
    interview_id: str,
    cancellation_reason: str = Query(...),
    service: InterviewService = Depends(get_interview_service)
):
    """Cancel interview"""
    try:
        interview = await service.cancel_interview(interview_id, cancellation_reason)
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/feedback", response_model=InterviewResponse)
async def submit_feedback(
    interview_id: str,
    feedback: InterviewFeedbackSubmit,
    service: InterviewService = Depends(get_interview_service)
):
    """Submit interview feedback"""
    try:
        interview = await service.submit_feedback(
            interview_id,
            feedback.rating,
            feedback.feedback_notes,
            feedback.recommendation
        )
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{interview_id}", status_code=204)
async def delete_interview(
    interview_id: str,
    service: InterviewService = Depends(get_interview_service)
):
    """Delete interview (soft delete)"""
    try:
        await service.delete_interview(interview_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
