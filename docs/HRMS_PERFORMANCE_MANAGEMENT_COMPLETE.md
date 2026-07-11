# HRMS Performance Management System - Complete Implementation Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features Implemented](#features-implemented)
3. [Architecture](#architecture)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Frontend Components](#frontend-components)
7. [Setup & Deployment](#setup--deployment)
8. [Usage Guide](#usage-guide)
9. [Testing](#testing)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The HRMS Performance Management System is a comprehensive solution for managing employee performance, goal setting, appraisals, 360-degree feedback, ratings, increments, and Individual Development Plans (IDP).

### Key Features

- **Goal Setting (KRA/KPI)**: Define and track Key Result Areas and Key Performance Indicators
- **Appraisal Cycles**: Manage periodic performance review cycles with configurable phases
- **360-Degree Feedback**: Collect feedback from multiple stakeholders (self, manager, peers, subordinates)
- **Rating & Increment**: Performance-based ratings and salary increment management
- **Individual Development Plans (IDP)**: Career development and skill enhancement planning
- **Complete Workflow**: From goal setting → self-assessment → manager review → HR review → increment

### Technology Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL Database
- Pydantic for validation

**Frontend:**
- React with TypeScript
- Axios for API calls
- React Router for navigation

---

## ✅ Features Implemented

### 1. Goal Setting (KRA/KPI)
- ✅ Create performance goals with weightage
- ✅ Goal types: KRA, KPI, Objective, Project
- ✅ Goal priorities: Low, Medium, High, Critical
- ✅ Progress tracking with percentage completion
- ✅ Submit goals for approval workflow
- ✅ Manager approval/rejection with comments
- ✅ Goal achievement calculation

### 2. Appraisal Cycles
- ✅ Create annual/periodic appraisal cycles
- ✅ Define phase timelines (goal setting, self-assessment, manager review, etc.)
- ✅ Status management (Draft → Active → Completed)
- ✅ Configuration options (enable/disable 360 feedback, self-assessment, goal setting)
- ✅ Track progress (total employees, completed appraisals)

### 3. Employee Appraisals
- ✅ Self-assessment with rating and comments
- ✅ Key achievements and improvement areas
- ✅ Manager review with separate rating
- ✅ Manager feedback on strengths and development areas
- ✅ HR review with normalization capability
- ✅ Final rating calculation
- ✅ Increment and promotion recommendations
- ✅ Complete appraisal workflow status tracking

### 4. 360-Degree Feedback
- ✅ Create feedback requests for multiple stakeholders
- ✅ Feedback types: Self, Manager, Peer, Subordinate, Customer, Other
- ✅ Competency-based ratings (Technical, Communication, Teamwork, Leadership, Problem Solving)
- ✅ Qualitative feedback (strengths, areas for improvement)
- ✅ Anonymous feedback option
- ✅ Feedback reminder system
- ✅ Consolidated feedback summary

### 5. Performance Increments
- ✅ Create increment records linked to appraisals
- ✅ Increment types: Annual, Promotion, Special, Performance-based, Market Correction
- ✅ Auto-calculation of increment amount and revised CTC
- ✅ Approval workflow
- ✅ Processing status tracking
- ✅ Integration with appraisal recommendations

### 6. Individual Development Plans (IDP)
- ✅ Create career development plans
- ✅ Define career goals and target roles
- ✅ Skill gap analysis
- ✅ Development activity tracking
- ✅ Activity types: Training, Certification, Workshop, Mentoring, Job Rotation, etc.
- ✅ Progress tracking with completion percentage
- ✅ Certificate and learning outcome management
- ✅ Submit and approval workflow

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + TypeScript)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Dashboard  │  │    Goals     │  │  Appraisals  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Feedback   │  │  Increments  │  │     IDP      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API (HTTPS)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Performance Routes (Router)                 │  │
│  │  /cycles  /goals  /appraisals  /feedback  /increments   │  │
│  │  /idp  /activities                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Performance Management Service (Business Logic)   │  │
│  │  - Goal calculation  - Workflow management                │  │
│  │  - Rating normalization  - Progress tracking              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Database Models (SQLAlchemy ORM)             │  │
│  │  AppraisalCycle, PerformanceGoal, EmployeeAppraisal,     │  │
│  │  FeedbackRequest, FeedbackResponse, PerformanceIncrement,│  │
│  │  IndividualDevelopmentPlan, DevelopmentActivity          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│  Tables: hrms_appraisal_cycles, hrms_performance_goals,         │
│          hrms_employee_appraisals, hrms_feedback_requests,      │
│          hrms_feedback_responses, hrms_performance_increments,  │
│          hrms_individual_development_plans,                     │
│          hrms_development_activities                            │
└─────────────────────────────────────────────────────────────────┘
```

### Layered Architecture

1. **Presentation Layer** (Frontend)
   - React components
   - TypeScript types
   - API service layer

2. **API Layer** (Backend Routes)
   - FastAPI routers
   - Request/response schemas
   - Authentication & authorization

3. **Business Logic Layer** (Services)
   - PerformanceManagementService
   - Workflow logic
   - Calculations & validations

4. **Data Access Layer** (Models)
   - SQLAlchemy ORM models
   - Database relationships
   - Query optimization

5. **Database Layer**
   - PostgreSQL
   - Tables with indexes
   - Constraints & triggers

---

## 📊 Database Schema

### Entity Relationship Diagram (ERD)

```
┌─────────────────────┐
│  AppraisalCycle     │
│  ─────────────────  │
│  id (PK)            │
│  cycle_code (UK)    │
│  cycle_name         │
│  fiscal_year        │
│  start_date         │
│  end_date           │
│  status             │
│  ...phase_dates     │
└─────────────────────┘
         │
         │ 1:N
         ┼────────────────────────────────────────────┐
         │                                            │
         ▼                                            ▼
┌─────────────────────┐                    ┌──────────────────────┐
│  PerformanceGoal    │                    │  EmployeeAppraisal   │
│  ─────────────────  │                    │  ──────────────────  │
│  id (PK)            │                    │  id (PK)             │
│  goal_code          │                    │  appraisal_code (UK) │
│  employee_id (FK)   │                    │  employee_id (FK)    │
│  cycle_id (FK)      │                    │  cycle_id (FK)       │
│  goal_type          │                    │  reviewer_id (FK)    │
│  priority           │                    │  status              │
│  target_value       │                    │  self_rating         │
│  achieved_value     │                    │  manager_rating      │
│  weightage          │                    │  final_rating        │
│  progress_%         │                    │  increment_%         │
│  status             │                    │  ...                 │
└─────────────────────┘                    └──────────────────────┘
                                                     │
                                                     │ 1:N
                                                     ▼
                                          ┌──────────────────────┐
                                          │  FeedbackRequest     │
                                          │  ──────────────────  │
                                          │  id (PK)             │
                                          │  employee_id (FK)    │
                                          │  reviewer_id (FK)    │
                                          │  cycle_id (FK)       │
                                          │  feedback_type       │
                                          │  status              │
                                          └──────────────────────┘
                                                     │
                                                     │ 1:1
                                                     ▼
                                          ┌──────────────────────┐
                                          │  FeedbackResponse    │
                                          │  ──────────────────  │
                                          │  id (PK)             │
                                          │  request_id (FK, UK) │
                                          │  overall_rating      │
                                          │  competency_ratings  │
                                          │  strengths           │
                                          │  improvements        │
                                          └──────────────────────┘

┌──────────────────────┐
│PerformanceIncrement  │
│  ──────────────────  │
│  id (PK)             │
│  employee_id (FK)    │
│  appraisal_id (FK)   │
│  cycle_id (FK)       │
│  increment_type      │
│  current_ctc         │
│  increment_%         │
│  revised_ctc         │
│  is_approved         │
│  is_processed        │
└──────────────────────┘

┌──────────────────────────┐
│IndividualDevelopmentPlan │
│  ──────────────────────  │
│  id (PK)                 │
│  idp_code (UK)           │
│  employee_id (FK)        │
│  cycle_id (FK)           │
│  career_goal             │
│  target_role             │
│  skill_gaps              │
│  progress_%              │
│  status                  │
└──────────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────────────┐
│  DevelopmentActivity     │
│  ──────────────────────  │
│  id (PK)                 │
│  idp_id (FK)             │
│  activity_code           │
│  activity_type           │
│  planned_dates           │
│  actual_dates            │
│  completion_%            │
│  certification           │
└──────────────────────────┘
```

### Key Tables

#### 1. hrms_appraisal_cycles
Manages appraisal cycle configuration and timeline.

**Key Fields:**
- `cycle_code`: Unique identifier (e.g., APR-2024-25)
- `fiscal_year`: Financial year
- `status`: Draft, Active, Goal Setting, Self Assessment, Manager Review, HR Review, Completed
- Phase dates: goal_setting_start/end, self_assessment_start/end, etc.

#### 2. hrms_performance_goals
Stores employee performance goals (KRA/KPI).

**Key Fields:**
- `goal_type`: KRA, KPI, Objective, Project
- `goal_priority`: Low, Medium, High, Critical
- `weightage`: Percentage contribution (0-100)
- `progress_percentage`: Achievement level (0-100)
- `status`: Draft, Submitted, Approved, Rejected, In Progress, Completed

#### 3. hrms_employee_appraisals
Main appraisal record for each employee per cycle.

**Key Fields:**
- `self_rating`, `manager_rating`, `final_rating`: RatingScale enum
- `self_rating_numeric`, `manager_rating_numeric`, `final_rating_numeric`: 1.00-5.00
- `normalized_rating`: After HR normalization
- `recommended_increment_percentage`: Manager's recommendation
- `recommended_promotion`: Boolean flag
- `status`: Tracks workflow progress

#### 4. hrms_feedback_requests & hrms_feedback_responses
360-degree feedback mechanism.

**Request Fields:**
- `feedback_type`: Self, Manager, Peer, Subordinate, Customer, Other
- `status`: Pending, Submitted, Acknowledged

**Response Fields:**
- Competency ratings: technical_skills, communication, teamwork, leadership, problem_solving (1-5)
- Qualitative: strengths, areas_for_improvement, additional_comments
- `is_anonymous`: Boolean for confidential feedback

#### 5. hrms_performance_increments
Salary increment tracking and approval.

**Key Fields:**
- `increment_type`: Annual, Promotion, Special, Performance-based, Market Correction
- `current_ctc`, `increment_percentage`, `increment_amount`, `revised_ctc`
- `is_approved`, `is_processed`: Workflow flags

#### 6. hrms_individual_development_plans & hrms_development_activities
Career development and learning tracking.

**IDP Fields:**
- `career_goal`, `target_role`, `target_designation_id`
- `current_skills`, `required_skills`, `skill_gaps`
- `overall_progress_percentage`

**Activity Fields:**
- `activity_type`: Training, Certification, Workshop, Mentoring, etc.
- `planned_start_date`, `planned_end_date`
- `actual_start_date`, `actual_end_date`
- `completion_percentage`, `is_completed`

### Database Indexes

All tables have optimized indexes on:
- Primary keys (id)
- Foreign keys (employee_id, cycle_id, etc.)
- Frequently queried fields (status, tenant_id)
- Unique constraints (cycle_code, appraisal_code, etc.)

---

## 🔌 API Endpoints

Base URL: `/api/v1/hrms/performance`

### Appraisal Cycles

```http
POST   /cycles                    # Create new cycle
GET    /cycles                    # List all cycles (with filters)
GET    /cycles/{id}               # Get cycle by ID
PATCH  /cycles/{id}               # Update cycle
DELETE /cycles/{id}               # Delete cycle
```

**Query Parameters for List:**
- `status`: Filter by AppraisalCycleStatus
- `fiscal_year`: Filter by fiscal year
- `skip`, `limit`: Pagination

### Performance Goals

```http
POST   /goals                                    # Create goal
GET    /goals/{id}                               # Get goal by ID
GET    /employees/{employee_id}/goals            # List employee goals
PATCH  /goals/{id}                               # Update goal
POST   /employees/{employee_id}/goals/submit     # Submit all goals
POST   /goals/{id}/approve                       # Approve goal
POST   /goals/{id}/reject                        # Reject goal
```

### Employee Appraisals

```http
POST   /appraisals                               # Create appraisal
GET    /appraisals                               # List appraisals (with filters)
GET    /appraisals/{id}                          # Get appraisal by ID
POST   /appraisals/{id}/self-assessment          # Submit self-assessment
POST   /appraisals/{id}/manager-review           # Submit manager review
POST   /appraisals/{id}/hr-review                # Submit HR review & finalize
```

### 360 Feedback

```http
POST   /feedback/requests                        # Create feedback request
GET    /feedback/requests/reviewer/{id}          # List requests for reviewer
POST   /feedback/requests/{id}/respond           # Submit feedback response
GET    /feedback/employee/{id}                   # List feedback for employee
```

### Performance Increments

```http
POST   /increments                               # Create increment
GET    /employees/{employee_id}/increments       # List employee increments
POST   /increments/{id}/approve                  # Approve increment
POST   /increments/{id}/process                  # Mark as processed
```

### Individual Development Plans

```http
POST   /idp                                      # Create IDP
GET    /idp/{id}                                 # Get IDP by ID
GET    /employees/{employee_id}/idp              # List employee IDPs
PATCH  /idp/{id}                                 # Update IDP
POST   /idp/{id}/submit                          # Submit for approval
POST   /idp/{id}/approve                         # Approve IDP
```

### Development Activities

```http
POST   /idp/activities                           # Create activity
GET    /idp/{idp_id}/activities                  # List activities for IDP
GET    /idp/activities/{id}                      # Get activity by ID
PATCH  /idp/activities/{id}                      # Update activity
```

### Example API Requests

#### Create Appraisal Cycle

```json
POST /api/v1/hrms/performance/cycles

{
  "cycle_code": "APR-2024-25",
  "cycle_name": "Annual Appraisal 2024-25",
  "cycle_description": "Annual performance review cycle",
  "fiscal_year": "2024-25",
  "start_date": "2024-04-01",
  "end_date": "2025-03-31",
  "goal_setting_start": "2024-04-01",
  "goal_setting_end": "2024-04-30",
  "self_assessment_start": "2025-01-01",
  "self_assessment_end": "2025-01-31",
  "manager_review_start": "2025-02-01",
  "manager_review_end": "2025-02-28",
  "hr_review_start": "2025-03-01",
  "hr_review_end": "2025-03-15",
  "enable_360_feedback": true,
  "enable_self_assessment": true,
  "enable_goal_setting": true
}
```

#### Create Performance Goal

```json
POST /api/v1/hrms/performance/goals

{
  "goal_code": "G-2024-001",
  "goal_title": "Complete Project Alpha on time",
  "goal_description": "Deliver Project Alpha with all features by Q4",
  "goal_type": "project",
  "goal_priority": "high",
  "employee_id": "uuid-here",
  "appraisal_cycle_id": "uuid-here",
  "measurement_criteria": "Project completion within timeline and budget",
  "target_value": "100%",
  "uom": "percentage",
  "weightage": 25,
  "start_date": "2024-04-01",
  "target_date": "2024-12-31"
}
```

#### Submit Self-Assessment

```json
POST /api/v1/hrms/performance/appraisals/{appraisal_id}/self-assessment

{
  "self_rating": "exceeds_expectations",
  "self_rating_numeric": 4.0,
  "self_comments": "Successfully completed all major projects...",
  "key_achievements": "Led Project Alpha, Mentored 2 junior developers...",
  "areas_of_improvement": "Need to improve public speaking skills..."
}
```

#### Submit Manager Review

```json
POST /api/v1/hrms/performance/appraisals/{appraisal_id}/manager-review

{
  "manager_rating": "exceeds_expectations",
  "manager_rating_numeric": 4.0,
  "manager_comments": "Excellent performance throughout the year...",
  "manager_strengths": "Strong technical skills, good team player...",
  "manager_development_areas": "Focus on leadership development...",
  "recommended_increment_percentage": 12,
  "recommended_promotion": false
}
```

---

## 🎨 Frontend Components

### File Structure

```
frontend/apps/admin-portal/src/
├── types/
│   └── performance.types.ts              # TypeScript types
├── services/
│   └── performance.service.ts            # API service layer
└── pages/
    └── performance/
        ├── PerformanceManagementRoutes.tsx
        ├── dashboard/
        │   └── PerformanceDashboard.tsx
        ├── cycles/
        │   ├── AppraisalCycleList.tsx
        │   ├── AppraisalCycleForm.tsx
        │   └── AppraisalCycleDetail.tsx
        ├── goals/
        │   ├── GoalsList.tsx
        │   ├── GoalsForm.tsx
        │   └── GoalsApproval.tsx
        ├── appraisals/
        │   ├── AppraisalsList.tsx
        │   ├── AppraisalDetail.tsx
        │   ├── SelfAssessmentForm.tsx
        │   ├── ManagerReviewForm.tsx
        │   └── HRReviewForm.tsx
        ├── feedback/
        │   ├── FeedbackRequestList.tsx
        │   ├── FeedbackResponseForm.tsx
        │   └── FeedbackSummary.tsx
        ├── increments/
        │   ├── IncrementsList.tsx
        │   ├── IncrementForm.tsx
        │   └── IncrementApproval.tsx
        └── idp/
            ├── IDPList.tsx
            ├── IDPForm.tsx
            ├── IDPDetail.tsx
            └── ActivityForm.tsx
```

### Key React Components

Refer to `docs/PERFORMANCE_MANAGEMENT_UI_SPECIFICATION.md` for detailed component specifications.

---

## 🚀 Setup & Deployment

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

2. **Database Migration**

```bash
# Run the migration script
psql -U postgres -d nbfc_db -f database/migrations/add_performance_management_tables.sql
```

Or use Alembic:

```bash
alembic upgrade head
```

3. **Verify Models**

```python
# In Python shell
from backend.shared.database.hrms_models import *
from backend.shared.database.connection import engine

# Check if tables exist
inspector = inspect(engine)
tables = inspector.get_table_names()
print([t for t in tables if 'performance' in t or 'appraisal' in t or 'idp' in t])
```

### Frontend Setup

1. **Install Dependencies**

```bash
cd frontend/apps/admin-portal
npm install
```

2. **Environment Configuration**

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

3. **Start Development Server**

```bash
npm run dev
```

### Testing the Implementation

1. **Test Backend APIs**

```bash
# Start backend server
cd backend
uvicorn main:app --reload

# Access API documentation
open http://localhost:8000/docs
```

2. **Test Endpoints**

Use the Swagger UI at `/docs` or:

```bash
# Create a cycle
curl -X POST http://localhost:8000/api/v1/hrms/performance/cycles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "cycle_code": "TEST-2024",
    "cycle_name": "Test Cycle",
    "fiscal_year": "2024-25",
    "start_date": "2024-04-01",
    "end_date": "2025-03-31"
  }'
```

---

## 📖 Usage Guide

### Complete Appraisal Workflow

#### Phase 1: Setup (HR Admin)

1. **Create Appraisal Cycle**
   - Navigate to Performance → Cycles
   - Click "New Cycle"
   - Fill in cycle details and phase timelines
   - Set status to "Active"

2. **Assign Appraisals**
   - System auto-creates appraisal records for all employees
   - Or manually create via Appraisals → New

#### Phase 2: Goal Setting (Employee & Manager)

1. **Employee Sets Goals**
   - Navigate to Performance → My Goals
   - Click "Add Goal"
   - Define KRA/KPI with measurement criteria
   - Set weightage (total should be 100%)
   - Save as draft or submit for approval

2. **Manager Approves Goals**
   - Navigate to Performance → Goal Approvals
   - Review employee goals
   - Approve with comments or reject with reason
   - Employee can revise and resubmit if rejected

#### Phase 3: Self-Assessment (Employee)

1. **Update Goal Progress**
   - Navigate to Performance → My Goals
   - Update achieved values and progress percentage
   - Add comments on achievements/challenges

2. **Submit Self-Assessment**
   - Navigate to Performance → My Appraisals
   - Click on current appraisal
   - Complete self-assessment form
   - Select rating (1-5 scale)
   - Describe key achievements
   - Identify areas for improvement
   - Submit for manager review

#### Phase 4: Manager Review

1. **Review Employee Performance**
   - Navigate to Performance → Team Appraisals
   - Select employee appraisal
   - Review self-assessment and goals

2. **Provide Feedback**
   - Rate employee performance
   - Document strengths
   - Identify development areas
   - Recommend increment percentage
   - Recommend for promotion (if applicable)
   - Submit for HR review

#### Phase 5: 360 Feedback (Optional)

1. **Request Feedback**
   - HR/Manager creates feedback requests
   - Select reviewers (peers, subordinates, customers)
   - Set due dates

2. **Submit Feedback**
   - Reviewers receive notification
   - Navigate to Performance → My Feedback Requests
   - Complete feedback form
   - Rate competencies
   - Provide qualitative feedback
   - Option to submit anonymously

#### Phase 6: HR Review & Normalization

1. **Review Appraisals**
   - Navigate to Performance → All Appraisals
   - Filter by status "Manager Review Submitted"
   - View rating distribution

2. **Normalize Ratings**
   - Apply bell curve normalization if needed
   - Adjust outliers with justification
   - Set final ratings

3. **Finalize Appraisals**
   - Add HR comments
   - Approve increment recommendations
   - Complete appraisal
   - Generate appraisal letters

#### Phase 7: Increment Processing

1. **Create Increment Records**
   - Navigate to Performance → Increments
   - Auto-populate from appraisal recommendations
   - Or manually create

2. **Approval Workflow**
   - HR reviews and approves
   - Finance department processes
   - Update payroll system

#### Phase 8: Individual Development Plan

1. **Create IDP (Employee)**
   - Navigate to Performance → My IDP
   - Define career goals
   - Identify skill gaps
   - Add development activities
   - Submit for manager approval

2. **Approve IDP (Manager)**
   - Review employee's career aspirations
   - Validate development activities
   - Approve with suggestions

3. **Track Progress**
   - Update activity completion
   - Upload certificates
   - Document learning outcomes

---

## 🧪 Testing

### Unit Tests

```python
# Test goal creation
def test_create_performance_goal():
    service = PerformanceManagementService(db, tenant_id, user_id)
    goal_data = PerformanceGoalCreate(
        goal_code="TEST-001",
        goal_title="Test Goal",
        employee_id=employee_id,
        appraisal_cycle_id=cycle_id,
        start_date=date.today(),
        target_date=date.today() + timedelta(days=90)
    )
    goal = service.create_performance_goal(goal_data)
    assert goal.id is not None
    assert goal.status == GoalStatus.DRAFT
```

### Integration Tests

```python
# Test complete appraisal workflow
def test_complete_appraisal_workflow():
    # 1. Create cycle
    cycle = create_appraisal_cycle()
    
    # 2. Create goals
    goals = create_employee_goals(employee_id, cycle.id)
    
    # 3. Submit goals
    submit_goals(employee_id, cycle.id)
    
    # 4. Approve goals
    for goal in goals:
        approve_goal(goal.id)
    
    # 5. Create appraisal
    appraisal = create_employee_appraisal(employee_id, cycle.id)
    
    # 6. Submit self-assessment
    submit_self_assessment(appraisal.id)
    
    # 7. Submit manager review
    submit_manager_review(appraisal.id)
    
    # 8. Submit HR review
    submit_hr_review(appraisal.id)
    
    # 9. Verify completion
    assert appraisal.status == AppraisalStatus.COMPLETED
    assert appraisal.final_rating is not None
```

---

## 💡 Best Practices

### For HR Administrators

1. **Cycle Planning**
   - Create cycles well in advance
   - Communicate timelines clearly
   - Buffer time for each phase

2. **Goal Setting**
   - Provide goal templates
   - Ensure SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
   - Total weightage should equal 100%

3. **Rating Normalization**
   - Use bell curve distribution
   - Document normalization rationale
   - Ensure fairness across departments

4. **Feedback Management**
   - Select diverse reviewers for 360 feedback
   - Send reminders before due dates
   - Ensure anonymity when requested

### For Managers

1. **Goal Approval**
   - Review goals for alignment with team/company objectives
   - Ensure measurable criteria
   - Provide constructive feedback

2. **Performance Review**
   - Be specific with examples
   - Balance positive and constructive feedback
   - Focus on behaviors, not personality
   - Document throughout the year, not just at review time

3. **Increment Recommendations**
   - Base on performance data
   - Consider market benchmarks
   - Be consistent within team

### For Employees

1. **Goal Setting**
   - Align with role expectations
   - Include stretch goals
   - Update progress regularly

2. **Self-Assessment**
   - Be honest and objective
   - Provide evidence for achievements
   - Identify genuine development areas

3. **Individual Development Plan**
   - Set realistic career goals
   - Identify specific skill gaps
   - Track learning actively

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Problem:** Cannot connect to database

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/nbfc_db

# Test connection
psql -U user -d nbfc_db -c "SELECT 1"
```

#### 2. Migration Failures

**Problem:** Tables not created

**Solution:**
```bash
# Check if migration file exists
ls database/migrations/add_performance_management_tables.sql

# Run migration manually
psql -U postgres -d nbfc_db -f database/migrations/add_performance_management_tables.sql

# Verify tables
psql -U postgres -d nbfc_db -c "\dt hrms_*"
```

#### 3. API 404 Errors

**Problem:** Endpoints not found

**Solution:**
```python
# Verify router is registered in main.py
from backend.services.hrms.routes.performance_routes import router as performance_router
app.include_router(performance_router, prefix="/api/v1/hrms/performance")

# Check route list
uvicorn main:app --reload
# Visit http://localhost:8000/docs
```

#### 4. Validation Errors

**Problem:** Pydantic validation fails

**Solution:**
- Check required fields are provided
- Verify data types match schema
- Ensure dates are in correct format (YYYY-MM-DD)
- Check numeric ranges (ratings 1-5, percentages 0-100)

#### 5. Authentication Errors

**Problem:** 401 Unauthorized

**Solution:**
```bash
# Ensure valid JWT token in header
Authorization: Bearer <token>

# Check token expiry
# Refresh token if needed
```

---

## 📚 Additional Resources

### Documentation Files

1. `PERFORMANCE_MANAGEMENT_UI_SPECIFICATION.md` - Complete UI component specifications
2. `add_performance_management_tables.sql` - Database migration script
3. API Documentation - Available at `/docs` when server is running

### Code Files

**Backend:**
- `backend/shared/database/hrms_models.py` - Database models
- `backend/services/hrms/schemas/performance_schemas.py` - Pydantic schemas
- `backend/services/hrms/services/performance_service.py` - Business logic
- `backend/services/hrms/routes/performance_routes.py` - API routes

**Frontend:**
- `frontend/apps/admin-portal/src/types/performance.types.ts` - TypeScript types
- `frontend/apps/admin-portal/src/services/performance.service.ts` - API service
- `frontend/apps/admin-portal/src/pages/performance/*` - UI components

### Related Modules

- HRMS Employee Management
- HRMS Payroll (for increment processing)
- HRMS Training (for IDP integration)
- Notification Service (for alerts and reminders)

---

## 🎉 Conclusion

The HRMS Performance Management System provides a complete, enterprise-grade solution for managing employee performance from goal setting through to increments and career development.

### Key Benefits

- **Comprehensive**: Covers entire performance management lifecycle
- **Flexible**: Configurable cycles, phases, and workflows
- **Fair**: 360-degree feedback and normalization support
- **Transparent**: Complete audit trail and status tracking
- **Integrated**: Links goals → appraisals → increments → development
- **Scalable**: Supports organizations of any size

### Next Steps

1. Run database migrations
2. Configure first appraisal cycle
3. Train HR team and managers
4. Communicate process to employees
5. Monitor adoption and gather feedback
6. Iterate and improve

For support or questions, refer to the project documentation or contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** ✅ Complete and Production-Ready
