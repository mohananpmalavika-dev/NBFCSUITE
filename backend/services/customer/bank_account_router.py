"""
Customer Bank Account API Router
FastAPI routes for bank account operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal

from backend.core.database import get_db
from backend.core.security import get_current_user
from .bank_account_service import CustomerBankAccountService
from .schemas import (
    CustomerBankAccountCreate, CustomerBankAccountUpdate,
    CustomerBankAccountResponse
)

router = APIRouter(prefix="/customers/{customer_id}/accounts", tags=["Customer Bank Accounts"])


def get_account_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
) -> CustomerBankAccountService:
    """Dependency to get bank account service"""
    return CustomerBankAccountService(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )


@router.post("", response_model=CustomerBankAccountResponse, status_code=status.HTTP_201_CREATED)
async def add_bank_account(
    customer_id: int,
    data: CustomerBankAccountCreate,
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Add bank account to customer
    
    - Validates IFSC code format (11 characters)
    - Auto-unsets other primary accounts if this is primary
    - Checks for duplicate account numbers
    """
    # Ensure customer_id matches
    data.customer_id = customer_id
    
    try:
        account = await service.create_bank_account(data)
        return account
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[CustomerBankAccountResponse])
async def get_bank_accounts(
    customer_id: int,
    is_primary: Optional[bool] = Query(None, description="Filter by primary status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Get all bank accounts for a customer
    
    Optional filters:
    - is_primary: Show only primary account
    - is_active: Show only active accounts
    
    Sorted by: Primary first, then by creation date
    """
    accounts = await service.get_customer_accounts(
        customer_id=customer_id,
        is_primary=is_primary,
        is_active=is_active
    )
    return accounts


@router.get("/primary", response_model=CustomerBankAccountResponse)
async def get_primary_account(
    customer_id: int,
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Get primary bank account for customer
    
    Used for loan disbursement and collections
    """
    account = await service.get_primary_account(customer_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No primary account found for this customer"
        )
    return account


@router.get("/{account_id}", response_model=CustomerBankAccountResponse)
async def get_bank_account(
    customer_id: int,
    account_id: int,
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """Get bank account by ID"""
    account = await service.get_bank_account(account_id)
    if not account or account.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank account with ID {account_id} not found"
        )
    return account


@router.put("/{account_id}", response_model=CustomerBankAccountResponse)
async def update_bank_account(
    customer_id: int,
    account_id: int,
    data: CustomerBankAccountUpdate,
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Update bank account details
    
    - All fields optional
    - Auto-handles primary account switching
    """
    try:
        account = await service.update_bank_account(account_id, data)
        if not account or account.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank account with ID {account_id} not found"
            )
        return account
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{account_id}/set-primary", response_model=CustomerBankAccountResponse)
async def set_primary_account(
    customer_id: int,
    account_id: int,
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Set account as primary
    
    - Automatically unsets other primary accounts
    - Used to change default account for transactions
    """
    account = await service.set_primary_account(account_id)
    if not account or account.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank account with ID {account_id} not found"
        )
    return account


@router.post("/{account_id}/verify", response_model=CustomerBankAccountResponse)
async def verify_account(
    customer_id: int,
    account_id: int,
    verification_method: str = Query(..., description="Method: penny_drop, statement, passbook"),
    remarks: Optional[str] = Query(None, description="Verification notes"),
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Verify bank account
    
    Methods:
    - penny_drop: Small amount deposited and verified
    - statement: Bank statement verified
    - passbook: Physical passbook verified
    """
    account = await service.verify_account(account_id, verification_method, remarks)
    if not account or account.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank account with ID {account_id} not found"
        )
    return account


@router.post("/{account_id}/penny-drop", response_model=CustomerBankAccountResponse)
async def penny_drop_verification(
    customer_id: int,
    account_id: int,
    amount: Decimal = Query(..., description="Amount deposited (e.g., 1.00)"),
    reference: str = Query(..., description="Transaction reference"),
    status: str = Query(..., description="Status: success or failed"),
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Record penny drop verification attempt
    
    - Deposits small amount (₹1) to verify account
    - If successful, marks account as verified
    - Records transaction reference
    """
    account = await service.penny_drop_verification(
        account_id=account_id,
        amount=float(amount),
        reference=reference,
        status=status
    )
    if not account or account.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank account with ID {account_id} not found"
        )
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bank_account(
    customer_id: int,
    account_id: int,
    service: CustomerBankAccountService = Depends(get_account_service)
):
    """
    Soft delete bank account
    
    - Cannot delete primary account if other accounts exist
    - Set another account as primary first
    """
    try:
        success = await service.delete_bank_account(account_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank account with ID {account_id} not found"
            )
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
