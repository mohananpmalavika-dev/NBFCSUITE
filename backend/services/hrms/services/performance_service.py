"""
Performance Management Service
Business logic for Goal Setting, Appraisals, 360 Feedback, Ratings & IDP
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from fastapi import HTTPException, status

from backend.shared.database.hrms_models import (
    AppraisalCycle, PerformanceGoal, EmployeeAppraisal,
    FeedbackRequest, FeedbackResponse, PerformanceIncrement,
    IndividualDevelopmentPlan, DevelopmentActivity,
    Employee, GoalStatus, AppraisalStatus, AppraisalCycleStatus,
    FeedbackStatus, IDPStatus
)
from backend.services.hrms.schemas.performance_schemas import (
    AppraisalCycleCreate, AppraisalCycleUpdate,
    PerformanceGoalCreate, PerformanceGoalUpdate,
    EmployeeAppraisalCreate, SelfAssessmentSubmit, ManagerReviewSubmit, HRReviewSubmit,
    FeedbackRequestCreate, FeedbackResponseSubmit,
    PerformanceIncrementCreate, PerformanceIncrementUpdate,
    IndividualDevelopmentPlanCreate, IndividualDevelopmentPlanUpdate,
    DevelopmentActivityCreate, DevelopmentActivityUpdate
)


class PerformanceManagementService:
    """Service class for performance management operations"""
    
    def __init__(self, db: Session, tenant_id: UUID, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # APPRAISAL CYCLE OPERATIONS
    # ========================================================================
    
    def create_appraisal_cycle(self, data: AppraisalCycleCreate) -> AppraisalCycle:
        """Create a new appraisal cycle"""
        # Check if cycle code already exists
        existing = self.db.query(AppraisalCycle).filter(
            and_(
                AppraisalCycle.tenant_id == self.tenant_id,
                AppraisalCycle.cycle_code == data.cycle_code,
                AppraisalCycle.is_active == True
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Appraisal cycle with code '{data.cycle_code}' already exists"
            )
        
        cycle = AppraisalCycle(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(cycle)
        self.db.commit()
        self.db.refresh(cycle)
        return cycle
    
    def get_appraisal_cycle(self, cycle_id: UUID) -> Optional[AppraisalCycle]:
        """Get appraisal cycle by ID"""
        return self.db.query(AppraisalCycle).filter(
            and_(
                AppraisalCycle.id == cycle_id,
                AppraisalCycle.tenant_id == self.tenant_id,
                AppraisalCycle.is_active == True
            )
        ).first()
    
    def list_appraisal_cycles(
        self,
        status: Optional[AppraisalCycleStatus] = None,
        fiscal_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[AppraisalCycle], int]:
        """List appraisal cycles with filters"""
        query = self.db.query(AppraisalCycle).filter(
            and_(
                AppraisalCycle.tenant_id == self.tenant_id,
                AppraisalCycle.is_active == True
            )
        )
        
        if status:
            query = query.filter(AppraisalCycle.status == status)
        if fiscal_year:
            query = query.filter(AppraisalCycle.fiscal_year == fiscal_year)
        
        total = query.count()
        cycles = query.order_by(AppraisalCycle.created_at.desc()).offset(skip).limit(limit).all()
        
        return cycles, total
    
    def update_appraisal_cycle(self, cycle_id: UUID, data: AppraisalCycleUpdate) -> AppraisalCycle:
        """Update appraisal cycle"""
        cycle = self.get_appraisal_cycle(cycle_id)
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal cycle not found"
            )
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cycle, field, value)
        
        cycle.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(cycle)
        return cycle
    
    def delete_appraisal_cycle(self, cycle_id: UUID) -> bool:
        """Soft delete appraisal cycle"""
        cycle = self.get_appraisal_cycle(cycle_id)
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal cycle not found"
            )
        
        cycle.is_active = False
        cycle.updated_by = self.user_id
        self.db.commit()
        return True
    
    # ========================================================================
    # PERFORMANCE GOAL OPERATIONS (KRA/KPI)
    # ========================================================================
    
    def create_performance_goal(self, data: PerformanceGoalCreate) -> PerformanceGoal:
        """Create a new performance goal"""
        # Verify employee exists
        employee = self.db.query(Employee).filter(
            and_(
                Employee.id == data.employee_id,
                Employee.tenant_id == self.tenant_id,
                Employee.is_active == True
            )
        ).first()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Verify appraisal cycle exists
        cycle = self.get_appraisal_cycle(data.appraisal_cycle_id)
        if not cycle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal cycle not found"
            )
        
        goal = PerformanceGoal(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def get_performance_goal(self, goal_id: UUID) -> Optional[PerformanceGoal]:
        """Get performance goal by ID"""
        return self.db.query(PerformanceGoal).filter(
            and_(
                PerformanceGoal.id == goal_id,
                PerformanceGoal.tenant_id == self.tenant_id,
                PerformanceGoal.is_active == True
            )
        ).first()
    
    def list_employee_goals(
        self,
        employee_id: UUID,
        appraisal_cycle_id: Optional[UUID] = None,
        status: Optional[GoalStatus] = None
    ) -> List[PerformanceGoal]:
        """List goals for an employee"""
        query = self.db.query(PerformanceGoal).filter(
            and_(
                PerformanceGoal.tenant_id == self.tenant_id,
                PerformanceGoal.employee_id == employee_id,
                PerformanceGoal.is_active == True
            )
        )
        
        if appraisal_cycle_id:
            query = query.filter(PerformanceGoal.appraisal_cycle_id == appraisal_cycle_id)
        if status:
            query = query.filter(PerformanceGoal.status == status)
        
        return query.order_by(PerformanceGoal.start_date.desc()).all()
    
    def update_performance_goal(self, goal_id: UUID, data: PerformanceGoalUpdate) -> PerformanceGoal:
        """Update performance goal"""
        goal = self.get_performance_goal(goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance goal not found"
            )
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        goal.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def submit_goals(self, employee_id: UUID, appraisal_cycle_id: UUID) -> bool:
        """Submit all goals for approval"""
        goals = self.list_employee_goals(employee_id, appraisal_cycle_id, GoalStatus.DRAFT)
        
        if not goals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No draft goals found to submit"
            )
        
        for goal in goals:
            goal.status = GoalStatus.SUBMITTED
            goal.submitted_date = datetime.utcnow()
            goal.updated_by = self.user_id
        
        self.db.commit()
        return True
    
    def approve_goal(self, goal_id: UUID, comments: Optional[str] = None) -> PerformanceGoal:
        """Approve a goal"""
        goal = self.get_performance_goal(goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance goal not found"
            )
        
        if goal.status != GoalStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted goals can be approved"
            )
        
        goal.status = GoalStatus.APPROVED
        goal.approved_by_id = self.user_id
        goal.approved_date = datetime.utcnow()
        if comments:
            goal.manager_comments = comments
        goal.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def reject_goal(self, goal_id: UUID, reason: str) -> PerformanceGoal:
        """Reject a goal"""
        goal = self.get_performance_goal(goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance goal not found"
            )
        
        if goal.status != GoalStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted goals can be rejected"
            )
        
        goal.status = GoalStatus.REJECTED
        goal.rejection_reason = reason
        goal.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def calculate_goal_achievement(self, employee_id: UUID, appraisal_cycle_id: UUID) -> Decimal:
        """Calculate overall goal achievement percentage"""
        goals = self.list_employee_goals(employee_id, appraisal_cycle_id, GoalStatus.COMPLETED)
        
        if not goals:
            return Decimal('0.00')
        
        total_weightage = sum(goal.weightage or Decimal('0') for goal in goals)
        if total_weightage == 0:
            return Decimal('0.00')
        
        weighted_achievement = sum(
            (goal.progress_percentage or 0) * (goal.weightage or Decimal('0')) / 100
            for goal in goals
        )
        
        return Decimal(str(weighted_achievement / total_weightage * 100)).quantize(Decimal('0.01'))
    
    # ========================================================================
    # EMPLOYEE APPRAISAL OPERATIONS
    # ========================================================================
    
    def create_employee_appraisal(self, data: EmployeeAppraisalCreate) -> EmployeeAppraisal:
        """Create a new employee appraisal"""
        # Check if appraisal already exists
        existing = self.db.query(EmployeeAppraisal).filter(
            and_(
                EmployeeAppraisal.tenant_id == self.tenant_id,
                EmployeeAppraisal.employee_id == data.employee_id,
                EmployeeAppraisal.appraisal_cycle_id == data.appraisal_cycle_id,
                EmployeeAppraisal.is_active == True
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appraisal already exists for this employee in this cycle"
            )
        
        appraisal = EmployeeAppraisal(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(appraisal)
        self.db.commit()
        self.db.refresh(appraisal)
        return appraisal
    
    def get_employee_appraisal(self, appraisal_id: UUID) -> Optional[EmployeeAppraisal]:
        """Get employee appraisal by ID"""
        return self.db.query(EmployeeAppraisal).filter(
            and_(
                EmployeeAppraisal.id == appraisal_id,
                EmployeeAppraisal.tenant_id == self.tenant_id,
                EmployeeAppraisal.is_active == True
            )
        ).first()
    
    def submit_self_assessment(
        self,
        appraisal_id: UUID,
        data: SelfAssessmentSubmit
    ) -> EmployeeAppraisal:
        """Submit self assessment"""
        appraisal = self.get_employee_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal not found"
            )
        
        if appraisal.status not in [AppraisalStatus.GOALS_APPROVED, AppraisalStatus.SELF_ASSESSMENT_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot submit self assessment at this stage"
            )
        
        appraisal.self_rating = data.self_rating
        appraisal.self_rating_numeric = data.self_rating_numeric
        appraisal.self_comments = data.self_comments
        appraisal.key_achievements = data.key_achievements
        appraisal.areas_of_improvement = data.areas_of_improvement
        appraisal.self_assessment_submitted_date = datetime.utcnow()
        appraisal.status = AppraisalStatus.SELF_ASSESSMENT_SUBMITTED
        appraisal.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(appraisal)
        return appraisal
    
    def submit_manager_review(
        self,
        appraisal_id: UUID,
        data: ManagerReviewSubmit
    ) -> EmployeeAppraisal:
        """Submit manager review"""
        appraisal = self.get_employee_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal not found"
            )
        
        if appraisal.status not in [AppraisalStatus.SELF_ASSESSMENT_SUBMITTED, AppraisalStatus.MANAGER_REVIEW_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot submit manager review at this stage"
            )
        
        appraisal.manager_rating = data.manager_rating
        appraisal.manager_rating_numeric = data.manager_rating_numeric
        appraisal.manager_comments = data.manager_comments
        appraisal.manager_strengths = data.manager_strengths
        appraisal.manager_development_areas = data.manager_development_areas
        appraisal.recommended_increment_percentage = data.recommended_increment_percentage
        appraisal.recommended_promotion = data.recommended_promotion
        appraisal.recommended_promotion_designation_id = data.recommended_promotion_designation_id
        appraisal.manager_review_submitted_date = datetime.utcnow()
        appraisal.status = AppraisalStatus.MANAGER_REVIEW_SUBMITTED
        appraisal.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(appraisal)
        return appraisal
    
    def submit_hr_review(
        self,
        appraisal_id: UUID,
        data: HRReviewSubmit
    ) -> EmployeeAppraisal:
        """Submit HR review and finalize appraisal"""
        appraisal = self.get_employee_appraisal(appraisal_id)
        if not appraisal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appraisal not found"
            )
        
        if appraisal.status not in [AppraisalStatus.MANAGER_REVIEW_SUBMITTED, AppraisalStatus.HR_REVIEW_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot submit HR review at this stage"
            )
        
        appraisal.hr_comments = data.hr_comments
        appraisal.final_rating = data.final_rating
        appraisal.final_rating_numeric = data.final_rating_numeric
        appraisal.normalized_rating = data.normalized_rating
        appraisal.normalized_rating_numeric = data.normalized_rating_numeric
        appraisal.hr_review_submitted_date = datetime.utcnow()
        appraisal.status = AppraisalStatus.COMPLETED
        appraisal.completed_date = datetime.utcnow()
        appraisal.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(appraisal)
        return appraisal
    
    def list_employee_appraisals(
        self,
        employee_id: Optional[UUID] = None,
        appraisal_cycle_id: Optional[UUID] = None,
        status: Optional[AppraisalStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[EmployeeAppraisal], int]:
        """List employee appraisals with filters"""
        query = self.db.query(EmployeeAppraisal).filter(
            and_(
                EmployeeAppraisal.tenant_id == self.tenant_id,
                EmployeeAppraisal.is_active == True
            )
        )
        
        if employee_id:
            query = query.filter(EmployeeAppraisal.employee_id == employee_id)
        if appraisal_cycle_id:
            query = query.filter(EmployeeAppraisal.appraisal_cycle_id == appraisal_cycle_id)
        if status:
            query = query.filter(EmployeeAppraisal.status == status)
        
        total = query.count()
        appraisals = query.order_by(EmployeeAppraisal.created_at.desc()).offset(skip).limit(limit).all()
        
        return appraisals, total
    
    # ========================================================================
    # 360 FEEDBACK OPERATIONS
    # ========================================================================
    
    def create_feedback_request(self, data: FeedbackRequestCreate) -> FeedbackRequest:
        """Create a new feedback request"""
        # Check if request already exists
        existing = self.db.query(FeedbackRequest).filter(
            and_(
                FeedbackRequest.tenant_id == self.tenant_id,
                FeedbackRequest.employee_id == data.employee_id,
                FeedbackRequest.reviewer_id == data.reviewer_id,
                FeedbackRequest.appraisal_cycle_id == data.appraisal_cycle_id,
                FeedbackRequest.is_active == True
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback request already exists"
            )
        
        request = FeedbackRequest(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def submit_feedback_response(
        self,
        feedback_request_id: UUID,
        data: FeedbackResponseSubmit
    ) -> FeedbackResponse:
        """Submit feedback response"""
        # Get feedback request
        request = self.db.query(FeedbackRequest).filter(
            and_(
                FeedbackRequest.id == feedback_request_id,
                FeedbackRequest.tenant_id == self.tenant_id,
                FeedbackRequest.is_active == True
            )
        ).first()
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback request not found"
            )
        
        if request.status == FeedbackStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback already submitted"
            )
        
        # Create response
        response = FeedbackResponse(
            feedback_request_id=feedback_request_id,
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(response)
        
        # Update request status
        request.status = FeedbackStatus.SUBMITTED
        request.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(response)
        return response
    
    def list_feedback_requests_for_reviewer(
        self,
        reviewer_id: UUID,
        status: Optional[FeedbackStatus] = None
    ) -> List[FeedbackRequest]:
        """List feedback requests for a reviewer"""
        query = self.db.query(FeedbackRequest).filter(
            and_(
                FeedbackRequest.tenant_id == self.tenant_id,
                FeedbackRequest.reviewer_id == reviewer_id,
                FeedbackRequest.is_active == True
            )
        )
        
        if status:
            query = query.filter(FeedbackRequest.status == status)
        
        return query.order_by(FeedbackRequest.requested_date.desc()).all()
    
    def list_feedback_for_employee(
        self,
        employee_id: UUID,
        appraisal_cycle_id: Optional[UUID] = None
    ) -> List[FeedbackResponse]:
        """List feedback responses for an employee"""
        query = self.db.query(FeedbackResponse).join(FeedbackRequest).filter(
            and_(
                FeedbackResponse.tenant_id == self.tenant_id,
                FeedbackRequest.employee_id == employee_id,
                FeedbackResponse.is_active == True
            )
        )
        
        if appraisal_cycle_id:
            query = query.filter(FeedbackRequest.appraisal_cycle_id == appraisal_cycle_id)
        
        return query.order_by(FeedbackResponse.submitted_date.desc()).all()
    
    # ========================================================================
    # PERFORMANCE INCREMENT OPERATIONS
    # ========================================================================
    
    def create_performance_increment(self, data: PerformanceIncrementCreate) -> PerformanceIncrement:
        """Create a new performance increment"""
        increment = PerformanceIncrement(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(increment)
        self.db.commit()
        self.db.refresh(increment)
        return increment
    
    def approve_increment(self, increment_id: UUID) -> PerformanceIncrement:
        """Approve performance increment"""
        increment = self.db.query(PerformanceIncrement).filter(
            and_(
                PerformanceIncrement.id == increment_id,
                PerformanceIncrement.tenant_id == self.tenant_id,
                PerformanceIncrement.is_active == True
            )
        ).first()
        
        if not increment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Increment not found"
            )
        
        increment.is_approved = True
        increment.approved_by_id = self.user_id
        increment.approved_date = datetime.utcnow()
        increment.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(increment)
        return increment
    
    def process_increment(self, increment_id: UUID) -> PerformanceIncrement:
        """Mark increment as processed"""
        increment = self.db.query(PerformanceIncrement).filter(
            and_(
                PerformanceIncrement.id == increment_id,
                PerformanceIncrement.tenant_id == self.tenant_id,
                PerformanceIncrement.is_active == True
            )
        ).first()
        
        if not increment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Increment not found"
            )
        
        if not increment.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Increment must be approved before processing"
            )
        
        increment.is_processed = True
        increment.processed_date = datetime.utcnow()
        increment.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(increment)
        return increment
    
    def list_employee_increments(
        self,
        employee_id: UUID,
        appraisal_cycle_id: Optional[UUID] = None
    ) -> List[PerformanceIncrement]:
        """List increments for an employee"""
        query = self.db.query(PerformanceIncrement).filter(
            and_(
                PerformanceIncrement.tenant_id == self.tenant_id,
                PerformanceIncrement.employee_id == employee_id,
                PerformanceIncrement.is_active == True
            )
        )
        
        if appraisal_cycle_id:
            query = query.filter(PerformanceIncrement.appraisal_cycle_id == appraisal_cycle_id)
        
        return query.order_by(PerformanceIncrement.effective_from.desc()).all()
    
    # ========================================================================
    # INDIVIDUAL DEVELOPMENT PLAN (IDP) OPERATIONS
    # ========================================================================
    
    def create_idp(self, data: IndividualDevelopmentPlanCreate) -> IndividualDevelopmentPlan:
        """Create a new Individual Development Plan"""
        idp = IndividualDevelopmentPlan(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(idp)
        self.db.commit()
        self.db.refresh(idp)
        return idp
    
    def get_idp(self, idp_id: UUID) -> Optional[IndividualDevelopmentPlan]:
        """Get IDP by ID"""
        return self.db.query(IndividualDevelopmentPlan).filter(
            and_(
                IndividualDevelopmentPlan.id == idp_id,
                IndividualDevelopmentPlan.tenant_id == self.tenant_id,
                IndividualDevelopmentPlan.is_active == True
            )
        ).first()
    
    def update_idp(self, idp_id: UUID, data: IndividualDevelopmentPlanUpdate) -> IndividualDevelopmentPlan:
        """Update IDP"""
        idp = self.get_idp(idp_id)
        if not idp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IDP not found"
            )
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(idp, field, value)
        
        idp.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(idp)
        return idp
    
    def submit_idp(self, idp_id: UUID) -> IndividualDevelopmentPlan:
        """Submit IDP for approval"""
        idp = self.get_idp(idp_id)
        if not idp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IDP not found"
            )
        
        if idp.status != IDPStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft IDPs can be submitted"
            )
        
        idp.status = IDPStatus.SUBMITTED
        idp.submitted_date = datetime.utcnow()
        idp.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(idp)
        return idp
    
    def approve_idp(self, idp_id: UUID) -> IndividualDevelopmentPlan:
        """Approve IDP"""
        idp = self.get_idp(idp_id)
        if not idp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IDP not found"
            )
        
        if idp.status != IDPStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only submitted IDPs can be approved"
            )
        
        idp.status = IDPStatus.APPROVED
        idp.approved_by_id = self.user_id
        idp.approved_date = datetime.utcnow()
        idp.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(idp)
        return idp
    
    def list_employee_idps(
        self,
        employee_id: UUID,
        status: Optional[IDPStatus] = None
    ) -> List[IndividualDevelopmentPlan]:
        """List IDPs for an employee"""
        query = self.db.query(IndividualDevelopmentPlan).filter(
            and_(
                IndividualDevelopmentPlan.tenant_id == self.tenant_id,
                IndividualDevelopmentPlan.employee_id == employee_id,
                IndividualDevelopmentPlan.is_active == True
            )
        )
        
        if status:
            query = query.filter(IndividualDevelopmentPlan.status == status)
        
        return query.order_by(IndividualDevelopmentPlan.created_at.desc()).all()
    
    # ========================================================================
    # DEVELOPMENT ACTIVITY OPERATIONS
    # ========================================================================
    
    def create_development_activity(self, data: DevelopmentActivityCreate) -> DevelopmentActivity:
        """Create a new development activity"""
        # Verify IDP exists
        idp = self.get_idp(data.idp_id)
        if not idp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IDP not found"
            )
        
        activity = DevelopmentActivity(
            **data.dict(),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        # Update IDP progress
        self._update_idp_progress(data.idp_id)
        
        return activity
    
    def get_development_activity(self, activity_id: UUID) -> Optional[DevelopmentActivity]:
        """Get development activity by ID"""
        return self.db.query(DevelopmentActivity).filter(
            and_(
                DevelopmentActivity.id == activity_id,
                DevelopmentActivity.tenant_id == self.tenant_id,
                DevelopmentActivity.is_active == True
            )
        ).first()
    
    def update_development_activity(
        self,
        activity_id: UUID,
        data: DevelopmentActivityUpdate
    ) -> DevelopmentActivity:
        """Update development activity"""
        activity = self.get_development_activity(activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Development activity not found"
            )
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(activity, field, value)
        
        activity.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(activity)
        
        # Update IDP progress
        self._update_idp_progress(activity.idp_id)
        
        return activity
    
    def list_idp_activities(self, idp_id: UUID) -> List[DevelopmentActivity]:
        """List activities for an IDP"""
        return self.db.query(DevelopmentActivity).filter(
            and_(
                DevelopmentActivity.tenant_id == self.tenant_id,
                DevelopmentActivity.idp_id == idp_id,
                DevelopmentActivity.is_active == True
            )
        ).order_by(DevelopmentActivity.planned_start_date).all()
    
    def _update_idp_progress(self, idp_id: UUID) -> None:
        """Update IDP overall progress based on activities"""
        activities = self.list_idp_activities(idp_id)
        
        if not activities:
            return
        
        total_progress = sum(activity.completion_percentage for activity in activities)
        overall_progress = int(total_progress / len(activities))
        
        idp = self.get_idp(idp_id)
        if idp:
            idp.overall_progress_percentage = overall_progress
            if overall_progress == 100:
                idp.status = IDPStatus.COMPLETED
            elif overall_progress > 0:
                idp.status = IDPStatus.IN_PROGRESS
            self.db.commit()
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_rating_numeric(self, rating: str) -> Decimal:
        """Convert rating scale to numeric value"""
        rating_map = {
            'outstanding': Decimal('5.00'),
            'exceeds_expectations': Decimal('4.00'),
            'meets_expectations': Decimal('3.00'),
            'needs_improvement': Decimal('2.00'),
            'unsatisfactory': Decimal('1.00')
        }
        return rating_map.get(rating, Decimal('3.00'))
