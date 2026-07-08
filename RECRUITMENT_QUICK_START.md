# HRMS Recruitment & Onboarding - Quick Start Guide

## 🚀 Quick Setup

### 1. Run Database Migration

```bash
# Connect to PostgreSQL
psql -U postgres -d nbfc_db

# Run the migration
\i database/migrations/add_recruitment_tables_migration.sql

# Verify tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('job_requisitions', 'job_postings', 'job_applications', 'interviews', 'onboarding', 'background_verifications');
```

### 2. Start Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 3. Start Frontend

```bash
cd frontend/apps/admin-portal
npm install
npm run dev
```

### 4. Access the Application

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## 📱 User Interface Pages

### 1. Job Requisitions
**URL**: `/recruitment/requisitions`

**Features**:
- View all job requisitions with filters
- Create new requisition
- Submit for approval
- Approve/Reject requisitions
- Track status (Draft → Pending → Approved/Rejected)

**Actions**:
- Click "+ New Requisition" to create
- Use filters to search by status, priority, department
- Click "Submit" to send for approval
- Click "Approve" or "Reject" for pending requisitions

### 2. Applicant Tracking System (ATS)
**URL**: `/recruitment/applications`

**Features**:
- Kanban board with 7 stages
- Drag-and-drop to change status
- View candidate details
- Schedule interviews
- Bulk actions

**Actions**:
- Drag cards between columns to update status
- Click "Shortlist" to move from New to Shortlisted
- Click "Schedule Interview" for shortlisted candidates
- Click "View Resume" to download resume

### 3. Interview Scheduling
**URL**: `/recruitment/interviews`

**Features**:
- Calendar view of all interviews
- Today's schedule highlight
- Schedule new interviews
- Mark completed/cancelled
- Submit feedback and ratings

**Actions**:
- Click "+ Schedule Interview" to create
- View today's interviews in highlight section
- Click "Complete" after interview
- Click "Add Feedback" to rate candidate

### 4. Onboarding Management
**URL**: `/recruitment/onboarding`

**Features**:
- Track all onboarding processes
- Interactive checklist
- Progress tracking
- Background verification status

**Actions**:
- Click "+ New Onboarding" to create
- Click "Checklist" to view/update tasks
- Check/uncheck items to track progress
- Click "Start" to begin onboarding
- Click "Complete" when all tasks done

## 🔧 API Endpoints Reference

### Job Requisitions
```bash
# List requisitions
GET /api/v1/recruitment/requisitions?page=1&page_size=20&status=APPROVED

# Create requisition
POST /api/v1/recruitment/requisitions
{
  "title": "Senior Software Engineer",
  "department_id": "uuid",
  "designation_id": "uuid",
  "number_of_positions": 2,
  "employment_type": "FULL_TIME",
  "work_location": "Bangalore",
  "priority": "HIGH"
}

# Submit for approval
POST /api/v1/recruitment/requisitions/{id}/submit

# Approve/Reject
POST /api/v1/recruitment/requisitions/{id}/approve
{
  "approved": true,
  "rejection_reason": null
}
```

### Job Postings
```bash
# Create posting from requisition
POST /api/v1/recruitment/postings
{
  "requisition_id": "uuid",
  "title": "Senior Software Engineer",
  "job_description": "...",
  "employment_type": "FULL_TIME",
  "work_location": "Bangalore"
}

# Publish posting
POST /api/v1/recruitment/postings/{id}/publish

# Get public postings (career page)
GET /api/v1/recruitment/postings/public?page=1&page_size=20
```

### Job Applications
```bash
# Get kanban view
GET /api/v1/recruitment/applications/kanban?posting_id=uuid

# Change status
POST /api/v1/recruitment/applications/{id}/status
{
  "status": "SHORTLISTED",
  "notes": "Candidate has good experience"
}

# Shortlist candidate
POST /api/v1/recruitment/applications/{id}/shortlist

# Reject candidate
POST /api/v1/recruitment/applications/{id}/reject?rejection_reason=Not%20suitable
```

### Interviews
```bash
# Schedule interview
POST /api/v1/recruitment/interviews
{
  "application_id": "uuid",
  "interview_type": "TECHNICAL",
  "round_number": 1,
  "scheduled_date": "2026-07-15",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "interview_mode": "VIDEO",
  "meeting_link": "https://zoom.us/j/xxx",
  "interviewer_ids": ["uuid1", "uuid2"]
}

# Submit feedback
POST /api/v1/recruitment/interviews/{id}/feedback
{
  "rating": 4.5,
  "feedback_notes": "Strong technical skills",
  "recommendation": "HIRE"
}
```

### Onboarding
```bash
# Create onboarding
POST /api/v1/recruitment/onboarding
{
  "application_id": "uuid",
  "joining_date": "2026-08-01",
  "department_id": "uuid",
  "designation_id": "uuid",
  "offered_salary": 1200000,
  "probation_period_months": 3
}

# Start onboarding
POST /api/v1/recruitment/onboarding/{id}/start

# Update checklist item
PUT /api/v1/recruitment/onboarding/{id}/checklist-item
{
  "item_key": "submit_documents",
  "completed": true
}
```

## 🔐 Authentication

All API requests require authentication:

```javascript
// Example with axios
axios.get('/api/v1/recruitment/requisitions', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': 'default'
  }
});
```

## 📊 Common Workflows

### Workflow 1: Hire a New Employee

1. **Create Requisition**
   - Go to `/recruitment/requisitions`
   - Click "+ New Requisition"
   - Fill form and save as Draft

2. **Submit for Approval**
   - Click "Submit" button
   - Status changes to "Pending Approval"

3. **Approve Requisition**
   - Manager clicks "Approve"
   - Status changes to "Approved"

4. **Create Job Posting**
   - Create posting from approved requisition
   - Click "Publish" to make live

5. **Receive Applications**
   - Applications appear in ATS
   - Start at "New" status

6. **Screen & Shortlist**
   - Review applications
   - Click "Shortlist" for good candidates

7. **Schedule Interviews**
   - Go to shortlisted applications
   - Click "Schedule Interview"
   - Fill interview details

8. **Conduct Interviews**
   - View today's schedule
   - Mark "Complete" after interview
   - Submit feedback and rating

9. **Make Offer**
   - Change application status to "Offered"
   - Candidate accepts

10. **Create Onboarding**
    - Go to `/recruitment/onboarding`
    - Create new onboarding record
    - Set joining date and details

11. **Track Onboarding**
    - Click "Start" to begin
    - Update checklist items
    - Track progress

12. **Complete Onboarding**
    - All tasks checked
    - Click "Complete"
    - Status changes to "Completed"

### Workflow 2: Reject a Candidate

1. Go to ATS kanban board
2. Find candidate card
3. Click "Reject" button
4. Enter rejection reason
5. Card moves to "Rejected" column

### Workflow 3: Reschedule Interview

1. Go to interview calendar
2. Find interview
3. Click interview code to view details
4. Click "Reschedule"
5. Enter new date/time and reason
6. Save changes

## 🎨 UI Tips

### Filters & Search
- Use search box for quick text search
- Combine multiple filters for precise results
- Click "Clear Filters" to reset

### Drag & Drop (ATS)
- Click and hold on application card
- Drag to another column
- Release to drop
- Status updates automatically

### Progress Tracking
- Green progress bars show completion
- Percentage displayed on right
- Click "Checklist" for details

### Status Badges
- **Gray**: Inactive/Draft
- **Yellow**: Pending/In Progress
- **Green**: Approved/Completed
- **Red**: Rejected/Failed
- **Blue**: Active/Scheduled

## 📈 Dashboard Metrics

### Requisition Dashboard
- Total requisitions created
- By status breakdown
- By priority distribution
- By department

### ATS Dashboard
- Applications per stage
- Source effectiveness
- Time in each stage
- Conversion rates

### Interview Dashboard
- Today's schedule
- Upcoming interviews
- Completion rate
- Average ratings

### Onboarding Dashboard
- Active onboardings
- Average completion time
- Pending verifications
- Completion rate

## 🐛 Troubleshooting

### Issue: API returns 401 Unauthorized
**Solution**: Check authentication token is valid and not expired

### Issue: Tables not found
**Solution**: Run database migration script

### Issue: Frontend not loading data
**Solution**: 
1. Check API server is running
2. Verify NEXT_PUBLIC_API_URL in .env
3. Check browser console for errors

### Issue: Drag and drop not working
**Solution**: 
1. Refresh the page
2. Clear browser cache
3. Check application status is valid for transition

### Issue: Checklist items not saving
**Solution**: 
1. Check onboarding status is "In Progress"
2. Verify network connection
3. Check API logs for errors

## 📞 Support

For issues or questions:
- Check API documentation: http://localhost:8000/docs
- Review error messages in browser console
- Check backend logs for API errors
- Refer to RECRUITMENT_MODULE_COMPLETE.md for detailed documentation

## ✅ Testing Checklist

- [ ] Database migration completed
- [ ] Backend server running
- [ ] Frontend server running
- [ ] Can access requisitions page
- [ ] Can create new requisition
- [ ] Can view ATS kanban board
- [ ] Drag and drop works
- [ ] Can schedule interview
- [ ] Can create onboarding
- [ ] Checklist modal works
- [ ] All filters functional
- [ ] Pagination works

---

**Quick Start Guide Version**: 1.0  
**Last Updated**: July 8, 2026  
**Module**: HRMS Recruitment & Onboarding
