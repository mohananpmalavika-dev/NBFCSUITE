"""Customer Management Service Package"""

from .router import router as customer_router
from .service import CustomerService
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListItem, PaginatedCustomerResponse
)

__all__ = [
    "customer_router",
    "CustomerService",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListItem",
    "PaginatedCustomerResponse",
]
