# CRM Customer Service - Quick Start Guide

**Get started with the Customer Service module in 15 minutes!**

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Run Database Migration

```bash
cd backend
alembic upgrade head
```

This creates all 8 required database tables:
- `crm_tickets`
- `crm_ticket_comments`
- `crm_ticket_attachments`
- `crm_ticket_activities`
- `crm_sla_policies`
- `crm_knowledge_base`
- `crm_kb_feedback`
- `crm_ticket_templates`

### Step 2: Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

### Step 3: Start Frontend

```bash
cd frontend/apps/admin-portal
npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## 📝 Quick Walkthrough (10 Minutes)

### 1. Create Your First SLA Policy

**Navigate to:** CRM → Customer Service → SLA Management

**Create a basic policy:**
```json
{
  "policy_name": "Standard Support SLA",
  "first_response_time": 60,      // 1 hour
  "resolution_time": 480,          // 8 hours
  "business_hours_only": true,
  "business_start_hour": 9,
  "business_end_hour": 18,
  "include_weekends": false
}
```

**Click "Create SLA Policy"** and fill in:
- Policy Name: "Standard Support SLA"
- First Response Time: 60 minutes
- Resolution Time: 480 minutes (8 hours)
- Business Hours: 9 AM to 6 PM
- Business Hours Only: Yes
- Include Weekends: No

---

### 2. Create Your First Support Ticket

**Navigate to:** CRM → Customer Service → Tickets

**Click "Create Ticket"** and fill in:

```
Customer ID: 1
Subject: "Unable to access loan account"
Description: "Customer reports they cannot login to view their loan account details. Error message: 'Invalid credentials'"
Category: Technical
Priority: High
Channel: Phone
Tags: login, loan_account
```

**Submit** → Ticket number generated: `TKT-20260712-0001`

---

### 3. Manage the Ticket

**View Ticket Details:**
- Click on the ticket from the list
- See all details, SLA status, and timeline

**Add a Comment:**
```
"Spoke with customer. Password reset initiated. Waiting for customer to check email."
```

**Update Status:**
- Change status to "In Progress"

**Resolve the Ticket:**
```
Resolution: "Password reset completed successfully. Customer confirmed they can now access their loan account."
```

---

### 4. Create a Knowledge Base Article

**Navigate to:** CRM → Customer Service → Knowledge Base

**Click "Create Article"** and fill in:

```
Title: "How to Reset Your Password"
Category: Getting Started
Summary: "Step-by-step guide to reset your account password"
Content:
"""
# Password Reset Instructions

If you've forgotten your password, follow these steps:

1. Go to the login page
2. Click "Forgot Password"
3. Enter your registered email address
4. Check your email for the reset link
5. Click the link and create a new password
6. Your password must:
   - Be at least 8 characters long
   - Include uppercase and lowercase letters
   - Include at least one number
   - Include at least one special character

If you don't receive the email within 5 minutes, check your spam folder or contact support.
"""
Tags: password, login, account
Keywords: password reset, forgot password, login issues
```

**Save as Draft** → **Publish**

---

## 🎯 Common Use Cases

### Use Case 1: Handle Customer Complaint

**Scenario:** Customer complains about unauthorized charges

```python
# Create ticket
POST /api/v1/crm/customer-service/tickets
{
  "customer_id": 123,
  "subject": "Unauthorized charges on account",
  "description": "Customer reports $50 charge they did not authorize",
  "category": "complaint",
  "priority": "urgent",
  "channel": "email"
}

# Assign to fraud team
POST /api/v1/crm/customer-service/tickets/{id}/assign
{
  "assigned_to_team": "Fraud Investigation",
  "notes": "Urgent - potential fraud case"
}

# Add investigation notes
POST /api/v1/crm/customer-service/tickets/{id}/comments
{
  "comment": "Reviewed transaction. Charge appears legitimate. Customer was notified of subscription renewal.",
  "is_internal": true
}

# Resolve
POST /api/v1/crm/customer-service/tickets/{id}/resolve
{
  "resolution": "Charge verified as legitimate subscription renewal. Customer confirmed and understood."
}
```

---

### Use Case 2: Technical Support Ticket

**Scenario:** App crashes on login

```python
# Create ticket
{
  "customer_id": 456,
  "subject": "Mobile app crashes on login",
  "description": "Customer reports app crashes immediately after entering credentials",
  "category": "technical",
  "priority": "high",
  "channel": "mobile_app",
  "tags": ["crash", "login", "mobile"]
}

# Technical team investigates
# Add internal notes
{
  "comment": "Reproduced issue. Found memory leak in authentication module. Fix deployed in v2.1.3",
  "is_internal": true
}

# Notify customer
{
  "comment": "Issue has been resolved in our latest app update. Please update to version 2.1.3 from the app store.",
  "is_internal": false
}

# Resolve with solution
{
  "resolution": "App crash fixed in version 2.1.3. Customer updated app and confirmed issue resolved."
}
```

---

### Use Case 3: Self-Service via Knowledge Base

**Scenario:** Create FAQ article to reduce ticket volume

```python
# Create comprehensive FAQ
{
  "title": "Loan Application FAQs",
  "category": "faq",
  "content": """
## Frequently Asked Questions about Loan Applications

### How long does loan approval take?
Most loans are approved within 24-48 hours of submission.

### What documents do I need?
- Valid ID proof
- Address proof
- Income proof (last 3 months)
- Bank statements (last 6 months)

### Can I track my application?
Yes! Log into your account and go to "My Applications" to see real-time status.

### What is the minimum credit score required?
We typically require a credit score of 650 or higher.

### Can I apply for multiple loans?
You can apply for one loan at a time. Once approved or rejected, you can apply for another.
  """,
  "keywords": ["loan", "application", "faq", "approval", "documents"],
  "is_public": true
}

# Publish article
POST /api/v1/crm/customer-service/knowledge-base/{id}/publish
```

**Result:** Customers can now find answers themselves, reducing support tickets by 40%!

---

## 📊 Monitor Your Performance

### View Dashboard

**Navigate to:** CRM → Customer Service → Dashboard

**Key Metrics to Track:**

1. **SLA Compliance Rate**
   - Target: > 95%
   - Track: Daily

2. **Average First Response Time**
   - Target: < 30 minutes
   - Track: Hourly

3. **Average Resolution Time**
   - Target: < 4 hours
   - Track: Daily

4. **Customer Satisfaction**
   - Target: > 4.5 / 5
   - Track: Weekly

5. **Ticket Volume Trends**
   - Monitor: Daily
   - Act on: Unusual spikes

---

## 🔧 Quick Configuration

### Configure SLA for Different Priorities

**Critical Priority:**
```json
{
  "policy_name": "Critical Priority SLA",
  "applies_to_priority": ["critical"],
  "first_response_time": 15,      // 15 minutes
  "resolution_time": 240,          // 4 hours
  "business_hours_only": false,    // 24/7
  "escalation_enabled": true
}
```

**Low Priority:**
```json
{
  "policy_name": "Low Priority SLA",
  "applies_to_priority": ["low"],
  "first_response_time": 240,     // 4 hours
  "resolution_time": 2880,        // 2 days
  "business_hours_only": true
}
```

---

## 🎓 Best Practices

### 1. Ticket Management
✅ **DO:**
- Assign tickets immediately
- Update status regularly
- Add detailed comments
- Use tags for organization
- Follow up before closing

❌ **DON'T:**
- Leave tickets unassigned
- Skip status updates
- Close without resolution
- Forget to notify customers
- Ignore SLA warnings

### 2. Knowledge Base
✅ **DO:**
- Write clear, concise articles
- Use screenshots and examples
- Keep articles updated
- Organize by category
- Monitor article performance

❌ **DON'T:**
- Create duplicate articles
- Use technical jargon
- Publish without review
- Ignore user feedback
- Leave outdated content

### 3. SLA Management
✅ **DO:**
- Set realistic targets
- Monitor compliance daily
- Review policies quarterly
- Escalate breaches immediately
- Track team performance

❌ **DON'T:**
- Set unrealistic SLAs
- Ignore approaching breaches
- Skip policy reviews
- Blame individuals
- Hide breach data

---

## 🆘 Troubleshooting

### Issue: Tickets not appearing

**Solution:**
```bash
# Check database connection
python -c "from backend.shared.database.connection import get_db; next(get_db())"

# Verify migration
alembic current

# Check tenant_id filter
# Ensure logged-in user has correct tenant_id
```

### Issue: SLA not calculating

**Solution:**
1. Verify SLA policy is active
2. Check policy matches ticket criteria
3. Ensure business hours configured correctly
4. Review server timezone settings

### Issue: Knowledge base search not working

**Solution:**
```python
# Rebuild search index
from backend.crm.services.customer_service import CustomerServiceService
# Re-index all articles
```

---

## 📚 Next Steps

### Day 1: Setup & Configuration
- [x] Run database migration
- [x] Create SLA policies
- [x] Create first ticket
- [x] Create first KB article

### Week 1: Team Onboarding
- [ ] Train support team
- [ ] Configure team assignments
- [ ] Set up notification rules
- [ ] Create ticket templates
- [ ] Build KB library (20+ articles)

### Month 1: Optimization
- [ ] Review SLA compliance
- [ ] Analyze ticket trends
- [ ] Optimize KB content
- [ ] Adjust team workflows
- [ ] Gather user feedback

### Quarter 1: Advanced Features
- [ ] Implement automation rules
- [ ] Create custom reports
- [ ] Integrate with email
- [ ] Set up chatbot
- [ ] Deploy customer portal

---

## 🔗 Quick Links

**Documentation:**
- Full Documentation: `CRM_CUSTOMER_SERVICE_COMPLETE.md`
- API Reference: http://localhost:8000/docs
- User Guide: Knowledge Base → "Getting Started"

**Support:**
- Technical Issues: Create ticket in system
- Feature Requests: Contact product team
- Bug Reports: GitHub issues

**Resources:**
- Training Videos: Coming soon
- Best Practices Guide: Coming soon
- Community Forum: Coming soon

---

## ✅ Quick Checklist

Before going live, ensure:

- [ ] Database migration completed
- [ ] At least one SLA policy created
- [ ] Team members have access
- [ ] Knowledge base has 10+ articles
- [ ] Ticket categories configured
- [ ] Email notifications tested
- [ ] SLA alerts configured
- [ ] Dashboard widgets verified
- [ ] Mobile responsiveness checked
- [ ] Security settings reviewed

---

## 🎉 You're Ready!

Congratulations! You've completed the quick start guide. Your Customer Service module is now ready to handle support tickets efficiently.

**Remember:**
- Start small and grow gradually
- Monitor metrics daily
- Listen to user feedback
- Iterate and improve continuously

**Need Help?**
- Check the full documentation
- Visit the API docs
- Contact support team

---

**Happy Supporting!** 🎊

Last Updated: July 12, 2026
