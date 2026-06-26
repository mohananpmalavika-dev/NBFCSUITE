from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Query, Header
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
    branch_id = Column(String, index=True, nullable=True)
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
    disbursed_date = Column(DateTime, nullable=True)
    disbursed_amount = Column(Float, nullable=True)
    lms_booking_status = Column(String, default="not_started")
    lms_loan_account_id = Column(String, nullable=True)
    lms_booking_error = Column(String, nullable=True)
    lms_disbursement_status = Column(String, default="not_started")
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationDocument(Base):
    __tablename__ = "application_documents"
    
    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("loan_applications.id"))
    document_type = Column(String)
    document_url = Column(String)
    document_service_id = Column(String, nullable=True)
    verification_status = Column(String, default="pending")
    ocr_result = Column(JSON, nullable=True)
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
    branch_id: Optional[str] = None
    product_code: str
    applied_amount: float
    tenure_months: int


class LoanApplicationResponse(BaseModel):
    id: str
    customer_id: str
    branch_id: Optional[str] = None
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
    branch_id: Optional[str] = None
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
    disbursed_date: Optional[datetime] = None
    disbursed_amount: Optional[float] = None
    lms_booking_status: Optional[str] = None
    lms_loan_account_id: Optional[str] = None
    lms_disbursement_status: Optional[str] = None
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
    lms_booking_status: Optional[str] = None
    lms_loan_account_id: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationDisbursementResponse(BaseModel):
    application_id: str
    status: str
    disbursed_date: datetime
    disbursed_amount: Optional[float] = None


# FastAPI App
app = FastAPI(title="los-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PrincipalScope:
    def __init__(self, branch_id: Optional[str] = None):
        self.branch_id = branch_id

    @property
    def is_scoped(self) -> bool:
        return bool(self.branch_id)


def get_principal_scope(
    branch_id: Optional[str] = Header(default=None, alias="X-Scope-Branch-Id"),
    legacy_branch_id: Optional[str] = Header(default=None, alias="X-Branch-Id"),
) -> PrincipalScope:
    return PrincipalScope(branch_id=branch_id or legacy_branch_id)


def _assert_application_in_scope(application: LoanApplication, scope: PrincipalScope) -> None:
    if not isinstance(scope, PrincipalScope):
        return
    if scope.is_scoped and application.branch_id != scope.branch_id:
        raise HTTPException(status_code=403, detail="Application is outside the caller's branch scope")


def _resolve_branch_id(requested_branch_id: Optional[str], scope: PrincipalScope) -> Optional[str]:
    if not isinstance(scope, PrincipalScope):
        return requested_branch_id
    if scope.is_scoped and requested_branch_id and requested_branch_id != scope.branch_id:
        raise HTTPException(status_code=403, detail="Branch is outside the caller's branch scope")
    return requested_branch_id or scope.branch_id


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


def _get_product_by_code(product_code: str, db: Session) -> LoanProduct:
    product = db.query(LoanProduct).filter(LoanProduct.product_code == product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if str(product.is_active).lower() not in {"1", "true", "yes", "active"}:
        raise HTTPException(status_code=400, detail="Product is inactive")
    return product


def _validate_terms(product: LoanProduct, amount: float, tenure_months: int) -> None:
    if amount < product.min_amount or amount > product.max_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Amount must be between {product.min_amount} and {product.max_amount}",
        )
    if tenure_months < product.min_tenor or tenure_months > product.max_tenor:
        raise HTTPException(
            status_code=400,
            detail=f"Tenure must be between {product.min_tenor} and {product.max_tenor} months",
        )


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


def trigger_underwriting_assistant(application: LoanApplication, event: str) -> None:
    """Best-effort FinDNA assistant hook; never blocks LOS state transitions."""
    try:
        import httpx

        findna_base = os.getenv("FINDNA_BASE_URL", "http://localhost:8006")
        payload = {
            "customer_id": application.customer_id,
            "application_id": application.id,
            "subject_type": "application",
            "subject_id": application.id,
            "source_service": "los",
            "source_reference_id": application.id,
            "context_text": (
                f"LOS {event}: status={application.application_status}, "
                f"amount={application.applied_amount}, tenure={application.tenure_months}"
            ),
        }
        with httpx.Client(timeout=5.0) as client:
            client.post(f"{findna_base}/underwriting-assistant/{application.id}", json=payload)
    except Exception:
        pass


def register_document_with_document_service(
    application: LoanApplication,
    document_type: str,
    document_name: str,
    document_url: str,
) -> dict:
    """Best-effort Document Service registration with deterministic local fallback."""
    try:
        import httpx

        document_base = os.getenv("DOCUMENT_BASE_URL", "http://localhost:8010")
        payload = {
            "subject_type": "loan_application",
            "subject_id": application.id,
            "document_type": document_type,
            "document_name": document_name,
            "document_url": document_url,
            "metadata": {
                "customer_id": application.customer_id,
                "branch_id": application.branch_id,
                "ocr_status": "queued",
                "source_service": "los",
            },
        }
        with httpx.Client(timeout=5.0) as client:
            response = client.post(f"{document_base}/documents", json=payload)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        return {
            "id": None,
            "status": "pending",
            "metadata": {
                "ocr_status": "deferred",
                "document_service_error": str(exc),
            },
        }


def book_approved_application_in_lms(application: LoanApplication) -> None:
    if application.lms_booking_status == "booked" and application.lms_loan_account_id:
        return

    application.lms_booking_status = "pending"
    application.lms_booking_error = None

    try:
        import httpx

        lms_base = os.getenv("LMS_BASE_URL", "http://localhost:8003")
        payload = {
            "application_id": application.id,
            "customer_id": application.customer_id,
            "branch_id": application.branch_id,
            "product_id": application.product_id,
            "sanction_amount": application.sanctioned_amount,
            "tenure_months": application.tenure_months,
            "interest_rate": application.final_interest_rate,
        }

        with httpx.Client(timeout=5.0) as client:
            response = client.post(f"{lms_base}/loans", json=payload)
            if response.status_code == 400 and "already exists" in response.text.lower():
                application.lms_booking_status = "booked"
                application.lms_booking_error = None
                return
            response.raise_for_status()
            loan_record = response.json()
            application.lms_booking_status = "booked"
            application.lms_loan_account_id = loan_record.get("id")
            application.lms_booking_error = None
    except Exception as exc:
        application.lms_booking_status = "failed"
        application.lms_booking_error = str(exc)


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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Create a new loan application."""
    from uuid import uuid4
    
    product = _get_product_by_code(app_data.product_code, db)
    _validate_terms(product, app_data.applied_amount, app_data.tenure_months)
    branch_id = _resolve_branch_id(app_data.branch_id, scope)
    
    # Create application
    new_app = LoanApplication(
        id=str(uuid4()),
        customer_id=app_data.customer_id,
        branch_id=branch_id,
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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Get application details."""
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(application, scope)
    
    return application


@app.get("/applications/{application_id}/detail", response_model=LoanApplicationDetailResponse)
async def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Get detailed application data for underwriting and integration."""
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(application, scope)
    
    return application


@app.get("/applications")
async def list_applications(
    customer_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """List applications with optional filters."""
    query = db.query(LoanApplication)
    
    if customer_id:
        query = query.filter(LoanApplication.customer_id == customer_id)
    selected_branch_id = _resolve_branch_id(branch_id, scope)
    if selected_branch_id:
        query = query.filter(LoanApplication.branch_id == selected_branch_id)
    
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
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Upload document for application."""
    from uuid import uuid4
    
    app = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(app, scope)
    
    # Simulate file upload (in production, save to S3/blob storage)
    document_url = f"s3://nbfcsuite-documents/{application_id}/{file.filename}"
    document_record = register_document_with_document_service(
        app,
        document_type,
        file.filename,
        document_url,
    )
    metadata = document_record.get("metadata") or {}
    
    doc = ApplicationDocument(
        id=str(uuid4()),
        application_id=application_id,
        document_type=document_type,
        document_url=document_url,
        document_service_id=document_record.get("id"),
        verification_status=document_record.get("status", "pending"),
        ocr_result={
            "status": metadata.get("ocr_status", "queued"),
            "document_service_id": document_record.get("id"),
            "error": metadata.get("document_service_error"),
        },
    )
    
    db.add(doc)
    db.commit()
    
    return {
        "message": "Document uploaded",
        "document_url": document_url,
        "document_service_id": doc.document_service_id,
        "verification_status": doc.verification_status,
        "ocr_result": doc.ocr_result,
    }


@app.post("/applications/{application_id}/submit")
async def submit_application(
    application_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Submit application for underwriting.

    Phase 1 wiring: on submit, generate FindNA behavioral scoring for the customer.
    """
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(application, scope)
    if application.application_status not in {"draft", "submitted"}:
        raise HTTPException(status_code=400, detail="Only draft applications can be submitted")

    application.application_status = "submitted"
    application.submitted_date = application.submitted_date or datetime.utcnow()
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

    trigger_underwriting_assistant(application, "submitted")

    return {"message": "Application submitted", "application_id": application.id}



@app.post("/applications/{application_id}/underwrite", response_model=ScorecardResponse)
async def underwrite_application(
    application_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Run underwriting on a submitted loan application."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(application, scope)
    if application.application_status not in {"submitted", "under_review"}:
        raise HTTPException(status_code=400, detail="Only submitted applications can be underwritten")

    application.application_status = "under_review"
    db.commit()
    db.refresh(application)

    scorecard = create_or_update_scorecard(application, db)
    trigger_underwriting_assistant(application, "under_review")
    return scorecard


@app.post("/applications/{application_id}/decision", response_model=UnderwritingDecisionResponse)
async def decide_application(
    application_id: str,
    decision: UnderwritingDecisionRequest,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Approve or reject an application based on underwriting."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(application, scope)
    if application.application_status == "approved" and decision.decision.lower() == "approved":
        book_approved_application_in_lms(application)
        db.commit()
        db.refresh(application)
        return UnderwritingDecisionResponse(
            application_id=application.id,
            status=application.application_status,
            message="Application already approved",
            sanctioned_amount=application.sanctioned_amount,
            final_interest_rate=application.final_interest_rate,
            decision_date=application.decision_date,
            lms_booking_status=application.lms_booking_status,
            lms_loan_account_id=application.lms_loan_account_id,
        )
    if application.application_status not in {"submitted", "under_review"}:
        raise HTTPException(status_code=400, detail="Application is not ready for decision")

    if decision.decision.lower() == "approved":
        if decision.approved_amount is None or decision.approved_tenure_months is None or decision.approved_interest_rate is None:
            raise HTTPException(status_code=400, detail="approved_amount, approved_tenure_months and approved_interest_rate are required for approval")
        product = db.query(LoanProduct).filter(LoanProduct.id == application.product_id).first()
        if product:
            _validate_terms(product, decision.approved_amount, decision.approved_tenure_months)
        if decision.approved_amount > application.applied_amount:
            raise HTTPException(status_code=400, detail="approved_amount cannot exceed applied_amount")
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

    if application.application_status == "approved":
        book_approved_application_in_lms(application)
        db.commit()
        db.refresh(application)

    trigger_underwriting_assistant(application, f"decision_{application.application_status}")

    return UnderwritingDecisionResponse(
        application_id=application.id,
        status=application.application_status,
        message=message,
        sanctioned_amount=application.sanctioned_amount,
        final_interest_rate=application.final_interest_rate,
        decision_date=application.decision_date,
        lms_booking_status=application.lms_booking_status,
        lms_loan_account_id=application.lms_loan_account_id,
    )


@app.post("/applications/{application_id}/disburse", response_model=ApplicationDisbursementResponse)
async def mark_application_disbursed(
    application_id: str,
    amount: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Mark an approved application as disbursed after LMS disbursement succeeds."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _assert_application_in_scope(application, scope)
    if application.application_status == "disbursed" and application.disbursed_date:
        return {
            "application_id": application.id,
            "status": application.application_status,
            "disbursed_date": application.disbursed_date,
            "disbursed_amount": application.disbursed_amount,
        }
    if application.application_status != "approved":
        raise HTTPException(status_code=400, detail="Only approved applications can be disbursed")

    disbursed_at = datetime.utcnow()
    application.application_status = "disbursed"
    application.disbursed_date = disbursed_at
    application.disbursed_amount = amount or application.sanctioned_amount
    application.lms_disbursement_status = "disbursed"
    db.commit()
    db.refresh(application)
    trigger_underwriting_assistant(application, "disbursed")
    return {
        "application_id": application.id,
        "status": application.application_status,
        "disbursed_date": disbursed_at,
        "disbursed_amount": application.disbursed_amount,
    }



@app.get("/applications/{application_id}/scorecard", response_model=ScorecardResponse)
async def get_scorecard(
    application_id: str,
    db: Session = Depends(get_db),
    scope: PrincipalScope = Depends(get_principal_scope),
):
    """Get application scorecard."""
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if application:
        _assert_application_in_scope(application, scope)
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
