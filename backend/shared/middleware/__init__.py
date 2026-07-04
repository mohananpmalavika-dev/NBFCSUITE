"""Middleware module"""

from shared.middleware.tenant import TenantMiddleware, get_tenant_id
from shared.middleware.logging import LoggingMiddleware
from shared.middleware.error_handler import (
    ErrorHandlerMiddleware,
    APIError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
    ConflictError
)

__all__ = [
    "TenantMiddleware",
    "get_tenant_id",
    "LoggingMiddleware",
    "ErrorHandlerMiddleware",
    "APIError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ValidationError",
    "ConflictError"
]
