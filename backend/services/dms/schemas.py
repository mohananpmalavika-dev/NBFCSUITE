"""
DMS Pydantic Schemas
Request and response models for DMS operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, UUID4
from enum import Enum


# Enums matching database models
class DocumentStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentTypeEnum(str, Enum):
    CONTRACT = "contract"
    POLICY = "policy"
    PROCEDURE = "procedure"
    FORM = "form"
    REPORT = "report"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CERTIFICATE = "certificate"
    LETTER = "letter"
    MEMORANDUM = "memorandum"
    AGREEMENT = "agreement"
    NOTICE = "notice"
    CIRCULAR = "circular"
    OTHER = "other"


class DocumentCategoryEnum(str, Enum):
    LEGAL = "legal"
    FINANCIAL = "financial"
    HR = "hr"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"
    MARKETING = "marketing"
    IT = "it"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    INTERNAL = "internal"


class AccessLevelEnum(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"


class WorkflowStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class ApprovalStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    SKIPPED = "skipped"


class SignatureStatusEnum(str, Enum):
    PENDING = "pending"
    SIGNED = "signed"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SignatureTypeEnum(str, Enum):
    SIMPLE = "simple"
    BASIC = "basic"
    ADVANCED = "advanced"
    QUALIFIED = "qualified"


# Document Schemas
class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: DocumentTypeEnum
    category: DocumentCategoryEnum
    access_level: AccessLevelEnum = AccessLevelEnum.INTERNAL
    department: Optional[str] = None
    tags: Optional[List[str]] = []
    custom_fields: Optional[Dict[str, Any]] = {}
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    parent_document_id: Optional[UUID4] = None
    reference_number: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: Optional[DocumentTypeEnum] = None
    category: Optional[DocumentCategoryEnum] = None
    access_level: Optional[AccessLevelEnum] = None
    status: Optional[DocumentStatusEnum] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    reference_number: Optional[str] = None


class DocumentVersionCreate(BaseModel):
    """Schema for creating a new document version"""
    version_notes: Optional[str] = None
    is_major_version: bool = False
    changes_summary: Optional[str] = None


class DocumentVersionResponse(BaseModel):
    """Response model for document version"""
    id: UUID4
    document_id: UUID4
    version_number: int
    file_name: str
    file_type: str
    file_size: int
    file_path: str
    file_hash: str
    version_notes: Optional[str]
    is_major_version: bool
    changes_summary: Optional[str]
    uploaded_by: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Response model for document"""
    id: UUID4
    document_number: str
    title: str
    description: Optional[str]
    document_type: str
    category: str
    access_level: str
    status: str
    version_number: int
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    owner_id: UUID4
    department: Optional[str]
    tags: Optional[List[str]]
    custom_fields: Optional[Dict[str, Any]]
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    review_date: Optional[datetime]
    parent_document_id: Optional[UUID4]
    reference_number: Optional[str]
    is_encrypted: bool
    is_locked: bool
    download_count: int
    view_count: int
    last_accessed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID4]
    updated_by: Optional[UUID4]

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response model for document list"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class DocumentSearchRequest(BaseModel):
    """Request model for document search"""
    query: Optional[str] = None
    document_type: Optional[DocumentTypeEnum] = None
    category: Optional[DocumentCategoryEnum] = None
    status: Optional[DocumentStatusEnum] = None
    access_level: Optional[AccessLevelEnum] = None
    department: Optional[str] = None
    owner_id: Optional[UUID4] = None
    tags: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    expiring_soon: Optional[bool] = False
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


# Workflow Schemas
class WorkflowStepCreate(BaseModel):
    """Schema for workflow step"""
    step_number: int
    step_name: str
    approver_id: UUID4
    approver_role: Optional[str] = None
    due_date: Optional[datetime] = None


class WorkflowCreate(BaseModel):
    """Schema for creating a workflow"""
    workflow_name: str
    workflow_type: str = "approval"
    description: Optional[str] = None
    steps: List[WorkflowStepCreate]
    is_sequential: bool = True
    require_all_approvals: bool = True
    priority: str = "normal"
    due_date: Optional[datetime] = None


class WorkflowTemplateCreate(BaseModel):
    """Schema for creating a workflow template"""
    name: str
    description: Optional[str] = None
    workflow_type: str
    applicable_document_types: Optional[List[str]] = []
    applicable_categories: Optional[List[str]] = []
    steps: List[Dict[str, Any]]
    is_sequential: bool = True
    require_all_approvals: bool = True


class ApprovalAction(BaseModel):
    """Schema for approval action"""
    status: ApprovalStatusEnum
    comments: Optional[str] = None
    attachments: Optional[List[str]] = []


class ApprovalResponse(BaseModel):
    """Response model for approval"""
    id: UUID4
    workflow_id: UUID4
    step_number: int
    step_name: str
    approver_id: UUID4
    status: str
    response_date: Optional[datetime]
    comments: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowResponse(BaseModel):
    """Response model for workflow"""
    id: UUID4
    document_id: UUID4
    workflow_name: str
    workflow_type: str
    status: str
    current_step: int
    total_steps: int
    initiated_by: UUID4
    initiated_at: datetime
    completed_at: Optional[datetime]
    priority: str
    due_date: Optional[datetime]
    approvals: Optional[List[ApprovalResponse]] = []

    class Config:
        from_attributes = True


# Permission Schemas
class PermissionCreate(BaseModel):
    """Schema for creating document permission"""
    document_id: UUID4
    user_id: Optional[UUID4] = None
    role_id: Optional[UUID4] = None
    department: Optional[str] = None
    can_view: bool = True
    can_download: bool = False
    can_edit: bool = False
    can_delete: bool = False
    can_share: bool = False
    can_approve: bool = False
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    grant_reason: Optional[str] = None

    @validator('user_id', 'role_id', 'department')
    def validate_subject(cls, v, values):
        """At least one subject must be specified"""
        if not any([values.get('user_id'), values.get('role_id'), values.get('department')]):
            raise ValueError('At least one of user_id, role_id, or department must be specified')
        return v


class PermissionResponse(BaseModel):
    """Response model for permission"""
    id: UUID4
    document_id: UUID4
    user_id: Optional[UUID4]
    role_id: Optional[UUID4]
    department: Optional[str]
    can_view: bool
    can_download: bool
    can_edit: bool
    can_delete: bool
    can_share: bool
    can_approve: bool
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    granted_by: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


# Signature Schemas
class SignatureRequest(BaseModel):
    """Schema for requesting a signature"""
    document_id: UUID4
    signer_id: UUID4
    signature_type: SignatureTypeEnum = SignatureTypeEnum.SIMPLE
    expires_at: Optional[datetime] = None


class SignatureAction(BaseModel):
    """Schema for signature action"""
    status: SignatureStatusEnum
    signature_data: Optional[str] = None  # Base64 signature
    verification_method: Optional[str] = None
    rejection_reason: Optional[str] = None


class SignatureResponse(BaseModel):
    """Response model for signature"""
    id: UUID4
    document_id: UUID4
    version_id: UUID4
    signer_id: UUID4
    signer_name: str
    signer_email: str
    signature_type: str
    status: str
    requested_at: datetime
    signed_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# Comment Schemas
class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    document_id: UUID4
    version_id: Optional[UUID4] = None
    parent_comment_id: Optional[UUID4] = None
    comment_text: str = Field(..., min_length=1)
    comment_type: str = "general"
    page_number: Optional[int] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None


class CommentResponse(BaseModel):
    """Response model for comment"""
    id: UUID4
    document_id: UUID4
    version_id: Optional[UUID4]
    parent_comment_id: Optional[UUID4]
    comment_text: str
    comment_type: str
    author_id: UUID4
    page_number: Optional[int]
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Audit Log Schema
class AuditLogResponse(BaseModel):
    """Response model for audit log"""
    id: UUID4
    document_id: UUID4
    action: str
    action_category: str
    description: Optional[str]
    user_id: Optional[UUID4]
    user_name: Optional[str]
    user_email: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# Statistics Schemas
class DocumentStatistics(BaseModel):
    """Statistics for documents"""
    total_documents: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_category: Dict[str, int]
    expiring_soon: int
    pending_approvals: int
    pending_signatures: int


class UserDocumentStats(BaseModel):
    """User-specific document statistics"""
    owned_documents: int
    pending_approvals: int
    pending_signatures: int
    recent_activity: List[Dict[str, Any]]
