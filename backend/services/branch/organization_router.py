"""
Organization Router
API endpoints for organizational hierarchy management
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.shared.database.branch_models import Organization
from backend.services.branch.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationHierarchy
)
from backend.services.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/branch/organizations", tags=["Branch - Organizations"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization unit"
)
async def create_organization(
    request: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new organizational unit"""
    
    # Check if code already exists
    stmt = select(Organization).where(
        and_(
            Organization.tenant_id == current_user.tenant_id,
            Organization.code == request.code,
            Organization.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return error_response(
            message="Organization code already exists",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Build hierarchy path
    hierarchy_path = f"/{request.code}"
    if request.parent_id:
        parent_stmt = select(Organization).where(Organization.id == request.parent_id)
        parent_result = await db.execute(parent_stmt)
        parent = parent_result.scalar_one_or_none()
        if parent:
            hierarchy_path = f"{parent.hierarchy_path}/{request.code}"
    
    # Create organization
    org = Organization(
        tenant_id=current_user.tenant_id,
        code=request.code,
        name=request.name,
        display_name=request.display_name,
        level=request.level,
        parent_id=request.parent_id,
        hierarchy_path=hierarchy_path,
        manager_id=request.manager_id,
        manager_name=request.manager_name,
        email=request.email,
        phone=request.phone,
        address_line1=request.address_line1,
        address_line2=request.address_line2,
        city=request.city,
        state=request.state,
        pincode=request.pincode,
        country=request.country,
        status=request.status,
        is_operational=request.is_operational,
        opening_date=request.opening_date,
        cash_limit=request.cash_limit,
        daily_transaction_limit=request.daily_transaction_limit,
        settings=request.settings,
        created_by=current_user.id
    )
    
    db.add(org)
    await db.commit()
    await db.refresh(org)
    
    return success_response(
        data=OrganizationResponse.model_validate(org).model_dump(mode='json'),
        message="Organization created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get(
    "",
    response_model=dict,
    summary="List organizations"
)
async def list_organizations(
    level: Optional[str] = Query(None, description="Filter by level"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get list of organizations"""
    
    stmt = select(Organization).where(
        and_(
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    )
    
    if level:
        stmt = stmt.where(Organization.level == level)
    if parent_id:
        stmt = stmt.where(Organization.parent_id == parent_id)
    if status:
        stmt = stmt.where(Organization.status == status)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated results
    stmt = stmt.order_by(Organization.hierarchy_path).offset(skip).limit(limit)
    result = await db.execute(stmt)
    organizations = result.scalars().all()
    
    return success_response(
        data={
            "items": [OrganizationResponse.model_validate(org).model_dump(mode='json') for org in organizations],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get(
    "/hierarchy",
    response_model=dict,
    summary="Get organization hierarchy tree"
)
async def get_hierarchy(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get complete organization hierarchy as tree"""
    
    stmt = select(Organization).where(
        and_(
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    ).order_by(Organization.hierarchy_path)
    
    result = await db.execute(stmt)
    organizations = result.scalars().all()
    
    # Build tree structure
    org_dict = {org.id: {
        "id": org.id,
        "code": org.code,
        "name": org.name,
        "level": org.level,
        "parent_id": org.parent_id,
        "children": []
    } for org in organizations}
    
    root_nodes = []
    for org_id, org_data in org_dict.items():
        parent_id = org_data["parent_id"]
        if parent_id and parent_id in org_dict:
            org_dict[parent_id]["children"].append(org_data)
        else:
            root_nodes.append(org_data)
    
    return success_response(data=root_nodes)


@router.get(
    "/{organization_id}",
    response_model=dict,
    summary="Get organization by ID"
)
async def get_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get organization details"""
    
    stmt = select(Organization).where(
        and_(
            Organization.id == organization_id,
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        return error_response(
            message="Organization not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    return success_response(
        data=OrganizationResponse.model_validate(org).model_dump(mode='json')
    )


@router.put(
    "/{organization_id}",
    response_model=dict,
    summary="Update organization"
)
async def update_organization(
    organization_id: UUID,
    request: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update organization details"""
    
    stmt = select(Organization).where(
        and_(
            Organization.id == organization_id,
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        return error_response(
            message="Organization not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    org.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(org)
    
    return success_response(
        data=OrganizationResponse.model_validate(org).model_dump(mode='json'),
        message="Organization updated successfully"
    )


@router.delete(
    "/{organization_id}",
    response_model=dict,
    summary="Delete organization"
)
async def delete_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Soft delete organization"""
    
    stmt = select(Organization).where(
        and_(
            Organization.id == organization_id,
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        return error_response(
            message="Organization not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # Check for children
    child_stmt = select(func.count()).where(
        and_(
            Organization.parent_id == organization_id,
            Organization.tenant_id == current_user.tenant_id,
            Organization.is_deleted == False
        )
    )
    child_result = await db.execute(child_stmt)
    child_count = child_result.scalar()
    
    if child_count > 0:
        return error_response(
            message=f"Cannot delete organization with {child_count} child organizations",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    org.is_deleted = True
    org.deleted_by = current_user.id
    org.deleted_at = func.now()
    
    await db.commit()
    
    return success_response(message="Organization deleted successfully")
