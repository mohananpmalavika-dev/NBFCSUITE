"""
Approval Workflow Execution Engine

Executes different approval patterns:
- Sequential: One after another
- Parallel: All must approve
- Any One: First to approve wins
- Majority: Threshold-based
- Conditional: Rule-based routing
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from backend.services.workflow.approval_models import (
    ApprovalChainConfig, ApprovalLevel, ApprovalType,
    ApprovalStatus, ApprovalAction
)


class ApprovalResult(str, Enum):
    """Approval result"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ApprovalEngine:
    """Approval workflow execution engine"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== START APPROVAL ====================
    
    def start_approval(
        self,
        chain_config: ApprovalChainConfig,
        entity_id: int,
        maker_id: int,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start approval process
        
        Args:
            chain_config: Approval chain configuration
            entity_id: Entity being approved
            maker_id: User who created/modified the entity
            variables: Context variables for condition evaluation
        
        Returns:
            Approval instance details
        """
        # Validate maker-checker rules
        if chain_config.maker_checker_enabled:
            validation = self._validate_maker_checker(chain_config, maker_id)
            if not validation['valid']:
                return {
                    "success": False,
                    "error": validation['error']
                }
        
        # Create approval instance
        from backend.shared.database.workflow_models import WorkflowInstance
        
        instance = WorkflowInstance(
            tenant_id=self.tenant_id,
            workflow_template_id=1,  # Placeholder
            instance_number=self._generate_instance_number(),
            instance_name=f"{chain_config.name} - {entity_id}",
            entity_type=chain_config.entity_type,
            entity_id=entity_id,
            initiated_by=maker_id,
            status='in_progress',
            workflow_variables={
                "chain_id": chain_config.chain_id,
                "maker_id": maker_id,
                "variables": variables or {},
                "approval_levels": []
            },
            started_at=datetime.utcnow()
        )
        
        self.db.add(instance)
        self.db.flush()
        
        # Start first level
        result = self._execute_level(
            instance=instance,
            chain_config=chain_config,
            level_number=1,
            variables=variables or {}
        )
        
        self.db.commit()
        
        return {
            "success": True,
            "instance_id": instance.id,
            "instance_number": instance.instance_number,
            "status": result['status'],
            "message": result['message']
        }
    
    # ==================== EXECUTE APPROVAL LEVELS ====================
    
    def _execute_level(
        self,
        instance: Any,
        chain_config: ApprovalChainConfig,
        level_number: int,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute approval level based on type"""
        # Get levels for this level number
        levels = [l for l in chain_config.levels if l.level == level_number]
        
        if not levels:
            # No more levels, approval complete
            instance.status = 'completed'
            instance.result = 'approved'
            instance.completed_at = datetime.utcnow()
            return {
                "status": ApprovalResult.COMPLETED,
                "message": "All approvals completed"
            }
        
        # Check skip conditions
        for level in levels:
            if self._should_skip_level(level, variables):
                # Skip this level, move to next
                return self._execute_level(
                    instance, chain_config, level_number + 1, variables
                )
        
        # Determine execution strategy
        if len(levels) == 1:
            level = levels[0]
            return self._execute_single_level(instance, level, variables)
        else:
            # Multiple levels at same number = parallel execution
            return self._execute_parallel_levels(instance, levels, variables)
    
    def _execute_single_level(
        self,
        instance: Any,
        level: ApprovalLevel,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single approval level"""
        from backend.shared.database.workflow_models import WorkflowTask
        
        # Create tasks based on approval type
        if level.approval_type == ApprovalType.SEQUENTIAL:
            # Create task for first approver
            task = self._create_approval_task(instance, level, 0)
            
        elif level.approval_type == ApprovalType.PARALLEL:
            # Create tasks for all approvers
            tasks = self._create_all_approval_tasks(instance, level)
            
        elif level.approval_type == ApprovalType.ANY_ONE:
            # Create tasks for all, but first to complete wins
            tasks = self._create_all_approval_tasks(instance, level)
            
        elif level.approval_type == ApprovalType.MAJORITY:
            # Create tasks for all, need threshold to approve
            tasks = self._create_all_approval_tasks(instance, level)
        
        return {
            "status": ApprovalResult.IN_PROGRESS,
            "message": f"Awaiting approval at level {level.level}"
        }
    
    def _execute_parallel_levels(
        self,
        instance: Any,
        levels: List[ApprovalLevel],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute multiple levels in parallel"""
        # Create tasks for all levels
        for level in levels:
            self._create_all_approval_tasks(instance, level)
        
        return {
            "status": ApprovalResult.IN_PROGRESS,
            "message": f"Awaiting parallel approvals at {len(levels)} levels"
        }
    
    # ==================== PROCESS APPROVAL ACTION ====================
    
    def process_approval(
        self,
        instance_id: int,
        task_id: int,
        action: ApprovalAction
    ) -> Dict[str, Any]:
        """
        Process approval action
        
        Handles: approve, reject, delegate, return
        """
        from backend.shared.database.workflow_models import (
            WorkflowInstance, WorkflowTask
        )
        
        # Get instance and task
        instance = self.db.query(WorkflowInstance).get(instance_id)
        task = self.db.query(WorkflowTask).get(task_id)
        
        if not instance or not task:
            return {"success": False, "error": "Instance or task not found"}
        
        # Validate maker-checker
        chain_config = self._get_chain_config(instance)
        if chain_config and chain_config.maker_checker_enabled:
            maker_id = instance.workflow_variables.get('maker_id')
            if maker_id == self.user_id and not chain_config.maker_checker_same_level:
                return {
                    "success": False,
                    "error": "Maker cannot approve their own submission"
                }
        
        # Process action
        if action.action == 'approve':
            return self._process_approve(instance, task, action, chain_config)
        elif action.action == 'reject':
            return self._process_reject(instance, task, action)
        elif action.action == 'delegate':
            return self._process_delegate(instance, task, action)
        elif action.action == 'return':
            return self._process_return(instance, task, action)
        else:
            return {"success": False, "error": f"Unknown action: {action.action}"}
    
    def _process_approve(
        self,
        instance: Any,
        task: Any,
        action: ApprovalAction,
        chain_config: Optional[ApprovalChainConfig]
    ) -> Dict[str, Any]:
        """Process approval"""
        # Mark task as completed
        task.status = 'completed'
        task.result = 'approved'
        task.comments = action.comments
        task.completed_at = datetime.utcnow()
        
        # Get level info
        level_info = self._get_level_info(instance, task)
        level_number = level_info['level_number']
        level_config = level_info['level_config']
        
        # Update approval count for this level
        approvals = instance.workflow_variables.get('approval_levels', [])
        level_approvals = next((a for a in approvals if a['level'] == level_number), None)
        
        if not level_approvals:
            level_approvals = {
                'level': level_number,
                'approved_count': 0,
                'rejected_count': 0,
                'required_count': self._get_required_count(level_config),
                'approvers': []
            }
            approvals.append(level_approvals)
        
        level_approvals['approved_count'] += 1
        level_approvals['approvers'].append({
            'user_id': self.user_id,
            'action': 'approved',
            'timestamp': datetime.utcnow().isoformat(),
            'comments': action.comments
        })
        
        instance.workflow_variables['approval_levels'] = approvals
        
        # Check if level is complete
        if self._is_level_complete(level_config, level_approvals):
            # Move to next level
            return self._execute_level(
                instance, chain_config, level_number + 1,
                instance.workflow_variables.get('variables', {})
            )
        
        # Check for ANY_ONE approval
        if level_config and level_config.approval_type == ApprovalType.ANY_ONE:
            # First approval wins, complete workflow
            instance.status = 'completed'
            instance.result = 'approved'
            instance.completed_at = datetime.utcnow()
            return {
                "success": True,
                "status": ApprovalResult.COMPLETED,
                "message": "Approval completed (any one)"
            }
        
        self.db.commit()
        
        return {
            "success": True,
            "status": ApprovalResult.IN_PROGRESS,
            "message": "Approval recorded, awaiting more approvals"
        }
    
    def _process_reject(
        self,
        instance: Any,
        task: Any,
        action: ApprovalAction
    ) -> Dict[str, Any]:
        """Process rejection"""
        # Mark task as rejected
        task.status = 'completed'
        task.result = 'rejected'
        task.comments = action.comments
        task.completed_at = datetime.utcnow()
        
        # Mark instance as rejected (rejection ends workflow)
        instance.status = 'completed'
        instance.result = 'rejected'
        instance.result_message = action.comments
        instance.completed_at = datetime.utcnow()
        
        # Cancel all other pending tasks
        from backend.shared.database.workflow_models import WorkflowTask
        pending_tasks = self.db.query(WorkflowTask).filter(
            WorkflowTask.workflow_instance_id == instance.id,
            WorkflowTask.status == 'pending'
        ).all()
        
        for t in pending_tasks:
            t.status = 'cancelled'
        
        self.db.commit()
        
        return {
            "success": True,
            "status": ApprovalResult.REJECTED,
            "message": "Approval rejected"
        }
    
    def _process_delegate(
        self,
        instance: Any,
        task: Any,
        action: ApprovalAction
    ) -> Dict[str, Any]:
        """Process delegation"""
        if not action.delegate_to:
            return {"success": False, "error": "delegate_to is required"}
        
        # Update task assignment
        task.assigned_to = action.delegate_to
        task.status = 'delegated'
        task.comments = action.comments
        
        # Create history
        from backend.shared.database.workflow_models import WorkflowHistory
        history = WorkflowHistory(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            workflow_step_id=task.workflow_step_id,
            event_type='task_delegated',
            actor_id=self.user_id,
            event_data={
                'from_user': self.user_id,
                'to_user': action.delegate_to,
                'reason': action.comments
            }
        )
        self.db.add(history)
        self.db.commit()
        
        return {
            "success": True,
            "status": ApprovalResult.IN_PROGRESS,
            "message": "Task delegated successfully"
        }
    
    def _process_return(
        self,
        instance: Any,
        task: Any,
        action: ApprovalAction
    ) -> Dict[str, Any]:
        """Process return to maker/previous level"""
        task.status = 'completed'
        task.result = 'returned'
        task.comments = action.comments
        task.completed_at = datetime.utcnow()
        
        # Mark instance as returned
        instance.status = 'returned'
        instance.result_message = action.comments
        
        self.db.commit()
        
        return {
            "success": True,
            "status": "returned",
            "message": "Returned to maker for corrections"
        }
    
    # ==================== HELPER METHODS ====================
    
    def _create_approval_task(
        self,
        instance: Any,
        level: ApprovalLevel,
        approver_index: int
    ) -> Any:
        """Create approval task for specific approver"""
        from backend.shared.database.workflow_models import WorkflowTask, WorkflowStep
        
        # Create step if not exists
        step = WorkflowStep(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            step_key=f"approval_level_{level.level}",
            step_name=level.name,
            step_type='user_task',
            status='in_progress',
            started_at=datetime.utcnow()
        )
        self.db.add(step)
        self.db.flush()
        
        # Determine assignee
        assigned_to = None
        assigned_role = None
        
        if level.assigned_users and approver_index < len(level.assigned_users):
            assigned_to = level.assigned_users[approver_index]
        elif level.assigned_roles:
            assigned_role = level.assigned_roles[approver_index % len(level.assigned_roles)]
        
        # Create task
        task = WorkflowTask(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            workflow_step_id=step.id,
            task_title=f"{level.name} - Approval Required",
            task_description=f"Please review and approve {instance.entity_type} #{instance.entity_id}",
            task_type='approval',
            assigned_to=assigned_to,
            assigned_role=assigned_role,
            status='pending',
            priority=instance.priority or 'normal',
            due_date=datetime.utcnow() + timedelta(hours=level.sla_hours or 24)
        )
        
        self.db.add(task)
        self.db.flush()
        
        return task
    
    def _create_all_approval_tasks(
        self,
        instance: Any,
        level: ApprovalLevel
    ) -> List[Any]:
        """Create approval tasks for all approvers in level"""
        tasks = []
        
        # Determine number of approvers
        num_approvers = 0
        if level.assigned_users:
            num_approvers = len(level.assigned_users)
        elif level.assigned_roles:
            num_approvers = len(level.assigned_roles)
        
        # Create task for each approver
        for i in range(max(num_approvers, 1)):
            task = self._create_approval_task(instance, level, i)
            tasks.append(task)
        
        return tasks
    
    def _should_skip_level(
        self,
        level: ApprovalLevel,
        variables: Dict[str, Any]
    ) -> bool:
        """Check if level should be skipped"""
        if not level.skip_conditions:
            return False
        
        for condition in level.skip_conditions:
            if self._evaluate_condition(condition, variables):
                return True
        
        return False
    
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> bool:
        """Evaluate condition"""
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not field or not operator:
            return False
        
        var_value = variables.get(field)
        
        if operator == '<':
            return var_value < value
        elif operator == '>':
            return var_value > value
        elif operator == '<=':
            return var_value <= value
        elif operator == '>=':
            return var_value >= value
        elif operator == '==':
            return var_value == value
        elif operator == '!=':
            return var_value != value
        
        return False
    
    def _is_level_complete(
        self,
        level: ApprovalLevel,
        level_approvals: Dict[str, Any]
    ) -> bool:
        """Check if approval level is complete"""
        if not level:
            return True
        
        approved = level_approvals.get('approved_count', 0)
        required = level_approvals.get('required_count', 1)
        
        if level.approval_type == ApprovalType.SEQUENTIAL:
            return approved >= required
        
        elif level.approval_type == ApprovalType.PARALLEL:
            return approved >= required
        
        elif level.approval_type == ApprovalType.ANY_ONE:
            return approved >= 1
        
        elif level.approval_type == ApprovalType.MAJORITY:
            if level.threshold:
                return approved >= level.threshold
            elif level.threshold_percentage:
                return (approved / required) >= (level.threshold_percentage / 100)
        
        return approved >= required
    
    def _get_required_count(self, level: Optional[ApprovalLevel]) -> int:
        """Get required approval count for level"""
        if not level:
            return 1
        
        if level.approval_type == ApprovalType.ANY_ONE:
            return 1
        
        if level.approval_type == ApprovalType.MAJORITY:
            if level.threshold:
                return level.threshold
            # Calculate from assigned approvers
            num_approvers = 0
            if level.assigned_users:
                num_approvers = len(level.assigned_users)
            elif level.assigned_roles:
                num_approvers = len(level.assigned_roles)
            
            if level.threshold_percentage:
                return int(num_approvers * level.threshold_percentage / 100)
            return (num_approvers // 2) + 1  # Default: majority
        
        # For sequential and parallel
        if level.assigned_users:
            return len(level.assigned_users)
        elif level.assigned_roles:
            return len(level.assigned_roles)
        
        return 1
    
    def _validate_maker_checker(
        self,
        chain_config: ApprovalChainConfig,
        maker_id: int
    ) -> Dict[str, Any]:
        """Validate maker-checker rules"""
        # Basic validation - can be extended
        return {
            "valid": True
        }
    
    def _get_chain_config(self, instance: Any) -> Optional[ApprovalChainConfig]:
        """Get chain config from instance"""
        # This should load from database in real implementation
        # For now, return None
        return None
    
    def _get_level_info(self, instance: Any, task: Any) -> Dict[str, Any]:
        """Get level information from task"""
        # Extract level number from step key
        step_key = task.step.step_key if hasattr(task, 'step') else 'approval_level_1'
        level_number = int(step_key.split('_')[-1])
        
        return {
            'level_number': level_number,
            'level_config': None  # Should load from config
        }
    
    def _generate_instance_number(self) -> str:
        """Generate unique instance number"""
        from datetime import datetime
        now = datetime.utcnow()
        return f"APR-{now.strftime('%Y%m')}-{now.strftime('%d%H%M%S')}"
