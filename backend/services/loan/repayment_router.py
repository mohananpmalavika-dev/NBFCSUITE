"""
Loan Repayment Router
API endpoints for loan repayment and payment operations
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.loan.repayment_service import LoanRepaymentService


router = APIRouter(prefix="/repayment", tags=["Loan Repayment"])


def get_repayment_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> LoanRepaymentService:
    """Dependency to get repayment service"""
    return LoanRepaymentService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"]
    )


@router.post("/record-payment", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_payment(
    account_id: Optional[int] = None,
    account_number: Optional[str] = None,
    payment_amount: Decimal = Query(..., gt=0),
    payment_date: Optional[date] = None,
    payment_mode: str = Query("cash", pattern="^(cash|cheque|neft|rtgs|upi|imps)$"),
    reference_number: Optional[str] = None,
    bank_name: Optional[str] = None,
    transaction_date: Optional[date] = None,
    remarks: Optional[str] = None,
    service: LoanRepaymentService = Depends(get_repayment_service)
):
    """Record a payment against loan account"""
    try:
        payment = await service.record_payment(
            account_id=account_id,
            account_number=account_number,
            payment_amount=payment_amount,
            payment_date=payment_date,
            payment_mode=payment_mode,
            reference_number=reference_number,
            bank_name=bank_name,
            transaction_date=transaction_date,
            remarks=remarks
        )
        
        return success_response(
            data=payment,
            message="Payment recorded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment-history", response_model=dict)
async def get_payment_history(
    account_id: Optional[int] = None,
    account_number: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: LoanRepaymentService = Depends(get_repayment_service)
):
    """Get payment history for loan account"""
    try:
        skip = (page - 1) * page_size
        history = await service.get_payment_history(
            account_id=account_id,
            account_number=account_number,
            skip=skip,
            limit=page_size
        )
        
        return success_response(data=history)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/receipt/{receipt_id}", response_model=dict)
async def get_receipt_by_id(
    receipt_id: int,
    service: LoanRepaymentService = Depends(get_repayment_service)
):
    """Get payment receipt by ID"""
    try:
        receipt = await service.get_receipt(receipt_id=receipt_id)
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        return success_response(data=receipt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/receipt/number/{receipt_number}", response_model=dict)
async def get_receipt_by_number(
    receipt_number: str,
    service: LoanRepaymentService = Depends(get_repayment_service)
):
    """Get payment receipt by number"""
    try:
        receipt = await service.get_receipt(receipt_number=receipt_number)
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        return success_response(data=receipt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outstanding/{account_id}", response_model=dict)
async def get_outstanding_balance(
    account_id: int,
    service: LoanRepaymentService = Depends(get_repayment_service)
):
    """Calculate outstanding amounts for loan account"""
    try:
        outstanding = await service.calculate_outstanding(account_id)
        return success_response(data=outstanding)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
