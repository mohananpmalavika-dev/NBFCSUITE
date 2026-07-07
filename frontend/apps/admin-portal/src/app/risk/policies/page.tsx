'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Eye, Edit, Trash2, CheckCircle, XCircle, FileText } from 'lucide-react'
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
import { riskService } from '@/services/risk.service'
import { formatDate } from '@/lib/utils'
import { toast } from 'sonner'

export default function CreditPoliciesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isActiveFilter, setIsActiveFilter] = useState<boolean | undefined>(undefined)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['credit-policies', page, search, isActiveFilter],
    queryFn: () => riskService.getCreditPolicies({
      page,
      page_size: 20,
      is_active: isActiveFilter,
    }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => riskService.deleteCreditPolicy(id),
    onSuccess: () => {
      toast.success('Credit policy deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['credit-policies'] })
    },
    onError: () => {
      toast.error('Failed to delete credit policy')
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete the policy "${name}"?`)) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Credit Policies</h1>
            <p className="text-gray-600 mt-1">Define and manage credit policy rules</p>
          </div>
          <Link href="/risk/policies/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Policy
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search policies..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={isActiveFilter === undefined ? 'all' : isActiveFilter ? 'active' : 'inactive'}
            onChange={(e) => setIsActiveFilter(
              e.target.value === 'all' ? undefined : e.target.value === 'active'
            )}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="all">All Policies</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard label="Total Policies" value={data?.total || 0} />
          <StatCard label="Active" value={data?.items.filter(p => p.is_active).length || 0} color="green" />
          <StatCard label="Inactive" value={data?.items.filter(p => !p.is_active).length || 0} color="gray" />
          <StatCard label="This Month" value={0} color="blue" />
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Policy Code</TableHead>
                <TableHead>Policy Name</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Products</TableHead>
                <TableHead>Min CIBIL</TableHead>
                <TableHead>Max DTI</TableHead>
                <TableHead>Loan Range</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Effective From</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  </TableRow>
                ))
              ) : data?.items && data.items.length > 0 ? (
                data.items.map((policy) => (
                  <TableRow key={policy.id}>
                    <TableCell className="font-medium">{policy.policy_code}</TableCell>
                    <TableCell>{policy.policy_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{policy.policy_version}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {policy.product_types.slice(0, 2).join(', ')}
                        {policy.product_types.length > 2 && ` +${policy.product_types.length - 2}`}
                      </div>
                    </TableCell>
                    <TableCell>{policy.min_cibil_score}</TableCell>
                    <TableCell>{policy.max_debt_to_income_ratio}%</TableCell>
                    <TableCell className="text-sm">
                      ₹{(policy.min_loan_amount / 100000).toFixed(1)}L - ₹{(policy.max_loan_amount / 100000).toFixed(1)}L
                    </TableCell>
                    <TableCell>
                      {policy.is_active ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Active
                        </Badge>
                      ) : (
                        <Badge variant="secondary">
                          <XCircle className="h-3 w-3 mr-1" />
                          Inactive
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>{formatDate(policy.effective_from)}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            Actions
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <Link href={`/risk/policies/${policy.id}`}>
                            <DropdownMenuItem>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                          </Link>
                          <Link href={`/risk/policies/${policy.id}/edit`}>
                            <DropdownMenuItem>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit Policy
                            </DropdownMenuItem>
                          </Link>
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => handleDelete(policy.id, policy.policy_name)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={10} className="text-center py-8 text-gray-500">
                    <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No credit policies found</p>
                    <Link href="/risk/policies/new">
                      <Button variant="link" className="mt-2">
                        Create your first policy
                      </Button>
                    </Link>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data && data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of {data.total} policies
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page * 20 >= data.total}
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

function StatCard({ label, value, color = 'blue' }: { label: string; value: number; color?: string }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    gray: 'bg-gray-100 text-gray-600',
  }

  return (
    <div className="bg-white rounded-lg border p-4">
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colors[color as keyof typeof colors]}`}>{value}</p>
    </div>
  )
}
