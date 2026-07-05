"""
Decision Management Router

API endpoints for decision-making, decision history, and analytics.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .decision_service import DecisionService
from .schemas import (
    DecisionRequest,
    DecisionResponse,
    DecisionResult,
    DecisionOverrideRequest
)

router = APIRouter(prefix="/rules/decisions", tags=["Rule Decisions"])


# ==================== DECISION MAKING ====================

@router.post("", response_model=dict, status_code=201)
def make_decision(
    request: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Make a rule-based decision
    
    Evaluates multiple rules and makes a final decision with confidence score.
    
    **Decision Types**:
    - credit_approval: Loan application approval
    - eligibility_check: Product/service eligibility
    - risk_assessment: Customer risk evaluation
    - fraud_detection: Fraud risk assessment
    - pricing: Dynamic pricing decision
    
    **Example**:
    ```json
    {
      "decision_type": "credit_approval",
      "entity_type": "loan_application",
      "entity_id": 12345,
      "input_data": {
        "customer": {
          "age": 35,
          "monthly_income": 50000,
          "credit_score": 720,
          "existing_loans": 0
        },
        "loan": {
          "amount": 500000,
          "tenure": 36,
          "purpose": "business"
        }
      },
      "category_codes": ["credit_policy", "risk_assessment"]
    }
    ```
    
    **Returns**:
    - decision_id: Unique decision identifier
    - decision_result: approved, rejected, manual_review, pending, error
    - confidence_score: 0-100 (higher = more confident)
    - rules_applied: List of rules evaluated
    - decision_factors: Key factors that influenced decision
    - recommendation: Human-readable recommendation
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    decision = service.make_decision(request)
    
    return success_response(
        message=f"Decision: {decision['decision_result']}",
        data=decision
    )


# ==================== DECISION RETRIEVAL ====================

@router.get("", response_model=dict)
def list_decisions(
    decision_type: Optional[str] = Query(None, description="Filter by decision type"),
    decision_result: Optional[DecisionResult] = Query(None, description="Filter by result"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List decisions with filters
    
    Returns historical decisions ordered by decision time (newest first).
    
    **Filters**:
    - decision_type: Type of decision (credit_approval, eligibility_check, etc.)
    - decision_result: Result (approved, rejected, manual_review, pending, error)
    
    **Use Cases**:
    - Decision audit trail
    - Performance monitoring
    - Compliance reporting
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    decisions = service.list_decisions(
        decision_type=decision_type,
        decision_result=decision_result,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(decisions)} decisions",
        data={
            "decisions": [
                {
                    "id": d.id,
                    "decision_id": str(d.decision_id),
                    "entity_type": d.entity_type,
                    "entity_id": d.entity_id,
                    "decision_type": d.decision_type,
                    "decision_result": d.decision_result,
                    "confidence_score": float(d.confidence_score) if d.confidence_score else None,
                    "override_applied": d.override_applied,
                    "decided_at": d.decided_at.isoformat()
                }
                for d in decisions
            ],
            "total": len(decisions),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{decision_id}", response_model=dict)
def get_decision(
    decision_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get decision details
    
    Returns complete decision information including:
    - Decision result and confidence
    - Rules applied
    - Decision factors
    - Recommendation
    - Override information (if any)
    
    **Use Cases**:
    - Decision review
    - Audit trail investigation
    - Customer explanation
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    decision = service.get_decision(decision_id)
    
    if not decision:
        from backend.shared.common.response import CustomException
        raise CustomException(status_code=404, message="Decision not found")
    
    return success_response(
        message="Decision retrieved successfully",
        data={
            "id": decision.id,
            "decision_id": str(decision.decision_id),
            "entity_type": decision.entity_type,
            "entity_id": decision.entity_id,
            "decision_type": decision.decision_type,
            "decision_result": decision.decision_result,
            "confidence_score": float(decision.confidence_score) if decision.confidence_score else None,
            "rules_applied": decision.rules_applied,
            "decision_factors": decision.decision_factors,
            "recommendation": decision.recommendation,
            "override_applied": decision.override_applied,
            "override_by": decision.override_by,
            "override_reason": decision.override_reason,
            "override_at": decision.override_at.isoformat() if decision.override_at else None,
            "decided_by": decision.decided_by,
            "decided_at": decision.decided_at.isoformat()
        }
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=dict)
def get_entity_decisions(
    entity_type: str,
    entity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all decisions for a specific entity
    
    Returns complete decision history for an entity.
    
    **Example**: Get all decisions for loan application #12345
    ```
    GET /rules/decisions/entity/loan_application/12345
    ```
    
    **Use Cases**:
    - View decision history
    - Audit why decision changed
    - Customer service inquiries
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    decisions = service.get_entity_decisions(
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(decisions)} decisions for {entity_type} #{entity_id}",
        data={
            "entity_type": entity_type,
            "entity_id": entity_id,
            "decisions": [
                {
                    "decision_id": str(d.decision_id),
                    "decision_type": d.decision_type,
                    "decision_result": d.decision_result,
                    "confidence_score": float(d.confidence_score) if d.confidence_score else None,
                    "override_applied": d.override_applied,
                    "decided_at": d.decided_at.isoformat()
                }
                for d in decisions
            ],
            "total": len(decisions)
        }
    )


# ==================== DECISION OVERRIDE ====================

@router.post("/{decision_id}/override", response_model=dict)
def override_decision(
    decision_id: UUID,
    override_request: DecisionOverrideRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Override a decision
    
    Allows authorized users to override automated decisions.
    
    **Use Cases**:
    - Manual approval override for borderline cases
    - Risk-based exceptions
    - Management discretion
    
    **Requirements**:
    - new_result: New decision result
    - reason: Detailed reason for override (minimum 10 characters)
    
    **Note**: This action is logged for audit purposes.
    May require special permissions in production.
    
    **Example**:
    ```json
    {
      "new_result": "approved",
      "reason": "Customer has strong payment history with company. Approved as exception with director authorization."
    }
    ```
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    decision = service.override_decision(decision_id, override_request)
    
    return success_response(
        message="Decision overridden successfully",
        data={
            "decision_id": str(decision.decision_id),
            "original_result": "See decision history",
            "new_result": decision.decision_result,
            "override_by": decision.override_by,
            "override_reason": decision.override_reason,
            "override_at": decision.override_at.isoformat()
        }
    )


# ==================== DECISION ANALYTICS ====================

@router.get("/statistics/summary", response_model=dict)
def get_decision_statistics(
    decision_type: Optional[str] = Query(None, description="Filter by decision type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get decision statistics
    
    Returns aggregated decision metrics including:
    - Total decisions
    - Approval/rejection rates
    - Manual review rate
    - Average confidence score
    - Override rate
    
    **Use Cases**:
    - Performance monitoring
    - Rule effectiveness analysis
    - Business intelligence
    
    **Example Response**:
    ```json
    {
      "decision_type": "credit_approval",
      "total_decisions": 1500,
      "approved": 900,
      "rejected": 450,
      "manual_review": 150,
      "approval_rate": 60.0,
      "rejection_rate": 30.0,
      "manual_review_rate": 10.0,
      "avg_confidence_score": 85.5,
      "override_count": 45,
      "override_rate": 3.0
    }
    ```
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    stats = service.get_decision_statistics(decision_type=decision_type)
    
    return success_response(
        message="Statistics retrieved successfully",
        data=stats
    )


@router.get("/statistics/trends", response_model=dict)
def get_decision_trends(
    decision_type: Optional[str] = Query(None, description="Filter by decision type"),
    days: int = Query(30, ge=1, le=90, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get decision trends over time
    
    Returns daily decision statistics showing trends.
    
    **Use Cases**:
    - Identify approval rate changes
    - Monitor rule performance over time
    - Detect anomalies
    - Capacity planning
    
    **Returns**: Daily breakdown with:
    - Date
    - Approved count
    - Rejected count
    - Manual review count
    - Total decisions
    """
    service = DecisionService(db, tenant_id, current_user["id"])
    trends = service.get_decision_trends(
        decision_type=decision_type,
        days=days
    )
    
    return success_response(
        message=f"Retrieved {len(trends)} days of trend data",
        data={
            "period_days": days,
            "decision_type": decision_type or "all",
            "trends": trends
        }
    )


@router.get("/statistics/confidence-distribution", response_model=dict)
def get_confidence_distribution(
    decision_type: Optional[str] = Query(None, description="Filter by decision type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get confidence score distribution
    
    Returns distribution of confidence scores across decisions.
    
    **Use Cases**:
    - Identify low-confidence decisions
    - Rule tuning insights
    - Quality assessment
    
    **Returns**: Histogram data showing:
    - Confidence ranges (0-20, 21-40, 41-60, 61-80, 81-100)
    - Count in each range
    - Average result for each range
    """
    from sqlalchemy import and_, case, func
    from backend.shared.database.rules_models import RuleDecision
    
    query = db.query(
        case(
            (RuleDecision.confidence_score <= 20, '0-20'),
            (RuleDecision.confidence_score <= 40, '21-40'),
            (RuleDecision.confidence_score <= 60, '41-60'),
            (RuleDecision.confidence_score <= 80, '61-80'),
            else_='81-100'
        ).label('range'),
        func.count(RuleDecision.id).label('count'),
        func.avg(RuleDecision.confidence_score).label('avg_confidence')
    ).filter(
        RuleDecision.tenant_id == tenant_id
    )
    
    if decision_type:
        query = query.filter(RuleDecision.decision_type == decision_type)
    
    query = query.group_by('range').order_by('range')
    
    results = query.all()
    
    distribution = [
        {
            "confidence_range": r.range,
            "count": r.count,
            "avg_confidence": round(float(r.avg_confidence or 0), 2)
        }
        for r in results
    ]
    
    return success_response(
        message="Confidence distribution retrieved",
        data={
            "decision_type": decision_type or "all",
            "distribution": distribution,
            "total_decisions": sum(d["count"] for d in distribution)
        }
    )


# ==================== DECISION REVIEW ====================

@router.get("/review/low-confidence", response_model=dict)
def get_low_confidence_decisions(
    threshold: float = Query(70.0, ge=0, le=100, description="Confidence threshold"),
    decision_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get low confidence decisions for review
    
    Returns decisions with confidence below threshold.
    These may need manual review.
    
    **Use Cases**:
    - Quality control
    - Manual review queue
    - Rule improvement insights
    
    **Default Threshold**: 70%
    """
    from sqlalchemy import and_
    from backend.shared.database.rules_models import RuleDecision
    
    query = db.query(RuleDecision).filter(
        and_(
            RuleDecision.tenant_id == tenant_id,
            RuleDecision.confidence_score < threshold
        )
    )
    
    if decision_type:
        query = query.filter(RuleDecision.decision_type == decision_type)
    
    query = query.order_by(
        RuleDecision.confidence_score.asc(),
        RuleDecision.decided_at.desc()
    )
    
    decisions = query.offset(skip).limit(limit).all()
    
    return success_response(
        message=f"Found {len(decisions)} low confidence decisions",
        data={
            "threshold": threshold,
            "decisions": [
                {
                    "decision_id": str(d.decision_id),
                    "entity_type": d.entity_type,
                    "entity_id": d.entity_id,
                    "decision_type": d.decision_type,
                    "decision_result": d.decision_result,
                    "confidence_score": float(d.confidence_score) if d.confidence_score else 0,
                    "override_applied": d.override_applied,
                    "decided_at": d.decided_at.isoformat()
                }
                for d in decisions
            ],
            "total": len(decisions)
        }
    )


@router.get("/review/overrides", response_model=dict)
def get_overridden_decisions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all overridden decisions
    
    Returns decisions that were manually overridden.
    
    **Use Cases**:
    - Audit overrides
    - Identify patterns in manual interventions
    - Rule improvement insights
    - Compliance reporting
    """
    from sqlalchemy import and_
    from backend.shared.database.rules_models import RuleDecision
    
    decisions = db.query(RuleDecision).filter(
        and_(
            RuleDecision.tenant_id == tenant_id,
            RuleDecision.override_applied == True
        )
    ).order_by(
        RuleDecision.override_at.desc()
    ).offset(skip).limit(limit).all()
    
    return success_response(
        message=f"Retrieved {len(decisions)} overridden decisions",
        data={
            "decisions": [
                {
                    "decision_id": str(d.decision_id),
                    "entity_type": d.entity_type,
                    "entity_id": d.entity_id,
                    "decision_type": d.decision_type,
                    "decision_result": d.decision_result,
                    "override_by": d.override_by,
                    "override_reason": d.override_reason,
                    "override_at": d.override_at.isoformat()
                }
                for d in decisions
            ],
            "total": len(decisions)
        }
    )
