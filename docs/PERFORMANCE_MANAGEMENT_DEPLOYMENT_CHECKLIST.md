# Performance Management System - Deployment Checklist

## Pre-Deployment Verification

### ✅ Backend Components
- [x] Database models added to `backend/shared/database/hrms_models.py`
  - AppraisalCycle, PerformanceGoal, EmployeeAppraisal
  - FeedbackRequest, FeedbackResponse
  - PerformanceIncrement, IndividualDevelopmentPlan, DevelopmentActivity
  - All 11 enums defined

- [x] Migration script created at `database/migrations/add_performance_management_tables.sql`
  - All 8 tables with proper constraints
  - Indexes for performance optimization
  - Triggers for audit trails

- [x] Pydantic schemas in `backend/services/hrms/schemas/performance_schemas.py`
  - 30+ schemas for request/response validation
  - Create, Update, Response schemas for all entities
  - Filter and pagination schemas

- [x] Business logic service in `backend/services/hrms/services/performance_service.py`
  - 40+ methods covering all operations
  - Proper error handling and validation
  - Authorization checks

- [x] API routes in `backend/services/hrms/routes/performance_routes.py`
  - 40+ endpoints with proper HTTP methods
  - Authentication and authorization
  - Pagination support

- [x] Routes registered in `backend/main.py`
  - Router imported and included
  - Prefix: `/api/v1/hrms/performance`
  - Tag: "HRMS - Performance Management"

### ✅ Frontend Components
- [x] TypeScript types in `frontend/apps/admin-portal/src/types/performance.types.ts`
  - 50+ interfaces matching backend models
  - All enums and utility types
  - Constants for UI display

- [x] API services in `frontend/apps/admin-portal/src/services/performance.service.ts`
  - Complete service layer with typed axios clients
  - Services for cycles, goals, appraisals, feedback, increments, IDP
  - Error handling and response typing

- [x] Reusable components:
  - `components/performance/RatingScaleSelector.tsx`
  - `components/performance/GoalProgressTracker.tsx`
  - `components/performance/StatusBadge.tsx`

- [x] Main pages implemented:
  - `pages/performance/dashboard/PerformanceDashboard.tsx`
  - `pages/performance/cycles/AppraisalCycleList.tsx`
  - `pages/performance/goals/GoalsList.tsx`
  - `pages/performance/appraisals/SelfAssessmentForm.tsx`
  - `pages/performance/appraisals/ManagerReviewForm.tsx`

- [x] Routing configuration:
  - `pages/performance/PerformanceManagementRoutes.tsx`

### ✅ Configuration & Scripts
- [x] Configuration script: `scripts/configure_first_appraisal_cycle.py`
- [x] Sample data script: `scripts/seed_performance_data.py`

### ✅ Documentation
- [x] UI Specifications: `docs/PERFORMANCE_MANAGEMENT_UI_SPECIFICATION.md`
- [x] Setup Guide: `docs/PERFORMANCE_MANAGEMENT_SETUP_GUIDE.md`
- [x] Quick Reference: `docs/PERFORMANCE_MANAGEMENT_QUICK_REFERENCE.md`
- [x] Complete Documentation: `docs/HRMS_PERFORMANCE_MANAGEMENT_COMPLETE.md`
- [x] Implementation Summary: `docs/PERFORMANCE_MANAGEMENT_IMPLEMENTATION_SUMMARY.md`
- [x] Final Summary: `docs/PERFORMANCE_MANAGEMENT_FINAL_SUMMARY.md`

---

## Deployment Steps

### Step 1: Database Setup (15 minutes)

```bash
# 1. Backup existing database
pg_dump -U postgres -d nbfc_suite > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migration script
psql -U postgres -d nbfc_suite -f database/migrations/add_performance_management_tables.sql

# 3. Verify tables created
psql -U postgres -d nbfc_suite -c "\dt performance_*"
```

**Expected Output:**
```
performance_appraisal_cycles
performance_goals
performance_employee_appraisals
performance_feedback_requests
performance_feedback_responses
performance_increments
performance_idps
performance_development_activities
```

### Step 2: Backend Deployment (10 minutes)

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies (if any new ones)
cd backend
pip install -r requirements.txt

# 3. Run database migrations (if using Alembic)
alembic upgrade head

# 4. Restart backend service
# For systemd:
sudo systemctl restart nbfc-backend

# For Docker:
docker-compose restart backend

# For manual:
# Stop existing process and start new one
python main.py
```

**Verify Backend:**
```bash
# Check API is running
curl http://localhost:8000/api/v1/hrms/performance/cycles

# Check OpenAPI docs
curl http://localhost:8000/docs
```

### Step 3: Frontend Deployment (10 minutes)

```bash
# 1. Build frontend
cd frontend/apps/admin-portal
npm run build

# 2. Deploy build (depends on your setup)
# For Nginx:
sudo cp -r dist/* /var/www/html/admin/

# For S3:
aws s3 sync dist/ s3://your-bucket/admin/

# For Docker:
docker-compose restart frontend

# 3. Verify build
ls -la dist/
```

**Verify Frontend:**
- Open browser: `http://your-domain/performance`
- Check console for errors
- Test navigation between pages

### Step 4: Configure First Appraisal Cycle (5 minutes)

```bash
# Run configuration script
cd scripts
python configure_first_appraisal_cycle.py
```

**Expected Output:**
```
✓ Appraisal Cycle 'APR-2024-25' created successfully
✓ Cycle period: April 1, 2024 to March 31, 2025
✓ Goal setting phase: April 1-30, 2024
✓ Self-assessment phase: January 1-31, 2025
✓ Manager review phase: February 1-28, 2025
✓ HR review phase: March 1-31, 2025
✓ Status: ACTIVE
✓ 150 employees assigned
```

### Step 5: Seed Sample Data (Optional, 5 minutes)

```bash
# Generate sample data for testing
python seed_performance_data.py
```

**Expected Output:**
```
✓ Created 5 sample appraisals
✓ Generated 20 goals (4 per employee)
✓ All goals have proper weightages (100% total)
```

### Step 6: User Communication (30 minutes)

**Send email to all employees:**

Subject: 📊 New Performance Management System Launched

Dear Team,

We're excited to announce the launch of our new Performance Management System! 🎉

**What's New:**
✓ Online goal setting and tracking
✓ Digital appraisal process
✓ 360-degree feedback
✓ Individual Development Plans (IDP)
✓ Real-time progress monitoring

**Current Appraisal Cycle:**
- Cycle: APR-2024-25 (April 1, 2024 - March 31, 2025)
- Goal Setting: April 1-30, 2024 ⏰ ACTIVE NOW
- Self-Assessment: January 1-31, 2025
- Manager Review: February 1-28, 2025
- HR Review & Finalization: March 1-31, 2025

**Action Required:**
1. Log in to the admin portal: https://your-domain
2. Navigate to Performance → My Goals
3. Set your performance goals for FY 2024-25
4. Submit for manager approval by April 30, 2024

**Need Help?**
- User Guide: https://your-domain/docs/performance-guide
- Training Video: https://your-domain/training/performance
- Support: hr@yourcompany.com

Best regards,
HR Team

---

**Send email to managers:**

Subject: 🎯 Performance Management System - Manager Guide

Dear Managers,

The new Performance Management System is now live. As a manager, you have additional responsibilities:

**Your Actions This Month:**
1. Review and approve team goals
2. Ensure goals are SMART and aligned with department objectives
3. Monitor team progress regularly

**Manager Dashboard:**
- View all team members' goals
- Approve/Reject with comments
- Track completion rates
- Schedule 1-on-1 meetings

**Manager Training:**
- Date: [Schedule training session]
- Duration: 1 hour
- Topics: Goal approval, feedback, ratings, increments

**Support:**
- Manager Guide: https://your-domain/docs/manager-guide
- HR Support: hr@yourcompany.com

Best regards,
HR Team

---

### Step 7: Monitoring & Testing (1 hour)

**Test Complete User Journey:**

1. **Employee Login → Goal Setting**
   - [ ] Can access Goals page
   - [ ] Can create new goal
   - [ ] Can edit draft goal
   - [ ] Can submit goal for approval
   - [ ] Receives confirmation

2. **Manager Login → Goal Approval**
   - [ ] Can see pending approvals
   - [ ] Can review goal details
   - [ ] Can approve with comments
   - [ ] Can reject with comments
   - [ ] Employee receives notification

3. **Employee Progress Updates**
   - [ ] Can update goal progress
   - [ ] Can add comments
   - [ ] Progress reflected in dashboard
   - [ ] Manager can see updates

4. **Self-Assessment (January)**
   - [ ] Can access self-assessment form
   - [ ] Can rate own performance
   - [ ] Can add achievements
   - [ ] Can submit assessment

5. **Manager Review (February)**
   - [ ] Can see self-assessment
   - [ ] Can add manager ratings
   - [ ] Can add comments
   - [ ] Can recommend increment
   - [ ] Can submit review

6. **HR Review (March)**
   - [ ] Can see all reviews
   - [ ] Can normalize ratings
   - [ ] Can finalize increments
   - [ ] Can generate reports

**Monitor API Performance:**

```bash
# Check API logs
tail -f /var/log/nbfc-backend/access.log | grep performance

# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/hrms/performance/cycles

# Check database performance
psql -U postgres -d nbfc_suite -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE tablename LIKE 'performance_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Monitor Frontend:**
- Check browser console for errors
- Test on different browsers (Chrome, Firefox, Safari)
- Test on mobile devices
- Check page load times

### Step 8: Post-Deployment Verification (30 minutes)

**Database Checks:**
```sql
-- Check cycle is active
SELECT * FROM performance_appraisal_cycles WHERE status = 'ACTIVE';

-- Check employees have access
SELECT cycle_id, COUNT(*) as employee_count 
FROM performance_employee_appraisals 
GROUP BY cycle_id;

-- Check goals are being created
SELECT COUNT(*) as goal_count FROM performance_goals;

-- Check audit trails are working
SELECT * FROM performance_goals ORDER BY created_at DESC LIMIT 5;
```

**API Health Check:**
```bash
# Test each endpoint category
curl -X GET http://localhost:8000/api/v1/hrms/performance/cycles
curl -X GET http://localhost:8000/api/v1/hrms/performance/goals
curl -X GET http://localhost:8000/api/v1/hrms/performance/appraisals
curl -X GET http://localhost:8000/api/v1/hrms/performance/feedback/requests
curl -X GET http://localhost:8000/api/v1/hrms/performance/increments
curl -X GET http://localhost:8000/api/v1/hrms/performance/idps
```

**Frontend Health Check:**
- [ ] Dashboard loads without errors
- [ ] All navigation links work
- [ ] Forms validate properly
- [ ] Data saves successfully
- [ ] Error messages display correctly
- [ ] Loading states work
- [ ] Pagination works
- [ ] Search/filter works

---

## Rollback Plan (If Needed)

### If Critical Issue Found:

1. **Disable Feature:**
```sql
-- Deactivate current cycle
UPDATE performance_appraisal_cycles 
SET status = 'DRAFT' 
WHERE status = 'ACTIVE';
```

2. **Restore Database:**
```bash
# Restore from backup
psql -U postgres -d nbfc_suite < backup_[timestamp].sql
```

3. **Revert Code:**
```bash
git revert HEAD
git push origin main
```

4. **Notify Users:**
Send email about temporary unavailability

---

## Production Go-Live Checklist

### Pre-Go-Live (1 week before)
- [ ] All code reviewed and tested
- [ ] Database migration tested on staging
- [ ] Performance testing completed
- [ ] Security audit completed
- [ ] User documentation prepared
- [ ] Training sessions scheduled
- [ ] Support team briefed
- [ ] Rollback plan documented

### Go-Live Day
- [ ] Backup database taken
- [ ] Deploy to production (off-peak hours)
- [ ] Run database migration
- [ ] Verify all services running
- [ ] Test critical user journeys
- [ ] Monitor logs for errors
- [ ] Send launch communication
- [ ] Support team on standby

### Post-Go-Live (First Week)
- [ ] Daily health checks
- [ ] Monitor user adoption
- [ ] Collect user feedback
- [ ] Address issues promptly
- [ ] Update documentation as needed
- [ ] Plan follow-up training if needed

### Success Metrics (First Month)
- [ ] 80%+ employees set goals
- [ ] 90%+ goal approval rate
- [ ] <2 second average API response time
- [ ] <5% error rate
- [ ] Positive user feedback (>4/5 rating)
- [ ] Zero critical bugs
- [ ] 95%+ system uptime

---

## Support & Maintenance

### Daily Tasks
- Monitor system health
- Check error logs
- Review user feedback
- Respond to support tickets

### Weekly Tasks
- Review performance metrics
- Check database growth
- Update documentation
- Plan improvements

### Monthly Tasks
- Generate usage reports
- Review and archive old data
- Update system documentation
- Plan new features

### Quarterly Tasks
- Security audit
- Performance optimization
- Major version updates
- User satisfaction survey

---

## Contact & Support

**Technical Issues:**
- Backend: backend-team@yourcompany.com
- Frontend: frontend-team@yourcompany.com
- Database: dba-team@yourcompany.com

**User Support:**
- HR Team: hr@yourcompany.com
- Help Desk: support@yourcompany.com
- Phone: 1-800-XXX-XXXX

**Emergency Contact:**
- On-Call Engineer: oncall@yourcompany.com
- Emergency Phone: 1-800-XXX-YYYY

---

## Conclusion

This deployment checklist ensures a smooth rollout of the Performance Management System. Follow each step carefully and verify completion before proceeding to the next step.

**Estimated Total Deployment Time:** 2-3 hours
**Recommended Deployment Window:** Off-peak hours (Saturday/Sunday morning)
**Team Required:** 1 Backend Dev, 1 Frontend Dev, 1 DBA, 1 HR Rep

**Status After Completion:**
✅ System fully operational
✅ Users can start using immediately
✅ Support team ready
✅ Monitoring in place

Good luck with the deployment! 🚀
