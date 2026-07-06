"""
Purity Testing Router
API endpoints for purity testing
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.gold.purity_service import PurityService
from backend.services.gold.schemas import (
    PurityTestCreateRequest,
    PurityTestUpdateRequest,
    PurityTestResponse
)

router = APIRouter(prefix="/purity-tests", tags=["Purity Testing"])


@router.post("/", response_model=PurityTestResponse)
async def create_purity_test(
    test_data: PurityTestCreateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Create new purity test"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    test = service.create_purity_test(test_data)
    return PurityTestResponse.from_orm(test)


@router.put("/{test_id}", response_model=PurityTestResponse)
async def update_purity_test(
    test_id: str,
    test_data: PurityTestUpdateRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Update purity test details"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    test = service.update_purity_test(test_id, test_data)
    return PurityTestResponse.from_orm(test)


@router.get("/{test_id}", response_model=PurityTestResponse)
async def get_purity_test(
    test_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get purity test by ID"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    test = service.get_purity_test(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Purity test not found")
    
    return PurityTestResponse.from_orm(test)


@router.get("/", response_model=List[PurityTestResponse])
async def list_purity_tests(
    loan_id: Optional[str] = Query(None),
    ornament_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    test_method: Optional[str] = Query(None),
    test_result: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """List purity tests with filters"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    tests = service.list_purity_tests(
        loan_id, ornament_id, customer_id, test_method, test_result, start_date, end_date
    )
    return [PurityTestResponse.from_orm(test) for test in tests]


@router.post("/{test_id}/certificate", response_model=PurityTestResponse)
async def generate_test_certificate(
    test_id: str,
    certificate_number: Optional[str] = Query(None),
    valid_days: int = Query(default=365, ge=1),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Generate purity test certificate"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    test = service.generate_test_certificate(test_id, certificate_number, valid_days)
    return PurityTestResponse.from_orm(test)


@router.post("/bulk-test/{loan_id}", response_model=List[PurityTestResponse])
async def perform_bulk_testing(
    loan_id: str,
    test_method: str = Query(..., description="Testing method"),
    tester_name: str = Query(..., description="Tester name"),
    equipment_id: Optional[str] = Query(None),
    equipment_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Perform purity testing for all ornaments in a loan"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    tests = service.perform_bulk_testing(loan_id, test_method, tester_name, equipment_id, equipment_name)
    return [PurityTestResponse.from_orm(test) for test in tests]


@router.get("/statistics/summary")
async def get_test_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    test_method: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Get purity test statistics"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    return service.get_test_statistics(start_date, end_date, test_method)


@router.get("/equipment/{equipment_id}/calibration")
async def verify_equipment_calibration(
    equipment_id: str,
    calibration_date: datetime = Query(...),
    valid_days: int = Query(default=180, ge=1),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Verify equipment calibration status"""
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    return service.verify_equipment_calibration(equipment_id, calibration_date, valid_days)


@router.post("/{test_id}/discrepancy", response_model=PurityTestResponse)
async def flag_discrepancy(
    test_id: str,
    action_taken: str = Query(..., description="Action taken"),
    adjusted_value: Optional[float] = Query(None),
    remarks: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user)
):
    """Flag and handle purity test discrepancy"""
    from decimal import Decimal
    service = PurityService(db, tenant_id, current_user.get("user_id"))
    adjusted_val = Decimal(str(adjusted_value)) if adjusted_value else None
    test = service.flag_discrepancy(test_id, action_taken, adjusted_val, remarks)
    return PurityTestResponse.from_orm(test)
