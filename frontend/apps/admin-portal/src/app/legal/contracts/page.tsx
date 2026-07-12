'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { 
  FileText, Plus, Filter, Search, Calendar, AlertCircle, 
  CheckCircle, XCircle, Clock, Eye, Edit, Trash2, Download 
} from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
import { Badge } from '@/components/ui/badge'
import { contractService, type ContractFilters, type ContractStatus, type ContractType } from '@/services/contract.service'

export default function ContractsListPage() {
  const [filters, setFilters] = useState<ContractFilters>({
    page: 1,
    page_size: 10,
    search_query: '',
  })

  const { data: contractsData, isLoading } = useQuery({
    queryKey: ['contracts', filters],
    queryFn: () => contractService.getContracts(filters),
  })

  const { data: statsData } = useQuery({
    queryKey: ['contract-statistics'],
    queryFn: () => contractService.getStatistics(),
  })

  const contracts = contractsData?.data?.items || []
  const stats = statsData?.data?.data
  const pagination = contractsData?.data

  const handleFilterChange = (key: keyof ContractFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }))
  }

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Contract Management</h1>
            <p className="text-gray-600 mt-1">Manage contracts, renewals, and lifecycle tracking</p>
          </div>
          <Link href="/legal/contracts/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Contract
            </Button>
          </Link>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Contracts"
            value={stats?.total_contracts || 0}
            icon={FileText}
            color="blue"
          />
          <StatCard
            title="Active Contracts"
            value={stats?.active_contracts || 0}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            title="Expiring Soon"
            value={stats?.expiring_soon || 0}
            icon={AlertCircle}
            color="yellow"
          />
          <StatCard
            title="Pending Renewals"
            value={stats?.pending_renewals || 0}
            icon={Clock}
            color="orange"
          />
          <StatCard
            title="Total Value"
            value={contractService.formatCurrency(stats?.total_contract_value)}
            icon={FileText}
            color="purple"
          />
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search contracts..."
                  value={filters.search_query || ''}
                  onChange={(e) => handleFilterChange('search_query', e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Contract Type */}
              <Select
                value={filters.contract_type || 'all'}
                onValueChange={(value) => handleFilterChange('contract_type', value === 'all' ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Contract Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="vendor">Vendor</SelectItem>
                  <SelectItem value="customer">Customer</SelectItem>
                  <SelectItem value="employee">Employee</SelectItem>
                  <SelectItem value="partnership">Partnership</SelectItem>
                  <SelectItem value="lease">Lease</SelectItem>
                  <SelectItem value="license">License</SelectItem>
                  <SelectItem value="service">Service</SelectItem>
                  <SelectItem value="nda">NDA</SelectItem>
                  <SelectItem value="sla">SLA</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>

              {/* Status */}
              <Select
                value={filters.status || 'all'}
                onValueChange={(value) => handleFilterChange('status', value === 'all' ? undefined : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="under_review">Under Review</SelectItem>
                  <SelectItem value="pending_approval">Pending Approval</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                  <SelectItem value="terminated">Terminated</SelectItem>
                  <SelectItem value="renewed">Renewed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>

              {/* Expiring Soon */}
              <Select
                value={filters.expiring_in_days?.toString() || 'all'}
                onValueChange={(value) => handleFilterChange('expiring_in_days', value === 'all' ? undefined : parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Expiry Filter" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Contracts</SelectItem>
                  <SelectItem value="30">Expiring in 30 days</SelectItem>
                  <SelectItem value="60">Expiring in 60 days</SelectItem>
                  <SelectItem value="90">Expiring in 90 days</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Contracts Table */}
        <Card>
          <CardHeader>
            <CardTitle>Contracts</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-gray-500">Loading contracts...</div>
            ) : contracts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No contracts found</div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Contract Number</TableHead>
                      <TableHead>Title</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Value</TableHead>
                      <TableHead>Effective Date</TableHead>
                      <TableHead>Expiry Date</TableHead>
                      <TableHead>Expiry Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {contracts.map((contract) => (
                      <TableRow key={contract.id}>
                        <TableCell className="font-medium">{contract.contract_number}</TableCell>
                        <TableCell>
                          <div className="max-w-xs truncate">{contract.title}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{contractService.getContractTypeLabel(contract.contract_type)}</Badge>
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={contract.status} />
                        </TableCell>
                        <TableCell>{contractService.formatCurrency(contract.contract_value, contract.currency)}</TableCell>
                        <TableCell>{contractService.formatDate(contract.effective_date)}</TableCell>
                        <TableCell>{contractService.formatDate(contract.expiry_date)}</TableCell>
                        <TableCell>
                          <ExpiryBadge contract={contract} />
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Link href={`/legal/contracts/${contract.id}`}>
                              <Button variant="ghost" size="sm">
                                <Eye className="h-4 w-4" />
                              </Button>
                            </Link>
                            <Link href={`/legal/contracts/${contract.id}/edit`}>
                              <Button variant="ghost" size="sm">
                                <Edit className="h-4 w-4" />
                              </Button>
                            </Link>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {pagination && pagination.total_pages > 1 && (
                  <div className="flex items-center justify-between mt-4">
                    <div className="text-sm text-gray-600">
                      Showing {((pagination.page - 1) * pagination.page_size) + 1} to {Math.min(pagination.page * pagination.page_size, pagination.total)} of {pagination.total} contracts
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={pagination.page === 1}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={pagination.page === pagination.total_pages}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function StatCard({ title, value, icon: Icon, color }: any) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    orange: 'bg-orange-100 text-orange-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          </div>
          <div className={`h-10 w-10 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function StatusBadge({ status }: { status: ContractStatus }) {
  const color = contractService.getContractStatusColor(status)
  const label = contractService.getContractStatusLabel(status)

  const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    gray: 'outline',
    blue: 'default',
    yellow: 'outline',
    green: 'default',
    red: 'destructive',
    purple: 'secondary',
  }

  return <Badge variant={variants[color] || 'outline'}>{label}</Badge>
}

function ExpiryBadge({ contract }: { contract: any }) {
  if (!contract.expiry_date) {
    return <Badge variant="outline">No Expiry</Badge>
  }

  if (contract.is_expired) {
    return <Badge variant="destructive">Expired</Badge>
  }

  if (contract.is_expiring_soon) {
    return (
      <Badge variant="outline" className="border-yellow-500 text-yellow-700">
        {contract.days_until_expiry} days left
      </Badge>
    )
  }

  return <Badge variant="outline">{contract.days_until_expiry} days</Badge>
}
