from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum as PyEnum
from uuid import uuid4
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class ApplicationStatus(str, PyEnum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    disbursed = "disbursed"


# SQLAlchemy Models
class LoanProduct(Base):
    __tablename__ = "loan_products"
    
    id = Column(String, primary_key=True)
    product_code = Column(String, unique=True, index=True)
    product_name = Column(String)
    product_type = Column(String)
    min_amount = Column(Float)
    max_amount = Column(Float)
    min_tenor = Column(Integer)
    max_tenor = Column(Integer)
    base_rate = Column(Float)
    processing_fee_percent = Column(Float)
    is_active = Column(String, default=True)


class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(String, primary_key=True)
    customer_id = Column(String, index=True)
    product_id = Column(String, ForeignKey("loan_products.id"))
    application_status = Column(String, default="draft")
    applied_amount = Column(Float)
    sanctioned_amount = Column(Float, nullable=True)
    tenure_months = Column(Integer)
    applied_interest_rate = Column(Float)
    final_interest_rate = Column(Float, nullable=True)
    application_date = Column(DateTime, default=datetime.utcnow)
    submitted_date = Column(DateTime, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    
    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("loan_applications.id"))
    document_type = Column(String)
    document_url = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)


class ApplicationScorecard(Base):
    __tablename__ = "application_scorecards"
    
    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("loan_applications.id"), unique=True)
    credit_score = Column(Integer)
    behavior_score = Column(Float)
    fraud_score = Column(Float)
    overall_score = Column(Float)
    recommendation = Column(String)
    scoring_date = Column(DateTime, default=datetime.utcnow)


# Pydantic Schemas
class LoanApplicationCreate(BaseModel):
    customer_id: str
    product_code: str
    applied_amount: float
    tenure_months: int


class LoanApplicationResponse(BaseModel):
    id: str
    customer_id: str
    application_status: str
    applied_amount: float
    tenure_months: int
    application_date: datetime
    
    class Config:
        from_attributes = True


class ScorecardResponse(BaseModel):
    credit_score: int
    behavior_score: float
    fraud_score: float
    overall_score: float
    recommendation: str
    
    class Config:
        from_attributes = True


class LoanProductCreate(BaseModel):
    product_code: str
    product_name: str
    product_type: str
    min_amount: float
    max_amount: float
    min_tenor: int
    max_tenor: int
    base_rate: float
    processing_fee_percent: float
    is_active: bool = True


class LoanProductResponse(BaseModel):
    id: str
    product_code: str
    product_name: str
    product_type: str
    min_amount: float
    max_amount: float
    min_tenor: int
    max_tenor: int
    base_rate: float
    processing_fee_percent: float
    is_active: str

    class Config:
        from_attributes = True


class LoanApplicationDetailResponse(BaseModel):
    id: str
    customer_id: str
    product_id: str
    application_status: str
    applied_amount: float
    sanctioned_amount: Optional[float] = None
    tenure_months: int
    applied_interest_rate: float
    final_interest_rate: Optional[float] = None
    application_date: datetime
    submitted_date: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UnderwritingDecisionRequest(BaseModel):
    decision: str
    approved_amount: Optional[float] = None
    approved_tenure_months: Optional[int] = None
    approved_interest_rate: Optional[float] = None
    rejection_reason: Optional[str] = None


class UnderwritingDecisionResponse(BaseModel):
    application_id: str
    status: str
    message: str
    sanctioned_amount: Optional[float] = None
    final_interest_rate: Optional[float] = None
    decision_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# FastAPI App
app = FastAPI(title="los-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def compute_underwriting_score(application: LoanApplication) -> dict:
    credit_score = min(850, max(300, 700 - int(application.applied_amount / 10000)))
    behavior_score = round(80 + (application.tenure_months / 12) * 2, 1)
    fraud_score = round(max(0.0, 10 - (application.applied_amount / 100000)), 1)
    overall = round((credit_score / 850 * 0.5) + (behavior_score / 100 * 0.3) + ((100 - fraud_score) / 100 * 0.2), 2) * 100
    recommendation = "approve" if overall >= 60 else "review"
    return {
        "credit_score": min(850, max(300, credit_score)),
        "behavior_score": min(100.0, behavior_score),
        "fraud_score": max(0.0, fraud_score),
        "overall_score": min(100.0, overall),
        "recommendation": recommendation
    }


def create_or_update_scorecard(application: LoanApplication, db: Session):
    scorecard_data = compute_underwriting_score(application)
    scorecard = db.query(ApplicationScorecard).filter(ApplicationScorecard.application_id == application.id).first()
    if scorecard:
        scorecard.credit_score = scorecard_data["credit_score"]
        scorecard.behavior_score = scorecard_data["behavior_score"]
        scorecard.fraud_score = scorecard_data["fraud_score"]
        scorecard.overall_score = scorecard_data["overall_score"]
        scorecard.recommendation = scorecard_data["recommendation"]
    else:
        scorecard = ApplicationScorecard(
            id=str(uuid4()),
            application_id=application.id,
            credit_score=scorecard_data["credit_score"],
            behavior_score=scorecard_data["behavior_score"],
            fraud_score=scorecard_data["fraud_score"],
            overall_score=scorecard_data["overall_score"],
            recommendation=scorecard_data["recommendation"]
        )
        db.add(scorecard)

    db.commit()
    db.refresh(scorecard)
    return scorecard


@app.get("/health")
async def health():
    return {"status": "ok", "service": "los"}


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    if db.query(LoanProduct).count() == 0:
        sample_products = [
            LoanProduct(
                id="prod-home-loan",
                product_code="HOME_LOAN",
                product_name="Home Loan",
                product_type="secured",
                min_amount=500000,
                max_amount=5000000,
                min_tenor=60,
                max_tenor=240,
                base_rate=8.5,
                processing_fee_percent=1.0,
                is_active="true"
            ),
            LoanProduct(
                id="prod-personal-loan",
                product_code="PERSONAL_LOAN",
                product_name="Personal Loan",
                product_type="unsecured",
                min_amount=50000,
                max_amount=500000,
                min_tenor=12,
                max_tenor=60,
                base_rate=14.5,
                processing_fee_percent=1.5,
                is_active="true"
            )
        ]
        db.add_all(sample_products)
        db.commit()
    db.close()


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/products", response_model=LoanProductResponse)
async def create_product(product_data: LoanProductCreate, db: Session = Depends(get_db)):
    existing = db.query(LoanProduct).filter(LoanProduct.product_code == product_data.product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")

    new_product = LoanProduct(
        id=str(uuid4()),
        product_code=product_data.product_code,
        product_name=product_data.product_name,
        product_type=product_data.product_type,
        min_amount=product_data.min_amount,
        max_amount=product_data.max_amount,
        min_tenor=product_data.min_tenor,
        max_tenor=product_data.max_tenor,
        base_rate=product_data.base_rate,
        processing_fee_percent=product_data.processing_fee_percent,
        is_active=str(product_data.is_active).lower(),
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=list[LoanProductResponse])
async def list_products(
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    query = db.query(LoanProduct)
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_code}", response_model=LoanProductResponse)
async def get_product(product_code: str, db: Session = Depends(get_db)):
    product = db.query(LoanProduct).filter(LoanProduct.product_code == product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/applications", response_model=LoanApplicationResponse)
async def create_application(
    app_data: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create a new loan application."""
    from uuid import uuid4
    
    # Validate product
    product = db.query(LoanProduct).filter(
        LoanProduct.product_code == app_data.product_code
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if app_data.applied_amount < product.min_amount or app_data.applied_amount > product.max_amount:
        raise HTTPException(status_code=400, detail="Amount outside product limits")
    
    # Create application
    new_app = LoanApplication(
        id=str(uuid4()),
        customer_id=app_data.customer_id,
        product_id=product.id,
        applied_amount=app_data.applied_amount,
        tenure_months=app_data.tenure_months,
        applied_interest_rate=product.base_rate,
        application_status="draft"
    )
    
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return new_app


@app.get("/applications/{application_id}", response_model=LoanApplicationResponse)
async def get_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get application details."""
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application


@app.get("/applications/{application_id}/detail", response_model=LoanApplicationDetailResponse)
async def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed application data for underwriting and integration."""
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application


@app.get("/applications")
async def list_applications(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """List applications with optional filters."""
    query = db.query(LoanApplication)
    
    if customer_id:
        query = query.filter(LoanApplication.customer_id == customer_id)
    
    if status:
        query = query.filter(LoanApplication.application_status == status)
    
    total = query.count()
    applications = query.offset(skip).limit(limit).all()
    
    return {
        "items": applications,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.post("/applications/{application_id}/documents")
async def upload_document(
    application_id: str,
    document_type: str = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload document for application."""
    from uuid import uuid4
    
    app = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Simulate file upload (in production, save to S3/blob storage)
    document_url = f"s3://nbfcsuite-documents/{application_id}/{file.filename}"
    
    doc = ApplicationDocument(
        id=str(uuid4()),
        application_id=application_id,
        document_type=document_type,
        document_url=document_url
    )
    
    db.add(doc)
    db.commit()
    
    return {"message": "Document uploaded", "document_url": document_url}


@app.post("/applications/{application_id}/submit")
async def submit_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Submit application for underwriting.

    Phase 1 wiring: on submit, generate FindNA behavioral scoring for the customer.
    """
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.application_status = "submitted"
    application.submitted_date = datetime.utcnow()
    db.commit()
    db.refresh(application)

    # Trigger FindNA behavioral score generation (best-effort).
    # We keep it synchronous for now; later this can be event-driven.
    try:
        # FindNA behavioral score endpoint:
        # POST /score/behavior with {customer_id, income_data?, bank_statement_url?, ...}
        # We only have application-level data here, so send minimal payload.
        import httpx

        findna_base = os.getenv("FINDNA_BASE_URL", "http://localhost:8006")
        payload = {
            "customer_id": application.customer_id,
            "application_id": application.id,
        }
        with httpx.Client(timeout=5.0) as client:
            client.post(f"{findna_base}/score/behavior", json=payload)
    except Exception:
        # Do not fail LOS submit on downstream scoring.
        pass

    return {"message": "Application submitted", "application_id": application.id}



@app.post("/applications/{application_id}/underwrite", response_model=ScorecardResponse)
async def underwrite_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Run underwriting on a submitted loan application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.application_status not in {"submitted", "under_review", "draft"}:
        raise HTTPException(status_code=400, detail="Only submitted applications can be underwritten")

    application.application_status = "under_review"
    db.commit()
    db.refresh(application)

    scorecard = create_or_update_scorecard(application, db)
    return scorecard


@app.post("/applications/{application_id}/decision", response_model=UnderwritingDecisionResponse)
async def decide_application(
    application_id: str,
    decision: UnderwritingDecisionRequest,
    db: Session = Depends(get_db)
):
    """Approve or reject an application based on underwriting."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.application_status not in {"submitted", "under_review"}:
        raise HTTPException(status_code=400, detail="Application is not ready for decision")

    if decision.decision.lower() == "approved":
        if decision.approved_amount is None or decision.approved_tenure_months is None or decision.approved_interest_rate is None:
            raise HTTPException(status_code=400, detail="approved_amount, approved_tenure_months and approved_interest_rate are required for approval")
        application.application_status = "approved"
        application.sanctioned_amount = decision.approved_amount
        application.final_interest_rate = decision.approved_interest_rate
        application.tenure_months = decision.approved_tenure_months
        application.decision_date = datetime.utcnow()
        application.rejection_reason = None
        message = "Application approved"
    elif decision.decision.lower() == "rejected":
        if not decision.rejection_reason:
            raise HTTPException(status_code=400, detail="rejection_reason is required for rejection")
        application.application_status = "rejected"
        application.rejection_reason = decision.rejection_reason
        application.decision_date = datetime.utcnow()
        message = "Application rejected"
    else:
        raise HTTPException(status_code=400, detail="Decision must be 'approved' or 'rejected'")

    db.commit()
    db.refresh(application)
    scorecard = db.query(ApplicationScorecard).filter(ApplicationScorecard.application_id == application_id).first()
    if not scorecard:
        scorecard = create_or_update_scorecard(application, db)

    # Phase 1 wiring: if approved, book the loan in LMS.
    if application.application_status == "approved":
        try:
            import httpx

            lms_base = os.getenv("LMS_BASE_URL", "http://localhost:8003")

            # LOS decision payload includes sanctioned_amount, tenure_months, final_interest_rate.
            # LMS expects: application_id, customer_id, product_id, sanction_amount, tenure_months, interest_rate.
            payload = {
                "application_id": application.id,
                "customer_id": application.customer_id,
                "product_id": application.product_id,
                "sanction_amount": application.sanctioned_amount,
                "tenure_months": application.tenure_months,
                "interest_rate": application.final_interest_rate,
            }

            with httpx.Client(timeout=5.0) as client:
                client.post(f"{lms_base}/loans", json=payload)
        except Exception:
            # Do not fail LOS decision on downstream booking.
            pass

    return UnderwritingDecisionResponse(
        application_id=application.id,
        status=application.application_status,
        message=message,
        sanctioned_amount=application.sanctioned_amount,
        final_interest_rate=application.final_interest_rate,
        decision_date=application.decision_date
    )



@app.get("/applications/{application_id}/scorecard", response_model=ScorecardResponse)
async def get_scorecard(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get application scorecard."""
    scorecard = db.query(ApplicationScorecard).filter(
        ApplicationScorecard.application_id == application_id
    ).first()
    
    if not scorecard:
        # Return mock scorecard if not yet generated
        return {
            "credit_score": 0,
            "behavior_score": 0.0,
            "fraud_score": 0.0,
            "overall_score": 0.0,
            "recommendation": "pending_scoring"
        }
    
    return scorecard


@app.get("/")
async def root():
    return {"service": "los", "version": "0.1.0"}
