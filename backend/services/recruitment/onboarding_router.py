"""
Onboarding Router
FastAPI endpoints for onboarding workflow and background verification
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.shared.database.connection import get_db
from backend.shared.dependencies.auth import get_current_user, get_tenant_id
from .onboarding_service import OnboardingService, BackgroundVerificationService
from .schemas import (
    OnboardingCreate, OnboardingUpdate, OnboardingResponse,
    OnboardingListResponse, OnboardingStatusEnum,
    OnboardingChecklistItemUpdate, BackgroundVerificationCreate,
    BackgroundVerificationUpdate, BackgroundVerificationResponse,
    BackgroundVerificationListResponse, VerificationStatusEnum
)


router = APIRouter()


def get_onboarding_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get onboarding service instance"""
    return OnboardingService(db, tenant_id, user_id)


def get_verification_service(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user)
):
    """Dependency to get verification service instance"""
    return BackgroundVerificationService(db, tenant_id, user_id)


# ==================== Onboarding Endpoints ====================

@router.post("/", response_model=OnboardingResponse, status_code=201)
async def create_onboarding(
    data: OnboardingCreate,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Create new onboarding record"""
    try:
        onboarding = await service.create_onboarding(data)
        return onboarding
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=OnboardingListResponse)
async def get_onboardings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[OnboardingStatusEnum] = Query(None),
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Get paginated list of onboarding records with filters"""
    try:
        onboardings, total = await service.get_onboardings(
            page=page,
            page_size=page_size,
            search=search,
            status=status
        )
        
        return {
            "items": onboardings,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{onboarding_id}", response_model=OnboardingResponse)
async def get_onboarding(
    onboarding_id: str,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Get onboarding by ID"""
    onboarding = await service.get_onboarding(onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding not found")
    return onboarding


@router.put("/{onboarding_id}", response_model=OnboardingResponse)
async def update_onboarding(
    onboarding_id: str,
    data: OnboardingUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Update onboarding"""
    try:
        onboarding = await service.update_onboarding(onboarding_id, data)
        return onboarding
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{onboarding_id}/start", response_model=OnboardingResponse)
async def start_onboarding(
    onboarding_id: str,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Start onboarding process"""
    try:
        onboarding = await service.start_onboarding(onboarding_id)
        return onboarding
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{onboarding_id}/complete", response_model=OnboardingResponse)
async def complete_onboarding(
    onboarding_id: str,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Complete onboarding process"""
    try:
        onboarding = await service.complete_onboarding(onboarding_id)
        return onboarding
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{onboarding_id}/checklist-item", response_model=OnboardingResponse)
async def update_checklist_item(
    onboarding_id: str,
    item_update: OnboardingChecklistItemUpdate,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Update checklist item status"""
    try:
        onboarding = await service.update_checklist_item(
            onboarding_id,
            item_update.item_key,
            item_update.completed
        )
        return onboarding
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{onboarding_id}", status_code=204)
async def delete_onboarding(
    onboarding_id: str,
    service: OnboardingService = Depends(get_onboarding_service)
):
    """Delete onboarding (soft delete)"""
    try:
        await service.delete_onboarding(onboarding_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Background Verification Endpoints ====================

@router.post("/verifications", response_model=BackgroundVerificationResponse, status_code=201)
async def create_verification(
    data: BackgroundVerificationCreate,
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Create new background verification"""
    try:
        verification = await service.create_verification(data)
        return verification
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verifications", response_model=BackgroundVerificationListResponse)
async def get_verifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    onboarding_id: Optional[str] = Query(None),
    status: Optional[VerificationStatusEnum] = Query(None),
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Get paginated list of verifications with filters"""
    try:
        verifications, total = await service.get_verifications(
            page=page,
            page_size=page_size,
            onboarding_id=onboarding_id,
            status=status
        )
        
        return {
            "items": verifications,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/verifications/{verification_id}", response_model=BackgroundVerificationResponse)
async def get_verification(
    verification_id: str,
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Get verification by ID"""
    verification = await service.get_verification(verification_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    return verification


@router.put("/verifications/{verification_id}", response_model=BackgroundVerificationResponse)
async def update_verification(
    verification_id: str,
    data: BackgroundVerificationUpdate,
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Update verification"""
    try:
        verification = await service.update_verification(verification_id, data)
        return verification
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verifications/{verification_id}/start", response_model=BackgroundVerificationResponse)
async def start_verification(
    verification_id: str,
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Start verification process"""
    try:
        verification = await service.start_verification(verification_id)
        return verification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verifications/{verification_id}/complete", response_model=BackgroundVerificationResponse)
async def complete_verification(
    verification_id: str,
    verified: bool = Query(...),
    verification_notes: Optional[str] = Query(None),
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Complete verification process"""
    try:
        verification = await service.complete_verification(
            verification_id,
            verified,
            verification_notes
        )
        return verification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/verifications/{verification_id}", status_code=204)
async def delete_verification(
    verification_id: str,
    service: BackgroundVerificationService = Depends(get_verification_service)
):
    """Delete verification (soft delete)"""
    try:
        await service.delete_verification(verification_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
