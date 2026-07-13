"""
Document Management System (DMS) Models
Comprehensive document lifecycle management with version control,
workflow approvals, e-signatures, and secure storage
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, ForeignKey, 
    DateTime, Enum, BigInteger, JSON, Index
)
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from backend.shared.database.connection import Base
from backend.shared.database.models import BaseModel


# Enums
class DocumentStatus(str, enum.Enum):
    """Document lifecycle status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentType(str, enum.Enum):
    """Document types"""
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


class DocumentCategory(str, enum.Enum):
    """Document categories for organization"""
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


class AccessLevel(str, enum.Enum):
    """Document access levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"


class WorkflowStatus(str, enum.Enum):
    """Workflow processing status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class ApprovalStatus(str, enum.Enum):
    """Approval status for individual approvers"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    SKIPPED = "skipped"


class SignatureStatus(str, enum.Enum):
    """Digital signature status"""
    PENDING = "pending"
    SIGNED = "signed"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SignatureType(str, enum.Enum):
    """Type of digital signature"""
    SIMPLE = "simple"  # Click to sign
    BASIC = "basic"    # Username/password
    ADVANCED = "advanced"  # OTP verification
    QUALIFIED = "qualified"  # Digital certificate


# Models
class Document(BaseModel):
    """
    Main document entity
    Stores document metadata and current version information
    """
    __tablename__ = "dms_documents"
    
    # Basic Information
    document_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Classification
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    category = Column(Enum(DocumentCategory), nullable=False, index=True)
    access_level = Column(Enum(AccessLevel), nullable=False, default=AccessLevel.INTERNAL, index=True)
    
    # Status
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT, index=True)
    
    # Version Control
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("dms_document_versions.id"), nullable=True)
    version_number = Column(Integer, default=1, nullable=False)
    
    # File Information
    file_name = Column(String(500), nullable=True)
    file_type = Column(String(100), nullable=True)  # MIME type
    file_size = Column(BigInteger, nullable=True)  # Size in bytes
    file_path = Column(String(1000), nullable=True)  # Storage path
    file_hash = Column(String(256), nullable=True)  # SHA-256 hash for integrity
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    department = Column(String(100), nullable=True, index=True)
    
    # Metadata
    tags = Column(JSONB, nullable=True, default=list)  # Array of tags
    custom_fields = Column(JSONB, nullable=True, default=dict)  # Custom metadata
    
    # Dates
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True, index=True)
    review_date = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # References
    parent_document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=True, index=True)
    reference_number = Column(String(100), nullable=True)  # External reference
    
    # Security
    is_encrypted = Column(Boolean, default=False, nullable=False)
    encryption_key_id = Column(String(100), nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    download_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], backref="owned_documents")
    versions = relationship("DocumentVersion", foreign_keys="DocumentVersion.document_id", 
                          back_populates="document", cascade="all, delete-orphan")
    current_version = relationship("DocumentVersion", foreign_keys=[current_version_id], 
                                  post_update=True, uselist=False)
    workflows = relationship("DocumentWorkflow", back_populates="document", cascade="all, delete-orphan")
    permissions = relationship("DocumentPermission", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("DocumentComment", back_populates="document", cascade="all, delete-orphan")
    signatures = relationship("DocumentSignature", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_document_status_type', 'status', 'document_type'),
        Index('idx_document_owner_status', 'owner_id', 'status'),
        Index('idx_document_expiry', 'expiry_date', 'status'),
    )


class DocumentVersion(BaseModel):
    """
    Document versions
    Maintains complete version history with immutable records
    """
    __tablename__ = "dms_document_versions"
    
    # Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # File Information
    file_name = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(1000), nullable=False)  # Versioned storage path
    file_hash = Column(String(256), nullable=False)  # SHA-256 hash
    
    # Version Metadata
    version_notes = Column(Text, nullable=True)
    is_major_version = Column(Boolean, default=False, nullable=False)  # Major vs minor version
    
    # Changes
    changes_summary = Column(Text, nullable=True)
    diff_from_previous = Column(JSONB, nullable=True)  # Structured diff
    
    # Security
    is_encrypted = Column(Boolean, default=False, nullable=False)
    encryption_key_id = Column(String(100), nullable=True)
    
    # Upload Information
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    upload_ip = Column(String(45), nullable=True)  # IPv4 or IPv6
    upload_user_agent = Column(String(500), nullable=True)
    
    # Relationships
    document = relationship("Document", foreign_keys=[document_id], back_populates="versions")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    __table_args__ = (
        Index('idx_version_document', 'document_id', 'version_number'),
        # Unique constraint on document + version
        Index('idx_unique_document_version', 'document_id', 'version_number', unique=True),
    )


class DocumentWorkflow(BaseModel):
    """
    Document workflow instances
    Manages approval and review workflows for documents
    """
    __tablename__ = "dms_document_workflows"
    
    # Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=False, index=True)
    workflow_template_id = Column(UUID(as_uuid=True), ForeignKey("dms_workflow_templates.id"), nullable=True)
    
    # Workflow Information
    workflow_name = Column(String(200), nullable=False)
    workflow_type = Column(String(50), nullable=False)  # approval, review, signature
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(WorkflowStatus), nullable=False, default=WorkflowStatus.PENDING, index=True)
    current_step = Column(Integer, default=1, nullable=False)
    total_steps = Column(Integer, nullable=False)
    
    # Initiator
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    initiated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Completion
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Metadata
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Configuration
    is_sequential = Column(Boolean, default=True, nullable=False)  # Sequential vs parallel
    require_all_approvals = Column(Boolean, default=True, nullable=False)
    auto_approve_on_timeout = Column(Boolean, default=False, nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="workflows")
    template = relationship("WorkflowTemplate")
    approvals = relationship("DocumentApproval", back_populates="workflow", cascade="all, delete-orphan")
    initiator = relationship("User", foreign_keys=[initiated_by])
    
    __table_args__ = (
        Index('idx_workflow_status_due', 'status', 'due_date'),
    )


class WorkflowTemplate(BaseModel):
    """
    Reusable workflow templates
    Defines standard approval workflows for different document types
    """
    __tablename__ = "dms_workflow_templates"
    
    # Basic Information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    workflow_type = Column(String(50), nullable=False, index=True)
    
    # Applicability
    applicable_document_types = Column(JSONB, nullable=True, default=list)
    applicable_categories = Column(JSONB, nullable=True, default=list)
    
    # Configuration
    steps = Column(JSONB, nullable=False)  # Array of step definitions
    is_sequential = Column(Boolean, default=True, nullable=False)
    require_all_approvals = Column(Boolean, default=True, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Usage Statistics
    usage_count = Column(Integer, default=0, nullable=False)


class DocumentApproval(BaseModel):
    """
    Individual approval steps within a workflow
    """
    __tablename__ = "dms_document_approvals"
    
    # Reference
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("dms_document_workflows.id"), nullable=False, index=True)
    
    # Step Information
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(200), nullable=False)
    
    # Approver
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    approver_role = Column(String(100), nullable=True)  # Optional role requirement
    
    # Status
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING, index=True)
    
    # Delegation
    delegated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    delegated_at = Column(DateTime(timezone=True), nullable=True)
    delegation_reason = Column(Text, nullable=True)
    
    # Response
    response_date = Column(DateTime(timezone=True), nullable=True)
    comments = Column(Text, nullable=True)
    attachments = Column(JSONB, nullable=True, default=list)
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    reminded_at = Column(DateTime(timezone=True), nullable=True)
    reminder_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    workflow = relationship("DocumentWorkflow", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_id])
    delegate = relationship("User", foreign_keys=[delegated_to])
    
    __table_args__ = (
        Index('idx_approval_workflow_step', 'workflow_id', 'step_number'),
        Index('idx_approval_approver_status', 'approver_id', 'status'),
    )


class DocumentPermission(BaseModel):
    """
    Document access permissions
    Granular access control for documents
    """
    __tablename__ = "dms_document_permissions"
    
    # Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=False, index=True)
    
    # Subject (User or Role)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True, index=True)
    department = Column(String(100), nullable=True, index=True)
    
    # Permissions
    can_view = Column(Boolean, default=True, nullable=False)
    can_download = Column(Boolean, default=False, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    can_share = Column(Boolean, default=False, nullable=False)
    can_approve = Column(Boolean, default=False, nullable=False)
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Grant Information
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    grant_reason = Column(Text, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="permissions")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role", foreign_keys=[role_id])
    granter = relationship("User", foreign_keys=[granted_by])
    
    __table_args__ = (
        Index('idx_permission_document_user', 'document_id', 'user_id'),
        Index('idx_permission_document_role', 'document_id', 'role_id'),
    )


class DocumentSignature(BaseModel):
    """
    Digital signatures for documents
    E-signature capability with audit trail
    """
    __tablename__ = "dms_document_signatures"
    
    # Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("dms_document_versions.id"), nullable=False)
    
    # Signer
    signer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    signer_name = Column(String(200), nullable=False)
    signer_email = Column(String(200), nullable=False)
    signer_title = Column(String(200), nullable=True)
    
    # Signature Information
    signature_type = Column(Enum(SignatureType), nullable=False, default=SignatureType.SIMPLE)
    status = Column(Enum(SignatureStatus), nullable=False, default=SignatureStatus.PENDING, index=True)
    
    # Signature Data
    signature_image_path = Column(String(1000), nullable=True)  # Path to signature image
    signature_data = Column(Text, nullable=True)  # Base64 signature or certificate
    signature_hash = Column(String(256), nullable=True)  # Hash of signed content
    
    # Certificate Information (for qualified signatures)
    certificate_issuer = Column(String(500), nullable=True)
    certificate_serial = Column(String(100), nullable=True)
    certificate_valid_from = Column(DateTime(timezone=True), nullable=True)
    certificate_valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Verification
    verification_method = Column(String(50), nullable=True)  # otp, password, certificate
    verification_data = Column(JSONB, nullable=True)  # Verification details
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    geolocation = Column(JSONB, nullable=True)
    
    # Rejection
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="signatures")
    version = relationship("DocumentVersion")
    signer = relationship("User", foreign_keys=[signer_id])
    
    __table_args__ = (
        Index('idx_signature_document_status', 'document_id', 'status'),
        Index('idx_signature_signer_status', 'signer_id', 'status'),
    )


class DocumentComment(BaseModel):
    """
    Comments and annotations on documents
    Collaboration and feedback mechanism
    """
    __tablename__ = "dms_document_comments"
    
    # Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("dms_document_versions.id"), nullable=True)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("dms_document_comments.id"), nullable=True)
    
    # Comment Content
    comment_text = Column(Text, nullable=False)
    comment_type = Column(String(50), default="general", nullable=False)  # general, question, issue, suggestion
    
    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Location (for annotations)
    page_number = Column(Integer, nullable=True)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Attachments
    attachments = Column(JSONB, nullable=True, default=list)
    
    # Relationships
    document = relationship("Document", back_populates="comments")
    version = relationship("DocumentVersion")
    author = relationship("User", foreign_keys=[author_id])
    resolver = relationship("User", foreign_keys=[resolved_by])
    # Self-referential relationship for nested comments
    replies = relationship("DocumentComment", 
                          foreign_keys=[parent_comment_id],
                          remote_side="DocumentComment.id",
                          backref="parent_comment")
    
    __table_args__ = (
        Index('idx_comment_document_author', 'document_id', 'author_id'),
    )


class DocumentAuditLog(BaseModel):
    """
    Comprehensive audit trail for all document operations
    """
    __tablename__ = "dms_document_audit_logs"
    
    # Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("dms_documents.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("dms_document_versions.id"), nullable=True)
    
    # Action
    action = Column(String(100), nullable=False, index=True)  # created, updated, viewed, downloaded, etc.
    action_category = Column(String(50), nullable=False, index=True)  # access, modification, workflow, security
    description = Column(Text, nullable=True)
    
    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    user_name = Column(String(200), nullable=True)
    user_email = Column(String(200), nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Changes (for modification actions)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    
    # Additional Data
    additional_data = Column(JSONB, nullable=True)  # Additional context (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    document = relationship("Document")
    version = relationship("DocumentVersion")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_audit_document_action', 'document_id', 'action'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )


# Import func for server_default
from sqlalchemy import func
