"""
Customer Timeline API Router
FastAPI routes for customer timeline and activity history
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.customer_models import ActivityType
from .timeline_service import CustomerTimelineService
from .schemas import (
    TimelineActivityCreate, TimelineActivityResponse,
    PaginatedTimelineResponse, TimelineSummaryResponse
)

router = APIRouter(prefix="/customers/{customer_id}/timeline", tags=["Customer Timeline"])


def get_timeline_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> CustomerTimelineService:
    """Dependency to get timeline service"""
    return CustomerTimelineService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# TIMELINE ENDPOINTS
# ============================================================================

@router.get("", response_model=PaginatedTimelineResponse)
async def get_customer_timeline(
    customer_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    activity_types: Optional[List[str]] = Query(None, description="Filter by activity types"),
    event_category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    important_only: bool = Query(False, description="Show only important events"),
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """
    Get customer timeline with filters
    
    Supports filtering by:
    - Activity types (kyc, loan, payment, etc.)
    - Event category
    - Date range
    - Important events only
    """
    
    # Convert activity types from strings to enums
    activity_type_enums = None
    if activity_types:
        try:
            activity_type_enums = [ActivityType[at.upper()] for at in activity_types]
        except KeyError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid activity type: {str(e)}"
            )
    
    items, total = await service.get_customer_timeline(
        customer_id=customer_id,
        page=page,
        page_size=page_size,
        activity_types=activity_type_enums,
        event_category=event_category,
        start_date=start_date,
        end_date=end_date,
        important_only=important_only
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedTimelineResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/recent", response_model=List[TimelineActivityResponse])
async def get_recent_activities(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of recent activities"),
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """
    Get recent activities for customer
    
    Returns the most recent N activities
    """
    activities = await service.get_recent_activities(customer_id, limit)
    return activities


@router.get("/summary", response_model=TimelineSummaryResponse)
async def get_activity_summary(
    customer_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to summarize"),
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """
    Get activity summary for last N days
    
    Returns count of activities by type
    """
    summary = await service.get_activity_summary(customer_id, days)
    return TimelineSummaryResponse(
        customer_id=customer_id,
        days=days,
        activity_counts=summary
    )



@router.get("/search", response_model=List[TimelineActivityResponse])
async def search_timeline(
    customer_id: int,
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results"),
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """
    Search customer timeline
    
    Searches in activity title and description
    """
    results = await service.search_timeline(customer_id, q, limit)
    return results


@router.post("", response_model=TimelineActivityResponse, status_code=status.HTTP_201_CREATED)
async def log_activity(
    customer_id: int,
    data: TimelineActivityCreate,
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """
    Log a customer activity manually
    
    Use this to add custom events, notes, or manual tracking
    """
    activity = await service.log_activity(
        customer_id=customer_id,
        activity_type=data.activity_type,
        title=data.title,
        description=data.description,
        event_category=data.event_category,
        related_entity_type=data.related_entity_type,
        related_entity_id=data.related_entity_id,
        metadata=data.metadata,
        is_important=data.is_important,
        is_visible_to_customer=data.is_visible_to_customer
    )
    return activity


@router.post("/notes", response_model=TimelineActivityResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    customer_id: int,
    note: str = Query(..., min_length=1, max_length=5000, description="Note text"),
    is_important: bool = Query(False, description="Mark as important"),
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """
    Add a note to customer timeline
    
    Quick way to add manual notes or comments
    """
    activity = await service.add_note(customer_id, note, is_important)
    return activity


@router.put("/{timeline_id}/important", response_model=TimelineActivityResponse)
async def mark_as_important(
    customer_id: int,
    timeline_id: int,
    service: CustomerTimelineService = Depends(get_timeline_service)
):
    """Mark timeline event as important"""
    activity = await service.mark_as_important(timeline_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline event {timeline_id} not found"
        )
    return activity
