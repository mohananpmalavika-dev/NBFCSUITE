"""
Facility & Administration Management Services
"""

from .building_router import router as building_router
from .housekeeping_router import router as housekeeping_router
from .cafeteria_router import router as cafeteria_router
from .transport_router import router as transport_router
from .visitor_router import router as visitor_router

__all__ = [
    "building_router",
    "housekeeping_router",
    "cafeteria_router",
    "transport_router",
    "visitor_router"
]
