"""
Loan Insurance Router
API endpoints for loan insurance tracking operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.lms.insurance_service import InsuranceService
from backend.services.lms import insurance_schemas as schemas


router = APIRouter(prefix="/loan-insurance", tags=["Loan Insurance"])


# ============================================
# Insurance Policy Endpoints
# ============================================

@router.post("/policies", response_model=dict)
async def create_insurance_policy(
    data: schemas.InsurancePolicyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new insurance policy for loan"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        policy_data = data.model_dump()
        policy = service.create_insurance_policy(
            policy_data=policy_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.InsurancePolicyResponse.model_validate(policy),
            message="Insurance policy created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/policies/{policy_id}", response_model=dict)
async def get_insurance_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get insurance policy by ID"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        policy = service.get_insurance_policy(policy_id)
        
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(
            data=schemas.InsurancePolicyResponse.model_validate(policy)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/policies", response_model=dict)
async def list_insurance_policies(
    loan_account_id: Optional[int] = None,
    insurance_type: Optional[schemas.InsuranceTypeEnum] = None,
    status: Optional[schemas.InsuranceStatusEnum] = None,
    is_mandatory: Optional[bool] = None,
    expiring_before: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List insurance policies with filters"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        policies = service.list_insurance_policies(
            loan_account_id=loan_account_id,
            insurance_type=insurance_type,
            status=status,
            is_mandatory=is_mandatory,
            expiring_before=expiring_before
        )
        
        return success_response(
            data=[schemas.InsurancePolicyResponse.model_validate(p) for p in policies]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/policies/loan/{loan_account_id}", response_model=dict)
async def get_loan_insurance_policies(
    loan_account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all insurance policies for a loan account"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        policies = service.list_insurance_policies(loan_account_id=loan_account_id)
        
        return success_response(
            data=[schemas.InsurancePolicyResponse.model_validate(p) for p in policies]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/policies/{policy_id}", response_model=dict)
async def update_insurance_policy(
    policy_id: int,
    data: schemas.InsurancePolicyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update insurance policy details"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude_unset=True)
        policy = service.update_insurance_policy(
            policy_id=policy_id,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(
            data=schemas.InsurancePolicyResponse.model_validate(policy),
            message="Insurance policy updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Policy Renewal Endpoints
# ============================================

@router.post("/policies/{policy_id}/renew", response_model=dict)
async def renew_insurance_policy(
    policy_id: int,
    data: schemas.InsurancePolicyRenewal,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Renew insurance policy"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        renewal_data = data.model_dump()
        policy = service.renew_insurance_policy(
            policy_id=policy_id,
            renewal_data=renewal_data,
            user_id=current_user["user_id"]
        )
        
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(
            data=schemas.InsurancePolicyResponse.model_validate(policy),
            message="Insurance policy renewed successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/policies/{policy_id}/cancel", response_model=dict)
async def cancel_insurance_policy(
    policy_id: int,
    data: schemas.InsurancePolicyCancellation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cancel insurance policy"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        cancellation_data = data.model_dump()
        policy = service.cancel_insurance_policy(
            policy_id=policy_id,
            cancellation_data=cancellation_data,
            user_id=current_user["user_id"]
        )
        
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(
            data=schemas.InsurancePolicyResponse.model_validate(policy),
            message="Insurance policy cancelled"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Expiry & Renewal Reminder Endpoints
# ============================================

@router.get("/policies/expiring/{days}", response_model=dict)
async def get_expiring_policies(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get insurance policies expiring in next X days"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        policies = service.get_expiring_policies(days)
        
        from datetime import timedelta
        alerts = [
            schemas.InsurancePolicyExpiryAlert(
                id=p.id,
                loan_account_id=p.loan_account_id,
                policy_number=p.policy_number,
                insurance_type=p.insurance_type,
                insurance_provider=p.insurance_provider,
                policy_end_date=p.policy_end_date,
                days_to_expiry=(p.policy_end_date - date.today()).days,
                sum_assured=p.sum_assured,
                premium_amount=p.premium_amount,
                is_mandatory=p.is_mandatory
            ) for p in policies
        ]
        
        return success_response(data=alerts)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/policies/{policy_id}/send-renewal-reminder", response_model=dict)
async def send_renewal_reminder(
    policy_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send renewal reminder for expiring policy"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        result = service.send_renewal_reminder(policy_id)
        
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance policy not found")
        
        return success_response(message="Renewal reminder sent successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Premium Payment Endpoints
# ============================================

@router.post("/premiums", response_model=dict)
async def create_premium_payment(
    data: schemas.PremiumPaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create premium payment record"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        payment_data = data.model_dump()
        payment = service.create_premium_payment(
            payment_data=payment_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.PremiumPaymentResponse.model_validate(payment),
            message="Premium payment record created"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/premiums/{payment_id}", response_model=dict)
async def update_premium_payment(
    payment_id: int,
    data: schemas.PremiumPaymentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update premium payment with payment details"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        payment_data = data.model_dump()
        payment = service.update_premium_payment(
            payment_id=payment_id,
            payment_data=payment_data,
            user_id=current_user["user_id"]
        )
        
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Premium payment not found")
        
        return success_response(
            data=schemas.PremiumPaymentResponse.model_validate(payment),
            message="Premium payment updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/premiums/policy/{policy_id}", response_model=dict)
async def get_policy_premiums(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all premium payments for a policy"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        payments = service.get_policy_premiums(policy_id)
        
        return success_response(
            data=[schemas.PremiumPaymentResponse.model_validate(p) for p in payments]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/premiums/overdue", response_model=dict)
async def get_overdue_premiums(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all overdue premium payments"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        payments = service.get_overdue_premiums()
        
        alerts = [
            schemas.PremiumOverdueAlert(
                id=p.id,
                insurance_policy_id=p.insurance_policy_id,
                loan_account_id=0,  # Would fetch from policy
                policy_number="",
                due_date=p.due_date,
                overdue_days=(date.today() - p.due_date).days,
                premium_amount=p.premium_amount
            ) for p in payments
        ]
        
        return success_response(data=alerts)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Insurance Claim Endpoints
# ============================================

@router.post("/claims", response_model=dict)
async def create_insurance_claim(
    data: schemas.InsuranceClaimCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new insurance claim"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        claim_data = data.model_dump()
        claim = service.create_insurance_claim(
            claim_data=claim_data,
            user_id=current_user["user_id"]
        )
        
        return success_response(
            data=schemas.InsuranceClaimResponse.model_validate(claim),
            message="Insurance claim created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/claims/{claim_id}", response_model=dict)
async def get_insurance_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get insurance claim by ID"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        claim = service.get_insurance_claim(claim_id)
        
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance claim not found")
        
        return success_response(
            data=schemas.InsuranceClaimResponse.model_validate(claim)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/claims", response_model=dict)
async def list_insurance_claims(
    insurance_policy_id: Optional[int] = None,
    loan_account_id: Optional[int] = None,
    claim_type: Optional[schemas.ClaimTypeEnum] = None,
    claim_status: Optional[schemas.ClaimStatusEnum] = None,
    incident_date_from: Optional[date] = None,
    incident_date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List insurance claims with filters"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        claims = service.list_insurance_claims(
            insurance_policy_id=insurance_policy_id,
            loan_account_id=loan_account_id,
            claim_type=claim_type,
            claim_status=claim_status,
            incident_date_from=incident_date_from,
            incident_date_to=incident_date_to
        )
        
        return success_response(
            data=[schemas.InsuranceClaimResponse.model_validate(c) for c in claims]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/claims/{claim_id}", response_model=dict)
async def update_insurance_claim(
    claim_id: int,
    data: schemas.InsuranceClaimUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update insurance claim details"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        updates = data.model_dump(exclude_unset=True)
        claim = service.update_insurance_claim(
            claim_id=claim_id,
            updates=updates,
            user_id=current_user["user_id"]
        )
        
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance claim not found")
        
        return success_response(
            data=schemas.InsuranceClaimResponse.model_validate(claim),
            message="Insurance claim updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/claims/{claim_id}/review", response_model=dict)
async def review_insurance_claim(
    claim_id: int,
    data: schemas.InsuranceClaimReview,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Review and approve/reject insurance claim"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        review_data = data.model_dump()
        claim = service.review_insurance_claim(
            claim_id=claim_id,
            review_data=review_data,
            reviewed_by=current_user["user_id"]
        )
        
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance claim not found")
        
        return success_response(
            data=schemas.InsuranceClaimResponse.model_validate(claim),
            message=f"Claim {data.status.value} successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/claims/{claim_id}/payment", response_model=dict)
async def record_claim_payment(
    claim_id: int,
    data: schemas.InsuranceClaimPayment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Record claim payment"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        payment_data = data.model_dump()
        claim = service.record_claim_payment(
            claim_id=claim_id,
            payment_data=payment_data,
            user_id=current_user["user_id"]
        )
        
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance claim not found")
        
        return success_response(
            data=schemas.InsuranceClaimResponse.model_validate(claim),
            message="Claim payment recorded successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/claims/pending/review", response_model=dict)
async def get_pending_claims(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all claims pending review"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        claims = service.get_pending_claims()
        
        return success_response(
            data=[schemas.InsuranceClaimResponse.model_validate(c) for c in claims]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Statistics & Dashboard Endpoints
# ============================================

@router.get("/statistics", response_model=dict)
async def get_insurance_statistics(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get overall insurance statistics"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        stats = service.get_insurance_statistics(
            from_date=from_date,
            to_date=to_date
        )
        
        return success_response(
            data=schemas.InsuranceStatistics(**stats)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/dashboard", response_model=dict)
async def get_insurance_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive insurance dashboard data"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        # Get all dashboard components
        stats = service.get_insurance_statistics()
        expiring_policies = service.get_expiring_policies(30)
        overdue_premiums = service.get_overdue_premiums()
        pending_claims = service.get_pending_claims()
        
        # Get recent renewals (last 30 days)
        from datetime import timedelta
        recent_date = date.today() - timedelta(days=30)
        recent_renewals = service.list_insurance_policies()[:10]  # Get top 10 recent
        
        # Convert to alert schemas
        from datetime import timedelta
        expiring_alerts = [
            schemas.InsurancePolicyExpiryAlert(
                id=p.id,
                loan_account_id=p.loan_account_id,
                policy_number=p.policy_number,
                insurance_type=p.insurance_type,
                insurance_provider=p.insurance_provider,
                policy_end_date=p.policy_end_date,
                days_to_expiry=(p.policy_end_date - date.today()).days,
                sum_assured=p.sum_assured,
                premium_amount=p.premium_amount,
                is_mandatory=p.is_mandatory
            ) for p in expiring_policies
        ]
        
        overdue_alerts = [
            schemas.PremiumOverdueAlert(
                id=p.id,
                insurance_policy_id=p.insurance_policy_id,
                loan_account_id=0,
                policy_number="",
                due_date=p.due_date,
                overdue_days=(date.today() - p.due_date).days,
                premium_amount=p.premium_amount
            ) for p in overdue_premiums[:10]
        ]
        
        dashboard = schemas.InsuranceDashboard(
            statistics=schemas.InsuranceStatistics(**stats),
            expiring_policies=expiring_alerts,
            overdue_premiums=overdue_alerts,
            pending_claims=[schemas.InsuranceClaimResponse.model_validate(c) for c in pending_claims[:10]],
            recent_renewals=[schemas.InsurancePolicyResponse.model_validate(p) for p in recent_renewals]
        )
        
        return success_response(data=dashboard)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/coverage-report", response_model=dict)
async def get_coverage_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get insurance coverage report for loan portfolio"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        report = service.get_coverage_report()
        
        return success_response(
            data=schemas.InsuranceCoverageReport(**report)
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# ============================================
# Bulk Operations Endpoints
# ============================================

@router.post("/bulk/renewal", response_model=dict)
async def bulk_renew_policies(
    data: schemas.BulkRenewalRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Bulk renew insurance policies"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        results = []
        errors = []
        successful = 0
        failed = 0
        
        for policy_id in data.policy_ids:
            try:
                renewal_data = {
                    "policy_number": f"RENEWED-{policy_id}",
                    "policy_start_date": data.renewal_start_date,
                    "policy_end_date": data.renewal_end_date,
                    "sum_assured": 0,  # Would fetch from existing policy
                    "premium_amount": 0,  # Would calculate with increase
                    "renewal_remarks": f"Bulk renewal: {data.bulk_renewal_reference}"
                }
                
                policy = service.renew_insurance_policy(
                    policy_id=policy_id,
                    renewal_data=renewal_data,
                    user_id=current_user["user_id"]
                )
                
                if policy:
                    results.append(schemas.InsurancePolicyResponse.model_validate(policy))
                    successful += 1
                else:
                    failed += 1
                    errors.append({
                        "policy_id": policy_id,
                        "error": "Unable to renew policy"
                    })
                    
            except Exception as e:
                failed += 1
                errors.append({
                    "policy_id": policy_id,
                    "error": str(e)
                })
        
        return success_response(
            data=schemas.BulkRenewalResponse(
                total_policies=len(data.policy_ids),
                successful=successful,
                failed=failed,
                bulk_renewal_reference=data.bulk_renewal_reference,
                renewed_policies=results,
                errors=errors
            ),
            message=f"Bulk renewal completed: {successful} successful, {failed} failed"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bulk/send-renewal-reminders", response_model=dict)
async def bulk_send_renewal_reminders(
    days: int = 30,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send renewal reminders for all expiring policies"""
    try:
        service = InsuranceService(db, current_user["tenant_id"])
        
        # Get expiring policies
        expiring_policies = service.get_expiring_policies(days)
        
        sent_count = 0
        failed_count = 0
        
        for policy in expiring_policies:
            try:
                service.send_renewal_reminder(policy.id)
                sent_count += 1
            except Exception:
                failed_count += 1
        
        return success_response(
            data={
                "total_policies": len(expiring_policies),
                "reminders_sent": sent_count,
                "failed": failed_count
            },
            message=f"Bulk reminders sent: {sent_count} successful, {failed_count} failed"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
