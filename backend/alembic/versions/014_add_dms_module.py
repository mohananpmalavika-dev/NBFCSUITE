"""add document management system (dms) module

Revision ID: 014_add_dms_module
Revises: 013_add_procurement_module
Create Date: 2026-07-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '014_add_dms_module'
down_revision = '013_add_procurement_module'
branch_labels = None
depends_on = None


def upgrade():
    # ========================================================================
    # DOCUMENTS TABLE
    # Main document entity with metadata and version control
    # ========================================================================
    op.create_table(
        'dms_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Basic Information
        sa.Column('document_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False, index=True),
        sa.Column('description', sa.Text),
        
        # Classification
        sa.Column('document_type', sa.String(50), nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('access_level', sa.String(50), nullable=False, default='internal', index=True),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, default='draft', index=True),
        
        # Version Control
        sa.Column('current_version_id', postgresql.UUID(as_uuid=True)),
        sa.Column('version_number', sa.Integer, default=1, nullable=False),
        
        # File Information
        sa.Column('file_name', sa.String(500)),
        sa.Column('file_type', sa.String(100)),
        sa.Column('file_size', sa.BigInteger),
        sa.Column('file_path', sa.String(1000)),
        sa.Column('file_hash', sa.String(256)),
        
        # Ownership
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('department', sa.String(100), index=True),
        
        # Metadata
        sa.Column('tags', postgresql.JSONB),
        sa.Column('custom_fields', postgresql.JSONB),
        
        # Dates
        sa.Column('effective_date', sa.DateTime(timezone=True)),
        sa.Column('expiry_date', sa.DateTime(timezone=True), index=True),
        sa.Column('review_date', sa.DateTime(timezone=True), index=True),
        
        # References
        sa.Column('parent_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), index=True),
        sa.Column('reference_number', sa.String(100)),
        
        # Security
        sa.Column('is_encrypted', sa.Boolean, default=False, nullable=False),
        sa.Column('encryption_key_id', sa.String(100)),
        sa.Column('is_locked', sa.Boolean, default=False, nullable=False),
        sa.Column('locked_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('locked_at', sa.DateTime(timezone=True)),
        
        # Statistics
        sa.Column('download_count', sa.Integer, default=0, nullable=False),
        sa.Column('view_count', sa.Integer, default=0, nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True)),
        sa.Column('last_accessed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_document_status_type', 'dms_documents', ['status', 'document_type'])
    op.create_index('idx_document_owner_status', 'dms_documents', ['owner_id', 'status'])
    op.create_index('idx_document_expiry', 'dms_documents', ['expiry_date', 'status'])
    
    # ========================================================================
    # DOCUMENT VERSIONS TABLE
    # Maintains complete version history
    # ========================================================================
    op.create_table(
        'dms_document_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), nullable=False, index=True),
        sa.Column('version_number', sa.Integer, nullable=False),
        
        # File Information
        sa.Column('file_name', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(100), nullable=False),
        sa.Column('file_size', sa.BigInteger, nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('file_hash', sa.String(256), nullable=False),
        
        # Version Metadata
        sa.Column('version_notes', sa.Text),
        sa.Column('is_major_version', sa.Boolean, default=False, nullable=False),
        
        # Changes
        sa.Column('changes_summary', sa.Text),
        sa.Column('diff_from_previous', postgresql.JSONB),
        
        # Security
        sa.Column('is_encrypted', sa.Boolean, default=False, nullable=False),
        sa.Column('encryption_key_id', sa.String(100)),
        
        # Upload Information
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('upload_ip', sa.String(45)),
        sa.Column('upload_user_agent', sa.String(500)),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_version_document', 'dms_document_versions', ['document_id', 'version_number'])
    op.create_index('idx_unique_document_version', 'dms_document_versions', ['document_id', 'version_number'], unique=True)
    
    # Add foreign key constraint from documents to current version
    op.create_foreign_key(
        'fk_documents_current_version',
        'dms_documents', 'dms_document_versions',
        ['current_version_id'], ['id']
    )
    
    # ========================================================================
    # WORKFLOW TEMPLATES TABLE
    # Reusable workflow templates
    # ========================================================================
    op.create_table(
        'dms_workflow_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Basic Information
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('workflow_type', sa.String(50), nullable=False, index=True),
        
        # Applicability
        sa.Column('applicable_document_types', postgresql.JSONB),
        sa.Column('applicable_categories', postgresql.JSONB),
        
        # Configuration
        sa.Column('steps', postgresql.JSONB, nullable=False),
        sa.Column('is_sequential', sa.Boolean, default=True, nullable=False),
        sa.Column('require_all_approvals', sa.Boolean, default=True, nullable=False),
        
        # Status
        sa.Column('is_active', sa.Boolean, default=True, nullable=False, index=True),
        
        # Usage Statistics
        sa.Column('usage_count', sa.Integer, default=0, nullable=False),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    # ========================================================================
    # DOCUMENT WORKFLOWS TABLE
    # Workflow instances for documents
    # ========================================================================
    op.create_table(
        'dms_document_workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), nullable=False, index=True),
        sa.Column('workflow_template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_workflow_templates.id')),
        
        # Workflow Information
        sa.Column('workflow_name', sa.String(200), nullable=False),
        sa.Column('workflow_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        sa.Column('current_step', sa.Integer, default=1, nullable=False),
        sa.Column('total_steps', sa.Integer, nullable=False),
        
        # Initiator
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # Completion
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        
        # Metadata
        sa.Column('priority', sa.String(20), default='normal', nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), index=True),
        
        # Configuration
        sa.Column('is_sequential', sa.Boolean, default=True, nullable=False),
        sa.Column('require_all_approvals', sa.Boolean, default=True, nullable=False),
        sa.Column('auto_approve_on_timeout', sa.Boolean, default=False, nullable=False),
        
        # Notes
        sa.Column('notes', sa.Text),
        sa.Column('cancellation_reason', sa.Text),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_workflow_status_due', 'dms_document_workflows', ['status', 'due_date'])
    
    # ========================================================================
    # DOCUMENT APPROVALS TABLE
    # Individual approval steps
    # ========================================================================
    op.create_table(
        'dms_document_approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_document_workflows.id'), nullable=False, index=True),
        
        # Step Information
        sa.Column('step_number', sa.Integer, nullable=False),
        sa.Column('step_name', sa.String(200), nullable=False),
        
        # Approver
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('approver_role', sa.String(100)),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        
        # Delegation
        sa.Column('delegated_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('delegated_at', sa.DateTime(timezone=True)),
        sa.Column('delegation_reason', sa.Text),
        
        # Response
        sa.Column('response_date', sa.DateTime(timezone=True)),
        sa.Column('comments', sa.Text),
        sa.Column('attachments', postgresql.JSONB),
        
        # Timing
        sa.Column('due_date', sa.DateTime(timezone=True)),
        sa.Column('reminded_at', sa.DateTime(timezone=True)),
        sa.Column('reminder_count', sa.Integer, default=0, nullable=False),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_approval_workflow_step', 'dms_document_approvals', ['workflow_id', 'step_number'])
    op.create_index('idx_approval_approver_status', 'dms_document_approvals', ['approver_id', 'status'])
    
    # ========================================================================
    # DOCUMENT PERMISSIONS TABLE
    # Granular access control
    # ========================================================================
    op.create_table(
        'dms_document_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), nullable=False, index=True),
        
        # Subject (User, Role, or Department)
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), index=True),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), index=True),
        sa.Column('department', sa.String(100), index=True),
        
        # Permissions
        sa.Column('can_view', sa.Boolean, default=True, nullable=False),
        sa.Column('can_download', sa.Boolean, default=False, nullable=False),
        sa.Column('can_edit', sa.Boolean, default=False, nullable=False),
        sa.Column('can_delete', sa.Boolean, default=False, nullable=False),
        sa.Column('can_share', sa.Boolean, default=False, nullable=False),
        sa.Column('can_approve', sa.Boolean, default=False, nullable=False),
        
        # Validity
        sa.Column('valid_from', sa.DateTime(timezone=True)),
        sa.Column('valid_until', sa.DateTime(timezone=True), index=True),
        
        # Grant Information
        sa.Column('granted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('grant_reason', sa.Text),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_permission_document_user', 'dms_document_permissions', ['document_id', 'user_id'])
    op.create_index('idx_permission_document_role', 'dms_document_permissions', ['document_id', 'role_id'])
    
    # ========================================================================
    # DOCUMENT SIGNATURES TABLE
    # E-signature capability
    # ========================================================================
    op.create_table(
        'dms_document_signatures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), nullable=False, index=True),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_document_versions.id'), nullable=False),
        
        # Signer
        sa.Column('signer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('signer_name', sa.String(200), nullable=False),
        sa.Column('signer_email', sa.String(200), nullable=False),
        sa.Column('signer_title', sa.String(200)),
        
        # Signature Information
        sa.Column('signature_type', sa.String(50), nullable=False, default='simple'),
        sa.Column('status', sa.String(50), nullable=False, default='pending', index=True),
        
        # Signature Data
        sa.Column('signature_image_path', sa.String(1000)),
        sa.Column('signature_data', sa.Text),
        sa.Column('signature_hash', sa.String(256)),
        
        # Certificate Information
        sa.Column('certificate_issuer', sa.String(500)),
        sa.Column('certificate_serial', sa.String(100)),
        sa.Column('certificate_valid_from', sa.DateTime(timezone=True)),
        sa.Column('certificate_valid_until', sa.DateTime(timezone=True)),
        
        # Verification
        sa.Column('verification_method', sa.String(50)),
        sa.Column('verification_data', postgresql.JSONB),
        
        # Timestamps
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('signed_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True), index=True),
        
        # Context
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('geolocation', postgresql.JSONB),
        
        # Rejection
        sa.Column('rejection_reason', sa.Text),
        sa.Column('rejected_at', sa.DateTime(timezone=True)),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_signature_document_status', 'dms_document_signatures', ['document_id', 'status'])
    op.create_index('idx_signature_signer_status', 'dms_document_signatures', ['signer_id', 'status'])
    
    # ========================================================================
    # DOCUMENT COMMENTS TABLE
    # Comments and annotations
    # ========================================================================
    op.create_table(
        'dms_document_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), nullable=False, index=True),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_document_versions.id')),
        sa.Column('parent_comment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_document_comments.id')),
        
        # Comment Content
        sa.Column('comment_text', sa.Text, nullable=False),
        sa.Column('comment_type', sa.String(50), default='general', nullable=False),
        
        # Author
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        
        # Location (for annotations)
        sa.Column('page_number', sa.Integer),
        sa.Column('position_x', sa.Integer),
        sa.Column('position_y', sa.Integer),
        
        # Status
        sa.Column('is_resolved', sa.Boolean, default=False, nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True)),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        
        # Attachments
        sa.Column('attachments', postgresql.JSONB),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True))
    )
    
    op.create_index('idx_comment_document_author', 'dms_document_comments', ['document_id', 'author_id'])
    
    # ========================================================================
    # DOCUMENT AUDIT LOG TABLE
    # Comprehensive audit trail
    # ========================================================================
    op.create_table(
        'dms_document_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        
        # Reference
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_documents.id'), nullable=False, index=True),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('dms_document_versions.id')),
        
        # Action
        sa.Column('action', sa.String(100), nullable=False, index=True),
        sa.Column('action_category', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.Text),
        
        # Actor
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), index=True),
        sa.Column('user_name', sa.String(200)),
        sa.Column('user_email', sa.String(200)),
        
        # Context
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        
        # Changes
        sa.Column('old_values', postgresql.JSONB),
        sa.Column('new_values', postgresql.JSONB),
        
        # Metadata
        sa.Column('metadata', postgresql.JSONB),
        
        # Timestamp
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        
        # Audit fields (minimal for audit log)
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False)
    )
    
    op.create_index('idx_audit_document_action', 'dms_document_audit_logs', ['document_id', 'action'])
    op.create_index('idx_audit_user_timestamp', 'dms_document_audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_action_timestamp', 'dms_document_audit_logs', ['action', 'timestamp'])
    
    print("✅ DMS Module tables created successfully!")


def downgrade():
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('dms_document_audit_logs')
    op.drop_table('dms_document_comments')
    op.drop_table('dms_document_signatures')
    op.drop_table('dms_document_permissions')
    op.drop_table('dms_document_approvals')
    op.drop_table('dms_document_workflows')
    op.drop_table('dms_workflow_templates')
    
    # Drop foreign key constraint before dropping version table
    op.drop_constraint('fk_documents_current_version', 'dms_documents', type_='foreignkey')
    
    op.drop_table('dms_document_versions')
    op.drop_table('dms_documents')
    
    print("✅ DMS Module tables dropped successfully!")
