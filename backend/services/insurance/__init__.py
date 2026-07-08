"""
Insurance & Bancassurance Module

Comprehensive insurance management system including:
- Policy management
- Premium collection
- Claims processing
- Commission tracking
"""

from backend.services.insurance import models, schemas
from backend.services.insurance.policy_service import PolicyService
from backend.services.insurance.policy_router import router as policy_router
from backend.services.insurance.premium_service import PremiumService
from backend.services.insurance.premium_router import router as premium_router
from backend.services.insurance.claim_service import ClaimService
from backend.services.insurance.claim_router import router as claim_router
from backend.services.insurance.commission_service import CommissionService
from backend.services.insurance.commission_router import router as commission_router

__all__ = [
    "models",
    "schemas",
    "PolicyService",
    "policy_router",
    "PremiumService",
    "premium_router",
    "ClaimService",
    "claim_router",
    "CommissionService",
    "commission_router",
]
