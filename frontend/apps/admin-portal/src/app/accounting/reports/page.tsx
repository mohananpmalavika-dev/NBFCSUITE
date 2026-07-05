'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, TrendingUp, TrendingDown, Calendar, Download, Eye } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
import { accountingService } from '@/services/accounting.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function FinancialReportsPage() {
  const [reportType, setReportType] = useState<'trial-balance' | 'profit-loss' | 'balance-sheet'>('trial-balance')
  const [balanceDate, setBalanceDate] = useState(new Date().toISOString().split('T')[0])
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState(new Date().toISOString().split('T')[0])
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split('T')[0])

  const trialBalanceQuery = useQuery({
    queryKey: ['trial-balance', balanceDate],
    queryFn: () => accountingService.getTrialBalance({ balance_date: balanceDate }),
    enabled: reportType === 'trial-balance' && !!balanceDate,
  })

  const profitLossQuery = useQuery({
    queryKey: ['profit-loss', fromDate, toDate],
    queryFn: () => accountingService.getProfitLoss({ from_date: fromDate, to_date: toDate }),
    enabled: reportType === 'profit-loss' && !!fromDate && !!toDate,
  })

  const balanceSheetQuery = useQuery({
    queryKey: ['balance-sheet', asOfDate],
    queryFn: () => accountingService.getBalanceSheet({ as_of_date: asOfDate }),
    enabled: reportType === 'balance-sheet' && !!asOfDate,
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Financial Reports</h1>
            <p className="text-gray-600 mt-1">Generate and view accounting reports and statements</p>
          </div>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>

        {/* Report Tabs */}
        <Tabs value={reportType} onValueChange={(v: any) => setReportType(v)}>
          <TabsList className="grid w-full md:w-auto grid-cols-3">
            <TabsTrigger value="trial-balance">Trial Balance</TabsTrigger>
            <TabsTrigger value="profit-loss">Profit & Loss</TabsTrigger>
            <TabsTrigger value="balance-sheet">Balance Sheet</TabsTrigger>
          </TabsList>

          {/* Trial Balance */}
          <TabsContent value="trial-balance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Trial Balance Parameters</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-4">
                  <div className="flex-1 space-y-2">
                    <label className="text-sm font-medium">Balance Date</label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        type="date"
                        className="pl-10"
                        value={balanceDate}
                        onChange={(e) => setBalanceDate(e.target.value)}
                      />
                    </div>
                  </div>
                  <Button>
                    <Eye className="h-4 w-4 mr-2" />
                    Generate Report
                  </Button>
                </div>
              </CardContent>
            </Card>

            <TrialBalanceReport query={trialBalanceQuery} />
          </TabsContent>

          {/* Profit & Loss */}
          <TabsContent value="profit-loss" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Profit & Loss Parameters</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-4">
                  <div className="flex-1 space-y-2">
                    <label className="text-sm font-medium">From Date</label>
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
                  <div className="flex-1 space-y-2">
                    <label className="text-sm font-medium">To Date</label>
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
                  <Button>
                    <Eye className="h-4 w-4 mr-2" />
                    Generate Report
                  </Button>
                </div>
              </CardContent>
            </Card>

            <ProfitLossReport query={profitLossQuery} />
          </TabsContent>

          {/* Balance Sheet */}
          <TabsContent value="balance-sheet" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Balance Sheet Parameters</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-4">
                  <div className="flex-1 space-y-2">
                    <label className="text-sm font-medium">As of Date</label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        type="date"
                        className="pl-10"
                        value={asOfDate}
                        onChange={(e) => setAsOfDate(e.target.value)}
                      />
                    </div>
                  </div>
                  <Button>
                    <Eye className="h-4 w-4 mr-2" />
                    Generate Report
                  </Button>
                </div>
              </CardContent>
            </Card>

            <BalanceSheetReport query={balanceSheetQuery} />
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function TrialBalanceReport({ query }: { query: any }) {
  const { data, isLoading } = query

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Trial Balance</span>
          {data?.data?.balance_date && (
            <span className="text-sm font-normal text-gray-600">
              As on {formatDate(data.data.balance_date)}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : data?.data?.accounts ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Account Code</TableHead>
                <TableHead>Account Name</TableHead>
                <TableHead className="text-right">Debit</TableHead>
                <TableHead className="text-right">Credit</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.data.accounts.map((account: any, index: number) => (
                <TableRow key={index}>
                  <TableCell className="font-mono text-sm">{account.account_code}</TableCell>
                  <TableCell>{account.account_name}</TableCell>
                  <TableCell className="text-right font-semibold">
                    {account.debit_balance > 0 ? formatCurrency(account.debit_balance) : '-'}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {account.credit_balance > 0 ? formatCurrency(account.credit_balance) : '-'}
                  </TableCell>
                </TableRow>
              ))}
              <TableRow className="border-t-2 font-bold">
                <TableCell colSpan={2}>Total</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(data.data.total_debit || 0)}
                </TableCell>
                <TableCell className="text-right">
                  {formatCurrency(data.data.total_credit || 0)}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p>Set parameters and click "Generate Report" to view trial balance</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ProfitLossReport({ query }: { query: any }) {
  const { data, isLoading } = query

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Profit & Loss Statement</span>
          {data?.data?.from_date && data?.data?.to_date && (
            <span className="text-sm font-normal text-gray-600">
              {formatDate(data.data.from_date)} to {formatDate(data.data.to_date)}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : data?.data ? (
          <div className="space-y-6">
            {/* Income Section */}
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Income
              </h3>
              <Table>
                <TableBody>
                  {data.data.income_accounts?.map((account: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{account.account_name}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(account.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="border-t font-bold">
                    <TableCell>Total Income</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.data.total_income || 0)}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>

            {/* Expense Section */}
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <TrendingDown className="h-5 w-5 mr-2 text-red-600" />
                Expenses
              </h3>
              <Table>
                <TableBody>
                  {data.data.expense_accounts?.map((account: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{account.account_name}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(account.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="border-t font-bold">
                    <TableCell>Total Expenses</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.data.total_expenses || 0)}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>

            {/* Net Profit/Loss */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold">
                  {(data.data.net_profit_loss || 0) >= 0 ? 'Net Profit' : 'Net Loss'}
                </h3>
                <p className={`text-3xl font-bold ${
                  (data.data.net_profit_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatCurrency(Math.abs(data.data.net_profit_loss || 0))}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p>Set parameters and click "Generate Report" to view profit & loss</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function BalanceSheetReport({ query }: { query: any }) {
  const { data, isLoading } = query

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Balance Sheet</span>
          {data?.data?.as_of_date && (
            <span className="text-sm font-normal text-gray-600">
              As on {formatDate(data.data.as_of_date)}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : data?.data ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Assets */}
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                Assets
              </h3>
              <Table>
                <TableBody>
                  {data.data.assets?.map((account: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{account.account_name}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(account.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="border-t font-bold">
                    <TableCell>Total Assets</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(data.data.total_assets || 0)}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>

            {/* Liabilities & Equity */}
            <div>
              <h3 className="font-semibold text-lg mb-3 flex items-center">
                <TrendingDown className="h-5 w-5 mr-2 text-red-600" />
                Liabilities & Equity
              </h3>
              <Table>
                <TableBody>
                  {data.data.liabilities?.map((account: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell>{account.account_name}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(account.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                  {data.data.equity?.map((account: any, index: number) => (
                    <TableRow key={`equity-${index}`}>
                      <TableCell>{account.account_name}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(account.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="border-t font-bold">
                    <TableCell>Total Liabilities & Equity</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency((data.data.total_liabilities || 0) + (data.data.total_equity || 0))}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p>Set parameters and click "Generate Report" to view balance sheet</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
