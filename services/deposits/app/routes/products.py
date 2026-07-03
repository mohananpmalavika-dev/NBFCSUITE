"""
Product Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import (
    DepositProductCreate, DepositProductResponse, 
    InterestSlabCreate, RateCalculationRequest, RateCalculationResponse
)
from ..services import ProductService
from ..engines import RateEngine

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=DepositProductResponse, status_code=201)
def create_product(
    product: DepositProductCreate,
    db: Session = Depends(get_db)
):
    """Create new deposit product"""
    try:
        service = ProductService(db)
        result = service.create_product(
            code=product.code,
            name=product.name,
            deposit_type=product.deposit_type,
            min_amount=product.min_amount,
            max_amount=product.max_amount,
            min_tenure_days=product.min_tenure_days,
            max_tenure_days=product.max_tenure_days,
            interest_method=product.interest_method,
            default_interest_rate=product.default_interest_rate,
            payout_frequency=product.payout_frequency,
            senior_citizen_rate_bonus=product.senior_citizen_rate_bonus,
            premature_allowed=product.premature_allowed,
            premature_penalty_percentage=product.premature_penalty_percentage,
            auto_renewal_allowed=product.auto_renewal_allowed,
            tds_applicable=product.tds_applicable,
            tds_rate=product.tds_rate
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[DepositProductResponse])
def get_products(
    deposit_type: Optional[str] = None,
    status: str = "ACTIVE",
    db: Session = Depends(get_db)
):
    """Get all deposit products"""
    service = ProductService(db)
    return service.get_all_products(deposit_type, status)


@router.get("/{product_id}")
def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get product details with interest slabs"""
    try:
        service = ProductService(db)
        return service.get_product_details(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{product_id}/slabs")
def add_interest_slab(
    product_id: str,
    slab: InterestSlabCreate,
    db: Session = Depends(get_db)
):
    """Add interest rate slab to product"""
    try:
        service = ProductService(db)
        return service.add_interest_slab(
            product_id=product_id,
            interest_rate=slab.interest_rate,
            min_amount=slab.min_amount,
            max_amount=slab.max_amount,
            min_tenure_days=slab.min_tenure_days,
            max_tenure_days=slab.max_tenure_days,
            senior_citizen_rate=slab.senior_citizen_rate,
            effective_from=slab.effective_from,
            effective_to=slab.effective_to
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculate-rate", response_model=RateCalculationResponse)
def calculate_rate(
    request: RateCalculationRequest,
    db: Session = Depends(get_db)
):
    """Calculate applicable interest rate"""
    try:
        rate_engine = RateEngine(db)
        result = rate_engine.calculate_applicable_rate(
            request.product_id,
            request.amount,
            request.tenure_days,
            request.is_senior_citizen
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}/rate-card")
def get_rate_card(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get complete rate card for product"""
    try:
        rate_engine = RateEngine(db)
        return rate_engine.get_rate_card(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/compare-rates")
def compare_rates(
    amount: float,
    tenure_days: int,
    is_senior_citizen: bool = False,
    db: Session = Depends(get_db)
):
    """Compare rates across all products"""
    from decimal import Decimal
    rate_engine = RateEngine(db)
    return rate_engine.compare_rates(
        Decimal(str(amount)),
        tenure_days,
        is_senior_citizen
    )


@router.post("/seed-defaults")
def seed_default_products(
    db: Session = Depends(get_db)
):
    """Seed default FD/RD products"""
    service = ProductService(db)
    return service.seed_default_products()
