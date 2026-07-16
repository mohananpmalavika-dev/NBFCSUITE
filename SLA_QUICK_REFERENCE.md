# SLA & Escalation Management - Quick Reference Guide

## 🚀 Quick Start

### 1. Create SLA Configuration (UI)
```typescript
// Navigate to SLA Configurator
<SLAConfigurator 
  entityType="loan_application"
  onSave={(config) => console.log('SLA created:', config)}
/>

// Fill in 4 steps:
// 1. Basic Settings (name, type, duration, thresholds)
// 2. Business Hours (working days, times)
// 3. Escalation Rules (triggers, actions)
// 4. Review & Save
```

### 2. Start SLA Tracking (API)
```typescript
import slaService from '@/services/slaService';

const sla = await slaService.startTracking({
  sla_config_id: 'loan_approval_sla',
  entity_id: 12345,
  workflow_instance_id: 67890
});
// Returns: { sla_instance_id, status, start_time, deadline }
```

### 3. Monitor SLA (UI)
```typescript
<SLADashboard 
  entityType="loan_application"
  autoRefresh={true}
  refreshInterval={30000}
/>
// Shows metrics cards + instances table with real-time updates
```

---

## 📋 Common Operations

### Pause SLA
```typescript
await slaService.pauseSLA(slaInstanceId, 'Customer requested documents');
```

### Resume SLA
```typescript
await slaService.resumeSLA(slaInstanceId);
```

### Complete SLA
```typescript
await slaService.completeSLA(slaInstanceId, true); // true = met, false = breached
```

### Get Status
```typescript
const status = await slaService.getSLAStatus(slaInstanceId);
console.log(`${status.sla_percentage}% complete`);
console.log(`${slaService.formatDuration(status.time_remaining_minutes)} remaining`);
```

### Process Escalations
```typescript
const result = await slaService.processEscalations(slaInstanceId);
console.log(`${result.escalations_triggered} escalations triggered`);
```

### View History
```typescript
<EscalationHistory slaInstanceId={slaInstanceId} />
// Shows timeline of all escalations
```

---

## 🔧 Configuration Examples

### Simple 24-Hour SLA
```json
{
  "name": "Simple Approval SLA",
  "entity_type": "loan_application",
  "sla": {
    "name": "24 Hour Approval",
    "sla_type": "resolution_time",
    "time_value": 24,
    "time_unit": "hours",
    "calculation_type": "calendar_hours",
    "warning_threshold": 70,
    "critical_threshold": 90
  },
  "escalation_rules": [
    {
      "name": "4 Hour Reminder",
      "trigger_after_hours": 4,
      "escalation_type": "soft",
      "send_reminder_to_assignee": true
    }
  ]
}
```

### Business Hours SLA with Multi-Level Escalation
```json
{
  "name": "Loan Approval SLA",
  "entity_type": "loan_application",
  "sla": {
    "name": "Loan Processing",
    "sla_type": "resolution_time",
    "time_value": 24,
    "time_unit": "hours",
    "calculation_type": "business_hours",
    "business_hours_config": {
      "enabled": true,
      "monday": { "start": "09:00", "end": "17:00" },
      "tuesday": { "start": "09:00", "end": "17:00" },
      "wednesday": { "start": "09:00", "end": "17:00" },
      "thursday": { "start": "09:00", "end": "17:00" },
      "friday": { "start": "09:00", "end": "17:00" },
      "saturday": null,
      "sunday": null,
      "timezone": "Asia/Kolkata"
    },
    "warning_threshold": 70,
    "critical_threshold": 90,
    "allow_pause": true,
    "pause_on_customer_action": true
  },
  "escalation_rules": [
    {
      "name": "2 Hour Reminder",
      "trigger_after_hours": 2,
      "escalation_type": "soft",
      "send_reminder_to_assignee": true,
      "notify_supervisor": false
    },
    {
      "name": "4 Hour Supervisor Notification",
      "trigger_after_hours": 4,
      "escalation_type": "notify",
      "send_reminder_to_assignee": true,
      "notify_supervisor": true
    },
    {
      "name": "6 Hour Auto-Escalation",
      "trigger_after_hours": 6,
      "escalation_type": "hard",
      "escalate_to_next_level": true
    }
  ]
}
```

---

## 📊 API Endpoints Reference

### Configuration
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workflow/sla/configurations` | Create SLA config |
| GET | `/api/workflow/sla/configurations` | List all configs |
| GET | `/api/workflow/sla/configurations/{id}` | Get config details |
| GET | `/api/workflow/sla/templates` | Get templates |

### Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workflow/sla/instances/start` | Start tracking |
| POST | `/api/workflow/sla/instances/{id}/pause` | Pause SLA |
| POST | `/api/workflow/sla/instances/{id}/resume` | Resume SLA |
| POST | `/api/workflow/sla/instances/{id}/complete` | Complete SLA |
| GET | `/api/workflow/sla/instances/{id}/status` | Get status |
| GET | `/api/workflow/sla/instances` | List instances |

### Escalation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workflow/sla/instances/{id}/process-escalations` | Trigger escalations |
| GET | `/api/workflow/sla/instances/{id}/escalation-history` | View history |

### Metrics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workflow/sla/metrics?entity_type=X&period_days=30` | Get metrics |

---

## 🎯 SLA Types

| Type | Description | Use Case |
|------|-------------|----------|
| `response_time` | Time to first response | Customer query response |
| `resolution_time` | Time to complete | Loan approval, KYC completion |
| `approval_time` | Time to approve/reject | Approval workflows |

---

## ⏱️ Time Calculation Types

| Type | Description | Behavior |
|------|-------------|----------|
| `calendar_hours` | 24/7 continuous | Includes weekends, holidays |
| `business_hours` | Working hours only | 9 AM - 5 PM, Mon-Fri |
| `working_days` | Working days only | Excludes weekends, holidays |

---

## 🚨 Escalation Types

| Type | Description | Actions |
|------|-------------|---------|
| `soft` | Reminder only | Send reminder to assignee |
| `notify` | Notify supervisor | Reminder + notify supervisor |
| `hard` | Auto-transfer | Transfer task to next level |
| `multi_level` | Multi-tier escalation | Escalate up hierarchy |

---

## 📈 Metrics & Reports

### Get Compliance Report
```typescript
const metrics = await slaService.getMetrics('loan_application', 30);

// Returns:
{
  total_slas: 156,
  met_slas: 147,
  breached_slas: 9,
  active_slas: 23,
  sla_compliance_rate: 94.2,
  average_completion_time_hours: 18.5,
  average_completion_percentage: 77.3,
  total_escalations: 45
}
```

### Dashboard Metrics Cards
- **Total SLAs**: Count of all SLAs in period
- **Compliance Rate**: (Met / Total Completed) × 100
- **Breached SLAs**: Count of breached SLAs
- **Active SLAs**: Currently in-progress SLAs
- **Avg Completion Time**: Average hours to complete
- **Total Escalations**: Count of all escalations

---

## 🎨 UI Component Props

### SLAConfigurator
```typescript
interface SLAConfiguratorProps {
  entityType: string;                          // Required
  onSave?: (config: SLAEscalationConfig) => void;
  existingConfig?: SLAEscalationConfig;        // For editing
}
```

### SLADashboard
```typescript
interface SLADashboardProps {
  entityType?: string;                         // Filter by entity type
  workflowInstanceId?: number;                 // Filter by workflow
  autoRefresh?: boolean;                       // Default: true
  refreshInterval?: number;                    // Default: 30000 (30s)
}
```

### EscalationHistory
```typescript
interface EscalationHistoryProps {
  slaInstanceId: number;                       // Required
}
```

---

## 🔄 Integration Patterns

### Pattern 1: Start SLA on Workflow Start
```python
# In workflow engine
from backend.services.workflow.sla_engine import SLAEngine

# When workflow starts
sla_engine = SLAEngine(db, tenant_id)
sla_instance = sla_engine.start_sla(
    config=sla_config,
    entity_id=loan_id,
    workflow_instance_id=workflow.id
)
```

### Pattern 2: Auto-Pause on Customer Action
```python
# When customer submits documents
if sla_config.pause_on_customer_action:
    sla_engine.pause_sla(
        sla_instance, 
        reason='Customer submitted additional documents'
    )
```

### Pattern 3: Complete SLA on Workflow Completion
```python
# When workflow completes
completion_time = workflow.completed_at
deadline = sla_instance.deadline

success = completion_time <= deadline
sla_engine.complete_sla(sla_instance, success)
```

### Pattern 4: Scheduled Escalation Processing
```python
# Background job (runs every 5 minutes)
@scheduler.task('*/5 * * * *')  # Every 5 minutes
def process_escalations():
    active_slas = get_active_slas()
    
    for sla in active_slas:
        # Update status
        sla_engine.update_sla_status(sla)
        
        # Check escalations
        rules = get_escalation_rules(sla.sla_config_id)
        escalations = sla_engine.process_escalations(sla, rules)
        
        # Send notifications
        for escalation in escalations:
            notify_users(escalation)
```

---

## 🛠️ Troubleshooting

### SLA Not Starting
**Issue**: SLA doesn't start when workflow begins
**Solution**:
1. Check SLA configuration exists
2. Verify entity_type matches
3. Check holiday calendar if using business hours
4. Verify database WorkflowSLA model is migrated

### Business Hours Calculation Wrong
**Issue**: Deadline calculation doesn't match expected
**Solution**:
1. Check business_hours_config is enabled
2. Verify working days are configured
3. Check timezone setting
4. Ensure holiday calendar is loaded

### Escalations Not Triggering
**Issue**: Escalation rules not firing
**Solution**:
1. Verify escalation rules are active (`is_active: true`)
2. Check trigger conditions (hours/percentage)
3. Ensure background job is running
4. Check escalation hasn't already been triggered
5. Verify max_escalations not reached

### SLA Percentage > 100%
**Issue**: SLA shows over 100% completion
**Solution**: This is normal for breached SLAs. Indicates SLA exceeded by X%.

---

## 💡 Best Practices

### 1. SLA Configuration
- Use business hours for internal processes
- Set realistic thresholds (70% warning, 90% critical)
- Enable pause for customer-dependent actions
- Configure multiple escalation levels

### 2. Escalation Rules
- Start with soft escalations (reminders)
- Gradually increase severity (notify → hard)
- Use reasonable intervals (2h → 4h → 6h)
- Set max escalation limits

### 3. Monitoring
- Enable auto-refresh on dashboard
- Monitor compliance rate regularly
- Review breach reasons
- Track escalation patterns

### 4. Performance
- Run scheduled jobs frequently (every 5 min)
- Index database fields (status, entity_type, deadline)
- Archive completed SLAs after 90 days
- Cache holiday calendars

---

## 📞 Support

For issues or questions:
1. Check this quick reference
2. Review `SLA_ESCALATION_MANAGEMENT_COMPLETE.md`
3. Check API documentation at `/docs`
4. Review database schema in `workflow_models.py`

---

**Last Updated**: January 2025
**Version**: 1.0
**Status**: ✅ Production Ready
