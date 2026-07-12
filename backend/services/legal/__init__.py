"""
Legal Services Module
Handles contract management, lifecycle tracking, renewals, and version control
"""

from .contract_service import ContractService
from .schemas import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractVersionResponse,
    ContractRenewalCreate,
    ContractRenewalResponse,
    ContractDocumentCreate,
    ContractDocumentResponse,
    ContractPartyCreate,
    ContractPartyResponse,
)

__all__ = [
    "ContractService",
    "ContractCreate",
    "ContractUpdate",
    "ContractResponse",
    "ContractListResponse",
    "ContractVersionResponse",
    "ContractRenewalCreate",
    "ContractRenewalResponse",
    "ContractDocumentCreate",
    "ContractDocumentResponse",
    "ContractPartyCreate",
    "ContractPartyResponse",
]
