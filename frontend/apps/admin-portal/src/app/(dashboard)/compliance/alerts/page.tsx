'use client'

/**
 * Compliance Alerts Page
 * Manage and respond to compliance alerts
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  Clock,
  Search,
  XCircle,
} from 'lucide-react'
import { complianceService } from '@/services/compliance.service'
import { formatDate } from '@/lib/utils'
import type { ComplianceAlert } from '@/types/compliance.types'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'

export default function ComplianceAlertsPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('open')
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState<ComplianceAlert | null>(null)
  const [resolutionNotes, setResolutionNotes] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['compliance-alerts', page, statusFilter, severityFilter],
    queryFn: () =>
      complianceService.getAlerts({
        skip: (page - 1) * 20,
        limit: 20,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        severity: severityFilter !== 'all' ? severityFilter : undefined,
      }),
  })

  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: string) => complianceService.acknowledgeAlert(alertId),
    onSuccess: () => {
      toast({
        title: 'Alert Acknowledged',
        description: 'Alert has been acknowledged successfully',
      })
      queryClient.invalidateQueries({ queryKey: ['compliance-alerts'] })
    },
  })

  const resolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) =>
      complianceService.resolveAlert(id, notes),
    onSuccess: () => {
      toast({
        title: 'Alert Resolved',
        description: 'Alert has been resolved successfully',
      })
      setResolveDialogOpen(false)
      setSelectedAlert(null)
      setResolutionNotes('')
      queryClient.invalidateQueries({ queryKey: ['compliance-alerts'] })
    },
  })

  const handleAcknowledge = (alertId: string) => {
    acknowledgeMutation.mutate(alertId)
  }

  const handleOpenResolve = (alert: ComplianceAlert) => {
    setSelectedAlert(alert)
    setResolveDialogOpen(true)
  }

  const handleResolve = () => {
    if (selectedAlert && resolutionNotes.trim()) {
      resolveMutation.mutate({
        id: selectedAlert.id,
        notes: resolutionNotes,
      })
    } else {
      toast({
        title: 'Error',
        description: 'Please enter resolution notes',
        variant: 'destructive',
      })
    }
  }

  const getSeverityBadge = (severity: string) => {
    const colors = {
      low: 'bg-blue-100 text-blue-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    }
    const icons = {
      low: <AlertCircle className="h-3 w-3" />,
      medium: <AlertTriangle className="h-3 w-3" />,
      high: <AlertTriangle className="h-3 w-3" />,
      critical: <XCircle className="h-3 w-3" />,
    }
    return (
      <Badge className={colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        <span className="flex items-center gap-1">
          {icons[severity as keyof typeof icons]}
          {severity.toUpperCase()}
        </span>
      </Badge>
    )
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      open: 'bg-red-100 text-red-800',
      acknowledged: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      dismissed: 'bg-gray-100 text-gray-800',
    }
    const icons = {
      open: <AlertCircle className="h-3 w-3" />,
      acknowledged: <Clock className="h-3 w-3" />,
      resolved: <CheckCircle className="h-3 w-3" />,
      dismissed: <XCircle className="h-3 w-3" />,
    }
    return (
      <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        <span className="flex items-center gap-1">
          {icons[status as keyof typeof icons]}
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </Badge>
    )
  }

  if (isLoading) {
    return <ComplianceAlertsSkeleton />
  }

  const alerts = data?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Alerts</h1>
          <p className="text-muted-foreground">
            Monitor and respond to compliance alerts and notifications
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Alerts</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {alerts.filter((a: ComplianceAlert) => a.status === 'open').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {alerts.filter((a: ComplianceAlert) => a.status === 'acknowledged').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {alerts.filter((a: ComplianceAlert) => a.severity === 'critical').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {alerts.filter((a: ComplianceAlert) => a.is_overdue).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search alerts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="acknowledged">Acknowledged</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severity</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Alerts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Severity</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {alerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    No compliance alerts found
                  </TableCell>
                </TableRow>
              ) : (
                alerts.map((alert: ComplianceAlert) => (
                  <TableRow key={alert.id} className={alert.is_overdue ? 'bg-red-50' : ''}>
                    <TableCell>{getSeverityBadge(alert.severity)}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{alert.alert_type}</div>
                        <div className="text-xs text-muted-foreground">
                          {alert.alert_category}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="max-w-md">
                        <div className="text-sm">{alert.alert_message}</div>
                        {alert.is_overdue && (
                          <Badge variant="destructive" className="mt-1">
                            OVERDUE
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(alert.status)}</TableCell>
                    <TableCell>{formatDate(alert.created_at)}</TableCell>
                    <TableCell>
                      {alert.due_date ? formatDate(alert.due_date) : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {alert.status === 'open' && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleAcknowledge(alert.id)}
                              disabled={acknowledgeMutation.isPending}
                            >
                              Acknowledge
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => handleOpenResolve(alert)}
                            >
                              Resolve
                            </Button>
                          </>
                        )}
                        {alert.status === 'acknowledged' && (
                          <Button
                            size="sm"
                            onClick={() => handleOpenResolve(alert)}
                          >
                            Resolve
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data && data.total > 20 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, data.total)} of {data.total} alerts
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page * 20 >= data.total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Resolve Dialog */}
      <Dialog open={resolveDialogOpen} onOpenChange={setResolveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolve Alert</DialogTitle>
            <DialogDescription>
              Provide resolution notes for this alert
            </DialogDescription>
          </DialogHeader>
          {selectedAlert && (
            <div className="space-y-4">
              <div className="rounded-lg bg-gray-50 p-4">
                <div className="flex items-start gap-2 mb-2">
                  {getSeverityBadge(selectedAlert.severity)}
                  <Badge>{selectedAlert.alert_type}</Badge>
                </div>
                <p className="text-sm">{selectedAlert.alert_message}</p>
              </div>
              <div>
                <Label htmlFor="resolution-notes">Resolution Notes *</Label>
                <Textarea
                  id="resolution-notes"
                  placeholder="Enter resolution details..."
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  rows={4}
                  className="mt-2"
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setResolveDialogOpen(false)
                setSelectedAlert(null)
                setResolutionNotes('')
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleResolve}
              disabled={resolveMutation.isPending || !resolutionNotes.trim()}
            >
              {resolveMutation.isPending ? 'Resolving...' : 'Resolve Alert'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function ComplianceAlertsSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-12 w-96" />
      <div className="grid gap-4 md:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardContent className="pt-6">
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
