'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, AlertTriangle, CheckCircle2, X } from 'lucide-react'
import { almService } from '@/services/alm.service'
import { toast } from 'sonner'

const MOCK_ALERTS = [
  { id: 1, alert_type: 'ratio_breach', severity: 'high', title: 'LCR Below Threshold', description: 'Liquidity Coverage Ratio dropped to 95%', status: 'active', created_at: '2024-01-15T10:30:00Z' },
  { id: 2, alert_type: 'gap_limit', severity: 'medium', title: 'Negative Gap in 1-month bucket', description: 'Cumulative gap: -₹50 Cr', status: 'active', created_at: '2024-01-14T15:20:00Z' },
  { id: 3, alert_type: 'concentration', severity: 'medium', title: 'Funding Concentration', description: 'Single counterparty exceeds 15%', status: 'acknowledged', created_at: '2024-01-13T09:00:00Z' },
  { id: 4, alert_type: 'irr_threshold', severity: 'low', title: 'IRR Impact Warning', description: 'NII impact exceeds 10% in stress scenario', status: 'resolved', created_at: '2024-01-12T14:45:00Z' },
]

export default function ALMAlertsPage() {
  const router = useRouter()
  const [alerts, setAlerts] = useState(MOCK_ALERTS)
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      low: 'bg-blue-100 text-blue-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    }
    return colors[severity] || 'bg-gray-100 text-gray-800'
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-red-100 text-red-800',
      acknowledged: 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter && alert.severity !== severityFilter) return false
    if (statusFilter && alert.status !== statusFilter) return false
    return true
  })

  const activeCount = alerts.filter(a => a.status === 'active').length
  const criticalCount = alerts.filter(a => a.severity === 'critical').length

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">ALM Alerts</h1>
            <p className="text-muted-foreground">Monitor limit breaches & risk thresholds</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Total Alerts</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{alerts.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Active</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{activeCount}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Critical</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{criticalCount}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">Resolved</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-green-600">{alerts.filter(a => a.status === 'resolved').length}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger><SelectValue placeholder="All severities" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Severities</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger><SelectValue placeholder="All statuses" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="acknowledged">Acknowledged</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={() => { setSeverityFilter(''); setStatusFilter('') }}>Clear Filters</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Alert List</CardTitle><CardDescription>All ALM system alerts</CardDescription></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Alert</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAlerts.map((alert) => (
                <TableRow key={alert.id}>
                  <TableCell>
                    <div><p className="font-medium">{alert.title}</p><p className="text-sm text-muted-foreground">{alert.description}</p></div>
                  </TableCell>
                  <TableCell><Badge variant="outline">{alert.alert_type.replace('_', ' ')}</Badge></TableCell>
                  <TableCell><Badge className={getSeverityColor(alert.severity)}>{alert.severity.toUpperCase()}</Badge></TableCell>
                  <TableCell><Badge className={getStatusColor(alert.status)}>{alert.status.toUpperCase()}</Badge></TableCell>
                  <TableCell>{new Date(alert.created_at).toLocaleString()}</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {alert.status === 'active' && <Button variant="ghost" size="sm"><CheckCircle2 className="h-4 w-4" /></Button>}
                      <Button variant="ghost" size="sm"><X className="h-4 w-4" /></Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
