# Performance Management - Quick Reference Guide

## 🎯 Quick Commands

### Run Database Migration
```bash
psql -U postgres -d nbfc_db -f database/migrations/add_performance_management_tables.sql
```

### Configure First Cycle
```bash
python scripts/configure_first_appraisal_cycle.py
```

### Seed Sample Data
```bash
python scripts/seed_performance_data.py
```

### Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend/apps/admin-portal
npm run dev
```

---

## 📍 Key URLs

- **API Documentation**: http://localhost:8000/docs
- **Frontend App**: http://localhost:3000
- **Performance Dashboard**: http://localhost:3000/performance
- **API Base**: http://localhost:8000/api/v1/hrms/performance

---

## 🔗 API Endpoints Quick Reference

### Appraisal Cycles
```
POST   /cycles                 Create cycle
GET    /cycles                 List cycles
GET    /cycles/{id}            Get cycle details
PATCH  /cycles/{id}            Update cycle
DELETE /cycles/{id}            Delete cycle
```

### Goals
```
POST   /goals                              Create goal
GET    /employees/{id}/goals               List employee goals
PATCH  /goals/{id}                         Update goal
POST   /employees/{id}/goals/submit        Submit goals
POST   /goals/{id}/approve                 Approve goal
POST   /goals/{id}/reject                  Reject goal
```

### Appraisals
```
POST   /appraisals                         Create appraisal
GET    /appraisals                         List appraisals
GET    /appraisals/{id}                    Get appraisal
POST   /appraisals/{id}/self-assessment    Submit self-assessment
POST   /appraisals/{id}/manager-review     Submit manager review
POST   /appraisals/{id}/hr-review          Submit HR review
```

### Feedback
```
POST   /feedback/requests                  Create request
GET    /feedback/requests/reviewer/{id}    List reviewer requests
POST   /feedback/requests/{id}/respond     Submit feedback
GET    /feedback/employee/{id}             Get employee feedback
```

### Increments
```
POST   /increments                         Create increment
GET    /employees/{id}/increments          List increments
POST   /increments/{id}/approve            Approve increment
POST   /increments/{id}/process            Process increment
```

### IDPs
```
POST   /idp                                Create IDP
GET    /idp/{id}                          Get IDP
GET    /employees/{id}/idp                 List employee IDPs
PATCH  /idp/{id}                          Update IDP
POST   /idp/{id}/submit                    Submit IDP
POST   /idp/{id}/approve                   Approve IDP
```

---

## 📊 Database Tables

```
hrms_appraisal_cycles             - Appraisal cycles
hrms_performance_goals            - Employee goals (KRA/KPI)
hrms_employee_appraisals          - Appraisal records
hrms_feedback_requests            - 360 feedback requests
hrms_feedback_responses           - Feedback submissions
hrms_performance_increments       - Salary increments
hrms_individual_development_plans - Career development plans
hrms_development_activities       - Learning activities
```

---

## 🔄 Workflow Phases

1. **Goal Setting** → Employee creates goals → Manager approves
2. **Execution** → Employee tracks progress throughout year
3. **Self-Assessment** → Employee rates self and documents achievements
4. **Manager Review** → Manager rates and provides feedback
5. **360 Feedback** (Optional) → Peers/subordinates provide input
6. **HR Review** → HR normalizes ratings and finalizes
7. **Increment** → Create and approve increments
8. **IDP** → Create development plans for next year

---

## 🎨 Status Values

### Appraisal Cycle Status
- `draft` - Being configured
- `active` - Currently active
- `goal_setting` - Goal setting phase
- `self_assessment` - Self-assessment phase
- `manager_review` - Manager review phase
- `hr_review` - HR review phase
- `completed` - Completed
- `closed` - Archived

### Goal Status
- `draft` - Being created
- `submitted` - Submitted for approval
- `approved` - Approved by manager
- `rejected` - Rejected by manager
- `in_progress` - Being executed
- `completed` - Achieved
- `cancelled` - Cancelled

### Appraisal Status
- `not_started` - Not begun
- `goal_setting_pending` - Needs goals
- `goals_approved` - Goals approved
- `self_assessment_pending` - Awaiting self-assessment
- `self_assessment_submitted` - Self-assessment done
- `manager_review_pending` - Awaiting manager
- `manager_review_submitted` - Manager review done
- `hr_review_pending` - Awaiting HR
- `completed` - Finalized

### Rating Scale
- `outstanding` (5.0) - Outstanding
- `exceeds_expectations` (4.0) - Exceeds Expectations
- `meets_expectations` (3.0) - Meets Expectations
- `needs_improvement` (2.0) - Needs Improvement
- `unsatisfactory` (1.0) - Unsatisfactory

---

## 📝 Sample API Requests

### Create Appraisal Cycle
```json
POST /api/v1/hrms/performance/cycles
{
  "cycle_code": "APR-2024-25",
  "cycle_name": "Annual Appraisal 2024-25",
  "fiscal_year": "2024-25",
  "start_date": "2024-04-01",
  "end_date": "2025-03-31",
  "goal_setting_start": "2024-04-01",
  "goal_setting_end": "2024-04-30",
  "enable_360_feedback": true
}
```

### Create Goal
```json
POST /api/v1/hrms/performance/goals
{
  "goal_code": "G-2024-001",
  "goal_title": "Complete Project Alpha",
  "goal_type": "project",
  "goal_priority": "high",
  "employee_id": "uuid",
  "appraisal_cycle_id": "uuid",
  "target_value": "100%",
  "weightage": 30,
  "start_date": "2024-04-01",
  "target_date": "2024-12-31"
}
```

### Submit Self-Assessment
```json
POST /api/v1/hrms/performance/appraisals/{id}/self-assessment
{
  "self_rating": "exceeds_expectations",
  "self_rating_numeric": 4.0,
  "key_achievements": "Delivered all projects on time...",
  "areas_of_improvement": "Need to improve presentation skills..."
}
```

---

## 🛠️ Common Tasks

### Check If Cycle Exists
```bash
curl http://localhost:8000/api/v1/hrms/performance/cycles | jq
```

### Get Active Cycle
```bash
curl "http://localhost:8000/api/v1/hrms/performance/cycles?status=active" | jq
```

### List Employee Goals
```bash
curl http://localhost:8000/api/v1/hrms/performance/employees/{id}/goals | jq
```

### Check Appraisal Status
```bash
curl http://localhost:8000/api/v1/hrms/performance/appraisals/{id} | jq .status
```

---

## 🐛 Troubleshooting

### Issue: Tables not found
```bash
# Verify tables exist
psql -U postgres -d nbfc_db -c "\dt hrms_*"

# Re-run migration if needed
psql -U postgres -d nbfc_db -f database/migrations/add_performance_management_tables.sql
```

### Issue: API returns 404
```bash
# Check if router is registered
grep "performance_router" backend/main.py

# Restart backend server
pkill -f "uvicorn main:app"
uvicorn main:app --reload
```

### Issue: Configuration script fails
```bash
# Check if tenant exists
psql -U postgres -d nbfc_db -c "SELECT * FROM tenants WHERE id='default'"

# Create tenant if missing
python scripts/init_tenant.py  # If this script exists
```

### Issue: Frontend can't connect
```bash
# Check .env file
cat frontend/apps/admin-portal/.env

# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings
```

---

## 📚 File Locations

### Backend
```
backend/shared/database/hrms_models.py                   # Models
backend/services/hrms/schemas/performance_schemas.py     # Schemas
backend/services/hrms/services/performance_service.py    # Services
backend/services/hrms/routes/performance_routes.py       # Routes
backend/main.py                                          # Router registration
```

### Frontend
```
frontend/apps/admin-portal/src/types/performance.types.ts    # Types
frontend/apps/admin-portal/src/services/performance.service.ts # API
frontend/apps/admin-portal/src/pages/performance/*           # Components
frontend/apps/admin-portal/src/components/performance/*      # Reusable
```

### Database
```
database/migrations/add_performance_management_tables.sql    # Migration
```

### Scripts
```
scripts/configure_first_appraisal_cycle.py                   # Setup
scripts/seed_performance_data.py                             # Sample data
```

### Documentation
```
docs/HRMS_PERFORMANCE_MANAGEMENT_COMPLETE.md                 # Full docs
docs/PERFORMANCE_MANAGEMENT_UI_SPECIFICATION.md              # UI specs
docs/PERFORMANCE_MANAGEMENT_SETUP_GUIDE.md                   # Setup guide
docs/PERFORMANCE_MANAGEMENT_QUICK_REFERENCE.md               # This file
```

---

## ✅ Verification Checklist

**Database**
- [ ] Tables created (8 tables)
- [ ] Enums created (11 enums)
- [ ] Indexes created
- [ ] Triggers working

**Backend**
- [ ] Models loaded
- [ ] Routes registered
- [ ] API docs accessible at /docs
- [ ] Can create cycle via API
- [ ] Can create goals via API

**Frontend**
- [ ] App runs without errors
- [ ] Can navigate to /performance
- [ ] Dashboard loads
- [ ] Can view cycles list
- [ ] Can create goals

**Configuration**
- [ ] First cycle created
- [ ] Sample data seeded (if testing)
- [ ] Employees can access system
- [ ] Managers can approve goals

---

## 🎯 Success Metrics

- **Cycle Setup Time**: < 5 minutes
- **Goal Creation**: < 2 minutes per goal
- **Self-Assessment**: < 15 minutes
- **Manager Review**: < 20 minutes
- **System Response**: < 2 seconds per API call
- **User Satisfaction**: > 4/5 rating

---

## 📞 Quick Support

**For Setup Issues:**
1. Check setup guide: `docs/PERFORMANCE_MANAGEMENT_SETUP_GUIDE.md`
2. Verify all prerequisites
3. Review troubleshooting section

**For API Issues:**
1. Check Swagger docs: http://localhost:8000/docs
2. Verify authentication token
3. Check request/response format

**For UI Issues:**
1. Check browser console for errors
2. Verify API_URL in .env
3. Clear browser cache

---

**Last Updated**: 2024
**Version**: 1.0.0
**Status**: Production Ready ✅
