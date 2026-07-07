'use client'

/**
 * RBI Returns Dashboard
 * Overview of all RBI regulatory returns, compliance metrics, and upcoming deadlines
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  FileText,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  Calendar,
  Download,
  Plus,
  ArrowRight,
} from 'lucide-react'
import { rbiReturnsService } from '@/services/rbi-returns.service'
import { formatCurrency, formatDate } from '@/lib/utils'
import { Skeleton } from '@/components/ui/skeleton'
import Link from 'next/link'

export default function RBIReturnsDashboardPage() {
  const [selectedTab, setSelectedTab] = useState('overview')

  // Fetch dashboard stats
  const { data: dashboardStats, isLoading: statsLoading } = useQuery({
    queryKey: ['rbi-returns-dashboard'],
    queryFn: () => rbiReturnsService.getDashboardStats(),
  })

  // Fetch calendar summary
  const { data: calendarSummary, isLoading: calendarLoading } = useQuery({
    queryKey: ['rbi-returns-calendar-summary'],
    queryFn: () => rbiReturnsService.getCalendarSummary(),
  })

  const isLoading = statsLoading || calendarLoading

  if (isLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">RBI Returns Automation</h1>
          <p className="text-muted-foreground">
            Automated regulatory reporting and compliance management
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/rbi-returns/nbs7">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Generate NBS-7
            </Button>
          </Link>
          <Link href="/rbi-returns/calendar">
            <Button variant="outline">
              <Calendar className="h-4 w-4 mr-2" />
              View Calendar
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Returns Due"
          value={dashboardStats?.total_returns_due || 0}
          icon={<FileText className="h-4 w-4" />}
          trend="This Month"
          color="blue"
        />
        <MetricCard
          title="Overdue"
          value={dashboardStats?.overdue_returns || 0}
          icon={<AlertCircle className="h-4 w-4" />}
          trend="Requires Attention"
          color="red"
        />
        <MetricCard
          title="Submitted"
          value={dashboardStats?.submitted_this_month || 0}
          icon={<CheckCircle className="h-4 w-4" />}
          trend="This Month"
          color="green"
        />
        <MetricCard
          title="Compliance Score"
          value={`${dashboardStats?.compliance_score?.toFixed(1) || 0}%`}
          icon={<TrendingUp className="h-4 w-4" />}
          trend={`${dashboardStats?.on_time_submission_rate?.toFixed(1) || 0}% On-Time`}
          color="purple"
        />
      </div>

      {/* Main Content Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="nbs7">NBS-7 Returns</TabsTrigger>
          <TabsTrigger value="statutory">Statutory Returns</TabsTrigger>
          <TabsTrigger value="deadlines">Upcoming Deadlines</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Status Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Return Status Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <StatusRow
                    label="Draft"
                    count={dashboardStats?.draft_returns || 0}
                    color="gray"
                  />
                  <StatusRow
                    label="Pending Approval"
                    count={dashboardStats?.pending_approval || 0}
                    color="yellow"
                  />
                  <StatusRow
                    label="Approved"
                    count={
                      (dashboardStats?.nbs7_monthly_status?.approved || 0) +
                      (dashboardStats?.nbs7_quarterly_status?.approved || 0)
                    }
                    color="green"
                  />
                  <StatusRow
                    label="Submitted"
                    count={dashboardStats?.submitted_this_month || 0}
                    color="blue"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Recent Submissions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Submissions</CardTitle>
              </CardHeader>
              <CardContent>
                {dashboardStats?.recent_submissions?.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No recent submissions
                  </p>
                ) : (
                  <div className="space-y-3">
                    {dashboardStats?.recent_submissions?.slice(0, 5).map((submission: any) => (
                      <div
                        key={submission.return_number}
                        className="flex items-center justify-between p-3 rounded-lg border"
                      >
                        <div>
                          <p className="font-medium text-sm">{submission.return_number}</p>
                          <p className="text-xs text-muted-foreground">
                            {submission.reporting_period}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">
                            {formatDate(submission.submitted_date)}
                          </p>
                          {submission.is_overdue && (
                            <Badge variant="destructive" className="text-xs mt-1">
                              Late
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Upcoming Deadlines */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Upcoming Deadlines (Next 30 Days)</CardTitle>
              <Link href="/rbi-returns/calendar">
                <Button variant="ghost" size="sm">
                  View All
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              {dashboardStats?.upcoming_deadlines?.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No upcoming deadlines
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Event</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Days Remaining</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {dashboardStats?.upcoming_deadlines?.map((deadline: any, idx: number) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">
                          {deadline.event_title}
                        </TableCell>
                        <TableCell>{formatDate(deadline.due_date)}</TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              deadline.days_remaining <= 3 ? 'destructive' : 'secondary'
                            }
                          >
                            {deadline.days_remaining} days
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <PriorityBadge priority={deadline.priority} />
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm">
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* NBS-7 Returns Tab */}
        <TabsContent value="nbs7">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>NBS-7 Returns</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Monthly and quarterly financial returns
                </p>
              </div>
              <Link href="/rbi-returns/nbs7">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Return
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 rounded-lg border">
                  <h3 className="font-semibold mb-2">Monthly Returns</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(dashboardStats?.nbs7_monthly_status || {}).map(
                      ([status, count]) => (
                        <div key={status} className="flex justify-between">
                          <span className="text-muted-foreground capitalize">
                            {status.replace('_', ' ')}
                          </span>
                          <span className="font-medium">{count as number}</span>
                        </div>
                      )
                    )}
                  </div>
                </div>
                <div className="p-4 rounded-lg border">
                  <h3 className="font-semibold mb-2">Quarterly Returns</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(dashboardStats?.nbs7_quarterly_status || {}).map(
                      ([status, count]) => (
                        <div key={status} className="flex justify-between">
                          <span className="text-muted-foreground capitalize">
                            {status.replace('_', ' ')}
                          </span>
                          <span className="font-medium">{count as number}</span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
              <div className="mt-4 text-center">
                <Link href="/rbi-returns/nbs7">
                  <Button variant="outline">View All NBS-7 Returns</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Statutory Returns Tab */}
        <TabsContent value="statutory">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Statutory Returns</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  ALM, NPA, Exposure, and other RBI returns
                </p>
              </div>
              <Link href="/rbi-returns/statutory">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  New Return
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(dashboardStats?.statutory_returns_status || {}).map(
                  ([status, count]) => (
                    <div
                      key={status}
                      className="flex items-center justify-between p-3 rounded-lg border"
                    >
                      <span className="font-medium capitalize">
                        {status.replace('_', ' ')}
                      </span>
                      <Badge>{count as number}</Badge>
                    </div>
                  )
                )}
              </div>
              <div className="mt-4 text-center">
                <Link href="/rbi-returns/statutory">
                  <Button variant="outline">View All Statutory Returns</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Deadlines Tab */}
        <TabsContent value="deadlines">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Compliance Deadlines</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3 mb-6">
                <div className="p-4 rounded-lg border text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {calendarSummary?.upcoming_events || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Upcoming Events</p>
                </div>
                <div className="p-4 rounded-lg border text-center">
                  <p className="text-2xl font-bold text-red-600">
                    {calendarSummary?.overdue_events || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Overdue Events</p>
                </div>
                <div className="p-4 rounded-lg border text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {calendarSummary?.completed_events || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">Completed</p>
                </div>
              </div>
              <div className="text-center">
                <Link href="/rbi-returns/calendar">
                  <Button>
                    <Calendar className="h-4 w-4 mr-2" />
                    Open Compliance Calendar
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Helper Components

function MetricCard({
  title,
  value,
  icon,
  trend,
  color,
}: {
  title: string
  value: string | number
  icon: React.ReactNode
  trend: string
  color: 'blue' | 'red' | 'green' | 'purple'
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    red: 'bg-red-100 text-red-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground mt-1">{trend}</p>
      </CardContent>
    </Card>
  )
}

function StatusRow({
  label,
  count,
  color,
}: {
  label: string
  count: number
  color: 'gray' | 'yellow' | 'green' | 'blue'
}) {
  const colorClasses = {
    gray: 'bg-gray-100',
    yellow: 'bg-yellow-100',
    green: 'bg-green-100',
    blue: 'bg-blue-100',
  }

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm">{label}</span>
      <Badge className={colorClasses[color]}>{count}</Badge>
    </div>
  )
}

function PriorityBadge({ priority }: { priority: string }) {
  const variants: Record<string, any> = {
    critical: 'destructive',
    high: 'default',
    medium: 'secondary',
    low: 'outline',
  }

  return (
    <Badge variant={variants[priority] || 'secondary'} className="capitalize">
      {priority}
    </Badge>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-2" />
              <Skeleton className="h-3 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    </div>
  )
}
