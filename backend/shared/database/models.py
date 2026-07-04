"""
Base Database Models
Includes multi-tenant support and common fields
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from shared.database.connection import Base


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
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
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
