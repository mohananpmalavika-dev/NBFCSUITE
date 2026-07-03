"""
AI Intelligence Routes
Deposit predictions and insights
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from ..database import get_db
from ..schemas import AIDepositPrediction, DepositCopilotQuery
from ..services import AIIntelligenceService

router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


@router.post("/predict-renewal")
def predict_renewal(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Predict renewal probability"""
    try:
        service = AIIntelligenceService(db)
        return service.predict_renewal_probability(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/analyze-churn")
def analyze_churn(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Analyze customer churn risk"""
    service = AIIntelligenceService(db)
    return service.analyze_churn_risk(customer_id)


@router.post("/recommend-product")
def recommend_product(
    customer_id: str,
    amount: float,
    tenure_days: int,
    db: Session = Depends(get_db)
):
    """Recommend best products for customer"""
    service = AIIntelligenceService(db)
    return service.recommend_product(
        customer_id,
        Decimal(str(amount)),
        tenure_days
    )


@router.get("/customer-behavior/{customer_id}")
def get_customer_behavior(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Analyze customer behavioral patterns"""
    service = AIIntelligenceService(db)
    result = service.analyze_customer_behavior(customer_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/copilot")
def deposit_copilot(
    query: DepositCopilotQuery,
    db: Session = Depends(get_db)
):
    """AI Copilot - Natural language deposit queries"""
    service = AIIntelligenceService(db)
    return service.deposit_copilot(query.question, query.context)


@router.get("/insights/renewal-candidates")
def get_renewal_candidates(
    days_ahead: int = 30,
    min_probability: float = 0.7,
    db: Session = Depends(get_db)
):
    """Get high-probability renewal candidates"""
    from ..engines import MaturityEngine
    
    maturity_engine = MaturityEngine(db)
    pipeline = maturity_engine.get_maturity_pipeline(days_ahead)
    
    ai_service = AIIntelligenceService(db)
    candidates = []
    
    for item in pipeline:
        try:
            prediction = ai_service.predict_renewal_probability(item["account_id"])
            
            if prediction["probability"] >= min_probability * 100:
                candidates.append({
                    "account_id": item["account_id"],
                    "account_number": item["account_number"],
                    "customer_id": item["customer_id"],
                    "maturity_date": item["maturity_date"],
                    "maturity_amount": item["maturity_amount"],
                    "renewal_probability": prediction["probability"],
                    "recommendation": prediction["recommendation"]
                })
        except Exception:
            continue
    
    return {
        "total_candidates": len(candidates),
        "candidates": candidates
    }


@router.get("/insights/churn-risk")
def get_churn_risk_customers(
    risk_level: str = "HIGH",
    db: Session = Depends(get_db)
):
    """Get customers at risk of churning"""
    from ..models import DepositAccount
    
    # Get unique customers with active deposits
    customers = db.query(DepositAccount.customer_id).distinct().all()
    
    ai_service = AIIntelligenceService(db)
    at_risk = []
    
    for (customer_id,) in customers[:50]:  # Limit for performance
        try:
            analysis = ai_service.analyze_churn_risk(customer_id)
            
            if analysis["churn_risk"] == risk_level:
                at_risk.append(analysis)
        except Exception:
            continue
    
    return {
        "risk_level": risk_level,
        "count": len(at_risk),
        "customers": at_risk
    }
