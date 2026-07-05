"""
Deposit Management Service Module

This module provides comprehensive deposit management functionality for NBFCs and Nidhi companies.

Services:
- Product Service: Deposit product management and calculations
- Account Service: Account opening, deposits, withdrawals
- Interest Service: Interest calculation and posting
- Transaction Service: Transaction management

All services follow multi-tenant architecture with complete audit trails.
"""

from .product_service import DepositProductService
from .account_service import DepositAccountService
from .interest_service import InterestCalculationService

__all__ = [
    "DepositProductService",
    "DepositAccountService",
    "InterestCalculationService",
]
