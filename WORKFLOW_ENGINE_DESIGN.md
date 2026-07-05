# 🔄 Workflow Engine Module - Complete Design

**Date**: July 5, 2026  
**Status**: 🎯 Starting Implementation  
**Priority**: HIGH - Critical Infrastructure Component

---

## 🎯 Module Overview

The Workflow Engine is a critical infrastructure component that enables dynamic workflow management across all modules of the NBFC Financial Suite. It provides a flexible, configurable system for defining business processes, approval chains, task management, and SLA tracking.

### Business Value
- **Process Automation**: Automate complex business processes
- **Approval Management**: Multi-level approval workflows
- **Compliance**: Audit trail and regulatory compliance
- **Efficiency**: Reduce manual intervention and errors
- **Flexibility**: Easy to configure without code changes
- **Scalability**: Handle thousands of concurrent workflows

---

## 📋 Core Concepts

### 1. Workflow Definition
A workflow is a series of steps (nodes) connected by transitions (edges) that define how a business process flows from start to completion.

**Key Components**:
- **Workflow Template**: Reusable workflow definition
- **Workflow Instance**: Actual execution of a workflow
- **Workflow Step**: Individual task/action in the workflow
- **Transition**: Connection between steps with conditions
- **Variables**: Data passed through workflow execution

### 2. Workflow Types

#### Sequential Workflow
Steps execute one after another in a defined order.
```
Start → Step 1 → Step 2 → Step 3 → End
```

#### Parallel Workflow
Multiple steps execute simultaneously.
```
        ┌─→ Step 2a ─┐
Start ──┤            ├─→ Step 4 → End
        └─→ Step 2b ─┘
```

#### Conditional Workflow
Steps execute based on conditions.
```
        ┌─→ Step 2a (if approved) ─→ End
Start ──┤
        └─→ Step 2b (if rejected) ─→ End
```

#### Approval Chain Workflow
Multi-level approval process.
```
Start → L1 Approval → L2 Approval → L3 Approval → End
         ↓ reject       ↓ reject       ↓ reject
         └──────────────┴──────────────┴─→ Rejected → End
```

### 3. Step Types

**Human Task Steps**:
- Approval Step (approve/reject)
- Review Step (review and comment)
- Data Entry Step (fill form)
- Document Upload Step

**System Task Steps**:
- API Call Step (invoke external service)
- Email/SMS Step (send notification)
- Calculation Step (compute values)
- Database Update Step

**Decision Steps**:
- If-Then-Else logic
- Switch/Case logic
- Rule evaluation

**Timer Steps**:
- Delay/Wait step
- Scheduled execution
- SLA tracking

---

## 🗄️ Database Schema

### 1. Workflow Templates Table
```sql
CREATE TABLE workflow_templates (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Template Details
    template_code VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- loan_approval, deposit_approval, customer_kyc
    
    -- Workflow Configuration
    workflow_type VARCHAR(50) NOT NULL, -- sequential, parallel, conditional
    trigger_event VARCHAR(100), -- manual, event_based, scheduled
    
    -- Definition (JSON)
    workflow_definition JSONB NOT NULL, -- Complete workflow graph
    default_variables JSONB, -- Default variable values
    
    -- Version Control
    version INTEGER DEFAULT 1,
    parent_template_id INTEGER,
    is_latest BOOLEAN DEFAULT true,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, archived
    is_active BOOLEAN DEFAULT true,
    
    -- SLA Configuration
    default_sla_hours INTEGER,
    escalation_enabled BOOLEAN DEFAULT false,
    escalation_rules JSONB,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_workflow_template_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_template_parent FOREIGN KEY (parent_template_id) REFERENCES workflow_templates(id)
);

CREATE INDEX idx_workflow_template_code ON workflow_templates(template_code);
CREATE INDEX idx_workflow_template_category ON workflow_templates(category);
CREATE INDEX idx_workflow_template_status ON workflow_templates(status);
```

### 2. Workflow Instances Table
```sql
CREATE TABLE workflow_instances (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    workflow_template_id INTEGER NOT NULL,
    
    -- Instance Identification
    instance_number VARCHAR(50) UNIQUE NOT NULL, -- WF-YYYYMM-XXXX
    instance_name VARCHAR(200),
    
    -- Context
    entity_type VARCHAR(50), -- loan_application, deposit_account, customer
    entity_id INTEGER, -- Related entity ID
    initiated_by INTEGER NOT NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed, cancelled
    current_step_id INTEGER,
    
    -- Variables (Runtime Data)
    workflow_variables JSONB, -- Current variable values
    context_data JSONB, -- Additional context
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    deadline TIMESTAMP, -- SLA deadline
    
    -- Priority
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high, urgent
    
    -- Escalation
    is_escalated BOOLEAN DEFAULT false,
    escalated_at TIMESTAMP,
    escalated_to INTEGER,
    
    -- Result
    result VARCHAR(50), -- approved, rejected, completed, error
    result_message TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_workflow_instance_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_instance_template FOREIGN KEY (workflow_template_id) REFERENCES workflow_templates(id),
    CONSTRAINT fk_workflow_instance_user FOREIGN KEY (initiated_by) REFERENCES users(id)
);

CREATE INDEX idx_workflow_instance_status ON workflow_instances(status);
CREATE INDEX idx_workflow_instance_entity ON workflow_instances(entity_type, entity_id);
CREATE INDEX idx_workflow_instance_deadline ON workflow_instances(deadline);
```

### 3. Workflow Steps Table
```sql
CREATE TABLE workflow_steps (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    workflow_instance_id INTEGER NOT NULL,
    
    -- Step Definition
    step_key VARCHAR(100) NOT NULL, -- Unique key from template
    step_name VARCHAR(200) NOT NULL,
    step_type VARCHAR(50) NOT NULL, -- human_task, system_task, decision, timer
    
    -- Execution
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed, skipped
    assigned_to INTEGER, -- User assigned to this step
    assigned_role VARCHAR(100), -- Or role assigned
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    deadline TIMESTAMP,
    actual_duration INTEGER, -- In minutes
    
    -- Step Data
    input_data JSONB, -- Input parameters
    output_data JSONB, -- Output/result data
    
    -- Action
    action_taken VARCHAR(100), -- approve, reject, complete, skip
    comments TEXT,
    
    -- Retry (for system tasks)
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_by INTEGER,
    
    CONSTRAINT fk_workflow_step_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_step_instance FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id),
    CONSTRAINT fk_workflow_step_assigned FOREIGN KEY (assigned_to) REFERENCES users(id),
    CONSTRAINT fk_workflow_step_completed FOREIGN KEY (completed_by) REFERENCES users(id)
);

CREATE INDEX idx_workflow_step_instance ON workflow_steps(workflow_instance_id);
CREATE INDEX idx_workflow_step_status ON workflow_steps(status);
CREATE INDEX idx_workflow_step_assigned ON workflow_steps(assigned_to);
```

### 4. Workflow History Table
```sql
CREATE TABLE workflow_history (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    workflow_instance_id INTEGER NOT NULL,
    workflow_step_id INTEGER,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL, -- started, step_completed, transitioned, completed, failed
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Actor
    actor_id INTEGER,
    actor_type VARCHAR(50), -- user, system
    
    -- Details
    from_step VARCHAR(100),
    to_step VARCHAR(100),
    action VARCHAR(100),
    
    -- Data
    event_data JSONB,
    comments TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_workflow_history_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_history_instance FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id),
    CONSTRAINT fk_workflow_history_step FOREIGN KEY (workflow_step_id) REFERENCES workflow_steps(id),
    CONSTRAINT fk_workflow_history_actor FOREIGN KEY (actor_id) REFERENCES users(id)
);

CREATE INDEX idx_workflow_history_instance ON workflow_history(workflow_instance_id);
CREATE INDEX idx_workflow_history_timestamp ON workflow_history(event_timestamp);
```

### 5. Workflow Tasks (User Task Queue)
```sql
CREATE TABLE workflow_tasks (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    workflow_instance_id INTEGER NOT NULL,
    workflow_step_id INTEGER NOT NULL,
    
    -- Task Details
    task_title VARCHAR(200) NOT NULL,
    task_description TEXT,
    task_type VARCHAR(50) NOT NULL, -- approval, review, data_entry, document_upload
    
    -- Assignment
    assigned_to INTEGER,
    assigned_role VARCHAR(100),
    assignment_type VARCHAR(50), -- direct, role_based, pool
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, claimed, in_progress, completed, cancelled
    claimed_at TIMESTAMP,
    claimed_by INTEGER,
    
    -- Priority
    priority VARCHAR(20) DEFAULT 'normal',
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Task Data
    form_data JSONB, -- Form to be filled
    attachments JSONB, -- Required attachments
    
    -- Result
    result VARCHAR(50),
    result_data JSONB,
    comments TEXT,
    
    -- Audit
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_workflow_task_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_task_instance FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id),
    CONSTRAINT fk_workflow_task_step FOREIGN KEY (workflow_step_id) REFERENCES workflow_steps(id),
    CONSTRAINT fk_workflow_task_assigned FOREIGN KEY (assigned_to) REFERENCES users(id),
    CONSTRAINT fk_workflow_task_claimed FOREIGN KEY (claimed_by) REFERENCES users(id)
);

CREATE INDEX idx_workflow_task_assigned ON workflow_tasks(assigned_to);
CREATE INDEX idx_workflow_task_status ON workflow_tasks(status);
CREATE INDEX idx_workflow_task_due_date ON workflow_tasks(due_date);
```

### 6. Workflow SLA Tracking
```sql
CREATE TABLE workflow_sla_tracking (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    workflow_instance_id INTEGER NOT NULL,
    workflow_step_id INTEGER,
    
    -- SLA Details
    sla_type VARCHAR(50), -- workflow_completion, step_completion
    sla_hours INTEGER NOT NULL,
    
    -- Timing
    start_time TIMESTAMP NOT NULL,
    deadline TIMESTAMP NOT NULL,
    completion_time TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, met, breached, cancelled
    breach_time TIMESTAMP,
    time_taken INTEGER, -- In minutes
    
    -- Escalation
    escalation_level INTEGER DEFAULT 0,
    escalated_to INTEGER,
    escalation_time TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_workflow_sla_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_sla_instance FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id),
    CONSTRAINT fk_workflow_sla_step FOREIGN KEY (workflow_step_id) REFERENCES workflow_steps(id)
);

CREATE INDEX idx_workflow_sla_status ON workflow_sla_tracking(status);
CREATE INDEX idx_workflow_sla_deadline ON workflow_sla_tracking(deadline);
```

---

## 💼 WORKFLOW DEFINITION FORMAT (JSON)

### Example: Loan Approval Workflow
```json
{
  "workflow_id": "loan_approval_v1",
  "name": "Loan Approval Workflow",
  "description": "Multi-level loan approval process",
  "version": "1.0",
  "steps": [
    {
      "key": "start",
      "name": "Start",
      "type": "start",
      "next": "credit_assessment"
    },
    {
      "key": "credit_assessment",
      "name": "Credit Assessment",
      "type": "system_task",
      "action": "calculate_credit_score",
      "sla_hours": 2,
      "next": "decision_credit_score"
    },
    {
      "key": "decision_credit_score",
      "name": "Credit Score Decision",
      "type": "decision",
      "conditions": [
        {
          "condition": "credit_score >= 700",
          "next": "credit_officer_approval"
        },
        {
          "condition": "credit_score >= 600",
          "next": "manual_review"
        },
        {
          "condition": "credit_score < 600",
          "next": "auto_reject"
        }
      ]
    },
    {
      "key": "credit_officer_approval",
      "name": "Credit Officer Approval",
      "type": "human_task",
      "task_type": "approval",
      "assigned_role": "credit_officer",
      "sla_hours": 24,
      "actions": ["approve", "reject", "return"],
      "transitions": [
        {
          "action": "approve",
          "next": "manager_approval"
        },
        {
          "action": "reject",
          "next": "rejected"
        },
        {
          "action": "return",
          "next": "credit_assessment"
        }
      ]
    },
    {
      "key": "manager_approval",
      "name": "Manager Approval",
      "type": "human_task",
      "task_type": "approval",
      "assigned_role": "manager",
      "sla_hours": 48,
      "condition": "loan_amount > 500000",
      "actions": ["approve", "reject"],
      "transitions": [
        {
          "action": "approve",
          "next": "approved"
        },
        {
          "action": "reject",
          "next": "rejected"
        }
      ]
    },
    {
      "key": "approved",
      "name": "Approved",
      "type": "end",
      "result": "approved",
      "action": "send_approval_notification"
    },
    {
      "key": "rejected",
      "name": "Rejected",
      "type": "end",
      "result": "rejected",
      "action": "send_rejection_notification"
    }
  ],
  "variables": [
    {
      "name": "loan_amount",
      "type": "decimal",
      "required": true
    },
    {
      "name": "credit_score",
      "type": "integer"
    },
    {
      "name": "approval_level",
      "type": "string"
    }
  ],
  "sla": {
    "total_hours": 72,
    "escalation_enabled": true,
    "escalation_hours": 48
  }
}
```

---

## 🚀 API ENDPOINTS STRUCTURE

### Workflow Templates (12 endpoints)
```
POST   /workflows/templates                    - Create template
GET    /workflows/templates                    - List templates
GET    /workflows/templates/{id}               - Get template
PUT    /workflows/templates/{id}               - Update template
DELETE /workflows/templates/{id}               - Delete template
POST   /workflows/templates/{id}/activate      - Activate template
POST   /workflows/templates/{id}/clone         - Clone template
GET    /workflows/templates/{id}/versions      - Get versions
POST   /workflows/templates/{id}/validate      - Validate definition
GET    /workflows/templates/categories         - Get categories
POST   /workflows/templates/{id}/test          - Test workflow
GET    /workflows/templates/{id}/statistics    - Template statistics
```

### Workflow Instances (15 endpoints)
```
POST   /workflows/instances                    - Start workflow
GET    /workflows/instances                    - List instances
GET    /workflows/instances/{id}               - Get instance
GET    /workflows/instances/{id}/steps         - Get steps
GET    /workflows/instances/{id}/history       - Get history
POST   /workflows/instances/{id}/cancel        - Cancel workflow
POST   /workflows/instances/{id}/retry         - Retry failed step
POST   /workflows/instances/{id}/escalate      - Manual escalate
GET    /workflows/instances/{id}/diagram       - Visual diagram
GET    /workflows/instances/my-workflows       - User's workflows
GET    /workflows/instances/pending            - Pending workflows
GET    /workflows/instances/overdue            - Overdue workflows
POST   /workflows/instances/{id}/reassign      - Reassign task
POST   /workflows/instances/{id}/skip-step     - Skip step (admin)
GET    /workflows/instances/{id}/sla-status    - SLA status
```

### Workflow Tasks (10 endpoints)
```
GET    /workflows/tasks                        - List user tasks
GET    /workflows/tasks/{id}                   - Get task details
POST   /workflows/tasks/{id}/claim             - Claim task
POST   /workflows/tasks/{id}/complete          - Complete task
POST   /workflows/tasks/{id}/approve           - Approve
POST   /workflows/tasks/{id}/reject            - Reject
POST   /workflows/tasks/{id}/return            - Return for rework
POST   /workflows/tasks/{id}/delegate          - Delegate task
GET    /workflows/tasks/my-tasks               - My active tasks
GET    /workflows/tasks/team-tasks             - Team tasks (pool)
```

### Workflow Analytics (5 endpoints)
```
GET    /workflows/analytics/dashboard          - Dashboard stats
GET    /workflows/analytics/sla-report         - SLA compliance
GET    /workflows/analytics/bottlenecks        - Identify bottlenecks
GET    /workflows/analytics/user-performance   - User performance
GET    /workflows/analytics/workflow-metrics   - Workflow metrics
```

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Foundation (Week 1)
- ✅ Design document
- Database models
- Workflow template service
- Basic CRUD operations
- Template validation

### Phase 2: Execution Engine (Week 2)
- Workflow instance service
- Step execution engine
- Transition logic
- State management
- Error handling

### Phase 3: Task Management (Week 3)
- Task creation and assignment
- Task queue management
- User task service
- Claim/complete logic
- Task notifications

### Phase 4: SLA & Escalation (Week 4)
- SLA tracking service
- Deadline calculation
- Escalation engine
- Automated escalation
- SLA reporting

### Phase 5: API & Integration (Week 5)
- API routers
- Pydantic schemas
- Event integration
- Notification service
- Testing & documentation

---

## ✅ Ready to Build!

Next steps:
1. Create database models
2. Build workflow template service
3. Build workflow execution service
4. Build task management service
5. Create API routers
6. Build Pydantic schemas
7. Integration & testing

Let's begin! 🚀
