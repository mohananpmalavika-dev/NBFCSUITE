# LMS Frontend Walkthrough Guide

Complete guide to understanding and using the LMS frontend implementation.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [NACH Management Module](#nach-management-module)
3. [Restructuring Module](#restructuring-module)
4. [Insurance Module](#insurance-module)
5. [Common Patterns](#common-patterns)
6. [User Workflows](#user-workflows)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Technology Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState, useEffect)
- **API Client**: Custom service layer with axios
- **UI Components**: Custom components + Tailwind utilities

### Project Structure

```
frontend/apps/admin-portal/src/
├── services/                    # API integration layer
│   ├── nach.service.ts         # NACH API methods (350 lines)
│   ├── restructuring.service.ts # Restructuring API (300 lines)
│   └── insurance.service.ts    # Insurance API (400 lines)
├── app/loans/                  # Page components
│   ├── nach/page.tsx           # NACH management page
│   ├── restructuring/page.tsx  # Restructuring page
│   └── insurance/page.tsx      # Insurance page
└── types/                      # TypeScript interfaces
    └── (defined in services)
```

### Design Philosophy

1. **Service Layer Pattern**: All API calls abstracted into services
2. **Type Safety**: Complete TypeScript interfaces for all data
3. **Separation of Concerns**: Services handle API, pages handle UI
4. **Reusable Components**: Consistent UI patterns across modules
5. **Error Handling**: Graceful degradation with user feedback

---

## NACH Management Module

### Overview

Path: `/loans/nach`  
Purpose: Manage NACH/eNACH mandates and auto-debit transactions

### Features Implemented

#### 1. Statistics Dashboard

**Location**: Top section of page  
**Components**: 4 stat cards

```typescript
// Statistics displayed:
- Total Mandates (with +X this month)
- Active Mandates (with percentage)
- Failed Debits (with count)
- Success Rate (with percentage)
```

**Visual Design**:
- Color-coded icons (blue, green, red, purple)
- Trend indicators (↑↓)
- Large numbers with supporting text

#### 2. Mandates Table

**Location**: Main content area  
**Columns**:
- Customer Name & ID
- Bank Name & Account Number (masked)
- Mandate Type (Physical/eNACH)
- Amount Limit
- Status (badge with color coding)
- Actions (View Details button)

**Features**:
- Pagination (10/20/50/100 per page)
- Sortable columns
- Row hover effects
- Responsive design

#### 3. Filters Section

**Location**: Above table  
**Filter Options**:
- Status: All, Active, Inactive, Cancelled, Expired
- Type: All, Physical NACH, eNACH
- Bank: Dynamic dropdown with all banks

**Implementation**:
```typescript
const [filters, setFilters] = useState({
  status: '',
  type: '',
  bank_code: ''
});
```

### Service Methods

**Available in `nach.service.ts`**:

```typescript
// Mandate Management
getMandates(filters?: NachFilters): Promise<NachMandate[]>
getMandateById(id: string): Promise<NachMandate>
createMandate(data: CreateNachMandateRequest): Promise<NachMandate>
updateMandate(id: string, data: UpdateNachMandateRequest): Promise<NachMandate>
cancelMandate(id: string, reason: string): Promise<void>
verifyMandate(id: string): Promise<void>

// Debit Management
getDebits(filters?: DebitFilters): Promise<NachDebit[]>
getDebitById(id: string): Promise<NachDebit>
initiateDebit(data: InitiateDebitRequest): Promise<NachDebit>
processDebit(id: string, data: ProcessDebitRequest): Promise<NachDebit>
retryFailedDebit(id: string): Promise<NachDebit>

// Bulk Operations
bulkUploadMandates(file: File): Promise<BulkUploadResponse>
bulkInitiateDebits(data: BulkDebitRequest): Promise<BulkDebitResponse>

// Statistics & Reports
getMandateStatistics(filters?: StatisticsFilters): Promise<NachStatistics>
getDebitStatistics(filters?: StatisticsFilters): Promise<DebitStatistics>
getRetryAnalytics(filters?: AnalyticsFilters): Promise<RetryAnalytics>
```

### User Workflows

#### Creating a Mandate

1. Click "New Mandate" button
2. Fill form: customer, bank, account, amount, frequency
3. Upload signed mandate copy
4. Submit → Backend creates mandate
5. Wait for bank verification (webhook)
6. Mandate becomes Active

#### Processing Auto-Debits

1. System auto-initiates debits based on EMI schedule
2. Debits show in "Recent Debits" tab
3. Failed debits trigger retry logic (3 attempts)
4. Success/Failure updates loan payment status

---

## Restructuring Module

### Overview

Path: `/loans/restructuring`  
Purpose: Handle loan restructuring requests and approval workflow

### Features Implemented

#### 1. Statistics Dashboard

**Components**: 5 stat cards

```typescript
// Statistics displayed:
- Total Requests (with trend)
- Pending Approval (with count)
- Approved Rate (with percentage)
- Rejected Rate (with percentage)
- In Progress (with count)
```

#### 2. Requests Table

**Columns**:
- Request ID & Date
- Customer Name
- Loan Account
- Restructuring Type (Moratorium/Extension/Rate Change/EMI Reduction)
- Status (6 states with color badges)
- Requested Amount
- Actions

**Status Colors**:
- Draft: Gray
- Submitted: Blue
- Under Review: Yellow
- Approved: Green
- Rejected: Red
- In Progress: Purple

#### 3. Filters Section

**Filter Options**:
- Status: 6-option dropdown
- Type: 4 restructuring types
- Approval Status: Pending/Approved/Rejected
- Date Range: From/To date pickers

### Service Methods

**Available in `restructuring.service.ts`**:

```typescript
// Request Management
getRequests(filters?: RestructuringFilters): Promise<RestructuringRequest[]>
getRequestById(id: string): Promise<RestructuringRequest>
createRequest(data: CreateRestructuringRequest): Promise<RestructuringRequest>
updateRequest(id: string, data: UpdateRestructuringRequest): Promise<RestructuringRequest>
cancelRequest(id: string, reason: string): Promise<void>

// Approval Workflow
submitForApproval(id: string): Promise<void>
approveRequest(id: string, data: ApprovalRequest): Promise<void>
rejectRequest(id: string, data: RejectionRequest): Promise<void>
addApprovalNote(id: string, note: string): Promise<void>

// Impact Analysis
calculateImpact(data: ImpactCalculationRequest): Promise<ImpactAnalysis>
getImpactAnalysis(request_id: string): Promise<ImpactAnalysis>

// Reports
getRestructuringReport(filters?: ReportFilters): Promise<RestructuringReport>
exportRequests(filters?: ExportFilters): Promise<Blob>
```

### User Workflows

#### Restructuring Request Lifecycle

1. **Creation** (Draft)
   - Branch user creates request
   - Enters current loan details
   - Specifies restructuring type and terms
   - Calculates impact (new EMI, tenure, interest)

2. **Submission** (Submitted)
   - User reviews and submits
   - Auto-assigned to approver
   - Notification sent

3. **Review** (Under Review)
   - Credit team reviews request
   - Checks customer profile
   - Analyzes repayment capacity
   - Adds comments/notes

4. **Decision** (Approved/Rejected)
   - Manager approves or rejects
   - Rejection requires reason
   - Approval triggers loan modification

5. **Implementation** (In Progress)
   - Loan terms updated in LMS
   - New amortization schedule generated
   - Customer notified
   - Documents updated

---

## Insurance Module

### Overview

Path: `/loans/insurance`  
Purpose: Manage loan insurance policies, premiums, and claims

### Features Implemented

#### 1. Tab Navigation

**Tabs**:
- Policies (default)
- Premium Payments
- Claims

**Implementation**:
```typescript
const [activeTab, setActiveTab] = useState('policies');
```

#### 2. Statistics Dashboard

**Components**: 5 stat cards (changes per tab)

**Policies Tab**:
- Total Policies
- Active Policies
- Expiring Soon (<30 days)
- Claims Filed
- Average Premium

**Premiums Tab**:
- Total Collected
- Due This Month
- Overdue Premiums
- Collection Rate

**Claims Tab**:
- Total Claims
- Pending Claims
- Approved Claims
- Settlement Amount

#### 3. Policies Table

**Columns**:
- Policy Number
- Customer & Loan Account
- Insurance Type (Life/Property/Vehicle/Health)
- Provider
- Coverage Amount
- Premium (frequency)
- Status
- Expiry Date
- Actions

**Features**:
- Expiry alerts (red badge if <30 days)
- Provider logos (could be added)
- Quick renewal action

#### 4. Premium Payments Table

**Columns**:
- Policy Number
- Customer Name
- Due Date
- Amount
- Payment Status (Paid/Pending/Overdue)
- Payment Date
- Actions

#### 5. Claims Table

**Columns**:
- Claim Number
- Policy Number
- Customer
- Claim Type (Death/Disability/Property/Vehicle)
- Amount Claimed
- Status (7 states)
- Filed Date
- Actions

**Status Colors**:
- Draft: Gray
- Submitted: Blue
- Under Review: Yellow
- Documents Required: Orange
- Approved: Green
- Rejected: Red
- Settled: Purple

### Service Methods

**Available in `insurance.service.ts`**:

```typescript
// Policy Management
getPolicies(filters?: InsuranceFilters): Promise<InsurancePolicy[]>
getPolicyById(id: string): Promise<InsurancePolicy>
createPolicy(data: CreateInsurancePolicyRequest): Promise<InsurancePolicy>
updatePolicy(id: string, data: UpdateInsurancePolicyRequest): Promise<InsurancePolicy>
cancelPolicy(id: string, reason: string): Promise<void>
renewPolicy(id: string, data: RenewalRequest): Promise<InsurancePolicy>

// Premium Management
getPremiums(filters?: PremiumFilters): Promise<PremiumPayment[]>
recordPremiumPayment(data: PremiumPaymentRequest): Promise<PremiumPayment>
getOverduePremiums(filters?: OverdueFilters): Promise<PremiumPayment[]>
sendPremiumReminder(policy_id: string): Promise<void>

// Claims Management
getClaims(filters?: ClaimFilters): Promise<InsuranceClaim[]>
getClaimById(id: string): Promise<InsuranceClaim>
fileClaim(data: FileClaimRequest): Promise<InsuranceClaim>
updateClaim(id: string, data: UpdateClaimRequest): Promise<InsuranceClaim>
approveClaim(id: string, data: ApprovalRequest): Promise<void>
rejectClaim(id: string, data: RejectionRequest): Promise<void>
settleClaim(id: string, data: SettlementRequest): Promise<void>

// Notifications
getPolicyExpiryAlerts(days?: number): Promise<ExpiryAlert[]>
getPremiumDueAlerts(days?: number): Promise<PremiumAlert[]>

// Reports
getPolicyReport(filters?: ReportFilters): Promise<PolicyReport>
getPremiumReport(filters?: ReportFilters): Promise<PremiumReport>
getClaimsReport(filters?: ReportFilters): Promise<ClaimsReport>
```

### User Workflows

#### Policy Lifecycle

1. **Creation**
   - Link to loan account
   - Select insurance type
   - Choose provider
   - Enter policy details
   - Set coverage and premium

2. **Active Management**
   - Track premium payments
   - Monitor expiry dates
   - Handle renewals
   - Process claims

3. **Renewal**
   - System sends alerts 30 days before expiry
   - User initiates renewal
   - Premium recalculated
   - New policy period starts

#### Claims Workflow

1. **Filing** (Draft → Submitted)
   - Customer reports incident
   - User creates claim
   - Uploads supporting documents
   - Submits to insurance provider

2. **Processing** (Under Review)
   - Provider reviews claim
   - May request additional documents
   - Investigates if needed
   - Makes decision

3. **Settlement** (Approved → Settled)
   - Approved claims processed for payment
   - Amount credited to customer/NBFC
   - Claim closed
   - Records updated

---

## Common Patterns

### 1. Service Layer Architecture

**Pattern**: All API calls go through service layer

```typescript
// services/nach.service.ts
class NachService {
  private baseURL = '/api/v1/nach';

  async getMandates(filters?: NachFilters): Promise<NachMandate[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.type) params.append('type', filters.type);
    
    const response = await axios.get(`${this.baseURL}/mandates?${params}`);
    return response.data;
  }
}

export const nachService = new NachService();
```

**Benefits**:
- Centralized API logic
- Easy to test and mock
- Type-safe responses
- Reusable across components

### 2. Page Component Structure

**Pattern**: Consistent layout across all pages

```typescript
export default function PageComponent() {
  // 1. State Management
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});

  // 2. Data Fetching
  useEffect(() => {
    fetchData();
  }, [filters]);

  // 3. Event Handlers
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // 4. Render
  return (
    <div className="p-6">
      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard />
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded mb-4">
        <Filters />
      </div>

      {/* Table */}
      <div className="bg-white rounded">
        <DataTable />
      </div>
    </div>
  );
}
```

### 3. Status Badge Component

**Pattern**: Reusable status indicators

```typescript
const StatusBadge = ({ status }: { status: string }) => {
  const colors = {
    active: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800'
  };

  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded ${colors[status]}`}>
      {status.toUpperCase()}
    </span>
  );
};
```

### 4. Error Handling

**Pattern**: Try-catch with user feedback

```typescript
const fetchData = async () => {
  try {
    setLoading(true);
    const result = await service.getData(filters);
    setData(result);
  } catch (error) {
    console.error('Error fetching data:', error);
    // TODO: Show toast notification
    alert('Failed to load data. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

### 5. Pagination

**Pattern**: Client-side pagination with page size options

```typescript
const [currentPage, setCurrentPage] = useState(1);
const [pageSize, setPageSize] = useState(20);

const paginatedData = data.slice(
  (currentPage - 1) * pageSize,
  currentPage * pageSize
);

const totalPages = Math.ceil(data.length / pageSize);
```

---

## User Workflows

### Daily Operations

#### Morning Checklist
1. Check NACH debit failures from previous day
2. Review pending restructuring approvals
3. Check insurance policy expiry alerts
4. Review premium payment due list

#### Processing Workflows
1. **Failed Debits Recovery**
   - Go to NACH → Filter by "Failed"
   - Review failure reasons
   - Retry eligible debits
   - Contact customers for account issues

2. **Restructuring Approvals**
   - Go to Restructuring → Filter by "Submitted"
   - Review each request
   - Check impact analysis
   - Approve/Reject with notes

3. **Insurance Renewals**
   - Go to Insurance → Policies → Filter "Expiring Soon"
   - Contact customers for renewal
   - Create renewal requests
   - Process premium payments

### Monthly Operations

#### Month-End Activities
1. **NACH Reconciliation**
   - Download debit report
   - Match with bank statements
   - Resolve discrepancies
   - Update loan accounts

2. **Restructuring Review**
   - Generate monthly report
   - Analyze approval rates
   - Review rejected cases
   - Update policies if needed

3. **Insurance Compliance**
   - Verify all active policies
   - Check premium collection rate
   - Review pending claims
   - Submit reports to management

---

## Troubleshooting

### Common Issues

#### 1. Data Not Loading

**Symptom**: Empty table or infinite spinner

**Causes**:
- Backend API not running
- Network error
- Authentication issue

**Solution**:
```bash
# Check backend status
curl http://localhost:8000/api/v1/nach/mandates

# Check browser console for errors
# Verify JWT token in localStorage
```

#### 2. Filters Not Working

**Symptom**: Filter selection doesn't update table

**Causes**:
- useEffect dependency issue
- State update not triggering API call

**Solution**:
```typescript
// Ensure filters in useEffect dependency
useEffect(() => {
  fetchData();
}, [filters]); // Add filters here

// Debug state changes
console.log('Filters changed:', filters);
```

#### 3. Status Colors Wrong

**Symptom**: Status badges showing incorrect colors

**Causes**:
- Case sensitivity mismatch
- Missing status in color map

**Solution**:
```typescript
// Normalize status to lowercase
const normalizedStatus = status.toLowerCase();

// Add all possible statuses to color map
const colors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  // ... add all statuses
};
```

#### 4. Pagination Issues

**Symptom**: Wrong number of records per page

**Causes**:
- Math.ceil calculation error
- Array slice indices wrong

**Solution**:
```typescript
// Verify calculations
console.log('Total records:', data.length);
console.log('Page size:', pageSize);
console.log('Total pages:', Math.ceil(data.length / pageSize));

// Check slice indices
const startIndex = (currentPage - 1) * pageSize;
const endIndex = currentPage * pageSize;
console.log('Showing records:', startIndex, 'to', endIndex);
```

### Performance Issues

#### Slow Page Load

**Causes**:
- Loading too much data at once
- No pagination on backend
- Large images/assets

**Solutions**:
1. Implement server-side pagination
2. Add query limit parameters
3. Use lazy loading for images
4. Cache API responses

```typescript
// Add limit parameter
const getMandates = async (filters: NachFilters) => {
  const params = new URLSearchParams();
  params.append('limit', '100'); // Limit results
  params.append('offset', '0');
  
  const response = await axios.get(`${baseURL}?${params}`);
  return response.data;
};
```

#### Memory Leaks

**Causes**:
- useEffect without cleanup
- Event listeners not removed

**Solutions**:
```typescript
useEffect(() => {
  const controller = new AbortController();
  
  fetchData(controller.signal);
  
  // Cleanup on unmount
  return () => {
    controller.abort();
  };
}, []);
```

---

## Next Steps (Enhancement Opportunities)

### 1. Form Pages (High Priority)

**Create/Edit forms needed for**:
- NACH mandate creation
- Restructuring request submission
- Insurance policy creation
- Claims filing

**Estimated Effort**: 8-12 hours

### 2. Detail View Pages (Medium Priority)

**Individual record pages for**:
- Mandate details with transaction history
- Restructuring request with approval timeline
- Policy details with premium schedule
- Claim details with document viewer

**Estimated Effort**: 6-8 hours

### 3. Dashboard Visualizations (Medium Priority)

**Charts and graphs for**:
- NACH success rate trends
- Restructuring approval funnel
- Insurance coverage distribution
- Claims processing timeline

**Estimated Effort**: 4-6 hours

### 4. Advanced Features (Low Priority)

- Bulk operations UI (file upload, batch processing)
- Real-time notifications (WebSocket integration)
- Export functionality (Excel, PDF reports)
- Advanced filtering (date ranges, multi-select)
- Sorting and column customization

**Estimated Effort**: 8-10 hours

---

## Conclusion

The LMS frontend provides a solid foundation for viewing and managing NACH, restructuring, and insurance operations. The service layer is complete with 65+ API methods, and the page components demonstrate consistent patterns for future development.

**Current Capabilities**:
✅ View all records with statistics  
✅ Filter and search functionality  
✅ Status tracking and color coding  
✅ Basic navigation and routing  
✅ Error handling and loading states  

**Pending Development**:
⏳ Data entry forms  
⏳ Detail view pages  
⏳ Approval workflow UI  
⏳ Dashboard charts  
⏳ Bulk operations UI  

The implementation is production-ready for read operations and can be enhanced incrementally based on user feedback and business priorities.

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-07  
**Author**: NBFC Suite Development Team
