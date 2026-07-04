# NBFCSUITE Setup Guide

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Docker & Docker Compose (optional, for containerized setup)

### 1. Set Up Database

#### Option A: Docker (Recommended)

```bash
cd C:\NBFCSUITE\infra
docker run --name nbfcsuite-postgres \
  -e POSTGRES_USER=nbfc_user \
  -e POSTGRES_PASSWORD=nbfc_pass \
  -e POSTGRES_DB=nbfcsuite \
  -p 5432:5432 \
  -d postgres:15-alpine
```

#### Option B: Local PostgreSQL

Create user and database:

```sql
CREATE USER nbfc_user WITH PASSWORD 'nbfc_pass';
CREATE DATABASE nbfcsuite OWNER nbfc_user;
```

### 2. Run Database Migrations

```bash
# Connect to PostgreSQL
psql -U nbfc_user -d nbfcsuite -h localhost

# Run migrations in order
\i C:\NBFCSUITE\infra\migrations\001_create_auth_tables.sql
\i C:\NBFCSUITE\infra\migrations\002_create_customer_tables.sql
\i C:\NBFCSUITE\infra\migrations\003_create_los_tables.sql
\i C:\NBFCSUITE\infra\migrations\004_create_lms_tables.sql
\i C:\NBFCSUITE\infra\migrations\005_create_collections_tables.sql
\i C:\NBFCSUITE\infra\migrations\006_seed_data.sql

# Exit psql
\q
```

### 3. Start Auth Service

```bash
# Navigate to auth service
cd C:\NBFCSUITE\services\auth

# Create virtual environment
python -m venv .venv
. .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start the service
uvicorn app.main:app --reload --port 8000
```

The service will start at `http://localhost:8000`.

### 4. Test Auth Service

#### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "service": "auth"}
```

#### Create a User

```bash
curl -X POST http://localhost:8000/auth/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password_123"
  }'
```

#### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password_123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get User Profile

```bash
curl http://localhost:8000/auth/users/{user_id} \
  -H "Authorization: Bearer {access_token}"
```

### 5. Using Docker Compose (Optional)

Once all services are scaffolded:

```bash
cd C:\NBFCSUITE\infra
docker compose up --build
```

## Project Structure

```
C:\NBFCSUITE\
├── apps/
│   ├── customer-app/         # Next.js web frontend
│   └── mobile-app/           # Flutter mobile app
├── services/
│   ├── auth/                 # Auth & IAM service
│   ├── los/                  # Loan Origination System
│   ├── lms/                  # Loan Management System
│   ├── collections/          # Collections service
│   ├── findna/               # AI/Behavioral Intelligence service
│   └── ...                   # Other services (TBD)
├── design/
│   ├── microservice-boundaries.md
│   ├── openapi-auth.yaml
│   ├── openapi-los.yaml
│   ├── openapi-lms.yaml
│   ├── openapi-collections.yaml
│   ├── openapi-customer.yaml
│   └── openapi-findna.yaml
├── infra/
│   ├── docker-compose.yml
│   ├── k8s/
│   └── migrations/           # SQL migration scripts
└── README.md
```

## Next Steps

1. Implement LOS service endpoints (loan application intake, document upload, scoring)
2. Implement LMS service endpoints (loan booking, EMI calculation, payments)
3. Implement Collections service endpoints
4. Build customer web app (Next.js)
5. Build mobile app (Flutter)
6. Implement FinDNA behavioral scoring engine
7. Set up CI/CD pipeline (GitHub Actions / Azure DevOps)
8. Deploy to Kubernetes

## Troubleshooting

### Database Connection Error

Check connection string in `.env`:
```
DATABASE_URL=postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite
```

### Port Already in Use

Change port in startup command:
```bash
uvicorn app.main:app --reload --port 8001
```

### Missing Python Dependencies

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```
