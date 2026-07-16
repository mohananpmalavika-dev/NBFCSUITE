"""
Credit Policy Integration Router
API endpoints for credit policy management
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_user, get_tenant_id
from .credit_policy_service import CreditPolicyService
from .credit_policy_models import (
    CreditPolicy, PolicyStatus,
    CreditPolicyCreate, CreditPolicyUpdate, CreditPolicyResponse,
    RiskBasedPricingSchema, ScoreBasedRateSchema, LTVRatioSchema,
    ExposureLimitSchema, ConcentrationLimitSchema, SectoralCapSchema,
    AutoApprovalCriteriaSchema, ManualReviewTriggerSchema,
    DecisionMatrixSchema, CounterOfferRuleSchema,
    PricingCalculationRequest, PricingCalculationResponse,
    CreditDecisionRequest, CreditDecisionResponse,
    ExposureCheckRequest, ExposureCheckResponse
)

router = APIRouter(prefix="/api/credit-policy", tags=["Credit Policy"])


def get_service(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id)
) -> CreditPolicyService:
    """Get credit policy service instance"""
    return CreditPolicyService(db, tenant_id)


# =====================================================================
# CREDIT POLICY CRUD
# =====================================================================

@router.post("/policies", response_model=CreditPolicyResponse)
async def create_policy(
    policy_data: CreditPolicyCreate,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Create new credit policy"""
    try:
        policy = service.create_policy(policy_data, UUID(current_user["id"]))
        return policy
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/policies", response_model=List[CreditPolicyResponse])
async def list_policies(
    product_id: Optional[UUID] = Query(None),
    status: Optional[PolicyStatus] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: CreditPolicyService = Depends(get_service),
    current_user: dict = Depends(get_current_user)
):
    """List credit policies with filters"""
    policies = service.list_policies(
        product_id=product_id,
        status=status,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return policies



@router.get("/policies/{policy_id}", response_model=CreditPolicyResponse)
async def get_policy(
    policy_id: UUID,
    service: CreditPolicyService = Depends(get_service),
    current_user: dict = Depends(get_current_user)
):
    """Get credit policy by ID"""
    policy = service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/policies/{policy_id}", response_model=CreditPolicyResponse)
async def update_policy(
    policy_id: UUID,
    policy_data: CreditPolicyUpdate,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Update credit policy"""
    policy = service.update_policy(policy_id, policy_data, UUID(current_user["id"]))
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.post("/policies/{policy_id}/activate", response_model=CreditPolicyResponse)
async def activate_policy(
    policy_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Activate credit policy"""
    policy = service.activate_policy(policy_id, UUID(current_user["id"]))
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.post("/policies/{policy_id}/deactivate", response_model=CreditPolicyResponse)
async def deactivate_policy(
    policy_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Deactivate credit policy"""
    policy = service.deactivate_policy(policy_id, UUID(current_user["id"]))
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Delete credit policy"""
    success = service.delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}


@router.post("/policies/{policy_id}/clone", response_model=CreditPolicyResponse)
async def clone_policy(
    policy_id: UUID,
    new_name: str = Query(...),
    new_code: str = Query(...),
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Clone an existing policy"""
    policy = service.clone_policy(policy_id, new_name, new_code, UUID(current_user["id"]))
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


# =====================================================================
# RISK-BASED PRICING
# =====================================================================

@router.post("/pricing/calculate", response_model=PricingCalculationResponse)
async def calculate_pricing(
    request: PricingCalculationRequest,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Calculate risk-based pricing"""
    try:
        pricing = service.calculate_pricing(request)
        return pricing
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# CREDIT DECISIONING
# =====================================================================

@router.post("/decision/evaluate", response_model=CreditDecisionResponse)
async def evaluate_credit_decision(
    request: CreditDecisionRequest,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Evaluate credit decision"""
    try:
        decision = service.evaluate_credit_decision(request)
        return decision
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# =====================================================================
# EXPOSURE CHECKING
# =====================================================================

@router.post("/exposure/check", response_model=ExposureCheckResponse)
async def check_exposure_limits(
    request: ExposureCheckRequest,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Check exposure limits"""
    try:
        result = service.check_exposure_limits(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# ANALYTICS & TESTING
# =====================================================================

@router.get("/policies/{policy_id}/statistics")
async def get_policy_statistics(
    policy_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Get policy statistics and metrics"""
    stats = service.get_policy_statistics(policy_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Policy not found")
    return stats


@router.post("/policies/{policy_id}/test")
async def test_policy(
    policy_id: UUID,
    test_scenarios: List[dict],
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Test policy with multiple scenarios"""
    try:
        results = service.test_policy(policy_id, test_scenarios)
        return {
            "policy_id": str(policy_id),
            "total_scenarios": len(test_scenarios),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================================
# POLICY DASHBOARD
# =====================================================================

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_user),
    service: CreditPolicyService = Depends(get_service)
):
    """Get dashboard summary"""
    policies = service.list_policies(limit=1000)
    
    summary = {
        "total_policies": len(policies),
        "active_policies": len([p for p in policies if p.is_active]),
        "draft_policies": len([p for p in policies if p.status == PolicyStatus.DRAFT]),
        "policies_by_product": {},
        "recent_policies": []
    }
    
    # Group by product
    for policy in policies:
        if policy.product_id:
            prod_id = str(policy.product_id)
            if prod_id not in summary["policies_by_product"]:
                summary["policies_by_product"][prod_id] = 0
            summary["policies_by_product"][prod_id] += 1
    
    # Recent policies (last 5)
    recent = sorted(policies, key=lambda p: p.created_at, reverse=True)[:5]
    summary["recent_policies"] = [
        {
            "id": str(p.id),
            "name": p.name,
            "code": p.code,
            "status": p.status.value,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat()
        }
        for p in recent
    ]
    
    return summary
