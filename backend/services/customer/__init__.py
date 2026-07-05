"""Customer Management Service Package"""

from .router import router as customer_router
from .family_router import router as family_router
from .document_router import router as document_router
from .bank_account_router import router as bank_account_router

from .service import CustomerService
from .family_service import CustomerFamilyService
from .document_service import CustomerDocumentService
from .bank_account_service import CustomerBankAccountService

from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListItem, PaginatedCustomerResponse,
    CustomerFamilyCreate, CustomerFamilyResponse,
    CustomerDocumentCreate, CustomerDocumentResponse,
    CustomerBankAccountCreate, CustomerBankAccountResponse
)

__all__ = [
    "customer_router",
    "family_router",
    "document_router",
    "bank_account_router",
    "CustomerService",
    "CustomerFamilyService",
    "CustomerDocumentService",
    "CustomerBankAccountService",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerListItem",
    "PaginatedCustomerResponse",
    "CustomerFamilyCreate",
    "CustomerFamilyResponse",
    "CustomerDocumentCreate",
    "CustomerDocumentResponse",
    "CustomerBankAccountCreate",
    "CustomerBankAccountResponse",
]
