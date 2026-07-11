'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Building2, FileText, DollarSign, Wrench, LayoutGrid, Key } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { propertyService } from '@/services/property.service'
import { formatCurrency } from '@/lib/utils'

export default function PropertyManagementDashboard() {
  const { data: propertyStats } = useQuery({
    queryKey: ['property-statistics'],
    queryFn: () => propertyService.getPropertyStatistics(),
  })

  const { data: leaseStats } = useQuery({
    queryKey: ['lease-statistics'],
    queryFn: () => propertyService.getLeaseStatistics(),
  })

  const { data: rentStats } = useQuery({
    queryKey: ['rent-statistics'],
    queryFn: () => propertyService.getRentStatistics(),
  })

  const { data: spaceStats } = useQuery({
    queryKey: ['space-statistics'],
    queryFn: () => propertyService.getSpaceStatistics(),
  })

  const { data: maintenanceStats } = useQuery({
    queryKey: ['maintenance-statistics'],
    queryFn: () => propertyService.getMaintenanceStatistics(),
  })

  const pStats = propertyStats?.data?.data
  const lStats = leaseStats?.data?.data
  const rStats = rentStats?.data?.data
  const sStats = spaceStats?.data?.data
  const mStats = maintenanceStats?.data?.data

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Property & Rent Management</h1>
          <p className="text-gray-600 mt-1">Comprehensive property and rental management dashboard</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Properties"
            value={pStats?.total_properties || 0}
            subtitle="Active properties"
            icon={Building2}
            color="blue"
          />
          <MetricCard
            title="Active Leases"
            value={lStats?.active_leases || 0}
            subtitle={`${lStats?.expiring_soon || 0} expiring soon`}
            icon={FileText}
            color="green"
          />
          <MetricCard
            title="Monthly Revenue"
            value={formatCurrency(lStats?.total_monthly_revenue || 0)}
            subtitle="Expected rental income"
            icon={DollarSign}
            color="emerald"
          />
          <MetricCard
            title="Occupancy Rate"
            value={`${sStats?.occupancy_rate || 0}%`}
            subtitle={`${sStats?.total_spaces || 0} total spaces`}
            icon={LayoutGrid}
            color="purple"
          />
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Link href="/property-management/properties/new">
              <Button variant="outline" className="w-full h-auto flex-col py-4">
                <Building2 className="h-6 w-6 mb-2" />
                <span>Add Property</span>
              </Button>
            </Link>
            <Link href="/property-management/leases/new">
              <Button variant="outline" className="w-full h-auto flex-col py-4">
                <Key className="h-6 w-6 mb-2" />
                <span>New Lease</span>
              </Button>
            </Link>
            <Link href="/property-management/rent">
              <Button variant="outline" className="w-full h-auto flex-col py-4">
                <DollarSign className="h-6 w-6 mb-2" />
                <span>Collect Rent</span>
              </Button>
            </Link>
            <Link href="/property-management/utilities">
              <Button variant="outline" className="w-full h-auto flex-col py-4">
                <LayoutGrid className="h-6 w-6 mb-2" />
                <span>Utilities</span>
              </Button>
            </Link>
            <Link href="/property-management/maintenance/new">
              <Button variant="outline" className="w-full h-auto flex-col py-4">
                <Wrench className="h-6 w-6 mb-2" />
                <span>Maintenance</span>
              </Button>
            </Link>
            <Link href="/property-management/spaces">
              <Button variant="outline" className="w-full h-auto flex-col py-4">
                <LayoutGrid className="h-6 w-6 mb-2" />
                <span>Spaces</span>
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Rent Collection Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Collected This Month</span>
                  <span className="font-semibold">{formatCurrency(rStats?.current_month_collected || 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Expected This Month</span>
                  <span className="font-semibold">{formatCurrency(rStats?.current_month_expected || 0)}</span>
                </div>
                <div className="flex justify-between items-center text-red-600">
                  <span>Overdue Payments</span>
                  <span className="font-semibold">{formatCurrency(rStats?.overdue_amount || 0)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Maintenance Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Requests</span>
                  <span className="font-semibold">{mStats?.total_requests || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Open Requests</span>
                  <span className="font-semibold">{mStats?.requests_by_status?.open || 0}</span>
                </div>
                <div className="flex justify-between items-center text-red-600">
                  <span>Urgent Requests</span>
                  <span className="font-semibold">{mStats?.urgent_requests || 0}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}

function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color
}: {
  title: string
  value: string | number
  subtitle: string
  icon: any
  color: string
}) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    emerald: 'bg-emerald-100 text-emerald-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
