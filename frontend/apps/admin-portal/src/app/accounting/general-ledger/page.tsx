'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, Calendar, BookOpen, TrendingUp, TrendingDown } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { accountingService } from '@/services/accounting.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function GeneralLedgerPage() {
  const [page, setPage] = useState(1)
  const [accountCode, setAccountCode] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['general-ledger', page, accountCode, fromDate, toDate],
    queryFn: () => accountingService.getGeneralLedger({ 
      page, 
      page_size: 20,
      account_code: accountCode || undefined,
      from_date: fromDate || undefined,
      to_date: toDate || undefined
    }),
    enabled: !!accountCode, // Only fetch when account is selected
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">General Ledger</h1>
            <p className="text-gray-600 mt-1">View detailed account transactions and balances</p>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Ledger Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Account Code</label>
                <div className="relative">
                  <BookOpen className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    type="text"
                    placeholder="Enter account code"
                    className="pl-10"
                    value={accountCode}
                    onChange={(e) => setAccountCode(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
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

              <div className="space-y-2">
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

              <div className="space-y-2">
                <label className="text-sm font-medium">&nbsp;</label>
                <Button className="w-full">
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Summary */}
        {data?.data && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard
              label="Opening Balance"
              value={formatCurrency(0)}
              icon={BookOpen}
              color="blue"
            />
            <StatCard
              label="Total Debit"
              value={formatCurrency(0)}
              icon={TrendingUp}
              color="green"
            />
            <StatCard
              label="Total Credit"
              value={formatCurrency(0)}
              icon={TrendingDown}
              color="red"
            />
            <StatCard
              label="Closing Balance"
              value={formatCurrency(0)}
              icon={BookOpen}
              color="purple"
            />
          </div>
        )}

        {/* Ledger Entries */}
        {!accountCode ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-gray-500">
                <BookOpen className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                <p className="text-lg font-medium">Select an Account</p>
                <p className="text-sm mt-1">Enter an account code above to view the general ledger</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="bg-white rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Entry Number</TableHead>
                  <TableHead>Narration</TableHead>
                  <TableHead>Debit</TableHead>
                  <TableHead>Credit</TableHead>
                  <TableHead>Balance</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                    </TableRow>
                  ))
                ) : data?.data?.entries && data.data.entries.length > 0 ? (
                  data.data.entries.map((entry: any, index: number) => {
                    // Calculate running balance
                    const runningBalance = 0 // Calculate based on your logic
                    
                    return (
                      <TableRow key={index}>
                        <TableCell className="text-sm text-gray-600">
                          {formatDate(entry.transaction_date)}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {entry.entry_number}
                        </TableCell>
                        <TableCell>{entry.narration}</TableCell>
                        <TableCell className="font-semibold">
                          {entry.debit_amount > 0 ? formatCurrency(entry.debit_amount) : '-'}
                        </TableCell>
                        <TableCell className="font-semibold">
                          {entry.credit_amount > 0 ? formatCurrency(entry.credit_amount) : '-'}
                        </TableCell>
                        <TableCell className="font-semibold">
                          {formatCurrency(entry.balance || 0)}
                        </TableCell>
                      </TableRow>
                    )
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                      <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                      <p>No ledger entries found for this account</p>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>

            {/* Pagination */}
            {data?.data && data.data.entries?.length > 0 && (
              <div className="flex items-center justify-between px-6 py-4 border-t">
                <p className="text-sm text-gray-600">
                  Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.metadata?.total || 0)} of {data.metadata?.total || 0} entries
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.metadata?.has_prev}
                    onClick={() => setPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!data.metadata?.has_next}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

function StatCard({ 
  label, 
  value, 
  icon: Icon,
  color = 'blue'
}: { 
  label: string
  value: string
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

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-xl font-bold text-gray-900">{value}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
