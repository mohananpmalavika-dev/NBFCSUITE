"""
Workflow Execution Service

Handles workflow instance execution including:
- Starting new workflow instances
- Step execution and transitions
- State management
- Error handling and retries
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from backend.shared.database.workflow_models import (
    WorkflowTemplate, WorkflowInstance, WorkflowStep,
    WorkflowHistory, WorkflowTask, WorkflowSLATracking
)
from backend.shared.common.response import CustomException
from .template_service import WorkflowTemplateService


class WorkflowExecutionService:
    """Service for executing workflows"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.template_service = WorkflowTemplateService(db, tenant_id, user_id)
    
    # ==================== WORKFLOW INSTANCE MANAGEMENT ====================
    
    def start_workflow(
        self,
        template_code: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        variables: Optional[Dict[str, Any]] = None,
        priority: str = 'normal',
        instance_name: Optional[str] = None
    ) -> WorkflowInstance:
        """
        Start a new workflow instance
        
        Args:
            template_code: Code of template to instantiate
            entity_type: Type of entity this workflow is for
            entity_id: ID of the entity
            variables: Initial workflow variables
            priority: Workflow priority (low, normal, high, urgent)
            instance_name: Optional custom name
            
        Returns:
            Created workflow instance
        """
        # Get template
        template = self.template_service.get_template_by_code(template_code)
        
        if not template.is_active:
            raise CustomException(
                status_code=400,
                message=f"Template {template_code} is not active"
            )
        
        # Generate instance number
        instance_number = self._generate_instance_number()
        
        # Merge default variables with provided variables
        workflow_variables = template.default_variables.copy() if template.default_variables else {}
        if variables:
            workflow_variables.update(variables)
        
        # Calculate deadline if SLA is configured
        deadline = None
        if template.default_sla_hours:
            deadline = datetime.utcnow() + timedelta(hours=template.default_sla_hours)
        
        # Create workflow instance
        instance = WorkflowInstance(
            tenant_id=self.tenant_id,
            workflow_template_id=template.id,
            instance_number=instance_number,
            instance_name=instance_name or f"{template.template_name} - {instance_number}",
            entity_type=entity_type,
            entity_id=entity_id,
            initiated_by=self.user_id,
            status='pending',
            workflow_variables=workflow_variables,
            priority=priority,
            deadline=deadline
        )
        
        self.db.add(instance)
        self.db.flush()
        
        # Create history entry
        self._create_history_entry(
            instance_id=instance.id,
            event_type='started',
            actor_id=self.user_id,
            event_data={'template_code': template_code}
        )
        
        # Create SLA tracking if configured
        if template.default_sla_hours:
            self._create_sla_tracking(
                instance_id=instance.id,
                sla_type='workflow_completion',
                sla_hours=template.default_sla_hours
            )
        
        self.db.commit()
        self.db.refresh(instance)
        
        # Execute first step
        self._execute_workflow(instance)
        
        return instance
    
    def _generate_instance_number(self) -> str:
        """Generate unique instance number in format WF-YYYYMM-XXXX"""
        today = datetime.now()
        prefix = f"WF-{today.strftime('%Y%m')}"
        
        # Get last instance number for this month
        last_instance = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.tenant_id == self.tenant_id,
                WorkflowInstance.instance_number.like(f"{prefix}%")
            )
        ).order_by(WorkflowInstance.id.desc()).first()
        
        if last_instance:
            last_number = int(last_instance.instance_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    def get_instance(self, instance_id: int) -> WorkflowInstance:
        """Get workflow instance by ID"""
        instance = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.id == instance_id,
                WorkflowInstance.tenant_id == self.tenant_id,
                WorkflowInstance.is_deleted == False
            )
        ).first()
        
        if not instance:
            raise CustomException(status_code=404, message="Workflow instance not found")
        
        return instance
    
    def list_instances(
        self,
        status: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        priority: Optional[str] = None,
        initiated_by: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WorkflowInstance]:
        """List workflow instances with filters"""
        query = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.tenant_id == self.tenant_id,
                WorkflowInstance.is_deleted == False
            )
        )
        
        if status:
            query = query.filter(WorkflowInstance.status == status)
        
        if entity_type:
            query = query.filter(WorkflowInstance.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(WorkflowInstance.entity_id == entity_id)
        
        if priority:
            query = query.filter(WorkflowInstance.priority == priority)
        
        if initiated_by:
            query = query.filter(WorkflowInstance.initiated_by == initiated_by)
        
        instances = query.order_by(
            WorkflowInstance.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return instances
    
    def cancel_workflow(
        self,
        instance_id: int,
        reason: Optional[str] = None
    ) -> WorkflowInstance:
        """Cancel a workflow instance"""
        instance = self.get_instance(instance_id)
        
        if instance.status in ['completed', 'failed', 'cancelled']:
            raise CustomException(
                status_code=400,
                message=f"Cannot cancel workflow in {instance.status} status"
            )
        
        instance.status = 'cancelled'
        instance.result = 'cancelled'
        instance.result_message = reason or "Cancelled by user"
        instance.completed_at = datetime.utcnow()
        
        # Cancel all pending steps
        pending_steps = self.db.query(WorkflowStep).filter(
            and_(
                WorkflowStep.workflow_instance_id == instance_id,
                WorkflowStep.status.in_(['pending', 'in_progress'])
            )
        ).all()
        
        for step in pending_steps:
            step.status = 'skipped'
            step.comments = "Workflow cancelled"
        
        # Create history entry
        self._create_history_entry(
            instance_id=instance.id,
            event_type='cancelled',
            actor_id=self.user_id,
            comments=reason
        )
        
        # Update SLA tracking
        self._complete_sla_tracking(instance_id, 'cancelled')
        
        self.db.commit()
        self.db.refresh(instance)
        
        return instance
    
    # ==================== WORKFLOW EXECUTION ====================
    
    def _execute_workflow(self, instance: WorkflowInstance) -> None:
        """Execute workflow from current state"""
        template = instance.template
        workflow_def = template.workflow_definition
        
        # Mark workflow as in_progress
        if instance.status == 'pending':
            instance.status = 'in_progress'
            instance.started_at = datetime.utcnow()
        
        # Find start step
        steps_def = workflow_def.get('steps', [])
        start_step = next((s for s in steps_def if s.get('type') == 'start'), None)
        
        if not start_step:
            raise CustomException(
                status_code=500,
                message="Workflow has no start step"
            )
        
        # Execute from start
        self._execute_step(instance, start_step)
    
    def _execute_step(
        self,
        instance: WorkflowInstance,
        step_def: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Execute a single workflow step"""
        # Create step record
        step = WorkflowStep(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            step_key=step_def['key'],
            step_name=step_def['name'],
            step_type=step_def['type'],
            status='in_progress',
            started_at=datetime.utcnow(),
            input_data=input_data or {}
        )
        
        # Set deadline if configured
        if step_def.get('sla_hours'):
            step.deadline = datetime.utcnow() + timedelta(hours=step_def['sla_hours'])
            # Create SLA tracking
            self._create_sla_tracking(
                instance_id=instance.id,
                step_id=step.id,
                sla_type='step_completion',
                sla_hours=step_def['sla_hours']
            )
        
        self.db.add(step)
        self.db.flush()
        
        # Update current step
        instance.current_step_id = step.id
        
        # Create history entry
        self._create_history_entry(
            instance_id=instance.id,
            step_id=step.id,
            event_type='step_started',
            actor_id=self.user_id,
            to_step=step_def['key']
        )
        
        # Handle different step types
        step_type = step_def['type']
        
        if step_type == 'start':
            # Auto-complete start step and move to next
            self._complete_step(step, 'started', {})
            self._transition_to_next(instance, step_def, 'started')
        
        elif step_type == 'end':
            # Complete workflow
            self._complete_step(step, 'completed', {})
            self._complete_workflow(instance, step_def.get('result', 'completed'))
        
        elif step_type == 'human_task':
            # Create user task
            self._create_user_task(instance, step, step_def)
        
        elif step_type == 'system_task':
            # Execute system task
            self._execute_system_task(instance, step, step_def)
        
        elif step_type == 'decision':
            # Evaluate decision
            self._execute_decision(instance, step, step_def)
        
        elif step_type == 'timer':
            # Schedule timer
            step.status = 'pending'
            # TODO: Implement timer scheduling
        
        self.db.commit()
    
    def _complete_step(
        self,
        step: WorkflowStep,
        action: str,
        output_data: Dict[str, Any]
    ) -> None:
        """Mark step as completed"""
        step.status = 'completed'
        step.action_taken = action
        step.output_data = output_data
        step.completed_at = datetime.utcnow()
        step.completed_by = self.user_id
        
        # Calculate duration
        if step.started_at:
            duration = (step.completed_at - step.started_at).total_seconds() / 60
            step.actual_duration = int(duration)
        
        # Create history entry
        self._create_history_entry(
            instance_id=step.workflow_instance_id,
            step_id=step.id,
            event_type='step_completed',
            actor_id=self.user_id,
            from_step=step.step_key,
            action=action,
            event_data=output_data
        )
        
        # Complete SLA tracking
        self._complete_step_sla_tracking(step.id)
    
    def _transition_to_next(
        self,
        instance: WorkflowInstance,
        current_step_def: Dict[str, Any],
        action: str
    ) -> None:
        """Transition to next step based on action"""
        template = instance.template
        workflow_def = template.workflow_definition
        steps_def = workflow_def.get('steps', [])
        
        next_step_key = None
        
        # Determine next step based on action
        if 'transitions' in current_step_def:
            # Look for matching transition
            for transition in current_step_def['transitions']:
                if transition.get('action') == action:
                    next_step_key = transition.get('next')
                    break
        
        # Fallback to default 'next'
        if not next_step_key:
            next_step_key = current_step_def.get('next')
        
        if next_step_key:
            # Find next step definition
            next_step_def = next((s for s in steps_def if s.get('key') == next_step_key), None)
            
            if next_step_def:
                # Execute next step
                self._execute_step(instance, next_step_def)
            else:
                raise CustomException(
                    status_code=500,
                    message=f"Next step {next_step_key} not found in workflow definition"
                )
    
    def _complete_workflow(
        self,
        instance: WorkflowInstance,
        result: str
    ) -> None:
        """Mark workflow as completed"""
        instance.status = 'completed'
        instance.result = result
        instance.completed_at = datetime.utcnow()
        
        # Create history entry
        self._create_history_entry(
            instance_id=instance.id,
            event_type='completed',
            actor_id=self.user_id,
            event_data={'result': result}
        )
        
        # Complete SLA tracking
        self._complete_sla_tracking(instance.id, 'met')
    
    # ==================== HELPER METHODS ====================
    
    def _create_history_entry(
        self,
        instance_id: int,
        event_type: str,
        actor_id: Optional[int] = None,
        step_id: Optional[int] = None,
        from_step: Optional[str] = None,
        to_step: Optional[str] = None,
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
            actor_id=actor_id or self.user_id,
            actor_type='user',
            from_step=from_step,
            to_step=to_step,
            action=action,
            event_data=event_data,
            comments=comments
        )
        
        self.db.add(history)
        self.db.flush()
        
        return history
    
    def _create_sla_tracking(
        self,
        instance_id: int,
        sla_type: str,
        sla_hours: int,
        step_id: Optional[int] = None
    ) -> WorkflowSLATracking:
        """Create SLA tracking record"""
        start_time = datetime.utcnow()
        deadline = start_time + timedelta(hours=sla_hours)
        
        sla = WorkflowSLATracking(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance_id,
            workflow_step_id=step_id,
            sla_type=sla_type,
            sla_hours=sla_hours,
            start_time=start_time,
            deadline=deadline,
            status='active'
        )
        
        self.db.add(sla)
        self.db.flush()
        
        return sla
    
    def _complete_sla_tracking(
        self,
        instance_id: int,
        status: str
    ) -> None:
        """Complete SLA tracking for workflow"""
        slas = self.db.query(WorkflowSLATracking).filter(
            and_(
                WorkflowSLATracking.workflow_instance_id == instance_id,
                WorkflowSLATracking.status == 'active'
            )
        ).all()
        
        for sla in slas:
            sla.completion_time = datetime.utcnow()
            sla.status = status
            
            if sla.start_time:
                time_taken = (sla.completion_time - sla.start_time).total_seconds() / 60
                sla.time_taken = int(time_taken)
                
                # Check if breached
                if sla.completion_time > sla.deadline:
                    sla.breach_time = sla.deadline
    
    def _complete_step_sla_tracking(self, step_id: int) -> None:
        """Complete SLA tracking for a step"""
        sla = self.db.query(WorkflowSLATracking).filter(
            and_(
                WorkflowSLATracking.workflow_step_id == step_id,
                WorkflowSLATracking.status == 'active'
            )
        ).first()
        
        if sla:
            completion_time = datetime.utcnow()
            sla.completion_time = completion_time
            
            if completion_time > sla.deadline:
                sla.status = 'breached'
                sla.breach_time = sla.deadline
            else:
                sla.status = 'met'
            
            if sla.start_time:
                time_taken = (completion_time - sla.start_time).total_seconds() / 60
                sla.time_taken = int(time_taken)
    
    def _create_user_task(
        self,
        instance: WorkflowInstance,
        step: WorkflowStep,
        step_def: Dict[str, Any]
    ) -> WorkflowTask:
        """Create user task for human task step"""
        task = WorkflowTask(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            workflow_step_id=step.id,
            task_title=step_def['name'],
            task_description=step_def.get('description'),
            task_type=step_def.get('task_type', 'approval'),
            assigned_role=step_def.get('assigned_role'),
            priority=instance.priority,
            due_date=step.deadline,
            status='pending'
        )
        
        self.db.add(task)
        self.db.flush()
        
        return task
    
    def _execute_system_task(
        self,
        instance: WorkflowInstance,
        step: WorkflowStep,
        step_def: Dict[str, Any]
    ) -> None:
        """Execute system task"""
        # TODO: Implement system task execution
        # This would call external services, APIs, etc.
        
        # For now, auto-complete
        self._complete_step(step, 'completed', {})
        self._transition_to_next(instance, step_def, 'completed')
    
    def _execute_decision(
        self,
        instance: WorkflowInstance,
        step: WorkflowStep,
        step_def: Dict[str, Any]
    ) -> None:
        """Execute decision step"""
        # Evaluate conditions
        conditions = step_def.get('conditions', [])
        workflow_vars = instance.workflow_variables or {}
        
        next_step_key = None
        for condition in conditions:
            # Simple condition evaluation
            # TODO: Implement proper expression evaluation
            if self._evaluate_condition(condition.get('condition'), workflow_vars):
                next_step_key = condition.get('next')
                break
        
        if next_step_key:
            self._complete_step(step, 'evaluated', {'next_step': next_step_key})
            
            # Find and execute next step
            template = instance.template
            workflow_def = template.workflow_definition
            steps_def = workflow_def.get('steps', [])
            next_step_def = next((s for s in steps_def if s.get('key') == next_step_key), None)
            
            if next_step_def:
                self._execute_step(instance, next_step_def)
    
    def _evaluate_condition(
        self,
        condition: str,
        variables: Dict[str, Any]
    ) -> bool:
        """Evaluate condition expression"""
        # Simple evaluation - would need proper expression parser
        # For now, just return True
        # TODO: Implement proper condition evaluation
        return True
