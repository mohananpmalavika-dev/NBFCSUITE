"""
CRM Lead Management Module
Complete lead lifecycle management with multi-channel capture, scoring, and routing
"""

from .router import router
from .service import CRMLeadService
from .schemas import (
    LeadCreate, LeadUpdate, LeadResponse,
    LeadFollowUpCreate, LeadFollowUpResponse,
    LeadDashboardStats
)

__all__ = [
    "router",
    "CRMLeadService",
    "LeadCreate",
    "LeadUpdate",
    "LeadResponse",
    "LeadFollowUpCreate",
    "LeadFollowUpResponse",
    "LeadDashboardStats"
]
