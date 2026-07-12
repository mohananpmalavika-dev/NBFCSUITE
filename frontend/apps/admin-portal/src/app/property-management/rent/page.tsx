'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Plus, Search, DollarSign, AlertCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { propertyService, type RentPayment } from '@/services/property.service'
import { formatCurrency, formatDate } from '@/lib/utils'

export default function RentCollectionPage() {
  const [page, setPage] = useState(1)
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['rent-payments', page, status],
    queryFn: () => propertyService.getRentPayments({
      page,
      page_size: 20,
      payment_status: status || undefined,
    }),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Rent Collection</h1>
            <p className="text-gray-600 mt-1">Track and manage rent payments</p>
          </div>
          <Link href="/property-management/rent/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Record Payment
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
            <option value="pending">Pending</option>
            <option value="partial">Partial</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>

        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Payment Number</TableHead>
                <TableHead>Tenant</TableHead>
                <TableHead>Month</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Paid</TableHead>
                <TableHead>Outstanding</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Overdue Days</TableHead>
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
                data.data.data.items.map((payment: RentPayment) => (
                  <TableRow key={payment.id}>
                    <TableCell className="font-mono text-sm">{payment.payment_number}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{payment.lessee_name}</p>
                        <p className="text-sm text-gray-500">{payment.lease_number}</p>
                      </div>
                    </TableCell>
                    <TableCell>{payment.payment_month}</TableCell>
                    <TableCell>{formatDate(payment.due_date)}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(payment.total_amount)}</TableCell>
                    <TableCell className="font-semibold text-green-600">{formatCurrency(payment.paid_amount)}</TableCell>
                    <TableCell className="font-semibold text-red-600">{formatCurrency(payment.outstanding_amount)}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(payment.payment_status)}>{payment.payment_status}</Badge>
                    </TableCell>
                    <TableCell>
                      {payment.days_overdue > 0 ? (
                        <span className="text-red-600 flex items-center gap-1">
                          <AlertCircle className="h-4 w-4" />
                          {payment.days_overdue} days
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    <DollarSign className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No rent payments found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} payments
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
    pending: 'bg-yellow-100 text-yellow-700',
    partial: 'bg-orange-100 text-orange-700',
    paid: 'bg-green-100 text-green-700',
    overdue: 'bg-red-100 text-red-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
