"""
Workflow Task Service

Handles workflow task management including:
- Task assignment (direct, role-based, pool)
- Task claiming and completion
- Approval/Rejection operations
- Task delegation
- Task notifications
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.shared.database.workflow_models import (
    WorkflowTask, WorkflowInstance, WorkflowStep, WorkflowHistory
)
from backend.shared.common.response import CustomException


class WorkflowTaskService:
    """Service for managing workflow tasks"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== TASK QUERIES ====================
    
    def get_task(self, task_id: int) -> WorkflowTask:
        """Get task by ID"""
        task = self.db.query(WorkflowTask).filter(
            and_(
                WorkflowTask.id == task_id,
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.is_deleted == False
            )
        ).first()
        
        if not task:
            raise CustomException(status_code=404, message="Task not found")
        
        return task
    
    def list_tasks(
        self,
        assigned_to: Optional[int] = None,
        assigned_role: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        task_type: Optional[str] = None,
        overdue_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTask]:
        """List tasks with filters"""
        query = self.db.query(WorkflowTask).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.is_deleted == False
            )
        )
        
        if assigned_to:
            query = query.filter(WorkflowTask.assigned_to == assigned_to)
        
        if assigned_role:
            query = query.filter(WorkflowTask.assigned_role == assigned_role)
        
        if status:
            query = query.filter(WorkflowTask.status == status)
        
        if priority:
            query = query.filter(WorkflowTask.priority == priority)
        
        if task_type:
            query = query.filter(WorkflowTask.task_type == task_type)
        
        if overdue_only:
            query = query.filter(
                and_(
                    WorkflowTask.due_date < datetime.utcnow(),
                    WorkflowTask.status.in_(['pending', 'claimed', 'in_progress'])
                )
            )
        
        tasks = query.order_by(
            WorkflowTask.priority.desc(),
            WorkflowTask.due_date.asc()
        ).offset(skip).limit(limit).all()
        
        return tasks
    
    def get_my_tasks(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTask]:
        """Get tasks assigned to current user"""
        return self.list_tasks(
            assigned_to=self.user_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    def get_team_tasks(
        self,
        roles: List[str],
        status: str = 'pending',
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTask]:
        """Get tasks available to user's roles (task pool)"""
        query = self.db.query(WorkflowTask).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.is_deleted == False,
                WorkflowTask.status == status,
                WorkflowTask.assignment_type.in_(['role_based', 'pool']),
                WorkflowTask.assigned_role.in_(roles)
            )
        )
        
        tasks = query.order_by(
            WorkflowTask.priority.desc(),
            WorkflowTask.due_date.asc()
        ).offset(skip).limit(limit).all()
        
        return tasks
    
    def get_overdue_tasks(
        self,
        assigned_to: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowTask]:
        """Get overdue tasks"""
        return self.list_tasks(
            assigned_to=assigned_to,
            overdue_only=True,
            skip=skip,
            limit=limit
        )
    
    # ==================== TASK OPERATIONS ====================
    
    def claim_task(self, task_id: int) -> WorkflowTask:
        """
        Claim a task from the pool
        
        Only works for role-based or pool assignments.
        Task must be in pending status.
        """
        task = self.get_task(task_id)
        
        # Validate task can be claimed
        if task.status != 'pending':
            raise CustomException(
                status_code=400,
                message=f"Cannot claim task in {task.status} status"
            )
        
        if task.assignment_type not in ['role_based', 'pool']:
            raise CustomException(
                status_code=400,
                message="This task is directly assigned and cannot be claimed"
            )
        
        # Check if already claimed by someone else
        if task.claimed_by and task.claimed_by != self.user_id:
            raise CustomException(
                status_code=400,
                message="Task already claimed by another user"
            )
        
        # TODO: Validate user has required role
        
        # Claim the task
        task.status = 'claimed'
        task.claimed_by = self.user_id
        task.claimed_at = datetime.utcnow()
        
        # Update step status
        step = task.step
        if step.status == 'pending':
            step.status = 'in_progress'
            step.assigned_to = self.user_id
        
        # Create history entry
        self._create_history_entry(
            instance_id=task.workflow_instance_id,
            step_id=task.workflow_step_id,
            event_type='task_claimed',
            actor_id=self.user_id,
            comments=f"Task claimed by user {self.user_id}"
        )
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def complete_task(
        self,
        task_id: int,
        result: str,
        result_data: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None
    ) -> WorkflowTask:
        """
        Complete a task with result
        
        Generic completion - use approve/reject for approval tasks.
        """
        task = self.get_task(task_id)
        
        # Validate user can complete task
        if task.status == 'completed':
            raise CustomException(
                status_code=400,
                message="Task already completed"
            )
        
        if task.status == 'cancelled':
            raise CustomException(
                status_code=400,
                message="Task is cancelled"
            )
        
        # For claimed tasks, only claimer can complete
        if task.claimed_by and task.claimed_by != self.user_id:
            raise CustomException(
                status_code=403,
                message="Only the user who claimed this task can complete it"
            )
        
        # For direct assignments, only assigned user can complete
        if task.assigned_to and task.assigned_to != self.user_id:
            raise CustomException(
                status_code=403,
                message="You are not assigned to this task"
            )
        
        # Complete the task
        task.status = 'completed'
        task.result = result
        task.result_data = result_data or {}
        task.comments = comments
        task.completed_at = datetime.utcnow()
        
        # Update workflow step
        step = task.step
        step.status = 'completed'
        step.action_taken = result
        step.output_data = result_data or {}
        step.comments = comments
        step.completed_at = datetime.utcnow()
        step.completed_by = self.user_id
        
        # Calculate step duration
        if step.started_at:
            duration = (step.completed_at - step.started_at).total_seconds() / 60
            step.actual_duration = int(duration)
        
        # Create history entry
        self._create_history_entry(
            instance_id=task.workflow_instance_id,
            step_id=task.workflow_step_id,
            event_type='task_completed',
            actor_id=self.user_id,
            action=result,
            event_data=result_data,
            comments=comments
        )
        
        # Continue workflow execution
        self._continue_workflow_execution(task, result)
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def approve_task(
        self,
        task_id: int,
        comments: Optional[str] = None
    ) -> WorkflowTask:
        """Approve an approval task"""
        task = self.get_task(task_id)
        
        if task.task_type != 'approval':
            raise CustomException(
                status_code=400,
                message="This task is not an approval task"
            )
        
        return self.complete_task(
            task_id=task_id,
            result='approved',
            result_data={'decision': 'approved'},
            comments=comments
        )
    
    def reject_task(
        self,
        task_id: int,
        reason: str,
        comments: Optional[str] = None
    ) -> WorkflowTask:
        """Reject an approval task"""
        task = self.get_task(task_id)
        
        if task.task_type != 'approval':
            raise CustomException(
                status_code=400,
                message="This task is not an approval task"
            )
        
        if not reason:
            raise CustomException(
                status_code=400,
                message="Rejection reason is required"
            )
        
        return self.complete_task(
            task_id=task_id,
            result='rejected',
            result_data={'decision': 'rejected', 'reason': reason},
            comments=comments
        )
    
    def return_task(
        self,
        task_id: int,
        reason: str,
        return_to_step: Optional[str] = None,
        comments: Optional[str] = None
    ) -> WorkflowTask:
        """
        Return task for rework
        
        Sends workflow back to a previous step for corrections.
        """
        task = self.get_task(task_id)
        
        if not reason:
            raise CustomException(
                status_code=400,
                message="Return reason is required"
            )
        
        # Complete current task as returned
        result_data = {
            'decision': 'returned',
            'reason': reason,
            'return_to_step': return_to_step
        }
        
        return self.complete_task(
            task_id=task_id,
            result='return',
            result_data=result_data,
            comments=comments
        )
    
    def delegate_task(
        self,
        task_id: int,
        delegate_to: int,
        reason: Optional[str] = None
    ) -> WorkflowTask:
        """
        Delegate task to another user
        
        Only the assigned/claimed user can delegate.
        """
        task = self.get_task(task_id)
        
        # Validate current user can delegate
        if task.claimed_by and task.claimed_by != self.user_id:
            raise CustomException(
                status_code=403,
                message="Only the user who claimed this task can delegate it"
            )
        
        if task.assigned_to and task.assigned_to != self.user_id:
            raise CustomException(
                status_code=403,
                message="Only the assigned user can delegate this task"
            )
        
        # Validate task can be delegated
        if task.status == 'completed':
            raise CustomException(
                status_code=400,
                message="Cannot delegate completed task"
            )
        
        # TODO: Validate delegate_to user exists and has required role
        
        # Delegate the task
        old_assignee = task.assigned_to or task.claimed_by
        task.assigned_to = delegate_to
        task.assignment_type = 'direct'
        task.claimed_by = None
        task.claimed_at = None
        task.status = 'pending'
        
        # Update step
        step = task.step
        step.assigned_to = delegate_to
        
        # Create history entry
        self._create_history_entry(
            instance_id=task.workflow_instance_id,
            step_id=task.workflow_step_id,
            event_type='task_delegated',
            actor_id=self.user_id,
            event_data={
                'from_user': old_assignee,
                'to_user': delegate_to,
                'reason': reason
            },
            comments=reason
        )
        
        # TODO: Send notification to new assignee
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def reassign_task(
        self,
        task_id: int,
        assign_to: int,
        reason: Optional[str] = None
    ) -> WorkflowTask:
        """
        Reassign task to another user (admin operation)
        
        Unlike delegation, this is an administrative action.
        """
        task = self.get_task(task_id)
        
        # Validate task can be reassigned
        if task.status == 'completed':
            raise CustomException(
                status_code=400,
                message="Cannot reassign completed task"
            )
        
        # TODO: Validate user has admin permission
        # TODO: Validate assign_to user exists
        
        # Reassign the task
        old_assignee = task.assigned_to or task.claimed_by
        task.assigned_to = assign_to
        task.assignment_type = 'direct'
        task.claimed_by = None
        task.claimed_at = None
        task.status = 'pending'
        
        # Update step
        step = task.step
        step.assigned_to = assign_to
        
        # Create history entry
        self._create_history_entry(
            instance_id=task.workflow_instance_id,
            step_id=task.workflow_step_id,
            event_type='task_reassigned',
            actor_id=self.user_id,
            event_data={
                'from_user': old_assignee,
                'to_user': assign_to,
                'reason': reason
            },
            comments=reason
        )
        
        # TODO: Send notification to new assignee
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def cancel_task(
        self,
        task_id: int,
        reason: Optional[str] = None
    ) -> WorkflowTask:
        """
        Cancel a task (admin operation)
        
        Usually done when cancelling the entire workflow.
        """
        task = self.get_task(task_id)
        
        if task.status == 'completed':
            raise CustomException(
                status_code=400,
                message="Cannot cancel completed task"
            )
        
        task.status = 'cancelled'
        task.comments = reason or "Task cancelled"
        
        # Update step
        step = task.step
        step.status = 'skipped'
        step.comments = reason or "Task cancelled"
        
        # Create history entry
        self._create_history_entry(
            instance_id=task.workflow_instance_id,
            step_id=task.workflow_step_id,
            event_type='task_cancelled',
            actor_id=self.user_id,
            comments=reason
        )
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    # ==================== TASK DETAILS ====================
    
    def get_task_details(self, task_id: int) -> Dict[str, Any]:
        """Get comprehensive task details with context"""
        task = self.get_task(task_id)
        instance = task.instance
        step = task.step
        
        # Get workflow history for this task
        history = self.db.query(WorkflowHistory).filter(
            and_(
                WorkflowHistory.workflow_step_id == step.id,
                WorkflowHistory.tenant_id == self.tenant_id
            )
        ).order_by(WorkflowHistory.event_timestamp.desc()).limit(10).all()
        
        return {
            "task": {
                "id": task.id,
                "title": task.task_title,
                "description": task.task_description,
                "type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "claimed_at": task.claimed_at.isoformat() if task.claimed_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            },
            "assignment": {
                "assigned_to": task.assigned_to,
                "assigned_role": task.assigned_role,
                "assignment_type": task.assignment_type,
                "claimed_by": task.claimed_by
            },
            "workflow": {
                "instance_id": instance.id,
                "instance_number": instance.instance_number,
                "instance_name": instance.instance_name,
                "template_name": instance.template.template_name,
                "entity_type": instance.entity_type,
                "entity_id": instance.entity_id
            },
            "step": {
                "step_key": step.step_key,
                "step_name": step.step_name,
                "step_type": step.step_type,
                "input_data": step.input_data
            },
            "form_data": task.form_data,
            "attachments": task.attachments,
            "history": [
                {
                    "event_type": h.event_type,
                    "timestamp": h.event_timestamp.isoformat(),
                    "actor_id": h.actor_id,
                    "comments": h.comments
                }
                for h in history
            ]
        }
    
    # ==================== TASK STATISTICS ====================
    
    def get_user_task_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get task statistics for a user"""
        target_user = user_id or self.user_id
        
        # Get counts by status
        stats = self.db.query(
            WorkflowTask.status,
            func.count(WorkflowTask.id)
        ).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.assigned_to == target_user,
                WorkflowTask.is_deleted == False
            )
        ).group_by(WorkflowTask.status).all()
        
        # Get overdue count
        overdue_count = self.db.query(func.count(WorkflowTask.id)).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.assigned_to == target_user,
                WorkflowTask.due_date < datetime.utcnow(),
                WorkflowTask.status.in_(['pending', 'claimed', 'in_progress']),
                WorkflowTask.is_deleted == False
            )
        ).scalar()
        
        # Get completion rate (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        completed_count = self.db.query(func.count(WorkflowTask.id)).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.assigned_to == target_user,
                WorkflowTask.status == 'completed',
                WorkflowTask.completed_at >= thirty_days_ago,
                WorkflowTask.is_deleted == False
            )
        ).scalar()
        
        # Get average completion time
        avg_time = self.db.query(
            func.avg(
                func.extract('epoch', WorkflowTask.completed_at - WorkflowTask.created_at) / 3600
            )
        ).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.assigned_to == target_user,
                WorkflowTask.status == 'completed',
                WorkflowTask.completed_at.isnot(None)
            )
        ).scalar()
        
        return {
            "user_id": target_user,
            "status_breakdown": {status: count for status, count in stats},
            "overdue_tasks": overdue_count or 0,
            "completed_last_30_days": completed_count or 0,
            "average_completion_hours": round(avg_time or 0, 2)
        }
    
    def get_team_task_stats(self, roles: List[str]) -> Dict[str, Any]:
        """Get task statistics for team (by roles)"""
        # Get counts by status for role-based tasks
        stats = self.db.query(
            WorkflowTask.status,
            func.count(WorkflowTask.id)
        ).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.assigned_role.in_(roles),
                WorkflowTask.assignment_type.in_(['role_based', 'pool']),
                WorkflowTask.is_deleted == False
            )
        ).group_by(WorkflowTask.status).all()
        
        # Get available tasks (pending, not claimed)
        available_count = self.db.query(func.count(WorkflowTask.id)).filter(
            and_(
                WorkflowTask.tenant_id == self.tenant_id,
                WorkflowTask.assigned_role.in_(roles),
                WorkflowTask.status == 'pending',
                WorkflowTask.claimed_by.is_(None),
                WorkflowTask.is_deleted == False
            )
        ).scalar()
        
        return {
            "roles": roles,
            "status_breakdown": {status: count for status, count in stats},
            "available_tasks": available_count or 0
        }
    
    # ==================== HELPER METHODS ====================
    
    def _create_history_entry(
        self,
        instance_id: int,
        event_type: str,
        actor_id: int,
        step_id: Optional[int] = None,
        action: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None
    ) -> WorkflowHistory:
        """Create workflow history entry"""
        history = WorkflowHistory(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance_id,
            workflow_step_id=step_id,
            event_type=event_type,
            actor_id=actor_id,
            actor_type='user',
            action=action,
            event_data=event_data,
            comments=comments
        )
        
        self.db.add(history)
        self.db.flush()
        
        return history
    
    def _continue_workflow_execution(
        self,
        task: WorkflowTask,
        action: str
    ) -> None:
        """Continue workflow execution after task completion"""
        instance = task.instance
        step = task.step
        template = instance.template
        workflow_def = template.workflow_definition
        
        # Find step definition
        steps_def = workflow_def.get('steps', [])
        step_def = next((s for s in steps_def if s.get('key') == step.step_key), None)
        
        if not step_def:
            return
        
        # Determine next step based on action
        next_step_key = None
        
        if 'transitions' in step_def:
            for transition in step_def['transitions']:
                if transition.get('action') == action:
                    next_step_key = transition.get('next')
                    break
        
        if not next_step_key:
            next_step_key = step_def.get('next')
        
        if next_step_key:
            # Find next step definition
            next_step_def = next((s for s in steps_def if s.get('key') == next_step_key), None)
            
            if next_step_def:
                # Import execution service to continue workflow
                from .execution_service import WorkflowExecutionService
                exec_service = WorkflowExecutionService(self.db, self.tenant_id, self.user_id)
                exec_service._execute_step(instance, next_step_def, step.output_data)
