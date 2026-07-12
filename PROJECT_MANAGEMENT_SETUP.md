# Project Management Module - Setup & Integration Guide

## Quick Setup Guide

### 1. Backend Integration

#### Step 1: Register the Router in Main Application

Edit `backend/main.py` to include the project management router:

```python
from backend.services.project_management import router as project_management_router

# Add to your FastAPI app
app.include_router(project_management_router)
```

#### Step 2: Run Database Migration

```bash
cd backend

# Create migration for new tables
alembic revision --autogenerate -m "Add project management tables"

# Apply migration
alembic upgrade head
```

#### Step 3: Verify Backend is Running

```bash
# Start backend server
python -m uvicorn main:app --reload --port 8000

# Check API documentation
# Navigate to: http://localhost:8000/docs
```

### 2. Frontend Integration

#### Step 1: Add Routes to Your Application

Create or edit your main routing file (e.g., `frontend/src/App.tsx`):

```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {
  ProjectList,
  TaskBoard,
  TimeTracking,
  BudgetManagement,
} from './components/project-management';

function App() {
  return (
    <Router>
      <Routes>
        {/* Project Management Routes */}
        <Route path="/project-management" element={<ProjectList />} />
        <Route path="/project-management/projects" element={<ProjectList />} />
        <Route path="/project-management/tasks" element={<TaskBoard />} />
        <Route path="/project-management/tasks/:projectId" element={<TaskBoard />} />
        <Route path="/project-management/time-tracking" element={<TimeTracking />} />
        <Route path="/project-management/budgets" element={<BudgetManagement />} />
        <Route path="/project-management/budgets/:projectId" element={<BudgetManagement />} />
        
        {/* Other routes */}
      </Routes>
    </Router>
  );
}

export default App;
```

#### Step 2: Add Navigation Menu Items

Update your navigation component to include project management links:

```typescript
<nav>
  <ul>
    <li>
      <a href="/project-management/projects">
        <i className="bi bi-folder"></i> Projects
      </a>
    </li>
    <li>
      <a href="/project-management/tasks">
        <i className="bi bi-check-square"></i> Tasks
      </a>
    </li>
    <li>
      <a href="/project-management/time-tracking">
        <i className="bi bi-clock"></i> Time Tracking
      </a>
    </li>
    <li>
      <a href="/project-management/budgets">
        <i className="bi bi-cash-stack"></i> Budgets
      </a>
    </li>
  </ul>
</nav>
```

#### Step 3: Configure API Base URL

Create or update `.env` file in frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production:

```env
REACT_APP_API_URL=https://your-production-api.com
```

#### Step 4: Install Required Dependencies

```bash
cd frontend

# Install dependencies if not already installed
npm install axios react-router-dom
npm install --save-dev @types/react-router-dom

# Install Bootstrap Icons (if not already installed)
npm install bootstrap-icons
```

Add Bootstrap Icons to your main CSS or index.html:

```html
<!-- In public/index.html -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
```

Or import in your main CSS file:

```css
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css");
```

### 3. Database Setup

The module requires the following relationships with existing tables:

#### Employee Relationships
The project management models link to the Employee table from HRMS module:
- Task assignments
- Time tracking
- Resource allocations
- Project managers

Ensure the `hrms_employees` table exists before running migrations.

#### Department Relationships
Projects can be linked to departments for organization-wide tracking.

### 4. Testing the Integration

#### Test Backend APIs

```bash
# Using curl
curl -X GET "http://localhost:8000/api/project-management/projects/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Or use the Swagger UI
http://localhost:8000/docs
```

#### Test Frontend

```bash
cd frontend
npm start

# Navigate to:
http://localhost:3000/project-management/projects
```

### 5. Sample Data Setup (Optional)

Create a script to populate sample data:

```python
# backend/scripts/seed_project_management.py
import asyncio
from datetime import date, timedelta
from backend.shared.database.connection import get_async_session
from backend.services.project_management.project_service import ProjectService
from backend.services.project_management.task_service import TaskService

async def seed_data():
    async for db in get_async_session():
        # Assuming you have a tenant_id and user_id
        tenant_id = "your-tenant-id"
        user_id = "your-user-id"
        
        # Create sample project
        project_service = ProjectService(db, tenant_id, user_id)
        project = await project_service.create_project({
            "project_name": "Sample Website Project",
            "project_type": "development",
            "project_priority": "high",
            "status": "in_progress",
            "planned_start_date": date.today(),
            "planned_end_date": date.today() + timedelta(days=90),
            "estimated_budget": 1000000,
            "is_billable": True
        })
        
        # Create sample tasks
        task_service = TaskService(db, tenant_id, user_id)
        await task_service.create_task({
            "task_title": "Setup Development Environment",
            "project_id": project.id,
            "task_type": "feature",
            "task_priority": "high",
            "status": "in_progress",
            "estimated_hours": 8
        })
        
        print("Sample data created successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
```

## Advanced Configuration

### Custom Permissions

Add role-based access control to protect routes:

```python
# In routers
from backend.shared.middleware.auth import require_role

@router.post("/", response_model=ProjectDetail)
@require_role("project_manager")  # Add custom decorator
async def create_project(data: ProjectCreate, ...):
    # Only users with project_manager role can create projects
    pass
```

### Email Notifications

Integrate email notifications for:
- Task assignments
- Time entry approvals
- Budget alerts
- Project status changes

```python
# Example notification service
from backend.services.notification import NotificationService

async def notify_task_assigned(task: Task):
    notification_service = NotificationService()
    await notification_service.send_email(
        to=task.assigned_to.official_email,
        subject=f"New Task Assigned: {task.task_title}",
        body=f"You have been assigned a new task..."
    )
```

### Webhooks Integration

Add webhook support for external integrations:

```python
@router.post("/webhooks/task-created")
async def task_created_webhook(task: Task):
    # Integrate with Slack, Teams, etc.
    await slack_notify(f"New task created: {task.task_title}")
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: Could not connect to database
```
**Solution**: Check your database configuration in `.env` file and ensure the database is running.

#### 2. CORS Error in Frontend
```
Access to XMLHttpRequest has been blocked by CORS policy
```
**Solution**: Configure CORS in `backend/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. Authentication Token Not Working
```
401 Unauthorized
```
**Solution**: Ensure the token is stored in localStorage and the interceptor is configured:

```typescript
// In projectManagementService.ts
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### 4. Frontend Components Not Rendering
```
Module not found: Can't resolve './components/project-management'
```
**Solution**: Check import paths and ensure all files are in correct locations.

#### 5. Migration Conflicts
```
Duplicate column name or table already exists
```
**Solution**: 
```bash
# Drop and recreate (development only!)
alembic downgrade base
alembic upgrade head

# Or create a new migration
alembic revision --autogenerate -m "Fix conflicts"
```

## Performance Optimization

### Backend Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_project_stats_cached(tenant_id: str):
    # Cache project statistics
    pass
```

### Frontend Optimization

```typescript
// Use React.memo for expensive components
export default React.memo(ProjectList);

// Debounce search inputs
import { debounce } from 'lodash';

const debouncedSearch = debounce((value) => {
  setSearch(value);
}, 300);
```

## Deployment Checklist

- [ ] Run database migrations in production
- [ ] Configure production API URL in frontend
- [ ] Set up environment variables
- [ ] Configure CORS for production domain
- [ ] Set up SSL certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging
- [ ] Test all API endpoints
- [ ] Test all frontend routes
- [ ] Set up user permissions
- [ ] Configure email notifications (if enabled)
- [ ] Load test with expected user volume
- [ ] Document any custom configurations

## Security Best Practices

1. **Input Validation**: All inputs validated on both frontend and backend
2. **SQL Injection Protection**: Using SQLAlchemy ORM with parameterized queries
3. **XSS Protection**: React automatically escapes output
4. **CSRF Protection**: Token-based authentication
5. **Authorization**: Check user permissions before operations
6. **Rate Limiting**: Implement rate limiting on API endpoints (recommended)
7. **Audit Logging**: Log all significant operations

## Support

For issues or questions:
1. Check this documentation
2. Review the API documentation at `/docs`
3. Check the comprehensive module documentation in `PROJECT_MANAGEMENT_MODULE.md`
4. Review the codebase for examples

## Maintenance

### Regular Tasks
- Monitor database size and optimize queries
- Review and archive old projects
- Clean up completed time entries
- Review budget alerts and thresholds
- Update dependencies regularly
- Backup database regularly

### Recommended Updates
- Weekly: Review and fix any bugs
- Monthly: Performance optimization
- Quarterly: Security audit
- Annually: Major feature updates

---

**Module Version**: 1.0.0  
**Last Updated**: July 12, 2026  
**Status**: Production Ready ✅
