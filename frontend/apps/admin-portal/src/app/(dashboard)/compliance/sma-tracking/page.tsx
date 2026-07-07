'use client'

/**
 * SMA Tracking Page
 * View and manage SMA status tracking for loan accounts
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Calculator, Search, Calendar, TrendingUp, AlertTriangle, History } from 'lucide-react'
import { complianceService } from '@/services/compliance.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { SMATracking, SMACalculationRequest } from '@/types/compliance.types'
import { toast } from '@/components/ui/use-toast'
import { Skeleton } from '@/components/ui/skeleton'

export default function SMATrackingPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [smaFilter, setSmaFilter] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [calculateDialogOpen, setCalculateDialogOpen] = useState(false)
  const [calculationDate, setCalculationDate] = useState(
    new Date().toISOString().split('T')[0]
  )

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['sma-tracking', page, smaFilter],
    queryFn: () =>
      complianceService.getSMATracking({
        skip: (page - 1) * 20,
        limit: 20,
        sma_status: smaFilter !== 'all' ? smaFilter : undefined,
      }),
  })

  const calculateMutation = useMutation({
    mutationFn: (data: SMACalculationRequest) =>
      complianceService.calculateSMA(data),
    onSuccess: (result) => {
      toast({
        title: 'SMA Calculation Complete',
        description: `Processed ${result.accounts_processed} accounts. ${result.status_changes} status changes detected.`,
      })
      setCalculateDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['sma-tracking'] })
      queryClient.invalidateQueries({ queryKey: ['sma-dashboard'] })
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to calculate SMA status',
        variant: 'destructive',
      })
    },
  })

  const handleCalculate = () => {
    calculateMutation.mutate({
      as_on_date: calculationDate,
      calculate_provisions: true,
    })
  }

  const getSMABadge = (status: string) => {
    const colors = {
      standard: 'bg-green-100 text-green-800',
      sma_0: 'bg-yellow-100 text-yellow-800',
      sma_1: 'bg-orange-100 text-orange-800',
      sma_2: 'bg-red-100 text-red-800',
      npa_substandard: 'bg-red-200 text-red-900',
    }
    const labels = {
      standard: 'Standard',
      sma_0: 'SMA-0',
      sma_1: 'SMA-1',
      sma_2: 'SMA-2',
      npa_substandard: 'NPA',
    }
    return (
      <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {labels[status as keyof typeof labels] || status}
      </Badge>
    )
  }

  const getProvisionColor = (percentage: number) => {
    if (percentage === 0) return 'text-green-600'
    if (percentage < 15) return 'text-yellow-600'
    if (percentage < 50) return 'text-orange-600'
    return 'text-red-600'
  }

  if (isLoading) {
    return <SMATrackingSkeleton />
  }

  const trackingRecords = data?.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">SMA Tracking</h1>
          <p className="text-muted-foreground">
            Real-time Special Mention Account status monitoring
          </p>
        </div>
        <Dialog open={calculateDialogOpen} onOpenChange={setCalculateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Calculator className="h-4 w-4 mr-2" />
              Calculate SMA Status
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Calculate SMA Status</DialogTitle>
              <DialogDescription>
                Run SMA calculation for all active loan accounts
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="calc-date">As On Date</Label>
                <Input
                  id="calc-date"
                  type="date"
                  value={calculationDate}
                  onChange={(e) => setCalculationDate(e.target.value)}
                />
              </div>
              <div className="rounded-lg bg-blue-50 p-4">
                <p className="text-sm text-blue-900">
                  This will calculate SMA status, DPD, and provisions for all active accounts.
                  Status changes will trigger alerts automatically.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button
                onClick={handleCalculate}
                disabled={calculateMutation.isPending}
              >
                {calculateMutation.isPending ? 'Calculating...' : 'Calculate'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by loan account number or borrower..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={smaFilter} onValueChange={setSmaFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by SMA" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="standard">Standard</SelectItem>
                <SelectItem value="sma_0">SMA-0</SelectItem>
                <SelectItem value="sma_1">SMA-1</SelectItem>
                <SelectItem value="sma_2">SMA-2</SelectItem>
                <SelectItem value="npa_substandard">NPA</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tracking Table */}
      <Card>
        <CardHeader>
          <CardTitle>SMA Status Tracking</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Loan Account</TableHead>
                <TableHead>As On Date</TableHead>
                <TableHead>SMA Status</TableHead>
                <TableHead className="text-center">DPD</TableHead>
                <TableHead className="text-right">Outstanding</TableHead>
                <TableHead className="text-right">Overdue</TableHead>
                <TableHead className="text-right">Provision</TableHead>
                <TableHead className="text-center">Alert</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trackingRecords.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    No SMA tracking records found
                  </TableCell>
                </TableRow>
              ) : (
                trackingRecords.map((tracking: SMATracking) => (
                  <TableRow key={tracking.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">Account #{tracking.loan_account_id.slice(0, 8)}</div>
                        <div className="text-xs text-muted-foreground">
                          Quarter: {tracking.reporting_quarter || '-'}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        {formatDate(tracking.as_on_date)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {getSMABadge(tracking.current_sma_status)}
                        {tracking.previous_sma_status && tracking.previous_sma_status !== tracking.current_sma_status && (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <TrendingUp className="h-3 w-3" />
                            From {tracking.previous_sma_status}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant={tracking.days_past_due > 0 ? 'destructive' : 'secondary'}>
                        {tracking.days_past_due} days
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div>
                        <div className="font-medium">
                          {formatCurrency(tracking.total_outstanding)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          P: {formatCurrency(tracking.principal_outstanding)}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div>
                        <div className="font-medium text-orange-600">
                          {formatCurrency(tracking.total_overdue)}
                        </div>
                        {tracking.total_overdue > 0 && (
                          <div className="text-xs text-muted-foreground">
                            {tracking.days_in_current_status} days in status
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div>
                        <div className={`font-medium ${getProvisionColor(tracking.provision_percentage)}`}>
                          {formatCurrency(tracking.provision_required)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {tracking.provision_percentage}%
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      {tracking.alert_triggered && (
                        <AlertTriangle className="h-5 w-5 text-orange-600 mx-auto" />
                      )}
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
                Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, data.total)} of {data.total} records
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

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Tracked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.total || 0}</div>
            <p className="text-xs text-muted-foreground">Active tracking records</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">At Risk (SMA)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {trackingRecords.filter((t: SMATracking) =>
                ['sma_0', 'sma_1', 'sma_2'].includes(t.current_sma_status)
              ).length}
            </div>
            <p className="text-xs text-muted-foreground">Requires monitoring</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Alerts Triggered</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {trackingRecords.filter((t: SMATracking) => t.alert_triggered).length}
            </div>
            <p className="text-xs text-muted-foreground">Requires action</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function SMATrackingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-96 mt-2" />
        </div>
        <Skeleton className="h-10 w-48" />
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
