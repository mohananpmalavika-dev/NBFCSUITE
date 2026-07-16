# 🚀 Approval Workflows - Quick Reference

## 5 Approval Types

### 1️⃣ Sequential (One after another)
```
Officer → Manager → Head
```
**When**: Standard hierarchical approval

### 2️⃣ Parallel (All must approve)
```
Risk + Legal + Finance (simultaneously)
```
**When**: Cross-functional review needed

### 3️⃣ Any One (First wins)
```
Any Regional Manager can approve
```
**When**: Distributed teams, faster processing

### 4️⃣ Majority (Threshold)
```
3 out of 5 committee members
```
**When**: Committee decisions, voting

### 5️⃣ Conditional (Rule-based)
```
IF Amount > 25L → Committee
ELSE → Manager
```
**When**: Different paths based on rules

---

## 🔐 Maker-Checker

**Rule**: Maker ≠ Checker (No self-approval)

```
Maker: Creates record
  ↓
Checker: Reviews & approves
  ↓
Complete: Audit trail saved
```

---

## ⚡ Quick Start

### Start Approval
```python
engine.start_approval(
    chain_config=config,
    entity_id=123,
    maker_id=user_id,
    variables={'amount': 500000}
)
```

### Approve Task
```typescript
approvalService.processApproval(instanceId, taskId, {
  action: 'approve',
  comments: 'Approved'
});
```

### Reject Task
```typescript
approvalService.processApproval(instanceId, taskId, {
  action: 'reject',
  comments: 'Insufficient docs'
});
```

---

## 📊 API Endpoints

```
POST   /api/v1/approvals/start
POST   /api/v1/approvals/instances/{id}/tasks/{task_id}/process
GET    /api/v1/approvals/my-pending
GET    /api/v1/approvals/templates
```

---

## 🎯 Use Cases

| Type | Use Case | Example |
|------|----------|---------|
| Sequential | Standard hierarchy | Loan approval chain |
| Parallel | All teams review | High-value transaction |
| Any One | Fast approval | Regional manager |
| Majority | Committee vote | Board decision |
| Conditional | Amount-based | Auto-routing by value |

---

## 🎨 Components

- **ApprovalChainConfigurator** - Build approval chains
- **ApprovalTaskInterface** - Approve/reject tasks
- **ApprovalTemplatesGallery** - Browse templates

---

## ✅ Actions Available

1. **Approve** - Accept request
2. **Reject** - Deny request (terminates)
3. **Delegate** - Assign to another user
4. **Return** - Send back to maker

---

For detailed docs: `ADVANCED_APPROVAL_WORKFLOWS_COMPLETE.md`
