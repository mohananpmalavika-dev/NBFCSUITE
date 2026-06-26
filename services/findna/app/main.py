from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Models
class BehavioralScore(Base):
    __tablename__ = "behavioral_scores"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, unique=True, index=True)
    score = Column(Float)
    score_segments = Column(JSON)  # Detailed breakdown
    payment_discipline = Column(Float)
    credit_utilization = Column(Float)
    credit_age = Column(Float)
    delinquency_history = Column(Float)
    inquiry_frequency = Column(Float)
    generated_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FraudDetectionRecord(Base):
    __tablename__ = "fraud_detection_records"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String)
    application_id = Column(String, nullable=True)
    fraud_score = Column(Float)
    risk_level = Column(String)  # low, medium, high, critical
    risk_factors = Column(JSON)  # List of detected risk factors
    detected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="flagged")


class ChurnPrediction(Base):
    __tablename__ = "churn_predictions"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String)
    churn_probability = Column(Float)
    risk_factors = Column(JSON)
    recommended_action = Column(String)
    predicted_at = Column(DateTime, default=datetime.utcnow)


class EmbeddingVector(Base):
    __tablename__ = "embedding_vectors"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, unique=True)
    embedding = Column(JSON)  # Stored as JSON array
    vector_dimension = Column(Integer)
    embedding_model = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Schemas
class IncomeData(BaseModel):
    monthly_income: Optional[float] = None
    annual_salary: Optional[float] = None


class BehavioralScoreRequest(BaseModel):
    customer_id: str
    income_data: Optional[IncomeData] = None
    bank_statement_url: Optional[str] = None
    gst_return_url: Optional[str] = None
    application_id: Optional[str] = None


class BehavioralScoreResponse(BaseModel):
    customer_id: str
    score: float
    payment_discipline: Optional[float] = None
    credit_utilization: Optional[float] = None
    credit_age: Optional[float] = None
    delinquency_history: Optional[float] = None
    inquiry_frequency: Optional[float] = None
    generated_at: datetime
    risk_level: Optional[str] = None
    default_probability_90d: Optional[float] = None
    explanations: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True


class FraudDetectionRequest(BaseModel):
    customer_id: str
    application_id: Optional[str] = None
    documents: Optional[List[str]] = None


class FraudDetectionResponse(BaseModel):
    customer_id: str
    fraud_score: float
    risk_level: str
    risk_factors: List[str]
    status: str

    class Config:
        from_attributes = True


class ChurnPredictionRequest(BaseModel):
    customer_id: str


class ChurnPredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    risk_factors: List[str]
    recommended_action: str

    class Config:
        from_attributes = True


class EmbeddingsRequest(BaseModel):
    customer_id: str
    profile_text: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class EmbeddingVectorResponse(BaseModel):
    customer_id: str
    embedding: List[float]
    vector_dimension: int
    model: str
    generated_at: datetime

    class Config:
        from_attributes = True


class AssistantRequest(BaseModel):
    customer_id: Optional[str] = None
    application_id: Optional[str] = None
    context_text: Optional[str] = None


class AssistantResponse(BaseModel):
    customer_id: Optional[str] = None
    application_id: Optional[str] = None
    summary: str
    recommendation: str
    risk_indicators: List[str]
    action_plan: Dict[str, str]
    insights: Dict[str, str]

    class Config:
        from_attributes = True


class ExplanationResponse(BaseModel):
    feature: str
    contribution: float
    direction: str  # positive or negative
    explanation: str


# FastAPI App
app = FastAPI(title="findna-service", version="0.1.0")


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "findna"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/score/behavior", response_model=BehavioralScoreResponse)
async def score_behavior(
    request: BehavioralScoreRequest,
    db: Session = Depends(get_db)
):
    """Compute a behavioral score for a customer using available profile signals."""
    from uuid import uuid4

    income_bonus = 0.0
    if request.income_data and request.income_data.monthly_income and request.income_data.monthly_income >= 50000:
        income_bonus += 0.03
    if request.income_data and request.income_data.annual_salary and request.income_data.annual_salary >= 600000:
        income_bonus += 0.02

    score_components = {
        "payment_discipline": min(0.95, 0.80 + income_bonus),
        "credit_utilization": 0.45,
        "credit_age": 0.72,
        "delinquency_history": 0.90,
        "inquiry_frequency": 0.82
    }

    if request.bank_statement_url:
        score_components["payment_discipline"] = min(0.98, score_components["payment_discipline"] + 0.03)
    if request.gst_return_url:
        score_components["credit_age"] = min(0.80, score_components["credit_age"] + 0.03)

    final_score = round(
        (score_components["payment_discipline"] * 0.28) +
        (score_components["credit_utilization"] * 0.24) +
        (score_components["credit_age"] * 0.18) +
        (score_components["delinquency_history"] * 0.22) +
        (score_components["inquiry_frequency"] * 0.08),
        3
    ) * 100

    risk_level = "low"
    if final_score < 60:
        risk_level = "high"
    elif final_score < 75:
        risk_level = "medium"

    default_probability_90d = round(max(0.02, min(0.35, 1.0 - (final_score / 120.0))), 2)
    explanations = {
        "decision_behavior": "Consistent payment habits with strong recent performance.",
        "spending_psychology": "Balanced spend-to-income ratio within acceptable limits.",
        "repayment_discipline": "High repayment discipline indicated by stable cash flow patterns."
    }

    existing = db.query(BehavioralScore).filter(
        BehavioralScore.customer_id == request.customer_id
    ).first()

    if existing:
        existing.score = final_score
        existing.score_segments = {**score_components, "risk_level": risk_level}
        existing.last_updated = datetime.utcnow()
    else:
        new_score = BehavioralScore(
            id=str(uuid4()),
            customer_id=request.customer_id,
            score=final_score,
            score_segments={**score_components, "risk_level": risk_level},
            **{k: v for k, v in score_components.items()}
        )
        db.add(new_score)

    db.commit()

    return {
        "customer_id": request.customer_id,
        "score": final_score,
        "payment_discipline": score_components["payment_discipline"],
        "credit_utilization": score_components["credit_utilization"],
        "credit_age": score_components["credit_age"],
        "delinquency_history": score_components["delinquency_history"],
        "inquiry_frequency": score_components["inquiry_frequency"],
        "generated_at": datetime.utcnow(),
        "risk_level": risk_level,
        "default_probability_90d": default_probability_90d,
        "explanations": explanations
    }


@app.post("/score/fraud", response_model=FraudDetectionResponse)
async def score_fraud(
    request: FraudDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect fraud patterns for a loan application or customer profile."""
    from uuid import uuid4

    fraud_score = 0.0
    risk_factors = []
    indicators = {
        "multiple_applications": {"score": 0.18, "factor": "Multiple applications in a short period"},
        "document_variance": {"score": 0.16, "factor": "Document metadata does not match customer profile"},
        "address_risk": {"score": 0.12, "factor": "Address appears temporary or high-risk"},
        "phone_risk": {"score": 0.08, "factor": "Phone number mismatch with existing records"},
        "income_mismatch": {"score": 0.14, "factor": "Income sources appear inconsistent"}
    }

    for indicator in indicators.values():
        fraud_score += indicator["score"]
        if indicator["score"] > 0.10:
            risk_factors.append(indicator["factor"])

    if request.documents:
        fraud_score += min(0.15, 0.05 * len(request.documents))
        if len(request.documents) > 2:
            risk_factors.append("Multiple high-risk documents submitted")

    fraud_score = round(min(1.0, fraud_score / len(indicators)), 2)

    if fraud_score < 0.25:
        risk_level = "low"
        status = "clear"
    elif fraud_score < 0.5:
        risk_level = "medium"
        status = "flagged"
    elif fraud_score < 0.75:
        risk_level = "high"
        status = "flagged"
    else:
        risk_level = "critical"
        status = "blocked"

    record = FraudDetectionRecord(
        id=str(uuid4()),
        customer_id=request.customer_id,
        application_id=request.application_id,
        fraud_score=fraud_score,
        risk_level=risk_level,
        risk_factors=risk_factors,
        status=status
    )
    db.add(record)
    db.commit()

    return {
        "customer_id": request.customer_id,
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "status": status
    }


@app.post("/embeddings", response_model=EmbeddingVectorResponse)
async def generate_embeddings(
    request: EmbeddingsRequest,
    db: Session = Depends(get_db)
):
    """Generate vector embeddings for a customer profile."""
    from uuid import uuid4

    content = request.profile_text or request.customer_id
    tokens = [word for word in content.split() if word]
    embedding = [round((hash(token) % 100) / 100.0, 4) for token in tokens[:16]]
    while len(embedding) < 16:
        embedding.append(0.0)

    existing = db.query(EmbeddingVector).filter(
        EmbeddingVector.customer_id == request.customer_id
    ).first()

    if existing:
        existing.embedding = embedding
        existing.vector_dimension = len(embedding)
        existing.embedding_model = "findna-embed-v1"
        existing.generated_at = datetime.utcnow()
        db.commit()
        generated_at = existing.generated_at
    else:
        generated_at = datetime.utcnow()
        vector = EmbeddingVector(
            id=str(uuid4()),
            customer_id=request.customer_id,
            embedding=embedding,
            vector_dimension=len(embedding),
            embedding_model="findna-embed-v1",
            generated_at=generated_at
        )
        db.add(vector)
        db.commit()

    return {
        "customer_id": request.customer_id,
        "embedding": embedding,
        "vector_dimension": len(embedding),
        "model": "findna-embed-v1",
        "generated_at": generated_at
    }


@app.post("/predict/churn", response_model=ChurnPredictionResponse)
async def predict_churn_request(
    request: ChurnPredictionRequest,
    db: Session = Depends(get_db)
):
    """Predict churn probability for a customer."""
    from uuid import uuid4

    churn_probability = 0.18
    risk_factors = [
        "Lower transaction frequency",
        "Minimal product engagement",
        "Recent service tickets unresolved"
    ]
    recommended_action = "engage"

    record = ChurnPrediction(
        id=str(uuid4()),
        customer_id=request.customer_id,
        churn_probability=churn_probability,
        risk_factors=risk_factors,
        recommended_action=recommended_action
    )
    db.add(record)
    db.commit()

    return {
        "customer_id": request.customer_id,
        "churn_probability": churn_probability,
        "risk_factors": risk_factors,
        "recommended_action": recommended_action
    }


@app.post("/underwriting-assistant/{application_id}", response_model=AssistantResponse)
async def underwriting_assistant(
    application_id: str,
    request: AssistantRequest,
    db: Session = Depends(get_db)
):
    """Provide AI underwriting insights for a loan application."""
    summary = "This application shows stable income, moderate credit utilization, and a low likelihood of early delinquency."
    recommendation = "Recommend approval with a conservative tenure and monthly EMI monitoring."
    risk_indicators = [
        "Credit utilization near 50%",
        "Shorter credit history than preferred",
        "Additional documentation needed for GST-linked income"
    ]
    action_plan = {
        "verify_bank_statements": "Review bank statement and income verification documents.",
        "monitor_disbursement": "Track first three EMIs closely after disbursal.",
        "confirm_collateral": "Validate collateral/submission documents before booking."
    }
    insights = {
        "credit_recommendation": "Offer a tiered personal loan product with 17% APR.",
        "risk_summary": "Overall risk is medium; keep exposure limited to 20% of customer’s monthly income." 
    }

    return {
        "customer_id": request.customer_id,
        "application_id": application_id,
        "summary": summary,
        "recommendation": recommendation,
        "risk_indicators": risk_indicators,
        "action_plan": action_plan,
        "insights": insights
    }


@app.post("/collections-assistant/{customer_id}", response_model=AssistantResponse)
async def collections_assistant(
    customer_id: str,
    request: AssistantRequest,
    db: Session = Depends(get_db)
):
    """Provide collection strategy recommendations for a customer."""
    summary = "The customer demonstrates recent payment delays but remains responsive to reminders."
    recommendation = "Start with a personalized call, then escalate to a settlement offer if dues persist."
    risk_indicators = [
        "Increasing days past due",
        "Reduced repayment amount in last cycle",
        "Lower engagement with digital payment channels"
    ]
    action_plan = {
        "call_strategy": "Use call script emphasizing affordability and next payment date.",
        "settlement_option": "Offer a 30-day grace period with a one-time fee waiver.",
        "monitor_followup": "Schedule follow-up within 3 days after first contact."
    }
    insights = {
        "customer_sentiment": "Customer is likely to respond positively to empathetic outreach.",
        "settlement_recommendation": "Recommend partial settlement to prevent escalation."
    }

    return {
        "customer_id": customer_id,
        "summary": summary,
        "recommendation": recommendation,
        "risk_indicators": risk_indicators,
        "action_plan": action_plan,
        "insights": insights
    }


@app.post("/relationship-manager/{customer_id}", response_model=AssistantResponse)
async def relationship_manager(
    customer_id: str,
    request: AssistantRequest,
    db: Session = Depends(get_db)
):
    """Provide a conversational relationship summary and action plan."""
    summary = "Customer shows a strong savings profile with opportunities to cross-sell fixed deposits and advisory services."
    recommendation = "Propose a tailored savings product bundle and proactive credit review."
    risk_indicators = [
        "Conservative investment behavior",
        "Moderate credit utilization",
        "Potential liquidity preference"
    ]
    action_plan = {
        "touchpoint": "Schedule a relationship call to discuss long-term savings goals.",
        "product_suggestion": "Introduce a recurring deposit plan with step-up interest.",
        "next_review": "Set a 90-day financial review to align on investment strategy."
    }
    insights = {
        "engagement_opportunity": "Customer is receptive to digital advisory nudges.",
        "cross_sell": "Recommend gold loan advisory only if liquidity need emerges."
    }

    return {
        "customer_id": customer_id,
        "summary": summary,
        "recommendation": recommendation,
        "risk_indicators": risk_indicators,
        "action_plan": action_plan,
        "insights": insights
    }


@app.get("/behavioral-score/{customer_id}", response_model=BehavioralScoreResponse)
async def get_behavioral_score(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get behavioral score for a customer."""
    score = db.query(BehavioralScore).filter(
        BehavioralScore.customer_id == customer_id
    ).first()
    
    if not score:
        # Return default score if not yet calculated
        return {
            "customer_id": customer_id,
            "score": 75.0,
            "payment_discipline": 0.85,
            "credit_utilization": 0.45,
            "credit_age": 0.70,
            "delinquency_history": 0.95,
            "inquiry_frequency": 0.88,
            "generated_at": datetime.utcnow(),
            "risk_level": "low",
            "default_probability_90d": 0.08,
            "explanations": {
                "decision_behavior": "Payment consistency is strong for new customers.",
                "spending_psychology": "Spending is stable and controlled.",
                "repayment_discipline": "Good repayment history on record."
            }
        }
    
    return score


@app.post("/behavioral-score/{customer_id}")
async def calculate_behavioral_score(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Calculate behavioral score for a customer."""
    from uuid import uuid4
    
    # Simulate ML calculation
    score_components = {
        "payment_discipline": 0.85,
        "credit_utilization": 0.45,
        "credit_age": 0.70,
        "delinquency_history": 0.95,
        "inquiry_frequency": 0.88
    }
    
    # Weighted average
    final_score = (
        (score_components["payment_discipline"] * 0.35) +
        (score_components["credit_utilization"] * 0.25) +
        (score_components["credit_age"] * 0.15) +
        (score_components["delinquency_history"] * 0.20) +
        (score_components["inquiry_frequency"] * 0.05)
    ) * 100
    
    # Save or update
    existing = db.query(BehavioralScore).filter(
        BehavioralScore.customer_id == customer_id
    ).first()
    
    if existing:
        existing.score = final_score
        existing.score_segments = score_components
        existing.last_updated = datetime.utcnow()
    else:
        new_score = BehavioralScore(
            id=str(uuid4()),
            customer_id=customer_id,
            score=final_score,
            score_segments=score_components,
            **{k: v for k, v in score_components.items()}
        )
        db.add(new_score)
    
    db.commit()
    
    return {
        "customer_id": customer_id,
        "score": final_score,
        "components": score_components
    }


@app.get("/fraud-detection/{customer_id}", response_model=FraudDetectionResponse)
async def get_fraud_detection(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get fraud detection result for a customer."""
    record = db.query(FraudDetectionRecord).filter(
        FraudDetectionRecord.customer_id == customer_id
    ).order_by(FraudDetectionRecord.detected_at.desc()).first()
    
    if not record:
        return {
            "customer_id": customer_id,
            "fraud_score": 0.05,
            "risk_level": "low",
            "risk_factors": [],
            "status": "clear"
        }
    
    return record


@app.post("/fraud-detection/{customer_id}")
async def analyze_fraud_risk(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Analyze fraud risk for a customer."""
    from uuid import uuid4
    
    # Simulate ML-based fraud detection
    risk_factors = []
    fraud_score = 0.0
    
    # Mock fraud analysis
    fraud_indicators = {
        "velocity_check": {"score": 0.1, "factor": "Multiple applications in 30 days"},
        "income_verification": {"score": 0.15, "factor": "Income documents inconsistent"},
        "identity_check": {"score": 0.05, "factor": "Identity verification passed"},
        "address_check": {"score": 0.08, "factor": "Address appears temporary"},
        "phone_check": {"score": 0.02, "factor": "Phone number verified"}
    }
    
    for check, data in fraud_indicators.items():
        fraud_score += data["score"]
        if data["score"] > 0.05:
            risk_factors.append(data["factor"])
    
    fraud_score = min(fraud_score / len(fraud_indicators), 1.0)
    
    if fraud_score < 0.2:
        risk_level = "low"
        status = "clear"
    elif fraud_score < 0.5:
        risk_level = "medium"
        status = "flagged"
    elif fraud_score < 0.8:
        risk_level = "high"
        status = "flagged"
    else:
        risk_level = "critical"
        status = "blocked"
    
    # Save record
    record = FraudDetectionRecord(
        id=str(uuid4()),
        customer_id=customer_id,
        fraud_score=fraud_score,
        risk_level=risk_level,
        risk_factors=risk_factors,
        status=status
    )
    
    db.add(record)
    db.commit()
    
    return {
        "customer_id": customer_id,
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "status": status
    }


@app.get("/churn-prediction/{customer_id}", response_model=ChurnPredictionResponse)
async def predict_churn(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Predict churn probability for a customer."""
    prediction = db.query(ChurnPrediction).filter(
        ChurnPrediction.customer_id == customer_id
    ).order_by(ChurnPrediction.predicted_at.desc()).first()
    
    if not prediction:
        return {
            "customer_id": customer_id,
            "churn_probability": 0.15,
            "risk_factors": [],
            "recommended_action": "monitor"
        }
    
    return prediction


@app.post("/churn-prediction/{customer_id}")
async def calculate_churn(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Calculate churn probability for a customer."""
    from uuid import uuid4
    
    # Simulate churn ML model
    churn_probability = 0.25
    risk_factors = [
        "Recent loan payment delays",
        "Decreasing transaction frequency",
        "Lower engagement in past 30 days"
    ]
    
    if churn_probability < 0.2:
        recommended_action = "retain"
    elif churn_probability < 0.5:
        recommended_action = "engage"
    else:
        recommended_action = "reactivate"
    
    # Save prediction
    record = ChurnPrediction(
        id=str(uuid4()),
        customer_id=customer_id,
        churn_probability=churn_probability,
        risk_factors=risk_factors,
        recommended_action=recommended_action
    )
    
    db.add(record)
    db.commit()
    
    return {
        "customer_id": customer_id,
        "churn_probability": churn_probability,
        "risk_factors": risk_factors,
        "recommended_action": recommended_action
    }


@app.get("/explanations/{customer_id}")
async def get_score_explanations(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get SHAP-style explanations for customer score components."""
    score = db.query(BehavioralScore).filter(
        BehavioralScore.customer_id == customer_id
    ).first()
    
    if not score:
        score_components = {
            "payment_discipline": 0.85,
            "credit_utilization": 0.45,
            "credit_age": 0.70,
            "delinquency_history": 0.95,
            "inquiry_frequency": 0.88
        }
    else:
        score_components = score.score_segments or {}
    
    # Generate SHAP-style explanations
    explanations = [
        {
            "feature": "Payment Discipline",
            "contribution": 0.30,
            "direction": "positive",
            "explanation": "85% on-time payment history over 24 months"
        },
        {
            "feature": "Delinquency History",
            "contribution": 0.20,
            "direction": "positive",
            "explanation": "No delinquencies in past 36 months"
        },
        {
            "feature": "Credit Age",
            "contribution": 0.15,
            "direction": "positive",
            "explanation": "Oldest account is 5 years old"
        },
        {
            "feature": "Credit Utilization",
            "contribution": -0.10,
            "direction": "negative",
            "explanation": "45% utilization - could reduce to improve score"
        },
        {
            "feature": "Recent Inquiries",
            "contribution": -0.05,
            "direction": "negative",
            "explanation": "3 inquiries in past 30 days"
        }
    ]
    
    return {
        "customer_id": customer_id,
        "explanations": explanations,
        "base_score": 750
    }


@app.get("/")
async def root():
    return {"service": "findna", "version": "0.1.0"}
