# Notification Service - Design Document

**Module**: Notification Service  
**Version**: 1.0  
**Date**: July 5, 2026  
**Status**: 🚧 In Progress - FINAL MODULE!  

---

## 📋 EXECUTIVE SUMMARY

The Notification Service is a multi-channel communication system that sends SMS, Email, and WhatsApp notifications to customers. It provides template management, delivery tracking, retry mechanisms, and priority queuing.

### Key Capabilities
- Multi-channel support (SMS, Email, WhatsApp)
- Dynamic template management with variables
- Delivery status tracking
- Priority-based queuing
- Automatic retry on failure
- Scheduled notifications
- Bulk notification support
- Complete audit trail

---

## 🎯 BUSINESS OBJECTIVES

### Primary Goals
1. **Reliability**: 99.9% delivery success rate
2. **Speed**: Send notifications within 30 seconds
3. **Scalability**: Handle 10,000+ notifications/hour
4. **Flexibility**: Easy template management
5. **Tracking**: Complete delivery visibility

### Use Cases
1. **Loan Application Notifications**
   - Application received confirmation
   - Approval/rejection notification
   - Disbursement notification
   - EMI reminders

2. **Payment Reminders**
   - Due date reminders (3 days before)
   - Overdue notifications
   - Payment received confirmation

3. **Account Notifications**
   - Account activation
   - Password reset
   - OTP for verification
   - Statement generation

4. **Marketing Notifications**
   - Pre-approved offers
   - Product promotions
   - Seasonal campaigns

5. **System Notifications**
   - Document upload reminders
   - KYC completion reminders
   - Application status updates

---

## 🏗️ ARCHITECTURE

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                 Notification Service                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Notification │  │   Template   │  │    Queue     │  │
│  │   Service    │  │   Service    │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │     SMS      │  │    Email     │  │  WhatsApp    │  │
│  │   Provider   │  │   Provider   │  │   Provider   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  External   │ │   SMTP      │ │  WhatsApp   │
    │  SMS API    │ │   Server    │ │ Business API│
    └─────────────┘ └─────────────┘ └─────────────┘
```

### Integration Points
- **All Modules**: Can send notifications
- **Customer Module**: Recipient details
- **Loan Module**: Loan-related notifications
- **Workflow Module**: Workflow event notifications
- **External APIs**: SMS/WhatsApp gateways

---

## 📊 DATABASE SCHEMA

### 1. NotificationTemplate
Template definitions for different notification types.

```python
class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    template_code = Column(String(50), unique=True, nullable=False)
    
    # Template Details
    template_name = Column(String(200), nullable=False)
    channel = Column(String(20), nullable=False)  # sms, email, whatsapp
    category = Column(String(50), nullable=False)  # transactional, marketing, otp
    
    # Content
    subject = Column(String(500), nullable=True)  # For email
    body_template = Column(Text, nullable=False)  # Template with {{variables}}
    
    # Variables
    variables = Column(JSON, nullable=True)  # List of allowed variables
    # ["customer_name", "loan_amount", "due_date"]
    
    # Configuration
    priority = Column(String(20), default="medium")  # high, medium, low
    retry_enabled = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
```

### 2. Notification
Individual notification records.

```python
class Notification(Base):
    __tablename__ = "notifications"
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    notification_number = Column(String(50), unique=True, nullable=False)
    
    # Template
    template_id = Column(Integer, nullable=True)  # NULL for ad-hoc
    template_code = Column(String(50), nullable=True)
    
    # Channel & Priority
    channel = Column(String(20), nullable=False)  # sms, email, whatsapp
    priority = Column(String(20), default="medium")  # high, medium, low
    
    # Recipient
    recipient_type = Column(String(50), nullable=False)  # customer, user, admin
    recipient_id = Column(Integer, nullable=False)
    recipient_contact = Column(String(200), nullable=False)  # phone or email
    recipient_name = Column(String(200), nullable=True)
    
    # Content
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Actual values used
    
    # Entity Reference
    entity_type = Column(String(50), nullable=True)  # loan, customer, etc.
    entity_id = Column(Integer, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default="pending")
    # pending, queued, sending, sent, failed, cancelled
    
    # Delivery
    delivery_status = Column(String(50), nullable=True)
    # delivered, failed, bounced, undelivered
    delivery_time = Column(DateTime, nullable=True)
    
    # Provider Response
    provider_id = Column(String(200), nullable=True)  # External ID
    provider_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Retry
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime, nullable=True)
    next_retry_at = Column(DateTime, nullable=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Audit
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3. NotificationQueue
Queue for batch processing.

```python
class NotificationQueue(Base):
    __tablename__ = "notification_queue"
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Notification Reference
    notification_id = Column(Integer, nullable=False, index=True)
    
    # Queue Details
    priority = Column(String(20), nullable=False)
    queue_time = Column(DateTime, default=datetime.utcnow)
    
    # Processing
    status = Column(String(50), default="queued")  # queued, processing, processed
    processed_at = Column(DateTime, nullable=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
```

### 4. NotificationLog
Detailed logs for troubleshooting.

```python
class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Notification Reference
    notification_id = Column(Integer, nullable=False, index=True)
    
    # Log Details
    event_type = Column(String(50), nullable=False)
    # created, queued, sending, sent, delivered, failed, retry
    event_time = Column(DateTime, default=datetime.utcnow)
    
    # Details
    message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
```

### 5. NotificationAnalytics
Aggregated metrics.

```python
class NotificationAnalytics(Base):
    __tablename__ = "notification_analytics"
    
    # Primary Key
    id = Column(Integer, primary_key=True)
    
    # Period
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)
    
    # Breakdown
    channel = Column(String(20), nullable=False)
    category = Column(String(50), nullable=True)
    
    # Metrics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_bounced = Column(Integer, default=0)
    
    # Rates
    delivery_rate = Column(Numeric(5, 2), default=0)
    failure_rate = Column(Numeric(5, 2), default=0)
    
    # Response Times
    avg_delivery_time_seconds = Column(Integer, default=0)
    
    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔧 SERVICE LAYER

### 1. NotificationService
Core notification management.

**Methods**:
- `send_notification(channel, recipient, subject, body)` - Send notification
- `send_from_template(template_code, recipient, variables)` - Send using template
- `schedule_notification(...)` - Schedule for later
- `cancel_notification(notification_id)` - Cancel pending
- `get_notification(notification_id)` - Get details
- `retry_notification(notification_id)` - Manual retry

### 2. TemplateService
Template management.

**Methods**:
- `create_template(data)` - Create template
- `update_template(template_id, data)` - Update
- `get_template(template_code)` - Get by code
- `render_template(template_code, variables)` - Render with variables
- `validate_variables(template_code, variables)` - Validate

### 3. QueueService
Queue management.

**Methods**:
- `enqueue(notification_id, priority)` - Add to queue
- `dequeue(batch_size)` - Get batch for processing
- `process_queue()` - Process pending notifications
- `get_queue_size()` - Current queue size

### 4. ProviderService
External provider integration.

**Methods**:
- `send_sms(phone, message)` - Send SMS
- `send_email(to, subject, body)` - Send email
- `send_whatsapp(phone, message)` - Send WhatsApp
- `get_delivery_status(provider_id)` - Check status

---

## 📡 API ENDPOINTS

### Template Management (6 endpoints)

```
POST   /notifications/templates       - Create template
GET    /notifications/templates       - List templates
GET    /notifications/templates/{id}  - Get template
PUT    /notifications/templates/{id}  - Update template
DELETE /notifications/templates/{id}  - Delete template
POST   /notifications/templates/test  - Test template
```

### Notification Operations (8 endpoints)

```
POST   /notifications/send            - Send notification
POST   /notifications/send-bulk       - Send bulk notifications
POST   /notifications/schedule        - Schedule notification
GET    /notifications                 - List notifications
GET    /notifications/{id}            - Get notification
POST   /notifications/{id}/cancel     - Cancel notification
POST   /notifications/{id}/retry      - Retry notification
GET    /notifications/recipient/{id}  - Recipient notifications
```

### Analytics (4 endpoints)

```
GET    /notifications/analytics/summary       - Overall summary
GET    /notifications/analytics/by-channel    - Channel breakdown
GET    /notifications/analytics/delivery-rate - Delivery rates
GET    /notifications/analytics/failed        - Failed notifications
```

**Total**: 18 endpoints

---

## 🔄 NOTIFICATION FLOW

### Send Flow

```
1. Create Notification
   ↓
2. Validate Recipient
   ↓
3. Render Template (if using template)
   ↓
4. Add to Queue (by priority)
   ↓
5. Process Queue (background worker)
   ↓
6. Select Provider
   ↓
7. Send via Provider API
   ↓
8. Update Status
   ↓
9. Log Event
   ↓
10. Record Analytics
```

### Retry Logic

```
If sending fails:
  - Check retry_enabled
  - Check retry_count < max_retries
  - Calculate next_retry_at (exponential backoff)
  - Re-queue notification
  - Log retry attempt
```

---

## 📝 TEMPLATE VARIABLES

### Common Variables
- `{{customer_name}}` - Customer name
- `{{customer_id}}` - Customer ID
- `{{mobile}}` - Mobile number
- `{{email}}` - Email address

### Loan Variables
- `{{loan_number}}` - Loan application number
- `{{loan_amount}}` - Loan amount
- `{{tenure}}` - Loan tenure
- `{{interest_rate}}` - Interest rate
- `{{emi}}` - Monthly EMI
- `{{due_date}}` - EMI due date

### Payment Variables
- `{{payment_amount}}` - Payment amount
- `{{payment_date}}` - Payment date
- `{{receipt_number}}` - Receipt number
- `{{outstanding}}` - Outstanding amount

---

## 🎯 SUCCESS CRITERIA

- ✅ 18 REST API endpoints
- ✅ Multi-channel support (SMS/Email/WhatsApp)
- ✅ Template management with variables
- ✅ Delivery tracking and retry
- ✅ Priority queuing
- ✅ Complete audit trail
- ✅ Analytics and reporting
- ✅ Multi-tenant support
- ✅ Production-ready code
- ✅ Complete documentation

---

## 📚 IMPLEMENTATION PHASES

### Phase 1: Foundation (30%)
- ✅ Design document
- ⏳ Database models
- ⏳ Pydantic schemas

### Phase 2: Core Services (40%)
- ⏳ NotificationService
- ⏳ TemplateService
- ⏳ QueueService
- ⏳ ProviderService

### Phase 3: API Layer (20%)
- ⏳ Template endpoints
- ⏳ Notification endpoints
- ⏳ Analytics endpoints

### Phase 4: Integration (10%)
- ⏳ Provider integration
- ⏳ Main.py registration

---

**Design Status**: ✅ Complete  
**Next Step**: Build database models  
**Target Completion**: Today (July 5, 2026)  
**Platform Impact**: 98% → 100% 🎉

---

*Design Document Created: July 5, 2026*  
*NBFC Financial Suite - Notification Service Module*  
*"The Final 2% - Reaching 100% Platform Completion"*
