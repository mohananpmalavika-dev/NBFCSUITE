"""
Loan Application Router
API endpoints for loan application management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from shared.database.base import get_db
from .application_service import LoanApplicationService
from .schemas import (
    LoanApplicationCreate, LoanApplicationUpdate, LoanApplicationResponse,
    LoanApplicationListResponse, LoanApplicationStats
)

router = APIRouter(prefix="/applications", tags=["Loan Applications"])


def get_application_service(db: Session = Depends(get_db)) -> LoanApplicationService:
    """Dependency to get application service"""
    # TODO: Get tenant_id from authenticated user context
    tenant_id = 1  # Hardcoded for now
    return LoanApplicationService(db, tenant_id)


@router.post("", response_model=LoanApplicationResponse, status_code=201)
async def create_application(
    data: LoanApplicationCreate,
    service: LoanApplicationService = Depends(get_application_service)
):
    """
    Create new loan application
    
    - **customer_id**: Customer applying for loan
    - **loan_product_id**: Loan product selected
    - **requested_amount**: Loan amount requested
    - **tenure_months**: Loan tenure in months
    - **loan_purpose_id**: Purpose of loan (optional)
    - **disbursement_bank_account_id**: Bank account for disbursement
    - **co_applicants**: List of co-applicants/guarantors (optional)
    - **documents**: List of documents (optional)
    
    Automatically calculates:
    - EMI amount
    - Total interest
    - Processing fees
    - Net disbursement amount
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        application = service.create_application(data, user_id)
        return LoanApplicationResponse.model_validate(application)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create application: {str(e)}")


@router.get("/stats", response_model=LoanApplicationStats)
async def get_application_stats(
    service: LoanApplicationService = Depends(get_application_service)
):
    """
    Get loan application statistics
    
    Returns counts by status and amount aggregations
    """
    try:
        return service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


@router.get("", response_model=LoanApplicationListResponse)
async def list_applications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    product_id: Optional[int] = Query(None, description="Filter by product"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in application number, customer name, mobile"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    service: LoanApplicationService = Depends(get_application_service)
):
    """
    List all loan applications with pagination and filters
    
    Filters available:
    - **customer_id**: Applications for specific customer
    - **product_id**: Applications for specific product
    - **status**: draft, submitted, under_review, credit_assessment, 
                  pending_approval, approved, rejected, disbursed, cancelled
    - **search**: Search in application number, customer name, code, mobile
    - **from_date**: Applications from date
    - **to_date**: Applications to date
    """
    try:
        return service.list_applications(
            page=page,
            page_size=page_size,
            customer_id=customer_id,
            product_id=product_id,
            status=status,
            search=search,
            from_date=from_date,
            to_date=to_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch applications: {str(e)}")


@router.get("/number/{application_number}", response_model=LoanApplicationResponse)
async def get_application_by_number(
    application_number: str,
    service: LoanApplicationService = Depends(get_application_service)
):
    """Get loan application by application number"""
    application = service.get_application_by_number(application_number)
    if not application:
        raise HTTPException(
            status_code=404,
            detail=f"Application '{application_number}' not found"
        )
    
    # Build enriched response
    response = LoanApplicationResponse.model_validate(application)
    
    if application.customer:
        response.customer_name = application.customer.full_name
        response.customer_code = application.customer.customer_code
        response.customer_mobile = application.customer.mobile
        response.customer_cibil_score = application.customer.cibil_score
    
    if application.loan_product:
        response.product_name = application.loan_product.product_name
        response.product_type = application.loan_product.product_type
    
    return response


@router.get("/{application_id}", response_model=LoanApplicationResponse)
async def get_application(
    application_id: int,
    service: LoanApplicationService = Depends(get_application_service)
):
    """Get loan application by ID with all related data"""
    application = service.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Build enriched response
    response = LoanApplicationResponse.model_validate(application)
    
    if application.customer:
        response.customer_name = application.customer.full_name
        response.customer_code = application.customer.customer_code
        response.customer_mobile = application.customer.mobile
        response.customer_cibil_score = application.customer.cibil_score
    
    if application.loan_product:
        response.product_name = application.loan_product.product_name
        response.product_type = application.loan_product.product_type
    
    return response


@router.put("/{application_id}", response_model=LoanApplicationResponse)
async def update_application(
    application_id: int,
    data: LoanApplicationUpdate,
    service: LoanApplicationService = Depends(get_application_service)
):
    """
    Update loan application
    
    Can only update applications in draft or submitted status
    Automatically recalculates EMI if amount or tenure changes
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        application = service.update_application(application_id, data, user_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        response = LoanApplicationResponse.model_validate(application)
        
        if application.customer:
            response.customer_name = application.customer.full_name
            response.customer_code = application.customer.customer_code
            response.customer_mobile = application.customer.mobile
        
        if application.loan_product:
            response.product_name = application.loan_product.product_name
            response.product_type = application.loan_product.product_type
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update application: {str(e)}")


@router.post("/{application_id}/submit", response_model=LoanApplicationResponse)
async def submit_application(
    application_id: int,
    service: LoanApplicationService = Depends(get_application_service)
):
    """
    Submit application for review
    
    Changes status from draft to submitted
    Validates required fields before submission
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        application = service.submit_application(application_id, user_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        response = LoanApplicationResponse.model_validate(application)
        
        if application.customer:
            response.customer_name = application.customer.full_name
            response.customer_code = application.customer.customer_code
            response.customer_mobile = application.customer.mobile
        
        if application.loan_product:
            response.product_name = application.loan_product.product_name
            response.product_type = application.loan_product.product_type
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit application: {str(e)}")


@router.get("/customer/{customer_id}/applications", response_model=LoanApplicationListResponse)
async def get_customer_applications(
    customer_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    service: LoanApplicationService = Depends(get_application_service)
):
    """Get all applications for a specific customer"""
    try:
        return service.list_applications(
            page=page,
            page_size=page_size,
            customer_id=customer_id,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer applications: {str(e)}")
