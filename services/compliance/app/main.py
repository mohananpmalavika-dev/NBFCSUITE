from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, DateTime, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    id = Column(String, primary_key=True)
    name = Column(String)
    list_type = Column(String)
    country = Column(String, nullable=True)
    risk_level = Column(String, default="medium")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(String, primary_key=True)
    customer_id = Column(String)
    check_type = Column(String)
    status = Column(String)
    score = Column(Float, nullable=True)
    details = Column(JSON, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    entity_type = Column(String)
    entity_id = Column(String)
    action = Column(String)
    performed_by = Column(String)
    performed_at = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)


class WatchlistEntryCreate(BaseModel):
    name: str
    list_type: str
    country: Optional[str] = None
    risk_level: Optional[str] = "medium"
    notes: Optional[str] = None


class ComplianceCheckCreate(BaseModel):
    customer_id: str
    check_type: str
    status: str
    score: Optional[float] = None
    details: Optional[dict] = None


class RunChecksRequest(BaseModel):
    performed_by: Optional[str] = "system"
    customer_name: Optional[str] = None
    source_service: Optional[str] = "customer"
    source_reference_id: Optional[str] = None


class AuditLogCreate(BaseModel):
    entity_type: str
    entity_id: str
    action: str
    performed_by: str
    details: Optional[dict] = None


app = FastAPI(title="compliance-service", version="0.1.0")

COMPLIANCE_STATUSES = {"pending", "passed", "flagged", "rejected"}
STATUS_ALIASES = {"pass": "passed", "fail": "rejected", "failed": "rejected"}


def normalize_status(status: str) -> str:
    normalized = STATUS_ALIASES.get(status.lower(), status.lower())
    if normalized not in COMPLIANCE_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"status must be one of {', '.join(sorted(COMPLIANCE_STATUSES))}",
        )
    return normalized


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
    return {"status": "ok", "service": "compliance"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/watchlist", response_model=WatchlistEntryCreate)
async def add_watchlist_entry(entry: WatchlistEntryCreate, db: Session = Depends(get_db)):
    new_entry = WatchlistEntry(
        id=str(uuid4()),
        name=entry.name,
        list_type=entry.list_type,
        country=entry.country,
        risk_level=entry.risk_level,
        notes=entry.notes
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return entry


@app.get("/watchlist")
async def list_watchlist(
    list_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(WatchlistEntry)
    if list_type:
        query = query.filter(WatchlistEntry.list_type == list_type)
    if risk_level:
        query = query.filter(WatchlistEntry.risk_level == risk_level)
    return {"items": query.offset(skip).limit(limit).all(), "skip": skip, "limit": limit}


@app.post("/compliance-checks")
async def add_compliance_check(check: ComplianceCheckCreate, db: Session = Depends(get_db)):
    status = normalize_status(check.status)
    new_check = ComplianceCheck(
        id=str(uuid4()),
        customer_id=check.customer_id,
        check_type=check.check_type,
        status=status,
        score=check.score,
        details=check.details
    )
    db.add(new_check)
    db.commit()
    db.refresh(new_check)
    return new_check


@app.post("/run-checks/{customer_id}")
async def run_customer_checks(
    customer_id: str,
    request: RunChecksRequest | None = None,
    db: Session = Depends(get_db),
):
    request = request or RunChecksRequest()
    source_reference_id = request.source_reference_id or customer_id
    watchlist_match = None
    if request.customer_name:
        watchlist_match = db.query(WatchlistEntry).filter(WatchlistEntry.name == request.customer_name).first()

    run_id = str(uuid4())
    check_specs = [
        ("kyc", "passed", 0.05),
        ("aml", "flagged" if watchlist_match else "passed", 0.95 if watchlist_match else 0.10),
        ("pep", "flagged" if watchlist_match and watchlist_match.list_type == "pep" else "passed", 0.85 if watchlist_match else 0.08),
    ]
    checks = []
    for check_type, status, score in check_specs:
        check = ComplianceCheck(
            id=str(uuid4()),
            customer_id=customer_id,
            check_type=check_type,
            status=status,
            score=score,
            details={
                "run_id": run_id,
                "subject_type": "customer",
                "subject_id": customer_id,
                "source_service": request.source_service,
                "source_reference_id": source_reference_id,
                "watchlist_entry_id": watchlist_match.id if watchlist_match else None,
            },
        )
        db.add(check)
        checks.append(check)

    overall_status = "flagged" if any(check.status == "flagged" for check in checks) else "passed"
    audit_log = AuditLog(
        id=str(uuid4()),
        entity_type="customer",
        entity_id=customer_id,
        action="compliance_run_checks",
        performed_by=request.performed_by or "system",
        details={
            "run_id": run_id,
            "subject_type": "customer",
            "subject_id": customer_id,
            "source_service": request.source_service,
            "source_reference_id": source_reference_id,
            "overall_status": overall_status,
            "check_ids": [check.id for check in checks],
        },
    )
    db.add(audit_log)
    db.commit()
    for check in checks:
        db.refresh(check)
    db.refresh(audit_log)
    return {
        "run_id": run_id,
        "customer_id": customer_id,
        "status": overall_status,
        "checks": checks,
        "audit_log_id": audit_log.id,
    }


@app.get("/compliance-checks/{customer_id}")
async def get_compliance_checks(customer_id: str, db: Session = Depends(get_db)):
    checks = db.query(ComplianceCheck).filter(ComplianceCheck.customer_id == customer_id).all()
    return {"customer_id": customer_id, "checks": checks}


@app.post("/audit-logs")
async def create_audit_log(log: AuditLogCreate, db: Session = Depends(get_db)):
    details = dict(log.details or {})
    details.setdefault("subject_type", log.entity_type)
    details.setdefault("subject_id", log.entity_id)
    new_log = AuditLog(
        id=str(uuid4()),
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        action=log.action,
        performed_by=log.performed_by,
        details=details
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@app.get("/audit-logs")
async def list_audit_logs(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    return {"items": query.offset(skip).limit(limit).all(), "skip": skip, "limit": limit}


@app.get("/reports/summary")
async def compliance_summary(db: Session = Depends(get_db)):
    checks = db.query(ComplianceCheck).all()
    by_status: dict[str, int] = {}
    by_check_type: dict[str, int] = {}
    for check in checks:
        by_status[check.status] = by_status.get(check.status, 0) + 1
        by_check_type[check.check_type] = by_check_type.get(check.check_type, 0) + 1
    return {
        "total_checks": len(checks),
        "by_status": by_status,
        "by_check_type": by_check_type,
        "flagged_customers": sorted({check.customer_id for check in checks if check.status == "flagged"}),
    }


@app.get("/")
async def root():
    return {"service": "compliance", "version": "0.1.0"}
