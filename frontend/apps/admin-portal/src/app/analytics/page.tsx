'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, BarChart3, PieChart, Activity, Calendar } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { reportsService } from '@/services/reports.service'
import { formatCurrency } from '@/lib/utils'
import { LineChart } from '@/components/charts/line-chart'
import { BarChart } from '@/components/charts/bar-chart'
import { AreaChart } from '@/components/charts/area-chart'
import { PieChart as PieChartComponent } from '@/components/charts/pie-chart'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly' | 'yearly'>('monthly')
  const [metric, setMetric] = useState<'disbursements' | 'collections' | 'customers' | 'deposits'>('disbursements')

  const trendsQuery = useQuery({
    queryKey: ['trends', metric, period],
    queryFn: () => reportsService.getTrends({ 
      metric, 
      period 
    }),
  })

  const comparativeQuery = useQuery({
    queryKey: ['comparative-analysis', period],
    queryFn: () => reportsService.getComparativeAnalysis({ period }),
  })

  // Sample data for charts
  const disbursementTrendData = [
    { month: 'Jan', amount: 45000, target: 50000 },
    { month: 'Feb', amount: 52000, target: 50000 },
    { month: 'Mar', amount: 48000, target: 50000 },
    { month: 'Apr', amount: 61000, target: 55000 },
    { month: 'May', amount: 55000, target: 55000 },
    { month: 'Jun', amount: 67000, target: 60000 },
  ]

  const collectionTrendData = [
    { month: 'Jan', collected: 42000, due: 45000 },
    { month: 'Feb', collected: 48000, due: 52000 },
    { month: 'Mar', collected: 45000, due: 48000 },
    { month: 'Apr', collected: 58000, due: 61000 },
    { month: 'May', collected: 52000, due: 55000 },
    { month: 'Jun', collected: 64000, due: 67000 },
  ]

  const customerGrowthData = [
    { month: 'Jan', customers: 1200 },
    { month: 'Feb', customers: 1350 },
    { month: 'Mar', customers: 1420 },
    { month: 'Apr', customers: 1580 },
    { month: 'May', customers: 1650 },
    { month: 'Jun', customers: 1820 },
  ]

  const portfolioGrowthData = [
    { month: 'Jan', loans: 850000, deposits: 650000 },
    { month: 'Feb', loans: 920000, deposits: 680000 },
    { month: 'Mar', loans: 880000, deposits: 710000 },
    { month: 'Apr', loans: 1050000, deposits: 750000 },
    { month: 'May', loans: 1100000, deposits: 780000 },
    { month: 'Jun', loans: 1250000, deposits: 850000 },
  ]

  const productComparisonData = [
    { product: 'Personal Loan', disbursed: 450000, collected: 420000 },
    { product: 'Business Loan', disbursed: 680000, collected: 650000 },
    { product: 'Gold Loan', disbursed: 320000, collected: 310000 },
    { product: 'Vehicle Loan', disbursed: 280000, collected: 270000 },
  ]

  const portfolioDistributionData = [
    { name: 'Personal Loan', value: 35 },
    { name: 'Business Loan', value: 28 },
    { name: 'Gold Loan', value: 20 },
    { name: 'Vehicle Loan', value: 12 },
    { name: 'Education Loan', value: 5 },
  ]

  const customerSegmentData = [
    { name: 'Salaried', value: 45 },
    { name: 'Self-Employed', value: 30 },
    { name: 'Business', value: 15 },
    { name: 'Others', value: 10 },
  ]

  const statusDistributionData = [
    { name: 'Active', value: 65 },
    { name: 'Overdue', value: 15 },
    { name: 'Closed', value: 18 },
    { name: 'NPA', value: 2 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Visualize trends and insights across your business</p>
          </div>
          <div className="flex gap-3">
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as any)}
              className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
        </div>

        {/* Key Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard
            label="Disbursement Trend"
            value={trendsQuery.data?.data?.disbursement_trend || 0}
            change={12.5}
            icon={TrendingUp}
            color="green"
          />
          <MetricCard
            label="Collection Trend"
            value={trendsQuery.data?.data?.collection_trend || 0}
            change={8.3}
            icon={TrendingUp}
            color="blue"
          />
          <MetricCard
            label="Customer Growth"
            value={trendsQuery.data?.data?.customer_growth || 0}
            change={5.7}
            icon={TrendingUp}
            color="purple"
          />
          <MetricCard
            label="NPA Trend"
            value={trendsQuery.data?.data?.npa_trend || 0}
            change={-2.1}
            icon={TrendingDown}
            color="red"
          />
        </div>

        {/* Analytics Tabs */}
        <Tabs defaultValue="trends">
          <TabsList>
            <TabsTrigger value="trends">
              <Activity className="h-4 w-4 mr-2" />
              Trends
            </TabsTrigger>
            <TabsTrigger value="comparative">
              <BarChart3 className="h-4 w-4 mr-2" />
              Comparative
            </TabsTrigger>
            <TabsTrigger value="distribution">
              <PieChart className="h-4 w-4 mr-2" />
              Distribution
            </TabsTrigger>
            <TabsTrigger value="forecast">
              <TrendingUp className="h-4 w-4 mr-2" />
              Forecast
            </TabsTrigger>
          </TabsList>

          {/* Trends Tab */}
          <TabsContent value="trends" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Disbursement Trends</CardTitle>
                    <Badge variant="outline">{period}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <LineChart
                    data={disbursementTrendData}
                    xKey="month"
                    lines={[
                      { key: 'amount', color: '#3b82f6', name: 'Disbursed' },
                      { key: 'target', color: '#10b981', name: 'Target' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Collection Trends</CardTitle>
                    <Badge variant="outline">{period}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <BarChart
                    data={collectionTrendData}
                    xKey="month"
                    bars={[
                      { key: 'collected', color: '#10b981', name: 'Collected' },
                      { key: 'due', color: '#ef4444', name: 'Due' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Customer Growth</CardTitle>
                    <Badge variant="outline">{period}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <AreaChart
                    data={customerGrowthData}
                    xKey="month"
                    areas={[
                      { key: 'customers', color: '#8b5cf6', name: 'Total Customers' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Portfolio Growth</CardTitle>
                    <Badge variant="outline">{period}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <AreaChart
                    data={portfolioGrowthData}
                    xKey="month"
                    areas={[
                      { key: 'loans', color: '#3b82f6', name: 'Loans' },
                      { key: 'deposits', color: '#10b981', name: 'Deposits' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Comparative Tab */}
          <TabsContent value="comparative" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Product Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <BarChart
                    data={productComparisonData}
                    xKey="product"
                    bars={[
                      { key: 'disbursed', color: '#3b82f6', name: 'Disbursed' },
                      { key: 'collected', color: '#10b981', name: 'Collected' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Year-over-Year Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <BarChart
                    data={[
                      { metric: 'Q1', current: 350000, previous: 320000 },
                      { metric: 'Q2', current: 420000, previous: 380000 },
                      { metric: 'Q3', current: 480000, previous: 410000 },
                      { metric: 'Q4', current: 520000, previous: 450000 },
                    ]}
                    xKey="metric"
                    bars={[
                      { key: 'current', color: '#3b82f6', name: 'Current Year' },
                      { key: 'previous', color: '#94a3b8', name: 'Previous Year' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Monthly Performance Matrix</CardTitle>
                </CardHeader>
                <CardContent>
                  {comparativeQuery.isLoading ? (
                    <div className="space-y-3">
                      {[...Array(6)].map((_, i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-3">Metric</th>
                            <th className="text-right p-3">Current</th>
                            <th className="text-right p-3">Previous</th>
                            <th className="text-right p-3">Change</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr className="border-b">
                            <td className="p-3">Disbursements</td>
                            <td className="text-right p-3 font-semibold">{formatCurrency(0)}</td>
                            <td className="text-right p-3">{formatCurrency(0)}</td>
                            <td className="text-right p-3">
                              <span className="text-green-600 font-medium">+0%</span>
                            </td>
                          </tr>
                          <tr className="border-b">
                            <td className="p-3">Collections</td>
                            <td className="text-right p-3 font-semibold">{formatCurrency(0)}</td>
                            <td className="text-right p-3">{formatCurrency(0)}</td>
                            <td className="text-right p-3">
                              <span className="text-green-600 font-medium">+0%</span>
                            </td>
                          </tr>
                          <tr className="border-b">
                            <td className="p-3">New Customers</td>
                            <td className="text-right p-3 font-semibold">0</td>
                            <td className="text-right p-3">0</td>
                            <td className="text-right p-3">
                              <span className="text-green-600 font-medium">+0%</span>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Distribution Tab */}
          <TabsContent value="distribution" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Portfolio Distribution by Product</CardTitle>
                </CardHeader>
                <CardContent>
                  <PieChartComponent
                    data={portfolioDistributionData}
                    dataKey="value"
                    nameKey="name"
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Customer Segmentation</CardTitle>
                </CardHeader>
                <CardContent>
                  <PieChartComponent
                    data={customerSegmentData}
                    dataKey="value"
                    nameKey="name"
                    colors={['#3b82f6', '#10b981', '#f59e0b', '#ef4444']}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Geographic Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <BarChart
                    data={[
                      { location: 'Mumbai', customers: 450 },
                      { location: 'Delhi', customers: 380 },
                      { location: 'Bangalore', customers: 320 },
                      { location: 'Pune', customers: 280 },
                      { location: 'Chennai', customers: 240 },
                    ]}
                    xKey="location"
                    bars={[
                      { key: 'customers', color: '#8b5cf6', name: 'Customers' },
                    ]}
                    height={280}
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Loan Status Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <PieChartComponent
                    data={statusDistributionData}
                    dataKey="value"
                    nameKey="name"
                    colors={['#10b981', '#f59e0b', '#3b82f6', '#ef4444']}
                    height={280}
                  />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Forecast Tab */}
          <TabsContent value="forecast" className="space-y-6">
            <div className="grid grid-cols-1 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Revenue Forecast (Next 6 Months)</CardTitle>
                </CardHeader>
                <CardContent>
                  <LineChart
                    data={[
                      { month: 'Jul', actual: 67000, forecast: 70000, lower: 65000, upper: 75000 },
                      { month: 'Aug', forecast: 73000, lower: 68000, upper: 78000 },
                      { month: 'Sep', forecast: 76000, lower: 71000, upper: 81000 },
                      { month: 'Oct', forecast: 79000, lower: 74000, upper: 84000 },
                      { month: 'Nov', forecast: 82000, lower: 77000, upper: 87000 },
                      { month: 'Dec', forecast: 85000, lower: 80000, upper: 90000 },
                    ]}
                    xKey="month"
                    lines={[
                      { key: 'actual', color: '#3b82f6', name: 'Actual' },
                      { key: 'forecast', color: '#10b981', name: 'Forecast' },
                      { key: 'lower', color: '#94a3b8', name: 'Lower Bound' },
                      { key: 'upper', color: '#94a3b8', name: 'Upper Bound' },
                    ]}
                    height={320}
                  />
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Disbursement Forecast</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <LineChart
                      data={[
                        { month: 'Jul', forecast: 70000 },
                        { month: 'Aug', forecast: 73000 },
                        { month: 'Sep', forecast: 76000 },
                        { month: 'Oct', forecast: 79000 },
                        { month: 'Nov', forecast: 82000 },
                        { month: 'Dec', forecast: 85000 },
                      ]}
                      xKey="month"
                      lines={[
                        { key: 'forecast', color: '#3b82f6', name: 'Forecast' },
                      ]}
                      height={280}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Collection Forecast</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <LineChart
                      data={[
                        { month: 'Jul', forecast: 67000 },
                        { month: 'Aug', forecast: 70000 },
                        { month: 'Sep', forecast: 73000 },
                        { month: 'Oct', forecast: 76000 },
                        { month: 'Nov', forecast: 79000 },
                        { month: 'Dec', forecast: 82000 },
                      ]}
                      xKey="month"
                      lines={[
                        { key: 'forecast', color: '#10b981', name: 'Forecast' },
                      ]}
                      height={280}
                    />
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function MetricCard({ 
  label, 
  value, 
  change,
  icon: Icon,
  color = 'blue'
}: { 
  label: string
  value: number
  change: number
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  const isPositive = change >= 0

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className={`flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            <span className="text-sm font-medium">{Math.abs(change)}%</span>
          </div>
        </div>
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}%</p>
      </CardContent>
    </Card>
  )
}
