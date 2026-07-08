"""
Job Posting Router
FastAPI endpoints for job posting operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.shared.database.connection import get_db
from backend.shared.dependencies.auth import get_current_user, get_tenant_id
from .posting_service import JobPostingService
from .schemas import (
    JobPostingCreate, JobPostingUpdate, JobPostingResponse,
    JobPostingListResponse, PostingStatusEnum
)


router = APIRouter()


def get_posting_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get posting service instance"""
    return JobPostingService(db, tenant_id, user_id)


@router.post("/", response_model=JobPostingResponse, status_code=201)
async def create_posting(
    data: JobPostingCreate,
    service: JobPostingService = Depends(get_posting_service)
):
    """Create new job posting from requisition"""
    try:
        posting = await service.create_posting(data)
        return posting
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=JobPostingListResponse)
async def get_postings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[PostingStatusEnum] = Query(None),
    is_featured: Optional[bool] = Query(None),
    include_expired: bool = Query(False),
    service: JobPostingService = Depends(get_posting_service)
):
    """Get paginated list of postings with filters"""
    try:
        postings, total = await service.get_postings(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            is_featured=is_featured,
            include_expired=include_expired
        )
        
        return {
            "items": postings,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/public", response_model=JobPostingListResponse)
async def get_public_postings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    service: JobPostingService = Depends(get_posting_service)
):
    """Get public job postings (for career page) - no auth required"""
    try:
        postings, total = await service.get_public_postings(
            page=page,
            page_size=page_size,
            search=search,
            employment_type=employment_type,
            location=location
        )
        
        return {
            "items": postings,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{posting_id}", response_model=JobPostingResponse)
async def get_posting(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Get posting by ID"""
    posting = await service.get_posting(posting_id)
    if not posting:
        raise HTTPException(status_code=404, detail="Posting not found")
    return posting


@router.get("/{posting_id}/statistics")
async def get_posting_statistics(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Get statistics for a posting"""
    try:
        stats = await service.get_posting_statistics(posting_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{posting_id}", response_model=JobPostingResponse)
async def update_posting(
    posting_id: str,
    data: JobPostingUpdate,
    service: JobPostingService = Depends(get_posting_service)
):
    """Update posting"""
    try:
        posting = await service.update_posting(posting_id, data)
        return posting
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{posting_id}/publish", response_model=JobPostingResponse)
async def publish_posting(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Publish job posting"""
    try:
        posting = await service.publish_posting(posting_id)
        return posting
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{posting_id}/unpublish", response_model=JobPostingResponse)
async def unpublish_posting(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Unpublish job posting"""
    try:
        posting = await service.unpublish_posting(posting_id)
        return posting
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{posting_id}/close", response_model=JobPostingResponse)
async def close_posting(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Close job posting"""
    try:
        posting = await service.close_posting(posting_id)
        return posting
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{posting_id}/view", response_model=JobPostingResponse)
async def increment_posting_views(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Increment posting view count"""
    try:
        posting = await service.increment_views(posting_id)
        return posting
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{posting_id}", status_code=204)
async def delete_posting(
    posting_id: str,
    service: JobPostingService = Depends(get_posting_service)
):
    """Delete posting (soft delete)"""
    try:
        await service.delete_posting(posting_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
