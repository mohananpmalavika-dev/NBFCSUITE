"""
Rule Evaluation Router

API endpoints for rule evaluation, testing, and evaluation history.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .evaluation_service import EvaluationService
from .schemas import (
    EvaluationRequest,
    EvaluationResponse,
    RuleTestRequest,
    RuleTestResponse,
    EvaluationResult
)

router = APIRouter(prefix="/rules", tags=["Rule Evaluation"])


# ==================== RULE EVALUATION ====================

@router.post("/evaluate", response_model=dict)
def evaluate_rules(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Evaluate rules against input data
    
    Evaluates applicable rules and returns results with matched rules and actions.
    
    **Evaluation Strategies**:
    - first_match: Stop at first matching rule (fast)
    - all_match: Evaluate all rules (comprehensive)
    - priority: Evaluate by priority, can stop on critical failure
    - best_match: Evaluate all, return best result
    
    **Example Request**:
    ```json
    {
      "category_code": "credit_policy",
      "entity_type": "loan_application",
      "entity_id": 12345,
      "input_data": {
        "customer": {
          "age": 35,
          "monthly_income": 50000,
          "credit_score": 720
        },
        "loan": {
          "amount": 500000,
          "tenure": 36
        }
      }
    }
    ```
    
    **Returns**:
    - evaluation_id: Unique evaluation identifier
    - total_rules_evaluated: Number of rules checked
    - rules_matched: Number of rules that matched
    - evaluation_results: Detailed results for each rule
    - overall_result: pass/fail/error
    - execution_time_ms: Performance metrics
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    result = service.evaluate_rules(request)
    
    return success_response(
        message=f"Evaluated {result['total_rules_evaluated']} rules, {result['rules_matched']} matched",
        data=result
    )


@router.post("/evaluate-batch", response_model=dict)
def evaluate_rules_batch(
    requests: list[EvaluationRequest],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Batch evaluate multiple entities
    
    Evaluates rules for multiple entities in a single request.
    Useful for bulk processing.
    
    **Use Cases**:
    - Batch loan application processing
    - End-of-day customer eligibility checks
    - Bulk risk assessment
    
    **Returns**: List of evaluation results, one per entity
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    results = []
    
    for request in requests:
        try:
            result = service.evaluate_rules(request)
            results.append({
                "entity_id": request.entity_id,
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "entity_id": request.entity_id,
                "status": "error",
                "error": str(e)
            })
    
    return success_response(
        message=f"Batch evaluation completed for {len(results)} entities",
        data={
            "total_entities": len(requests),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
    )


@router.post("/test", response_model=dict)
def test_rule(
    test_request: RuleTestRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Test a rule with sample data
    
    Tests a single rule without creating permanent evaluation records.
    Useful for:
    - Rule validation during creation
    - Testing rule changes before activation
    - Debugging rule logic
    
    **Example**:
    ```json
    {
      "rule_id": 123,
      "test_data": {
        "customer": {
          "age": 30,
          "income": 40000
        },
        "loan": {
          "amount": 300000
        }
      }
    }
    ```
    
    **Returns**: Evaluation result with execution details
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    result = service.test_rule(
        rule_id=test_request.rule_id,
        test_data=test_request.test_data
    )
    
    return success_response(
        message="Rule test completed",
        data=result
    )


@router.post("/simulate", response_model=dict)
def simulate_rule_changes(
    rule_id: int,
    test_data: dict,
    proposed_changes: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Simulate rule changes
    
    Tests how proposed rule changes would affect evaluation.
    Shows before/after comparison.
    
    **Use Cases**:
    - Impact analysis before rule updates
    - A/B testing different rule configurations
    - Rule optimization
    
    **Note**: This is a read-only operation. No changes are saved.
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    
    # Test current rule
    current_result = service.test_rule(rule_id, test_data)
    
    # TODO: Implement simulation with proposed changes
    # For now, return current result with simulation flag
    
    return success_response(
        message="Simulation completed",
        data={
            "current_result": current_result,
            "proposed_changes": proposed_changes,
            "note": "Full simulation with proposed changes coming soon"
        }
    )


# ==================== EVALUATION HISTORY ====================

@router.get("/evaluations", response_model=dict)
def list_evaluations(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    rule_id: Optional[int] = Query(None, description="Filter by rule"),
    result: Optional[EvaluationResult] = Query(None, description="Filter by result"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List evaluation history
    
    Returns historical evaluations with filters.
    Ordered by evaluation time (newest first).
    
    **Filters**:
    - entity_type: Type of entity evaluated (loan_application, customer, etc.)
    - entity_id: Specific entity ID
    - rule_id: Specific rule
    - result: pass, fail, error
    
    **Use Cases**:
    - Audit trail review
    - Performance analysis
    - Debugging rule behavior
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    evaluations = service.get_evaluations(
        entity_type=entity_type,
        entity_id=entity_id,
        rule_id=rule_id,
        result=result,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(evaluations)} evaluations",
        data={
            "evaluations": [
                {
                    "id": e.id,
                    "evaluation_id": str(e.evaluation_id),
                    "rule_id": e.rule_id,
                    "entity_type": e.entity_type,
                    "entity_id": e.entity_id,
                    "evaluation_result": e.evaluation_result,
                    "matched": e.matched,
                    "execution_time_ms": e.execution_time_ms,
                    "evaluated_at": e.evaluated_at.isoformat()
                }
                for e in evaluations
            ],
            "total": len(evaluations),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/evaluations/{evaluation_id}", response_model=dict)
def get_evaluation_details(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get detailed evaluation information
    
    Returns complete evaluation details including:
    - Input data snapshot
    - Evaluation result
    - Output data
    - Execution time
    - Error details (if any)
    
    **Use Cases**:
    - Debugging specific evaluations
    - Audit trail investigation
    - Performance analysis
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    evaluation = service.get_evaluation_by_id(evaluation_id)
    
    if not evaluation:
        from backend.shared.common.response import CustomException
        raise CustomException(status_code=404, message="Evaluation not found")
    
    return success_response(
        message="Evaluation details retrieved",
        data={
            "id": evaluation.id,
            "evaluation_id": str(evaluation.evaluation_id),
            "rule_id": evaluation.rule_id,
            "entity_type": evaluation.entity_type,
            "entity_id": evaluation.entity_id,
            "input_data": evaluation.input_data,
            "evaluation_result": evaluation.evaluation_result,
            "matched": evaluation.matched,
            "output_data": evaluation.output_data,
            "execution_time_ms": evaluation.execution_time_ms,
            "error_message": evaluation.error_message,
            "evaluated_by": evaluation.evaluated_by,
            "evaluated_at": evaluation.evaluated_at.isoformat()
        }
    )


@router.get("/evaluations/entity/{entity_type}/{entity_id}", response_model=dict)
def get_entity_evaluations(
    entity_type: str,
    entity_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all evaluations for a specific entity
    
    Returns complete evaluation history for an entity (e.g., all rules evaluated for a loan application).
    
    **Example**: Get all evaluations for loan application #12345
    ```
    GET /rules/evaluations/entity/loan_application/12345
    ```
    
    **Use Cases**:
    - View complete decision history
    - Audit why application was approved/rejected
    - Track rule changes over time
    """
    service = EvaluationService(db, tenant_id, current_user["id"])
    evaluations = service.get_evaluations(
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
    
    # Group by evaluation_id (batch evaluations)
    from collections import defaultdict
    grouped = defaultdict(list)
    
    for e in evaluations:
        grouped[str(e.evaluation_id)].append({
            "rule_id": e.rule_id,
            "matched": e.matched,
            "evaluation_result": e.evaluation_result,
            "execution_time_ms": e.execution_time_ms,
            "evaluated_at": e.evaluated_at.isoformat()
        })
    
    return success_response(
        message=f"Retrieved evaluations for {entity_type} #{entity_id}",
        data={
            "entity_type": entity_type,
            "entity_id": entity_id,
            "total_evaluations": len(evaluations),
            "evaluation_groups": [
                {
                    "evaluation_id": eval_id,
                    "rules": rules
                }
                for eval_id, rules in grouped.items()
            ]
        }
    )


# ==================== PERFORMANCE ANALYTICS ====================

@router.get("/analytics/performance", response_model=dict)
def get_performance_analytics(
    rule_id: Optional[int] = Query(None, description="Specific rule"),
    category_id: Optional[int] = Query(None, description="Category"),
    days: int = Query(30, ge=1, le=90, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get rule performance analytics
    
    Returns performance metrics including:
    - Average execution time
    - Match rates
    - Error rates
    - Trend analysis
    
    **Use Cases**:
    - Identify slow rules
    - Monitor rule effectiveness
    - Performance optimization
    """
    from datetime import datetime, timedelta
    from sqlalchemy import and_, func
    from backend.shared.database.rules_models import RuleEvaluation, BusinessRule
    
    service = EvaluationService(db, tenant_id, current_user["id"])
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query = db.query(
        RuleEvaluation.rule_id,
        func.count(RuleEvaluation.id).label('total_evaluations'),
        func.sum(func.cast(RuleEvaluation.matched, db.Integer)).label('total_matches'),
        func.avg(RuleEvaluation.execution_time_ms).label('avg_execution_time'),
        func.max(RuleEvaluation.execution_time_ms).label('max_execution_time'),
        func.min(RuleEvaluation.execution_time_ms).label('min_execution_time')
    ).filter(
        and_(
            RuleEvaluation.tenant_id == tenant_id,
            RuleEvaluation.evaluated_at >= start_date
        )
    )
    
    if rule_id:
        query = query.filter(RuleEvaluation.rule_id == rule_id)
    
    if category_id:
        query = query.join(BusinessRule).filter(BusinessRule.category_id == category_id)
    
    query = query.group_by(RuleEvaluation.rule_id)
    
    results = query.all()
    
    analytics = []
    for r in results:
        match_rate = (r.total_matches / r.total_evaluations * 100) if r.total_evaluations > 0 else 0
        analytics.append({
            "rule_id": r.rule_id,
            "total_evaluations": r.total_evaluations,
            "total_matches": r.total_matches or 0,
            "match_rate": round(match_rate, 2),
            "avg_execution_time_ms": round(float(r.avg_execution_time or 0), 2),
            "max_execution_time_ms": r.max_execution_time,
            "min_execution_time_ms": r.min_execution_time
        })
    
    # Sort by average execution time (slowest first)
    analytics.sort(key=lambda x: x['avg_execution_time_ms'], reverse=True)
    
    return success_response(
        message="Performance analytics retrieved",
        data={
            "period_days": days,
            "analytics": analytics,
            "total_rules_analyzed": len(analytics)
        }
    )


@router.get("/analytics/usage", response_model=dict)
def get_usage_statistics(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get rule usage statistics
    
    Returns:
    - Total evaluations by day
    - Most frequently evaluated rules
    - Success/failure rates
    - Trend analysis
    
    **Use Cases**:
    - Monitor system usage
    - Capacity planning
    - Identify popular rules
    """
    from datetime import datetime, timedelta
    from sqlalchemy import and_, func, cast, Date
    from backend.shared.database.rules_models import RuleEvaluation
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily evaluation counts
    daily_stats = db.query(
        cast(RuleEvaluation.evaluated_at, Date).label('date'),
        func.count(RuleEvaluation.id).label('count'),
        func.sum(func.cast(RuleEvaluation.matched, db.Integer)).label('matched')
    ).filter(
        and_(
            RuleEvaluation.tenant_id == tenant_id,
            RuleEvaluation.evaluated_at >= start_date
        )
    ).group_by(
        cast(RuleEvaluation.evaluated_at, Date)
    ).order_by(
        cast(RuleEvaluation.evaluated_at, Date)
    ).all()
    
    # Format daily stats
    daily_data = [
        {
            "date": str(stat.date),
            "total_evaluations": stat.count,
            "total_matched": stat.matched or 0,
            "match_rate": round((stat.matched or 0) / stat.count * 100, 2) if stat.count > 0 else 0
        }
        for stat in daily_stats
    ]
    
    # Most evaluated rules
    top_rules = db.query(
        RuleEvaluation.rule_id,
        func.count(RuleEvaluation.id).label('count')
    ).filter(
        and_(
            RuleEvaluation.tenant_id == tenant_id,
            RuleEvaluation.evaluated_at >= start_date
        )
    ).group_by(
        RuleEvaluation.rule_id
    ).order_by(
        func.count(RuleEvaluation.id).desc()
    ).limit(10).all()
    
    return success_response(
        message="Usage statistics retrieved",
        data={
            "period_days": days,
            "daily_stats": daily_data,
            "top_rules": [
                {"rule_id": r.rule_id, "evaluation_count": r.count}
                for r in top_rules
            ],
            "summary": {
                "total_evaluations": sum(d["total_evaluations"] for d in daily_data),
                "total_matched": sum(d["total_matched"] for d in daily_data),
                "avg_daily_evaluations": round(sum(d["total_evaluations"] for d in daily_data) / len(daily_data), 2) if daily_data else 0
            }
        }
    )
