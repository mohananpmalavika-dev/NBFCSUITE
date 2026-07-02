import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Column, Date, DateTime, JSON, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Policy(Base):
    __tablename__ = "policy"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    policy_number = Column(String, nullable=False)
    title = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    version = Column(String, nullable=True)
    effective_date = Column(Date, nullable=True)
    review_date = Column(Date, nullable=True)
    status = Column(String, default="draft")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Regulation(Base):
    __tablename__ = "regulation"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=True)
    effective_date = Column(Date, nullable=True)
    status = Column(String, default="active")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceObligation(Base):
    __tablename__ = "compliance_obligation"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    regulation_id = Column(String, nullable=True)
    clause = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    frequency = Column(String, nullable=True)
    evidence = Column(String, nullable=True)
    status = Column(String, default="open")
    risk_level = Column(String, default="medium")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Assessment(Base):
    __tablename__ = "assessment"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    assessment_type = Column(String, nullable=False)
    title = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    status = Column(String, default="draft")
    findings = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditPlan(Base):
    __tablename__ = "audit_plan"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    audit_type = Column(String, nullable=False)
    title = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    status = Column(String, default="planned")
    findings = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Issue(Base):
    __tablename__ = "issue"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    status = Column(String, default="open")
    severity = Column(String, default="medium")
    description = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CorrectiveAction(Base):
    __tablename__ = "corrective_action"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    issue_id = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    action_plan = Column(String, nullable=True)
    status = Column(String, default="pending")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PolicyCreate(BaseModel):
    tenant_id: str
    policy_number: str
    title: str
    owner: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    status: Optional[str] = "draft"
    metadata: Optional[Dict[str, Any]] = None


class PolicyResponse(PolicyCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceObligationResponse(BaseModel):
    tenant_id: str
    items: List[ComplianceObligation]


class AssessmentCreate(BaseModel):
    tenant_id: str
    assessment_type: str
    title: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = "draft"
    findings: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AssessmentResponse(AssessmentCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditCreate(BaseModel):
    tenant_id: str
    audit_type: str
    title: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = "planned"
    findings: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditResponse(AuditCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class IssueCreate(BaseModel):
    tenant_id: str
    title: str
    owner: Optional[str] = None
    severity: Optional[str] = "medium"
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IssueResponse(IssueCreate):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CorrectiveActionCreate(BaseModel):
    tenant_id: str
    issue_id: Optional[str] = None
    owner: Optional[str] = None
    action_plan: Optional[str] = None
    status: Optional[str] = "pending"
    metadata: Optional[Dict[str, Any]] = None


class CorrectiveActionResponse(CorrectiveActionCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class RegulationResponse(BaseModel):
    tenant_id: str
    items: List[Regulation]


class GrcDashboardResponse(BaseModel):
    tenant_id: str
    active_policies: int
    obligations_due: int
    open_audits: int
    open_issues: int
    corrective_actions: int
    compliance_score: int
    status: str


app = FastAPI(title="grc-service", version="0.1.0")


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
    return {"status": "ok", "service": "grc"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.get("/api/v1/grc/dashboard", response_model=GrcDashboardResponse)
async def get_grc_dashboard(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    active_policies = db.query(Policy).filter(Policy.tenant_id == tenant_id, Policy.status != "archived").count()
    obligations_due = db.query(ComplianceObligation).filter(ComplianceObligation.tenant_id == tenant_id, ComplianceObligation.status != "closed").count()
    open_audits = db.query(AuditPlan).filter(AuditPlan.tenant_id == tenant_id, AuditPlan.status != "completed").count()
    open_issues = db.query(Issue).filter(Issue.tenant_id == tenant_id, Issue.status != "closed").count()
    corrective_actions = db.query(CorrectiveAction).filter(CorrectiveAction.tenant_id == tenant_id, CorrectiveAction.status != "closed").count()
    return GrcDashboardResponse(
        tenant_id=tenant_id,
        active_policies=active_policies,
        obligations_due=obligations_due,
        open_audits=open_audits,
        open_issues=open_issues,
        corrective_actions=corrective_actions,
        compliance_score=92,
        status="operational",
    )


@app.get("/api/v1/grc/policies", response_model=List[PolicyResponse])
async def list_policies(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Policy).filter(Policy.tenant_id == tenant_id).order_by(Policy.created_at.desc()).all()


@app.post("/api/v1/grc/policies", response_model=PolicyResponse)
async def create_policy(payload: PolicyCreate, db: Session = Depends(get_db)):
    policy = Policy(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        policy_number=payload.policy_number,
        title=payload.title,
        owner=payload.owner,
        version=payload.version,
        effective_date=payload.effective_date,
        review_date=payload.review_date,
        status=payload.status,
        metadata=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@app.get("/api/v1/grc/obligations", response_model=List[ComplianceObligation])
async def list_obligations(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(ComplianceObligation).filter(ComplianceObligation.tenant_id == tenant_id).order_by(ComplianceObligation.created_at.desc()).all()


@app.post("/api/v1/grc/assessments", response_model=AssessmentResponse)
async def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    assessment = Assessment(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        assessment_type=payload.assessment_type,
        title=payload.title,
        owner=payload.owner,
        status=payload.status,
        findings=payload.findings,
        metadata=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@app.post("/api/v1/grc/audits", response_model=AuditResponse)
async def create_audit(payload: AuditCreate, db: Session = Depends(get_db)):
    audit = AuditPlan(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        audit_type=payload.audit_type,
        title=payload.title,
        owner=payload.owner,
        status=payload.status,
        findings=payload.findings,
        metadata=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


@app.post("/api/v1/grc/issues", response_model=IssueResponse)
async def create_issue(payload: IssueCreate, db: Session = Depends(get_db)):
    issue = Issue(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        title=payload.title,
        owner=payload.owner,
        status="open",
        severity=payload.severity,
        description=payload.description,
        metadata=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@app.post("/api/v1/grc/corrective-actions", response_model=CorrectiveActionResponse)
async def create_corrective_action(payload: CorrectiveActionCreate, db: Session = Depends(get_db)):
    action = CorrectiveAction(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        issue_id=payload.issue_id,
        owner=payload.owner,
        action_plan=payload.action_plan,
        status=payload.status,
        metadata=payload.metadata,
        created_at=datetime.utcnow(),
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@app.get("/api/v1/grc/regulations", response_model=List[Regulation])
async def list_regulations(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(Regulation).filter(Regulation.tenant_id == tenant_id).order_by(Regulation.created_at.desc()).all()


@app.get("/api/v1/grc/reports")
async def get_reports(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return {
        "tenant_id": tenant_id,
        "reports": [
            {"report_type": "compliance_dashboard", "status": "ready"},
            {"report_type": "audit_findings", "status": "ready"},
            {"report_type": "issue_register", "status": "ready"},
        ],
    }
