"""
Statement Generation Router

API endpoints for account statement operations including:
- Generate statement (PDF/Excel)
- Email statement
- View statement online
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .statement_service import StatementService
from .schemas import StatementRequest, StatementResponse, SuccessResponse

router = APIRouter(prefix="/statement", tags=["Deposit Statement"])


@router.post("", response_model=StatementResponse)
def generate_statement(
    request: StatementRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate account statement
    
    Returns statement data with transactions for the specified period.
    """
    service = StatementService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    statement = service.generate_statement(
        account_id=request.account_id,
        from_date=request.from_date,
        to_date=request.to_date
    )
    
    return statement


@router.get("/{account_id}/pdf")
def generate_statement_pdf(
    account_id: int,
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate statement PDF
    
    Creates a PDF document with account statement.
    """
    service = StatementService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    pdf_result = service.generate_statement_pdf(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date
    )
    
    from fastapi.responses import Response
    
    return Response(
        content=pdf_result['pdf_content'],
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={pdf_result['filename']}"
        }
    )


@router.get("/{account_id}/excel")
def generate_statement_excel(
    account_id: int,
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate statement Excel
    
    Creates an Excel file with account statement.
    """
    service = StatementService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    excel_result = service.generate_statement_excel(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date
    )
    
    from fastapi.responses import Response
    
    return Response(
        content=excel_result['excel_content'],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={excel_result['filename']}"
        }
    )


@router.post("/{account_id}/email", response_model=SuccessResponse)
def email_statement(
    account_id: int,
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    email_address: Optional[str] = Query(None, description="Custom email address"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Email statement to customer
    
    Generates PDF statement and sends via email.
    """
    service = StatementService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    result = service.email_statement(
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
        email_address=email_address
    )
    
    return SuccessResponse(
        success=True,
        message=f"Statement emailed to {result['email_address']}",
        data=result
    )


@router.get("/{account_id}/quarterly")
def get_quarterly_statement(
    account_id: int,
    year: int = Query(..., description="Year"),
    quarter: int = Query(..., ge=1, le=4, description="Quarter (1-4)"),
    format: str = Query("json", description="Format: json, pdf, excel"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get quarterly statement
    
    Automatically calculates date range for the specified quarter.
    """
    service = StatementService(
        db=db,
        tenant_id=current_user['tenant_id'],
        user_id=current_user['user_id']
    )
    
    # Calculate quarter dates
    from datetime import date as dt
    quarter_start = {
        1: dt(year, 1, 1),
        2: dt(year, 4, 1),
        3: dt(year, 7, 1),
        4: dt(year, 10, 1)
    }[quarter]
    
    quarter_end = {
        1: dt(year, 3, 31),
        2: dt(year, 6, 30),
        3: dt(year, 9, 30),
        4: dt(year, 12, 31)
    }[quarter]
    
    if format == "pdf":
        pdf_result = service.generate_statement_pdf(
            account_id=account_id,
            from_date=quarter_start,
            to_date=quarter_end
        )
        
        from fastapi.responses import Response
        return Response(
            content=pdf_result['pdf_content'],
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={pdf_result['filename']}"}
        )
    
    elif format == "excel":
        excel_result = service.generate_statement_excel(
            account_id=account_id,
            from_date=quarter_start,
            to_date=quarter_end
        )
        
        from fastapi.responses import Response
        return Response(
            content=excel_result['excel_content'],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={excel_result['filename']}"}
        )
    
    else:
        statement = service.generate_statement(
            account_id=account_id,
            from_date=quarter_start,
            to_date=quarter_end
        )
        return statement
