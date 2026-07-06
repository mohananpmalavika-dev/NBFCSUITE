"""
NACH Router
API endpoints for NACH/eNACH mandate and debit operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.lms.nach_service import NACHService
from backend.services.lms import nach_schemas as schemas


router = APIRouter(prefix="/nach", tags=["NACH Management"])


# ============================================
# Mandate Management Endpoints
# ============================================

@router.post("/mandates/physical", response_model=dict)
async def create_physical_mandate(
    data: schemas.PhysicalMandateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create physical NACH mandate"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        mandate_data = data.model_dump()
        mandate = service.create_mandate(
            mandate_data=mandate_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate),
            message="Physical NACH mandate created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/mandates/enach", response_model=dict)
async def create_enach_mandate(
    data: schemas.ENACHMandateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create eNACH mandate and get authentication URL"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        mandate_data = data.model_dump()
        mandate = service.create_mandate(
            mandate_data=mandate_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate),
            message="eNACH mandate created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/mandates/{mandate_id}/initiate-enach", response_model=dict)
async def initiate_enach_authentication(
    mandate_id: int,
    redirect_url: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initiate eNACH authentication process"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        result = service.initiate_enach_authentication(
            mandate_id=mandate_id,
            redirect_url=redirect_url
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mandate not found or not eligible for eNACH"
            )
        
        return success_response(
            data=schemas.ENACHAuthenticationResponse(
                mandate_id=mandate_id,
                mandate_number=result["mandate_number"],
                enach_request_id=result["enach_request_id"],
                authentication_url=result["authentication_url"],
                message="Please redirect customer to authentication URL"
            ),
            message="eNACH authentication initiated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mandates/{mandate_id}", response_model=dict)
async def get_mandate(
    mandate_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get mandate by ID"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        mandate = service.get_mandate(mandate_id)
        
        if not mandate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mandate not found")
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mandates", response_model=dict)
async def list_mandates(
    loan_account_id: Optional[int] = None,
    status: Optional[schemas.MandateStatusEnum] = None,
    mandate_type: Optional[schemas.MandateTypeEnum] = None,
    expiring_before: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List mandates with filters"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        mandates = service.list_mandates(
            loan_account_id=loan_account_id,
            status=status,
            mandate_type=mandate_type,
            expiring_before=expiring_before
        )
        
        return success_response(
            data=[schemas.MandateResponse.model_validate(m) for m in mandates]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mandates/loan/{loan_account_id}/active", response_model=dict)
async def get_active_mandate(
    loan_account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get active mandate for loan account"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        mandate = service.get_active_mandate(loan_account_id)
        
        if not mandate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active mandate found for this loan account"
            )
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/mandates/{mandate_id}/approve", response_model=dict)
async def approve_mandate(
    mandate_id: int,
    umrn: str,
    sponsor_bank_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve mandate after bank confirmation"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        mandate = service.approve_mandate(
            mandate_id=mandate_id,
            umrn=umrn,
            sponsor_bank_code=sponsor_bank_code,
            approved_by=current_user["user_id"]
        )
        
        if not mandate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mandate not found")
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate),
            message="Mandate approved successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/mandates/{mandate_id}/reject", response_model=dict)
async def reject_mandate(
    mandate_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reject mandate"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        mandate = service.reject_mandate(
            mandate_id=mandate_id,
            rejection_reason=rejection_reason,
            rejected_by=current_user["user_id"]
        )
        
        if not mandate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mandate not found")
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate),
            message="Mandate rejected"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/mandates/{mandate_id}/cancel", response_model=dict)
async def cancel_mandate(
    mandate_id: int,
    cancellation_reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel active mandate"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        mandate = service.cancel_mandate(
            mandate_id=mandate_id,
            cancellation_reason=cancellation_reason,
            cancelled_by=current_user["user_id"]
        )
        
        if not mandate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mandate not found")
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate),
            message="Mandate cancelled successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/mandates/{mandate_id}", response_model=dict)
async def update_mandate(
    mandate_id: int,
    data: schemas.MandateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update mandate details"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude_unset=True)
        mandate = service.update_mandate(
            mandate_id=mandate_id,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not mandate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mandate not found")
        
        return success_response(
            data=schemas.MandateResponse.model_validate(mandate),
            message="Mandate updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Debit Transaction Endpoints
# ============================================

@router.post("/debits/initiate", response_model=dict)
async def initiate_debit(
    data: schemas.DebitInitiateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initiate NACH debit transaction"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        debit_data = data.model_dump()
        transaction = service.initiate_auto_debit(
            mandate_id=data.mandate_id,
            debit_data=debit_data,
            user_id=current_user["user_id"]
        )
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to initiate debit. Check mandate status and amount limits."
            )
        
        return success_response(
            data=schemas.DebitTransactionResponse.model_validate(transaction),
            message="Debit transaction initiated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/debits/bulk-initiate", response_model=dict)
async def bulk_initiate_debits(
    data: schemas.BulkDebitInitiateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initiate multiple NACH debit transactions"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        results = []
        errors = []
        successful = 0
        failed = 0
        
        for debit_request in data.debit_requests:
            try:
                debit_data = debit_request.model_dump()
                transaction = service.initiate_auto_debit(
                    mandate_id=debit_request.mandate_id,
                    debit_data=debit_data,
                    user_id=current_user["user_id"]
                )
                
                if transaction:
                    results.append(schemas.DebitTransactionResponse.model_validate(transaction))
                    successful += 1
                else:
                    failed += 1
                    errors.append({
                        "mandate_id": debit_request.mandate_id,
                        "error": "Unable to initiate debit"
                    })
            except Exception as e:
                failed += 1
                errors.append({
                    "mandate_id": debit_request.mandate_id,
                    "error": str(e)
                })
        
        batch_reference = data.batch_reference or f"BATCH-{date.today().strftime('%Y%m%d')}-{len(results)}"
        
        return success_response(
            data=schemas.BulkDebitResponse(
                total_requests=len(data.debit_requests),
                successful=successful,
                failed=failed,
                batch_reference=batch_reference,
                debit_transactions=results,
                errors=errors
            ),
            message=f"Bulk debit initiated: {successful} successful, {failed} failed"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/debits/{transaction_id}", response_model=dict)
async def get_debit_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get debit transaction by ID"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        transaction = service.get_debit_transaction(transaction_id)
        
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        
        return success_response(
            data=schemas.DebitTransactionResponse.model_validate(transaction)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/debits", response_model=dict)
async def list_debit_transactions(
    mandate_id: Optional[int] = None,
    loan_account_id: Optional[int] = None,
    status: Optional[schemas.DebitStatusEnum] = None,
    debit_date_from: Optional[date] = None,
    debit_date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List debit transactions with filters"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        transactions = service.list_debit_transactions(
            mandate_id=mandate_id,
            loan_account_id=loan_account_id,
            status=status,
            debit_date_from=debit_date_from,
            debit_date_to=debit_date_to
        )
        
        return success_response(
            data=[schemas.DebitTransactionResponse.model_validate(t) for t in transactions]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/debits/{transaction_id}/response", response_model=dict)
async def process_debit_response(
    transaction_id: int,
    data: schemas.DebitResponseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process debit response from bank/NPCI"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        response_data = data.model_dump()
        transaction = service.process_debit_response(
            transaction_reference=data.transaction_reference,
            response_data=response_data
        )
        
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        
        return success_response(
            data=schemas.DebitTransactionResponse.model_validate(transaction),
            message="Debit response processed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/debits/{transaction_id}/retry", response_model=dict)
async def retry_failed_debit(
    transaction_id: int,
    data: schemas.DebitRetryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retry failed debit transaction"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        new_transaction = service.retry_failed_debit(
            transaction_id=transaction_id,
            retry_date=data.retry_date,
            retry_reason=data.retry_reason,
            user_id=current_user["user_id"]
        )
        
        if not new_transaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to retry. Check transaction status and retry limit."
            )
        
        return success_response(
            data=schemas.DebitTransactionResponse.model_validate(new_transaction),
            message="Debit retry scheduled successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/debits/pending-retry", response_model=dict)
async def get_pending_retry_debits(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all debits pending retry"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        transactions = service.get_pending_retry_debits()
        
        return success_response(
            data=[schemas.DebitTransactionResponse.model_validate(t) for t in transactions]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Statistics & Dashboard Endpoints
# ============================================

@router.get("/statistics/mandates", response_model=dict)
async def get_mandate_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get mandate statistics"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        stats = service.get_mandate_statistics()
        
        return success_response(
            data=schemas.MandateStatistics(**stats)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/debits", response_model=dict)
async def get_debit_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get debit transaction statistics"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        stats = service.get_debit_statistics(
            date_from=date_from,
            date_to=date_to
        )
        
        return success_response(
            data=schemas.DebitStatistics(**stats)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard", response_model=dict)
async def get_nach_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive NACH dashboard data"""
    try:
        service = NACHService(db, current_user["tenant_id"])
        
        # Get all dashboard components
        mandate_stats = service.get_mandate_statistics()
        debit_stats = service.get_debit_statistics()
        
        # Get recent failures
        recent_failures = service.list_debit_transactions(
            status=schemas.DebitStatusEnum.FAILED
        )[:10]
        
        # Get expiring mandates (30 days)
        from datetime import timedelta
        expiring_date = date.today() + timedelta(days=30)
        expiring_mandates = service.list_mandates(
            expiring_before=expiring_date,
            status=schemas.MandateStatusEnum.ACTIVE
        )
        
        # Get pending approvals
        pending_approvals = service.list_mandates(
            status=schemas.MandateStatusEnum.PENDING_BANK
        )
        
        dashboard = schemas.NACHDashboard(
            mandate_statistics=schemas.MandateStatistics(**mandate_stats),
            debit_statistics=schemas.DebitStatistics(**debit_stats),
            recent_failures=[schemas.DebitTransactionResponse.model_validate(t) for t in recent_failures],
            expiring_mandates=[schemas.MandateResponse.model_validate(m) for m in expiring_mandates],
            pending_approvals=[schemas.MandateResponse.model_validate(m) for m in pending_approvals]
        )
        
        return success_response(data=dashboard)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# Webhook Endpoints (for NPCI integration)
# ============================================

@router.post("/webhooks/enach-status")
async def enach_webhook(
    data: schemas.ENACHWebhookPayload,
    db: Session = Depends(get_db)
):
    """Webhook endpoint for eNACH status updates from NPCI"""
    try:
        # Note: In production, add webhook signature verification here
        service = NACHService(db, tenant_id=1)  # Get tenant from webhook signature
        
        # Process the webhook
        # This would update mandate status based on NPCI response
        # Implementation depends on NPCI specification
        
        return success_response(message="Webhook processed successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/webhooks/debit-status")
async def debit_webhook(
    data: schemas.DebitWebhookPayload,
    db: Session = Depends(get_db)
):
    """Webhook endpoint for debit status updates from NPCI"""
    try:
        # Note: In production, add webhook signature verification here
        service = NACHService(db, tenant_id=1)  # Get tenant from webhook signature
        
        # Process the webhook
        response_data = {
            "transaction_reference": data.transaction_reference,
            "status": data.status,
            "bank_reference": data.bank_reference,
            "utr_number": data.utr_number,
            "failure_reason": data.failure_reason,
            "processed_date": data.processed_date
        }
        
        service.process_debit_response(
            transaction_reference=data.transaction_reference,
            response_data=response_data
        )
        
        return success_response(message="Webhook processed successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
