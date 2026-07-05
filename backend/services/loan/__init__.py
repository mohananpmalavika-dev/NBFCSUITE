"""
Loan Management Service
Complete loan lifecycle management
"""

from fastapi import APIRouter
from .product_router import router as product_router
from .application_router import router as application_router
from .approval_router import router as approval_router
from .disbursement_router import router as disbursement_router
from .repayment_router import router as repayment_router
from .collection_router import router as collection_router

# Main loan router
router = APIRouter(prefix="/loans", tags=["Loans"])

# Include sub-routers
router.include_router(product_router)
router.include_router(application_router)
router.include_router(approval_router)
router.include_router(disbursement_router)
router.include_router(repayment_router)
router.include_router(collection_router)

__all__ = ["router"]
