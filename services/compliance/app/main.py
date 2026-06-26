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


class AuditLogCreate(BaseModel):
    entity_type: str
    entity_id: str
    action: str
    performed_by: str
    details: Optional[dict] = None


app = FastAPI(title="compliance-service", version="0.1.0")


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
    new_check = ComplianceCheck(
        id=str(uuid4()),
        customer_id=check.customer_id,
        check_type=check.check_type,
        status=check.status,
        score=check.score,
        details=check.details
    )
    db.add(new_check)
    db.commit()
    db.refresh(new_check)
    return new_check


@app.get("/compliance-checks/{customer_id}")
async def get_compliance_checks(customer_id: str, db: Session = Depends(get_db)):
    checks = db.query(ComplianceCheck).filter(ComplianceCheck.customer_id == customer_id).all()
    return {"customer_id": customer_id, "checks": checks}


@app.post("/audit-logs")
async def create_audit_log(log: AuditLogCreate, db: Session = Depends(get_db)):
    new_log = AuditLog(
        id=str(uuid4()),
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        action=log.action,
        performed_by=log.performed_by,
        details=log.details
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


@app.get("/")
async def root():
    return {"service": "compliance", "version": "0.1.0"}
