"""
Document Management Router
Phase 10: Document Management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
import secrets

from app.database import get_db
from app.models.documents import (
    DocumentCategory, Document, DocumentVersion, DocumentMetadata,
    DocumentTemplate, DocumentWorkflow, DocumentApproval, DocumentTag,
    DocumentTagMapping, DocumentAccessLog, DocumentRetentionPolicy, DocumentShare
)
from app.schemas.documents import (
    # Category schemas
    DocumentCategoryCreate, DocumentCategoryUpdate, DocumentCategoryResponse,
    # Document schemas
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentUploadRequest,
    # Version schemas
    DocumentVersionResponse,
    # Metadata schemas
    DocumentMetadataCreate, DocumentMetadataUpdate, DocumentMetadataResponse,
    # Template schemas
    DocumentTemplateCreate, DocumentTemplateUpdate, DocumentTemplateResponse,
    # Workflow schemas
    DocumentWorkflowCreate, DocumentWorkflowUpdate, DocumentWorkflowResponse,
    # Approval schemas
    DocumentApprovalCreate, DocumentApprovalUpdate, DocumentApprovalResponse,
    DocumentApprovalActionRequest,
    # Tag schemas
    DocumentTagCreate, DocumentTagUpdate, DocumentTagResponse,
    DocumentTagMappingCreate, DocumentTagMappingResponse,
    # Access log schemas
    DocumentAccessLogCreate, DocumentAccessLogResponse,
    # Retention policy schemas
    DocumentRetentionPolicyCreate, DocumentRetentionPolicyUpdate, DocumentRetentionPolicyResponse,
    # Share schemas
    DocumentShareCreate, DocumentShareUpdate, DocumentShareResponse, DocumentShareRevoke,
    # Filter schemas
    DocumentListFilter, DocumentApprovalListFilter, DocumentAccessLogFilter,
    # Bulk operation schemas
    BulkDocumentTagRequest, BulkDocumentDeleteRequest, BulkDocumentMoveRequest,
    # OCR schemas
    DocumentOCRRequest, DocumentOCRResponse,
    # Statistics schemas
    DocumentStatistics, WorkflowStatistics
)

router = APIRouter(prefix="/documents", tags=["Document Management"])


# ============================================================================
# DOCUMENT CATEGORY ENDPOINTS
# ============================================================================

@router.post("/categories", response_model=DocumentCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_document_category(
    category: DocumentCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new document category"""
    # Check if category code already exists
    existing = db.query(DocumentCategory).filter(
        DocumentCategory.category_code == category.category_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with code '{category.category_code}' already exists"
        )
    
    db_category = DocumentCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories", response_model=List[DocumentCategoryResponse])
async def list_document_categories(
    is_active: Optional[bool] = Query(None),
    parent_category_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all document categories with optional filters"""
    query = db.query(DocumentCategory)
    
    if is_active is not None:
        query = query.filter(DocumentCategory.is_active == is_active)
    
    if parent_category_id is not None:
        query = query.filter(DocumentCategory.parent_category_id == parent_category_id)
    
    query = query.order_by(DocumentCategory.display_order, DocumentCategory.category_name)
    categories = query.offset(skip).limit(limit).all()
    return categories


@router.get("/categories/{category_id}", response_model=DocumentCategoryResponse)
async def get_document_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document category by ID"""
    category = db.query(DocumentCategory).filter(
        DocumentCategory.category_id == category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document category not found"
        )
    return category


@router.put("/categories/{category_id}", response_model=DocumentCategoryResponse)
async def update_document_category(
    category_id: UUID,
    category_update: DocumentCategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a document category"""
    db_category = db.query(DocumentCategory).filter(
        DocumentCategory.category_id == category_id
    ).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document category not found"
        )
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a document category (soft delete)"""
    db_category = db.query(DocumentCategory).filter(
        DocumentCategory.category_id == category_id
    ).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document category not found"
        )
    
    # Check if category has documents
    doc_count = db.query(func.count(Document.document_id)).filter(
        Document.category_id == category_id
    ).scalar()
    if doc_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {doc_count} associated documents"
        )
    
    db_category.is_active = False
    db.commit()


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document record"""
    # Verify category exists
    category = db.query(DocumentCategory).filter(
        DocumentCategory.category_id == document.category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document category not found"
        )
    
    # Generate document number
    doc_count = db.query(func.count(Document.document_id)).scalar()
    document_number = f"DOC{datetime.now().strftime('%Y%m')}{doc_count + 1:06d}"
    
    db_document = Document(
        **document.dict(),
        document_number=document_number,
        current_version=1
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    category_id: Optional[UUID] = Query(None),
    document_type: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[UUID] = Query(None),
    storage_status: Optional[str] = Query(None),
    is_deleted: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all documents with optional filters"""
    query = db.query(Document)
    
    if category_id:
        query = query.filter(Document.category_id == category_id)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if entity_type:
        query = query.filter(Document.entity_type == entity_type)
    
    if entity_id:
        query = query.filter(Document.entity_id == entity_id)
    
    if storage_status:
        query = query.filter(Document.storage_status == storage_status)
    
    if is_deleted is not None:
        query = query.filter(Document.is_deleted == is_deleted)
    
    if search:
        search_filter = or_(
            Document.title.ilike(f"%{search}%"),
            Document.description.ilike(f"%{search}%"),
            Document.document_number.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if from_date:
        query = query.filter(Document.created_at >= from_date)
    
    if to_date:
        query = query.filter(Document.created_at <= to_date)
    
    query = query.order_by(desc(Document.created_at))
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document by ID"""
    document = db.query(Document).filter(
        Document.document_id == document_id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update a document"""
    db_document = db.query(Document).filter(
        Document.document_id == document_id
    ).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    deleted_by: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """Delete a document (soft delete)"""
    db_document = db.query(Document).filter(
        Document.document_id == document_id
    ).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db_document.is_deleted = True
    db_document.deleted_at = datetime.now()
    db_document.deleted_by = deleted_by
    db.commit()


@router.post("/{document_id}/restore", response_model=DocumentResponse)
async def restore_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Restore a deleted document"""
    db_document = db.query(Document).filter(
        Document.document_id == document_id,
        Document.is_deleted == True
    ).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted document not found"
        )
    
    db_document.is_deleted = False
    db_document.deleted_at = None
    db_document.deleted_by = None
    db.commit()
    db.refresh(db_document)
    return db_document


# ============================================================================
# DOCUMENT VERSION ENDPOINTS
# ============================================================================

@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def list_document_versions(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """List all versions of a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    versions = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id
    ).order_by(desc(DocumentVersion.version_number)).all()
    return versions


@router.get("/{document_id}/versions/{version_number}", response_model=DocumentVersionResponse)
async def get_document_version(
    document_id: UUID,
    version_number: int,
    db: Session = Depends(get_db)
):
    """Get a specific version of a document"""
    version = db.query(DocumentVersion).filter(
        and_(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version_number
        )
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document version not found"
        )
    return version


@router.post("/{document_id}/versions/{version_number}/restore", response_model=DocumentResponse)
async def restore_document_version(
    document_id: UUID,
    version_number: int,
    restored_by: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """Restore a previous version of a document"""
    # Get the version to restore
    version = db.query(DocumentVersion).filter(
        and_(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version_number
        )
    ).first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document version not found"
        )
    
    # Get the current document
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Create a new version with the old content
    new_version_number = document.current_version + 1
    new_version = DocumentVersion(
        document_id=document_id,
        version_number=new_version_number,
        file_name=version.file_name,
        file_size_bytes=version.file_size_bytes,
        file_hash=version.file_hash,
        storage_path=version.storage_path,
        mime_type=version.mime_type,
        change_description=f"Restored from version {version_number}",
        created_by=restored_by
    )
    db.add(new_version)
    
    # Update document
    document.current_version = new_version_number
    document.file_size_bytes = version.file_size_bytes
    document.updated_by = restored_by
    
    db.commit()
    db.refresh(document)
    return document


# ============================================================================
# DOCUMENT METADATA ENDPOINTS
# ============================================================================

@router.post("/{document_id}/metadata", response_model=DocumentMetadataResponse, status_code=status.HTTP_201_CREATED)
async def add_document_metadata(
    document_id: UUID,
    metadata: DocumentMetadataCreate,
    db: Session = Depends(get_db)
):
    """Add metadata to a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if metadata key already exists
    existing = db.query(DocumentMetadata).filter(
        and_(
            DocumentMetadata.document_id == document_id,
            DocumentMetadata.metadata_key == metadata.metadata_key
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Metadata key '{metadata.metadata_key}' already exists for this document"
        )
    
    db_metadata = DocumentMetadata(document_id=document_id, **metadata.dict())
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata


@router.get("/{document_id}/metadata", response_model=List[DocumentMetadataResponse])
async def list_document_metadata(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """List all metadata for a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    metadata = db.query(DocumentMetadata).filter(
        DocumentMetadata.document_id == document_id
    ).order_by(DocumentMetadata.metadata_key).all()
    return metadata


@router.put("/{document_id}/metadata/{metadata_id}", response_model=DocumentMetadataResponse)
async def update_document_metadata(
    document_id: UUID,
    metadata_id: UUID,
    metadata_update: DocumentMetadataUpdate,
    db: Session = Depends(get_db)
):
    """Update document metadata"""
    db_metadata = db.query(DocumentMetadata).filter(
        and_(
            DocumentMetadata.metadata_id == metadata_id,
            DocumentMetadata.document_id == document_id
        )
    ).first()
    if not db_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document metadata not found"
        )
    
    update_data = metadata_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_metadata, field, value)
    
    db.commit()
    db.refresh(db_metadata)
    return db_metadata


@router.delete("/{document_id}/metadata/{metadata_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_metadata(
    document_id: UUID,
    metadata_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete document metadata"""
    db_metadata = db.query(DocumentMetadata).filter(
        and_(
            DocumentMetadata.metadata_id == metadata_id,
            DocumentMetadata.document_id == document_id
        )
    ).first()
    if not db_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document metadata not found"
        )
    
    db.delete(db_metadata)
    db.commit()


# ============================================================================
# DOCUMENT TEMPLATE ENDPOINTS
# ============================================================================

@router.post("/templates", response_model=DocumentTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_document_template(
    template: DocumentTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new document template"""
    # Check if template code already exists
    existing = db.query(DocumentTemplate).filter(
        DocumentTemplate.template_code == template.template_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with code '{template.template_code}' already exists"
        )
    
    db_template = DocumentTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/templates", response_model=List[DocumentTemplateResponse])
async def list_document_templates(
    category_id: Optional[UUID] = Query(None),
    template_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all document templates with optional filters"""
    query = db.query(DocumentTemplate)
    
    if category_id:
        query = query.filter(DocumentTemplate.category_id == category_id)
    
    if template_type:
        query = query.filter(DocumentTemplate.template_type == template_type)
    
    if is_active is not None:
        query = query.filter(DocumentTemplate.is_active == is_active)
    
    query = query.order_by(DocumentTemplate.template_name)
    templates = query.offset(skip).limit(limit).all()
    return templates


@router.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def get_document_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document template by ID"""
    template = db.query(DocumentTemplate).filter(
        DocumentTemplate.template_id == template_id
    ).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document template not found"
        )
    return template


@router.put("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def update_document_template(
    template_id: UUID,
    template_update: DocumentTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update a document template"""
    db_template = db.query(DocumentTemplate).filter(
        DocumentTemplate.template_id == template_id
    ).first()
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document template not found"
        )
    
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_template(
    template_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a document template (soft delete)"""
    db_template = db.query(DocumentTemplate).filter(
        DocumentTemplate.template_id == template_id
    ).first()
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document template not found"
        )
    
    db_template.is_active = False
    db.commit()


# ============================================================================
# DOCUMENT WORKFLOW ENDPOINTS
# ============================================================================

@router.post("/workflows", response_model=DocumentWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_document_workflow(
    workflow: DocumentWorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new document workflow"""
    # Check if workflow code already exists
    existing = db.query(DocumentWorkflow).filter(
        DocumentWorkflow.workflow_code == workflow.workflow_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow with code '{workflow.workflow_code}' already exists"
        )
    
    db_workflow = DocumentWorkflow(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.get("/workflows", response_model=List[DocumentWorkflowResponse])
async def list_document_workflows(
    category_id: Optional[UUID] = Query(None),
    workflow_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all document workflows with optional filters"""
    query = db.query(DocumentWorkflow)
    
    if category_id:
        query = query.filter(DocumentWorkflow.category_id == category_id)
    
    if workflow_type:
        query = query.filter(DocumentWorkflow.workflow_type == workflow_type)
    
    if is_active is not None:
        query = query.filter(DocumentWorkflow.is_active == is_active)
    
    query = query.order_by(DocumentWorkflow.workflow_name)
    workflows = query.offset(skip).limit(limit).all()
    return workflows


@router.get("/workflows/{workflow_id}", response_model=DocumentWorkflowResponse)
async def get_document_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document workflow by ID"""
    workflow = db.query(DocumentWorkflow).filter(
        DocumentWorkflow.workflow_id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document workflow not found"
        )
    return workflow


@router.put("/workflows/{workflow_id}", response_model=DocumentWorkflowResponse)
async def update_document_workflow(
    workflow_id: UUID,
    workflow_update: DocumentWorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update a document workflow"""
    db_workflow = db.query(DocumentWorkflow).filter(
        DocumentWorkflow.workflow_id == workflow_id
    ).first()
    if not db_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document workflow not found"
        )
    
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_workflow, field, value)
    
    db.commit()
    db.refresh(db_workflow)
    return db_workflow


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a document workflow (soft delete)"""
    db_workflow = db.query(DocumentWorkflow).filter(
        DocumentWorkflow.workflow_id == workflow_id
    ).first()
    if not db_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document workflow not found"
        )
    
    db_workflow.is_active = False
    db.commit()


# ============================================================================
# DOCUMENT APPROVAL ENDPOINTS
# ============================================================================

@router.post("/approvals", response_model=DocumentApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_document_approval(
    approval: DocumentApprovalCreate,
    db: Session = Depends(get_db)
):
    """Initiate a document approval workflow"""
    # Verify document and workflow exist
    document = db.query(Document).filter(Document.document_id == approval.document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    workflow = db.query(DocumentWorkflow).filter(
        DocumentWorkflow.workflow_id == approval.workflow_id
    ).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Generate approval number
    approval_count = db.query(func.count(DocumentApproval.approval_id)).scalar()
    approval_number = f"APR{datetime.now().strftime('%Y%m')}{approval_count + 1:06d}"
    
    # Calculate total steps from workflow
    total_steps = len(workflow.workflow_steps) if workflow.workflow_steps else 1
    
    db_approval = DocumentApproval(
        **approval.dict(),
        approval_number=approval_number,
        current_step=1,
        total_steps=total_steps,
        approval_status='pending'
    )
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval


@router.get("/approvals", response_model=List[DocumentApprovalResponse])
async def list_document_approvals(
    workflow_id: Optional[UUID] = Query(None),
    approval_status: Optional[str] = Query(None),
    assigned_to: Optional[UUID] = Query(None),
    initiated_by: Optional[UUID] = Query(None),
    priority: Optional[str] = Query(None),
    is_escalated: Optional[bool] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all document approvals with optional filters"""
    query = db.query(DocumentApproval)
    
    if workflow_id:
        query = query.filter(DocumentApproval.workflow_id == workflow_id)
    
    if approval_status:
        query = query.filter(DocumentApproval.approval_status == approval_status)
    
    if assigned_to:
        query = query.filter(DocumentApproval.assigned_to == assigned_to)
    
    if initiated_by:
        query = query.filter(DocumentApproval.initiated_by == initiated_by)
    
    if priority:
        query = query.filter(DocumentApproval.priority == priority)
    
    if is_escalated is not None:
        query = query.filter(DocumentApproval.is_escalated == is_escalated)
    
    if from_date:
        query = query.filter(DocumentApproval.initiated_at >= from_date)
    
    if to_date:
        query = query.filter(DocumentApproval.initiated_at <= to_date)
    
    query = query.order_by(desc(DocumentApproval.initiated_at))
    approvals = query.offset(skip).limit(limit).all()
    return approvals


@router.get("/approvals/{approval_id}", response_model=DocumentApprovalResponse)
async def get_document_approval(
    approval_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document approval by ID"""
    approval = db.query(DocumentApproval).filter(
        DocumentApproval.approval_id == approval_id
    ).first()
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document approval not found"
        )
    return approval


@router.post("/approvals/{approval_id}/action", response_model=DocumentApprovalResponse)
async def take_approval_action(
    approval_id: UUID,
    action_request: DocumentApprovalActionRequest,
    db: Session = Depends(get_db)
):
    """Take action on a document approval (approve/reject/return)"""
    db_approval = db.query(DocumentApproval).filter(
        DocumentApproval.approval_id == approval_id
    ).first()
    if not db_approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document approval not found"
        )
    
    if db_approval.approval_status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot take action on approval with status '{db_approval.approval_status}'"
        )
    
    action = action_request.action.lower()
    
    if action == 'approve':
        if db_approval.current_step < db_approval.total_steps:
            # Move to next step
            db_approval.current_step += 1
            db_approval.approval_status = 'pending'
        else:
            # Final approval
            db_approval.approval_status = 'approved'
            db_approval.completed_at = datetime.now()
    
    elif action == 'reject':
        db_approval.approval_status = 'rejected'
        db_approval.rejection_reason = action_request.rejection_reason
        db_approval.completed_at = datetime.now()
    
    elif action == 'return':
        db_approval.approval_status = 'returned'
        db_approval.remarks = action_request.comments
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{action}'. Must be 'approve', 'reject', or 'return'"
        )
    
    # Update approval steps
    if not db_approval.approval_steps:
        db_approval.approval_steps = []
    
    step_data = {
        'step': db_approval.current_step,
        'action': action,
        'action_by': str(action_request.action_by),
        'action_at': datetime.now().isoformat(),
        'comments': action_request.comments
    }
    db_approval.approval_steps.append(step_data)
    
    db.commit()
    db.refresh(db_approval)
    return db_approval


@router.put("/approvals/{approval_id}", response_model=DocumentApprovalResponse)
async def update_document_approval(
    approval_id: UUID,
    approval_update: DocumentApprovalUpdate,
    db: Session = Depends(get_db)
):
    """Update a document approval"""
    db_approval = db.query(DocumentApproval).filter(
        DocumentApproval.approval_id == approval_id
    ).first()
    if not db_approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document approval not found"
        )
    
    update_data = approval_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_approval, field, value)
    
    db.commit()
    db.refresh(db_approval)
    return db_approval


# ============================================================================
# DOCUMENT TAG ENDPOINTS
# ============================================================================

@router.post("/tags", response_model=DocumentTagResponse, status_code=status.HTTP_201_CREATED)
async def create_document_tag(
    tag: DocumentTagCreate,
    db: Session = Depends(get_db)
):
    """Create a new document tag"""
    # Check if tag name already exists
    existing = db.query(DocumentTag).filter(
        DocumentTag.tag_name == tag.tag_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag.tag_name}' already exists"
        )
    
    db_tag = DocumentTag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/tags", response_model=List[DocumentTagResponse])
async def list_document_tags(
    tag_category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all document tags with optional filters"""
    query = db.query(DocumentTag)
    
    if tag_category:
        query = query.filter(DocumentTag.tag_category == tag_category)
    
    if is_active is not None:
        query = query.filter(DocumentTag.is_active == is_active)
    
    if search:
        query = query.filter(DocumentTag.tag_name.ilike(f"%{search}%"))
    
    query = query.order_by(desc(DocumentTag.usage_count), DocumentTag.tag_name)
    tags = query.offset(skip).limit(limit).all()
    return tags


@router.get("/tags/{tag_id}", response_model=DocumentTagResponse)
async def get_document_tag(
    tag_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document tag by ID"""
    tag = db.query(DocumentTag).filter(DocumentTag.tag_id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document tag not found"
        )
    return tag


@router.put("/tags/{tag_id}", response_model=DocumentTagResponse)
async def update_document_tag(
    tag_id: UUID,
    tag_update: DocumentTagUpdate,
    db: Session = Depends(get_db)
):
    """Update a document tag"""
    db_tag = db.query(DocumentTag).filter(DocumentTag.tag_id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document tag not found"
        )
    
    update_data = tag_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tag, field, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_tag(
    tag_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a document tag (soft delete)"""
    db_tag = db.query(DocumentTag).filter(DocumentTag.tag_id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document tag not found"
        )
    
    db_tag.is_active = False
    db.commit()


@router.post("/{document_id}/tags", response_model=DocumentTagMappingResponse, status_code=status.HTTP_201_CREATED)
async def add_tag_to_document(
    document_id: UUID,
    mapping: DocumentTagMappingCreate,
    db: Session = Depends(get_db)
):
    """Add a tag to a document"""
    # Verify document and tag exist
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    tag = db.query(DocumentTag).filter(DocumentTag.tag_id == mapping.tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if mapping already exists
    existing = db.query(DocumentTagMapping).filter(
        and_(
            DocumentTagMapping.document_id == document_id,
            DocumentTagMapping.tag_id == mapping.tag_id
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already added to this document"
        )
    
    db_mapping = DocumentTagMapping(**mapping.dict())
    db.add(db_mapping)
    
    # Increment tag usage count
    tag.usage_count += 1
    
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


@router.get("/{document_id}/tags", response_model=List[DocumentTagResponse])
async def list_document_tags_for_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """List all tags for a document"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    tags = db.query(DocumentTag).join(
        DocumentTagMapping,
        DocumentTag.tag_id == DocumentTagMapping.tag_id
    ).filter(
        DocumentTagMapping.document_id == document_id
    ).all()
    return tags


@router.delete("/{document_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_document(
    document_id: UUID,
    tag_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove a tag from a document"""
    db_mapping = db.query(DocumentTagMapping).filter(
        and_(
            DocumentTagMapping.document_id == document_id,
            DocumentTagMapping.tag_id == tag_id
        )
    ).first()
    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag mapping not found"
        )
    
    # Decrement tag usage count
    tag = db.query(DocumentTag).filter(DocumentTag.tag_id == tag_id).first()
    if tag and tag.usage_count > 0:
        tag.usage_count -= 1
    
    db.delete(db_mapping)
    db.commit()


# ============================================================================
# DOCUMENT ACCESS LOG ENDPOINTS
# ============================================================================

@router.post("/access-logs", response_model=DocumentAccessLogResponse, status_code=status.HTTP_201_CREATED)
async def create_document_access_log(
    access_log: DocumentAccessLogCreate,
    db: Session = Depends(get_db)
):
    """Create a document access log entry"""
    db_log = DocumentAccessLog(**access_log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/access-logs", response_model=List[DocumentAccessLogResponse])
async def list_document_access_logs(
    document_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    action_type: Optional[str] = Query(None),
    access_result: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List document access logs with optional filters"""
    query = db.query(DocumentAccessLog)
    
    if document_id:
        query = query.filter(DocumentAccessLog.document_id == document_id)
    
    if user_id:
        query = query.filter(DocumentAccessLog.user_id == user_id)
    
    if action_type:
        query = query.filter(DocumentAccessLog.action_type == action_type)
    
    if access_result:
        query = query.filter(DocumentAccessLog.access_result == access_result)
    
    if from_date:
        query = query.filter(DocumentAccessLog.accessed_at >= from_date)
    
    if to_date:
        query = query.filter(DocumentAccessLog.accessed_at <= to_date)
    
    query = query.order_by(desc(DocumentAccessLog.accessed_at))
    logs = query.offset(skip).limit(limit).all()
    return logs


@router.get("/{document_id}/access-logs", response_model=List[DocumentAccessLogResponse])
async def get_document_access_logs(
    document_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get access logs for a specific document"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    logs = db.query(DocumentAccessLog).filter(
        DocumentAccessLog.document_id == document_id
    ).order_by(desc(DocumentAccessLog.accessed_at)).offset(skip).limit(limit).all()
    return logs


# ============================================================================
# DOCUMENT RETENTION POLICY ENDPOINTS
# ============================================================================

@router.post("/retention-policies", response_model=DocumentRetentionPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_retention_policy(
    policy: DocumentRetentionPolicyCreate,
    db: Session = Depends(get_db)
):
    """Create a new document retention policy"""
    # Check if policy code already exists
    existing = db.query(DocumentRetentionPolicy).filter(
        DocumentRetentionPolicy.policy_code == policy.policy_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Retention policy with code '{policy.policy_code}' already exists"
        )
    
    db_policy = DocumentRetentionPolicy(**policy.dict())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy


@router.get("/retention-policies", response_model=List[DocumentRetentionPolicyResponse])
async def list_retention_policies(
    category_id: Optional[UUID] = Query(None),
    document_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all retention policies with optional filters"""
    query = db.query(DocumentRetentionPolicy)
    
    if category_id:
        query = query.filter(DocumentRetentionPolicy.category_id == category_id)
    
    if document_type:
        query = query.filter(DocumentRetentionPolicy.document_type == document_type)
    
    if is_active is not None:
        query = query.filter(DocumentRetentionPolicy.is_active == is_active)
    
    query = query.order_by(desc(DocumentRetentionPolicy.priority), DocumentRetentionPolicy.policy_name)
    policies = query.offset(skip).limit(limit).all()
    return policies


@router.get("/retention-policies/{policy_id}", response_model=DocumentRetentionPolicyResponse)
async def get_retention_policy(
    policy_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a retention policy by ID"""
    policy = db.query(DocumentRetentionPolicy).filter(
        DocumentRetentionPolicy.policy_id == policy_id
    ).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retention policy not found"
        )
    return policy


@router.put("/retention-policies/{policy_id}", response_model=DocumentRetentionPolicyResponse)
async def update_retention_policy(
    policy_id: UUID,
    policy_update: DocumentRetentionPolicyUpdate,
    db: Session = Depends(get_db)
):
    """Update a retention policy"""
    db_policy = db.query(DocumentRetentionPolicy).filter(
        DocumentRetentionPolicy.policy_id == policy_id
    ).first()
    if not db_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retention policy not found"
        )
    
    update_data = policy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_policy, field, value)
    
    db.commit()
    db.refresh(db_policy)
    return db_policy


@router.delete("/retention-policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_retention_policy(
    policy_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a retention policy (soft delete)"""
    db_policy = db.query(DocumentRetentionPolicy).filter(
        DocumentRetentionPolicy.policy_id == policy_id
    ).first()
    if not db_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retention policy not found"
        )
    
    db_policy.is_active = False
    db.commit()


# ============================================================================
# DOCUMENT SHARE ENDPOINTS
# ============================================================================

@router.post("/shares", response_model=DocumentShareResponse, status_code=status.HTTP_201_CREATED)
async def create_document_share(
    share: DocumentShareCreate,
    db: Session = Depends(get_db)
):
    """Create a document share link"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == share.document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Generate unique share token
    share_token = secrets.token_urlsafe(32)
    
    share_data = share.dict(exclude={'password'})
    db_share = DocumentShare(
        **share_data,
        share_token=share_token
    )
    
    # Handle password if provided
    if share.is_password_protected and share.password:
        # In production, use proper password hashing (bcrypt, argon2, etc.)
        db_share.password_hash = share.password  # Simplified for this example
    
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share


@router.get("/shares", response_model=List[DocumentShareResponse])
async def list_document_shares(
    document_id: Optional[UUID] = Query(None),
    shared_by: Optional[UUID] = Query(None),
    is_revoked: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all document shares with optional filters"""
    query = db.query(DocumentShare)
    
    if document_id:
        query = query.filter(DocumentShare.document_id == document_id)
    
    if shared_by:
        query = query.filter(DocumentShare.shared_by == shared_by)
    
    if is_revoked is not None:
        query = query.filter(DocumentShare.is_revoked == is_revoked)
    
    query = query.order_by(desc(DocumentShare.shared_at))
    shares = query.offset(skip).limit(limit).all()
    return shares


@router.get("/shares/{share_id}", response_model=DocumentShareResponse)
async def get_document_share(
    share_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a document share by ID"""
    share = db.query(DocumentShare).filter(DocumentShare.share_id == share_id).first()
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document share not found"
        )
    return share


@router.get("/shares/token/{share_token}", response_model=DocumentShareResponse)
async def get_document_share_by_token(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get a document share by token"""
    share = db.query(DocumentShare).filter(DocumentShare.share_token == share_token).first()
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document share not found"
        )
    
    # Check if share is valid
    if share.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This share link has been revoked"
        )
    
    if share.expires_at and share.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This share link has expired"
        )
    
    if share.max_access_count and share.access_count >= share.max_access_count:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This share link has reached its maximum access count"
        )
    
    # Increment access count and update last accessed
    share.access_count += 1
    share.last_accessed_at = datetime.now()
    db.commit()
    db.refresh(share)
    
    return share


@router.put("/shares/{share_id}", response_model=DocumentShareResponse)
async def update_document_share(
    share_id: UUID,
    share_update: DocumentShareUpdate,
    db: Session = Depends(get_db)
):
    """Update a document share"""
    db_share = db.query(DocumentShare).filter(DocumentShare.share_id == share_id).first()
    if not db_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document share not found"
        )
    
    update_data = share_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_share, field, value)
    
    db.commit()
    db.refresh(db_share)
    return db_share


@router.post("/shares/{share_id}/revoke", response_model=DocumentShareResponse)
async def revoke_document_share(
    share_id: UUID,
    revoke_request: DocumentShareRevoke,
    db: Session = Depends(get_db)
):
    """Revoke a document share"""
    db_share = db.query(DocumentShare).filter(DocumentShare.share_id == share_id).first()
    if not db_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document share not found"
        )
    
    if db_share.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This share has already been revoked"
        )
    
    db_share.is_revoked = True
    db_share.revoked_at = datetime.now()
    db_share.revoked_by = revoke_request.revoked_by
    db_share.revocation_reason = revoke_request.revocation_reason
    
    db.commit()
    db.refresh(db_share)
    return db_share


@router.get("/{document_id}/shares", response_model=List[DocumentShareResponse])
async def list_shares_for_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """List all shares for a specific document"""
    # Verify document exists
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    shares = db.query(DocumentShare).filter(
        DocumentShare.document_id == document_id
    ).order_by(desc(DocumentShare.shared_at)).all()
    return shares


# ============================================================================
# BULK OPERATION ENDPOINTS
# ============================================================================

@router.post("/bulk/tag", status_code=status.HTTP_200_OK)
async def bulk_tag_documents(
    request: BulkDocumentTagRequest,
    db: Session = Depends(get_db)
):
    """Add tags to multiple documents"""
    success_count = 0
    failed_count = 0
    errors = []
    
    for document_id in request.document_ids:
        # Verify document exists
        document = db.query(Document).filter(Document.document_id == document_id).first()
        if not document:
            errors.append(f"Document {document_id} not found")
            failed_count += 1
            continue
        
        for tag_id in request.tag_ids:
            # Check if mapping already exists
            existing = db.query(DocumentTagMapping).filter(
                and_(
                    DocumentTagMapping.document_id == document_id,
                    DocumentTagMapping.tag_id == tag_id
                )
            ).first()
            
            if not existing:
                mapping = DocumentTagMapping(
                    document_id=document_id,
                    tag_id=tag_id,
                    tagged_by=request.tagged_by
                )
                db.add(mapping)
                
                # Increment tag usage count
                tag = db.query(DocumentTag).filter(DocumentTag.tag_id == tag_id).first()
                if tag:
                    tag.usage_count += 1
        
        success_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Bulk tagging completed",
        "success_count": success_count,
        "failed_count": failed_count,
        "errors": errors
    }


@router.post("/bulk/delete", status_code=status.HTTP_200_OK)
async def bulk_delete_documents(
    request: BulkDocumentDeleteRequest,
    db: Session = Depends(get_db)
):
    """Delete multiple documents (soft delete)"""
    success_count = 0
    failed_count = 0
    errors = []
    
    for document_id in request.document_ids:
        document = db.query(Document).filter(Document.document_id == document_id).first()
        if not document:
            errors.append(f"Document {document_id} not found")
            failed_count += 1
            continue
        
        document.is_deleted = True
        document.deleted_at = datetime.now()
        document.deleted_by = request.deleted_by
        document.deletion_reason = request.deletion_reason
        success_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Bulk deletion completed",
        "success_count": success_count,
        "failed_count": failed_count,
        "errors": errors
    }


@router.post("/bulk/move", status_code=status.HTTP_200_OK)
async def bulk_move_documents(
    request: BulkDocumentMoveRequest,
    db: Session = Depends(get_db)
):
    """Move multiple documents to a different category"""
    # Verify target category exists
    target_category = db.query(DocumentCategory).filter(
        DocumentCategory.category_id == request.target_category_id
    ).first()
    if not target_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target category not found"
        )
    
    success_count = 0
    failed_count = 0
    errors = []
    
    for document_id in request.document_ids:
        document = db.query(Document).filter(Document.document_id == document_id).first()
        if not document:
            errors.append(f"Document {document_id} not found")
            failed_count += 1
            continue
        
        document.category_id = request.target_category_id
        document.updated_by = request.moved_by
        success_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Bulk move completed",
        "success_count": success_count,
        "failed_count": failed_count,
        "errors": errors
    }


# ============================================================================
# OCR ENDPOINTS
# ============================================================================

@router.post("/ocr/extract", response_model=DocumentOCRResponse)
async def extract_document_text_ocr(
    request: DocumentOCRRequest,
    db: Session = Depends(get_db)
):
    """Extract text from document using OCR"""
    # Verify document exists
    document = db.query(Document).filter(
        Document.document_id == request.document_id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # In production, this would call an actual OCR service (Tesseract, AWS Textract, Google Vision, etc.)
    # For now, return a mock response
    ocr_result = DocumentOCRResponse(
        document_id=request.document_id,
        ocr_status='completed',
        extracted_text='Sample extracted text from OCR processing...',
        extracted_data={
            'language': request.ocr_language,
            'pages': 1,
            'words_count': 150,
            'confidence': 0.95
        },
        confidence_score=0.95,
        processing_time_seconds=3,
        processed_at=datetime.now()
    )
    
    # Update document with OCR data
    if not document.ocr_text:
        document.ocr_text = ocr_result.extracted_text
    if not document.extracted_data:
        document.extracted_data = ocr_result.extracted_data
    
    db.commit()
    
    return ocr_result


@router.post("/{document_id}/ocr/reprocess", response_model=DocumentOCRResponse)
async def reprocess_document_ocr(
    document_id: UUID,
    ocr_language: str = Query(default='eng', max_length=10),
    db: Session = Depends(get_db)
):
    """Reprocess OCR for a document"""
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Mock OCR reprocessing
    ocr_result = DocumentOCRResponse(
        document_id=document_id,
        ocr_status='completed',
        extracted_text='Reprocessed text from OCR...',
        extracted_data={'language': ocr_language, 'reprocessed': True},
        confidence_score=0.96,
        processing_time_seconds=2,
        processed_at=datetime.now()
    )
    
    document.ocr_text = ocr_result.extracted_text
    document.extracted_data = ocr_result.extracted_data
    db.commit()
    
    return ocr_result


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@router.get("/statistics/overview", response_model=DocumentStatistics)
async def get_document_statistics(
    db: Session = Depends(get_db)
):
    """Get overall document management statistics"""
    # Total documents
    total_documents = db.query(func.count(Document.document_id)).filter(
        Document.is_deleted == False
    ).scalar() or 0
    
    # Total size
    total_size = db.query(func.sum(Document.file_size_bytes)).filter(
        Document.is_deleted == False
    ).scalar() or 0
    total_size_mb = round(total_size / (1024 * 1024), 2) if total_size else 0
    
    # Documents by category
    category_stats = db.query(
        DocumentCategory.category_name,
        func.count(Document.document_id)
    ).join(Document).filter(
        Document.is_deleted == False
    ).group_by(DocumentCategory.category_name).all()
    
    documents_by_category = {cat: count for cat, count in category_stats}
    
    # Documents by type
    type_stats = db.query(
        Document.document_type,
        func.count(Document.document_id)
    ).filter(
        Document.is_deleted == False
    ).group_by(Document.document_type).all()
    
    documents_by_type = {dtype: count for dtype, count in type_stats}
    
    # Documents by status
    status_stats = db.query(
        Document.storage_status,
        func.count(Document.document_id)
    ).filter(
        Document.is_deleted == False
    ).group_by(Document.storage_status).all()
    
    documents_by_status = {status: count for status, count in status_stats}
    
    # Recent uploads (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_uploads = db.query(func.count(Document.document_id)).filter(
        and_(
            Document.created_at >= seven_days_ago,
            Document.is_deleted == False
        )
    ).scalar() or 0
    
    # Pending approvals
    pending_approvals = db.query(func.count(DocumentApproval.approval_id)).filter(
        DocumentApproval.approval_status == 'pending'
    ).scalar() or 0
    
    # Documents expiring soon (next 30 days)
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    documents_expiring = db.query(func.count(Document.document_id)).filter(
        and_(
            Document.expiry_date.isnot(None),
            Document.expiry_date <= thirty_days_from_now,
            Document.is_deleted == False
        )
    ).scalar() or 0
    
    return DocumentStatistics(
        total_documents=total_documents,
        total_size_mb=total_size_mb,
        documents_by_category=documents_by_category,
        documents_by_type=documents_by_type,
        documents_by_status=documents_by_status,
        recent_uploads=recent_uploads,
        pending_approvals=pending_approvals,
        documents_expiring_soon=documents_expiring
    )


@router.get("/statistics/workflows", response_model=WorkflowStatistics)
async def get_workflow_statistics(
    db: Session = Depends(get_db)
):
    """Get workflow and approval statistics"""
    from datetime import timedelta
    
    # Total workflows
    total_workflows = db.query(func.count(DocumentWorkflow.workflow_id)).scalar() or 0
    
    # Active workflows
    active_workflows = db.query(func.count(DocumentWorkflow.workflow_id)).filter(
        DocumentWorkflow.is_active == True
    ).scalar() or 0
    
    # Pending approvals
    pending_approvals = db.query(func.count(DocumentApproval.approval_id)).filter(
        DocumentApproval.approval_status == 'pending'
    ).scalar() or 0
    
    # Approved today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    approved_today = db.query(func.count(DocumentApproval.approval_id)).filter(
        and_(
            DocumentApproval.approval_status == 'approved',
            DocumentApproval.completed_at >= today_start
        )
    ).scalar() or 0
    
    # Rejected today
    rejected_today = db.query(func.count(DocumentApproval.approval_id)).filter(
        and_(
            DocumentApproval.approval_status == 'rejected',
            DocumentApproval.completed_at >= today_start
        )
    ).scalar() or 0
    
    # Average approval time (in hours)
    completed_approvals = db.query(
        DocumentApproval.initiated_at,
        DocumentApproval.completed_at
    ).filter(
        and_(
            DocumentApproval.approval_status.in_(['approved', 'rejected']),
            DocumentApproval.completed_at.isnot(None)
        )
    ).limit(100).all()
    
    if completed_approvals:
        total_hours = sum([
            (completed - initiated).total_seconds() / 3600
            for initiated, completed in completed_approvals
        ])
        avg_approval_time = round(total_hours / len(completed_approvals), 2)
    else:
        avg_approval_time = 0
    
    # Escalated workflows
    escalated_workflows = db.query(func.count(DocumentApproval.approval_id)).filter(
        DocumentApproval.is_escalated == True
    ).scalar() or 0
    
    # Overdue workflows
    overdue_workflows = db.query(func.count(DocumentApproval.approval_id)).filter(
        and_(
            DocumentApproval.approval_status == 'pending',
            DocumentApproval.due_date.isnot(None),
            DocumentApproval.due_date < datetime.now()
        )
    ).scalar() or 0
    
    return WorkflowStatistics(
        total_workflows=total_workflows,
        active_workflows=active_workflows,
        pending_approvals=pending_approvals,
        approved_today=approved_today,
        rejected_today=rejected_today,
        average_approval_time_hours=avg_approval_time,
        escalated_workflows=escalated_workflows,
        overdue_workflows=overdue_workflows
    )


@router.get("/statistics/category/{category_id}")
async def get_category_statistics(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific category"""
    # Verify category exists
    category = db.query(DocumentCategory).filter(
        DocumentCategory.category_id == category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Document count
    doc_count = db.query(func.count(Document.document_id)).filter(
        and_(
            Document.category_id == category_id,
            Document.is_deleted == False
        )
    ).scalar() or 0
    
    # Total size
    total_size = db.query(func.sum(Document.file_size_bytes)).filter(
        and_(
            Document.category_id == category_id,
            Document.is_deleted == False
        )
    ).scalar() or 0
    
    # Recent uploads (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_count = db.query(func.count(Document.document_id)).filter(
        and_(
            Document.category_id == category_id,
            Document.created_at >= thirty_days_ago,
            Document.is_deleted == False
        )
    ).scalar() or 0
    
    return {
        "category_id": str(category_id),
        "category_name": category.category_name,
        "total_documents": doc_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0,
        "recent_uploads_30d": recent_count
    }


@router.get("/statistics/user/{user_id}")
async def get_user_document_statistics(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get document statistics for a specific user"""
    # Documents uploaded
    uploaded_count = db.query(func.count(Document.document_id)).filter(
        and_(
            Document.uploaded_by == user_id,
            Document.is_deleted == False
        )
    ).scalar() or 0
    
    # Approvals pending
    pending_approvals = db.query(func.count(DocumentApproval.approval_id)).filter(
        and_(
            DocumentApproval.assigned_to == user_id,
            DocumentApproval.approval_status == 'pending'
        )
    ).scalar() or 0
    
    # Approvals completed
    completed_approvals = db.query(func.count(DocumentApproval.approval_id)).filter(
        and_(
            DocumentApproval.assigned_to == user_id,
            DocumentApproval.approval_status.in_(['approved', 'rejected'])
        )
    ).scalar() or 0
    
    # Recent access count (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    access_count = db.query(func.count(DocumentAccessLog.log_id)).filter(
        and_(
            DocumentAccessLog.user_id == user_id,
            DocumentAccessLog.accessed_at >= seven_days_ago
        )
    ).scalar() or 0
    
    return {
        "user_id": str(user_id),
        "documents_uploaded": uploaded_count,
        "pending_approvals": pending_approvals,
        "completed_approvals": completed_approvals,
        "recent_access_count_7d": access_count
    }
