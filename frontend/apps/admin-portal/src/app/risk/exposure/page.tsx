'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, TrendingUp, AlertTriangle, CheckCircle, DollarSign } from 'lucide-react'
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
import { toast } from 'sonner'
import { Doughnut, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default function ExposureLimitsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [limitTypeFilter, setLimitTypeFilter] = useState<string | undefined>()
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [showModal, setShowModal] = useState(false)
  const [selectedLimit, setSelectedLimit] = useState<any>(null)
  const [actionType, setActionType] = useState<'utilize' | 'release' | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['exposure-limits', page, limitTypeFilter],
    queryFn: () => riskService.getExposureLimits({
      page,
      page_size: 20,
      limit_type: limitTypeFilter,
    }),
  })

  const { data: stats } = useQuery({
    queryKey: ['exposure-stats'],
    queryFn: async () => {
      // Mock stats - replace with actual API call
      return {
        total_limits: 25,
        breached: 3,
        warning: 5,
        healthy: 17,
        total_exposure: 15000000000,
        total_limit: 20000000000,
        avg_utilization: 75,
      }
    },
  })

  const utilizeMutation = useMutation({
    mutationFn: ({ limitId, amount, reference }: any) =>
      riskService.utilizeExposure(limitId, { amount, reference_type: 'loan', reference_id: reference }),
    onSuccess: () => {
      toast.success('Exposure utilized successfully')
      queryClient.invalidateQueries({ queryKey: ['exposure-limits'] })
      setShowModal(false)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to utilize exposure')
    },
  })

  const releaseMutation = useMutation({
    mutationFn: ({ limitId, amount, reference }: any) =>
      riskService.releaseExposure(limitId, { amount, reference_type: 'loan', reference_id: reference }),
    onSuccess: () => {
      toast.success('Exposure released successfully')
      queryClient.invalidateQueries({ queryKey: ['exposure-limits'] })
      setShowModal(false)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to release exposure')
    },
  })

  const getUtilizationPercentage = (used: number, limit: number) => {
    return (used / limit) * 100
  }

  const getUtilizationColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500'
    if (percentage >= 75) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStatusBadge = (percentage: number) => {
    if (percentage >= 100) return <Badge variant="destructive">Breached</Badge>
    if (percentage >= 90) return <Badge className="bg-red-100 text-red-800">Critical</Badge>
    if (percentage >= 75) return <Badge className="bg-yellow-100 text-yellow-800">Warning</Badge>
    return <Badge className="bg-green-100 text-green-800">Healthy</Badge>
  }

  const handleUtilize = (limit: any) => {
    setSelectedLimit(limit)
    setActionType('utilize')
    setShowModal(true)
  }

  const handleRelease = (limit: any) => {
    setSelectedLimit(limit)
    setActionType('release')
    setShowModal(true)
  }

  // Filter data based on status
  const filteredData = data?.items.filter(item => {
    if (!statusFilter) return true
    const pct = getUtilizationPercentage(item.utilized_amount, item.limit_amount)
    if (statusFilter === 'breached') return pct >= 100
    if (statusFilter === 'warning') return pct >= 75 && pct < 100
    if (statusFilter === 'healthy') return pct < 75
    return true
  })

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Exposure Limits</h1>
            <p className="text-gray-600 mt-1">Monitor and manage concentration risk limits</p>
          </div>
          <Button onClick={() => setShowModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Limit
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Limits"
            value={stats?.total_limits || 0}
            icon={TrendingUp}
            color="blue"
          />
          <StatCard
            label="Breached"
            value={stats?.breached || 0}
            icon={AlertTriangle}
            color="red"
          />
          <StatCard
            label="Warning"
            value={stats?.warning || 0}
            icon={AlertTriangle}
            color="yellow"
          />
          <StatCard
            label="Healthy"
            value={stats?.healthy || 0}
            icon={CheckCircle}
            color="green"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Utilization by Limit Type</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Doughnut
                  data={{
                    labels: ['Single Borrower', 'Group', 'Sector', 'Geographic'],
                    datasets: [{
                      data: [35, 25, 20, 20],
                      backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                      ],
                    }],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' },
                    },
                  }}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Top 5 Utilized Limits</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Bar
                  data={{
                    labels: ['ABC Corp', 'XYZ Group', 'Tech Sector', 'Mumbai', 'DEF Ltd'],
                    datasets: [{
                      label: 'Utilization %',
                      data: [95, 88, 82, 78, 72],
                      backgroundColor: (context: any) => {
                        const value = context.parsed.y
                        if (value >= 90) return 'rgba(239, 68, 68, 0.8)'
                        if (value >= 75) return 'rgba(245, 158, 11, 0.8)'
                        return 'rgba(16, 185, 129, 0.8)'
                      },
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
                        max: 100,
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

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search limits..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            value={limitTypeFilter || ''}
            onChange={(e) => setLimitTypeFilter(e.target.value || undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Types</option>
            <option value="single_borrower">Single Borrower</option>
            <option value="group">Group</option>
            <option value="sector">Sector</option>
            <option value="geographic">Geographic</option>
            <option value="product">Product</option>
          </select>
          <select
            value={statusFilter || ''}
            onChange={(e) => setStatusFilter(e.target.value || undefined)}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">All Status</option>
            <option value="breached">Breached</option>
            <option value="warning">Warning</option>
            <option value="healthy">Healthy</option>
          </select>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Limit Code</TableHead>
                <TableHead>Entity/Category</TableHead>
                <TableHead>Limit Type</TableHead>
                <TableHead>Limit Amount</TableHead>
                <TableHead>Utilized</TableHead>
                <TableHead>Available</TableHead>
                <TableHead>Utilization</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    {[...Array(9)].map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : filteredData && filteredData.length > 0 ? (
                filteredData.map((limit) => {
                  const utilization = getUtilizationPercentage(limit.utilized_amount, limit.limit_amount)
                  const available = limit.limit_amount - limit.utilized_amount

                  return (
                    <TableRow key={limit.id}>
                      <TableCell className="font-medium">{limit.limit_code}</TableCell>
                      <TableCell>{limit.entity_id || limit.category}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {limit.limit_type.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>₹{(limit.limit_amount / 10000000).toFixed(2)}Cr</TableCell>
                      <TableCell>₹{(limit.utilized_amount / 10000000).toFixed(2)}Cr</TableCell>
                      <TableCell>₹{(available / 10000000).toFixed(2)}Cr</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${getUtilizationColor(utilization)}`}
                                style={{ width: `${Math.min(utilization, 100)}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium w-12">{utilization.toFixed(1)}%</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(utilization)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleUtilize(limit)}
                            disabled={available <= 0}
                          >
                            Utilize
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRelease(limit)}
                            disabled={limit.utilized_amount <= 0}
                          >
                            Release
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                    No exposure limits found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {data && filteredData && filteredData.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t">
              <p className="text-sm text-gray-600">
                Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.total)} of {data.total} limits
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

      {/* Transaction Modal */}
      {showModal && actionType && selectedLimit && (
        <TransactionModal
          limit={selectedLimit}
          action={actionType}
          onClose={() => {
            setShowModal(false)
            setSelectedLimit(null)
            setActionType(null)
          }}
          onSubmit={(data) => {
            if (actionType === 'utilize') {
              utilizeMutation.mutate({ limitId: selectedLimit.id, ...data })
            } else {
              releaseMutation.mutate({ limitId: selectedLimit.id, ...data })
            }
          }}
        />
      )}
    </DashboardLayout>
  )
}

function StatCard({ label, value, icon: Icon, color = 'blue' }: any) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
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

function TransactionModal({ limit, action, onClose, onSubmit }: any) {
  const [formData, setFormData] = useState({
    amount: '',
    reference: '',
    remarks: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      amount: parseFloat(formData.amount),
      reference: formData.reference,
      remarks: formData.remarks,
    })
  }

  const available = limit.limit_amount - limit.utilized_amount
  const maxAmount = action === 'utilize' ? available : limit.utilized_amount

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {action === 'utilize' ? 'Utilize' : 'Release'} Exposure
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <div className="flex justify-between text-sm">
              <span>Limit:</span>
              <span className="font-medium">₹{(limit.limit_amount / 10000000).toFixed(2)}Cr</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Utilized:</span>
              <span className="font-medium">₹{(limit.utilized_amount / 10000000).toFixed(2)}Cr</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Available:</span>
              <span className="font-medium text-green-600">₹{(available / 10000000).toFixed(2)}Cr</span>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">
              Amount (₹) *
            </label>
            <Input
              type="number"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              max={maxAmount}
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Max: ₹{(maxAmount / 10000000).toFixed(2)}Cr
            </p>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">
              Reference (Loan ID) *
            </label>
            <Input
              value={formData.reference}
              onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
              placeholder="LN-2024-001"
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Remarks</label>
            <textarea
              value={formData.remarks}
              onChange={(e) => setFormData({ ...formData, remarks: e.target.value })}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              placeholder="Optional remarks..."
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              {action === 'utilize' ? 'Utilize' : 'Release'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
