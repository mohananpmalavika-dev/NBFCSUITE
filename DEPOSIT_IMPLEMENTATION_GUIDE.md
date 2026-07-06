# DEPOSIT MANAGEMENT - IMPLEMENTATION GUIDE

## 🎯 Quick Start Guide

### Prerequisites
```bash
# Python 3.11+
python --version

# Install dependencies
pip install reportlab openpyxl fastapi sqlalchemy pydantic
```

### Step-by-Step Implementation

#### **Step 1: Database Setup**

Run migrations to create new tables:
```bash
cd backend
alembic revision --autogenerate -m "Add deposit advanced features"
alembic upgrade head
```

New tables created:
- `deposit_standing_instructions`
- `deposit_account_freezes`
- `deposit_account_liens`
- `deposit_joint_holders`

---

#### **Step 2: Update Main Application Router**

Edit `backend/main.py`:

```python
from backend.services.deposit import (
    product_router,
    account_router,
    interest_router,
    passbook_router,
    statement_router,
    certificate_router,
    batch_router,
    reports_router
)

# Add all deposit routers
app.include_router(product_router, prefix="/api/v1/deposit", tags=["Deposit Products"])
app.include_router(account_router, prefix="/api/v1/deposit", tags=["Deposit Accounts"])
app.include_router(interest_router, prefix="/api/v1/deposit", tags=["Interest Management"])
app.include_router(passbook_router, prefix="/api/v1/deposit", tags=["Passbook"])
app.include_router(statement_router, prefix="/api/v1/deposit", tags=["Statements"])
app.include_router(certificate_router, prefix="/api/v1/deposit", tags=["Certificates"])
app.include_router(batch_router, prefix="/api/v1/deposit", tags=["Batch Operations"])
app.include_router(reports_router, prefix="/api/v1/deposit", tags=["Reports"])
```

---

#### **Step 3: Configure Scheduled Jobs**

**Option A: Using APScheduler (Recommended)**

Create `backend/scheduler.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from backend.services.deposit.scheduled_jobs import DepositScheduledJobs
from backend.shared.database.connection import SessionLocal

scheduler = BackgroundScheduler()

def run_daily_jobs():
    db = SessionLocal()
    try:
        jobs = DepositScheduledJobs(tenant_id=1)
        result = jobs.run_daily_jobs(db)
        print(f"Daily jobs completed: {result}")
    finally:
        db.close()

def run_monthly_jobs():
    db = SessionLocal()
    try:
        jobs = DepositScheduledJobs(tenant_id=1)
        result = jobs.run_monthly_jobs(db)
        print(f"Monthly jobs completed: {result}")
    finally:
        db.close()

# Schedule jobs
scheduler.add_job(run_daily_jobs, 'cron', hour=6, minute=0)  # 6:00 AM daily
scheduler.add_job(run_monthly_jobs, 'cron', day=1, hour=2, minute=0)  # 2:00 AM on 1st

scheduler.start()
```

Add to `main.py`:
```python
from backend.scheduler import scheduler

@app.on_event("startup")
async def startup_event():
    # Start scheduler
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
```

**Option B: Using System Cron**

```bash
# Edit crontab
crontab -e

# Add these lines:
0 6 * * * cd /path/to/project && python -m backend.services.deposit.scheduled_jobs daily
0 2 1 * * cd /path/to/project && python -m backend.services.deposit.scheduled_jobs monthly
0 23 31 3,6,9,12 * cd /path/to/project && python -m backend.services.deposit.scheduled_jobs quarterly 2024-2025 1
```

---

#### **Step 4: Configure Email/SMS Services**

Create `backend/shared/services/notification_provider.py`:

```python
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    """Email service implementation"""
    
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"  # Configure
        self.smtp_port = 587
        self.smtp_user = "your-email@gmail.com"
        self.smtp_password = "your-password"
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: List[Dict[str, Any]] = None
    ):
        """Send email"""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachments if any
        if attachments:
            for attachment in attachments:
                # Add attachment logic
                pass
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)


class SMSService:
    """SMS service implementation"""
    
    def send_sms(self, phone: str, message: str):
        """Send SMS via Twilio/AWS SNS"""
        # Implement SMS sending
        pass
```

---

#### **Step 5: Test API Endpoints**

Start the server:
```bash
uvicorn backend.main:app --reload
```

Open Swagger UI:
```
http://localhost:8000/docs
```

Test key endpoints:
1. Create deposit product
2. Open account
3. Make deposit
4. Generate passbook PDF
5. Generate statement
6. Run batch maturity processing
7. View reports dashboard

---

## 📊 Feature Usage Examples

### Example 1: Complete Deposit Flow

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/deposit"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 1. Create FD Product
product = requests.post(
    f"{BASE_URL}/product",
    headers=headers,
    json={
        "product_code": "FD-12M-7.5",
        "product_name": "12 Month Fixed Deposit - 7.5%",
        "product_type": "fd",
        "interest_rate": 7.5,
        "interest_calculation_method": "compound",
        "interest_calculation_frequency": "quarterly",
        "min_tenure_days": 365,
        "max_tenure_days": 365,
        "min_deposit_amount": 10000,
        "premature_withdrawal_allowed": true,
        "premature_withdrawal_penalty": 1.0,
        "tds_applicable": true
    }
).json()

# 2. Open Account
account = requests.post(
    f"{BASE_URL}/account",
    headers=headers,
    json={
        "customer_id": 123,
        "deposit_product_id": product['id'],
        "principal_amount": 100000,
        "tenure_days": 365,
        "auto_renewal": false,
        "nominee_name": "John Doe",
        "nominee_relationship": "Spouse"
    }
).json()

# 3. Generate Passbook PDF
pdf = requests.get(
    f"{BASE_URL}/passbook/{account['id']}/pdf",
    headers=headers
)

# 4. Get Dashboard
dashboard = requests.get(
    f"{BASE_URL}/reports/dashboard",
    headers=headers
).json()
```

### Example 2: Batch Operations

```python
# Process Maturities
maturity_result = requests.post(
    f"{BASE_URL}/batch/maturity/process",
    headers=headers,
    params={"days_ahead": 0}
).json()

# Apply Penalties
penalty_result = requests.post(
    f"{BASE_URL}/batch/penalties/apply",
    headers=headers,
    params={"penalty_type": "rd_missed"}
).json()

# Process MIS Payouts
mis_result = requests.post(
    f"{BASE_URL}/batch/mis-payout/process",
    headers=headers
).json()
```

### Example 3: Reports

```python
from datetime import date, timedelta

# Get Maturity Calendar
calendar = requests.get(
    f"{BASE_URL}/reports/maturity-calendar",
    headers=headers,
    params={
        "from_date": date.today().isoformat(),
        "to_date": (date.today() + timedelta(days=30)).isoformat()
    }
).json()

# Get Interest Accrual
accrual = requests.get(
    f"{BASE_URL}/reports/interest-accrual",
    headers=headers,
    params={
        "from_date": "2025-01-01",
        "to_date": "2025-01-31"
    }
).json()

# Get Compliance Dashboard
compliance = requests.get(
    f"{BASE_URL}/regulatory/compliance-dashboard",
    headers=headers
).json()
```

---

## 🔐 Security Configuration

### JWT Authentication

Ensure all endpoints require authentication:

```python
from fastapi import Depends
from backend.services.auth.dependencies import get_current_user

@router.get("/protected-endpoint")
async def protected_route(
    current_user: dict = Depends(get_current_user)
):
    # Access user info
    tenant_id = current_user['tenant_id']
    user_id = current_user['user_id']
    # ... business logic
```

### Rate Limiting

Add rate limiting for batch operations:

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@router.post("/batch/maturity/process")
@limiter.limit("5/hour")  # 5 requests per hour
async def process_maturity(
    request: Request,
    db: Session = Depends(get_db)
):
    # Process maturity
    pass
```

---

## 📈 Performance Optimization

### Database Indexing

Add indexes for frequently queried fields:

```sql
-- Add indexes
CREATE INDEX idx_deposit_account_customer ON deposit_accounts(customer_id, tenant_id);
CREATE INDEX idx_deposit_account_status ON deposit_accounts(status, tenant_id);
CREATE INDEX idx_deposit_account_maturity ON deposit_accounts(maturity_date, tenant_id);
CREATE INDEX idx_deposit_transaction_date ON deposit_transactions(transaction_date, deposit_account_id);
CREATE INDEX idx_deposit_transaction_type ON deposit_transactions(transaction_type, tenant_id);
```

### Caching Strategy

Implement Redis caching for reports:

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_report(ttl=3600):
    """Cache report for 1 hour"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"report:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_report(ttl=1800)  # 30 minutes
def get_dashboard(db: Session, tenant_id: int):
    # Generate dashboard
    pass
```

---

## 🧪 Testing

### Unit Tests Example

Create `tests/test_deposit_passbook.py`:

```python
import pytest
from datetime import date
from backend.services.deposit.passbook_service import PassbookService

def test_get_passbook_entries(db_session):
    service = PassbookService(db_session, tenant_id=1, user_id=1)
    
    # Test getting entries
    result = service.get_passbook_entries(
        account_id=1,
        from_date=date(2025, 1, 1),
        to_date=date(2025, 1, 31)
    )
    
    assert 'entries' in result
    assert 'total_count' in result

def test_generate_passbook_pdf(db_session):
    service = PassbookService(db_session, tenant_id=1, user_id=1)
    
    # Test PDF generation
    result = service.generate_passbook_pdf(account_id=1)
    
    assert 'pdf_content' in result
    assert 'filename' in result
    assert result['filename'].endswith('.pdf')
```

Run tests:
```bash
pytest tests/ -v --cov=backend/services/deposit
```

---

## 📝 Monitoring & Logging

### Add Logging

```python
import logging

logger = logging.getLogger(__name__)

# In service methods
logger.info(f"Processing maturity for account {account_id}")
logger.error(f"Failed to process maturity: {str(e)}")
logger.warning(f"Account {account_id} has insufficient balance")
```

### Health Checks

Add health check endpoint:

```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database
        db.execute("SELECT 1")
        
        # Check Redis
        redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cache": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

## 🚀 Deployment Checklist

### Pre-deployment

- [ ] All migrations run successfully
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Email/SMS services configured
- [ ] Scheduled jobs configured
- [ ] Database indexes added
- [ ] Redis configured (optional)
- [ ] Logging configured
- [ ] Monitoring setup

### Production Settings

```python
# .env.production
DATABASE_URL=postgresql://user:pass@prod-db:5432/nbfc
REDIS_URL=redis://prod-redis:6379/0
EMAIL_SERVICE=sendgrid
EMAIL_API_KEY=your-key
SMS_SERVICE=twilio
SMS_API_KEY=your-key
ENVIRONMENT=production
DEBUG=false
```

### Deployment Commands

```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart nbfc-api
sudo systemctl restart nbfc-scheduler

# Check status
sudo systemctl status nbfc-api
sudo systemctl status nbfc-scheduler
```

---

## 📚 Additional Resources

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Database Schema
- See `backend/shared/database/deposit_models.py`

### Service Documentation
- See docstrings in each service file

### Support
- Internal documentation: `/docs/deposit_management/`
- Technical support: tech-support@company.com

---

## ✅ Success Criteria

You'll know the implementation is successful when:

1. ✅ All API endpoints return 200 status
2. ✅ Passbook PDF generates correctly
3. ✅ Statement generation works (PDF & Excel)
4. ✅ Certificates generate properly
5. ✅ Batch jobs run without errors
6. ✅ Reports load within 2 seconds
7. ✅ Notifications send successfully
8. ✅ Scheduled jobs execute on time
9. ✅ Database queries are optimized
10. ✅ No security vulnerabilities

---

*Implementation Guide Version 1.0*
*Last Updated: January 2026*
*Status: Production Ready*
