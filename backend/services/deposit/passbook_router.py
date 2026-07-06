"""
Passbook Management Router

API endpoints for passbook operations including:
- View passbook entries
- Print passbook
- Generate passbook PDF
- Update print status
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .passbook_service import PassbookService
from .schemas import (
    PassbookResponse,
    PassbookEntryResponse,
    SuccessResponse,
    PaginationMeta
)

router = APIRouter(prefix="/passbook", tags=["Deposit Passbook"])


@router.get("/{account_id}/entries", response_model=PassbookResponse)
def get_passbook_entries(
    account_id: int,
    from_date: Optional[date] = Query(None, description="Start date"),
    to_date: Optional[date] = Query(None, description="End date"),
    unprinted_only: bool = Query(False, description="Show only unprinted entries"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get passbook entries for an account
    
    Supports filtering by date range and printed status.
    Useful for passbook printing and customer viewing.
    """
    service = PassbookService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.get_passbook_entries(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        unprinted_only=unprinted_only,
        skip=skip,
        limit=limit
    )
    
    return result


@router.post("/{account_id}/mark-printed", response_model=SuccessResponse)
def mark_entries_as_printed(
    account_id: int,
    entry_ids: List[int],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark passbook entries as printed
    
    Called after physical passbook printing to track printed entries.
    """
    service = PassbookService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.mark_entries_as_printed(
        account_id=account_id,
        entry_ids=entry_ids
    )
    
    return SuccessResponse(
        success=True,
        message=f"Marked {result['marked_count']} entries as printed",
        data=result
    )


@router.get("/{account_id}/pdf")
def generate_passbook_pdf(
    account_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    unprinted_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate passbook PDF
    
    Creates a PDF document with passbook entries formatted for printing.
    """
    service = PassbookService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    pdf_result = service.generate_passbook_pdf(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        unprinted_only=unprinted_only
    )
    
    from fastapi.responses import Response
    
    return Response(
        content=pdf_result['pdf_content'],
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={pdf_result['filename']}"
        }
    )


@router.get("/{account_id}/summary")
def get_passbook_summary(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get passbook summary
    
    Returns total entries, printed/unprinted count, last print date.
    """
    service = PassbookService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    summary = service.get_passbook_summary(account_id)
    
    return {
        "success": True,
        "data": summary
    }


@router.post("/{account_id}/issue", response_model=SuccessResponse)
def issue_passbook(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark passbook as issued
    
    Sets the passbook_issued flag on the account.
    """
    service = PassbookService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.issue_passbook(account_id)
    
    return SuccessResponse(
        success=True,
        message="Passbook issued successfully",
        data=result
    )
