"""
Property & Rent Management Service

Comprehensive property management module including:
- Property Master Management
- Lease Tracking & Management
- Rent Collection & Payment Tracking
- Utility Bill Management
- Space Allocation & Occupancy
- Property Maintenance Tracking
"""

from .property_router import router as property_router
from .lease_router import router as lease_router
from .rent_router import router as rent_router
from .utility_router import router as utility_router
from .space_router import router as space_router
from .maintenance_router import router as maintenance_router

__all__ = [
    'property_router',
    'lease_router',
    'rent_router',
    'utility_router',
    'space_router',
    'maintenance_router',
]
