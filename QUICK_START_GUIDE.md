# NBFC Financial Suite - Quick Start Guide 🚀

## Get Started in 5 Minutes

This guide will help you get the NBFC Financial Suite running on your local machine.

---

## 📋 Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 20 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7 or higher (optional for development)
- **Git**: Latest version

### Check Installations
```bash
python --version    # Should be 3.11+
node --version      # Should be 20+
npm --version
psql --version      # Should be 15+
git --version
```

---

## ⚡ Quick Start (Development Mode)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd NBFCSUITE
```

### Step 2: Setup Database
```bash
# Create PostgreSQL database
createdb nbfc_dev

# Or using psql
psql -U postgres
CREATE DATABASE nbfc_dev;
\q
```

### Step 3: Setup Backend
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your database credentials
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/nbfc_dev

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn backend.main:app --reload
```

Backend should now be running at: **http://localhost:8000**

### Step 4: Setup Frontend
```bash
# Open new terminal
cd frontend/apps/admin-portal

# Install dependencies
npm install --legacy-peer-deps

# Create .env.local file
cp .env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start frontend development server
npm run dev
```

Frontend should now be running at: **http://localhost:3000**

### Step 5: Access Application

1. Open browser: **http://localhost:3000**
2. Login with demo credentials:
   - Username: `admin`
   - Password: `admin123`
3. Explore the application!

---

## 📚 API Documentation

Once backend is running, access API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🗂️ Project Structure

```
NBFCSUITE/
├── backend/                      # Backend (FastAPI)
│   ├── services/                 # Business logic modules
│   │   ├── auth/                 # Authentication
│   │   ├── customer/             # Customer management
│   │   ├── loan/                 # Loan management
│   │   ├── deposit/              # Deposit management
│   │   ├── gold/                 # Gold loan management
│   │   ├── accounting/           # Accounting module
│   │   ├── workflow/             # Workflow engine
│   │   ├── notification/         # Notifications
│   │   └── file_upload/          # File uploads
│   ├── shared/                   # Shared utilities
│   │   ├── database/             # Database models
│   │   ├── common/               # Common utilities
│   │   └── middleware/           # Middleware
│   ├── main.py                   # Application entry point
│   └── requirements.txt          # Python dependencies
│
├── frontend/apps/admin-portal/   # Frontend (Next.js)
│   ├── src/
│   │   ├── app/                  # Pages (App Router)
│   │   │   ├── dashboard/        # Dashboard
│   │   │   ├── customers/        # Customer pages
│   │   │   ├── loans/            # Loan pages
│   │   │   ├── deposits/         # Deposit pages
│   │   │   ├── gold-loans/       # Gold loan pages
│   │   │   ├── accounting/       # Accounting pages
│   │   │   └── workflow/         # Workflow pages
│   │   ├── components/           # React components
│   │   │   ├── ui/               # UI components
│   │   │   ├── layout/           # Layout components
│   │   │   └── charts/           # Chart components
│   │   ├── services/             # API services
│   │   ├── lib/                  # Utilities
│   │   └── types/                # TypeScript types
│   └── package.json              # Node dependencies
│
├── uploads/                      # File upload storage
├── logs/                         # Application logs
├── nginx/                        # Nginx configuration
├── .github/workflows/            # CI/CD pipelines
└── *.md                          # Documentation files
```

---

## 🔧 Environment Variables

### Backend (.env)
```env
# Application
APP_NAME=NBFC Financial Suite
APP_ENV=development
APP_DEBUG=true

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/nbfc_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nbfc_dev
DB_USER=postgres
DB_PASSWORD=your_password

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=true

# Multi-tenancy
TENANT_ISOLATION_ENABLED=true
DEFAULT_TENANT=default

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
MAX_FILES_PER_UPLOAD=10
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🎯 Common Tasks

### Create Database Migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Run Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

### Build Frontend for Production
```bash
cd frontend/apps/admin-portal
npm run build
npm run start
```

### View Backend Logs
```bash
cd backend
tail -f logs/app.log
```

### Clear Database and Start Fresh
```bash
# Drop and recreate database
dropdb nbfc_dev
createdb nbfc_dev

# Run migrations
cd backend
alembic upgrade head
```

---

## 🧪 Testing the Application

### Test Backend API
```bash
# Using curl
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/docs
```

### Test Gold Loan Module
1. Create a gold loan product:
   - Go to Gold Loans → Products
   - Click "New Product"
   - Fill in details (LTV: 75%, Interest: 12%)

2. Create a gold loan:
   - Go to Gold Loans → New Gold Loan
   - Enter customer ID
   - Add ornaments (Chain, Bangle, etc.)
   - System calculates LTV automatically
   - Submit to create loan

3. View loan details:
   - Click on loan account number
   - View 4 tabs: Details, Ornaments, Payments, Releases

### Test File Upload
```python
# Using Python test script
python test_file_upload_api.py
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue**: Database connection error
```bash
# Check PostgreSQL is running
# Windows:
pg_ctl status

# macOS:
brew services list

# Fix: Start PostgreSQL
# Windows: Start PostgreSQL service
# macOS: brew services start postgresql@15
```

**Issue**: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Issue**: Alembic migration error
```bash
# Reset alembic
alembic downgrade base
alembic upgrade head
```

### Frontend Issues

**Issue**: Module not found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**Issue**: Port already in use
```bash
# Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

**Issue**: API connection error
```bash
# Check backend is running on port 8000
# Check NEXT_PUBLIC_API_URL in .env.local
```

---

## 📖 Learning Resources

### For Backend Developers
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Pydantic Documentation: https://docs.pydantic.dev/

### For Frontend Developers
- Next.js 14 Documentation: https://nextjs.org/docs
- React Documentation: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/docs
- Recharts: https://recharts.org/

### Project Documentation
- API Documentation: http://localhost:8000/docs
- Module Documentation: See `*_COMPLETE.md` files
- Deployment Guide: `STAGING_DEPLOYMENT_GUIDE.md`
- Final Status: `FINAL_PROJECT_STATUS.md`

---

## 🚀 Next Steps

After getting the application running:

1. **Explore the UI**
   - Dashboard with statistics
   - Customer management
   - Loan applications
   - Gold loan module
   - Accounting operations

2. **Test API Endpoints**
   - Open Swagger UI
   - Try different endpoints
   - Test authentication
   - Test gold loan creation

3. **Review Code**
   - Backend service layer
   - Frontend components
   - Database models
   - API routing

4. **Customize**
   - Modify products
   - Add new features
   - Customize UI theme
   - Add validations

5. **Deploy to Staging**
   - Follow `STAGING_DEPLOYMENT_GUIDE.md`
   - Set up Docker Compose
   - Configure Nginx
   - Test deployment

---

## 💡 Development Tips

### Backend Development
```bash
# Auto-reload is enabled with --reload flag
uvicorn backend.main:app --reload

# View SQL queries (add to config.py)
ECHO_SQL=True

# Use IPython for REPL
pip install ipython
ipython
>>> from backend.shared.database.connection import get_db
```

### Frontend Development
```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format

# Build and analyze bundle
npm run build
npm run analyze
```

### Database Operations
```bash
# Connect to database
psql -U postgres -d nbfc_dev

# View tables
\dt

# View table schema
\d table_name

# Query data
SELECT * FROM gold_loan_accounts LIMIT 10;
```

---

## 🎓 Key Modules Overview

### 1. Gold Loan Module (New!)
- **Location**: `backend/services/gold/`
- **Features**: Ornament tracking, LTV calculation, payments, releases
- **API**: `/api/v1/gold-loans/`
- **Frontend**: `/gold-loans/`

### 2. Customer Management
- **Location**: `backend/services/customer/`
- **Features**: CIF, KYC, family members, documents
- **API**: `/api/v1/customers/`
- **Frontend**: `/customers/`

### 3. Loan Management
- **Location**: `backend/services/loan/`
- **Features**: Applications, approvals, disbursement, repayment
- **API**: `/api/v1/loans/`
- **Frontend**: `/loans/applications/`

### 4. Deposit Management
- **Location**: `backend/services/deposit/`
- **Features**: Accounts, products, interest calculation
- **API**: `/api/v1/deposits/`
- **Frontend**: `/deposits/`

### 5. Accounting
- **Location**: `backend/services/accounting/`
- **Features**: Chart of accounts, journal entries, reports
- **API**: `/api/v1/accounting/`
- **Frontend**: `/accounting/`

---

## 📞 Support & Resources

### Documentation Files
- `FINAL_PROJECT_STATUS.md` - Complete project overview
- `GOLD_LOAN_MODULE_COMPLETE.md` - Gold loan documentation
- `FILE_UPLOAD_API_COMPLETE.md` - File upload guide
- `STAGING_DEPLOYMENT_GUIDE.md` - Deployment instructions

### Need Help?
1. Check API documentation: http://localhost:8000/docs
2. Review module documentation files
3. Check troubleshooting section above
4. Review code comments in source files

---

## ✅ Checklist for New Developers

- [ ] Clone repository
- [ ] Install prerequisites (Python, Node.js, PostgreSQL)
- [ ] Create database
- [ ] Setup backend virtual environment
- [ ] Install backend dependencies
- [ ] Configure backend .env file
- [ ] Run database migrations
- [ ] Start backend server
- [ ] Install frontend dependencies
- [ ] Configure frontend .env.local
- [ ] Start frontend server
- [ ] Access application at http://localhost:3000
- [ ] Login with demo credentials
- [ ] Explore dashboard and modules
- [ ] Test gold loan creation
- [ ] Review API documentation
- [ ] Read module documentation files

---

## 🎉 You're Ready!

Congratulations! You now have a fully functional NBFC Financial Suite running locally.

**Start building amazing financial solutions!** 🚀

---

**Last Updated**: July 5, 2026  
**Version**: 2.0.0  
**Status**: Production Ready ✅
