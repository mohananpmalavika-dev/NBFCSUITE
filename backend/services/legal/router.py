"""
Legal Contract Management - API Router
REST API endpoints for contract management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.database.models import User
from .contract_service import ContractService
from .schemas import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractVersionCreate,
    ContractVersionResponse,
    ContractRenewalCreate,
    ContractRenewalUpdate,
    ContractRenewalResponse,
    ContractDocumentCreate,
    ContractDocumentResponse,
    ContractPartyCreate,
    ContractPartyUpdate,
    ContractPartyResponse,
    ContractFilterParams,
    ContractStatistics,
)
from backend.shared.database.legal_models import ContractType, ContractStatus, RenewalStatus


router = APIRouter(prefix="/api/v1/legal/contracts", tags=["Legal - Contract Management"])


def map_contract_to_response(contract) -> ContractResponse:
    """Map contract model to response schema with computed fields"""
    response = ContractResponse.from_orm(contract)
    
    # Calculate days until expiry
    if contract.expiry_date:
        delta = (contract.expiry_date - date.today()).days
        response.days_until_expiry = delta
        response.is_expiring_soon = 0 <= delta <= contract.alert_before_expiry_days
        response.is_expired = delta < 0
    
    return response


# ============================================
# CONTRACT CRUD ENDPOINTS
# ============================================

@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a new contract
    
    - **title**: Contract title (required)
    - **contract_type**: Type of contract (vendor, customer, employee, etc.)
    - **effective_date**: Contract start date
    - **expiry_date**: Contract end date (optional)
    - **contract_value**: Monetary value of contract
    - **is_renewable**: Whether contract can be renewed
    - **auto_renewal**: Automatic renewal flag
    """
    contract = await ContractService.create_contract(
        db=db,
        contract_data=contract_data,
        tenant_id=tenant_id,
        user_id=current_user.id
    )
    return map_contract_to_response(contract)


@router.get("", response_model=ContractListResponse)
async def list_contracts(
    contract_type: Optional[ContractType] = None,
    status: Optional[ContractStatus] = None,
    renewal_status: Optional[RenewalStatus] = None,
    is_renewable: Optional[bool] = None,
    expiring_in_days: Optional[int] = None,
    effective_date_from: Optional[date] = None,
    effective_date_to: Optional[date] = None,
    expiry_date_from: Optional[date] = None,
    expiry_date_to: Optional[date] = None,
    search_query: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List contracts with filtering, search, and pagination
    
    - **contract_type**: Filter by contract type
    - **status**: Filter by contract status
    - **renewal_status**: Filter by renewal status
    - **expiring_in_days**: Get contracts expiring within N days
    - **search_query**: Search in contract number, title, description
    """
    filters = ContractFilterParams(
        contract_type=contract_type,
        status=status,
        renewal_status=renewal_status,
        is_renewable=is_renewable,
        expiring_in_days=expiring_in_days,
        effective_date_from=effective_date_from,
        effective_date_to=effective_date_to,
        expiry_date_from=expiry_date_from,
        expiry_date_to=expiry_date_to,
        search_query=search_query,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    contracts, total = await ContractService.list_contracts(
        db=db,
        tenant_id=tenant_id,
        filters=filters
    )
    
    items = [map_contract_to_response(contract) for contract in contracts]
    total_pages = (total + page_size - 1) // page_size
    
    return ContractListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/statistics", response_model=ContractStatistics)
async def get_contract_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get contract statistics and analytics
    
    Returns:
    - Total contracts count
    - Active/expired/expiring soon counts
    - Pending renewals
    - Total contract value
    - Contracts by type and status
    """
    stats = await ContractService.get_contract_statistics(db=db, tenant_id=tenant_id)
    return stats


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get contract by ID with all related data
    
    Returns:
    - Contract details
    - All versions
    - Renewal history
    - Associated documents
    - Contract parties
    """
    contract = await ContractService.get_contract(
        db=db,
        contract_id=contract_id,
        tenant_id=tenant_id
    )
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return map_contract_to_response(contract)


@router.patch("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: UUID,
    contract_data: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Update contract
    
    - Updating critical fields (title, value, dates, document) creates a new version
    - All changes are tracked in version history
    """
    contract = await ContractService.update_contract(
        db=db,
        contract_id=contract_id,
        tenant_id=tenant_id,
        contract_data=contract_data,
        user_id=current_user.id
    )
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return map_contract_to_response(contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete contract (soft delete)
    
    - Contract is marked as deleted but not removed from database
    - All related data remains intact for audit purposes
    """
    success = await ContractService.delete_contract(
        db=db,
        contract_id=contract_id,
        tenant_id=tenant_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )


# ============================================
# CONTRACT PARTY ENDPOINTS
# ============================================

@router.post("/{contract_id}/parties", response_model=ContractPartyResponse, status_code=status.HTTP_201_CREATED)
async def add_contract_party(
    contract_id: UUID,
    party_data: ContractPartyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Add party to contract
    
    - **party_type**: PRIMARY, SECONDARY, WITNESS, GUARANTOR, LEGAL_REPRESENTATIVE
    - **party_name**: Full name of the party
    - **is_signatory**: Whether this party signs the contract
    """
    party = await ContractService.add_contract_party(
        db=db,
        contract_id=contract_id,
        tenant_id=tenant_id,
        party_data=party_data
    )
    
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return ContractPartyResponse.from_orm(party)


@router.get("/{contract_id}/parties", response_model=List[ContractPartyResponse])
async def list_contract_parties(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all parties associated with a contract"""
    contract = await ContractService.get_contract(db=db, contract_id=contract_id, tenant_id=tenant_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return [ContractPartyResponse.from_orm(party) for party in contract.parties]


# ============================================
# CONTRACT DOCUMENT ENDPOINTS
# ============================================

@router.post("/{contract_id}/documents", response_model=ContractDocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_contract_document(
    contract_id: UUID,
    document_data: ContractDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Add document to contract
    
    - **document_name**: Display name for the document
    - **document_type**: agreement, amendment, addendum, supporting
    - **file_url**: URL to the stored file
    - **is_confidential**: Mark document as confidential
    """
    document = await ContractService.add_contract_document(
        db=db,
        contract_id=contract_id,
        tenant_id=tenant_id,
        document_data=document_data,
        user_id=current_user.id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return ContractDocumentResponse.from_orm(document)


@router.get("/{contract_id}/documents", response_model=List[ContractDocumentResponse])
async def list_contract_documents(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all documents associated with a contract"""
    contract = await ContractService.get_contract(db=db, contract_id=contract_id, tenant_id=tenant_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return [ContractDocumentResponse.from_orm(doc) for doc in contract.documents if not doc.is_deleted]


# ============================================
# CONTRACT VERSION ENDPOINTS
# ============================================

@router.get("/{contract_id}/versions", response_model=List[ContractVersionResponse])
async def list_contract_versions(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all versions of a contract
    
    - Returns complete version history
    - Includes change summaries and reasons
    - Ordered by version number (latest first)
    """
    contract = await ContractService.get_contract(db=db, contract_id=contract_id, tenant_id=tenant_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    versions = sorted(contract.versions, key=lambda v: v.version_number, reverse=True)
    return [ContractVersionResponse.from_orm(version) for version in versions]


# ============================================
# CONTRACT RENEWAL ENDPOINTS
# ============================================

@router.post("/{contract_id}/renewals", response_model=ContractRenewalResponse, status_code=status.HTTP_201_CREATED)
async def create_contract_renewal(
    contract_id: UUID,
    renewal_data: ContractRenewalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Initiate contract renewal
    
    - **renewal_due_date**: Date by which renewal should be completed
    - **new_expiry_date**: New expiry date after renewal
    - **new_contract_value**: Updated contract value (if applicable)
    - **terms_modified**: Flag if terms have changed
    """
    renewal = await ContractService.create_renewal(
        db=db,
        contract_id=contract_id,
        tenant_id=tenant_id,
        renewal_data=renewal_data,
        user_id=current_user.id
    )
    
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    return ContractRenewalResponse.from_orm(renewal)


@router.patch("/renewals/{renewal_id}", response_model=ContractRenewalResponse)
async def update_contract_renewal(
    renewal_id: UUID,
    renewal_data: ContractRenewalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Update contract renewal
    
    - Update renewal status (PENDING, IN_PROGRESS, COMPLETED, REJECTED)
    - Track approval workflow
    - When completed, updates parent contract expiry date
    """
    renewal = await ContractService.update_renewal(
        db=db,
        renewal_id=renewal_id,
        tenant_id=tenant_id,
        renewal_data=renewal_data,
        user_id=current_user.id
    )
    
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )
    
    return ContractRenewalResponse.from_orm(renewal)


@router.get("/{contract_id}/renewals", response_model=List[ContractRenewalResponse])
async def list_contract_renewals(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all renewals for a contract
    
    - Returns complete renewal history
    - Ordered by renewal number (latest first)
    """
    contract = await ContractService.get_contract(db=db, contract_id=contract_id, tenant_id=tenant_id)
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    renewals = sorted(contract.renewals, key=lambda r: r.renewal_number, reverse=True)
    return [ContractRenewalResponse.from_orm(renewal) for renewal in renewals]


# ============================================
# BULK OPERATIONS
# ============================================

@router.post("/bulk/status-update", status_code=status.HTTP_200_OK)
async def bulk_update_status(
    contract_ids: List[UUID],
    new_status: ContractStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Bulk update contract status
    
    - Update multiple contracts at once
    - Useful for batch approvals or status changes
    """
    updated_count = 0
    
    for contract_id in contract_ids:
        update_data = ContractUpdate(status=new_status)
        contract = await ContractService.update_contract(
            db=db,
            contract_id=contract_id,
            tenant_id=tenant_id,
            contract_data=update_data,
            user_id=current_user.id
        )
        if contract:
            updated_count += 1
    
    return {
        "success": True,
        "message": f"Updated {updated_count} out of {len(contract_ids)} contracts",
        "updated_count": updated_count
    }
