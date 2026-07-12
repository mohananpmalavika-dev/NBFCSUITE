# CRM Customer Service Module - Complete Implementation Guide

## Overview

The CRM Customer Service module provides a comprehensive support ticket management system with knowledge base and SLA tracking capabilities. This implementation includes full backend services, frontend UI components, and routing infrastructure.

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: December 2024

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Backend Implementation](#backend-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [API Reference](#api-reference)
6. [User Guide](#user-guide)
7. [Configuration](#configuration)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## Features

### ✅ Ticket Management
- **Create, Read, Update, Delete** tickets
- **Auto-numbering**: TKT-YYYYMMDD-XXXX format
- **Multi-channel support**: Email, Phone, Web, Chat, Social Media, Walk-in
- **Priority levels**: Low, Medium, High, Urgent, Critical
- **Status workflow**: New → Open → In Progress → Pending → Resolved → Closed
- **Categories**: Technical, Billing, Account, Product, Complaint, Feature Request, General
- **Comment threading** with internal/external visibility
- **File attachments** support
- **SLA tracking** with breach detection
- **Assignment** to users and teams
- **Tags** for organization
- **Customer satisfaction** ratings
- **Kanban board** view for visual management

### ✅ Knowledge Base
- **Article management** with version control
- **Auto-numbering**: KB-XXXXXX format
- **Categories**: FAQ, How To, Troubleshooting, Policy, Announcement, Guide
- **Rich content** with HTML/Markdown support
- **Search functionality** with full-text search
- **View tracking** for analytics
- **User feedback** (helpful/not helpful)
- **Featured articles** for prominence
- **Tags and keywords** for SEO
- **Related articles** linking
- **File attachments**

### ✅ SLA Management
- **Configurable SLAs** by priority and category
- **Response time** targets
- **Resolution time** targets
- **Business hours** calculation
- **Automatic escalation**
- **Breach detection** and alerts
- **Performance metrics** and compliance tracking

### ✅ Service Dashboard
- **Real-time statistics**
- **Ticket distribution** charts
- **Performance metrics**
- **SLA compliance** tracking
- **Customer satisfaction** metrics
- **Quick actions** for common tasks

---

## Architecture

### Technology Stack

**Backend**:
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL database
- Pydantic for validation

**Frontend**:
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS

### Database Models

**Ticket** (`crm_ticket`):
- Core ticket information
- Status, priority, category tracking
- Contact and assignment details
- SLA timestamps
- Soft delete support

**TicketComment** (`crm_ticket_comment`):
- Comment threading
- Internal/external visibility
- System-generated comments

**TicketAttachment** (`crm_ticket_attachment`):
- File storage references
- MIME type tracking

**KnowledgeArticle** (`crm_knowledge_article`):
- Article content with versioning
- SEO metadata
- View and feedback tracking

**SLA** (`crm_sla`):
- SLA configuration
- Business hours setup
- Escalation rules

**SLAViolation** (`crm_sla_violation`):
- Breach tracking
- Violation details

---

## Backend Implementation

### File Structure

```
backend/
├── shared/
│   ├── database/
│   │   └── crm_service_models.py       # 7 database models
│   └── schemas/
│       └── crm_service_schemas.py      # Request/response schemas
└── crm/
    ├── services/
    │   └── service_service.py          # Business logic (3 services)
    └── routes/
        └── service_routes.py           # 21 API endpoints
```

### Models Created

1. **Ticket**: Main ticket entity with SLA tracking
2. **TicketComment**: Threaded comments with visibility control
3. **TicketAttachment**: File attachment references
4. **KnowledgeArticle**: Help articles with versioning
5. **ArticleAttachment**: Article file attachments
6. **SLA**: Service level agreement configurations
7. **SLAViolation**: SLA breach tracking

### Services Implemented

#### TicketService
- `create_ticket()`: Create new ticket with auto-numbering and SLA assignment
- `get_ticket()`: Retrieve ticket with related data
- `update_ticket()`: Update ticket and track SLA milestones
- `list_tickets()`: Paginated list with filtering
- `add_comment()`: Add comment to ticket
- `add_attachment()`: Attach file to ticket
- `get_ticket_stats()`: Calculate statistics

#### KnowledgeBaseService
- `create_article()`: Create article with auto-numbering
- `get_article()`: Retrieve article (with optional view increment)
- `update_article()`: Update article and increment version
- `list_articles()`: Paginated list with search
- `search_articles()`: Full-text search
- `record_feedback()`: Track helpful/not helpful votes

#### SLAService
- `create_sla()`: Create SLA configuration
- `get_sla()`: Retrieve SLA
- `list_slas()`: List all SLAs
- `calculate_due_dates()`: Calculate SLA deadlines
- `check_sla_breach()`: Detect violations
- `get_violations()`: List breaches

### API Endpoints

**Tickets** (8 endpoints):
- `POST /tickets` - Create ticket
- `GET /tickets` - List tickets with filters
- `GET /tickets/{id}` - Get ticket details
- `PUT /tickets/{id}` - Update ticket
- `DELETE /tickets/{id}` - Delete ticket
- `POST /tickets/{id}/comments` - Add comment
- `POST /tickets/{id}/attachments` - Add attachment
- `GET /tickets/stats/overview` - Get statistics

**Knowledge Base** (7 endpoints):
- `POST /knowledge/articles` - Create article
- `GET /knowledge/articles` - List articles
- `GET /knowledge/articles/{id}` - Get article
- `GET /knowledge/articles/slug/{slug}` - Get by slug
- `PUT /knowledge/articles/{id}` - Update article
- `DELETE /knowledge/articles/{id}` - Delete article
- `POST /knowledge/articles/{id}/feedback` - Record feedback

**SLA** (6 endpoints):
- `POST /slas` - Create SLA
- `GET /slas` - List SLAs
- `GET /slas/{id}` - Get SLA
- `PUT /slas/{id}` - Update SLA
- `DELETE /slas/{id}` - Delete SLA
- `GET /slas/violations/list` - List violations

---

## Frontend Implementation

### File Structure

```
frontend/apps/admin-portal/src/
├── services/
│   └── customerServiceApi.ts           # API client with types
├── components/crm/
│   ├── TicketList.tsx                  # Ticket list with filters
│   ├── TicketDetail.tsx                # Full ticket view
│   ├── TicketForm.tsx                  # Create/edit ticket
│   ├── TicketBoard.tsx                 # Kanban board view
│   ├── ArticleList.tsx                 # Knowledge base grid
│   ├── ArticleDetail.tsx               # Article reader
│   ├── ArticleForm.tsx                 # Article editor
│   ├── SLAList.tsx                     # SLA configurations
│   ├── SLAForm.tsx                     # SLA editor
│   └── ServiceDashboard.tsx            # Main dashboard
└── app/crm/
    ├── tickets/
    │   ├── page.tsx                    # List view
    │   ├── board/page.tsx              # Board view
    │   ├── new/page.tsx                # Create form
    │   ├── [id]/page.tsx               # Detail view
    │   └── [id]/edit/page.tsx          # Edit form
    ├── knowledge/
    │   ├── page.tsx                    # Article list
    │   ├── new/page.tsx                # Create article
    │   ├── [slug]/page.tsx             # Article view
    │   └── [id]/edit/page.tsx          # Edit article
    ├── slas/
    │   ├── page.tsx                    # SLA list
    │   ├── new/page.tsx                # Create SLA
    │   └── [id]/edit/page.tsx          # Edit SLA
    └── service-dashboard/
        └── page.tsx                    # Dashboard
```

### Components Overview

#### Ticket Components

**TicketList**:
- Paginated ticket table
- Filters: status, priority, category, SLA, search
- Quick actions: view, edit
- SLA breach indicators

**TicketDetail**:
- Full ticket information
- Comment thread with add functionality
- Status update widget
- SLA tracking display
- Contact information
- Timestamps and audit trail

**TicketForm**:
- Create/edit ticket form
- Validation with required fields
- Dynamic tag management
- Account selection
- Assignment controls

**TicketBoard**:
- Kanban-style board
- Columns by status: New, Open, In Progress, Pending, Resolved
- Drag-to-update (via dropdown)
- Priority indicators
- Quick status changes

#### Knowledge Base Components

**ArticleList**:
- Grid view with cards
- Filters: status, category, featured, search
- View counts and feedback stats
- Featured article indicators

**ArticleDetail**:
- Full article rendering
- View tracking
- Feedback buttons (helpful/not helpful)
- Attachment downloads
- Version information

**ArticleForm**:
- Rich text editor (HTML/Markdown)
- Auto-slug generation
- Tag and keyword management
- Category and status selection
- Featured article toggle

#### SLA Components

**SLAList**:
- Table view of configurations
- Shows priority, response/resolution times
- Active/inactive status
- Default SLA indicator

**SLAForm**:
- Response and resolution time inputs
- Business hours configuration
- Day of week selection
- Escalation setup
- Priority/category filters

#### Dashboard

**ServiceDashboard**:
- 8 stat cards: Total, New, Open, In Progress, Pending, Resolved, Closed, SLA Breached
- Performance metrics: Avg response time, resolution time, satisfaction
- Status distribution charts
- SLA compliance rate
- Quick action buttons

---

## API Reference

### TypeScript Types

```typescript
// Ticket Types
type TicketPriority = 'low' | 'medium' | 'high' | 'urgent' | 'critical'
type TicketStatus = 'new' | 'open' | 'in_progress' | 'pending_customer' | 
                    'pending_internal' | 'resolved' | 'closed' | 'cancelled'
type TicketCategory = 'technical' | 'billing' | 'account' | 'product' | 
                      'complaint' | 'feature_request' | 'general' | 'other'
type TicketChannel = 'email' | 'phone' | 'web' | 'chat' | 'social_media' | 'walk_in'

// Article Types
type ArticleStatus = 'draft' | 'published' | 'archived' | 'under_review'
type ArticleCategory = 'faq' | 'how_to' | 'troubleshooting' | 'policy' | 
                       'announcement' | 'guide'

// SLA Types
type SLAStatus = 'active' | 'inactive'
```

### API Client Usage

```typescript
import { customerServiceApi } from '@/services/customerServiceApi'

// Create ticket
const ticket = await customerServiceApi.tickets.create({
  subject: 'Login issue',
  description: 'Cannot login to account',
  category: 'technical',
  priority: 'high',
  contact_email: 'user@example.com'
})

// List tickets with filters
const tickets = await customerServiceApi.tickets.list({
  status: 'open',
  priority: 'urgent',
  limit: 20
})

// Add comment
await customerServiceApi.tickets.addComment(ticketId, {
  content: 'Working on this issue',
  is_internal: false
})

// Create article
const article = await customerServiceApi.knowledge.create({
  title: 'How to reset password',
  content: '<p>Step 1: Click forgot password...</p>',
  category: 'how_to',
  status: 'published'
})

// Get stats
const stats = await customerServiceApi.tickets.getStats()
```

---

## User Guide

### Getting Started

1. **Access the Service Dashboard**:
   - Navigate to `/crm/service-dashboard`
   - View overview of all support operations

2. **Create Your First Ticket**:
   - Click "+ Create Ticket" button
   - Fill in required fields (subject, description, category)
   - Select priority and channel
   - Assign to team member (optional)
   - Click "Create Ticket"

3. **Set Up SLAs**:
   - Navigate to `/crm/slas`
   - Click "+ Create SLA"
   - Define response and resolution times
   - Configure business hours if needed
   - Set as default if applicable

4. **Build Knowledge Base**:
   - Navigate to `/crm/knowledge`
   - Click "+ Create Article"
   - Write helpful content
   - Add tags for discoverability
   - Publish when ready

### Ticket Management Workflows

#### Creating a Ticket

1. Click "+ Create Ticket" from any ticket view
2. Enter ticket details:
   - **Subject**: Brief description
   - **Description**: Detailed information
   - **Category**: Type of issue
   - **Priority**: Urgency level
   - **Channel**: How ticket was received
3. Add contact information (optional but recommended)
4. Link to customer account (if applicable)
5. Assign to agent or team
6. Add tags for organization
7. Submit

#### Working a Ticket

1. Open ticket from list or board view
2. Review ticket details and history
3. Add comments:
   - External: Visible to customer
   - Internal: Only visible to team
4. Update status as work progresses:
   - **Open**: Acknowledged
   - **In Progress**: Actively working
   - **Pending Customer**: Waiting for customer response
   - **Resolved**: Issue fixed, awaiting confirmation
   - **Closed**: Confirmed resolved
5. Monitor SLA countdown
6. Attach files if needed

#### Using the Kanban Board

1. Navigate to `/crm/tickets/board`
2. View tickets organized by status
3. Use dropdown to change ticket status
4. Click ticket card to view details
5. Monitor priority with color indicators:
   - Gray: Low
   - Blue: Medium
   - Yellow: High
   - Orange: Urgent
   - Red: Critical

### Knowledge Base Management

#### Creating Articles

1. Navigate to `/crm/knowledge`
2. Click "+ Create Article"
3. Enter title (slug auto-generates)
4. Write content in HTML or Markdown
5. Add excerpt for previews
6. Select category and status
7. Add tags and keywords for SEO
8. Toggle "Featured" if important
9. Save as draft or publish

#### Organizing Articles

- **Categories**: Group by type (FAQ, How To, etc.)
- **Tags**: Cross-cutting topics
- **Keywords**: SEO optimization
- **Featured**: Highlight important articles
- **Display Order**: Control sorting

#### Tracking Performance

- **View Count**: See how many times article was read
- **Helpful Votes**: Customer feedback
- **Not Helpful Votes**: Identify improvement needs

### SLA Configuration

#### Creating an SLA

1. Navigate to `/crm/slas`
2. Click "+ Create SLA"
3. Name the SLA (e.g., "Critical Priority SLA")
4. Set filters:
   - Priority: Which priorities this applies to
   - Category: Which categories this applies to
   - Leave blank for "all"
5. Define times (in hours):
   - **First Response**: Time to first agent reply
   - **Resolution**: Time to close ticket
6. Configure business hours (optional):
   - Enable if SLA only counts during work hours
   - Set start/end times
   - Select business days
7. Set up escalation (optional):
   - Enable automatic escalation
   - Set escalation time
   - Specify escalation recipient
8. Mark as default if needed
9. Save

#### SLA Matching Logic

1. System checks for matching SLA based on ticket priority and category
2. If multiple matches, uses most specific
3. If no match, uses default SLA
4. Calculates due dates based on configuration
5. Monitors in real-time for breaches

### Dashboard Usage

#### Understanding Metrics

**Ticket Counts**:
- **Total**: All active tickets
- **New**: Just created, not yet acknowledged
- **Open**: Acknowledged, waiting to start
- **In Progress**: Actively being worked
- **Pending**: Waiting on customer or internal
- **Resolved**: Fixed, awaiting confirmation
- **Closed**: Confirmed complete
- **SLA Breached**: Missed deadline

**Performance Metrics**:
- **Avg First Response**: How quickly team responds
- **Avg Resolution Time**: How quickly issues are resolved
- **Customer Satisfaction**: Average rating (out of 5)

**SLA Compliance**:
- Shows percentage of tickets meeting SLA
- Highlights breached tickets needing attention

#### Quick Actions

Dashboard provides one-click access to:
- Create new ticket
- View all tickets
- Open Kanban board
- Access knowledge base
- Manage SLA configurations

---

## Configuration

### Environment Variables

Add to `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nbfcsuite

# Tenant (for multi-tenancy)
DEFAULT_TENANT=default

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=/uploads/support
```

### Backend Configuration

In `backend/main.py`, ensure routes are registered:

```python
from backend.crm.routes.service_routes import router as service_router

app.include_router(service_router, prefix="/api/crm", tags=["Customer Service"])
```

### Frontend Configuration

API client is configured in `services/customerServiceApi.ts` and uses the shared `apiClient` which handles:
- Base URL configuration
- Authentication tokens
- Error handling
- Response formatting

---

## Deployment

### Database Migration

1. Backend models are already defined in `crm_service_models.py`
2. Models are imported in `backend/main.py`
3. Run Alembic migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add customer service tables"
   alembic upgrade head
   ```

### Backend Deployment

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Start FastAPI server:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Deployment

1. Build Next.js application:
   ```bash
   cd frontend/apps/admin-portal
   npm run build
   ```

2. Start production server:
   ```bash
   npm start
   ```

### Health Checks

Test endpoints:
- Backend: `http://localhost:8000/docs` (Swagger UI)
- Frontend: `http://localhost:3000/crm/service-dashboard`

---

## Troubleshooting

### Common Issues

#### Tickets Not Saving

**Symptom**: Error when creating ticket  
**Cause**: Missing required fields or database connection  
**Solution**:
1. Check all required fields are provided
2. Verify database connection
3. Check backend logs for specific error
4. Ensure models are migrated

#### SLA Not Calculating

**Symptom**: No due dates on tickets  
**Cause**: No matching or default SLA configured  
**Solution**:
1. Create at least one SLA configuration
2. Mark one SLA as "default"
3. Verify SLA is active
4. Check priority/category filters

#### Knowledge Base Articles Not Showing

**Symptom**: Articles created but not visible  
**Cause**: Status is "draft" or "archived"  
**Solution**:
1. Ensure article status is "published"
2. Check category filters
3. Verify search terms

#### Comments Not Appearing

**Symptom**: Added comment doesn't show  
**Cause**: Page needs refresh or API error  
**Solution**:
1. Refresh the page
2. Check if comment was actually saved (check backend)
3. Verify ticket ID is correct

### Performance Optimization

**For Large Ticket Volumes**:
- Use database indexes on frequently filtered fields
- Implement caching for dashboard stats
- Paginate all list views
- Archive old closed tickets

**For Knowledge Base**:
- Implement full-text search indexes
- Cache popular articles
- Optimize image attachments
- Use CDN for static content

---

## API Response Examples

### Create Ticket Response

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ticket_number": "TKT-20241215-0001",
    "subject": "Login issue",
    "status": "new",
    "priority": "high",
    "category": "technical",
    "sla_breached": false,
    "first_response_due": "2024-12-15T11:00:00Z",
    "resolution_due": "2024-12-15T18:00:00Z",
    "created_at": "2024-12-15T09:00:00Z"
  }
}
```

### Ticket Statistics Response

```json
{
  "success": true,
  "data": {
    "total_tickets": 1247,
    "new_tickets": 45,
    "open_tickets": 89,
    "in_progress_tickets": 156,
    "pending_tickets": 67,
    "resolved_tickets": 234,
    "closed_tickets": 656,
    "sla_breached_tickets": 12,
    "avg_first_response_time": 45.5,
    "avg_resolution_time": 180.3,
    "avg_satisfaction_rating": 4.2
  }
}
```

---

## Security Considerations

1. **Authentication**: All API endpoints require authentication
2. **Authorization**: Check user permissions before operations
3. **Data Validation**: All inputs validated via Pydantic schemas
4. **SQL Injection**: Protected via SQLAlchemy ORM
5. **XSS Protection**: Sanitize HTML content in articles
6. **File Upload**: Validate file types and sizes
7. **Sensitive Data**: Internal comments not exposed to customers
8. **Audit Trail**: Track who created/modified records

---

## Future Enhancements

- [ ] Email integration for ticket creation
- [ ] SMS notifications for SLA breaches
- [ ] Advanced reporting and analytics
- [ ] Customer portal for self-service
- [ ] AI-powered article suggestions
- [ ] Automated ticket routing
- [ ] Multi-language support
- [ ] Integration with external tools (Slack, Jira)
- [ ] Mobile application
- [ ] Voice ticket creation

---

## Support

For questions or issues:
1. Check this documentation
2. Review API documentation at `/docs`
3. Check application logs
4. Contact development team

---

## Changelog

### Version 1.0.0 (December 2024)
- ✅ Complete backend implementation (7 models, 3 services, 21 endpoints)
- ✅ Complete frontend implementation (10 components, 13 pages)
- ✅ Ticket management with SLA tracking
- ✅ Knowledge base with feedback
- ✅ Service dashboard with metrics
- ✅ Kanban board view
- ✅ Comprehensive documentation

---

**End of Implementation Guide**
