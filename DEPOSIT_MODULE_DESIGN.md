# 🏦 Deposit Management Module - Complete Design

**Date**: July 5, 2026  
**Status**: 🚀 Starting Implementation  
**Priority**: HIGH - Core Banking Feature for Nidhi Companies

---

## 🎯 Module Overview

The Deposit Management module handles all deposit operations for Nidhi companies and NBFCs, including Savings Accounts (CASA), Fixed Deposits (FD), Recurring Deposits (RD), and Monthly Income Scheme (MIS).

### Business Value
- **Revenue Generation**: Interest income from deposits
- **Customer Retention**: Attractive deposit schemes
- **Regulatory Compliance**: RBI/NABARD guidelines
- **Liquidity Management**: Deposit portfolio tracking

---

## 📋 Deposit Types

### 1. Savings Account (CASA)
- Current and Savings Account
- Variable balance with interest
- Daily/Monthly interest calculation
- Minimum balance requirement
- Transaction limits (daily/monthly)
- Passbook generation

### 2. Fixed Deposit (FD)
- Lump sum deposit for fixed tenure
- Fixed interest rate
- Tenure: 7 days to 10 years
- Premature withdrawal with penalty
- Auto-renewal option
- Loan against FD
- Cumulative and non-cumulative options

### 3. Recurring Deposit (RD)
- Monthly fixed installments
- Fixed tenure (6 months to 10 years)
- Interest compounded quarterly
- Maturity amount calculation
- Missed installment penalty
- Premature closure with penalty

### 4. Monthly Income Scheme (MIS)
- Lump sum deposit
- Monthly interest payout
- Fixed tenure (1-5 years)
- Principal returned at maturity
- No premature withdrawal (or heavy penalty)

---

## 🗄️ Database Schema

### 1. Deposit Products Table
```sql
CREATE TABLE deposit_products (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Product Details
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL, -- savings, fd, rd, mis
    description TEXT,
    
    -- Interest Configuration
    interest_rate DECIMAL(5,2) NOT NULL,
    interest_calculation_method VARCHAR(50) NOT NULL, -- simple, compound
    interest_calculation_frequency VARCHAR(50) NOT NULL, -- daily, monthly, quarterly
    interest_payout_frequency VARCHAR(50), -- monthly, quarterly, maturity
    
    -- Tenure Configuration (for FD/RD/MIS)
    min_tenure_days INTEGER,
    max_tenure_days INTEGER,
    tenure_unit VARCHAR(20), -- days, months, years
    
    -- Amount Configuration
    min_deposit_amount DECIMAL(15,2) NOT NULL,
    max_deposit_amount DECIMAL(15,2),
    
    -- For Savings
    min_balance DECIMAL(15,2),
    min_balance_penalty DECIMAL(10,2),
    
    -- For RD
    installment_amount DECIMAL(15,2),
    installment_frequency VARCHAR(50), -- monthly, quarterly
    missed_installment_penalty DECIMAL(5,2),
    
    -- Withdrawal Rules
    premature_withdrawal_allowed BOOLEAN DEFAULT false,
    premature_withdrawal_penalty DECIMAL(5,2),
    max_withdrawals_per_month INTEGER,
    
    -- Renewal
    auto_renewal_allowed BOOLEAN DEFAULT false,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_deposit_product_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
```


### 2. Deposit Accounts Table
```sql
CREATE TABLE deposit_accounts (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL, -- DEP-YYYYMM-XXXX
    
    -- Links
    customer_id INTEGER NOT NULL,
    deposit_product_id INTEGER NOT NULL,
    
    -- Account Details
    account_type VARCHAR(50) NOT NULL, -- savings, fd, rd, mis
    principal_amount DECIMAL(15,2) NOT NULL,
    current_balance DECIMAL(15,2) NOT NULL,
    interest_earned DECIMAL(15,2) DEFAULT 0,
    total_deposits DECIMAL(15,2) DEFAULT 0,
    total_withdrawals DECIMAL(15,2) DEFAULT 0,
    
    -- Interest Details
    interest_rate DECIMAL(5,2) NOT NULL,
    last_interest_date DATE,
    next_interest_date DATE,
    
    -- Tenure (for FD/RD/MIS)
    tenure_days INTEGER,
    opening_date DATE NOT NULL,
    maturity_date DATE,
    maturity_amount DECIMAL(15,2),
    
    -- For RD
    installment_amount DECIMAL(15,2),
    installments_paid INTEGER DEFAULT 0,
    total_installments INTEGER,
    next_installment_date DATE,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- active, matured, closed, premature_closed
    
    -- Renewal
    auto_renewal BOOLEAN DEFAULT false,
    renewal_count INTEGER DEFAULT 0,
    
    -- Closure
    closure_date DATE,
    closure_amount DECIMAL(15,2),
    premature_closure BOOLEAN DEFAULT false,
    penalty_amount DECIMAL(10,2),
    
    -- Nomination
    nominee_name VARCHAR(200),
    nominee_relationship VARCHAR(100),
    nominee_dob DATE,
    nominee_percentage DECIMAL(5,2) DEFAULT 100,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_deposit_account_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_deposit_account_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_deposit_account_product FOREIGN KEY (deposit_product_id) REFERENCES deposit_products(id)
);
```

### 3. Deposit Transactions Table
```sql
CREATE TABLE deposit_transactions (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    deposit_account_id INTEGER NOT NULL,
    
    transaction_number VARCHAR(50) UNIQUE NOT NULL, -- TXN-YYYYMMDD-XXXX
    transaction_type VARCHAR(50) NOT NULL, -- deposit, withdrawal, interest_credit, penalty, opening, closure
    
    amount DECIMAL(15,2) NOT NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    
    transaction_date DATE NOT NULL,
    value_date DATE NOT NULL,
    
    payment_mode VARCHAR(50), -- cash, cheque, neft, rtgs, imps, upi
    reference_number VARCHAR(100),
    
    remarks TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    
    CONSTRAINT fk_deposit_txn_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_deposit_txn_account FOREIGN KEY (deposit_account_id) REFERENCES deposit_accounts(id)
);
```


### 4. Interest Calculations Table
```sql
CREATE TABLE deposit_interest_calculations (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    deposit_account_id INTEGER NOT NULL,
    
    calculation_period_start DATE NOT NULL,
    calculation_period_end DATE NOT NULL,
    
    opening_balance DECIMAL(15,2) NOT NULL,
    average_balance DECIMAL(15,2),
    
    interest_rate DECIMAL(5,2) NOT NULL,
    days_in_period INTEGER NOT NULL,
    interest_amount DECIMAL(10,2) NOT NULL,
    
    calculation_method VARCHAR(50) NOT NULL,
    
    posted BOOLEAN DEFAULT false,
    posted_date DATE,
    transaction_id INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_interest_calc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_interest_calc_account FOREIGN KEY (deposit_account_id) REFERENCES deposit_accounts(id)
);
```

---

## 💼 BUSINESS LOGIC

### Interest Calculation Methods

#### 1. Simple Interest (for FD/MIS)
```
Interest = Principal × Rate × Time / 100
Maturity Amount = Principal + Interest
```

#### 2. Compound Interest (for FD/RD)
```
Maturity Amount = Principal × (1 + Rate/Frequency)^(Frequency × Time)
Interest = Maturity Amount - Principal
```

#### 3. Daily Balance Interest (for Savings)
```
Interest = Σ(Daily Balance × Rate × Days / 365) / 100
```

#### 4. Monthly Average Balance (for Savings)
```
Average Balance = Sum of Daily Balances / Days in Month
Interest = Average Balance × Rate × Days / (100 × 365)
```

### RD Maturity Calculation
```
M = P × n × (n + 1) / 2 × r / 1200
Where:
  M = Maturity Amount
  P = Monthly Installment
  n = Number of Installments
  r = Interest Rate (per annum)
```

### Premature Withdrawal Penalty
```
Penalty = Reduced Interest Rate × Principal × Time / 100
Payout = Principal + Interest at Reduced Rate - Penalty Charges
```

---

## 🔧 KEY FEATURES

### 1. Account Opening
- Customer KYC verification
- Product selection
- Nomination setup
- Initial deposit (for FD/MIS/Savings)
- Auto-generate account number
- Passbook generation

### 2. Deposits & Withdrawals
- Multiple payment modes
- Real-time balance update
- Transaction receipt
- Minimum balance check (Savings)
- Withdrawal limits validation

### 3. Interest Calculation
- Automated daily/monthly calculation
- Configurable posting frequency
- TDS calculation and deduction
- Interest certificate generation

### 4. Maturity Processing
- Automated maturity detection
- Interest + Principal payout
- Auto-renewal option
- Maturity notification (SMS/Email)

### 5. Premature Closure
- Penalty calculation
- Reduced interest rate application
- Final settlement amount
- Closure certificate

---

## 📊 API Endpoints Structure

### Deposit Products (8 endpoints)
- POST /deposit-products - Create product
- GET /deposit-products - List products
- GET /deposit-products/{id} - Get product
- PUT /deposit-products/{id} - Update product
- DELETE /deposit-products/{id} - Delete product
- GET /deposit-products/active - Active products
- POST /deposit-products/calculate-maturity - Calculate maturity
- POST /deposit-products/calculate-interest - Calculate interest

### Deposit Accounts (12 endpoints)
- POST /deposit-accounts - Open account
- GET /deposit-accounts - List accounts
- GET /deposit-accounts/{id} - Get account details
- GET /deposit-accounts/customer/{id} - Customer accounts
- PUT /deposit-accounts/{id} - Update account
- POST /deposit-accounts/{id}/deposit - Make deposit
- POST /deposit-accounts/{id}/withdraw - Make withdrawal
- POST /deposit-accounts/{id}/close - Close account
- POST /deposit-accounts/{id}/renew - Renew account
- GET /deposit-accounts/{id}/passbook - Get passbook
- GET /deposit-accounts/{id}/statement - Account statement
- GET /deposit-accounts/maturity-due - Accounts due for maturity

### Interest & Calculations (5 endpoints)
- POST /deposit-interest/calculate - Calculate interest
- POST /deposit-interest/post - Post interest
- GET /deposit-interest/{account_id} - Interest history
- GET /deposit-interest/certificate/{account_id} - Interest certificate
- POST /deposit-interest/batch-calculate - Batch calculation

### Transactions (3 endpoints)
- GET /deposit-transactions/{account_id} - Account transactions
- GET /deposit-transactions/receipt/{txn_id} - Transaction receipt
- GET /deposit-transactions/search - Search transactions

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Foundation (Current)
- Database models
- Product service
- Basic CRUD operations

### Phase 2: Core Operations
- Account opening
- Deposit/Withdrawal
- Transaction management

### Phase 3: Interest Engine
- Interest calculation service
- Automated posting
- TDS handling

### Phase 4: Maturity & Closure
- Maturity processing
- Auto-renewal
- Premature closure

---

## ✅ Ready to Build!

Next steps:
1. Create database models
2. Build product service
3. Build account service
4. Build interest calculation service
5. Create API routers
6. Build Pydantic schemas
7. Integration & testing

Let's begin! 🚀
