"""
Locker Management Router

API endpoints for locker operations including:
- Locker master CRUD
- Allocation management
- Rent payment processing
- Dashboard and analytics
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .locker_service import LockerService
from .allocation_service import AllocationService
from .payment_service import PaymentService
from .schemas import (
    # Locker Master
    LockerMasterCreate, LockerMasterUpdate, LockerMasterResponse,
    LockerMasterFilter, LockerSize, LockerStatus,
    # Allocation
    LockerAllocationCreate, LockerAllocationUpdate, LockerAllocationResponse,
    LockerAllocationFilter, AllocationStatus,
    AllocationClosureRequest, AllocationRenewalRequest,
    # Payment
    LockerRentPaymentCreate, LockerRentPaymentUpdate, LockerRentPaymentResponse,
    RentPaymentFilter, RentCalculationRequest, RentCalculationResponse,
    PaymentType, PaymentMode, PaymentStatus,
    # Analytics
    AvailabilityCheckRequest, AvailabilityCheckResponse,
    LockerOccupancyStats, LockerRevenueStats, LockerDashboardResponse
)

router = APIRouter(prefix="/lockers", tags=["Locker Management"])

# ==================== LOCKER MASTER ENDPOINTS ====================

@router.post("/master", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_locker(
    locker_data: LockerMasterCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new locker in inventory"""
    service = LockerService(db, tenant_id, current_user["id"])
    locker = service.create_locker(locker_data.dict())
    
    return success_response(
        message="Locker created successfully",
        data=LockerMasterResponse.from_orm(locker).dict()
    )


@router.get("/master", response_model=dict)
def list_lockers(
    locker_size: Optional[LockerSize] = Query(None),
    branch_id: Optional[uuid.UUID] = Query(None),
    vault_room: Optional[str] = Query(None),
    status: Optional[LockerStatus] = Query(None),
    is_available: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all lockers with optional filters"""
    service = LockerService(db, tenant_id, current_user["id"])
    lockers = service.list_lockers(
        locker_size=locker_size,
        branch_id=branch_id,
        vault_room=vault_room,
        status=status,
        is_available=is_available,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(lockers)} lockers",
        data={
            "lockers": [LockerMasterResponse.from_orm(l).dict() for l in lockers],
            "total": len(lockers),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/master/{locker_id}", response_model=dict)
def get_locker(
    locker_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get locker by ID"""
    service = LockerService(db, tenant_id, current_user["id"])
    locker = service.get_locker(locker_id)
    
    return success_response(
        message="Locker retrieved successfully",
        data=LockerMasterResponse.from_orm(locker).dict()
    )


@router.put("/master/{locker_id}", response_model=dict)
def update_locker(
    locker_id: uuid.UUID,
    update_data: LockerMasterUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update locker details"""
    service = LockerService(db, tenant_id, current_user["id"])
    locker = service.update_locker(locker_id, update_data.dict(exclude_unset=True))
    
    return success_response(
        message="Locker updated successfully",
        data=LockerMasterResponse.from_orm(locker).dict()
    )


@router.delete("/master/{locker_id}", response_model=dict)
def delete_locker(
    locker_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Delete locker (soft delete)"""
    service = LockerService(db, tenant_id, current_user["id"])
    service.delete_locker(locker_id)
    
    return success_response(message="Locker deleted successfully")


@router.get("/availability", response_model=dict)
def check_availability(
    branch_id: Optional[uuid.UUID] = Query(None),
    locker_size: Optional[LockerSize] = Query(None),
    vault_room: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check available lockers matching criteria"""
    service = LockerService(db, tenant_id, current_user["id"])
    available = service.check_availability(
        branch_id=branch_id,
        locker_size=locker_size,
        vault_room=vault_room
    )
    
    return success_response(
        message=f"Found {len(available)} available lockers",
        data={
            "available_count": len(available),
            "available_lockers": [LockerMasterResponse.from_orm(l).dict() for l in available]
        }
    )


@router.get("/floor-plan", response_model=dict)
def get_floor_plan(
    branch_id: uuid.UUID = Query(...),
    vault_room: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get floor plan layout for vault room"""
    service = LockerService(db, tenant_id, current_user["id"])
    layout = service.get_floor_plan(branch_id, vault_room)
    
    return success_response(
        message="Floor plan retrieved successfully",
        data={"layout": layout}
    )


@router.get("/occupancy-stats", response_model=dict)
def get_occupancy_stats(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get locker occupancy statistics"""
    service = LockerService(db, tenant_id, current_user["id"])
    stats = service.get_occupancy_stats(branch_id)
    
    return success_response(
        message="Occupancy stats retrieved successfully",
        data=stats
    )


# ==================== ALLOCATION ENDPOINTS ====================

@router.post("/allocations", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_allocation(
    allocation_data: LockerAllocationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create new locker allocation"""
    service = AllocationService(db, tenant_id, current_user["id"])
    allocation = service.create_allocation(allocation_data.dict())
    
    return success_response(
        message="Allocation created successfully",
        data=LockerAllocationResponse.from_orm(allocation).dict()
    )


@router.get("/allocations", response_model=dict)
def list_allocations(
    customer_id: Optional[uuid.UUID] = Query(None),
    locker_id: Optional[uuid.UUID] = Query(None),
    status: Optional[AllocationStatus] = Query(None),
    branch_id: Optional[uuid.UUID] = Query(None),
    expiring_within_days: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all allocations with optional filters"""
    service = AllocationService(db, tenant_id, current_user["id"])
    allocations = service.list_allocations(
        customer_id=customer_id,
        locker_id=locker_id,
        status=status,
        branch_id=branch_id,
        expiring_within_days=expiring_within_days,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(allocations)} allocations",
        data={
            "allocations": [LockerAllocationResponse.from_orm(a).dict() for a in allocations],
            "total": len(allocations),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/allocations/{allocation_id}", response_model=dict)
def get_allocation(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get allocation by ID"""
    service = AllocationService(db, tenant_id, current_user["id"])
    allocation = service.get_allocation(allocation_id)
    
    return success_response(
        message="Allocation retrieved successfully",
        data=LockerAllocationResponse.from_orm(allocation).dict()
    )


@router.put("/allocations/{allocation_id}", response_model=dict)
def update_allocation(
    allocation_id: uuid.UUID,
    update_data: LockerAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update allocation details"""
    service = AllocationService(db, tenant_id, current_user["id"])
    allocation = service.update_allocation(allocation_id, update_data.dict(exclude_unset=True))
    
    return success_response(
        message="Allocation updated successfully",
        data=LockerAllocationResponse.from_orm(allocation).dict()
    )


@router.post("/allocations/{allocation_id}/calculate-rent", response_model=dict)
def calculate_rent(
    allocation_id: uuid.UUID,
    calc_request: RentCalculationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate rent for a period"""
    service = AllocationService(db, tenant_id, current_user["id"])
    calculation = service.calculate_rent(
        allocation_id=calc_request.allocation_id,
        period_from=calc_request.period_from,
        period_to=calc_request.period_to,
        include_gst=calc_request.include_gst,
        include_penalty=calc_request.include_penalty
    )
    
    return success_response(
        message="Rent calculated successfully",
        data=calculation
    )


@router.post("/allocations/{allocation_id}/renew", response_model=dict)
def renew_allocation(
    allocation_id: uuid.UUID,
    renewal_data: AllocationRenewalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Renew an allocation"""
    service = AllocationService(db, tenant_id, current_user["id"])
    allocation = service.renew_allocation(
        allocation_id=allocation_id,
        new_end_date=renewal_data.new_end_date,
        annual_rent=renewal_data.annual_rent,
        adjust_security_deposit=renewal_data.adjust_security_deposit,
        additional_deposit=renewal_data.additional_deposit,
        remarks=renewal_data.remarks
    )
    
    return success_response(
        message="Allocation renewed successfully",
        data=LockerAllocationResponse.from_orm(allocation).dict()
    )


@router.post("/allocations/{allocation_id}/close", response_model=dict)
def close_allocation(
    allocation_id: uuid.UUID,
    closure_data: AllocationClosureRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Close an allocation"""
    service = AllocationService(db, tenant_id, current_user["id"])
    allocation, settlement = service.close_allocation(
        allocation_id=allocation_id,
        closure_date=closure_data.closure_date,
        closure_reason=closure_data.closure_reason,
        refund_security_deposit=closure_data.refund_security_deposit,
        closure_charges=closure_data.closure_charges,
        final_settlement_amount=closure_data.final_settlement_amount,
        remarks=closure_data.remarks
    )
    
    return success_response(
        message="Allocation closed successfully",
        data={
            "allocation": LockerAllocationResponse.from_orm(allocation).dict(),
            "settlement": settlement
        }
    )


@router.get("/allocations/expiring/alerts", response_model=dict)
def get_expiring_allocations(
    days_threshold: int = Query(30, ge=1, le=365),
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get allocations expiring soon"""
    service = AllocationService(db, tenant_id, current_user["id"])
    expiring = service.get_expiring_allocations(days_threshold, branch_id)
    
    return success_response(
        message=f"Found {len(expiring)} expiring allocations",
        data={"expiring_allocations": expiring}
    )


@router.get("/allocations/overdue/alerts", response_model=dict)
def get_overdue_rents(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get allocations with overdue rent"""
    service = AllocationService(db, tenant_id, current_user["id"])
    overdue = service.get_overdue_rents(branch_id)
    
    return success_response(
        message=f"Found {len(overdue)} overdue payments",
        data={"overdue_rents": overdue}
    )


# ==================== PAYMENT ENDPOINTS ====================

@router.post("/payments", response_model=dict, status_code=status.HTTP_201_CREATED)
def record_payment(
    payment_data: LockerRentPaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Record a rent payment"""
    service = PaymentService(db, tenant_id, current_user["id"])
    payment = service.record_payment(payment_data.dict())
    
    return success_response(
        message="Payment recorded successfully",
        data=LockerRentPaymentResponse.from_orm(payment).dict()
    )


@router.get("/payments", response_model=dict)
def list_payments(
    allocation_id: Optional[uuid.UUID] = Query(None),
    customer_id: Optional[uuid.UUID] = Query(None),
    payment_type: Optional[PaymentType] = Query(None),
    payment_mode: Optional[PaymentMode] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List all payments with optional filters"""
    service = PaymentService(db, tenant_id, current_user["id"])
    payments = service.list_payments(
        allocation_id=allocation_id,
        customer_id=customer_id,
        payment_type=payment_type,
        payment_mode=payment_mode,
        payment_status=payment_status,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(payments)} payments",
        data={
            "payments": [LockerRentPaymentResponse.from_orm(p).dict() for p in payments],
            "total": len(payments),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/payments/{payment_id}", response_model=dict)
def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get payment by ID"""
    service = PaymentService(db, tenant_id, current_user["id"])
    payment = service.get_payment(payment_id)
    
    return success_response(
        message="Payment retrieved successfully",
        data=LockerRentPaymentResponse.from_orm(payment).dict()
    )


@router.put("/payments/{payment_id}", response_model=dict)
def update_payment(
    payment_id: uuid.UUID,
    update_data: LockerRentPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update payment details"""
    service = PaymentService(db, tenant_id, current_user["id"])
    payment = service.update_payment(payment_id, update_data.dict(exclude_unset=True))
    
    return success_response(
        message="Payment updated successfully",
        data=LockerRentPaymentResponse.from_orm(payment).dict()
    )


@router.post("/payments/{payment_id}/cancel", response_model=dict)
def cancel_payment(
    payment_id: uuid.UUID,
    reason: str = Query(..., min_length=5),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Cancel a payment"""
    service = PaymentService(db, tenant_id, current_user["id"])
    payment = service.cancel_payment(payment_id, reason)
    
    return success_response(
        message="Payment cancelled successfully",
        data=LockerRentPaymentResponse.from_orm(payment).dict()
    )


@router.get("/payments/allocation/{allocation_id}/history", response_model=dict)
def get_payment_history(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get payment history for an allocation"""
    service = PaymentService(db, tenant_id, current_user["id"])
    history = service.get_payment_history(allocation_id)
    
    return success_response(
        message="Payment history retrieved successfully",
        data=history
    )


@router.get("/payments/revenue/stats", response_model=dict)
def get_revenue_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get revenue statistics"""
    from datetime import date as dt_date
    
    start = dt_date.fromisoformat(start_date) if start_date else None
    end = dt_date.fromisoformat(end_date) if end_date else None
    
    service = PaymentService(db, tenant_id, current_user["id"])
    stats = service.get_revenue_stats(start, end, branch_id)
    
    return success_response(
        message="Revenue stats retrieved successfully",
        data=stats
    )


@router.get("/payments/collection/efficiency", response_model=dict)
def get_collection_efficiency(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get collection efficiency metrics"""
    service = PaymentService(db, tenant_id, current_user["id"])
    efficiency = service.get_collection_efficiency(branch_id)
    
    return success_response(
        message="Collection efficiency retrieved successfully",
        data=efficiency
    )


# ==================== DASHBOARD & ANALYTICS ====================

@router.get("/dashboard", response_model=dict)
def get_dashboard(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get comprehensive locker management dashboard"""
    locker_service = LockerService(db, tenant_id, current_user["id"])
    allocation_service = AllocationService(db, tenant_id, current_user["id"])
    payment_service = PaymentService(db, tenant_id, current_user["id"])
    
    # Get occupancy stats
    occupancy = locker_service.get_occupancy_stats(branch_id)
    
    # Get revenue stats
    revenue = payment_service.get_revenue_stats(branch_id=branch_id)
    
    # Get expiring allocations
    expiring = allocation_service.get_expiring_allocations(30, branch_id)
    
    # Get maintenance due
    maintenance_due = locker_service.get_maintenance_due(30, branch_id)
    
    # Get collection efficiency
    collection = payment_service.get_collection_efficiency(branch_id)
    
    dashboard_data = {
        "occupancy": occupancy,
        "revenue": revenue,
        "expiring_allocations": expiring,
        "maintenance_due": maintenance_due,
        "collection_efficiency": collection,
        "recent_allocations": len(allocation_service.list_allocations(skip=0, limit=5)),
        "recent_payments": len(payment_service.list_payments(skip=0, limit=5)),
    }
    
    return success_response(
        message="Dashboard data retrieved successfully",
        data=dashboard_data
    )


@router.get("/reports/inventory", response_model=dict)
def get_inventory_report(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get comprehensive inventory report"""
    service = LockerService(db, tenant_id, current_user["id"])
    report = service.get_inventory_report(branch_id)
    
    return success_response(
        message="Inventory report generated successfully",
        data=report
    )


@router.get("/reports/maintenance-due", response_model=dict)
def get_maintenance_due_report(
    days_threshold: int = Query(30, ge=1, le=365),
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get maintenance due report"""
    service = LockerService(db, tenant_id, current_user["id"])
    maintenance_due = service.get_maintenance_due(days_threshold, branch_id)
    
    return success_response(
        message=f"Found {len(maintenance_due)} lockers requiring maintenance",
        data={"maintenance_due": maintenance_due}
    )


# ==================== HEALTH CHECK ====================

@router.get("/health", response_model=dict)
def health_check():
    """Health check endpoint for locker service"""
    return success_response(
        message="Locker service is healthy",
        data={"status": "healthy", "service": "locker-management"}
    )



# ==================== CUSTOMER MANAGEMENT ENDPOINTS ====================

from .customer_service import LockerCustomerService
from .rent_structure_service import RentStructureService
from .schemas import (
    # Customer
    LockerCustomerCreate, LockerCustomerUpdate, LockerCustomerResponse,
    LockerCustomerSearchRequest, LockerCustomerListResponse,
    CustomerType, CustomerCategory, VerificationStatus,
    # Joint Holder
    LockerJointHolderCreate, LockerJointHolderUpdate, LockerJointHolderResponse,
    OperationMode, HolderType,
    # KYC
    LockerKYCCreate, LockerKYCUpdate, LockerKYCResponse,
    BulkKYCUploadRequest, BulkKYCUploadResponse,
    KYCDocumentType, KYCDocumentCategory,
    # Nominee
    LockerNomineeCreate, LockerNomineeUpdate, LockerNomineeResponse,
    NomineePercentageValidation,
    # Authorization
    LockerAuthorizationCreate, LockerAuthorizationUpdate, LockerAuthorizationResponse,
    AuthorizationApprovalRequest, AuthorizationRevokeRequest,
    AuthorizationType, ApprovalStatus,
    # Rent Structure
    LockerRentStructureCreate, LockerRentStructureUpdate, LockerRentStructureResponse,
    # Analytics
    CustomerAnalytics, JointHolderAnalytics, NomineeAnalytics
)


@router.post("/customers", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_locker_customer(
    customer_data: LockerCustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new locker customer profile"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    customer = await service.create_customer(customer_data)
    
    return success_response(
        message="Locker customer created successfully",
        data=LockerCustomerResponse.from_orm(customer).dict()
    )


@router.get("/customers/{customer_id}", response_model=dict)
async def get_locker_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get locker customer by ID"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    customer = await service.get_customer(customer_id)
    
    if not customer:
        return success_response(
            message="Customer not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Customer retrieved successfully",
        data=LockerCustomerResponse.from_orm(customer).dict()
    )


@router.get("/customers/{customer_id}/complete-profile", response_model=dict)
async def get_customer_complete_profile(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get complete customer profile with all related data"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    profile = await service.get_customer_complete_profile(customer_id)
    
    if not profile:
        return success_response(
            message="Customer not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Customer profile retrieved successfully",
        data=profile
    )


@router.put("/customers/{customer_id}", response_model=dict)
async def update_locker_customer(
    customer_id: uuid.UUID,
    customer_data: LockerCustomerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update locker customer details"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    customer = await service.update_customer(customer_id, customer_data)
    
    if not customer:
        return success_response(
            message="Customer not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Customer updated successfully",
        data=LockerCustomerResponse.from_orm(customer).dict()
    )


@router.post("/customers/{customer_id}/verify", response_model=dict)
async def verify_locker_customer(
    customer_id: uuid.UUID,
    verification_status: VerificationStatus,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Verify customer KYC and details"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    customer = await service.verify_customer(customer_id, verification_status, remarks)
    
    if not customer:
        return success_response(
            message="Customer not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message=f"Customer verification status updated to {verification_status.value}",
        data=LockerCustomerResponse.from_orm(customer).dict()
    )


@router.post("/customers/search", response_model=dict)
async def search_locker_customers(
    search_request: LockerCustomerSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Search locker customers with filters"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    customers, total = await service.search_customers(
        search_query=search_request.search_query,
        customer_category=search_request.customer_category.value if search_request.customer_category else None,
        verification_status=search_request.verification_status.value if search_request.verification_status else None,
        status=search_request.status,
        page=search_request.page,
        page_size=search_request.page_size
    )
    
    return success_response(
        message=f"Found {total} customers",
        data={
            "customers": [LockerCustomerResponse.from_orm(c).dict() for c in customers],
            "total": total,
            "page": search_request.page,
            "page_size": search_request.page_size
        }
    )


# ==================== JOINT HOLDER ENDPOINTS ====================

@router.post("/joint-holders", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_joint_holder(
    joint_holder_data: LockerJointHolderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add a joint holder to an allocation"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    joint_holder = await service.add_joint_holder(joint_holder_data)
    
    return success_response(
        message="Joint holder added successfully",
        data=LockerJointHolderResponse.from_orm(joint_holder).dict()
    )


@router.get("/joint-holders/{joint_holder_id}", response_model=dict)
async def get_joint_holder(
    joint_holder_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get joint holder by ID"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    joint_holder = await service.get_joint_holder(joint_holder_id)
    
    if not joint_holder:
        return success_response(
            message="Joint holder not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Joint holder retrieved successfully",
        data=LockerJointHolderResponse.from_orm(joint_holder).dict()
    )


@router.get("/allocations/{allocation_id}/joint-holders", response_model=dict)
async def get_allocation_joint_holders(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all joint holders for an allocation"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    joint_holders = await service.get_allocation_joint_holders(allocation_id)
    
    return success_response(
        message=f"Retrieved {len(joint_holders)} joint holders",
        data=[LockerJointHolderResponse.from_orm(jh).dict() for jh in joint_holders]
    )


@router.put("/joint-holders/{joint_holder_id}", response_model=dict)
async def update_joint_holder(
    joint_holder_id: uuid.UUID,
    joint_holder_data: LockerJointHolderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update joint holder details"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    joint_holder = await service.update_joint_holder(joint_holder_id, joint_holder_data)
    
    if not joint_holder:
        return success_response(
            message="Joint holder not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Joint holder updated successfully",
        data=LockerJointHolderResponse.from_orm(joint_holder).dict()
    )


@router.post("/joint-holders/{joint_holder_id}/deactivate", response_model=dict)
async def deactivate_joint_holder(
    joint_holder_id: uuid.UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Deactivate a joint holder"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    joint_holder = await service.deactivate_joint_holder(joint_holder_id, reason)
    
    if not joint_holder:
        return success_response(
            message="Joint holder not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Joint holder deactivated successfully",
        data=LockerJointHolderResponse.from_orm(joint_holder).dict()
    )



# ==================== KYC DOCUMENT ENDPOINTS ====================

@router.post("/kyc/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_kyc_document(
    kyc_data: LockerKYCCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Upload a KYC document"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    kyc = await service.upload_kyc_document(kyc_data)
    
    return success_response(
        message="KYC document uploaded successfully",
        data=LockerKYCResponse.from_orm(kyc).dict()
    )


@router.post("/kyc/bulk-upload", response_model=dict)
async def bulk_upload_kyc(
    bulk_request: BulkKYCUploadRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Bulk upload KYC documents"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    result = await service.bulk_upload_kyc(
        bulk_request.locker_customer_id,
        bulk_request.documents
    )
    
    return success_response(
        message=f"Uploaded {result['successful']} of {result['total_uploaded']} documents",
        data=result
    )


@router.get("/kyc/{kyc_id}", response_model=dict)
async def get_kyc_document(
    kyc_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get KYC document by ID"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    kyc = await service.get_kyc_document(kyc_id)
    
    if not kyc:
        return success_response(
            message="KYC document not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="KYC document retrieved successfully",
        data=LockerKYCResponse.from_orm(kyc).dict()
    )


@router.get("/customers/{locker_customer_id}/kyc", response_model=dict)
async def get_customer_kyc_documents(
    locker_customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all KYC documents for a customer"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    kyc_documents = await service.get_customer_kyc_documents(locker_customer_id)
    
    return success_response(
        message=f"Retrieved {len(kyc_documents)} KYC documents",
        data=[LockerKYCResponse.from_orm(kyc).dict() for kyc in kyc_documents]
    )


@router.post("/kyc/{kyc_id}/verify", response_model=dict)
async def verify_kyc_document(
    kyc_id: uuid.UUID,
    verification_status: VerificationStatus,
    verification_remarks: Optional[str] = None,
    rejection_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Verify or reject a KYC document"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    kyc = await service.verify_kyc_document(
        kyc_id, verification_status, verification_remarks, rejection_reason
    )
    
    if not kyc:
        return success_response(
            message="KYC document not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message=f"KYC document {verification_status.value}",
        data=LockerKYCResponse.from_orm(kyc).dict()
    )


@router.get("/customers/{locker_customer_id}/kyc-compliance", response_model=dict)
async def check_kyc_compliance(
    locker_customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check if customer has all mandatory KYC documents"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    compliance = await service.check_kyc_compliance(locker_customer_id)
    
    return success_response(
        message="KYC compliance check completed",
        data=compliance
    )


# ==================== NOMINEE ENDPOINTS ====================

@router.post("/nominees", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_nominee(
    nominee_data: LockerNomineeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add a nominee to an allocation"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    nominee = await service.add_nominee(nominee_data)
    
    return success_response(
        message="Nominee added successfully",
        data=LockerNomineeResponse.from_orm(nominee).dict()
    )


@router.get("/nominees/{nominee_id}", response_model=dict)
async def get_nominee(
    nominee_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get nominee by ID"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    nominee = await service.get_nominee(nominee_id)
    
    if not nominee:
        return success_response(
            message="Nominee not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Nominee retrieved successfully",
        data=LockerNomineeResponse.from_orm(nominee).dict()
    )


@router.get("/allocations/{allocation_id}/nominees", response_model=dict)
async def get_allocation_nominees(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all nominees for an allocation"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    nominees = await service.get_allocation_nominees(allocation_id)
    
    return success_response(
        message=f"Retrieved {len(nominees)} nominees",
        data=[LockerNomineeResponse.from_orm(n).dict() for n in nominees]
    )


@router.put("/nominees/{nominee_id}", response_model=dict)
async def update_nominee(
    nominee_id: uuid.UUID,
    nominee_data: LockerNomineeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update nominee details"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    nominee = await service.update_nominee(nominee_id, nominee_data)
    
    if not nominee:
        return success_response(
            message="Nominee not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Nominee updated successfully",
        data=LockerNomineeResponse.from_orm(nominee).dict()
    )


@router.post("/nominees/{nominee_id}/verify", response_model=dict)
async def verify_nominee(
    nominee_id: uuid.UUID,
    verification_status: VerificationStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Verify nominee details"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    nominee = await service.verify_nominee(nominee_id, verification_status)
    
    if not nominee:
        return success_response(
            message="Nominee not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message=f"Nominee {verification_status.value}",
        data=LockerNomineeResponse.from_orm(nominee).dict()
    )


@router.get("/allocations/{allocation_id}/nominees/validate-percentages", response_model=dict)
async def validate_nominee_percentages(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Validate that nominee percentages total 100%"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    validation = await service.validate_nominee_percentages(allocation_id)
    
    return success_response(
        message="Nominee percentage validation completed",
        data=validation
    )



# ==================== AUTHORIZATION ENDPOINTS ====================

@router.post("/authorizations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_authorization(
    auth_data: LockerAuthorizationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create an authorization for locker access"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    authorization = await service.create_authorization(auth_data)
    
    return success_response(
        message="Authorization created successfully",
        data=LockerAuthorizationResponse.from_orm(authorization).dict()
    )


@router.get("/authorizations/{auth_id}", response_model=dict)
async def get_authorization(
    auth_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get authorization by ID"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    authorization = await service.get_authorization(auth_id)
    
    if not authorization:
        return success_response(
            message="Authorization not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Authorization retrieved successfully",
        data=LockerAuthorizationResponse.from_orm(authorization).dict()
    )


@router.get("/allocations/{allocation_id}/authorizations", response_model=dict)
async def get_allocation_authorizations(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all authorizations for an allocation"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    authorizations = await service.get_allocation_authorizations(allocation_id)
    
    return success_response(
        message=f"Retrieved {len(authorizations)} authorizations",
        data=[LockerAuthorizationResponse.from_orm(auth).dict() for auth in authorizations]
    )


@router.put("/authorizations/{auth_id}", response_model=dict)
async def update_authorization(
    auth_id: uuid.UUID,
    auth_data: LockerAuthorizationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update authorization details"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    authorization = await service.update_authorization(auth_id, auth_data)
    
    if not authorization:
        return success_response(
            message="Authorization not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Authorization updated successfully",
        data=LockerAuthorizationResponse.from_orm(authorization).dict()
    )


@router.post("/authorizations/{auth_id}/approve", response_model=dict)
async def approve_authorization(
    auth_id: uuid.UUID,
    approval_request: AuthorizationApprovalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve or reject an authorization"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    authorization = await service.approve_authorization(
        auth_id,
        approval_request.approval_status,
        approval_request.approval_remarks,
        approval_request.rejection_reason
    )
    
    if not authorization:
        return success_response(
            message="Authorization not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message=f"Authorization {approval_request.approval_status.value}",
        data=LockerAuthorizationResponse.from_orm(authorization).dict()
    )


@router.post("/authorizations/{auth_id}/revoke", response_model=dict)
async def revoke_authorization(
    auth_id: uuid.UUID,
    revoke_request: AuthorizationRevokeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Revoke an authorization"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    authorization = await service.revoke_authorization(
        auth_id,
        revoke_request.revocation_reason,
        revoke_request.revocation_document_path
    )
    
    if not authorization:
        return success_response(
            message="Authorization not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Authorization revoked successfully",
        data=LockerAuthorizationResponse.from_orm(authorization).dict()
    )


@router.get("/authorizations/{auth_id}/check-validity", response_model=dict)
async def check_authorization_validity(
    auth_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check if authorization is currently valid"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    validity = await service.check_authorization_validity(auth_id)
    
    return success_response(
        message="Authorization validity checked",
        data=validity
    )


# ==================== RENT STRUCTURE ENDPOINTS ====================

@router.post("/rent-structures", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_rent_structure(
    structure_data: LockerRentStructureCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new rent structure"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    structure = await service.create_rent_structure(structure_data)
    
    return success_response(
        message="Rent structure created successfully",
        data=LockerRentStructureResponse.from_orm(structure).dict()
    )


@router.get("/rent-structures/{structure_id}", response_model=dict)
async def get_rent_structure(
    structure_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get rent structure by ID"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    structure = await service.get_rent_structure(structure_id)
    
    if not structure:
        return success_response(
            message="Rent structure not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Rent structure retrieved successfully",
        data=LockerRentStructureResponse.from_orm(structure).dict()
    )


@router.get("/rent-structures", response_model=dict)
async def list_rent_structures(
    locker_size: Optional[LockerSize] = Query(None),
    customer_category: Optional[CustomerCategory] = Query(None),
    branch_id: Optional[uuid.UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List rent structures with filters"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    structures, total = await service.list_rent_structures(
        locker_size=locker_size,
        customer_category=customer_category,
        branch_id=branch_id,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    return success_response(
        message=f"Retrieved {len(structures)} rent structures",
        data={
            "structures": [LockerRentStructureResponse.from_orm(s).dict() for s in structures],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.put("/rent-structures/{structure_id}", response_model=dict)
async def update_rent_structure(
    structure_id: uuid.UUID,
    structure_data: LockerRentStructureUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update rent structure"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    structure = await service.update_rent_structure(structure_id, structure_data)
    
    if not structure:
        return success_response(
            message="Rent structure not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Rent structure updated successfully",
        data=LockerRentStructureResponse.from_orm(structure).dict()
    )


@router.post("/rent-structures/{structure_id}/deactivate", response_model=dict)
async def deactivate_rent_structure(
    structure_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Deactivate a rent structure"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    structure = await service.deactivate_rent_structure(structure_id)
    
    if not structure:
        return success_response(
            message="Rent structure not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Rent structure deactivated successfully",
        data=LockerRentStructureResponse.from_orm(structure).dict()
    )


@router.post("/rent-structures/calculate-rent", response_model=dict)
async def calculate_rent(
    calculation_request: RentCalculationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate rent amount based on parameters"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    calculation = await service.calculate_rent(calculation_request)
    
    return success_response(
        message="Rent calculated successfully",
        data=calculation.dict()
    )


@router.get("/rent-structures/comparison/{locker_size}", response_model=dict)
async def get_rent_structure_comparison(
    locker_size: LockerSize,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Compare rent structures across customer categories"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    comparison = await service.get_rent_structure_comparison(locker_size)
    
    return success_response(
        message="Rent structure comparison retrieved",
        data=comparison
    )


@router.get("/rent-structures/pricing-summary", response_model=dict)
async def get_pricing_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get pricing summary across all sizes and categories"""
    service = RentStructureService(db, tenant_id, current_user["id"])
    summary = await service.get_pricing_summary()
    
    return success_response(
        message="Pricing summary retrieved",
        data=summary
    )


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics/customers", response_model=dict)
async def get_customer_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get customer analytics summary"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    analytics = await service.get_customer_analytics()
    
    return success_response(
        message="Customer analytics retrieved",
        data=analytics.dict()
    )


@router.get("/analytics/joint-holders", response_model=dict)
async def get_joint_holder_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get joint holder analytics"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    analytics = await service.get_joint_holder_analytics()
    
    return success_response(
        message="Joint holder analytics retrieved",
        data=analytics.dict()
    )


@router.get("/analytics/nominees", response_model=dict)
async def get_nominee_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get nominee analytics"""
    service = LockerCustomerService(db, tenant_id, current_user["id"])
    analytics = await service.get_nominee_analytics()
    
    return success_response(
        message="Nominee analytics retrieved",
        data=analytics.dict()
    )


# ==================== APPLICATION ENDPOINTS ====================

from .application_service import ApplicationService
from .schemas import (
    LockerApplicationCreate, LockerApplicationUpdate, LockerApplicationResponse,
    ApplicationReviewRequest, ApplicationApprovalRequest, ApplicationAllocationRequest,
    ApplicationFilter, ApplicationStatus, ApplicationType, ApplicationAnalytics
)

@router.post("/applications", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: LockerApplicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new locker rental application"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.create_application(application_data)
    
    return success_response(
        message="Application submitted successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.get("/applications/{application_id}", response_model=dict)
async def get_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get application by ID"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.get_application(application_id)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message="Application retrieved successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.get("/applications/number/{application_number}", response_model=dict)
async def get_application_by_number(
    application_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get application by application number"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.get_application_by_number(application_number)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message="Application retrieved successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.post("/applications/list", response_model=dict)
async def list_applications(
    filters: ApplicationFilter,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List applications with filters"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    skip = (filters.page - 1) * filters.page_size
    applications, total = await service.list_applications(filters, skip, filters.page_size)
    
    return success_response(
        message=f"Retrieved {len(applications)} applications",
        data={
            "applications": [LockerApplicationResponse.from_orm(a).dict() for a in applications],
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size
        }
    )


@router.put("/applications/{application_id}", response_model=dict)
async def update_application(
    application_id: uuid.UUID,
    update_data: LockerApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update application details"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.update_application(application_id, update_data)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message="Application updated successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.post("/applications/{application_id}/review", response_model=dict)
async def review_application(
    application_id: uuid.UUID,
    review_data: ApplicationReviewRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Review an application"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.review_application(application_id, review_data)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message="Application reviewed successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.post("/applications/{application_id}/approve", response_model=dict)
async def approve_application(
    application_id: uuid.UUID,
    approval_data: ApplicationApprovalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve or reject an application"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.approve_application(application_id, approval_data)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message=f"Application {approval_data.approved and 'approved' or 'rejected'} successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.post("/applications/{application_id}/allocate", response_model=dict)
async def allocate_locker_to_application(
    application_id: uuid.UUID,
    allocation_data: ApplicationAllocationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Allocate locker to approved application"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.allocate_locker(application_id, allocation_data)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message="Locker allocated successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.post("/applications/{application_id}/cancel", response_model=dict)
async def cancel_application(
    application_id: uuid.UUID,
    reason: str = Query(..., min_length=5),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Cancel an application"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    application = await service.cancel_application(application_id, reason)
    
    if not application:
        return success_response(message="Application not found", data=None, status_code=404)
    
    return success_response(
        message="Application cancelled successfully",
        data=LockerApplicationResponse.from_orm(application).dict()
    )


@router.get("/applications/pending-approvals", response_model=dict)
async def get_pending_approvals(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get applications pending approval"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    applications = await service.get_pending_approvals(branch_id)
    
    return success_response(
        message=f"Found {len(applications)} pending approvals",
        data=[LockerApplicationResponse.from_orm(a).dict() for a in applications]
    )


@router.get("/applications/customer/{customer_id}", response_model=dict)
async def get_customer_applications(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all applications for a customer"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    applications = await service.get_applications_by_customer(customer_id)
    
    return success_response(
        message=f"Retrieved {len(applications)} applications",
        data=[LockerApplicationResponse.from_orm(a).dict() for a in applications]
    )


@router.get("/applications/{application_id}/history", response_model=dict)
async def get_application_history(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get application processing history"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    history = await service.get_application_history(application_id)
    
    return success_response(
        message="Application history retrieved successfully",
        data={"history": history}
    )


@router.get("/applications/analytics", response_model=dict)
async def get_application_analytics(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get application analytics"""
    service = ApplicationService(db, tenant_id, current_user["id"])
    analytics = await service.get_analytics(branch_id)
    
    return success_response(
        message="Application analytics retrieved successfully",
        data=analytics.dict()
    )


# ==================== WAITING LIST ENDPOINTS ====================

from .waiting_list_service import WaitingListService
from .schemas import (
    LockerWaitingListCreate, LockerWaitingListUpdate, LockerWaitingListResponse,
    WaitingListOfferRequest, WaitingListOfferResponse, WaitingListFilter,
    WaitingListStatus, WaitingListAnalytics, WaitingListStatistics
)

@router.post("/waiting-list", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_to_waiting_list(
    waiting_list_data: LockerWaitingListCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add customer to waiting list"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.add_to_waiting_list(waiting_list_data)
    
    return success_response(
        message="Added to waiting list successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.get("/waiting-list/{entry_id}", response_model=dict)
async def get_waiting_list_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get waiting list entry by ID"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.get_waiting_entry(entry_id)
    
    if not entry:
        return success_response(message="Entry not found", data=None, status_code=404)
    
    return success_response(
        message="Waiting list entry retrieved successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.post("/waiting-list/list", response_model=dict)
async def list_waiting_list(
    filters: WaitingListFilter,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List waiting list entries with filters"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    skip = (filters.page - 1) * filters.page_size
    entries, total = await service.list_waiting_entries(filters, skip, filters.page_size)
    
    return success_response(
        message=f"Retrieved {len(entries)} waiting list entries",
        data={
            "entries": [LockerWaitingListResponse.from_orm(e).dict() for e in entries],
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size
        }
    )


@router.put("/waiting-list/{entry_id}", response_model=dict)
async def update_waiting_list_entry(
    entry_id: uuid.UUID,
    update_data: LockerWaitingListUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update waiting list entry"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.update_waiting_entry(entry_id, update_data)
    
    if not entry:
        return success_response(message="Entry not found", data=None, status_code=404)
    
    return success_response(
        message="Waiting list entry updated successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.post("/waiting-list/{entry_id}/make-offer", response_model=dict)
async def make_locker_offer(
    entry_id: uuid.UUID,
    offer_data: WaitingListOfferRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Make locker offer to waiting list customer"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.make_offer(entry_id, offer_data)
    
    if not entry:
        return success_response(message="Entry not found", data=None, status_code=404)
    
    return success_response(
        message="Offer made successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.post("/waiting-list/{entry_id}/respond", response_model=dict)
async def record_customer_response(
    entry_id: uuid.UUID,
    response_data: WaitingListOfferResponse,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Record customer response to offer"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.record_customer_response(entry_id, response_data)
    
    if not entry:
        return success_response(message="Entry not found", data=None, status_code=404)
    
    return success_response(
        message="Customer response recorded successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.post("/waiting-list/{entry_id}/allocate", response_model=dict)
async def process_waiting_list_allocation(
    entry_id: uuid.UUID,
    allocation_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Mark entry as allocated"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.process_allocation(entry_id, allocation_id)
    
    if not entry:
        return success_response(message="Entry not found", data=None, status_code=404)
    
    return success_response(
        message="Allocation processed successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.delete("/waiting-list/{entry_id}", response_model=dict)
async def remove_from_waiting_list(
    entry_id: uuid.UUID,
    reason: str = Query(..., min_length=5),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Remove customer from waiting list"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.remove_from_waiting_list(entry_id, reason)
    
    if not entry:
        return success_response(message="Entry not found", data=None, status_code=404)
    
    return success_response(
        message="Removed from waiting list successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.get("/waiting-list/next-in-queue", response_model=dict)
async def get_next_in_queue(
    branch_id: uuid.UUID = Query(...),
    locker_size: LockerSize = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get next customer in queue"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entry = await service.get_next_in_queue(branch_id, locker_size)
    
    if not entry:
        return success_response(message="No customers in queue", data=None, status_code=404)
    
    return success_response(
        message="Next customer retrieved successfully",
        data=LockerWaitingListResponse.from_orm(entry).dict()
    )


@router.get("/waiting-list/customer/{customer_id}", response_model=dict)
async def get_customer_waiting_entries(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all waiting list entries for customer"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    entries = await service.get_customer_waiting_entries(customer_id)
    
    return success_response(
        message=f"Retrieved {len(entries)} waiting list entries",
        data=[LockerWaitingListResponse.from_orm(e).dict() for e in entries]
    )


@router.get("/waiting-list/analytics", response_model=dict)
async def get_waiting_list_analytics(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get waiting list analytics"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    analytics = await service.get_analytics(branch_id)
    
    return success_response(
        message="Waiting list analytics retrieved successfully",
        data=analytics.dict()
    )


@router.get("/waiting-list/statistics", response_model=dict)
async def get_waiting_list_statistics(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get waiting list statistics"""
    service = WaitingListService(db, tenant_id, current_user["id"])
    statistics = await service.get_statistics(branch_id)
    
    return success_response(
        message="Waiting list statistics retrieved successfully",
        data=statistics.dict()
    )


# ==================== KEY HANDOVER ENDPOINTS ====================

from .key_handover_service import KeyHandoverService
from .schemas import (
    LockerKeyHandoverCreate, LockerKeyHandoverUpdate, LockerKeyHandoverResponse,
    KeyLostReportRequest, KeyReturnRequest, KeyHandoverFilter,
    HandoverType, KeyStatus, KeyHandoverStatistics
)

@router.post("/key-handovers", response_model=dict, status_code=status.HTTP_201_CREATED)
async def issue_keys(
    handover_data: LockerKeyHandoverCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Issue locker keys to customer"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.issue_keys(handover_data)
    
    return success_response(
        message="Keys issued successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.get("/key-handovers/{handover_id}", response_model=dict)
async def get_key_handover(
    handover_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get key handover by ID"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.get_handover(handover_id)
    
    if not handover:
        return success_response(message="Key handover not found", data=None, status_code=404)
    
    return success_response(
        message="Key handover retrieved successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.get("/key-handovers/allocation/{allocation_id}", response_model=dict)
async def get_handover_by_allocation(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get active key handover for allocation"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.get_handover_by_allocation(allocation_id)
    
    if not handover:
        return success_response(message="Key handover not found", data=None, status_code=404)
    
    return success_response(
        message="Key handover retrieved successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.post("/key-handovers/list", response_model=dict)
async def list_key_handovers(
    filters: KeyHandoverFilter,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List key handovers with filters"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    skip = (filters.page - 1) * filters.page_size
    handovers, total = await service.list_handovers(filters, skip, filters.page_size)
    
    return success_response(
        message=f"Retrieved {len(handovers)} key handovers",
        data={
            "handovers": [LockerKeyHandoverResponse.from_orm(h).dict() for h in handovers],
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size
        }
    )


@router.put("/key-handovers/{handover_id}", response_model=dict)
async def update_key_handover(
    handover_id: uuid.UUID,
    update_data: LockerKeyHandoverUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update key handover details"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.update_handover(handover_id, update_data)
    
    if not handover:
        return success_response(message="Key handover not found", data=None, status_code=404)
    
    return success_response(
        message="Key handover updated successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.post("/key-handovers/{handover_id}/return", response_model=dict)
async def return_keys(
    handover_id: uuid.UUID,
    return_data: KeyReturnRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Process key return"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.return_keys(handover_id, return_data)
    
    if not handover:
        return success_response(message="Key handover not found", data=None, status_code=404)
    
    return success_response(
        message="Keys returned successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.post("/key-handovers/{handover_id}/report-lost", response_model=dict)
async def report_lost_key(
    handover_id: uuid.UUID,
    report_data: KeyLostReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Report lost key"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.report_lost_key(handover_id, report_data)
    
    if not handover:
        return success_response(message="Key handover not found", data=None, status_code=404)
    
    return success_response(
        message="Lost key reported successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.post("/key-handovers/{handover_id}/issue-duplicate", response_model=dict)
async def issue_duplicate_key(
    handover_id: uuid.UUID,
    reason: str = Query(..., min_length=5),
    authorization: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Issue duplicate key"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handover = await service.issue_duplicate_key(handover_id, reason, authorization)
    
    if not handover:
        return success_response(message="Key handover not found", data=None, status_code=404)
    
    return success_response(
        message="Duplicate key issued successfully",
        data=LockerKeyHandoverResponse.from_orm(handover).dict()
    )


@router.get("/key-handovers/customer/{customer_id}/active", response_model=dict)
async def get_customer_active_keys(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get active keys for customer"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handovers = await service.get_active_keys_by_customer(customer_id)
    
    return success_response(
        message=f"Retrieved {len(handovers)} active key handovers",
        data=[LockerKeyHandoverResponse.from_orm(h).dict() for h in handovers]
    )


@router.get("/key-handovers/lost-keys/pending-action", response_model=dict)
async def get_lost_keys_pending_action(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get lost keys pending recovery action"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    handovers = await service.get_lost_keys_pending_action()
    
    return success_response(
        message=f"Found {len(handovers)} lost keys pending action",
        data=[LockerKeyHandoverResponse.from_orm(h).dict() for h in handovers]
    )


@router.get("/key-handovers/locker/{locker_id}/verify-dual-key", response_model=dict)
async def verify_dual_key_availability(
    locker_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Verify both keys available for locker access"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    verification = await service.verify_dual_key_availability(locker_id)
    
    return success_response(
        message="Dual key verification completed",
        data=verification
    )


@router.get("/key-handovers/statistics", response_model=dict)
async def get_key_handover_statistics(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get key handover statistics"""
    service = KeyHandoverService(db, tenant_id, current_user["id"])
    statistics = await service.get_statistics(branch_id)
    
    return success_response(
        message="Key handover statistics retrieved successfully",
        data=statistics.dict()
    )


# ==================== AGREEMENT ENDPOINTS ====================

from .agreement_service import AgreementService
from .schemas import (
    LockerAgreementCreate, LockerAgreementUpdate, LockerAgreementResponse,
    AgreementSignatureRequest, AgreementExecutionRequest, AgreementRenewalRequest,
    AgreementTerminationRequest, AgreementAmendmentRequest, AgreementFilter,
    AgreementStatus, AgreementType, AgreementStatistics
)

@router.post("/agreements", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_agreement(
    agreement_data: LockerAgreementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new locker rental agreement"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.create_agreement(agreement_data)
    
    return success_response(
        message="Agreement created successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.get("/agreements/{agreement_id}", response_model=dict)
async def get_agreement(
    agreement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get agreement by ID"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.get_agreement(agreement_id)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement retrieved successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.get("/agreements/number/{agreement_number}", response_model=dict)
async def get_agreement_by_number(
    agreement_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get agreement by agreement number"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.get_agreement_by_number(agreement_number)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement retrieved successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.get("/agreements/allocation/{allocation_id}", response_model=dict)
async def get_agreement_by_allocation(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get active agreement for allocation"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.get_agreement_by_allocation(allocation_id)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement retrieved successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.post("/agreements/list", response_model=dict)
async def list_agreements(
    filters: AgreementFilter,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List agreements with filters"""
    service = AgreementService(db, tenant_id, current_user["id"])
    skip = (filters.page - 1) * filters.page_size
    agreements, total = await service.list_agreements(filters, skip, filters.page_size)
    
    return success_response(
        message=f"Retrieved {len(agreements)} agreements",
        data={
            "agreements": [LockerAgreementResponse.from_orm(a).dict() for a in agreements],
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size
        }
    )


@router.put("/agreements/{agreement_id}", response_model=dict)
async def update_agreement(
    agreement_id: uuid.UUID,
    update_data: LockerAgreementUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update agreement details"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.update_agreement(agreement_id, update_data)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement updated successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.post("/agreements/{agreement_id}/sign", response_model=dict)
async def add_signature_to_agreement(
    agreement_id: uuid.UUID,
    signature_data: AgreementSignatureRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add signature to agreement"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.add_signature(agreement_id, signature_data)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Signature added successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.post("/agreements/{agreement_id}/execute", response_model=dict)
async def execute_agreement(
    agreement_id: uuid.UUID,
    execution_data: AgreementExecutionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Execute agreement"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.execute_agreement(agreement_id, execution_data)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement executed successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.post("/agreements/{agreement_id}/renew", response_model=dict)
async def renew_agreement(
    agreement_id: uuid.UUID,
    renewal_data: AgreementRenewalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Renew agreement"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.renew_agreement(agreement_id, renewal_data)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement renewed successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.post("/agreements/{agreement_id}/terminate", response_model=dict)
async def terminate_agreement(
    agreement_id: uuid.UUID,
    termination_data: AgreementTerminationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Terminate agreement"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.terminate_agreement(agreement_id, termination_data)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement terminated successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.post("/agreements/{agreement_id}/amend", response_model=dict)
async def amend_agreement(
    agreement_id: uuid.UUID,
    amendment_data: AgreementAmendmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add amendment to agreement"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreement = await service.amend_agreement(agreement_id, amendment_data)
    
    if not agreement:
        return success_response(message="Agreement not found", data=None, status_code=404)
    
    return success_response(
        message="Agreement amended successfully",
        data=LockerAgreementResponse.from_orm(agreement).dict()
    )


@router.get("/agreements/expiring", response_model=dict)
async def get_expiring_agreements(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get agreements expiring within specified days"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreements = await service.check_expiring_agreements(days)
    
    return success_response(
        message=f"Found {len(agreements)} expiring agreements",
        data=[LockerAgreementResponse.from_orm(a).dict() for a in agreements]
    )


@router.get("/agreements/pending-signatures", response_model=dict)
async def get_pending_signatures(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get agreements pending signatures"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreements = await service.get_pending_signatures(branch_id)
    
    return success_response(
        message=f"Found {len(agreements)} agreements pending signatures",
        data=[LockerAgreementResponse.from_orm(a).dict() for a in agreements]
    )


@router.get("/agreements/customer/{customer_id}", response_model=dict)
async def get_customer_agreements(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get all agreements for customer"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreements = await service.get_customer_agreements(customer_id)
    
    return success_response(
        message=f"Retrieved {len(agreements)} agreements",
        data=[LockerAgreementResponse.from_orm(a).dict() for a in agreements]
    )


@router.get("/agreements/allocation/{allocation_id}/history", response_model=dict)
async def get_agreement_history(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get complete agreement history for allocation"""
    service = AgreementService(db, tenant_id, current_user["id"])
    agreements = await service.get_agreement_history(allocation_id)
    
    return success_response(
        message=f"Retrieved {len(agreements)} agreements",
        data=[LockerAgreementResponse.from_orm(a).dict() for a in agreements]
    )


@router.get("/agreements/statistics", response_model=dict)
async def get_agreement_statistics(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get agreement statistics"""
    service = AgreementService(db, tenant_id, current_user["id"])
    statistics = await service.get_statistics(branch_id)
    
    return success_response(
        message="Agreement statistics retrieved successfully",
        data=statistics.dict()
    )


@router.post("/agreements/send-renewal-notices", response_model=dict)
async def send_renewal_notices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send renewal notices for agreements with auto-renewal"""
    service = AgreementService(db, tenant_id, current_user["id"])
    result = await service.send_renewal_notices()
    
    return success_response(
        message=f"Sent {result['notices_sent']} renewal notices",
        data=result
    )


# ==================== LOCKER ACCESS & OPERATIONS ENDPOINTS ====================

from .access_service import LockerAccessService
from .operating_hours_service import LockerOperatingHoursService
from .schemas import (
    LockerAccessLogCreate, LockerAccessLogUpdate, LockerAccessLogResponse
)
from datetime import datetime, date, time

@router.post("/access/request", response_model=dict, status_code=status.HTTP_201_CREATED)
async def request_locker_access(
    access_data: LockerAccessLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Request locker access with verification"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    access_log = await service.request_access(access_data)
    
    return success_response(
        message="Access request created successfully",
        data=access_log.dict()
    )


@router.patch("/access/{access_log_id}/complete", response_model=dict)
async def complete_locker_access(
    access_log_id: uuid.UUID,
    exit_time: datetime,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Complete locker access by recording exit time"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    access_log = await service.complete_access(access_log_id, exit_time, remarks)
    
    return success_response(
        message="Access completed successfully",
        data=access_log.dict()
    )


@router.patch("/access/{access_log_id}/verify-biometric", response_model=dict)
async def verify_biometric(
    access_log_id: uuid.UUID,
    biometric_data: str,
    verified: bool,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Record biometric verification for access"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    access_log = await service.verify_biometric(access_log_id, biometric_data, verified)
    
    return success_response(
        message="Biometric verification recorded",
        data=access_log.dict()
    )


@router.patch("/access/{access_log_id}/capture-photo", response_model=dict)
async def capture_photo(
    access_log_id: uuid.UUID,
    photo_path: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Record photo capture for access"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    access_log = await service.capture_photo(access_log_id, photo_path)
    
    return success_response(
        message="Photo captured successfully",
        data=access_log.dict()
    )


@router.patch("/access/{access_log_id}/capture-signature", response_model=dict)
async def capture_signature(
    access_log_id: uuid.UUID,
    signature_path: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Record signature capture for access"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    access_log = await service.capture_signature(access_log_id, signature_path)
    
    return success_response(
        message="Signature captured successfully",
        data=access_log.dict()
    )


@router.get("/access/logs", response_model=dict)
async def list_access_logs(
    locker_id: Optional[uuid.UUID] = Query(None),
    allocation_id: Optional[uuid.UUID] = Query(None),
    customer_id: Optional[uuid.UUID] = Query(None),
    access_date_from: Optional[date] = Query(None),
    access_date_to: Optional[date] = Query(None),
    accessor_type: Optional[str] = Query(None),
    purpose: Optional[str] = Query(None),
    emergency_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List access logs with filters"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    result = await service.list_access_logs(
        locker_id=locker_id,
        allocation_id=allocation_id,
        customer_id=customer_id,
        access_date_from=access_date_from,
        access_date_to=access_date_to,
        accessor_type=accessor_type,
        purpose=purpose,
        emergency_only=emergency_only,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(result['access_logs'])} access logs",
        data=result
    )


@router.get("/access/logs/{access_log_id}", response_model=dict)
async def get_access_log(
    access_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get access log by ID"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    access_log = await service.get_access_log(access_log_id)
    
    if not access_log:
        return success_response(
            message="Access log not found",
            data=None,
            status_code=404
        )
    
    return success_response(
        message="Access log retrieved successfully",
        data=access_log.dict()
    )


@router.get("/access/active-sessions", response_model=dict)
async def get_active_sessions(
    locker_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get currently active access sessions"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    sessions = await service.get_active_access_sessions(locker_id)
    
    return success_response(
        message=f"Retrieved {len(sessions)} active sessions",
        data={"active_sessions": [s.dict() for s in sessions]}
    )


@router.get("/access/customer/{customer_id}/history", response_model=dict)
async def get_customer_access_history(
    customer_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get access history for a customer"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    history = await service.get_customer_access_history(customer_id, limit)
    
    return success_response(
        message=f"Retrieved {len(history)} access records",
        data={"access_history": [h.dict() for h in history]}
    )


@router.get("/access/statistics", response_model=dict)
async def get_access_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get access statistics"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    stats = await service.get_access_statistics(date_from, date_to)
    
    return success_response(
        message="Statistics retrieved successfully",
        data=stats
    )


@router.get("/access/register/report", response_model=dict)
async def get_access_register_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    locker_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Generate access register report for audit"""
    service = LockerAccessService(db, tenant_id, current_user["id"])
    report = await service.get_access_register_report(date_from, date_to, locker_id)
    
    return success_response(
        message="Access register report generated",
        data={"register": report, "date_from": date_from, "date_to": date_to}
    )


# ==================== OPERATING HOURS ENDPOINTS ====================

@router.get("/operations/facility-status", response_model=dict)
async def check_facility_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check if locker facility is currently open"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    status = await service.is_facility_open()
    
    return success_response(
        message="Facility status retrieved successfully",
        data=status
    )


@router.get("/operations/hours", response_model=dict)
async def get_operating_hours(
    for_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get operating hours for a specific date"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    hours = await service.get_operating_hours(for_date)
    
    return success_response(
        message="Operating hours retrieved successfully",
        data=hours
    )


@router.get("/operations/hours/weekly", response_model=dict)
async def get_weekly_schedule(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get weekly operating hours schedule"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    schedule = await service.get_weekly_schedule()
    
    return success_response(
        message="Weekly schedule retrieved successfully",
        data={"weekly_schedule": schedule}
    )


@router.post("/operations/special-access/holiday", response_model=dict)
async def request_holiday_access(
    customer_id: uuid.UUID,
    locker_id: uuid.UUID,
    allocation_id: uuid.UUID,
    access_date: date,
    reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Request special holiday access"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    request = await service.request_holiday_access(
        customer_id=customer_id,
        locker_id=locker_id,
        allocation_id=allocation_id,
        access_date=access_date,
        reason=reason
    )
    
    return success_response(
        message="Holiday access request submitted successfully",
        data=request
    )


@router.post("/operations/special-access/after-hours", response_model=dict)
async def request_after_hours_access(
    customer_id: uuid.UUID,
    locker_id: uuid.UUID,
    allocation_id: uuid.UUID,
    access_date: date,
    access_time: time,
    reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Request after-hours access"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    request = await service.request_after_hours_access(
        customer_id=customer_id,
        locker_id=locker_id,
        allocation_id=allocation_id,
        access_date=access_date,
        access_time=access_time,
        reason=reason
    )
    
    return success_response(
        message="After-hours access request submitted successfully",
        data=request
    )


@router.post("/operations/special-access/approve", response_model=dict)
async def approve_special_access(
    request_id: uuid.UUID,
    approved: bool,
    approval_remarks: Optional[str] = None,
    rejection_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve or reject special access request"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    result = await service.approve_special_access(
        request_id=request_id,
        approved=approved,
        approval_remarks=approval_remarks,
        rejection_reason=rejection_reason
    )
    
    return success_response(
        message=f"Special access request {approved and 'approved' or 'rejected'} successfully",
        data=result
    )


@router.get("/operations/emergency-protocol", response_model=dict)
async def get_emergency_protocol(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get emergency access protocol and authorization requirements"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    protocol = await service.get_emergency_access_protocol()
    
    return success_response(
        message="Emergency protocol retrieved successfully",
        data=protocol
    )


@router.get("/operations/escort-requirements", response_model=dict)
async def get_escort_requirements(
    access_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get escort service requirements"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    requirements = await service.get_escort_requirements(access_type)
    
    return success_response(
        message="Escort requirements retrieved successfully",
        data=requirements
    )


@router.get("/operations/statistics/after-hours", response_model=dict)
async def get_after_hours_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get after-hours access statistics"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    statistics = await service.get_after_hours_statistics(date_from, date_to)
    
    return success_response(
        message="After-hours statistics retrieved successfully",
        data=statistics
    )


@router.get("/operations/statistics/peak-hours", response_model=dict)
async def get_peak_hours_analysis(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get peak hours analysis with staffing recommendations"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    analysis = await service.get_peak_hours_analysis(date_from, date_to)
    
    return success_response(
        message="Peak hours analysis retrieved successfully",
        data=analysis
    )


@router.put("/operations/hours/update", response_model=dict)
async def update_operating_hours(
    weekday_start: Optional[time] = Query(None),
    weekday_end: Optional[time] = Query(None),
    saturday_start: Optional[time] = Query(None),
    saturday_end: Optional[time] = Query(None),
    lunch_start: Optional[time] = Query(None),
    lunch_end: Optional[time] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update operating hours configuration"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    config = await service.update_operating_hours_config(
        weekday_start=weekday_start,
        weekday_end=weekday_end,
        saturday_start=saturday_start,
        saturday_end=saturday_end,
        lunch_start=lunch_start,
        lunch_end=lunch_end
    )
    
    return success_response(
        message="Operating hours updated successfully",
        data=config
    )


@router.get("/operations/holidays", response_model=dict)
async def get_holiday_calendar(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get holiday calendar"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    holidays = await service.get_holiday_calendar(year)
    
    return success_response(
        message="Holiday calendar retrieved successfully",
        data={"holidays": holidays}
    )


@router.post("/operations/holidays", response_model=dict)
async def add_holiday(
    holiday_date: date,
    holiday_name: str,
    recurring: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add holiday to calendar"""
    service = LockerOperatingHoursService(db, tenant_id, current_user["id"])
    holiday = await service.add_holiday(
        holiday_date=holiday_date,
        holiday_name=holiday_name,
        recurring=recurring
    )
    
    return success_response(
        message="Holiday added successfully",
        data=holiday
    )


# ==================== RENT COLLECTION ENDPOINTS ====================

from .rent_collection_service import LockerRentCollectionService
from .rent_arrears_service import LockerRentArrearsService

@router.get("/rent/calculate-annual/{allocation_id}", response_model=dict)
async def calculate_annual_rent(
    allocation_id: uuid.UUID,
    for_year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate annual rent for an allocation"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    calculation = service.calculate_annual_rent(str(allocation_id), for_year)
    
    return success_response(
        message="Annual rent calculated successfully",
        data=calculation
    )


@router.post("/rent/calculate-prorata", response_model=dict)
async def calculate_prorata_rent(
    allocation_id: uuid.UUID = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate pro-rata rent for partial period"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    calculation = service.calculate_prorata_rent(str(allocation_id), from_date, to_date)
    
    return success_response(
        message="Pro-rata rent calculated successfully",
        data=calculation
    )


@router.post("/rent/calculate-advance", response_model=dict)
async def calculate_advance_rent(
    allocation_id: uuid.UUID = Query(...),
    number_of_years: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate advance rent for multiple years"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    calculation = service.calculate_advance_rent(str(allocation_id), number_of_years)
    
    return success_response(
        message="Advance rent calculated successfully",
        data=calculation
    )


@router.post("/rent/collect", response_model=dict, status_code=status.HTTP_201_CREATED)
async def collect_rent(
    allocation_id: uuid.UUID = Query(...),
    payment_data: dict = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Collect rent payment"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    payment = await service.collect_rent(str(allocation_id), payment_data)
    
    return success_response(
        message="Rent collected successfully",
        data={"payment_id": payment.id, "receipt_number": payment.receipt_number}
    )


@router.post("/rent/auto-debit/{allocation_id}", response_model=dict)
async def auto_debit_rent(
    allocation_id: uuid.UUID,
    customer_account_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Auto-debit rent from customer account"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    result = await service.auto_debit_rent(str(allocation_id), customer_account_id)
    
    return success_response(
        message="Rent auto-debited successfully",
        data=result
    )


@router.post("/rent/reminder/send", response_model=dict)
async def send_rent_reminder(
    allocation_id: uuid.UUID = Query(...),
    reminder_type: str = Query(...),
    days_before_due: int = Query(..., ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send rent payment reminder"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    result = await service.send_rent_reminder(str(allocation_id), reminder_type, days_before_due)
    
    return success_response(
        message="Reminder sent successfully",
        data=result
    )


@router.post("/rent/reminder/bulk-send", response_model=dict)
async def send_bulk_reminders(
    reminder_type: str = Query(...),
    days_before_due: int = Query(..., ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send reminders to all allocations with rent due"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    result = await service.send_bulk_reminders(reminder_type, days_before_due)
    
    return success_response(
        message=f"Bulk reminders sent: {result['sent_count']} successful, {result['failed_count']} failed",
        data=result
    )


@router.get("/rent/receipt/{payment_id}", response_model=dict)
async def generate_rent_receipt(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Generate rent receipt"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    receipt = service.generate_rent_receipt(str(payment_id))
    
    return success_response(
        message="Receipt generated successfully",
        data=receipt
    )


@router.get("/rent/overdue", response_model=dict)
async def get_overdue_allocations(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get allocations with overdue rent"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    overdue = service.get_overdue_allocations(str(branch_id) if branch_id else None)
    
    return success_response(
        message=f"Found {len(overdue)} overdue allocations",
        data={"overdue_allocations": overdue}
    )


@router.get("/rent/collection-summary", response_model=dict)
async def get_rent_collection_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get rent collection summary"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    summary = service.get_rent_collection_summary(
        start_date, 
        end_date, 
        str(branch_id) if branch_id else None
    )
    
    return success_response(
        message="Collection summary retrieved successfully",
        data=summary
    )


@router.get("/rent/upcoming-due", response_model=dict)
async def get_upcoming_due_dates(
    days_ahead: int = Query(30, ge=1, le=365),
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get allocations with rent due in upcoming days"""
    service = LockerRentCollectionService(db, tenant_id, current_user["id"])
    upcoming = await service.get_upcoming_due_dates(
        days_ahead, 
        str(branch_id) if branch_id else None
    )
    
    return success_response(
        message=f"Found {len(upcoming)} allocations with rent due",
        data={"upcoming_due": upcoming}
    )


# ==================== RENT ARREARS ENDPOINTS ====================

@router.post("/arrears/calculate-penalty", response_model=dict)
async def calculate_penalty(
    allocation_id: uuid.UUID = Query(...),
    overdue_days: int = Query(..., ge=0),
    overdue_amount: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate penalty for overdue rent"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    penalty = service.calculate_penalty(str(allocation_id), overdue_days, Decimal(str(overdue_amount)))
    
    return success_response(
        message="Penalty calculated successfully",
        data=penalty
    )


@router.get("/arrears/{allocation_id}", response_model=dict)
async def get_allocation_arrears(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get arrears details for an allocation"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    arrears = service.get_allocation_arrears(str(allocation_id))
    
    return success_response(
        message="Arrears details retrieved successfully",
        data=arrears
    )


@router.post("/arrears/send-notification", response_model=dict)
async def send_overdue_notification(
    allocation_id: uuid.UUID = Query(...),
    notification_type: str = Query("first_reminder"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send overdue rent notification"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    result = await service.send_overdue_notification(str(allocation_id), notification_type)
    
    return success_response(
        message="Notification sent successfully",
        data=result
    )


@router.post("/arrears/send-final-notice/{allocation_id}", response_model=dict)
async def send_final_notice(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send final notice before locker breaking"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    result = await service.send_final_notice(str(allocation_id))
    
    return success_response(
        message="Final notice sent successfully",
        data=result
    )


@router.post("/arrears/send-legal-notice/{allocation_id}", response_model=dict)
async def send_legal_notice(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send legal notice for long-term non-payment"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    result = await service.send_legal_notice(str(allocation_id))
    
    return success_response(
        message="Legal notice sent successfully",
        data=result
    )


@router.get("/arrears/breaking-eligibility/{allocation_id}", response_model=dict)
async def check_breaking_eligibility(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check if locker is eligible for breaking"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    eligibility = service.check_breaking_eligibility(str(allocation_id))
    
    return success_response(
        message="Eligibility checked successfully",
        data=eligibility
    )


@router.post("/arrears/initiate-breaking", response_model=dict)
async def initiate_breaking_procedure(
    allocation_id: uuid.UUID = Query(...),
    authorized_by: str = Query(...),
    witnesses: List[str] = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Initiate locker breaking procedure"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    result = await service.initiate_breaking_procedure(
        str(allocation_id), 
        authorized_by, 
        witnesses
    )
    
    return success_response(
        message="Breaking procedure initiated successfully",
        data=result
    )


@router.get("/arrears/summary", response_model=dict)
async def get_arrears_summary(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get arrears summary and statistics"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    summary = service.get_arrears_summary(str(branch_id) if branch_id else None)
    
    return success_response(
        message="Arrears summary retrieved successfully",
        data=summary
    )


@router.get("/arrears/breaking-eligible", response_model=dict)
async def get_breaking_eligible_lockers(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get lockers eligible for breaking"""
    service = LockerRentArrearsService(db, tenant_id, current_user["id"])
    eligible = service.get_breaking_eligible_lockers(str(branch_id) if branch_id else None)
    
    return success_response(
        message=f"Found {len(eligible)} lockers eligible for breaking",
        data={"breaking_eligible": eligible}
    )


# ==================== LOCKER BREAKING ENDPOINTS ====================

from .breaking_service import LockerBreakingService
from .schemas import (
    BreakingAuthorizationCheck, BreakingInitiateRequest, BreakingRecordVideographyRequest,
    BreakingInventoryRequest, BreakingValuationRequest, BreakingStorageRequest,
    BreakingChargesRequest, BreakingCompleteRequest, BreakingRecordResponse
)

@router.get("/breaking/{allocation_id}/check-authorization", response_model=dict)
async def check_breaking_authorization(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check if allocation is authorized for locker breaking"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    authorization = await service.check_breaking_authorization(allocation_id)
    
    return success_response(
        message="Authorization check completed",
        data=authorization
    )


@router.post("/breaking/initiate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def initiate_locker_breaking(
    breaking_data: BreakingInitiateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Initiate locker breaking procedure"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.initiate_breaking(breaking_data)
    
    return success_response(
        message="Locker breaking initiated successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.post("/breaking/{breaking_id}/videography", response_model=dict)
async def record_breaking_videography(
    breaking_id: uuid.UUID,
    video_data: BreakingRecordVideographyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Record videography details for breaking process"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.record_videography(breaking_id, video_data)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Videography recorded successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.post("/breaking/{breaking_id}/inventory", response_model=dict)
async def prepare_breaking_inventory(
    breaking_id: uuid.UUID,
    inventory_data: BreakingInventoryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Prepare item-wise inventory of locker contents"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.prepare_inventory(breaking_id, inventory_data)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Inventory prepared successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.post("/breaking/{breaking_id}/valuation", response_model=dict)
async def conduct_breaking_valuation(
    breaking_id: uuid.UUID,
    valuation_data: BreakingValuationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Conduct valuation of high-value contents"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.conduct_valuation(breaking_id, valuation_data)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Valuation conducted successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.post("/breaking/{breaking_id}/storage", response_model=dict)
async def store_breaking_contents(
    breaking_id: uuid.UUID,
    storage_data: BreakingStorageRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Store locker contents in bank custody"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.store_contents(breaking_id, storage_data)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Contents stored successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.post("/breaking/{breaking_id}/calculate-charges", response_model=dict)
async def calculate_breaking_charges(
    breaking_id: uuid.UUID,
    charges_data: BreakingChargesRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate breaking charges with GST"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.calculate_breaking_charges(breaking_id, charges_data)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Breaking charges calculated successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.post("/breaking/{breaking_id}/complete", response_model=dict)
async def complete_locker_breaking(
    breaking_id: uuid.UUID,
    completion_data: BreakingCompleteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Complete locker breaking procedure"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.complete_breaking(breaking_id, completion_data)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Locker breaking completed successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.get("/breaking/{breaking_id}", response_model=dict)
async def get_breaking_record(
    breaking_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get breaking record by ID"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.get_breaking_record(breaking_id)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Breaking record retrieved successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.get("/breaking/allocation/{allocation_id}", response_model=dict)
async def get_breaking_by_allocation(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get breaking record for allocation"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    breaking = await service.get_breaking_by_allocation(allocation_id)
    
    if not breaking:
        return success_response(message="Breaking record not found", data=None, status_code=404)
    
    return success_response(
        message="Breaking record retrieved successfully",
        data=BreakingRecordResponse.from_orm(breaking).dict()
    )


@router.get("/breaking/records", response_model=dict)
async def list_breaking_records(
    branch_id: Optional[uuid.UUID] = Query(None),
    reason: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List breaking records with filters"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    result = await service.list_breaking_records(
        branch_id=branch_id,
        reason=reason,
        status=status,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(result['records'])} breaking records",
        data=result
    )


@router.get("/breaking/statistics", response_model=dict)
async def get_breaking_statistics(
    branch_id: Optional[uuid.UUID] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get locker breaking statistics"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    statistics = await service.get_breaking_statistics(branch_id, year)
    
    return success_response(
        message="Breaking statistics retrieved successfully",
        data=statistics
    )


@router.get("/breaking/pending-action", response_model=dict)
async def get_breaking_pending_action(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get breaking records pending action"""
    service = LockerBreakingService(db, tenant_id, current_user["id"])
    records = await service.get_breaking_pending_action(branch_id)
    
    return success_response(
        message=f"Found {len(records)} breaking records pending action",
        data={"pending_records": [BreakingRecordResponse.from_orm(r).dict() for r in records]}
    )


# ==================== VOLUNTARY SURRENDER ENDPOINTS ====================

from .surrender_service import LockerSurrenderService
from .schemas import (
    SurrenderApplicationRequest, SurrenderApprovalRequest, SurrenderDuesClearanceRequest,
    SurrenderKeyReturnRequest, SurrenderInspectionRequest, SurrenderRefundRequest,
    SurrenderCertificateRequest, SurrenderCompleteRequest, SurrenderRecordResponse
)

@router.get("/surrender/{allocation_id}/check-eligibility", response_model=dict)
async def check_surrender_eligibility(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check if allocation is eligible for voluntary surrender"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    eligibility = await service.check_surrender_eligibility(allocation_id)
    
    return success_response(
        message="Eligibility check completed",
        data=eligibility
    )


@router.post("/surrender/submit-application", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_surrender_application(
    application_data: SurrenderApplicationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Submit voluntary surrender application"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.submit_surrender_application(application_data)
    
    return success_response(
        message="Surrender application submitted successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/approve", response_model=dict)
async def approve_surrender_application(
    surrender_id: uuid.UUID,
    approval_data: SurrenderApprovalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve or reject surrender application"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.approve_application(surrender_id, approval_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message=f"Surrender application {approval_data.approved and 'approved' or 'rejected'} successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/clear-dues", response_model=dict)
async def clear_surrender_dues(
    surrender_id: uuid.UUID,
    dues_data: SurrenderDuesClearanceRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Clear all outstanding dues for surrender"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.clear_dues(surrender_id, dues_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Dues cleared successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/return-keys", response_model=dict)
async def return_surrender_keys(
    surrender_id: uuid.UUID,
    keys_data: SurrenderKeyReturnRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Return customer and bank keys for surrender"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.return_keys(surrender_id, keys_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Keys returned successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/inspection", response_model=dict)
async def conduct_surrender_inspection(
    surrender_id: uuid.UUID,
    inspection_data: SurrenderInspectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Conduct locker inspection for damage assessment"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.conduct_inspection(surrender_id, inspection_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Inspection conducted successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/process-refund", response_model=dict)
async def process_surrender_refund(
    surrender_id: uuid.UUID,
    refund_data: SurrenderRefundRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Process security deposit refund"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.process_refund(surrender_id, refund_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Refund processed successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/issue-certificate", response_model=dict)
async def issue_closure_certificate(
    surrender_id: uuid.UUID,
    certificate_data: SurrenderCertificateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Issue closure certificate"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.issue_closure_certificate(surrender_id, certificate_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Closure certificate issued successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/complete", response_model=dict)
async def complete_surrender(
    surrender_id: uuid.UUID,
    completion_data: SurrenderCompleteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Complete surrender process"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.complete_surrender(surrender_id, completion_data)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Surrender completed successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.post("/surrender/{surrender_id}/calculate-settlement", response_model=dict)
async def calculate_final_settlement(
    surrender_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Calculate final settlement amount"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    settlement = await service.calculate_final_settlement(surrender_id)
    
    return success_response(
        message="Final settlement calculated successfully",
        data=settlement
    )


@router.get("/surrender/{surrender_id}", response_model=dict)
async def get_surrender_record(
    surrender_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get surrender record by ID"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.get_surrender_record(surrender_id)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Surrender record retrieved successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.get("/surrender/allocation/{allocation_id}", response_model=dict)
async def get_surrender_by_allocation(
    allocation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get surrender record for allocation"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    surrender = await service.get_surrender_by_allocation(allocation_id)
    
    if not surrender:
        return success_response(message="Surrender record not found", data=None, status_code=404)
    
    return success_response(
        message="Surrender record retrieved successfully",
        data=SurrenderRecordResponse.from_orm(surrender).dict()
    )


@router.get("/surrender/records", response_model=dict)
async def list_surrender_records(
    branch_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    reason: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List surrender records with filters"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    result = await service.list_surrender_records(
        branch_id=branch_id,
        status=status,
        reason=reason,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(result['records'])} surrender records",
        data=result
    )


@router.get("/surrender/statistics", response_model=dict)
async def get_surrender_statistics(
    branch_id: Optional[uuid.UUID] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get surrender statistics"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    statistics = await service.get_surrender_statistics(branch_id, year)
    
    return success_response(
        message="Surrender statistics retrieved successfully",
        data=statistics
    )


@router.get("/surrender/pending-approval", response_model=dict)
async def get_surrender_pending_approval(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get surrender applications pending approval"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    records = await service.get_pending_approvals(branch_id)
    
    return success_response(
        message=f"Found {len(records)} surrender applications pending approval",
        data={"pending_approvals": [SurrenderRecordResponse.from_orm(r).dict() for r in records]}
    )


@router.get("/surrender/in-progress", response_model=dict)
async def get_surrender_in_progress(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get surrender processes in progress"""
    service = LockerSurrenderService(db, tenant_id, current_user["id"])
    records = await service.get_in_progress(branch_id)
    
    return success_response(
        message=f"Found {len(records)} surrender processes in progress",
        data={"in_progress": [SurrenderRecordResponse.from_orm(r).dict() for r in records]}
    )


# ==================== LOCKER MAINTENANCE ENDPOINTS ====================

from .maintenance_service import LockerMaintenanceService
from .schemas import (
    MaintenanceScheduleRequest, MaintenanceReportRequest, MaintenanceLockServicingRequest,
    MaintenanceKeyDuplicationRequest, MaintenanceCleaningRequest, MaintenanceVaultRequest,
    MaintenanceFireCheckRequest, MaintenanceResolveJammingRequest, MaintenanceHandleLostKeyRequest,
    MaintenanceReplaceLockRequest, MaintenanceRegenerateMasterKeyRequest, MaintenanceRepairRequest,
    MaintenanceCompleteRequest, MaintenanceRecordResponse, MaintenanceStatistics
)

@router.post("/maintenance/schedule", response_model=dict, status_code=status.HTTP_201_CREATED)
async def schedule_preventive_maintenance(
    schedule_data: MaintenanceScheduleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Schedule preventive maintenance for locker"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.schedule_preventive_maintenance(schedule_data)
    
    return success_response(
        message="Preventive maintenance scheduled successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/report-breakdown", response_model=dict, status_code=status.HTTP_201_CREATED)
async def report_breakdown_maintenance(
    breakdown_data: MaintenanceReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Report breakdown maintenance issue"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.report_breakdown(breakdown_data)
    
    return success_response(
        message="Breakdown reported successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/lock-servicing", response_model=dict)
async def perform_lock_servicing(
    maintenance_id: uuid.UUID,
    servicing_data: MaintenanceLockServicingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Perform lock servicing maintenance"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.perform_lock_servicing(maintenance_id, servicing_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Lock servicing completed successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/key-duplication", response_model=dict)
async def perform_key_duplication(
    maintenance_id: uuid.UUID,
    duplication_data: MaintenanceKeyDuplicationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Perform key duplication maintenance"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.perform_key_duplication(maintenance_id, duplication_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Key duplication completed successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/cleaning", response_model=dict)
async def perform_locker_cleaning(
    maintenance_id: uuid.UUID,
    cleaning_data: MaintenanceCleaningRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Perform locker cleaning maintenance"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.perform_locker_cleaning(maintenance_id, cleaning_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Locker cleaning completed successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/vault-maintenance", response_model=dict)
async def perform_vault_maintenance(
    maintenance_id: uuid.UUID,
    vault_data: MaintenanceVaultRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Perform vault room maintenance"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.perform_vault_maintenance(maintenance_id, vault_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Vault maintenance completed successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/fire-check", response_model=dict)
async def check_fire_protection_system(
    maintenance_id: uuid.UUID,
    fire_check_data: MaintenanceFireCheckRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Check fire protection system"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.check_fire_protection_system(maintenance_id, fire_check_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Fire protection system checked successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/resolve-jamming", response_model=dict)
async def resolve_lock_jamming(
    maintenance_id: uuid.UUID,
    jamming_data: MaintenanceResolveJammingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Resolve lock jamming breakdown"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.resolve_lock_jamming(maintenance_id, jamming_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Lock jamming resolved successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/handle-lost-key", response_model=dict)
async def handle_lost_key(
    maintenance_id: uuid.UUID,
    lost_key_data: MaintenanceHandleLostKeyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Handle lost key breakdown"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.handle_lost_key(maintenance_id, lost_key_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Lost key handled successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/replace-lock", response_model=dict)
async def replace_lock(
    maintenance_id: uuid.UUID,
    lock_data: MaintenanceReplaceLockRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Replace locker lock"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.replace_lock(maintenance_id, lock_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Lock replaced successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/regenerate-master-key", response_model=dict)
async def regenerate_master_key(
    maintenance_id: uuid.UUID,
    master_key_data: MaintenanceRegenerateMasterKeyRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Regenerate master key for vault"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.regenerate_master_key(maintenance_id, master_key_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Master key regenerated successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/repair", response_model=dict)
async def repair_locker(
    maintenance_id: uuid.UUID,
    repair_data: MaintenanceRepairRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Repair locker damage"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.repair_locker(maintenance_id, repair_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Locker repair completed successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.post("/maintenance/{maintenance_id}/complete", response_model=dict)
async def complete_maintenance(
    maintenance_id: uuid.UUID,
    completion_data: MaintenanceCompleteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Complete maintenance with quality check and satisfaction"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.complete_maintenance(maintenance_id, completion_data)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Maintenance completed successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.get("/maintenance/{maintenance_id}", response_model=dict)
async def get_maintenance_record(
    maintenance_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get maintenance record by ID"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance = await service.get_maintenance_record(maintenance_id)
    
    if not maintenance:
        return success_response(message="Maintenance record not found", data=None, status_code=404)
    
    return success_response(
        message="Maintenance record retrieved successfully",
        data=MaintenanceRecordResponse.from_orm(maintenance).dict()
    )


@router.get("/maintenance/locker/{locker_id}", response_model=dict)
async def get_maintenance_by_locker(
    locker_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get maintenance records for a locker"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    maintenance_records = await service.get_maintenance_by_locker(locker_id)
    
    return success_response(
        message=f"Retrieved {len(maintenance_records)} maintenance records",
        data={"maintenance_records": [MaintenanceRecordResponse.from_orm(m).dict() for m in maintenance_records]}
    )


@router.get("/maintenance/records", response_model=dict)
async def list_maintenance_records(
    locker_id: Optional[uuid.UUID] = Query(None),
    maintenance_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    scheduled_date_from: Optional[date] = Query(None),
    scheduled_date_to: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List maintenance records with filters"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    result = await service.list_maintenance_records(
        locker_id=locker_id,
        maintenance_type=maintenance_type,
        status=status,
        priority=priority,
        scheduled_date_from=scheduled_date_from,
        scheduled_date_to=scheduled_date_to,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(result['records'])} maintenance records",
        data=result
    )


@router.get("/maintenance/upcoming", response_model=dict)
async def get_upcoming_maintenance(
    days_ahead: int = Query(30, ge=1, le=365),
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get upcoming maintenance schedule"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    upcoming = await service.get_upcoming_maintenance(days_ahead, branch_id)
    
    return success_response(
        message=f"Found {len(upcoming)} upcoming maintenance tasks",
        data={"upcoming_maintenance": [MaintenanceRecordResponse.from_orm(m).dict() for m in upcoming]}
    )


@router.get("/maintenance/overdue", response_model=dict)
async def get_overdue_maintenance(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get overdue maintenance tasks"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    overdue = await service.get_overdue_maintenance(branch_id)
    
    return success_response(
        message=f"Found {len(overdue)} overdue maintenance tasks",
        data={"overdue_maintenance": [MaintenanceRecordResponse.from_orm(m).dict() for m in overdue]}
    )


@router.get("/maintenance/breakdowns", response_model=dict)
async def get_pending_breakdowns(
    branch_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get pending breakdown maintenance tasks"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    breakdowns = await service.get_pending_breakdowns(branch_id)
    
    return success_response(
        message=f"Found {len(breakdowns)} pending breakdown tasks",
        data={"pending_breakdowns": [MaintenanceRecordResponse.from_orm(m).dict() for m in breakdowns]}
    )


@router.get("/maintenance/statistics", response_model=dict)
async def get_maintenance_statistics(
    branch_id: Optional[uuid.UUID] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get maintenance statistics and analytics"""
    service = LockerMaintenanceService(db, tenant_id, current_user["id"])
    statistics = await service.get_maintenance_statistics(branch_id, year)
    
    return success_response(
        message="Maintenance statistics retrieved successfully",
        data=statistics.dict()
    )
