"""
Deposit Account Router

API endpoints for deposit account management including:
- Account opening
- Deposits and withdrawals
- RD installments
- Account closure
- Passbook and statements
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .account_service import DepositAccountService
from .schemas import (
    DepositAccountCreate,
    DepositAccountUpdate,
    DepositAccountResponse,
    AccountSummaryResponse,
    DepositRequest,
    WithdrawalRequest,
    RDInstallmentRequest,
    TransactionResponse,
    TransactionListResponse,
    PrematureClosureRequest,
    ClosureResponse,
    DepositType,
    AccountStatus
)

router = APIRouter(prefix="/deposit-accounts", tags=["Deposit Accounts"])


# ==================== ACCOUNT MANAGEMENT ====================

@router.post("", response_model=dict, status_code=201)
def open_account(
    account_data: DepositAccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Open new deposit account
    
    Steps:
    1. Validates customer and product
    2. Checks eligibility (amount, tenure)
    3. Generates account number (DEP-YYYYMM-XXXX)
    4. Calculates maturity details
    5. Creates opening transaction
    6. Generates passbook entry
    
    Required fields:
    - **customer_id**: Customer ID
    - **deposit_product_id**: Product ID
    - **principal_amount**: Initial deposit amount
    - **tenure_days**: Tenure (for FD/RD/MIS)
    
    Optional:
    - **nominee details**: For nomination
    - **auto_renewal**: Enable auto-renewal
    - **linked_account_number**: For auto-debit
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.open_account(account_data.dict())
    
    return success_response(
        message="Account opened successfully",
        data=DepositAccountResponse.from_orm(account).dict()
    )


@router.get("", response_model=dict)
def list_accounts(
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    account_type: Optional[DepositType] = Query(None, description="Filter by account type"),
    status: Optional[AccountStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List deposit accounts with filters
    
    Supports filtering by:
    - Customer
    - Account type (savings, fd, rd, mis)
    - Status (active, matured, closed, etc.)
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    accounts = service.list_accounts(
        customer_id=customer_id,
        account_type=account_type,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(accounts)} accounts",
        data={
            "accounts": [DepositAccountResponse.from_orm(a).dict() for a in accounts],
            "total": len(accounts),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{account_id}", response_model=dict)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get account details by ID
    
    Returns complete account information including:
    - Account details
    - Balance information
    - Interest details
    - Maturity information
    - Nominee details
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account(account_id)
    
    return success_response(
        message="Account retrieved successfully",
        data=DepositAccountResponse.from_orm(account).dict()
    )


@router.get("/number/{account_number}", response_model=dict)
def get_account_by_number(
    account_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get account by account number
    
    Alternative lookup using account number instead of ID
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account_by_number(account_number)
    
    return success_response(
        message="Account retrieved successfully",
        data=DepositAccountResponse.from_orm(account).dict()
    )


@router.get("/customer/{customer_id}", response_model=dict)
def get_customer_accounts(
    customer_id: int,
    account_type: Optional[DepositType] = Query(None, description="Filter by account type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all accounts for a customer
    
    Convenience endpoint for customer-specific account listing
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    accounts = service.list_accounts(
        customer_id=customer_id,
        account_type=account_type,
        skip=0,
        limit=1000
    )
    
    return success_response(
        message=f"Retrieved {len(accounts)} accounts for customer",
        data={"accounts": [DepositAccountResponse.from_orm(a).dict() for a in accounts]}
    )


@router.put("/{account_id}", response_model=dict)
def update_account(
    account_id: int,
    update_data: DepositAccountUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Update account details
    
    Allows updating:
    - Nominee details
    - Auto-renewal setting
    - Linked account
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account(account_id)
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        if hasattr(account, key):
            setattr(account, key, value)
    
    account.updated_by = current_user["id"]
    
    db = service.db
    db.commit()
    db.refresh(account)
    
    return success_response(
        message="Account updated successfully",
        data=DepositAccountResponse.from_orm(account).dict()
    )


@router.get("/{account_id}/summary", response_model=dict)
def get_account_summary(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get comprehensive account summary
    
    Returns:
    - Account details
    - Balance breakdown
    - Transaction statistics
    - Product information
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    summary = service.get_account_summary(account_id)
    
    return success_response(
        message="Account summary retrieved successfully",
        data=summary
    )


# ==================== DEPOSITS & WITHDRAWALS ====================

@router.post("/deposit", response_model=dict)
def make_deposit(
    deposit_request: DepositRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Make deposit to account
    
    Only applicable for savings accounts.
    
    Creates:
    - Transaction record
    - Passbook entry
    - Updates account balance
    
    Payment modes:
    - cash, cheque, neft, rtgs, imps, upi
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    transaction = service.make_deposit(
        account_id=deposit_request.account_id,
        amount=deposit_request.amount,
        payment_mode=deposit_request.payment_mode,
        reference_number=deposit_request.reference_number,
        remarks=deposit_request.remarks
    )
    
    return success_response(
        message="Deposit successful",
        data=TransactionResponse.from_orm(transaction).dict()
    )


@router.post("/withdraw", response_model=dict)
def make_withdrawal(
    withdrawal_request: WithdrawalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Make withdrawal from account
    
    Only applicable for savings accounts.
    
    Validations:
    - Sufficient balance
    - Minimum balance check
    - Monthly withdrawal limit
    
    Charges:
    - Withdrawal charge (if applicable)
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    transaction = service.make_withdrawal(
        account_id=withdrawal_request.account_id,
        amount=withdrawal_request.amount,
        payment_mode=withdrawal_request.payment_mode,
        reference_number=withdrawal_request.reference_number,
        remarks=withdrawal_request.remarks
    )
    
    return success_response(
        message="Withdrawal successful",
        data=TransactionResponse.from_orm(transaction).dict()
    )


@router.post("/rd-installment", response_model=dict)
def pay_rd_installment(
    installment_request: RDInstallmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Pay RD installment
    
    Only applicable for recurring deposit accounts.
    
    Validations:
    - Correct installment amount
    - Not exceeded total installments
    
    Updates:
    - Installments paid count
    - Next installment date
    - Account balance
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    transaction = service.pay_rd_installment(
        account_id=installment_request.account_id,
        amount=installment_request.amount,
        payment_mode=installment_request.payment_mode,
        reference_number=installment_request.reference_number
    )
    
    return success_response(
        message="RD installment paid successfully",
        data=TransactionResponse.from_orm(transaction).dict()
    )


# ==================== ACCOUNT CLOSURE ====================

@router.post("/{account_id}/close-at-maturity", response_model=dict)
def close_at_maturity(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Close account at maturity
    
    Only for accounts that have reached maturity date.
    
    Process:
    1. Validates maturity date reached
    2. Calculates final amount
    3. Creates closure transaction
    4. Updates account status to 'matured'
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    result = service.close_account_at_maturity(account_id)
    
    return success_response(
        message="Account closed at maturity",
        data=result
    )


@router.post("/close-prematurely", response_model=dict)
def close_prematurely(
    closure_request: PrematureClosureRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Close account before maturity
    
    Only if product allows premature closure.
    
    Process:
    1. Validates premature closure allowed
    2. Calculates penalty
    3. Calculates interest at reduced rate
    4. Creates closure transactions
    5. Updates account status to 'premature_closed'
    
    Returns:
    - Days held
    - Penalty amount
    - Final closure amount
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    result = service.close_account_prematurely(
        account_id=closure_request.account_id,
        closure_reason=closure_request.closure_reason
    )
    
    return success_response(
        message="Account closed prematurely",
        data=result
    )


# ==================== TRANSACTIONS ====================

@router.get("/{account_id}/transactions", response_model=dict)
def get_account_transactions(
    account_id: int,
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get account transactions
    
    Returns transaction history with optional filters:
    - Transaction type
    - Date range
    """
    from backend.shared.database.deposit_models import DepositTransaction
    from sqlalchemy import and_
    
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account(account_id)
    
    query = db.query(DepositTransaction).filter(
        DepositTransaction.deposit_account_id == account_id
    )
    
    if transaction_type:
        query = query.filter(DepositTransaction.transaction_type == transaction_type)
    
    if from_date:
        query = query.filter(DepositTransaction.transaction_date >= from_date)
    
    if to_date:
        query = query.filter(DepositTransaction.transaction_date <= to_date)
    
    total = query.count()
    transactions = query.order_by(
        DepositTransaction.transaction_date.desc()
    ).offset(skip).limit(limit).all()
    
    return success_response(
        message=f"Retrieved {len(transactions)} transactions",
        data={
            "transactions": [TransactionResponse.from_orm(t).dict() for t in transactions],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/transaction/{transaction_id}/receipt", response_model=dict)
def get_transaction_receipt(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get transaction receipt
    
    Returns formatted receipt for printing/download
    """
    from backend.shared.database.deposit_models import DepositTransaction
    from sqlalchemy import and_
    
    transaction = db.query(DepositTransaction).filter(
        and_(
            DepositTransaction.id == transaction_id,
            DepositTransaction.tenant_id == tenant_id
        )
    ).first()
    
    if not transaction:
        return success_response(
            message="Transaction not found",
            data=None,
            status_code=404
        )
    
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account(transaction.deposit_account_id)
    
    receipt = {
        "transaction": TransactionResponse.from_orm(transaction).dict(),
        "account": {
            "account_number": account.account_number,
            "account_type": account.account_type,
            "customer_id": account.customer_id
        },
        "receipt_date": date.today().isoformat(),
        "generated_by": current_user["email"]
    }
    
    return success_response(
        message="Receipt generated successfully",
        data=receipt
    )


# ==================== PASSBOOK & STATEMENT ====================

@router.get("/{account_id}/passbook", response_model=dict)
def get_passbook(
    account_id: int,
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get account passbook
    
    Returns formatted passbook entries for printing
    """
    from backend.shared.database.deposit_models import DepositPassbookEntry
    from sqlalchemy import and_
    
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account(account_id)
    
    query = db.query(DepositPassbookEntry).filter(
        DepositPassbookEntry.deposit_account_id == account_id
    )
    
    if from_date:
        query = query.filter(DepositPassbookEntry.entry_date >= from_date)
    
    if to_date:
        query = query.filter(DepositPassbookEntry.entry_date <= to_date)
    
    entries = query.order_by(
        DepositPassbookEntry.entry_date.asc()
    ).offset(skip).limit(limit).all()
    
    passbook_data = {
        "account_number": account.account_number,
        "account_type": account.account_type,
        "customer_id": account.customer_id,
        "from_date": from_date.isoformat() if from_date else account.opening_date.isoformat(),
        "to_date": to_date.isoformat() if to_date else date.today().isoformat(),
        "entries": [
            {
                "entry_date": e.entry_date.isoformat(),
                "particulars": e.particulars,
                "withdrawal": float(e.withdrawal_amount),
                "deposit": float(e.deposit_amount),
                "balance": float(e.balance)
            }
            for e in entries
        ]
    }
    
    return success_response(
        message="Passbook retrieved successfully",
        data=passbook_data
    )


@router.get("/{account_id}/statement", response_model=dict)
def get_account_statement(
    account_id: int,
    from_date: date = Query(..., description="Statement from date"),
    to_date: date = Query(..., description="Statement to date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get account statement
    
    Detailed statement including:
    - Opening and closing balance
    - All transactions
    - Summary statistics
    """
    from backend.shared.database.deposit_models import DepositTransaction
    from sqlalchemy import and_, func
    
    service = DepositAccountService(db, tenant_id, current_user["id"])
    account = service.get_account(account_id)
    
    # Get opening balance
    opening_txn = db.query(DepositTransaction).filter(
        and_(
            DepositTransaction.deposit_account_id == account_id,
            DepositTransaction.transaction_date < from_date
        )
    ).order_by(DepositTransaction.transaction_date.desc()).first()
    
    opening_balance = opening_txn.balance_after if opening_txn else 0
    
    # Get transactions in period
    transactions = db.query(DepositTransaction).filter(
        and_(
            DepositTransaction.deposit_account_id == account_id,
            DepositTransaction.transaction_date >= from_date,
            DepositTransaction.transaction_date <= to_date
        )
    ).order_by(DepositTransaction.transaction_date.asc()).all()
    
    # Calculate summary
    total_deposits = sum(
        float(t.amount) for t in transactions 
        if t.transaction_type in ['deposit', 'interest_credit', 'opening', 'installment']
    )
    total_withdrawals = sum(
        float(t.amount) for t in transactions 
        if t.transaction_type in ['withdrawal', 'closure']
    )
    total_interest = sum(
        float(t.amount) for t in transactions 
        if t.transaction_type == 'interest_credit'
    )
    
    closing_balance = transactions[-1].balance_after if transactions else opening_balance
    
    statement = {
        "account": {
            "account_number": account.account_number,
            "account_type": account.account_type,
            "customer_id": account.customer_id
        },
        "period": {
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        },
        "opening_balance": float(opening_balance),
        "closing_balance": float(closing_balance),
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_interest": total_interest,
        "transactions": [TransactionResponse.from_orm(t).dict() for t in transactions],
        "statement_date": date.today().isoformat()
    }
    
    return success_response(
        message="Statement generated successfully",
        data=statement
    )


# ==================== MATURITY MANAGEMENT ====================

@router.get("/maturity-due", response_model=dict)
def get_maturity_due_accounts(
    days_ahead: int = Query(7, ge=1, le=90, description="Days ahead to check"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get accounts due for maturity
    
    Returns accounts maturing in next N days
    """
    service = DepositAccountService(db, tenant_id, current_user["id"])
    accounts = service.get_accounts_due_for_maturity(days_ahead)
    
    return success_response(
        message=f"Found {len(accounts)} accounts due for maturity",
        data={
            "accounts": [DepositAccountResponse.from_orm(a).dict() for a in accounts],
            "days_ahead": days_ahead
        }
    )
