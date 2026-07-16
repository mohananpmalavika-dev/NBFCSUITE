# 🚀 Workflow Engine - Quick Start Guide

## 5-Minute Setup

### 1. Start the Backend Service
```bash
# The workflow engine is included in the operations service
python backend/main_operations.py
```

### 2. Access the Designer
```
Frontend URL: http://localhost:3000/workflow/designer
Dashboard URL: http://localhost:3000/workflow/dashboard
Templates URL: http://localhost:3000/workflow/templates
```

---

## Quick Examples

### Example 1: Use a Pre-Built Template

**Via UI**:
1. Go to Template Library
2. Click "Use Template" on "Loan Approval Workflow"
3. Customize if needed
4. Save and activate

**Via API**:
```bash
curl -X POST http://localhost:8000/api/v1/bpmn/templates/library/loan_approval_workflow/instantiate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 2: Start a Loan Approval Workflow

**Python**:
```python
from backend.services.workflow.integrations import on_loan_application_created

result = on_loan_application_created(
    db=db,
    tenant_id=1,
    user_id=1,
    loan_application_id=123,
    loan_amount=750000,
    customer_id=456
)
print(result)  # {'success': True, 'instance_id': 1, 'instance_number': 'WF-202607-0001'}
```

**REST API**:
```bash
curl -X POST http://localhost:8000/api/v1/workflow/integrations/loan/start-approval \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "loan_application_id": 123,
    "loan_amount": 750000,
    "customer_id": 456,
    "priority": "high"
  }'
```

### Example 3: Complete a User Task

**TypeScript/React**:
```typescript
import workflowService from './services/workflowService';

// User approves loan
await workflowService.completeTask(taskId, {
  result: 'approved',
  result_data: {
    approved: true,
    comments: 'Loan approved with conditions'
  }
});
```

**REST API**:
```bash
curl -X POST http://localhost:8000/api/v1/workflow/tasks/1/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "result": "approved",
    "result_data": {"approved": true},
    "comments": "Loan approved"
  }'
```

---

## Common Workflows

### 1. Loan Approval
```
Start → Credit Check → Risk Assessment → Gateway
  ├─ Low Amount → Officer Approval → End
  └─ High Amount → Manager → Committee → End
```

### 2. KYC Verification
```
Start → Document Collection → Parallel (Identity + Address + Photo) → Compliance → End
```

### 3. Deposit Approval
```
Start → Operations Review → Manager Approval → Send Email → End
```

---

## Key Endpoints

### Workflow Designer
- `POST /api/v1/bpmn/workflows` - Create workflow
- `GET /api/v1/bpmn/workflows/{id}` - Get workflow
- `PUT /api/v1/bpmn/workflows/{id}` - Update workflow
- `POST /api/v1/bpmn/workflows/{id}/start` - Start execution
- `POST /api/v1/bpmn/workflows/{id}/validate` - Validate

### Templates
- `GET /api/v1/bpmn/templates/library` - List templates
- `POST /api/v1/bpmn/templates/library/{id}/instantiate` - Use template

### Task Management
- `GET /api/v1/workflow/tasks/my-tasks` - My tasks
- `POST /api/v1/workflow/tasks/{id}/complete` - Complete task
- `POST /api/v1/workflow/tasks/{id}/claim` - Claim task

### Integrations
- `POST /api/v1/workflow/integrations/loan/start-approval` - Start loan workflow
- `POST /api/v1/workflow/integrations/deposit/start-approval` - Start deposit workflow
- `POST /api/v1/workflow/integrations/customer/start-kyc` - Start KYC workflow
- `GET /api/v1/workflow/integrations/entity/{type}/{id}` - Get entity workflows

---

## Node Types Quick Reference

### Events
- **Start (Green Circle)**: Entry point
- **End (Red Circle)**: Exit point

### Tasks
- **User Task (Blue)**: Manual task requiring user action
- **Service Task (Purple)**: Automated API call
- **Script Task (Orange)**: Execute Python/JavaScript code
- **Send Task (Cyan)**: Send email/SMS/notification

### Gateways
- **Exclusive (Yellow Diamond)**: XOR - Take ONE path
- **Parallel (Yellow Diamond)**: AND - Take ALL paths
- **Inclusive (Yellow Diamond)**: OR - Take MULTIPLE paths

---

## Configuration Examples

### User Task Configuration
```javascript
{
  assignment_type: 'role',
  assigned_role: 'loan_officer',
  priority: 'high',
  due_date: '+2d',
  form_fields: [
    {name: 'approved', type: 'boolean', label: 'Approve?'},
    {name: 'comments', type: 'text', label: 'Comments'}
  ]
}
```

### Service Task Configuration
```javascript
{
  implementation: 'api',
  api_endpoint: '/api/risk/calculate-score',
  api_method: 'POST',
  result_variable: 'risk_score',
  retry_enabled: true,
  max_retries: 3
}
```

### Gateway Condition (Simple)
```javascript
{
  type: 'simple',
  variable: 'loan_amount',
  operator: '>=',
  value: 500000
}
```

### Gateway Condition (Script)
```javascript
{
  type: 'script',
  script: 'loan_amount > 500000 and risk_score < 5',
  language: 'python'
}
```

---

## Troubleshooting

### Issue: Workflow not starting
**Check**:
1. Template is activated (`is_active: true`)
2. Workflow definition is valid (use validate endpoint)
3. Required variables are provided
4. User has permissions

### Issue: Task not appearing
**Check**:
1. Task assignment (user ID or role)
2. Task status (`pending` or `claimed`)
3. User's role matches assigned role
4. Workflow instance is `in_progress`

### Issue: Gateway not routing correctly
**Check**:
1. Condition syntax is correct
2. Variables exist in workflow context
3. Condition type matches (simple vs script)
4. Gateway type is correct (exclusive vs parallel)

---

## Best Practices

### 1. Workflow Design
- ✅ Always start with a start event
- ✅ Always end with an end event
- ✅ Use descriptive node names
- ✅ Add descriptions to complex nodes
- ✅ Test with validation before activating

### 2. Task Assignment
- ✅ Use role-based assignment for flexibility
- ✅ Set appropriate priorities
- ✅ Define realistic due dates
- ✅ Provide clear task descriptions

### 3. Service Tasks
- ✅ Enable retry for critical operations
- ✅ Store results in variables
- ✅ Handle errors gracefully
- ✅ Set reasonable timeouts

### 4. Gateways
- ✅ Use exclusive for single-path decisions
- ✅ Use parallel for concurrent execution
- ✅ Test all condition branches
- ✅ Provide default flow for exclusive gateways

---

## Support & Documentation

- **Full Documentation**: `WORKFLOW_ENGINE_COMPLETE.md`
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Frontend Components**: `frontend/src/components/workflow/`
- **Backend Services**: `backend/services/workflow/`

---

## Quick Commands

```bash
# Validate workflow
curl -X POST http://localhost:8000/api/v1/bpmn/workflows/{id}/validate

# Get my tasks
curl -X GET http://localhost:8000/api/v1/workflow/tasks/my-tasks

# Get workflow status
curl -X GET http://localhost:8000/api/v1/workflow/instances/{id}

# Cancel workflow
curl -X POST http://localhost:8000/api/v1/workflow/instances/{id}/cancel

# Get entity workflows
curl -X GET http://localhost:8000/api/v1/workflow/integrations/entity/loan_application/123
```

---

**Ready to build workflows! 🚀**

For detailed information, see `WORKFLOW_ENGINE_COMPLETE.md`
