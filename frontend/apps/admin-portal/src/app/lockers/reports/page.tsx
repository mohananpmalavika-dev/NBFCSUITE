'use client'

import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  FileText, 
  Download, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Package, 
  AlertCircle,
  Clock,
  BarChart3,
  PieChart,
  Activity,
  Calendar
} from 'lucide-react'
import { 
  reportsService,
  ReportType,
  ExportFormat,
  ReportPeriod
} from '@/services/locker.service'
import { format } from 'date-fns'

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedReport, setSelectedReport] = useState<ReportType | null>(null)
  const [exportDialogOpen, setExportDialogOpen] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>(ExportFormat.PDF)
  const [selectedPeriod, setSelectedPeriod] = useState<ReportPeriod>(ReportPeriod.THIS_MONTH)
  
  const queryClient = useQueryClient()

  // Auto-refresh every 60 seconds
  const refreshInterval = 60000

  // Fetch dashboard data
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['locker-reports-dashboard'],
    queryFn: () => reportsService.getDashboard(),
    refetchInterval: refreshInterval,
  })

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: (data: { report_type: ReportType; format: ExportFormat; filters?: any }) =>
      reportsService.exportReport(data),
    onSuccess: (result) => {
      console.log('Export successful:', result)
      setExportDialogOpen(false)
    },
  })

  const handleExport = () => {
    if (selectedReport) {
      exportMutation.mutate({
        report_type: selectedReport,
        format: selectedFormat,
        filters: {}
      })
    }
  }

  const handleGenerateReport = (reportType: ReportType) => {
    setSelectedReport(reportType)
    setActiveTab('report-viewer')
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Locker Reports & Analytics</h1>
          <p className="text-gray-500">Comprehensive reporting and insights</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setExportDialogOpen(true)} variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="report-viewer">Report Viewer</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-4">
          <DashboardTab data={dashboardData} loading={dashboardLoading} />
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-4">
          <ReportsTab onGenerateReport={handleGenerateReport} />
        </TabsContent>

        {/* Report Viewer Tab */}
        <TabsContent value="report-viewer" className="space-y-4">
          <ReportViewerTab 
            reportType={selectedReport} 
            period={selectedPeriod}
            onPeriodChange={setSelectedPeriod}
          />
        </TabsContent>
      </Tabs>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onOpenChange={setExportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Export Report</DialogTitle>
            <DialogDescription>
              Select report type and export format
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Report Type</Label>
              <Select
                value={selectedReport || ''}
                onValueChange={(value) => setSelectedReport(value as ReportType)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(ReportType).map((type) => (
                    <SelectItem key={type} value={type}>
                      {type.replace(/_/g, ' ').toUpperCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Export Format</Label>
              <Select
                value={selectedFormat}
                onValueChange={(value) => setSelectedFormat(value as ExportFormat)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ExportFormat.PDF}>PDF</SelectItem>
                  <SelectItem value={ExportFormat.EXCEL}>Excel</SelectItem>
                  <SelectItem value={ExportFormat.CSV}>CSV</SelectItem>
                  <SelectItem value={ExportFormat.JSON}>JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setExportDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleExport} disabled={!selectedReport}>
              Export
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}


// ============================================
// Dashboard Tab Component
// ============================================

function DashboardTab({ data, loading }: any) {
  if (loading) {
    return <div className="text-center py-8">Loading dashboard...</div>
  }

  if (!data) {
    return <div className="text-center py-8">No data available</div>
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards Row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Lockers */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Total Lockers
              </CardTitle>
              <Package className="h-4 w-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.total_lockers?.total || 0}</div>
            <div className="mt-2 space-y-1">
              {Object.entries(data.total_lockers?.by_size || {}).map(([size, count]) => (
                <div key={size} className="flex justify-between text-xs">
                  <span className="text-gray-500 capitalize">{size}:</span>
                  <span className="font-medium">{count as number}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Occupancy */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Occupancy Rate
              </CardTitle>
              <PieChart className="h-4 w-4 text-green-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {data.occupancy?.occupancy_percentage || 0}%
            </div>
            <div className="mt-2 space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Occupied:</span>
                <span className="font-medium">{data.occupancy?.occupied || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Available:</span>
                <span className="font-medium">{data.occupancy?.available || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rent Collection */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Rent Collection
              </CardTitle>
              <DollarSign className="h-4 w-4 text-purple-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ₹{(data.rent_collection?.current_month?.collected || 0).toLocaleString()}
            </div>
            <div className="mt-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Collection %:</span>
                <span className="font-medium text-green-600">
                  {data.rent_collection?.current_month?.collection_percentage || 0}%
                </span>
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-gray-500">Pending:</span>
                <span className="font-medium text-orange-600">
                  ₹{(data.rent_collection?.current_month?.pending || 0).toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Overdue */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Overdue Rent
              </CardTitle>
              <AlertCircle className="h-4 w-4 text-red-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {data.overdue?.total_overdue_lockers || 0}
            </div>
            <div className="mt-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Amount:</span>
                <span className="font-medium text-red-600">
                  ₹{(data.overdue?.total_overdue_amount || 0).toLocaleString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* KPI Cards Row 2 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Waiting List */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Waiting List
              </CardTitle>
              <Clock className="h-4 w-4 text-yellow-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data.waiting_list?.total_waiting || 0}</div>
            <p className="text-xs text-gray-500 mt-1">
              Avg wait: {data.waiting_list?.average_wait_days || 0} days
            </p>
          </CardContent>
        </Card>

        {/* Recent Allocations */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Recent Allocations
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Today:</span>
                <span className="font-medium">{data.recent_allocations?.today || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">This Week:</span>
                <span className="font-medium">{data.recent_allocations?.this_week || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">This Month:</span>
                <span className="font-medium">{data.recent_allocations?.this_month || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Surrenders */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-gray-500">
                Recent Surrenders
              </CardTitle>
              <Activity className="h-4 w-4 text-gray-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Today:</span>
                <span className="font-medium">{data.recent_surrenders?.today || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">This Week:</span>
                <span className="font-medium">{data.recent_surrenders?.this_week || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">This Month:</span>
                <span className="font-medium">{data.recent_surrenders?.this_month || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Revenue Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trends</CardTitle>
            <CardDescription>Monthly revenue from lockers</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(data.revenue_trends || []).map((trend: any) => (
                <div key={trend.month} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{trend.month}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${(trend.revenue / 500000) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-24 text-right">
                      ₹{trend.revenue.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Occupancy Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Occupancy Trends</CardTitle>
            <CardDescription>Monthly occupancy percentage</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(data.occupancy_trends || []).map((trend: any) => (
                <div key={trend.month} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{trend.month}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${trend.percentage}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium w-16 text-right">
                      {trend.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}


// ============================================
// Reports Tab Component
// ============================================

function ReportsTab({ onGenerateReport }: any) {
  const reportCategories = [
    {
      category: 'Operational Reports',
      reports: [
        {
          type: ReportType.ALLOCATION_REGISTER,
          name: 'Locker Allocation Register',
          description: 'Complete register of all locker allocations',
          icon: FileText
        },
        {
          type: ReportType.AVAILABLE_OCCUPIED,
          name: 'Available/Occupied Lockers',
          description: 'Current status of all lockers',
          icon: Package
        },
        {
          type: ReportType.WAITING_LIST,
          name: 'Waiting List Report',
          description: 'Customers waiting for locker allocation',
          icon: Clock
        },
        {
          type: ReportType.ACCESS_LOG,
          name: 'Access Log Report',
          description: 'Locker access history and logs',
          icon: Activity
        },
        {
          type: ReportType.LOCKER_BREAKING,
          name: 'Locker Breaking Register',
          description: 'Record of all locker breaking incidents',
          icon: AlertCircle
        }
      ]
    },
    {
      category: 'Financial Reports',
      reports: [
        {
          type: ReportType.RENT_COLLECTION,
          name: 'Rent Collection Report',
          description: 'Summary of rent collections',
          icon: DollarSign
        },
        {
          type: ReportType.OVERDUE_RENT,
          name: 'Overdue Rent Report',
          description: 'List of overdue rent payments',
          icon: AlertCircle
        },
        {
          type: ReportType.REVENUE,
          name: 'Revenue Report',
          description: 'Total revenue from locker operations',
          icon: TrendingUp
        }
      ]
    },
    {
      category: 'Analytics Reports',
      reports: [
        {
          type: ReportType.BRANCH_WISE,
          name: 'Branch-wise Report',
          description: 'Performance across all branches',
          icon: BarChart3
        },
        {
          type: ReportType.OCCUPANCY_RATE,
          name: 'Occupancy Rate Report',
          description: 'Historical occupancy trends',
          icon: PieChart
        },
        {
          type: ReportType.CUSTOMER_DEMOGRAPHICS,
          name: 'Customer Demographics',
          description: 'Analysis of customer profiles',
          icon: Users
        }
      ]
    }
  ]

  return (
    <div className="space-y-6">
      {reportCategories.map((category) => (
        <Card key={category.category}>
          <CardHeader>
            <CardTitle>{category.category}</CardTitle>
            <CardDescription>
              {category.reports.length} reports available
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.reports.map((report) => {
                const Icon = report.icon
                return (
                  <Card key={report.type} className="cursor-pointer hover:border-blue-500 transition-colors">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <Icon className="h-5 w-5 text-blue-500" />
                        <Button 
                          size="sm" 
                          onClick={() => onGenerateReport(report.type)}
                        >
                          Generate
                        </Button>
                      </div>
                      <CardTitle className="text-base mt-2">{report.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-500">{report.description}</p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// ============================================
// Report Viewer Tab Component
// ============================================

function ReportViewerTab({ reportType, period, onPeriodChange }: any) {
  const [filters, setFilters] = useState({
    branch_id: '',
    from_date: '',
    to_date: ''
  })

  // Fetch report data based on type
  const { data: reportData, isLoading, refetch } = useQuery({
    queryKey: ['report', reportType, period, filters],
    queryFn: async () => {
      if (!reportType) return null

      switch (reportType) {
        case ReportType.ALLOCATION_REGISTER:
          return reportsService.generateAllocationRegister(filters)
        
        case ReportType.AVAILABLE_OCCUPIED:
          return reportsService.generateAvailableOccupiedReport(filters.branch_id)
        
        case ReportType.WAITING_LIST:
          return reportsService.generateWaitingListReport(filters.branch_id)
        
        case ReportType.RENT_COLLECTION:
          return reportsService.generateRentCollectionReport({ period })
        
        case ReportType.OVERDUE_RENT:
          return reportsService.generateOverdueRentReport({ branch_id: filters.branch_id })
        
        case ReportType.ACCESS_LOG:
          return reportsService.generateAccessLogReport({ period })
        
        case ReportType.LOCKER_BREAKING:
          return reportsService.generateLockerBreakingReport({ period })
        
        case ReportType.BRANCH_WISE:
          return reportsService.generateBranchWiseReport()
        
        case ReportType.REVENUE:
          return reportsService.generateRevenueReport({ period })
        
        case ReportType.OCCUPANCY_RATE:
          return reportsService.generateOccupancyRateReport({ period })
        
        case ReportType.CUSTOMER_DEMOGRAPHICS:
          return reportsService.generateCustomerDemographicsReport(filters.branch_id)
        
        default:
          return null
      }
    },
    enabled: !!reportType
  })

  if (!reportType) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No report selected</h3>
            <p className="mt-1 text-sm text-gray-500">
              Go to Reports tab and select a report to generate
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto" />
            <p className="mt-4 text-sm text-gray-500">Generating report...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Report Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Report Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <Label>Period</Label>
              <Select value={period} onValueChange={onPeriodChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ReportPeriod.TODAY}>Today</SelectItem>
                  <SelectItem value={ReportPeriod.THIS_WEEK}>This Week</SelectItem>
                  <SelectItem value={ReportPeriod.THIS_MONTH}>This Month</SelectItem>
                  <SelectItem value={ReportPeriod.LAST_MONTH}>Last Month</SelectItem>
                  <SelectItem value={ReportPeriod.THIS_QUARTER}>This Quarter</SelectItem>
                  <SelectItem value={ReportPeriod.THIS_YEAR}>This Year</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Branch</Label>
              <Select
                value={filters.branch_id}
                onValueChange={(value) => setFilters({ ...filters, branch_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Branches" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Branches</SelectItem>
                  <SelectItem value="branch-001">Branch 001</SelectItem>
                  <SelectItem value="branch-002">Branch 002</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>From Date</Label>
              <Input
                type="date"
                value={filters.from_date}
                onChange={(e) => setFilters({ ...filters, from_date: e.target.value })}
              />
            </div>

            <div>
              <Label>To Date</Label>
              <Input
                type="date"
                value={filters.to_date}
                onChange={(e) => setFilters({ ...filters, to_date: e.target.value })}
              />
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <Button onClick={() => refetch()}>
              Apply Filters
            </Button>
            <Button 
              variant="outline" 
              onClick={() => setFilters({ branch_id: '', from_date: '', to_date: '' })}
            >
              Clear
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Report Display */}
      {reportData && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {reportType.replace(/_/g, ' ').toUpperCase()}
                </CardTitle>
                <CardDescription>
                  Generated at: {format(new Date(reportData.generated_at), 'PPpp')}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Download className="mr-2 h-4 w-4" />
                  Export PDF
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="mr-2 h-4 w-4" />
                  Export Excel
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Summary Section */}
            <div className="mb-6">
              <h3 className="font-semibold mb-3">Summary</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(reportData.summary || {}).map(([key, value]) => {
                  if (typeof value === 'object') return null
                  return (
                    <div key={key} className="bg-gray-50 p-3 rounded">
                      <p className="text-xs text-gray-500 capitalize">
                        {key.replace(/_/g, ' ')}
                      </p>
                      <p className="text-lg font-semibold mt-1">
                        {typeof value === 'number' && key.includes('amount') 
                          ? `₹${value.toLocaleString()}`
                          : typeof value === 'number' && key.includes('percentage')
                          ? `${value}%`
                          : value}
                      </p>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Data Table */}
            {reportData.data && reportData.data.length > 0 && (
              <div>
                <h3 className="font-semibold mb-3">Details</h3>
                <div className="border rounded">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        {Object.keys(reportData.data[0]).slice(0, 6).map((key) => (
                          <TableHead key={key} className="capitalize">
                            {key.replace(/_/g, ' ')}
                          </TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {reportData.data.slice(0, 10).map((row: any, idx: number) => (
                        <TableRow key={idx}>
                          {Object.values(row).slice(0, 6).map((value: any, cellIdx: number) => (
                            <TableCell key={cellIdx}>
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                {reportData.data.length > 10 && (
                  <p className="text-sm text-gray-500 mt-2">
                    Showing 10 of {reportData.total_records} records
                  </p>
                )}
              </div>
            )}

            {(!reportData.data || reportData.data.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                No data available for the selected filters
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
