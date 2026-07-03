"""
Document Management Models
Phase 10: Document Management
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Date, Text, 
    DECIMAL, BigInteger, ARRAY, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class DocumentCategory(Base):
    """Document categories and classification hierarchy"""
    __tablename__ = "gold_document_categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_code = Column(String(50), nullable=False, unique=True, index=True)
    category_name = Column(String(200), nullable=False)
    description = Column(Text)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_categories.category_id'))
    category_level = Column(Integer, nullable=False, default=1)
    is_system_category = Column(Boolean, nullable=False, default=False)
    retention_period_days = Column(Integer)
    is_mandatory = Column(Boolean, nullable=False, default=False)
    allowed_extensions = Column(ARRAY(Text))
    max_file_size_mb = Column(DECIMAL(10, 2))
    requires_approval = Column(Boolean, nullable=False, default=False)
    requires_ocr = Column(Boolean, nullable=False, default=False)
    metadata_schema = Column(JSONB)
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="category")
    templates = relationship("DocumentTemplate", back_populates="category")
    workflows = relationship("DocumentWorkflow", back_populates="category")
    retention_policies = relationship("DocumentRetentionPolicy", back_populates="category")
    parent = relationship("DocumentCategory", remote_side=[category_id], backref="children")


class Document(Base):
    """Core documents table with metadata and storage information"""
    __tablename__ = "gold_documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_number = Column(String(50), nullable=False, unique=True, index=True)
    document_name = Column(String(300), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_categories.category_id'), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    
    # File information
    file_name = Column(String(300), nullable=False)
    file_extension = Column(String(20), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_path = Column(Text, nullable=False)
    storage_provider = Column(String(50), nullable=False, default='s3')
    checksum = Column(String(64), nullable=False)
    current_version = Column(Integer, nullable=False, default=1)
    
    # Encryption
    is_encrypted = Column(Boolean, nullable=False, default=True)
    encryption_key_id = Column(String(100))
    
    # OCR
    ocr_status = Column(String(20), nullable=False, default='pending', index=True)
    ocr_text = Column(Text)
    ocr_confidence = Column(DECIMAL(5, 2))
    ocr_processed_at = Column(DateTime(timezone=True))
    
    # Signature
    is_signed = Column(Boolean, nullable=False, default=False)
    signature_status = Column(String(20), index=True)
    signed_by = Column(UUID(as_uuid=True))
    signed_at = Column(DateTime(timezone=True))
    signature_certificate = Column(Text)
    
    # Access and retention
    access_level = Column(String(20), nullable=False, default='internal')
    retention_until = Column(Date, index=True)
    
    # Archive and deletion
    is_archived = Column(Boolean, nullable=False, default=False, index=True)
    archived_at = Column(DateTime(timezone=True))
    archived_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(UUID(as_uuid=True))
    
    # Additional metadata
    tags = Column(ARRAY(Text))
    metadata = Column(JSONB)
    remarks = Column(Text)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("DocumentCategory", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    metadata_entries = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")
    approvals = relationship("DocumentApproval", back_populates="document", cascade="all, delete-orphan")
    access_logs = relationship("DocumentAccessLog", back_populates="document", cascade="all, delete-orphan")
    shares = relationship("DocumentShare", back_populates="document", cascade="all, delete-orphan")
    tag_mappings = relationship("DocumentTagMapping", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_documents_entity', 'entity_type', 'entity_id'),
    )


class DocumentVersion(Base):
    """Document version history and change tracking"""
    __tablename__ = "gold_document_versions"

    version_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('gold_documents.document_id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    file_name = Column(String(300), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    storage_path = Column(Text, nullable=False)
    checksum = Column(String(64), nullable=False)
    change_description = Column(Text)
    version_type = Column(String(20), nullable=False, default='minor')
    is_current = Column(Boolean, nullable=False, default=False)
    replaced_version_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_versions.version_id'))
    ocr_text = Column(Text)
    ocr_confidence = Column(DECIMAL(5, 2))
    metadata = Column(JSONB)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    document = relationship("Document", back_populates="versions")

    __table_args__ = (
        Index('idx_doc_versions_current', 'document_id', 'is_current'),
    )


class DocumentMetadata(Base):
    """Flexible document metadata storage"""
    __tablename__ = "gold_document_metadata"

    metadata_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('gold_documents.document_id'), nullable=False, index=True)
    metadata_key = Column(String(100), nullable=False, index=True)
    metadata_value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False)
    is_indexed = Column(Boolean, nullable=False, default=False)
    is_searchable = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="metadata_entries")

    __table_args__ = (
        Index('idx_doc_metadata_searchable', 'metadata_key', 'metadata_value'),
    )


class DocumentTemplate(Base):
    """Document templates for generation"""
    __tablename__ = "gold_document_templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_code = Column(String(50), nullable=False, unique=True, index=True)
    template_name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_categories.category_id'), nullable=False, index=True)
    template_type = Column(String(50), nullable=False, index=True)
    file_format = Column(String(20), nullable=False)
    storage_path = Column(Text, nullable=False)
    template_variables = Column(JSONB)
    merge_rules = Column(JSONB)
    is_system_template = Column(Boolean, nullable=False, default=False)
    version = Column(String(20), nullable=False, default='1.0')
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    usage_count = Column(Integer, nullable=False, default=0)
    last_used_at = Column(DateTime(timezone=True))
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("DocumentCategory", back_populates="templates")


class DocumentWorkflow(Base):
    """Document approval and review workflows"""
    __tablename__ = "gold_document_workflows"

    workflow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_code = Column(String(50), nullable=False, unique=True, index=True)
    workflow_name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_categories.category_id'), index=True)
    workflow_type = Column(String(50), nullable=False, index=True)
    workflow_steps = Column(JSONB, nullable=False)
    trigger_conditions = Column(JSONB)
    escalation_rules = Column(JSONB)
    sla_hours = Column(Integer)
    is_mandatory = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("DocumentCategory", back_populates="workflows")
    approvals = relationship("DocumentApproval", back_populates="workflow")


class DocumentApproval(Base):
    """Document approval tracking and status"""
    __tablename__ = "gold_document_approvals"

    approval_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('gold_documents.document_id'), nullable=False, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_workflows.workflow_id'), nullable=False, index=True)
    approval_number = Column(String(50), nullable=False, unique=True, index=True)
    current_step = Column(Integer, nullable=False, default=1)
    total_steps = Column(Integer, nullable=False)
    approval_status = Column(String(20), nullable=False, default='pending', index=True)
    priority = Column(String(20), nullable=False, default='medium')
    initiated_by = Column(UUID(as_uuid=True), nullable=False)
    initiated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_to = Column(UUID(as_uuid=True), index=True)
    assigned_at = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True), index=True)
    completed_at = Column(DateTime(timezone=True))
    approval_steps = Column(JSONB)
    rejection_reason = Column(Text)
    is_escalated = Column(Boolean, nullable=False, default=False, index=True)
    escalated_at = Column(DateTime(timezone=True))
    escalated_to = Column(UUID(as_uuid=True))
    remarks = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="approvals")
    workflow = relationship("DocumentWorkflow", back_populates="approvals")


class DocumentTag(Base):
    """Document tags and labels"""
    __tablename__ = "gold_document_tags"

    tag_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tag_name = Column(String(100), nullable=False, unique=True, index=True)
    tag_category = Column(String(50), index=True)
    tag_color = Column(String(7))
    description = Column(Text)
    usage_count = Column(Integer, nullable=False, default=0)
    is_system_tag = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mappings = relationship("DocumentTagMapping", back_populates="tag", cascade="all, delete-orphan")


class DocumentTagMapping(Base):
    """Document-Tag many-to-many relationship"""
    __tablename__ = "gold_document_tag_mappings"

    mapping_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('gold_documents.document_id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_tags.tag_id', ondelete='CASCADE'), nullable=False, index=True)
    tagged_by = Column(UUID(as_uuid=True), nullable=False)
    tagged_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="tag_mappings")
    tag = relationship("DocumentTag", back_populates="mappings")


class DocumentAccessLog(Base):
    """Document access audit trail"""
    __tablename__ = "gold_document_access_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('gold_documents.document_id'), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_role = Column(String(50))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    access_location = Column(String(100))
    access_device = Column(String(50))
    session_id = Column(String(100))
    access_result = Column(String(20), nullable=False, index=True)
    denial_reason = Column(Text)
    file_version = Column(Integer)
    download_size_bytes = Column(BigInteger)
    access_duration_seconds = Column(Integer)
    metadata = Column(JSONB)
    accessed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    document = relationship("Document", back_populates="access_logs")


class DocumentRetentionPolicy(Base):
    """Document retention and compliance policies"""
    __tablename__ = "gold_document_retention_policies"

    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_code = Column(String(50), nullable=False, unique=True, index=True)
    policy_name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('gold_document_categories.category_id'), index=True)
    document_type = Column(String(50), index=True)
    retention_period_days = Column(Integer, nullable=False)
    retention_trigger = Column(String(50), nullable=False)
    archive_after_days = Column(Integer)
    delete_after_retention = Column(Boolean, nullable=False, default=False)
    requires_legal_hold = Column(Boolean, nullable=False, default=False)
    compliance_regulation = Column(String(100))
    auto_apply = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, index=True)
    affected_documents_count = Column(Integer, nullable=False, default=0)
    last_executed_at = Column(DateTime(timezone=True))
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("DocumentCategory", back_populates="retention_policies")


class DocumentShare(Base):
    """Document sharing and external access control"""
    __tablename__ = "gold_document_shares"

    share_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('gold_documents.document_id'), nullable=False, index=True)
    share_token = Column(String(100), nullable=False, unique=True, index=True)
    share_type = Column(String(20), nullable=False)
    shared_with_user_id = Column(UUID(as_uuid=True), index=True)
    shared_with_email = Column(String(255))
    permissions = Column(JSONB, nullable=False)
    access_count = Column(Integer, nullable=False, default=0)
    max_access_count = Column(Integer)
    expires_at = Column(DateTime(timezone=True))
    is_password_protected = Column(Boolean, nullable=False, default=False)
    password_hash = Column(String(255))
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime(timezone=True))
    revoked_by = Column(UUID(as_uuid=True))
    revocation_reason = Column(Text)
    shared_by = Column(UUID(as_uuid=True), nullable=False)
    shared_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="shares")

    __table_args__ = (
        Index('idx_doc_shares_active', 'is_revoked', 'expires_at'),
    )
