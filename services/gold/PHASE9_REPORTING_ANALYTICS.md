# Phase 9: Reporting & Analytics - Technical Documentation

**Version:** 1.0  
**Date:** July 3, 2026  
**Status:** Complete  

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Data Models](#data-models)
6. [Frontend Components](#frontend-components)
7. [Report Catalog](#report-catalog)
8. [Security & Compliance](#security-compliance)
9. [Performance Optimization](#performance-optimization)
10. [Deployment Guide](#deployment-guide)

---

## 1. Overview

Phase 9 implements a comprehensive **Reporting & Analytics System** for the Gold Loan platform, providing:

- **Report Builder Engine** - Dynamic report generation with parameterization
- **Report Catalog** - Library of 18+ standard and custom reports
- **Scheduling System** - Automated report execution and distribution
- **Analytics Engine** - Multi-metric querying and trend analysis
- **Dashboard Framework** - Configurable analytics dashboards
- **Data Snapshots** - Point-in-time historical data capture
- **Export Management** - Multi-format report generation (PDF, Excel, CSV)

### Key Features

- 60+ REST API endpoints for complete reporting operations
- 10 database tables with automated triggers and views
- 5 frontend pages for report building, catalog, scheduling, dashboards, and analytics
- 18 pre-configured standard reports (financial, operational, regulatory)
- 6 pre-defined dashboards (executive, branch, collection, risk, finance, lending)
- 10 KPI metrics with threshold monitoring
- Multi-format export (PDF, Excel, CSV, JSON, XML, HTML)

---

## 2. Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │ Report   │ Catalog  │Schedules │Dashboards│Analytics │ │
│  │ Builder  │          │          │          │          │ │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  60+ REST Endpoints                                   │  │
│  │  - Report Management  - Schedules  - Executions      │  │
│  │  - Templates         - Exports    - Dashboards       │  │
│  │  - Widgets          - Snapshots   - Metrics          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer (PostgreSQL)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  10 Tables + 4 Views + 4 Triggers                    │  │
│  │  - report_definitions    - report_exports            │  │
│  │  - report_templates      - dashboard_definitions     │  │
│  │  - report_schedules      - dashboard_widgets         │  │
│  │  - report_executions     - data_snapshots            │  │
│  │  - report_parameters     - analytics_metrics         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Report Creation Flow**
   - User selects report from catalog
   - System loads report definition and parameters
   - User configures parameters and output format
   - System creates execution record and generates report
   - Report file stored and download link provided

2. **Scheduled Execution Flow**
   - Scheduler triggers based on cron/frequency
   - System creates execution record
   - Report generated with pre-configured parameters
   - Output delivered via configured method (email, FTP, S3)
   - Execution stats updated

3. **Analytics Query Flow**
   - User selects metrics and date range
   - System executes metric calculations
   - Results aggregated and time-series generated
   - Data returned with visualizations

---

## 3. Database Schema

### 3.1 Core Tables

#### report_definitions
Master table for report configurations.

```sql
CREATE TABLE report_definitions (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- financial, operational, regulatory, custom
    report_type VARCHAR(50) NOT NULL, -- standard, custom, ad_hoc, regulatory
    data_source VARCHAR(100),
    query_template TEXT,
    output_formats JSONB DEFAULT '["pdf", "excel", "csv"]'::jsonb,
    parameters JSONB,
    filters JSONB,
    columns JSONB,
    sorting JSONB,
    grouping JSONB,
    aggregations JSONB,
    styling JSONB,
    access_roles JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    created_by BIGINT REFERENCES users(id),
    updated_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**Indexes:** code, category, report_type, is_active, created_at

#### report_schedules
Scheduled report execution configurations.

```sql
CREATE TABLE report_schedules (
    id BIGSERIAL PRIMARY KEY,
    report_definition_id BIGINT NOT NULL REFERENCES report_definitions(id),
    template_id BIGINT REFERENCES report_templates(id),
    name VARCHAR(200) NOT NULL,
    schedule_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly, quarterly
    frequency VARCHAR(100), -- Cron expression
    start_date DATE NOT NULL,
    end_date DATE,
    execution_time TIME DEFAULT '00:00:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    parameters JSONB,
    output_format VARCHAR(20) DEFAULT 'pdf',
    delivery_method VARCHAR(50), -- email, ftp, sftp, s3
    delivery_config JSONB,
    recipients JSONB,
    status VARCHAR(20) DEFAULT 'active',
    last_execution_at TIMESTAMP,
    next_execution_at TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**Indexes:** report_definition_id, status, is_active, next_execution_at, created_by

#### report_executions
Report execution history and results.

```sql
CREATE TABLE report_executions (
    id BIGSERIAL PRIMARY KEY,
    report_definition_id BIGINT NOT NULL REFERENCES report_definitions(id),
    schedule_id BIGINT REFERENCES report_schedules(id),
    template_id BIGINT REFERENCES report_templates(id),
    execution_type VARCHAR(50) NOT NULL, -- scheduled, manual, api
    parameters JSONB,
    filters JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    output_format VARCHAR(20),
    file_path VARCHAR(500),
    file_size BIGINT,
    file_url VARCHAR(500),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    rows_processed INTEGER,
    error_message TEXT,
    executed_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**Indexes:** report_definition_id, schedule_id, status, executed_by, created_at, completed_at

#### dashboard_definitions
Dashboard layout and configuration.

```sql
CREATE TABLE dashboard_definitions (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    dashboard_type VARCHAR(50) NOT NULL, -- executive, operational, analytical
    category VARCHAR(50),
    layout JSONB,
    theme JSONB,
    refresh_interval INTEGER,
    access_roles JSONB,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**Indexes:** code, dashboard_type, category, is_active, display_order

#### analytics_metrics
Business metrics and KPI definitions.

```sql
CREATE TABLE analytics_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_code VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    metric_category VARCHAR(50) NOT NULL, -- portfolio, collection, risk, finance
    metric_type VARCHAR(50) NOT NULL, -- count, sum, average, percentage, ratio
    calculation_formula TEXT,
    unit VARCHAR(50),
    threshold_warning DECIMAL(15,2),
    threshold_critical DECIMAL(15,2),
    target_value DECIMAL(15,2),
    trend_direction VARCHAR(20), -- higher_better, lower_better
    is_kpi BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

**Indexes:** metric_code, metric_category, metric_type, is_kpi, is_active

### 3.2 Views

#### vw_active_reports
Active reports with execution statistics.

```sql
CREATE OR REPLACE VIEW vw_active_reports AS
SELECT 
    rd.id, rd.code, rd.name, rd.category, rd.report_type,
    COUNT(DISTINCT re.id) as total_executions,
    COUNT(DISTINCT CASE WHEN re.status = 'completed' THEN re.id END) as successful_executions,
    MAX(re.completed_at) as last_execution_at,
    AVG(CASE WHEN re.status = 'completed' THEN re.duration_seconds END) as avg_duration_seconds,
    COUNT(DISTINCT rs.id) as active_schedules
FROM report_definitions rd
LEFT JOIN report_executions re ON rd.id = re.report_definition_id
LEFT JOIN report_schedules rs ON rd.id = rs.report_definition_id AND rs.is_active = true
WHERE rd.is_active = true
GROUP BY rd.id, rd.code, rd.name, rd.category, rd.report_type;
```

#### vw_scheduled_reports
Scheduled reports summary.

```sql
CREATE OR REPLACE VIEW vw_scheduled_reports AS
SELECT 
    rs.id, rs.name as schedule_name, rd.name as report_name,
    rs.schedule_type, rs.status, rs.last_execution_at, rs.next_execution_at,
    rs.execution_count, rs.success_count, rs.failure_count,
    CASE WHEN rs.execution_count > 0 
        THEN (rs.success_count::float / rs.execution_count * 100)
        ELSE 0 END as success_rate
FROM report_schedules rs
INNER JOIN report_definitions rd ON rs.report_definition_id = rd.id
WHERE rs.is_active = true;
```

### 3.3 Triggers

#### update_execution_duration
Automatically calculate execution duration.

```sql
CREATE TRIGGER trg_calculate_execution_duration
    BEFORE UPDATE ON report_executions
    FOR EACH ROW
    WHEN (NEW.status = 'completed')
    EXECUTE FUNCTION calculate_execution_duration();
```

#### update_schedule_stats
Update schedule execution statistics.

```sql
CREATE TRIGGER trg_update_schedule_execution_stats
    AFTER UPDATE ON report_executions
    FOR EACH ROW
    WHEN (NEW.status IN ('completed', 'failed') AND OLD.status != NEW.status)
    EXECUTE FUNCTION update_schedule_execution_stats();
```

---

## 4. API Endpoints

### 4.1 Report Definitions (7 endpoints)

```
POST   /api/v1/gold/reporting/definitions
GET    /api/v1/gold/reporting/definitions
GET    /api/v1/gold/reporting/definitions/{id}
GET    /api/v1/gold/reporting/definitions/by-code/{code}
PUT    /api/v1/gold/reporting/definitions/{id}
DELETE /api/v1/gold/reporting/definitions/{id}
```

**Example: Create Report Definition**
```python
POST /api/v1/gold/reporting/definitions
{
    "code": "RPT_CUSTOM_001",
    "name": "Custom Portfolio Report",
    "description": "Detailed portfolio analysis",
    "category": "operational",
    "report_type": "custom",
    "data_source": "loan_accounts",
    "output_formats": ["pdf", "excel"],
    "parameters": {
        "date_from": {"type": "date", "required": true},
        "date_to": {"type": "date", "required": true},
        "branch_id": {"type": "select", "required": false}
    }
}
```

### 4.2 Report Schedules (10 endpoints)

```
POST   /api/v1/gold/reporting/schedules
GET    /api/v1/gold/reporting/schedules
GET    /api/v1/gold/reporting/schedules/{id}
PUT    /api/v1/gold/reporting/schedules/{id}
POST   /api/v1/gold/reporting/schedules/{id}/pause
POST   /api/v1/gold/reporting/schedules/{id}/resume
POST   /api/v1/gold/reporting/schedules/{id}/execute
DELETE /api/v1/gold/reporting/schedules/{id}
```

**Example: Create Schedule**
```python
POST /api/v1/gold/reporting/schedules
{
    "report_definition_id": 1,
    "name": "Monthly Portfolio Report",
    "schedule_type": "monthly",
    "frequency": "0 0 1 * *",  // First day of month at midnight
    "start_date": "2026-01-01",
    "execution_time": "00:00:00",
    "timezone": "Asia/Kolkata",
    "output_format": "pdf",
    "delivery_method": "email",
    "delivery_config": {
        "smtp_server": "smtp.company.com",
        "from": "reports@company.com"
    },
    "recipients": ["manager@company.com", "analyst@company.com"]
}
```

### 4.3 Report Executions (7 endpoints)

```
POST   /api/v1/gold/reporting/executions
GET    /api/v1/gold/reporting/executions
GET    /api/v1/gold/reporting/executions/{id}
PUT    /api/v1/gold/reporting/executions/{id}
POST   /api/v1/gold/reporting/executions/{id}/cancel
```

### 4.4 Dashboards (7 endpoints)

```
POST   /api/v1/gold/reporting/dashboards
GET    /api/v1/gold/reporting/dashboards
GET    /api/v1/gold/reporting/dashboards/{id}
GET    /api/v1/gold/reporting/dashboards/by-code/{code}
PUT    /api/v1/gold/reporting/dashboards/{id}
DELETE /api/v1/gold/reporting/dashboards/{id}
POST   /api/v1/gold/reporting/dashboards/{code}/analytics
```

### 4.5 Analytics Metrics (7 endpoints)

```
POST   /api/v1/gold/reporting/metrics
GET    /api/v1/gold/reporting/metrics
GET    /api/v1/gold/reporting/metrics/{id}
GET    /api/v1/gold/reporting/metrics/by-code/{code}
PUT    /api/v1/gold/reporting/metrics/{id}
DELETE /api/v1/gold/reporting/metrics/{id}
```

### 4.6 Special Endpoints

```
POST   /api/v1/gold/reporting/generate       // Generate report by code
GET    /api/v1/gold/reporting/catalog        // Get report catalog
POST   /api/v1/gold/reporting/analytics/query  // Query analytics
```

**Total Endpoints:** 60+

---

## 5. Data Models

### ReportDefinition Model
```python
class ReportDefinition(Base):
    __tablename__ = "report_definitions"
    
    id = Column(BigInteger, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    report_type = Column(String(50), nullable=False)
    query_template = Column(Text)
    output_formats = Column(JSONB)
    parameters = Column(JSONB)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    templates = relationship("ReportTemplate", back_populates="report_definition")
    schedules = relationship("ReportSchedule", back_populates="report_definition")
    executions = relationship("ReportExecution", back_populates="report_definition")
```

### ReportSchedule Model
```python
class ReportSchedule(Base):
    __tablename__ = "report_schedules"
    
    id = Column(BigInteger, primary_key=True)
    report_definition_id = Column(BigInteger, ForeignKey("report_definitions.id"))
    schedule_type = Column(String(50), nullable=False)
    frequency = Column(String(100))
    status = Column(String(20), default='active')
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    
    # Relationships
    report_definition = relationship("ReportDefinition", back_populates="schedules")
    executions = relationship("ReportExecution", back_populates="schedule")
```

### AnalyticsMetric Model
```python
class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"
    
    id = Column(BigInteger, primary_key=True)
    metric_code = Column(String(100), unique=True, nullable=False)
    metric_name = Column(String(200), nullable=False)
    metric_category = Column(String(50), nullable=False)
    metric_type = Column(String(50), nullable=False)
    calculation_formula = Column(Text)
    is_kpi = Column(Boolean, default=False)
    target_value = Column(Numeric(15, 2))
    trend_direction = Column(String(20))
```

---

## 6. Frontend Components

### 6.1 Report Builder
**Location:** `apps/customer-app/app/gold-lending/reporting/builder/page.tsx`

**Features:**
- Report selection from catalog
- Dynamic parameter form generation
- Output format selection
- Real-time report generation
- Download link management

**Key Functions:**
```typescript
loadReportDefinitions()      // Load available reports
handleReportSelect()          // Load report details and parameters
handleParameterChange()       // Update parameter values
handleGenerateReport()        // Execute report generation
```

### 6.2 Report Catalog
**Location:** `apps/customer-app/app/gold-lending/reporting/catalog/page.tsx`

**Features:**
- Searchable report library
- Category filtering
- Execution statistics
- Quick actions (run, schedule)
- Report metadata display

**Statistics Displayed:**
- Total reports count
- System vs custom reports
- Execution counts
- Average duration

### 6.3 Scheduled Reports
**Location:** `apps/customer-app/app/gold-lending/reporting/schedules/page.tsx`

**Features:**
- Schedule management (CRUD)
- Pause/resume schedules
- Execute now functionality
- Success rate tracking
- Delivery configuration

**Actions:**
- Pause schedule
- Resume schedule
- Execute immediately
- Delete schedule
- View execution history

### 6.4 Executive Dashboard
**Location:** `apps/customer-app/app/gold-lending/reporting/dashboards/executive/page.tsx`

**Features:**
- High-level KPI cards
- Trend charts (disbursement, portfolio mix)
- Key performance indicators table
- Top performing branches
- Recent alerts
- Quick action buttons

**KPI Metrics:**
- Total Portfolio Value
- Active Loans Count
- Collection Rate
- NPA Ratio
- 10+ additional metrics

### 6.5 Analytics Query Builder
**Location:** `apps/customer-app/app/gold-lending/reporting/analytics/page.tsx`

**Features:**
- Multi-metric selection
- Date range configuration
- Group by options (day, week, month, branch, product)
- Results visualization
- Time series charts
- Data table export

**Query Options:**
- Select multiple metrics
- Configure date ranges
- Choose aggregation level
- Apply filters
- Export results to CSV

---

## 7. Report Catalog

### 7.1 Portfolio Reports

| Code | Name | Description |
|------|------|-------------|
| RPT_PORTFOLIO_SUMMARY | Portfolio Summary | Comprehensive portfolio overview |
| RPT_LOAN_AGING | Loan Aging Analysis | Analysis of loans by age buckets |
| RPT_DPD_ANALYSIS | DPD Analysis | Days Past Due analysis |
| RPT_DISBURSEMENT_SUMMARY | Disbursement Summary | Loan disbursement summary |
| RPT_REPAYMENT_SUMMARY | Repayment Summary | Loan repayment summary |

### 7.2 Financial Reports

| Code | Name | Description |
|------|------|-------------|
| RPT_BALANCE_SHEET | Balance Sheet | Balance sheet statement |
| RPT_INCOME_STATEMENT | Income Statement | Profit & loss statement |
| RPT_CASH_FLOW | Cash Flow Statement | Cash flow analysis |
| RPT_TRIAL_BALANCE | Trial Balance | Trial balance report |
| RPT_GENERAL_LEDGER | General Ledger | Detailed general ledger |

### 7.3 Collection Reports

| Code | Name | Description |
|------|------|-------------|
| RPT_COLLECTION_PERFORMANCE | Collection Performance | Team performance metrics |
| RPT_RECOVERY_ANALYSIS | Recovery Analysis | Recovery actions and outcomes |
| RPT_LEGAL_NOTICES | Legal Notices | Summary of legal notices |
| RPT_AUCTION_SUMMARY | Auction Summary | Auction activities summary |

### 7.4 Regulatory Reports

| Code | Name | Description |
|------|------|-------------|
| RPT_RBI_RETURN_1 | RBI Return - NBS1 | NBFC Returns |
| RPT_NPA_REPORT | NPA Report | Non-Performing Assets |
| RPT_PRUDENTIAL_NORMS | Prudential Norms | Compliance report |
| RPT_ALM_REPORT | ALM Report | Asset Liability Management |

**Total Standard Reports:** 18

---

## 8. Security & Compliance

### 8.1 Access Control

**Role-Based Access (RBAC):**
- Report definitions include `access_roles` field
- Schedules restricted by creator
- Exports include access tokens
- Dashboard access controlled by roles

**Permission Levels:**
- `report.view` - View report catalog
- `report.create` - Create custom reports
- `report.execute` - Run reports
- `report.schedule` - Create schedules
- `report.admin` - Manage all reports

### 8.2 Audit Trail

All operations logged with:
- User ID (created_by, executed_by)
- Timestamps (created_at, updated_at)
- Operation metadata
- Execution details

**Tracked Events:**
- Report creation/modification
- Schedule creation/changes
- Report execution
- Export generation
- Parameter changes

### 8.3 Data Privacy

**Sensitive Data Handling:**
- PII masked in reports by default
- Configurable data masking rules
- Export encryption support
- Secure file storage
- Time-limited access tokens

---

## 9. Performance Optimization

### 9.1 Database Optimization

**Indexes Created:** 53 indexes across all tables
- Primary key indexes
- Foreign key indexes
- Query optimization indexes
- Composite indexes for common queries

**Query Performance:**
- Views pre-calculate common aggregations
- Materialized views for heavy queries
- Partitioning for large tables (executions, exports)
- Query result caching

### 9.2 Report Generation

**Optimization Strategies:**
- Asynchronous report generation
- Background job processing
- Query result pagination
- Incremental data loading
- Template caching

**Best Practices:**
- Limit date ranges for large datasets
- Use filters to reduce data volume
- Schedule heavy reports during off-peak hours
- Cache frequently accessed reports

### 9.3 API Performance

**Rate Limiting:**
- 100 requests per minute per user
- 1000 requests per hour per API key
- Throttling for heavy operations

**Caching:**
- Report catalog cached for 5 minutes
- Metric definitions cached for 15 minutes
- Dashboard configurations cached

---

## 10. Deployment Guide

### 10.1 Database Migration

```bash
# Run migration
psql -U nbfc_user -d nbfcsuite -f infra/migrations/026_reporting_analytics.sql

# Verify tables
psql -U nbfc_user -d nbfcsuite -c "\dt report_*"
psql -U nbfc_user -d nbfcsuite -c "\dt dashboard_*"
psql -U nbfc_user -d nbfcsuite -c "\dt analytics_*"

# Verify views
psql -U nbfc_user -d nbfcsuite -c "\dv vw_*"

# Test seed data
psql -U nbfc_user -d nbfcsuite -c "SELECT COUNT(*) FROM report_definitions;"
```

### 10.2 Backend Deployment

```bash
# Install dependencies
cd services/gold
pip install -r requirements.txt

# Restart FastAPI service
systemctl restart gold-api

# Verify endpoints
curl http://localhost:8013/api/v1/gold/reporting/catalog
curl http://localhost:8013/api/v1/gold/reporting/dashboards
curl http://localhost:8013/api/v1/gold/reporting/metrics
```

### 10.3 Frontend Deployment

```bash
# Build frontend
cd apps/customer-app
npm run build

# Deploy
npm run start

# Verify pages
# http://localhost:3000/gold-lending/reporting/builder
# http://localhost:3000/gold-lending/reporting/catalog
# http://localhost:3000/gold-lending/reporting/schedules
```

### 10.4 Configuration

**Environment Variables:**
```bash
REPORT_STORAGE_PATH=/var/reports
REPORT_TEMP_PATH=/tmp/reports
REPORT_MAX_SIZE_MB=100
REPORT_RETENTION_DAYS=90
SMTP_SERVER=smtp.company.com
SMTP_PORT=587
```

---

## Appendix A: Sample Queries

### Generate Portfolio Report
```python
response = requests.post(
    'http://localhost:8013/api/v1/gold/reporting/generate',
    json={
        'report_code': 'RPT_PORTFOLIO_SUMMARY',
        'parameters': {
            'date_from': '2026-01-01',
            'date_to': '2026-01-31',
            'branch_id': 'BR001'
        },
        'output_format': 'pdf'
    }
)
```

### Query Analytics
```python
response = requests.post(
    'http://localhost:8013/api/v1/gold/reporting/analytics/query',
    json={
        'metric_codes': ['MTR_TOTAL_PORTFOLIO', 'MTR_ACTIVE_LOANS', 'MTR_NPA_RATIO'],
        'date_from': '2026-01-01',
        'date_to': '2026-06-30',
        'group_by': 'month'
    }
)
```

---

## Appendix B: Troubleshooting

### Common Issues

**Issue:** Report generation fails
**Solution:** Check query_template syntax, verify data_source exists

**Issue:** Schedule not executing
**Solution:** Verify next_execution_at is in future, check status is 'active'

**Issue:** Dashboard not loading
**Solution:** Verify widgets are visible, check data source queries

**Issue:** Slow report generation
**Solution:** Add filters, limit date range, optimize query_template

---

**Document Version:** 1.0  
**Last Updated:** July 3, 2026  
**Total Pages:** ~25
