"""
Loan Origination & Disbursement Router
Phase 6: Complete loan lifecycle API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

from app.database import get_db
from app.models.loan import (
    LoanApplication, ApplicationOrnament, CreditEvaluation,
    LoanApproval, LoanAccount, Disbursement, LoanDocument,
    LoanCharge, LoanStatusHistory, LMSIntegrationLog
)
from app.schemas.loan import (
    LoanApplicationCreate, LoanApplicationUpdate, LoanApplicationSubmit, LoanApplicationResponse,
    ApplicationOrnamentResponse,
    CreditEvaluationCreate, CreditEvaluationResponse,
    LoanApprovalCreate, LoanApprovalDecision, LoanApprovalResponse,
    LoanAccountCreate, LoanAccountResponse,
    DisbursementCreate, DisbursementVerify, DisbursementResponse,
    LoanDocumentCreate, LoanDocumentResponse,
    LoanChargeCreate, LoanChargeResponse,
    LoanStatusHistoryCreate, LoanStatusHistoryResponse,
    ApplicationSummary, LoanPortfolioSummary,
    LMSIntegrationCreate, LMSIntegrationResponse
)

router = APIRouter(prefix="/api/v1/gold", tags=["Loan Origination & Disbursement"])


# ============================================================================
# LOAN APPLICATIONS
# ============================================================================

@router.post("/applications", response_model=LoanApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_loan_application(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create new loan application"""
    
    # Generate application number
    app_number = f"APP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create application
    db_application = LoanApplication(
        application_number=app_number,
        **application.dict(exclude={'ornament_ids'})
    )
    
    db.add(db_application)
    db.flush()
    
    # Link ornaments
    for ornament_id in application.ornament_ids:
        # In real implementation, fetch ornament details from gold_ornaments table
        app_ornament = ApplicationOrnament(
            application_id=db_application.id,
            ornament_id=ornament_id,
            ornament_type="Gold",  # Fetch from ornament
            gross_weight=Decimal(0),  # Fetch from ornament
            net_weight=Decimal(0),  # Fetch from ornament
            purity=Decimal(0),  # Fetch from ornament
            valuation_amount=Decimal(0)  # Fetch from ornament
        )
        db.add(app_ornament)
    
    # Create status history
    status_history = LoanStatusHistory(
        application_id=db_application.id,
        to_status='draft',
        stage='application',
        changed_by=application.customer_id,
        reason='Application created'
    )
    db.add(status_history)
    
    db.commit()
    db.refresh(db_application)
    
    return db_application


@router.get("/applications", response_model=List[LoanApplicationResponse])
def list_loan_applications(
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """List loan applications with filters"""
    
    query = db.query(LoanApplication)
    
    if status:
        query = query.filter(LoanApplication.status == status)
    if stage:
        query = query.filter(LoanApplication.stage == stage)
    if branch_id:
        query = query.filter(LoanApplication.branch_id == branch_id)
    if customer_id:
        query = query.filter(LoanApplication.customer_id == customer_id)
    if from_date:
        query = query.filter(LoanApplication.created_at >= from_date)
    if to_date:
        query = query.filter(LoanApplication.created_at <= to_date)
    
    applications = query.order_by(LoanApplication.created_at.desc()).offset(skip).limit(limit).all()
    return applications


@router.get("/applications/{application_id}", response_model=LoanApplicationResponse)
def get_loan_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get loan application details"""
    
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application


@router.put("/applications/{application_id}", response_model=LoanApplicationResponse)
def update_loan_application(
    application_id: str,
    application_update: LoanApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update loan application"""
    
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Track status changes
    old_status = application.status
    
    for key, value in application_update.dict(exclude_unset=True).items():
        setattr(application, key, value)
    
    application.updated_at = datetime.now()
    
    # Add status history if status changed
    if application_update.status and application_update.status != old_status:
        status_history = LoanStatusHistory(
            application_id=application.id,
            from_status=old_status,
            to_status=application_update.status,
            changed_at=datetime.now(),
            reason='Status updated'
        )
        db.add(status_history)
    
    db.commit()
    db.refresh(application)
    
    return application


@router.post("/applications/{application_id}/submit", response_model=LoanApplicationResponse)
def submit_loan_application(
    application_id: str,
    submission: LoanApplicationSubmit,
    db: Session = Depends(get_db)
):
    """Submit loan application for processing"""
    
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != 'draft':
        raise HTTPException(status_code=400, detail="Only draft applications can be submitted")
    
    application.status = 'submitted'
    application.stage = 'credit_check'
    application.submitted_at = datetime.now()
    application.submitted_by = submission.submitted_by
    
    # Add status history
    status_history = LoanStatusHistory(
        application_id=application.id,
        from_status='draft',
        to_status='submitted',
        stage='credit_check',
        changed_by=submission.submitted_by,
        changed_at=datetime.now(),
        reason='Application submitted for processing'
    )
    db.add(status_history)
    
    db.commit()
    db.refresh(application)
    
    return application


@router.get("/applications/{application_id}/ornaments", response_model=List[ApplicationOrnamentResponse])
def get_application_ornaments(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get ornaments linked to application"""
    
    ornaments = db.query(ApplicationOrnament).filter(
        ApplicationOrnament.application_id == application_id
    ).all()
    
    return ornaments


@router.delete("/applications/{application_id}")
def delete_loan_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Delete loan application (only draft status)"""
    
    application = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != 'draft':
        raise HTTPException(status_code=400, detail="Only draft applications can be deleted")
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}


# ============================================================================
# CREDIT EVALUATION
# ============================================================================

@router.post("/credit-evaluations", response_model=CreditEvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_credit_evaluation(
    evaluation: CreditEvaluationCreate,
    db: Session = Depends(get_db)
):
    """Create credit evaluation for application"""
    
    # Check if evaluation already exists
    existing = db.query(CreditEvaluation).filter(
        CreditEvaluation.application_id == evaluation.application_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Credit evaluation already exists for this application")
    
    db_evaluation = CreditEvaluation(**evaluation.dict())
    db_evaluation.evaluation_status = 'completed'
    db_evaluation.evaluated_at = datetime.now()
    
    db.add(db_evaluation)
    
    # Update application stage
    application = db.query(LoanApplication).filter(
        LoanApplication.id == evaluation.application_id
    ).first()
    if application:
        application.stage = 'approval'
    
    db.commit()
    db.refresh(db_evaluation)
    
    return db_evaluation


@router.get("/credit-evaluations/{evaluation_id}", response_model=CreditEvaluationResponse)
def get_credit_evaluation(
    evaluation_id: str,
    db: Session = Depends(get_db)
):
    """Get credit evaluation details"""
    
    evaluation = db.query(CreditEvaluation).filter(CreditEvaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Credit evaluation not found")
    
    return evaluation


@router.get("/applications/{application_id}/credit-evaluation", response_model=CreditEvaluationResponse)
def get_application_credit_evaluation(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get credit evaluation for application"""
    
    evaluation = db.query(CreditEvaluation).filter(
        CreditEvaluation.application_id == application_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Credit evaluation not found for this application")
    
    return evaluation


# ============================================================================
# APPROVAL WORKFLOW
# ============================================================================

@router.post("/approvals", response_model=LoanApprovalResponse, status_code=status.HTTP_201_CREATED)
def create_loan_approval(
    approval: LoanApprovalCreate,
    db: Session = Depends(get_db)
):
    """Create approval level for application"""
    
    db_approval = LoanApproval(**approval.dict())
    
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    
    return db_approval


@router.post("/approvals/{approval_id}/decision", response_model=LoanApprovalResponse)
def submit_approval_decision(
    approval_id: str,
    decision: LoanApprovalDecision,
    db: Session = Depends(get_db)
):
    """Submit approval decision"""
    
    approval = db.query(LoanApproval).filter(LoanApproval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval.status != 'pending':
        raise HTTPException(status_code=400, detail="Approval already processed")
    
    # Update approval
    for key, value in decision.dict(exclude_unset=True).items():
        setattr(approval, key, value)
    
    approval.status = 'approved' if decision.decision == 'approve' else 'rejected'
    approval.responded_at = datetime.now()
    
    # Update application status if final approval
    if approval.is_final_approval:
        application = db.query(LoanApplication).filter(
            LoanApplication.id == approval.application_id
        ).first()
        if application:
            if decision.decision == 'approve':
                application.status = 'approved'
                application.stage = 'disbursement'
            elif decision.decision == 'reject':
                application.status = 'rejected'
            
            # Add status history
            status_history = LoanStatusHistory(
                application_id=application.id,
                from_status='under_review',
                to_status=application.status,
                stage=application.stage,
                changed_at=datetime.now(),
                reason=f'Final approval: {decision.decision}'
            )
            db.add(status_history)
    
    db.commit()
    db.refresh(approval)
    
    return approval


@router.get("/applications/{application_id}/approvals", response_model=List[LoanApprovalResponse])
def get_application_approvals(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get all approval levels for application"""
    
    approvals = db.query(LoanApproval).filter(
        LoanApproval.application_id == application_id
    ).order_by(LoanApproval.sequence_order).all()
    
    return approvals


# ============================================================================
# LOAN ACCOUNTS
# ============================================================================

@router.post("/loan-accounts", response_model=LoanAccountResponse, status_code=status.HTTP_201_CREATED)
def create_loan_account(
    loan_account: LoanAccountCreate,
    db: Session = Depends(get_db)
):
    """Create loan account after approval"""
    
    # Check if application is approved
    application = db.query(LoanApplication).filter(
        LoanApplication.id == loan_account.application_id
    ).first()
    
    if not application or application.status != 'approved':
        raise HTTPException(status_code=400, detail="Application must be approved first")
    
    # Check if loan account already exists
    existing = db.query(LoanAccount).filter(
        LoanAccount.application_id == loan_account.application_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Loan account already exists for this application")
    
    # Generate loan account number
    loan_number = f"GL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate total charges
    total_charges = (
        loan_account.processing_fee +
        loan_account.documentation_charges +
        loan_account.valuation_charges +
        loan_account.other_charges
    )
    
    # Create loan account
    db_loan = LoanAccount(
        loan_account_number=loan_number,
        **loan_account.dict(),
        total_charges=total_charges,
        outstanding_principal=loan_account.principal_amount,
        total_outstanding=loan_account.principal_amount + total_charges
    )
    
    db.add(db_loan)
    
    # Update application stage
    application.stage = 'disbursement'
    
    db.commit()
    db.refresh(db_loan)
    
    return db_loan


@router.get("/loan-accounts", response_model=List[LoanAccountResponse])
def list_loan_accounts(
    status: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    is_npa: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """List loan accounts with filters"""
    
    query = db.query(LoanAccount)
    
    if status:
        query = query.filter(LoanAccount.status == status)
    if customer_id:
        query = query.filter(LoanAccount.customer_id == customer_id)
    if branch_id:
        query = query.filter(LoanAccount.branch_id == branch_id)
    if is_npa is not None:
        query = query.filter(LoanAccount.is_npa == is_npa)
    
    loans = query.order_by(LoanAccount.created_at.desc()).offset(skip).limit(limit).all()
    return loans


@router.get("/loan-accounts/{loan_id}", response_model=LoanAccountResponse)
def get_loan_account(
    loan_id: str,
    db: Session = Depends(get_db)
):
    """Get loan account details"""
    
    loan = db.query(LoanAccount).filter(LoanAccount.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan account not found")
    
    return loan


# ============================================================================
# DISBURSEMENTS
# ============================================================================

@router.post("/disbursements", response_model=DisbursementResponse, status_code=status.HTTP_201_CREATED)
def create_disbursement(
    disbursement: DisbursementCreate,
    db: Session = Depends(get_db)
):
    """Create disbursement request"""
    
    # Generate disbursement number
    disb_number = f"DISB-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    db_disbursement = Disbursement(
        disbursement_number=disb_number,
        **disbursement.dict()
    )
    
    db.add(db_disbursement)
    
    # Update loan account disbursement status if provided
    if disbursement.loan_account_id:
        loan = db.query(LoanAccount).filter(
            LoanAccount.id == disbursement.loan_account_id
        ).first()
        if loan:
            loan.disbursement_status = 'processing'
    
    db.commit()
    db.refresh(db_disbursement)
    
    return db_disbursement


@router.post("/disbursements/{disbursement_id}/verify", response_model=DisbursementResponse)
def verify_disbursement(
    disbursement_id: str,
    verification: DisbursementVerify,
    db: Session = Depends(get_db)
):
    """Verify and complete disbursement"""
    
    disbursement = db.query(Disbursement).filter(Disbursement.id == disbursement_id).first()
    if not disbursement:
        raise HTTPException(status_code=404, detail="Disbursement not found")
    
    disbursement.status = 'completed'
    disbursement.verified_by = verification.verified_by
    disbursement.verified_at = datetime.now()
    disbursement.verification_notes = verification.verification_notes
    disbursement.utr_number = verification.utr_number
    disbursement.transaction_id = verification.transaction_id
    disbursement.bank_reference = verification.bank_reference
    
    # Update loan account
    if disbursement.loan_account_id:
        loan = db.query(LoanAccount).filter(
            LoanAccount.id == disbursement.loan_account_id
        ).first()
        if loan:
            loan.disbursement_status = 'completed'
    
    db.commit()
    db.refresh(disbursement)
    
    return disbursement


@router.get("/disbursements/{disbursement_id}", response_model=DisbursementResponse)
def get_disbursement(
    disbursement_id: str,
    db: Session = Depends(get_db)
):
    """Get disbursement details"""
    
    disbursement = db.query(Disbursement).filter(Disbursement.id == disbursement_id).first()
    if not disbursement:
        raise HTTPException(status_code=404, detail="Disbursement not found")
    
    return disbursement


@router.get("/applications/{application_id}/disbursements", response_model=List[DisbursementResponse])
def get_application_disbursements(
    application_id: str,
    db: Session = Depends(get_db)
):
    """Get all disbursements for application"""
    
    disbursements = db.query(Disbursement).filter(
        Disbursement.application_id == application_id
    ).order_by(Disbursement.created_at.desc()).all()
    
    return disbursements


# ============================================================================
# SUMMARY & STATS
# ============================================================================

@router.get("/applications/summary", response_model=ApplicationSummary)
def get_applications_summary(
    branch_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get applications summary statistics"""
    
    query = db.query(LoanApplication)
    
    if branch_id:
        query = query.filter(LoanApplication.branch_id == branch_id)
    if from_date:
        query = query.filter(LoanApplication.created_at >= from_date)
    if to_date:
        query = query.filter(LoanApplication.created_at <= to_date)
    
    total = query.count()
    draft = query.filter(LoanApplication.status == 'draft').count()
    submitted = query.filter(LoanApplication.status == 'submitted').count()
    under_review = query.filter(LoanApplication.status == 'under_review').count()
    approved = query.filter(LoanApplication.status == 'approved').count()
    rejected = query.filter(LoanApplication.status == 'rejected').count()
    
    total_amount = db.query(func.sum(LoanApplication.loan_amount)).filter(
        LoanApplication.status.in_(['submitted', 'under_review', 'approved'])
    ).scalar() or Decimal(0)
    
    avg_ltv = db.query(func.avg(LoanApplication.ltv_percentage)).filter(
        LoanApplication.status.in_(['submitted', 'under_review', 'approved'])
    ).scalar() or Decimal(0)
    
    return ApplicationSummary(
        total_applications=total,
        draft=draft,
        submitted=submitted,
        under_review=under_review,
        approved=approved,
        rejected=rejected,
        total_amount=total_amount,
        avg_ltv=avg_ltv
    )


@router.get("/loan-accounts/portfolio", response_model=LoanPortfolioSummary)
def get_loan_portfolio(
    branch_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get loan portfolio summary"""
    
    query = db.query(LoanAccount)
    
    if branch_id:
        query = query.filter(LoanAccount.branch_id == branch_id)
    
    total = query.count()
    active = query.filter(LoanAccount.status == 'active').count()
    
    total_principal = db.query(func.sum(LoanAccount.principal_amount)).filter(
        LoanAccount.status == 'active'
    ).scalar() or Decimal(0)
    
    total_outstanding = db.query(func.sum(LoanAccount.total_outstanding)).filter(
        LoanAccount.status == 'active'
    ).scalar() or Decimal(0)
    
    npa_count = query.filter(LoanAccount.is_npa == True).count()
    npa_amount = db.query(func.sum(LoanAccount.total_outstanding)).filter(
        and_(LoanAccount.status == 'active', LoanAccount.is_npa == True)
    ).scalar() or Decimal(0)
    
    collection_efficiency = Decimal(100) - (npa_amount / total_outstanding * 100) if total_outstanding > 0 else Decimal(100)
    
    return LoanPortfolioSummary(
        total_loans=total,
        active_loans=active,
        total_principal=total_principal,
        total_outstanding=total_outstanding,
        npa_count=npa_count,
        npa_amount=npa_amount,
        collection_efficiency=collection_efficiency
    )
