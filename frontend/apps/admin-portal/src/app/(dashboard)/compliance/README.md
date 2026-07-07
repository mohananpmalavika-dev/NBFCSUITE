# Compliance Module - Frontend Documentation

## Overview

Complete frontend implementation for CRILC & SMA Compliance Reporting module with real-time dashboards, tracking, and reporting capabilities.

## Pages Implemented

### 1. SMA Dashboard (`/compliance/sma-dashboard`)
**Real-time Special Mention Account monitoring dashboard**

Features:
- Key metrics (Total Accounts, Total Exposure, Provisions, Open Alerts)
- SMA classification breakdown (Standard, SMA-0, SMA-1, SMA-2, NPA)
- Portfolio health summary
- Quick action links
- Date filter for historical data
- Auto-refresh capability

Components:
- Stat cards with icons
- Classification cards with color coding
- Portfolio health analysis
- Skeleton loading states

### 2. Large Credits (`/compliance/large-credits`)
**CRILC Large Credit Borrower Management (≥₹5 Crore)**

Features:
- List all large credit borrowers
- Search by name, code, or PAN
- Filter by SMA status
- Large credit identification dialog
- Summary statistics
- Pagination support

Actions:
- Identify Large Credits (threshold-based)
- View borrower details
- Filter and search

### 3. SMA Tracking (`/compliance/sma-tracking`)
**Real-time SMA status tracking for loan accounts**

Features:
- Comprehensive tracking table
- SMA status with color-coded badges
- DPD (Days Past Due) monitoring
- Outstanding/overdue breakdown
- Provision calculations
- Alert indicators
- Calculate SMA dialog

Data Displayed:
- Loan account details
- As-on date and reporting quarter
- Current and previous SMA status
- Days past due
- Outstanding amounts (Principal + Interest)
- Overdue amounts
- Provision required and percentage
- Alert status

### 4. Compliance Alerts (`/compliance/alerts`)
**Manage and respond to compliance alerts**

Features:
- Alert listing with severity levels
- Status-based filtering (Open, Acknowledged, Resolved)
- Severity-based filtering (Low, Medium, High, Critical)
- Overdue indicators
- Acknowledge workflow
- Resolve workflow with notes
- Alert statistics dashboard

Alert Types:
- SMA status change
- Large credit threshold breach
- Overdue breach
- NPA risk

Actions:
- Acknowledge alert
- Resolve alert with resolution notes
- Filter by status and severity
- Search alerts

### 5. Quarterly Reports (`/compliance/quarterly-reports`)
**Generate and manage CRILC & SMA quarterly returns**

Features:
- Two tabs: CRILC Returns and SMA Reports
- Generate new returns dialog
- Return history table
- Status workflow (Draft → Approved → Submitted)
- Summary statistics
- Report metadata

CRILC Return Actions:
- Generate new return
- Approve return
- Submit to RBI
- View return details

Report Details:
- Return number
- Reporting quarter and year
- As-on date
- Total borrowers
- Total exposure
- SMA breakdown
- Status tracking

## Components Structure

```
src/app/(dashboard)/compliance/
├── sma-dashboard/
│   └── page.tsx          # SMA Dashboard
├── large-credits/
│   └── page.tsx          # Large Credits List
├── sma-tracking/
│   └── page.tsx          # SMA Tracking
├── alerts/
│   └── page.tsx          # Compliance Alerts
├── quarterly-reports/
│   └── page.tsx          # Quarterly Reports
└── README.md             # This file
```

## Services

### Compliance Service (`services/compliance.service.ts`)

API Methods:
- `getBorrowers()` - Fetch CRILC borrowers
- `getBorrower(id)` - Get single borrower
- `createBorrower()` - Create new borrower
- `updateBorrower()` - Update borrower
- `getBorrowerFacilities()` - Get borrower facilities
- `identifyLargeCredits()` - Run identification
- `calculateSMA()` - Calculate SMA status
- `getSMATracking()` - Get tracking records
- `getSMADashboard()` - Get dashboard stats
- `getAlerts()` - Get compliance alerts
- `acknowledgeAlert()` - Acknowledge alert
- `resolveAlert()` - Resolve alert
- `getQuarterlyReturns()` - Get CRILC returns
- `generateQuarterlyReturn()` - Generate return
- `approveQuarterlyReturn()` - Approve return
- `submitQuarterlyReturn()` - Submit to RBI

## Types

### Compliance Types (`types/compliance.types.ts`)

Key Interfaces:
- `CRILCBorrower` - Large credit borrower
- `CRILCFacility` - Credit facility
- `SMATracking` - SMA status tracking
- `SMAStatusHistory` - Status change history
- `SMADashboardStats` - Dashboard statistics
- `CRILCQuarterlyReturn` - Quarterly return
- `SMAQuarterlyReport` - SMA report
- `ComplianceAlert` - Alert entity

Enums:
- `BorrowerType` - Type of borrower
- `SMAStatus` - SMA classification
- `AssetClassification` - Asset class
- `FacilityType` - Type of facility
- `ReportStatus` - Report status
- `AlertSeverity` - Alert severity

## UI Components Used

### shadcn/ui Components
- `Card` - Content containers
- `Button` - Action buttons
- `Input` - Form inputs
- `Badge` - Status indicators
- `Table` - Data tables
- `Dialog` - Modal dialogs
- `Select` - Dropdowns
- `Tabs` - Tab navigation
- `Skeleton` - Loading states
- `Textarea` - Multi-line input
- `Label` - Form labels

### Icons (lucide-react)
- `AlertCircle`, `AlertTriangle` - Alerts
- `Users`, `DollarSign` - Stats
- `Calendar` - Dates
- `Search` - Search
- `RefreshCw` - Refresh
- `Calculator` - Calculate
- `CheckCircle` - Approve
- `Send` - Submit
- `Eye` - View
- `Shield` - Compliance

## Color Coding

### SMA Status Colors
- **Standard** (0 DPD): Green (`bg-green-100 text-green-800`)
- **SMA-0** (1-30 DPD): Yellow (`bg-yellow-100 text-yellow-800`)
- **SMA-1** (31-60 DPD): Orange (`bg-orange-100 text-orange-800`)
- **SMA-2** (61-90 DPD): Red (`bg-red-100 text-red-800`)
- **NPA** (>90 DPD): Dark Red (`bg-red-200 text-red-900`)

### Alert Severity Colors
- **Low**: Blue (`bg-blue-100 text-blue-800`)
- **Medium**: Yellow (`bg-yellow-100 text-yellow-800`)
- **High**: Orange (`bg-orange-100 text-orange-800`)
- **Critical**: Red (`bg-red-100 text-red-800`)

### Report Status Colors
- **Draft**: Gray (`bg-gray-100 text-gray-800`)
- **Pending Review**: Blue (`bg-blue-100 text-blue-800`)
- **Approved**: Green (`bg-green-100 text-green-800`)
- **Submitted**: Purple (`bg-purple-100 text-purple-800`)
- **Rejected**: Red (`bg-red-100 text-red-800`)

## Data Flow

### 1. SMA Dashboard
```
Component → useQuery → complianceService.getSMADashboard()
         → API: GET /api/v1/compliance/sma/dashboard
         → Display stats and breakdowns
```

### 2. Calculate SMA
```
User clicks "Calculate SMA" → Dialog opens
User enters date → Clicks "Calculate"
         → useMutation → complianceService.calculateSMA()
         → API: POST /api/v1/compliance/sma/calculate
         → Invalidate queries → Refresh dashboard
```

### 3. Generate Quarterly Return
```
User clicks "Generate" → Dialog opens
User fills form → Clicks "Generate"
         → useMutation → complianceService.generateQuarterlyReturn()
         → API: POST /api/v1/compliance/crilc/quarterly-returns
         → Return created → Refresh list
```

### 4. Resolve Alert
```
User clicks "Resolve" → Dialog opens
User enters notes → Clicks "Resolve"
         → useMutation → complianceService.resolveAlert()
         → API: POST /api/v1/compliance/alerts/{id}/resolve
         → Alert resolved → Refresh alerts
```

## State Management

Using **React Query (TanStack Query)** for:
- Server state management
- Caching
- Automatic refetching
- Optimistic updates
- Loading and error states

Query Keys:
- `['sma-dashboard', asOnDate]`
- `['large-credits', page, smaFilter]`
- `['sma-tracking', page, smaFilter]`
- `['compliance-alerts', page, statusFilter, severityFilter]`
- `['crilc-quarterly-returns', page]`

## Forms and Validation

### Required Fields
- **Identify Large Credits**: threshold_amount, as_on_date
- **Calculate SMA**: as_on_date
- **Generate Return**: reporting_quarter, reporting_year, as_on_date
- **Resolve Alert**: resolution_notes

### Validation Rules
- Dates must be valid ISO format
- Threshold must be positive number
- Quarter format: Q1FY25, Q2FY25, etc.
- Year format: FY2024-25

## Navigation Integration

Added to sidebar (`components/layout/sidebar.tsx`):

```typescript
{
  title: 'Compliance',
  href: '/compliance',
  icon: Shield,
  children: [
    { title: 'SMA Dashboard', href: '/compliance/sma-dashboard' },
    { title: 'Large Credits', href: '/compliance/large-credits' },
    { title: 'SMA Tracking', href: '/compliance/sma-tracking' },
    { title: 'Alerts', href: '/compliance/alerts' },
    { title: 'Quarterly Reports', href: '/compliance/quarterly-reports' },
  ],
}
```

## Responsive Design

All pages are fully responsive:
- Mobile: Single column layout
- Tablet: 2 column grid
- Desktop: 3-4 column grid

Breakpoints:
- `md:` - Medium screens (768px+)
- `lg:` - Large screens (1024px+)

## Loading States

All pages implement:
- Skeleton loading for initial load
- Button loading states (disabled + "Loading..." text)
- Spinner animations for refresh actions
- Empty states with helpful messages

## Error Handling

- Toast notifications for success/error
- Form validation errors
- API error handling with user-friendly messages
- Confirmation dialogs for destructive actions

## Accessibility

- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus states on interactive elements
- Color contrast compliance

## Performance Optimizations

- React Query caching
- Pagination for large lists
- Lazy loading of dialogs
- Debounced search inputs
- Memoized calculations

## Future Enhancements

1. **Export Functionality**
   - Export tables to Excel/CSV
   - Download quarterly reports

2. **Advanced Filters**
   - Date range filters
   - Multi-select filters
   - Saved filter presets

3. **Charts and Visualizations**
   - SMA trend charts
   - Provision requirement graphs
   - Industry-wise breakdown

4. **Real-time Updates**
   - WebSocket notifications
   - Auto-refresh intervals
   - Live alert count

5. **Bulk Actions**
   - Bulk acknowledge alerts
   - Batch SMA calculations
   - Multiple return approvals

## Testing Recommendations

### Unit Tests
- Component rendering
- Button click handlers
- Form validation
- Utility functions

### Integration Tests
- API service calls
- Query/mutation flows
- Navigation routing
- Dialog workflows

### E2E Tests
- Complete SMA calculation flow
- Quarterly return generation
- Alert resolution workflow
- Large credit identification

## Deployment Checklist

- [ ] Environment variables configured
- [ ] API base URL set correctly
- [ ] All dependencies installed
- [ ] Build succeeds without errors
- [ ] Routes accessible
- [ ] Navigation links working
- [ ] API integration tested
- [ ] Loading states working
- [ ] Error handling verified
- [ ] Responsive design checked

## API Integration

Base URL: `/api/v1/compliance`

Ensure backend is running and accessible. All API calls use:
- Token-based authentication
- Tenant isolation
- Error handling middleware
- Request/response logging

## Support

For issues or questions:
- Check backend API documentation
- Review network requests in DevTools
- Check React Query DevTools
- Review browser console for errors

---

**Version**: 1.0.0  
**Last Updated**: January 20, 2024  
**Module**: Compliance & Regulatory Reporting Frontend
