'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Wrench, AlertCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { propertyService, type PropertyMaintenance } from '@/services/property.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function MaintenancePage() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')
  const [priority, setPriority] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['maintenance-requests', page, status, priority],
    queryFn: () => propertyService.getMaintenanceRequests({
      page,
      page_size: 20,
      status: status || undefined,
      priority: priority || undefined,
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Property Maintenance</h1>
            <p className="text-gray-600 mt-1">Track maintenance requests and repairs</p>
          </div>
          <Link href="/property-management/maintenance/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Request
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
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ticket Number</TableHead>
                <TableHead>Property</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Issue</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Request Date</TableHead>
                <TableHead>Estimated Cost</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    {[...Array(8)].map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data?.data?.data?.items && data.data.data.items.length > 0 ? (
                data.data.data.items.map((request: PropertyMaintenance) => (
                  <TableRow key={request.id}>
                    <TableCell className="font-mono text-sm">{request.ticket_number}</TableCell>
                    <TableCell>{request.property_name}</TableCell>
                    <TableCell className="capitalize">{request.maintenance_type}</TableCell>
                    <TableCell>
                      <div className="max-w-xs truncate" title={request.issue_description}>
                        {request.issue_description}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getPriorityColor(request.priority)}>
                        {request.priority === 'urgent' && <AlertCircle className="h-3 w-3 mr-1" />}
                        {request.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(request.status)}>{request.status}</Badge>
                    </TableCell>
                    <TableCell>{formatDate(request.request_date)}</TableCell>
                    <TableCell>
                      {request.estimated_cost ? formatCurrency(request.estimated_cost) : '-'}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                    <Wrench className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No maintenance requests found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} requests
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

function getPriorityColor(priority: string) {
  const colors: Record<string, string> = {
    low: 'bg-gray-100 text-gray-700',
    medium: 'bg-blue-100 text-blue-700',
    high: 'bg-orange-100 text-orange-700',
    urgent: 'bg-red-100 text-red-700',
  }
  return colors[priority] || 'bg-gray-100 text-gray-700'
}

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    open: 'bg-yellow-100 text-yellow-700',
    assigned: 'bg-blue-100 text-blue-700',
    in_progress: 'bg-purple-100 text-purple-700',
    completed: 'bg-green-100 text-green-700',
    cancelled: 'bg-gray-100 text-gray-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
