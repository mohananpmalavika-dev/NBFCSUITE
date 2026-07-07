"""
Risk Management Router
API endpoints for credit policies, risk-based pricing, exposure limits, risk ratings, and early warning systems
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.risk.service import RiskManagementService
from backend.services.risk import schemas


router = APIRouter(prefix="/risk", tags=["Risk Management"])


def get_risk_service(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> RiskManagementService:
    """Dependency to get risk management service"""
    return RiskManagementService(db, current_user["tenant_id"])


# ============================================
# Credit Policy Endpoints
# ============================================

@router.post("/policies", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_credit_policy(
    data: schemas.CreditPolicyCreate,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create new credit policy
    
    - **policy_code**: Unique policy identifier
    - **policy_name**: Policy name
    - **min_cibil_score**: Minimum credit score requirement
    - **max_debt_to_income_ratio**: Maximum DTI ratio
    - **product_types**: Applicable product types
    - **customer_segments**: Applicable customer segments
    """
    try:
        policy = service.create_credit_policy(data, current_user["user_id"])
        return success_response(
            data=schemas.CreditPolicyResponse.model_validate(policy),
            message="Credit policy created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/policies", response_model=dict)
async def list_credit_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    product_type: Optional[str] = Query(None),
    service: RiskManagementService = Depends(get_risk_service)
):
    """List all credit policies with pagination and filters"""
    try:
        result = service.list_credit_policies(page, page_size, is_active, product_type)
        return success_response(
            data=result.model_dump(),
            message="Credit policies retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/policies/{policy_id}", response_model=dict)
async def get_credit_policy(
    policy_id: int,
    service: RiskManagementService = Depends(get_risk_service)
):
    """Get credit policy by ID"""
    policy = service.get_credit_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit policy not found")
    
    return success_response(
        data=schemas.CreditPolicyResponse.model_validate(policy),
        message="Credit policy retrieved successfully"
    )


@router.get("/policies/code/{policy_code}", response_model=dict)
async def get_credit_policy_by_code(
    policy_code: str,
    service: RiskManagementService = Depends(get_risk_service)
):
    """Get credit policy by policy code"""
    policy = service.get_credit_policy_by_code(policy_code)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit policy not found")
    
    return success_response(
        data=schemas.CreditPolicyResponse.model_validate(policy),
        message="Credit policy retrieved successfully"
    )



@router.put("/policies/{policy_id}", response_model=dict)
async def update_credit_policy(
    policy_id: int,
    data: schemas.CreditPolicyUpdate,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """Update credit policy"""
    try:
        policy = service.update_credit_policy(policy_id, data, current_user["user_id"])
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit policy not found")
        
        return success_response(
            data=schemas.CreditPolicyResponse.model_validate(policy),
            message="Credit policy updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/policies/{policy_id}", response_model=dict)
async def delete_credit_policy(
    policy_id: int,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete credit policy (soft delete)"""
    try:
        success = service.delete_credit_policy(policy_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit policy not found")
        
        return success_response(message="Credit policy deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/policies/evaluate", response_model=dict)
async def evaluate_policy(
    request: schemas.PolicyEvaluationRequest,
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    Evaluate loan application against credit policies
    
    Returns eligibility result with passed/failed checks and recommendations
    """
    try:
        result = service.evaluate_policy(request)
        return success_response(
            data=result.model_dump(),
            message="Policy evaluation completed"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Risk-Based Pricing Endpoints
# ============================================

@router.post("/pricing-rules", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_pricing_rule(
    data: schemas.RiskPricingRuleCreate,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """Create risk-based pricing rule"""
    try:
        rule = service.create_pricing_rule(data, current_user["user_id"])
        return success_response(
            data=schemas.RiskPricingRuleResponse.model_validate(rule),
            message="Pricing rule created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/pricing-rules", response_model=dict)
async def list_pricing_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    policy_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: RiskManagementService = Depends(get_risk_service)
):
    """List risk-based pricing rules"""
    try:
        result = service.list_pricing_rules(page, page_size, policy_id, is_active)
        return success_response(
            data=result.model_dump(),
            message="Pricing rules retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/pricing-rules/calculate", response_model=dict)
async def calculate_pricing(
    request: schemas.PricingCalculationRequest,
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    Calculate risk-based pricing for a loan
    
    Returns applicable interest rate based on risk factors
    """
    try:
        result = service.calculate_pricing(request)
        return success_response(
            data=result.model_dump(),
            message="Pricing calculated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Exposure Limit Endpoints
# ============================================

@router.post("/exposure-limits", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_exposure_limit(
    data: schemas.ExposureLimitCreate,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create exposure limit
    
    - **limit_type**: customer, group, industry, geography, product, collateral_type, dealer
    - **limit_amount**: Maximum exposure allowed
    - **warning_threshold_percentage**: Alert threshold (default: 75%)
    - **critical_threshold_percentage**: Critical threshold (default: 90%)
    """
    try:
        limit = service.create_exposure_limit(data, current_user["user_id"])
        return success_response(
            data=schemas.ExposureLimitResponse.model_validate(limit),
            message="Exposure limit created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/exposure-limits", response_model=dict)
async def list_exposure_limits(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    limit_type: Optional[str] = Query(None),
    is_breached: Optional[bool] = Query(None),
    service: RiskManagementService = Depends(get_risk_service)
):
    """List exposure limits with pagination and filters"""
    try:
        result = service.list_exposure_limits(page, page_size, limit_type, is_breached)
        return success_response(
            data=result.model_dump(),
            message="Exposure limits retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/exposure-limits/{limit_id}", response_model=dict)
async def get_exposure_limit(
    limit_id: int,
    service: RiskManagementService = Depends(get_risk_service)
):
    """Get exposure limit by ID"""
    limit = service.get_exposure_limit(limit_id)
    if not limit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exposure limit not found")
    
    return success_response(
        data=schemas.ExposureLimitResponse.model_validate(limit),
        message="Exposure limit retrieved successfully"
    )


@router.post("/exposure-limits/{limit_id}/utilize", response_model=dict)
async def utilize_exposure(
    limit_id: int,
    request: schemas.ExposureUtilizationRequest,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Utilize exposure limit
    
    Books the specified amount against the exposure limit
    """
    try:
        transaction = service.utilize_exposure(limit_id, request, current_user["user_id"])
        return success_response(
            data=schemas.ExposureTransactionResponse.model_validate(transaction),
            message="Exposure utilized successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/exposure-limits/{limit_id}/release", response_model=dict)
async def release_exposure(
    limit_id: int,
    request: schemas.ExposureUtilizationRequest,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Release exposure limit
    
    Releases the specified amount from the exposure limit
    """
    try:
        transaction = service.release_exposure(limit_id, request, current_user["user_id"])
        return success_response(
            data=schemas.ExposureTransactionResponse.model_validate(transaction),
            message="Exposure released successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Risk Rating Endpoints
# ============================================

@router.post("/ratings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_risk_rating(
    data: schemas.RiskRatingCreate,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create risk rating for customer/application/account
    
    - **rating_type**: customer, application, or account
    - **risk_grade**: A+, A, B+, B, C+, C, or D
    - **risk_score**: 0-1000 score
    - Optionally includes PD, LGD, EAD for expected loss calculation
    """
    try:
        rating = service.create_risk_rating(data, current_user["user_id"])
        return success_response(
            data=schemas.RiskRatingResponse.model_validate(rating),
            message="Risk rating created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ratings", response_model=dict)
async def list_risk_ratings(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    customer_id: Optional[str] = Query(None),
    risk_grade: Optional[str] = Query(None),
    rating_type: Optional[str] = Query(None),
    service: RiskManagementService = Depends(get_risk_service)
):
    """List risk ratings with pagination and filters"""
    try:
        result = service.list_risk_ratings(page, page_size, customer_id, risk_grade, rating_type)
        return success_response(
            data=result.model_dump(),
            message="Risk ratings retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ratings/customer/{customer_id}/latest", response_model=dict)
async def get_latest_customer_rating(
    customer_id: str,
    rating_type: str = Query("customer"),
    service: RiskManagementService = Depends(get_risk_service)
):
    """Get latest risk rating for a customer"""
    rating = service.get_latest_risk_rating(customer_id, rating_type)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No risk rating found for customer")
    
    return success_response(
        data=schemas.RiskRatingResponse.model_validate(rating),
        message="Latest risk rating retrieved successfully"
    )


@router.post("/ratings/{rating_id}/override", response_model=dict)
async def override_risk_rating(
    rating_id: int,
    request: schemas.RiskRatingOverrideRequest,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Override risk rating
    
    Allows manual override of system-generated risk rating with approval
    """
    try:
        rating = service.override_risk_rating(rating_id, request, current_user["user_id"])
        if not rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk rating not found")
        
        return success_response(
            data=schemas.RiskRatingResponse.model_validate(rating),
            message="Risk rating overridden successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ratings/statistics", response_model=dict)
async def get_risk_rating_statistics(
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    Get risk rating portfolio statistics
    
    Returns distribution by grade, average scores, high-risk counts, and expected loss
    """
    try:
        stats = service.get_risk_rating_stats()
        return success_response(
            data=stats.model_dump(),
            message="Risk rating statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Early Warning Signal Endpoints
# ============================================

@router.post("/ews/signals", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_ews_signal(
    data: schemas.EarlyWarningSignalCreate,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Create early warning signal configuration
    
    - **signal_category**: payment_behavior, financial_stress, credit_bureau, etc.
    - **severity_level**: low, medium, high, critical
    - **detection_rule**: JSON rule defining when to trigger alert
    """
    try:
        signal = service.create_ews_signal(data, current_user["user_id"])
        return success_response(
            data=schemas.EarlyWarningSignalResponse.model_validate(signal),
            message="Early warning signal created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ews/signals", response_model=dict)
async def list_ews_signals(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: RiskManagementService = Depends(get_risk_service)
):
    """List early warning signal configurations"""
    try:
        result = service.list_ews_signals(page, page_size, category, is_active)
        return success_response(
            data=result.model_dump(),
            message="Early warning signals retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ews/alerts", response_model=dict)
async def list_ews_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    List early warning alerts
    
    Filter by status, severity, category, or customer
    """
    try:
        result = service.list_ews_alerts(
            page, page_size, status_filter, severity, category, customer_id
        )
        return success_response(
            data=result.model_dump(),
            message="Early warning alerts retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/ews/alerts/{alert_id}/action", response_model=dict)
async def take_alert_action(
    alert_id: int,
    request: schemas.AlertActionRequest,
    service: RiskManagementService = Depends(get_risk_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Take action on early warning alert
    
    - **action**: acknowledge, assign, resolve, escalate, mark_false_positive
    """
    try:
        alert = service.take_alert_action(alert_id, request, current_user["user_id"])
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        
        return success_response(
            data=schemas.EarlyWarningAlertResponse.model_validate(alert),
            message=f"Alert {request.action} successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ews/alerts/statistics", response_model=dict)
async def get_ews_alert_statistics(
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    Get early warning alert statistics
    
    Returns counts by status, severity, category, and resolution metrics
    """
    try:
        stats = service.get_ews_alert_stats()
        return success_response(
            data=stats.model_dump(),
            message="Alert statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/ews/detect/{loan_account_id}", response_model=dict)
async def detect_early_warnings(
    loan_account_id: int,
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    Detect and create early warning alerts for a loan account
    
    Evaluates all active EWS signals against the account
    """
    try:
        alerts = service.detect_early_warnings(loan_account_id)
        return success_response(
            data={"alerts_created": len(alerts), "alert_ids": [a.id for a in alerts]},
            message=f"{len(alerts)} early warning alert(s) detected"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Dashboard & Analytics Endpoints
# ============================================

@router.get("/dashboard/summary", response_model=dict)
async def get_risk_dashboard_summary(
    service: RiskManagementService = Depends(get_risk_service)
):
    """
    Get risk management dashboard summary
    
    Aggregates key metrics across all risk areas
    """
    try:
        # Get statistics from each area
        rating_stats = service.get_risk_rating_stats()
        alert_stats = service.get_ews_alert_stats()
        
        # Get exposure limits summary
        exposure_limits = service.list_exposure_limits(page=1, page_size=1000)
        breached_limits = sum(1 for limit in exposure_limits.items if limit.is_breached)
        high_utilization = sum(1 for limit in exposure_limits.items if limit.utilization_percentage >= 75)
        
        summary = {
            "risk_ratings": rating_stats.model_dump(),
            "early_warning_alerts": alert_stats.model_dump(),
            "exposure_limits": {
                "total_limits": exposure_limits.total,
                "breached_limits": breached_limits,
                "high_utilization_limits": high_utilization
            }
        }
        
        return success_response(
            data=summary,
            message="Risk dashboard summary retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
