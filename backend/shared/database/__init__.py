"""Database module"""

from backend.shared.database.connection import engine, Base, get_db, AsyncSessionLocal
from backend.shared.database.models import BaseModel, Tenant, TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin

# NOTE: Model imports are now handled conditionally in conditional_imports.py
# This prevents unconditional loading of disabled modules

__all__ = [
    "engine",
    "Base",
    "get_db",
    "AsyncSessionLocal",
    "BaseModel",
    "Tenant",
    "TenantMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin"
]
