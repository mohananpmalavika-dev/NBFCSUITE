'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, TrendingUp, TrendingDown, AlertCircle, Activity } from 'lucide-react'
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
import { Skeleton } from '@/components/ui/skeleton'
import { riskService } from '@/services/risk.service'
import { formatDate } from '@/lib/utils'
import { Doughnut, Line, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const RISK_GRADES = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D']
const GRADE_COLORS = {
  'A+': '#10b981',
  'A': '#22c55e',
  'B+': '#3b82f6',
  'B': '#6366f1',
  'C+': '#eab308',
  'C': '#f97316',
  'D': '#ef4444',
}

export default function RiskRatingsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [gradeFilter, setGradeFilter] = useState<string | undefined>()

  const { data, isLoading } = useQuery({
    queryKey: ['risk-ratings', page, search, gradeFilter],
    queryFn: () => riskService.getRiskRatings({
      page,
      page_size: 20,
      risk_grade: gradeFilter,
    }),
  })

  const { data: stats } = useQuery({
    queryKey: ['risk-rating-stats'],
    queryFn: async () => {
      // Mock stats - replace with actual API call
      return {
        total_ratings: 1250,
        avg_pd: 2.5,
        high_risk_count: 85,
        rating_distribution: {
          'A+': 150,
          'A': 280,
          'B+': 320,
          'B': 245,
          'C+': 140,
          'C': 65,
          'D': 50,
        },
        trend_data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          avgPD: [2.8, 2.7, 2.6, 2.5, 2.4, 2.5],
        },
      }
    },
  })

  const getRiskGradeBadge = (grade: string) => {
    const color = GRADE_COLORS[grade as keyof typeof GRADE_COLORS]
    return (
      <Badge
        style={{ backgroundColor: color, color: 'white' }}
        className="font-semibold"
      >
        {grade}
      </Badge>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Risk Ratings</h1>
            <p className="text-gray-600 mt-1">Portfolio risk analysis and rating distribution</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Ratings"
            value={stats?.total_ratings.toLocaleString() || '0'}
            icon={Activity}
            color="blue"
          />
          <StatCard
            label="Avg PD"
            value={`${stats?.avg_pd.toFixed(2)}%` || '0%'}
            icon={TrendingDown}
            color="green"
          />
          <StatCard
            label="High Risk (C+, C, D)"
            value={stats?.high_risk_count || 0}
            icon={AlertCircle}
            color="red"
          />
          <StatCard
            label="Low Risk (A+, A)"
            value={((stats?.rating_distribution['A+'] || 0) + (stats?.rating_distribution['A'] || 0))}
            icon={TrendingUp}
            color="green"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Rating Distribution */}
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle>Rating Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Doughnut
                  data={{
                    labels: RISK_GRADES,
                    datasets: [{
                      data: RISK_GRADES.map(grade => stats?.rating_distribution[grade as keyof typeof stats.rating_distribution] || 0),
                      backgroundColor: RISK_GRADES.map(grade => GRADE_COLORS[grade as keyof typeof GRADE_COLORS]),
                    }],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: {
                          padding: 10,
                          font: { size: 11 },
                        },
                      },
                      tooltip: {
                        callbacks: {
                          label: (context) => {
                            const label = context.label || ''
                            const value = context.parsed || 0
                            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
                            const percentage = ((value / total) * 100).toFixed(1)
                            return `${label}: ${value} (${percentage}%)`
                          },
                        },
                      },
                    },
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* PD Trend */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Average PD Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Line
                  data={{
                    labels: stats?.trend_data.labels || [],
                    datasets: [{
                      label: 'Average PD (%)',
                      data: stats?.trend_data.avgPD || [],
                      borderColor: 'rgb(59, 130, 246)',
                      backgroundColor: 'rgba(59, 130, 246, 0.1)',
                      tension: 0.4,
                      fill: true,
                    }],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          callback: (value) => value + '%',
                        },
                      },
                    },
                  }}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Rating Breakdown by Grade */}
        <Card>
          <CardHeader>
            <CardTitle>Portfolio Breakdown by Risk Grade</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Bar
                data={{
                  labels: RISK_GRADES,
                  datasets: [{
                    label: 'Number of Accounts',
                    data: RISK_GRADES.map(grade => stats?.rating_distribution[grade as keyof typeof stats.rating_distribution] || 0),
                    backgroundColor: RISK_GRADES.map(grade => GRADE_COLORS[grade as keyof typeof GRADE_COLORS]),
                  }],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by customer or loan..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={gradeFilter || ''}
            onChange={(e) => setGradeFilter(e.target.value || undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Grades</option>
            {RISK_GRADES.map(grade => (
              <option key={grade} value={grade}>{grade}</option>
            ))}
          </select>
        </div>

        {/* Recent Ratings Table */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Risk Ratings</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Rating Date</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Loan Account</TableHead>
                  <TableHead>Risk Grade</TableHead>
                  <TableHead>PD (%)</TableHead>
                  <TableHead>LGD (%)</TableHead>
                  <TableHead>EAD</TableHead>
                  <TableHead>Expected Loss</TableHead>
                  <TableHead>Model Version</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <TableRow key={i}>
                      {[...Array(10)].map((_, j) => (
                        <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : data?.items && data.items.length > 0 ? (
                  data.items.map((rating) => (
                    <TableRow key={rating.id}>
                      <TableCell>{formatDate(rating.rating_date)}</TableCell>
                      <TableCell>
                        <Link href={`/customers/${rating.customer_id}`} className="text-blue-600 hover:underline">
                          Customer #{rating.customer_id}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Link href={`/loans/${rating.loan_id}`} className="text-blue-600 hover:underline">
                          {rating.loan_id ? `LN-${rating.loan_id}` : '-'}
                        </Link>
                      </TableCell>
                      <TableCell>{getRiskGradeBadge(rating.risk_grade)}</TableCell>
                      <TableCell>{rating.probability_of_default.toFixed(2)}%</TableCell>
                      <TableCell>{rating.loss_given_default.toFixed(2)}%</TableCell>
                      <TableCell>₹{(rating.exposure_at_default / 100000).toFixed(2)}L</TableCell>
                      <TableCell className="text-red-600 font-medium">
                        ₹{(rating.expected_loss / 100000).toFixed(2)}L
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{rating.model_version}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Link href={`/risk/ratings/${rating.id}`}>
                          <Button variant="ghost" size="sm">
                            View Details
                          </Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={10} className="text-center py-8 text-gray-500">
                      No risk ratings found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Pagination */}
        {data && data.items.length > 0 && (
          <div className="flex items-center justify-between px-6 py-4 bg-white rounded-lg border">
            <p className="text-sm text-gray-600">
              Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of {data.total} ratings
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
    </DashboardLayout>
  )
}

function StatCard({ label, value, icon: Icon, color = 'blue' }: any) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
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
