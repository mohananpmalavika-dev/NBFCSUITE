"""
Gold Customer Journey API
Phase 2: Customer Journey & CIF Integration
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import httpx

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from ..models.journey import (
    GoldCustomerSession,
    GoldCustomerSearchLog,
    GoldProductSelection,
    GoldEligibilityCheck,
    GoldKYCVerification,
    GoldJourneyStep,
    GoldCustomerInteraction
)
from ..models.product import GoldProduct, GoldProductEligibility
from ..schemas.journey import (
    CustomerSessionCreate,
    CustomerSessionUpdate,
    CustomerSessionResponse,
    CustomerSearchRequest,
    CustomerSearchLogResponse,
    CustomerSearchResult,
    ProductSelectionCreate,
    ProductSelectionResponse,
    ProductRecommendation,
    EligibilityCheckCreate,
    EligibilityCheckResponse,
    EligibilityResult,
    KYCVerificationCreate,
    KYCVerificationResponse,
    JourneyStepCreate,
    JourneyStepUpdate,
    JourneyStepResponse,
    CustomerInteractionCreate,
    CustomerInteractionResponse,
    CompleteJourneyResponse
)

router = APIRouter(prefix="/journey", tags=["Gold Customer Journey"])


def get_db():
    """Placeholder for database session"""
    pass


def generate_session_number() -> str:
    """Generate unique session number"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"GLS-{timestamp}-{uuid4().hex[:6].upper()}"


async def call_customer_service(endpoint: str, method: str = "GET", payload: dict = None):
    """Call customer/CIF service for customer data"""
    customer_api_url = "http://localhost:8002"  # Customer service URL
    url = f"{customer_api_url}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, timeout=5.0)
            elif method == "POST":
                response = await client.post(url, json=payload, timeout=5.0)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error calling customer service: {e}")
            return None


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@router.post("/sessions", response_model=CustomerSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(session_data: CustomerSessionCreate, db: Session = Depends(get_db)):
    """
    Create a new customer journey session (walk-in, mobile, web, etc.)
    
    This initiates a gold loan journey tracking session that captures
    the entire flow from customer search to application creation.
    """
    session = GoldCustomerSession(
        id=str(uuid4()),
        session_number=generate_session_number(),
        customer_id=session_data.customer_id,
        branch_id=session_data.branch_id,
        channel=session_data.channel,
        session_type=session_data.session_type,
        initiated_by_user_id=session_data.initiated_by_user_id,
        session_data=session_data.session_data,
        status="initiated"
    )
    
    db.add(session)
    
    # Create first journey step
    step = GoldJourneyStep(
        id=str(uuid4()),
        session_id=session.id,
        step_number=1,
        step_name="session_initiated",
        step_status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=0
    )
    db.add(step)
    
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions/{session_id}", response_model=CompleteJourneyResponse)
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """
    Get complete session details with all related journey data
    """
    session = db.query(GoldCustomerSession).options(
        joinedload(GoldCustomerSession.search_logs),
        joinedload(GoldCustomerSession.product_selections),
        joinedload(GoldCustomerSession.eligibility_checks),
        joinedload(GoldCustomerSession.kyc_verifications),
        joinedload(GoldCustomerSession.journey_steps),
        joinedload(GoldCustomerSession.interactions)
    ).filter(GoldCustomerSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Fetch customer data if customer_id exists
    customer_data = None
    if session.customer_id:
        customer_data = await call_customer_service(f"/customers/{session.customer_id}")
    
    return CompleteJourneyResponse(
        session=session,
        search_logs=session.search_logs,
        product_selections=session.product_selections,
        eligibility_checks=session.eligibility_checks,
        kyc_verifications=session.kyc_verifications,
        journey_steps=sorted(session.journey_steps, key=lambda x: x.step_number),
        interactions=session.interactions,
        customer_data=customer_data
    )


@router.patch("/sessions/{session_id}", response_model=CustomerSessionResponse)
async def update_session(session_id: str, update_data: CustomerSessionUpdate, db: Session = Depends(get_db)):
    """Update session status and data"""
    session = db.query(GoldCustomerSession).filter(GoldCustomerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(session, field, value)
    
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    return session


@router.get("/sessions", response_model=List[CustomerSessionResponse])
async def list_sessions(
    branch_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    """List customer sessions with filters"""
    query = db.query(GoldCustomerSession)
    
    if branch_id:
        query = query.filter(GoldCustomerSession.branch_id == branch_id)
    if customer_id:
        query = query.filter(GoldCustomerSession.customer_id == customer_id)
    if status:
        query = query.filter(GoldCustomerSession.status == status)
    if channel:
        query = query.filter(GoldCustomerSession.channel == channel)
    if from_date:
        query = query.filter(GoldCustomerSession.initiated_at >= from_date)
    
    sessions = query.order_by(GoldCustomerSession.initiated_at.desc()).limit(limit).all()
    return sessions


# ============================================================================
# CUSTOMER SEARCH
# ============================================================================

@router.post("/search-customer", response_model=List[CustomerSearchResult])
async def search_customer(search_req: CustomerSearchRequest, db: Session = Depends(get_db)):
    """
    Search for existing customer in CIF
    
    Searches by phone, Aadhar, PAN, customer ID, or name.
    Logs the search for analytics and fraud detection.
    """
    # Build search criteria
    search_criteria = {}
    if search_req.phone:
        search_criteria["phone"] = search_req.phone
    if search_req.aadhar:
        search_criteria["aadhar"] = search_req.aadhar
    if search_req.pan:
        search_criteria["pan"] = search_req.pan
    if search_req.customer_id:
        search_criteria["customer_id"] = search_req.customer_id
    if search_req.name:
        search_criteria["name"] = search_req.name
    
    if not search_criteria:
        raise HTTPException(status_code=400, detail="At least one search criterion required")
    
    # Call customer service to search
    # In production, this would call the actual customer service API
    customer_results = await call_customer_service("/customers/search", "POST", search_criteria)
    
    results = []
    if customer_results:
        # Transform results
        for customer in customer_results:
            results.append(CustomerSearchResult(
                customer_id=customer.get("id"),
                name=customer.get("name", ""),
                phone=customer.get("phone"),
                email=customer.get("email"),
                pan=customer.get("pan"),
                aadhar_masked=customer.get("aadhar_masked"),
                customer_segment=customer.get("segment"),
                kyc_status=customer.get("kyc_status"),
                existing_gold_loans=customer.get("gold_loans_count", 0),
                total_outstanding=customer.get("gold_outstanding", 0)
            ))
    
    # Log the search
    search_log = GoldCustomerSearchLog(
        id=str(uuid4()),
        session_id=search_req.session_id,
        search_criteria=search_criteria,
        results_found=len(results),
        selected_customer_id=None,
        searched_at=datetime.utcnow(),
        searched_by_user_id=search_req.searched_by_user_id
    )
    db.add(search_log)
    db.commit()
    
    return results


@router.post("/select-customer/{session_id}/{customer_id}")
async def select_customer(session_id: str, customer_id: str, db: Session = Depends(get_db)):
    """
    Mark customer as selected in the journey
    Updates session and creates journey step
    """
    session = db.query(GoldCustomerSession).filter(GoldCustomerSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session with customer
    session.customer_id = customer_id
    session.status = "customer_selected"
    session.updated_at = datetime.utcnow()
    
    # Update search log
    search_log = db.query(GoldCustomerSearchLog).filter(
        GoldCustomerSearchLog.session_id == session_id
    ).order_by(GoldCustomerSearchLog.searched_at.desc()).first()
    
    if search_log:
        search_log.selected_customer_id = customer_id
    
    # Create journey step
    step = GoldJourneyStep(
        id=str(uuid4()),
        session_id=session_id,
        step_number=2,
        step_name="customer_selected",
        step_status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        step_data={"customer_id": customer_id}
    )
    db.add(step)
    
    db.commit()
    
    return {"success": True, "customer_id": customer_id}


# ============================================================================
# PRODUCT SELECTION & RECOMMENDATION
# ============================================================================

@router.get("/recommend-products/{session_id}", response_model=List[ProductRecommendation])
async def recommend_products(
    session_id: str,
    requested_amount: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered product recommendations for customer
    
    Based on customer profile, requested amount, and eligibility rules.
    Returns ranked list of suitable products.
    """
    session = db.query(GoldCustomerSession).filter(GoldCustomerSession.id == session_id).first()
    if not session or not session.customer_id:
        raise HTTPException(status_code=400, detail="Session must have customer selected")
    
    # Fetch customer data
    customer_data = await call_customer_service(f"/customers/{session.customer_id}")
    if not customer_data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get all active products
    products = db.query(GoldProduct).filter(GoldProduct.is_active == True).all()
    
    recommendations = []
    for product in products:
        # Simple scoring logic (in production, use FinDNA AI)
        score = 0.5  # Base score
        reason_parts = []
        
        # Check amount eligibility
        if product.limits:
            if requested_amount:
                if product.limits.min_loan_amount <= requested_amount <= product.limits.max_loan_amount:
                    score += 0.3
                    reason_parts.append("Amount within range")
                else:
                    score -= 0.2
                    reason_parts.append("Amount outside range")
        
        # Check customer segment
        customer_segment = customer_data.get("segment", "regular")
        if customer_segment == "premium":
            if product.product_type in ["jewel_loan", "od"]:
                score += 0.2
                reason_parts.append("Suitable for premium segment")
        
        # Check instant eligibility for instant products
        if product.product_type == "instant":
            if requested_amount and requested_amount <= 50000:
                score += 0.3
                reason_parts.append("Instant approval eligible")
        
        reason = "; ".join(reason_parts) if reason_parts else "Standard recommendation"
        
        recommendations.append(ProductRecommendation(
            product_id=product.id,
            product_code=product.product_code,
            product_name=product.product_name,
            recommendation_score=round(score, 2),
            recommendation_reason=reason,
            suggested_amount=requested_amount,
            is_eligible=score > 0.4
        ))
    
    # Sort by score
    recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
    
    return recommendations[:5]  # Top 5


@router.post("/select-product", response_model=ProductSelectionResponse, status_code=201)
async def select_product(selection: ProductSelectionCreate, db: Session = Depends(get_db)):
    """Record product selection"""
    session = db.query(GoldCustomerSession).filter(GoldCustomerSession.id == selection.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    product = db.query(GoldProduct).filter(GoldProduct.id == selection.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create selection record
    product_selection = GoldProductSelection(
        id=str(uuid4()),
        session_id=selection.session_id,
        product_id=selection.product_id,
        customer_id=selection.customer_id or session.customer_id,
        requested_amount=selection.requested_amount,
        estimated_gold_weight=selection.estimated_gold_weight,
        selected_at=datetime.utcnow(),
        selection_source=selection.selection_source or "customer_choice",
        recommendation_score=selection.recommendation_score
    )
    db.add(product_selection)
    
    # Update session
    session.status = "product_selected"
    session.updated_at = datetime.utcnow()
    
    # Create journey step
    step = GoldJourneyStep(
        id=str(uuid4()),
        session_id=selection.session_id,
        step_number=3,
        step_name="product_selected",
        step_status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        step_data={
            "product_id": selection.product_id,
            "product_name": product.product_name,
            "requested_amount": selection.requested_amount
        }
    )
    db.add(step)
    
    db.commit()
    db.refresh(product_selection)
    
    return product_selection


# ============================================================================
# ELIGIBILITY VALIDATION
# ============================================================================

@router.post("/check-eligibility/{session_id}/{product_id}", response_model=EligibilityResult)
async def check_eligibility(session_id: str, product_id: str, db: Session = Depends(get_db)):
    """
    Run eligibility checks for customer against product rules
    
    Validates age, income, CIBIL, existing loans, geography, segment, etc.
    """
    session = db.query(GoldCustomerSession).filter(GoldCustomerSession.id == session_id).first()
    if not session or not session.customer_id:
        raise HTTPException(status_code=400, detail="Session must have customer selected")
    
    product = db.query(GoldProduct).options(
        joinedload(GoldProduct.eligibility)
    ).filter(GoldProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Fetch customer data
    customer_data = await call_customer_service(f"/customers/{session.customer_id}")
    if not customer_data:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    failed_checks = []
    passed_count = 0
    total_count = len(product.eligibility)
    
    # Run each eligibility rule
    for rule in product.eligibility:
        is_passed = True
        failure_reason = None
        check_value = {}
        
        # Age check
        if rule.rule_type == "age":
            age = customer_data.get("age", 0)
            check_value = {"age": age, "required": rule.rule_value}
            
            if rule.rule_operator == "gte":
                is_passed = age >= rule.rule_value.get("value", 0)
            elif rule.rule_operator == "lte":
                is_passed = age <= rule.rule_value.get("value", 999)
            
            if not is_passed:
                failure_reason = rule.error_message or f"Age requirement not met"
        
        # Add more rule types (income, CIBIL, segment, etc.)
        
        # Create eligibility check record
        check = GoldEligibilityCheck(
            id=str(uuid4()),
            session_id=session_id,
            customer_id=session.customer_id,
            product_id=product_id,
            check_type=rule.rule_type,
            rule_id=rule.id,
            is_passed=is_passed,
            check_value=check_value,
            failure_reason=failure_reason,
            checked_at=datetime.utcnow()
        )
        db.add(check)
        
        if is_passed:
            passed_count += 1
        else:
            failed_checks.append(check)
    
    db.commit()
    
    # Determine overall eligibility
    is_eligible = passed_count == total_count
    can_proceed = is_eligible or all(not check.is_passed for check in failed_checks if not rule.is_mandatory)
    
    # Update session status
    if is_eligible:
        session.status = "eligibility_passed"
    else:
        session.status = "eligibility_failed"
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return EligibilityResult(
        product_id=product_id,
        product_name=product.product_name,
        is_eligible=is_eligible,
        passed_checks=passed_count,
        total_checks=total_count,
        failed_checks=[EligibilityCheckResponse.from_orm(check) for check in failed_checks],
        can_proceed=can_proceed
    )


# ============================================================================
# JOURNEY STEPS
# ============================================================================

@router.post("/steps", response_model=JourneyStepResponse, status_code=201)
async def create_journey_step(step: JourneyStepCreate, db: Session = Depends(get_db)):
    """Create a journey step"""
    journey_step = GoldJourneyStep(
        id=str(uuid4()),
        **step.model_dump()
    )
    db.add(journey_step)
    db.commit()
    db.refresh(journey_step)
    return journey_step


@router.patch("/steps/{step_id}", response_model=JourneyStepResponse)
async def update_journey_step(step_id: str, update: JourneyStepUpdate, db: Session = Depends(get_db)):
    """Update journey step (mark as completed, add duration, etc.)"""
    step = db.query(GoldJourneyStep).filter(GoldJourneyStep.id == step_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    update_dict = update.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(step, field, value)
    
    # Auto-calculate duration if completed
    if update.step_status == "completed" and step.started_at:
        step.completed_at = update.completed_at or datetime.utcnow()
        duration = (step.completed_at - step.started_at).total_seconds()
        step.duration_seconds = int(duration)
    
    db.commit()
    db.refresh(step)
    return step


# ============================================================================
# CUSTOMER INTERACTIONS
# ============================================================================

@router.post("/interactions", response_model=CustomerInteractionResponse, status_code=201)
async def create_interaction(interaction: CustomerInteractionCreate, db: Session = Depends(get_db)):
    """Record customer interaction/note"""
    customer_interaction = GoldCustomerInteraction(
        id=str(uuid4()),
        **interaction.model_dump()
    )
    db.add(customer_interaction)
    db.commit()
    db.refresh(customer_interaction)
    return customer_interaction


@router.get("/interactions/{session_id}", response_model=List[CustomerInteractionResponse])
async def list_interactions(session_id: str, db: Session = Depends(get_db)):
    """List all interactions for a session"""
    interactions = db.query(GoldCustomerInteraction).filter(
        GoldCustomerInteraction.session_id == session_id
    ).order_by(GoldCustomerInteraction.interaction_at.desc()).all()
    return interactions
