"""
Interest Certificate Router

API endpoints for interest certificate generation including:
- Annual interest certificate
- TDS certificate (Form 16A)
- Interest summary
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .certificate_service import CertificateService
from .schemas import InterestCertificateRequest, InterestCertificateResponse, SuccessResponse

router = APIRouter(prefix="/certificate", tags=["Deposit Certificates"])


@router.post("/interest", response_model=InterestCertificateResponse)
def generate_interest_certificate(
    request: InterestCertificateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate interest certificate for financial year
    
    Returns detailed interest calculation breakdown for tax purposes.
    """
    service = CertificateService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    certificate = service.generate_interest_certificate(
        account_id=request.account_id,
        financial_year=request.financial_year
    )
    
    return certificate


@router.get("/{account_id}/interest/pdf")
def generate_interest_certificate_pdf(
    account_id: int,
    financial_year: Optional[str] = Query(None, description="FY in format YYYY-YYYY"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate interest certificate PDF
    
    Creates a printable interest certificate.
    """
    service = CertificateService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    pdf_result = service.generate_interest_certificate_pdf(
        account_id=account_id,
        financial_year=financial_year
    )
    
    from fastapi.responses import Response
    
    return Response(
        content=pdf_result['pdf_content'],
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={pdf_result['filename']}"
        }
    )


@router.get("/{account_id}/tds-certificate")
def generate_tds_certificate(
    account_id: int,
    financial_year: str = Query(..., description="FY in format YYYY-YYYY"),
    quarter: Optional[int] = Query(None, ge=1, le=4, description="Quarter (1-4)"),
    format: str = Query("pdf", description="Format: pdf, json"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate TDS certificate (Form 16A)
    
    Certificate for tax deducted at source on interest income.
    """
    service = CertificateService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    if format == "pdf":
        pdf_result = service.generate_tds_certificate_pdf(
            account_id=account_id,
            financial_year=financial_year,
            quarter=quarter
        )
        
        from fastapi.responses import Response
        return Response(
            content=pdf_result['pdf_content'],
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={pdf_result['filename']}"}
        )
    else:
        certificate = service.generate_tds_certificate(
            account_id=account_id,
            financial_year=financial_year,
            quarter=quarter
        )
        return certificate


@router.post("/{account_id}/issue-certificate", response_model=SuccessResponse)
def mark_certificate_issued(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark certificate as issued
    
    Updates account flag to track certificate issuance.
    """
    service = CertificateService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.mark_certificate_issued(account_id)
    
    return SuccessResponse(
        success=True,
        message="Certificate marked as issued",
        data=result
    )


@router.get("/{account_id}/interest-summary")
def get_interest_summary(
    account_id: int,
    financial_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get interest summary
    
    Returns summarized interest information for the account.
    """
    service = CertificateService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    summary = service.get_interest_summary(
        account_id=account_id,
        financial_year=financial_year
    )
    
    return {
        "success": True,
        "data": summary
    }
