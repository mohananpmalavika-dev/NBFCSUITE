"""
Accounting API Router
FastAPI endpoints for accounting operations
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user
from backend.services.accounting.accounting_service import AccountingService
from backend.services.accounting import schemas
from backend.shared.database.accounting_models import (
    AccountType,
    JournalEntryStatus,
    JournalEntryType
)


router = APIRouter(prefix="/accounting", tags=["Accounting"])


def get_accounting_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AccountingService:
    """Dependency to get accounting service"""
    return AccountingService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"]
    )


# ============================================================================
# Chart of Accounts Endpoints
# ============================================================================

@router.post("/accounts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: schemas.ChartOfAccountsCreate,
    service: AccountingService = Depends(get_accounting_service)
):
    """Create new account in chart of accounts"""
    try:
        account = await service.create_account(
            account_code=account_data.account_code,
            account_name=account_data.account_name,
            account_type=account_data.account_type,
            account_sub_type=account_data.account_sub_type,
            parent_account_id=account_data.parent_account_id,
            level=account_data.level,
            is_group=account_data.is_group,
            allow_manual_entry=account_data.allow_manual_entry,
            opening_balance=account_data.opening_balance,
            description=account_data.description,
            notes=account_data.notes
        )
        
        return success_response(
            data=schemas.ChartOfAccountsResponse.from_orm(account),
            message="Account created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating account: {str(e)}")


@router.get("/accounts/{account_id}", response_model=dict)
async def get_account(
    account_id: int,
    service: AccountingService = Depends(get_accounting_service)
):
    """Get account by ID"""
    try:
        account = await service.get_account(account_id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return success_response(
            data=schemas.ChartOfAccountsResponse.from_orm(account)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/code/{account_code}", response_model=dict)
async def get_account_by_code(
    account_code: str,
    service: AccountingService = Depends(get_accounting_service)
):
    """Get account by code"""
    try:
        account = await service.get_account(account_code=account_code)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return success_response(
            data=schemas.ChartOfAccountsResponse.from_orm(account)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts", response_model=dict)
async def list_accounts(
    account_type: Optional[AccountType] = None,
    is_active: bool = True,
    is_group: Optional[bool] = None,
    parent_account_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    service: AccountingService = Depends(get_accounting_service)
):
    """List accounts with filters"""
    try:
        skip = (page - 1) * page_size
        accounts, total = await service.list_accounts(
            account_type=account_type,
            is_active=is_active,
            is_group=is_group,
            parent_account_id=parent_account_id,
            skip=skip,
            limit=page_size
        )
        
        return success_response(
            data={
                "accounts": [schemas.ChartOfAccountsResponse.from_orm(acc) for acc in accounts],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/accounts/{account_id}", response_model=dict)
async def update_account(
    account_id: int,
    account_data: schemas.ChartOfAccountsUpdate,
    service: AccountingService = Depends(get_accounting_service)
):
    """Update account"""
    try:
        update_data = account_data.dict(exclude_unset=True)
        account = await service.update_account(account_id, **update_data)
        
        return success_response(
            data=schemas.ChartOfAccountsResponse.from_orm(account),
            message="Account updated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts/hierarchy/tree", response_model=dict)
async def get_account_hierarchy(
    service: AccountingService = Depends(get_accounting_service)
):
    """Get account hierarchy tree"""
    try:
        hierarchy = await service.get_account_hierarchy()
        return success_response(data={"hierarchy": hierarchy})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Journal Entry Endpoints
# ============================================================================

@router.post("/journal-entries", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_data: schemas.JournalEntryCreate,
    service: AccountingService = Depends(get_accounting_service)
):
    """Create new journal entry"""
    try:
        line_items = [item.dict() for item in entry_data.line_items]
        
        journal_entry = await service.create_journal_entry(
            entry_date=entry_data.entry_date,
            narration=entry_data.narration,
            line_items=line_items,
            entry_type=entry_data.entry_type,
            reference_type=entry_data.reference_type,
            reference_id=entry_data.reference_id,
            reference_number=entry_data.reference_number,
            internal_notes=entry_data.internal_notes,
            auto_post=False
        )
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(journal_entry),
            message="Journal entry created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal-entries/{entry_id}", response_model=dict)
async def get_journal_entry(
    entry_id: int,
    service: AccountingService = Depends(get_accounting_service)
):
    """Get journal entry by ID"""
    try:
        entry = await service.get_journal_entry(entry_id=entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(entry)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal-entries/number/{entry_number}", response_model=dict)
async def get_journal_entry_by_number(
    entry_number: str,
    service: AccountingService = Depends(get_accounting_service)
):
    """Get journal entry by number"""
    try:
        entry = await service.get_journal_entry(entry_number=entry_number)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(entry)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal-entries", response_model=dict)
async def list_journal_entries(
    status: Optional[JournalEntryStatus] = None,
    entry_type: Optional[JournalEntryType] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    reference_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    service: AccountingService = Depends(get_accounting_service)
):
    """List journal entries with filters"""
    try:
        skip = (page - 1) * page_size
        entries, total = await service.list_journal_entries(
            status=status,
            entry_type=entry_type,
            from_date=from_date,
            to_date=to_date,
            reference_type=reference_type,
            skip=skip,
            limit=page_size
        )
        
        return success_response(
            data={
                "entries": [schemas.JournalEntryResponse.from_orm(e) for e in entries],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/journal-entries/{entry_id}/post", response_model=dict)
async def post_journal_entry(
    entry_id: int,
    post_request: Optional[schemas.JournalEntryPostRequest] = None,
    service: AccountingService = Depends(get_accounting_service)
):
    """Post journal entry to general ledger"""
    try:
        posting_date = post_request.posting_date if post_request else None
        entry = await service.post_journal_entry(entry_id, posting_date)
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(entry),
            message="Journal entry posted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/journal-entries/{entry_id}/reverse", response_model=dict)
async def reverse_journal_entry(
    entry_id: int,
    reversal_request: schemas.JournalEntryReversalRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Reverse a posted journal entry"""
    try:
        reversal_entry = await service.reverse_journal_entry(
            entry_id=entry_id,
            reversal_date=reversal_request.reversal_date,
            narration=reversal_request.narration
        )
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(reversal_entry),
            message="Journal entry reversed successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# General Ledger Endpoints
# ============================================================================

@router.get("/general-ledger", response_model=dict)
async def get_general_ledger(
    account_id: Optional[int] = None,
    account_code: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    financial_year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    service: AccountingService = Depends(get_accounting_service)
):
    """Get general ledger entries"""
    try:
        skip = (page - 1) * page_size
        entries, total = await service.get_general_ledger_entries(
            account_id=account_id,
            account_code=account_code,
            from_date=from_date,
            to_date=to_date,
            financial_year=financial_year,
            skip=skip,
            limit=page_size
        )
        
        return success_response(
            data={
                "entries": [schemas.GeneralLedgerEntryResponse.from_orm(e) for e in entries],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/general-ledger/account-statement", response_model=dict)
async def get_account_statement(
    statement_request: schemas.AccountStatementRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Generate account statement"""
    try:
        statement = await service.get_account_statement(
            account_id=statement_request.account_id,
            from_date=statement_request.from_date,
            to_date=statement_request.to_date
        )
        
        return success_response(data=statement)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Trial Balance Endpoints
# ============================================================================

@router.post("/trial-balance", response_model=dict)
async def get_trial_balance(
    tb_request: schemas.TrialBalanceRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Generate trial balance"""
    try:
        trial_balance = await service.generate_trial_balance(
            balance_date=tb_request.balance_date,
            account_type=tb_request.account_type
        )
        
        return success_response(data=trial_balance)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Financial Statements Endpoints
# ============================================================================

@router.post("/reports/profit-loss", response_model=dict)
async def get_profit_loss(
    pl_request: schemas.ProfitLossRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Generate Profit & Loss statement"""
    try:
        profit_loss = await service.generate_profit_loss(
            from_date=pl_request.from_date,
            to_date=pl_request.to_date
        )
        
        return success_response(data=profit_loss)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/balance-sheet", response_model=dict)
async def get_balance_sheet(
    bs_request: schemas.BalanceSheetRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Generate Balance Sheet"""
    try:
        balance_sheet = await service.generate_balance_sheet(
            as_of_date=bs_request.as_of_date
        )
        
        return success_response(data=balance_sheet)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# Event-driven Accounting Endpoints
# ============================================================================

@router.post("/events/loan-disbursement", response_model=dict)
async def record_loan_disbursement(
    disbursement_data: schemas.LoanDisbursementAccountingRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Record loan disbursement accounting entry"""
    try:
        entry = await service.record_loan_disbursement(
            loan_account_id=disbursement_data.loan_account_id,
            disbursement_amount=disbursement_data.disbursement_amount,
            disbursement_date=disbursement_data.disbursement_date,
            processing_fee=disbursement_data.processing_fee,
            documentation_charges=disbursement_data.documentation_charges,
            insurance_premium=disbursement_data.insurance_premium,
            net_disbursement=disbursement_data.net_disbursement
        )
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(entry),
            message="Loan disbursement recorded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/loan-repayment", response_model=dict)
async def record_loan_repayment(
    repayment_data: schemas.LoanRepaymentAccountingRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Record loan repayment accounting entry"""
    try:
        entry = await service.record_loan_repayment(
            loan_account_id=repayment_data.loan_account_id,
            repayment_id=repayment_data.repayment_id,
            payment_date=repayment_data.payment_date,
            principal_amount=repayment_data.principal_amount,
            interest_amount=repayment_data.interest_amount,
            penal_interest=repayment_data.penal_interest,
            charges=repayment_data.charges,
            total_amount=repayment_data.total_amount
        )
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(entry),
            message="Loan repayment recorded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/events/interest-accrual", response_model=dict)
async def record_interest_accrual(
    accrual_data: schemas.InterestAccrualRequest,
    service: AccountingService = Depends(get_accounting_service)
):
    """Record interest accrual accounting entry"""
    try:
        entry = await service.record_interest_accrual(
            loan_account_id=accrual_data.loan_account_id,
            accrual_date=accrual_data.accrual_date,
            interest_amount=accrual_data.interest_amount
        )
        
        return success_response(
            data=schemas.JournalEntryResponse.from_orm(entry),
            message="Interest accrual recorded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# Statistics and Dashboard Endpoints
# ============================================================================

@router.get("/statistics", response_model=dict)
async def get_statistics(
    service: AccountingService = Depends(get_accounting_service)
):
    """Get accounting module statistics"""
    try:
        stats = await service.get_statistics()
        return success_response(data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
