# NBFCSUITE File Navigation Guide

Quick reference to understand the monorepo structure and where to find what.

## 📖 Documentation Files (Start Here!)

| File | Purpose |
|------|---------|
| `README.md` | Main project overview, features, tech stack |
| `SETUP.md` | Step-by-step setup guide (database, services, testing) |
| `CONTRIBUTING.md` | Developer guidelines, code standards, workflow |
| `API.md` | Complete API reference for all microservices |
| `PROJECT_STATUS.md` | Current progress, completed tasks, roadmap |
| This File | Navigation guide |

## 🏗️ Design & Architecture

| File | Purpose |
|------|---------|
| `design/microservice-boundaries.md` | Service boundaries, responsibilities, key endpoints |
| `design/openapi-auth.yaml` | OpenAPI spec: Auth service endpoints |
| `design/openapi-customer.yaml` | OpenAPI spec: Customer 360 / CIF service |
| `design/openapi-los.yaml` | OpenAPI spec: Loan Origination System |
| `design/openapi-lms.yaml` | OpenAPI spec: Loan Management System |
| `design/openapi-collections.yaml` | OpenAPI spec: Collections workflow |
| `design/openapi-findna.yaml` | OpenAPI spec: FinDNA behavioral intelligence |
| `design/openapi-crm.yaml` | OpenAPI spec: CRM service |
| `design/openapi-accounting.yaml` | OpenAPI spec: Accounting service |
| `design/openapi-deposits.yaml` | OpenAPI spec: Deposits service |
| `design/openapi-document.yaml` | OpenAPI spec: Document service |
| `design/openapi-compliance.yaml` | OpenAPI spec: Compliance service |

## 🔧 Backend Services

### Auth Service
```
services/auth/
├── app/
│   ├── main.py              ← Auth endpoints (login, user CRUD, roles)
│   ├── config.py            ← Settings & environment variables
│   ├── database.py          ← SQLAlchemy session & DB connection
│   ├── models.py            ← User, Role entities
│   ├── schemas.py           ← Pydantic request/response schemas
│   └── security.py          ← JWT & password hashing utilities
├── requirements.txt         ← Python dependencies
├── Dockerfile               ← Docker image definition
├── .env.example             ← Environment variable template
└── README.md                ← Service documentation
```

### Other Services (LOS, LMS, Collections, FinDNA)
Similar structure — add endpoints as you implement features.

## 🗄️ Database

| File | Purpose |
|------|---------|
| `infra/migrations/001_create_auth_tables.sql` | Users, Roles, Permissions |
| `infra/migrations/002_create_customer_tables.sql` | Customers, KYC, Addresses |
| `infra/migrations/003_create_los_tables.sql` | Applications, Scorecards, Underwriting |
| `infra/migrations/004_create_lms_tables.sql` | Loan accounts, EMI, Payments |
| `infra/migrations/005_create_collections_tables.sql` | Collections, Settlements, NPA |
| `infra/migrations/006_seed_data.sql` | Initial data (roles, products) |
| `infra/migrations/README.md` | How to run migrations |

## 🐳 Infrastructure & DevOps

| File | Purpose |
|------|---------|
| `infra/docker-compose.yml` | Local development setup (all services) |
| `infra/k8s/README.md` | Kubernetes deployment guides (TBD) |
| `services/{service}/Dockerfile` | Docker image for each service |

## 📱 Frontend (TBD)

| Folder | Purpose |
|--------|---------|
| `apps/customer-app/` | Next.js web portal (to be scaffolded) |
| `apps/mobile-app/` | Flutter mobile app (to be scaffolded) |

## 📋 Configuration

| File | Purpose |
|------|---------|
| `.gitignore` | Git ignore patterns (Python, Node, build artifacts) |
| `services/auth/.env.example` | Environment variable template |
| `infra/docker-compose.yml` | Docker Compose configuration |

## 🧪 Testing (TBD)

| Folder | Purpose |
|--------|---------|
| `services/{service}/tests/` | Unit & integration tests per service |
| `tests/e2e/` | End-to-end test scenarios |

## 🔑 Key Quick Links

### For Developers

- **Want to understand the architecture?** → Read `design/microservice-boundaries.md`
- **Need to implement a new endpoint?** → Check corresponding `design/openapi-*.yaml`
- **Setting up locally?** → Follow `SETUP.md`
- **Coding standards?** → See `CONTRIBUTING.md`
- **What's been done?** → Check `PROJECT_STATUS.md`
- **API testing?** → Go to `API.md`

### For DevOps/SRE

- **Local development setup?** → `infra/docker-compose.yml`
- **Database migrations?** → `infra/migrations/README.md`
- **Kubernetes?** → `infra/k8s/` (TBD)
- **CI/CD?** → `.github/workflows/` (TBD)

### For Product/Business

- **Project overview?** → `README.md`
- **Current status & roadmap?** → `PROJECT_STATUS.md`
- **Features & timeline?** → `README.md` > Roadmap section

---

## 🚀 Quick Navigation Commands

```bash
# Navigate to a service
cd C:\NBFCSUITE\services\auth

# View database migrations
ls C:\NBFCSUITE\infra\migrations\

# Check API specs
ls C:\NBFCSUITE\design\openapi-*.yaml

# View Docker setup
cat C:\NBFCSUITE\infra\docker-compose.yml
```

---

## 📝 File Naming Conventions

- **SQL migrations:** `{number}_{description}.sql` (e.g., `001_create_auth_tables.sql`)
- **OpenAPI specs:** `openapi-{service}.yaml` (e.g., `openapi-auth.yaml`)
- **Dockerfiles:** `Dockerfile` (per service)
- **Environment files:** `.env` (git-ignored), `.env.example` (template)
- **Python modules:** `snake_case.py` (e.g., `models.py`, `schemas.py`)

---

## 🔄 Development Workflow

1. **Pick a task** from `PROJECT_STATUS.md`
2. **Read the design** from `design/microservice-boundaries.md` & OpenAPI specs
3. **Follow setup** from `SETUP.md`
4. **Write code** in `services/{service}/app/`
5. **Add tests** in `services/{service}/tests/`
6. **Commit & submit PR** following `CONTRIBUTING.md`
7. **Update docs** if needed

---

## 📞 Still Lost?

- Check `CONTRIBUTING.md` for contact info
- Review corresponding OpenAPI spec for endpoint details
- Read service-specific `README.md` file
- Ask in Slack: `#nbfcsuite-dev`

---

**Last Updated:** 2026-06-26  
**Maintainer:** NBFCSUITE Team
