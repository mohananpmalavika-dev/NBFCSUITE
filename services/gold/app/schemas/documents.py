"""
Document Management Schemas
Phase 10: Document Management
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# ============================================================================
# DOCUMENT CATEGORY SCHEMAS
# ============================================================================

class DocumentCategoryBase(BaseModel):
    category_code: str = Field(..., max_length=50)
    category_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    category_level: int = Field(default=1)
    is_system_category: bool = Field(default=False)
    retention_period_days: Optional[int] = None
    is_mandatory: bool = Field(default=False)
    allowed_extensions: Optional[List[str]] = None
    max_file_size_mb: Optional[Decimal] = None
    requires_approval: bool = Field(default=False)
    requires_ocr: bool = Field(default=False)
    metadata_schema: Optional[Dict[str, Any]] = None
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class DocumentCategoryCreate(DocumentCategoryBase):
    created_by: UUID


class DocumentCategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    retention_period_days: Optional[int] = None
    is_mandatory: Optional[bool] = None
    allowed_extensions: Optional[List[str]] = None
    max_file_size_mb: Optional[Decimal] = None
    requires_approval: Optional[bool] = None
    requires_ocr: Optional[bool] = None
    metadata_schema: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    updated_by: UUID


class DocumentCategoryResponse(DocumentCategoryBase):
    category_id: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================

class DocumentBase(BaseModel):
    document_name: str = Field(..., max_length=300)
    description: Optional[str] = None
    category_id: UUID
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID
    document_type: str = Field(..., max_length=50)
    access_level: str = Field(default='internal', max_length=20)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None


class DocumentCreate(DocumentBase):
    file_name: str = Field(..., max_length=300)
    file_extension: str = Field(..., max_length=20)
    file_size_bytes: int
    mime_type: str = Field(..., max_length=100)
    storage_path: str
    storage_provider: str = Field(default='s3', max_length=50)
    checksum: str = Field(..., max_length=64)
    is_encrypted: bool = Field(default=True)
    encryption_key_id: Optional[str] = Field(None, max_length=100)
    created_by: UUID


class DocumentUpdate(BaseModel):
    document_name: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    access_level: Optional[str] = Field(None, max_length=20)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    remarks: Optional[str] = None
    updated_by: UUID


class DocumentResponse(DocumentBase):
    document_id: UUID
    document_number: str
    file_name: str
    file_extension: str
    file_size_bytes: int
    mime_type: str
    storage_path: str
    storage_provider: str
    checksum: str
    current_version: int
    is_encrypted: bool
    encryption_key_id: Optional[str]
    ocr_status: str
    ocr_text: Optional[str]
    ocr_confidence: Optional[Decimal]
    ocr_processed_at: Optional[datetime]
    is_signed: bool
    signature_status: Optional[str]
    signed_by: Optional[UUID]
    signed_at: Optional[datetime]
    signature_certificate: Optional[str]
    retention_until: Optional[date]
    is_archived: bool
    archived_at: Optional[datetime]
    archived_by: Optional[UUID]
    is_deleted: bool
    deleted_at: Optional[datetime]
    deleted_by: Optional[UUID]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadRequest(BaseModel):
    document_name: str = Field(..., max_length=300)
    description: Optional[str] = None
    category_id: UUID
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID
    document_type: str = Field(..., max_length=50)
    access_level: str = Field(default='internal')
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by: UUID


class DocumentSignRequest(BaseModel):
    signed_by: UUID
    signature_certificate: Optional[str] = None


# ============================================================================
# DOCUMENT VERSION SCHEMAS
# ============================================================================

class DocumentVersionBase(BaseModel):
    version_number: int
    file_name: str = Field(..., max_length=300)
    file_size_bytes: int
    storage_path: str
    checksum: str = Field(..., max_length=64)
    change_description: Optional[str] = None
    version_type: str = Field(default='minor', max_length=20)
    metadata: Optional[Dict[str, Any]] = None


class DocumentVersionCreate(DocumentVersionBase):
    document_id: UUID
    replaced_version_id: Optional[UUID] = None
    created_by: UUID


class DocumentVersionResponse(DocumentVersionBase):
    version_id: UUID
    document_id: UUID
    is_current: bool
    replaced_version_id: Optional[UUID]
    ocr_text: Optional[str]
    ocr_confidence: Optional[Decimal]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT METADATA SCHEMAS
# ============================================================================

class DocumentMetadataBase(BaseModel):
    metadata_key: str = Field(..., max_length=100)
    metadata_value: str
    value_type: str = Field(..., max_length=20)
    is_indexed: bool = Field(default=False)
    is_searchable: bool = Field(default=True)
    display_order: int = Field(default=0)


class DocumentMetadataCreate(DocumentMetadataBase):
    document_id: UUID
    created_by: UUID


class DocumentMetadataUpdate(BaseModel):
    metadata_value: Optional[str] = None
    value_type: Optional[str] = Field(None, max_length=20)
    is_indexed: Optional[bool] = None
    is_searchable: Optional[bool] = None
    display_order: Optional[int] = None
    updated_by: UUID


class DocumentMetadataResponse(DocumentMetadataBase):
    metadata_id: UUID
    document_id: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT TEMPLATE SCHEMAS
# ============================================================================

class DocumentTemplateBase(BaseModel):
    template_code: str = Field(..., max_length=50)
    template_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: UUID
    template_type: str = Field(..., max_length=50)
    file_format: str = Field(..., max_length=20)
    storage_path: str
    template_variables: Optional[Dict[str, Any]] = None
    merge_rules: Optional[Dict[str, Any]] = None
    is_system_template: bool = Field(default=False)
    version: str = Field(default='1.0', max_length=20)
    is_active: bool = Field(default=True)


class DocumentTemplateCreate(DocumentTemplateBase):
    created_by: UUID


class DocumentTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    template_type: Optional[str] = Field(None, max_length=50)
    file_format: Optional[str] = Field(None, max_length=20)
    storage_path: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    merge_rules: Optional[Dict[str, Any]] = None
    version: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    updated_by: UUID


class DocumentTemplateResponse(DocumentTemplateBase):
    template_id: UUID
    usage_count: int
    last_used_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentTemplateGenerateRequest(BaseModel):
    template_id: UUID
    variables: Dict[str, Any]
    output_format: Optional[str] = Field(default='pdf')
    created_by: UUID


# ============================================================================
# DOCUMENT WORKFLOW SCHEMAS
# ============================================================================

class DocumentWorkflowBase(BaseModel):
    workflow_code: str = Field(..., max_length=50)
    workflow_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    workflow_type: str = Field(..., max_length=50)
    workflow_steps: Dict[str, Any]
    trigger_conditions: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    is_mandatory: bool = Field(default=False)
    is_active: bool = Field(default=True)


class DocumentWorkflowCreate(DocumentWorkflowBase):
    created_by: UUID


class DocumentWorkflowUpdate(BaseModel):
    workflow_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    workflow_steps: Optional[Dict[str, Any]] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None
    updated_by: UUID


class DocumentWorkflowResponse(DocumentWorkflowBase):
    workflow_id: UUID
    usage_count: int
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT APPROVAL SCHEMAS
# ============================================================================

class DocumentApprovalBase(BaseModel):
    document_id: UUID
    workflow_id: UUID
    priority: str = Field(default='medium', max_length=20)
    remarks: Optional[str] = None


class DocumentApprovalCreate(DocumentApprovalBase):
    initiated_by: UUID


class DocumentApprovalUpdate(BaseModel):
    assigned_to: Optional[UUID] = None
    priority: Optional[str] = Field(None, max_length=20)
    remarks: Optional[str] = None


class DocumentApprovalActionRequest(BaseModel):
    action: str = Field(..., max_length=20)  # 'approve', 'reject', 'return'
    comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    action_by: UUID


class DocumentApprovalResponse(DocumentApprovalBase):
    approval_id: UUID
    approval_number: str
    current_step: int
    total_steps: int
    approval_status: str
    initiated_by: UUID
    initiated_at: datetime
    assigned_to: Optional[UUID]
    assigned_at: Optional[datetime]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    approval_steps: Optional[Dict[str, Any]]
    rejection_reason: Optional[str]
    is_escalated: bool
    escalated_at: Optional[datetime]
    escalated_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT TAG SCHEMAS
# ============================================================================

class DocumentTagBase(BaseModel):
    tag_name: str = Field(..., max_length=100)
    tag_category: Optional[str] = Field(None, max_length=50)
    tag_color: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None
    is_system_tag: bool = Field(default=False)
    is_active: bool = Field(default=True)


class DocumentTagCreate(DocumentTagBase):
    created_by: UUID


class DocumentTagUpdate(BaseModel):
    tag_name: Optional[str] = Field(None, max_length=100)
    tag_category: Optional[str] = Field(None, max_length=50)
    tag_color: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: UUID


class DocumentTagResponse(DocumentTagBase):
    tag_id: UUID
    usage_count: int
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentTagMappingCreate(BaseModel):
    document_id: UUID
    tag_id: UUID
    tagged_by: UUID


class DocumentTagMappingResponse(BaseModel):
    mapping_id: UUID
    document_id: UUID
    tag_id: UUID
    tagged_by: UUID
    tagged_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT ACCESS LOG SCHEMAS
# ============================================================================

class DocumentAccessLogCreate(BaseModel):
    document_id: UUID
    action_type: str = Field(..., max_length=50)
    user_id: UUID
    user_role: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    access_location: Optional[str] = Field(None, max_length=100)
    access_device: Optional[str] = Field(None, max_length=50)
    session_id: Optional[str] = Field(None, max_length=100)
    access_result: str = Field(..., max_length=20)
    denial_reason: Optional[str] = None
    file_version: Optional[int] = None
    download_size_bytes: Optional[int] = None
    access_duration_seconds: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentAccessLogResponse(DocumentAccessLogCreate):
    log_id: UUID
    accessed_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT RETENTION POLICY SCHEMAS
# ============================================================================

class DocumentRetentionPolicyBase(BaseModel):
    policy_code: str = Field(..., max_length=50)
    policy_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    document_type: Optional[str] = Field(None, max_length=50)
    retention_period_days: int
    retention_trigger: str = Field(..., max_length=50)
    archive_after_days: Optional[int] = None
    delete_after_retention: bool = Field(default=False)
    requires_legal_hold: bool = Field(default=False)
    compliance_regulation: Optional[str] = Field(None, max_length=100)
    auto_apply: bool = Field(default=False)
    priority: int = Field(default=0)
    is_active: bool = Field(default=True)
    effective_from: date
    effective_to: Optional[date] = None


class DocumentRetentionPolicyCreate(DocumentRetentionPolicyBase):
    created_by: UUID


class DocumentRetentionPolicyUpdate(BaseModel):
    policy_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    retention_period_days: Optional[int] = None
    archive_after_days: Optional[int] = None
    delete_after_retention: Optional[bool] = None
    requires_legal_hold: Optional[bool] = None
    auto_apply: Optional[bool] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    effective_to: Optional[date] = None
    updated_by: UUID


class DocumentRetentionPolicyResponse(DocumentRetentionPolicyBase):
    policy_id: UUID
    affected_documents_count: int
    last_executed_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT SHARE SCHEMAS
# ============================================================================

class DocumentShareBase(BaseModel):
    document_id: UUID
    share_type: str = Field(..., max_length=20)
    shared_with_user_id: Optional[UUID] = None
    shared_with_email: Optional[str] = Field(None, max_length=255)
    permissions: Dict[str, Any]
    max_access_count: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_password_protected: bool = Field(default=False)
    password: Optional[str] = None


class DocumentShareCreate(DocumentShareBase):
    shared_by: UUID


class DocumentShareUpdate(BaseModel):
    permissions: Optional[Dict[str, Any]] = None
    max_access_count: Optional[int] = None
    expires_at: Optional[datetime] = None


class DocumentShareRevoke(BaseModel):
    revoked_by: UUID
    revocation_reason: Optional[str] = None


class DocumentShareResponse(BaseModel):
    share_id: UUID
    document_id: UUID
    share_token: str
    share_type: str
    shared_with_user_id: Optional[UUID]
    shared_with_email: Optional[str]
    permissions: Dict[str, Any]
    access_count: int
    max_access_count: Optional[int]
    expires_at: Optional[datetime]
    is_password_protected: bool
    is_revoked: bool
    revoked_at: Optional[datetime]
    revoked_by: Optional[UUID]
    revocation_reason: Optional[str]
    shared_by: UUID
    shared_at: datetime
    last_accessed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LIST AND FILTER SCHEMAS
# ============================================================================

class DocumentListFilter(BaseModel):
    category_id: Optional[UUID] = None
    document_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    storage_status: Optional[str] = None
    is_deleted: Optional[bool] = None
    tag_ids: Optional[List[UUID]] = None
    search: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)


class DocumentApprovalListFilter(BaseModel):
    workflow_id: Optional[UUID] = None
    approval_status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    initiated_by: Optional[UUID] = None
    priority: Optional[str] = None
    is_escalated: Optional[bool] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)


class DocumentAccessLogFilter(BaseModel):
    document_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    action_type: Optional[str] = None
    access_result: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)


# ============================================================================
# BULK OPERATION SCHEMAS
# ============================================================================

class BulkDocumentTagRequest(BaseModel):
    document_ids: List[UUID]
    tag_ids: List[UUID]
    tagged_by: UUID


class BulkDocumentDeleteRequest(BaseModel):
    document_ids: List[UUID]
    deleted_by: UUID
    deletion_reason: str


class BulkDocumentMoveRequest(BaseModel):
    document_ids: List[UUID]
    target_category_id: UUID
    moved_by: UUID


class DocumentUploadRequest(BaseModel):
    category_id: UUID
    document_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    uploaded_by: UUID


class DocumentOCRRequest(BaseModel):
    document_id: UUID
    ocr_language: str = Field(default='eng', max_length=10)
    extract_tables: bool = Field(default=False)
    extract_signatures: bool = Field(default=False)


class DocumentOCRResponse(BaseModel):
    document_id: UUID
    ocr_status: str
    extracted_text: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    confidence_score: Optional[Decimal]
    processing_time_seconds: Optional[int]
    processed_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class DocumentStatistics(BaseModel):
    total_documents: int
    total_size_mb: Decimal
    documents_by_category: Dict[str, int]
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    recent_uploads: int
    pending_approvals: int
    documents_expiring_soon: int


class WorkflowStatistics(BaseModel):
    total_workflows: int
    active_workflows: int
    pending_approvals: int
    approved_today: int
    rejected_today: int
    average_approval_time_hours: Decimal
    escalated_workflows: int
    overdue_workflows: int
