"""Shared schemas module"""

from backend.shared.schemas.base import (
    BaseSchema,
    TimestampSchema,
    TenantSchema,
    BaseDBSchema,
    SuccessResponse,
    ErrorDetail,
    ErrorResponse,
    PaginationMeta,
    PaginatedResponse,
    TenantCreate,
    TenantResponse,
    HealthCheck
)

__all__ = [
    "BaseSchema",
    "TimestampSchema",
    "TenantSchema",
    "BaseDBSchema",
    "SuccessResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PaginationMeta",
    "PaginatedResponse",
    "TenantCreate",
    "TenantResponse",
    "HealthCheck"
]
