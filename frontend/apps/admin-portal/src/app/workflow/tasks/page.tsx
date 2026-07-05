'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Link from 'next/link'
import { Search, Filter, CheckCircle, XCircle, Clock, User, AlertCircle } from 'lucide-react'
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
import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { workflowService } from '@/services/workflow.service'
import { formatDate, getStatusColor } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import type { WorkflowTask } from '@/types'

export default function MyTasksPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('pending')
  const [selectedTask, setSelectedTask] = useState<WorkflowTask | null>(null)
  const [actionComments, setActionComments] = useState('')

  const queryClient = useQueryClient()
  const { toast } = useToast()

  const { data, isLoading } = useQuery({
    queryKey: ['my-tasks', page, search, statusFilter],
    queryFn: () => workflowService.getMyTasks({ 
      page, 
      page_size: 20,
      status: statusFilter || undefined
    }),
  })

  const claimMutation = useMutation({
    mutationFn: (taskId: string) => workflowService.claimTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-tasks'] })
      toast({
        title: 'Task claimed',
        description: 'Task has been assigned to you',
      })
      setSelectedTask(null)
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to claim task',
        variant: 'destructive',
      })
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ taskId, comments }: { taskId: string; comments?: string }) => 
      workflowService.approveTask(taskId, comments),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-tasks'] })
      toast({
        title: 'Task approved',
        description: 'Task has been approved successfully',
      })
      setSelectedTask(null)
      setActionComments('')
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to approve task',
        variant: 'destructive',
      })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: ({ taskId, comments }: { taskId: string; comments: string }) => 
      workflowService.rejectTask(taskId, comments),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-tasks'] })
      toast({
        title: 'Task rejected',
        description: 'Task has been rejected',
      })
      setSelectedTask(null)
      setActionComments('')
    },
    onError: () => {
      toast({
        title: 'Error',
        description: 'Failed to reject task',
        variant: 'destructive',
      })
    },
  })

  const handleClaim = (task: WorkflowTask) => {
    claimMutation.mutate(task.id)
  }

  const handleApprove = (task: WorkflowTask) => {
    approveMutation.mutate({ taskId: task.id, comments: actionComments })
  }

  const handleReject = (task: WorkflowTask) => {
    if (!actionComments.trim()) {
      toast({
        title: 'Comments required',
        description: 'Please provide comments for rejection',
        variant: 'destructive',
      })
      return
    }
    rejectMutation.mutate({ taskId: task.id, comments: actionComments })
  }

  // Calculate stats
  const stats = data?.data?.items?.reduce(
    (acc, task: WorkflowTask) => {
      if (task.task_status === 'pending') acc.pending++
      else if (task.task_status === 'in_progress') acc.inProgress++
      else if (task.task_status === 'completed') acc.completed++
      else if (task.task_status === 'rejected') acc.rejected++
      
      // Check overdue
      if (task.due_date && new Date(task.due_date) < new Date() && 
          !['completed', 'rejected'].includes(task.task_status)) {
        acc.overdue++
      }
      
      return acc
    },
    { pending: 0, inProgress: 0, completed: 0, rejected: 0, overdue: 0 }
  ) || { pending: 0, inProgress: 0, completed: 0, rejected: 0, overdue: 0 }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
            <p className="text-gray-600 mt-1">View and manage your assigned workflow tasks</p>
          </div>
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
            icon={User}
            color="purple"
          />
          <StatCard
            label="Completed"
            value={stats.completed}
            icon={CheckCircle}
            color="green"
          />
          <StatCard
            label="Rejected"
            value={stats.rejected}
            icon={XCircle}
            color="red"
          />
          <StatCard
            label="Overdue"
            value={stats.overdue}
            icon={AlertCircle}
            color="orange"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="Search tasks by name..."
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

        {/* Tasks Tabs */}
        <Tabs value={statusFilter} onValueChange={setStatusFilter}>
          <TabsList>
            <TabsTrigger value="">All Tasks</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="claimed">Claimed</TabsTrigger>
            <TabsTrigger value="in_progress">In Progress</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
          </TabsList>

          <TabsContent value={statusFilter} className="space-y-4">
            {/* Table */}
            <div className="bg-white rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Task Name</TableHead>
                    <TableHead>Task Type</TableHead>
                    <TableHead>Instance</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Assigned</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {isLoading ? (
                    [...Array(5)].map((_, i) => (
                      <TableRow key={i}>
                        <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                        <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                        <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                        <TableCell><Skeleton className="h-8 w-24 ml-auto" /></TableCell>
                      </TableRow>
                    ))
                  ) : data?.data?.items && data.data.items.length > 0 ? (
                    data.data.items.map((task: WorkflowTask) => {
                      const isOverdue = task.due_date && new Date(task.due_date) < new Date() && 
                        !['completed', 'rejected'].includes(task.task_status)
                      
                      return (
                        <TableRow key={task.id}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{task.task_name}</p>
                              <p className="text-sm text-gray-500">ID: {task.id.slice(0, 8)}</p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{task.task_type}</Badge>
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            <Link 
                              href={`/workflow/instances/${task.instance_id}`}
                              className="text-blue-600 hover:underline"
                            >
                              {task.instance_id.slice(0, 12)}
                            </Link>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Badge className={getStatusColor(task.task_status)}>
                                {task.task_status}
                              </Badge>
                              {isOverdue && (
                                <Badge className="bg-red-100 text-red-700">
                                  Overdue
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600">
                            {task.due_date ? formatDate(task.due_date) : 'No due date'}
                          </TableCell>
                          <TableCell>
                            <p className="text-sm">
                              {task.assigned_to ? 'You' : task.assigned_to_role || 'Unassigned'}
                            </p>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              {task.task_status === 'pending' && !task.assigned_to && (
                                <Button
                                  size="sm"
                                  onClick={() => handleClaim(task)}
                                  disabled={claimMutation.isPending}
                                >
                                  Claim
                                </Button>
                              )}
                              {['claimed', 'in_progress'].includes(task.task_status) && (
                                <>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => setSelectedTask(task)}
                                  >
                                    View
                                  </Button>
                                  <Button
                                    size="sm"
                                    onClick={() => {
                                      setSelectedTask(task)
                                      setActionComments('')
                                    }}
                                  >
                                    Action
                                  </Button>
                                </>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    })
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                        <Clock className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                        <p>No tasks found</p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>

              {/* Pagination */}
              {data?.data && data.data.items.length > 0 && (
                <div className="flex items-center justify-between px-6 py-4 border-t">
                  <p className="text-sm text-gray-600">
                    Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, data.metadata?.total || 0)} of {data.metadata?.total || 0} tasks
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

        {/* Task Action Modal */}
        {selectedTask && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <div className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold">Task Action</h2>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setSelectedTask(null)
                      setActionComments('')
                    }}
                  >
                    <XCircle className="h-5 w-5" />
                  </Button>
                </div>

                <div className="space-y-4 border-t pt-4">
                  <div>
                    <p className="text-sm text-gray-600">Task Name</p>
                    <p className="font-semibold">{selectedTask.task_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Task Type</p>
                    <Badge variant="outline">{selectedTask.task_type}</Badge>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <Badge className={getStatusColor(selectedTask.task_status)}>
                      {selectedTask.task_status}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Comments (optional for approval, required for rejection)</label>
                    <textarea
                      className="w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                      placeholder="Add your comments here..."
                      value={actionComments}
                      onChange={(e) => setActionComments(e.target.value)}
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button
                      className="flex-1"
                      onClick={() => handleApprove(selectedTask)}
                      disabled={approveMutation.isPending}
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                    <Button
                      variant="destructive"
                      className="flex-1"
                      onClick={() => handleReject(selectedTask)}
                      disabled={rejectMutation.isPending}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Reject
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}
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
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'orange'
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
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
