# Minimal Deployment Quick Reference

**Version**: Minimal v1.0  
**Memory Target**: ~220MB  
**Entry Point**: `backend/main_minimal.py`  
**Status**: Deployed to Render.com

## 🎯 What's Included

### Core Modules (5)

#### 1. Authentication & Authorization ✅
- **Router**: `/api/v1/auth`
- **Features**:
  - User login/logout
  - JWT token generation
  - Role-based access control (RBAC)
  - Multi-tenant support
  - Session management

#### 2. Dashboard & Statistics ✅
- **Router**: `/api/v1/dashboard`
- **Features**:
  - Real-time statistics
  - Total customers count
  - Active loans count
  - Total outstanding amount
  - Overdue amount tracking
  - Recent activities feed

#### 3. Master Data Management ✅
- **Router**: `/api/v1/master`
- **Features**:
  - Branch management
  - Loan product configuration
  - Fee/charge definitions
  - Document type setup
  - System configurations

#### 4. Customer Management ✅
- **Router**: `/api/v1/customers`
- **Features**:
  - Customer registration
  - KYC document upload
  - Customer search and filtering
  - Customer profile management
  - Contact information updates

#### 5. Loan Management ✅
- **Router**: `/api/v1/loans`
- **Features**:
  - Loan application creation
  - Loan application workflow
  - Loan account management
  - EMI schedule generation
  - Repayment tracking
  - Loan status updates

## 🚫 What's NOT Included

These modules are **disabled** to save memory (~305MB):

| Module | Router Path | Memory Saved |
|--------|-------------|--------------|
| Accounting | `/api/v1/accounting` | ~40MB |
| Deposits | `/api/v1/deposits` | ~35MB |
| Gold Loans | `/api/v1/gold-loans` | ~30MB |
| HRMS | `/api/v1/hrms` | ~30MB |
| CRM | `/api/v1/crm` | ~25MB |
| Treasury | `/api/v1/treasury` | ~25MB |
| Compliance | `/api/v1/compliance` | ~20MB |
| Legal | `/api/v1/legal` | ~20MB |
| DMS | `/api/v1/dms` | ~20MB |
| Facility | `/api/v1/facility` | ~15MB |
| Reporting | `/api/v1/reporting` | ~15MB |
| Insurance | `/api/v1/insurance` | ~15MB |
| Collections | `/api/v1/collections` | ~15MB |

**Total Saved**: ~305MB

## 📊 Memory Breakdown

```
Base FastAPI App:         ~50MB
Database Connection:      ~20MB
Authentication Module:    ~30MB
Dashboard Module:         ~20MB
Master Data Module:       ~30MB
Customer Module:          ~35MB
Loan Module:              ~35MB
--------------------------------
Total (Estimated):        ~220MB
Free Tier Limit:          512MB
Safety Margin:            292MB (57%)
```

## 🔧 Configuration

### Environment Variables Required

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
DB_ECHO=false

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://your-frontend.com,http://localhost:3000

# Application
APP_ENV=production
LOG_LEVEL=INFO
ENABLE_SWAGGER=true

# Feature Flags (in config.py)
ENABLE_ACCOUNTING=false
ENABLE_DEPOSITS=false
ENABLE_GOLD_LOANS=false
ENABLE_HRMS=false
ENABLE_CRM=false
ENABLE_TREASURY=false
ENABLE_COMPLIANCE=false
ENABLE_LEGAL=false
ENABLE_DMS=false
ENABLE_FACILITY=false
ENABLE_REPORTING=false
ENABLE_INSURANCE=false
ENABLE_COLLECTIONS=false
```

## 🌐 API Endpoints

### Health & Docs
```
GET  /health              - Health check
GET  /docs                - Swagger UI
GET  /redoc               - ReDoc UI
```

### Authentication
```
POST /api/v1/auth/login           - User login
POST /api/v1/auth/logout          - User logout
POST /api/v1/auth/refresh         - Refresh token
GET  /api/v1/auth/me              - Current user info
```

### Dashboard
```
GET  /api/v1/dashboard/stats      - Dashboard statistics
GET  /api/v1/dashboard/activities - Recent activities
```

### Master Data
```
GET  /api/v1/master/branches      - List branches
POST /api/v1/master/branches      - Create branch
GET  /api/v1/master/products      - List loan products
POST /api/v1/master/products      - Create loan product
```

### Customers
```
GET  /api/v1/customers            - List customers
POST /api/v1/customers            - Create customer
GET  /api/v1/customers/{id}       - Get customer details
PUT  /api/v1/customers/{id}       - Update customer
```

### Loans
```
GET  /api/v1/loans/applications   - List loan applications
POST /api/v1/loans/applications   - Create loan application
GET  /api/v1/loans/accounts       - List loan accounts
GET  /api/v1/loans/accounts/{id}  - Get loan account details
POST /api/v1/loans/repayments     - Record repayment
```

## 🔄 Enabling Additional Modules

To enable more modules, you have 2 options:

### Option 1: Upgrade Render Plan
```
Free Tier:     512MB  (current)
Starter Tier:  512MB  (same, not helpful)
Standard Tier: 2GB    (can enable all modules)
Pro Tier:      4GB    (recommended for production)
```

### Option 2: Selective Module Enabling
1. Edit `backend/shared/config.py`
2. Set feature flag to `True`
3. Edit `backend/main_minimal.py`
4. Uncomment the module import and router
5. Monitor memory usage carefully

**Example**: Enable Accounting
```python
# In config.py
ENABLE_ACCOUNTING: bool = Field(default=True, env="ENABLE_ACCOUNTING")

# In main_minimal.py
if settings.ENABLE_ACCOUNTING:
    from backend.services.accounting.router import router as accounting_router
    app.include_router(accounting_router, prefix="/api/v1", tags=["Accounting"])
```

**Memory Impact**: Each module adds ~15-40MB

## 📈 Scaling Strategy

### Phase 1: Free Tier (Current)
- **Memory**: 512MB limit
- **Modules**: 5 core modules
- **Users**: Development/Testing only
- **Cost**: $0/month

### Phase 2: Standard Tier
- **Memory**: 2GB
- **Modules**: Enable 8-10 critical modules
- **Users**: Small production deployment
- **Cost**: $7/month

### Phase 3: Pro Tier
- **Memory**: 4GB
- **Modules**: All 18 modules enabled
- **Users**: Full production deployment
- **Cost**: $25/month

## ⚡ Performance Expectations

### Response Times (Minimal Version)
- Health check: < 100ms
- Authentication: < 200ms
- Dashboard stats: < 500ms
- Customer list (paginated): < 300ms
- Loan application: < 400ms

### Database Queries
- Most queries: < 100ms
- Complex aggregations: < 500ms
- Report generation: N/A (reporting disabled)

### Cold Start Time
- First request after sleep: ~20 seconds (Render free tier)
- Subsequent requests: < 500ms

## 🚀 Testing Checklist

After deployment, verify:

- [ ] Health check responds
- [ ] Swagger docs load
- [ ] Can create user/login
- [ ] Can create customer
- [ ] Can create loan product
- [ ] Can create loan application
- [ ] Dashboard shows correct stats
- [ ] Memory stays under 512MB for 1 hour
- [ ] No errors in logs
- [ ] Response times acceptable

## 📞 Support

### Deployment Issues
1. Check Render logs
2. Verify all 24 fixes applied
3. Check environment variables
4. Review `DEPLOYMENT_MONITOR_GUIDE.md`

### Memory Issues
1. Verify minimal entry point used
2. Check which modules actually loading
3. Review memory breakdown
4. Consider disabling more features

### Configuration Issues
1. Check `backend/shared/config.py`
2. Verify environment variables
3. Check `render.yaml` settings
4. Review `FIX_24_RENDER_CONFIG.md`

---

**Last Updated**: 2026-07-12  
**Version**: 1.0-minimal  
**Status**: Deployed & Monitoring  
**Next Review**: After 24 hours of stable operation
