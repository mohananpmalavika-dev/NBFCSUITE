'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, Mail, MessageSquare, CheckCircle, Trash2, Eye, AlertCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { notificationService } from '@/services/notification.service'
import { formatDateTime, getStatusColor } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import type { Notification } from '@/types'

export default function NotificationsPage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [channelFilter, setChannelFilter] = useState<string>('')

  const queryClient = useQueryClient()
  const { toast } = useToast()

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', page, statusFilter, channelFilter],
    queryFn: () => notificationService.getNotifications({ 
      page, 
      page_size: 20,
      status: statusFilter || undefined,
      channel: channelFilter || undefined
    }),
  })

  const markAsReadMutation = useMutation({
    mutationFn: (id: string) => notificationService.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      toast({
        title: 'Marked as read',
        description: 'Notification has been marked as read',
      })
    },
  })

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationService.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      toast({
        title: 'All marked as read',
        description: 'All notifications have been marked as read',
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => notificationService.deleteNotification(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      toast({
        title: 'Deleted',
        description: 'Notification has been deleted',
      })
    },
  })

  // Calculate stats
  const stats = data?.data?.items?.reduce(
    (acc, notification: Notification) => {
      if (notification.status === 'pending') acc.pending++
      else if (notification.status === 'sent') acc.sent++
      else if (notification.status === 'delivered') acc.delivered++
      else if (notification.status === 'failed') acc.failed++
      
      return acc
    },
    { pending: 0, sent: 0, delivered: 0, failed: 0 }
  ) || { pending: 0, sent: 0, delivered: 0, failed: 0 }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
            <p className="text-gray-600 mt-1">View and manage system notifications</p>
          </div>
          <Button
            onClick={() => markAllAsReadMutation.mutate()}
            disabled={markAllAsReadMutation.isPending}
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Mark All Read
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Pending"
            value={stats.pending}
            icon={Bell}
            color="blue"
          />
          <StatCard
            label="Sent"
            value={stats.sent}
            icon={Mail}
            color="purple"
          />
          <StatCard
            label="Delivered"
            value={stats.delivered}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            label="Failed"
            value={stats.failed}
            icon={AlertCircle}
            color="red"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Channels</option>
            <option value="SMS">SMS</option>
            <option value="Email">Email</option>
            <option value="WhatsApp">WhatsApp</option>
          </select>
        </div>

        {/* Notifications Tabs */}
        <Tabs value={statusFilter} onValueChange={setStatusFilter}>
          <TabsList>
            <TabsTrigger value="">All</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="sent">Sent</TabsTrigger>
            <TabsTrigger value="delivered">Delivered</TabsTrigger>
            <TabsTrigger value="failed">Failed</TabsTrigger>
          </TabsList>

          <TabsContent value={statusFilter} className="space-y-4">
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Card key={i}>
                    <CardContent className="pt-6">
                      <Skeleton className="h-20 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : data?.data?.items && data.data.items.length > 0 ? (
              <>
                <div className="space-y-3">
                  {data.data.items.map((notification: Notification) => (
                    <NotificationCard
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={() => markAsReadMutation.mutate(notification.id)}
                      onDelete={() => deleteMutation.mutate(notification.id)}
                    />
                  ))}
                </div>

                {/* Pagination */}
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.metadata?.total || 0)} of {data.metadata?.total || 0} notifications
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
              </>
            ) : (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center text-gray-500">
                    <Bell className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-lg font-medium">No notifications found</p>
                    <p className="text-sm mt-1">You're all caught up!</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function NotificationCard({ 
  notification, 
  onMarkAsRead, 
  onDelete 
}: { 
  notification: Notification
  onMarkAsRead: () => void
  onDelete: () => void
}) {
  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'Email':
        return Mail
      case 'SMS':
        return MessageSquare
      case 'WhatsApp':
        return MessageSquare
      default:
        return Bell
    }
  }

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'Email':
        return 'bg-blue-100 text-blue-700'
      case 'SMS':
        return 'bg-green-100 text-green-700'
      case 'WhatsApp':
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700'
      case 'low':
        return 'bg-blue-100 text-blue-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const Icon = getChannelIcon(notification.channel)

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className={`h-12 w-12 rounded-lg ${getChannelColor(notification.channel)} flex items-center justify-center flex-shrink-0`}>
            <Icon className="h-6 w-6" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4 mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge className={getChannelColor(notification.channel)}>
                    {notification.channel}
                  </Badge>
                  <Badge className={getPriorityColor(notification.priority)}>
                    {notification.priority}
                  </Badge>
                  <Badge className={getStatusColor(notification.status)}>
                    {notification.status}
                  </Badge>
                </div>
                {notification.subject && (
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {notification.subject}
                  </h3>
                )}
              </div>
              <p className="text-xs text-gray-500 whitespace-nowrap">
                {formatDateTime(notification.scheduled_at || notification.sent_at || new Date().toISOString())}
              </p>
            </div>

            <p className="text-sm text-gray-600 mb-2">
              To: {notification.recipient}
            </p>

            <p className="text-sm text-gray-700 line-clamp-2 mb-3">
              {notification.content}
            </p>

            {notification.error_message && (
              <div className="bg-red-50 border border-red-200 rounded p-2 mb-3">
                <p className="text-xs text-red-700">
                  <strong>Error:</strong> {notification.error_message}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-2">
              {notification.status === 'pending' && (
                <Button size="sm" variant="ghost" onClick={onMarkAsRead}>
                  <Eye className="h-4 w-4 mr-1" />
                  Mark Read
                </Button>
              )}
              <Button size="sm" variant="ghost" className="text-red-600" onClick={onDelete}>
                <Trash2 className="h-4 w-4 mr-1" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function StatCard({ 
  label, 
  value, 
  icon: Icon,
  color = 'blue'
}: { 
  label: string
  value: number
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
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
