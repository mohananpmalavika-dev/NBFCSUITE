# Getting Started with Phase 9: Reporting & Analytics

**Quick Start Guide**  
**Version:** 1.0  
**Date:** July 3, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Quick Start Examples](#quick-start-examples)
4. [Common Use Cases](#common-use-cases)
5. [API Examples](#api-examples)
6. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### System Requirements
- Python 3.9+
- PostgreSQL 13+
- Node.js 18+
- 2GB RAM minimum
- 10GB disk space for reports

### Dependencies
```bash
# Python packages
fastapi>=0.100.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
alembic>=1.11.0

# Node packages
next>=14.0.0
react>=18.0.0
typescript>=5.0.0
```

### Access Requirements
- Database access with CREATE privileges
- API access token
- Report storage directory with write permissions

---

## 2. Setup Instructions

### Step 1: Database Setup

```bash
# Run migration
psql -U nbfc_user -d nbfcsuite -f infra/migrations/026_reporting_analytics.sql

# Verify installation
psql -U nbfc_user -d nbfcsuite -c "
  SELECT table_name FROM information_schema.tables 
  WHERE table_name LIKE 'report_%' OR table_name LIKE 'dashboard_%'
"
```

Expected output: 10 tables created

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd services/gold

# Install dependencies
pip install -r requirements.txt

# Start service
uvicorn app.main:app --reload --port 8013
```

Verify: `http://localhost:8013/health`

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd apps/customer-app

# Install dependencies
npm install

# Start development server
npm run dev
```

Verify: `http://localhost:3000/gold-lending/reporting/builder`

### Step 4: Initial Configuration

```bash
# Create report storage directory
mkdir -p /var/reports/{temp,archive}
chmod 755 /var/reports

# Set environment variables
export REPORT_STORAGE_PATH=/var/reports
export REPORT_TEMP_PATH=/var/reports/temp
```

---

## 3. Quick Start Examples

### Example 1: Generate Your First Report

**Step 1:** Access Report Builder
```
Navigate to: http://localhost:3000/gold-lending/reporting/builder
```

**Step 2:** Select a report
```
Click on "Portfolio Summary Report" from the list
```

**Step 3:** Configure parameters
```
- From Date: 2026-01-01
- To Date: 2026-01-31
- Output Format: PDF
```

**Step 4:** Generate
```
Click "Generate Report" button
Wait for completion and download
```

### Example 2: Create a Report Schedule

**API Request:**
```bash
curl -X POST http://localhost:8013/api/v1/gold/reporting/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "report_definition_id": 1,
    "name": "Daily Portfolio Report",
    "schedule_type": "daily",
    "frequency": "0 6 * * *",
    "start_date": "2026-07-01",
    "execution_time": "06:00:00",
    "timezone": "Asia/Kolkata",
    "output_format": "pdf",
    "delivery_method": "email",
    "recipients": ["manager@company.com"]
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Daily Portfolio Report",
  "status": "active",
  "next_execution_at": "2026-07-01T06:00:00"
}
```

### Example 3: Query Analytics

**Access Analytics Query Builder:**
```
Navigate to: http://localhost:3000/gold-lending/reporting/analytics
```

**Select Metrics:**
- Total Portfolio Value
- Active Loans Count
- Collection Rate

**Configure Query:**
- Date Range: Last 30 days
- Group By: Daily

**View Results:**
- Summary cards with current values
- Trend chart over time
- Detailed data table

### Example 4: View Executive Dashboard

**Access Dashboard:**
```
Navigate to: http://localhost:3000/gold-lending/reporting/dashboards/executive
```

**Dashboard Shows:**
- 4 Key KPI cards
- Disbursement trend chart
- Portfolio mix visualization
- Top 5 performing branches
- Recent alerts
- Quick action buttons

---

## 4. Common Use Cases

### Use Case 1: Daily Operations Report

**Scenario:** Generate daily portfolio snapshot for branch managers

**Solution:**
1. Create report definition with portfolio metrics
2. Schedule daily execution at 7 AM
3. Configure email delivery to branch managers
4. Set up alerts for threshold breaches

**Configuration:**
```python
{
    "report_code": "RPT_DAILY_OPERATIONS",
    "schedule_type": "daily",
    "execution_time": "07:00:00",
    "delivery_method": "email",
    "recipients": ["branch1@company.com", "branch2@company.com"]
}
```

### Use Case 2: Monthly Regulatory Reporting

**Scenario:** Automated RBI return generation

**Solution:**
1. Use pre-configured RBI report template
2. Schedule monthly execution on 1st of month
3. Generate in required format
4. Archive for compliance

**Configuration:**
```python
{
    "report_code": "RPT_RBI_RETURN_1",
    "schedule_type": "monthly",
    "frequency": "0 0 1 * *",
    "output_format": "excel",
    "delivery_method": "sftp",
    "delivery_config": {
        "host": "sftp.rbi.org.in",
        "path": "/returns/monthly"
    }
}
```

### Use Case 3: Ad-hoc Portfolio Analysis

**Scenario:** Executive requests custom analysis

**Steps:**
1. Go to Analytics Query Builder
2. Select relevant metrics (Portfolio, NPA, Collection Rate)
3. Set date range (e.g., Q1 2026)
4. Group by branch or product
5. Export results to Excel

**Metrics to Select:**
- Total Portfolio Value
- Active Loans Count
- NPA Ratio
- Collection Rate
- Average Loan Size

### Use Case 4: Collection Performance Tracking

**Scenario:** Monitor collection team performance

**Solution:**
1. Access Collections Dashboard
2. View team performance metrics
3. Track individual collector stats
4. Monitor collection efficiency
5. Set up performance alerts

**Key Metrics:**
- Cases handled
- Collection rate
- Promise fulfillment
- Recovery amount
- Average resolution time

---

## 5. API Examples

### Example 1: Generate Report via API

**Python:**
```python
import requests

response = requests.post(
    'http://localhost:8013/api/v1/gold/reporting/generate',
    json={
        'report_code': 'RPT_PORTFOLIO_SUMMARY',
        'parameters': {
            'date_from': '2026-01-01',
            'date_to': '2026-06-30',
            'branch_id': 'BR001'
        },
        'output_format': 'pdf'
    }
)

result = response.json()
print(f"Execution ID: {result['execution_id']}")
print(f"Status: {result['status']}")
```

### Example 2: List Available Reports

**Python:**
```python
import requests

response = requests.get(
    'http://localhost:8013/api/v1/gold/reporting/catalog',
    params={'category': 'financial'}
)

catalog = response.json()
print(f"Total Reports: {catalog['total_count']}")

for report in catalog['reports']:
    print(f"- {report['name']} ({report['code']})")
    print(f"  Executions: {report['execution_count']}")
    print(f"  Avg Duration: {report['avg_duration']}s")
```

### Example 3: Query Analytics Metrics

**Python:**
```python
import requests
from datetime import date, timedelta

# Get last 30 days of data
end_date = date.today()
start_date = end_date - timedelta(days=30)

response = requests.post(
    'http://localhost:8013/api/v1/gold/reporting/analytics/query',
    json={
        'metric_codes': [
            'MTR_TOTAL_PORTFOLIO',
            'MTR_ACTIVE_LOANS',
            'MTR_COLLECTION_RATE',
            'MTR_NPA_RATIO'
        ],
        'date_from': start_date.isoformat(),
        'date_to': end_date.isoformat(),
        'group_by': 'day'
    }
)

data = response.json()
for metric in data['metrics']:
    print(f"{metric['metric_name']}: {metric['value']} ({metric['unit']})")
    if metric['change_percentage']:
        print(f"  Change: {metric['change_percentage']}%")
```

### Example 4: Create Dashboard Widget

**Python:**
```python
import requests

response = requests.post(
    'http://localhost:8013/api/v1/gold/reporting/dashboards/1/widgets',
    json={
        'widget_type': 'chart',
        'chart_type': 'line',
        'title': 'Disbursement Trend',
        'data_source': 'disbursement_transactions',
        'query': 'SELECT DATE(disbursed_at), SUM(disbursed_amount) ...',
        'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4},
        'refresh_interval': 300
    }
)

widget = response.json()
print(f"Widget created: {widget['id']}")
```

---

## 6. Troubleshooting

### Issue 1: Report Generation Fails

**Symptom:** Report execution status shows 'failed'

**Possible Causes:**
- Invalid query template
- Missing data source
- Insufficient permissions
- Database connection timeout

**Solutions:**
```bash
# Check execution details
curl http://localhost:8013/api/v1/gold/reporting/executions/{id}

# Review error message
psql -U nbfc_user -d nbfcsuite -c "
  SELECT error_message, error_details 
  FROM report_executions 
  WHERE id = {id}
"

# Verify data source
psql -U nbfc_user -d nbfcsuite -c "\dt loan_accounts"
```

### Issue 2: Schedule Not Executing

**Symptom:** Schedule shows 'active' but not executing

**Possible Causes:**
- next_execution_at in the past
- Scheduler service not running
- Invalid cron expression
- Timezone mismatch

**Solutions:**
```bash
# Check schedule details
curl http://localhost:8013/api/v1/gold/reporting/schedules/{id}

# Verify next execution time
psql -U nbfc_user -d nbfcsuite -c "
  SELECT next_execution_at, timezone, frequency 
  FROM report_schedules 
  WHERE id = {id}
"

# Update next execution
curl -X POST http://localhost:8013/api/v1/gold/reporting/schedules/{id}/resume
```

### Issue 3: Dashboard Not Loading

**Symptom:** Dashboard page shows empty or error

**Possible Causes:**
- Dashboard not found
- Widgets have invalid queries
- Missing dashboard permissions
- Frontend API connection issue

**Solutions:**
```bash
# Verify dashboard exists
curl http://localhost:8013/api/v1/gold/reporting/dashboards/by-code/DASH_EXECUTIVE

# Check widgets
curl http://localhost:8013/api/v1/gold/reporting/dashboards/1/widgets

# Test widget data
curl http://localhost:8013/api/v1/gold/reporting/widgets/1/data
```

### Issue 4: Slow Report Performance

**Symptom:** Report takes too long to generate

**Solutions:**
1. **Add Filters:** Limit date ranges and data volume
2. **Optimize Query:** Review query_template for efficiency
3. **Use Indexes:** Ensure proper database indexes
4. **Schedule Off-Peak:** Run heavy reports during low-traffic hours
5. **Enable Caching:** Cache frequently accessed data

**Performance Tips:**
```python
# Bad: No filters
{
    "date_from": "2020-01-01",
    "date_to": "2026-12-31"
}

# Good: Reasonable date range
{
    "date_from": "2026-01-01",
    "date_to": "2026-06-30",
    "branch_id": "BR001"
}
```

### Issue 5: Export File Not Found

**Symptom:** Download link returns 404

**Possible Causes:**
- Export expired (default: 30 days)
- File deleted from storage
- Invalid access token
- Storage path misconfigured

**Solutions:**
```bash
# Check export status
curl http://localhost:8013/api/v1/gold/reporting/exports/{id}

# Verify storage path
ls -la $REPORT_STORAGE_PATH

# Re-generate export
curl -X POST http://localhost:8013/api/v1/gold/reporting/executions/{exec_id}
```

---

## Quick Reference

### Key URLs

```
Report Builder:    http://localhost:3000/gold-lending/reporting/builder
Report Catalog:    http://localhost:3000/gold-lending/reporting/catalog
Schedules:         http://localhost:3000/gold-lending/reporting/schedules
Executive Dashboard: http://localhost:3000/gold-lending/reporting/dashboards/executive
Analytics:         http://localhost:3000/gold-lending/reporting/analytics

API Base:          http://localhost:8013/api/v1/gold/reporting
```

### Common Commands

```bash
# Generate report
curl -X POST /api/v1/gold/reporting/generate -d '{"report_code": "..."}'

# List reports
curl /api/v1/gold/reporting/catalog

# Query analytics
curl -X POST /api/v1/gold/reporting/analytics/query -d '{"metric_codes": [...]}'

# Get dashboard data
curl -X POST /api/v1/gold/reporting/dashboards/DASH_EXECUTIVE/analytics
```

### Support

For additional help:
- Check technical documentation: `PHASE9_REPORTING_ANALYTICS.md`
- Review API schemas in Swagger: `http://localhost:8013/docs`
- Contact support: support@company.com

---

**Document Version:** 1.0  
**Last Updated:** July 3, 2026  
