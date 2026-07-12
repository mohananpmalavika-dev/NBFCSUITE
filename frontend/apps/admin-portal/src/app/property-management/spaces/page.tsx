'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, LayoutGrid } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { propertyService, type PropertySpace } from '@/services/property.service'
import { formatCurrency } from '@/lib/utils'

export default function SpacesPage() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['property-spaces', page, status],
    queryFn: () => propertyService.getPropertySpaces({
      page,
      page_size: 20,
      status: status || undefined,
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Space Allocation</h1>
            <p className="text-gray-600 mt-1">Manage property spaces and units</p>
          </div>
          <Link href="/property-management/spaces/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Space
            </Button>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="available">Available</option>
            <option value="occupied">Occupied</option>
            <option value="reserved">Reserved</option>
            <option value="under_maintenance">Under Maintenance</option>
          </select>
        </div>

        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Space Code</TableHead>
                <TableHead>Space Name</TableHead>
                <TableHead>Property</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Floor</TableHead>
                <TableHead>Area</TableHead>
                <TableHead>Base Rent</TableHead>
                <TableHead>Furnishing</TableHead>
                <TableHead>Status</TableHead>
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
                data.data.data.items.map((space: PropertySpace) => (
                  <TableRow key={space.id}>
                    <TableCell className="font-mono text-sm">{space.space_code}</TableCell>
                    <TableCell className="font-medium">{space.space_name}</TableCell>
                    <TableCell>{space.property_name}</TableCell>
                    <TableCell className="capitalize">{space.space_type}</TableCell>
                    <TableCell>{space.floor_number || '-'}</TableCell>
                    <TableCell>{space.area} {space.area_unit}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(space.base_rent)}</TableCell>
                    <TableCell className="capitalize">{space.furnishing_status || '-'}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(space.status)}>{space.status}</Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    <LayoutGrid className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No spaces found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} spaces
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
    available: 'bg-green-100 text-green-700',
    occupied: 'bg-blue-100 text-blue-700',
    reserved: 'bg-yellow-100 text-yellow-700',
    under_maintenance: 'bg-red-100 text-red-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
