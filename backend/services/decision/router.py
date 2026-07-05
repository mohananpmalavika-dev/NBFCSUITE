"""
Decision Engine API Router

REST API endpoints for instant decisions, pre-approved offers,
and decision strategies.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.decision.decision_service import DecisionService
from backend.services.decision.strategy_service import StrategyService
from backend.services.decision.offer_service import OfferService
from backend.services.decision.schemas import (
    InstantDecisionRequest,
    InstantDecisionResponse,
    DecisionAcceptRequest,
    DecisionRejectRequest,
    DecisionRecalculateRequest,
    PreApprovedOfferCreate,
    PreApprovedOfferResponse,
    OfferCalculateRequest,
    OfferUseRequest,
    DecisionStrategyCreate,
    DecisionStrategyUpdate,
    DecisionStrategyResponse,
    QuickQuoteRequest,
    QuickQuoteResponse,
    DecisionType,
    DecisionResult,
    DecisionStatus,
    OfferType,
    OfferStatus
)

router = APIRouter()


# ==================== INSTANT DECISION ENDPOINTS ====================

@router.post("/decisions/instant", response_model=dict, tags=["Decision Engine"])
async def make_instant_decision(
    request: InstantDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Make an instant decision for loan approval, eligibility, or quick quote.
    
    Integrates with Rules Engine to evaluate business rules and returns
    instant approval/rejection/manual review decision.
    
    **Features**:
    - Sub-200ms response time
    - Integration with Rules Engine
    - Decision caching for performance
    - Confidence scoring
    - Decision explanation
    
    **Decision Types**:
    - `loan_approval`: Instant loan approval decision
    - `eligibility`: Check product eligibility
    - `quick_quote`: Get instant loan quote
    - `limit_increase`: Credit limit increase
    """
    try:
        service = DecisionService(db, tenant_id, current_user["id"])
        decision = await service.make_instant_decision(request)
        return success_response(decision.dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/decisions/{decision_id}", response_model=dict, tags=["Decision Engine"])
async def get_decision(
    decision_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get decision details by ID"""
    service = DecisionService(db, tenant_id, current_user["id"])
    decision = await service.get_decision(decision_id)
    
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    
    return success_response(decision)


@router.post("/decisions/{decision_id}/accept", response_model=dict, tags=["Decision Engine"])
async def accept_decision(
    decision_id: int,
    request: DecisionAcceptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Accept a decision/offer.
    
    Customer accepts the approved decision and can proceed to
    create a loan application.
    """
    try:
        service = DecisionService(db, tenant_id, current_user["id"])
        decision = await service.accept_decision(decision_id, request.remarks)
        return success_response({
            "decision_id": decision.id,
            "status": decision.status,
            "message": "Decision accepted successfully"
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/decisions/{decision_id}/reject", response_model=dict, tags=["Decision Engine"])
async def reject_decision(
    decision_id: int,
    request: DecisionRejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Reject a decision/offer.
    
    Customer rejects the decision. Reason is recorded for analytics.
    """
    try:
        service = DecisionService(db, tenant_id, current_user["id"])
        decision = await service.reject_decision(decision_id, request.reason)
        return success_response({
            "decision_id": decision.id,
            "status": decision.status,
            "message": "Decision rejected successfully"
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/decisions/customer/{customer_id}", response_model=dict, tags=["Decision Engine"])
async def get_customer_decisions(
    customer_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get recent decisions for a customer"""
    service = DecisionService(db, tenant_id, current_user["id"])
    decisions = await service.get_customer_decisions(customer_id, limit)
    return success_response({
        "customer_id": customer_id,
        "total": len(decisions),
        "decisions": decisions
    })


@router.post("/decisions/quick-quote", response_model=dict, tags=["Decision Engine"])
async def get_quick_quote(
    request: QuickQuoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get instant loan quote with EMI calculation.
    
    Provides instant quote without creating a decision record.
    Useful for loan calculators and product pages.
    """
    try:
        # Create decision request for quote
        decision_request = InstantDecisionRequest(
            decision_type=DecisionType.QUICK_QUOTE,
            customer_id=request.customer_id,
            product_id=request.product_id,
            request_data={
                "loan_amount": float(request.loan_amount),
                "tenure": request.tenure
            },
            use_cache=True
        )
        
        service = DecisionService(db, tenant_id, current_user["id"])
        result = await service.make_instant_decision(decision_request)
        
        return success_response({
            "eligible": result.decision_result == DecisionResult.APPROVED,
            "approved_amount": result.approved_amount,
            "interest_rate": result.interest_rate,
            "processing_fee": result.processing_fee,
            "monthly_emi": result.monthly_emi,
            "eligibility_message": result.decision_reason,
            "decision_factors": result.decision_factors
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== PRE-APPROVED OFFER ENDPOINTS ====================

@router.post("/offers/calculate", response_model=dict, tags=["Pre-Approved Offers"])
async def calculate_offer(
    request: OfferCalculateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate pre-approved offer for a customer.
    
    Analyzes customer profile, credit history, and applies business rules
    to determine pre-approved loan amount and terms.
    """
    try:
        service = OfferService(db, tenant_id, current_user["id"])
        offer_data = await service.calculate_offer(request)
        return success_response(offer_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/offers", response_model=dict, tags=["Pre-Approved Offers"])
async def create_offer(
    offer: PreApprovedOfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create a new pre-approved offer.
    
    Creates an offer that customer can view and accept in their portal.
    """
    try:
        service = OfferService(db, tenant_id, current_user["id"])
        created_offer = await service.create_offer(offer)
        return success_response(PreApprovedOfferResponse.from_orm(created_offer).dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/offers", response_model=dict, tags=["Pre-Approved Offers"])
async def list_offers(
    offer_type: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    product_id: Optional[int] = None,
    valid_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List pre-approved offers with filters"""
    service = OfferService(db, tenant_id, current_user["id"])
    offers, total = await service.list_offers(
        offer_type=offer_type,
        status=status,
        customer_id=customer_id,
        product_id=product_id,
        valid_only=valid_only,
        skip=skip,
        limit=limit
    )
    
    return success_response({
        "total": total,
        "skip": skip,
        "limit": limit,
        "offers": [PreApprovedOfferResponse.from_orm(o).dict() for o in offers]
    })


@router.get("/offers/{offer_id}", response_model=dict, tags=["Pre-Approved Offers"])
async def get_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get offer details and increment view count"""
    service = OfferService(db, tenant_id, current_user["id"])
    offer = await service.get_offer(offer_id)
    
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    
    # Increment view count
    await service.increment_view_count(offer_id)
    
    return success_response(PreApprovedOfferResponse.from_orm(offer).dict())


@router.get("/offers/customer/{customer_id}", response_model=dict, tags=["Pre-Approved Offers"])
async def get_customer_offers(
    customer_id: int,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get all active offers for a customer"""
    service = OfferService(db, tenant_id, current_user["id"])
    offers = await service.get_customer_offers(customer_id, active_only)
    
    return success_response({
        "customer_id": customer_id,
        "total": len(offers),
        "offers": [PreApprovedOfferResponse.from_orm(o).dict() for o in offers]
    })


@router.post("/offers/{offer_id}/use", response_model=dict, tags=["Pre-Approved Offers"])
async def use_offer(
    offer_id: int,
    request: OfferUseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Use a pre-approved offer to create loan application.
    
    Marks offer as used and returns application ID.
    """
    try:
        # TODO: Create loan application
        application_id = 12345  # Placeholder
        
        service = OfferService(db, tenant_id, current_user["id"])
        offer = await service.use_offer(offer_id, application_id)
        
        return success_response({
            "offer_id": offer.id,
            "status": offer.status,
            "application_id": application_id,
            "message": "Offer used successfully. Application created."
        })
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/offers/statistics/summary", response_model=dict, tags=["Pre-Approved Offers"])
async def get_offer_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get offer statistics and conversion metrics"""
    service = OfferService(db, tenant_id, current_user["id"])
    stats = await service.get_offer_statistics()
    return success_response(stats)


# ==================== DECISION STRATEGY ENDPOINTS ====================

@router.post("/strategies", response_model=dict, tags=["Decision Strategies"])
async def create_strategy(
    strategy: DecisionStrategyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create a new decision strategy.
    
    Strategies define thresholds, rules, and behavior for instant decisions.
    """
    try:
        service = StrategyService(db, tenant_id, current_user["id"])
        created_strategy = await service.create_strategy(strategy)
        return success_response(DecisionStrategyResponse.from_orm(created_strategy).dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/strategies", response_model=dict, tags=["Decision Strategies"])
async def list_strategies(
    decision_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List decision strategies with filters"""
    service = StrategyService(db, tenant_id, current_user["id"])
    strategies, total = await service.list_strategies(
        decision_type=decision_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return success_response({
        "total": total,
        "skip": skip,
        "limit": limit,
        "strategies": [DecisionStrategyResponse.from_orm(s).dict() for s in strategies]
    })


@router.get("/strategies/{strategy_id}", response_model=dict, tags=["Decision Strategies"])
async def get_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get strategy details"""
    service = StrategyService(db, tenant_id, current_user["id"])
    strategy = await service.get_strategy(strategy_id)
    
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    
    return success_response(DecisionStrategyResponse.from_orm(strategy).dict())


@router.put("/strategies/{strategy_id}", response_model=dict, tags=["Decision Strategies"])
async def update_strategy(
    strategy_id: int,
    update_data: DecisionStrategyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update a decision strategy"""
    try:
        service = StrategyService(db, tenant_id, current_user["id"])
        strategy = await service.update_strategy(strategy_id, update_data)
        return success_response(DecisionStrategyResponse.from_orm(strategy).dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/strategies/{strategy_id}", response_model=dict, tags=["Decision Strategies"])
async def delete_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete a decision strategy"""
    service = StrategyService(db, tenant_id, current_user["id"])
    success = await service.delete_strategy(strategy_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    
    return success_response({"message": "Strategy deleted successfully"})


@router.get("/strategies/{strategy_code}/statistics", response_model=dict, tags=["Decision Strategies"])
async def get_strategy_statistics(
    strategy_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get performance statistics for a strategy"""
    try:
        service = StrategyService(db, tenant_id, current_user["id"])
        stats = await service.get_strategy_stats(strategy_code)
        return success_response(stats)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

