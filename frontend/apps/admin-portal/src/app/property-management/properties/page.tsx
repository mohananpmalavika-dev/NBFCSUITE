'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, Filter, Eye, Edit, Trash2, Building2, MapPin, TrendingUp } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
import { propertyService, type Property } from '@/services/property.service'
import { formatCurrency } from '@/lib/utils'

export default function PropertiesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [propertyType, setPropertyType] = useState('')
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['properties', page, search, propertyType, status],
    queryFn: () => propertyService.getProperties({
      page,
      page_size: 20,
      search: search || undefined,
      property_type: propertyType || undefined,
      status: status || undefined,
    }),
  })

  const { data: statsData } = useQuery({
    queryKey: ['property-statistics'],
    queryFn: () => propertyService.getPropertyStatistics(),
  })

  const stats = statsData?.data?.data

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Property Master</h1>
            <p className="text-gray-600 mt-1">Manage all properties and real estate assets</p>
          </div>
          <Link href="/property-management/properties/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Property
            </Button>
          </Link>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Properties"
            value={stats?.total_properties || 0}
            icon={Building2}
            color="blue"
          />
          <StatCard
            label="Active Properties"
            value={stats?.properties_by_status?.active || 0}
            icon={Building2}
            color="green"
          />
          <StatCard
            label="Occupied"
            value={stats?.properties_by_occupancy?.occupied || 0}
            icon={MapPin}
            color="purple"
          />
          <StatCard
            label="Total Value"
            value={formatCurrency(stats?.total_property_value || 0)}
            icon={TrendingUp}
            color="green"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by name, code, address..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={propertyType}
            onChange={(e) => setPropertyType(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="office">Office</option>
            <option value="residential">Residential</option>
            <option value="commercial">Commercial</option>
            <option value="warehouse">Warehouse</option>
            <option value="land">Land</option>
          </select>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="under_maintenance">Under Maintenance</option>
          </select>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Property Code</TableHead>
                <TableHead>Property Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Total Area</TableHead>
                <TableHead>Ownership</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Occupancy</TableHead>
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
                data.data.data.items.map((property: Property) => (
                  <TableRow key={property.id}>
                    <TableCell className="font-mono text-sm">{property.property_code}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{property.property_name}</p>
                        <p className="text-sm text-gray-500">{property.address_line1}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {property.property_type}
                      </Badge>
                    </TableCell>
                    <TableCell>{property.city}, {property.state}</TableCell>
                    <TableCell>{property.total_area} {property.area_unit}</TableCell>
                    <TableCell className="capitalize">{property.ownership_type}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(property.status)}>
                        {property.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getOccupancyColor(property.occupancy_status)}>
                        {property.occupancy_status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <Link href={`/property-management/properties/${property.id}`}>
                            <DropdownMenuItem>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                          </Link>
                          <Link href={`/property-management/properties/${property.id}/edit`}>
                            <DropdownMenuItem>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                          </Link>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    <Building2 className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No properties found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} properties
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
                  disabled={page >= (data.data.data.total_pages || 1)}
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
  color?: 'blue' | 'green' | 'yellow' | 'purple'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600',
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

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    inactive: 'bg-gray-100 text-gray-700',
    under_maintenance: 'bg-yellow-100 text-yellow-700',
    under_construction: 'bg-blue-100 text-blue-700',
    sold: 'bg-red-100 text-red-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}

function getOccupancyColor(status: string) {
  const colors: Record<string, string> = {
    vacant: 'bg-gray-100 text-gray-700',
    occupied: 'bg-green-100 text-green-700',
    partially_occupied: 'bg-yellow-100 text-yellow-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
