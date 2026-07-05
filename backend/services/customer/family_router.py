"""
Customer Family API Router
FastAPI routes for family member operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.core.database import get_db
from backend.core.security import get_current_user
from .family_service import CustomerFamilyService
from .schemas import (
    CustomerFamilyCreate, CustomerFamilyUpdate,
    CustomerFamilyResponse
)

router = APIRouter(prefix="/customers/{customer_id}/family", tags=["Customer Family"])


def get_family_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> CustomerFamilyService:
    """Dependency to get family service"""
    return CustomerFamilyService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


@router.post("", response_model=CustomerFamilyResponse, status_code=status.HTTP_201_CREATED)
async def add_family_member(
    customer_id: int,
    data: CustomerFamilyCreate,
    service: CustomerFamilyService = Depends(get_family_service)
):
    """
    Add family member to customer
    
    - Automatically calculates age from DOB
    - Validates nominee percentage
    - Supports multiple nominees (total must be 100%)
    """
    # Ensure customer_id matches
    data.customer_id = customer_id
    
    try:
        member = await service.create_family_member(data)
        return member
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[CustomerFamilyResponse])
async def get_family_members(
    customer_id: int,
    is_nominee: Optional[bool] = Query(None, description="Filter by nominee status"),
    is_emergency_contact: Optional[bool] = Query(None, description="Filter by emergency contact"),
    service: CustomerFamilyService = Depends(get_family_service)
):
    """
    Get all family members for a customer
    
    Optional filters:
    - is_nominee: Show only nominees
    - is_emergency_contact: Show only emergency contacts
    """
    members = await service.get_family_members(
        customer_id=customer_id,
        is_nominee=is_nominee,
        is_emergency_contact=is_emergency_contact
    )
    return members


@router.get("/validate-nominees")
async def validate_nominees(
    customer_id: int,
    service: CustomerFamilyService = Depends(get_family_service)
):
    """
    Validate that nominee percentages add up to 100%
    
    Returns validation status and total percentage
    """
    validation = await service.validate_nominee_percentage(customer_id)
    return validation


@router.get("/{member_id}", response_model=CustomerFamilyResponse)
async def get_family_member(
    customer_id: int,
    member_id: int,
    service: CustomerFamilyService = Depends(get_family_service)
):
    """Get family member by ID"""
    member = await service.get_family_member(member_id)
    if not member or member.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member with ID {member_id} not found"
        )
    return member


@router.put("/{member_id}", response_model=CustomerFamilyResponse)
async def update_family_member(
    customer_id: int,
    member_id: int,
    data: CustomerFamilyUpdate,
    service: CustomerFamilyService = Depends(get_family_service)
):
    """
    Update family member details
    
    - All fields optional
    - Age auto-calculated if DOB changed
    """
    member = await service.update_family_member(member_id, data)
    if not member or member.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member with ID {member_id} not found"
        )
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family_member(
    customer_id: int,
    member_id: int,
    service: CustomerFamilyService = Depends(get_family_service)
):
    """Soft delete family member"""
    success = await service.delete_family_member(member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family member with ID {member_id} not found"
        )
    return None
