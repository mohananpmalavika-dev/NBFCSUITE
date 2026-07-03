"""
Deposit Account Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from ..database import get_db
from ..schemas import (
    DepositAccountCreate, DepositAccountResponse,
    DepositAccountSearch, RDAccountCreate
)
from ..services import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/fd", status_code=201)
async def open_fd_account(
    request: DepositAccountCreate,
    db: Session = Depends(get_db)
):
    """Open Fixed Deposit account"""
    try:
        service = AccountService(db)
        result = await service.open_fd_account(
            customer_id=request.customer_id,
            cif_number=request.cif_number,
            product_id=request.product_id,
            principal_amount=request.principal_amount,
            tenure_days=request.tenure_days,
            is_senior_citizen=request.is_senior_citizen,
            nominees=[n.dict() for n in request.nominees] if request.nominees else None,
            branch_code=request.branch_code
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rd", status_code=201)
async def open_rd_account(
    request: RDAccountCreate,
    db: Session = Depends(get_db)
):
    """Open Recurring Deposit account"""
    try:
        service = AccountService(db)
        result = await service.open_rd_account(
            customer_id=request.customer_id,
            cif_number=request.cif_number,
            product_id=request.product_id,
            installment_amount=request.installment_amount,
            num_installments=request.num_installments,
            is_senior_citizen=request.is_senior_citizen,
            nominees=[n.dict() for n in request.nominees] if request.nominees else None,
            branch_code=request.branch_code
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{account_id}/approve")
def approve_account(
    account_id: str,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Approve deposit account"""
    try:
        service = AccountService(db)
        return service.approve_account(account_id, approved_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{account_id}")
def get_account(
    account_id: str,
    db: Session = Depends(get_db)
):
    """Get account details"""
    try:
        service = AccountService(db)
        return service.get_account_details(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/search")
def search_accounts(
    search: DepositAccountSearch,
    db: Session = Depends(get_db)
):
    """Search deposit accounts"""
    service = AccountService(db)
    return service.search_accounts(
        customer_id=search.customer_id,
        cif_number=search.cif_number,
        status=search.status,
        branch_code=search.branch_code
    )


@router.get("/customer/{customer_id}")
def get_customer_accounts(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get all accounts for a customer"""
    service = AccountService(db)
    return service.search_accounts(customer_id=customer_id)
