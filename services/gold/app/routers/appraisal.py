"""
Gold Appraisal Engine API
Phase 3: Advanced Ornament Cataloging & Valuation
"""
from datetime import datetime, date
from typing import List, Optional
from uuid import uuid4
import random
import string

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc

from ..models.appraisal import (
    GoldOrnamentType,
    GoldMarketRate,
    GoldAppraisalSession,
    GoldPurityTest,
    GoldWeightVerification,
    GoldOrnamentValuation,
    GoldAppraisalAnomaly
)
from ..schemas.appraisal import (
    OrnamentTypeResponse,
    MarketRateCreate,
    MarketRateResponse,
    AppraisalSessionCreate,
    AppraisalSessionUpdate,
    AppraisalSessionResponse,
    OrnamentCreate,
    OrnamentResponse,
    OrnamentPhotoUpload,
    PurityTestCreate,
    PurityTestVerify,
    PurityTestResponse,
    WeightMeasurement,
    WeightVerificationSubmit,
    WeightVerificationResponse,
    ValuationCreate,
    ValuationResponse,
    AnomalyCreate,
    AnomalyResolve,
    AnomalyResponse,
    AppraisalSummary,
    QuickAppraisal,
    QuickAppraisalResult
)

router = APIRouter(prefix="/appraisal", tags=["Gold Appraisal"])


def get_db():
    """Placeholder for database session"""
    pass


def generate_barcode() -> str:
    """Generate unique barcode for ornament"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"GLO-{timestamp}-{random_part}"


def generate_session_number() -> str:
    """Generate unique appraisal session number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"GLA-{timestamp}-{uuid4().hex[:6].upper()}"


# ============================================================================
# ORNAMENT TYPES
# ============================================================================

@router.get("/ornament-types", response_model=List[OrnamentTypeResponse])
async def list_ornament_types(
    category: Optional[str] = Query(None),
    is_active: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List all ornament types"""
    query = db.query(GoldOrnamentType).filter(GoldOrnamentType.is_active == is_active)
    
    if category:
        query = query.filter(GoldOrnamentType.category == category)
    
    types = query.order_by(GoldOrnamentType.display_order).all()
    return types


# ============================================================================
# GOLD MARKET RATES
# ============================================================================

@router.post("/market-rates", response_model=MarketRateResponse, status_code=201)
async def create_market_rate(rate_data: MarketRateCreate, db: Session = Depends(get_db)):
    """
    Create or update gold market rate
    
    Rates can be set per city, branch, or globally.
    Multiple rates for different purities (22K, 18K, 24K).
    """
    # Check for existing active rate for same date, purity, location
    existing = db.query(GoldMarketRate).filter(
        and_(
            GoldMarketRate.rate_date == rate_data.rate_date,
            GoldMarketRate.purity_karat == rate_data.purity_karat,
            GoldMarketRate.is_active == True
        )
    ).first()
    
    if existing and rate_data.branch_id:
        # Check if same branch
        if existing.branch_id == rate_data.branch_id:
            existing.is_active = False  # Deactivate old rate
    
    # Calculate rate per 10 gram
    rate_per_10gram = rate_data.rate_per_10gram or (rate_data.rate_per_gram * 10)
    
    rate = GoldMarketRate(
        id=str(uuid4()),
        rate_date=rate_data.rate_date,
        rate_source=rate_data.rate_source,
        purity_karat=rate_data.purity_karat,
        rate_per_gram=rate_data.rate_per_gram,
        rate_per_10gram=rate_per_10gram,
        currency=rate_data.currency,
        city=rate_data.city,
        branch_id=rate_data.branch_id,
        effective_from=rate_data.effective_from,
        effective_to=rate_data.effective_to,
        rate_metadata=rate_data.rate_metadata
    )
    
    db.add(rate)
    db.commit()
    db.refresh(rate)
    
    return rate


@router.get("/market-rates/current", response_model=List[MarketRateResponse])
async def get_current_rates(
    purity_karat: Optional[float] = Query(None),
    branch_id: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get current active gold rates
    
    Returns most recent active rates filtered by purity, branch, or city.
    """
    query = db.query(GoldMarketRate).filter(
        and_(
            GoldMarketRate.is_active == True,
            GoldMarketRate.effective_from <= datetime.utcnow(),
            or_(
                GoldMarketRate.effective_to.is_(None),
                GoldMarketRate.effective_to >= datetime.utcnow()
            )
        )
    )
    
    if purity_karat:
        query = query.filter(GoldMarketRate.purity_karat == purity_karat)
    if branch_id:
        query = query.filter(GoldMarketRate.branch_id == branch_id)
    if city:
        query = query.filter(GoldMarketRate.city == city)
    
    rates = query.order_by(desc(GoldMarketRate.effective_from)).all()
    return rates


@router.get("/market-rates/{rate_id}", response_model=MarketRateResponse)
async def get_market_rate(rate_id: str, db: Session = Depends(get_db)):
    """Get specific market rate"""
    rate = db.query(GoldMarketRate).filter(GoldMarketRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=404, detail="Market rate not found")
    return rate


# ============================================================================
# APPRAISAL SESSIONS
# ============================================================================

@router.post("/sessions", response_model=AppraisalSessionResponse, status_code=201)
async def create_appraisal_session(
    session_data: AppraisalSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create new appraisal session
    
    Links to application and tracks multiple ornaments being appraised.
    """
    # Check if application already has an active session
    existing = db.query(GoldAppraisalSession).filter(
        and_(
            GoldAppraisalSession.application_id == session_data.application_id,
            GoldAppraisalSession.session_status.in_(["in_progress", "completed"])
        )
    ).first()
    
    if existing:
        return existing  # Return existing session
    
    # Get current gold rate if not provided
    gold_rate_id = session_data.gold_rate_id
    if not gold_rate_id:
        current_rate = db.query(GoldMarketRate).filter(
            and_(
                GoldMarketRate.is_active == True,
                GoldMarketRate.purity_karat == 22.0  # Default to 22K
            )
        ).order_by(desc(GoldMarketRate.effective_from)).first()
        
        if current_rate:
            gold_rate_id = current_rate.id
    
    session = GoldAppraisalSession(
        id=str(uuid4()),
        application_id=session_data.application_id,
        session_number=generate_session_number(),
        customer_id=session_data.customer_id,
        appraiser_user_id=session_data.appraiser_user_id,
        gold_rate_id=gold_rate_id,
        ltv_percent=session_data.ltv_percent,
        session_notes=session_data.session_notes
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions/{session_id}", response_model=AppraisalSummary)
async def get_appraisal_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get complete appraisal session with all ornaments, tests, and anomalies
    """
    session = db.query(GoldAppraisalSession).options(
        joinedload(GoldAppraisalSession.gold_rate)
    ).filter(GoldAppraisalSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Appraisal session not found")
    
    # Get all ornaments in this session
    from ..models.journey import Base as JourneyBase  # Import for gold_ornaments
    # In production, import actual GoldOrnament model
    ornaments = []  # Placeholder - fetch from gold_ornaments table
    
    # Get all purity tests
    purity_tests = db.query(GoldPurityTest).filter(
        GoldPurityTest.ornament_id.in_([o.id for o in ornaments])
    ).all() if ornaments else []
    
    # Get anomalies
    anomalies = db.query(GoldAppraisalAnomaly).filter(
        GoldAppraisalAnomaly.appraisal_session_id == session_id
    ).all()
    
    # Calculate stats
    total_stats = {
        "total_ornaments": session.total_ornaments,
        "total_gross_weight": session.total_gross_weight,
        "total_net_weight": session.total_net_weight,
        "total_value": session.total_appraised_value,
        "average_purity": session.average_purity_karat,
        "eligible_loan": session.eligible_loan_amount,
        "ltv": session.ltv_percent
    }
    
    return AppraisalSummary(
        session=session,
        ornaments=ornaments,
        purity_tests=purity_tests,
        anomalies=anomalies,
        gold_rate=session.gold_rate,
        total_stats=total_stats
    )


@router.patch("/sessions/{session_id}", response_model=AppraisalSessionResponse)
async def update_appraisal_session(
    session_id: str,
    update_data: AppraisalSessionUpdate,
    db: Session = Depends(get_db)
):
    """Update appraisal session"""
    session = db.query(GoldAppraisalSession).filter(
        GoldAppraisalSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    
    return session


@router.post("/sessions/{session_id}/complete")
async def complete_appraisal_session(session_id: str, db: Session = Depends(get_db)):
    """
    Complete appraisal session and calculate final values
    
    Recalculates all totals, applies LTV, determines eligible loan amount.
    """
    session = db.query(GoldAppraisalSession).filter(
        GoldAppraisalSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.session_status == "completed":
        return {"message": "Session already completed"}
    
    # Fetch all ornaments (placeholder - actual implementation needed)
    # Calculate totals from ornaments
    total_gross = 0
    total_net = 0
    total_value = 0
    ornament_count = 0
    total_purity = 0
    
    # For each ornament in session:
    #   total_gross += ornament.gross_weight_grams
    #   total_net += ornament.net_weight_grams
    #   total_value += ornament.appraised_value
    #   total_purity += ornament.purity_karat
    #   ornament_count += 1
    
    # Update session
    session.total_ornaments = ornament_count
    session.total_gross_weight = total_gross
    session.total_net_weight = total_net
    session.total_appraised_value = total_value
    session.average_purity_karat = total_purity / ornament_count if ornament_count > 0 else 0
    
    # Calculate eligible loan amount
    ltv = session.ltv_percent or 75.0
    session.eligible_loan_amount = round(total_value * ltv / 100, 2)
    
    session.session_status = "completed"
    session.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Appraisal completed successfully",
        "eligible_loan_amount": session.eligible_loan_amount,
        "total_value": session.total_appraised_value
    }


# ============================================================================
# PURITY TESTS
# ============================================================================

@router.post("/purity-tests", response_model=PurityTestResponse, status_code=201)
async def create_purity_test(test_data: PurityTestCreate, db: Session = Depends(get_db)):
    """
    Record purity test for an ornament
    
    Supports multiple test methods: touchstone, XRF, fire assay, acid test.
    Multiple tests can be conducted on same ornament for verification.
    """
    # Calculate purity percentage from karat
    purity_percent = round((test_data.tested_karat / 24) * 100, 4)
    
    test = GoldPurityTest(
        id=str(uuid4()),
        ornament_id=test_data.ornament_id,
        test_number=test_data.test_number,
        test_method=test_data.test_method,
        tested_karat=test_data.tested_karat,
        tested_purity_percent=purity_percent,
        test_equipment=test_data.test_equipment,
        test_location=test_data.test_location,
        tested_by_user_id=test_data.tested_by_user_id,
        test_results=test_data.test_results,
        test_certificate_url=test_data.test_certificate_url,
        notes=test_data.notes
    )
    
    db.add(test)
    db.commit()
    db.refresh(test)
    
    # Check for purity variance anomaly
    previous_tests = db.query(GoldPurityTest).filter(
        and_(
            GoldPurityTest.ornament_id == test_data.ornament_id,
            GoldPurityTest.id != test.id
        )
    ).all()
    
    if previous_tests:
        variance = abs(test.tested_karat - previous_tests[0].tested_karat)
        if variance > 1.0:  # More than 1K variance
            anomaly = GoldAppraisalAnomaly(
                id=str(uuid4()),
                ornament_id=test_data.ornament_id,
                anomaly_type="purity_variance",
                severity="high" if variance > 2.0 else "medium",
                anomaly_description=f"Purity test variance of {variance}K detected",
                detected_by="system",
                detection_data={"variance_karat": variance, "test_id": test.id}
            )
            db.add(anomaly)
            db.commit()
    
    return test


@router.patch("/purity-tests/{test_id}/verify", response_model=PurityTestResponse)
async def verify_purity_test(
    test_id: str,
    verify_data: PurityTestVerify,
    db: Session = Depends(get_db)
):
    """Verify purity test (maker-checker)"""
    test = db.query(GoldPurityTest).filter(GoldPurityTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Purity test not found")
    
    test.is_verified = verify_data.is_verified
    test.verified_by_user_id = verify_data.verified_by_user_id
    test.verified_at = datetime.utcnow()
    
    if verify_data.notes:
        test.notes = f"{test.notes or ''}\nVerification: {verify_data.notes}"
    
    db.commit()
    db.refresh(test)
    
    return test


@router.get("/purity-tests/ornament/{ornament_id}", response_model=List[PurityTestResponse])
async def list_purity_tests(ornament_id: str, db: Session = Depends(get_db)):
    """List all purity tests for an ornament"""
    tests = db.query(GoldPurityTest).filter(
        GoldPurityTest.ornament_id == ornament_id
    ).order_by(GoldPurityTest.test_number).all()
    return tests


# ============================================================================
# WEIGHT VERIFICATION
# ============================================================================

@router.post("/weight-measurements", response_model=WeightVerificationResponse, status_code=201)
async def record_weight_measurement(
    measurement: WeightMeasurement,
    db: Session = Depends(get_db)
):
    """
    Record weight measurement (maker step)
    
    Implements maker-checker pattern for critical weight measurements.
    """
    verification = GoldWeightVerification(
        id=str(uuid4()),
        ornament_id=measurement.ornament_id,
        measurement_type=measurement.measurement_type,
        measured_by_user_id=measurement.measured_by_user_id,
        measured_weight=measurement.measured_weight,
        weighing_scale_id=measurement.weighing_scale_id
    )
    
    db.add(verification)
    db.commit()
    db.refresh(verification)
    
    return verification


@router.post("/weight-measurements/{verification_id}/verify", response_model=WeightVerificationResponse)
async def verify_weight_measurement(
    verification_id: str,
    verify_data: WeightVerificationSubmit,
    verified_by_user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Verify weight measurement (checker step)
    
    Calculates variance and flags if outside tolerance.
    """
    verification = db.query(GoldWeightVerification).filter(
        GoldWeightVerification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Weight verification not found")
    
    if verification.measured_by_user_id == verified_by_user_id:
        raise HTTPException(
            status_code=400,
            detail="Verifier cannot be the same as measurer (maker-checker violation)"
        )
    
    variance = abs(verify_data.verified_weight - verification.measured_weight)
    
    verification.verified_by_user_id = verified_by_user_id
    verification.verified_weight = verify_data.verified_weight
    verification.verification_timestamp = datetime.utcnow()
    verification.variance_grams = variance
    verification.is_accepted = verify_data.is_accepted
    verification.rejection_reason = verify_data.rejection_reason
    
    # Flag anomaly if variance is high
    if variance > 0.1:  # More than 0.1g variance
        anomaly = GoldAppraisalAnomaly(
            id=str(uuid4()),
            ornament_id=verification.ornament_id,
            anomaly_type="weight_mismatch",
            severity="high" if variance > 0.5 else "medium",
            anomaly_description=f"Weight variance of {variance}g detected",
            detected_by="system",
            detection_data={"variance_grams": variance, "verification_id": verification_id}
        )
        db.add(anomaly)
    
    db.commit()
    db.refresh(verification)
    
    return verification


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

@router.post("/anomalies", response_model=AnomalyResponse, status_code=201)
async def create_anomaly(anomaly_data: AnomalyCreate, db: Session = Depends(get_db)):
    """Report anomaly or suspicious activity"""
    anomaly = GoldAppraisalAnomaly(
        id=str(uuid4()),
        **anomaly_data.model_dump()
    )
    
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    
    return anomaly


@router.patch("/anomalies/{anomaly_id}/resolve", response_model=AnomalyResponse)
async def resolve_anomaly(
    anomaly_id: str,
    resolve_data: AnomalyResolve,
    db: Session = Depends(get_db)
):
    """Resolve or mark anomaly as false positive"""
    anomaly = db.query(GoldAppraisalAnomaly).filter(
        GoldAppraisalAnomaly.id == anomaly_id
    ).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    anomaly.status = resolve_data.status
    anomaly.resolution_notes = resolve_data.resolution_notes
    anomaly.resolved_by_user_id = resolve_data.resolved_by_user_id
    anomaly.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(anomaly)
    
    return anomaly


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def list_anomalies(
    session_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List anomalies with filters"""
    query = db.query(GoldAppraisalAnomaly)
    
    if session_id:
        query = query.filter(GoldAppraisalAnomaly.appraisal_session_id == session_id)
    if severity:
        query = query.filter(GoldAppraisalAnomaly.severity == severity)
    if status:
        query = query.filter(GoldAppraisalAnomaly.status == status)
    
    anomalies = query.order_by(desc(GoldAppraisalAnomaly.created_at)).all()
    return anomalies


# ============================================================================
# QUICK APPRAISAL (for instant loans)
# ============================================================================

@router.post("/quick-appraisal", response_model=QuickAppraisalResult)
async def perform_quick_appraisal(
    appraisal: QuickAppraisal,
    db: Session = Depends(get_db)
):
    """
    Quick appraisal for instant gold loans
    
    Provides instant valuation without full appraisal process.
    Limited to small amounts and simplified assessment.
    """
    # Get current gold rate
    gold_rate = db.query(GoldMarketRate).filter(
        and_(
            GoldMarketRate.is_active == True,
            GoldMarketRate.purity_karat == appraisal.estimated_purity_karat
        )
    ).order_by(desc(GoldMarketRate.effective_from)).first()
    
    if not gold_rate:
        raise HTTPException(status_code=404, detail="Current gold rate not available")
    
    # Simple valuation calculation
    purity_percent = (appraisal.estimated_purity_karat / 24) * 100
    estimated_value = round(
        appraisal.gross_weight_grams * gold_rate.rate_per_gram * purity_percent / 100,
        2
    )
    
    # Apply conservative LTV for instant loans
    instant_ltv = 70.0
    eligible_amount = round(estimated_value * instant_ltv / 100, 2)
    
    # Check instant approval limits
    instant_limit = 50000  # ₹50,000 instant approval limit
    instant_approval = eligible_amount <= instant_limit
    requires_full_appraisal = eligible_amount > instant_limit
    
    return QuickAppraisalResult(
        estimated_value=estimated_value,
        eligible_loan_amount=eligible_amount,
        gold_rate_used=gold_rate.rate_per_gram,
        ltv_applied=instant_ltv,
        instant_approval=instant_approval,
        approval_limit=instant_limit,
        requires_full_appraisal=requires_full_appraisal
    )
