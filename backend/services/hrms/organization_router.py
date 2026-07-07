"""
HRMS Organization API Router
FastAPI routes for organization operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .organization_service import OrganizationService
from .schemas import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationListItem
)

router = APIRouter(prefix="/hrms/organizations", tags=["HRMS - Organizations"])


def get_organization_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> OrganizationService:
    """Dependency to get organization service"""
    return OrganizationService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# ORGANIZATION CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Create new organization
    
    - Auto-generates organization code (ORG-XXXX)
    - Stores company registration details
    - Multi-tenant support
    """
    try:
        organization = await service.create_organization(data)
        return organization
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def get_organizations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Get paginated list of organizations
    
    Supports:
    - Search across name, code
    - Filter by active status
    - Pagination with configurable page size
    """
    organizations, total = await service.get_organizations(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return {
        "items": organizations,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get("/active", response_model=List[OrganizationListItem])
async def get_active_organizations(
    service: OrganizationService = Depends(get_organization_service)
):
    """Get all active organizations (for dropdowns)"""
    organizations = await service.get_all_active()
    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: str,
    service: OrganizationService = Depends(get_organization_service)
):
    """Get organization by ID with all details"""
    organization = await service.get_organization(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization


@router.get("/code/{organization_code}", response_model=OrganizationResponse)
async def get_organization_by_code(
    organization_code: str,
    service: OrganizationService = Depends(get_organization_service)
):
    """Get organization by organization code"""
    organization = await service.get_organization_by_code(organization_code)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    data: OrganizationUpdate,
    service: OrganizationService = Depends(get_organization_service)
):
    """Update organization details"""
    try:
        organization = await service.update_organization(organization_id, data)
        return organization
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: str,
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Soft delete organization
    
    Note: Cannot delete organization with departments or employees
    """
    try:
        await service.delete_organization(organization_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
