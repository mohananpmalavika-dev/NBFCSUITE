# CRM Customer Service - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you quickly set up and start using the CRM Customer Service module.

---

## Prerequisites

- Backend server running on `http://localhost:8000`
- Frontend application running on `http://localhost:3000`
- Database migrations completed
- User authenticated in the system

---

## Step 1: Access the Dashboard

1. Open your browser
2. Navigate to: `http://localhost:3000/crm/service-dashboard`
3. You'll see the main service dashboard

---

## Step 2: Configure Your First SLA (2 minutes)

1. Click on **"SLA Config"** button in the dashboard
2. Click **"+ Create SLA"**
3. Fill in the form:
   ```
   Name: Standard Support SLA
   Priority: Leave blank (applies to all)
   First Response Time: 1 hour
   Resolution Time: 8 hours
   Status: Active
   Default SLA: ✓ Check this box
   ```
4. Click **"Create SLA"**

**Done!** All new tickets will now have SLA tracking.

---

## Step 3: Create Your First Ticket (1 minute)

1. From dashboard, click **"+ New Ticket"**
2. Fill in the essential fields:
   ```
   Subject: Test ticket - Login issue
   Description: User cannot login to their account
   Category: Technical
   Priority: High
   Channel: Web
   Contact Email: user@example.com
   ```
3. Click **"Create Ticket"**

**Success!** Your ticket is created with number `TKT-YYYYMMDD-0001`

---

## Step 4: Work on the Ticket (1 minute)

1. You'll be redirected to the ticket detail page
2. Add a comment:
   ```
   Content: "Investigating the login issue now"
   Internal: Leave unchecked (visible to customer)
   ```
3. Click **"Add Comment"**
4. Update status to **"In Progress"** using the dropdown

---

## Step 5: Create a Knowledge Base Article (1 minute)

1. Click browser back or navigate to `/crm/knowledge`
2. Click **"+ Create Article"**
3. Fill in:
   ```
   Title: How to Reset Your Password
   Category: How To
   Content: 
   Step 1: Click "Forgot Password" on login page
   Step 2: Enter your email address
   Step 3: Check your email for reset link
   Step 4: Create new password
   
   Status: Published
   Featured: ✓ Check this box
   ```
4. Click **"Create Article"**

**Great!** Your first help article is live!

---

## Quick Reference

### Common URLs

| Page | URL |
|------|-----|
| Dashboard | `/crm/service-dashboard` |
| Ticket List | `/crm/tickets` |
| Ticket Board | `/crm/tickets/board` |
| Create Ticket | `/crm/tickets/new` |
| Knowledge Base | `/crm/knowledge` |
| SLA Config | `/crm/slas` |

### Ticket Statuses

| Status | Meaning |
|--------|---------|
| New | Just created |
| Open | Acknowledged |
| In Progress | Being worked on |
| Pending Customer | Waiting for customer |
| Resolved | Fixed, awaiting confirmation |
| Closed | Confirmed complete |

### Priority Levels

| Priority | Use When |
|----------|----------|
| Low | Minor issues, can wait |
| Medium | Standard issues |
| High | Important issues affecting work |
| Urgent | Critical issues, immediate attention |
| Critical | System down, blocking operations |

---

## Tips for Success

### 🎯 Best Practices

1. **Always Set SLA First**: Create at least one default SLA before creating tickets
2. **Use Categories**: Properly categorize tickets for better routing and reporting
3. **Add Comments**: Keep communication history in the ticket
4. **Update Status**: Keep ticket status current for accurate metrics
5. **Tag Everything**: Use tags to organize and find tickets quickly
6. **Build Knowledge Base**: Document common solutions to reduce ticket volume

### 🔥 Power User Tips

1. **Keyboard Shortcuts**: Use browser back/forward for quick navigation
2. **Kanban View**: Use `/crm/tickets/board` for visual management
3. **Filters**: Combine multiple filters to find specific tickets
4. **Featured Articles**: Mark frequently accessed articles as featured
5. **Internal Comments**: Use for team communication without customer visibility

### ⚠️ Common Mistakes to Avoid

1. ❌ Creating tickets without SLA configured
2. ❌ Forgetting to update ticket status
3. ❌ Not adding contact information
4. ❌ Publishing articles in draft status
5. ❌ Ignoring SLA breach warnings

---

## Next Steps

### Learn More

- Read the [Complete Implementation Guide](./CRM_CUSTOMER_SERVICE_COMPLETE.md)
- Explore the [API Documentation](http://localhost:8000/docs)
- Review [User Workflows](#user-workflows)

### Advanced Features

Once you're comfortable with basics, explore:
- **Business Hours SLA**: Configure SLAs that only count during work hours
- **Escalation Rules**: Automatically escalate tickets
- **Article Attachments**: Add files to knowledge base articles
- **Customer Satisfaction**: Enable ratings on closed tickets
- **Dashboard Analytics**: Monitor team performance

---

## Troubleshooting

### Issue: Can't create ticket
**Solution**: Check that you're logged in and have proper permissions

### Issue: No SLA on ticket
**Solution**: Create a default SLA configuration first

### Issue: Article not showing
**Solution**: Ensure article status is "Published"

### Issue: Dashboard shows no data
**Solution**: Create some tickets first, then refresh

---

## Quick Commands

### Using the API Client

```typescript
import { customerServiceApi } from '@/services/customerServiceApi'

// Create ticket
const ticket = await customerServiceApi.tickets.create({
  subject: 'Issue title',
  description: 'Details here',
  category: 'technical',
  priority: 'high'
})

// Get statistics
const stats = await customerServiceApi.tickets.getStats()

// Add comment
await customerServiceApi.tickets.addComment(ticketId, {
  content: 'My comment',
  is_internal: false
})
```

---

## Sample Data

### Sample Ticket

```json
{
  "subject": "Cannot access reports",
  "description": "Getting error 403 when trying to access monthly reports",
  "category": "technical",
  "priority": "high",
  "channel": "email",
  "contact_name": "John Doe",
  "contact_email": "john@example.com",
  "tags": ["reports", "access", "403-error"]
}
```

### Sample Article

```json
{
  "title": "How to Export Reports",
  "content": "<h2>Exporting Reports</h2><p>Follow these steps...</p>",
  "category": "how_to",
  "status": "published",
  "tags": ["reports", "export", "data"],
  "is_featured": true
}
```

### Sample SLA

```json
{
  "name": "Critical Priority SLA",
  "priority": "critical",
  "first_response_time": 15,
  "resolution_time": 120,
  "use_business_hours": false,
  "status": "active"
}
```

---

## Visual Guide

### Ticket Lifecycle

```
New → Open → In Progress → Resolved → Closed
           ↓                    ↑
    Pending Customer ←→ Pending Internal
```

### SLA Timeline

```
Ticket Created
    ↓
[First Response Time: 1 hour]
    ↓
First Agent Response
    ↓
[Resolution Time: 8 hours]
    ↓
Ticket Resolved
```

### Priority Color Codes

- 🔵 **Low**: Gray dot
- 🔵 **Medium**: Blue dot
- 🟡 **High**: Yellow dot
- 🟠 **Urgent**: Orange dot
- 🔴 **Critical**: Red dot

---

## Success Metrics to Track

Monitor these KPIs on your dashboard:

1. **First Response Time**: Target < 1 hour
2. **Resolution Time**: Target < 8 hours
3. **SLA Compliance**: Target > 95%
4. **Customer Satisfaction**: Target > 4.0/5
5. **Open Ticket Count**: Keep under control
6. **SLA Breach Rate**: Target < 5%

---

## Getting Help

1. **Check Dashboard**: Most operations start here
2. **Review This Guide**: Common tasks covered above
3. **API Docs**: Visit `/docs` for API reference
4. **Logs**: Check backend logs for errors

---

## Cheat Sheet

### Quick Actions

| Action | Location | Shortcut |
|--------|----------|----------|
| New Ticket | Dashboard or List | "+ Create Ticket" button |
| View Ticket | Click ticket number | Any list view |
| Edit Ticket | Ticket detail | "Edit" button |
| Change Status | Ticket detail | Status dropdown |
| Add Comment | Ticket detail | Comment form at bottom |
| New Article | Knowledge Base | "+ Create Article" button |
| View Stats | Dashboard | Main page |

### Filters

**Ticket Filters**:
- Search (ticket number, subject, contact)
- Status
- Priority
- Category
- SLA Breached (Yes/No)

**Article Filters**:
- Search (title, content)
- Status
- Category
- Featured (Yes/No)

---

## Congratulations! 🎉

You've completed the quick start guide. You now know how to:
- ✅ Set up SLAs
- ✅ Create and manage tickets
- ✅ Use the Kanban board
- ✅ Build knowledge base articles
- ✅ Monitor dashboard metrics

Start managing support tickets like a pro!

---

**Need More Help?** Check the [Complete Implementation Guide](./CRM_CUSTOMER_SERVICE_COMPLETE.md) for advanced features and detailed documentation.
