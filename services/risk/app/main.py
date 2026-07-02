import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class RiskCategory(Base):
    __tablename__ = "risk_categories"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskRegisterEntry(Base):
    __tablename__ = "risk_register"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    risk_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    business_owner = Column(String, nullable=True)
    risk_owner = Column(String, nullable=True)
    likelihood = Column(String, nullable=True)
    impact = Column(String, nullable=True)
    inherent_risk = Column(String, nullable=True)
    residual_risk = Column(String, nullable=True)
    status = Column(String, default="identified")
    treatment = Column(String, nullable=True)
    review_date = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    risk_id = Column(String, nullable=False)
    assessed_by = Column(String, nullable=True)
    assessed_at = Column(DateTime, default=datetime.utcnow)
    likelihood = Column(Integer, nullable=True)
    impact = Column(Integer, nullable=True)
    velocity = Column(Integer, nullable=True)
    detectability = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)
    findings = Column(String, nullable=True)
    status = Column(String, default="draft")
    metadata = Column(JSON, nullable=True)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    incident_type = Column(String, nullable=False)
    reported_by = Column(String, nullable=True)
    branch_id = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    status = Column(String, default="open")
    description = Column(String, nullable=True)
    loss_amount = Column(Float, default=0.0)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)


class KRI(Base):
    __tablename__ = "kri"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    threshold = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    status = Column(String, default="normal")
    last_updated = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)


class RiskCreate(BaseModel):
    tenant_id: str
    risk_name: str
    category: Optional[str] = None
    business_owner: Optional[str] = None
    risk_owner: Optional[str] = None
    likelihood: Optional[str] = None
    impact: Optional[str] = None
    treatment: Optional[str] = None
    review_date: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RiskResponse(RiskCreate):
    id: str
    inherent_risk: Optional[str] = None
    residual_risk: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentCreate(BaseModel):
    tenant_id: str
    risk_id: str
    assessed_by: Optional[str] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    velocity: Optional[int] = None
    detectability: Optional[int] = None
    findings: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RiskAssessmentResponse(RiskAssessmentCreate):
    id: str
    score: Optional[float] = None
    status: str
    assessed_at: datetime

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    tenant_id: str
    incident_type: str
    reported_by: Optional[str] = None
    branch_id: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    loss_amount: Optional[float] = 0.0
    metadata: Optional[Dict[str, Any]] = None


class IncidentResponse(IncidentCreate):
    id: str
    status: str
    occurred_at: datetime

    class Config:
        from_attributes = True


class KriCreate(BaseModel):
    tenant_id: str
    name: str
    category: Optional[str] = None
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class KriResponse(KriCreate):
    id: str
    status: str
    last_updated: datetime

    class Config:
        from_attributes = True


class RiskDashboardResponse(BaseModel):
    tenant_id: str
    open_risks: int
    high_risks: int
    critical_risks: int
    incidents: int
    loss_events: int
    controls_under_test: int
    risk_score: int
    compliance_issues: int
    status: str


class KriListResponse(BaseModel):
    tenant_id: str
    items: List[KriResponse]


class RiskRegisterListResponse(BaseModel):
    tenant_id: str
    items: List[RiskResponse]


class IncidentListResponse(BaseModel):
    tenant_id: str
    items: List[IncidentResponse]


class RiskAssessmentListResponse(BaseModel):
    tenant_id: str
    items: List[RiskAssessmentResponse]


app = FastAPI(title="risk-service", version="0.1.0")


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
    return {"status": "ok", "service": "risk"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.get("/api/v1/risk/dashboard", response_model=RiskDashboardResponse)
async def get_risk_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    open_risks = db.query(RiskRegisterEntry).filter(RiskRegisterEntry.tenant_id == tenant_id, RiskRegisterEntry.status != "closed").count()
    high_risks = db.query(RiskRegisterEntry).filter(RiskRegisterEntry.tenant_id == tenant_id, RiskRegisterEntry.residual_risk == "high").count()
    critical_risks = db.query(RiskRegisterEntry).filter(RiskRegisterEntry.tenant_id == tenant_id, RiskRegisterEntry.residual_risk == "critical").count()
    incidents = db.query(Incident).filter(Incident.tenant_id == tenant_id, Incident.status != "closed").count()
    loss_events = db.query(Incident).filter(Incident.tenant_id == tenant_id, Incident.loss_amount > 0).count()
    controls_under_test = db.query(RiskAssessment).filter(RiskAssessment.tenant_id == tenant_id, RiskAssessment.status == "in_review").count()
    compliance_issues = db.query(RiskRegisterEntry).filter(RiskRegisterEntry.tenant_id == tenant_id, RiskRegisterEntry.status == "compliance" ).count()
    return RiskDashboardResponse(
        tenant_id=tenant_id,
        open_risks=open_risks,
        high_risks=high_risks,
        critical_risks=critical_risks,
        incidents=incidents,
        loss_events=loss_events,
        controls_under_test=controls_under_test,
        risk_score=84,
        compliance_issues=compliance_issues,
        status="operational",
    )


@app.get("/api/v1/risk/register", response_model=RiskRegisterListResponse)
async def list_risk_register(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    items = db.query(RiskRegisterEntry).filter(RiskRegisterEntry.tenant_id == tenant_id).order_by(RiskRegisterEntry.created_at.desc()).all()
    return RiskRegisterListResponse(tenant_id=tenant_id, items=items)


@app.post("/api/v1/risk/register", response_model=RiskResponse)
async def create_risk_register_entry(payload: RiskCreate, db: Session = Depends(get_db)):
    entry = RiskRegisterEntry(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        risk_name=payload.risk_name,
        category=payload.category,
        business_owner=payload.business_owner,
        risk_owner=payload.risk_owner,
        likelihood=payload.likelihood,
        impact=payload.impact,
        inherent_risk="medium",
        residual_risk="medium",
        status="identified",
        treatment=payload.treatment,
        review_date=payload.review_date,
        metadata=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.post("/api/v1/risk/assessment", response_model=RiskAssessmentResponse)
async def create_risk_assessment(payload: RiskAssessmentCreate, db: Session = Depends(get_db)):
    score = None
    if payload.likelihood is not None and payload.impact is not None and payload.velocity is not None and payload.detectability is not None:
        score = round((payload.likelihood * payload.impact * payload.velocity) / max(payload.detectability, 1), 2)
    assessment = RiskAssessment(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        risk_id=payload.risk_id,
        assessed_by=payload.assessed_by,
        likelihood=payload.likelihood,
        impact=payload.impact,
        velocity=payload.velocity,
        detectability=payload.detectability,
        score=score,
        findings=payload.findings,
        status="in_review",
        metadata=payload.metadata,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@app.get("/api/v1/risk/kri", response_model=KriListResponse)
async def list_kri(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    items = db.query(KRI).filter(KRI.tenant_id == tenant_id).order_by(KRI.last_updated.desc()).all()
    return KriListResponse(tenant_id=tenant_id, items=items)


@app.post("/api/v1/risk/incident", response_model=IncidentResponse)
async def report_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        incident_type=payload.incident_type,
        reported_by=payload.reported_by,
        branch_id=payload.branch_id,
        severity=payload.severity,
        description=payload.description,
        loss_amount=payload.loss_amount or 0.0,
        status="open",
        metadata=payload.metadata,
        occurred_at=datetime.utcnow(),
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@app.post("/api/v1/risk/rcsa", response_model=RiskAssessmentResponse)
async def create_rcsa(payload: RiskAssessmentCreate, db: Session = Depends(get_db)):
    assessment = RiskAssessment(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        risk_id=payload.risk_id,
        assessed_by=payload.assessed_by,
        likelihood=payload.likelihood,
        impact=payload.impact,
        velocity=payload.velocity,
        detectability=payload.detectability,
        score=round((payload.likelihood or 0) * (payload.impact or 0) / max(payload.detectability or 1, 1), 2) if payload.likelihood and payload.impact else None,
        findings=payload.findings,
        status="rcsa_in_progress",
        metadata=payload.metadata,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@app.get("/api/v1/risk/heatmap")
async def get_risk_heatmap(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return {
        "tenant_id": tenant_id,
        "heatmap": [
            {"category": "Credit", "likelihood": 4, "impact": 5},
            {"category": "Operational", "likelihood": 3, "impact": 4},
            {"category": "Liquidity", "likelihood": 2, "impact": 5},
        ],
    }


@app.get("/api/v1/risk/reports")
async def get_risk_reports(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return {
        "tenant_id": tenant_id,
        "reports": [
            {"report_type": "risk_register", "status": "ready"},
            {"report_type": "kri_dashboard", "status": "ready"},
            {"report_type": "incident_report", "status": "ready"},
        ],
    }
