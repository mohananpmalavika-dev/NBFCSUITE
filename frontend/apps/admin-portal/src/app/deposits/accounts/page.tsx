'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Filter, Eye, MoreVertical, PiggyBank, TrendingUp } from 'lucide-react'
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'
import { depositService } from '@/services/deposit.service'
import { formatCurrency, formatDate, getStatusColor } from '@/lib/utils'
import type { DepositAccount } from '@/types'

export default function DepositAccountsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['deposit-accounts', page, search, typeFilter, statusFilter],
    queryFn: () => depositService.getAccounts({ 
      page, 
      page_size: 20,
      deposit_type: typeFilter || undefined,
      status: statusFilter || undefined
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Deposit Accounts</h1>
            <p className="text-gray-600 mt-1">Manage savings, FD, RD, and MIS accounts</p>
          </div>
          <Link href="/deposits/accounts/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Open Account
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by account number, customer name..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="Savings">Savings</option>
            <option value="Fixed">Fixed Deposit</option>
            <option value="Recurring">Recurring Deposit</option>
            <option value="MIS">MIS</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="Active">Active</option>
            <option value="Matured">Matured</option>
            <option value="Closed">Closed</option>
          </select>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Accounts"
            value={data?.metadata?.total || 0}
            icon={PiggyBank}
            color="blue"
          />
          <StatCard
            label="Total Balance"
            value="₹0"
            icon={TrendingUp}
            color="green"
          />
          <StatCard
            label="Active Accounts"
            value="0"
            icon={PiggyBank}
            color="blue"
          />
          <StatCard
            label="Matured Accounts"
            value="0"
            icon={PiggyBank}
            color="yellow"
          />
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Account Number</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Balance</TableHead>
                <TableHead>Interest Rate</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Opened On</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-8 ml-auto" /></TableCell>
                  </TableRow>
                ))
              ) : data?.data?.items && data.data.items.length > 0 ? (
                data.data.items.map((account: DepositAccount) => (
                  <TableRow key={account.id}>
                    <TableCell className="font-mono text-sm">
                      {account.account_number}
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{account.customer_name || 'N/A'}</p>
                        <p className="text-sm text-gray-500">ID: {account.customer_id.slice(0, 8)}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{account.deposit_type}</Badge>
                    </TableCell>
                    <TableCell className="font-semibold">
                      {formatCurrency(account.deposit_amount)}
                    </TableCell>
                    <TableCell className="font-semibold">
                      {formatCurrency(account.account_balance)}
                    </TableCell>
                    <TableCell>
                      {account.interest_rate}% p.a.
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(account.account_status)}>
                        {account.account_status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {formatDate(account.opening_date)}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <Link href={`/deposits/accounts/${account.id}`}>
                            <DropdownMenuItem>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                          </Link>
                          {account.account_status === 'Active' && (
                            <>
                              <DropdownMenuItem>
                                Deposit
                              </DropdownMenuItem>
                              {account.deposit_type === 'Savings' && (
                                <DropdownMenuItem>
                                  Withdraw
                                </DropdownMenuItem>
                              )}
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    <PiggyBank className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No deposit accounts found</p>
                    <Link href="/deposits/accounts/new">
                      <Button variant="link" className="mt-2">
                        Open your first deposit account
                      </Button>
                    </Link>
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
  value: string | number
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
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
