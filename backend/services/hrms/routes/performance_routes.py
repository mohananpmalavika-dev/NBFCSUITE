"""
Performance Management API Routes
REST endpoints for Goal Setting, Appraisals, 360 Feedback, Ratings & IDP
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.hrms.services.performance_service import PerformanceManagementService
from backend.services.hrms.schemas.performance_schemas import (
    # Appraisal Cycle
    AppraisalCycleCreate, AppraisalCycleUpdate, AppraisalCycleResponse,
    # Performance Goal
    PerformanceGoalCreate, PerformanceGoalUpdate, PerformanceGoalResponse,
    # Employee Appraisal
    EmployeeAppraisalCreate, EmployeeAppraisalResponse,
    SelfAssessmentSubmit, ManagerReviewSubmit, HRReviewSubmit,
    # Feedback
    FeedbackRequestCreate, FeedbackRequestResponse,
    FeedbackResponseSubmit, FeedbackResponseResponse,
    # Increment
    PerformanceIncrementCreate, PerformanceIncrementUpdate, PerformanceIncrementResponse,
    # IDP
    IndividualDevelopmentPlanCreate, IndividualDevelopmentPlanUpdate, IndividualDevelopmentPlanResponse,
    # Development Activity
    DevelopmentActivityCreate, DevelopmentActivityUpdate, DevelopmentActivityResponse,
    # Common
    MessageResponse, PaginatedResponse,
    # Enums
    AppraisalCycleStatusEnum, GoalStatusEnum, AppraisalStatusEnum, FeedbackStatusEnum, IDPStatusEnum
)


router = APIRouter(prefix="/performance", tags=["Performance Management"])


def get_performance_service(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_current_user)
) -> PerformanceManagementService:
    """Dependency to get performance service instance"""
    return PerformanceManagementService(db, tenant_id, user_id)


# ============================================================================
# APPRAISAL CYCLE ROUTES
# ============================================================================

@router.post("/cycles", response_model=AppraisalCycleResponse, status_code=status.HTTP_201_CREATED)
async def create_appraisal_cycle(
    data: AppraisalCycleCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new appraisal cycle"""
    return service.create_appraisal_cycle(data)



@router.get("/cycles", response_model=PaginatedResponse)
async def list_appraisal_cycles(
    status: Optional[AppraisalCycleStatusEnum] = None,
    fiscal_year: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List appraisal cycles with filters"""
    cycles, total = service.list_appraisal_cycles(status, fiscal_year, skip, limit)
    
    return {
        "items": [AppraisalCycleResponse.from_orm(cycle).dict() for cycle in cycles],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/cycles/{cycle_id}", response_model=AppraisalCycleResponse)
async def get_appraisal_cycle(
    cycle_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Get appraisal cycle by ID"""
    cycle = service.get_appraisal_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Appraisal cycle not found")
    return cycle


@router.patch("/cycles/{cycle_id}", response_model=AppraisalCycleResponse)
async def update_appraisal_cycle(
    cycle_id: UUID,
    data: AppraisalCycleUpdate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Update appraisal cycle"""
    return service.update_appraisal_cycle(cycle_id, data)


@router.delete("/cycles/{cycle_id}", response_model=MessageResponse)
async def delete_appraisal_cycle(
    cycle_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Delete appraisal cycle"""
    service.delete_appraisal_cycle(cycle_id)
    return {"message": "Appraisal cycle deleted successfully", "success": True}


# ============================================================================
# PERFORMANCE GOAL ROUTES (KRA/KPI)
# ============================================================================

@router.post("/goals", response_model=PerformanceGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_goal(
    data: PerformanceGoalCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new performance goal"""
    return service.create_performance_goal(data)



@router.get("/goals/{goal_id}", response_model=PerformanceGoalResponse)
async def get_performance_goal(
    goal_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Get performance goal by ID"""
    goal = service.get_performance_goal(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Performance goal not found")
    return goal


@router.get("/employees/{employee_id}/goals", response_model=List[PerformanceGoalResponse])
async def list_employee_goals(
    employee_id: UUID,
    appraisal_cycle_id: Optional[UUID] = None,
    status: Optional[GoalStatusEnum] = None,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List goals for an employee"""
    return service.list_employee_goals(employee_id, appraisal_cycle_id, status)


@router.patch("/goals/{goal_id}", response_model=PerformanceGoalResponse)
async def update_performance_goal(
    goal_id: UUID,
    data: PerformanceGoalUpdate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Update performance goal"""
    return service.update_performance_goal(goal_id, data)


@router.post("/employees/{employee_id}/goals/submit", response_model=MessageResponse)
async def submit_employee_goals(
    employee_id: UUID,
    appraisal_cycle_id: UUID = Query(...),
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Submit all goals for approval"""
    service.submit_goals(employee_id, appraisal_cycle_id)
    return {"message": "Goals submitted successfully", "success": True}


@router.post("/goals/{goal_id}/approve", response_model=PerformanceGoalResponse)
async def approve_goal(
    goal_id: UUID,
    comments: Optional[str] = None,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Approve a goal"""
    return service.approve_goal(goal_id, comments)


@router.post("/goals/{goal_id}/reject", response_model=PerformanceGoalResponse)
async def reject_goal(
    goal_id: UUID,
    reason: str = Query(..., description="Rejection reason"),
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Reject a goal"""
    return service.reject_goal(goal_id, reason)



# ============================================================================
# EMPLOYEE APPRAISAL ROUTES
# ============================================================================

@router.post("/appraisals", response_model=EmployeeAppraisalResponse, status_code=status.HTTP_201_CREATED)
async def create_employee_appraisal(
    data: EmployeeAppraisalCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new employee appraisal"""
    return service.create_employee_appraisal(data)


@router.get("/appraisals", response_model=PaginatedResponse)
async def list_employee_appraisals(
    employee_id: Optional[UUID] = None,
    appraisal_cycle_id: Optional[UUID] = None,
    status: Optional[AppraisalStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List employee appraisals with filters"""
    appraisals, total = service.list_employee_appraisals(employee_id, appraisal_cycle_id, status, skip, limit)
    
    return {
        "items": [EmployeeAppraisalResponse.from_orm(appraisal).dict() for appraisal in appraisals],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/appraisals/{appraisal_id}", response_model=EmployeeAppraisalResponse)
async def get_employee_appraisal(
    appraisal_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Get employee appraisal by ID"""
    appraisal = service.get_employee_appraisal(appraisal_id)
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    return appraisal


@router.post("/appraisals/{appraisal_id}/self-assessment", response_model=EmployeeAppraisalResponse)
async def submit_self_assessment(
    appraisal_id: UUID,
    data: SelfAssessmentSubmit,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Submit self assessment"""
    return service.submit_self_assessment(appraisal_id, data)


@router.post("/appraisals/{appraisal_id}/manager-review", response_model=EmployeeAppraisalResponse)
async def submit_manager_review(
    appraisal_id: UUID,
    data: ManagerReviewSubmit,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Submit manager review"""
    return service.submit_manager_review(appraisal_id, data)


@router.post("/appraisals/{appraisal_id}/hr-review", response_model=EmployeeAppraisalResponse)
async def submit_hr_review(
    appraisal_id: UUID,
    data: HRReviewSubmit,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Submit HR review and finalize appraisal"""
    return service.submit_hr_review(appraisal_id, data)



# ============================================================================
# 360 FEEDBACK ROUTES
# ============================================================================

@router.post("/feedback/requests", response_model=FeedbackRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback_request(
    data: FeedbackRequestCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new feedback request"""
    return service.create_feedback_request(data)


@router.get("/feedback/requests/reviewer/{reviewer_id}", response_model=List[FeedbackRequestResponse])
async def list_feedback_requests_for_reviewer(
    reviewer_id: UUID,
    status: Optional[FeedbackStatusEnum] = None,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List feedback requests for a reviewer"""
    return service.list_feedback_requests_for_reviewer(reviewer_id, status)


@router.post("/feedback/requests/{request_id}/respond", response_model=FeedbackResponseResponse)
async def submit_feedback_response(
    request_id: UUID,
    data: FeedbackResponseSubmit,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Submit feedback response"""
    return service.submit_feedback_response(request_id, data)


@router.get("/feedback/employee/{employee_id}", response_model=List[FeedbackResponseResponse])
async def list_feedback_for_employee(
    employee_id: UUID,
    appraisal_cycle_id: Optional[UUID] = None,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List feedback responses for an employee"""
    return service.list_feedback_for_employee(employee_id, appraisal_cycle_id)


# ============================================================================
# PERFORMANCE INCREMENT ROUTES
# ============================================================================

@router.post("/increments", response_model=PerformanceIncrementResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_increment(
    data: PerformanceIncrementCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new performance increment"""
    return service.create_performance_increment(data)


@router.get("/employees/{employee_id}/increments", response_model=List[PerformanceIncrementResponse])
async def list_employee_increments(
    employee_id: UUID,
    appraisal_cycle_id: Optional[UUID] = None,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List increments for an employee"""
    return service.list_employee_increments(employee_id, appraisal_cycle_id)


@router.post("/increments/{increment_id}/approve", response_model=PerformanceIncrementResponse)
async def approve_increment(
    increment_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Approve performance increment"""
    return service.approve_increment(increment_id)


@router.post("/increments/{increment_id}/process", response_model=PerformanceIncrementResponse)
async def process_increment(
    increment_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Mark increment as processed"""
    return service.process_increment(increment_id)



# ============================================================================
# INDIVIDUAL DEVELOPMENT PLAN (IDP) ROUTES
# ============================================================================

@router.post("/idp", response_model=IndividualDevelopmentPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_idp(
    data: IndividualDevelopmentPlanCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new Individual Development Plan"""
    return service.create_idp(data)


@router.get("/idp/{idp_id}", response_model=IndividualDevelopmentPlanResponse)
async def get_idp(
    idp_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Get IDP by ID"""
    idp = service.get_idp(idp_id)
    if not idp:
        raise HTTPException(status_code=404, detail="IDP not found")
    return idp


@router.get("/employees/{employee_id}/idp", response_model=List[IndividualDevelopmentPlanResponse])
async def list_employee_idps(
    employee_id: UUID,
    status: Optional[IDPStatusEnum] = None,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List IDPs for an employee"""
    return service.list_employee_idps(employee_id, status)


@router.patch("/idp/{idp_id}", response_model=IndividualDevelopmentPlanResponse)
async def update_idp(
    idp_id: UUID,
    data: IndividualDevelopmentPlanUpdate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Update IDP"""
    return service.update_idp(idp_id, data)


@router.post("/idp/{idp_id}/submit", response_model=IndividualDevelopmentPlanResponse)
async def submit_idp(
    idp_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Submit IDP for approval"""
    return service.submit_idp(idp_id)


@router.post("/idp/{idp_id}/approve", response_model=IndividualDevelopmentPlanResponse)
async def approve_idp(
    idp_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Approve IDP"""
    return service.approve_idp(idp_id)


# ============================================================================
# DEVELOPMENT ACTIVITY ROUTES
# ============================================================================

@router.post("/idp/activities", response_model=DevelopmentActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_development_activity(
    data: DevelopmentActivityCreate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Create a new development activity"""
    return service.create_development_activity(data)


@router.get("/idp/{idp_id}/activities", response_model=List[DevelopmentActivityResponse])
async def list_idp_activities(
    idp_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """List activities for an IDP"""
    return service.list_idp_activities(idp_id)


@router.get("/idp/activities/{activity_id}", response_model=DevelopmentActivityResponse)
async def get_development_activity(
    activity_id: UUID,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Get development activity by ID"""
    activity = service.get_development_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Development activity not found")
    return activity


@router.patch("/idp/activities/{activity_id}", response_model=DevelopmentActivityResponse)
async def update_development_activity(
    activity_id: UUID,
    data: DevelopmentActivityUpdate,
    service: PerformanceManagementService = Depends(get_performance_service)
):
    """Update development activity"""
    return service.update_development_activity(activity_id, data)
