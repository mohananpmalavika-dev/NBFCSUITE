"""
Customer Management API Router
FastAPI routes for customer operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .service import CustomerService
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CustomerListItem, PaginatedCustomerResponse,
    CustomerDashboardStats, KYCStatusEnum, RiskRatingEnum
)

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_customer_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> CustomerService:
    """Dependency to get customer service"""
    return CustomerService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


# ============================================================================
# CUSTOMER CRUD ENDPOINTS
# ============================================================================

@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Create new customer
    
    - Auto-generates customer code (CUS-YYYYMM-XXXX)
    - Calculates full name and age
    - Creates initial KYC record
    - Validates PAN and Aadhaar format
    """
    customer = await service.create_customer(data)
    return customer


@router.get("", response_model=PaginatedCustomerResponse)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code, mobile, email, PAN"),
    kyc_status: Optional[KYCStatusEnum] = Query(None, description="Filter by KYC status"),
    risk_rating: Optional[RiskRatingEnum] = Query(None, description="Filter by risk rating"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get paginated list of customers
    
    Supports:
    - Search across name, code, mobile, email, PAN
    - Filter by KYC status, risk rating, active status
    - Pagination with configurable page size
    """
    customers, total = await service.get_customers(
        page=page,
        page_size=page_size,
        search=search,
        kyc_status=kyc_status,
        risk_rating=risk_rating,
        is_active=is_active
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedCustomerResponse(
        items=customers,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/stats", response_model=CustomerDashboardStats)
async def get_customer_stats(
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get customer dashboard statistics
    
    Returns:
    - Total customers
    - Active customers
    - KYC pending/completed
    - High risk customers
    - Blacklisted customers
    - New customers this month
    - Average CIBIL score
    """
    stats = await service.get_dashboard_stats()
    return stats


@router.get("/search", response_model=List[CustomerResponse])
async def search_customers(
    mobile: Optional[str] = Query(None, description="Search by mobile number"),
    pan: Optional[str] = Query(None, description="Search by PAN number"),
    aadhaar: Optional[str] = Query(None, description="Search by Aadhaar number"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Search customers by mobile, PAN, or Aadhaar
    
    Useful for:
    - Quick customer lookup during loan application
    - Duplicate detection
    - Customer verification
    """
    if not any([mobile, pan, aadhaar]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search parameter (mobile, pan, or aadhaar) is required"
        )
    
    customers = await service.search_customers(
        mobile=mobile,
        pan=pan,
        aadhaar=aadhaar
    )
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get customer by ID
    
    Returns complete customer details including:
    - Personal information
    - KYC status
    - Documents
    - Family members
    - Bank accounts
    """
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    return customer


@router.get("/code/{customer_code}", response_model=CustomerResponse)
async def get_customer_by_code(
    customer_code: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get customer by customer code
    
    Example: CUS-202607-0001
    """
    customer = await service.get_customer_by_code(customer_code)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with code {customer_code} not found"
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Update customer details
    
    - All fields are optional
    - Full name and age auto-calculated
    - Updates timestamp and user tracking
    """
    customer = await service.update_customer(customer_id, data)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Soft delete customer
    
    - Sets is_deleted = True
    - Sets is_active = False
    - Preserves all data for audit trail
    """
    success = await service.delete_customer(customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    return None


# ============================================================================
# CUSTOMER ACTIONS
# ============================================================================

@router.post("/{customer_id}/blacklist", response_model=CustomerResponse)
async def blacklist_customer(
    customer_id: int,
    reason: str = Query(..., description="Reason for blacklisting"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Blacklist a customer
    
    - Prevents new loan applications
    - Requires reason for audit
    """
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    from datetime import datetime
    customer.is_blacklisted = True
    customer.blacklist_reason = reason
    customer.blacklist_date = datetime.utcnow()
    customer.is_active = False
    
    await service.db.commit()
    await service.db.refresh(customer)
    
    return customer


@router.post("/{customer_id}/unblacklist", response_model=CustomerResponse)
async def unblacklist_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service)
):
    """Remove customer from blacklist"""
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    customer.is_blacklisted = False
    customer.blacklist_reason = None
    customer.blacklist_date = None
    customer.is_active = True
    
    await service.db.commit()
    await service.db.refresh(customer)
    
    return customer


@router.post("/{customer_id}/update-cibil", response_model=CustomerResponse)
async def update_cibil_score(
    customer_id: int,
    cibil_score: int = Query(..., ge=300, le=900, description="CIBIL score (300-900)"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Update customer CIBIL score
    
    - Validates score range (300-900)
    - Updates last checked timestamp
    - May affect risk rating
    """
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    from datetime import datetime
    customer.cibil_score = cibil_score
    customer.cibil_last_checked = datetime.utcnow()
    
    # Auto-adjust risk rating based on CIBIL
    if cibil_score >= 750:
        from backend.shared.database.customer_models import RiskRating
        customer.risk_rating = RiskRating.LOW
    elif cibil_score >= 650:
        customer.risk_rating = RiskRating.MEDIUM
    else:
        customer.risk_rating = RiskRating.HIGH
    
    await service.db.commit()
    await service.db.refresh(customer)
    
    return customer
