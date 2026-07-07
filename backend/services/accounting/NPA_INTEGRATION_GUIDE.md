# NPA Management - Integration Guide

## Overview

This guide explains how to integrate the NPA Management module with other system components.

## Table of Contents

1. [LMS Integration](#lms-integration)
2. [Collections Integration](#collections-integration)
3. [Reporting Integration](#reporting-integration)
4. [Scheduled Jobs](#scheduled-jobs)
5. [Event-Driven Architecture](#event-driven-architecture)
6. [API Integration Examples](#api-integration-examples)

---

## LMS Integration

### 1. Fetch Loan Data for Classification

The NPA module needs loan account data from LMS to perform classification.

#### Required Data Points

```python
from backend.services.lms.loan_service import LoanService

async def get_loan_for_npa_classification(loan_account_id: int):
    """
    Fetch loan data required for NPA classification
    """
    loan_service = LoanService(db, tenant_id, user_id)
    loan = await loan_service.get_loan_account(loan_account_id)
    
    return {
        "loan_account_id": loan.id,
        "loan_account_number": loan.account_number,
        "customer_id": loan.customer_id,
        "customer_name": loan.customer.full_name,
        "outstanding_principal": loan.outstanding_principal,
        "outstanding_interest": loan.outstanding_interest,
        "days_past_due": loan.days_past_due,  # Calculated by LMS
        "last_payment_date": loan.last_payment_date,
        "is_secured": loan.is_secured,
        "security_value": loan.collateral_value,
        "loan_amount": loan.approved_amount,
        "disbursement_date": loan.disbursement_date,
        "maturity_date": loan.maturity_date,
        "is_restructured": loan.is_restructured,
        "is_written_off": loan.is_written_off
    }
```

#### Calculate Days Past Due (DPD)

The LMS should calculate DPD based on last payment due date:

```python
from datetime import date

def calculate_dpd(last_due_date: date, as_of_date: date = None) -> int:
    """
    Calculate Days Past Due
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    if last_due_date >= as_of_date:
        return 0  # Not overdue
    
    dpd = (as_of_date - last_due_date).days
    return dpd
```

### 2. Batch Classification Integration

```python
from backend.services.accounting.npa_service import NPAService
from backend.services.lms.loan_service import LoanService

async def classify_entire_portfolio(
    db: AsyncSession,
    tenant_id: int,
    user_id: int,
    as_of_date: date
):
    """
    Classify entire loan portfolio
    """
    loan_service = LoanService(db, tenant_id, user_id)
    npa_service = NPAService(db, tenant_id, user_id)
    
    # Get all active loans
    loans = await loan_service.get_active_loans()
    
    classifications = []
    
    for loan in loans:
        # Get DPD
        dpd = calculate_dpd(loan.last_due_date, as_of_date)
        
        # Classify
        npa_category = npa_service.classify_asset(
            days_past_due=dpd,
            is_restructured=loan.is_restructured,
            is_written_off=loan.is_written_off
        )
        
        # Calculate security coverage
        security_coverage = Decimal("0.00")
        if loan.is_secured and loan.outstanding_principal > 0:
            security_coverage = min(
                (loan.collateral_value / loan.outstanding_principal) * 100,
                Decimal("100.00")
            )
        
        # Calculate provisioning
        provisioning = npa_service.calculate_provisioning_amount(
            outstanding_principal=loan.outstanding_principal,
            npa_category=npa_category,
            is_secured=loan.is_secured,
            security_coverage_ratio=security_coverage,
            existing_provision=loan.provision_held
        )
        
        # Update loan record
        await loan_service.update_loan_classification(
            loan_id=loan.id,
            npa_category=npa_category.value,
            provision_required=provisioning["required_provision"],
            classification_date=as_of_date
        )
        
        # Create provision entry if needed
        if provisioning["additional_provision"] > 0:
            await npa_service.create_provisioning_entry(
                loan_account_id=loan.id,
                provision_amount=provisioning["additional_provision"],
                npa_category=npa_category,
                as_of_date=as_of_date
            )
        
        classifications.append({
            "loan_id": loan.id,
            "old_category": loan.npa_category,
            "new_category": npa_category.value,
            "provision_created": provisioning["additional_provision"]
        })
    
    return classifications
```

### 3. Update LMS Loan Model

Add NPA-related fields to the loan model:

```python
class LoanAccount(Base):
    __tablename__ = "loan_accounts"
    
    # ... existing fields ...
    
    # NPA Management fields
    days_past_due = Column(Integer, default=0)
    npa_category = Column(String(50), default="STANDARD")
    classification_date = Column(Date)
    provision_required = Column(Numeric(15, 2), default=0.00)
    provision_held = Column(Numeric(15, 2), default=0.00)
    is_restructured = Column(Boolean, default=False)
    is_written_off = Column(Boolean, default=False)
    write_off_date = Column(Date, nullable=True)
    write_off_amount = Column(Numeric(15, 2), nullable=True)
```

---

## Collections Integration

### 1. Trigger Collection Workflows

When a loan becomes NPA, trigger collection workflows:

```python
from backend.services.collection.strategy_service import CollectionStrategyService

async def trigger_npa_collection_workflow(
    loan_account_id: int,
    npa_category: NPACategory,
    outstanding_amount: Decimal
):
    """
    Trigger appropriate collection workflow based on NPA category
    """
    collection_service = CollectionStrategyService(db, tenant_id, user_id)
    
    if npa_category == NPACategory.SUBSTANDARD:
        # Assign to collection team
        await collection_service.assign_to_collection_team(
            loan_account_id=loan_account_id,
            priority="HIGH",
            strategy="SOFT_COLLECTION"
        )
    
    elif npa_category in [NPACategory.DOUBTFUL_1, NPACategory.DOUBTFUL_2]:
        # Escalate to field agents
        await collection_service.assign_to_field_agent(
            loan_account_id=loan_account_id,
            priority="CRITICAL",
            strategy="FIELD_VISIT"
        )
    
    elif npa_category == NPACategory.DOUBTFUL_3:
        # Legal action
        await collection_service.initiate_legal_action(
            loan_account_id=loan_account_id,
            action_type="NOTICE"
        )
    
    elif npa_category == NPACategory.LOSS:
        # Consider write-off
        await collection_service.recommend_write_off(
            loan_account_id=loan_account_id,
            outstanding_amount=outstanding_amount
        )
```

### 2. Update on Collections

When payments are received:

```python
async def process_npa_payment(
    loan_account_id: int,
    payment_amount: Decimal,
    payment_date: date
):
    """
    Process payment for NPA account and re-evaluate classification
    """
    loan_service = LoanService(db, tenant_id, user_id)
    npa_service = NPAService(db, tenant_id, user_id)
    
    # Record payment
    await loan_service.record_payment(
        loan_account_id=loan_account_id,
        payment_amount=payment_amount,
        payment_date=payment_date
    )
    
    # Recalculate DPD
    loan = await loan_service.get_loan_account(loan_account_id)
    new_dpd = calculate_dpd(loan.last_due_date, payment_date)
    
    # Re-classify if DPD improved
    old_category = loan.npa_category
    new_category = npa_service.classify_asset(
        days_past_due=new_dpd,
        is_restructured=loan.is_restructured,
        is_written_off=loan.is_written_off
    )
    
    if old_category != new_category.value:
        # Upgrade detected
        await loan_service.update_loan_classification(
            loan_id=loan.id,
            npa_category=new_category.value,
            classification_date=payment_date
        )
        
        # Reverse excess provision if upgraded to standard
        if new_category == NPACategory.STANDARD:
            await reverse_excess_provision(loan.id, payment_date)
```

---

## Reporting Integration

### 1. Dashboard Integration

```python
from backend.services.dashboard.router import router

@router.get("/npa-dashboard")
async def get_npa_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    NPA Dashboard with key metrics
    """
    npa_service = NPAService(db, current_user["tenant_id"], current_user["id"])
    
    summary = await npa_service.get_npa_summary(date.today())
    pcr = await npa_service.generate_provisioning_coverage_ratio(date.today())
    
    return {
        "gross_npa_ratio": summary["gross_npa_ratio"],
        "net_npa_ratio": summary["net_npa_ratio"],
        "provisioning_coverage": pcr["pcr_percentage"],
        "total_npa_accounts": summary["npa_assets"]["account_count"],
        "total_npa_amount": summary["npa_assets"]["outstanding_amount"],
        "category_distribution": summary,
        "alerts": {
            "high_risk_accounts": summary["sma_assets"]["account_count"],
            "fresh_npas_this_month": 0,  # Would calculate from movement
            "provision_shortfall": pcr["shortfall"]
        }
    }
```

### 2. Export Reports

```python
import pandas as pd
from io import BytesIO

async def export_asset_classification_register_to_excel(
    as_of_date: date,
    db: AsyncSession,
    tenant_id: int,
    user_id: int
):
    """
    Export asset classification register to Excel
    """
    npa_service = NPAService(db, tenant_id, user_id)
    
    register = await npa_service.generate_asset_classification_register(as_of_date)
    
    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Summary sheet
        summary_df = pd.DataFrame([register["summary"]])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Category-wise sheets
        for category, data in register["categories"].items():
            if data["accounts"]:
                df = pd.DataFrame(data["accounts"])
                df.to_excel(writer, sheet_name=category, index=False)
    
    output.seek(0)
    return output
```

---

## Scheduled Jobs

### 1. Daily DPD Calculation

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=1, minute=0)  # Run at 1 AM daily
async def daily_dpd_calculation():
    """
    Calculate DPD for all active loans daily
    """
    async with get_db() as db:
        loan_service = LoanService(db, tenant_id=None, user_id=1)
        await loan_service.update_all_dpd_values(date.today())
```

### 2. Monthly NPA Classification

```python
@scheduler.scheduled_job('cron', day='last', hour=23, minute=0)  # Last day of month
async def monthly_npa_classification():
    """
    Run monthly NPA classification for entire portfolio
    """
    async with get_db() as db:
        npa_service = NPAService(db, tenant_id=None, user_id=1)
        
        # Get last day of current month
        today = date.today()
        last_day = date(today.year, today.month, 
                       (today.replace(day=28) + timedelta(days=4)).day)
        
        result = await npa_service.run_monthly_npa_classification(last_day)
        
        # Send notification to management
        await send_npa_classification_report(result)
```

### 3. Weekly SMA Monitoring

```python
@scheduler.scheduled_job('cron', day_of_week='mon', hour=9, minute=0)  # Monday 9 AM
async def weekly_sma_monitoring():
    """
    Generate weekly report of SMA accounts for early intervention
    """
    async with get_db() as db:
        loan_service = LoanService(db, tenant_id=None, user_id=1)
        
        # Get SMA accounts
        sma_accounts = await loan_service.get_loans_by_category([
            "SPECIAL_MENTION_0",
            "SPECIAL_MENTION_1", 
            "SPECIAL_MENTION_2"
        ])
        
        # Send alerts to collections team
        await send_sma_alerts(sma_accounts)
```

---

## Event-Driven Architecture

### 1. Loan Downgrade Event

```python
from backend.shared.events.event_bus import EventBus

class LoanDowngradedEvent:
    def __init__(self, loan_id: int, old_category: str, new_category: str):
        self.loan_id = loan_id
        self.old_category = old_category
        self.new_category = new_category
        self.timestamp = datetime.utcnow()

# Publish event when loan is downgraded
async def on_loan_downgraded(loan_id: int, old_category: str, new_category: str):
    event = LoanDowngradedEvent(loan_id, old_category, new_category)
    await EventBus.publish("loan.downgraded", event)

# Subscribe to event
@EventBus.subscribe("loan.downgraded")
async def handle_loan_downgrade(event: LoanDowngradedEvent):
    # Trigger collection workflow
    await trigger_npa_collection_workflow(
        loan_account_id=event.loan_id,
        npa_category=event.new_category,
        outstanding_amount=None  # Would fetch from loan
    )
    
    # Send notification
    await send_downgrade_notification(event.loan_id, event.new_category)
```

### 2. Provision Created Event

```python
class ProvisionCreatedEvent:
    def __init__(self, loan_id: int, provision_amount: Decimal, 
                 journal_entry_id: int):
        self.loan_id = loan_id
        self.provision_amount = provision_amount
        self.journal_entry_id = journal_entry_id
        self.timestamp = datetime.utcnow()

@EventBus.subscribe("provision.created")
async def handle_provision_created(event: ProvisionCreatedEvent):
    # Update loan record
    await update_loan_provision(event.loan_id, event.provision_amount)
    
    # Update financial reports
    await refresh_financial_reports()
```

---

## API Integration Examples

### Example 1: Frontend Dashboard

```javascript
// Fetch NPA Summary
async function fetchNPASummary() {
    const response = await fetch('/api/accounting/npa/summary', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    return data;
}

// Display in dashboard
function displayNPAMetrics(summary) {
    document.getElementById('gross-npa-ratio').textContent = 
        `${summary.gross_npa_ratio}%`;
    document.getElementById('net-npa-ratio').textContent = 
        `${summary.net_npa_ratio}%`;
    document.getElementById('npa-accounts').textContent = 
        summary.npa_assets.account_count;
}
```

### Example 2: Mobile App Integration

```dart
// Flutter/Dart example
Future<NPASummary> fetchNPASummary() async {
  final response = await http.get(
    Uri.parse('$baseUrl/accounting/npa/summary'),
    headers: {'Authorization': 'Bearer $token'},
  );
  
  if (response.statusCode == 200) {
    return NPASummary.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to load NPA summary');
  }
}
```

### Example 3: Third-party Integration

```python
import requests

def get_npa_data_for_credit_bureau(tenant_id: int, as_of_date: str):
    """
    Fetch NPA data for credit bureau reporting
    """
    api_url = f"{base_url}/accounting/npa/register"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "as_of_date": as_of_date,
        "category_filter": None
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Transform for credit bureau format
        return transform_for_credit_bureau(data)
    else:
        raise Exception(f"API Error: {response.text}")
```

---

## Webhook Integration

### 1. NPA Classification Webhook

```python
from fastapi import BackgroundTasks

async def send_webhook_notification(
    webhook_url: str,
    event_type: str,
    payload: dict
):
    """
    Send webhook notification to external systems
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                webhook_url,
                json={
                    "event": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": payload
                },
                timeout=10.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
            return False

# Trigger webhook on NPA classification
async def classify_with_webhook(loan_id: int):
    classification = await classify_loan(loan_id)
    
    if classification["is_npa"]:
        await send_webhook_notification(
            webhook_url=WEBHOOK_URL,
            event_type="loan.npa_classified",
            payload={
                "loan_id": loan_id,
                "npa_category": classification["npa_category"],
                "outstanding": classification["outstanding_amount"]
            }
        )
```

---

## Testing Integration

### 1. Integration Test Example

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_npa_workflow(async_client: AsyncClient):
    """
    Test complete NPA workflow from classification to provisioning
    """
    # Step 1: Create a loan
    loan_response = await async_client.post("/lms/loans", json={
        "customer_id": 1,
        "loan_amount": 100000,
        "loan_type": "personal"
    })
    loan_id = loan_response.json()["data"]["id"]
    
    # Step 2: Simulate 120 days overdue
    await async_client.put(f"/lms/loans/{loan_id}/dpd", json={
        "days_past_due": 120
    })
    
    # Step 3: Classify the loan
    classify_response = await async_client.post("/accounting/npa/classify", json={
        "days_past_due": 120,
        "is_restructured": False,
        "is_written_off": False
    })
    assert classify_response.json()["data"]["npa_category"] == "SUBSTANDARD"
    
    # Step 4: Calculate provisioning
    provision_response = await async_client.post(
        "/accounting/npa/provisioning/calculate",
        json={
            "outstanding_principal": 100000,
            "npa_category": "SUBSTANDARD",
            "is_secured": True,
            "security_coverage_ratio": 100,
            "existing_provision": 0
        }
    )
    assert provision_response.json()["data"]["provisioning_rate"] == 15.0
    
    # Step 5: Create provision entry
    create_provision_response = await async_client.post(
        "/accounting/npa/provisioning/create",
        json={
            "loan_account_id": loan_id,
            "provision_amount": 15000,
            "npa_category": "SUBSTANDARD",
            "as_of_date": "2026-07-31"
        }
    )
    assert create_provision_response.status_code == 201
```

---

## Summary

This integration guide covers:

✅ **LMS Integration** - Fetch loan data, batch classification
✅ **Collections Integration** - Trigger workflows, handle payments  
✅ **Reporting Integration** - Dashboards, exports
✅ **Scheduled Jobs** - Daily, weekly, monthly automation
✅ **Event-Driven** - Publish/subscribe patterns
✅ **API Examples** - Frontend, mobile, third-party
✅ **Webhooks** - External system notifications
✅ **Testing** - Integration test patterns

The NPA module is designed for seamless integration with existing NBFC systems while maintaining modularity and scalability.
