"""
Locker Management Service

Provides comprehensive locker management functionality for financial institutions including:
- Locker inventory management
- Customer allocation and agreements
- Rent collection and tracking
- Maintenance scheduling
- Access logging and audit trail
"""

from .router import router

__all__ = ["router"]
