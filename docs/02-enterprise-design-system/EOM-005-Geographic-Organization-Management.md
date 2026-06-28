# EOM-005 — Geographic Organization Management (GOM)

## Overview

Geographic Organization Management is where ARTH.OS becomes significantly more powerful than traditional banking software. Most systems stop at Zone → Region → Branch, but ARTH.OS should support a fully configurable geographic organization model because different institutions organize operations differently.

- An NBFC may use Zone → Region → Area → Branch
- A cooperative bank may use District → Branch
- A global institution may use Country → State → City → Branch
- A sales organization may use Territory → Cluster → Branch

The hierarchy should be fully configurable.

---

## Vision

Provide a configurable geographical hierarchy that supports:

- Organization hierarchy
- Branch hierarchy
- Sales hierarchy
- Collection hierarchy
- Service hierarchy
- Compliance hierarchy
- Reporting hierarchy

---

## Geographic Hierarchy

### Default template

```text
World
│
└── Country
    │
    └── State / Province
        │
        └── District
            │
            └── City
                │
                └── Zone
                    │
                    └── Region
                        │
                        └── Area
                            │
                            └── Cluster
                                │
                                └── Branch
```

However, every level can be enabled or disabled.

Examples:

```text
Country → Region → Branch
```

or

```text
Country → State → District → Branch
```

---

## Business Objectives

The module should support:

- Unlimited hierarchy levels
- Configurable hierarchy
- GIS mapping
- Territory ownership
- Route planning
- Branch coverage
- Collections territories
- Sales territories

---

## Geographic Dashboard

### KPIs

- Countries
- States
- Districts
- Zones
- Regions
- Areas
- Clusters
- Branches
- Coverage %
- Population Served

### Charts

- Branch heatmap
- Geographic growth
- Revenue by geography
- Collections by geography
- Customer density
- Service coverage

---

## Workspace

```text
Dashboard
↓
Geography Explorer
↓
Map View
↓
Territory Management
↓
Coverage Analysis
↓
Reports
```

---

## Geography Explorer

### Tree view

```text
India
├── Kerala
│   ├── Kollam
│   │   ├── South Zone
│   │   ├── Region A
│   │   ├── Area 3
│   │   ├── Cluster 2
│   │   └── Branch
```

Features:

- Lazy loading
- Drag and drop
- Expand/collapse
- Search
- Bulk action

---

## Geographic Map

An interactive GIS map should display:

- Branches
- Territories
- Customers
- Sales
- Collections
- Heatmaps
- Radius
- Coverage

Supports:

- Zoom
- Layers
- Satellite view
- Street map view

---

## Geographic Objects

Every geography level shares common properties:

```text
Code
Name
Type
Parent
Status
Manager
Coordinates
Population
Area Size
Description
```

---

## Create Geography Wizard

### Step 1 — General

Fields:

- Geography Code
- Name
- Type
- Parent
- Status

### Step 2 — Location

Fields:

- Country
- State
- District
- City
- Latitude
- Longitude
- Geo Boundary

Polygon support should be included.

### Step 3 — Management

Fields:

- Manager
- Alternate Manager
- Business Unit
- Legal Entity
- Brand

### Step 4 — Operations

Fields:

- Branches
- Products
- Working Calendar
- Coverage Radius

### Step 5 — Financial

Fields:

- Budget
- Cost Center
- Profit Center

### Step 6 — Compliance

Fields:

- Regulatory Zone
- Risk Level
- Audit Frequency

### Step 7 — Documents

Upload:

- Boundary Maps
- Government Notifications
- Licenses
- Operational Manual

### Step 8 — Review

Flow:

```text
Review
↓
Submit
```

---

## Territory Types

The module should support multiple territory models.

### Sales

```text
Zone → Region → Sales Area
```

### Collections

```text
Region → Recovery Area → Collector Route
```

### Service

```text
Region → Service Area
```

### Audit

```text
Audit Region → Audit Circle
```

---

## Branch Assignment

Each branch belongs to a hierarchy such as:

```text
Country → State → District → Zone → Region → Area → Cluster
```

This hierarchy drives reporting and permissions.

---

## Territory Manager

Every geography level should support:

- Primary Manager
- Backup Manager
- Regional Head
- Functional Head

---

## Coverage Analysis

The module should show:

- Branch density
- Customer density
- Revenue density
- Service gaps
- Expansion opportunities

---

## Map Analytics

Examples of analytics:

- Customer concentration
- Loan portfolio
- Gold loan density
- NPA concentration
- Collection efficiency
- Cash movement

---

## Radius Search

Example:

```text
Find all branches within 25 KM
```

Useful for:

- Customer onboarding
- Service routing
- Emergency support

---

## Distance Matrix

Supports:

```text
Branch A → Branch B → Distance → Travel Time
```

Useful for:

- Cash logistics
- Gold transfer
- Audit planning
- Employee transfers

---

## Geographic KPIs

Examples:

- Branches
- Customers
- Employees
- Revenue
- Collections
- NPA
- Deposits
- Gold Portfolio
- Profit

These should be available per geography level.

---

## AI Features

Example capabilities:

```text
Suggest new branch location.
↓
Identify underserved regions.
↓
Predict branch demand.
↓
Optimize collection routes.
↓
Recommend area restructuring.
↓
Forecast customer growth.
```

---

## Reports

Standard reports should include:

- Geographic Hierarchy
- Branch Coverage
- Customer Distribution
- Revenue by Geography
- Collection Efficiency
- Territory Performance
- Expansion Opportunities
- Branch Density
- Route Analysis

---

## Permissions

| Role | Access |
| --- | --- |
| Enterprise Admin | All Geography |
| Zone Manager | Assigned Zone |
| Regional Manager | Assigned Region |
| Area Manager | Assigned Area |
| Cluster Manager | Assigned Cluster |
| Branch Manager | Assigned Branch |

---

## Database Tables

```text
country
state
district
city
zone
region
area
cluster
territory
geo_boundary
geo_manager
geo_budget
geo_document
geo_audit
geo_settings
```

---

## APIs

```text
GET    /api/v1/eom/geography/tree
GET    /api/v1/eom/geography/map
POST   /api/v1/eom/geography
PUT    /api/v1/eom/geography/{id}
GET    /api/v1/eom/geography/{id}
GET    /api/v1/eom/geography/{id}/analytics
GET    /api/v1/eom/geography/{id}/coverage
GET    /api/v1/eom/geography/search-radius
```

---

## Events

```text
GEOGRAPHY_CREATED
GEOGRAPHY_UPDATED
BOUNDARY_CHANGED
MANAGER_ASSIGNED
BRANCH_ASSIGNED
TERRITORY_CREATED
COVERAGE_UPDATED
GEO_ANALYTICS_UPDATED
```

---

## Backend Structure

```text
services/eom/geography/
├── domain/
├── application/
├── infrastructure/
├── api/
├── gis/
├── analytics/
├── events/
└── tests/
```

---

## Frontend Structure

```text
modules/eom/geography/
├── dashboard/
├── explorer/
├── map/
├── territory/
├── analytics/
├── reports/
├── settings/
├── components/
└── hooks/
```

---

## Integration Points

Geographic Organization Management should integrate with:

- Branch Management
- Customer Management
- Lending
- Deposits
- Collections
- Treasury
- Cash Logistics
- HRMS
- CRM
- Risk
- Analytics
- AI Platform

---

## Definition of Done

The module is complete when it supports:

- Configurable geography hierarchy
- GIS-enabled map visualization
- Territory management
- Radius search
- Coverage analysis
- Branch assignment
- Geographic analytics
- Workflow integration
- Audit trail
- AI recommendations

---

## Enterprise Recommendation

Rather than treating geography as static master data, it should be modeled as a Geographic Intelligence Platform.

Each geographic node should provide:

### Business View

- Customers
- Products
- Branches
- Revenue

### Operational View

- Employee distribution
- Branch capacity
- Cash logistics
- Service coverage

### Financial View

- Revenue
- Expenses
- Profitability
- Budget utilization

### Risk View

- NPA concentration
- Fraud hotspots
- Audit findings
- Compliance exceptions

### Market View

- Population
- Competitor branches
- Economic indicators
- Market penetration

### AI View

- Recommended branch expansion
- Territory optimization
- Collection route optimization
- Demand forecasting
- Risk heatmaps

This transforms geography from a simple hierarchy into a strategic decision-making platform for expansion, operations, and risk management.

---

## Updated EOM Roadmap

| Package | Status |
| --- | --- |
| EOM-001 Enterprise | Complete |
| EOM-002 Brand | Complete |
| EOM-003 Legal Entity | Complete |
| EOM-004 Business Unit | Complete |
| EOM-005 Geographic Organization | Complete |
| EOM-006 Zone / Region / Area / Cluster | Next |
| EOM-007 Branch Management | Pending |
| EOM-008 Department Management | Pending |
| EOM-009 Section & Team | Pending |
| EOM-010 Grade | Pending |
| EOM-011 Designation | Pending |
| EOM-012 Position | Pending |
| EOM-013 Cost Center | Pending |
| EOM-014 Profit Center | Pending |
| EOM-015 Organization Explorer & Org Chart | Pending |

## Recommendation

Instead of implementing Zone / Region / Area / Cluster as a completely separate module, they should be specialized geography types within the Geographic Organization Management framework. That avoids duplicated code, simplifies administration, and lets customers configure their own hierarchy without requiring new modules.

The next logical step should be EOM-007 — Branch Management, which is the operational heart of the organization and is referenced by HRMS, Customer, Lending, Deposits, Accounting, Treasury, CRM, and almost every other business module.
