'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react'
import Link from 'next/link'
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
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Skeleton } from '@/components/ui/skeleton'
import { riskService } from '@/services/risk.service'
import { formatDate } from '@/lib/utils'
import { toast } from 'sonner'
import { Bar, Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default function EarlyWarningAlertsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [severityFilter, setSeverityFilter] = useState<string | undefined>()
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>()
  const [selectedAlert, setSelectedAlert] = useState<any>(null)
  const [showActionModal, setShowActionModal] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['ews-alerts', page, search, statusFilter, severityFilter, categoryFilter],
    queryFn: () => riskService.getEWSAlerts({
      page,
      page_size: 20,
      status: statusFilter,
      severity: severityFilter,
      category: categoryFilter,
    }),
  })

  const { data: stats } = useQuery({
    queryKey: ['ews-alert-stats'],
    queryFn: async () => {
      // Mock stats - replace with actual API call
      return {
        total_alerts: 156,
        open_alerts: 45,
        critical_alerts: 12,
        resolved_today: 8,
        alerts_by_category: {
          'Payment Behavior': 35,
          'Credit Utilization': 28,
          'Financial Health': 22,
          'External Events': 15,
          'Compliance': 10,
        },
        trend_data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          new_alerts: [8, 12, 10, 15, 9, 6, 7],
          resolved: [5, 8, 7, 10, 6, 4, 5],
        },
      }
    },
  })

  const actionMutation = useMutation({
    mutationFn: ({ alertId, action, remarks }: any) =>
      riskService.performAlertAction(alertId, { action_taken: action, remarks }),
    onSuccess: () => {
      toast.success('Alert action performed successfully')
      queryClient.invalidateQueries({ queryKey: ['ews-alerts'] })
      setShowActionModal(false)
      setSelectedAlert(null)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to perform action')
    },
  })

  const getSeverityBadge = (severity: string) => {
    const variants: any = {
      critical: { className: 'bg-red-600 text-white', label: 'Critical' },
      high: { className: 'bg-orange-500 text-white', label: 'High' },
      medium: { className: 'bg-yellow-500 text-white', label: 'Medium' },
      low: { className: 'bg-blue-500 text-white', label: 'Low' },
    }
    const variant = variants[severity] || variants.medium
    return <Badge className={variant.className}>{variant.label}</Badge>
  }

  const getStatusBadge = (status: string) => {
    const variants: any = {
      open: { className: 'bg-blue-100 text-blue-800', label: 'Open' },
      acknowledged: { className: 'bg-yellow-100 text-yellow-800', label: 'Acknowledged' },
      in_progress: { className: 'bg-purple-100 text-purple-800', label: 'In Progress' },
      resolved: { className: 'bg-green-100 text-green-800', label: 'Resolved' },
      false_positive: { className: 'bg-gray-100 text-gray-800', label: 'False Positive' },
    }
    const variant = variants[status] || variants.open
    return <Badge className={variant.className}>{variant.label}</Badge>
  }

  const handleAction = (alert: any) => {
    setSelectedAlert(alert)
    setShowActionModal(true)
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Early Warning Alerts</h1>
            <p className="text-gray-600 mt-1">Monitor and manage early warning signals</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Alerts"
            value={stats?.total_alerts || 0}
            icon={AlertTriangle}
            color="blue"
          />
          <StatCard
            label="Open Alerts"
            value={stats?.open_alerts || 0}
            icon={Clock}
            color="orange"
          />
          <StatCard
            label="Critical"
            value={stats?.critical_alerts || 0}
            icon={AlertTriangle}
            color="red"
          />
          <StatCard
            label="Resolved Today"
            value={stats?.resolved_today || 0}
            icon={CheckCircle}
            color="green"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Alerts by Category */}
          <Card>
            <CardHeader>
              <CardTitle>Alerts by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Bar
                  data={{
                    labels: Object.keys(stats?.alerts_by_category || {}),
                    datasets: [{
                      label: 'Number of Alerts',
                      data: Object.values(stats?.alerts_by_category || {}),
                      backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    }],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                    },
                    scales: {
                      y: { beginAtZero: true },
                    },
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* Alert Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Alert Trend (Last 7 Days)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Line
                  data={{
                    labels: stats?.trend_data.labels || [],
                    datasets: [
                      {
                        label: 'New Alerts',
                        data: stats?.trend_data.new_alerts || [],
                        borderColor: 'rgb(239, 68, 68)',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4,
                      },
                      {
                        label: 'Resolved',
                        data: stats?.trend_data.resolved || [],
                        borderColor: 'rgb(16, 185, 129)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' },
                    },
                    scales: {
                      y: { beginAtZero: true },
                    },
                  }}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px] relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search alerts..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={statusFilter || ''}
            onChange={(e) => setStatusFilter(e.target.value || undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="false_positive">False Positive</option>
          </select>
          <select
            value={severityFilter || ''}
            onChange={(e) => setSeverityFilter(e.target.value || undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={categoryFilter || ''}
            onChange={(e) => setCategoryFilter(e.target.value || undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Categories</option>
            <option value="payment_behavior">Payment Behavior</option>
            <option value="credit_utilization">Credit Utilization</option>
            <option value="financial_health">Financial Health</option>
            <option value="external_events">External Events</option>
            <option value="compliance">Compliance</option>
          </select>
        </div>

        {/* Alerts Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Alert Number</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Account</TableHead>
                <TableHead>Signal Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Detected Value</TableHead>
                <TableHead>Threshold</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Alert Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    {[...Array(11)].map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data?.items && data.items.length > 0 ? (
                data.items.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell className="font-medium">
                      <Link href={`/risk/alerts/${alert.id}`} className="text-blue-600 hover:underline">
                        EWS-{alert.id.toString().padStart(6, '0')}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Link href={`/customers/${alert.customer_id}`} className="text-blue-600 hover:underline">
                        Customer #{alert.customer_id}
                      </Link>
                    </TableCell>
                    <TableCell>
                      {alert.loan_id ? (
                        <Link href={`/loans/${alert.loan_id}`} className="text-blue-600 hover:underline">
                          LN-{alert.loan_id}
                        </Link>
                      ) : '-'}
                    </TableCell>
                    <TableCell>{alert.signal_name || 'N/A'}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {alert.category?.replace('_', ' ') || 'General'}
                      </Badge>
                    </TableCell>
                    <TableCell>{getSeverityBadge(alert.severity)}</TableCell>
                    <TableCell className="font-medium">{alert.detected_value || 'N/A'}</TableCell>
                    <TableCell>{alert.threshold_value || 'N/A'}</TableCell>
                    <TableCell>{getStatusBadge(alert.status)}</TableCell>
                    <TableCell>{formatDate(alert.alert_date)}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAction(alert)}
                        disabled={alert.status === 'resolved' || alert.status === 'false_positive'}
                      >
                        Take Action
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={11} className="text-center py-8 text-gray-500">
                    No alerts found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data && data.items.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of {data.total} alerts
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

      {/* Action Modal */}
      {showActionModal && selectedAlert && (
        <AlertActionModal
          alert={selectedAlert}
          onClose={() => {
            setShowActionModal(false)
            setSelectedAlert(null)
          }}
          onSubmit={(data) => {
            actionMutation.mutate({ alertId: selectedAlert.id, ...data })
          }}
          isPending={actionMutation.isPending}
        />
      )}
    </DashboardLayout>
  )
}

function StatCard({ label, value, icon: Icon, color = 'blue' }: any) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{label}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color as keyof typeof colors]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function AlertActionModal({ alert, onClose, onSubmit, isPending }: any) {
  const [formData, setFormData] = useState({
    action: '',
    remarks: '',
    assigned_to: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      action: formData.action,
      remarks: formData.remarks,
    })
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Take Action on Alert</DialogTitle>
        </DialogHeader>

        {/* Alert Summary */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-2">
          <div className="flex justify-between text-sm">
            <span className="font-medium">Alert Number:</span>
            <span>EWS-{alert.id.toString().padStart(6, '0')}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="font-medium">Signal:</span>
            <span>{alert.signal_name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="font-medium">Customer:</span>
            <span>Customer #{alert.customer_id}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="font-medium">Detected Value:</span>
            <span className="text-red-600 font-medium">{alert.detected_value}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="font-medium">Threshold:</span>
            <span>{alert.threshold_value}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">Action *</label>
            <select
              value={formData.action}
              onChange={(e) => setFormData({ ...formData, action: e.target.value })}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              required
            >
              <option value="">Select Action</option>
              <option value="acknowledge">Acknowledge</option>
              <option value="assign">Assign for Review</option>
              <option value="escalate">Escalate</option>
              <option value="resolve">Resolve</option>
              <option value="mark_false_positive">Mark as False Positive</option>
            </select>
          </div>

          {formData.action === 'assign' && (
            <div>
              <label className="text-sm font-medium mb-1 block">Assign To</label>
              <Input
                value={formData.assigned_to}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                placeholder="User ID or Email"
              />
            </div>
          )}

          <div>
            <label className="text-sm font-medium mb-1 block">Remarks *</label>
            <textarea
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              placeholder="Enter your remarks..."
              required
            />
          </div>

          {/* Action History */}
          {alert.action_history && alert.action_history.length > 0 && (
            <div>
              <label className="text-sm font-medium mb-2 block">Action History</label>
              <div className="border rounded-md p-3 max-h-40 overflow-y-auto space-y-2">
                {alert.action_history.map((action: any, idx: number) => (
                  <div key={idx} className="text-sm border-l-2 border-blue-500 pl-3">
                    <div className="flex justify-between">
                      <span className="font-medium">{action.action_taken}</span>
                      <span className="text-gray-500 text-xs">{formatDate(action.action_date)}</span>
                    </div>
                    <p className="text-gray-600 text-xs mt-1">{action.remarks}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Submitting...' : 'Submit Action'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
