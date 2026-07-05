"""
Loan Product Router
API endpoints for loan product management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from shared.database.base import get_db
from .product_service import LoanProductService
from .schemas import (
    LoanProductCreate, LoanProductUpdate, LoanProductResponse,
    LoanProductListResponse, EMICalculationRequest, EMICalculationResponse,
    EMIScheduleResponse
)

router = APIRouter(prefix="/products", tags=["Loan Products"])


def get_product_service(db: Session = Depends(get_db)) -> LoanProductService:
    """Dependency to get product service"""
    # TODO: Get tenant_id from authenticated user context
    tenant_id = 1  # Hardcoded for now
    return LoanProductService(db, tenant_id)


@router.post("", response_model=LoanProductResponse, status_code=201)
async def create_product(
    data: LoanProductCreate,
    service: LoanProductService = Depends(get_product_service)
):
    """
    Create new loan product
    
    - **product_code**: Unique product identifier
    - **product_name**: Display name
    - **product_type**: personal, business, gold, vehicle, home, education, agriculture
    - **loan_category**: secured or unsecured
    - **Interest rates**: min, max, and default rates
    - **Loan amounts**: min and max loan amounts
    - **Tenure**: min and max tenure in months
    - **Fees**: processing fee (fixed or percentage), documentation charges
    - **Penal interest**: rate and grace period
    - **Eligibility**: age, income, CIBIL score requirements
    """
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        product = service.create_product(data, user_id)
        return LoanProductResponse.model_validate(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.get("", response_model=LoanProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    loan_category: Optional[str] = Query(None, description="Filter by loan category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name, code, description"),
    service: LoanProductService = Depends(get_product_service)
):
    """
    List all loan products with pagination and filters
    
    Filters available:
    - **product_type**: personal, business, gold, vehicle, home, education, agriculture
    - **loan_category**: secured, unsecured
    - **is_active**: true/false
    - **search**: Search in product name, code, and description
    """
    try:
        return service.list_products(
            page=page,
            page_size=page_size,
            product_type=product_type,
            loan_category=loan_category,
            is_active=is_active,
            search=search
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")


@router.get("/active", response_model=List[LoanProductResponse])
async def get_active_products(
    service: LoanProductService = Depends(get_product_service)
):
    """Get all active loan products (for dropdown/selection)"""
    try:
        products = service.get_active_products()
        return [LoanProductResponse.model_validate(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active products: {str(e)}")


@router.get("/featured", response_model=List[LoanProductResponse])
async def get_featured_products(
    service: LoanProductService = Depends(get_product_service)
):
    """Get featured loan products (for customer-facing display)"""
    try:
        products = service.get_featured_products()
        return [LoanProductResponse.model_validate(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch featured products: {str(e)}")


@router.get("/code/{product_code}", response_model=LoanProductResponse)
async def get_product_by_code(
    product_code: str,
    service: LoanProductService = Depends(get_product_service)
):
    """Get loan product by product code"""
    product = service.get_product_by_code(product_code)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_code}' not found")
    return LoanProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=LoanProductResponse)
async def get_product(
    product_id: int,
    service: LoanProductService = Depends(get_product_service)
):
    """Get loan product by ID"""
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return LoanProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=LoanProductResponse)
async def update_product(
    product_id: int,
    data: LoanProductUpdate,
    service: LoanProductService = Depends(get_product_service)
):
    """Update loan product"""
    try:
        # TODO: Get user_id from authenticated user
        user_id = 1
        product = service.update_product(product_id, data, user_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return LoanProductResponse.model_validate(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    service: LoanProductService = Depends(get_product_service)
):
    """Soft delete loan product"""
    try:
        success = service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")


@router.post("/calculate-emi", response_model=EMICalculationResponse)
async def calculate_emi(
    request: EMICalculationRequest,
    product_id: Optional[int] = Query(None, description="Product ID to include fees"),
    service: LoanProductService = Depends(get_product_service)
):
    """
    Calculate EMI for given loan parameters
    
    - **loan_amount**: Principal amount
    - **interest_rate**: Annual interest rate (%)
    - **tenure_months**: Loan tenure in months
    - **interest_rate_type**: flat, reducing, or compound
    - **product_id**: Optional - include to calculate processing fees
    
    Returns EMI amount, total interest, and total repayment
    """
    try:
        product = None
        if product_id:
            product = service.get_product(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
        
        return service.calculate_emi(request, product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EMI calculation failed: {str(e)}")


@router.post("/{product_id}/generate-schedule", response_model=EMIScheduleResponse)
async def generate_emi_schedule(
    product_id: int,
    request: EMICalculationRequest,
    service: LoanProductService = Depends(get_product_service)
):
    """
    Generate complete EMI schedule for a loan product
    
    Returns month-by-month breakdown of:
    - EMI amount
    - Principal component
    - Interest component
    - Opening and closing principal balance
    """
    try:
        from datetime import datetime
        
        product = service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate tenure is within product limits
        if request.tenure_months < product.min_tenure_months:
            raise HTTPException(
                status_code=400,
                detail=f"Tenure must be at least {product.min_tenure_months} months"
            )
        if request.tenure_months > product.max_tenure_months:
            raise HTTPException(
                status_code=400,
                detail=f"Tenure must not exceed {product.max_tenure_months} months"
            )
        
        # Validate loan amount
        if request.loan_amount < product.min_loan_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Loan amount must be at least ₹{product.min_loan_amount}"
            )
        if request.loan_amount > product.max_loan_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Loan amount must not exceed ₹{product.max_loan_amount}"
            )
        
        # Generate schedule starting from next month
        start_date = datetime.utcnow()
        
        return service.generate_emi_schedule(
            loan_amount=request.loan_amount,
            interest_rate=request.interest_rate,
            tenure_months=request.tenure_months,
            start_date=start_date,
            interest_rate_type=product.interest_rate_type
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule generation failed: {str(e)}")


@router.post("/{product_id}/check-eligibility")
async def check_eligibility(
    product_id: int,
    customer_age: int = Query(..., ge=18, le=100),
    customer_income: float = Query(..., ge=0),
    customer_cibil: int = Query(..., ge=300, le=900),
    requested_amount: float = Query(..., gt=0),
    service: LoanProductService = Depends(get_product_service)
):
    """
    Check customer eligibility for loan product
    
    Returns eligibility status and list of any eligibility issues
    """
    try:
        from decimal import Decimal
        
        product = service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        is_eligible, errors = service.check_eligibility(
            product=product,
            customer_age=customer_age,
            customer_income=Decimal(str(customer_income)),
            customer_cibil=customer_cibil,
            requested_amount=Decimal(str(requested_amount))
        )
        
        return {
            "eligible": is_eligible,
            "product_name": product.product_name,
            "product_code": product.product_code,
            "errors": errors if not is_eligible else [],
            "message": "Customer is eligible" if is_eligible else "Customer does not meet eligibility criteria"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eligibility check failed: {str(e)}")
