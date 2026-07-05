'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Search, Filter, Eye, MoreVertical, GitBranch, Clock, CheckCircle, XCircle } from 'lucide-react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { workflowService } from '@/services/workflow.service'
import { formatDate, formatDateTime, getStatusColor } from '@/lib/utils'
import type { WorkflowInstance } from '@/types'

export default function WorkflowInstancesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['workflow-instances', page, search, statusFilter],
    queryFn: () => workflowService.getInstances({ 
      page, 
      page_size: 20,
      status: statusFilter || undefined
    }),
  })

  // Calculate stats
  const stats = data?.data?.items?.reduce(
    (acc, instance: WorkflowInstance) => {
      if (instance.instance_status === 'pending') acc.pending++
      else if (instance.instance_status === 'in_progress') acc.inProgress++
      else if (instance.instance_status === 'completed') acc.completed++
      else if (instance.instance_status === 'cancelled') acc.cancelled++
      else if (instance.instance_status === 'failed') acc.failed++
      
      return acc
    },
    { pending: 0, inProgress: 0, completed: 0, cancelled: 0, failed: 0 }
  ) || { pending: 0, inProgress: 0, completed: 0, cancelled: 0, failed: 0 }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Workflow Instances</h1>
            <p className="text-gray-600 mt-1">Monitor and manage workflow execution instances</p>
          </div>
          <Link href="/workflow/templates">
            <Button variant="outline">
              <GitBranch className="h-4 w-4 mr-2" />
              View Templates
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <StatCard
            label="Pending"
            value={stats.pending}
            icon={Clock}
            color="blue"
          />
          <StatCard
            label="In Progress"
            value={stats.inProgress}
            icon={GitBranch}
            color="purple"
          />
          <StatCard
            label="Completed"
            value={stats.completed}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            label="Cancelled"
            value={stats.cancelled}
            icon={XCircle}
            color="yellow"
          />
          <StatCard
            label="Failed"
            value={stats.failed}
            icon={XCircle}
            color="red"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search by instance number, template..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>

        {/* Instances Tabs */}
        <Tabs value={statusFilter} onValueChange={setStatusFilter}>
          <TabsList>
            <TabsTrigger value="">All Instances</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="in_progress">In Progress</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="cancelled">Cancelled</TabsTrigger>
          </TabsList>

          <TabsContent value={statusFilter} className="space-y-4">
            {/* Table */}
            <div className="bg-white rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Instance Number</TableHead>
                    <TableHead>Template</TableHead>
                    <TableHead>Entity</TableHead>
                    <TableHead>Current Step</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Started At</TableHead>
                    <TableHead>Completed At</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    [...Array(5)].map((_, i) => (
                      <TableRow key={i}>
                        <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                        <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                        <TableCell><Skeleton className="h-8 w-8 ml-auto" /></TableCell>
                      </TableRow>
                    ))
                  ) : data?.data?.items && data.data.items.length > 0 ? (
                    data.data.items.map((instance: WorkflowInstance) => (
                      <TableRow key={instance.id}>
                        <TableCell className="font-mono text-sm font-medium">
                          {instance.instance_number}
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{instance.template_name || 'N/A'}</p>
                            <p className="text-sm text-gray-500">
                              ID: {instance.template_id.slice(0, 8)}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          {instance.entity_type ? (
                            <div>
                              <Badge variant="outline">{instance.entity_type}</Badge>
                              <p className="text-xs text-gray-500 mt-1">
                                {instance.entity_id?.slice(0, 8)}
                              </p>
                            </div>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {instance.current_step ? (
                            <Badge variant="outline">{instance.current_step}</Badge>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(instance.instance_status)}>
                            {instance.instance_status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {formatDateTime(instance.started_at)}
                        </TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {instance.completed_at 
                            ? formatDateTime(instance.completed_at)
                            : '-'}
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <Link href={`/workflow/instances/${instance.id}`}>
                                <DropdownMenuItem>
                                  <Eye className="h-4 w-4 mr-2" />
                                  View Details
                                </DropdownMenuItem>
                              </Link>
                              {['pending', 'in_progress'].includes(instance.instance_status) && (
                                <DropdownMenuItem className="text-red-600">
                                  <XCircle className="h-4 w-4 mr-2" />
                                  Cancel Instance
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-gray-500">
                        <GitBranch className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                        <p>No workflow instances found</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              {/* Pagination */}
              {data?.data && data.data.items.length > 0 && (
                <div className="flex items-center justify-between px-6 py-4 border-t">
                  <p className="text-sm text-gray-600">
                    Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.metadata?.total || 0)} of {data.metadata?.total || 0} instances
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!data.metadata?.has_prev}
                      onClick={() => setPage(page - 1)}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!data.metadata?.has_next}
                      onClick={() => setPage(page + 1)}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}

function StatCard({ 
  label, 
  value, 
  icon: Icon,
  color = 'blue'
}: { 
  label: string
  value: number
  icon: any
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{label}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
          <div className={`h-12 w-12 rounded-lg ${colors[color]} flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
