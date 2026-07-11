# HRMS Training & Development - Quick Start Guide 🚀

## Overview

This guide will help you quickly get started with the HRMS Training & Development module.

---

## 🎯 Quick Start Steps

### 1. Database Setup

The training models are already registered in `backend/main.py`. On application startup, tables will be created automatically.

**Manual table creation** (if needed):
```bash
# Access the init-db endpoint
POST http://localhost:8000/init-db
```

### 2. Start the Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API Documentation

Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Look for the **"HRMS - Training & Development"** tag to see all 25+ endpoints.

---

## 📝 Basic Usage Examples

### Example 1: Create a Training Course

**Request:**
```http
POST /api/v1/hrms/training/courses
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "course_name": "Python Programming Fundamentals",
  "course_description": "Introduction to Python programming",
  "training_type": "online",
  "training_category": "technical",
  "delivery_mode": "self_paced",
  "duration_hours": 40,
  "duration_days": 5,
  "max_participants": 30,
  "learning_objectives": "Learn Python basics, OOP, and web development",
  "provides_certificate": true,
  "certificate_validity_months": 36,
  "is_published": true
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "course_code": "TRN-202607-0001",
  "course_name": "Python Programming Fundamentals",
  "training_type": "online",
  "duration_hours": 40,
  "is_active": true,
  "created_at": "2026-07-10T10:00:00Z"
}
```

### Example 2: Schedule a Training Session

**Request:**
```http
POST /api/v1/hrms/training/sessions
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "session_name": "Python Fundamentals - July Batch",
  "course_id": "course-uuid-here",
  "start_date": "2026-07-20",
  "end_date": "2026-07-24",
  "start_time": "09:00",
  "end_time": "17:00",
  "location_type": "virtual",
  "virtual_meeting_link": "https://zoom.us/j/123456789",
  "max_participants": 30,
  "status": "scheduled"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "session_code": "SES-202607-0001",
  "session_name": "Python Fundamentals - July Batch",
  "enrolled_count": 0,
  "max_participants": 30,
  "status": "scheduled"
}
```

### Example 3: Nominate Employee for Training

**Request:**
```http
POST /api/v1/hrms/training/participants
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "session_id": "session-uuid-here",
  "employee_id": "employee-uuid-here",
  "nominated_by_id": "manager-uuid-here",
  "nomination_reason": "Skill enhancement for upcoming project",
  "status": "nominated"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "employee_name": "John Doe",
  "employee_code": "EMP-202601-0001",
  "status": "nominated",
  "attended": false,
  "passed": false
}
```

### Example 4: Issue Certificate

**Request:**
```http
POST /api/v1/hrms/training/certifications?employee_id=emp-uuid&course_id=course-uuid&validity_months=36
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "id": "uuid-here",
  "certificate_number": "CERT-2026-000001",
  "certificate_name": "Python Programming Fundamentals",
  "employee_name": "John Doe",
  "course_name": "Python Programming Fundamentals",
  "issue_date": "2026-07-24",
  "expiry_date": "2029-07-24",
  "status": "issued",
  "verification_code": "VER-12345678"
}
```

### Example 5: Add Skill to Employee

**Request:**
```http
POST /api/v1/hrms/training/employee-skills
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "employee_id": "employee-uuid-here",
  "skill_id": "skill-uuid-here",
  "proficiency_level": "intermediate",
  "proficiency_percentage": 65,
  "is_certified": true,
  "certification_name": "Python Programming Fundamentals",
  "years_of_experience": 2
}
```

### Example 6: Get Training Calendar

**Request:**
```http
GET /api/v1/hrms/training/calendar?start_date=2026-07-01&end_date=2026-07-31
Authorization: Bearer <your-token>
```

**Response:**
```json
[
  {
    "id": "uuid-here",
    "session_code": "SES-202607-0001",
    "session_name": "Python Fundamentals - July Batch",
    "course_name": "Python Programming Fundamentals",
    "start_date": "2026-07-20",
    "end_date": "2026-07-24",
    "venue": "Virtual",
    "trainer_name": "Jane Smith",
    "enrolled_count": 25,
    "max_participants": 30,
    "status": "scheduled"
  }
]
```

### Example 7: Get Dashboard Statistics

**Request:**
```http
GET /api/v1/hrms/training/stats
Authorization: Bearer <your-token>
```

**Response:**
```json
{
  "total_courses": 45,
  "active_courses": 38,
  "total_sessions": 120,
  "upcoming_sessions": 15,
  "ongoing_sessions": 3,
  "completed_sessions": 102,
  "total_participants": 850,
  "certifications_issued": 680,
  "average_training_rating": 4.5,
  "compliance_completion_rate": 92.5
}
```

---

## 🔍 Common Queries

### Get All Active Courses
```http
GET /api/v1/hrms/training/courses?is_active=true&is_published=true&page=1&page_size=20
```

### Search Courses
```http
GET /api/v1/hrms/training/courses?search=python&training_category=technical
```

### Get Upcoming Sessions
```http
GET /api/v1/hrms/training/sessions?status=scheduled&start_date_from=2026-07-10
```

### Get Session Participants
```http
GET /api/v1/hrms/training/sessions/{session-id}/participants?status=confirmed
```

### Get Employee Certifications
```http
GET /api/v1/hrms/training/employees/{employee-id}/certifications
```

### Get Employee Skills
```http
GET /api/v1/hrms/training/employees/{employee-id}/skills
```

---

## 🎨 Frontend Integration

### Using TypeScript Types

```typescript
import {
  TrainingCourse,
  TrainingSession,
  TrainingCourseCreate,
  TrainingType,
  TrainingCategory
} from '@/types/training.types';

const newCourse: TrainingCourseCreate = {
  course_name: "Advanced SQL",
  training_type: TrainingType.ONLINE,
  training_category: TrainingCategory.TECHNICAL,
  duration_hours: 20,
  // ... other fields
};
```

### Using Service Functions

```typescript
import {
  createTrainingCourse,
  getTrainingCourses,
  createTrainingSession,
  getTrainingCalendar,
  issueTrainingCertificate,
  getTrainingStats
} from '@/services/training.service';

// Create course
const course = await createTrainingCourse({
  course_name: "Advanced SQL",
  training_type: "online",
  training_category: "technical",
  duration_hours: 20,
  // ...
});

// Get courses with filters
const { items, total, pages } = await getTrainingCourses(1, 20, {
  training_category: "technical",
  is_active: true
});

// Get calendar
const calendar = await getTrainingCalendar("2026-07-01", "2026-07-31");

// Get dashboard stats
const stats = await getTrainingStats();
```

---

## 📊 Filter Options

### Course Filters
- `search` - Search in name, code, description
- `training_type` - Filter by type (classroom, online, etc.)
- `training_category` - Filter by category (technical, soft_skills, etc.)
- `is_active` - Filter active/inactive
- `is_published` - Filter published/draft
- `is_mandatory` - Filter mandatory/optional

### Session Filters
- `course_id` - Filter by course
- `status` - Filter by status (scheduled, in_progress, completed)
- `start_date_from` - Start date range
- `start_date_to` - End date range

### Participant Filters
- `status` - Filter by participant status (nominated, confirmed, attended)

---

## 🔐 Authentication

All endpoints require authentication. Include the JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

The token should contain:
- `tenant_id` - For multi-tenant isolation
- `user_id` - For audit trail

---

## 📈 Response Formats

### Success Response
```json
{
  "id": "uuid",
  "field1": "value1",
  // ... entity fields
  "created_at": "2026-07-10T10:00:00Z"
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [...]
  }
}
```

---

## 🧪 Testing

### Using cURL

```bash
# Create a course
curl -X POST http://localhost:8000/api/v1/hrms/training/courses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "Python Programming",
    "training_type": "online",
    "training_category": "technical",
    "duration_hours": 40
  }'
```

### Using Python Requests

```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your-jwt-token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Create course
course_data = {
    "course_name": "Python Programming",
    "training_type": "online",
    "training_category": "technical",
    "duration_hours": 40
}
response = requests.post(
    f"{API_URL}/hrms/training/courses",
    headers=headers,
    json=course_data
)
print(response.json())
```

---

## 🎯 Next Steps

1. **Test the APIs** using Swagger UI or Postman
2. **Create sample data** for courses, sessions, and skills
3. **Build frontend components** for training management
4. **Integrate with LMS** if you have external learning platforms
5. **Setup notifications** for training reminders
6. **Configure reports** for training analytics

---

## 📚 Related Documentation

- [Complete Implementation Guide](HRMS_TRAINING_DEVELOPMENT_COMPLETE.md)
- [API Reference](http://localhost:8000/docs)
- [HRMS Module Documentation](docs/HRMS_MODULE.md)

---

## 🆘 Troubleshooting

### Issue: Tables not created
**Solution**: Call the `/init-db` endpoint or restart the application

### Issue: Authentication errors
**Solution**: Check JWT token validity and ensure user has proper permissions

### Issue: Foreign key violations
**Solution**: Ensure referenced entities (employees, courses) exist before creating relationships

### Issue: Validation errors
**Solution**: Check required fields and data types in the API documentation

---

## 💡 Tips

1. **Auto-generated codes**: Don't provide codes manually - they're auto-generated
2. **Soft deletes**: Deleted records are not removed, just marked as deleted
3. **Tenant isolation**: All data is automatically filtered by tenant_id
4. **Pagination**: Use page and page_size parameters for large datasets
5. **Relationships**: Use selectinload for eager loading when needed

---

**Version**: 1.0.0  
**Last Updated**: July 10, 2026  
**Status**: Production Ready ✅
