# HRMS Service

Core employee master service for Phase 2.

## Features

- Employee profile creation and updates
- IAM `user_id` to employee mapping
- Branch assignment for hierarchy-aware operations
- Filters by branch, department, and status
- Health and readiness endpoints

## Run

```bash
uvicorn app.main:app --reload --port 8012
```
