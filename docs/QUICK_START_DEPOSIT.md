# 🚀 Deposit Module - Quick Start Guide

## ⚡ Get Running in 5 Minutes

### Step 1: Setup Database (1 minute)

```powershell
# Create database
psql -U postgres
CREATE DATABASE nbfc_deposits;
\q

# Run migrations
psql -U postgres -d nbfc_deposits -f services\deposits\migrations\001_create_deposit_tables.sql
```

### Step 2: Install Dependencies (1 minute)

```powershell
cd services\deposits

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure Environment (30 seconds)

```powershell
# Copy environment file
copy .env.example .env

# Edit .env (update DATABASE_URL if needed)
notepad .env
```

### Step 4: Seed Data (30 seconds)

```powershell
# Load default products and sample data
python scripts\seed_data.py
```

Expected output:
```
===========================================================
   DEPOSIT OS - DATABASE SEEDING
===========================================================

🌱 Seeding deposit products...
  ✅ Created: Fixed Deposit - Regular
  ✅ Created: Fixed Deposit - Senior Citizen
  ✅ Created: Fixed Deposit - Monthly Interest
  ✅ Created: Fixed Deposit - Cumulative
  ✅ Created: Recurring Deposit - Regular
✅ Products seeded!

🌱 Seeding interest slabs...
  ✅ Added slab: ₹10000 - ₹99999, 6.5%
  ✅ Added slab: ₹10000 - ₹99999, 7.0%
  ✅ Added slab: ₹100000 - ₹499999, 7.5%
  ✅ Added slab: ₹500000 - No Limit, 8.0%
✅ Interest slabs seeded!

===========================================================
   ✅ SEEDING COMPLETED SUCCESSFULLY!
===========================================================
```

### Step 5: Start Service (30 seconds)

```powershell
# Run the service
uvicorn app.main:app --reload --port 8007
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8007
INFO:     🚀 Deposit Operating System starting...
INFO:     📊 Initializing deposit engines...
INFO:     🤖 Loading AI models...
INFO:     ✅ Deposit OS ready!
```

---

## 🎯 Test Your Setup

### Open API Documentation

Visit: **http://localhost:8007/api/docs**

### Quick API Tests

#### 1. Check Health
```powershell
curl http://localhost:8007/health
```

Response:
```json
{
  "status": "healthy",
  "service": "deposit-os",
  "version": "1.0.0"
}
```

#### 2. List Products
```powershell
curl http://localhost:8007/api/v1/products
```

You should see 5 products: FD Regular, FD Senior Citizen, FD Monthly Interest, FD Cumulative, RD Regular.

#### 3. Calculate Interest

```powershell
curl -X POST http://localhost:8007/api/v1/interest/calculate-simple `
  -H "Content-Type: application/json" `
  -d '{
    "principal": 100000,
    "rate": 7.0,
    "days": 365
  }'
```

Response:
```json
{
  "method": "SIMPLE",
  "principal": 100000,
  "rate": 7.0,
  "days": 365,
  "interest": 7000.00,
  "maturity_amount": 107000.00
}
```

#### 4. Calculate Applicable Rate

```powershell
curl -X POST http://localhost:8007/api/v1/products/calculate-rate `
  -H "Content-Type: application/json" `
  -d '{
    "product_id": "<paste-product-id>",
    "amount": 150000,
    "tenure_days": 365,
    "is_senior_citizen": false
  }'
```

#### 5. Open Fixed Deposit

```powershell
curl -X POST http://localhost:8007/api/v1/accounts/fd `
  -H "Content-Type: application/json" `
  -d '{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "cif_number": "CIF12345",
    "product_id": "<paste-product-id>",
    "principal_amount": 100000,
    "tenure_days": 365,
    "is_senior_citizen": false,
    "branch_code": "BR001",
    "nominees": [
      {
        "name": "John Doe",
        "relationship": "SPOUSE",
        "allocation_percentage": 100
      }
    ]
  }'
```

#### 6. Get Dashboard

```powershell
curl http://localhost:8007/api/v1/dashboard/summary
```

#### 7. Get Maturity Pipeline

```powershell
curl http://localhost:8007/api/v1/maturity/pipeline?days_ahead=30
```

---

## 📊 Explore the System

### Using Swagger UI

1. Go to http://localhost:8007/api/docs
2. Click "Try it out" on any endpoint
3. Fill in the parameters
4. Click "Execute"
5. See the response

### Key Endpoints to Try

**Products**
- `GET /api/v1/products` - List all products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/compare-rates` - Compare rates

**Accounts**
- `POST /api/v1/accounts/fd` - Open Fixed Deposit
- `POST /api/v1/accounts/rd` - Open Recurring Deposit
- `GET /api/v1/accounts/{id}` - Get account details

**Interest**
- `POST /api/v1/interest/calculate` - Calculate interest
- `POST /api/v1/interest/generate-schedule` - Generate schedule

**Maturity**
- `GET /api/v1/maturity/pipeline` - Upcoming maturities
- `GET /api/v1/maturity/{id}/calculate` - Calculate maturity

**AI Intelligence**
- `POST /api/v1/ai/predict-renewal` - Predict renewal
- `POST /api/v1/ai/analyze-churn` - Analyze churn risk
- `POST /api/v1/ai/recommend-product` - Recommend products

**Dashboard**
- `GET /api/v1/dashboard/summary` - Dashboard metrics
- `GET /api/v1/dashboard/treasury` - Treasury analytics

---

## 🧪 Sample API Workflows

### Workflow 1: Open FD with Complete Flow

```python
import httpx
import json

base_url = "http://localhost:8007/api/v1"

# 1. Get products
products = httpx.get(f"{base_url}/products").json()
fd_product = next(p for p in products if p["code"] == "FD_REGULAR")

# 2. Calculate rate for customer
rate_request = {
    "product_id": fd_product["id"],
    "amount": 200000,
    "tenure_days": 365,
    "is_senior_citizen": False
}
rate = httpx.post(f"{base_url}/products/calculate-rate", json=rate_request).json()
print(f"Applicable Rate: {rate['applicable_rate']}%")

# 3. Calculate interest
interest_request = {
    "principal": 200000,
    "rate": rate["applicable_rate"],
    "days": 365,
    "method": "SIMPLE"
}
interest = httpx.post(f"{base_url}/interest/calculate", json=interest_request).json()
print(f"Maturity Amount: ₹{interest['maturity_amount']}")

# 4. Open FD account
fd_request = {
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "cif_number": "CIF12345",
    "product_id": fd_product["id"],
    "principal_amount": 200000,
    "tenure_days": 365,
    "is_senior_citizen": False,
    "branch_code": "BR001",
    "nominees": [
        {
            "name": "Jane Doe",
            "relationship": "SPOUSE",
            "allocation_percentage": 100
        }
    ]
}
account = httpx.post(f"{base_url}/accounts/fd", json=fd_request).json()
print(f"Account Created: {account['account_number']}")

# 5. Approve account
approval = httpx.post(
    f"{base_url}/accounts/{account['account_id']}/approve",
    params={"approved_by": "admin"}
).json()
print(f"Status: {approval['status']}")
```

### Workflow 2: RD with Installment Payments

```python
# 1. Open RD account
rd_request = {
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "cif_number": "CIF12345",
    "product_id": "<rd-product-id>",
    "installment_amount": 5000,
    "num_installments": 12,
    "is_senior_citizen": False,
    "branch_code": "BR001"
}
rd_account = httpx.post(f"{base_url}/accounts/rd", json=rd_request).json()

# 2. Get installment schedule
schedule = httpx.get(f"{base_url}/rd/{rd_account['account_id']}/schedule").json()

# 3. Pay first installment
payment = {
    "schedule_id": schedule[0]["schedule_id"],
    "amount": 5000,
    "payment_date": "2024-01-05",
    "payment_mode": "CASH",
    "payment_reference": "PMT001"
}
result = httpx.post(f"{base_url}/rd/installments/pay", json=payment).json()
```

### Workflow 3: Maturity Processing

```python
# 1. Get maturity pipeline
pipeline = httpx.get(f"{base_url}/maturity/pipeline?days_ahead=30").json()

# 2. For each maturing account, predict renewal
for account in pipeline[:5]:
    prediction = httpx.post(
        f"{base_url}/ai/predict-renewal",
        params={"account_id": account["account_id"]}
    ).json()
    
    print(f"Account: {account['account_number']}")
    print(f"Renewal Probability: {prediction['probability']}%")
    print(f"Recommendation: {prediction['recommendation']}")

# 3. Process maturity (example: auto-renew)
maturity_action = {
    "account_id": pipeline[0]["account_id"],
    "action": "RENEW",
    "renewal_tenure_days": 365
}
result = httpx.post(
    f"{base_url}/maturity/{pipeline[0]['account_id']}/process",
    json=maturity_action
).json()
```

---

## 🎨 Frontend Integration (Coming Next)

The backend APIs are ready. Frontend development will include:

### Customer Portal
- Browse deposit products
- Apply for FD/RD online
- View account dashboard
- Download statements
- Request premature closure

### Admin Dashboard
- Deposit analytics
- Maturity pipeline
- Approval workflows
- Reports generation
- AI insights

### Branch App
- Quick FD/RD opening
- Customer search
- Payment collection
- Certificate printing

---

## 🐛 Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```

**Solution:**
```powershell
# Check PostgreSQL is running
Get-Service postgresql*

# Start if needed
Start-Service postgresql-x64-14
```

### Port Already in Use
```
Error: [Errno 10048] Only one usage of each socket address
```

**Solution:**
```powershell
# Find process using port 8007
netstat -ano | findstr :8007

# Kill the process
taskkill /F /PID <process-id>
```

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

---

## 📚 Next Steps

1. **Explore APIs**: Try all endpoints in Swagger UI
2. **Read Documentation**: Check `/services/deposits/README.md`
3. **Review Code**: Understand the engines and services
4. **Build Frontend**: Start with deposit product catalog
5. **Add Tests**: Write unit and integration tests
6. **Deploy**: Set up staging environment

---

## 💡 Pro Tips

1. **Use Swagger UI**: It's the fastest way to test APIs
2. **Check Logs**: Watch the console for debugging
3. **Database GUI**: Use pgAdmin or DBeaver to explore data
4. **API Client**: Use Postman or Insomnia for advanced testing
5. **Hot Reload**: The service auto-reloads on code changes

---

## 🎉 You're Ready!

Your Deposit Operating System is now running with:

- ✅ 5 Pre-configured Products
- ✅ Interest Rate Slabs
- ✅ Sample Accounts
- ✅ 47 API Endpoints
- ✅ AI Intelligence
- ✅ Treasury Analytics

**Start building amazing deposit experiences!** 🚀

---

**Need Help?**
- Documentation: `services/deposits/README.md`
- Roadmap: `DEPOSIT_MODULE_ROADMAP.md`
- API Docs: http://localhost:8007/api/docs
