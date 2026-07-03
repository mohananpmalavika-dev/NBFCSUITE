# Phase 8: Collections & Recovery Management

## Overview

Phase 8 implements a comprehensive collections and recovery system for managing overdue loans, conducting field visits, legal proceedings, and auction management. This enterprise-grade system rivals solutions from Oracle FLEXCUBE, Mambu, and Newgen with AI-powered workflows and complete audit trails.

## Table of Contents

1. [Architecture](#architecture)
2. [Database Schema](#database-schema)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Business Logic](#business-logic)
6. [Frontend Components](#frontend-components)
7. [Security & Compliance](#security--compliance)
8. [Integration Points](#integration-points)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Collections & Recovery                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Collection  │  │    Field     │  │   Payment    │      │
│  │    Cases     │  │   Visits     │  │   Promises   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Recovery   │  │    Legal     │  │   Auction    │      │
│  │   Actions    │  │   Notices    │  │  Management  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Communication │  │  Settlement  │  │ Performance  │      │
│  │     Logs     │  │   Offers     │  │  Tracking    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 14+ with advanced indexing
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **API**: RESTful with 53 endpoints
- **Authentication**: JWT-based with role-based access control

---

## Database Schema

### 1. Collection Cases (`gold_collection_cases`)

Tracks overdue loans under collection management.

```sql
CREATE TABLE gold_collection_cases (
    id UUID PRIMARY KEY,
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id),
    case_number VARCHAR(50) NOT NULL UNIQUE,
    case_status VARCHAR(20) NOT NULL DEFAULT 'open',
    bucket_type VARCHAR(20) NOT NULL,  -- DPD buckets
    overdue_days INTEGER NOT NULL,
    overdue_amount DECIMAL(15,2) NOT NULL,
    total_outstanding DECIMAL(15,2) NOT NULL,
    principal_overdue DECIMAL(15,2) NOT NULL,
    interest_overdue DECIMAL(15,2) NOT NULL,
    penalty_overdue DECIMAL(15,2) NOT NULL,
    assigned_to_user_id UUID NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    last_contact_date DATE,
    next_action_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Bucket Types**:
- `dpd_0_30`: 0-30 days past due
- `dpd_31_60`: 31-60 days past due
- `dpd_61_90`: 61-90 days past due
- `dpd_90_plus`: 90+ days past due
- `npa`: Non-Performing Asset

**Case Statuses**: `open`, `in_progress`, `legal`, `npa`, `closed`, `settled`

**Priorities**: `low`, `medium`, `high`, `critical`

### 2. Collection Activities (`gold_collection_activities`)

Tracks all collection follow-up activities.

```sql
CREATE TABLE gold_collection_activities (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    activity_type VARCHAR(30) NOT NULL,
    activity_date DATE NOT NULL,
    contact_mode VARCHAR(20) NOT NULL,
    disposition VARCHAR(30) NOT NULL,
    discussion_summary TEXT,
    amount_promised DECIMAL(15,2),
    promise_date DATE,
    performed_by_user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Activity Types**: `call`, `sms`, `email`, `whatsapp`, `field_visit`, `legal_notice`, `payment_received`

**Dispositions**: `contacted`, `not_reachable`, `promised_to_pay`, `partial_payment`, `dispute`, `refused`, `legal_action`, `settled`

### 3. Field Visits (`gold_field_visits`)

Tracks customer field visits and outcomes.

```sql
CREATE TABLE gold_field_visits (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    visit_number VARCHAR(30) NOT NULL UNIQUE,
    visit_date DATE NOT NULL,
    visit_type VARCHAR(30) NOT NULL,
    visit_status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    field_officer_id UUID NOT NULL,
    visit_address TEXT NOT NULL,
    customer_met BOOLEAN DEFAULT FALSE,
    amount_collected DECIMAL(15,2),
    visit_outcome VARCHAR(30),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Visit Types**: `courtesy`, `reminder`, `demand`, `legal`, `repossession`, `verification`

**Visit Outcomes**: `payment_collected`, `promise_obtained`, `customer_absent`, `dispute`, `legal_required`, `settled`

### 4. Payment Promises (`gold_payment_promises`)

Tracks customer payment commitments.

```sql
CREATE TABLE gold_payment_promises (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    promise_number VARCHAR(30) NOT NULL UNIQUE,
    promise_date DATE NOT NULL,
    promised_amount DECIMAL(15,2) NOT NULL,
    promised_payment_date DATE NOT NULL,
    promise_type VARCHAR(20) NOT NULL,
    promise_status VARCHAR(20) NOT NULL DEFAULT 'active',
    amount_received DECIMAL(15,2) DEFAULT 0,
    fulfillment_percentage DECIMAL(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Promise Statuses**: `active`, `kept`, `broken`, `partial`, `cancelled`

### 5. Recovery Actions (`gold_recovery_actions`)

Tracks recovery and repossession activities.

```sql
CREATE TABLE gold_recovery_actions (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    action_number VARCHAR(30) NOT NULL UNIQUE,
    action_type VARCHAR(30) NOT NULL,
    action_date DATE NOT NULL,
    action_status VARCHAR(20) NOT NULL DEFAULT 'planned',
    action_description TEXT NOT NULL,
    assets_recovered TEXT,
    estimated_value DECIMAL(15,2),
    police_assistance BOOLEAN DEFAULT FALSE,
    outcome VARCHAR(30),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Action Types**: `reminder`, `notice`, `repossession`, `seizure`, `auction_prep`, `legal_filing`, `settlement`

### 6. Legal Notices (`gold_legal_notices`)

Manages legal notices and demand letters.

```sql
CREATE TABLE gold_legal_notices (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    notice_number VARCHAR(50) NOT NULL UNIQUE,
    notice_type VARCHAR(30) NOT NULL,
    notice_date DATE NOT NULL,
    notice_status VARCHAR(20) NOT NULL DEFAULT 'draft',
    demand_amount DECIMAL(15,2) NOT NULL,
    response_deadline DATE NOT NULL,
    delivery_mode VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Notice Types**: `reminder`, `demand`, `final_demand`, `legal_action`, `arbitration`, `suit_filing`, `auction_notice`

### 7. Auction Management

#### Auction Lots (`gold_auction_lots`)

```sql
CREATE TABLE gold_auction_lots (
    id UUID PRIMARY KEY,
    lot_number VARCHAR(50) NOT NULL UNIQUE,
    auction_date DATE NOT NULL,
    lot_status VARCHAR(20) NOT NULL DEFAULT 'planned',
    total_gold_weight DECIMAL(10,3) NOT NULL,
    reserve_price DECIMAL(15,2) NOT NULL,
    winning_bid_amount DECIMAL(15,2),
    bid_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### Auction Bids (`gold_auction_bids`)

```sql
CREATE TABLE gold_auction_bids (
    id UUID PRIMARY KEY,
    auction_lot_id UUID NOT NULL REFERENCES gold_auction_lots(id),
    bid_number VARCHAR(30) NOT NULL UNIQUE,
    bidder_id UUID NOT NULL,
    bid_amount DECIMAL(15,2) NOT NULL,
    bid_status VARCHAR(20) NOT NULL DEFAULT 'active',
    is_winning_bid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 8. Communication Logs (`gold_communication_logs`)

Comprehensive communication history.

```sql
CREATE TABLE gold_communication_logs (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    communication_type VARCHAR(20) NOT NULL,
    communication_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    direction VARCHAR(10) NOT NULL,
    message_content TEXT,
    communication_status VARCHAR(20) NOT NULL DEFAULT 'sent',
    response_received BOOLEAN DEFAULT FALSE
);
```

### 9. Settlement Offers (`gold_settlement_offers`)

Tracks settlement negotiations.

```sql
CREATE TABLE gold_settlement_offers (
    id UUID PRIMARY KEY,
    collection_case_id UUID NOT NULL REFERENCES gold_collection_cases(id),
    offer_number VARCHAR(30) NOT NULL UNIQUE,
    total_outstanding DECIMAL(15,2) NOT NULL,
    settlement_amount DECIMAL(15,2) NOT NULL,
    waiver_amount DECIMAL(15,2) NOT NULL,
    offer_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 10. Collection Performance (`gold_collection_performance`)

Team and individual performance metrics.

```sql
CREATE TABLE gold_collection_performance (
    id UUID PRIMARY KEY,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    user_id UUID NOT NULL,
    total_cases_assigned INTEGER DEFAULT 0,
    total_cases_resolved INTEGER DEFAULT 0,
    total_collected_amount DECIMAL(15,2) DEFAULT 0,
    collection_percentage DECIMAL(5,2),
    performance_rating VARCHAR(20),
    incentive_earned DECIMAL(10,2)
);
```

### Database Views

#### Active Collection Cases Summary

```sql
CREATE OR REPLACE VIEW vw_active_collection_cases AS
SELECT 
    cc.id,
    cc.case_number,
    cc.bucket_type,
    cc.overdue_amount,
    COUNT(DISTINCT ca.id) as total_activities,
    COUNT(DISTINCT fv.id) as total_field_visits,
    MAX(ca.activity_date) as last_activity_date
FROM gold_collection_cases cc
LEFT JOIN gold_collection_activities ca ON cc.id = ca.collection_case_id
LEFT JOIN gold_field_visits fv ON cc.id = fv.collection_case_id
WHERE cc.case_status IN ('open', 'in_progress', 'legal')
GROUP BY cc.id;
```

#### Collection Dashboard

```sql
CREATE OR REPLACE VIEW vw_collection_dashboard AS
SELECT 
    cc.bucket_type,
    COUNT(DISTINCT cc.id) as total_cases,
    SUM(cc.total_outstanding) as total_outstanding,
    SUM(cc.overdue_amount) as total_overdue,
    COUNT(DISTINCT ln.id) as total_legal_notices
FROM gold_collection_cases cc
LEFT JOIN gold_legal_notices ln ON cc.id = ln.collection_case_id
GROUP BY cc.bucket_type;
```

### Database Triggers

#### Update Case on Activity

```sql
CREATE OR REPLACE FUNCTION update_collection_case_on_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE gold_collection_cases
    SET last_contact_date = NEW.activity_date,
        next_action_date = NEW.next_followup_date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.collection_case_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## API Endpoints

### Base URL
```
/api/v1/gold/collections
```

### Collection Cases

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/cases` | Create new collection case |
| GET | `/cases` | List all collection cases with filters |
| GET | `/cases/{case_id}` | Get specific case details |
| PATCH | `/cases/{case_id}` | Update case status/details |
| DELETE | `/cases/{case_id}` | Delete collection case |
| GET | `/cases/{case_id}/statistics` | Get case statistics |
| GET | `/cases/{case_id}/timeline` | Get complete case timeline |

### Collection Activities

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/activities` | Log new activity |
| GET | `/activities` | List activities with filters |
| GET | `/activities/{activity_id}` | Get activity details |
| DELETE | `/activities/{activity_id}` | Delete activity |

### Field Visits

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/field-visits` | Schedule field visit |
| GET | `/field-visits` | List all field visits |
| GET | `/field-visits/{visit_id}` | Get visit details |
| PATCH | `/field-visits/{visit_id}` | Update visit status |
| DELETE | `/field-visits/{visit_id}` | Cancel field visit |

### Payment Promises

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payment-promises` | Record payment promise |
| GET | `/payment-promises` | List all promises |
| GET | `/payment-promises/{promise_id}` | Get promise details |
| PATCH | `/payment-promises/{promise_id}` | Update promise status |
| DELETE | `/payment-promises/{promise_id}` | Delete promise |

### Recovery Actions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recovery-actions` | Create recovery action |
| GET | `/recovery-actions` | List all actions |
| GET | `/recovery-actions/{action_id}` | Get action details |
| PATCH | `/recovery-actions/{action_id}` | Update action |
| DELETE | `/recovery-actions/{action_id}` | Delete action |

### Legal Notices

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/legal-notices` | Create legal notice |
| GET | `/legal-notices` | List all notices |
| GET | `/legal-notices/{notice_id}` | Get notice details |
| PATCH | `/legal-notices/{notice_id}` | Update notice |
| DELETE | `/legal-notices/{notice_id}` | Delete notice |

### Auction Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auction-lots` | Create auction lot |
| GET | `/auction-lots` | List all lots |
| GET | `/auction-lots/{lot_id}` | Get lot details |
| PATCH | `/auction-lots/{lot_id}` | Update lot |
| POST | `/auction-bids` | Place bid |
| GET | `/auction-bids` | List all bids |

### Dashboard & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Get collection dashboard metrics |

---

## Data Models

### Collection Case Model

```python
class CollectionCase(Base):
    __tablename__ = "gold_collection_cases"
    
    id = Column(UUID, primary_key=True)
    loan_account_id = Column(UUID, ForeignKey("gold_loan_accounts.id"))
    case_number = Column(String(50), unique=True)
    case_status = Column(String(20), default="open")
    bucket_type = Column(String(20))
    overdue_days = Column(Integer)
    overdue_amount = Column(Numeric(15, 2))
    total_outstanding = Column(Numeric(15, 2))
    assigned_to_user_id = Column(UUID)
    priority = Column(String(20), default="medium")
    
    # Relationships
    activities = relationship("CollectionActivity", back_populates="collection_case")
    field_visits = relationship("FieldVisit", back_populates="collection_case")
    payment_promises = relationship("PaymentPromise", back_populates="collection_case")
```

---

## Business Logic

### Collection Case Lifecycle

```
┌────────┐     ┌─────────────┐     ┌────────┐     ┌────────┐
│  Open  │────>│ In Progress │────>│ Legal  │────>│  NPA   │
└────────┘     └─────────────┘     └────────┘     └────────┘
    │                  │                               │
    │                  │                               │
    └──────────────────┴───────────────────────────────┴────>┌─────────┐
                                                               │ Closed  │
                                                               └─────────┘
```

### DPD Bucket Assignment

```python
def assign_bucket(overdue_days: int) -> str:
    if overdue_days <= 30:
        return "dpd_0_30"
    elif overdue_days <= 60:
        return "dpd_31_60"
    elif overdue_days <= 90:
        return "dpd_61_90"
    elif overdue_days <= 180:
        return "dpd_90_plus"
    else:
        return "npa"
```

### Priority Assignment

```python
def assign_priority(overdue_amount: Decimal, overdue_days: int) -> str:
    if overdue_days > 90 or overdue_amount > 100000:
        return "critical"
    elif overdue_days > 60 or overdue_amount > 50000:
        return "high"
    elif overdue_days > 30:
        return "medium"
    else:
        return "low"
```

---

## Frontend Components

### 1. Collection Cases Dashboard
- **Route**: `/gold-lending/collections/cases`
- **Features**: Case listing, filters, status updates, bucket visualization
- **Components**: Status badges, priority indicators, action buttons

### 2. Field Visits Management
- **Route**: `/gold-lending/collections/field-visits`
- **Features**: Visit scheduling, GPS tracking, outcome recording
- **Components**: Calendar view, visit forms, expense tracking

### 3. Payment Promises
- **Route**: `/gold-lending/collections/promises`
- **Features**: Promise recording, fulfillment tracking, reminders
- **Components**: Promise timeline, fulfillment gauge

### 4. Legal Notices
- **Route**: `/gold-lending/collections/legal-notices`
- **Features**: Notice creation, tracking, delivery status
- **Components**: Notice templates, delivery tracking

### 5. Auction Management
- **Route**: `/gold-lending/collections/auctions`
- **Features**: Lot creation, bidding, winner selection
- **Components**: Auction calendar, bid history, lot details

### 6. Recovery Actions
- **Route**: `/gold-lending/collections/recovery`
- **Features**: Action planning, execution tracking, outcome recording
- **Components**: Action timeline, approval workflow

### 7. Communication Logs
- **Route**: `/gold-lending/collections/communication`
- **Features**: Complete communication history, multi-channel logging
- **Components**: Communication feed, response tracking

### 8. Performance Dashboard
- **Route**: `/gold-lending/collections/performance`
- **Features**: Team metrics, KPIs, incentive tracking
- **Components**: Performance cards, leaderboard, charts

---

## Security & Compliance

### Access Control

```python
# Role-based access
PERMISSIONS = {
    "collection_officer": ["read_cases", "create_activities", "schedule_visits"],
    "collection_manager": ["read_cases", "update_cases", "approve_settlements"],
    "legal_team": ["read_cases", "create_notices", "update_legal"],
    "admin": ["all"]
}
```

### Audit Trail

Every action is logged with:
- User ID and timestamp
- Action type and details
- Previous and new values
- IP address and location

### Data Privacy

- PII encryption at rest
- Role-based data masking
- Compliance with GDPR/local regulations
- Secure communication channels

---

## Integration Points

### 1. Loan Management System (LMS)
- **Direction**: Bidirectional
- **Data**: Overdue loan identification, payment updates
- **Frequency**: Real-time

### 2. Core Banking System
- **Direction**: Inbound
- **Data**: Customer details, account status
- **Frequency**: On-demand

### 3. SMS/Email Gateway
- **Direction**: Outbound
- **Data**: Notifications, reminders, notices
- **Frequency**: Real-time

### 4. Payment Gateway
- **Direction**: Inbound
- **Data**: Collection receipts, payment confirmations
- **Frequency**: Real-time

### 5. Credit Bureau
- **Direction**: Outbound
- **Data**: NPA reporting, credit updates
- **Frequency**: Monthly

---

## Performance Metrics

### Database Performance
- Indexed queries: < 50ms
- Complex aggregations: < 200ms
- Concurrent users: 500+

### API Performance
- Average response time: < 100ms
- P95 response time: < 300ms
- Throughput: 1000 req/s

### Frontend Performance
- Initial load: < 2s
- Page transitions: < 500ms
- Time to interactive: < 3s

---

## Deployment

### Database Migration

```bash
# Run migration
alembic upgrade head

# Verify migration
psql -d nbfcsuite -c "SELECT COUNT(*) FROM gold_collection_cases;"
```

### API Deployment

```bash
# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8013

# Health check
curl http://localhost:8013/health
```

### Frontend Deployment

```bash
# Build
npm run build

# Start
npm run start
```

---

## Monitoring & Maintenance

### Key Metrics to Monitor
1. Collection efficiency rate
2. Average resolution time
3. Promise fulfillment rate
4. Legal notice effectiveness
5. Field visit success rate

### Alerts
- Overdue cases > 90 days
- High-value cases unassigned
- Legal notice response deadlines
- Auction lot payment deadlines

---

## Future Enhancements

1. **AI-Powered Prioritization**: Machine learning for case assignment
2. **Predictive Analytics**: Default probability scoring
3. **Mobile App**: Field officer mobile application
4. **Automated Workflows**: Rule-based action triggers
5. **WhatsApp Integration**: Two-way communication via WhatsApp Business API

---

## Support & Documentation

For additional support:
- Technical Documentation: This file
- API Documentation: Swagger UI at `/docs`
- Quick Start Guide: `GETTING_STARTED_PHASE8.md`
- Issue Tracker: GitHub Issues

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-03  
**Maintained By**: NBFC Suite Development Team
