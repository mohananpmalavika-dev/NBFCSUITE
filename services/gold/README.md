# Gold Lending Operating System

**Version**: 2.0  
**Status**: Phase 1-4 Complete (27% of Full Platform)  
**Last Updated**: July 3, 2026

---

## Overview

An AI-powered, enterprise-grade Gold Lending Operating System built to rival platforms like Oracle FLEXCUBE, Mambu, and Newgen. This system provides end-to-end gold loan lifecycle management from customer onboarding to auction recovery.

## ✅ Completed Phases

### Phase 1: Product Configuration Engine
- **10 tables** | **20+ endpoints** | **4 pre-configured products**
- Database-driven product configuration
- Interest, tenure, LTV, charges, eligibility rules
- Multi-channel support (branch, mobile, web)
- **Docs**: `PHASE1_PRODUCT_ENGINE.md`

### Phase 2: Customer Journey Management
- **7 tables** | **15+ endpoints** | **5-step UI**
- Digital customer journey from walk-in to application
- AI-powered product recommendations
- Real-time eligibility validation
- Complete session tracking
- **Docs**: `PHASE2_CUSTOMER_JOURNEY.md`

### Phase 3: Advanced Appraisal Engine
- **8 tables** | **15+ endpoints** | **15 ornament types**
- Automated valuation with market rates
- Multi-step purity testing
- Maker-checker weight verification
- Anomaly detection system
- Photo management
- **Docs**: `PHASE3_APPRAISAL_ENGINE.md`

### Phase 4: Enhanced Ornament Catalog
- **10+ tables** | **30+ endpoints** | **8-tab profile page**
- Multi-photo management with categorization
- Comprehensive stone catalog with certification
- GPS-tracked movement history
- Maker-checker verification workflow
- Condition monitoring system
- AI-powered fraud detection (comparison engine)
- Certificate & insurance management
- **Docs**: `PHASE4_ORNAMENT_CATALOG.md`

---

## Architecture

### Technology Stack
```
Backend:   Python 3.11, FastAPI, SQLAlchemy, Pydantic
Frontend:  Next.js 14, TypeScript, Tailwind CSS
Database:  PostgreSQL with JSONB
API:       RESTful with OpenAPI documentation
```

### Directory Structure
```
services/gold/
├── app/
│   ├── models/          # SQLAlchemy models (35+ tables)
│   │   ├── product.py
│   │   ├── journey.py
│   │   ├── appraisal.py
│   │   └── catalog.py
│   ├── schemas/         # Pydantic schemas (60+ schemas)
│   │   ├── product.py
│   │   ├── journey.py
│   │   ├── appraisal.py
│   │   └── catalog.py
│   ├── routers/         # API endpoints (80+ endpoints)
│   │   ├── products.py
│   │   ├── journey.py
│   │   ├── appraisal.py
│   │   └── catalog.py
│   ├── main.py          # FastAPI application
│   └── seed_products.py # Sample data loader
├── PHASE1_PRODUCT_ENGINE.md
├── PHASE2_CUSTOMER_JOURNEY.md
├── PHASE3_APPRAISAL_ENGINE.md
├── PHASE4_ORNAMENT_CATALOG.md
├── GOLD_LENDING_PLATFORM_SUMMARY.md
├── GETTING_STARTED_PHASE4.md
└── requirements.txt
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup
```bash
# Navigate to gold service
cd services/gold

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite"

# Run server
uvicorn app.main:app --reload --port 8013
```

### Database Setup
```bash
# Navigate to project root
cd NBFCSUITE

# Apply migrations in order
psql -U nbfc_user -d nbfcsuite -f infra/migrations/018_gold_product_configuration.sql
psql -U nbfc_user -d nbfcsuite -f infra/migrations/019_gold_customer_journey.sql
psql -U nbfc_user -d nbfcsuite -f infra/migrations/020_gold_appraisal_engine.sql
psql -U nbfc_user -d nbfcsuite -f infra/migrations/021_ornament_catalog.sql

# Seed sample products
cd services/gold
python -m app.seed_products
```

### Frontend Setup
```bash
# Navigate to customer app
cd apps/customer-app

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access Points
- **API Server**: http://localhost:8013
- **API Docs**: http://localhost:8013/docs (Interactive Swagger UI)
- **Frontend**: http://localhost:3000
- **Gold Lending**: http://localhost:3000/gold-lending

---

## API Overview

### Products (Phase 1)
```
GET    /api/v1/gold/products              # List all products
POST   /api/v1/gold/products              # Create product
GET    /api/v1/gold/products/{id}         # Get product details
PATCH  /api/v1/gold/products/{id}         # Update product
DELETE /api/v1/gold/products/{id}         # Delete product

# Configuration endpoints
POST   /api/v1/gold/products/{id}/interest
POST   /api/v1/gold/products/{id}/tenure
POST   /api/v1/gold/products/{id}/limits
POST   /api/v1/gold/products/{id}/charges
POST   /api/v1/gold/products/{id}/documents
POST   /api/v1/gold/products/{id}/eligibility
POST   /api/v1/gold/products/{id}/workflow
```

### Customer Journey (Phase 2)
```
POST   /api/v1/gold/journey/sessions      # Create session
GET    /api/v1/gold/journey/sessions/{id} # Get session
PATCH  /api/v1/gold/journey/sessions/{id} # Update session
POST   /api/v1/gold/journey/search-customer
POST   /api/v1/gold/journey/select-customer/{session_id}/{customer_id}
GET    /api/v1/gold/journey/recommend-products/{session_id}
POST   /api/v1/gold/journey/select-product
POST   /api/v1/gold/journey/check-eligibility/{session_id}/{product_id}
```

### Appraisal (Phase 3)
```
GET    /api/v1/gold/appraisal/ornament-types
POST   /api/v1/gold/appraisal/market-rates
GET    /api/v1/gold/appraisal/market-rates/current
POST   /api/v1/gold/appraisal/sessions
GET    /api/v1/gold/appraisal/sessions/{id}
POST   /api/v1/gold/appraisal/sessions/{id}/ornaments
POST   /api/v1/gold/appraisal/purity-tests
POST   /api/v1/gold/appraisal/weight-measurements
POST   /api/v1/gold/appraisal/anomalies
POST   /api/v1/gold/appraisal/quick-appraisal
```

### Catalog (Phase 4)
```
# Photos
POST   /api/v1/gold/catalog/photos
GET    /api/v1/gold/catalog/photos/ornament/{id}
DELETE /api/v1/gold/catalog/photos/{id}

# Stones
POST   /api/v1/gold/catalog/stones
GET    /api/v1/gold/catalog/stones/ornament/{id}
PUT    /api/v1/gold/catalog/stones/{id}

# Movements
POST   /api/v1/gold/catalog/movements
POST   /api/v1/gold/catalog/movements/{id}/verify
GET    /api/v1/gold/catalog/movements/ornament/{id}

# Conditions
POST   /api/v1/gold/catalog/conditions
GET    /api/v1/gold/catalog/conditions/ornament/{id}

# Complete Profile
GET    /api/v1/gold/catalog/profile/{ornament_id}
```

---

## Key Features

### 🎯 Product Configuration Engine
- Unlimited product variants
- Per-product business rules
- Regional customization
- No code changes needed

### 🚀 Customer Journey
- 5-step digital workflow
- AI-powered recommendations
- Real-time eligibility
- Complete funnel analytics

### 💎 Appraisal Engine
- Automated valuation
- Multi-step purity testing
- Maker-checker controls
- Anomaly detection

### 📸 Ornament Catalog
- Multi-photo documentation
- Stone-level tracking
- GPS movement history
- Fraud detection engine
- Certificate management
- Insurance integration

---

## Security Features

### Authentication & Authorization
- JWT token-based authentication (ready for integration)
- Role-based access control (RBAC ready)
- User action tracking

### Audit Trail
- Complete operation logging
- User attribution (created_by, updated_by)
- Timestamp tracking
- GPS coordinates for movements

### Fraud Prevention
- Anomaly detection in appraisal
- Ornament comparison engine
- Similarity scoring
- Investigation workflow

### Maker-Checker Controls
- Weight verification (dual approval)
- Movement verification (dual approval)
- Purity test verification
- Prevents single-user fraud

---

## Performance Considerations

### Database Optimization
- Strategic indexing on high-traffic columns
- Foreign key constraints for integrity
- JSONB for flexible metadata
- Connection pooling

### API Performance
- Async/await throughout
- Efficient query patterns
- Pagination support
- Response caching ready

### Scalability
- Stateless API design
- Horizontal scaling capable
- Microservices architecture
- Database sharding ready

---

## Testing

### Backend Tests
```bash
cd services/gold
pytest tests/
```

### API Testing
```bash
# Using curl
curl http://localhost:8013/health

# Using Swagger UI
# Navigate to http://localhost:8013/docs
```

### Frontend Tests
```bash
cd apps/customer-app
npm test
```

---

## Documentation

### Phase Documentation
- `PHASE1_PRODUCT_ENGINE.md` - Product configuration details
- `PHASE2_CUSTOMER_JOURNEY.md` - Customer journey workflows
- `PHASE3_APPRAISAL_ENGINE.md` - Appraisal system details
- `PHASE4_ORNAMENT_CATALOG.md` - Catalog lifecycle management

### Getting Started Guides
- `GETTING_STARTED_PHASE4.md` - Phase 4 quick start
- `GOLD_LENDING_PLATFORM_SUMMARY.md` - Complete platform overview

### API Documentation
- Interactive Swagger UI at `/docs`
- OpenAPI JSON at `/openapi.json`

---

## Roadmap

### ✅ Completed (27%)
- [x] Phase 1: Product Configuration Engine
- [x] Phase 2: Customer Journey Management
- [x] Phase 3: Advanced Appraisal Engine
- [x] Phase 4: Enhanced Ornament Catalog

### 🔄 In Progress (0%)
- [ ] Phase 5: Vault & Packet Management
- [ ] Phase 6: Disbursement & Loan Booking

### 📅 Planned (73%)
- [ ] Phase 7: Interest, Renewal & Release
- [ ] Phase 8: Auction & Recovery
- [ ] Phase 9: Gold Rate Engine
- [ ] Phase 10: AI & FinDNA Intelligence
- [ ] Phase 11: Dashboards & Analytics
- [ ] Phase 12: Mobile Branch Operations
- [ ] Phase 13: Customer Mobile App
- [ ] Phase 14: Audit & Compliance
- [ ] Phase 15: Partner Integrations

---

## Support & Contribution

### Issue Reporting
- Create detailed issue reports with steps to reproduce
- Include logs and screenshots where applicable
- Tag appropriately (bug, feature, enhancement)

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Write comprehensive tests
- Document all public APIs
- Keep migrations reversible

---

## License

Internal Use Only - Proprietary Software

---

## Contact

- **Technical Lead**: [Contact Information]
- **Product Owner**: [Contact Information]
- **Support Team**: [Contact Information]

---

**Last Updated**: July 3, 2026  
**Version**: 2.0 (Phases 1-4 Complete)  
**Status**: Production Ready for Pilot Deployment
