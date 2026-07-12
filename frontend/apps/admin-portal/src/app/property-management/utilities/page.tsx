'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Zap, Droplet, Flame } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { propertyService, type UtilityBill } from '@/services/property.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function UtilitiesPage() {
  const [page, setPage] = useState(1)
  const [utilityType, setUtilityType] = useState('')
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['utility-bills', page, utilityType, status],
    queryFn: () => propertyService.getUtilityBills({
      page,
      page_size: 20,
      utility_type: utilityType || undefined,
      payment_status: status || undefined,
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Utility Management</h1>
            <p className="text-gray-600 mt-1">Track electricity, water, and gas bills</p>
          </div>
          <Link href="/property-management/utilities/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Bill
            </Button>
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <select
            value={utilityType}
            onChange={(e) => setUtilityType(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="electricity">Electricity</option>
            <option value="water">Water</option>
            <option value="gas">Gas</option>
            <option value="sewage">Sewage</option>
            <option value="maintenance">Maintenance</option>
          </select>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>

        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Bill Number</TableHead>
                <TableHead>Property</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Month</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Consumption</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Paid</TableHead>
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
                data.data.data.items.map((bill: UtilityBill) => (
                  <TableRow key={bill.id}>
                    <TableCell className="font-mono text-sm">{bill.bill_number}</TableCell>
                    <TableCell>{bill.property_name}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getUtilityIcon(bill.utility_type)}
                        <span className="capitalize">{bill.utility_type}</span>
                      </div>
                    </TableCell>
                    <TableCell>{bill.bill_month}</TableCell>
                    <TableCell>{formatDate(bill.due_date)}</TableCell>
                    <TableCell>{bill.consumption_units ? `${bill.consumption_units} units` : '-'}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(bill.total_amount)}</TableCell>
                    <TableCell className="font-semibold text-green-600">{formatCurrency(bill.paid_amount)}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(bill.payment_status)}>{bill.payment_status}</Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    <Zap className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No utility bills found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} bills
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

function getUtilityIcon(type: string) {
  switch (type) {
    case 'electricity':
      return <Zap className="h-4 w-4 text-yellow-600" />
    case 'water':
      return <Droplet className="h-4 w-4 text-blue-600" />
    case 'gas':
      return <Flame className="h-4 w-4 text-orange-600" />
    default:
      return <Zap className="h-4 w-4 text-gray-600" />
  }
}

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    paid: 'bg-green-100 text-green-700',
    partial: 'bg-orange-100 text-orange-700',
    overdue: 'bg-red-100 text-red-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
