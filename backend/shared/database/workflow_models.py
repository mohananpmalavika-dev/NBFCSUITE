"""
Workflow Engine Database Models

This module contains all database models for workflow management including:
- Workflow Templates (reusable workflow definitions)
- Workflow Instances (active workflow executions)
- Workflow Steps (individual step executions)
- Workflow History (audit trail)
- Workflow Tasks (user task queue)
- Workflow SLA Tracking (deadline monitoring)

All models follow multi-tenant architecture with soft delete pattern.
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base


class WorkflowTemplate(Base):
    """
    Workflow Template
    
    Defines reusable workflow definitions that can be instantiated multiple times.
    Contains the workflow graph (steps and transitions) in JSON format.
    """
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Template Details
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    template_name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)  # loan_approval, deposit_approval, customer_kyc, etc.
    
    # Workflow Configuration
    workflow_type = Column(String(50), nullable=False)  # sequential, parallel, conditional
    trigger_event = Column(String(100))  # manual, event_based, scheduled
    
    # Definition (JSON structure of workflow graph)
    workflow_definition = Column(JSON, nullable=False)  # Complete workflow graph
    default_variables = Column(JSON)  # Default variable values
    
    # Version Control
    version = Column(Integer, default=1)
    parent_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    is_latest = Column(Boolean, default=True, index=True)
    
    # Status
    status = Column(String(50), default='draft', index=True)  # draft, active, archived
    is_active = Column(Boolean, default=True, index=True)
    
    # SLA Configuration
    default_sla_hours = Column(Integer)  # Default SLA for workflow completion
    escalation_enabled = Column(Boolean, default=False)
    escalation_rules = Column(JSON)  # Escalation configuration
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    instances = relationship("WorkflowInstance", back_populates="template")
    parent_template = relationship("WorkflowTemplate", remote_side=[id], backref="child_versions")
    
    def __repr__(self):
        return f"<WorkflowTemplate {self.template_code} - {self.template_name}>"


class WorkflowInstance(Base):
    """
    Workflow Instance
    
    Represents an active execution of a workflow template.
    Tracks current state, variables, and execution status.
    """
    __tablename__ = "workflow_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False, index=True)
    
    # Instance Identification
    instance_number = Column(String(50), unique=True, nullable=False, index=True)  # WF-YYYYMM-XXXX
    instance_name = Column(String(200))
    
    # Context (what entity is this workflow for)
    entity_type = Column(String(50), index=True)  # loan_application, deposit_account, customer, etc.
    entity_id = Column(Integer, index=True)  # Related entity ID
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(String(50), default='pending', index=True)
    # Status values: pending, in_progress, completed, failed, cancelled
    current_step_id = Column(Integer, ForeignKey("workflow_steps.id"))
    
    # Variables (Runtime Data)
    workflow_variables = Column(JSON)  # Current variable values during execution
    context_data = Column(JSON)  # Additional context information
    
    # Timing
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)
    deadline = Column(DateTime, index=True)  # SLA deadline
    
    # Priority
    priority = Column(String(20), default='normal', index=True)  # low, normal, high, urgent
    
    # Escalation
    is_escalated = Column(Boolean, default=False, index=True)
    escalated_at = Column(DateTime)
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Result
    result = Column(String(50))  # approved, rejected, completed, error
    result_message = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    template = relationship("WorkflowTemplate", back_populates="instances")
    initiator = relationship("User", foreign_keys=[initiated_by])
    escalated_user = relationship("User", foreign_keys=[escalated_to])
    steps = relationship("WorkflowStep", back_populates="instance", cascade="all, delete-orphan", 
                        foreign_keys="WorkflowStep.workflow_instance_id")
    history = relationship("WorkflowHistory", back_populates="instance", cascade="all, delete-orphan")
    tasks = relationship("WorkflowTask", back_populates="instance", cascade="all, delete-orphan")
    sla_tracking = relationship("WorkflowSLATracking", back_populates="instance", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkflowInstance {self.instance_number} - {self.status}>"


class WorkflowStep(Base):
    """
    Workflow Step
    
    Represents execution of an individual step within a workflow instance.
    Tracks step status, timing, assignment, and results.
    """
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    
    # Step Definition
    step_key = Column(String(100), nullable=False, index=True)  # Unique key from template
    step_name = Column(String(200), nullable=False)
    step_type = Column(String(50), nullable=False, index=True)
    # Step types: human_task, system_task, decision, timer, start, end
    
    # Execution Status
    status = Column(String(50), default='pending', index=True)
    # Status: pending, in_progress, completed, failed, skipped
    
    # Assignment (for human tasks)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)  # Specific user
    assigned_role = Column(String(100), index=True)  # Or role-based assignment
    
    # Timing
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)
    deadline = Column(DateTime, index=True)
    actual_duration = Column(Integer)  # Duration in minutes
    
    # Step Data
    input_data = Column(JSON)  # Input parameters for this step
    output_data = Column(JSON)  # Output/result data from this step
    
    # Action Taken
    action_taken = Column(String(100))  # approve, reject, complete, skip, etc.
    comments = Column(Text)
    
    # Retry Logic (for system tasks)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="steps", 
                           foreign_keys=[workflow_instance_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    completed_user = relationship("User", foreign_keys=[completed_by])
    tasks = relationship("WorkflowTask", back_populates="step")
    sla_tracking = relationship("WorkflowSLATracking", back_populates="step")
    
    def __repr__(self):
        return f"<WorkflowStep {self.step_name} - {self.status}>"


class WorkflowHistory(Base):
    """
    Workflow History
    
    Audit trail of all events that occur during workflow execution.
    Provides complete history for compliance and debugging.
    """
    __tablename__ = "workflow_history"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), index=True)
    
    # Event Details
    event_type = Column(String(50), nullable=False, index=True)
    # Event types: started, step_started, step_completed, transitioned, completed, failed, cancelled
    event_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Actor (who/what triggered this event)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    actor_type = Column(String(50))  # user, system
    
    # Transition Details
    from_step = Column(String(100))  # Previous step key
    to_step = Column(String(100))  # Next step key
    action = Column(String(100))  # Action that triggered transition
    
    # Event Data
    event_data = Column(JSON)  # Additional event data
    comments = Column(Text)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="history")
    step = relationship("WorkflowStep")
    actor = relationship("User")
    
    def __repr__(self):
        return f"<WorkflowHistory {self.event_type} at {self.event_timestamp}>"


class WorkflowTask(Base):
    """
    Workflow Task
    
    User-facing task that needs to be completed as part of workflow step.
    Appears in user's task queue/inbox.
    """
    __tablename__ = "workflow_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), nullable=False, index=True)
    
    # Task Details
    task_title = Column(String(200), nullable=False)
    task_description = Column(Text)
    task_type = Column(String(50), nullable=False, index=True)
    # Task types: approval, review, data_entry, document_upload
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)  # Direct assignment
    assigned_role = Column(String(100), index=True)  # Role-based assignment
    assignment_type = Column(String(50))  # direct, role_based, pool
    
    # Status
    status = Column(String(50), default='pending', index=True)
    # Status: pending, claimed, in_progress, completed, cancelled
    claimed_at = Column(DateTime)
    claimed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Priority
    priority = Column(String(20), default='normal', index=True)  # low, normal, high, urgent
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    due_date = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)
    
    # Task Data
    form_data = Column(JSON)  # Form fields to be filled
    attachments = Column(JSON)  # Required attachments
    
    # Result
    result = Column(String(50))  # approved, rejected, completed, etc.
    result_data = Column(JSON)  # Result data from task completion
    comments = Column(Text)
    
    # Audit Fields
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="tasks")
    step = relationship("WorkflowStep", back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    claimed_user = relationship("User", foreign_keys=[claimed_by])
    
    def __repr__(self):
        return f"<WorkflowTask {self.task_title} - {self.status}>"


class WorkflowSLATracking(Base):
    """
    Workflow SLA Tracking
    
    Tracks Service Level Agreement (SLA) compliance for workflows and steps.
    Monitors deadlines, breaches, and escalations.
    """
    __tablename__ = "workflow_sla_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), index=True)
    
    # SLA Details
    sla_type = Column(String(50), nullable=False, index=True)  # workflow_completion, step_completion
    sla_hours = Column(Integer, nullable=False)  # SLA duration in hours
    
    # Timing
    start_time = Column(DateTime, nullable=False, index=True)
    deadline = Column(DateTime, nullable=False, index=True)
    completion_time = Column(DateTime, index=True)
    
    # Status
    status = Column(String(50), default='active', index=True)
    # Status: active, met, breached, cancelled
    breach_time = Column(DateTime, index=True)  # When SLA was breached
    time_taken = Column(Integer)  # Actual time taken in minutes
    
    # Escalation
    escalation_level = Column(Integer, default=0)  # 0 = no escalation, 1+ = escalation levels
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    escalation_time = Column(DateTime)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instance = relationship("WorkflowInstance", back_populates="sla_tracking")
    step = relationship("WorkflowStep", back_populates="sla_tracking")
    escalated_user = relationship("User")
    
    def __repr__(self):
        return f"<WorkflowSLATracking {self.sla_type} - {self.status}>"


class WorkflowSLA(Base):
    """
    Enhanced Workflow SLA with Business Hours and Escalation Management
    
    Advanced SLA tracking with:
    - Business hours calculation
    - Holiday calendar support
    - Pause/resume functionality
    - Multi-level escalation
    - Detailed metrics
    """
    __tablename__ = "workflow_sla"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # SLA Configuration Reference
    sla_config_id = Column(String(100), nullable=False, index=True)
    
    # Associated Entity
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id"), index=True)
    
    # Status
    status = Column(String(50), default='active', nullable=False, index=True)
    # Status: active, met, breached, paused, cancelled
    
    # Time Tracking
    start_time = Column(DateTime, nullable=False, index=True)
    deadline = Column(DateTime, nullable=False, index=True)
    completion_time = Column(DateTime, index=True)
    
    # Pause Tracking
    total_paused_duration = Column(Integer, default=0)  # Total paused time in minutes
    pause_start = Column(DateTime)  # Current pause start time (if paused)
    pause_reason = Column(Text)
    
    # Escalation Tracking
    escalation_count = Column(Integer, default=0)
    last_escalation_time = Column(DateTime)
    escalated_to_users = Column(JSON, default=list)  # List of user IDs escalated to
    
    # Metrics (calculated periodically)
    time_elapsed_minutes = Column(Integer, default=0)  # Elapsed time excluding pauses
    time_remaining_minutes = Column(Integer, default=0)  # Time remaining
    sla_percentage = Column(Integer, default=0)  # 0-100, percentage of SLA consumed
    
    # Breach Information
    breach_time = Column(DateTime)  # When SLA was breached
    breach_duration_minutes = Column(Integer)  # How long breached
    
    # Metadata
    sla_metadata = Column(JSON)  # Additional SLA configuration and tracking data
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WorkflowSLA {self.entity_type}#{self.entity_id} - {self.status}>"
