'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Calendar, Download, FileText, TrendingUp, TrendingDown, Users, PiggyBank, DollarSign } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { reportsService } from '@/services/reports.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function ReportsPage() {
  const [reportType, setReportType] = useState<'loan' | 'deposit' | 'customer' | 'performance'>('loan')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState(new Date().toISOString().split('T')[0])

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
            <p className="text-gray-600 mt-1">Generate comprehensive business reports</p>
          </div>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export All
          </Button>
        </div>

        {/* Report Tabs */}
        <Tabs value={reportType} onValueChange={(v: any) => setReportType(v)}>
          <TabsList className="grid w-full md:w-auto grid-cols-4">
            <TabsTrigger value="loan">Loan Reports</TabsTrigger>
            <TabsTrigger value="deposit">Deposit Reports</TabsTrigger>
            <TabsTrigger value="customer">Customer Reports</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>

          {/* Loan Reports */}
          <TabsContent value="loan" className="space-y-6">
            <LoanReports fromDate={fromDate} toDate={toDate} setFromDate={setFromDate} setToDate={setToDate} />
          </TabsContent>

          {/* Deposit Reports */}
          <TabsContent value="deposit" className="space-y-6">
            <DepositReports fromDate={fromDate} toDate={toDate} setFromDate={setFromDate} setToDate={setToDate} />
          </TabsContent>

          {/* Customer Reports */}
          <TabsContent value="customer" className="space-y-6">
            <CustomerReports fromDate={fromDate} toDate={toDate} setFromDate={setFromDate} setToDate={setToDate} />
          </TabsContent>

          {/* Performance Reports */}
          <TabsContent value="performance" className="space-y-6">
            <PerformanceReports fromDate={fromDate} toDate={toDate} setFromDate={setFromDate} setToDate={setToDate} />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function LoanReports({ fromDate, toDate, setFromDate, setToDate }: any) {
  const portfolioQuery = useQuery({
    queryKey: ['loan-portfolio', fromDate, toDate],
    queryFn: () => reportsService.getLoanPortfolioReport({ from_date: fromDate, to_date: toDate }),
    enabled: !!toDate,
  })

  const npaQuery = useQuery({
    queryKey: ['npa-report', toDate],
    queryFn: () => reportsService.getNPAReport({ as_of_date: toDate }),
    enabled: !!toDate,
  })

  return (
    <>
      {/* Date Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Report Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>From Date</Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="date"
                  className="pl-10"
                  value={fromDate}
                  onChange={(e) => setFromDate(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>To Date</Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="date"
                  className="pl-10"
                  value={toDate}
                  onChange={(e) => setToDate(e.target.value)}
                />
              </div>
            </div>
            <div className="flex items-end">
              <Button className="w-full">Generate Reports</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Portfolio"
          value={formatCurrency(portfolioQuery.data?.data?.total_portfolio || 0)}
          icon={DollarSign}
          color="blue"
          loading={portfolioQuery.isLoading}
        />
        <StatCard
          label="Active Loans"
          value={portfolioQuery.data?.data?.active_loans || 0}
          icon={FileText}
          color="green"
          loading={portfolioQuery.isLoading}
        />
        <StatCard
          label="Disbursed This Month"
          value={formatCurrency(portfolioQuery.data?.data?.monthly_disbursement || 0)}
          icon={TrendingUp}
          color="purple"
          loading={portfolioQuery.isLoading}
        />
        <StatCard
          label="NPA Ratio"
          value={`${npaQuery.data?.data?.npa_ratio || 0}%`}
          icon={TrendingDown}
          color="red"
          loading={npaQuery.isLoading}
        />
      </div>

      {/* Detailed Reports */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Loan Portfolio by Product</CardTitle>
              <Button variant="ghost" size="sm">
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {portfolioQuery.isLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : portfolioQuery.data?.data?.by_product ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead className="text-right">Count</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {portfolioQuery.data.data.by_product.map((item: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{item.product_name}</TableCell>
                      <TableCell className="text-right">{item.count}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(item.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-center text-gray-500 py-8">No data available</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>NPA Analysis</CardTitle>
              <Button variant="ghost" size="sm">
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {npaQuery.isLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : npaQuery.data?.data?.breakdown ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Count</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {npaQuery.data.data.breakdown.map((item: any, i: number) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium">{item.category}</TableCell>
                      <TableCell className="text-right">{item.count}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(item.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-center text-gray-500 py-8">No data available</p>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  )
}

function DepositReports({ fromDate, toDate, setFromDate, setToDate }: any) {
  const portfolioQuery = useQuery({
    queryKey: ['deposit-portfolio', fromDate, toDate],
    queryFn: () => reportsService.getDepositPortfolioReport({ from_date: fromDate, to_date: toDate }),
    enabled: !!toDate,
  })

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Report Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>From Date</Label>
              <Input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>To Date</Label>
              <Input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button className="w-full">Generate Reports</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Deposits"
          value={formatCurrency(portfolioQuery.data?.data?.total_deposits || 0)}
          icon={PiggyBank}
          color="green"
          loading={portfolioQuery.isLoading}
        />
        <StatCard
          label="Active Accounts"
          value={portfolioQuery.data?.data?.active_accounts || 0}
          icon={FileText}
          color="blue"
          loading={portfolioQuery.isLoading}
        />
        <StatCard
          label="New Deposits"
          value={formatCurrency(portfolioQuery.data?.data?.new_deposits || 0)}
          icon={TrendingUp}
          color="purple"
          loading={portfolioQuery.isLoading}
        />
        <StatCard
          label="Matured This Month"
          value={portfolioQuery.data?.data?.matured_count || 0}
          icon={FileText}
          color="orange"
          loading={portfolioQuery.isLoading}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Deposit Portfolio by Type</CardTitle>
        </CardHeader>
        <CardContent>
          {portfolioQuery.isLoading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : portfolioQuery.data?.data?.by_type ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Count</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {portfolioQuery.data.data.by_type.map((item: any, i: number) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{item.type}</TableCell>
                    <TableCell className="text-right">{item.count}</TableCell>
                    <TableCell className="text-right font-semibold">
                      {formatCurrency(item.amount)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-center text-gray-500 py-8">No data available</p>
          )}
        </CardContent>
      </Card>
    </>
  )
}

function CustomerReports({ fromDate, toDate, setFromDate, setToDate }: any) {
  const acquisitionQuery = useQuery({
    queryKey: ['customer-acquisition', fromDate, toDate],
    queryFn: () => reportsService.getCustomerAcquisitionReport({ from_date: fromDate, to_date: toDate }),
    enabled: !!toDate,
  })

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Report Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>From Date</Label>
              <Input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>To Date</Label>
              <Input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button className="w-full">Generate Reports</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Customers"
          value={acquisitionQuery.data?.data?.total_customers || 0}
          icon={Users}
          color="blue"
          loading={acquisitionQuery.isLoading}
        />
        <StatCard
          label="New Customers"
          value={acquisitionQuery.data?.data?.new_customers || 0}
          icon={TrendingUp}
          color="green"
          loading={acquisitionQuery.isLoading}
        />
        <StatCard
          label="Active Customers"
          value={acquisitionQuery.data?.data?.active_customers || 0}
          icon={Users}
          color="purple"
          loading={acquisitionQuery.isLoading}
        />
        <StatCard
          label="Growth Rate"
          value={`${acquisitionQuery.data?.data?.growth_rate || 0}%`}
          icon={TrendingUp}
          color="orange"
          loading={acquisitionQuery.isLoading}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Customer Acquisition Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-gray-500 py-8">
            Chart visualization will be displayed here
          </p>
        </CardContent>
      </Card>
    </>
  )
}

function PerformanceReports({ fromDate, toDate, setFromDate, setToDate }: any) {
  const metricsQuery = useQuery({
    queryKey: ['performance-metrics', fromDate, toDate],
    queryFn: () => reportsService.getPerformanceMetrics({ from_date: fromDate, to_date: toDate }),
    enabled: !!toDate,
  })

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Report Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>From Date</Label>
              <Input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>To Date</Label>
              <Input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button className="w-full">Generate Reports</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Collection Efficiency"
          value={`${metricsQuery.data?.data?.collection_efficiency || 0}%`}
          icon={TrendingUp}
          color="green"
          loading={metricsQuery.isLoading}
        />
        <StatCard
          label="ROA"
          value={`${metricsQuery.data?.data?.roa || 0}%`}
          icon={DollarSign}
          color="blue"
          loading={metricsQuery.isLoading}
        />
        <StatCard
          label="ROE"
          value={`${metricsQuery.data?.data?.roe || 0}%`}
          icon={DollarSign}
          color="purple"
          loading={metricsQuery.isLoading}
        />
        <StatCard
          label="Net Profit Margin"
          value={`${metricsQuery.data?.data?.net_profit_margin || 0}%`}
          icon={TrendingUp}
          color="orange"
          loading={metricsQuery.isLoading}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Key Performance Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-gray-500 py-8">
            Performance metrics visualization will be displayed here
          </p>
        </CardContent>
      </Card>
    </>
  )
}

function StatCard({ 
  label, 
  value, 
  icon: Icon,
  color = 'blue',
  loading = false
}: { 
  label: string
  value: string | number
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'orange'
  loading?: boolean
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        {loading ? (
          <Skeleton className="h-20 w-full" />
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">{label}</p>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
            </div>
            <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
              <Icon className="h-6 w-6" />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
