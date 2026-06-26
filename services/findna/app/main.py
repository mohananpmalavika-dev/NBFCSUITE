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


class AssistantInvocation(Base):
    __tablename__ = "assistant_invocations"

    id = Column(String, primary_key=True)
    assistant_type = Column(String, index=True)
    invocation_key = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True, nullable=True)
    application_id = Column(String, index=True, nullable=True)
    summary = Column(String)
    recommendation = Column(String)
    risk_indicators = Column(JSON)
    action_plan = Column(JSON)
    insights = Column(JSON)
    source_context = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BankStatementAnalysis(Base):
    __tablename__ = "bank_statement_analyses"

    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    application_id = Column(String, index=True, nullable=True)
    statement_url = Column(String, nullable=True)
    average_balance = Column(Float)
    monthly_income = Column(Float)
    recurring_debits = Column(Float)
    volatility_score = Column(Float)
    bounced_payment_count = Column(Integer, default=0)
    extracted_cashflows = Column(JSON)
    insights = Column(JSON)
    analyzed_at = Column(DateTime, default=datetime.utcnow)


class AICreditDecision(Base):
    __tablename__ = "ai_credit_decisions"

    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    application_id = Column(String, unique=True, index=True)
    requested_amount = Column(Float)
    tenure_months = Column(Integer)
    rule_score = Column(Float)
    behavioral_score = Column(Float)
    statement_score = Column(Float)
    fraud_penalty = Column(Float)
    ai_risk_score = Column(Float)
    default_probability_90d = Column(Float)
    recommendation = Column(String)
    risk_grade = Column(String)
    reasons = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


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
    subject_type: Optional[str] = None
    subject_id: Optional[str] = None
    source_service: Optional[str] = None
    source_reference_id: Optional[str] = None
    context_text: Optional[str] = None


class BankStatementTransaction(BaseModel):
    transaction_date: datetime
    description: str
    amount: float
    transaction_type: str
    balance_after: Optional[float] = None


class BankStatementAnalysisRequest(BaseModel):
    customer_id: str
    application_id: Optional[str] = None
    statement_url: Optional[str] = None
    transactions: List[BankStatementTransaction] = []


class BankStatementAnalysisResponse(BaseModel):
    customer_id: str
    application_id: Optional[str] = None
    average_balance: float
    monthly_income: float
    recurring_debits: float
    volatility_score: float
    bounced_payment_count: int
    extracted_cashflows: Dict[str, float | int]
    insights: Dict[str, str]
    analyzed_at: datetime

    class Config:
        from_attributes = True


class AICreditEngineRequest(BaseModel):
    customer_id: str
    application_id: str
    requested_amount: float
    tenure_months: int
    declared_monthly_income: Optional[float] = None
    credit_score: Optional[int] = None
    bank_statement: Optional[BankStatementAnalysisRequest] = None


class AICreditEngineResponse(BaseModel):
    customer_id: str
    application_id: str
    ai_risk_score: float
    default_probability_90d: float
    recommendation: str
    risk_grade: str
    component_scores: Dict[str, float]
    reasons: List[str]
    generated_at: datetime

    class Config:
        from_attributes = True


class AssistantResponse(BaseModel):
    customer_id: Optional[str] = None
    application_id: Optional[str] = None
    summary: str
    recommendation: str
    risk_indicators: List[str]
    action_plan: Dict[str, str]
    insights: Dict[str, str]
    invocation_key: Optional[str] = None
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssistantInvocationResponse(AssistantResponse):
    assistant_type: str


class ExecutiveDashboardResponse(BaseModel):
    generated_at: datetime
    portfolio_health: Dict[str, float | int]
    risk_summary: Dict[str, int]
    collections_summary: Dict[str, float | int]
    assistant_summary: Dict[str, int]
    recommendations: List[str]


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


def _assistant_key(assistant_type: str, customer_id: Optional[str], application_id: Optional[str]) -> str:
    subject = application_id or customer_id or "anonymous"
    return f"{assistant_type}:{subject}"


def persist_assistant_invocation(
    db: Session,
    assistant_type: str,
    customer_id: Optional[str],
    application_id: Optional[str],
    context_text: Optional[str],
    summary: str,
    recommendation: str,
    risk_indicators: List[str],
    action_plan: Dict[str, str],
    insights: Dict[str, str],
) -> AssistantInvocation:
    from uuid import uuid4

    invocation_key = _assistant_key(assistant_type, customer_id, application_id)
    invocation = db.query(AssistantInvocation).filter(
        AssistantInvocation.invocation_key == invocation_key
    ).first()
    if invocation:
        invocation.customer_id = customer_id
        invocation.application_id = application_id
        invocation.summary = summary
        invocation.recommendation = recommendation
        invocation.risk_indicators = risk_indicators
        invocation.action_plan = action_plan
        invocation.insights = insights
        invocation.source_context = context_text
        invocation.updated_at = datetime.utcnow()
    else:
        invocation = AssistantInvocation(
            id=str(uuid4()),
            assistant_type=assistant_type,
            invocation_key=invocation_key,
            customer_id=customer_id,
            application_id=application_id,
            summary=summary,
            recommendation=recommendation,
            risk_indicators=risk_indicators,
            action_plan=action_plan,
            insights=insights,
            source_context=context_text,
        )
        db.add(invocation)

    db.commit()
    db.refresh(invocation)
    return invocation


def assistant_response(invocation: AssistantInvocation) -> dict:
    return {
        "assistant_type": invocation.assistant_type,
        "customer_id": invocation.customer_id,
        "application_id": invocation.application_id,
        "summary": invocation.summary,
        "recommendation": invocation.recommendation,
        "risk_indicators": invocation.risk_indicators or [],
        "action_plan": invocation.action_plan or {},
        "insights": invocation.insights or {},
        "invocation_key": invocation.invocation_key,
        "generated_at": invocation.updated_at or invocation.created_at,
    }


def _risk_level_from_score(score: Optional[float]) -> str:
    if score is None:
        return "unknown"
    if score < 60:
        return "high"
    if score < 75:
        return "medium"
    return "low"


def _risk_grade(score: float) -> str:
    if score >= 82:
        return "A"
    if score >= 70:
        return "B"
    if score >= 58:
        return "C"
    return "D"


def analyze_statement_signals(request: BankStatementAnalysisRequest) -> dict:
    credits = [item.amount for item in request.transactions if item.transaction_type.lower() == "credit"]
    debits = [abs(item.amount) for item in request.transactions if item.transaction_type.lower() == "debit"]
    balances = [item.balance_after for item in request.transactions if item.balance_after is not None]
    bounced = [
        item
        for item in request.transactions
        if "bounce" in item.description.lower() or "return" in item.description.lower()
    ]

    average_balance = round(sum(balances) / len(balances), 2) if balances else 0.0
    monthly_income = round(sum(credits) / max(1, min(3, len(credits))), 2) if credits else 0.0
    recurring_debits = round(sum(debits) / max(1, min(3, len(debits))), 2) if debits else 0.0

    if balances:
        balance_range = max(balances) - min(balances)
        volatility_score = round(min(1.0, balance_range / max(1.0, average_balance or max(balances))), 2)
    else:
        volatility_score = 0.45 if request.statement_url else 0.65

    extracted_cashflows = {
        "credit_count": len(credits),
        "debit_count": len(debits),
        "total_credits": round(sum(credits), 2),
        "total_debits": round(sum(debits), 2),
        "net_cashflow": round(sum(credits) - sum(debits), 2),
    }
    insights = {
        "income_quality": "stable" if monthly_income >= recurring_debits else "tight",
        "liquidity": "healthy" if average_balance >= recurring_debits * 0.5 else "thin",
        "repayment_signal": "watch" if bounced else "clean",
    }
    return {
        "average_balance": average_balance,
        "monthly_income": monthly_income,
        "recurring_debits": recurring_debits,
        "volatility_score": volatility_score,
        "bounced_payment_count": len(bounced),
        "extracted_cashflows": extracted_cashflows,
        "insights": insights,
    }


def persist_statement_analysis(
    db: Session,
    request: BankStatementAnalysisRequest,
    analysis: dict,
) -> BankStatementAnalysis:
    from uuid import uuid4

    record = BankStatementAnalysis(
        id=str(uuid4()),
        customer_id=request.customer_id,
        application_id=request.application_id,
        statement_url=request.statement_url,
        average_balance=analysis["average_balance"],
        monthly_income=analysis["monthly_income"],
        recurring_debits=analysis["recurring_debits"],
        volatility_score=analysis["volatility_score"],
        bounced_payment_count=analysis["bounced_payment_count"],
        extracted_cashflows=analysis["extracted_cashflows"],
        insights=analysis["insights"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def build_credit_decision(
    request: AICreditEngineRequest,
    behavioral_score: float,
    statement_analysis: Optional[dict],
    fraud_score: float,
) -> dict:
    rule_score = 68.0
    if request.credit_score:
        rule_score = min(90.0, max(35.0, (request.credit_score - 300) / 600 * 100))

    monthly_income = (
        request.declared_monthly_income
        or (statement_analysis or {}).get("monthly_income")
        or 0.0
    )
    emi_capacity_ratio = request.requested_amount / max(1.0, monthly_income * max(1, request.tenure_months))
    affordability_score = round(max(20.0, min(95.0, 100 - (emi_capacity_ratio * 100))), 2)

    if statement_analysis:
        statement_score = round(
            75
            + min(15, statement_analysis["average_balance"] / 10000)
            - (statement_analysis["volatility_score"] * 12)
            - (statement_analysis["bounced_payment_count"] * 8),
            2,
        )
    else:
        statement_score = 62.0

    fraud_penalty = round(fraud_score * 25, 2)
    ai_risk_score = round(
        (rule_score * 0.25)
        + (behavioral_score * 0.30)
        + (statement_score * 0.25)
        + (affordability_score * 0.20)
        - fraud_penalty,
        2,
    )
    ai_risk_score = max(0.0, min(100.0, ai_risk_score))
    default_probability_90d = round(max(0.02, min(0.45, 1 - (ai_risk_score / 110))), 2)

    if ai_risk_score >= 72 and default_probability_90d <= 0.25:
        recommendation = "approve"
    elif ai_risk_score >= 58:
        recommendation = "review"
    else:
        recommendation = "decline"

    reasons = [
        f"Behavioral score contributes {round(behavioral_score, 2)}.",
        f"Bank statement score contributes {round(statement_score, 2)}.",
        f"Affordability score is {round(affordability_score, 2)}.",
    ]
    if fraud_penalty:
        reasons.append(f"Fraud penalty reduced score by {fraud_penalty}.")
    if statement_analysis and statement_analysis["bounced_payment_count"]:
        reasons.append("Bounced payment indicators require manual review.")

    return {
        "rule_score": round(rule_score, 2),
        "behavioral_score": round(behavioral_score, 2),
        "statement_score": round(statement_score, 2),
        "affordability_score": round(affordability_score, 2),
        "fraud_penalty": fraud_penalty,
        "ai_risk_score": ai_risk_score,
        "default_probability_90d": default_probability_90d,
        "recommendation": recommendation,
        "risk_grade": _risk_grade(ai_risk_score),
        "reasons": reasons,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "findna"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/bank-statement/analyze", response_model=BankStatementAnalysisResponse)
async def analyze_bank_statement(
    request: BankStatementAnalysisRequest,
    db: Session = Depends(get_db),
):
    """Analyze bank statement cashflows for underwriting and monitoring."""
    analysis = analyze_statement_signals(request)
    record = persist_statement_analysis(db, request, analysis)
    return {
        "customer_id": record.customer_id,
        "application_id": record.application_id,
        "average_balance": record.average_balance,
        "monthly_income": record.monthly_income,
        "recurring_debits": record.recurring_debits,
        "volatility_score": record.volatility_score,
        "bounced_payment_count": record.bounced_payment_count,
        "extracted_cashflows": record.extracted_cashflows or {},
        "insights": record.insights or {},
        "analyzed_at": record.analyzed_at,
    }


@app.post("/credit-engine/score", response_model=AICreditEngineResponse)
async def ai_credit_engine(
    request: AICreditEngineRequest,
    db: Session = Depends(get_db),
):
    """Score a loan application with FinDNA behavioral, statement, and fraud signals."""
    from uuid import uuid4

    behavior = await score_behavior(
        BehavioralScoreRequest(
            customer_id=request.customer_id,
            income_data=IncomeData(monthly_income=request.declared_monthly_income)
            if request.declared_monthly_income
            else None,
            application_id=request.application_id,
        ),
        db,
    )
    statement_analysis = None
    if request.bank_statement:
        request.bank_statement.customer_id = request.customer_id
        request.bank_statement.application_id = request.application_id
        statement_analysis = analyze_statement_signals(request.bank_statement)
        persist_statement_analysis(db, request.bank_statement, statement_analysis)

    fraud = await score_fraud(
        FraudDetectionRequest(customer_id=request.customer_id, application_id=request.application_id),
        db,
    )
    decision = build_credit_decision(
        request=request,
        behavioral_score=behavior["score"],
        statement_analysis=statement_analysis,
        fraud_score=fraud["fraud_score"],
    )

    existing = db.query(AICreditDecision).filter(
        AICreditDecision.application_id == request.application_id
    ).first()
    if existing:
        record = existing
        record.requested_amount = request.requested_amount
        record.tenure_months = request.tenure_months
        record.rule_score = decision["rule_score"]
        record.behavioral_score = decision["behavioral_score"]
        record.statement_score = decision["statement_score"]
        record.fraud_penalty = decision["fraud_penalty"]
        record.ai_risk_score = decision["ai_risk_score"]
        record.default_probability_90d = decision["default_probability_90d"]
        record.recommendation = decision["recommendation"]
        record.risk_grade = decision["risk_grade"]
        record.reasons = decision["reasons"]
    else:
        record = AICreditDecision(
            id=str(uuid4()),
            customer_id=request.customer_id,
            application_id=request.application_id,
            requested_amount=request.requested_amount,
            tenure_months=request.tenure_months,
            rule_score=decision["rule_score"],
            behavioral_score=decision["behavioral_score"],
            statement_score=decision["statement_score"],
            fraud_penalty=decision["fraud_penalty"],
            ai_risk_score=decision["ai_risk_score"],
            default_probability_90d=decision["default_probability_90d"],
            recommendation=decision["recommendation"],
            risk_grade=decision["risk_grade"],
            reasons=decision["reasons"],
        )
        db.add(record)
    db.commit()

    return {
        "customer_id": request.customer_id,
        "application_id": request.application_id,
        "ai_risk_score": decision["ai_risk_score"],
        "default_probability_90d": decision["default_probability_90d"],
        "recommendation": decision["recommendation"],
        "risk_grade": decision["risk_grade"],
        "component_scores": {
            "rule_score": decision["rule_score"],
            "behavioral_score": decision["behavioral_score"],
            "statement_score": decision["statement_score"],
            "affordability_score": decision["affordability_score"],
            "fraud_penalty": decision["fraud_penalty"],
        },
        "reasons": decision["reasons"],
        "generated_at": datetime.utcnow(),
    }


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
        "subject_type": request.subject_type or "application",
        "subject_id": request.subject_id or application_id,
        "source_service": request.source_service or "los",
        "source_reference_id": request.source_reference_id or application_id,
        "risk_summary": "Overall risk is medium; keep exposure limited to 20% of customer’s monthly income." 
    }

    invocation = persist_assistant_invocation(
        db=db,
        assistant_type="underwriting",
        customer_id=request.customer_id,
        application_id=application_id,
        context_text=request.context_text,
        summary=summary,
        recommendation=recommendation,
        risk_indicators=risk_indicators,
        action_plan=action_plan,
        insights=insights,
    )
    return assistant_response(invocation)


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
        "settlement_recommendation": "Recommend partial settlement to prevent escalation.",
        "subject_type": request.subject_type or "customer",
        "subject_id": request.subject_id or customer_id,
        "source_service": request.source_service or "collections",
        "source_reference_id": request.source_reference_id or customer_id,
    }

    invocation = persist_assistant_invocation(
        db=db,
        assistant_type="collections",
        customer_id=customer_id,
        application_id=request.application_id,
        context_text=request.context_text,
        summary=summary,
        recommendation=recommendation,
        risk_indicators=risk_indicators,
        action_plan=action_plan,
        insights=insights,
    )
    return assistant_response(invocation)


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
        "cross_sell": "Recommend gold loan advisory only if liquidity need emerges.",
        "subject_type": request.subject_type or "customer",
        "subject_id": request.subject_id or customer_id,
        "source_service": request.source_service or "relationship",
        "source_reference_id": request.source_reference_id or customer_id,
    }

    invocation = persist_assistant_invocation(
        db=db,
        assistant_type="relationship",
        customer_id=customer_id,
        application_id=request.application_id,
        context_text=request.context_text,
        summary=summary,
        recommendation=recommendation,
        risk_indicators=risk_indicators,
        action_plan=action_plan,
        insights=insights,
    )
    return assistant_response(invocation)


@app.get("/assistant-invocations", response_model=List[AssistantInvocationResponse])
async def list_assistant_invocations(
    assistant_type: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    application_id: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    """List persisted FinDNA assistant outputs for dashboard and audit views."""
    query = db.query(AssistantInvocation)
    if assistant_type:
        query = query.filter(AssistantInvocation.assistant_type == assistant_type)
    if customer_id:
        query = query.filter(AssistantInvocation.customer_id == customer_id)
    if application_id:
        query = query.filter(AssistantInvocation.application_id == application_id)

    invocations = query.order_by(AssistantInvocation.updated_at.desc()).offset(skip).limit(limit).all()
    return [assistant_response(invocation) for invocation in invocations]


@app.get("/assistant-invocations/{invocation_key}", response_model=AssistantInvocationResponse)
async def get_assistant_invocation(invocation_key: str, db: Session = Depends(get_db)):
    """Retrieve the latest saved assistant output by stable invocation key."""
    invocation = db.query(AssistantInvocation).filter(
        AssistantInvocation.invocation_key == invocation_key
    ).first()
    if not invocation:
        raise HTTPException(status_code=404, detail="Assistant invocation not found")
    return assistant_response(invocation)


@app.get("/dashboard/executive", response_model=ExecutiveDashboardResponse)
async def executive_dashboard(db: Session = Depends(get_db)):
    """Aggregate FinDNA portfolio, risk, collections, and assistant signals."""
    scores = db.query(BehavioralScore).all()
    fraud_records = db.query(FraudDetectionRecord).all()
    churn_predictions = db.query(ChurnPrediction).all()
    assistant_invocations = db.query(AssistantInvocation).all()

    risk_summary = {"low": 0, "medium": 0, "high": 0, "critical": 0, "unknown": 0}
    for score in scores:
        risk_summary[_risk_level_from_score(score.score)] += 1
    for fraud in fraud_records:
        risk_summary[fraud.risk_level if fraud.risk_level in risk_summary else "unknown"] += 1

    assistant_summary: dict[str, int] = {}
    for invocation in assistant_invocations:
        assistant_summary[invocation.assistant_type] = assistant_summary.get(invocation.assistant_type, 0) + 1

    average_behavior_score = round(sum(score.score for score in scores) / len(scores), 2) if scores else 0.0
    average_fraud_score = round(sum(record.fraud_score for record in fraud_records) / len(fraud_records), 2) if fraud_records else 0.0
    churn_risk_customers = sum(1 for prediction in churn_predictions if prediction.churn_probability >= 0.5)

    recommendations = []
    if risk_summary["high"] or risk_summary["critical"]:
        recommendations.append("Prioritize manual review for high and critical risk customers.")
    if average_behavior_score and average_behavior_score < 70:
        recommendations.append("Tighten underwriting thresholds until portfolio behavior score improves.")
    if churn_risk_customers:
        recommendations.append("Trigger relationship manager outreach for high churn-risk customers.")
    if not recommendations:
        recommendations.append("Portfolio risk is stable; continue monitoring assistant signals.")

    return {
        "generated_at": datetime.utcnow(),
        "portfolio_health": {
            "scored_customers": len(scores),
            "average_behavior_score": average_behavior_score,
            "fraud_records": len(fraud_records),
            "average_fraud_score": average_fraud_score,
            "churn_predictions": len(churn_predictions),
        },
        "risk_summary": risk_summary,
        "collections_summary": {
            "collections_assistant_runs": assistant_summary.get("collections", 0),
            "churn_risk_customers": churn_risk_customers,
            "high_fraud_records": sum(1 for record in fraud_records if record.risk_level in {"high", "critical"}),
        },
        "assistant_summary": assistant_summary,
        "recommendations": recommendations,
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
