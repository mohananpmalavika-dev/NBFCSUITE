"""
Reporting & Analytics Service
Comprehensive reporting infrastructure with 100+ pre-built reports
"""

from .template_router import router as template_router
from .generation_router import router as generation_router
from .dashboard_router import router as dashboard_router
from .analytics_router import router as analytics_router
from .builder_router import router as builder_router

__all__ = [
    "template_router",
    "generation_router", 
    "dashboard_router",
    "analytics_router",
    "builder_router"
]
