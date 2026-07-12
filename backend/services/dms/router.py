"""
Document Management System (DMS) Router
FastAPI endpoints for DMS operations
"""

from typing import List, Optional
from fastapi import (
    APIRouter, Depends, File, UploadFile, HTTPException, 
    Query, status, Form, Response
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
import io
from pathlib import Path

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user
from backend.services.dms.service import DocumentService
from backend.services.dms.workflow_service import WorkflowService
from backend.services.dms.signature_service import SignatureService
from backend.services.dms.permission_service import PermissionService
from backend.services.dms import schemas


router = APIRouter(prefix="/dms", tags=["Document Management"])


# Service Dependencies
def get_document_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> DocumentService:
    """Dependency to get document service"""
    return DocumentService(
        db=db,
        user_id=current_user["id"],
        tenant_id=current_user["tenant_id"]
    )


def get_workflow_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> WorkflowService:
    """Dependency to get workflow service"""
    return WorkflowService(
        db=db,
        user_id=current_user["id"],
        tenant_id=current_user["tenant_id"]
    )


def get_signature_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> SignatureService:
    """Dependency to get signature service"""
    return SignatureService(
        db=db,
        user_id=current_user["id"],
        tenant_id=current_user["tenant_id"]
    )


def get_permission_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> PermissionService:
    """Dependency to get permission service"""
    return PermissionService(
        db=db,
        user_id=current_user["id"],
        tenant_id=current_user["tenant_id"]
    )


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@router.post("/documents", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(
    title: str = Form(...),
    document_type: schemas.DocumentTypeEnum = Form(...),
    category: schemas.DocumentCategoryEnum = Form(...),
    access_level: schemas.AccessLevelEnum = Form(schemas.AccessLevelEnum.INTERNAL),
    description: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    reference_number: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    service: DocumentService = Depends(get_document_service)
):
    """
    Create a new document with optional file upload
    
    - **title**: Document title (required)
    - **document_type**: Type of document (required)
    - **category**: Document category (required)
    - **access_level**: Access level (default: internal)
    - **description**: Document description
    - **department**: Department
    - **reference_number**: External reference
    - **file**: File to upload
    """
    document_data = schemas.DocumentCreate(
        title=title,
        description=description,
        document_type=document_type,
        category=category,
        access_level=access_level,
        department=department,
        reference_number=reference_number
    )
    
    document = await service.create_document(document_data, file)
    return success_response(
        data=document.model_dump(),
        message="Document created successfully"
    )


@router.get("/documents/{document_id}", response_model=dict)
async def get_document(
    document_id: UUID4,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID"""
    document = await service.get_document(document_id)
    return success_response(data=document.model_dump())


@router.put("/documents/{document_id}", response_model=dict)
async def update_document(
    document_id: UUID4,
    document_data: schemas.DocumentUpdate,
    service: DocumentService = Depends(get_document_service)
):
    """Update document metadata"""
    document = await service.update_document(document_id, document_data)
    return success_response(
        data=document.model_dump(),
        message="Document updated successfully"
    )


@router.delete("/documents/{document_id}", response_model=dict)
async def delete_document(
    document_id: UUID4,
    service: DocumentService = Depends(get_document_service)
):
    """Soft delete a document"""
    await service.delete_document(document_id)
    return success_response(message="Document deleted successfully")


@router.post("/documents/search", response_model=dict)
async def search_documents(
    search_params: schemas.DocumentSearchRequest,
    service: DocumentService = Depends(get_document_service)
):
    """
    Search documents with filters
    
    Supports filtering by:
    - Query text (title, description, document number)
    - Document type, category, status
    - Access level, department, owner
    - Date ranges
    - Expiring soon flag
    """
    results = await service.search_documents(search_params)
    return success_response(data=results.model_dump())


@router.get("/documents", response_model=dict)
async def list_documents(
    query: Optional[str] = Query(None),
    document_type: Optional[schemas.DocumentTypeEnum] = Query(None),
    category: Optional[schemas.DocumentCategoryEnum] = Query(None),
    status: Optional[schemas.DocumentStatusEnum] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DocumentService = Depends(get_document_service)
):
    """List documents with optional filters"""
    search_params = schemas.DocumentSearchRequest(
        query=query,
        document_type=document_type,
        category=category,
        status=status,
        page=page,
        page_size=page_size
    )
    results = await service.search_documents(search_params)
    return success_response(data=results.model_dump())


# ============================================================================
# DOCUMENT VERSION ENDPOINTS
# ============================================================================

@router.post("/documents/{document_id}/versions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document_version(
    document_id: UUID4,
    file: UploadFile = File(...),
    version_notes: Optional[str] = Form(None),
    is_major_version: bool = Form(False),
    changes_summary: Optional[str] = Form(None),
    service: DocumentService = Depends(get_document_service)
):
    """
    Upload a new version of a document
    
    - **file**: File to upload (required)
    - **version_notes**: Notes about this version
    - **is_major_version**: Whether this is a major version
    - **changes_summary**: Summary of changes
    """
    version_data = schemas.DocumentVersionCreate(
        version_notes=version_notes,
        is_major_version=is_major_version,
        changes_summary=changes_summary
    )
    
    version = await service.upload_version(document_id, file, version_data)
    return success_response(
        data=version.model_dump(),
        message="New version uploaded successfully"
    )


@router.get("/documents/{document_id}/versions", response_model=dict)
async def get_document_versions(
    document_id: UUID4,
    service: DocumentService = Depends(get_document_service)
):
    """Get all versions of a document"""
    versions = await service.get_document_versions(document_id)
    return success_response(data=[v.model_dump() for v in versions])


@router.get("/documents/{document_id}/download", response_class=StreamingResponse)
async def download_document(
    document_id: UUID4,
    version: Optional[int] = Query(None, description="Version number to download"),
    service: DocumentService = Depends(get_document_service)
):
    """Download document file"""
    # Get document
    document = await service.get_document(document_id)
    
    if not document.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document has no file"
        )
    
    # Read file
    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on server"
        )
    
    # Update download count
    # (This would need to be implemented in the service)
    
    # Return file stream
    def iterfile():
        with open(file_path, 'rb') as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type=document.file_type or 'application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename="{document.file_name}"'
        }
    )


# ============================================================================
# WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/workflows", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    document_id: UUID4,
    workflow_data: schemas.WorkflowCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Create a new approval workflow for a document
    
    - **document_id**: Document to create workflow for
    - **workflow_data**: Workflow configuration including steps and approvers
    """
    workflow = await service.create_workflow(document_id, workflow_data)
    return success_response(
        data=workflow.model_dump(),
        message="Workflow created successfully"
    )


@router.get("/workflows/{workflow_id}", response_model=dict)
async def get_workflow(
    workflow_id: UUID4,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow by ID"""
    workflow = await service.get_workflow(workflow_id)
    return success_response(data=workflow.model_dump())


@router.get("/documents/{document_id}/workflows", response_model=dict)
async def get_document_workflows(
    document_id: UUID4,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get all workflows for a document"""
    workflows = await service.get_document_workflows(document_id)
    return success_response(data=[w.model_dump() for w in workflows])


@router.get("/workflows/pending-approvals", response_model=dict)
async def get_pending_approvals(
    approver_id: Optional[UUID4] = Query(None),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get pending approvals for current user or specified user"""
    approvals = await service.get_pending_approvals(approver_id)
    return success_response(data=[a.model_dump() for a in approvals])


@router.post("/approvals/{approval_id}/process", response_model=dict)
async def process_approval(
    approval_id: UUID4,
    action: schemas.ApprovalAction,
    service: WorkflowService = Depends(get_workflow_service)
):
    """
    Process an approval (approve/reject)
    
    - **approval_id**: Approval to process
    - **action**: Approval action with status and comments
    """
    approval = await service.process_approval(approval_id, action)
    return success_response(
        data=approval.model_dump(),
        message=f"Approval {action.status} successfully"
    )


@router.post("/approvals/{approval_id}/delegate", response_model=dict)
async def delegate_approval(
    approval_id: UUID4,
    delegate_to: UUID4,
    reason: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Delegate an approval to another user"""
    approval = await service.delegate_approval(approval_id, delegate_to, reason)
    return success_response(
        data=approval.model_dump(),
        message="Approval delegated successfully"
    )


@router.delete("/workflows/{workflow_id}", response_model=dict)
async def cancel_workflow(
    workflow_id: UUID4,
    reason: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Cancel a workflow"""
    await service.cancel_workflow(workflow_id, reason)
    return success_response(message="Workflow cancelled successfully")


# Workflow Templates
@router.post("/workflow-templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_workflow_template(
    template_data: schemas.WorkflowTemplateCreate,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create a reusable workflow template"""
    template = await service.create_workflow_template(template_data)
    return success_response(
        data=template,
        message="Workflow template created successfully"
    )


@router.get("/workflow-templates", response_model=dict)
async def get_workflow_templates(
    workflow_type: Optional[str] = Query(None),
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow templates"""
    templates = await service.get_workflow_templates(workflow_type)
    return success_response(data=templates)


# ============================================================================
# SIGNATURE ENDPOINTS
# ============================================================================

@router.post("/signatures", response_model=dict, status_code=status.HTTP_201_CREATED)
async def request_signature(
    signature_data: schemas.SignatureRequest,
    service: SignatureService = Depends(get_signature_service)
):
    """
    Request a digital signature on a document
    
    - **signature_data**: Signature request including document, signer, and type
    """
    signature = await service.request_signature(signature_data)
    return success_response(
        data=signature.model_dump(),
        message="Signature request created successfully"
    )


@router.get("/signatures/{signature_id}", response_model=dict)
async def get_signature(
    signature_id: UUID4,
    service: SignatureService = Depends(get_signature_service)
):
    """Get signature by ID"""
    signature = await service.get_signature(signature_id)
    return success_response(data=signature.model_dump())


@router.post("/signatures/{signature_id}/process", response_model=dict)
async def process_signature(
    signature_id: UUID4,
    action: schemas.SignatureAction,
    service: SignatureService = Depends(get_signature_service)
):
    """
    Process a signature request (sign/reject)
    
    - **signature_id**: Signature to process
    - **action**: Signature action with status and signature data
    """
    signature = await service.process_signature(signature_id, action)
    return success_response(
        data=signature.model_dump(),
        message=f"Signature {action.status} successfully"
    )


@router.get("/documents/{document_id}/signatures", response_model=dict)
async def get_document_signatures(
    document_id: UUID4,
    service: SignatureService = Depends(get_signature_service)
):
    """Get all signatures for a document"""
    signatures = await service.get_document_signatures(document_id)
    return success_response(data=[s.model_dump() for s in signatures])


@router.get("/signatures/pending", response_model=dict)
async def get_pending_signatures(
    signer_id: Optional[UUID4] = Query(None),
    service: SignatureService = Depends(get_signature_service)
):
    """Get pending signatures for current user or specified user"""
    signatures = await service.get_pending_signatures(signer_id)
    return success_response(data=[s.model_dump() for s in signatures])


@router.delete("/signatures/{signature_id}", response_model=dict)
async def cancel_signature(
    signature_id: UUID4,
    reason: Optional[str] = None,
    service: SignatureService = Depends(get_signature_service)
):
    """Cancel a signature request"""
    await service.cancel_signature(signature_id, reason)
    return success_response(message="Signature request cancelled successfully")


@router.post("/signatures/{signature_id}/resend", response_model=dict)
async def resend_signature(
    signature_id: UUID4,
    service: SignatureService = Depends(get_signature_service)
):
    """Resend/extend a signature request"""
    signature = await service.resend_signature_request(signature_id)
    return success_response(
        data=signature.model_dump(),
        message="Signature request resent successfully"
    )


@router.get("/signatures/{signature_id}/verify", response_model=dict)
async def verify_signature(
    signature_id: UUID4,
    service: SignatureService = Depends(get_signature_service)
):
    """Verify the integrity of a signature"""
    verification = await service.verify_signature(signature_id)
    return success_response(data=verification)


# ============================================================================
# PERMISSION ENDPOINTS
# ============================================================================

@router.post("/permissions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def grant_permission(
    permission_data: schemas.PermissionCreate,
    service: PermissionService = Depends(get_permission_service)
):
    """
    Grant permission to a user, role, or department
    
    - **permission_data**: Permission details including subject and access rights
    """
    permission = await service.grant_permission(permission_data)
    return success_response(
        data=permission.model_dump(),
        message="Permission granted successfully"
    )


@router.delete("/permissions/{permission_id}", response_model=dict)
async def revoke_permission(
    permission_id: UUID4,
    service: PermissionService = Depends(get_permission_service)
):
    """Revoke a permission"""
    await service.revoke_permission(permission_id)
    return success_response(message="Permission revoked successfully")


@router.get("/documents/{document_id}/permissions", response_model=dict)
async def get_document_permissions(
    document_id: UUID4,
    service: PermissionService = Depends(get_permission_service)
):
    """Get all permissions for a document"""
    permissions = await service.get_document_permissions(document_id)
    return success_response(data=[p.model_dump() for p in permissions])


@router.get("/permissions/check", response_model=dict)
async def check_permission(
    document_id: UUID4 = Query(...),
    user_id: UUID4 = Query(...),
    permission_type: str = Query(..., regex="^(view|download|edit|delete|share|approve)$"),
    service: PermissionService = Depends(get_permission_service)
):
    """Check if a user has a specific permission on a document"""
    has_permission = await service.check_permission(document_id, user_id, permission_type)
    return success_response(data={"has_permission": has_permission})


@router.post("/permissions/bulk-grant", response_model=dict)
async def bulk_grant_permissions(
    document_ids: List[UUID4],
    user_id: Optional[UUID4] = None,
    role_id: Optional[UUID4] = None,
    department: Optional[str] = None,
    can_view: bool = True,
    can_download: bool = False,
    can_edit: bool = False,
    service: PermissionService = Depends(get_permission_service)
):
    """Grant permissions to multiple documents at once"""
    permissions = {
        "can_view": can_view,
        "can_download": can_download,
        "can_edit": can_edit
    }
    count = await service.bulk_grant_permission(
        document_ids=document_ids,
        user_id=user_id,
        role_id=role_id,
        department=department,
        permissions=permissions
    )
    return success_response(
        data={"permissions_created": count},
        message=f"Granted permissions to {count} documents"
    )


# ============================================================================
# COMMENT ENDPOINTS
# ============================================================================

@router.post("/comments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_comment(
    comment_data: schemas.CommentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Add a comment to a document"""
    comment = await service.add_comment(comment_data)
    return success_response(
        data=comment.model_dump(),
        message="Comment added successfully"
    )


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/statistics", response_model=dict)
async def get_statistics(
    service: DocumentService = Depends(get_document_service)
):
    """Get document statistics for the tenant"""
    stats = await service.get_document_statistics()
    return success_response(data=stats.model_dump())


@router.get("/my-documents", response_model=dict)
async def get_my_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Get documents owned by current user"""
    search_params = schemas.DocumentSearchRequest(
        owner_id=current_user["id"],
        page=page,
        page_size=page_size
    )
    results = await service.search_documents(search_params)
    return success_response(data=results.model_dump())


@router.get("/dashboard", response_model=dict)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
    workflow_service: WorkflowService = Depends(get_workflow_service),
    signature_service: SignatureService = Depends(get_signature_service)
):
    """Get dashboard data for current user"""
    # Get statistics
    stats = await doc_service.get_document_statistics()
    
    # Get pending items
    pending_approvals = await workflow_service.get_pending_approvals()
    pending_signatures = await signature_service.get_pending_signatures()
    
    # Get recent documents
    recent_docs = await doc_service.search_documents(
        schemas.DocumentSearchRequest(
            owner_id=current_user["id"],
            page=1,
            page_size=5
        )
    )
    
    return success_response(data={
        "statistics": stats.model_dump(),
        "pending_approvals_count": len(pending_approvals),
        "pending_signatures_count": len(pending_signatures),
        "recent_documents": recent_docs.model_dump()
    })
