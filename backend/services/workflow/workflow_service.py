"""
Workflow Engine Service
Enterprise-grade BPMN 2.0 compliant workflow execution engine
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json

from backend.services.workflow.workflow_models import (
    WorkflowTemplate, WorkflowNode, WorkflowConnection,
    ApprovalConfig, EscalationRule, WorkflowInstance,
    WorkflowExecution, ApprovalExecution, SLATracking, HolidayCalendar,
    NodeType, WorkflowStatus, TaskStatus, ApprovalDecision,
    ApprovalType, EscalationType, SLAUnit, GatewayType,
    WorkflowTemplateCreate, WorkflowNodeCreate, WorkflowConnectionCreate,
    ApprovalConfigCreate, EscalationRuleCreate, WorkflowInstanceCreate,
    ApprovalDecisionRequest, WorkflowStats, NodeStats
)


class WorkflowService:
    """Service for workflow management and execution"""
    
    def __init__(self, db: Session, tenant_id: UUID, user_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # =====================================================================
    # WORKFLOW TEMPLATE MANAGEMENT
    # =====================================================================
    
    def create_template(self, data: WorkflowTemplateCreate) -> WorkflowTemplate:
        """Create a new workflow template"""
        template = WorkflowTemplate(
            tenant_id=self.tenant_id,
            name=data.name,
            code=data.code,
            description=data.description,
            category=data.category,
            version=data.version,
            trigger_type=data.trigger_type,
            trigger_config=data.trigger_config,
            bpmn_xml=data.bpmn_xml,
            diagram_json=data.diagram_json,
            tags=data.tags,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def get_template(self, template_id: UUID) -> Optional[WorkflowTemplate]:
        """Get workflow template by ID"""
        return self.db.query(WorkflowTemplate).filter(
            and_(
                WorkflowTemplate.id == template_id,
                WorkflowTemplate.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_templates(
        self,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        status: Optional[WorkflowStatus] = None,
        search: Optional[str] = None
    ) -> List[WorkflowTemplate]:
        """List workflow templates with filters"""
        query = self.db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tenant_id == self.tenant_id
        )
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if status:
            query = query.filter(WorkflowTemplate.status == status)
        
        if search:
            query = query.filter(
                or_(
                    WorkflowTemplate.name.ilike(f"%{search}%"),
                    WorkflowTemplate.code.ilike(f"%{search}%"),
                    WorkflowTemplate.description.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(WorkflowTemplate.created_at)).offset(skip).limit(limit).all()
    
    def update_template(self, template_id: UUID, data: Dict[str, Any]) -> Optional[WorkflowTemplate]:
        """Update workflow template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        for key, value in data.items():
            if hasattr(template, key) and key not in ['id', 'tenant_id', 'created_at', 'created_by']:
                setattr(template, key, value)
        
        template.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def delete_template(self, template_id: UUID) -> bool:
        """Delete workflow template"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        # Check if there are active instances
        active_count = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.template_id == template_id,
                WorkflowInstance.tenant_id == self.tenant_id,
                WorkflowInstance.status == WorkflowStatus.ACTIVE
            )
        ).count()
        
        if active_count > 0:
            raise ValueError(f"Cannot delete template with {active_count} active instances")
        
        self.db.delete(template)
        self.db.commit()
        return True
    
    def activate_template(self, template_id: UUID) -> Optional[WorkflowTemplate]:
        """Activate workflow template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Validate template has at least start and end nodes
        start_nodes = [n for n in template.nodes if n.node_type == NodeType.START_EVENT]
        end_nodes = [n for n in template.nodes if n.node_type == NodeType.END_EVENT]
        
        if not start_nodes:
            raise ValueError("Template must have at least one START_EVENT node")
        if not end_nodes:
            raise ValueError("Template must have at least one END_EVENT node")
        
        template.status = WorkflowStatus.ACTIVE
        template.is_active = True
        template.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def deactivate_template(self, template_id: UUID) -> Optional[WorkflowTemplate]:
        """Deactivate workflow template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        template.is_active = False
        template.updated_by = self.user_id
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def clone_template(self, template_id: UUID, new_name: str, new_code: str) -> Optional[WorkflowTemplate]:
        """Clone workflow template"""
        original = self.get_template(template_id)
        if not original:
            return None
        
        # Create new template
        cloned = WorkflowTemplate(
            tenant_id=self.tenant_id,
            name=new_name,
            code=new_code,
            description=f"Cloned from {original.name}",
            category=original.category,
            version="1.0",
            trigger_type=original.trigger_type,
            trigger_config=original.trigger_config,
            bpmn_xml=original.bpmn_xml,
            diagram_json=original.diagram_json,
            tags=original.tags,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(cloned)
        self.db.flush()
        
        # Clone nodes
        node_mapping = {}  # Map old node IDs to new objects
        for node in original.nodes:
            cloned_node = WorkflowNode(
                template_id=cloned.id,
                tenant_id=self.tenant_id,
                node_id=node.node_id,
                node_type=node.node_type,
                name=node.name,
                description=node.description,
                position_x=node.position_x,
                position_y=node.position_y,
                width=node.width,
                height=node.height,
                config=node.config,
                assignee_type=node.assignee_type,
                assignee_value=node.assignee_value,
                form_key=node.form_key,
                service_class=node.service_class,
                service_method=node.service_method,
                service_params=node.service_params,
                script_language=node.script_language,
                script_content=node.script_content,
                gateway_type=node.gateway_type,
                default_path=node.default_path,
                timer_duration=node.timer_duration,
                timer_date=node.timer_date,
                timer_cycle=node.timer_cycle,
                sla_duration=node.sla_duration,
                sla_unit=node.sla_unit,
                sla_business_hours_only=node.sla_business_hours_only
            )
            self.db.add(cloned_node)
            node_mapping[node.id] = cloned_node
        
        self.db.flush()
        
        # Clone connections
        for conn in original.connections:
            cloned_conn = WorkflowConnection(
                template_id=cloned.id,
                tenant_id=self.tenant_id,
                connection_id=conn.connection_id,
                name=conn.name,
                source_node_id=conn.source_node_id,
                target_node_id=conn.target_node_id,
                condition_expression=conn.condition_expression,
                condition_type=conn.condition_type,
                is_default=conn.is_default,
                waypoints=conn.waypoints
            )
            self.db.add(cloned_conn)
        
        self.db.commit()
        self.db.refresh(cloned)
        return cloned
    
    # =====================================================================
    # WORKFLOW NODE MANAGEMENT
    # =====================================================================
    
    def create_node(self, template_id: UUID, data: WorkflowNodeCreate) -> WorkflowNode:
        """Create workflow node"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")
        
        node = WorkflowNode(
            template_id=template_id,
            tenant_id=self.tenant_id,
            **data.dict()
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node
    
    def get_node(self, node_id: UUID) -> Optional[WorkflowNode]:
        """Get workflow node by ID"""
        return self.db.query(WorkflowNode).filter(
            and_(
                WorkflowNode.id == node_id,
                WorkflowNode.tenant_id == self.tenant_id
            )
        ).first()
    
    def update_node(self, node_id: UUID, data: Dict[str, Any]) -> Optional[WorkflowNode]:
        """Update workflow node"""
        node = self.get_node(node_id)
        if not node:
            return None
        
        for key, value in data.items():
            if hasattr(node, key) and key not in ['id', 'template_id', 'tenant_id', 'created_at']:
                setattr(node, key, value)
        
        self.db.commit()
        self.db.refresh(node)
        return node
    
    def delete_node(self, node_id: UUID) -> bool:
        """Delete workflow node"""
        node = self.get_node(node_id)
        if not node:
            return False
        
        self.db.delete(node)
        self.db.commit()
        return True
    
    # =====================================================================
    # WORKFLOW CONNECTION MANAGEMENT
    # =====================================================================
    
    def create_connection(self, template_id: UUID, data: WorkflowConnectionCreate) -> WorkflowConnection:
        """Create workflow connection"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")
        
        connection = WorkflowConnection(
            template_id=template_id,
            tenant_id=self.tenant_id,
            **data.dict()
        )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection
    
    def delete_connection(self, connection_id: UUID) -> bool:
        """Delete workflow connection"""
        connection = self.db.query(WorkflowConnection).filter(
            and_(
                WorkflowConnection.id == connection_id,
                WorkflowConnection.tenant_id == self.tenant_id
            )
        ).first()
        
        if not connection:
            return False
        
        self.db.delete(connection)
        self.db.commit()
        return True
    
    # =====================================================================
    # APPROVAL CONFIGURATION
    # =====================================================================
    
    def create_approval_config(self, node_id: UUID, data: ApprovalConfigCreate) -> ApprovalConfig:
        """Create approval configuration for a node"""
        node = self.get_node(node_id)
        if not node:
            raise ValueError("Node not found")
        
        if node.node_type != NodeType.USER_TASK:
            raise ValueError("Approval config can only be added to USER_TASK nodes")
        
        config = ApprovalConfig(
            node_id=node_id,
            tenant_id=self.tenant_id,
            **data.dict()
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_approval_config(self, config_id: UUID, data: Dict[str, Any]) -> Optional[ApprovalConfig]:
        """Update approval configuration"""
        config = self.db.query(ApprovalConfig).filter(
            and_(
                ApprovalConfig.id == config_id,
                ApprovalConfig.tenant_id == self.tenant_id
            )
        ).first()
        
        if not config:
            return None
        
        for key, value in data.items():
            if hasattr(config, key) and key not in ['id', 'node_id', 'tenant_id', 'created_at']:
                setattr(config, key, value)
        
        self.db.commit()
        self.db.refresh(config)
        return config
    
    # =====================================================================
    # ESCALATION RULES
    # =====================================================================
    
    def create_escalation_rule(self, node_id: UUID, data: EscalationRuleCreate) -> EscalationRule:
        """Create escalation rule for a node"""
        node = self.get_node(node_id)
        if not node:
            raise ValueError("Node not found")
        
        rule = EscalationRule(
            node_id=node_id,
            tenant_id=self.tenant_id,
            **data.dict()
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_escalation_rules(self, node_id: UUID) -> List[EscalationRule]:
        """Get all escalation rules for a node"""
        return self.db.query(EscalationRule).filter(
            and_(
                EscalationRule.node_id == node_id,
                EscalationRule.tenant_id == self.tenant_id
            )
        ).order_by(EscalationRule.escalation_level).all()
    
    # =====================================================================
    # WORKFLOW INSTANCE EXECUTION
    # =====================================================================
    
    def start_workflow(self, data: WorkflowInstanceCreate) -> WorkflowInstance:
        """Start a new workflow instance"""
        template = self.get_template(data.template_id)
        if not template:
            raise ValueError("Template not found")
        
        if not template.is_active:
            raise ValueError("Template is not active")
        
        # Create instance
        instance = WorkflowInstance(
            template_id=data.template_id,
            tenant_id=self.tenant_id,
            instance_name=data.instance_name or template.name,
            business_key=data.business_key,
            variables=data.variables or {},
            priority=data.priority,
            status=WorkflowStatus.ACTIVE,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        self.db.add(instance)
        self.db.flush()
        
        # Find start node
        start_node = next((n for n in template.nodes if n.node_type == NodeType.START_EVENT), None)
        if not start_node:
            raise ValueError("Template has no START_EVENT node")
        
        # Execute start node
        instance.current_node_id = start_node.node_id
        self._execute_node(instance, start_node)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def get_instance(self, instance_id: UUID) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID"""
        return self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.id == instance_id,
                WorkflowInstance.tenant_id == self.tenant_id
            )
        ).first()
    
    def list_instances(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[WorkflowStatus] = None,
        template_id: Optional[UUID] = None,
        business_key: Optional[str] = None
    ) -> List[WorkflowInstance]:
        """List workflow instances with filters"""
        query = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id
        )
        
        if status:
            query = query.filter(WorkflowInstance.status == status)
        
        if template_id:
            query = query.filter(WorkflowInstance.template_id == template_id)
        
        if business_key:
            query = query.filter(WorkflowInstance.business_key == business_key)
        
        return query.order_by(desc(WorkflowInstance.created_at)).offset(skip).limit(limit).all()
    
    def cancel_instance(self, instance_id: UUID, reason: str = None) -> Optional[WorkflowInstance]:
        """Cancel workflow instance"""
        instance = self.get_instance(instance_id)
        if not instance:
            return None
        
        instance.status = WorkflowStatus.CANCELLED
        instance.error_message = reason
        instance.completed_at = datetime.utcnow()
        instance.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def _execute_node(self, instance: WorkflowInstance, node: WorkflowNode):
        """Execute a workflow node"""
        # Create execution record
        execution = WorkflowExecution(
            instance_id=instance.id,
            tenant_id=self.tenant_id,
            node_id=node.node_id,
            node_name=node.name,
            node_type=node.node_type,
            status=TaskStatus.IN_PROGRESS
        )
        self.db.add(execution)
        self.db.flush()
        
        # Create SLA tracking if configured
        if node.sla_duration and node.sla_unit:
            due_date = self._calculate_sla_due_date(
                node.sla_duration,
                node.sla_unit,
                node.sla_business_hours_only
            )
            sla_tracking = SLATracking(
                instance_id=instance.id,
                execution_id=execution.id,
                tenant_id=self.tenant_id,
                node_id=node.node_id,
                node_name=node.name,
                sla_duration=node.sla_duration,
                sla_unit=node.sla_unit,
                business_hours_only=node.sla_business_hours_only,
                due_date=due_date
            )
            self.db.add(sla_tracking)
            execution.due_date = due_date
        
        # Handle different node types
        if node.node_type == NodeType.START_EVENT:
            # Start event - immediately move to next node
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            self._move_to_next_node(instance, node)
        
        elif node.node_type == NodeType.END_EVENT:
            # End event - complete workflow
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.utcnow()
        
        elif node.node_type == NodeType.USER_TASK:
            # User task - create approval if configured
            execution.status = TaskStatus.PENDING
            if node.approval_config:
                self._create_approval_executions(instance, execution, node.approval_config)
        
        elif node.node_type == NodeType.SERVICE_TASK:
            # Service task - execute service (simulated for now)
            try:
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                self._move_to_next_node(instance, node)
            except Exception as e:
                execution.status = TaskStatus.FAILED
                execution.error_message = str(e)
        
        elif node.node_type == NodeType.SCRIPT_TASK:
            # Script task - execute script (simulated for now)
            try:
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                self._move_to_next_node(instance, node)
            except Exception as e:
                execution.status = TaskStatus.FAILED
                execution.error_message = str(e)
        
        elif node.node_type in [NodeType.EXCLUSIVE_GATEWAY, NodeType.PARALLEL_GATEWAY, NodeType.INCLUSIVE_GATEWAY]:
            # Gateway - evaluate conditions and route
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            self._execute_gateway(instance, node)
        
        elif node.node_type == NodeType.TIMER_EVENT:
            # Timer event - schedule for later (simulated)
            execution.status = TaskStatus.PENDING
    
    def _move_to_next_node(self, instance: WorkflowInstance, current_node: WorkflowNode):
        """Move workflow to next node"""
        template = instance.template
        
        # Find outgoing connections
        connections = [c for c in template.connections if c.source_node_id == current_node.node_id]
        
        if not connections:
            # No outgoing connections - workflow stuck
            instance.status = WorkflowStatus.ERROR
            instance.error_message = f"Node {current_node.node_id} has no outgoing connections"
            return
        
        # For simple case, take first connection
        next_connection = connections[0]
        next_node = next((n for n in template.nodes if n.node_id == next_connection.target_node_id), None)
        
        if next_node:
            instance.current_node_id = next_node.node_id
            self._execute_node(instance, next_node)
    
    def _execute_gateway(self, instance: WorkflowInstance, gateway_node: WorkflowNode):
        """Execute gateway logic"""
        template = instance.template
        connections = [c for c in template.connections if c.source_node_id == gateway_node.node_id]
        
        if gateway_node.gateway_type == GatewayType.EXCLUSIVE:
            # Exclusive gateway - take one path based on condition
            for conn in connections:
                if conn.is_default or self._evaluate_condition(conn.condition_expression, instance.variables):
                    next_node = next((n for n in template.nodes if n.node_id == conn.target_node_id), None)
                    if next_node:
                        instance.current_node_id = next_node.node_id
                        self._execute_node(instance, next_node)
                    break
        
        elif gateway_node.gateway_type == GatewayType.PARALLEL:
            # Parallel gateway - execute all paths simultaneously (simulated as sequential)
            for conn in connections:
                next_node = next((n for n in template.nodes if n.node_id == conn.target_node_id), None)
                if next_node:
                    self._execute_node(instance, next_node)
        
        elif gateway_node.gateway_type == GatewayType.INCLUSIVE:
            # Inclusive gateway - execute paths that meet conditions
            for conn in connections:
                if conn.is_default or self._evaluate_condition(conn.condition_expression, instance.variables):
                    next_node = next((n for n in template.nodes if n.node_id == conn.target_node_id), None)
                    if next_node:
                        self._execute_node(instance, next_node)
    
    def _evaluate_condition(self, condition: Optional[str], variables: Dict[str, Any]) -> bool:
        """Evaluate condition expression (simplified)"""
        if not condition:
            return True
        
        # Simple evaluation - in production, use proper expression evaluator
        try:
            # Replace variable references with actual values
            for key, value in variables.items():
                condition = condition.replace(f"${{{key}}}", str(value))
            
            # Evaluate as Python expression (UNSAFE - use proper parser in production)
            return eval(condition)
        except:
            return False
    
    def _create_approval_executions(
        self,
        instance: WorkflowInstance,
        execution: WorkflowExecution,
        config: ApprovalConfig
    ):
        """Create approval executions based on approval configuration"""
        approvers = self._get_approvers(config)
        
        if config.approval_type == ApprovalType.SEQUENTIAL:
            # Sequential - create first approval only
            if approvers:
                self._create_approval(instance, execution, approvers[0], config, 1)
        
        elif config.approval_type == ApprovalType.PARALLEL:
            # Parallel - create all approvals
            for idx, approver_id in enumerate(approvers, 1):
                self._create_approval(instance, execution, approver_id, config, idx)
        
        elif config.approval_type == ApprovalType.ANY_ONE:
            # Any one - create all approvals
            for idx, approver_id in enumerate(approvers, 1):
                self._create_approval(instance, execution, approver_id, config, idx)
        
        elif config.approval_type == ApprovalType.MAJORITY:
            # Majority - create all approvals
            for idx, approver_id in enumerate(approvers, 1):
                self._create_approval(instance, execution, approver_id, config, idx)
    
    def _get_approvers(self, config: ApprovalConfig) -> List[UUID]:
        """Get list of approver user IDs based on configuration"""
        approvers = []
        
        if config.approver_users:
            approvers.extend([UUID(u) for u in config.approver_users])
        
        if config.approver_roles:
            # In production, query users with these roles
            # For now, return empty list
            pass
        
        return approvers
    
    def _create_approval(
        self,
        instance: WorkflowInstance,
        execution: WorkflowExecution,
        approver_id: UUID,
        config: ApprovalConfig,
        level: int
    ):
        """Create single approval execution"""
        due_date = execution.due_date or (datetime.utcnow() + timedelta(days=1))
        
        approval = ApprovalExecution(
            instance_id=instance.id,
            execution_id=execution.id,
            tenant_id=self.tenant_id,
            approver_id=approver_id,
            approval_level=level,
            due_date=due_date
        )
        self.db.add(approval)
    
    # =====================================================================
    # APPROVAL PROCESSING
    # =====================================================================
    
    def process_approval(
        self,
        approval_id: UUID,
        decision_data: ApprovalDecisionRequest
    ) -> Optional[ApprovalExecution]:
        """Process an approval decision"""
        approval = self.db.query(ApprovalExecution).filter(
            and_(
                ApprovalExecution.id == approval_id,
                ApprovalExecution.tenant_id == self.tenant_id,
                ApprovalExecution.approver_id == self.user_id
            )
        ).first()
        
        if not approval:
            raise ValueError("Approval not found or not assigned to current user")
        
        if approval.decision != ApprovalDecision.PENDING:
            raise ValueError("Approval already processed")
        
        # Update approval
        approval.decision = decision_data.decision
        approval.comments = decision_data.comments
        approval.reason = decision_data.reason
        approval.responded_at = datetime.utcnow()
        
        # Get instance and execution
        instance = approval.instance
        execution = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.id == approval.execution_id
        ).first()
        
        # Check if approval flow is complete
        if self._is_approval_complete(execution, approval):
            # Mark execution as completed
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            
            # Move to next node
            template = instance.template
            current_node = next((n for n in template.nodes if n.node_id == execution.node_id), None)
            if current_node:
                self._move_to_next_node(instance, current_node)
        
        self.db.commit()
        self.db.refresh(approval)
        return approval
    
    def _is_approval_complete(self, execution: WorkflowExecution, latest_approval: ApprovalExecution) -> bool:
        """Check if approval flow is complete"""
        # Get all approvals for this execution
        all_approvals = self.db.query(ApprovalExecution).filter(
            ApprovalExecution.execution_id == execution.id
        ).all()
        
        # Get node and approval config
        node = self.db.query(WorkflowNode).filter(
            WorkflowNode.node_id == execution.node_id
        ).first()
        
        if not node or not node.approval_config:
            return True
        
        config = node.approval_config
        
        if config.approval_type == ApprovalType.SEQUENTIAL:
            # Check if current approval is approved
            if latest_approval.decision == ApprovalDecision.APPROVED:
                # Check if there are more approvers
                pending_approvals = [a for a in all_approvals if a.decision == ApprovalDecision.PENDING]
                if not pending_approvals:
                    return True
                # Create next approval if needed
            else:
                # Rejected - workflow stops
                return True
        
        elif config.approval_type == ApprovalType.PARALLEL:
            # All must approve
            approved = [a for a in all_approvals if a.decision == ApprovalDecision.APPROVED]
            rejected = [a for a in all_approvals if a.decision == ApprovalDecision.REJECTED]
            
            if rejected:
                return True  # Any rejection completes the flow
            
            if len(approved) == len(all_approvals):
                return True  # All approved
        
        elif config.approval_type == ApprovalType.ANY_ONE:
            # First approval/rejection completes
            return latest_approval.decision in [ApprovalDecision.APPROVED, ApprovalDecision.REJECTED]
        
        elif config.approval_type == ApprovalType.MAJORITY:
            # Check if threshold met
            approved = [a for a in all_approvals if a.decision == ApprovalDecision.APPROVED]
            rejected = [a for a in all_approvals if a.decision == ApprovalDecision.REJECTED]
            
            if config.approval_threshold:
                if len(approved) >= config.approval_threshold:
                    return True
            elif config.approval_percentage:
                approval_rate = len(approved) / len(all_approvals) * 100
                if approval_rate >= config.approval_percentage:
                    return True
        
        return False
    
    def get_pending_approvals(
        self,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ApprovalExecution]:
        """Get pending approvals for a user"""
        query = self.db.query(ApprovalExecution).filter(
            and_(
                ApprovalExecution.tenant_id == self.tenant_id,
                ApprovalExecution.decision == ApprovalDecision.PENDING
            )
        )
        
        if user_id:
            query = query.filter(ApprovalExecution.approver_id == user_id)
        else:
            query = query.filter(ApprovalExecution.approver_id == self.user_id)
        
        return query.order_by(ApprovalExecution.due_date).offset(skip).limit(limit).all()
    
    # =====================================================================
    # SLA TRACKING
    # =====================================================================
    
    def _calculate_sla_due_date(
        self,
        duration: int,
        unit: SLAUnit,
        business_hours_only: bool = False
    ) -> datetime:
        """Calculate SLA due date"""
        now = datetime.utcnow()
        
        if unit == SLAUnit.MINUTES:
            return now + timedelta(minutes=duration)
        elif unit == SLAUnit.HOURS:
            return now + timedelta(hours=duration)
        elif unit == SLAUnit.DAYS:
            return now + timedelta(days=duration)
        elif unit == SLAUnit.BUSINESS_DAYS:
            # Calculate business days (excluding weekends and holidays)
            current = now
            days_added = 0
            
            while days_added < duration:
                current += timedelta(days=1)
                # Check if it's a weekday (Monday=0, Sunday=6)
                if current.weekday() < 5:  # Monday to Friday
                    # Check if it's not a holiday
                    is_holiday = self.db.query(HolidayCalendar).filter(
                        and_(
                            HolidayCalendar.tenant_id == self.tenant_id,
                            HolidayCalendar.holiday_date == current.date(),
                            HolidayCalendar.is_working_day == False
                        )
                    ).first()
                    
                    if not is_holiday:
                        days_added += 1
            
            return current
        
        return now
    
    def check_sla_breaches(self) -> List[SLATracking]:
        """Check and update SLA breaches"""
        now = datetime.utcnow()
        
        # Get all pending SLA trackings
        sla_trackings = self.db.query(SLATracking).filter(
            and_(
                SLATracking.tenant_id == self.tenant_id,
                SLATracking.completed_at.is_(None),
                SLATracking.is_paused == False
            )
        ).all()
        
        breached = []
        for sla in sla_trackings:
            if now > sla.due_date and not sla.is_breached:
                sla.is_breached = True
                sla.breach_duration = int((now - sla.due_date).total_seconds())
                breached.append(sla)
        
        if breached:
            self.db.commit()
        
        return breached
    
    def pause_sla(self, sla_id: UUID, reason: str) -> Optional[SLATracking]:
        """Pause SLA tracking"""
        sla = self.db.query(SLATracking).filter(
            and_(
                SLATracking.id == sla_id,
                SLATracking.tenant_id == self.tenant_id
            )
        ).first()
        
        if not sla:
            return None
        
        sla.is_paused = True
        sla.paused_at = datetime.utcnow()
        sla.pause_reason = reason
        
        self.db.commit()
        self.db.refresh(sla)
        return sla
    
    def resume_sla(self, sla_id: UUID) -> Optional[SLATracking]:
        """Resume SLA tracking"""
        sla = self.db.query(SLATracking).filter(
            and_(
                SLATracking.id == sla_id,
                SLATracking.tenant_id == self.tenant_id
            )
        ).first()
        
        if not sla or not sla.is_paused:
            return None
        
        now = datetime.utcnow()
        pause_duration = int((now - sla.paused_at).total_seconds())
        sla.paused_duration += pause_duration
        sla.is_paused = False
        sla.resumed_at = now
        # Extend due date by pause duration
        sla.due_date = sla.due_date + timedelta(seconds=pause_duration)
        
        self.db.commit()
        self.db.refresh(sla)
        return sla
    
    # =====================================================================
    # ESCALATION PROCESSING
    # =====================================================================
    
    def check_escalations(self) -> List[ApprovalExecution]:
        """Check and trigger escalations"""
        now = datetime.utcnow()
        escalated = []
        
        # Get pending approvals
        pending_approvals = self.db.query(ApprovalExecution).filter(
            and_(
                ApprovalExecution.tenant_id == self.tenant_id,
                ApprovalExecution.decision == ApprovalDecision.PENDING,
                ApprovalExecution.is_escalated == False
            )
        ).all()
        
        for approval in pending_approvals:
            # Get execution and node
            execution = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.id == approval.execution_id
            ).first()
            
            if not execution:
                continue
            
            node = self.db.query(WorkflowNode).filter(
                and_(
                    WorkflowNode.node_id == execution.node_id,
                    WorkflowNode.tenant_id == self.tenant_id
                )
            ).first()
            
            if not node:
                continue
            
            # Check escalation rules
            for rule in node.escalation_rules:
                trigger_time = approval.assigned_at + self._get_timedelta(
                    rule.trigger_after_duration,
                    rule.trigger_after_unit
                )
                
                if now >= trigger_time:
                    # Trigger escalation
                    approval.is_escalated = True
                    approval.escalated_at = now
                    approval.escalation_level = rule.escalation_level
                    escalated.append(approval)
                    
                    # Handle escalation actions
                    if rule.escalation_type == EscalationType.HARD and rule.auto_reassign:
                        # Reassign to next level (simulated)
                        pass
        
        if escalated:
            self.db.commit()
        
        return escalated
    
    def _get_timedelta(self, duration: int, unit: SLAUnit) -> timedelta:
        """Convert duration and unit to timedelta"""
        if unit == SLAUnit.MINUTES:
            return timedelta(minutes=duration)
        elif unit == SLAUnit.HOURS:
            return timedelta(hours=duration)
        elif unit in [SLAUnit.DAYS, SLAUnit.BUSINESS_DAYS]:
            return timedelta(days=duration)
        return timedelta(0)
    
    # =====================================================================
    # ANALYTICS & MONITORING
    # =====================================================================
    
    def get_workflow_stats(self, template_id: Optional[UUID] = None) -> WorkflowStats:
        """Get workflow statistics"""
        query = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.tenant_id == self.tenant_id
        )
        
        if template_id:
            query = query.filter(WorkflowInstance.template_id == template_id)
        
        total_instances = query.count()
        active_instances = query.filter(WorkflowInstance.status == WorkflowStatus.ACTIVE).count()
        completed_instances = query.filter(WorkflowInstance.status == WorkflowStatus.COMPLETED).count()
        
        # Pending approvals
        pending_approvals = self.db.query(ApprovalExecution).filter(
            and_(
                ApprovalExecution.tenant_id == self.tenant_id,
                ApprovalExecution.decision == ApprovalDecision.PENDING
            )
        ).count()
        
        # SLA breached
        sla_breached = self.db.query(SLATracking).filter(
            and_(
                SLATracking.tenant_id == self.tenant_id,
                SLATracking.is_breached == True,
                SLATracking.completed_at.is_(None)
            )
        ).count()
        
        # Average cycle time
        completed_with_time = query.filter(
            and_(
                WorkflowInstance.status == WorkflowStatus.COMPLETED,
                WorkflowInstance.completed_at.isnot(None)
            )
        ).all()
        
        if completed_with_time:
            total_hours = sum([
                (inst.completed_at - inst.started_at).total_seconds() / 3600
                for inst in completed_with_time
            ])
            avg_cycle_time = total_hours / len(completed_with_time)
        else:
            avg_cycle_time = 0.0
        
        # Completion rate
        completion_rate = (completed_instances / total_instances * 100) if total_instances > 0 else 0.0
        
        return WorkflowStats(
            total_instances=total_instances,
            active_instances=active_instances,
            completed_instances=completed_instances,
            pending_approvals=pending_approvals,
            sla_breached=sla_breached,
            avg_cycle_time_hours=round(avg_cycle_time, 2),
            completion_rate=round(completion_rate, 2)
        )
    
    def get_node_stats(self, template_id: UUID) -> List[NodeStats]:
        """Get statistics per node for a template"""
        template = self.get_template(template_id)
        if not template:
            return []
        
        node_stats_list = []
        
        for node in template.nodes:
            # Get all executions for this node
            executions = self.db.query(WorkflowExecution).join(
                WorkflowInstance
            ).filter(
                and_(
                    WorkflowInstance.template_id == template_id,
                    WorkflowInstance.tenant_id == self.tenant_id,
                    WorkflowExecution.node_id == node.node_id
                )
            ).all()
            
            total_executions = len(executions)
            pending_count = len([e for e in executions if e.status == TaskStatus.PENDING])
            
            # Calculate average duration for completed executions
            completed_executions = [
                e for e in executions
                if e.status == TaskStatus.COMPLETED and e.completed_at
            ]
            
            if completed_executions:
                total_minutes = sum([
                    (e.completed_at - e.started_at).total_seconds() / 60
                    for e in completed_executions
                ])
                avg_duration = total_minutes / len(completed_executions)
            else:
                avg_duration = 0.0
            
            # SLA breach count
            sla_breach_count = self.db.query(SLATracking).join(
                WorkflowInstance
            ).filter(
                and_(
                    WorkflowInstance.template_id == template_id,
                    WorkflowInstance.tenant_id == self.tenant_id,
                    SLATracking.node_id == node.node_id,
                    SLATracking.is_breached == True
                )
            ).count()
            
            node_stats_list.append(NodeStats(
                node_id=node.node_id,
                node_name=node.name,
                total_executions=total_executions,
                avg_duration_minutes=round(avg_duration, 2),
                pending_count=pending_count,
                sla_breach_count=sla_breach_count
            ))
        
        return node_stats_list
    
    def get_bottleneck_nodes(self, template_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """Identify bottleneck nodes with longest pending times"""
        template = self.get_template(template_id)
        if not template:
            return []
        
        bottlenecks = []
        
        for node in template.nodes:
            # Get pending executions
            pending_executions = self.db.query(WorkflowExecution).join(
                WorkflowInstance
            ).filter(
                and_(
                    WorkflowInstance.template_id == template_id,
                    WorkflowInstance.tenant_id == self.tenant_id,
                    WorkflowExecution.node_id == node.node_id,
                    WorkflowExecution.status == TaskStatus.PENDING
                )
            ).all()
            
            if pending_executions:
                now = datetime.utcnow()
                total_pending_hours = sum([
                    (now - e.started_at).total_seconds() / 3600
                    for e in pending_executions
                ])
                avg_pending_hours = total_pending_hours / len(pending_executions)
                
                bottlenecks.append({
                    'node_id': node.node_id,
                    'node_name': node.name,
                    'pending_count': len(pending_executions),
                    'avg_pending_hours': round(avg_pending_hours, 2),
                    'total_pending_hours': round(total_pending_hours, 2)
                })
        
        # Sort by total pending hours
        bottlenecks.sort(key=lambda x: x['total_pending_hours'], reverse=True)
        return bottlenecks[:limit]
    
    def get_user_productivity(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get user productivity metrics"""
        target_user = user_id or self.user_id
        
        query = self.db.query(ApprovalExecution).filter(
            and_(
                ApprovalExecution.tenant_id == self.tenant_id,
                ApprovalExecution.approver_id == target_user
            )
        )
        
        if start_date:
            query = query.filter(ApprovalExecution.assigned_at >= start_date)
        
        if end_date:
            query = query.filter(ApprovalExecution.assigned_at <= end_date)
        
        all_approvals = query.all()
        total_assigned = len(all_approvals)
        completed = [a for a in all_approvals if a.decision != ApprovalDecision.PENDING]
        pending = [a for a in all_approvals if a.decision == ApprovalDecision.PENDING]
        
        approved = [a for a in completed if a.decision == ApprovalDecision.APPROVED]
        rejected = [a for a in completed if a.decision == ApprovalDecision.REJECTED]
        
        # Calculate average response time
        if completed:
            total_response_hours = sum([
                (a.responded_at - a.assigned_at).total_seconds() / 3600
                for a in completed if a.responded_at
            ])
            avg_response_hours = total_response_hours / len(completed)
        else:
            avg_response_hours = 0.0
        
        # Calculate approval rate
        approval_rate = (len(approved) / len(completed) * 100) if completed else 0.0
        
        return {
            'user_id': str(target_user),
            'total_assigned': total_assigned,
            'completed': len(completed),
            'pending': len(pending),
            'approved': len(approved),
            'rejected': len(rejected),
            'avg_response_hours': round(avg_response_hours, 2),
            'approval_rate': round(approval_rate, 2),
            'completion_rate': round(len(completed) / total_assigned * 100, 2) if total_assigned > 0 else 0.0
        }
    
    # =====================================================================
    # PROCESS MINING
    # =====================================================================
    
    def get_actual_workflow_paths(self, template_id: UUID) -> Dict[str, Any]:
        """Analyze actual workflow execution paths (process mining)"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        # Get all completed instances
        instances = self.db.query(WorkflowInstance).filter(
            and_(
                WorkflowInstance.template_id == template_id,
                WorkflowInstance.tenant_id == self.tenant_id,
                WorkflowInstance.status == WorkflowStatus.COMPLETED
            )
        ).all()
        
        path_frequencies = {}
        
        for instance in instances:
            # Get execution sequence
            executions = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.instance_id == instance.id
            ).order_by(WorkflowExecution.started_at).all()
            
            # Create path string
            path = " -> ".join([e.node_id for e in executions])
            
            if path in path_frequencies:
                path_frequencies[path] += 1
            else:
                path_frequencies[path] = 1
        
        # Sort by frequency
        sorted_paths = sorted(
            path_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'template_id': str(template_id),
            'total_instances': len(instances),
            'unique_paths': len(path_frequencies),
            'most_common_paths': [
                {'path': path, 'frequency': freq, 'percentage': round(freq / len(instances) * 100, 2)}
                for path, freq in sorted_paths[:10]
            ] if instances else []
        }
    
    def get_deviation_analysis(self, template_id: UUID) -> Dict[str, Any]:
        """Analyze deviations from designed workflow"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        # Get designed path (simplified - just node sequence)
        designed_nodes = [n.node_id for n in sorted(template.nodes, key=lambda x: x.position_x)]
        designed_path = " -> ".join(designed_nodes)
        
        # Get actual paths
        actual_paths = self.get_actual_workflow_paths(template_id)
        
        deviations = []
        if actual_paths.get('most_common_paths'):
            for path_data in actual_paths['most_common_paths']:
                if path_data['path'] != designed_path:
                    deviations.append({
                        'actual_path': path_data['path'],
                        'frequency': path_data['frequency'],
                        'percentage': path_data['percentage'],
                        'deviation_type': 'PATH_MISMATCH'
                    })
        
        return {
            'template_id': str(template_id),
            'designed_path': designed_path,
            'total_deviations': len(deviations),
            'deviation_rate': round(
                sum([d['percentage'] for d in deviations]),
                2
            ),
            'deviations': deviations
        }
    
    # =====================================================================
    # HOLIDAY CALENDAR
    # =====================================================================
    
    def add_holiday(
        self,
        holiday_date: datetime,
        holiday_name: str,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> HolidayCalendar:
        """Add holiday to calendar"""
        holiday = HolidayCalendar(
            tenant_id=self.tenant_id,
            holiday_date=holiday_date,
            holiday_name=holiday_name,
            country=country,
            state=state,
            city=city,
            created_by=self.user_id
        )
        self.db.add(holiday)
        self.db.commit()
        self.db.refresh(holiday)
        return holiday
    
    def get_holidays(
        self,
        start_date: datetime,
        end_date: datetime,
        country: Optional[str] = None
    ) -> List[HolidayCalendar]:
        """Get holidays in date range"""
        query = self.db.query(HolidayCalendar).filter(
            and_(
                HolidayCalendar.tenant_id == self.tenant_id,
                HolidayCalendar.holiday_date >= start_date,
                HolidayCalendar.holiday_date <= end_date
            )
        )
        
        if country:
            query = query.filter(HolidayCalendar.country == country)
        
        return query.order_by(HolidayCalendar.holiday_date).all()
