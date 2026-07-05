"""
Deposit Management Service Module

This module provides comprehensive deposit management functionality for NBFCs and Nidhi companies.

Services:
- Product Service: Deposit product management and calculations
- Account Service: Account opening, deposits, withdrawals
- Interest Service: Interest calculation and posting

Routers:
- Product Router: 13 API endpoints for product management
- Account Router: 18 API endpoints for account operations
- Interest Router: 15 API endpoints for interest management

All services follow multi-tenant architecture with complete audit trails.
"""

from .product_service import DepositProductService
from .account_service import DepositAccountService
from .interest_service import InterestCalculationService
from .product_router import router as product_router
from .account_router import router as account_router
from .interest_router import router as interest_router

__all__ = [
    "DepositProductService",
    "DepositAccountService",
    "InterestCalculationService",
    "product_router",
    "account_router",
    "interest_router",
]
