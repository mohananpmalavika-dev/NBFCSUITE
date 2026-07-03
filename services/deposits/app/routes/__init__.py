"""
API Routes Package
"""

from .products import router as products_router
from .accounts import router as accounts_router
from .rd import router as rd_router
from .interest import router as interest_router
from .maturity import router as maturity_router
from .premature_closure import router as premature_closure_router
from .ai_intelligence import router as ai_router
from .dashboard import router as dashboard_router

__all__ = [
    "products_router",
    "accounts_router",
    "rd_router",
    "interest_router",
    "maturity_router",
    "premature_closure_router",
    "ai_router",
    "dashboard_router"
]
