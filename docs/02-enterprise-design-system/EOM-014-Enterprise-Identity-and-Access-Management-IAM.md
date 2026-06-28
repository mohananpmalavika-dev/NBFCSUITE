# EP-014 — Enterprise Identity & Access Management (IAM)

## Overview

Enterprise Identity & Access Management is the security backbone of ARTH.OS. It controls authentication, authorization, MFA, SSO, RBAC, ABAC, delegation, session management, API security, and approval authority.

This module is not a simple users-and-roles screen. It is the platform control plane used by every API, screen, workflow, and mobile application in the enterprise suite.

---

## Vision

IAM ensures that the right person, at the right time, from the right device, with the right access, can perform the right action.

It provides:

- Authentication
- Authorization
- MFA
- SSO
- RBAC
- ABAC
- Delegation
- Session management
- API security
- Approval authority
- Auditability

---

## IAM Architecture

```text
Identity Layer
│
├── Authentication
├── Authorization
├── Access Policies
├── Workflow Authority
└── Audit
```

---

## Enterprise Security Model

```text
Enterprise
↓
Legal Entity
↓
Business Unit
↓
Branch
↓
Department
↓
Position
↓
Role
↓
Permission
↓
User
```

### Core Principle

- Employees are assigned to positions
- Positions receive roles
- Roles receive permissions
- Permissions are never assigned directly to employees

---

## IAM Modules

```text
Identity
Authentication
Authorization
Roles
Permissions
User Groups
Delegation
Session
SSO
MFA
API Keys
OAuth
Audit
Password Policy
Device Management
Access Requests
Privileged Access
Secrets
```

---

## User Lifecycle

```text
Create User
↓
Identity Verification
↓
Approval
↓
Role Assignment
↓
Position Mapping
↓
MFA Setup
↓
Activation
↓
Login
```

---

## IAM Dashboard

### KPIs

- Users
- Active Users
- Locked Users
- MFA Enabled
- SSO Users
- Failed Logins
- Active Sessions
- Delegated Access
- High Risk Users
- Dormant Accounts

### Charts

- Login trend
- MFA adoption
- Failed logins
- User growth
- Access requests
- Security events

---

## Workspace

```text
Dashboard
↓
Users
↓
Roles
↓
Permissions
↓
Access Policies
↓
Sessions
↓
Devices
↓
Audit
↓
Reports
```

---

## User Profile

### Tabs

- Overview
- Identity
- Organization
- Roles
- Permissions
- Devices
- Sessions
- Delegation
- Security
- Timeline
- Audit
- AI

---

## User Creation Wizard

### Step 1 — Identity

Fields:

- Employee
- Username
- Email
- Phone
- Photo

### Step 2 — Organization

Fields:

- Enterprise
- Legal Entity
- Business Unit
- Branch
- Department
- Position

### Step 3 — Access

Fields:

- Role
- Additional Roles
- Approval Authority
- Temporary Access

### Step 4 — Security

Fields:

- Password Policy
- MFA
- Authenticator
- Biometric
- FIDO Key

### Step 5 — Review

- Review summary
- Approval route
- Activate account

---

## Role Hierarchy

```text
Enterprise Admin
↓
Business Head
↓
Regional Manager
↓
Branch Manager
↓
Operations Manager
↓
Officer
↓
Executive
```

---

## Permission Categories

```text
View
Create
Edit
Delete
Approve
Export
Import
Print
Override
Configure
```

---

## Permission Matrix

Example:

```text
Module | View | Create | Edit | Approve
Customer | ✓ | ✓ | ✓ | ✓
Loan | ✓ | ✓ | ✓ | ✓
Deposit | ✓ | ✓ | ✓ | ✓
Accounting | ✓ | ✓ | Limited | Limited
HR | Limited | Limited | Limited | Limited
```

---

## Resource-Based Security

Access can be restricted by:

- Enterprise
- Legal Entity
- Business Unit
- Branch
- Department
- Customer
- Loan Account
- Vault

Example:

```text
Branch Manager
Can access only Branch 102
```

---

## Attribute-Based Access (ABAC)

Examples:

```text
Loan Amount > ₹50 Lakhs → Require Regional Manager
```

or

```text
Gold Loan → Only Gold Appraisers
```

---

## Delegation

Example:

```text
Branch Manager on leave
↓
Delegate Assistant Manager
↓
7 days
```

Delegation should be automatic and expiration-based.

---

## Session Management

Track:

- Active sessions
- Login time
- IP address
- Browser
- Location
- Device
- Risk score

Force logout should be supported.

---

## Device Management

Supported devices:

- Laptop
- Mobile
- Tablet
- Desktop
- Biometric device

Unknown devices should be blocked or challenged.

---

## MFA

Supports:

- OTP
- Authenticator apps
- Push notification
- Biometric
- Security key (FIDO2 / WebAuthn)

Risk-based MFA should be configurable.

---

## Single Sign-On

Supports:

- SAML 2.0
- OAuth 2.0
- OpenID Connect
- LDAP
- Active Directory
- Azure AD
- Google Workspace

---

## Password Policy

Configurable:

- Length
- Complexity
- History
- Expiry
- Lockout
- Passwordless support (optional)

---

## Privileged Access Management

Special handling for:

- Enterprise Admin
- DBA
- Security Admin
- Auditor
- Treasury Admin

Features:

- Time-bound access
- Approval workflow
- Session recording
- Emergency access / break-glass access

---

## API Security

Supports:

- OAuth2
- JWT
- Refresh tokens
- API keys
- Service accounts
- Token rotation
- Rate limiting

---

## Audit

Every action should be recorded, including:

- Login
- Logout
- Failed login
- Password change
- Role assignment
- Permission change
- Approval configuration

Logs should be immutable.

---

## AI Features

Examples:

```text
Detect suspicious login
↓
Recommend permission cleanup
↓
Find dormant users
↓
Detect toxic permission combinations
↓
Predict insider risk
↓
Recommend least privilege
```

---

## Security Health Score

Calculated from:

- MFA adoption
- Dormant accounts
- Failed logins
- Excessive privileges
- Password compliance
- Device compliance
- Delegation issues

Example:

```text
Security Health Score: 96% ★★★★★
```

---

## Database Tables

```text
user
role
permission
role_permission
user_role
position_role
access_policy
delegation
session
device
mfa
password_history
api_key
service_account
oauth_client
audit_log
security_event
access_request
approval_authority
```

---

## APIs

```text
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/users
POST   /api/v1/users
PUT    /api/v1/users/{id}
GET    /api/v1/roles
POST   /api/v1/roles
GET    /api/v1/permissions
GET    /api/v1/access-policies
POST   /api/v1/delegations
GET    /api/v1/sessions
GET    /api/v1/security/dashboard
```

---

## Events

```text
USER_CREATED
USER_ACTIVATED
USER_LOCKED
ROLE_ASSIGNED
PERMISSION_GRANTED
MFA_ENABLED
SESSION_STARTED
SESSION_TERMINATED
DELEGATION_CREATED
ACCESS_REQUEST_APPROVED
```

---

## Backend Structure

```text
services/iam/
├── identity/
├── authentication/
├── authorization/
├── roles/
├── permissions/
├── policies/
├── sessions/
├── devices/
├── mfa/
├── oauth/
├── audit/
└── analytics/
```

---

## Frontend Structure

```text
modules/iam/
├── dashboard/
├── users/
├── roles/
├── permissions/
├── groups/
├── policies/
├── sessions/
├── devices/
├── delegation/
├── audit/
├── reports/
└── components/
```

---

## Integration Matrix

- HRMS: employee to user provisioning
- Workflow: approval authority
- Accounting: financial approvals
- Treasury: high-security operations
- Lending: loan approvals
- Deposits: teller permissions
- Gold Loan: appraiser authorization
- CRM: customer access control
- DMS: document permissions
- API Gateway: token validation

---

## Enterprise Security 360

Every user gets a Security 360 profile.

### Identity View

- Employee
- Position
- Branch
- Department

### Access View

- Roles
- Permissions
- Policies
- Delegations

### Activity View

- Login history
- Devices
- Sessions
- API usage

### Risk View

- Failed logins
- Privilege score
- Security incidents
- Compliance status

### AI View

- Risk score
- Least-privilege recommendations
- Suspicious behavior alerts
- Access optimization

---

## Definition of Done

IAM is complete when it supports:

- Enterprise authentication
- RBAC + ABAC
- Position-based access control
- MFA
- SSO
- Delegation
- Privileged Access Management
- Session management
- API security
- Immutable audit logs
- AI-driven security insights

---

## Major Architectural Recommendation

ARTH.OS should go beyond classic RBAC and implement PBAC (Position-Based Access Control) as the primary model.

The access hierarchy should be:

```text
Employee
↓
Position
↓
Role
↓
Permission
↓
Policy
↓
Resource
```

This simplifies administration, reduces permission errors, and scales better for enterprises with thousands of employees and frequent transfers.

---

## Recommended Next Step

With IAM complete, the next foundational platform service should be the Enterprise Document Management System (DMS).

This will provide:

- Central document repository
- OCR and intelligent indexing
- Version control
- Digital signatures
- Document workflows
- Retention and archival policies
- Access control integration with IAM
- Document templates
- AI-powered document classification and extraction
