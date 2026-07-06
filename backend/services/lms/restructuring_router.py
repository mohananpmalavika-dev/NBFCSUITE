"""
Loan Restructuring Router
API endpoints for loan restructuring operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.lms.restructuring_service import RestructuringService
from backend.services.lms import restructuring_schemas as schemas


router = APIRouter(prefix="/restructuring", tags=["Loan Restructuring"])


# ============================================
# Restructuring Request Endpoints
# ============================================

@router.post("/requests", response_model=dict)
async def create_restructuring_request(
    data: schemas.RestructuringRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new loan restructuring request"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        request_data = data.model_dump()
        restructuring = service.create_restructuring_request(
            request_data=request_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring),
            message="Restructuring request created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests/{restructuring_id}", response_model=dict)
async def get_restructuring_request(
    restructuring_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get restructuring request by ID"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        restructuring = service.get_restructuring(restructuring_id)
        
        if not restructuring:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restructuring request not found")
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests", response_model=dict)
async def list_restructuring_requests(
    loan_account_id: Optional[int] = None,
    status: Optional[schemas.RestructuringStatusEnum] = None,
    restructuring_type: Optional[schemas.RestructuringTypeEnum] = None,
    reason: Optional[schemas.RestructuringReasonEnum] = None,
    created_from: Optional[date] = None,
    created_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List restructuring requests with filters"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        requests = service.list_restructuring_requests(
            loan_account_id=loan_account_id,
            status=status,
            restructuring_type=restructuring_type,
            reason=reason,
            created_from=created_from,
            created_to=created_to
        )
        
        return success_response(
            data=[schemas.RestructuringResponse.model_validate(r) for r in requests]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests/loan/{loan_account_id}", response_model=dict)
async def get_loan_restructuring_requests(
    loan_account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all restructuring requests for a loan account"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        requests = service.list_restructuring_requests(loan_account_id=loan_account_id)
        
        return success_response(
            data=[schemas.RestructuringResponse.model_validate(r) for r in requests]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/requests/{restructuring_id}", response_model=dict)
async def update_restructuring_request(
    restructuring_id: int,
    data: schemas.RestructuringRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update restructuring request (only in draft/pending status)"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude_unset=True)
        restructuring = service.update_restructuring_request(
            restructuring_id=restructuring_id,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not restructuring:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restructuring request not found")
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring),
            message="Restructuring request updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Approval Workflow Endpoints
# ============================================

@router.post("/requests/{restructuring_id}/approve", response_model=dict)
async def approve_restructuring(
    restructuring_id: int,
    data: schemas.RestructuringApprovalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve restructuring request"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        approval_data = data.model_dump()
        restructuring = service.approve_restructuring(
            restructuring_id=restructuring_id,
            approval_data=approval_data,
            approved_by=current_user["user_id"]
        )
        
        if not restructuring:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restructuring request not found")
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring),
            message="Restructuring request approved successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests/{restructuring_id}/reject", response_model=dict)
async def reject_restructuring(
    restructuring_id: int,
    data: schemas.RestructuringRejectionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reject restructuring request"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        rejection_data = data.model_dump()
        restructuring = service.reject_restructuring(
            restructuring_id=restructuring_id,
            rejection_data=rejection_data,
            rejected_by=current_user["user_id"]
        )
        
        if not restructuring:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restructuring request not found")
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring),
            message="Restructuring request rejected"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests/{restructuring_id}/implement", response_model=dict)
async def implement_restructuring(
    restructuring_id: int,
    data: schemas.RestructuringImplementationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Implement approved restructuring"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        implementation_data = data.model_dump()
        restructuring = service.implement_restructuring(
            restructuring_id=restructuring_id,
            implementation_data=implementation_data,
            user_id=current_user["user_id"]
        )
        
        if not restructuring:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to implement. Check if restructuring is approved."
            )
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring),
            message="Restructuring implemented successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests/{restructuring_id}/cancel", response_model=dict)
async def cancel_restructuring(
    restructuring_id: int,
    cancellation_reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel restructuring request"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        restructuring = service.cancel_restructuring(
            restructuring_id=restructuring_id,
            cancellation_reason=cancellation_reason,
            user_id=current_user["user_id"]
        )
        
        if not restructuring:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restructuring request not found")
        
        return success_response(
            data=schemas.RestructuringResponse.model_validate(restructuring),
            message="Restructuring request cancelled"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Pending Requests Endpoints
# ============================================

@router.get("/requests/pending/approval", response_model=dict)
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all requests pending approval"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        requests = service.get_pending_approvals()
        
        return success_response(
            data=[schemas.RestructuringResponse.model_validate(r) for r in requests]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests/pending/implementation", response_model=dict)
async def get_pending_implementations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all approved requests pending implementation"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        requests = service.get_pending_implementations()
        
        return success_response(
            data=[schemas.RestructuringResponse.model_validate(r) for r in requests]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Analysis & Summary Endpoints
# ============================================

@router.get("/summary/loan/{loan_account_id}", response_model=dict)
async def get_loan_restructuring_summary(
    loan_account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get restructuring summary for a loan account"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        summary = service.get_loan_restructuring_summary(loan_account_id)
        
        return success_response(
            data=schemas.RestructuringSummary(**summary)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history/loan/{loan_account_id}", response_model=dict)
async def get_restructuring_history(
    loan_account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get complete restructuring history for a loan"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        history = service.get_restructuring_history(loan_account_id)
        
        if not history:
            return success_response(
                data={
                    "loan_account_id": loan_account_id,
                    "restructuring_count": 0,
                    "previous_restructurings": []
                }
            )
        
        return success_response(
            data={
                "loan_account_id": loan_account_id,
                "restructuring_count": len(history),
                "previous_restructurings": [schemas.RestructuringResponse.model_validate(r) for r in history],
                "last_restructuring_date": history[0].created_at.date() if history else None
            }
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/analysis/impact", response_model=dict)
async def analyze_restructuring_impact(
    loan_account_id: int,
    proposed_emi: Optional[float] = None,
    proposed_tenure: Optional[int] = None,
    proposed_interest_rate: Optional[float] = None,
    moratorium_months: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Analyze financial impact of proposed restructuring"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        # This would call a helper method to calculate impact
        # For now, returning a placeholder
        analysis = {
            "loan_account_id": loan_account_id,
            "current_emi": 10000,
            "current_outstanding": 500000,
            "current_tenure_remaining": 48,
            "current_total_payable": 600000,
            "proposed_emi": proposed_emi or 8000,
            "proposed_tenure": proposed_tenure or 60,
            "proposed_total_payable": 650000,
            "emi_reduction": 2000,
            "emi_reduction_percentage": 20.0,
            "tenure_increase": 12,
            "additional_interest": 50000,
            "npv_loss": 30000,
            "impact_level": "medium",
            "recommendation": "Acceptable restructuring with moderate impact on profitability",
            "is_affordable": True,
            "minimum_required_income": 25000
        }
        
        return success_response(data=analysis)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Statistics Endpoints
# ============================================

@router.get("/statistics", response_model=dict)
async def get_restructuring_statistics(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get overall restructuring statistics"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        stats = service.get_restructuring_statistics(
            from_date=from_date,
            to_date=to_date
        )
        
        return success_response(
            data=schemas.RestructuringStatistics(**stats)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Bulk Operations Endpoints
# ============================================

@router.post("/bulk/create", response_model=dict)
async def bulk_create_restructuring(
    data: schemas.BulkRestructuringRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create restructuring requests for multiple loans (e.g., COVID relief)"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        results = []
        errors = []
        successful = 0
        failed = 0
        
        for loan_account_id in data.loan_account_ids:
            try:
                request_data = {
                    "loan_account_id": loan_account_id,
                    "restructuring_type": data.restructuring_type,
                    "reason": data.reason,
                    "reason_details": data.reason_details,
                    "moratorium_months": data.moratorium_months,
                    "current_emi": 0,  # Would fetch from loan account
                    "current_outstanding": 0,
                    "current_tenure_remaining": 0
                }
                
                restructuring = service.create_restructuring_request(
                    request_data=request_data,
                    user_id=current_user["user_id"]
                )
                
                # Auto-approve if committee approval provided
                if data.approved_by_committee and data.auto_implement:
                    approval_data = {
                        "approved_moratorium_months": data.moratorium_months,
                        "approval_remarks": f"Bulk approval: {data.bulk_approval_reference}",
                        "credit_committee_approval": True
                    }
                    restructuring = service.approve_restructuring(
                        restructuring_id=restructuring.id,
                        approval_data=approval_data,
                        approved_by=current_user["user_id"]
                    )
                
                results.append(schemas.RestructuringResponse.model_validate(restructuring))
                successful += 1
                
            except Exception as e:
                failed += 1
                errors.append({
                    "loan_account_id": loan_account_id,
                    "error": str(e)
                })
        
        return success_response(
            data=schemas.BulkRestructuringResponse(
                total_requests=len(data.loan_account_ids),
                successful=successful,
                failed=failed,
                bulk_approval_reference=data.bulk_approval_reference,
                restructuring_responses=results,
                errors=errors
            ),
            message=f"Bulk restructuring created: {successful} successful, {failed} failed"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Eligibility Check Endpoint
# ============================================

@router.get("/eligibility/loan/{loan_account_id}", response_model=dict)
async def check_restructuring_eligibility(
    loan_account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check if loan is eligible for restructuring"""
    try:
        service = RestructuringService(db, current_user["tenant_id"])
        
        # Check existing restructurings
        summary = service.get_loan_restructuring_summary(loan_account_id)
        
        eligibility = {
            "loan_account_id": loan_account_id,
            "is_eligible": summary["can_request_new"],
            "reason": "Loan is eligible for restructuring" if summary["can_request_new"] else "Cooling period active or pending request exists",
            "cooling_period_days": summary.get("cooling_period_days", 0),
            "pending_requests": summary["pending_requests"],
            "total_restructurings": summary["total_restructurings"],
            "max_restructurings_allowed": 3,
            "can_request_date": None  # Calculate based on cooling period
        }
        
        return success_response(data=eligibility)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
