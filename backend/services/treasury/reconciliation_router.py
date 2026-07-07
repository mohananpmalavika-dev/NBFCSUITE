"""
Treasury - Bank Reconciliation Router
API endpoints for bank reconciliation, statements, and matching
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.services.treasury.reconciliation_service import ReconciliationService
from backend.services.treasury.reconciliation_schemas import (
    BankStatementCreate, BankStatementUpdate, BankStatementResponse,
    BankStatementBulkImport, BankReconciliationCreate, BankReconciliationUpdate,
    BankReconciliationResponse, BankReconciliationDetail, ReconciliationItemCreate,
    ReconciliationItemUpdate, ReconciliationItemResponse, MatchTransactionRequest,
    UnmatchTransactionRequest, AutoMatchRequest, ReconciliationStatistics,
    BankStatementSummary, ReconciliationDifference, BankReconciliationApprove,
    BankReconciliationReject, ReconciliationStatus
)

router = APIRouter(prefix="/reconciliation", tags=["Treasury - Reconciliation"])


def get_service(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Dependency to get reconciliation service"""
    return ReconciliationService(db, current_user["tenant_id"], current_user["id"])


# ============================================================================
# BANK STATEMENT ENDPOINTS
# ============================================================================

@router.post("/bank-statements", response_model=BankStatementResponse, status_code=status.HTTP_201_CREATED)
def create_bank_statement(
    data: BankStatementCreate,
    service: ReconciliationService = Depends(get_service)
):
    """Create a new bank statement entry"""
    return service.create_bank_statement(data)


@router.post("/bank-statements/bulk-import", response_model=List[BankStatementResponse], status_code=status.HTTP_201_CREATED)
def bulk_import_statements(
    data: BankStatementBulkImport,
    service: ReconciliationService = Depends(get_service)
):
    """Bulk import bank statements"""
    return service.bulk_import_statements(data)



@router.get("/bank-statements/{statement_id}", response_model=BankStatementResponse)
def get_bank_statement(
    statement_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Get bank statement by ID"""
    return service.get_bank_statement(statement_id)


@router.get("/bank-statements", response_model=dict)
def list_bank_statements(
    bank_account_id: Optional[int] = Query(None),
    is_matched: Optional[bool] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ReconciliationService = Depends(get_service)
):
    """List bank statements with filters"""
    statements, total = service.list_bank_statements(
        bank_account_id=bank_account_id,
        is_matched=is_matched,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return {"total": total, "items": statements, "skip": skip, "limit": limit}


@router.patch("/bank-statements/{statement_id}", response_model=BankStatementResponse)
def update_bank_statement(
    statement_id: int,
    data: BankStatementUpdate,
    service: ReconciliationService = Depends(get_service)
):
    """Update bank statement"""
    return service.update_bank_statement(statement_id, data)


@router.delete("/bank-statements/{statement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank_statement(
    statement_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Delete bank statement"""
    service.delete_bank_statement(statement_id)



@router.get("/bank-statements/account/{bank_account_id}/summary", response_model=BankStatementSummary)
def get_bank_statement_summary(
    bank_account_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Get bank statement summary for an account"""
    return service.get_bank_statement_summary(bank_account_id)


# ============================================================================
# BANK RECONCILIATION ENDPOINTS
# ============================================================================

@router.post("", response_model=BankReconciliationResponse, status_code=status.HTTP_201_CREATED)
def create_reconciliation(
    data: BankReconciliationCreate,
    service: ReconciliationService = Depends(get_service)
):
    """Create a new bank reconciliation"""
    return service.create_reconciliation(data)


@router.get("/{reconciliation_id}", response_model=BankReconciliationDetail)
def get_reconciliation(
    reconciliation_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Get reconciliation with items"""
    return service.get_reconciliation(reconciliation_id)


@router.get("", response_model=dict)
def list_reconciliations(
    bank_account_id: Optional[int] = Query(None),
    status: Optional[ReconciliationStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: ReconciliationService = Depends(get_service)
):
    """List reconciliations with filters"""
    reconciliations, total = service.list_reconciliations(
        bank_account_id=bank_account_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return {"total": total, "items": reconciliations, "skip": skip, "limit": limit}



@router.patch("/{reconciliation_id}", response_model=BankReconciliationResponse)
def update_reconciliation(
    reconciliation_id: int,
    data: BankReconciliationUpdate,
    service: ReconciliationService = Depends(get_service)
):
    """Update reconciliation"""
    return service.update_reconciliation(reconciliation_id, data)


@router.delete("/{reconciliation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation(
    reconciliation_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Delete reconciliation"""
    service.delete_reconciliation(reconciliation_id)


# ============================================================================
# RECONCILIATION ITEMS
# ============================================================================

@router.post("/{reconciliation_id}/items", response_model=ReconciliationItemResponse, status_code=status.HTTP_201_CREATED)
def add_reconciliation_item(
    reconciliation_id: int,
    data: ReconciliationItemCreate,
    service: ReconciliationService = Depends(get_service)
):
    """Add item to reconciliation"""
    return service.add_reconciliation_item(reconciliation_id, data)


@router.patch("/items/{item_id}", response_model=ReconciliationItemResponse)
def update_reconciliation_item(
    item_id: int,
    data: ReconciliationItemUpdate,
    service: ReconciliationService = Depends(get_service)
):
    """Update reconciliation item"""
    return service.update_reconciliation_item(item_id, data)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reconciliation_item(
    item_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Delete reconciliation item"""
    service.delete_reconciliation_item(item_id)



# ============================================================================
# MATCHING OPERATIONS
# ============================================================================

@router.post("/match-transaction", response_model=BankStatementResponse)
def match_transaction(
    data: MatchTransactionRequest,
    service: ReconciliationService = Depends(get_service)
):
    """Match bank statement with GL entry"""
    return service.match_transaction(data)


@router.post("/unmatch-transaction", response_model=BankStatementResponse)
def unmatch_transaction(
    data: UnmatchTransactionRequest,
    service: ReconciliationService = Depends(get_service)
):
    """Unmatch a bank statement transaction"""
    return service.unmatch_transaction(data)


@router.post("/auto-match", response_model=dict)
def auto_match_transactions(
    data: AutoMatchRequest,
    service: ReconciliationService = Depends(get_service)
):
    """Automatically match transactions"""
    return service.auto_match_transactions(data)


# ============================================================================
# APPROVAL WORKFLOW
# ============================================================================

@router.post("/{reconciliation_id}/submit", response_model=BankReconciliationResponse)
def submit_for_approval(
    reconciliation_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Submit reconciliation for approval"""
    return service.submit_for_approval(reconciliation_id)


@router.post("/{reconciliation_id}/approve", response_model=BankReconciliationResponse)
def approve_reconciliation(
    reconciliation_id: int,
    data: BankReconciliationApprove,
    service: ReconciliationService = Depends(get_service)
):
    """Approve reconciliation"""
    return service.approve_reconciliation(reconciliation_id, data.approval_notes)



@router.post("/{reconciliation_id}/reject", response_model=BankReconciliationResponse)
def reject_reconciliation(
    reconciliation_id: int,
    data: BankReconciliationReject,
    service: ReconciliationService = Depends(get_service)
):
    """Reject reconciliation"""
    return service.reject_reconciliation(reconciliation_id, data.approval_notes)


# ============================================================================
# STATISTICS & REPORTS
# ============================================================================

@router.get("/statistics/summary", response_model=ReconciliationStatistics)
def get_reconciliation_statistics(
    service: ReconciliationService = Depends(get_service)
):
    """Get reconciliation statistics"""
    return service.get_reconciliation_statistics()


@router.get("/{reconciliation_id}/difference-breakdown", response_model=ReconciliationDifference)
def get_reconciliation_difference_breakdown(
    reconciliation_id: int,
    service: ReconciliationService = Depends(get_service)
):
    """Get breakdown of reconciliation differences by type"""
    return service.get_reconciliation_difference_breakdown(reconciliation_id)
