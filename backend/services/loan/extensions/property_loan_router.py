"""
Property Loan Router
API endpoints for property/mortgage loan extension (LAP/Home Loan)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.loan.extensions.property_loan_service import PropertyLoanService
from backend.services.loan.extensions import property_schemas as schemas


router = APIRouter(prefix="/property-loans", tags=["Property Loans"])


# ============================================
# Property Details Endpoints
# ============================================

@router.post("/details", response_model=dict)
async def create_property_details(
    data: schemas.PropertyDetailsCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create property details for loan application"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        property_data = data.model_dump(exclude={"loan_application_id"})
        property_loan = service.create_property_details(
            loan_application_id=data.loan_application_id,
            property_data=property_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.PropertyDetailsResponse.model_validate(property_loan),
            message="Property details created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/details/{loan_application_id}", response_model=dict)
async def get_property_details(
    loan_application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get property details by loan application ID"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        property_loan = service.get_property_details(loan_application_id)
        
        if not property_loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property details not found")
        
        return success_response(
            data=schemas.PropertyDetailsResponse.model_validate(property_loan)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/details/{property_id}", response_model=dict)
async def update_property_details(
    property_id: int,
    data: schemas.PropertyDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update property details"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        property_data = data.model_dump(exclude_unset=True)
        property_loan = service.update_property_details(
            property_id=property_id,
            property_data=property_data,
            user_id=current_user["user_id"]
        )
        
        if not property_loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
        
        return success_response(
            data=schemas.PropertyDetailsResponse.model_validate(property_loan),
            message="Property details updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Legal Verification Endpoints
# ============================================

@router.post("/legal-verification", response_model=dict)
async def create_legal_verification(
    data: schemas.LegalVerificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initialize legal verification for property"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        legal_data = data.model_dump(exclude={"property_loan_id", "loan_application_id"})
        legal_verification = service.create_legal_verification(
            property_loan_id=data.property_loan_id,
            loan_application_id=data.loan_application_id,
            legal_data=legal_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.LegalVerificationResponse.model_validate(legal_verification),
            message="Legal verification initiated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/legal-verification/{legal_id}", response_model=dict)
async def update_legal_verification(
    legal_id: int,
    data: schemas.LegalVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update legal verification details"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude_unset=True)
        legal_verification = service.update_legal_verification(
            legal_id=legal_id,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not legal_verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal verification not found")
        
        return success_response(
            data=schemas.LegalVerificationResponse.model_validate(legal_verification),
            message="Legal verification updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/legal-verification/pending", response_model=dict)
async def get_pending_legal_verifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all pending legal verification cases"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        pending = service.get_pending_legal_verifications()
        
        return success_response(
            data=[schemas.LegalVerificationResponse.model_validate(l) for l in pending]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Technical Verification Endpoints
# ============================================

@router.post("/technical-verification", response_model=dict)
async def create_technical_verification(
    data: schemas.TechnicalVerificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initialize technical verification for property"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        technical_data = data.model_dump(exclude={"property_loan_id", "loan_application_id"})
        technical_verification = service.create_technical_verification(
            property_loan_id=data.property_loan_id,
            loan_application_id=data.loan_application_id,
            technical_data=technical_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.TechnicalVerificationResponse.model_validate(technical_verification),
            message="Technical verification initiated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/technical-verification/{technical_id}/schedule-visit", response_model=dict)
async def schedule_site_visit(
    technical_id: int,
    data: schemas.SiteVisitSchedule,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Schedule site visit for technical verification"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        technical_verification = service.schedule_site_visit(
            technical_id=technical_id,
            inspection_date=data.inspection_date,
            engineer_name=data.engineer_name,
            user_id=current_user["user_id"]
        )
        
        if not technical_verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technical verification not found")
        
        return success_response(
            data=schemas.TechnicalVerificationResponse.model_validate(technical_verification),
            message="Site visit scheduled successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/technical-verification/{technical_id}", response_model=dict)
async def update_technical_verification(
    technical_id: int,
    data: schemas.TechnicalVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update technical verification details"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude_unset=True)
        technical_verification = service.update_technical_verification(
            technical_id=technical_id,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not technical_verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technical verification not found")
        
        return success_response(
            data=schemas.TechnicalVerificationResponse.model_validate(technical_verification),
            message="Technical verification updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/technical-verification/pending", response_model=dict)
async def get_pending_technical_verifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all pending technical verification cases"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        pending = service.get_pending_technical_verifications()
        
        return success_response(
            data=[schemas.TechnicalVerificationResponse.model_validate(t) for t in pending]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Document Management Endpoints
# ============================================

@router.post("/documents", response_model=dict)
async def upload_property_document(
    data: schemas.PropertyDocumentUpload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload property document"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        document_data = data.model_dump(exclude={"property_loan_id", "loan_application_id"})
        document = service.upload_property_document(
            property_loan_id=data.property_loan_id,
            loan_application_id=data.loan_application_id,
            document_data=document_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.PropertyDocumentResponse.model_validate(document),
            message="Document uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/documents/{document_id}/verify", response_model=dict)
async def verify_document(
    document_id: int,
    data: schemas.DocumentVerification,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Verify property document"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        document = service.verify_document(
            document_id=document_id,
            verified=data.is_verified,
            remarks=data.verification_remarks,
            user_id=current_user["user_id"]
        )
        
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        return success_response(
            data=schemas.PropertyDocumentResponse.model_validate(document),
            message="Document verification updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/documents/{property_loan_id}", response_model=dict)
async def get_property_documents(
    property_loan_id: int,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get property documents"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        documents = service.get_property_documents(property_loan_id, document_type)
        
        return success_response(
            data=[schemas.PropertyDocumentResponse.model_validate(d) for d in documents]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/documents/{property_loan_id}/compliance", response_model=dict)
async def check_document_compliance(
    property_loan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check if all mandatory documents are uploaded and verified"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        compliance = service.check_mandatory_documents(property_loan_id)
        
        return success_response(
            data=schemas.DocumentComplianceStatus(**compliance)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Mortgage Management Endpoints
# ============================================

@router.post("/mortgage", response_model=dict)
async def create_mortgage(
    data: schemas.MortgageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create mortgage entry for property"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        mortgage_data = data.model_dump(exclude={"property_loan_id", "loan_application_id"})
        mortgage = service.create_mortgage(
            property_loan_id=data.property_loan_id,
            loan_application_id=data.loan_application_id,
            mortgage_data=mortgage_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.MortgageResponse.model_validate(mortgage),
            message="Mortgage created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/mortgage/{mortgage_id}/status", response_model=dict)
async def update_mortgage_status(
    mortgage_id: int,
    data: schemas.MortgageStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update mortgage status"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude={"mortgage_status"}, exclude_unset=True)
        mortgage = service.update_mortgage_status(
            mortgage_id=mortgage_id,
            status=data.mortgage_status,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not mortgage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mortgage not found")
        
        return success_response(
            data=schemas.MortgageResponse.model_validate(mortgage),
            message="Mortgage status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/mortgage/{mortgage_id}/discharge", response_model=dict)
async def initiate_mortgage_discharge(
    mortgage_id: int,
    data: schemas.MortgageDischarge,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initiate mortgage discharge process"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        
        mortgage = service.initiate_discharge(
            mortgage_id=mortgage_id,
            loan_closed_date=data.loan_closed_date,
            user_id=current_user["user_id"]
        )
        
        if not mortgage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mortgage not found")
        
        return success_response(
            data=schemas.MortgageResponse.model_validate(mortgage),
            message="Mortgage discharge initiated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mortgage/pending", response_model=dict)
async def get_pending_mortgages(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get pending mortgage registrations"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        pending = service.get_pending_mortgages()
        
        return success_response(
            data=[schemas.MortgageResponse.model_validate(m) for m in pending]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mortgage/discharge-pending", response_model=dict)
async def get_discharge_pending_cases(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cases where loan is closed but discharge pending"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        cases = service.get_discharge_pending_cases()
        
        return success_response(
            data=[schemas.MortgageResponse.model_validate(m) for m in cases]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Summary & Analytics Endpoints
# ============================================

@router.get("/summary/{loan_application_id}", response_model=dict)
async def get_property_loan_summary(
    loan_application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get complete property loan summary"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        summary = service.get_property_loan_summary(loan_application_id)
        
        if not summary:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property loan not found")
        
        # Convert to response schema
        result = schemas.PropertyLoanSummary(
            property_details=schemas.PropertyDetailsResponse.model_validate(summary["property_details"]),
            legal_verification=schemas.LegalVerificationResponse.model_validate(summary["legal_verification"]) if summary.get("legal_verification") else None,
            technical_verification=schemas.TechnicalVerificationResponse.model_validate(summary["technical_verification"]) if summary.get("technical_verification") else None,
            mortgage=schemas.MortgageResponse.model_validate(summary["mortgage"]) if summary.get("mortgage") else None,
            document_compliance=schemas.DocumentComplianceStatus(**summary["document_compliance"]),
            verification_status=schemas.VerificationStatus(**summary["verification_status"]),
            is_ready_for_disbursement=schemas.DisbursementReadiness(**summary["is_ready_for_disbursement"])
        )
        
        return success_response(data=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics", response_model=dict)
async def get_property_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get property loan statistics"""
    try:
        service = PropertyLoanService(db, current_user["tenant_id"])
        stats = service.get_property_statistics()
        
        return success_response(
            data=schemas.PropertyStatistics(**stats)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
