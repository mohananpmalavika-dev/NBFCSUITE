'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Eye, FileText, Calendar } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { propertyService, type Lease } from '@/services/property.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function LeasesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['leases', page, search, status],
    queryFn: () => propertyService.getLeases({
      page,
      page_size: 20,
      search: search || undefined,
      status: status || undefined,
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Lease Agreements</h1>
            <p className="text-gray-600 mt-1">Manage lease agreements and tenant contracts</p>
          </div>
          <Link href="/property-management/leases/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Lease
            </Button>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search leases..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="terminated">Terminated</option>
          </select>
        </div>

        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Lease Number</TableHead>
                <TableHead>Tenant</TableHead>
                <TableHead>Property</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Monthly Rent</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    {[...Array(9)].map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data?.data?.data?.items && data.data.data.items.length > 0 ? (
                data.data.data.items.map((lease: Lease) => (
                  <TableRow key={lease.id}>
                    <TableCell className="font-mono text-sm">{lease.lease_number}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{lease.lessee_name}</p>
                        <p className="text-sm text-gray-500">{lease.lessee_contact}</p>
                      </div>
                    </TableCell>
                    <TableCell>{lease.property_name}</TableCell>
                    <TableCell className="capitalize">{lease.lease_type}</TableCell>
                    <TableCell>{formatDate(lease.lease_start_date)}</TableCell>
                    <TableCell>{formatDate(lease.lease_end_date)}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(lease.total_monthly_payment)}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(lease.status)}>{lease.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/property-management/leases/${lease.id}`}>
                        <Button variant="ghost" size="icon">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    <FileText className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No leases found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} leases
              </p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
                  Previous
                </Button>
                <Button variant="outline" size="sm" disabled={page >= (data.data.data.total_pages || 1)} onClick={() => setPage(page + 1)}>
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

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    active: 'bg-green-100 text-green-700',
    expired: 'bg-yellow-100 text-yellow-700',
    terminated: 'bg-red-100 text-red-700',
    renewed: 'bg-blue-100 text-blue-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
