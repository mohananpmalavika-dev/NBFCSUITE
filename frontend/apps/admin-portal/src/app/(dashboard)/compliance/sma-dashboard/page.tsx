'use client'

/**
 * SMA Dashboard Page
 * Real-time Special Mention Account monitoring
 */

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  AlertCircle,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  RefreshCw,
  Calendar,
  AlertTriangle,
} from 'lucide-react'
import { complianceService } from '@/services/compliance.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { SMADashboardStats } from '@/types/compliance.types'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from '@/components/ui/use-toast'

export default function SMADashboardPage() {
  const [asOnDate, setAsOnDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  )

  const {
    data: dashboardStats,
    isLoading,
    refetch,
    isRefetching,
  } = useQuery({
    queryKey: ['sma-dashboard', asOnDate],
    queryFn: () => complianceService.getSMADashboard(asOnDate),
  })

  const handleRefresh = () => {
    refetch()
    toast({
      title: 'Dashboard Refreshed',
      description: 'SMA statistics updated successfully',
    })
  }

  const getSMABadgeColor = (status: string) => {
    switch (status) {
      case 'standard':
        return 'bg-green-100 text-green-800'
      case 'sma_0':
        return 'bg-yellow-100 text-yellow-800'
      case 'sma_1':
        return 'bg-orange-100 text-orange-800'
      case 'sma_2':
        return 'bg-red-100 text-red-800'
      case 'npa':
        return 'bg-red-200 text-red-900'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return <DashboardSkeleton />
  }

  const stats = dashboardStats || {} as SMADashboardStats

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">SMA Dashboard</h1>
          <p className="text-muted-foreground">
            Special Mention Account Monitoring & Classification
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <Input
              type="date"
              value={asOnDate}
              onChange={(e) => setAsOnDate(e.target.value)}
              className="w-48"
            />
          </div>
          <Button
            onClick={handleRefresh}
            disabled={isRefetching}
            variant="outline"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Accounts</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_accounts || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active loan accounts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Exposure</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(stats.total_exposure || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Outstanding amount
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Provision Required</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(stats.provision_required || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Total provisions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Alerts</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {stats.alerts_open || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Requires attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* SMA Classification Breakdown */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Standard */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Standard (0 DPD)</CardTitle>
              <Badge className={getSMABadgeColor('standard')}>✓ Healthy</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Accounts:</span>
                <span className="font-semibold">{stats.standard_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Amount:</span>
                <span className="font-semibold">
                  {formatCurrency(stats.standard_amount || 0)}
                </span>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-muted-foreground">
                  {stats.total_accounts > 0
                    ? `${((stats.standard_count / stats.total_accounts) * 100).toFixed(1)}% of portfolio`
                    : '0% of portfolio'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* SMA-0 */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">SMA-0 (1-30 DPD)</CardTitle>
              <Badge className={getSMABadgeColor('sma_0')}>⚠️ Watch</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Accounts:</span>
                <span className="font-semibold">{stats.sma_0_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Amount:</span>
                <span className="font-semibold">
                  {formatCurrency(stats.sma_0_amount || 0)}
                </span>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-yellow-600 font-medium">
                  Early contact required
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* SMA-1 */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">SMA-1 (31-60 DPD)</CardTitle>
              <Badge className={getSMABadgeColor('sma_1')}>⚠️ Action</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Accounts:</span>
                <span className="font-semibold">{stats.sma_1_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Amount:</span>
                <span className="font-semibold">
                  {formatCurrency(stats.sma_1_amount || 0)}
                </span>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-orange-600 font-medium">
                  Follow-up + restructure discussion
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* SMA-2 */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">SMA-2 (61-90 DPD)</CardTitle>
              <Badge className={getSMABadgeColor('sma_2')}>🚨 Urgent</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Accounts:</span>
                <span className="font-semibold">{stats.sma_2_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Amount:</span>
                <span className="font-semibold">
                  {formatCurrency(stats.sma_2_amount || 0)}
                </span>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-red-600 font-medium">
                  Urgent action + legal notice
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* NPA */}
        <Card className="border-red-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">NPA (&gt;90 DPD)</CardTitle>
              <Badge className={getSMABadgeColor('npa')}>🔴 NPA</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Accounts:</span>
                <span className="font-semibold text-red-600">
                  {stats.npa_count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Amount:</span>
                <span className="font-semibold text-red-600">
                  {formatCurrency(stats.npa_amount || 0)}
                </span>
              </div>
              <div className="pt-2 border-t">
                <div className="text-xs text-red-600 font-medium">
                  Legal action initiated
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Portfolio Health Summary */}
        <Card className="bg-blue-50">
          <CardHeader>
            <CardTitle className="text-base">Portfolio Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Standard %:</span>
                <span className="font-semibold text-green-600">
                  {stats.total_accounts > 0
                    ? `${((stats.standard_count / stats.total_accounts) * 100).toFixed(1)}%`
                    : '0%'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">At Risk (SMA):</span>
                <span className="font-semibold text-orange-600">
                  {((stats.sma_0_count || 0) + (stats.sma_1_count || 0) + (stats.sma_2_count || 0))} accounts
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">NPA Ratio:</span>
                <span className="font-semibold text-red-600">
                  {stats.total_exposure > 0
                    ? `${(((stats.npa_amount || 0) / stats.total_exposure) * 100).toFixed(2)}%`
                    : '0%'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button variant="outline" className="w-full" asChild>
              <a href="/compliance/sma-tracking">View SMA Tracking</a>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <a href="/compliance/alerts">Manage Alerts ({stats.alerts_open || 0})</a>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <a href="/compliance/quarterly-reports">Quarterly Reports</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-96 mt-2" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
              <Skeleton className="h-3 w-24 mt-2" />
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
