"""
HRMS Schemas Package
Contains all Pydantic schemas for HRMS module
"""

from backend.services.hrms.schemas.exit_schemas import *
from backend.services.hrms.schemas.performance_schemas import *

__all__ = [
    # Exit schemas
    "ExitRequestCreate",
    "ExitRequestUpdate",
    "ExitRequestResponse",
    # Performance schemas
    "PerformanceReviewCreate",
    "PerformanceReviewUpdate",
    "PerformanceReviewResponse",
]
