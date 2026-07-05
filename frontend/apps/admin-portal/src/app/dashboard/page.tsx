'use client'

import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, 
  TrendingDown,
  Users, 
  Wallet, 
  PiggyBank, 
  AlertCircle,
  Clock,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { dashboardService } from '@/services/dashboard.service'
import { formatCurrency, formatNumber, formatRelativeTime } from '@/lib/utils'
import { DashboardLayout } from '@/components/layout/dashboard-layout'

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardService.getStats(),
  })

  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ['dashboard-activities'],
    queryFn: () => dashboardService.getRecentActivities(10),
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome to NBFC Suite Admin Portal</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Customers"
            value={stats?.data?.total_customers || 0}
            icon={Users}
            trend={{ value: 12, isPositive: true }}
            loading={statsLoading}
          />
          <StatCard
            title="Active Loans"
            value={stats?.data?.active_loans || 0}
            icon={Wallet}
            trend={{ value: 8, isPositive: true }}
            loading={statsLoading}
          />
          <StatCard
            title="Total Outstanding"
            value={formatCurrency(stats?.data?.total_outstanding || 0)}
            icon={TrendingUp}
            trend={{ value: 5, isPositive: true }}
            loading={statsLoading}
            valueClassName="text-2xl"
          />
          <StatCard
            title="Overdue Amount"
            value={formatCurrency(stats?.data?.overdue_amount || 0)}
            icon={AlertCircle}
            trend={{ value: 3, isPositive: false }}
            loading={statsLoading}
            valueClassName="text-2xl"
            iconClassName="text-red-600"
          />
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Collection Efficiency
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">
                    {stats?.data?.collection_efficiency || 0}%
                  </span>
                  <Badge variant="success" className="text-xs">
                    Target: 95%
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Deposits
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-32" />
              ) : (
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-gray-900">
                    {formatCurrency(stats?.data?.total_deposits || 0)}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">
                Overdue Accounts
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-20" />
              ) : (
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-red-600">
                    {formatNumber(stats?.data?.overdue_accounts || 0)}
                  </span>
                  <span className="text-sm text-gray-600">accounts</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activities</CardTitle>
          </CardHeader>
          <CardContent>
            {activitiesLoading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-start gap-4">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/2" />
                    </div>
                  </div>
                ))}
              </div>
            ) : activities?.data && activities.data.length > 0 ? (
              <div className="space-y-4">
                {activities.data.map((activity: any) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                <p>No recent activities</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <QuickActionButton
                icon={Users}
                label="Add Customer"
                href="/customers/new"
              />
              <QuickActionButton
                icon={Wallet}
                label="New Loan"
                href="/loans/applications/new"
              />
              <QuickActionButton
                icon={PiggyBank}
                label="Open Deposit"
                href="/deposits/accounts/new"
              />
              <QuickActionButton
                icon={CheckCircle}
                label="My Tasks"
                href="/workflows/tasks"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  loading,
  valueClassName = 'text-3xl',
  iconClassName = 'text-blue-600',
}: {
  title: string
  value: string | number
  icon: any
  trend?: { value: number; isPositive: boolean }
  loading?: boolean
  valueClassName?: string
  iconClassName?: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        <Icon className={`h-5 w-5 ${iconClassName}`} />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-24" />
        ) : (
          <div>
            <div className={`font-bold text-gray-900 ${valueClassName}`}>
              {value}
            </div>
            {trend && (
              <div className="flex items-center mt-2 text-sm">
                {trend.isPositive ? (
                  <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                )}
                <span className={trend.isPositive ? 'text-green-600' : 'text-red-600'}>
                  {trend.value}%
                </span>
                <span className="text-gray-600 ml-1">vs last month</span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ActivityItem({ activity }: { activity: any }) {
  return (
    <div className="flex items-start gap-4">
      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
        <CheckCircle className="h-5 w-5 text-blue-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{activity.description}</p>
        <p className="text-xs text-gray-600 mt-1">
          {activity.user && `by ${activity.user} • `}
          {formatRelativeTime(activity.timestamp)}
        </p>
      </div>
      {activity.status && (
        <Badge variant={activity.status === 'completed' ? 'success' : 'default'}>
          {activity.status}
        </Badge>
      )}
    </div>
  )
}

function QuickActionButton({ 
  icon: Icon, 
  label, 
  href 
}: { 
  icon: any
  label: string
  href: string 
}) {
  return (
    <a
      href={href}
      className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors group"
    >
      <Icon className="h-8 w-8 text-gray-400 group-hover:text-blue-600 mb-2" />
      <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600 text-center">
        {label}
      </span>
    </a>
  )
}
