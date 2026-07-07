# Frontend Implementation Guide - Accounting Features

## Overview

This document provides a complete guide to implementing the frontend for TDS, GST, and Asset Management features.

---

## ✅ What's Been Implemented

### 1. API Services (100% Complete)
**File**: `frontend/apps/admin-portal/src/services/accounting.service.ts`

**Added Services:**
- `tdsService` - Complete TDS API integration
  - Sections, deductions, challans, certificates, returns
  - Calculate TDS, record deductions, generate certificates
  
- `gstService` - Complete GST API integration
  - Configuration, HSN/SAC, transactions, ITC
  - Calculate GST, prepare GSTR-1/3B returns
  
- `assetService` - Complete Asset Management API integration
  - CRUD operations, depreciation, transfers, disposal
  - Maintenance tracking, reporting

### 2. Frontend Components Created

#### TDS Dashboard
**File**: `frontend/apps/admin-portal/src/app/accounting/tds/page.tsx`

**Features:**
- Summary statistics (deductions, amounts, pending payments)
- Section-wise summary chart
- Payment status tracking
- Quick action buttons
- Tabbed navigation (Overview, Deductions, Challans, Certificates, Returns)

---

## 📋 Components to Create

### TDS Module Components

#### 1. TDS Sections Configuration
**File**: `frontend/apps/admin-portal/src/app/accounting/tds/sections/page.tsx`

```tsx
'use client'

import { useState, useEffect } from 'react'
import { tdsService, TDSSection } from '@/services/accounting.service'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import {Dialog,DialogContent,DialogHeader,DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function TDSSectionsPage() {
  const [sections, setSections] = useState<TDSSection[]>([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [financialYear] = useState(new Date().getFullYear())
  
  const columns = [
    { header: 'Section Code', accessorKey: 'section_code' },
    { header: 'Section Name', accessorKey: 'section_name' },
    { header: 'Rate (%)', accessorKey: 'tds_rate' },
    { header: 'Threshold', accessorKey: 'threshold_limit' },
    { header: 'Rate w/o PAN', accessorKey: 'rate_without_pan' },
    { header: 'Status', accessorKey: 'is_active' },
  ]

  useEffect(() => {
    loadSections()
  }, [])

  const loadSections = async () => {
    const response = await tdsService.getSections(financialYear)
    setSections(response.data.sections)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h1 className="text-2xl font-bold">TDS Sections</h1>
        <Button onClick={() => setIsDialogOpen(true)}>Add Section</Button>
      </div>
      
      <DataTable columns={columns} data={sections} />
      
      {/* Add Section Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add TDS Section</DialogTitle>
          </DialogHeader>
          {/* Form fields for section configuration */}
        </DialogContent>
      </Dialog>
    </div>
  )
}
```

#### 2. TDS Deductions List & Form
**Files**: 
- `frontend/apps/admin-portal/src/app/accounting/tds/deductions/page.tsx`
- `frontend/apps/admin-portal/src/app/accounting/tds/deductions/new/page.tsx`

**Features:**
- List all deductions with filters (FY, quarter, section, status)
- Pagination
- Create new deduction form with:
  - Section selection
  - Deductee details (name, PAN)
  - Transaction details
  - Auto-calculate TDS
  - Validation

#### 3. TDS Challans
**File**: `frontend/apps/admin-portal/src/app/accounting/tds/challans/page.tsx`

**Features:**
- List all challans
- Create challan form with:
  - Select pending deductions
  - Bank details (BSR code, bank name)
  - Payment mode
  - Generate challan number

#### 4. TDS Certificates
**File**: `frontend/apps/admin-portal/src/app/accounting/tds/certificates/page.tsx`

**Features:**
- List certificates
- Generate Form 16A
- Download PDF
- Bulk certificate generation

#### 5. TDS Returns
**File**: `frontend/apps/admin-portal/src/app/accounting/tds/returns/page.tsx`

**Features:**
- Prepare Form 26Q
- Review deductions summary
- Export return file
- File status tracking

---

### GST Module Components

#### 1. GST Dashboard
**File**: `frontend/apps/admin-portal/src/app/accounting/gst/page.tsx`

```tsx
'use client'

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { gstService } from '@/services/accounting.service'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function GSTPage() {
  const [summary, setSummary] = useState<any>(null)
  const [financialYear] = useState(new Date().getFullYear())
  
  useEffect(() => {
    loadSummary()
  }, [])
  
  const loadSummary = async () => {
    const response = await gstService.getSummary(financialYear)
    setSummary(response.data)
  }
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">GST Management</h1>
      
      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Outward Supplies</CardTitle>
            <CardDescription>Sales & Services</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary?.outward_supplies?.taxable_amount?.toLocaleString('en-IN') || 0}
            </div>
            <p className="text-sm text-muted-foreground">
              GST: ₹{summary?.outward_supplies?.total_gst?.toLocaleString('en-IN') || 0}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Inward Supplies</CardTitle>
            <CardDescription>Purchases</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{summary?.inward_supplies?.taxable_amount?.toLocaleString('en-IN') || 0}
            </div>
            <p className="text-sm text-muted-foreground">
              ITC: ₹{summary?.inward_supplies?.total_itc?.toLocaleString('en-IN') || 0}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Net Liability</CardTitle>
            <CardDescription>To be paid</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ₹{summary?.net_liability?.toLocaleString('en-IN') || 0}
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Tabs for different sections */}
      <Tabs defaultValue="transactions">
        <TabsList>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="itc">Input Credit</TabsTrigger>
          <TabsTrigger value="returns">Returns</TabsTrigger>
        </TabsList>
        
        <TabsContent value="transactions">{/* Transaction list */}</TabsContent>
        <TabsContent value="itc">{/* ITC list */}</TabsContent>
        <TabsContent value="returns">{/* Returns */}</TabsContent>
      </Tabs>
    </div>
  )
}
```

#### 2. GST Configuration
**File**: `frontend/apps/admin-portal/src/app/accounting/gst/configuration/page.tsx`

**Features:**
- Setup GSTIN details
- Multiple GSTIN support
- State registration
- Contact information

#### 3. HSN/SAC Master
**File**: `frontend/apps/admin-portal/src/app/accounting/gst/hsn-sac/page.tsx`

**Features:**
- List HSN/SAC codes
- Add/edit codes with rates
- Search and filter

#### 4. GST Transactions
**File**: `frontend/apps/admin-portal/src/app/accounting/gst/transactions/page.tsx`

**Features:**
- Record GST transactions
- Automatic tax calculation
- Inter-state vs intra-state
- Party GSTIN validation

#### 5. GST Returns (GSTR-1, GSTR-3B)
**Files**: 
- `frontend/apps/admin-portal/src/app/accounting/gst/returns/gstr1/page.tsx`
- `frontend/apps/admin-portal/src/app/accounting/gst/returns/gstr3b/page.tsx`

**Features:**
- Month selection
- Auto-populate data
- Summary tables
- Export functionality

---

### Asset Management Components

#### 1. Asset Dashboard
**File**: `frontend/apps/admin-portal/src/app/accounting/assets/page.tsx`

```tsx
'use client'

import { useState, useEffect } from 'react'
import { assetService, FixedAsset } from '@/services/accounting.service'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function AssetsPage() {
  const [assets, setAssets] = useState<FixedAsset[]>([])
  const [stats, setStats] = useState({
    total_assets: 0,
    total_cost: 0,
    total_depreciation: 0,
    total_wdv: 0
  })
  
  useEffect(() => {
    loadAssets()
  }, [])
  
  const loadAssets = async () => {
    const response = await assetService.getAssets({ page: 1, page_size: 100 })
    setAssets(response.data.assets)
    
    // Calculate stats
    const totalCost = response.data.assets.reduce((sum, a) => sum + a.purchase_cost, 0)
    const totalDep = response.data.assets.reduce((sum, a) => sum + a.accumulated_depreciation, 0)
    const totalWDV = response.data.assets.reduce((sum, a) => sum + a.written_down_value, 0)
    
    setStats({
      total_assets: response.data.total,
      total_cost: totalCost,
      total_depreciation: totalDep,
      total_wdv: totalWDV
    })
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h1 className="text-3xl font-bold">Asset Management</h1>
        <Button asChild>
          <Link href="/accounting/assets/new">Add Asset</Link>
        </Button>
      </div>
      
      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total_assets}</div>
            <p className="text-sm text-muted-foreground">Total Assets</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">₹{stats.total_cost.toLocaleString('en-IN')}</div>
            <p className="text-sm text-muted-foreground">Total Cost</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">₹{stats.total_depreciation.toLocaleString('en-IN')}</div>
            <p className="text-sm text-muted-foreground">Accumulated Depreciation</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">₹{stats.total_wdv.toLocaleString('en-IN')}</div>
            <p className="text-sm text-muted-foreground">Written Down Value</p>
          </CardContent>
        </Card>
      </div>
      
      {/* Asset List Table */}
      <Card>
        <CardHeader>
          <CardTitle>Fixed Assets</CardTitle>
        </CardHeader>
        <CardContent>
          {/* DataTable component with assets */}
        </CardContent>
      </Card>
    </div>
  )
}
```

#### 2. Asset Form (Create/Edit)
**File**: `frontend/apps/admin-portal/src/app/accounting/assets/new/page.tsx`

**Features:**
- Asset details form
- Category selection
- Depreciation method and rate
- Location and department
- File upload for invoice

#### 3. Asset Details & Actions
**File**: `frontend/apps/admin-portal/src/app/accounting/assets/[id]/page.tsx`

**Features:**
- View asset details
- Depreciation schedule
- Transfer asset
- Record maintenance
- Dispose asset

#### 4. Depreciation Management
**File**: `frontend/apps/admin-portal/src/app/accounting/assets/depreciation/page.tsx`

**Features:**
- Monthly depreciation posting
- Bulk depreciation run
- Depreciation schedule view
- Post to GL integration

---

## 🔧 Shared Components to Create

### 1. Data Table Component
**File**: `frontend/apps/admin-portal/src/components/ui/data-table.tsx`

Generic table component with:
- Sorting
- Filtering
- Pagination
- Export to Excel/PDF

### 2. Form Components
**Files in**: `frontend/apps/admin-portal/src/components/forms/`

- `TDSDeductionForm.tsx`
- `GSTTransactionForm.tsx`
- `AssetForm.tsx`
- `ChallanForm.tsx`

### 3. Charts & Visualizations
**Files in**: `frontend/apps/admin-portal/src/components/charts/`

- `TDSSummaryChart.tsx` - Section-wise bar chart
- `GSTTrendChart.tsx` - Monthly trend line
- `AssetDistributionChart.tsx` - Category pie chart

### 4. PDF Export Components
**Files in**: `frontend/apps/admin-portal/src/lib/pdf/`

- `tds-certificate-pdf.ts` - Generate Form 16A
- `gst-invoice-pdf.ts` - Generate GST invoice
- `asset-register-pdf.ts` - Asset register report

---

## 🔗 Navigation Menu Updates

**File**: `frontend/apps/admin-portal/src/components/layout/sidebar.tsx`

Add to accounting section:

```tsx
{
  title: 'Accounting',
  items: [
    { title: 'Dashboard', href: '/accounting', icon: LayoutDashboard },
    { title: 'Chart of Accounts', href: '/accounting/chart-of-accounts' },
    { title: 'Journal Entries', href: '/accounting/journal-entries' },
    {
      title: 'TDS',
      icon: Receipt,
      sub: [
        { title: 'Dashboard', href: '/accounting/tds' },
        { title: 'Deductions', href: '/accounting/tds/deductions' },
        { title: 'Challans', href: '/accounting/tds/challans' },
        { title: 'Certificates', href: '/accounting/tds/certificates' },
        { title: 'Returns', href: '/accounting/tds/returns' },
      ]
    },
    {
      title: 'GST',
      icon: FileText,
      sub: [
        { title: 'Dashboard', href: '/accounting/gst' },
        { title: 'Transactions', href: '/accounting/gst/transactions' },
        { title: 'Input Credit', href: '/accounting/gst/itc' },
        { title: 'Returns', href: '/accounting/gst/returns' },
      ]
    },
    {
      title: 'Assets',
      icon: Package,
      sub: [
        { title: 'Dashboard', href: '/accounting/assets' },
        { title: 'Asset Register', href: '/accounting/assets/register' },
        { title: 'Depreciation', href: '/accounting/assets/depreciation' },
        { title: 'Maintenance', href: '/accounting/assets/maintenance' },
      ]
    },
    { title: 'Reports', href: '/accounting/reports' },
  ]
}
```

---

## 📊 State Management

**File**: `frontend/apps/admin-portal/src/contexts/AccountingContext.tsx`

```tsx
'use client'

import { createContext, useContext, useState } from 'react'

interface AccountingContextType {
  financialYear: number
  setFinancialYear: (year: number) => void
  tdsFilters: any
  setTDSFilters: (filters: any) => void
  gstFilters: any
  setGSTFilters: (filters: any) => void
}

const AccountingContext = createContext<AccountingContextType | undefined>(undefined)

export function AccountingProvider({ children }: { children: React.ReactNode }) {
  const [financialYear, setFinancialYear] = useState(new Date().getFullYear())
  const [tdsFilters, setTDSFilters] = useState({})
  const [gstFilters, setGSTFilters] = useState({})
  
  return (
    <AccountingContext.Provider value={{
      financialYear,
      setFinancialYear,
      tdsFilters,
      setTDSFilters,
      gstFilters,
      setGSTFilters,
    }}>
      {children}
    </AccountingContext.Provider>
  )
}

export const useAccounting = () => {
  const context = useContext(AccountingContext)
  if (!context) throw new Error('useAccounting must be used within AccountingProvider')
  return context
}
```

---

## ✅ Implementation Checklist

### Phase 1: Core Setup (1-2 days)
- [x] API services created
- [x] TDS dashboard created
- [ ] Update navigation menu
- [ ] Add routing configuration
- [ ] Setup state management

### Phase 2: TDS Module (3-4 days)
- [x] Dashboard
- [ ] Sections configuration page
- [ ] Deductions list & form
- [ ] Challans list & form
- [ ] Certificates generation
- [ ] Returns preparation

### Phase 3: GST Module (3-4 days)
- [ ] Dashboard
- [ ] Configuration page
- [ ] HSN/SAC master
- [ ] Transactions list & form
- [ ] ITC tracking
- [ ] GSTR-1 & GSTR-3B returns

### Phase 4: Asset Management (3-4 days)
- [ ] Dashboard
- [ ] Asset list & form
- [ ] Depreciation posting
- [ ] Transfer management
- [ ] Disposal tracking
- [ ] Maintenance records

### Phase 5: Shared Components (2-3 days)
- [ ] Data table component
- [ ] Form components
- [ ] Charts
- [ ] PDF generators
- [ ] Export utilities

### Phase 6: Testing & Polish (2-3 days)
- [ ] API integration testing
- [ ] Form validation
- [ ] Error handling
- [ ] Loading states
- [ ] Responsive design
- [ ] Accessibility

---

## 🚀 Deployment Steps

1. **Install Dependencies**
```bash
cd frontend/apps/admin-portal
npm install
```

2. **Configure Environment**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. **Run Development Server**
```bash
npm run dev
```

4. **Build for Production**
```bash
npm run build
npm run start
```

---

## 📝 Notes

- All components use TypeScript for type safety
- Forms use React Hook Form with Zod validation
- Tables use TanStack Table (React Table)
- Charts use Recharts library
- PDF generation uses jsPDF
- State management uses React Context API
- API calls use Axios with interceptors for auth

---

**Status**: API Services Complete, Dashboards In Progress
**Next**: Complete TDS, GST, and Asset module pages
**Timeline**: 2-3 weeks for full frontend implementation
