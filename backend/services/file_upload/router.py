"""
File Upload Router
FastAPI endpoints for file upload operations
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, status, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.file_upload.service import FileUploadService
from backend.services.file_upload import schemas


router = APIRouter(prefix="/files", tags=["File Upload"])


def get_file_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> FileUploadService:
    """Dependency to get file upload service"""
    return FileUploadService(
        db=db,
        user_id=current_user["id"],
        tenant_id=current_user["tenant_id"],
        upload_dir="uploads"
    )


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    document_number: Optional[str] = Form(None),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    service: FileUploadService = Depends(get_file_service)
):
    """
    Upload a single file
    
    - **file**: File to upload (max 10MB)
    - **document_type**: Type of document (required)
    - **document_number**: Document reference number (optional)
    - **entity_type**: Entity type like 'customer', 'loan' (optional)
    - **entity_id**: Entity ID (optional)
    - **remarks**: Additional notes (optional)
    """
    try:
        uploaded_file = await service.upload_file(
            file=file,
            document_type=document_type,
            document_number=document_number,
            entity_type=entity_type,
            entity_id=entity_id,
            remarks=remarks
        )
        
        return success_response(
            data=schemas.FileUploadResponse.from_orm(uploaded_file),
            message="File uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.post("/upload-multiple", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    document_type: str = Form(...),
    document_number: Optional[str] = Form(None),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
    remarks: Optional[str] = Form(None),
    service: FileUploadService = Depends(get_file_service)
):
    """
    Upload multiple files (max 10 files)
    
    - **files**: List of files to upload
    - **document_type**: Type of document (required)
    - **document_number**: Document reference number (optional)
    - **entity_type**: Entity type like 'customer', 'loan' (optional)
    - **entity_id**: Entity ID (optional)
    - **remarks**: Additional notes (optional)
    """
    try:
        uploaded_files = await service.upload_multiple_files(
            files=files,
            document_type=document_type,
            document_number=document_number,
            entity_type=entity_type,
            entity_id=entity_id,
            remarks=remarks
        )
        
        return success_response(
            data={
                "files": [schemas.FileUploadResponse.from_orm(f) for f in uploaded_files],
                "count": len(uploaded_files)
            },
            message=f"{len(uploaded_files)} file(s) uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}"
        )


@router.get("/{file_id}", response_model=dict)
async def get_file_metadata(
    file_id: str,
    service: FileUploadService = Depends(get_file_service)
):
    """Get file metadata by ID"""
    try:
        file_record = await service.get_file(file_id)
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return success_response(
            data=schemas.FileUploadResponse.from_orm(file_record)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    service: FileUploadService = Depends(get_file_service)
):
    """
    Download file by ID
    
    Returns the file as a stream with appropriate headers
    """
    try:
        content, mime_type, filename = await service.get_file_content(file_id)
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/entity/{entity_type}/{entity_id}", response_model=dict)
async def get_files_by_entity(
    entity_type: str,
    entity_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: FileUploadService = Depends(get_file_service)
):
    """
    Get all files for a specific entity
    
    - **entity_type**: Type of entity (customer, loan, etc.)
    - **entity_id**: Entity ID
    """
    try:
        skip = (page - 1) * page_size
        files, total = await service.get_files_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            skip=skip,
            limit=page_size
        )
        
        return success_response(
            data={
                "files": [schemas.FileUploadResponse.from_orm(f) for f in files],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{file_id}", response_model=dict)
async def delete_file(
    file_id: str,
    service: FileUploadService = Depends(get_file_service)
):
    """
    Delete file (soft delete)
    
    Marks the file as inactive in the database
    """
    try:
        success = await service.delete_file(file_id)
        
        return success_response(
            data={"success": success},
            message="File deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
