# Database Migrations — NBFCSUITE

This directory contains PostgreSQL migration scripts to set up the database schema for the NBFC Operating System.

## Migration Files

- `001_create_auth_tables.sql` — Users, Roles, Permissions, RBAC foundation
- `002_create_customer_tables.sql` — Customers (CIF), Addresses, KYC documents, Financial profiles
- `003_create_los_tables.sql` — Loan Origination System (LOS): Applications, Documents, Scorecards, Underwriting
- `004_create_lms_tables.sql` — Loan Management System (LMS): Accounts, EMI schedules, Payments, Modifications
- `005_create_collections_tables.sql` — Collections: Buckets, Assignments, Activities, Settlements, NPA, Legal cases
- `006_seed_data.sql` — Initial seed data: Roles, Permissions, Loan products, Collection buckets
- `007_create_findna_tables.sql` — FinDNA/AI scoring, fraud, churn, embeddings
- `008_create_crm_tables.sql` — CRM leads, campaigns, opportunities
- `009_create_accounting_tables.sql` — Accounting GL, journal entries, bank reconciliation
- `010_create_deposits_tables.sql` — Deposit products, deposit accounts, standing instructions
- `011_create_document_tables.sql` — Document registry, versioning, expiry tracking
- `012_create_compliance_tables.sql` — Watchlist, compliance checks, audit logs

## Running Migrations

### Prerequisites

- PostgreSQL 12+ installed
- Database created (e.g., `nbfcsuite`)
- Connection details ready

### Manual Migration (Using psql)

```bash
# Connect to the database
psql -U nbfc_user -d nbfcsuite -h localhost

# Run migrations in order
\i 001_create_auth_tables.sql
\i 002_create_customer_tables.sql
\i 003_create_los_tables.sql
\i 004_create_lms_tables.sql
\i 005_create_collections_tables.sql
\i 006_seed_data.sql

# Verify
\dt                 # List all tables
\d users            # Describe users table
```

### Automated Migration (Using Docker)

A migration script will be added to `docker-compose.yml` to auto-run migrations on startup.

### Reverting Migrations

If needed, you can drop tables (warning: destructive):

```sql
DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS permissions CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS users CASCADE;
-- ... repeat for other tables
```

## Schema Overview

### Core Domains

**Auth Domain**
- `users`, `roles`, `permissions`, `user_roles`, `role_permissions`

**Customer Domain**
- `customers`, `customer_addresses`, `kyc_documents`, `customer_financial_profiles`

**LOS Domain**
- `loan_products`, `loan_applications`, `application_documents`, `application_scorecards`, `underwriting_assignments`

**LMS Domain**
- `loan_accounts`, `emi_schedule`, `payment_transactions`, `loan_modifications`, `loan_charges`

**Collections Domain**
- `collection_buckets`, `collection_assignments`, `collection_activities`, `settlement_negotiations`, `npa_records`, `legal_cases`

## Next Steps

- Add migrations for Deposits, Accounts, Treasury, Payments, Accounting modules
- Implement migration tool (Alembic or Flyway) for version tracking
- Add data validation and audit trail tables
