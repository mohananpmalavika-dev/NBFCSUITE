"""
CRM Account Management Routes
FastAPI endpoints for account operations
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.schemas.crm_account_schemas import (
    CRMAccountCreate, CRMAccountUpdate,
    CRMContactCreate, CRMContactUpdate,
    CRMAccountRelationshipCreate, CRMAccountRelationshipUpdate
)
from backend.crm.services.account_service import (
    CRMAccountService, CRMContactService, CRMRelationshipService
)

router = APIRouter(prefix="/crm/accounts", tags=["CRM - Account Management"])


# Helper to convert async session to sync for service layer
async def get_sync_db(db: AsyncSession = Depends(get_db)) -> Session:
    """Convert async session to sync session for service layer"""
    return db.sync_session


# ============================================================================
# ACCOUNT ROUTES
# ============================================================================

@router.post("", response_model=dict, status_code=201)
async def create_account(
    account_data: CRMAccountCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new CRM account
    
    - **account_name**: Name of the account (required)
    - **account_type**: Type of account (individual, business, partner, etc.)
    - **status**: Account status (prospect, customer, active, etc.)
    """
    tenant_id = "default"  # TODO: Get from auth context
    user_id = None  # TODO: Get from current user
    
    # Use sync_session for service layer
    result = CRMAccountService.create_account(
        db.sync_session, account_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to create account")
        )
    
    return result


@router.get("", response_model=dict)
async def list_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in account name, number, email, phone"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    account_owner_id: Optional[UUID] = Query(None, description="Filter by account owner"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all CRM accounts with pagination and filters
    
    Supports:
    - Pagination with skip/limit
    - Search by name, number, email, phone
    - Filter by status, type, and owner
    """
    tenant_id = "default"
    
    result = CRMAccountService.list_accounts(
        db.sync_session, tenant_id, skip, limit, search, status_filter, account_type, account_owner_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to list accounts")
        )
    
    return result


@router.get("/{account_id}", response_model=dict)
async def get_account(
    account_id: UUID = Path(..., description="Account ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get account details by ID
    """
    tenant_id = "default"
    
    result = CRMAccountService.get_account(db.sync_session, account_id, tenant_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "ACCOUNT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@router.get("/{account_id}/360", response_model=dict)
async def get_account_360_view(
    account_id: UUID = Path(..., description="Account ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete 360-degree view of an account
    
    Includes:
    - Account details
    - All contacts
    - Account relationships
    - Recent activities
    - Child accounts
    - Business metrics
    """
    tenant_id = "default"
    
    result = CRMAccountService.get_account_360_view(db.sync_session, account_id, tenant_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "ACCOUNT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@router.put("/{account_id}", response_model=dict)
async def update_account(
    account_id: UUID = Path(..., description="Account ID"),
    account_data: CRMAccountUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """
    Update account details
    
    All fields are optional. Only provided fields will be updated.
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMAccountService.update_account(
        db.sync_session, account_id, account_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "ACCOUNT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@router.delete("/{account_id}", response_model=dict)
async def delete_account(
    account_id: UUID = Path(..., description="Account ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an account (soft delete)
    
    The account will be marked as deleted but not removed from the database.
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMAccountService.delete_account(db.sync_session, account_id, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "ACCOUNT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


# ============================================================================
# CONTACT ROUTES
# ============================================================================

@router.post("/contacts", response_model=dict, status_code=201)
async def create_contact(
    contact_data: CRMContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new contact
    
    - **account_id**: Associated account ID (required)
    - **first_name**: Contact first name (required)
    - **last_name**: Contact last name (required)
    - **contact_type**: Type of contact (primary, secondary, decision_maker, etc.)
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMContactService.create_contact(db.sync_session, contact_data, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to create contact")
        )
    
    return result


@router.get("/contacts", response_model=dict)
async def list_contacts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in contact name, number, email, phone"),
    account_id: Optional[UUID] = Query(None, description="Filter by account"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    contact_type: Optional[str] = Query(None, description="Filter by contact type"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all contacts with pagination and filters
    
    Supports:
    - Pagination with skip/limit
    - Search by name, number, email, phone
    - Filter by account, status, and type
    """
    tenant_id = "default"
    
    result = CRMContactService.list_contacts(
        db.sync_session, tenant_id, skip, limit, search, account_id, status_filter, contact_type
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to list contacts")
        )
    
    return result


@router.get("/contacts/{contact_id}", response_model=dict)
async def get_contact(
    contact_id: UUID = Path(..., description="Contact ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get contact details by ID
    """
    tenant_id = "default"
    
    result = CRMContactService.get_contact(db.sync_session, contact_id, tenant_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "CONTACT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@router.put("/contacts/{contact_id}", response_model=dict)
async def update_contact(
    contact_id: UUID = Path(..., description="Contact ID"),
    contact_data: CRMContactUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """
    Update contact details
    
    All fields are optional. Only provided fields will be updated.
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMContactService.update_contact(
        db.sync_session, contact_id, contact_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "CONTACT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@router.delete("/contacts/{contact_id}", response_model=dict)
async def delete_contact(
    contact_id: UUID = Path(..., description="Contact ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a contact (soft delete)
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMContactService.delete_contact(db.sync_session, contact_id, tenant_id, user_id)
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "CONTACT_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


# ============================================================================
# RELATIONSHIP ROUTES
# ============================================================================

@router.post("/relationships", response_model=dict, status_code=201)
async def create_relationship(
    relationship_data: CRMAccountRelationshipCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new account relationship
    
    - **primary_account_id**: Primary account ID (required)
    - **related_account_id**: Related account ID (required)
    - **relationship_type**: Type of relationship (parent_child, partner, vendor, etc.)
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMRelationshipService.create_relationship(
        db.sync_session, relationship_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to create relationship")
        )
    
    return result


@router.get("/relationships", response_model=dict)
async def list_relationships(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all relationships with pagination
    
    - If account_id is provided, returns all relationships for that account
    - Otherwise returns all relationships in the system
    """
    tenant_id = "default"
    
    result = CRMRelationshipService.list_relationships(
        db.sync_session, tenant_id, account_id, skip, limit
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.get("message", "Failed to list relationships")
        )
    
    return result


@router.put("/relationships/{relationship_id}", response_model=dict)
async def update_relationship(
    relationship_id: UUID = Path(..., description="Relationship ID"),
    relationship_data: CRMAccountRelationshipUpdate = ...,
    db: AsyncSession = Depends(get_db)
):
    """
    Update relationship details
    
    All fields are optional. Only provided fields will be updated.
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMRelationshipService.update_relationship(
        db.sync_session, relationship_id, relationship_data, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "RELATIONSHIP_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result


@router.delete("/relationships/{relationship_id}", response_model=dict)
async def delete_relationship(
    relationship_id: UUID = Path(..., description="Relationship ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a relationship (soft delete)
    """
    tenant_id = "default"
    user_id = None
    
    result = CRMRelationshipService.delete_relationship(
        db.sync_session, relationship_id, tenant_id, user_id
    )
    
    if not result.get("success"):
        error = result.get("error", {})
        status_code = status.HTTP_404_NOT_FOUND if error.get("code") == "RELATIONSHIP_NOT_FOUND" else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=error.get("message"))
    
    return result
