"""
BPMN 2.0 Workflow Execution Engine

State machine that executes BPMN workflows:
- Processes BPMN nodes
- Evaluates gateway conditions
- Manages parallel execution
- Handles events and timers
- Executes service tasks
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import asyncio
import requests
from enum import Enum

from backend.services.workflow.bpmn_models import (
    BPMNProcess, BPMNNodeType, GatewayType, EventType,
    ConditionExpression
)
from backend.shared.database.workflow_models import (
    WorkflowInstance, WorkflowStep, WorkflowHistory,
    WorkflowTask, WorkflowSLATracking
)
from backend.shared.common.response import CustomException


class ExecutionStatus(str, Enum):
    """Execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    WAITING = "waiting"
    ERROR = "error"


class BPMNExecutionEngine:
    """BPMN 2.0 Workflow Execution Engine"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== START WORKFLOW ====================
    
    def start_workflow(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        initial_variables: Optional[Dict[str, Any]] = None
    ) -> Tuple[ExecutionStatus, str]:
        """
        Start workflow execution from start event
        
        Returns:
            (status, message)
        """
        try:
            # Find start event
            if not process.start_events:
                raise CustomException(
                    status_code=400,
                    message="Workflow has no start event"
                )
            
            start_event = process.start_events[0]
            
            # Initialize workflow variables
            variables = process.variables.copy() if process.variables else {}
            if initial_variables:
                variables.update(initial_variables)
            
            instance.workflow_variables = variables
            instance.status = 'in_progress'
            instance.started_at = datetime.utcnow()
            
            # Create workflow history
            self._create_history(
                instance,
                event_type='workflow_started',
                event_data={'start_event': start_event.id}
            )
            
            # Execute start event
            status, message = self._execute_start_event(
                process, instance, start_event
            )
            
            self.db.commit()
            
            return status, message
            
        except Exception as e:
            self.db.rollback()
            return ExecutionStatus.ERROR, str(e)
    
    # ==================== EXECUTE NODES ====================
    
    def _execute_start_event(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        start_event: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute start event"""
        # Create step record
        step = self._create_step(
            instance,
            step_key=start_event.id,
            step_name=start_event.name,
            step_type='start_event',
            status='completed'
        )
        step.started_at = datetime.utcnow()
        step.completed_at = datetime.utcnow()
        
        # Find next node
        next_flows = self._get_outgoing_flows(process, start_event.id)
        
        if not next_flows:
            return ExecutionStatus.ERROR, "No outgoing flow from start event"
        
        # Follow the flow
        return self._execute_sequence_flow(
            process, instance, next_flows[0]
        )
    
    def _execute_user_task(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        task_node: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute user task - creates task for user"""
        # Create step record
        step = self._create_step(
            instance,
            step_key=task_node.id,
            step_name=task_node.name,
            step_type='user_task',
            status='in_progress'
        )
        step.started_at = datetime.utcnow()
        
        # Parse assignment
        config = task_node.config
        assigned_to = None
        assigned_role = None
        assignment_type = config.assignment_type
        
        if assignment_type == 'direct' and config.assigned_user_id:
            assigned_to = config.assigned_user_id
            step.assigned_to = assigned_to
        elif assignment_type == 'role' and config.assigned_role:
            assigned_role = config.assigned_role
            step.assigned_role = assigned_role
        
        # Create workflow task
        task = WorkflowTask(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            workflow_step_id=step.id,
            task_title=task_node.name,
            task_description=task_node.description,
            task_type='approval',
            assigned_to=assigned_to,
            assigned_role=assigned_role,
            assignment_type=assignment_type,
            status='pending',
            priority=config.priority,
            form_data=config.form_fields
        )
        
        # Set due date
        if config.due_date:
            task.due_date = self._evaluate_date_expression(
                config.due_date, instance.workflow_variables
            )
        
        self.db.add(task)
        
        # Update instance current step
        instance.current_step_id = step.id
        
        # Create history
        self._create_history(
            instance,
            workflow_step_id=step.id,
            event_type='user_task_created',
            event_data={'task_id': task.id, 'node_id': task_node.id}
        )
        
        return ExecutionStatus.WAITING, f"Waiting for user task: {task_node.name}"
    
    def _execute_service_task(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        task_node: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute service task - makes API call or executes service"""
        # Create step record
        step = self._create_step(
            instance,
            step_key=task_node.id,
            step_name=task_node.name,
            step_type='service_task',
            status='in_progress'
        )
        step.started_at = datetime.utcnow()
        
        config = task_node.config
        
        try:
            # Execute based on implementation type
            if config.implementation == 'api':
                result = self._execute_api_call(config, instance.workflow_variables)
            elif config.implementation == 'expression':
                result = self._evaluate_expression(
                    config.expression, instance.workflow_variables
                )
            else:
                raise ValueError(f"Unsupported implementation: {config.implementation}")
            
            # Store result in variable
            if config.result_variable:
                instance.workflow_variables[config.result_variable] = result
            
            # Mark step as completed
            step.status = 'completed'
            step.completed_at = datetime.utcnow()
            step.output_data = {'result': result}
            
            # Create history
            self._create_history(
                instance,
                workflow_step_id=step.id,
                event_type='service_task_completed',
                event_data={'node_id': task_node.id, 'result': result}
            )
            
            # Continue to next node
            next_flows = self._get_outgoing_flows(process, task_node.id)
            if next_flows:
                return self._execute_sequence_flow(process, instance, next_flows[0])
            
            return ExecutionStatus.ERROR, "No outgoing flow from service task"
            
        except Exception as e:
            step.status = 'failed'
            step.last_error = str(e)
            
            # Retry logic
            if config.retry_enabled and step.retry_count < config.max_retries:
                step.retry_count += 1
                return ExecutionStatus.WAITING, f"Service task failed, will retry"
            
            return ExecutionStatus.ERROR, f"Service task failed: {str(e)}"
    
    def _execute_script_task(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        task_node: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute script task - runs Python script"""
        # Create step record
        step = self._create_step(
            instance,
            step_key=task_node.id,
            step_name=task_node.name,
            step_type='script_task',
            status='in_progress'
        )
        step.started_at = datetime.utcnow()
        
        config = task_node.config
        
        try:
            # Execute script with variables in scope
            local_vars = instance.workflow_variables.copy()
            exec(config.script, {"__builtins__": {}}, local_vars)
            
            # Store result if specified
            if config.result_variable and config.result_variable in local_vars:
                instance.workflow_variables[config.result_variable] = (
                    local_vars[config.result_variable]
                )
            
            # Mark step as completed
            step.status = 'completed'
            step.completed_at = datetime.utcnow()
            
            # Create history
            self._create_history(
                instance,
                workflow_step_id=step.id,
                event_type='script_task_completed',
                event_data={'node_id': task_node.id}
            )
            
            # Continue to next node
            next_flows = self._get_outgoing_flows(process, task_node.id)
            if next_flows:
                return self._execute_sequence_flow(process, instance, next_flows[0])
            
            return ExecutionStatus.ERROR, "No outgoing flow from script task"
            
        except Exception as e:
            step.status = 'failed'
            step.last_error = str(e)
            return ExecutionStatus.ERROR, f"Script execution failed: {str(e)}"
    
    def _execute_gateway(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        gateway_node: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute gateway - decision point"""
        # Create step record
        step = self._create_step(
            instance,
            step_key=gateway_node.id,
            step_name=gateway_node.name,
            step_type=f'gateway_{gateway_node.gateway_type}',
            status='in_progress'
        )
        step.started_at = datetime.utcnow()
        
        gateway_type = gateway_node.gateway_type
        outgoing_flows = self._get_outgoing_flows(process, gateway_node.id)
        
        if not outgoing_flows:
            return ExecutionStatus.ERROR, "Gateway has no outgoing flows"
        
        if gateway_type == GatewayType.EXCLUSIVE:
            # XOR - take ONE path based on conditions
            return self._execute_exclusive_gateway(
                process, instance, gateway_node, outgoing_flows, step
            )
        
        elif gateway_type == GatewayType.PARALLEL:
            # AND - take ALL paths simultaneously
            return self._execute_parallel_gateway(
                process, instance, gateway_node, outgoing_flows, step
            )
        
        elif gateway_type == GatewayType.INCLUSIVE:
            # OR - take MULTIPLE paths that match conditions
            return self._execute_inclusive_gateway(
                process, instance, gateway_node, outgoing_flows, step
            )
        
        else:
            return ExecutionStatus.ERROR, f"Unsupported gateway type: {gateway_type}"
    
    def _execute_exclusive_gateway(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        gateway_node: Any,
        outgoing_flows: List[Any],
        step: WorkflowStep
    ) -> Tuple[ExecutionStatus, str]:
        """Execute exclusive (XOR) gateway - take ONE path"""
        # Evaluate conditions on outgoing flows
        for flow in outgoing_flows:
            if flow.condition:
                if self._evaluate_condition(flow.condition, instance.workflow_variables):
                    # Take this path
                    step.status = 'completed'
                    step.completed_at = datetime.utcnow()
                    step.output_data = {'selected_flow': flow.id}
                    
                    self._create_history(
                        instance,
                        workflow_step_id=step.id,
                        event_type='gateway_executed',
                        event_data={
                            'gateway_type': 'exclusive',
                            'selected_flow': flow.id
                        }
                    )
                    
                    return self._execute_sequence_flow(process, instance, flow)
        
        # No condition matched, take default flow if exists
        if gateway_node.default_flow:
            default_flow = next(
                (f for f in outgoing_flows if f.id == gateway_node.default_flow),
                None
            )
            if default_flow:
                step.status = 'completed'
                step.completed_at = datetime.utcnow()
                return self._execute_sequence_flow(process, instance, default_flow)
        
        # Take first flow as fallback
        step.status = 'completed'
        step.completed_at = datetime.utcnow()
        return self._execute_sequence_flow(process, instance, outgoing_flows[0])
    
    def _execute_parallel_gateway(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        gateway_node: Any,
        outgoing_flows: List[Any],
        step: WorkflowStep
    ) -> Tuple[ExecutionStatus, str]:
        """Execute parallel (AND) gateway - take ALL paths"""
        step.status = 'completed'
        step.completed_at = datetime.utcnow()
        
        selected_flows = [flow.id for flow in outgoing_flows]
        step.output_data = {'selected_flows': selected_flows}
        
        self._create_history(
            instance,
            workflow_step_id=step.id,
            event_type='gateway_executed',
            event_data={
                'gateway_type': 'parallel',
                'selected_flows': selected_flows
            }
        )
        
        # Execute all paths (in this simple implementation, sequentially)
        # In a real implementation, these would be executed concurrently
        for flow in outgoing_flows:
            status, message = self._execute_sequence_flow(process, instance, flow)
            if status == ExecutionStatus.ERROR:
                return status, message
        
        return ExecutionStatus.SUCCESS, "Parallel gateway executed"
    
    def _execute_inclusive_gateway(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        gateway_node: Any,
        outgoing_flows: List[Any],
        step: WorkflowStep
    ) -> Tuple[ExecutionStatus, str]:
        """Execute inclusive (OR) gateway - take MULTIPLE matching paths"""
        selected_flows = []
        
        # Evaluate all conditions
        for flow in outgoing_flows:
            if flow.condition:
                if self._evaluate_condition(flow.condition, instance.workflow_variables):
                    selected_flows.append(flow)
            else:
                # No condition means always take
                selected_flows.append(flow)
        
        if not selected_flows:
            return ExecutionStatus.ERROR, "No path selected in inclusive gateway"
        
        step.status = 'completed'
        step.completed_at = datetime.utcnow()
        step.output_data = {'selected_flows': [f.id for f in selected_flows]}
        
        # Execute all selected paths
        for flow in selected_flows:
            status, message = self._execute_sequence_flow(process, instance, flow)
            if status == ExecutionStatus.ERROR:
                return status, message
        
        return ExecutionStatus.SUCCESS, "Inclusive gateway executed"
    
    def _execute_end_event(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        end_event: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute end event - complete workflow"""
        # Create step record
        step = self._create_step(
            instance,
            step_key=end_event.id,
            step_name=end_event.name,
            step_type='end_event',
            status='completed'
        )
        step.started_at = datetime.utcnow()
        step.completed_at = datetime.utcnow()
        
        # Complete workflow
        instance.status = 'completed'
        instance.completed_at = datetime.utcnow()
        instance.result = 'completed'
        
        # Create history
        self._create_history(
            instance,
            workflow_step_id=step.id,
            event_type='workflow_completed',
            event_data={'end_event': end_event.id}
        )
        
        return ExecutionStatus.SUCCESS, "Workflow completed"
    
    # ==================== SEQUENCE FLOW ====================
    
    def _execute_sequence_flow(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        flow: Any
    ) -> Tuple[ExecutionStatus, str]:
        """Execute sequence flow - transition to next node"""
        target_id = flow.target_ref
        
        # Find target node
        target_node = self._find_node_by_id(process, target_id)
        
        if not target_node:
            return ExecutionStatus.ERROR, f"Target node not found: {target_id}"
        
        # Route to appropriate executor based on node type
        node_type = target_node.type
        
        if node_type in [BPMNNodeType.END_NONE, BPMNNodeType.END_TERMINATE, 
                        BPMNNodeType.END_ERROR, BPMNNodeType.END_MESSAGE]:
            return self._execute_end_event(process, instance, target_node)
        
        elif node_type == BPMNNodeType.USER_TASK:
            return self._execute_user_task(process, instance, target_node)
        
        elif node_type == BPMNNodeType.SERVICE_TASK:
            return self._execute_service_task(process, instance, target_node)
        
        elif node_type == BPMNNodeType.SCRIPT_TASK:
            return self._execute_script_task(process, instance, target_node)
        
        elif node_type in [BPMNNodeType.EXCLUSIVE_GATEWAY, BPMNNodeType.PARALLEL_GATEWAY,
                          BPMNNodeType.INCLUSIVE_GATEWAY]:
            return self._execute_gateway(process, instance, target_node)
        
        else:
            return ExecutionStatus.ERROR, f"Unsupported node type: {node_type}"
    
    # ==================== TASK COMPLETION ====================
    
    def complete_user_task(
        self,
        process: BPMNProcess,
        instance: WorkflowInstance,
        task: WorkflowTask,
        result: str,
        result_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[ExecutionStatus, str]:
        """Complete user task and continue workflow"""
        try:
            # Update task
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            task.result = result
            task.result_data = result_data
            
            # Update step
            step = self.db.query(WorkflowStep).get(task.workflow_step_id)
            if step:
                step.status = 'completed'
                step.completed_at = datetime.utcnow()
                step.action_taken = result
                step.output_data = result_data
                step.completed_by = self.user_id
            
            # Store result in workflow variables
            if result_data:
                instance.workflow_variables.update(result_data)
            
            # Create history
            self._create_history(
                instance,
                workflow_step_id=step.id if step else None,
                event_type='user_task_completed',
                event_data={
                    'task_id': task.id,
                    'result': result
                }
            )
            
            # Find next node
            next_flows = self._get_outgoing_flows(process, step.step_key)
            
            if not next_flows:
                return ExecutionStatus.ERROR, "No outgoing flow from user task"
            
            # Continue workflow
            status, message = self._execute_sequence_flow(
                process, instance, next_flows[0]
            )
            
            self.db.commit()
            return status, message
            
        except Exception as e:
            self.db.rollback()
            return ExecutionStatus.ERROR, str(e)
    
    # ==================== HELPER METHODS ====================
    
    def _create_step(
        self,
        instance: WorkflowInstance,
        step_key: str,
        step_name: str,
        step_type: str,
        status: str = 'pending'
    ) -> WorkflowStep:
        """Create workflow step"""
        step = WorkflowStep(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            step_key=step_key,
            step_name=step_name,
            step_type=step_type,
            status=status
        )
        self.db.add(step)
        self.db.flush()
        return step
    
    def _create_history(
        self,
        instance: WorkflowInstance,
        event_type: str,
        workflow_step_id: Optional[int] = None,
        event_data: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None
    ) -> WorkflowHistory:
        """Create workflow history entry"""
        history = WorkflowHistory(
            tenant_id=self.tenant_id,
            workflow_instance_id=instance.id,
            workflow_step_id=workflow_step_id,
            event_type=event_type,
            event_timestamp=datetime.utcnow(),
            actor_id=self.user_id,
            actor_type='user',
            event_data=event_data,
            comments=comments
        )
        self.db.add(history)
        return history
    
    def _get_outgoing_flows(
        self,
        process: BPMNProcess,
        node_id: str
    ) -> List[Any]:
        """Get outgoing sequence flows from a node"""
        return [
            flow for flow in process.sequence_flows
            if flow.source_ref == node_id
        ]
    
    def _find_node_by_id(self, process: BPMNProcess, node_id: str) -> Optional[Any]:
        """Find node in process by ID"""
        # Search in all node collections
        all_nodes = (
            process.start_events +
            process.end_events +
            process.user_tasks +
            process.service_tasks +
            process.script_tasks +
            process.send_tasks +
            process.gateways +
            process.intermediate_events
        )
        
        for node in all_nodes:
            if node.id == node_id:
                return node
        
        return None
    
    # ==================== CONDITION EVALUATION ====================
    
    def _evaluate_condition(
        self,
        condition: ConditionExpression,
        variables: Dict[str, Any]
    ) -> bool:
        """Evaluate condition expression"""
        if condition.type == 'simple':
            # Simple comparison
            var_value = variables.get(condition.variable)
            operator = condition.operator
            compare_value = condition.value
            
            if operator == '==':
                return var_value == compare_value
            elif operator == '!=':
                return var_value != compare_value
            elif operator == '>':
                return var_value > compare_value
            elif operator == '<':
                return var_value < compare_value
            elif operator == '>=':
                return var_value >= compare_value
            elif operator == '<=':
                return var_value <= compare_value
            elif operator == 'in':
                return var_value in compare_value
            elif operator == 'not_in':
                return var_value not in compare_value
            else:
                return False
        
        elif condition.type == 'script':
            # Script-based condition
            try:
                local_vars = variables.copy()
                result = eval(condition.script, {"__builtins__": {}}, local_vars)
                return bool(result)
            except Exception:
                return False
        
        return False
    
    def _evaluate_expression(
        self,
        expression: str,
        variables: Dict[str, Any]
    ) -> Any:
        """Evaluate expression"""
        try:
            return eval(expression, {"__builtins__": {}}, variables)
        except Exception as e:
            raise ValueError(f"Expression evaluation failed: {str(e)}")
    
    def _evaluate_date_expression(
        self,
        expression: str,
        variables: Dict[str, Any]
    ) -> datetime:
        """Evaluate date expression"""
        # Simple implementation - supports relative dates
        if expression.startswith('+'):
            # Relative date (e.g., "+3d" = 3 days from now)
            import re
            match = re.match(r'\+(\d+)([hdwm])', expression)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'h':
                    return datetime.utcnow() + timedelta(hours=amount)
                elif unit == 'd':
                    return datetime.utcnow() + timedelta(days=amount)
                elif unit == 'w':
                    return datetime.utcnow() + timedelta(weeks=amount)
                elif unit == 'm':
                    return datetime.utcnow() + timedelta(days=amount * 30)
        
        # Default: 1 day from now
        return datetime.utcnow() + timedelta(days=1)
    
    # ==================== API EXECUTION ====================
    
    def _execute_api_call(
        self,
        config: Any,
        variables: Dict[str, Any]
    ) -> Any:
        """Execute API call"""
        url = config.api_endpoint
        method = config.api_method.upper()
        headers = config.api_headers or {}
        
        # Replace variables in URL
        for key, value in variables.items():
            url = url.replace(f"{{{key}}}", str(value))
        
        # Prepare body
        body = config.api_body or {}
        
        # Make request
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=body, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Return JSON if available
            try:
                return response.json()
            except Exception:
                return response.text
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"API call failed: {str(e)}")


# ==================== BPMN VALIDATOR ====================

class BPMNValidator:
    """Validates BPMN process definitions"""
    
    @staticmethod
    def validate_process(process: BPMNProcess) -> Dict[str, Any]:
        """
        Validate BPMN process
        
        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "warnings": List[str]
            }
        """
        errors = []
        warnings = []
        
        # Check for start events
        if not process.start_events:
            errors.append("Process must have at least one start event")
        
        # Check for end events
        if not process.end_events:
            warnings.append("Process should have at least one end event")
        
        # Collect all node IDs
        all_node_ids = set()
        all_nodes = (
            process.start_events +
            process.end_events +
            process.user_tasks +
            process.service_tasks +
            process.script_tasks +
            process.send_tasks +
            process.gateways +
            process.intermediate_events
        )
        
        for node in all_nodes:
            if node.id in all_node_ids:
                errors.append(f"Duplicate node ID: {node.id}")
            all_node_ids.add(node.id)
        
        # Validate sequence flows
        for flow in process.sequence_flows:
            if flow.source_ref not in all_node_ids:
                errors.append(f"Flow {flow.id} references non-existent source: {flow.source_ref}")
            if flow.target_ref not in all_node_ids:
                errors.append(f"Flow {flow.id} references non-existent target: {flow.target_ref}")
        
        # Check connectivity
        nodes_with_outgoing = {flow.source_ref for flow in process.sequence_flows}
        nodes_with_incoming = {flow.target_ref for flow in process.sequence_flows}
        
        # Start events should not have incoming flows
        for start_event in process.start_events:
            if start_event.id in nodes_with_incoming:
                warnings.append(f"Start event {start_event.id} has incoming flows")
        
        # End events should not have outgoing flows
        for end_event in process.end_events:
            if end_event.id in nodes_with_outgoing:
                errors.append(f"End event {end_event.id} has outgoing flows")
        
        # Non-end nodes should have outgoing flows
        non_end_nodes = [n for n in all_nodes if n not in process.end_events]
        for node in non_end_nodes:
            if node.id not in nodes_with_outgoing:
                warnings.append(f"Node {node.id} has no outgoing flows")
        
        # Validate gateways have multiple outgoing flows
        for gateway in process.gateways:
            outgoing_count = sum(
                1 for flow in process.sequence_flows 
                if flow.source_ref == gateway.id
            )
            if outgoing_count < 2:
                warnings.append(
                    f"Gateway {gateway.id} should have multiple outgoing flows"
                )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
