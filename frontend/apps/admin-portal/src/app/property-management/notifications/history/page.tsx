'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bell, Mail, MessageSquare, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { notificationService, type NotificationLog } from '@/services/notification.service'
import { formatDate } from '@/lib/utils'

export default function NotificationHistoryPage() {
  const [page, setPage] = useState(1)
  const [channel, setChannel] = useState('')
  const [status, setStatus] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['notification-logs', page, channel, status],
    queryFn: () => notificationService.getLogs({
      page,
      page_size: 20,
      channel: channel || undefined,
      status: status || undefined,
    }),
  })

  const { data: statsData } = useQuery({
    queryKey: ['notification-statistics'],
    queryFn: () => notificationService.getStatistics(),
  })

  const stats = statsData?.data?.data

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Notification History</h1>
          <p className="text-gray-600 mt-1">View all sent notifications and delivery status</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Sent"
            value={stats?.total_notifications || 0}
            icon={Bell}
            color="blue"
          />
          <StatCard
            label="Delivered"
            value={stats?.by_status?.sent || 0}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            label="Failed"
            value={stats?.by_status?.failed || 0}
            icon={XCircle}
            color="red"
          />
          <StatCard
            label="Pending"
            value={stats?.by_status?.pending || 0}
            icon={Clock}
            color="yellow"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <select
            value={channel}
            onChange={(e) => setChannel(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Channels</option>
            <option value="rent_due_reminder">Rent Due Reminder</option>
            <option value="lease_expiry_alert">Lease Expiry Alert</option>
            <option value="payment_received">Payment Received</option>
            <option value="maintenance_update">Maintenance Update</option>
            <option value="payment_overdue">Payment Overdue</option>
          </select>

          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="sent">Sent</option>
            <option value="delivered">Delivered</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>

        {/* Notification List */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Channel</TableHead>
                <TableHead>Recipient</TableHead>
                <TableHead>Subject/Message</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Sent At</TableHead>
                <TableHead>Error</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    {[...Array(7)].map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data?.data?.data?.items && data.data.data.items.length > 0 ? (
                data.data.data.items.map((log: NotificationLog) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {log.notification_type === 'email' ? (
                          <Mail className="h-4 w-4 text-blue-600" />
                        ) : (
                          <MessageSquare className="h-4 w-4 text-green-600" />
                        )}
                        <span className="capitalize">{log.notification_type}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {log.channel.replace(/_/g, ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div>
                        {log.recipient_name && <p className="font-medium">{log.recipient_name}</p>}
                        <p className="text-sm text-gray-500">
                          {log.recipient_email || log.recipient_phone}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="max-w-xs truncate" title={log.subject}>
                        {log.subject || '-'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(log.status)}>
                        {log.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {log.sent_at ? formatDate(log.sent_at) : '-'}
                    </TableCell>
                    <TableCell>
                      {log.error_message ? (
                        <div className="flex items-center gap-1 text-red-600">
                          <AlertCircle className="h-4 w-4" />
                          <span className="text-xs truncate max-w-[150px]" title={log.error_message}>
                            {log.error_message}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                    <Bell className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p>No notifications found</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data?.data?.data && data.data.data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.data.data.total || 0)} of {data.data.data.total || 0} notifications
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
  color
}: {
  label: string
  value: string | number
  icon: any
  color: string
}) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    yellow: 'bg-yellow-100 text-yellow-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{label}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
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
    sent: 'bg-green-100 text-green-700',
    delivered: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700',
    pending: 'bg-yellow-100 text-yellow-700',
    read: 'bg-purple-100 text-purple-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
