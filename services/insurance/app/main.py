from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, JSON, String, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"
    __table_args__ = (UniqueConstraint("tenant_id", "policy_number", name="uq_insurance_policy_tenant_number"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    policy_number = Column(String, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    product_type = Column(String, index=True)
    insurer_name = Column(String)
    sum_assured = Column(Float)
    premium_amount = Column(Float)
    premium_frequency = Column(String, default="monthly")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    next_premium_due_date = Column(DateTime)
    status = Column(String, default="active", index=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PremiumPayment(Base):
    __tablename__ = "insurance_premium_payments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    policy_id = Column(String, index=True, nullable=False)
    amount = Column(Float)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_mode = Column(String)
    reference = Column(String, index=True, nullable=True)
    status = Column(String, default="success")


class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    policy_id = Column(String, index=True, nullable=False)
    claim_number = Column(String, index=True)
    claim_type = Column(String)
    claim_amount = Column(Float)
    approved_amount = Column(Float, nullable=True)
    incident_date = Column(DateTime)
    status = Column(String, default="submitted", index=True)
    documents = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PolicyCreate(BaseModel):
    tenant_id: str
    customer_id: str
    product_type: str
    insurer_name: str
    sum_assured: float = Field(gt=0)
    premium_amount: float = Field(gt=0)
    premium_frequency: str = Field(default="monthly", pattern="^(monthly|quarterly|annual)$")
    start_date: Optional[datetime] = None
    term_months: int = Field(default=12, gt=0)
    metadata: Optional[dict] = None


class PolicyResponse(BaseModel):
    id: str
    tenant_id: str
    policy_number: str
    customer_id: str
    product_type: str
    insurer_name: str
    sum_assured: float
    premium_amount: float
    premium_frequency: str
    start_date: datetime
    end_date: datetime
    next_premium_due_date: datetime
    status: str
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class PremiumPaymentCreate(BaseModel):
    tenant_id: str
    amount: Optional[float] = None
    payment_mode: str
    reference: Optional[str] = None


class PremiumPaymentResponse(BaseModel):
    id: str
    tenant_id: str
    policy_id: str
    amount: float
    payment_date: datetime
    payment_mode: str
    reference: Optional[str]
    status: str

    class Config:
        from_attributes = True


class ClaimCreate(BaseModel):
    tenant_id: str
    claim_type: str
    claim_amount: float = Field(gt=0)
    incident_date: datetime
    documents: Optional[List[str]] = None
    notes: Optional[str] = None


class ClaimDecision(BaseModel):
    status: str = Field(pattern="^(approved|rejected|settled)$")
    approved_amount: Optional[float] = None
    notes: Optional[str] = None


class ClaimResponse(BaseModel):
    id: str
    tenant_id: str
    policy_id: str
    claim_number: str
    claim_type: str
    claim_amount: float
    approved_amount: Optional[float]
    incident_date: datetime
    status: str
    documents: Optional[list]
    notes: Optional[str]

    class Config:
        from_attributes = True


app = FastAPI(title="insurance-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "insurance"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def _policy(policy_id: str, tenant_id: str, db: Session) -> InsurancePolicy:
    policy = db.query(InsurancePolicy).filter(
        InsurancePolicy.id == policy_id,
        InsurancePolicy.tenant_id == tenant_id,
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found for tenant")
    return policy


def _next_due_date(current: datetime, frequency: str) -> datetime:
    if frequency == "annual":
        return current + timedelta(days=365)
    if frequency == "quarterly":
        return current + timedelta(days=90)
    return current + timedelta(days=30)


def _policy_response(policy: InsurancePolicy) -> dict:
    return {
        "id": policy.id,
        "tenant_id": policy.tenant_id,
        "policy_number": policy.policy_number,
        "customer_id": policy.customer_id,
        "product_type": policy.product_type,
        "insurer_name": policy.insurer_name,
        "sum_assured": policy.sum_assured,
        "premium_amount": policy.premium_amount,
        "premium_frequency": policy.premium_frequency,
        "start_date": policy.start_date,
        "end_date": policy.end_date,
        "next_premium_due_date": policy.next_premium_due_date,
        "status": policy.status,
        "metadata": policy.metadata_json,
    }


@app.post("/policies", response_model=PolicyResponse)
async def create_policy(payload: PolicyCreate, db: Session = Depends(get_db)):
    start_date = payload.start_date or datetime.utcnow()
    policy = InsurancePolicy(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        policy_number=f"POL-{str(uuid4())[:10].upper()}",
        customer_id=payload.customer_id,
        product_type=payload.product_type,
        insurer_name=payload.insurer_name,
        sum_assured=payload.sum_assured,
        premium_amount=payload.premium_amount,
        premium_frequency=payload.premium_frequency,
        start_date=start_date,
        end_date=start_date + timedelta(days=30 * payload.term_months),
        next_premium_due_date=_next_due_date(start_date, payload.premium_frequency),
        metadata_json=payload.metadata,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return _policy_response(policy)


@app.get("/policies", response_model=List[PolicyResponse])
async def list_policies(
    tenant_id: str = Query(...),
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    product_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(InsurancePolicy).filter(InsurancePolicy.tenant_id == tenant_id)
    if customer_id:
        query = query.filter(InsurancePolicy.customer_id == customer_id)
    if status:
        query = query.filter(InsurancePolicy.status == status)
    if product_type:
        query = query.filter(InsurancePolicy.product_type == product_type)
    return [_policy_response(policy) for policy in query.order_by(InsurancePolicy.created_at.desc()).all()]


@app.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _policy_response(_policy(policy_id, tenant_id, db))


@app.post("/policies/{policy_id}/premium-payments", response_model=PremiumPaymentResponse)
async def collect_premium(policy_id: str, payload: PremiumPaymentCreate, db: Session = Depends(get_db)):
    policy = _policy(policy_id, payload.tenant_id, db)
    if policy.status not in {"active", "lapsed"}:
        raise HTTPException(status_code=400, detail="Policy is not eligible for premium collection")
    amount = payload.amount if payload.amount is not None else policy.premium_amount
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Premium amount must be positive")
    payment = PremiumPayment(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        policy_id=policy.id,
        amount=amount,
        payment_mode=payload.payment_mode,
        reference=payload.reference or f"PREM-{str(uuid4())[:10].upper()}",
    )
    policy.status = "active"
    policy.next_premium_due_date = _next_due_date(policy.next_premium_due_date or datetime.utcnow(), policy.premium_frequency)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@app.get("/premium-payments", response_model=List[PremiumPaymentResponse])
async def list_premium_payments(
    tenant_id: str = Query(...),
    policy_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PremiumPayment).filter(PremiumPayment.tenant_id == tenant_id)
    if policy_id:
        query = query.filter(PremiumPayment.policy_id == policy_id)
    return query.order_by(PremiumPayment.payment_date.desc()).all()


@app.post("/policies/{policy_id}/claims", response_model=ClaimResponse)
async def submit_claim(policy_id: str, payload: ClaimCreate, db: Session = Depends(get_db)):
    policy = _policy(policy_id, payload.tenant_id, db)
    if policy.status != "active":
        raise HTTPException(status_code=400, detail="Only active policies can receive claims")
    if payload.claim_amount > policy.sum_assured:
        raise HTTPException(status_code=400, detail="Claim amount cannot exceed sum assured")
    claim = InsuranceClaim(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        policy_id=policy.id,
        claim_number=f"CLM-{str(uuid4())[:10].upper()}",
        claim_type=payload.claim_type,
        claim_amount=payload.claim_amount,
        incident_date=payload.incident_date,
        documents=payload.documents or [],
        notes=payload.notes,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@app.post("/claims/{claim_id}/decision", response_model=ClaimResponse)
async def decide_claim(
    claim_id: str,
    decision: ClaimDecision,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    claim = db.query(InsuranceClaim).filter(
        InsuranceClaim.id == claim_id,
        InsuranceClaim.tenant_id == tenant_id,
    ).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found for tenant")
    if decision.status in {"approved", "settled"}:
        approved_amount = decision.approved_amount if decision.approved_amount is not None else claim.claim_amount
        if approved_amount <= 0 or approved_amount > claim.claim_amount:
            raise HTTPException(status_code=400, detail="approved_amount must be positive and not exceed claim_amount")
        claim.approved_amount = approved_amount
    else:
        claim.approved_amount = 0.0
    claim.status = decision.status
    claim.notes = decision.notes or claim.notes
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(claim)
    return claim


@app.get("/claims", response_model=List[ClaimResponse])
async def list_claims(
    tenant_id: str = Query(...),
    policy_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(InsuranceClaim).filter(InsuranceClaim.tenant_id == tenant_id)
    if policy_id:
        query = query.filter(InsuranceClaim.policy_id == policy_id)
    if status:
        query = query.filter(InsuranceClaim.status == status)
    return query.order_by(InsuranceClaim.created_at.desc()).all()


@app.get("/")
async def root():
    return {"service": "insurance", "version": "0.1.0"}
