"""
Treasury Bank Account Router
API endpoints for bank account management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.treasury_models import (
    BankAccountStatus,
    BankAccountType,
    BankAccountPurpose
)
from . import bank_account_service as service
from . import bank_account_schemas as schemas

router = APIRouter(prefix="/bank-accounts", tags=["Treasury - Bank Accounts"])


@router.post("/", response_model=schemas.TreasuryBankAccountResponse, status_code=201)
def create_bank_account(
    data: schemas.TreasuryBankAccountCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new treasury bank account
    
    Creates a new bank account in the treasury system with all required details.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.create_bank_account(data)


@router.get("/{account_id}", response_model=schemas.TreasuryBankAccountResponse)
def get_bank_account(
    account_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get bank account by ID
    
    Retrieves detailed information about a specific bank account.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.get_bank_account(account_id)


@router.get("/", response_model=schemas.TreasuryBankAccountListResponse)
def list_bank_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    status: Optional[BankAccountStatus] = Query(None, description="Filter by account status"),
    account_type: Optional[BankAccountType] = Query(None, description="Filter by account type"),
    account_purpose: Optional[BankAccountPurpose] = Query(None, description="Filter by account purpose"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    search: Optional[str] = Query(None, description="Search in account number, name, or bank name"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all bank accounts with filters
    
    Returns paginated list of bank accounts with optional filtering.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.list_bank_accounts(
        skip=skip,
        limit=limit,
        status=status,
        account_type=account_type,
        account_purpose=account_purpose,
        branch_id=branch_id,
        search=search
    )


@router.patch("/{account_id}", response_model=schemas.TreasuryBankAccountResponse)
def update_bank_account(
    account_id: int,
    data: schemas.TreasuryBankAccountUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update bank account details
    
    Updates specified fields of a bank account. Only provided fields will be updated.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.update_bank_account(account_id, data)


@router.delete("/{account_id}")
def delete_bank_account(
    account_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete bank account (soft delete)
    
    Marks account as deleted. Account must have zero balance to be deleted.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.delete_bank_account(account_id)


@router.get("/active/list", response_model=List[schemas.TreasuryBankAccountResponse])
def get_active_accounts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active bank accounts
    
    Returns list of all active bank accounts without pagination.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.get_active_accounts()


@router.get("/{account_id}/balance", response_model=schemas.BankAccountBalanceResponse)
def get_account_balance(
    account_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current balance of bank account
    
    Returns current balance, available balance, and minimum balance information.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.get_account_balance(account_id)


@router.post("/{account_id}/update-balance", response_model=schemas.BankAccountBalanceResponse)
def update_account_balance(
    account_id: int,
    data: schemas.BankAccountBalanceUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update bank account balance
    
    Updates the current balance of a bank account. Optionally creates journal entry.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.update_account_balance(account_id, data)


@router.get("/branch/{branch_id}/accounts", response_model=List[schemas.TreasuryBankAccountResponse])
def get_accounts_by_branch(
    branch_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all accounts for a specific branch
    
    Returns all bank accounts associated with the specified branch.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.get_accounts_by_branch(branch_id)


@router.get("/statistics/summary", response_model=schemas.BankAccountStatistics)
def get_bank_account_statistics(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get bank account statistics
    
    Returns comprehensive statistics including:
    - Total, active, and inactive accounts
    - Total balance across all accounts
    - Accounts below minimum balance
    - Distribution by type and purpose
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.get_statistics()


@router.post("/bulk/create", response_model=schemas.BankAccountBulkCreateResponse)
def bulk_create_accounts(
    data: schemas.BankAccountBulkCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk create bank accounts
    
    Creates multiple bank accounts in a single request.
    Returns summary of created and failed accounts.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.bulk_create_accounts(data)


@router.get("/{account_id}/history", response_model=List[dict])
def get_account_history(
    account_id: int,
    start_date: Optional[date] = Query(None, description="Start date for history"),
    end_date: Optional[date] = Query(None, description="End date for history"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get account balance history
    
    Returns historical balance data for the specified account and date range.
    """
    svc = service.BankAccountService(db, current_user.tenant_id, current_user.id)
    return svc.get_account_history(account_id, start_date, end_date)
