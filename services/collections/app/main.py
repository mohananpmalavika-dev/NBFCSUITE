from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Models
class CollectionBucket(Base):
    __tablename__ = "collection_buckets"
    
    id = Column(String, primary_key=True)
    bucket_name = Column(String)
    min_dpd = Column(Integer)
    max_dpd = Column(Integer)


class CollectionAssignment(Base):
    __tablename__ = "collection_assignments"
    
    id = Column(String, primary_key=True)
    loan_account_id = Column(String, index=True)
    customer_id = Column(String, index=True, nullable=True)
    collector_user_id = Column(String)
    branch_id = Column(String, index=True, nullable=True)
    assigned_date = Column(DateTime, default=datetime.utcnow)
    bucket_id = Column(String)
    days_past_due = Column(Integer, default=0)
    status = Column(String, default="active")
    priority = Column(String, default="medium")
    outstanding_amount = Column(Float)


class CollectionActivity(Base):
    __tablename__ = "collection_activities"
    
    id = Column(String, primary_key=True)
    assignment_id = Column(String, ForeignKey("collection_assignments.id"))
    activity_type = Column(String)
    activity_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String)
    promised_amount = Column(Float, nullable=True)
    promised_date = Column(DateTime, nullable=True)
    customer_response = Column(String)


class SettlementNegotiation(Base):
    __tablename__ = "settlement_negotiations"
    
    id = Column(String, primary_key=True)
    loan_account_id = Column(String)
    outstanding_amount = Column(Float)
    offer_amount = Column(Float)
    settlement_percentage = Column(Float)
    offered_date = Column(DateTime, default=datetime.utcnow)
    customer_response = Column(String, nullable=True)
    settlement_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")


class NPARecord(Base):
    __tablename__ = "npa_records"
    
    id = Column(String, primary_key=True)
    loan_account_id = Column(String, unique=True)
    classification_date = Column(DateTime, default=datetime.utcnow)
    npa_type = Column(String)
    provision_percentage = Column(Float)
    recovery_amount = Column(Float, default=0)
    recovery_date = Column(DateTime, nullable=True)


# Pydantic Schemas
class CollectionActivityCreate(BaseModel):
    activity_type: str
    notes: str
    promised_amount: Optional[float] = None
    promised_date: Optional[datetime] = None
    customer_response: str


class ActivityResponse(BaseModel):
    id: str
    activity_type: str
    activity_date: datetime
    notes: str
    customer_response: str
    
    class Config:
        from_attributes = True


class CollectionStatusResponse(BaseModel):
    loan_account_id: str
    collector_name: str
    status: str
    priority: str
    outstanding_amount: float
    assigned_date: datetime
    latest_activity: Optional[ActivityResponse] = None


class SettlementOfferRequest(BaseModel):
    offer_amount: float


class CollectionBucketCreate(BaseModel):
    bucket_name: str
    min_dpd: int
    max_dpd: int


class CollectionBucketResponse(BaseModel):
    id: str
    bucket_name: str
    min_dpd: int
    max_dpd: int
    loan_count: int = 0

    class Config:
        from_attributes = True


class CollectionAssignmentCreate(BaseModel):
    loan_account_id: str
    customer_id: Optional[str] = None
    collector_user_id: str
    branch_id: Optional[str] = None
    bucket_id: Optional[str] = None
    days_past_due: int = Field(default=0, ge=0)
    outstanding_amount: float
    priority: Optional[str] = "medium"


class CollectionAssignmentResponse(BaseModel):
    id: str
    loan_account_id: str
    customer_id: Optional[str]
    collector_user_id: str
    branch_id: Optional[str]
    bucket_id: str
    bucket_name: Optional[str] = None
    days_past_due: int
    status: str
    priority: str
    outstanding_amount: float
    assigned_date: datetime

    class Config:
        from_attributes = True


# FastAPI App
app = FastAPI(title="collections-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_collection_buckets(db: Session) -> None:
    from uuid import uuid4

    default_buckets = [
        ("0-30 DPD", 0, 30),
        ("30-60 DPD", 31, 60),
        ("60-90 DPD", 61, 90),
        ("90+ DPD", 91, 9999),
    ]
    for bucket_name, min_dpd, max_dpd in default_buckets:
        existing = db.query(CollectionBucket).filter(CollectionBucket.bucket_name == bucket_name).first()
        if not existing:
            db.add(
                CollectionBucket(
                    id=str(uuid4()),
                    bucket_name=bucket_name,
                    min_dpd=min_dpd,
                    max_dpd=max_dpd,
                )
            )
    db.commit()


def find_bucket_for_dpd(db: Session, days_past_due: int) -> CollectionBucket:
    bucket = (
        db.query(CollectionBucket)
        .filter(CollectionBucket.min_dpd <= days_past_due, CollectionBucket.max_dpd >= days_past_due)
        .order_by(CollectionBucket.min_dpd.asc())
        .first()
    )
    if not bucket:
        raise HTTPException(status_code=400, detail="No collection bucket configured for days_past_due")
    return bucket


def assignment_response(assignment: CollectionAssignment, db: Session) -> CollectionAssignmentResponse:
    bucket = db.query(CollectionBucket).filter(CollectionBucket.id == assignment.bucket_id).first()
    return CollectionAssignmentResponse(
        id=assignment.id,
        loan_account_id=assignment.loan_account_id,
        customer_id=assignment.customer_id,
        collector_user_id=assignment.collector_user_id,
        branch_id=assignment.branch_id,
        bucket_id=assignment.bucket_id,
        bucket_name=bucket.bucket_name if bucket else None,
        days_past_due=assignment.days_past_due,
        status=assignment.status,
        priority=assignment.priority,
        outstanding_amount=assignment.outstanding_amount,
        assigned_date=assignment.assigned_date,
    )


def trigger_collections_assistant(loan_id: str, activity_type: str, notes: str) -> None:
    """Best-effort FinDNA hook keyed by loan account because assignments do not store customer_id."""
    try:
        import httpx

        findna_base = os.getenv("FINDNA_BASE_URL", "http://localhost:8006")
        payload = {
            "customer_id": loan_id,
            "subject_type": "loan_account",
            "subject_id": loan_id,
            "source_service": "collections",
            "source_reference_id": loan_id,
            "context_text": f"Collections activity: type={activity_type}, notes={notes}",
        }
        with httpx.Client(timeout=5.0) as client:
            client.post(f"{findna_base}/collections-assistant/{loan_id}", json=payload)
    except Exception:
        pass


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_collection_buckets(db)
    finally:
        db.close()


@app.post("/collection-buckets", response_model=dict)
async def create_bucket(bucket: CollectionBucketCreate, db: Session = Depends(get_db)):
    from uuid import uuid4

    existing = db.query(CollectionBucket).filter(CollectionBucket.bucket_name == bucket.bucket_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bucket already exists")

    new_bucket = CollectionBucket(
        id=str(uuid4()),
        bucket_name=bucket.bucket_name,
        min_dpd=bucket.min_dpd,
        max_dpd=bucket.max_dpd,
    )
    db.add(new_bucket)
    db.commit()
    db.refresh(new_bucket)
    return {"bucket_id": new_bucket.id, "bucket_name": new_bucket.bucket_name}


@app.post("/assignments", response_model=CollectionAssignmentResponse)
async def create_assignment(
    assignment: CollectionAssignmentCreate,
    db: Session = Depends(get_db)
):
    from uuid import uuid4

    bucket = (
        db.query(CollectionBucket).filter(CollectionBucket.id == assignment.bucket_id).first()
        if assignment.bucket_id
        else find_bucket_for_dpd(db, assignment.days_past_due)
    )
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")

    new_assignment = CollectionAssignment(
        id=str(uuid4()),
        loan_account_id=assignment.loan_account_id,
        customer_id=assignment.customer_id,
        collector_user_id=assignment.collector_user_id,
        branch_id=assignment.branch_id,
        bucket_id=assignment.bucket_id,
        days_past_due=assignment.days_past_due,
        outstanding_amount=assignment.outstanding_amount,
        priority=assignment.priority,
    )
    new_assignment.bucket_id = bucket.id
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return assignment_response(new_assignment, db)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "collections"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.get("/collection-buckets", response_model=List[CollectionBucketResponse])
@app.get("/buckets", response_model=List[CollectionBucketResponse])
async def get_buckets(db: Session = Depends(get_db)):
    """Get all collection buckets."""
    buckets = db.query(CollectionBucket).all()
    responses = []
    for bucket in buckets:
        loan_count = db.query(CollectionAssignment).filter(CollectionAssignment.bucket_id == bucket.id).count()
        responses.append(
            CollectionBucketResponse(
                id=bucket.id,
                bucket_name=bucket.bucket_name,
                min_dpd=bucket.min_dpd,
                max_dpd=bucket.max_dpd,
                loan_count=loan_count,
            )
        )
    return responses


@app.get("/buckets/{bucket_id}/loans")
async def get_bucket_loans(bucket_id: str, db: Session = Depends(get_db)):
    bucket = db.query(CollectionBucket).filter(CollectionBucket.id == bucket_id).first()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    assignments = (
        db.query(CollectionAssignment)
        .filter(CollectionAssignment.bucket_id == bucket_id)
        .order_by(CollectionAssignment.assigned_date.desc())
        .all()
    )
    return {"bucket_id": bucket_id, "bucket_name": bucket.bucket_name, "items": assignments, "total": len(assignments)}


@app.get("/assignments")
async def list_assignments(
    collector_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """List collection assignments."""
    query = db.query(CollectionAssignment)
    
    if collector_id:
        query = query.filter(CollectionAssignment.collector_user_id == collector_id)
    if branch_id:
        query = query.filter(CollectionAssignment.branch_id == branch_id)
    
    if status:
        query = query.filter(CollectionAssignment.status == status)
    
    total = query.count()
    assignments = query.order_by(CollectionAssignment.assigned_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": [assignment_response(assignment, db) for assignment in assignments],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.get("/loan/{loan_id}/status")
async def get_collection_status(
    loan_id: str,
    db: Session = Depends(get_db)
):
    """Get collection status for a loan."""
    assignment = db.query(CollectionAssignment).filter(
        CollectionAssignment.loan_account_id == loan_id
    ).first()
    
    if not assignment:
        return {"status": "not_assigned", "loan_id": loan_id}
    
    # Get latest activity
    latest_activity = db.query(CollectionActivity).filter(
        CollectionActivity.assignment_id == assignment.id
    ).order_by(CollectionActivity.activity_date.desc()).first()
    
    bucket = db.query(CollectionBucket).filter(CollectionBucket.id == assignment.bucket_id).first()
    return {
        "loan_id": loan_id,
        "customer_id": assignment.customer_id,
        "branch_id": assignment.branch_id,
        "collector_id": assignment.collector_user_id,
        "bucket_id": assignment.bucket_id,
        "bucket_name": bucket.bucket_name if bucket else None,
        "days_past_due": assignment.days_past_due,
        "status": assignment.status,
        "priority": assignment.priority,
        "outstanding_amount": assignment.outstanding_amount,
        "assigned_date": assignment.assigned_date,
        "latest_activity": latest_activity
    }


@app.post("/loan/{loan_id}/activity")
async def log_activity(
    loan_id: str,
    activity: CollectionActivityCreate,
    db: Session = Depends(get_db)
):
    """Log collection activity for a loan."""
    from uuid import uuid4
    
    assignment = db.query(CollectionAssignment).filter(
        CollectionAssignment.loan_account_id == loan_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="No active assignment for this loan")
    
    # Create activity
    new_activity = CollectionActivity(
        id=str(uuid4()),
        assignment_id=assignment.id,
        activity_type=activity.activity_type,
        notes=activity.notes,
        promised_amount=activity.promised_amount,
        promised_date=activity.promised_date,
        customer_response=activity.customer_response
    )
    
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    trigger_collections_assistant(loan_id, activity.activity_type, activity.notes)
    
    return {
        "activity_id": new_activity.id,
        "message": "Activity logged successfully"
    }


@app.post("/loan/{loan_id}/settlement-offer")
async def create_settlement_offer(
    loan_id: str,
    request: SettlementOfferRequest,
    db: Session = Depends(get_db)
):
    """Create a settlement offer for a loan."""
    from uuid import uuid4
    
    assignment = db.query(CollectionAssignment).filter(
        CollectionAssignment.loan_account_id == loan_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    outstanding = assignment.outstanding_amount
    settlement_percentage = (request.offer_amount / outstanding) * 100
    
    negotiation = SettlementNegotiation(
        id=str(uuid4()),
        loan_account_id=loan_id,
        outstanding_amount=outstanding,
        offer_amount=request.offer_amount,
        settlement_percentage=settlement_percentage,
        status="pending"
    )
    
    db.add(negotiation)
    db.commit()
    
    return {
        "negotiation_id": negotiation.id,
        "outstanding_amount": outstanding,
        "offer_amount": request.offer_amount,
        "settlement_percentage": settlement_percentage,
        "status": "pending"
    }


@app.post("/loan/{loan_id}/npa-classification")
async def classify_npa(
    loan_id: str,
    npa_type: str = Query("substandard"),
    db: Session = Depends(get_db)
):
    """Classify loan as NPA."""
    from uuid import uuid4
    
    # Check if already classified
    existing = db.query(NPARecord).filter(
        NPARecord.loan_account_id == loan_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Loan already classified as NPA")
    
    # Create NPA record
    provision_percentages = {
        "substandard": 0.15,
        "doubtful": 0.25,
        "loss": 1.0
    }
    
    npa_record = NPARecord(
        id=str(uuid4()),
        loan_account_id=loan_id,
        npa_type=npa_type,
        provision_percentage=provision_percentages.get(npa_type, 0.15)
    )
    
    db.add(npa_record)
    db.commit()
    
    return {
        "message": f"Loan classified as NPA - {npa_type}",
        "provision_percentage": npa_record.provision_percentage
    }


@app.get("/")
async def root():
    return {"service": "collections", "version": "0.1.0"}
