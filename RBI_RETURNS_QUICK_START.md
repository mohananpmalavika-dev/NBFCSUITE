# RBI Returns Automation - Quick Start Guide

## 🚀 Getting Started

### Step 1: Run Database Migration

```bash
# Navigate to backend directory
cd backend

# Run the migration
alembic upgrade head

# Verify tables were created
python -c "from shared.database.connection import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('RBI Returns Tables:', [t for t in inspector.get_table_names() if 'rbi' in t or 'nbs7' in t or 'xbrl' in t])"
```

Expected output:
```
RBI Returns Tables: ['rbi_return_master', 'nbs7_returns', 'statutory_returns', 'xbrl_documents', 'compliance_calendar', 'return_submission_history']
```

### Step 2: Seed Return Master Data (Optional)

```python
# Python script to create common return types
from backend.services.compliance.rbi_returns_service import RBIReturnsService
from backend.shared.database.connection import get_db

db = next(get_db())
service = RBIReturnsService(db, tenant_id="default", user_id="admin_user_id")

# Create NBS-7 Monthly return master
service.create_return_master({
    "return_code": "NBS7-M",
    "return_name": "NBS-7 Monthly Financial Return",
    "return_type": "nbs_7_monthly",
    "description": "Monthly financial position for NBFCs",
    "applicable_to": ["nbfc_d", "nbfc_nd_si"],
    "is_mandatory": True,
    "frequency": "monthly",
    "due_days_after_period": 30,
    "grace_period_days": 3,
    "has_xbrl": True,
    "xbrl_taxonomy": "rbi_nbfc_2024",
    "file_formats": ["excel", "pdf", "xbrl"],
    "submission_portal": "https://cosmos.rbi.org.in",
    "submission_method": "online",
    "is_active": True
})

# Create NBS-7 Quarterly return master
service.create_return_master({
    "return_code": "NBS7-Q",
    "return_name": "NBS-7 Quarterly Financial Return",
    "return_type": "nbs_7_quarterly",
    "description": "Quarterly financial position for NBFCs",
    "applicable_to": ["nbfc_d", "nbfc_nd_si"],
    "is_mandatory": True,
    "frequency": "quarterly",
    "due_days_after_period": 30,
    "grace_period_days": 3,
    "has_xbrl": True,
    "xbrl_taxonomy": "rbi_nbfc_2024",
    "file_formats": ["excel", "pdf", "xbrl"],
    "submission_portal": "https://cosmos.rbi.org.in",
    "submission_method": "online",
    "is_active": True
})

db.close()
print("✅ Return masters created successfully!")
```

### Step 3: Test the API

```bash
# Start the backend server
cd backend
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test Endpoints with cURL

#### A. List Return Masters
```bash
curl -X GET "http://localhost:8000/api/rbi-returns/masters" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### B. Generate NBS-7 Return
```bash
curl -X POST "http://localhost:8000/api/rbi-returns/nbs7/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reporting_period": "2024-06",
    "period_start_date": "2024-06-01",
    "period_end_date": "2024-06-30",
    "as_on_date": "2024-06-30",
    "financial_year": "FY2024-25",
    "quarter": "Q1",
    "include_sectoral": true,
    "include_geographic": true
  }'
```

#### C. List NBS-7 Returns
```bash
curl -X GET "http://localhost:8000/api/rbi-returns/nbs7?financial_year=FY2024-25" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### D. Get Dashboard Stats
```bash
curl -X GET "http://localhost:8000/api/rbi-returns/dashboard/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### E. Create Compliance Calendar Event
```bash
curl -X POST "http://localhost:8000/api/rbi-returns/calendar" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_title": "Submit NBS-7 June 2024",
    "event_type": "return_due",
    "event_date": "2024-07-30",
    "due_date": "2024-07-30",
    "priority": "high",
    "category": "RBI",
    "reminder_enabled": true,
    "reminder_days_before": [7, 3, 1]
  }'
```

---

## 📊 Usage Examples

### Example 1: Complete NBS-7 Return Workflow

```python
from datetime import date
from backend.services.compliance.rbi_returns_service import RBIReturnsService
from backend.services.compliance.schemas import NBS7ReturnGenerateRequest

# Initialize service
service = RBIReturnsService(db, tenant_id="your_tenant", user_id="user_uuid")

# 1. Generate return from system data
request = NBS7ReturnGenerateRequest(
    reporting_period="2024-06",
    period_start_date=date(2024, 6, 1),
    period_end_date=date(2024, 6, 30),
    as_on_date=date(2024, 6, 30),
    financial_year="FY2024-25",
    quarter="Q1",
    include_sectoral=True,
    include_geographic=True,
    remarks="June 2024 monthly return"
)

nbs7_return = service.generate_nbs7_return(request)
print(f"✅ Generated Return: {nbs7_return.return_number}")
print(f"Total Assets: ₹{nbs7_return.total_assets:,.2f}")
print(f"Total Liabilities: ₹{nbs7_return.total_liabilities:,.2f}")
print(f"NPA Ratio: {nbs7_return.npa_ratio:.2f}%")
print(f"CRAR: {nbs7_return.crar_percentage:.2f}%")

# 2. Review and update if needed
from backend.services.compliance.schemas import NBS7ReturnUpdate
update = NBS7ReturnUpdate(
    remarks="Updated after review"
)
nbs7_return = service.update_nbs7_return(nbs7_return.id, update)

# 3. Approve the return
nbs7_return = service.approve_nbs7_return(nbs7_return.id)
print(f"✅ Return Approved at {nbs7_return.approved_date}")

# 4. Submit to RBI
nbs7_return = service.submit_nbs7_return(
    nbs7_return.id,
    submission_reference="RBI-SUB-2024-06-12345"
)
print(f"✅ Submitted with reference: {nbs7_return.submission_reference}")
```

### Example 2: Generate XBRL Document

```python
from backend.services.compliance.schemas import XBRLGenerateRequest

# Generate XBRL from approved NBS-7 return
xbrl_request = XBRLGenerateRequest(
    return_type="nbs_7_monthly",
    return_id=nbs7_return.id,
    taxonomy_version="rbi_nbfc_2024",
    entity_identifier="NBFC123456",
    entity_name="ABC NBFC Limited",
    include_validation=True
)

xbrl_doc = service.generate_xbrl_document(xbrl_request)
print(f"✅ XBRL Document: {xbrl_doc.document_number}")
print(f"Validation Status: {'PASSED' if xbrl_doc.is_valid else 'FAILED'}")
print(f"File Size: {xbrl_doc.xbrl_file_size} bytes")

# Download the XBRL XML
print(f"Download URL: {xbrl_doc.xbrl_file_url}")
```

### Example 3: Compliance Calendar Management

```python
from backend.services.compliance.schemas import ComplianceCalendarCreate

# Create a recurring monthly event
event = ComplianceCalendarCreate(
    event_code="NBS7-MONTHLY",
    event_title="Submit NBS-7 Monthly Return",
    event_type="return_due",
    description="Monthly NBS-7 return submission to RBI",
    event_date=date(2024, 7, 30),
    due_date=date(2024, 7, 30),
    priority="critical",
    category="RBI",
    is_recurring=True,
    recurrence_pattern="monthly",
    recurrence_day=30,
    reminder_enabled=True,
    reminder_days_before=[30, 15, 7, 3, 1],
    notes="Ensure all data is validated before submission"
)

calendar_event = service.create_calendar_event(event)
print(f"✅ Calendar Event: {calendar_event.event_title}")

# Get upcoming deadlines
upcoming = service.get_upcoming_deadlines(days_ahead=30, limit=10)
print(f"\n📅 Upcoming Deadlines ({len(upcoming)}):")
for deadline in upcoming:
    days_left = (deadline.due_date - date.today()).days
    print(f"  - {deadline.event_title} (Due: {deadline.due_date}, {days_left} days left)")
```

### Example 4: Dashboard Analytics

```python
# Get comprehensive dashboard stats
stats = service.get_returns_dashboard_stats()

print("📊 RBI Returns Dashboard")
print("=" * 50)
print(f"Returns Due This Month: {stats['total_returns_due']}")
print(f"Overdue Returns: {stats['overdue_returns']}")
print(f"Pending Approval: {stats['pending_approval']}")
print(f"Draft Returns: {stats['draft_returns']}")
print(f"Compliance Score: {stats['compliance_score']:.1f}%")
print(f"On-Time Submission Rate: {stats['on_time_submission_rate']:.1f}%")

print("\n📈 NBS-7 Status Breakdown:")
for status, count in stats['nbs7_monthly_status'].items():
    print(f"  {status}: {count}")

print("\n⏰ Upcoming Deadlines:")
for deadline in stats['upcoming_deadlines'][:5]:
    print(f"  - {deadline['event_title']} ({deadline['days_remaining']} days)")

# Get calendar summary
calendar_summary = service.get_compliance_calendar_summary()
print(f"\n📅 Calendar Summary:")
print(f"Total Events: {calendar_summary['total_events']}")
print(f"Upcoming: {calendar_summary['upcoming_events']}")
print(f"Overdue: {calendar_summary['overdue_events']}")
print(f"Completed: {calendar_summary['completed_events']}")
```

---

## 🔍 Testing Scenarios

### Scenario 1: Monthly Return Cycle
1. Generate NBS-7 return (auto-fetch data)
2. Review generated data
3. Make manual adjustments if needed
4. Approve return
5. Generate XBRL
6. Download XML file
7. Submit to RBI portal
8. Record acknowledgement number

### Scenario 2: Overdue Tracking
1. Create calendar events with due dates
2. System flags overdue returns
3. Dashboard shows overdue count
4. Notifications sent to assignees
5. Track days overdue

### Scenario 3: Multi-Return Management
1. Generate multiple returns for different periods
2. Filter by financial year
3. Filter by quarter
4. View submission history
5. Compare period-over-period

---

## 🐛 Troubleshooting

### Issue: Migration fails
```bash
# Check current revision
alembic current

# Reset to previous revision if needed
alembic downgrade -1

# Re-run upgrade
alembic upgrade head
```

### Issue: Data not auto-generating
- Verify loan accounts exist in database
- Check deposit accounts are active
- Ensure GL accounts are properly mapped
- Verify date ranges are correct

### Issue: XBRL validation fails
- Check taxonomy version is supported
- Verify all required fields have data
- Ensure numeric fields are properly formatted
- Review validation error messages

---

## 📝 Configuration Checklist

- [ ] Database migration completed
- [ ] Return masters created
- [ ] Test data in loan_accounts
- [ ] Test data in deposit_accounts
- [ ] GL accounts mapped correctly
- [ ] User authentication working
- [ ] Tenant isolation configured
- [ ] File storage paths configured
- [ ] Email notifications setup (optional)

---

## 🎯 Next Steps

1. **Test Backend Thoroughly**
   - Generate sample returns
   - Test all workflows
   - Verify calculations

2. **Build Frontend**
   - Dashboard page
   - NBS-7 management
   - Calendar view
   - XBRL export

3. **Production Deployment**
   - Setup production database
   - Configure file storage (S3/Azure)
   - Enable email notifications
   - Setup monitoring

4. **User Training**
   - Create user guides
   - Train finance team
   - Setup approval workflows

---

## 📞 API Reference

**Base URL**: `http://localhost:8000`

**Authentication**: Bearer token in Authorization header

**Common Response Format**:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

---

**Ready to use!** 🚀

For complete API documentation, visit: http://localhost:8000/docs
