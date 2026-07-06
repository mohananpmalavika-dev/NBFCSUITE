"""
Base Database Models
Includes multi-tenant support and common fields
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, func, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from backend.shared.database.connection import Base


class TenantMixin:
    """
    Multi-tenant mixin
    Add tenant_id to enable row-level security
    """
    tenant_id = Column(String(50), nullable=False, index=True, default="default")


class TimestampMixin:
    """
    Timestamp mixin
    Automatically tracks creation and update times
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """
    Soft delete mixin
    Marks records as deleted instead of removing them
    """
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)


class AuditMixin:
    """
    Audit trail mixin
    Tracks who created and updated records
    """
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)


class BaseModel(Base, TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """
    Base model with all common fields
    All application models should inherit from this
    """
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    def dict(self):
        """Convert model to dictionary - only includes column values, not relationships"""
        from sqlalchemy import inspect
        
        # Use the instance mapper to get column values without triggering lazy loads
        mapper = inspect(self.__class__)
        result = {}
        
        for column in mapper.columns:
            # Use __dict__ directly to avoid lazy loading through descriptors
            if column.key in self.__dict__:
                result[column.key] = self.__dict__[column.key]
        
        return result
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class Tenant(Base, TimestampMixin):
    """
    Tenant model
    Represents an organization using the platform
    """
    __tablename__ = "tenants"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    domain = Column(String(100), nullable=True, unique=True)
    
    # Contact information
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Subscription
    subscription_plan = Column(String(50), default="basic")
    subscription_status = Column(String(20), default="active")
    
    # Configuration
    settings = Column(String, nullable=True)  # JSON string
    
    # Limits
    max_users = Column(Integer, default=50)
    max_branches = Column(Integer, default=10)
    max_customers = Column(Integer, default=10000)
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name})>"


class User(BaseModel):
    """
    User model
    Represents a user in the system (employees, admins, etc.)
    """
    __tablename__ = "users"
    
    # Authentication
    email = Column(String(100), nullable=False, index=True)
    username = Column(String(50), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Employee Details
    employee_code = Column(String(50), nullable=True, index=True)
    designation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Session Management
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    must_change_password = Column(Boolean, default=False)
    
    # Preferences
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="Asia/Kolkata")
    
    # Unique constraints per tenant
    __table_args__ = (
        # Email unique per tenant
        Index('idx_tenant_email', 'tenant_id', 'email', unique=True),
        # Username unique per tenant
        Index('idx_tenant_username', 'tenant_id', 'username', unique=True),
        # Employee code unique per tenant
        Index('idx_tenant_employee_code', 'tenant_id', 'employee_code', unique=True),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Role(BaseModel):
    """
    Role model
    Represents a role that can be assigned to users
    """
    __tablename__ = "roles"
    
    name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Role Type
    role_type = Column(String(50), default="custom")  # system, custom
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Unique constraint: role name per tenant
    __table_args__ = (
        Index('idx_tenant_role_name', 'tenant_id', 'name', unique=True),
    )
    
    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(BaseModel):
    """
    Permission model
    Represents a specific permission in the system
    """
    __tablename__ = "permissions"
    
    resource = Column(String(100), nullable=False)  # e.g., 'customers', 'loans'
    action = Column(String(50), nullable=False)  # e.g., 'create', 'read', 'update', 'delete'
    description = Column(String(500), nullable=True)
    
    # Permission Type
    permission_type = Column(String(50), default="entity")  # entity, function, report
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Unique constraint: resource + action per tenant
    __table_args__ = (
        Index('idx_tenant_resource_action', 'tenant_id', 'resource', 'action', unique=True),
    )
    
    def __repr__(self):
        return f"<Permission(id={self.id}, resource={self.resource}, action={self.action})>"


class UserRole(BaseModel):
    """
    UserRole model
    Many-to-many relationship between users and roles
    """
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Assignment details
    assigned_by = Column(UUID(as_uuid=True), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Expiry (optional)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Unique constraint: user + role per tenant
    __table_args__ = (
        Index('idx_tenant_user_role', 'tenant_id', 'user_id', 'role_id', unique=True),
    )
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class RolePermission(BaseModel):
    """
    RolePermission model
    Many-to-many relationship between roles and permissions
    """
    __tablename__ = "role_permissions"
    
    role_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    permission_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Assignment details
    assigned_by = Column(UUID(as_uuid=True), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint: role + permission per tenant
    __table_args__ = (
        Index('idx_tenant_role_permission', 'tenant_id', 'role_id', 'permission_id', unique=True),
    )
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


class FileUpload(Base, TenantMixin, TimestampMixin):
    """
    FileUpload model
    Stores metadata for uploaded files
    """
    __tablename__ = "file_uploads"
    
    id = Column(String(50), primary_key=True, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)  # Unique filename (stored)
    original_filename = Column(String(255), nullable=False)  # Original filename
    file_path = Column(String(500), nullable=False)  # Full file path
    file_size = Column(Integer, nullable=False)  # File size in bytes
    mime_type = Column(String(100), nullable=False)  # MIME type
    
    # Document metadata
    document_type = Column(String(100), nullable=False, index=True)  # Type of document
    document_number = Column(String(100), nullable=True)  # Document reference number
    
    # Entity relationship
    entity_type = Column(String(50), nullable=True, index=True)  # customer, loan, deposit, etc.
    entity_id = Column(String(50), nullable=True, index=True)  # ID of related entity
    
    # Upload information
    uploaded_by = Column(String(50), nullable=False)  # User ID who uploaded
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Additional info
    remarks = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_file_entity', 'tenant_id', 'entity_type', 'entity_id'),
        Index('idx_file_uploaded_by', 'tenant_id', 'uploaded_by'),
        Index('idx_file_document_type', 'tenant_id', 'document_type'),
    )
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename={self.filename}, document_type={self.document_type})>"
