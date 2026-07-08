"""
Job Application Router
FastAPI endpoints for applicant tracking system
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .application_service import ApplicationService
from .schemas import (
    JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse,
    PaginatedApplicationResponse, ApplicationStatusEnum, ApplicationSourceEnum,
    ApplicationBulkAction, ApplicationStatusChange
)


router = APIRouter()


def get_application_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get application service instance"""
    return ApplicationService(db, tenant_id, user_id)


@router.post("/", response_model=JobApplicationResponse, status_code=201)
async def create_application(
    data: JobApplicationCreate,
    service: ApplicationService = Depends(get_application_service)
):
    """Create new job application"""
    try:
        application = await service.create_application(data)
        return application
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedApplicationResponse)
async def get_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    posting_id: Optional[str] = Query(None),
    status: Optional[ApplicationStatusEnum] = Query(None),
    source: Optional[ApplicationSourceEnum] = Query(None),
    service: ApplicationService = Depends(get_application_service)
):
    """Get paginated list of applications with filters"""
    try:
        applications, total = await service.get_applications(
            page=page,
            page_size=page_size,
            search=search,
            posting_id=posting_id,
            status=status,
            source=source
        )
        
        return {
            "items": applications,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/kanban")
async def get_applications_kanban(
    posting_id: Optional[str] = Query(None),
    service: ApplicationService = Depends(get_application_service)
):
    """Get applications grouped by status for kanban view"""
    try:
        kanban_data = await service.get_applications_by_status(posting_id)
        return kanban_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}", response_model=JobApplicationResponse)
async def get_application(
    application_id: str,
    service: ApplicationService = Depends(get_application_service)
):
    """Get application by ID"""
    application = await service.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.put("/{application_id}", response_model=JobApplicationResponse)
async def update_application(
    application_id: str,
    data: JobApplicationUpdate,
    service: ApplicationService = Depends(get_application_service)
):
    """Update application"""
    try:
        application = await service.update_application(application_id, data)
        return application
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/status", response_model=JobApplicationResponse)
async def change_application_status(
    application_id: str,
    status_change: ApplicationStatusChange,
    service: ApplicationService = Depends(get_application_service)
):
    """Change application status"""
    try:
        application = await service.change_status(
            application_id, 
            status_change.status, 
            status_change.notes
        )
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/shortlist", response_model=JobApplicationResponse)
async def shortlist_application(
    application_id: str,
    service: ApplicationService = Depends(get_application_service)
):
    """Shortlist application"""
    try:
        application = await service.shortlist_application(application_id)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/reject", response_model=JobApplicationResponse)
async def reject_application(
    application_id: str,
    rejection_reason: str = Query(...),
    service: ApplicationService = Depends(get_application_service)
):
    """Reject application"""
    try:
        application = await service.reject_application(application_id, rejection_reason)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-action")
async def bulk_action(
    action: ApplicationBulkAction,
    service: ApplicationService = Depends(get_application_service)
):
    """Perform bulk action on applications"""
    try:
        if action.action == "shortlist":
            for app_id in action.application_ids:
                await service.shortlist_application(app_id)
        elif action.action == "reject":
            for app_id in action.application_ids:
                await service.reject_application(app_id, action.notes or "Bulk rejection")
        elif action.action == "change_status":
            if not action.new_status:
                raise ValueError("new_status is required for change_status action")
            for app_id in action.application_ids:
                await service.change_status(app_id, action.new_status, action.notes)
        else:
            raise ValueError(f"Unknown action: {action.action}")
        
        return {"message": f"Bulk action '{action.action}' completed for {len(action.application_ids)} applications"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{application_id}", status_code=204)
async def delete_application(
    application_id: str,
    service: ApplicationService = Depends(get_application_service)
):
    """Delete application (soft delete)"""
    try:
        await service.delete_application(application_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/resume/upload")
async def upload_resume(
    application_id: str,
    file: UploadFile = File(...),
    service: ApplicationService = Depends(get_application_service)
):
    """Upload resume file for application"""
    try:
        # In a real implementation, this would upload to cloud storage
        # For now, just return success
        application = await service.get_application(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # TODO: Implement file upload to cloud storage (S3, Azure Blob, etc.)
        file_url = f"storage/resumes/{application_id}/{file.filename}"
        
        return {
            "message": "Resume uploaded successfully",
            "file_url": file_url,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
