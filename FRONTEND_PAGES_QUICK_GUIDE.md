# Frontend Pages Quick Implementation Guide

## 📄 Remaining Pages to Build (6 pages)

All pages follow the same patterns established in:
- `/risk/page.tsx` (Dashboard)
- `/risk/policies/page.tsx` (List view)

---

## 1. Credit Policy Form (`/risk/policies/new/page.tsx`)

**Purpose**: Create new credit policy

**Key Components**:
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { riskService } from '@/services/risk.service'

// Form with sections:
- Basic Info (code, name, version)
- Applicability (products, segments)
- Credit Criteria (CIBIL, DTI, income)
- Loan Limits (amount, tenure)
- Age & Employment
- Geographic Restrictions
- Negative Profiles
- Documentation
```

**Pattern**: Copy from `/loans/applications/new/page.tsx`

---

## 2. Pricing Rules Page (`/risk/pricing/page.tsx`)

**Purpose**: Manage risk-based pricing rules

**Features**:
- Table with rules (code, name, priority, rate)
- Filters: policy, status, priority
- Actions: Create, Edit, Delete, Test
- Pricing calculator sidebar

**Data Fetching**:
```typescript
const { data } = useQuery({
  queryKey: ['pricing-rules', page, policyId],
  queryFn: () => riskService.getPricingRules({ page, policy_id: policyId })
})
```

**Pattern**: Copy table structure from `/risk/policies/page.tsx`

---

## 3. Exposure Limits Page (`/risk/exposure/page.tsx`)

**Purpose**: Monitor concentration risk

**Features**:
- Table with utilization progress bars
- Filters: limit type, status (breached/warning)
- Color-coded alerts (green/yellow/red)
- Charts: Utilization by type
- Actions: Utilize, Release, Adjust

**Visual Elements**:
```typescript
// Progress bar component
<div className="w-full bg-gray-200 rounded-full h-2">
  <div 
    className={`h-2 rounded-full ${getUtilizationColor(percentage)}`}
    style={{ width: `${percentage}%` }}
  />
</div>

function getUtilizationColor(pct: number) {
  if (pct >= 90) return 'bg-red-500'
  if (pct >= 75) return 'bg-yellow-500'
  return 'bg-green-500'
}
```

**Pattern**: Table + charts from `/treasury/cash-position/page.tsx`

---

## 4. Risk Ratings Dashboard (`/risk/ratings/page.tsx`)

**Purpose**: Portfolio risk analysis

**Layout**:
```
┌─────────────────────────────────────┐
│  Stats Cards (Total, High Risk)    │
├──────────────┬──────────────────────┤
│              │                      │
│  Rating      │  Recent Ratings     │
│  Distribution│  Table with         │
│  Chart       │  Filters            │
│  (Donut)     │                      │
│              │                      │
└──────────────┴──────────────────────┘
```

**Charts**:
```typescript
import { Doughnut, Bar } from 'react-chartjs-2'

// Rating distribution
<Doughnut 
  data={{
    labels: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D'],
    datasets: [{
      data: Object.values(stats.rating_distribution),
      backgroundColor: [
        '#10b981', '#22c55e', '#3b82f6', '#6366f1',
        '#eab308', '#f97316', '#ef4444'
      ]
    }]
  }}
/>
```

**Pattern**: Dashboard with charts from `/risk/page.tsx` + table

---

## 5. Early Warning Alerts Page (`/risk/alerts/page.tsx`)

**Purpose**: Monitor and manage alerts

**Features**:
- Alerts table with severity badges
- Filters: status, severity, category
- Alert actions modal
- Statistics cards
- Alert history timeline

**Table Columns**:
```typescript
- Alert Number (link to detail)
- Customer Name
- Account Number
- Signal Name
- Severity (badge with color)
- Detected Value vs Threshold
- Status (badge)
- Alert Date
- Actions (dropdown)
```

**Action Modal**:
```typescript
function AlertActionModal({ alert, onClose, onSubmit }) {
  const actions = [
    'acknowledge',
    'assign',
    'resolve',
    'escalate',
    'mark_false_positive'
  ]
  
  return (
    <Dialog>
      <Select name="action" options={actions} />
      <Textarea name="remarks" />
      <Button onClick={handleSubmit}>Submit</Button>
    </Dialog>
  )
}
```

**Pattern**: Table from `/compliance/alerts/page.tsx`

---

## 6. Policy Details Page (`/risk/policies/[id]/page.tsx`)

**Purpose**: View policy details

**Sections**:
```typescript
- Header (code, name, status badge)
- Basic Information
- Eligibility Criteria
- Loan Parameters
- Employment & Age Rules
- Geographic Restrictions
- Negative Profiles
- Documentation Requirements
- Approval Matrix
- Pricing Rules (linked)
- Audit Trail
```

**Pattern**: Details view from `/loans/applications/[id]/page.tsx`

---

## Common Patterns

### 1. Data Fetching with React Query

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['resource', id, filters],
  queryFn: () => service.getResource({ ...filters })
})

const mutation = useMutation({
  mutationFn: (data) => service.createResource(data),
  onSuccess: () => {
    toast.success('Created successfully')
    queryClient.invalidateQueries(['resource'])
  },
  onError: (error) => {
    toast.error(error.message)
  }
})
```

### 2. Table with Pagination

```typescript
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Column 1</TableHead>
      {/* ... */}
    </TableRow>
  </TableHeader>
  <TableBody>
    {isLoading ? (
      <SkeletonRows count={5} />
    ) : data?.items.map((item) => (
      <TableRow key={item.id}>
        <TableCell>{item.field}</TableCell>
        {/* ... */}
      </TableRow>
    ))}
  </TableBody>
</Table>

{/* Pagination */}
<div className="flex justify-between items-center p-4">
  <span>Showing {start} to {end} of {total}</span>
  <div className="flex gap-2">
    <Button onClick={() => setPage(p => p - 1)} disabled={!hasPrev}>
      Previous
    </Button>
    <Button onClick={() => setPage(p => p + 1)} disabled={!hasNext}>
      Next
    </Button>
  </div>
</div>
```

### 3. Form with Validation

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  field1: z.string().min(3),
  field2: z.number().positive(),
  // ...
})

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema)
})

const onSubmit = async (data) => {
  try {
    await mutation.mutateAsync(data)
  } catch (error) {
    // Handle error
  }
}

return (
  <form onSubmit={handleSubmit(onSubmit)}>
    <Input {...register('field1')} />
    {errors.field1 && <span>{errors.field1.message}</span>}
    
    <Button type="submit" disabled={mutation.isPending}>
      {mutation.isPending ? 'Saving...' : 'Save'}
    </Button>
  </form>
)
```

### 4. Filters

```typescript
const [filters, setFilters] = useState({
  search: '',
  status: undefined,
  dateFrom: undefined,
  dateTo: undefined
})

// Debounced search
const debouncedSearch = useDebounce(filters.search, 500)

// In query
queryFn: () => service.getItems({
  ...filters,
  search: debouncedSearch
})

// Filter UI
<div className="flex gap-4">
  <Input 
    placeholder="Search..." 
    value={filters.search}
    onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
  />
  <Select 
    value={filters.status}
    onChange={(value) => setFilters(f => ({ ...f, status: value }))}
  >
    <option value="">All</option>
    <option value="active">Active</option>
    <option value="inactive">Inactive</option>
  </Select>
</div>
```

### 5. Stats Cards

```typescript
function StatsCard({ title, value, icon: Icon, color = 'blue' }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
  }
  
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

### 6. Charts with Chart.js

```typescript
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

// Usage
<Line 
  data={{
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Metric',
      data: [65, 59, 80],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
    }]
  }}
  options={{
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Chart Title' }
    }
  }}
/>
```

---

## UI Component Library

All pages use shadcn/ui components:

```typescript
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
```

---

## Utilities

```typescript
// Formatting
import { formatCurrency, formatDate, formatNumber } from '@/lib/utils'

formatCurrency(500000) // "₹5,00,000"
formatDate('2024-01-15') // "15 Jan 2024"
formatNumber(1234567) // "1,234,567"

// Toast notifications
import { toast } from 'sonner'

toast.success('Operation successful')
toast.error('Operation failed')
toast.info('Information message')
toast.warning('Warning message')

// Class merging
import { cn } from '@/lib/utils'

<div className={cn(
  'base-classes',
  condition && 'conditional-class',
  'more-classes'
)} />
```

---

## Time Estimate

Per page (8-12 hours each):
1. Credit Policy Form - 12 hours (complex, many fields)
2. Pricing Rules - 8 hours (table + simple form)
3. Exposure Limits - 10 hours (table + charts + actions)
4. Risk Ratings - 10 hours (dashboard + charts)
5. EWS Alerts - 10 hours (table + action modal)
6. Policy Details - 6 hours (read-only display)

**Total**: ~56 hours (7 working days)

---

## Testing Checklist

For each page:
- [ ] Data loads correctly
- [ ] Pagination works
- [ ] Filters apply correctly
- [ ] Search is debounced
- [ ] Create/Edit forms validate
- [ ] Success/error toasts show
- [ ] Loading states display
- [ ] Empty states show
- [ ] Actions work (CRUD)
- [ ] Mobile responsive
- [ ] Accessibility (keyboard nav, screen readers)

---

## Resources

- **Existing Pages**: Copy patterns from `/loans` and `/customers`
- **Components**: `/components/ui/` (shadcn/ui)
- **Icons**: lucide-react
- **Charts**: react-chartjs-2
- **Forms**: react-hook-form + zod
- **Data**: @tanstack/react-query

---

**Quick Start**: Pick any page, copy the closest existing page, update the API calls to use `riskService`, and customize the fields/columns!
