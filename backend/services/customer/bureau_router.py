"""
Credit Bureau API Router
FastAPI routes for credit bureau operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.customer_models import BureauProvider
from .bureau_service import CreditBureauService
from .schemas import (
    BureauPullRequest, BureauPullResponse,
    BureauHistoryResponse, CreditScoreResponse
)

router = APIRouter(prefix="/customers/{customer_id}/bureau", tags=["Credit Bureau"])


def get_bureau_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> CreditBureauService:
    """Dependency to get bureau service"""
    return CreditBureauService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# BUREAU PULL ENDPOINTS
# ============================================================================

@router.post("/pull", response_model=BureauPullResponse, status_code=status.HTTP_201_CREATED)
async def pull_credit_report(
    customer_id: int,
    data: BureauPullRequest,
    service: CreditBureauService = Depends(get_bureau_service)
):
    """
    Pull credit report from bureau
    
    Supports pulling from:
    - CIBIL (TransUnion)
    - Equifax
    - Experian
    - CRIF High Mark
    
    Requires:
    - Customer must have PAN number
    - Bureau provider must be configured
    - Consent tracking for compliance
    """
    
    try:
        # Validate bureau provider
        try:
            bureau_provider = BureauProvider[data.bureau_provider.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid bureau provider: {data.bureau_provider}. "
                       f"Must be one of: {', '.join([p.value for p in BureauProvider])}"
            )
        
        # Pull credit report
        history = await service.pull_credit_report(
            customer_id=customer_id,
            bureau_provider=bureau_provider,
            request_purpose=data.request_purpose or "loan_application"
        )
        
        return history
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull credit report: {str(e)}"
        )


@router.post("/pull-cibil", response_model=BureauPullResponse, status_code=status.HTTP_201_CREATED)
async def pull_cibil_report(
    customer_id: int,
    request_purpose: str = Query("loan_application", description="Purpose of request"),
    service: CreditBureauService = Depends(get_bureau_service)
):
    """
    Quick endpoint to pull CIBIL report
    
    Convenience method for most common bureau
    """
    try:
        history = await service.pull_credit_report(
            customer_id=customer_id,
            bureau_provider=BureauProvider.CIBIL,
            request_purpose=request_purpose
        )
        return history
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull CIBIL report: {str(e)}"
        )



@router.get("/history", response_model=List[BureauHistoryResponse])
async def get_bureau_history(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of records"),
    service: CreditBureauService = Depends(get_bureau_service)
):
    """
    Get bureau pull history for customer
    
    Returns history of all credit report pulls with:
    - Bureau provider
    - Pull date and time
    - Credit score
    - Status (success/failed)
    - Response time
    """
    history = await service.get_bureau_history(customer_id, limit)
    return history


@router.get("/latest-score", response_model=CreditScoreResponse)
async def get_latest_credit_score(
    customer_id: int,
    service: CreditBureauService = Depends(get_bureau_service)
):
    """
    Get latest credit score for customer
    
    Returns the most recent successful credit score
    from any bureau
    """
    score = await service.get_latest_score(customer_id)
    
    if score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No credit score found for this customer"
        )
    
    return CreditScoreResponse(
        customer_id=customer_id,
        credit_score=score
    )


@router.get("/available-providers")
async def get_available_providers(
    service: CreditBureauService = Depends(get_bureau_service)
):
    """
    Get list of configured bureau providers
    
    Returns which bureau providers are available
    based on API configuration
    """
    available = [
        {
            "provider": provider.value,
            "name": provider.value.upper(),
            "configured": provider in service.providers
        }
        for provider in BureauProvider
    ]
    
    return {
        "providers": available,
        "total_configured": len(service.providers)
    }
