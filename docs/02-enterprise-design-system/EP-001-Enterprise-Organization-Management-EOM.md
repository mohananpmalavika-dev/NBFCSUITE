# EP-001 — Enterprise Organization Management (EOM)

## Overview

Enterprise Organization Management is the master organizational backbone of ARTH.OS. It is not a simple HR module. It is the foundation used by every product and every business domain in the platform.

Every major business object ultimately connects back to EOM:

- Customer
- Branch
- Area
- Region
- Zone
- Enterprise
- Department
- Cost center
- Profit center
- Position
- Employee

This makes EOM the shared operating model for the entire enterprise platform.

---

## Vision

EOM should act as a digital enterprise twin for the organization.

Every organizational object should expose:

- Operational view
- Financial view
- People view
- Risk view
- Performance view
- Document view
- AI insights

This makes ARTH.OS much more powerful than traditional banking software because all modules share the same organizational model instead of maintaining fragmented, duplicated structures.

---

## Enterprise Hierarchy

The organization hierarchy should be configurable and support the following structure:

Enterprise → Brand → Legal Entity → Business Group → Business Unit → Zone → Region → Area → Cluster → Branch → Department → Section → Team → Position → Employee

This hierarchy should be available to HRMS, Accounting, Lending, Deposits, Treasury, Procurement, CRM, Risk, and other modules.

---

## Master Modules

### Organization

Contains:

- Enterprise
- Brand
- Company
- Legal Entity
- Business Unit

### Geography

Contains:

- Country
- State
- District
- City
- Zone
- Region
- Area
- Cluster

### Branch Network

Contains:

- Branch
- Branch type
- Branch category
- Branch timing
- Branch services
- Branch contacts

### Organization Structure

Contains:

- Department
- Section
- Team
- Designation
- Grade
- Position

### Financial Mapping

Contains:

- Cost center
- Profit center
- Business segment
- GL mapping
- Budget owner

### Approval Structure

Contains:

- Reporting manager
- Functional manager
- Approvers
- Delegates
- Escalation matrix

---

## EOM Dashboard

The EOM dashboard should provide an executive operational view of the enterprise.

Suggested widgets:

- Enterprises
- Brands
- Branches
- Departments
- Employees
- Positions
- Open approvals

Suggested charts:

- Branch growth
- Employee distribution
- Organization hierarchy
- Department budget
- Branch status

---

## Workspace Structure

The EOM workspace should follow a consistent experience:

- Dashboard
- Enterprise list
- Hierarchy explorer
- Organization chart
- Branch network
- Reports

---

## Organization Explorer

The organization explorer is the most important EOM screen.

It should provide a tree-based view of the enterprise:

- Enterprise
  - Brand
    - Company
      - Business unit
        - Zone
          - Region
            - Area
              - Branch
                - Department
                  - Position
                    - Employee

The explorer should support:

- Expand / collapse
- Lazy loading
- Search
- Detailed drill-down

---

## Branch Module

The branch profile should be a rich operational workspace.

Suggested sections:

- Overview
- Address
- Contacts
- Working hours
- Cash limits
- Vault
- Employees
- Departments
- Products and services
- Assets
- Audit timeline

---

## Department Module

The department module should show:

- Overview
- Employees
- Positions
- Cost center
- Budget
- Approvers
- Documents
- Timeline

---

## Position Module

The position module should capture:

- Position
- Designation
- Grade
- Department
- Reporting manager
- Vacancy
- Status

---

## Cost Center

Cost center records should support:

- General details
- Budget
- Manager
- Departments
- GL mapping
- Reports

---

## Profit Center

Profit center records should support:

- Revenue details
- Expenses
- Business units
- Departments
- Reports

---

## Organization Chart

The organization chart should support:

- Hierarchy view
- Reporting structure
- Department structure
- Position view
- Employee view

It should be interactive and support:

- Zoom
- Search
- Export

---

## Branch Network Map

The branch network map should visualize geography from:

- Country
- State
- Region
- Area
- Branch

This should provide a geographic operational view of the enterprise footprint.

---

## EOM Wizards

Every object should be created through a guided wizard.

### Enterprise wizard

Suggested steps:

- Basic details
- Brand selection
- Legal entity setup
- Address
- Settings
- Review

### Branch wizard

Suggested steps:

- Basic details
- Location
- Departments
- Services
- Cash configuration
- Review

### Department wizard

Suggested steps:

- Basic details
- Hierarchy placement
- Cost center
- Approvers
- Review

---

## Workflow Integration

EOM should use the shared workflow framework.

Examples:

### Branch creation workflow

Draft → Submit → Operations approval → Finance approval → IT approval → Created

### Department creation workflow

HR → Finance → Completed

---

## Permissions

The platform should support role-based visibility and action permissions.

Suggested roles:

- Enterprise admin: full access
- Zone manager: own zone only
- Regional manager: own region only
- Area manager: own area only
- Branch manager: own branch only
- Department head: own department only

---

## Search

Search should be universal across EOM objects.

Supported entities:

- Enterprise
- Brand
- Branch
- Department
- Employee
- Cost center
- Profit center

---

## Reports

The module should provide standard reports such as:

- Branch list
- Branch hierarchy
- Department list
- Cost center report
- Profit center report
- Position vacancy
- Reporting structure
- Employee distribution
- Branch performance
- Organization tree

---

## AI Features

EOM should include AI-driven assistance such as:

- Show vacant positions
- Suggest reporting changes
- Find duplicate branches
- Recommend organization optimization
- Predict staffing needs
- Show overloaded managers

---

## Database Domains

The EOM domain model should be organized around the following business entities:

- enterprise
- brand
- legal_entity
- business_unit
- zone
- region
- area
- cluster
- branch
- department
- section
- team
- designation
- grade
- position
- cost_center
- profit_center
- reporting
- approval_matrix

Each should be treated as a first-class domain or aggregate.

---

## Event Catalog

Suggested standard events:

- ENTERPRISE_CREATED
- BRAND_CREATED
- BRANCH_CREATED
- BRANCH_UPDATED
- DEPARTMENT_CREATED
- POSITION_CREATED
- COSTCENTER_CREATED
- PROFITCENTER_CREATED
- ORG_CHANGED

---

## API Groups

Suggested API grouping:

- /api/eom/enterprise
- /api/eom/brand
- /api/eom/legal-entity
- /api/eom/business-unit
- /api/eom/zone
- /api/eom/region
- /api/eom/area
- /api/eom/cluster
- /api/eom/branch
- /api/eom/department
- /api/eom/designation
- /api/eom/grade
- /api/eom/position
- /api/eom/cost-center
- /api/eom/profit-center

---

## Folder Structure

A reference implementation should follow this structure:

services/eom/src/
├── enterprise/
├── brand/
├── legal_entity/
├── business_unit/
├── geography/
├── branch/
├── department/
├── designation/
├── grade/
├── position/
├── cost_center/
├── profit_center/
├── reporting/
├── approvals/
├── shared/
└── api/

---

## Implementation Roadmap

Instead of building everything in one release, EOM should be delivered in 15 implementation packages:

- EOM-001: Enterprise
- EOM-002: Brand
- EOM-003: Legal entity
- EOM-004: Business unit
- EOM-005: Geography
- EOM-006: Zone / Region / Area / Cluster
- EOM-007: Branch management
- EOM-008: Department management
- EOM-009: Section and team
- EOM-010: Grade
- EOM-011: Designation
- EOM-012: Position
- EOM-013: Cost center
- EOM-014: Profit center
- EOM-015: Organization explorer and org chart

---

## Definition of Done

Each package should only be considered complete when it includes:

- Business requirements
- UX screens
- Wizard flow
- Database schema
- ER diagram
- APIs
- Backend architecture
- Frontend architecture
- Permissions
- Workflow
- Audit capability
- Reports
- AI features
- Unit tests
- Integration tests

---

## Recommendation

The first implementation should be EOM-001 — Enterprise Master. This should include the complete business specification, screen-by-screen UI, database schema, APIs, FastAPI architecture, Next.js architecture, permission matrix, workflow integration, and production-ready code structure.

This will become the root entity on which every other organizational object depends.
