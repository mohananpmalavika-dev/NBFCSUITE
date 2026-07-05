"""
Deposit Product Router

API endpoints for deposit product management including:
- CRUD operations
- Maturity calculations
- Eligibility checks
- Product statistics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .product_service import DepositProductService
from .schemas import (
    DepositProductCreate,
    DepositProductUpdate,
    DepositProductResponse,
    MaturityCalculationRequest,
    MaturityCalculationResponse,
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    PrematureClosureRequest as PrematureClosureCalcRequest,
    PrematureClosureResponse as PrematureClosureCalcResponse,
    ProductStatistics,
    DepositProductFilter,
    DepositType
)

router = APIRouter(prefix="/deposit-products", tags=["Deposit Products"])


# ==================== CRUD OPERATIONS ====================

@router.post("", response_model=dict, status_code=201)
def create_product(
    product_data: DepositProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create new deposit product
    
    - **product_code**: Unique product code
    - **product_name**: Display name
    - **product_type**: savings, fd, rd, or mis
    - **interest_rate**: Annual interest rate (percentage)
    - **min_deposit_amount**: Minimum deposit amount
    
    Returns created product with ID
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    product = service.create_product(product_data.dict())
    
    return success_response(
        message="Deposit product created successfully",
        data=DepositProductResponse.from_orm(product).dict()
    )


@router.get("", response_model=dict)
def list_products(
    product_type: Optional[DepositType] = Query(None, description="Filter by product type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List all deposit products with optional filters
    
    - **product_type**: Filter by savings, fd, rd, or mis
    - **is_active**: Filter active/inactive products
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum records to return
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    products = service.list_products(
        product_type=product_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(products)} products",
        data={
            "products": [DepositProductResponse.from_orm(p).dict() for p in products],
            "total": len(products),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/active", response_model=dict)
def list_active_products(
    product_type: Optional[DepositType] = Query(None, description="Filter by product type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List all active deposit products
    
    Convenience endpoint for getting only active products
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    products = service.list_products(
        product_type=product_type,
        is_active=True,
        skip=0,
        limit=1000
    )
    
    return success_response(
        message=f"Retrieved {len(products)} active products",
        data={"products": [DepositProductResponse.from_orm(p).dict() for p in products]}
    )


@router.get("/{product_id}", response_model=dict)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get deposit product by ID
    
    Returns complete product details including all configuration
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    product = service.get_product(product_id)
    
    return success_response(
        message="Product retrieved successfully",
        data=DepositProductResponse.from_orm(product).dict()
    )


@router.get("/code/{product_code}", response_model=dict)
def get_product_by_code(
    product_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get deposit product by product code
    
    Alternative lookup method using product code instead of ID
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    product = service.get_product_by_code(product_code)
    
    return success_response(
        message="Product retrieved successfully",
        data=DepositProductResponse.from_orm(product).dict()
    )


@router.put("/{product_id}", response_model=dict)
def update_product(
    product_id: int,
    update_data: DepositProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Update deposit product
    
    Only provided fields will be updated. Product type cannot be changed.
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    product = service.update_product(
        product_id,
        update_data.dict(exclude_unset=True)
    )
    
    return success_response(
        message="Product updated successfully",
        data=DepositProductResponse.from_orm(product).dict()
    )


@router.delete("/{product_id}", response_model=dict)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Delete deposit product (soft delete)
    
    Product cannot be deleted if it has active accounts
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    service.delete_product(product_id)
    
    return success_response(
        message="Product deleted successfully",
        data={"product_id": product_id, "deleted": True}
    )


# ==================== CALCULATIONS ====================

@router.post("/calculate-maturity", response_model=dict)
def calculate_maturity(
    calc_request: MaturityCalculationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate maturity amount for FD/RD/MIS
    
    - **FD**: Calculates maturity based on principal, rate, and tenure
    - **RD**: Calculates maturity based on installments
    - **MIS**: Calculates monthly payout
    
    Returns detailed calculation breakdown
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    product = service.get_product(calc_request.product_id)
    
    if product.product_type == 'fd':
        result = service.calculate_fd_maturity(
            calc_request.product_id,
            calc_request.principal_amount,
            calc_request.tenure_days
        )
    elif product.product_type == 'rd':
        if not calc_request.installment_amount or not calc_request.total_installments:
            return success_response(
                message="Installment amount and total installments required for RD",
                data=None,
                status_code=400
            )
        result = service.calculate_rd_maturity(
            calc_request.product_id,
            calc_request.installment_amount,
            calc_request.total_installments
        )
    elif product.product_type == 'mis':
        result = service.calculate_mis_payout(
            calc_request.product_id,
            calc_request.principal_amount,
            calc_request.tenure_days
        )
    else:
        return success_response(
            message="Maturity calculation not applicable for savings accounts",
            data=None,
            status_code=400
        )
    
    return success_response(
        message="Maturity calculated successfully",
        data=result
    )


@router.post("/calculate-interest", response_model=dict)
def calculate_interest(
    principal: float = Query(..., gt=0, description="Principal amount"),
    rate: float = Query(..., ge=0, le=100, description="Interest rate (annual %)"),
    days: int = Query(..., ge=1, description="Number of days"),
    method: str = Query("simple", regex="^(simple|compound)$", description="Calculation method"),
    frequency: str = Query("quarterly", description="Compounding frequency"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate interest for given parameters
    
    Generic interest calculator without product context
    
    - **simple**: Simple interest calculation
    - **compound**: Compound interest with specified frequency
    """
    from decimal import Decimal
    
    service = DepositProductService(db, tenant_id, current_user["id"])
    
    if method == 'simple':
        result = service.calculate_simple_interest(
            Decimal(str(principal)),
            Decimal(str(rate)),
            days
        )
    else:
        result = service.calculate_compound_interest(
            Decimal(str(principal)),
            Decimal(str(rate)),
            days,
            frequency
        )
    
    return success_response(
        message="Interest calculated successfully",
        data=result
    )


@router.post("/check-eligibility", response_model=dict)
def check_eligibility(
    eligibility_request: EligibilityCheckRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Check eligibility for deposit amount and tenure
    
    Validates:
    - Amount within min/max limits
    - Tenure within allowed range (for FD/RD/MIS)
    
    Returns eligibility status with error messages if not eligible
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    result = service.validate_eligibility(
        eligibility_request.product_id,
        eligibility_request.amount,
        eligibility_request.tenure_days
    )
    
    return success_response(
        message="Eligibility check completed",
        data=result
    )


@router.post("/calculate-premature-closure", response_model=dict)
def calculate_premature_closure(
    closure_request: PrematureClosureCalcRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Calculate premature closure amount with penalty
    
    Returns:
    - Interest at reduced rate
    - Penalty amount
    - Net closure amount
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    result = service.calculate_premature_closure(
        closure_request.product_id,
        closure_request.principal_amount,
        closure_request.days_held,
        closure_request.interest_rate
    )
    
    return success_response(
        message="Premature closure amount calculated",
        data=result
    )


# ==================== STATISTICS ====================

@router.get("/{product_id}/statistics", response_model=dict)
def get_product_statistics(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get statistics for deposit product
    
    Returns:
    - Total accounts
    - Total deposits
    - Total balance
    - Total interest paid
    - Status breakdown
    """
    service = DepositProductService(db, tenant_id, current_user["id"])
    stats = service.get_product_statistics(product_id)
    
    return success_response(
        message="Statistics retrieved successfully",
        data=stats
    )
