# Collection Management System - Quick Start Guide

## 🚀 Getting Started

This guide will help you set up and use the Collection Management System for your NBFC/Nidhi operations.

---

## 📋 Prerequisites

### System Requirements
- ✅ Backend service layer (already implemented)
- ⏳ API routers (needs to be created)
- ⏳ Database migration (needs to be run)
- ✅ Frontend pages (already implemented)

### User Roles Required
- **Collection Manager**: Full access to all collection features
- **Field Agent**: Mobile access for visits and collections
- **Legal Team**: Access to legal notices and cases
- **Approver**: Settlement proposal approvals

---

## 📦 Module Overview

The Collection Management System consists of 6 major modules:

### 1. Collection Strategies 💡
**Purpose**: Automate collection workflows based on DPD buckets

**Key Features**:
- DPD-based targeting (0-30, 31-60, 61-90, 91+)
- Multi-action workflows (SMS, Email, Call, Field Visit)
- Auto-assignment to field agents
- Priority-based execution
- Template integration

**Use Cases**:
- Early stage reminders (0-30 DPD)
- Follow-up calls (31-60 DPD)
- Field visits (61-90 DPD)
- Legal notices (90+ DPD)

### 2. Field Agent Management 👤
**Purpose**: Manage field agents and territory assignments

**Key Features**:
- Agent profiles with territories
- Pincode-based assignment
- Case allocation tracking
- Visit management
- Performance analytics

**Use Cases**:
- Assign agents to territories
- Allocate cases to agents
- Track field visits
- Monitor performance

### 3. Payment Promise Tracking 🤝
**Purpose**: Record and track payment commitments

**Key Features**:
- Promise creation (full/partial/installment)
- Due date tracking with alerts
- Fulfillment workflow
- Broken promise tracking
- Automated reminders

**Use Cases**:
- Record customer promises
- Send payment reminders
- Track fulfillment rates
- Identify serial defaulters

### 4. Legal & Recovery ⚖️
**Purpose**: Manage legal proceedings and recovery actions

**Key Features**:
- Legal notice generation (6 types)
- Delivery tracking
- Case management
- Hearing schedules
- Document management
- Recovery tracking

**Use Cases**:
- Send demand notices
- File legal cases
- Track court hearings
- Monitor recovery amounts

### 5. Settlement/OTS 💰
**Purpose**: One-Time Settlement proposals with approval workflow

**Key Features**:
- Proposal creation
- Outstanding breakdown
- Waiver calculation
- NPV analysis
- Multi-level approval
- Payment tracking

**Use Cases**:
- Create settlement offers
- Calculate NPV benefit
- Approval workflow
- Track settlements

### 6. Communication Templates 📧
**Purpose**: Reusable templates for all communications

**Key Features**:
- Multiple template types
- Variable system
- Active/inactive management
- Usage tracking

**Use Cases**:
- SMS reminders
- Email notifications
- Legal notices
- Call scripts

---

## 🎯 Quick Start Workflows

### Workflow 1: Setting Up Collection Automation

**Step 1: Create Communication Templates**
1. Navigate to `/collections/templates`
2. Click "+ New Template"
3. Select template type (SMS/Email/Legal Notice)
4. Add content with variables: `{customer_name}`, `{due_amount}`, etc.
5. Save and activate

**Step 2: Create Collection Strategy**
1. Navigate to `/collections/strategies`
2. Click "+ New Strategy"
3. Configure:
   - Name: "Early Stage Personal Loan"
   - DPD Range: 0-30 days
   - Product: Personal Loan
   - Priority: 5
4. Add actions:
   - Day 1: Send SMS (select template)
   - Day 5: Send Email (select template)
   - Day 15: Schedule Call
   - Day 25: Schedule Field Visit
5. Enable auto-assignment
6. Save strategy

**Step 3: Execute Strategy**
1. Go to strategy detail page
2. Click "Execute Strategy"
3. System will:
   - Find eligible loans (matching DPD and product)
   - Execute actions based on trigger days
   - Auto-assign field visits to agents
   - Track execution status

### Workflow 2: Field Agent Operations

**Step 1: Setup Field Agent**
1. Navigate to `/collections/field-agents`
2. Click "+ Add Field Agent"
3. Enter details:
   - Name, Employee ID, Mobile
   - Max cases (e.g., 50)
   - Status: Active
4. Assign territories:
   - Add territory name
   - Add pincodes (e.g., 110001, 110002)
   - Mark as active
5. Save agent

**Step 2: Assign Cases**
1. Go to agent detail page
2. Click "Assign Cases"
3. Select loans from list
4. Confirm assignment

**Step 3: Record Field Visit**
1. Agent visits customer location
2. Navigate to `/collections/field-agents/visits`
3. Click "Record Visit"
4. Fill details:
   - Loan account
   - Visit date and time
   - Disposition (Customer Met, Payment Collected, etc.)
   - Amount collected (if any)
   - Next action
5. Save visit

**Step 4: View Performance**
1. Go to agent detail page
2. View metrics:
   - Total collections
   - Visit completion rate
   - Success rate
   - Target achievement

### Workflow 3: Payment Promise Management

**Step 1: Record Promise**
1. Customer commits to payment
2. Navigate to `/collections/promises`
3. Click "Record New Promise"
4. Enter:
   - Loan account
   - Promise amount
   - Promise date
   - Promise type (full/partial)
   - Channel (call/visit/email)
   - Notes
5. Save promise

**Step 2: Track Due Promises**
1. View promises list
2. Filter by status: Pending
3. System shows:
   - 🟢 Green: 3+ days until due
   - 🟡 Yellow: Due in 1-3 days
   - 🔴 Red: Overdue

**Step 3: Send Reminders**
1. Select pending promises
2. Click "Send Reminder"
3. Choose channel (SMS/Email/Call)
4. Confirm send

**Step 4: Mark Fulfillment**
When payment received:
1. Go to promise detail page
2. Click "Mark as Fulfilled"
3. Enter:
   - Amount received
   - Payment date
   - Payment mode
   - Reference number
4. Save

### Workflow 4: Legal Action Process

**Step 1: Generate Legal Notice**
1. Navigate to `/collections/legal`
2. Click "Create Legal Notice"
3. Select notice type:
   - Demand Notice
   - Legal Notice (Sec 138)
   - Arbitration Notice
   - Possession Notice
4. Fill details:
   - Loan account
   - Outstanding amount
   - Customer details
   - Response deadline
5. Use template or custom content
6. Save notice

**Step 2: Send Notice**
1. Go to notice detail page
2. Click "Send Notice"
3. Select delivery mode:
   - Registered Post
   - Courier
   - Email
   - Hand Delivery
4. Enter tracking details
5. Confirm send

**Step 3: Track Response**
1. Monitor delivery status
2. When response received:
   - Go to notice detail
   - Click "Record Response"
   - Enter response date and details
   - Save

**Step 4: File Legal Case** (if needed)
1. From notice page, click "Create Legal Case"
2. Fill case details:
   - Case type (Civil/Criminal/DRT/SARFAESI)
   - Court name and location
   - Filing date
   - Claim amount
   - Advocate details
3. Upload documents
4. Save case

**Step 5: Manage Hearings**
1. Go to case detail page
2. Click "Add Hearing"
3. Enter:
   - Hearing date
   - Purpose
   - Outcome
   - Next hearing date
4. Save hearing record

### Workflow 5: Settlement (OTS) Process

**Step 1: Create Settlement Proposal**
1. Navigate to `/collections/settlement`
2. Click "+ New Settlement Proposal"
3. Enter loan details:
   - Loan account
   - Customer name and contact
4. Enter outstanding breakdown:
   - Principal: ₹5,00,000
   - Interest: ₹1,50,000
   - Penalty: ₹50,000
   - Total: ₹7,00,000
5. Enter settlement terms:
   - Settlement amount: ₹5,50,000
   - Payment terms: Lumpsum
   - Valid until: 30 days
6. Calculate NPV (optional):
   - Est. recovery time: 12 months
   - Est. recovery amount: ₹6,00,000
   - Discount rate: 12%
   - Click "Calculate NPV"
   - System shows NPV benefit
7. Add justification:
   - Reason for settlement
   - Detailed business justification
   - Internal notes
8. Submit for approval

**Step 2: Review and Approve**
1. Approver receives notification
2. Go to `/collections/settlement`
3. Click on pending proposal
4. Review:
   - Outstanding breakdown
   - Settlement terms
   - Waiver amount (₹1,50,000 = 21.4%)
   - NPV analysis
   - Justification
5. Decision:
   - **Approve**: Add approval notes, click "Approve"
   - **Reject**: Add rejection reason, click "Reject"

**Step 3: Record Payment**
1. When payment received:
   - Go to approved proposal
   - Click "Record Payment"
   - Enter payment details
   - Mark as completed

---

## 📊 Reports and Analytics

### Dashboard Metrics
Navigate to `/collections` to view:

**Collection Performance**
- Total portfolio at risk
- DPD bucket distribution
- Collection efficiency ratio
- Recovery rate

**Field Agent Performance**
- Active agents
- Total cases assigned
- Visit completion rate
- Collection amount

**Promise Analytics**
- Total promises
- Fulfillment rate
- Broken promise rate
- Average promise amount

**Legal Status**
- Active legal notices
- Filed cases
- Cases with hearings
- Recovery amount

**Settlement Performance**
- Proposals pending approval
- Approved settlements
- Waiver percentage
- NPV benefit

### Custom Reports
Generate custom reports:
1. Navigate to module (e.g., Field Agents)
2. Click "Reports"
3. Select report type
4. Choose date range and filters
5. Export as CSV/Excel/PDF

---

## 🎨 User Interface Guide

### Navigation Structure
```
Collections (Main Menu)
├── Dashboard
├── Strategies
│   ├── List
│   └── Create
├── Field Agents
│   ├── List
│   └── Agent Detail
├── Promises
│   ├── List
│   └── Promise Detail
├── Legal & Recovery
│   ├── Notices (Tab)
│   └── Cases (Tab)
├── Settlement/OTS
│   ├── List
│   ├── Create
│   └── Approve
└── Templates
    ├── Library
    └── Create
```

### Color Coding System

**Status Colors**:
- 🟢 Green: Active, Fulfilled, Completed, Success
- 🟡 Yellow: Pending, Due Soon, In Progress
- 🔴 Red: Overdue, Broken, Rejected, Failed
- 🔵 Blue: Sent, Scheduled
- 🟣 Purple: Approved, Settled
- ⚫ Gray: Inactive, Draft, Cancelled

**DPD Buckets**:
- 🟢 0-30 DPD: Early stage (green)
- 🟡 31-60 DPD: Follow-up (yellow)
- 🟠 61-90 DPD: Serious (orange)
- 🔴 91-180 DPD: NPA (red)
- ⚫ 181+ DPD: Write-off (dark red)

### Common UI Patterns

**List Pages**:
- Filters at top
- Stats cards below filters
- Table/grid of items
- Actions on right

**Detail Pages**:
- Header with title and status
- Quick actions on right
- Main content in center
- Sidebar with additional info

**Forms**:
- Sections with headers
- Required fields marked with *
- Inline validation
- Save/Submit buttons at bottom

---

## 🔧 Configuration

### System Settings

**Collection Parameters**:
```
DPD Calculation: Days Past Due from EMI date
Early DPD Threshold: 30 days
NPA Threshold: 90 days
Write-off Threshold: 180 days
```

**Field Agent Limits**:
```
Max Cases Per Agent: 50
Max Daily Visits: 10
Territory Overlap: Not allowed
Case Reallocation: After 30 days inactive
```

**Promise Settings**:
```
Reminder Days Before Due: 3, 1
Overdue Grace Period: 2 days
Auto-break After Days: 7
```

**Legal Notice Settings**:
```
Default Response Deadline: 15 days
Auto-escalate to Case: After 30 days no response
Required Documents: Loan agreement, notices
```

**Settlement Rules**:
```
Min Settlement %: 60% of outstanding
Max Waiver %: 40% of outstanding
Approval Levels: 
  - <₹1L: Manager
  - ₹1L-₹5L: Senior Manager
  - >₹5L: VP/Director
NPV Discount Rate: 12%
```

---

## 🔐 Permissions and Roles

### Collection Manager
**Access**: Full access to all modules
**Capabilities**:
- Create/edit strategies
- Manage field agents
- View all promises
- Access legal module
- Approve settlements (based on amount)
- Manage templates

### Field Agent
**Access**: Mobile app + agent-specific data
**Capabilities**:
- View assigned cases
- Record visits
- Record promises
- Collect payments
- Update case status
- View performance

### Legal Team
**Access**: Legal module only
**Capabilities**:
- Create legal notices
- File cases
- Manage hearings
- Track responses
- Upload documents
- Record recovery

### Approver (Settlement)
**Access**: Settlement module
**Capabilities**:
- View proposals
- Approve/reject
- Add notes
- View analytics

### Viewer (Reports)
**Access**: Read-only all modules
**Capabilities**:
- View dashboards
- Generate reports
- Export data
- No create/edit

---

## 📱 Mobile App (Field Agent)

### Features
- Today's visit schedule
- Case details with map
- Payment collection form
- Visit disposition
- Offline support
- GPS tracking

### Usage
1. Login with agent credentials
2. View today's schedule
3. Navigate to customer location
4. Record visit outcome
5. Collect payment (if applicable)
6. Sync data when online

---

## 🔔 Notifications and Alerts

### Automated Notifications

**For Collection Managers**:
- Daily summary report (email)
- High DPD alerts (>90 days)
- Promise due/overdue alerts
- Settlement approval requests
- Legal case hearing reminders

**For Field Agents**:
- Daily visit schedule (SMS)
- Case assignment notifications
- Performance alerts
- Payment reminders to send

**For Customers**:
- Payment reminders (SMS/Email)
- Promise confirmation
- Legal notice alerts
- Settlement offers

### Alert Configuration
Navigate to Settings > Notifications to configure:
- Alert frequency
- Notification channels
- Alert thresholds
- Recipient groups

---

## 🐛 Troubleshooting

### Common Issues

**Issue 1: Strategy not executing**
- ✅ Check strategy is active
- ✅ Verify DPD range matches loans
- ✅ Ensure templates are active
- ✅ Check execution logs

**Issue 2: Field agent can't see cases**
- ✅ Verify agent status is active
- ✅ Check territory assignment
- ✅ Confirm cases are allocated
- ✅ Check mobile app sync

**Issue 3: Promise reminders not sending**
- ✅ Check promise due date
- ✅ Verify customer contact details
- ✅ Check SMS/Email gateway
- ✅ Review reminder settings

**Issue 4: Legal notice not generated**
- ✅ Check template exists
- ✅ Verify customer details
- ✅ Check outstanding amount
- ✅ Review notice type

**Issue 5: Settlement approval stuck**
- ✅ Check approval amount threshold
- ✅ Verify approver assignment
- ✅ Check approval workflow
- ✅ Review proposal status

---

## 📈 Best Practices

### Collection Strategy
1. **Start Early**: Begin collection efforts at 1 DPD
2. **Multi-Channel**: Use SMS + Email + Call + Field Visit
3. **Progressive**: Escalate actions as DPD increases
4. **Personalize**: Use customer name and specific amounts
5. **Track**: Monitor strategy performance and adjust

### Field Agent Management
1. **Balance Workload**: Keep cases per agent < 50
2. **Clear Territories**: Avoid overlaps
3. **Set Targets**: Daily visits and monthly collection
4. **Regular Training**: Product knowledge and soft skills
5. **Incentivize**: Performance-based rewards

### Promise Tracking
1. **Record Immediately**: Log promises as soon as made
2. **Be Specific**: Get exact date and amount
3. **Follow Up**: Send reminders 3 days before due
4. **Track Patterns**: Identify serial promise breakers
5. **Escalate**: Move to legal if 3+ broken promises

### Legal Action
1. **Document Everything**: Keep all communication records
2. **Follow Process**: Send demand notice before legal case
3. **Timely Action**: File cases within 30 days of notice
4. **Track Diligently**: Update hearing outcomes immediately
5. **Recover Costs**: Include legal expenses in recovery

### Settlement/OTS
1. **Assess Carefully**: Calculate NPV before offering
2. **Set Minimums**: Don't go below 60% recovery
3. **Time-bound**: Give 15-30 days validity
4. **Proper Approval**: Follow approval hierarchy
5. **Get Commitment**: Ensure payment capability

---

## 📊 Sample Reports

### Daily Collection Report
```
Date: 15-Jan-2024
Portfolio at Risk: ₹12.5 Cr
Collections Today: ₹25 Lakhs
Target: ₹30 Lakhs
Achievement: 83%

By DPD Bucket:
0-30:   ₹8 Lakhs   (32%)
31-60:  ₹10 Lakhs  (40%)
61-90:  ₹5 Lakhs   (20%)
90+:    ₹2 Lakhs   (8%)

By Channel:
Online:       ₹15 Lakhs (60%)
Field Agent:  ₹8 Lakhs  (32%)
Direct:       ₹2 Lakhs  (8%)
```

### Field Agent Performance Report
```
Agent: Rajesh Kumar
Territory: North Delhi
Period: Jan 2024

Cases Assigned: 45
Visits Completed: 28 / 30 (93%)
Collections: ₹18.5 Lakhs
Target: ₹20 Lakhs (93%)
Success Rate: 71%

Top Dispositions:
Payment Collected: 15
Promise to Pay: 8
Customer Met: 3
Not Available: 2
```

### Promise Fulfillment Report
```
Period: Jan 2024
Total Promises: 125
Fulfilled: 85 (68%)
Broken: 25 (20%)
Pending: 15 (12%)

Average Promise Amount: ₹45,000
Fulfillment Rate by Type:
Full Payment: 75%
Partial Payment: 65%
Installment: 55%

Broken Promise Analysis:
First Time: 15
Second Time: 7
Serial Breakers: 3
```

---

## 🎓 Training Resources

### Video Tutorials (to be created)
1. Collection Strategy Setup (10 min)
2. Field Agent Mobile App (15 min)
3. Promise Tracking Workflow (8 min)
4. Legal Notice Generation (12 min)
5. Settlement Approval Process (10 min)

### Documentation
- User Manual (PDF) - Comprehensive guide
- Field Agent Handbook - Mobile app usage
- Legal Process Guide - Step-by-step legal workflow
- Settlement Calculator Guide - NPV analysis

### Training Plan
**Week 1**: Collection Manager Training
- System overview
- Strategy setup
- Agent management
- Reports and analytics

**Week 2**: Field Agent Training
- Mobile app usage
- Visit recording
- Payment collection
- Best practices

**Week 3**: Legal Team Training
- Notice generation
- Case management
- Document handling
- Recovery tracking

**Week 4**: Go Live Support
- On-site assistance
- Issue resolution
- Process refinement
- Performance monitoring

---

## 📞 Support

### Contact Information
- **Technical Support**: tech-support@nbfc.com
- **Business Support**: collections@nbfc.com
- **Helpdesk**: 1800-XXX-XXXX
- **Hours**: Mon-Sat, 9 AM - 6 PM

### Getting Help
1. Check this Quick Start Guide
2. Review troubleshooting section
3. Contact helpdesk
4. Raise support ticket

### Feedback
We value your feedback! Send suggestions to: feedback@nbfc.com

---

## 🚀 Next Steps

### Immediate Actions
1. ✅ Review this guide
2. ⏳ Wait for API routers to be created
3. ⏳ Database migration to be run
4. ⏳ User training to be scheduled

### Post Go-Live
1. Monitor system performance
2. Gather user feedback
3. Refine processes
4. Plan enhancements

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2024 | Initial release |

---

**Document Owner**: Collection Operations Team  
**Last Updated**: January 2024  
**Next Review**: March 2024

---

## 🎯 Quick Reference Card

### Most Common Actions
```
Create Strategy:     /collections/strategies/new
Record Visit:        Field Agent Menu > Record Visit
Create Promise:      /collections/promises > New Promise
Send Legal Notice:   /collections/legal > Create Notice
New Settlement:      /collections/settlement/new
```

### Keyboard Shortcuts (when implemented)
```
Ctrl + N: New item (context-based)
Ctrl + S: Save
Ctrl + F: Search
Ctrl + R: Refresh
Esc: Cancel/Close
```

### Important URLs
```
Dashboard:    /collections
Strategies:   /collections/strategies
Field Agents: /collections/field-agents
Promises:     /collections/promises
Legal:        /collections/legal
Settlement:   /collections/settlement
Templates:    /collections/templates
```

---

**🎉 You're all set! Start with Workflow 1 to create your first collection strategy.**
