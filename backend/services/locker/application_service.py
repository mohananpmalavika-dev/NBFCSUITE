"""
Locker Application Service

Handles locker rental application lifecycle including:
- Application submission and validation
- Priority score calculation
- Document verification
- Multi-level approval workflow
- Waiting list integration
- Allocation processing
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerApplication,
    LockerWaitingList,
    LockerMaster,
    LockerAllocation,
    LockerCustomer,
    LockerKYC
)
from backend.services.locker.schemas import (
    LockerApplicationCreate,
    LockerApplicationUpdate,
    LockerApplicationResponse,
    ApplicationReviewRequest,
    ApplicationApprovalRequest,
    ApplicationAllocationRequest,
    ApplicationFilter,
    ApplicationStatus,
    ApplicationStage,
    LockerStatus,
    ApplicationAnalytics
)
from backend.shared.utils import generate_reference_number


class ApplicationService:
    """Service for managing locker applications"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_application(
        self,
        data: LockerApplicationCreate
    ) -> LockerApplication:
        """
        Create new locker application with priority calculation
        """
        # Generate application number
        application_number = generate_reference_number("LA")
        
        # Calculate priority score
        priority_score, priority_factors = self._calculate_priority_score(data)
        
        # Create application
        application = LockerApplication(
            application_number=application_number,
            tenant_id=self.tenant_id,
            customer_id=data.customer_id,
            locker_customer_id=data.locker_customer_id,
            branch_id=data.branch_id,
            application_date=data.application_date,
            application_type=data.application_type,
            preferred_locker_size=data.preferred_locker_size,
            alternate_size_1=data.alternate_size_1,
            alternate_size_2=data.alternate_size_2,
            preferred_location=data.preferred_location,
            preferred_locker_id=data.preferred_locker_id,
            purpose_of_locker=data.purpose_of_locker,
            purpose_details=data.purpose_details,
            estimated_value_of_contents=data.estimated_value_of_contents,
            insurance_required=data.insurance_required,
            insurance_coverage_amount=data.insurance_coverage_amount,
            proposed_rent_frequency=data.proposed_rent_frequency,
            willing_to_pay_advance=data.willing_to_pay_advance,
            advance_payment_months=data.advance_payment_months,
            is_existing_customer=data.is_existing_customer,
            existing_customer_since=data.existing_customer_since,
            customer_category=data.customer_category,
            deposit_with_bank=data.deposit_with_bank,
            loan_accounts=data.loan_accounts,
            credit_score=data.credit_score,
            priority_score=priority_score,
            priority_reason=priority_factors,
            status=ApplicationStatus.SUBMITTED,
            current_stage=ApplicationStage.DOCUMENT_VERIFICATION,
            submitted_by=self.user_id,
            special_requirements=data.special_requirements,
            remarks=data.remarks,
            application_valid_till=data.application_date + timedelta(days=90),
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        
        # Check if locker is available, otherwise suggest waiting list
        await self._check_availability_and_notify(application)
        
        return application
    
    def _calculate_priority_score(
        self,
        data: LockerApplicationCreate
    ) -> Tuple[int, str]:
        """
        Calculate priority score based on multiple factors
        
        Priority Rules:
        - Existing customer: +30 points
        - Senior citizen: +25 points
        - Staff member: +20 points
        - Premium customer: +15 points
        - High deposit (>5L): +15 points
        - Medium deposit (2-5L): +10 points
        - Multiple loan accounts: +5 points per account (max 15)
        - Good credit score (>750): +10 points
        - Willing to pay advance: +5 points
        """
        score = 0
        factors = []
        
        # Base priority
        score += 10
        factors.append("Base priority: 10")
        
        # Existing customer bonus
        if data.is_existing_customer:
            score += 30
            factors.append("Existing customer: +30")
            
            # Customer relationship duration
            if data.existing_customer_since:
                years = (date.today() - data.existing_customer_since).days / 365
                if years >= 5:
                    score += 10
                    factors.append(f"Long relationship ({int(years)}y): +10")
        
        # Customer category bonuses
        if data.customer_category == "senior_citizen":
            score += 25
            factors.append("Senior citizen: +25")
        elif data.customer_category == "staff":
            score += 20
            factors.append("Staff member: +20")
        elif data.customer_category == "premium":
            score += 15
            factors.append("Premium customer: +15")
        elif data.customer_category == "vip":
            score += 20
            factors.append("VIP customer: +20")
        
        # Deposit size bonus
        if data.deposit_with_bank:
            if data.deposit_with_bank >= 500000:  # 5 lakhs
                score += 15
                factors.append("High deposits (>5L): +15")
            elif data.deposit_with_bank >= 200000:  # 2 lakhs
                score += 10
                factors.append("Medium deposits (2-5L): +10")
            elif data.deposit_with_bank >= 50000:
                score += 5
                factors.append("Deposits (>50k): +5")
        
        # Loan accounts bonus
        if data.loan_accounts:
            loan_bonus = min(data.loan_accounts * 5, 15)
            score += loan_bonus
            factors.append(f"Loan accounts ({data.loan_accounts}): +{loan_bonus}")
        
        # Credit score bonus
        if data.credit_score:
            if data.credit_score >= 750:
                score += 10
                factors.append("Excellent credit (>750): +10")
            elif data.credit_score >= 650:
                score += 5
                factors.append("Good credit (>650): +5")
        
        # Advance payment willingness
        if data.willing_to_pay_advance:
            score += 5
            factors.append("Advance payment: +5")
        
        # High value storage (insurance required)
        if data.insurance_required and data.insurance_coverage_amount:
            if data.insurance_coverage_amount >= 1000000:  # 10 lakhs
                score += 5
                factors.append("High value storage: +5")
        
        return score, "; ".join(factors)
    
    async def _check_availability_and_notify(
        self,
        application: LockerApplication
    ) -> None:
        """Check locker availability and notify customer"""
        # Check if requested locker is available
        available_lockers = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.branch_id == application.branch_id,
                LockerMaster.locker_size == application.preferred_locker_size,
                LockerMaster.status == LockerStatus.AVAILABLE,
                LockerMaster.is_available == True,
                LockerMaster.is_deleted == False
            )
        ).count()
        
        if available_lockers == 0:
            # No lockers available, suggest waiting list
            application.status = ApplicationStatus.WAITING_LIST
            application.added_to_waiting_list = True
            application.follow_up_required = True
            application.follow_up_date = date.today() + timedelta(days=7)
            self.db.commit()
    
    async def get_application(
        self,
        application_id: uuid.UUID
    ) -> Optional[LockerApplication]:
        """Get application by ID"""
        return self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.id == application_id,
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.is_deleted == False
            )
        ).first()
    
    async def get_application_by_number(
        self,
        application_number: str
    ) -> Optional[LockerApplication]:
        """Get application by application number"""
        return self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.application_number == application_number,
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.is_deleted == False
            )
        ).first()
    
    async def list_applications(
        self,
        filters: ApplicationFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[LockerApplication], int]:
        """List applications with filters and pagination"""
        query = self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.customer_id:
            query = query.filter(LockerApplication.customer_id == filters.customer_id)
        
        if filters.branch_id:
            query = query.filter(LockerApplication.branch_id == filters.branch_id)
        
        if filters.application_type:
            query = query.filter(LockerApplication.application_type == filters.application_type)
        
        if filters.status:
            query = query.filter(LockerApplication.status == filters.status)
        
        if filters.current_stage:
            query = query.filter(LockerApplication.current_stage == filters.current_stage)
        
        if filters.preferred_locker_size:
            query = query.filter(LockerApplication.preferred_locker_size == filters.preferred_locker_size)
        
        if filters.application_date_from:
            query = query.filter(LockerApplication.application_date >= filters.application_date_from)
        
        if filters.application_date_to:
            query = query.filter(LockerApplication.application_date <= filters.application_date_to)
        
        # Get total count
        total = query.count()
        
        # Order by priority score (highest first) and application date
        query = query.order_by(
            desc(LockerApplication.priority_score),
            LockerApplication.application_date
        )
        
        # Pagination
        applications = query.offset(skip).limit(limit).all()
        
        return applications, total
    
    async def update_application(
        self,
        application_id: uuid.UUID,
        data: LockerApplicationUpdate
    ) -> Optional[LockerApplication]:
        """Update application details"""
        application = await self.get_application(application_id)
        if not application:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)
        
        application.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def review_application(
        self,
        application_id: uuid.UUID,
        review: ApplicationReviewRequest
    ) -> Optional[LockerApplication]:
        """
        Review application and move to next stage
        """
        application = await self.get_application(application_id)
        if not application:
            return None
        
        # Update review details
        application.reviewed_by = self.user_id
        application.review_date = date.today()
        application.review_remarks = review.review_remarks
        application.kyc_verified = review.kyc_verified
        
        # Move to next stage
        if review.move_to_stage:
            application.current_stage = review.move_to_stage
        else:
            # Auto-progress to next stage
            if application.current_stage == ApplicationStage.DOCUMENT_VERIFICATION:
                if review.kyc_verified:
                    application.current_stage = ApplicationStage.CREDIT_CHECK
            elif application.current_stage == ApplicationStage.CREDIT_CHECK:
                if review.credit_check_done:
                    application.current_stage = ApplicationStage.MANAGER_REVIEW
            elif application.current_stage == ApplicationStage.MANAGER_REVIEW:
                application.current_stage = ApplicationStage.FINAL_APPROVAL
        
        # Update status
        if application.current_stage == ApplicationStage.FINAL_APPROVAL:
            application.status = ApplicationStatus.PENDING_APPROVAL
        else:
            application.status = ApplicationStatus.UNDER_REVIEW
        
        application.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def approve_application(
        self,
        application_id: uuid.UUID,
        approval: ApplicationApprovalRequest
    ) -> Optional[LockerApplication]:
        """
        Approve or reject application
        """
        application = await self.get_application(application_id)
        if not application:
            return None
        
        if approval.approved:
            # Approve application
            application.approved_by = self.user_id
            application.approval_date = date.today()
            application.approval_remarks = approval.approval_remarks
            application.approval_level += 1
            application.status = ApplicationStatus.APPROVED
            application.current_stage = ApplicationStage.ALLOCATION
            
            # Check if locker is available for allocation
            available = await self._check_locker_availability(application)
            
            if not available and approval.add_to_waiting_list:
                # Add to waiting list
                application.status = ApplicationStatus.WAITING_LIST
                application.added_to_waiting_list = True
                application.waiting_list_date = date.today()
        else:
            # Reject application
            application.rejected_by = self.user_id
            application.rejection_date = date.today()
            application.rejection_reason = approval.rejection_reason
            application.status = ApplicationStatus.REJECTED
        
        application.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def _check_locker_availability(
        self,
        application: LockerApplication
    ) -> bool:
        """Check if requested locker size is available"""
        available_count = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.branch_id == application.branch_id,
                or_(
                    LockerMaster.locker_size == application.preferred_locker_size,
                    LockerMaster.locker_size == application.alternate_size_1,
                    LockerMaster.locker_size == application.alternate_size_2
                ),
                LockerMaster.status == LockerStatus.AVAILABLE,
                LockerMaster.is_available == True,
                LockerMaster.is_deleted == False
            )
        ).count()
        
        return available_count > 0
    
    async def allocate_locker(
        self,
        application_id: uuid.UUID,
        allocation_data: ApplicationAllocationRequest
    ) -> Optional[LockerApplication]:
        """
        Allocate locker to approved application
        """
        application = await self.get_application(application_id)
        if not application:
            return None
        
        if application.status != ApplicationStatus.APPROVED:
            raise ValueError("Application must be approved before allocation")
        
        # Verify locker is available
        locker = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.id == allocation_data.locker_id,
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.status == LockerStatus.AVAILABLE,
                LockerMaster.is_available == True,
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if not locker:
            raise ValueError("Locker is not available for allocation")
        
        # Update application
        application.allocated_locker_id = allocation_data.locker_id
        application.allocation_date = allocation_data.allocation_date
        application.status = ApplicationStatus.ALLOCATED
        
        # Update locker status
        locker.status = LockerStatus.ALLOCATED
        locker.is_available = False
        locker.updated_by = self.user_id
        
        application.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def cancel_application(
        self,
        application_id: uuid.UUID,
        reason: str
    ) -> Optional[LockerApplication]:
        """Cancel application"""
        application = await self.get_application(application_id)
        if not application:
            return None
        
        application.status = ApplicationStatus.CANCELLED
        application.rejection_reason = reason
        application.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(application)
        
        return application
    
    async def get_pending_approvals(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> List[LockerApplication]:
        """Get applications pending approval"""
        query = self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.status == ApplicationStatus.PENDING_APPROVAL,
                LockerApplication.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerApplication.branch_id == branch_id)
        
        return query.order_by(
            desc(LockerApplication.priority_score),
            LockerApplication.application_date
        ).all()
    
    async def get_applications_by_customer(
        self,
        customer_id: uuid.UUID
    ) -> List[LockerApplication]:
        """Get all applications for a customer"""
        return self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.customer_id == customer_id,
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.is_deleted == False
            )
        ).order_by(desc(LockerApplication.application_date)).all()
    
    async def check_expired_applications(self) -> List[LockerApplication]:
        """Check and mark expired applications"""
        expired = self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.application_valid_till < date.today(),
                LockerApplication.status.in_([
                    ApplicationStatus.SUBMITTED,
                    ApplicationStatus.UNDER_REVIEW,
                    ApplicationStatus.PENDING_APPROVAL
                ]),
                LockerApplication.is_expired == False,
                LockerApplication.is_deleted == False
            )
        ).all()
        
        for app in expired:
            app.is_expired = True
            app.status = ApplicationStatus.EXPIRED
            app.updated_by = self.user_id
        
        if expired:
            self.db.commit()
        
        return expired
    
    async def get_analytics(
        self,
        branch_id: Optional[uuid.UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> ApplicationAnalytics:
        """Get application analytics"""
        query = self.db.query(LockerApplication).filter(
            and_(
                LockerApplication.tenant_id == self.tenant_id,
                LockerApplication.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerApplication.branch_id == branch_id)
        
        if date_from:
            query = query.filter(LockerApplication.application_date >= date_from)
        
        if date_to:
            query = query.filter(LockerApplication.application_date <= date_to)
        
        total_applications = query.count()
        
        # By status
        by_status = {}
        status_counts = query.with_entities(
            LockerApplication.status,
            func.count(LockerApplication.id)
        ).group_by(LockerApplication.status).all()
        
        for status, count in status_counts:
            by_status[status] = count
        
        # By type
        by_type = {}
        type_counts = query.with_entities(
            LockerApplication.application_type,
            func.count(LockerApplication.id)
        ).group_by(LockerApplication.application_type).all()
        
        for app_type, count in type_counts:
            by_type[app_type] = count
        
        # Status-specific counts
        pending_review = query.filter(
            LockerApplication.status == ApplicationStatus.UNDER_REVIEW
        ).count()
        
        pending_approval = query.filter(
            LockerApplication.status == ApplicationStatus.PENDING_APPROVAL
        ).count()
        
        approved_count = query.filter(
            LockerApplication.status == ApplicationStatus.APPROVED
        ).count()
        
        rejected_count = query.filter(
            LockerApplication.status == ApplicationStatus.REJECTED
        ).count()
        
        # Average processing time
        completed = query.filter(
            or_(
                LockerApplication.status == ApplicationStatus.APPROVED,
                LockerApplication.status == ApplicationStatus.ALLOCATED
            )
        ).all()
        
        avg_processing_days = 0
        if completed:
            total_days = sum([
                (app.approval_date - app.application_date).days
                for app in completed
                if app.approval_date
            ])
            avg_processing_days = total_days // len(completed) if completed else 0
        
        return ApplicationAnalytics(
            total_applications=total_applications,
            by_status=by_status,
            by_type=by_type,
            pending_review=pending_review,
            pending_approval=pending_approval,
            approved_count=approved_count,
            rejected_count=rejected_count,
            average_processing_days=avg_processing_days
        )
    
    async def bulk_approve_applications(
        self,
        application_ids: List[uuid.UUID],
        approval_remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk approve multiple applications"""
        successful = []
        failed = []
        
        for app_id in application_ids:
            try:
                approval = ApplicationApprovalRequest(
                    approved=True,
                    approval_remarks=approval_remarks,
                    add_to_waiting_list=True
                )
                result = await self.approve_application(app_id, approval)
                if result:
                    successful.append(str(app_id))
                else:
                    failed.append({"id": str(app_id), "reason": "Not found"})
            except Exception as e:
                failed.append({"id": str(app_id), "reason": str(e)})
        
        return {
            "total": len(application_ids),
            "successful": len(successful),
            "failed": len(failed),
            "successful_ids": successful,
            "failed_items": failed
        }
    
    async def send_notification(
        self,
        application_id: uuid.UUID,
        notification_type: str
    ) -> bool:
        """Send notification to customer about application status"""
        application = await self.get_application(application_id)
        if not application:
            return False
        
        # Update notification tracking
        application.notification_sent = True
        application.last_notification_date = date.today()
        
        self.db.commit()
        
        # TODO: Integrate with notification service (email/SMS)
        return True
    
    async def get_application_history(
        self,
        application_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """Get application processing history"""
        application = await self.get_application(application_id)
        if not application:
            return []
        
        history = []
        
        # Submission
        history.append({
            "date": application.application_date,
            "stage": "Submitted",
            "user": str(application.submitted_by) if application.submitted_by else None,
            "remarks": "Application submitted"
        })
        
        # Review
        if application.review_date:
            history.append({
                "date": application.review_date,
                "stage": "Reviewed",
                "user": str(application.reviewed_by) if application.reviewed_by else None,
                "remarks": application.review_remarks
            })
        
        # Approval/Rejection
        if application.approval_date:
            history.append({
                "date": application.approval_date,
                "stage": "Approved",
                "user": str(application.approved_by) if application.approved_by else None,
                "remarks": application.approval_remarks
            })
        elif application.rejection_date:
            history.append({
                "date": application.rejection_date,
                "stage": "Rejected",
                "user": str(application.rejected_by) if application.rejected_by else None,
                "remarks": application.rejection_reason
            })
        
        # Allocation
        if application.allocation_date:
            history.append({
                "date": application.allocation_date,
                "stage": "Allocated",
                "user": str(application.updated_by) if application.updated_by else None,
                "remarks": f"Locker allocated: {application.allocated_locker_id}"
            })
        
        return history
