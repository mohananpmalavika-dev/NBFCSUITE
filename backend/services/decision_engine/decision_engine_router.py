"""
Decision Engine REST API Router
Endpoints for instant decision framework
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from backend.shared.database import get_db
from backend.shared.auth import get_current_user, get_current_tenant
from .decision_engine_service import DecisionEngineService
from .decision_engine_models import (
    DecisionRequest, DecisionRequestCreate, DecisionStatus, DecisionOutcome
)

router = APIRouter(prefix="/api/decision-engine", tags=["Decision Engine"])


# =====================================================================
# DECISION PROCESSING
# =====================================================================

@router.post("/decisions", response_model=dict)
async def submit_decision_request(
    request_data: DecisionRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Submit a new decision request for instant processing
    
    This endpoint processes loan applications in real-time with parallel checks:
    - Bureau credit check (CIBIL, Experian, Equifax)
    - Bank statement AI analysis
    - KYC verification (Aadhaar, PAN)
    - Fraud detection (device, geo, velocity)
    - Eligibility rules validation
    
    Target processing time: < 60 seconds
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        decision = await service.process_decision(request_data, UUID(current_user["id"]))
        
        return {
            "success": True,
            "message": "Decision processed successfully",
            "data": {
                "id": str(decision.id),
                "application_id": str(decision.application_id),
                "decision_outcome": decision.decision_outcome.value,
                "decision_score": decision.decision_score,
                "confidence_score": decision.confidence_score,
                "approved_amount": decision.approved_amount,
                "approved_rate": decision.approved_rate,
                "decline_reasons": decision.decline_reasons,
                "conditions": decision.conditions,
                "requires_manual_review": decision.requires_manual_review,
                "total_duration_ms": decision.total_duration_ms,
                "passed_checks": decision.passed_checks,
                "failed_checks": decision.failed_checks,
                "warning_checks": decision.warning_checks
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/decisions/{decision_id}/rerun", response_model=dict)
async def rerun_decision(
    decision_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Rerun an existing decision with the same inputs
    
    Useful for:
    - Testing decision logic changes
    - Comparing results after policy updates
    - Manual review reprocessing
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        decision = await service.rerun_decision(decision_id, UUID(current_user["id"]))
        
        return {
            "success": True,
            "message": "Decision rerun completed",
            "data": {
                "id": str(decision.id),
                "original_decision_id": str(decision_id),
                "decision_outcome": decision.decision_outcome.value,
                "decision_score": decision.decision_score,
                "approved_amount": decision.approved_amount
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================================
# DECISION RETRIEVAL
# =====================================================================

@router.get("/decisions", response_model=dict)
def list_decisions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    outcome: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    List decision requests with filters
    
    Filters:
    - status: IN_PROGRESS, COMPLETED, FAILED
    - outcome: APPROVED, APPROVED_WITH_CONDITIONS, DECLINED, MANUAL_REVIEW
    - customer_id: Filter by customer
    - from_date/to_date: Date range filter
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        
        # Convert string enums
        status_enum = DecisionStatus(status) if status else None
        outcome_enum = DecisionOutcome(outcome) if outcome else None
        
        decisions = service.list_decisions(
            skip=skip,
            limit=limit,
            status=status_enum,
            outcome=outcome_enum,
            customer_id=customer_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return {
            "success": True,
            "data": [
                {
                    "id": str(d.id),
                    "application_id": str(d.application_id),
                    "customer_id": str(d.customer_id),
                    "product_id": str(d.product_id),
                    "loan_amount": d.loan_amount,
                    "tenure_months": d.tenure_months,
                    "status": d.status.value,
                    "decision_outcome": d.decision_outcome.value if d.decision_outcome else None,
                    "decision_score": d.decision_score,
                    "confidence_score": d.confidence_score,
                    "approved_amount": d.approved_amount,
                    "approved_rate": d.approved_rate,
                    "requires_manual_review": d.requires_manual_review,
                    "request_time": d.request_time.isoformat(),
                    "total_duration_ms": d.total_duration_ms
                }
                for d in decisions
            ],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": len(decisions)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/decisions/{decision_id}", response_model=dict)
def get_decision(
    decision_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Get decision details by ID
    
    Returns basic decision information without detailed check results.
    Use /decisions/{id}/details for complete information.
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        decision = service.get_decision(decision_id)
        
        if not decision:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        return {
            "success": True,
            "data": {
                "id": str(decision.id),
                "application_id": str(decision.application_id),
                "customer_id": str(decision.customer_id),
                "product_id": str(decision.product_id),
                "loan_amount": decision.loan_amount,
                "tenure_months": decision.tenure_months,
                "purpose": decision.purpose,
                "status": decision.status.value,
                "decision_outcome": decision.decision_outcome.value if decision.decision_outcome else None,
                "decision_score": decision.decision_score,
                "confidence_score": decision.confidence_score,
                "approved_amount": decision.approved_amount,
                "approved_rate": decision.approved_rate,
                "decline_reasons": decision.decline_reasons,
                "conditions": decision.conditions,
                "requires_manual_review": decision.requires_manual_review,
                "manual_review_reason": decision.manual_review_reason,
                "fraud_score": decision.fraud_score,
                "fraud_risk_level": decision.fraud_risk_level.value if decision.fraud_risk_level else None,
                "fraud_indicators": decision.fraud_indicators,
                "total_checks": decision.total_checks,
                "passed_checks": decision.passed_checks,
                "failed_checks": decision.failed_checks,
                "warning_checks": decision.warning_checks,
                "request_time": decision.request_time.isoformat(),
                "start_time": decision.start_time.isoformat() if decision.start_time else None,
                "end_time": decision.end_time.isoformat() if decision.end_time else None,
                "total_duration_ms": decision.total_duration_ms,
                "applicant_data": decision.applicant_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/decisions/{decision_id}/details", response_model=dict)
def get_decision_details(
    decision_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Get complete decision details with all check results
    
    Includes:
    - Main decision record
    - Bureau check results
    - Bank statement analysis
    - KYC verification results
    - Fraud check results
    - Eligibility check results
    - Complete audit trail
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        details = service.get_decision_details(decision_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        decision = details["decision"]
        
        return {
            "success": True,
            "data": {
                "decision": {
                    "id": str(decision.id),
                    "application_id": str(decision.application_id),
                    "customer_id": str(decision.customer_id),
                    "decision_outcome": decision.decision_outcome.value if decision.decision_outcome else None,
                    "decision_score": decision.decision_score,
                    "confidence_score": decision.confidence_score,
                    "approved_amount": decision.approved_amount,
                    "approved_rate": decision.approved_rate,
                    "decline_reasons": decision.decline_reasons,
                    "conditions": decision.conditions
                },
                "bureau_checks": [
                    {
                        "id": str(b.id),
                        "bureau_provider": b.bureau_provider.value,
                        "status": b.status.value,
                        "result": b.result.value if b.result else None,
                        "credit_score": b.credit_score,
                        "total_accounts": b.total_accounts,
                        "active_accounts": b.active_accounts,
                        "total_outstanding": b.total_outstanding,
                        "credit_utilization": b.credit_utilization,
                        "max_dpd_last_12m": b.max_dpd_last_12m,
                        "enquiries_last_6m": b.enquiries_last_6m,
                        "duration_ms": b.duration_ms
                    }
                    for b in details["bureau_checks"]
                ],
                "bank_analysis": [
                    {
                        "id": str(ba.id),
                        "status": ba.status.value,
                        "result": ba.result.value if ba.result else None,
                        "bank_name": ba.bank_name,
                        "statement_period_months": ba.statement_period_months,
                        "average_monthly_credit": ba.average_monthly_credit,
                        "salary_amount": ba.salary_amount,
                        "salary_regularity_score": ba.salary_regularity_score,
                        "average_monthly_debit": ba.average_monthly_debit,
                        "emi_deductions": ba.emi_deductions,
                        "bounced_cheques_count": ba.bounced_cheques_count,
                        "banking_behavior_score": ba.banking_behavior_score,
                        "calculated_monthly_income": ba.calculated_monthly_income,
                        "calculated_dti": ba.calculated_dti,
                        "duration_ms": ba.duration_ms
                    }
                    for ba in details["bank_analysis"]
                ],
                "kyc_verification": [
                    {
                        "id": str(k.id),
                        "status": k.status.value,
                        "result": k.result.value if k.result else None,
                        "aadhaar_verified": k.aadhaar_verified,
                        "aadhaar_name_match": k.aadhaar_name_match,
                        "pan_verified": k.pan_verified,
                        "pan_name_match": k.pan_name_match,
                        "address_verified": k.address_verified,
                        "employment_verified": k.employment_verified,
                        "kyc_score": k.kyc_score,
                        "duration_ms": k.duration_ms
                    }
                    for k in details["kyc_verification"]
                ],
                "fraud_checks": [
                    {
                        "id": str(f.id),
                        "status": f.status.value,
                        "result": f.result.value if f.result else None,
                        "device_id": f.device_id,
                        "device_type": f.device_type,
                        "device_risk_score": f.device_risk_score,
                        "ip_address": f.ip_address,
                        "geo_country": f.geo_country,
                        "geo_state": f.geo_state,
                        "geo_city": f.geo_city,
                        "applications_last_24h": f.applications_last_24h,
                        "applications_last_7d": f.applications_last_7d,
                        "applications_last_30d": f.applications_last_30d,
                        "duplicate_applications": f.duplicate_applications,
                        "blacklisted": f.blacklisted,
                        "fraud_score": f.fraud_score,
                        "fraud_risk_level": f.fraud_risk_level.value if f.fraud_risk_level else None,
                        "fraud_indicators": f.fraud_indicators,
                        "duration_ms": f.duration_ms
                    }
                    for f in details["fraud_checks"]
                ],
                "eligibility_checks": [
                    {
                        "id": str(e.id),
                        "status": e.status.value,
                        "result": e.result.value if e.result else None,
                        "age": e.age,
                        "age_eligible": e.age_eligible,
                        "monthly_income": e.monthly_income,
                        "income_eligible": e.income_eligible,
                        "dti_ratio": e.dti_ratio,
                        "dti_eligible": e.dti_eligible,
                        "employment_type": e.employment_type,
                        "employment_eligible": e.employment_eligible,
                        "credit_score": e.credit_score,
                        "credit_score_eligible": e.credit_score_eligible,
                        "overall_eligible": e.overall_eligible,
                        "failed_criteria": e.failed_criteria,
                        "eligibility_score": e.eligibility_score,
                        "duration_ms": e.duration_ms
                    }
                    for e in details["eligibility_checks"]
                ],
                "audit_trail": [
                    {
                        "id": str(a.id),
                        "action": a.action,
                        "details": a.details,
                        "timestamp": a.timestamp.isoformat()
                    }
                    for a in details["audit_trail"]
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/decisions/{decision_id}/audit", response_model=dict)
def get_decision_audit_trail(
    decision_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Get audit trail for a decision
    
    Returns chronological list of all actions taken during decision processing.
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        details = service.get_decision_details(decision_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        return {
            "success": True,
            "data": [
                {
                    "id": str(a.id),
                    "action": a.action,
                    "details": a.details,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in details["audit_trail"]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================================
# ANALYTICS & DASHBOARD
# =====================================================================

@router.get("/dashboard", response_model=dict)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Get dashboard summary with today's statistics
    
    Returns:
    - Today's decision statistics
    - Pending decisions count
    - Decisions requiring manual review
    - Recent decisions (last 10)
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        summary = service.get_dashboard_summary()
        
        return {
            "success": True,
            "data": {
                "today_stats": summary["today_stats"],
                "pending_decisions": summary["pending_decisions"],
                "needs_manual_review": summary["needs_manual_review"],
                "recent_decisions": [
                    {
                        "id": str(d.id),
                        "application_id": str(d.application_id),
                        "customer_id": str(d.customer_id),
                        "loan_amount": d.loan_amount,
                        "decision_outcome": d.decision_outcome.value if d.decision_outcome else None,
                        "decision_score": d.decision_score,
                        "request_time": d.request_time.isoformat()
                    }
                    for d in summary["recent_decisions"]
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=dict)
def get_decision_statistics(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """
    Get decision statistics for a date range
    
    Returns:
    - Total decisions
    - Outcome breakdown (approved, declined, manual review)
    - Approval rate
    - Average scores (decision, confidence)
    - Average processing time
    - Fraud risk distribution
    """
    try:
        service = DecisionEngineService(db, tenant_id)
        stats = service.get_decision_statistics(from_date, to_date)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
