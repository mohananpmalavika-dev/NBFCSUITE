'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Filter, Eye, BookOpen, TrendingUp, TrendingDown, DollarSign } from 'lucide-react'
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
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { accountingService } from '@/services/accounting.service'
import { formatCurrency, getStatusColor } from '@/lib/utils'
import type { ChartOfAccount } from '@/types'

export default function ChartOfAccountsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [groupFilter, setGroupFilter] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['chart-of-accounts', page, search, typeFilter, groupFilter],
    queryFn: () => accountingService.getAccounts({ 
      page, 
      page_size: 20,
      account_type: typeFilter || undefined,
      is_group: groupFilter ? groupFilter === 'true' : undefined
    }),
  })

  // Calculate stats by type
  const stats = data?.data?.items?.reduce(
    (acc, account: ChartOfAccount) => {
      if (account.account_type === 'Asset') acc.assets++
      else if (account.account_type === 'Liability') acc.liabilities++
      else if (account.account_type === 'Equity') acc.equity++
      else if (account.account_type === 'Income') acc.income++
      else if (account.account_type === 'Expense') acc.expenses++
      
      return acc
    },
    { assets: 0, liabilities: 0, equity: 0, income: 0, expenses: 0 }
  ) || { assets: 0, liabilities: 0, equity: 0, income: 0, expenses: 0 }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Chart of Accounts</h1>
            <p className="text-gray-600 mt-1">Manage your accounting ledger accounts</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Account
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <StatCard
            label="Assets"
            value={stats.assets}
            icon={TrendingUp}
            color="green"
          />
          <StatCard
            label="Liabilities"
            value={stats.liabilities}
            icon={TrendingDown}
            color="red"
          />
          <StatCard
            label="Equity"
            value={stats.equity}
            icon={DollarSign}
            color="blue"
          />
          <StatCard
            label="Income"
            value={stats.income}
            icon={TrendingUp}
            color="green"
          />
          <StatCard
            label="Expenses"
            value={stats.expenses}
            icon={TrendingDown}
            color="orange"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by account code, name..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={groupFilter}
            onChange={(e) => setGroupFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Accounts</option>
            <option value="true">Groups Only</option>
            <option value="false">Leaf Accounts Only</option>
          </select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Accounts Tabs */}
        <Tabs value={typeFilter} onValueChange={setTypeFilter}>
          <TabsList>
            <TabsTrigger value="">All Types</TabsTrigger>
            <TabsTrigger value="Asset">Assets</TabsTrigger>
            <TabsTrigger value="Liability">Liabilities</TabsTrigger>
            <TabsTrigger value="Equity">Equity</TabsTrigger>
            <TabsTrigger value="Income">Income</TabsTrigger>
            <TabsTrigger value="Expense">Expenses</TabsTrigger>
          </TabsList>

          <TabsContent value={typeFilter} className="space-y-4">
            {/* Table */}
            <div className="bg-white rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Account Code</TableHead>
                    <TableHead>Account Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Sub Type</TableHead>
                    <TableHead>Level</TableHead>
                    <TableHead>Balance</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    [...Array(5)].map((_, i) => (
                      <TableRow key={i}>
                        <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-40" /></TableCell>
                        <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                        <TableCell><Skeleton className="h-5 w-16" /></TableCell>
                        <TableCell><Skeleton className="h-8 w-20 ml-auto" /></TableCell>
                      </TableRow>
                    ))
                  ) : data?.data?.items && data.data.items.length > 0 ? (
                    data.data.items.map((account: ChartOfAccount) => (
                      <TableRow key={account.id}>
                        <TableCell className="font-mono text-sm font-medium">
                          {account.account_code}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {account.is_group && (
                              <BookOpen className="h-4 w-4 text-blue-600" />
                            )}
                            <span className={account.is_group ? 'font-semibold' : ''}>
                              {account.account_name}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{account.account_type}</Badge>
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {account.account_sub_type}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs">
                            L{account.level}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-semibold">
                          {formatCurrency(account.current_balance)}
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(account.is_active ? 'Active' : 'Inactive')}>
                            {account.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4 mr-2" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                        <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                        <p>No accounts found</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              {/* Pagination */}
              {data?.data && data.data.items.length > 0 && (
                <div className="flex items-center justify-between px-6 py-4 border-t">
                  <p className="text-sm text-gray-600">
                    Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.metadata?.total || 0)} of {data.metadata?.total || 0} accounts
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
          </TabsContent>
        </Tabs>
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
  value: number
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'orange'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    orange: 'bg-orange-100 text-orange-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
