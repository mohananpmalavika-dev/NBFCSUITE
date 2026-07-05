"""
Gold Loan Router
API endpoints for gold loan management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.gold.gold_loan_service import GoldLoanService
from backend.services.gold import schemas


router = APIRouter(prefix="/gold-loans", tags=["Gold Loans"])


def get_gold_loan_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> GoldLoanService:
    """Dependency to get gold loan service"""
    return GoldLoanService(
        db=db,
        user_id=current_user["id"],
        tenant_id=current_user["tenant_id"]
    )


# ============================================
# Gold Loan Product Endpoints
# ============================================

@router.post("/products", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gold_loan_product(
    product_data: schemas.GoldLoanProductCreate,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """
    Create a new gold loan product
    
    - **product_code**: Unique product code
    - **product_name**: Product name
    - **ltv_ratio**: Loan-to-Value ratio percentage
    - **interest_rate**: Interest rate details
    """
    product = await service.create_product(product_data)
    return success_response(
        data=schemas.GoldLoanProductResponse.from_orm(product),
        message="Gold loan product created successfully"
    )


@router.get("/products", response_model=dict)
async def list_gold_loan_products(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """List all gold loan products"""
    products = await service.list_products(is_active=is_active)
    return success_response(
        data={
            "products": [schemas.GoldLoanProductResponse.from_orm(p) for p in products],
            "total": len(products)
        }
    )


@router.get("/products/{product_id}", response_model=dict)
async def get_gold_loan_product(
    product_id: str,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """Get gold loan product by ID"""
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return success_response(
        data=schemas.GoldLoanProductResponse.from_orm(product)
    )


@router.put("/products/{product_id}", response_model=dict)
async def update_gold_loan_product(
    product_id: str,
    product_data: schemas.GoldLoanProductUpdate,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """Update gold loan product"""
    product = await service.update_product(product_id, product_data)
    return success_response(
        data=schemas.GoldLoanProductResponse.from_orm(product),
        message="Product updated successfully"
    )


# ============================================
# Gold Loan Account Endpoints
# ============================================

@router.post("/accounts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gold_loan_account(
    loan_data: schemas.GoldLoanAccountCreate,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """
    Create a new gold loan account
    
    Requires:
    - Customer ID
    - Product ID
    - Loan amount
    - List of gold ornaments with weights and purity
    """
    loan, ornaments = await service.create_gold_loan(loan_data)
    
    return success_response(
        data={
            "loan": schemas.GoldLoanAccountResponse.from_orm(loan),
            "ornaments": [schemas.GoldOrnamentResponse.from_orm(o) for o in ornaments]
        },
        message="Gold loan created successfully"
    )


@router.get("/accounts", response_model=dict)
async def list_gold_loan_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    is_npa: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """
    List gold loan accounts with filters and pagination
    
    Filters:
    - status: Active, Overdue, NPA, Closed, etc.
    - customer_id: Filter by customer
    - branch_id: Filter by branch
    - is_npa: Filter NPA loans
    - search: Search by account number or customer
    """
    params = schemas.GoldLoanListParams(
        page=page,
        page_size=page_size,
        status=status,
        customer_id=customer_id,
        branch_id=branch_id,
        is_npa=is_npa,
        search=search
    )
    
    loans, total = await service.list_gold_loans(params)
    
    return success_response(
        data={
            "loans": [schemas.GoldLoanAccountResponse.from_orm(loan) for loan in loans],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/accounts/{loan_id}", response_model=dict)
async def get_gold_loan_account(
    loan_id: str,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """Get gold loan account details with ornaments"""
    result = await service.get_gold_loan_with_ornaments(loan_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gold loan not found"
        )
    
    loan, ornaments = result
    
    return success_response(
        data={
            "loan": schemas.GoldLoanAccountResponse.from_orm(loan),
            "ornaments": [schemas.GoldOrnamentResponse.from_orm(o) for o in ornaments]
        }
    )


# ============================================
# Transaction Endpoints
# ============================================

@router.post("/accounts/{loan_id}/payments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_payment(
    loan_id: str,
    payment_data: schemas.GoldLoanTransactionCreate,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """
    Record a payment for gold loan
    
    Payment allocation:
    - Charges first
    - Penal interest
    - Interest
    - Principal
    """
    payment_data.gold_loan_id = loan_id
    transaction = await service.record_payment(payment_data)
    
    return success_response(
        data=schemas.GoldLoanTransactionResponse.from_orm(transaction),
        message="Payment recorded successfully"
    )


# ============================================
# Gold Release Endpoints
# ============================================

@router.post("/accounts/{loan_id}/release", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_release_request(
    loan_id: str,
    request_data: schemas.GoldReleaseRequestCreate,
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """
    Create gold release request
    
    Types:
    - **Partial**: Release some ornaments with payment
    - **Full**: Release all ornaments after full payment
    - **Closure**: Close loan and release all gold
    """
    request_data.gold_loan_id = loan_id
    release_request = await service.create_release_request(request_data)
    
    return success_response(
        data=schemas.GoldReleaseRequestResponse.from_orm(release_request),
        message="Release request created successfully"
    )


# ============================================
# Statistics & Reports
# ============================================

@router.get("/statistics", response_model=dict)
async def get_gold_loan_statistics(
    service: GoldLoanService = Depends(get_gold_loan_service)
):
    """
    Get gold loan statistics
    
    Returns:
    - Total and active loans
    - Disbursed and outstanding amounts
    - Total gold weight
    - Average LTV
    - NPA statistics
    - Overdue statistics
    """
    stats = await service.get_statistics()
    return success_response(data=stats)


# ============================================
# Utility Endpoints
# ============================================

@router.get("/ornament-types", response_model=dict)
async def get_ornament_types():
    """Get list of supported ornament types"""
    ornament_types = [
        "Ring", "Chain", "Necklace", "Bracelet", "Bangle",
        "Earring", "Pendant", "Anklet", "Nose Ring", "Coin",
        "Bar", "Biscuit", "Other"
    ]
    return success_response(data={"ornament_types": ornament_types})


@router.get("/purity-options", response_model=dict)
async def get_purity_options():
    """Get gold purity options"""
    purity_options = [
        {"karat": 24, "percentage": 99.90, "label": "24K (99.9%)"},
        {"karat": 22, "percentage": 91.67, "label": "22K (91.67%)"},
        {"karat": 18, "percentage": 75.00, "label": "18K (75%)"},
        {"karat": 14, "percentage": 58.33, "label": "14K (58.33%)"},
    ]
    return success_response(data={"purity_options": purity_options})


@router.post("/calculate-ltv", response_model=dict)
async def calculate_ltv(
    gold_value: float = Query(..., gt=0, description="Total gold value"),
    loan_amount: float = Query(..., gt=0, description="Requested loan amount")
):
    """Calculate LTV ratio"""
    ltv_ratio = (loan_amount / gold_value) * 100
    
    return success_response(
        data={
            "gold_value": gold_value,
            "loan_amount": loan_amount,
            "ltv_ratio": round(ltv_ratio, 2),
            "is_valid": ltv_ratio <= 75.00
        }
    )
