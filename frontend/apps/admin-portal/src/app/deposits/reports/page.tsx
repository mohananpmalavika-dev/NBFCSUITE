'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, 
  TrendingDown, 
  PiggyBank, 
  Users, 
  Calendar,
  AlertCircle,
  FileText,
  Download,
  RefreshCw
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { depositService } from '@/services/deposit.service'
import { formatCurrency, formatDate, formatNumber } from '@/lib/utils'

export default function DepositReportsPage() {
  const [activeTab, setActiveTab] = useState('dashboard')

  // Fetch dashboard data
  const { data: dashboardData, isLoading: dashboardLoading, refetch } = useQuery({
    queryKey: ['deposit-reports-dashboard'],
    queryFn: () => depositService.getReportsDashboard(),
  })

  // Fetch maturity calendar
  const { data: maturityData, isLoading: maturityLoading } = useQuery({
    queryKey: ['deposit-maturity-calendar'],
    queryFn: () => depositService.getMaturityCalendar(30),
  })

  // Fetch product performance
  const { data: performanceData, isLoading: performanceLoading } = useQuery({
    queryKey: ['deposit-product-performance'],
    queryFn: () => depositService.getProductPerformance(),
  })

  // Fetch dormancy report
  const { data: dormancyData, isLoading: dormancyLoading } = useQuery({
    queryKey: ['deposit-dormancy-report'],
    queryFn: () => depositService.getDormancyReport(),
  })

  const handleRefresh = () => {
    refetch()
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Deposit Reports</h1>
            <p className="text-gray-600 mt-1">Comprehensive analytics and insights</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export All
            </Button>
          </div>
        </div>

        {/* KPI Cards */}
        {dashboardLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardHeader className="pb-2">
                  <Skeleton className="h-4 w-24" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-32" />
                  <Skeleton className="h-3 w-20 mt-2" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Total Deposits
                </CardTitle>
                <PiggyBank className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(dashboardData?.data?.total_balance || 0)}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  {formatNumber(dashboardData?.data?.total_accounts || 0)} accounts
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Active Accounts
                </CardTitle>
                <Users className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(dashboardData?.data?.active_accounts || 0)}
                </div>
                <p className="text-xs text-green-600 mt-1 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  {((dashboardData?.data?.active_accounts / dashboardData?.data?.total_accounts) * 100).toFixed(1)}% of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Maturing Soon
                </CardTitle>
                <Calendar className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(dashboardData?.data?.pending_maturities_30_days || 0)}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Next 30 days
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  Interest Paid (YTD)
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(dashboardData?.data?.total_interest_paid || 0)}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Year to date
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tabs for Different Reports */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard">Overview</TabsTrigger>
            <TabsTrigger value="maturity">Maturity Calendar</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="dormancy">Dormancy</TabsTrigger>
            <TabsTrigger value="more">More Reports</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Account Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Account Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  {dashboardLoading ? (
                    <div className="space-y-3">
                      {[1, 2, 3, 4].map((i) => (
                        <Skeleton key={i} className="h-12 w-full" />
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-8 bg-blue-500 rounded" />
                          <div>
                            <p className="font-medium">Savings</p>
                            <p className="text-sm text-gray-600">
                              {formatNumber(dashboardData?.data?.savings_accounts || 0)} accounts
                            </p>
                          </div>
                        </div>
                        <p className="font-semibold">{formatCurrency(dashboardData?.data?.savings_balance || 0)}</p>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-8 bg-green-500 rounded" />
                          <div>
                            <p className="font-medium">Fixed Deposits</p>
                            <p className="text-sm text-gray-600">
                              {formatNumber(dashboardData?.data?.fd_accounts || 0)} accounts
                            </p>
                          </div>
                        </div>
                        <p className="font-semibold">{formatCurrency(dashboardData?.data?.fd_balance || 0)}</p>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-8 bg-purple-500 rounded" />
                          <div>
                            <p className="font-medium">Recurring Deposits</p>
                            <p className="text-sm text-gray-600">
                              {formatNumber(dashboardData?.data?.rd_accounts || 0)} accounts
                            </p>
                          </div>
                        </div>
                        <p className="font-semibold">{formatCurrency(dashboardData?.data?.rd_balance || 0)}</p>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-8 bg-orange-500 rounded" />
                          <div>
                            <p className="font-medium">MIS</p>
                            <p className="text-sm text-gray-600">
                              {formatNumber(dashboardData?.data?.mis_accounts || 0)} accounts
                            </p>
                          </div>
                        </div>
                        <p className="font-semibold">{formatCurrency(dashboardData?.data?.mis_balance || 0)}</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Key Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-2 border-b">
                      <span className="text-gray-600">Matured Accounts</span>
                      <span className="font-semibold">{formatNumber(dashboardData?.data?.matured_accounts || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b">
                      <span className="text-gray-600">Dormant Accounts</span>
                      <Badge variant="destructive">
                        {formatNumber(dashboardData?.data?.dormant_accounts || 0)}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b">
                      <span className="text-gray-600">Accounts with Liens</span>
                      <span className="font-semibold">{formatNumber(dashboardData?.data?.accounts_with_liens || 0)}</span>
                    </div>
                    <div className="flex items-center justify-between py-2">
                      <span className="text-gray-600">Total Balance</span>
                      <span className="font-bold text-lg">{formatCurrency(dashboardData?.data?.total_balance || 0)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Maturity Calendar Tab */}
          <TabsContent value="maturity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Maturities (Next 30 Days)</CardTitle>
              </CardHeader>
              <CardContent>
                {maturityLoading ? (
                  <div className="space-y-2">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-12 w-full" />
                    ))}
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Account Number</TableHead>
                          <TableHead>Customer</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Maturity Date</TableHead>
                          <TableHead className="text-right">Principal</TableHead>
                          <TableHead className="text-right">Interest</TableHead>
                          <TableHead className="text-right">Maturity Amount</TableHead>
                          <TableHead>Auto Renew</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {maturityData?.data?.accounts?.map((account: any) => (
                          <TableRow key={account.id}>
                            <TableCell className="font-medium">{account.account_number}</TableCell>
                            <TableCell>{account.customer_name}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{account.account_type}</Badge>
                            </TableCell>
                            <TableCell>{formatDate(account.maturity_date)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(account.principal_amount)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(account.interest_amount)}</TableCell>
                            <TableCell className="text-right font-semibold">{formatCurrency(account.maturity_amount)}</TableCell>
                            <TableCell>
                              {account.auto_renewal ? (
                                <Badge className="bg-green-100 text-green-800">Yes</Badge>
                              ) : (
                                <Badge variant="secondary">No</Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    {(!maturityData?.data?.accounts || maturityData.data.accounts.length === 0) && (
                      <div className="text-center py-8 text-gray-500">
                        <Calendar className="h-12 w-12 mx-auto mb-2 opacity-50" />
                        <p>No accounts maturing in the next 30 days</p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Product Performance</CardTitle>
              </CardHeader>
              <CardContent>
                {performanceLoading ? (
                  <Skeleton className="h-64 w-full" />
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Product Type</TableHead>
                          <TableHead className="text-right">Total Accounts</TableHead>
                          <TableHead className="text-right">Active Accounts</TableHead>
                          <TableHead className="text-right">Total Balance</TableHead>
                          <TableHead className="text-right">Avg Balance</TableHead>
                          <TableHead className="text-right">Interest Paid</TableHead>
                          <TableHead className="text-right">Growth</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {performanceData?.data?.products?.map((product: any) => (
                          <TableRow key={product.product_type}>
                            <TableCell className="font-medium">{product.product_type}</TableCell>
                            <TableCell className="text-right">{formatNumber(product.total_accounts)}</TableCell>
                            <TableCell className="text-right">{formatNumber(product.active_accounts)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(product.total_balance)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(product.avg_balance)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(product.interest_paid)}</TableCell>
                            <TableCell className="text-right">
                              {product.growth_rate >= 0 ? (
                                <span className="text-green-600 flex items-center justify-end">
                                  <TrendingUp className="h-4 w-4 mr-1" />
                                  {product.growth_rate}%
                                </span>
                              ) : (
                                <span className="text-red-600 flex items-center justify-end">
                                  <TrendingDown className="h-4 w-4 mr-1" />
                                  {Math.abs(product.growth_rate)}%
                                </span>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Dormancy Tab */}
          <TabsContent value="dormancy" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Dormant Accounts</CardTitle>
                <Badge variant="destructive" className="text-lg">
                  {dormancyData?.data?.total_dormant || 0} Accounts
                </Badge>
              </CardHeader>
              <CardContent>
                {dormancyLoading ? (
                  <Skeleton className="h-64 w-full" />
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Account Number</TableHead>
                          <TableHead>Customer</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Last Transaction</TableHead>
                          <TableHead className="text-right">Balance</TableHead>
                          <TableHead>Dormant Since</TableHead>
                          <TableHead>Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {dormancyData?.data?.accounts?.map((account: any) => (
                          <TableRow key={account.id}>
                            <TableCell className="font-medium">{account.account_number}</TableCell>
                            <TableCell>{account.customer_name}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{account.account_type}</Badge>
                            </TableCell>
                            <TableCell>{formatDate(account.last_transaction_date)}</TableCell>
                            <TableCell className="text-right">{formatCurrency(account.balance)}</TableCell>
                            <TableCell>
                              <Badge variant="destructive">{account.dormant_months} months</Badge>
                            </TableCell>
                            <TableCell>
                              <Button variant="outline" size="sm">
                                Reactivate
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    {(!dormancyData?.data?.accounts || dormancyData.data.accounts.length === 0) && (
                      <div className="text-center py-8 text-gray-500">
                        <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                        <p>No dormant accounts found</p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* More Reports Tab */}
          <TabsContent value="more" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    Aging Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Account age distribution and trends
                  </p>
                  <Button variant="outline" className="w-full">
                    View Report
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-green-600" />
                    Interest Accrual
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Interest calculation and accrual details
                  </p>
                  <Button variant="outline" className="w-full">
                    View Report
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-purple-600" />
                    TDS Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    TDS deductions and certificates
                  </p>
                  <Button variant="outline" className="w-full">
                    View Report
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-orange-600" />
                    Transaction Volume
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Deposits and withdrawals analysis
                  </p>
                  <Button variant="outline" className="w-full">
                    View Report
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-red-600" />
                    Deposit Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Complete portfolio summary
                  </p>
                  <Button variant="outline" className="w-full">
                    View Report
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-teal-600" />
                    Customer Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 mb-4">
                    Customer-wise deposit details
                  </p>
                  <Button variant="outline" className="w-full">
                    View Report
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
