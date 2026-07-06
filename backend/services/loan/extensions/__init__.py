"""
Loan Extensions Module
Product-specific loan extensions (Vehicle, Property/LAP)
"""

from backend.services.loan.extensions.vehicle_loan_router import router as vehicle_loan_router
from backend.services.loan.extensions.property_loan_router import router as property_loan_router

__all__ = ["vehicle_loan_router", "property_loan_router"]
