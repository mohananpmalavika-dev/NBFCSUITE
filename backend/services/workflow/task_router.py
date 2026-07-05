"""
Workflow Task Router

API endpoints for workflow task management including:
- Task querying (my tasks, team tasks)
- Task operations (claim, complete, approve, reject)
- Task delegation and reassignment
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .task_service import WorkflowTaskService
from .schemas import (
    WorkflowTaskResponse,
    TaskDetailsResponse,
    ClaimTaskRequest,
    CompleteTaskRequest,
    ApproveTaskRequest,
    RejectTaskRequest,
    ReturnTaskRequest,
    DelegateTaskRequest,
    ReassignTaskRequest,
    TaskStatistics,
    TeamTaskStatistics,
    TaskStatus,
    Priority,
    TaskType
)

router = APIRouter(prefix="/workflows/tasks", tags=["Workflow Tasks"])


# ==================== TASK QUERIES ====================

@router.get("", response_model=dict)
def list_tasks(
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    assigned_role: Optional[str] = Query(None, description="Filter by assigned role"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    task_type: Optional[TaskType] = Query(None, description="Filter by task type"),
    overdue_only: bool = Query(False, description="Show only overdue tasks"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List workflow tasks with filters
    
    Returns tasks based on filters, ordered by priority and due date.
    
    **Filters**:
    - assigned_to: User ID
    - assigned_role: Role name
    - status: pending, claimed, in_progress, completed, cancelled
    - priority: low, normal, high, urgent
    - task_type: approval, review, data_entry, document_upload
    - overdue_only: Boolean flag for overdue tasks only
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    tasks = service.list_tasks(
        assigned_to=assigned_to,
        assigned_role=assigned_role,
        status=status,
        priority=priority,
        task_type=task_type,
        overdue_only=overdue_only,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(tasks)} tasks",
        data={
            "tasks": [WorkflowTaskResponse.from_orm(t).dict() for t in tasks],
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/my-tasks", response_model=dict)
def get_my_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get tasks assigned to current user
    
    Returns all tasks directly assigned to or claimed by the logged-in user.
    Ordered by priority (highest first) and due date (earliest first).
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    tasks = service.get_my_tasks(
        status=status,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(tasks)} tasks",
        data={
            "tasks": [WorkflowTaskResponse.from_orm(t).dict() for t in tasks],
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/team-tasks", response_model=dict)
def get_team_tasks(
    roles: List[str] = Query(..., description="User's roles"),
    status: TaskStatus = Query(TaskStatus.PENDING, description="Task status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get team tasks (task pool)
    
    Returns tasks available to user's roles that can be claimed.
    These are role-based or pool assignments that haven't been claimed yet.
    
    **Required**:
    - roles: List of user's role names
    
    Use this for "Available Tasks" or "Task Pool" views.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    tasks = service.get_team_tasks(
        roles=roles,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(tasks)} team tasks",
        data={
            "tasks": [WorkflowTaskResponse.from_orm(t).dict() for t in tasks],
            "roles": roles,
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{task_id}", response_model=dict)
def get_task_details(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get comprehensive task details
    
    Returns complete task information including:
    - Task details
    - Assignment information
    - Workflow context
    - Step information
    - Form data and attachments
    - Task history
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    details = service.get_task_details(task_id)
    
    return success_response(
        message="Task details retrieved successfully",
        data=details
    )


# ==================== TASK OPERATIONS ====================

@router.post("/{task_id}/claim", response_model=dict)
def claim_task(
    task_id: int,
    claim_request: ClaimTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Claim task from pool
    
    Claims a task that is assigned to a role (not directly to a user).
    Only works for tasks with role-based or pool assignment.
    Task must be in 'pending' status.
    
    After claiming, task becomes exclusive to the claiming user.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    task = service.claim_task(task_id)
    
    return success_response(
        message="Task claimed successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


@router.post("/{task_id}/complete", response_model=dict)
def complete_task(
    task_id: int,
    complete_request: CompleteTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Complete task with result
    
    Generic task completion with result data.
    Use approve/reject endpoints for approval tasks.
    
    **Required**:
    - result: Result code (e.g., 'completed', 'submitted')
    
    **Optional**:
    - result_data: Additional result data (JSON)
    - comments: User comments
    
    Completing a task advances the workflow to the next step.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    task = service.complete_task(
        task_id=task_id,
        result=complete_request.result,
        result_data=complete_request.result_data,
        comments=complete_request.comments
    )
    
    return success_response(
        message="Task completed successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


@router.post("/{task_id}/approve", response_model=dict)
def approve_task(
    task_id: int,
    approve_request: ApproveTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Approve approval task
    
    Approves an approval-type task and moves workflow forward.
    Only works for tasks with task_type = 'approval'.
    
    **Optional**:
    - comments: Approval comments
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    task = service.approve_task(
        task_id=task_id,
        comments=approve_request.comments
    )
    
    return success_response(
        message="Task approved successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


@router.post("/{task_id}/reject", response_model=dict)
def reject_task(
    task_id: int,
    reject_request: RejectTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Reject approval task
    
    Rejects an approval-type task.
    Only works for tasks with task_type = 'approval'.
    
    **Required**:
    - reason: Rejection reason (mandatory)
    
    **Optional**:
    - comments: Additional comments
    
    Rejection typically ends the workflow or routes to rejection path.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    task = service.reject_task(
        task_id=task_id,
        reason=reject_request.reason,
        comments=reject_request.comments
    )
    
    return success_response(
        message="Task rejected successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


@router.post("/{task_id}/return", response_model=dict)
def return_task(
    task_id: int,
    return_request: ReturnTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Return task for rework
    
    Returns task to a previous step for corrections or additional work.
    
    **Required**:
    - reason: Reason for returning (mandatory)
    
    **Optional**:
    - return_to_step: Specific step to return to
    - comments: Additional comments
    
    Workflow will go back to the specified step (or a default previous step).
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    task = service.return_task(
        task_id=task_id,
        reason=return_request.reason,
        return_to_step=return_request.return_to_step,
        comments=return_request.comments
    )
    
    return success_response(
        message="Task returned for rework",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


@router.post("/{task_id}/delegate", response_model=dict)
def delegate_task(
    task_id: int,
    delegate_request: DelegateTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Delegate task to another user
    
    Transfers task ownership to another user.
    Only the currently assigned or claimed user can delegate.
    
    **Required**:
    - delegate_to: User ID to delegate to
    
    **Optional**:
    - reason: Delegation reason
    
    The new user receives the task directly assigned.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    task = service.delegate_task(
        task_id=task_id,
        delegate_to=delegate_request.delegate_to,
        reason=delegate_request.reason
    )
    
    return success_response(
        message="Task delegated successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


# ==================== ADMIN OPERATIONS ====================

@router.post("/{task_id}/reassign", response_model=dict)
def reassign_task(
    task_id: int,
    reassign_request: ReassignTaskRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Reassign task to another user (admin operation)
    
    Administrative reassignment of tasks.
    Unlike delegation, this is a management action.
    
    **Required**:
    - assign_to: User ID to assign to
    
    **Optional**:
    - reason: Reassignment reason
    
    **Requires admin permission**
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    
    # TODO: Check admin permission
    
    task = service.reassign_task(
        task_id=task_id,
        assign_to=reassign_request.assign_to,
        reason=reassign_request.reason
    )
    
    return success_response(
        message="Task reassigned successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


@router.post("/{task_id}/cancel", response_model=dict)
def cancel_task(
    task_id: int,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Cancel task (admin operation)
    
    Cancels a task without completing it.
    Usually done when cancelling the entire workflow.
    
    **Optional**:
    - reason: Cancellation reason
    
    **Requires admin permission**
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    
    # TODO: Check admin permission
    
    task = service.cancel_task(task_id, reason)
    
    return success_response(
        message="Task cancelled successfully",
        data=WorkflowTaskResponse.from_orm(task).dict()
    )


# ==================== TASK STATISTICS ====================

@router.get("/statistics/my-stats", response_model=dict)
def get_my_task_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get task statistics for current user
    
    Returns:
    - Task count by status
    - Overdue tasks count
    - Tasks completed in last 30 days
    - Average completion time
    
    Useful for user dashboard and performance tracking.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    stats = service.get_user_task_stats()
    
    return success_response(
        message="User task statistics retrieved successfully",
        data=stats
    )


@router.get("/statistics/user/{user_id}", response_model=dict)
def get_user_task_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get task statistics for specific user (admin view)
    
    Returns task statistics for any user.
    Useful for manager dashboards and performance reviews.
    
    **May require manager/admin permission**
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    
    # TODO: Check permission to view other user's stats
    
    stats = service.get_user_task_stats(user_id)
    
    return success_response(
        message="User task statistics retrieved successfully",
        data=stats
    )


@router.get("/statistics/team-stats", response_model=dict)
def get_team_task_stats(
    roles: List[str] = Query(..., description="Team roles"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get task statistics for team/roles
    
    Returns aggregate statistics for tasks assigned to specific roles.
    
    **Required**:
    - roles: List of role names
    
    Returns:
    - Task count by status for the roles
    - Available tasks in the pool
    
    Useful for team dashboards.
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    stats = service.get_team_task_stats(roles)
    
    return success_response(
        message="Team task statistics retrieved successfully",
        data=stats
    )


# ==================== TASK QUERIES (CONVENIENCE) ====================

@router.get("/overdue/my-overdue", response_model=dict)
def get_my_overdue_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get my overdue tasks
    
    Returns tasks assigned to current user that are past their due date.
    Ordered by due date (oldest first).
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    tasks = service.get_overdue_tasks(
        assigned_to=current_user["id"],
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(tasks)} overdue tasks",
        data={
            "tasks": [WorkflowTaskResponse.from_orm(t).dict() for t in tasks],
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/overdue/all", response_model=dict)
def get_all_overdue_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get all overdue tasks (admin view)
    
    Returns all overdue tasks across the tenant.
    Useful for monitoring and escalation.
    
    **May require manager/admin permission**
    """
    service = WorkflowTaskService(db, tenant_id, current_user["id"])
    
    # TODO: Check permission
    
    tasks = service.get_overdue_tasks(
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(tasks)} overdue tasks",
        data={
            "tasks": [WorkflowTaskResponse.from_orm(t).dict() for t in tasks],
            "total": len(tasks),
            "skip": skip,
            "limit": limit
        }
    )
