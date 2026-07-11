# Performance Management System - Setup & Deployment Guide

## 🚀 Quick Start Guide

This guide will help you set up and configure the Performance Management system from scratch.

---

## Prerequisites

Before you begin, ensure you have:

- ✅ PostgreSQL database running
- ✅ Backend FastAPI server set up
- ✅ Frontend React application configured
- ✅ Python 3.9+ installed
- ✅ Node.js 16+ installed
- ✅ Database migrations ready

---

## Step 1: Database Setup

### 1.1 Run Performance Management Migration

```bash
# Navigate to project root
cd c:\NBFCSUITE

# Run the migration script
psql -U postgres -d nbfc_db -f database/migrations/add_performance_management_tables.sql
```

**Expected Output:**
```
CREATE TYPE
CREATE TYPE
...
CREATE TABLE
CREATE TABLE
✅ Migration completed successfully
```

### 1.2 Verify Tables Created

```bash
psql -U postgres -d nbfc_db -c "\dt hrms_*"
```

**You should see:**
- hrms_appraisal_cycles
- hrms_performance_goals
- hrms_employee_appraisals
- hrms_feedback_requests
- hrms_feedback_responses
- hrms_performance_increments
- hrms_individual_development_plans
- hrms_development_activities

---

## Step 2: Backend Configuration

### 2.1 Verify Routes Registered

Check `backend/main.py` contains:

```python
from backend.services.hrms.routes.performance_routes import router as performance_router
app.include_router(performance_router, prefix="/api/v1/hrms/performance", tags=["HRMS - Performance Management"])
```

### 2.2 Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2.3 Verify API Documentation

Open browser: `http://localhost:8000/docs`

Look for **"HRMS - Performance Management"** section with endpoints:
- POST /api/v1/hrms/performance/cycles
- GET /api/v1/hrms/performance/cycles
- POST /api/v1/hrms/performance/goals
- etc.

---

## Step 3: Configure First Appraisal Cycle

### 3.1 Run Configuration Script

```bash
# From project root
python scripts/configure_first_appraisal_cycle.py
```

**Expected Output:**
```
============================================================
PERFORMANCE MANAGEMENT - FIRST CYCLE CONFIGURATION
============================================================
✓ Using tenant: Default Organization

📅 Fiscal Year: 2024-25
   Start: 2024-04-01
   End: 2025-03-31

✅ Appraisal cycle created successfully!
   Cycle Code: APR-2024-25
   Cycle Name: Annual Performance Appraisal 2024-25
   Status: active

📋 Phase Timeline:
   Goal Setting:     2024-04-01 to 2024-04-30
   Self Assessment:  2025-01-01 to 2025-01-31
   Manager Review:   2025-02-01 to 2025-02-28
   HR Review:        2025-03-01 to 2025-03-15

⚙️  Configuration:
   Goal Setting: Enabled
   Self Assessment: Enabled
   360 Feedback: Enabled

👥 Employee Statistics:
   Total Employees: X
   Appraisals to be created: X

🎉 Configuration Complete!
```

### 3.2 Verify Cycle Created

Via API:
```bash
curl http://localhost:8000/api/v1/hrms/performance/cycles
```

Or via Swagger UI:
`http://localhost:8000/docs` → GET /cycles → Try it out → Execute

---

## Step 4: Seed Sample Data (Optional for Testing)

### 4.1 Run Seeding Script

```bash
python scripts/seed_performance_data.py
```

**Expected Output:**
```
============================================================
PERFORMANCE MANAGEMENT - SAMPLE DATA SEEDING
============================================================
✓ Using cycle: Annual Performance Appraisal 2024-25
✓ Found 5 employees

👤 Processing Employee: EMP001
   ✓ Created 4 goals
   ✓ Created appraisal record

...

✅ SAMPLE DATA CREATED SUCCESSFULLY!

📊 Summary:
   Employees Processed: 5
   Goals Created: 20
   Appraisals Created: 5
```

---

## Step 5: Frontend Setup

### 5.1 Install Dependencies

```bash
cd frontend/apps/admin-portal
npm install
```

### 5.2 Configure API URL

Create/update `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_BASE_URL=http://localhost:8000
```

### 5.3 Start Frontend Development Server

```bash
npm run dev
```

Frontend should be available at: `http://localhost:3000`

---

## Step 6: Access the Application

### 6.1 Login to Application

Navigate to: `http://localhost:3000`

Login with your credentials.

### 6.2 Navigate to Performance Management

Main Menu → HRMS → Performance Management

Or directly: `http://localhost:3000/performance`

### 6.3 Verify Dashboard Loads

You should see:
- Performance Dashboard
- Current cycle information
- Quick stats
- Navigation cards

---

## Step 7: Test Complete Workflow

### 7.1 As Employee - Set Goals

1. Navigate to **Performance → My Goals**
2. Click **"+ Add Goal"**
3. Fill in goal details:
   - Goal Title: "Complete Project Alpha"
   - Goal Type: Project
   - Priority: High
   - Target Value: 100%
   - Weightage: 30%
4. Click **"Save Goal"**
5. Repeat to create 3-4 goals (total weightage = 100%)
6. Click **"Submit for Approval"**

### 7.2 As Manager - Approve Goals

1. Navigate to **Performance → Goal Approvals**
2. View submitted goals
3. Click **"Approve"** for each goal
4. Add optional comments
5. Confirm approval

### 7.3 As Employee - Update Progress

1. Navigate to **Performance → My Goals**
2. Update **Achieved Value** and **Progress %** for each goal
3. Add comments on achievements/challenges
4. Progress is saved automatically

### 7.4 As Employee - Submit Self-Assessment

1. Navigate to **Performance → My Appraisals**
2. Click on current appraisal
3. Click **"Complete Self-Assessment"**
4. Select overall rating
5. Describe key achievements
6. Identify areas for improvement
7. Click **"Submit Self-Assessment"**

### 7.5 As Manager - Submit Review

1. Navigate to **Performance → Team Appraisals**
2. Select employee appraisal
3. Click **"Submit Manager Review"**
4. Provide manager rating
5. Document strengths and development areas
6. Recommend increment % and promotion (if any)
7. Click **"Submit Review"**

### 7.6 As HR - Finalize Appraisal

1. Navigate to **Performance → All Appraisals**
2. Filter by status: "Manager Review Submitted"
3. Review ratings and feedback
4. Apply normalization if needed
5. Set final rating
6. Add HR comments
7. Click **"Complete Appraisal"**

---

## Step 8: Configuration Options

### 8.1 Customize Cycle Timeline

Edit cycle via API or UI:

```json
PATCH /api/v1/hrms/performance/cycles/{id}
{
  "goal_setting_end": "2024-05-15",
  "self_assessment_start": "2024-12-01"
}
```

### 8.2 Enable/Disable Features

```json
PATCH /api/v1/hrms/performance/cycles/{id}
{
  "enable_360_feedback": false,
  "enable_self_assessment": true
}
```

### 8.3 Change Cycle Status

```json
PATCH /api/v1/hrms/performance/cycles/{id}
{
  "status": "self_assessment"
}
```

---

## Step 9: User Communication

### 9.1 Announce Cycle Launch

**Email Template:**

```
Subject: Performance Appraisal Cycle 2024-25 - Action Required

Dear Team,

We are pleased to announce the launch of the Performance Appraisal Cycle 2024-25.

Key Dates:
- Goal Setting: April 1 - April 30, 2024
- Self-Assessment: January 1 - January 31, 2025
- Manager Review: February 1 - February 28, 2025

What You Need to Do:
1. Set your performance goals by April 30
2. Ensure goals align with team/company objectives
3. Total goal weightage should equal 100%
4. Submit goals for manager approval

Access the Performance Management system:
[Link to Performance Dashboard]

For questions, contact HR.

Best regards,
HR Team
```

### 9.2 Send Reminders

**Goal Submission Reminder:**
```
Subject: Reminder: Goal Setting Deadline - April 30

Dear [Employee Name],

This is a reminder that the goal setting deadline is April 30, 2024.

Current Status:
- Goals Created: X
- Goals Submitted: [Yes/No]
- Total Weightage: X%

Action Needed:
- Complete remaining goals
- Ensure total weightage = 100%
- Submit for manager approval

[Link to My Goals]

HR Team
```

---

## Step 10: Monitoring & Reports

### 10.1 Track Progress

**Via Dashboard:**
- Total employees in cycle
- Completed appraisals
- Pending actions by phase

**Via API:**
```bash
# Get cycle statistics
GET /api/v1/hrms/performance/cycles/{id}

# Get appraisals by status
GET /api/v1/hrms/performance/appraisals?status=pending

# Get goals by employee
GET /api/v1/hrms/performance/employees/{id}/goals
```

### 10.2 Generate Reports

Reports to generate:
- Goal Achievement Report
- Rating Distribution Report
- Increment Budget Report
- Appraisal Completion Report

---

## Troubleshooting

### Issue: Tables Not Created

**Solution:**
```bash
# Check if migration ran
psql -U postgres -d nbfc_db -c "\dt hrms_*"

# If empty, re-run migration
psql -U postgres -d nbfc_db -f database/migrations/add_performance_management_tables.sql
```

### Issue: API 404 Errors

**Solution:**
```bash
# Verify router registered in main.py
grep "performance_router" backend/main.py

# Restart server
uvicorn main:app --reload
```

### Issue: Frontend API Calls Failing

**Solution:**
```bash
# Check .env file
cat frontend/apps/admin-portal/.env

# Verify API URL is correct
REACT_APP_API_URL=http://localhost:8000/api/v1

# Check CORS settings in backend
```

### Issue: Configuration Script Fails

**Solution:**
```bash
# Check database connection
psql -U postgres -d nbfc_db -c "SELECT 1"

# Verify tenant exists
psql -U postgres -d nbfc_db -c "SELECT * FROM tenants WHERE id='default'"

# Check Python path
python --version
```

---

## Next Steps

1. ✅ **Customize for Your Organization**
   - Adjust phase timelines
   - Modify rating scales
   - Add custom competencies

2. ✅ **Train Users**
   - Conduct training sessions
   - Provide user guides
   - Set up help desk support

3. ✅ **Monitor Adoption**
   - Track completion rates
   - Gather feedback
   - Make improvements

4. ✅ **Scale Up**
   - Add more employees
   - Create multiple cycles
   - Implement advanced features

---

## Support & Resources

- **Documentation**: `/docs/HRMS_PERFORMANCE_MANAGEMENT_COMPLETE.md`
- **UI Specs**: `/docs/PERFORMANCE_MANAGEMENT_UI_SPECIFICATION.md`
- **API Docs**: `http://localhost:8000/docs`
- **Scripts**: `/scripts/` directory

---

## Success Checklist

- [ ] Database tables created
- [ ] First appraisal cycle configured
- [ ] Sample data seeded (for testing)
- [ ] Backend API accessible
- [ ] Frontend application running
- [ ] Can login and access dashboard
- [ ] Can create and submit goals
- [ ] Can approve goals as manager
- [ ] Can complete self-assessment
- [ ] Can submit manager review
- [ ] Can finalize appraisals as HR

---

**🎉 Congratulations! Your Performance Management system is ready to use!**

For questions or issues, refer to the troubleshooting section or contact the development team.
