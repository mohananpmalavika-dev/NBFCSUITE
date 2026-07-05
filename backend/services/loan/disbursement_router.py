"""
Loan Disbursement Router
API endpoints for loan disbursement and account management
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.loan.disbursement_service import LoanDisbursementService
from backend.services.loan.schemas import (
    SanctionLetterResponse,
    DisbursementApprovalRequest,
    DisbursementResponse,
    LoanAccountResponse,
    LoanAccountDetailResponse,
    LoanAccountListResponse
)


router = APIRouter(prefix="/disbursement", tags=["Loan Disbursement"])


@router.post("/{application_id}/sanction-letter", response_model=dict)
async def generate_sanction_letter(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Generate sanction letter for approved loan application
    
    **Required Status**: Application must be approved
    
    **Returns**: Sanction letter with all loan terms and conditions
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        sanction_letter = await service.generate_sanction_letter(application_id)
        
        return success_response(
            data=sanction_letter,
            message="Sanction letter generated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sanction letter: {str(e)}")


@router.post("/{application_id}/approve", response_model=dict)
async def approve_disbursement(
    application_id: int,
    request: DisbursementApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Approve and process loan disbursement
    
    **Process**:
    1. Validates application approval status
    2. Verifies bank account details
    3. Creates loan account with unique account number
    4. Generates EMI schedule
    5. Updates application status to 'disbursed'
    6. Initiates fund transfer (in real scenario)
    
    **Required Fields**:
    - bank_account_id: Customer's verified bank account
    - disbursement_date: Date of fund transfer
    - disbursement_mode: neft, rtgs, imps, or cheque
    - emi_start_day: Day of month for EMI (default: 5)
    
    **Returns**: Loan account details and disbursement confirmation
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        
        disbursement_details = await service.approve_disbursement(
            application_id=application_id,
            bank_account_id=request.bank_account_id,
            disbursement_date=request.disbursement_date,
            disbursement_mode=request.disbursement_mode,
            emi_start_day=request.emi_start_day,
            remarks=request.remarks
        )
        
        return success_response(
            data=disbursement_details,
            message="Loan disbursed successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing disbursement: {str(e)}")


@router.get("/accounts/{account_id}", response_model=dict)
async def get_loan_account(
    account_id: int,
    include_schedule: bool = Query(False, description="Include EMI schedule in response"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get loan account details by ID
    
    **Query Parameters**:
    - include_schedule: Set to true to include complete EMI schedule
    
    **Returns**: 
    - Loan account with all details
    - Outstanding balances (principal, interest, charges)
    - EMI schedule (if requested)
    - Payment status and dates
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        account = await service.get_loan_account(
            account_id=account_id,
            include_schedule=include_schedule
        )
        
        if not account:
            raise HTTPException(status_code=404, detail="Loan account not found")
        
        return success_response(
            data=account,
            message="Loan account retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving loan account: {str(e)}")


@router.get("/accounts/number/{account_number}", response_model=dict)
async def get_loan_account_by_number(
    account_number: str,
    include_schedule: bool = Query(False, description="Include EMI schedule in response"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get loan account details by account number
    
    **Query Parameters**:
    - include_schedule: Set to true to include complete EMI schedule
    
    **Returns**: Loan account with all details
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        account = await service.get_loan_account(
            account_number=account_number,
            include_schedule=include_schedule
        )
        
        if not account:
            raise HTTPException(status_code=404, detail="Loan account not found")
        
        return success_response(
            data=account,
            message="Loan account retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving loan account: {str(e)}")


@router.get("/accounts", response_model=dict)
async def list_loan_accounts(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by account status"),
    product_id: Optional[int] = Query(None, description="Filter by loan product"),
    overdue_only: bool = Query(False, description="Show only overdue accounts"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Pagination limit"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List loan accounts with filters and pagination
    
    **Filters**:
    - customer_id: Filter by specific customer
    - status: active, overdue, npa, closed, settled, written_off
    - product_id: Filter by loan product
    - overdue_only: Show only accounts with pending payments
    
    **Pagination**:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 500)
    
    **Returns**: List of loan accounts with pagination metadata
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        
        result = await service.list_loan_accounts(
            customer_id=customer_id,
            status=status,
            product_id=product_id,
            overdue_only=overdue_only,
            skip=skip,
            limit=limit
        )
        
        return success_response(
            data=result,
            message=f"Retrieved {len(result['accounts'])} loan accounts"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing loan accounts: {str(e)}")


@router.get("/accounts/{account_id}/schedule", response_model=dict)
async def get_emi_schedule(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get complete EMI schedule for a loan account
    
    **Returns**: 
    - Complete EMI schedule with all installments
    - Principal and interest breakdown for each EMI
    - Payment status for each installment
    - Overdue information if applicable
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        account = await service.get_loan_account(
            account_id=account_id,
            include_schedule=True
        )
        
        if not account:
            raise HTTPException(status_code=404, detail="Loan account not found")
        
        if "emi_schedule" not in account:
            raise HTTPException(status_code=404, detail="EMI schedule not found")
        
        return success_response(
            data={
                "loan_account_number": account["loan_account_number"],
                "emi_amount": account["emi_amount"],
                "total_emis": len(account["emi_schedule"]),
                "schedule": account["emi_schedule"]
            },
            message="EMI schedule retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving EMI schedule: {str(e)}")


@router.get("/statistics", response_model=dict)
async def get_disbursement_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get disbursement and portfolio statistics
    
    **Returns**:
    - Total loans disbursed (count and amount)
    - Active portfolio size
    - Average loan size
    - Status-wise breakdown
    - Overdue statistics
    """
    try:
        service = LoanDisbursementService(db, tenant_id, current_user["id"])
        
        # Get all accounts for statistics
        all_accounts = await service.list_loan_accounts(limit=10000)
        accounts = all_accounts["accounts"]
        
        # Calculate statistics
        total_loans = len(accounts)
        total_disbursed = sum(acc["disbursed_amount"] for acc in accounts)
        total_outstanding = sum(acc["total_outstanding"] for acc in accounts)
        active_loans = len([acc for acc in accounts if acc["status"] == "active"])
        overdue_loans = len([acc for acc in accounts if acc["overdue_days"] > 0])
        
        avg_loan_size = total_disbursed / total_loans if total_loans > 0 else 0
        
        # Status breakdown
        status_breakdown = {}
        for acc in accounts:
            status = acc["status"]
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        statistics = {
            "total_loans_disbursed": total_loans,
            "total_disbursed_amount": total_disbursed,
            "total_outstanding_amount": total_outstanding,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans,
            "average_loan_size": avg_loan_size,
            "status_breakdown": status_breakdown,
            "collection_efficiency": ((total_disbursed - total_outstanding) / total_disbursed * 100) if total_disbursed > 0 else 0
        }
        
        return success_response(
            data=statistics,
            message="Statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
